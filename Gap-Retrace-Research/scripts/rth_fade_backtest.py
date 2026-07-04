"""
Cross-instrument fade-strategy backtest (answers "is the tradeable edge better on
another instrument, and should we drill M5/retest there too?").

Until now the fade P&L was GER40-only. US indices barely gap intra-week, so their
tradeable gap is the RTH cash-open (09:30-ET). Here we run the SAME entry engine
(compare_entries.run_session: 30-min warmup, breakout close-back-through-open, stop
beyond session extreme, target=prior close, 2pt cost) but anchored to each
instrument's RTH session, for GER40 (Xetra), US500 and US30 (NYSE cash).

Reported per instrument: gap>=0.15% and >=0.25%, all sessions vs skip-first-of-week
(the weekend/Monday gap analog). This is the apples-to-apples instrument comparison.
"""
import csv
import os
from datetime import datetime, timezone, time
from zoneinfo import ZoneInfo
from collections import defaultdict
import compare_entries as C

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
OUT = os.path.join(os.path.dirname(__file__), "..", "analysis")

# instrument -> (M15 file, tz, RTH start local, RTH end local, min bars/day)
INSTR = {
    "GER40": ("GER40_M15_2y.csv", ZoneInfo("Europe/Berlin"), time(9, 0), time(17, 30), 20),
    "US500": ("US500_M15_2y.csv", ZoneInfo("America/New_York"), time(9, 30), time(16, 0), 20),
    "US30":  ("US30_M15_2y.csv",  ZoneInfo("America/New_York"), time(9, 30), time(16, 0), 20),
}


def load(path):
    rows = []
    with open(path) as f:
        for r in csv.DictReader(f):
            dt = datetime.fromtimestamp(int(r["timestamp"]) / 1000, tz=timezone.utc)
            rows.append({"dt": dt, "o": float(r["open"]), "h": float(r["high"]),
                         "l": float(r["low"]), "c": float(r["close"])})
    rows.sort(key=lambda x: x["dt"])
    return rows


def rth_sessions(rows, tz, t_start, t_end, min_bars):
    byday = defaultdict(list)
    for b in rows:
        loc = b["dt"].astimezone(tz)
        if t_start <= loc.time() < t_end:
            byday[loc.date()].append(b)
    days = sorted(byday)
    return [(d, byday[d]) for d in days if len(byday[d]) >= min_bars]


def run_instrument(name):
    m15file, tz, ts, te, mb = INSTR[name]
    rows = load(os.path.join(DATA, m15file))
    sess = rth_sessions(rows, tz, ts, te, mb)
    # build trades keyed by (gap_thr, skip_weekend, style)
    results = {}
    for gthr in (0.15, 0.25):
        for style in ("breakout", "break-retest"):
            trades_all, trades_wd = [], []
            for i in range(1, len(sess)):
                (pd, prev), (cd, cur) = sess[i - 1], sess[i]
                pc = prev[-1]["c"]; o = cur[0]["o"]; gap = o - pc
                if gap == 0:
                    continue
                gpct = gap / pc * 100
                if not (gthr <= abs(gpct) <= 1.0):
                    continue
                weekend = (cd - pd).days > 1  # first session of the week / after holiday
                tr = C.run_session(cur, o, pc, gap > 0, weekend, style)
                if not tr:
                    continue
                tr = dict(tr, date=cd)
                trades_all.append(tr)
                if not weekend:
                    trades_wd.append(tr)
            results[(gthr, style)] = (trades_all, trades_wd, len(sess))
    return results


def summ(tr):
    n = len(tr)
    if not n:
        return dict(n=0, win=0, exp=0, tot=0, q="0/0")
    wins = sum(1 for t in tr if t["R"] > 0)
    byq = defaultdict(float)
    for t in tr:
        byq[f"{t['date'].year}Q{(t['date'].month-1)//3+1}"] += t["R"]
    qpos = sum(1 for q in byq if byq[q] > 0)
    return dict(n=n, win=100 * wins / n, exp=sum(t["R"] for t in tr) / n,
                tot=sum(t["R"] for t in tr), q=f"{qpos}/{len(byq)}")


def main():
    L = ["=" * 104,
         "CROSS-INSTRUMENT FADE BACKTEST — RTH cash-open anchor, M15, breakout entry, 2pt cost, 2y",
         "same entry engine as the GER40 experiment (compare_entries.run_session)", "=" * 104]
    for name in ("GER40", "US500", "US30"):
        res = run_instrument(name)
        L.append(f"\n### {name}  (RTH-anchored)")
        L.append(f"  {'config':28s} {'N':>4s} {'win%':>6s} {'exp(R)':>8s} {'totR':>7s} {'+qtrs':>6s}")
        for gthr in (0.15, 0.25):
            for style in ("breakout", "break-retest"):
                all_t, wd_t, nsess = res[(gthr, style)]
                sa, sw = summ(all_t), summ(wd_t)
                L.append(f"  {style+' >='+str(gthr)+'% all':28s} {sa['n']:>4d} {sa['win']:>6.1f} "
                         f"{sa['exp']:>+8.3f} {sa['tot']:>+7.1f} {sa['q']:>6s}")
                L.append(f"  {style+' >='+str(gthr)+'% skip-wknd':28s} {sw['n']:>4d} {sw['win']:>6.1f} "
                         f"{sw['exp']:>+8.3f} {sw['tot']:>+7.1f} {sw['q']:>6s}")
    L.append("\nReference — GER40 NATIVE overnight-void anchor (weekday-only >=0.25%): +0.247R, 59% win, +12R (49 trades).")
    L.append("RTH rows above use the 09:30-ET / Xetra cash open instead, so GER40 here is NOT its best anchor.")
    txt = "\n".join(L)
    print(txt)
    with open(os.path.join(OUT, "cross_instrument_fade.txt"), "w") as f:
        f.write(txt + "\n")


if __name__ == "__main__":
    main()
