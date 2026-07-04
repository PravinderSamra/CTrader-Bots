"""
Entry-execution experiment (answers research questions #2 and #3).

Holds the SETUP layer fixed (same sessions, same gap qualification, same prior-day
close target, defined from M15) and varies only the EXECUTION:

  timeframe : M15 vs M5   -> does entering on 5-min bars catch the move earlier and
                            change win% / R?  (question #2)
  style     : BREAKOUT vs BREAK-&-RETEST                                (question #3)
     BREAKOUT      : enter when a bar CLOSES back through the session open in the fade
                     direction (the current rule — a break of the level, no retest).
     BREAK-RETEST  : after that break, wait for price to RETEST the open level and
                     enter there (limit), i.e. sell the pullback into the zone. Better
                     price + tighter stop, but sessions that never retest are skipped.

Warmup / max-wait / retest windows are TIME-based (minutes) so M15 and M5 are compared
apples-to-apples. Stop = beyond the running session extreme + buffer. Target = prior
close. Order-of-touch on the chosen timeframe's bars, adverse-first tie-break, 2pt cost.
Common window = the M5 file's span, so every cell sees the same calendar period.
"""
import csv
import os
from datetime import datetime, timezone, timedelta

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, "..", "data")
OUT = os.path.join(HERE, "..", "analysis")

P = dict(MIN_GAP_PCT=0.25, MAX_GAP_PCT=1.0, WARMUP_MIN=30, MAXWAIT_MIN=240,
         RETEST_MIN=180, STOP_BUF_PCT=0.10, COST_PTS=2.0, SKIP_WEEKEND=True)


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


def m5_slice(m5, t0, t1):
    return [b for b in m5 if t0 <= b["dt"] <= t1]


def run_session(bars, o, prior_close, up, weekend, style):
    """bars: execution-timeframe bars covering the session (ascending). Returns trade or None."""
    if not bars:
        return None
    t0 = bars[0]["dt"]
    warm = t0 + timedelta(minutes=P["WARMUP_MIN"])
    wait_end = t0 + timedelta(minutes=P["MAXWAIT_MIN"])
    ext = o
    break_idx = None
    for i, b in enumerate(bars):
        ext = max(ext, b["h"]) if up else min(ext, b["l"])
        if b["dt"] < warm:
            continue
        if b["dt"] > wait_end:
            break
        trig = (b["c"] < o) if up else (b["c"] > o)
        if trig:
            break_idx = i
            break
    if break_idx is None:
        return None

    if style == "breakout":
        entry = bars[break_idx]["c"]
        entry_i = break_idx
        entry_ext = ext
    else:  # break-retest: after the break, wait for price to return to the open level
        retest_end = bars[break_idx]["dt"] + timedelta(minutes=P["RETEST_MIN"])
        entry_i = None
        entry_ext = ext
        for j in range(break_idx + 1, len(bars)):
            b = bars[j]
            entry_ext = max(entry_ext, b["h"]) if up else min(entry_ext, b["l"])
            if b["dt"] > retest_end:
                break
            # retest of the open zone: price trades back to the open level
            if (up and b["h"] >= o) or (not up and b["l"] <= o):
                entry_i = j
                entry = o  # limit fill at the level
                break
        if entry_i is None:
            return None

    buf = abs(o - prior_close) * P["STOP_BUF_PCT"]
    if up:
        sl = entry_ext + buf; tp = prior_close
        risk = sl - entry
    else:
        sl = entry_ext - buf; tp = prior_close
        risk = entry - sl
    if risk <= 0:
        return None
    tp_valid = (tp < entry) if up else (tp > entry)
    if not tp_valid:
        return None

    res, exitp, exit_t = "close", bars[-1]["c"], bars[-1]["dt"]
    for b in bars[entry_i + 1:]:
        hit_tp = (b["l"] <= tp) if up else (b["h"] >= tp)
        hit_sl = (b["h"] >= sl) if up else (b["l"] <= sl)
        if hit_tp and hit_sl:
            res, exitp, exit_t = "sl", sl, b["dt"]; break
        if hit_tp:
            res, exitp, exit_t = "tp", tp, b["dt"]; break
        if hit_sl:
            res, exitp, exit_t = "sl", sl, b["dt"]; break
    rr = ((entry - exitp) if up else (exitp - entry)) / risk
    rr -= P["COST_PTS"] / risk
    tte = (bars[entry_i]["dt"] - t0).total_seconds() / 60
    return {"res": res, "R": rr, "risk": risk, "weekend": weekend, "tte": tte}


