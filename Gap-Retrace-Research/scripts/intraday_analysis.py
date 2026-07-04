"""
Intraday gap-and-retrace mechanics for GER40 (DAX) from M15 data.

We segment the continuous M15 stream into trading sessions by splitting on the
nightly void (>60 min with no bars). For each session that follows a prior
session we define the OPENING GAP and then trace, bar by bar, exactly how the
day retraces toward / through the gap before it makes its directional move.

Per gap day we record:
  gap_pts / gap_pct        open[t] - prior_close, and %.
  filled                   did price return to prior_close intraday (gap closed)?
  time_to_fill_min         minutes from session open to first touch of prior_close.
  max_retrace_frac         deepest retrace toward fill, as fraction of the gap,
                           measured BEFORE the session's directional extreme in the
                           gap direction (answers "how deep before it runs").
  reenter_prior_range      did price trade back inside prior day's H/L (wick) range?
  fade_or_go               did the session CLOSE in the gap direction (go) or against (fade)?
  open_hour_utc            session-open hour (context).

Reference-level convention tested:
  * gap is measured close-to-open (prior session close -> this session open)
  * prior-day RANGE marked wick-to-wick (true H/L) as the retrace target zone.
"""
import csv
import os
from datetime import datetime, timezone

DATA = os.path.join(os.path.dirname(__file__), "..", "data", "GER40_M15.csv")
OUT = os.path.join(os.path.dirname(__file__), "..", "analysis")
os.makedirs(OUT, exist_ok=True)


def load(path):
    rows = []
    with open(path) as f:
        for r in csv.DictReader(f):
            rows.append({
                "dt": datetime.fromtimestamp(int(r["timestamp"]) / 1000, tz=timezone.utc),
                "o": float(r["open"]), "h": float(r["high"]),
                "l": float(r["low"]), "c": float(r["close"]),
            })
    rows.sort(key=lambda x: x["dt"])
    return rows


def segment(rows, void_min=60):
    sessions, cur = [], [rows[0]]
    for i in range(1, len(rows)):
        dm = (rows[i]["dt"] - rows[i - 1]["dt"]).total_seconds() / 60
        if dm > void_min:
            sessions.append(cur)
            cur = []
        cur.append(rows[i])
    if cur:
        sessions.append(cur)
    return [s for s in sessions if len(s) >= 10]  # drop stub sessions


def analyze():
    rows = load(DATA)
    sessions = segment(rows)
    recs = []
    for i in range(1, len(sessions)):
        prev, ses = sessions[i - 1], sessions[i]
        prior_close = prev[-1]["c"]
        prior_hi = max(b["h"] for b in prev)
        prior_lo = min(b["l"] for b in prev)
        o = ses[0]["o"]
        gap = o - prior_close
        if gap == 0:
            continue
        up = gap > 0
        gap_pct = gap / prior_close * 100
        dh = (ses[0]["dt"] - prev[-1]["dt"]).total_seconds() / 3600
        weekend = dh > 40

        # walk the session
        filled = False
        t_fill = None
        run_ext = o          # directional extreme so far (gap direction)
        max_retrace_frac = 0.0
        reenter = False
        t0 = ses[0]["dt"]
        for b in ses:
            # track directional extreme
            if up:
                run_ext = max(run_ext, b["h"])
                # retrace = how far below open toward fill, before we consider fill
                retr = (o - b["l"]) / abs(gap)
            else:
                run_ext = min(run_ext, b["l"])
                retr = (b["h"] - o) / abs(gap)
            # only count retrace happening before/around the run; we take running max
            max_retrace_frac = max(max_retrace_frac, retr)
            # fill check
            if not filled:
                if (up and b["l"] <= prior_close) or (not up and b["h"] >= prior_close):
                    filled = True
                    t_fill = (b["dt"] - t0).total_seconds() / 60
            # re-enter prior range (wick)
            if b["l"] <= prior_hi and b["h"] >= prior_lo:
                reenter = True
        close = ses[-1]["c"]
        go = (close - o) * (1 if up else -1) > 0
        recs.append({
            "date": ses[0]["dt"].date().isoformat(),
            "open_hour": ses[0]["dt"].hour,
            "weekend": weekend, "up": up,
            "gap_pct": gap_pct, "abs_pct": abs(gap_pct), "gap_pts": abs(gap),
            "filled": filled, "t_fill": t_fill,
            "max_retrace_frac": min(max_retrace_frac, 2.0),
            "reenter": reenter, "go": go,
        })
    return recs


