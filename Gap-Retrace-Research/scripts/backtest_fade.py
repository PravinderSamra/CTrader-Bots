"""
Mechanical backtest of the gap-FADE (mean-reversion) play on GER40 M15.

The daily+intraday studies show GER40 overnight/weekend gaps fill ~85%/73% of
the time and more often CLOSE against the gap (fade). Here we put concrete
win-rate / expectancy numbers on trading that, using true intra-session
order-of-touch (which price level is reached first, walking the M15 bars).

Setups (per tradeable gap day, |gap| >= min_gap_pct):
  BASELINE OPEN-FADE  — at session open, fade toward the fill:
       gap up  -> SELL at open ; gap down -> BUY at open
       TP = prior_close (the gap fill)         [reward = 1.0 x gap]
       SL = open +/- stop_mult x gap           [risk  = stop_mult x gap]
       R:R = 1 / stop_mult.  We test stop_mult in {0.5, 1.0, 1.5}.

  CONFIRMATION FADE  — don't fade blindly at the open. Let the session first
       extend in the gap direction; ENTER only after a 15m bar closes back
       through the session-open level toward the fill (momentum rejection).
       SL = beyond the session extreme made so far (+ small buffer).
       TP1 = prior_close (fill).  We report win rate to TP1 and R multiple
       using actual SL distance.

Win/loss decided by which level the subsequent M15 bars touch first.
"""
import csv
import os
from datetime import datetime, timezone

DATA = os.path.join(os.path.dirname(__file__), "..", "data", "GER40_M15.csv")
OUT = os.path.join(os.path.dirname(__file__), "..", "analysis")


def load():
    rows = []
    with open(DATA) as f:
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
        if (rows[i]["dt"] - rows[i - 1]["dt"]).total_seconds() / 60 > void_min:
            sessions.append(cur); cur = []
        cur.append(rows[i])
    if cur:
        sessions.append(cur)
    return [s for s in sessions if len(s) >= 10]


def build_gaps(min_gap_pct):
    rows = load()
    sess = segment(rows)
    gaps = []
    for i in range(1, len(sess)):
        prev, s = sess[i - 1], sess[i]
        pc = prev[-1]["c"]
        o = s[0]["o"]
        g = o - pc
        if g == 0 or abs(g) / pc * 100 < min_gap_pct:
            continue
        gaps.append({"prior_close": pc, "open": o, "gap": g, "up": g > 0, "bars": s,
                     "date": s[0]["dt"].date().isoformat()})
    return gaps


def touch_first(bars, up_is_target, tp, sl):
    """Walk bars; return 'tp' or 'sl' depending which is touched first, else None.
       up_is_target True => TP is above (we are BUY/long, or fade of gap-down)."""
    for b in bars:
        hit_tp = b["h"] >= tp if up_is_target else b["l"] <= tp
        hit_sl = b["l"] <= sl if up_is_target else b["h"] >= sl
        if hit_tp and hit_sl:
            return "sl"  # conservative: assume adverse first when a bar spans both
        if hit_tp:
            return "tp"
        if hit_sl:
            return "sl"
    return None


def baseline(gaps, stop_mult):
    wins = losses = neither = 0
    Rs = []
    reward = 1.0
    risk = stop_mult
    for gp in gaps:
        o, g, pc = gp["open"], gp["gap"], gp["prior_close"]
        bars = gp["bars"]
        if gp["up"]:  # SELL at open, TP below at pc, SL above
            tp, sl = pc, o + stop_mult * abs(g)
            res = touch_first(bars, up_is_target=False, tp=tp, sl=sl)
        else:         # BUY at open, TP above at pc, SL below
            tp, sl = pc, o - stop_mult * abs(g)
            res = touch_first(bars, up_is_target=True, tp=tp, sl=sl)
        if res == "tp":
            wins += 1; Rs.append(reward / risk)
        elif res == "sl":
            losses += 1; Rs.append(-1.0)
        else:
            neither += 1
            # unresolved by session end: mark to prior_close vs open (settle at close)
            last = bars[-1]["c"]
            pnl = (o - last) if gp["up"] else (last - o)
            Rs.append((pnl / (stop_mult * abs(g))))
    n = len(gaps)
    wr = 100 * wins / n
    exp = sum(Rs) / n
    return n, wr, exp, wins, losses, neither


