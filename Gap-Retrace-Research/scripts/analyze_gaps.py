"""
Gap & retrace statistical analysis on the downloaded D_1 data.

For every daily bar we compute the gap vs the prior bar's close, classify it as
continuous (intra-week, no market closure) or session gap (weekend/holiday, a real
void), then measure same-day fill and retrace depth.

Definitions (per bar t, prior bar t-1):
  gap_pts   = open[t] - close[t-1]
  gap_pct   = gap_pts / close[t-1] * 100
  UP gap    : gap_pts > 0 ; fill measured by how far LOW[t] falls back toward close[t-1]
  DOWN gap  : gap_pts < 0 ; fill measured by how far HIGH[t] rises back toward close[t-1]
  fill_frac = fraction of the gap retraced intraday, capped display at 1.5
              UP:   (open[t] - low[t])  / gap        (>=1.0 => gap fully filled)
              DOWN: (high[t] - open[t]) / |gap|
  full_fill : gap completely closed same session (fill_frac >= 1.0)
  go_frac   : continuation beyond the open in gap direction, relative to gap size
  outcome   : did the bar CLOSE in the gap direction (continuation) or against (fade)?

Session gap vs continuous is decided by the wall-clock delta between consecutive
bar opens: ~24h => continuous weekday roll; >40h => a weekend/holiday closure.
"""
import csv
import glob
import os
from datetime import datetime, timezone

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "analysis")
os.makedirs(OUT_DIR, exist_ok=True)


def load(path):
    rows = []
    with open(path) as f:
        for r in csv.DictReader(f):
            rows.append({
                "ts": int(r["timestamp"]),
                "dt": datetime.fromtimestamp(int(r["timestamp"]) / 1000, tz=timezone.utc),
                "o": float(r["open"]), "h": float(r["high"]),
                "l": float(r["low"]), "c": float(r["close"]),
            })
    rows.sort(key=lambda x: x["ts"])
    return rows


def pct(n, d):
    return 100.0 * n / d if d else 0.0