def pctf(n, d):
    return 100.0 * n / d if d else 0.0


def report(recs, thr=0.10):
    lines = ["=" * 78, "GER40 (DAX) INTRADAY GAP-&-RETRACE MECHANICS  — M15, ~5.4 months", "=" * 78]

    def block(sub, label):
        nonlocal lines
        n = len(sub)
        if not n:
            lines.append(f"\n{label}: (none)")
            return
        filled = [r for r in sub if r["filled"]]
        fillrate = pctf(len(filled), n)
        tf = sorted(r["t_fill"] for r in filled if r["t_fill"] is not None)
        med_tf = tf[len(tf) // 2] if tf else float("nan")
        within60 = pctf(sum(1 for r in filled if r["t_fill"] is not None and r["t_fill"] <= 60), n)
        within120 = pctf(sum(1 for r in filled if r["t_fill"] is not None and r["t_fill"] <= 120), n)
        reenter = pctf(sum(1 for r in sub if r["reenter"]), n)
        go = pctf(sum(1 for r in sub if r["go"]), n)
        rf = sorted(r["max_retrace_frac"] for r in sub)
        med_rf = rf[n // 2]
        # retrace-before-run buckets
        b = {"<25%": 0, "25-50%": 0, "50-75%": 0, "75-100%": 0, ">=100%": 0}
        for r in sub:
            f = r["max_retrace_frac"]
            if f >= 1.0: b[">=100%"] += 1
            elif f >= .75: b["75-100%"] += 1
            elif f >= .5: b["50-75%"] += 1
            elif f >= .25: b["25-50%"] += 1
            else: b["<25%"] += 1
        lines += [
            f"\n{label}: N={n}  (up {sum(1 for r in sub if r['up'])} / down {sum(1 for r in sub if not r['up'])})",
            f"   median gap {sorted(r['abs_pct'] for r in sub)[n//2]:.2f}%  ({sorted(r['gap_pts'] for r in sub)[n//2]:.0f} pts)",
            f"   GAP FILLED same session: {fillrate:.1f}%   |  re-entered prior-day range: {reenter:.1f}%",
            f"   time-to-fill: median {med_tf:.0f} min  | filled <=60min {within60:.0f}%  | <=120min {within120:.0f}%",
            f"   closed in gap direction (GO): {go:.1f}%  (FADE {100-go:.1f}%)",
            f"   max retrace toward fill (frac of gap): median {med_rf*100:.0f}%",
            f"   retrace-depth distribution: " + "  ".join(f"{k}:{pctf(v,n):.0f}%" for k, v in b.items()),
        ]

    block(recs, "ALL overnight+weekend gaps (any size)")
    block([r for r in recs if r["abs_pct"] >= thr], f"TRADEABLE gaps >= {thr}%")
    block([r for r in recs if r["weekend"]], "WEEKEND gaps only")
    block([r for r in recs if not r["weekend"] and r["abs_pct"] >= thr], f"WEEKDAY overnight gaps >= {thr}%")
    block([r for r in recs if r["up"] and r["abs_pct"] >= thr], f"GAP-UP >= {thr}%")
    block([r for r in recs if not r["up"] and r["abs_pct"] >= thr], f"GAP-DOWN >= {thr}%")

    txt = "\n".join(lines)
    print(txt)
    with open(os.path.join(OUT, "intraday_gap_stats.txt"), "w") as f:
        f.write(txt + "\n")
    return recs


if __name__ == "__main__":
    report(analyze())