def experiment():
    m15 = load(os.path.join(DATA, "GER40_M15_2y.csv"))
    m5 = load(os.path.join(DATA, "GER40_M5_12m.csv"))
    lo = m5[0]["dt"]  # common window start
    sessions = segment(m15)

    setups = []  # (o, prior_close, up, weekend, m15_bars, t0, t1)
    for i in range(1, len(sessions)):
        prev, s = sessions[i - 1], sessions[i]
        if s[0]["dt"] < lo:
            continue
        pc = prev[-1]["c"]; o = s[0]["o"]; gap = o - pc
        if gap == 0:
            continue
        gpct = gap / pc * 100
        if not (P["MIN_GAP_PCT"] <= abs(gpct) <= P["MAX_GAP_PCT"]):
            continue
        weekend = (s[0]["dt"] - prev[-1]["dt"]).total_seconds() / 3600 > 40
        if P["SKIP_WEEKEND"] and weekend:
            continue
        setups.append((o, pc, gap > 0, weekend, s, s[0]["dt"], s[-1]["dt"]))

    def run_all(style, tf):
        trades = []
        for o, pc, up, wk, s, t0, t1 in setups:
            bars = s if tf == "M15" else m5_slice(m5, t0, t1)
            tr = run_session(bars, o, pc, up, wk, style)
            if tr:
                trades.append(tr)
        return trades

    def summ(tr, n_setups):
        n = len(tr)
        if not n:
            return "n=0"
        wins = [t for t in tr if t["R"] > 0]
        loss = [t for t in tr if t["R"] <= 0]
        exp = sum(t["R"] for t in tr) / n
        aw = sum(t["R"] for t in wins) / len(wins) if wins else 0
        al = sum(t["R"] for t in loss) / len(loss) if loss else 0
        tte = sorted(t["tte"] for t in tr)[n // 2]
        trig = 100 * n / n_setups
        return (f"n={n:3d} trig%={trig:4.0f} win%={100*len(wins)/n:5.1f} "
                f"exp={exp:+.3f}R tot={sum(t['R'] for t in tr):+6.1f}R "
                f"avgW={aw:+.2f} avgL={al:+.2f} medTTE={tte:.0f}m")

    L = ["=" * 100,
         f"ENTRY-EXECUTION EXPERIMENT — GER40, common window {lo.date()} .. {m15[-1]['dt'].date()}",
         f"setups (weekday gaps {P['MIN_GAP_PCT']}-{P['MAX_GAP_PCT']}%): {len(setups)}   "
         f"warmup {P['WARMUP_MIN']}m  maxwait {P['MAXWAIT_MIN']}m  retest {P['RETEST_MIN']}m  cost {P['COST_PTS']}pt",
         "=" * 100]
    for style in ("breakout", "break-retest"):
        L.append(f"\n[{style.upper()}]")
        for tf in ("M15", "M5"):
            L.append(f"  {tf:4s}: " + summ(run_all(style, tf), len(setups)))
    L.append("\nColumns: trig%=share of setups that produced an entry; medTTE=median minutes from")
    L.append("session open to entry; avgW/avgL = mean R of winners / losers.")
    txt = "\n".join(L)
    print(txt)
    with open(os.path.join(OUT, "entry_experiment.txt"), "w") as f:
        f.write(txt + "\n")


if __name__ == "__main__":
    experiment()
