"""
Coded gap-FADE strategy — the exact mechanical rule the cBot implements, backtested
on M15 with a spread cost model, day-of-week split, walk-forward (quarter-by-quarter)
and a parameter-sensitivity grid.

RULE (per trading session, defined by splitting the M15 stream on the nightly void):
  prior_close/high/low  = prior session's close / max high / min low.
  gap        = session_open - prior_close ;  gap_pct = gap/prior_close*100.
  qualify    : MIN_GAP_PCT <= |gap_pct| <= MAX_GAP_PCT.
  bias       : gap up -> SHORT the fade ; gap down -> LONG the fade.
  warmup     : ignore the first WARMUP bars (let the gap extend / show its extreme).
  TRIGGER (confirmation): after WARMUP bars, the first M15 bar that CLOSES back
             through the SESSION OPEN in the fade direction (a momentum-rejection of
             the gap), tracking the running extreme meanwhile:
                gap up  -> first bar closing < session_open -> enter SHORT at that close
                gap down-> first bar closing > session_open -> enter LONG  at that close
             must occur within MAX_WAIT bars, else no trade. (Selling into a rejection
             near the highs, NOT chasing a downside break — that entry tested worse.)
  stop       : beyond the session extreme seen so far +/- STOP_BUF_PCT*gap.
  target     : TP = prior_close (the fill).
  exit       : TP or SL by intra-bar touch (adverse-first if a bar spans both);
               else mark-to-close at session end.
  costs      : COST_PTS points deducted per round trip (spread + slippage proxy).

This is deliberately simple and un-optimised; the point is a robust, positive edge
that survives costs and out-of-sample time slices, not a curve-fit peak.
"""
import csv
import os
from datetime import datetime, timezone
from collections import defaultdict

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, "..", "data")
OUT = os.path.join(HERE, "..", "analysis")

# Recommended config from the 2y walk-forward: gap>=0.25%, weekday-only (see report).
DEFAULTS = dict(MIN_GAP_PCT=0.25, MAX_GAP_PCT=1.0, WARMUP=2, MAX_WAIT=16,
                STOP_BUF_PCT=0.10, COST_PTS=2.0)


def load(path):
    rows = []
    with open(path) as f:
        for r in csv.DictReader(f):
            rows.append({"dt": datetime.fromtimestamp(int(r["timestamp"]) / 1000, tz=timezone.utc),
                         "o": float(r["open"]), "h": float(r["high"]),
                         "l": float(r["low"]), "c": float(r["close"])})
    rows.sort(key=lambda x: x["dt"])
    return rows


def segment(rows, void_min=60):
    ss, cur = [], [rows[0]]
    for i in range(1, len(rows)):
        if (rows[i]["dt"] - rows[i - 1]["dt"]).total_seconds() / 60 > void_min:
            ss.append(cur); cur = []
        cur.append(rows[i])
    if cur:
        ss.append(cur)
    return [s for s in ss if len(s) >= 12]


def backtest(rows, p):
    ss = segment(rows)
    trades = []
    for i in range(1, len(ss)):
        prev, s = ss[i - 1], ss[i]
        pc = prev[-1]["c"]
        o = s[0]["o"]
        gap = o - pc
        if gap == 0:
            continue
        gpct = gap / pc * 100
        if not (p["MIN_GAP_PCT"] <= abs(gpct) <= p["MAX_GAP_PCT"]):
            continue
        if len(s) < p["WARMUP"] + 2:
            continue
        up = gap > 0
        dh = (s[0]["dt"] - prev[-1]["dt"]).total_seconds() / 3600
        weekend = dh > 40
        ext = o
        entry_idx = None
        for j in range(0, min(len(s), p["WARMUP"] + p["MAX_WAIT"])):
            b = s[j]
            ext = max(ext, b["h"]) if up else min(ext, b["l"])
            if j < p["WARMUP"]:
                continue
            if up and b["c"] < o:
                entry_idx = j; entry = b["c"]; break
            if (not up) and b["c"] > o:
                entry_idx = j; entry = b["c"]; break
        if entry_idx is None:
            continue
        buf = abs(gap) * p["STOP_BUF_PCT"]
        if up:  # SHORT, TP below at pc, SL above extreme
            sl = ext + buf; tp = pc
            risk = sl - entry
            if risk <= 0:
                continue
            res, exitp = _walk(s[entry_idx + 1:], tp, sl, long=False)
            rr = (entry - exitp) / risk
        else:   # LONG
            sl = ext - buf; tp = pc
            risk = entry - sl
            if risk <= 0:
                continue
            res, exitp = _walk(s[entry_idx + 1:], tp, sl, long=True)
            rr = (exitp - entry) / risk
        # costs: deduct round-trip points expressed in R
        rr -= p["COST_PTS"] / risk
        trades.append({"date": s[0]["dt"].date(), "dow": s[0]["dt"].weekday(),
                       "weekend": weekend, "up": up, "gap_pct": gpct,
                       "res": res, "R": rr, "risk_pts": risk})
    return trades


