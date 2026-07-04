"""
US cash-session (RTH) opening-gap study — the classic 09:30 ET gap the 24h CFD
"hides" (see Phase 1 §2). We reconstruct the Regular-Trading-Hours session
(09:30-16:00 America/New_York, DST-correct via zoneinfo) from the continuous
cTrader M15 feed and measure the overnight gap and its same-session fill.

For each RTH session t (prior RTH session t-1):
  rth_open   = open of the first M15 bar at/after 09:30 ET
  prior_close= close of the last M15 bar before 16:00 ET on day t-1
  gap        = rth_open - prior_close ; gap_pct
  fill       = did RTH price return to prior_close during 09:30-16:00 ET?
  time_to_fill, retrace depth, and directional close (fade vs go) as in Phase 1.

This is the price you actually trade on the CFD, windowed to US cash hours, so the
prior cash close is a real reference level even though the CFD had no literal void.
"""
import csv
import os
from datetime import datetime, timezone, time
from zoneinfo import ZoneInfo

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, "..", "data")
OUT = os.path.join(HERE, "..", "analysis")
NY = ZoneInfo("America/New_York")
RTH_START = time(9, 30)
RTH_END = time(16, 0)


def load(path):
    rows = []
    with open(path) as f:
        for r in csv.DictReader(f):
            dt = datetime.fromtimestamp(int(r["timestamp"]) / 1000, tz=timezone.utc)
            rows.append({"dt": dt, "et": dt.astimezone(NY),
                         "o": float(r["open"]), "h": float(r["high"]),
                         "l": float(r["low"]), "c": float(r["close"])})
    rows.sort(key=lambda x: x["dt"])
    return rows


def rth_sessions(rows):
    """Group bars into RTH sessions keyed by ET calendar date."""
    byday = {}
    for b in rows:
        et = b["et"]
        if RTH_START <= et.time() < RTH_END:
            byday.setdefault(et.date(), []).append(b)
    days = sorted(byday)
    return [(d, byday[d]) for d in days if len(byday[d]) >= 20]  # ~26 M15 bars in a full RTH day


def pctf(n, d):
    return 100.0 * n / d if d else 0.0


def analyze(symbol, m15_file, thr=0.10):
    rows = load(os.path.join(DATA, m15_file))
    sess = rth_sessions(rows)
    recs = []
    for i in range(1, len(sess)):
        (_, prev), (_, cur) = sess[i - 1], sess[i]
        prior_close = prev[-1]["c"]
        o = cur[0]["o"]
        gap = o - prior_close
        if gap == 0:
            continue
        up = gap > 0
        gpct = gap / prior_close * 100
        filled = False
        t_fill = None
        t0 = cur[0]["dt"]
        max_retr = 0.0
        for b in cur:
            retr = (o - b["l"]) / abs(gap) if up else (b["h"] - o) / abs(gap)
            max_retr = max(max_retr, retr)
            if not filled and ((up and b["l"] <= prior_close) or (not up and b["h"] >= prior_close)):
                filled = True
                t_fill = (b["dt"] - t0).total_seconds() / 60
        close = cur[-1]["c"]
        go = (close - o) * (1 if up else -1) > 0
        recs.append({"abs_pct": abs(gpct), "up": up, "filled": filled, "t_fill": t_fill,
                     "max_retr": min(max_retr, 2.0), "go": go})
    return summarize(symbol, m15_file, rows, sess, recs, thr)


def summarize(symbol, m15_file, rows, sess, recs, thr):
    L = ["=" * 80, f"US RTH CASH-OPEN GAP STUDY — {symbol}  ({m15_file})",
         f"span {rows[0]['et'].date()} .. {rows[-1]['et'].date()}  |  RTH sessions {len(sess)}", "=" * 80]

    def block(sub, label):
        nonlocal L
        n = len(sub)
        if not n:
            L.append(f"\n{label}: (none)"); return
        filled = [r for r in sub if r["filled"]]
        tf = sorted(r["t_fill"] for r in filled if r["t_fill"] is not None)
        med_tf = tf[len(tf) // 2] if tf else float("nan")
        w60 = pctf(sum(1 for r in filled if r["t_fill"] is not None and r["t_fill"] <= 60), n)
        go = pctf(sum(1 for r in sub if r["go"]), n)
        med_gap = sorted(r["abs_pct"] for r in sub)[n // 2]
        L += [
            f"\n{label}: N={n}  (up {sum(1 for r in sub if r['up'])}/down {sum(1 for r in sub if not r['up'])})  median gap {med_gap:.2f}%",
            f"   RTH GAP FILLED same session: {pctf(len(filled),n):.1f}%   time-to-fill median {med_tf:.0f}min  (<=60min {w60:.0f}%)",
            f"   closed in gap direction (GO): {go:.1f}%   (FADE {100-go:.1f}%)",
        ]

    block(recs, "ALL RTH gaps")
    block([r for r in recs if r["abs_pct"] >= thr], f"TRADEABLE RTH gaps >= {thr}%")
    # fill by size
    L.append("   FILL RATE BY GAP SIZE:")
    for lo, hi in [(0, .25), (.25, .5), (.5, 1.0), (1.0, 99)]:
        sub = [r for r in recs if lo <= r["abs_pct"] < hi]
        if sub:
            hl = f"{hi:.2f}" if hi < 99 else "+"
            L.append(f"     {lo:.2f}-{hl}% : N={len(sub):3d}  fill {pctf(sum(r['filled'] for r in sub),len(sub)):.0f}%")
    txt = "\n".join(L)
    print(txt)
    with open(os.path.join(OUT, f"rth_gap_{symbol}.txt"), "a") as f:
        f.write(txt + "\n")
    return recs


def main():
    open(os.path.join(OUT, "rth_gap_US500.txt"), "w").close()
    open(os.path.join(OUT, "rth_gap_US30.txt"), "w").close()
    for sym, f in (("US500", "US500_M15_2y.csv"), ("US30", "US30_M15_2y.csv")):
        p = os.path.join(DATA, f)
        if not os.path.exists(p):
            print(f"[skip] {f} not present yet"); continue
        analyze(sym, f)


if __name__ == "__main__":
    main()