def analyze(name, rows, gap_threshold_pct=0.15):
    """gap_threshold_pct: minimum |gap%| to count as a tradeable gap (filters noise)."""
    gaps = []
    for i in range(1, len(rows)):
        a, b = rows[i - 1], rows[i]
        dh = (b["dt"] - a["dt"]).total_seconds() / 3600.0
        session_gap = dh > 40  # weekend/holiday closure vs ~24h weekday roll
        gp = b["o"] - a["c"]
        gpct = gp / a["c"] * 100.0
        if gp == 0:
            continue
        up = gp > 0
        if up:
            fill = (b["o"] - b["l"]) / abs(gp)
            full = b["l"] <= a["c"]
            go = (b["h"] - b["o"]) / abs(gp)
        else:
            fill = (b["h"] - b["o"]) / abs(gp)
            full = b["h"] >= a["c"]
            go = (b["o"] - b["l"]) / abs(gp)
        cont = (b["c"] - b["o"]) * (1 if up else -1) > 0  # closed in gap direction
        gaps.append({
            "dt": b["dt"], "session_gap": session_gap, "up": up,
            "gap_pts": gp, "gap_pct": gpct, "abs_pct": abs(gpct),
            "fill": fill, "full": full, "go": go, "cont": cont,
            "range_pct": (b["h"] - b["l"]) / a["c"] * 100.0,
        })

    def summarize(subset, label):
        n = len(subset)
        if n == 0:
            return f"  {label}: (none)"
        ups = [g for g in subset if g["up"]]
        downs = [g for g in subset if not g["up"]]
        absp = sorted(g["abs_pct"] for g in subset)
        med = absp[n // 2]
        mean = sum(absp) / n
        p90 = absp[int(n * 0.9)]
        full = sum(1 for g in subset if g["full"])
        fills = sorted(min(g["fill"], 1.5) for g in subset)
        med_fill = fills[n // 2]
        # retrace-depth buckets (fraction of gap retraced same day)
        buckets = {"<25%": 0, "25-50%": 0, "50-75%": 0, "75-100%": 0, ">=100% (full)": 0}
        for g in subset:
            fr = g["fill"]
            if fr >= 1.0:
                buckets[">=100% (full)"] += 1
            elif fr >= 0.75:
                buckets["75-100%"] += 1
            elif fr >= 0.50:
                buckets["50-75%"] += 1
            elif fr >= 0.25:
                buckets["25-50%"] += 1
            else:
                buckets["<25%"] += 1
        cont = sum(1 for g in subset if g["cont"])
        lines = [
            f"  {label}: N={n}  (up {len(ups)} / down {len(downs)})",
            f"      gap size %: median {med:.2f}  mean {mean:.2f}  p90 {p90:.2f}",
            f"      SAME-DAY FULL FILL: {full}/{n} = {pct(full,n):.1f}%   median retrace {med_fill*100:.0f}% of gap",
            f"      closed in gap direction (continuation): {pct(cont,n):.1f}%   (fade {pct(n-cont,n):.1f}%)",
            f"      retrace-depth distribution: " + "  ".join(f"{k}:{pct(v,n):.0f}%" for k, v in buckets.items()),
        ]
        return "\n".join(lines)

    out = [f"\n{'='*78}", f"{name}  ({rows[0]['dt'].date()} .. {rows[-1]['dt'].date()}, {len(rows)} daily bars)", "="*78]
    sess = [g for g in gaps if g["session_gap"]]
    cont_g = [g for g in gaps if not g["session_gap"]]
    sess_thr = [g for g in sess if g["abs_pct"] >= gap_threshold_pct]
    cont_thr = [g for g in cont_g if g["abs_pct"] >= gap_threshold_pct]

    # how often the continuous weekday roll even produces a >threshold gap
    out.append(f"  Continuous weekday rolls: {len(cont_g)}, of which |gap|>={gap_threshold_pct}%: "
               f"{len(cont_thr)} ({pct(len(cont_thr),len(cont_g)):.1f}%)  <- shows intraweek gaps are ~absent")
    out.append(summarize(sess, "WEEKEND/HOLIDAY gaps (ALL sizes)"))
    out.append(summarize(sess_thr, f"WEEKEND/HOLIDAY gaps >= {gap_threshold_pct}%"))

    # fill rate conditioned on gap-size bucket (session gaps)
    size_buckets = [(0.0, 0.25), (0.25, 0.5), (0.5, 1.0), (1.0, 99)]
    out.append("      FILL RATE BY GAP SIZE (weekend/holiday gaps):")
    for lo, hi in size_buckets:
        sub = [g for g in sess if lo <= g["abs_pct"] < hi]
        if sub:
            fr = pct(sum(1 for g in sub if g["full"]), len(sub))
            hi_lbl = f"{hi:.2f}" if hi < 99 else "+"
            out.append(f"        gap {lo:.2f}-{hi_lbl}% : N={len(sub):3d}  full-fill {fr:.0f}%")
    return "\n".join(out), {
        "name": name, "session_gaps": len(sess),
        "session_gaps_thr": len(sess_thr),
        "full_fill_rate_all": pct(sum(1 for g in sess if g["full"]), len(sess)) if sess else 0,
        "full_fill_rate_thr": pct(sum(1 for g in sess_thr if g["full"]), len(sess_thr)) if sess_thr else 0,
        "median_gap_pct": (sorted(g["abs_pct"] for g in sess)[len(sess)//2]) if sess else 0,
        "cont_rate_thr": pct(sum(1 for g in sess_thr if g["cont"]), len(sess_thr)) if sess_thr else 0,
    }


def main():
    reports, summary = [], []
    for path in sorted(glob.glob(os.path.join(DATA_DIR, "*_D1.csv"))):
        name = os.path.basename(path).replace("_D1.csv", "")
        rows = load(path)
        rep, s = analyze(name, rows)
        reports.append(rep)
        summary.append(s)

    # ranking table
    tbl = ["\n" + "="*78, "INSTRUMENT RANKING (weekend/holiday session gaps, 3y)", "="*78,
           f"{'sym':8s} {'#gaps':>6s} {'#>=.15%':>8s} {'medGap%':>8s} {'fill%(all)':>11s} {'fill%(>=.15)':>13s} {'cont%':>7s}"]
    for s in sorted(summary, key=lambda x: -x["full_fill_rate_thr"]):
        tbl.append(f"{s['name']:8s} {s['session_gaps']:6d} {s['session_gaps_thr']:8d} "
                   f"{s['median_gap_pct']:8.2f} {s['full_fill_rate_all']:11.1f} "
                   f"{s['full_fill_rate_thr']:13.1f} {s['cont_rate_thr']:7.1f}")
    full = "\n".join(reports) + "\n" + "\n".join(tbl)
    print(full)
    with open(os.path.join(OUT_DIR, "daily_gap_stats.txt"), "w") as f:
        f.write(full + "\n")


if __name__ == "__main__":
    main()