def _walk(bars, tp, sl, long):
    for b in bars:
        hit_tp = b["h"] >= tp if long else b["l"] <= tp
        hit_sl = b["l"] <= sl if long else b["h"] >= sl
        if hit_tp and hit_sl:
            return "sl", sl           # adverse-first (conservative)
        if hit_tp:
            return "tp", tp
        if hit_sl:
            return "sl", sl
    return "close", bars[-1]["c"] if bars else tp


def summ(trades):
    n = len(trades)
    if not n:
        return dict(n=0, win=0, exp=0, tot=0)
    wins = sum(1 for t in trades if t["R"] > 0)
    tot = sum(t["R"] for t in trades)
    return dict(n=n, win=100 * wins / n, exp=tot / n, tot=tot)


def report(symbol="GER40", m15_file="GER40_M15.csv"):
    rows = load(os.path.join(DATA, m15_file))
    p = dict(DEFAULTS)
    trades = backtest(rows, p)
    span = f"{rows[0]['dt'].date()} .. {rows[-1]['dt'].date()}"
    L = ["=" * 82, f"CODED GAP-FADE STRATEGY — {symbol}  ({m15_file}, {span})",
         f"params: {p}", "=" * 82]
    s = summ(trades)
    L.append(f"\nHEADLINE (all qualifying sessions, gap>={p['MIN_GAP_PCT']}%): trades={s['n']}  win%={s['win']:.1f}  "
             f"expectancy={s['exp']:.3f}R  total={s['tot']:.1f}R")
    rec = [t for t in trades if not t["weekend"]]
    sr = summ(rec)
    L.append(f"** RECOMMENDED (weekday-only, gap>={p['MIN_GAP_PCT']}%): trades={sr['n']}  win%={sr['win']:.1f}  "
             f"expectancy={sr['exp']:.3f}R  total={sr['tot']:.1f}R **")

    # day-of-week (0=Mon ... 4=Fri). Monday sessions = post-weekend gap.
    L.append("\nBY DAY-OF-WEEK (session open day):")
    dows = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    byd = defaultdict(list)
    for t in trades:
        byd[t["dow"]].append(t)
    for d in sorted(byd):
        ss = summ(byd[d])
        L.append(f"  {dows[d]}: n={ss['n']:3d}  win%={ss['win']:5.1f}  exp={ss['exp']:+.3f}R  tot={ss['tot']:+.1f}R")

    # weekend vs weekday
    for lab, sub in (("WEEKEND gaps", [t for t in trades if t["weekend"]]),
                     ("WEEKDAY overnight gaps", [t for t in trades if not t["weekend"]])):
        ss = summ(sub)
        L.append(f"  [{lab}] n={ss['n']}  win%={ss['win']:.1f}  exp={ss['exp']:+.3f}R  tot={ss['tot']:+.1f}R")

    # walk-forward by calendar quarter (time stability, no refitting)
    L.append("\nWALK-FORWARD by calendar quarter (same fixed params — checks time stability):")
    byq = defaultdict(list)
    for t in trades:
        q = f"{t['date'].year}Q{(t['date'].month-1)//3+1}"
        byq[q].append(t)
    for q in sorted(byq):
        ss = summ(byq[q])
        L.append(f"  {q}: n={ss['n']:3d}  win%={ss['win']:5.1f}  exp={ss['exp']:+.3f}R  tot={ss['tot']:+.1f}R")

    # parameter sensitivity grid (robustness, not optimisation)
    L.append("\nPARAMETER SENSITIVITY (expectancy R / #trades), across MIN_GAP x WARMUP:")
    hdr = "MIN_GAP\\WARMUP"
    warms = (1, 2, 4)
    L.append(f"  {hdr:>16s}" + "".join(f"{w:>12d}" for w in warms))
    for mg in (0.10, 0.15, 0.25):
        cells = []
        for w in warms:
            pp = dict(DEFAULTS); pp["MIN_GAP_PCT"] = mg; pp["WARMUP"] = w
            ss = summ(backtest(rows, pp))
            cells.append(f"{ss['exp']:+.2f}/{ss['n']:d}")
        L.append(f"  {mg:>16.2f}" + "".join(f"{c:>12s}" for c in cells))

    txt = "\n".join(L)
    print(txt)
    with open(os.path.join(OUT, f"strategy_{symbol}.txt"), "w") as f:
        f.write(txt + "\n")
    return trades


if __name__ == "__main__":
    import sys
    # prefer 2y file if present
    f = "GER40_M15_2y.csv" if os.path.exists(os.path.join(DATA, "GER40_M15_2y.csv")) else "GER40_M15.csv"
    report("GER40", f)