def confirmation(gaps, buffer_frac=0.10, warmup=2, max_wait=12):
    """Enter after a 15m bar closes back through the open toward fill, within first
       max_wait bars, after warmup bars of extension. SL beyond running extreme."""
    wins = losses = neither = notrig = 0
    Rs = []
    for gp in gaps:
        o, pc = gp["open"], gp["prior_close"]
        bars = gp["bars"]
        up = gp["up"]
        ext = o
        entry_idx = None
        for j, b in enumerate(bars[:max_wait]):
            ext = max(ext, b["h"]) if up else min(ext, b["l"])
            if j < warmup:
                continue
            # rejection: bar closes back through the open toward fill
            if (up and b["c"] < o) or (not up and b["c"] > o):
                entry_idx = j
                entry = b["c"]
                extreme = ext
                break
        if entry_idx is None:
            notrig += 1
            continue
        buf = abs(gp["gap"]) * buffer_frac
        if up:   # fading up -> SELL, SL above extreme, TP at fill (below)
            sl = extreme + buf
            tp = pc
            risk = sl - entry
            if risk <= 0:
                notrig += 1; continue
            res = touch_first(bars[entry_idx + 1:], up_is_target=False, tp=tp, sl=sl)
            rr = (entry - tp) / risk
        else:    # fading down -> BUY, SL below extreme, TP above
            sl = extreme - buf
            tp = pc
            risk = entry - sl
            if risk <= 0:
                notrig += 1; continue
            res = touch_first(bars[entry_idx + 1:], up_is_target=True, tp=tp, sl=sl)
            rr = (tp - entry) / risk
        if res == "tp":
            wins += 1; Rs.append(rr)
        elif res == "sl":
            losses += 1; Rs.append(-1.0)
        else:
            last = bars[-1]["c"]
            pnl = (entry - last) if up else (last - entry)
            Rs.append(pnl / risk); neither += 1
    traded = wins + losses + neither
    wr = 100 * wins / traded if traded else 0
    exp = sum(Rs) / traded if traded else 0
    avg_rr = sum(1 for _ in Rs)  # placeholder
    return traded, wr, exp, wins, losses, neither, notrig


def main():
    lines = ["=" * 78, "GER40 GAP-FADE MECHANICAL BACKTEST (M15, ~5.4 months)", "=" * 78]
    for mg in (0.10, 0.20):
        gaps = build_gaps(mg)
        lines.append(f"\n--- min gap {mg:.2f}%  (N={len(gaps)} gap days) ---")
        lines.append("BASELINE OPEN-FADE (TP=fill):")
        lines.append(f"  {'stop(xgap)':>11s} {'R:R':>6s} {'win%':>6s} {'expectancy(R)':>13s} {'W/L/none':>12s}")
        for sm in (0.5, 1.0, 1.5):
            n, wr, exp, w, l, ne = baseline(gaps, sm)
            lines.append(f"  {sm:11.1f} {1/sm:6.2f} {wr:6.1f} {exp:13.3f}   {w}/{l}/{ne}")
        t, wr, exp, w, l, ne, nt = confirmation(gaps)
        lines.append("CONFIRMATION FADE (enter on 15m rejection back through open; SL beyond extreme; TP=fill):")
        lines.append(f"  traded {t}/{len(gaps)} (no-trigger {nt})  win% {wr:.1f}  expectancy {exp:.3f}R  W/L/none {w}/{l}/{ne}")
    txt = "\n".join(lines)
    print(txt)
    with open(os.path.join(OUT, "fade_backtest.txt"), "w") as f:
        f.write(txt + "\n")


if __name__ == "__main__":
    main()
