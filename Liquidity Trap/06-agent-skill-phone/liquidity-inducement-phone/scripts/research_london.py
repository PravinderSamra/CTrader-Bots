#!/usr/bin/env python3
"""
research_london.py — does the liquidity model produce tradeable setups in the
LONDON morning, not just the New York session?

The skill currently gates intraday setups to NY and its London run-in
(SKILL.md gate 5). This asks whether that gate is costing a London-based
trader real setups, by replaying historical M5 bars and scoring every
sweep+reclaim as if it had been taken.

METHOD (and its limits — read these before trusting any number)
  * For each session window on each day, walk the bars forward. At each bar,
    detect a sweep+reclaim using the same rule as analyze.py: a bar trades
    beyond the prior swing extreme and CLOSES back through it.
  * Entry is assumed on the next bar's open (a pessimistic stand-in for the
    LB retest, which may never come — see BIAS below).
  * Stop = beyond the sweep extreme + a buffer. Target = the opposing swing
    extreme of the lookback window, which stands in for "the opposing pool".
  * Walk forward to the session end. Record whether stop or target hit first;
    intrabar order is unknowable from OHLC, so a bar touching both is scored
    as a LOSS (pessimistic).
  * R = reward/risk actually realised (+1R target, -1R stop, or the open
    P&L at session end scaled by the stop distance).

BIAS / LIMITS — the result is indicative, not a backtest:
  - No spread or slippage beyond the stop buffer.
  - Entry at next-bar open is more permissive than waiting for a retest that
    might never fill: it takes trades the real rules would have missed.
  - "Opposing swing extreme" is a proxy for a confirmed pool; it does not
    apply the confirmed/swept/too_close filters the live analyzer uses.
  - Sample is a handful of sessions. Treat single-digit trade counts as
    anecdote, not evidence.

Usage:  python3 research_london.py [SYMBOL] [--days N]
"""

import argparse
import statistics
import sys
from datetime import timezone
from zoneinfo import ZoneInfo

try:
    import ctrader_http as ct
except Exception:
    sys.path.insert(0, __file__.rsplit("/", 1)[0])
    import ctrader_http as ct

LONDON = ZoneInfo("Europe/London")
NY = ZoneInfo("America/New_York")

# Session windows, in *local* clock time so DST is handled automatically.
WINDOWS = {
    # London open through late morning — before the NY run-in begins.
    "LONDON_AM": (LONDON, (8, 0), (11, 0)),
    # The run-in the current gate already allows.
    "LONDON_PRE_NY": (LONDON, (11, 0), (14, 30)),
    # The session the model is actually written for.
    "NY_AM": (NY, (9, 30), (12, 0)),
}

LOOKBACK = 12      # bars used to define the prior swing extreme
BUFFER_FRAC = 0.5  # stop buffer as a fraction of the noise tolerance


def in_window(bar, tz, start, end):
    t = bar["time"].astimezone(tz)
    return (start[0], start[1]) <= (t.hour, t.minute) < (end[0], end[1])


def replay(bars, tol):
    """Score every sweep+reclaim in this list of bars. Returns list of dicts."""
    trades = []
    buf = tol * BUFFER_FRAC
    i = LOOKBACK
    while i < len(bars) - 1:
        b = bars[i]
        prior = bars[i - LOOKBACK:i]
        rmax = max(p["high"] for p in prior)
        rmin = min(p["low"] for p in prior)

        side = None
        if b["high"] > rmax and b["close"] < rmax:
            side = "short"
            stop = b["high"] + buf
            target = rmin
        elif b["low"] < rmin and b["close"] > rmin:
            side = "long"
            stop = b["low"] - buf
            target = rmax
        if side is None:
            i += 1
            continue

        entry = bars[i + 1]["open"]
        risk = abs(entry - stop)
        reward = abs(target - entry)
        if risk <= 0 or reward <= 0:
            i += 1
            continue
        rr = reward / risk

        outcome, r_mult = "open", 0.0
        for f in bars[i + 1:]:
            hit_stop = f["low"] <= stop if side == "long" else f["high"] >= stop
            hit_tgt = f["high"] >= target if side == "long" else f["low"] <= target
            if hit_stop and hit_tgt:      # order unknowable -> pessimistic
                outcome, r_mult = "stop", -1.0
                break
            if hit_stop:
                outcome, r_mult = "stop", -1.0
                break
            if hit_tgt:
                outcome, r_mult = "target", rr
                break
        if outcome == "open":             # session ended flat-ish
            last = bars[-1]["close"]
            pnl = (last - entry) if side == "long" else (entry - last)
            r_mult = pnl / risk

        trades.append({"time": b["time"], "side": side, "rr_planned": rr,
                       "outcome": outcome, "r": r_mult,
                       "risk": risk, "reward": reward})
        i += LOOKBACK // 2                # avoid re-counting the same event
    return trades


def summarise(name, trades):
    if not trades:
        return f"{name:16s} no setups"
    n = len(trades)
    wins = [t for t in trades if t["outcome"] == "target"]
    stops = [t for t in trades if t["outcome"] == "stop"]
    tot_r = sum(t["r"] for t in trades)
    med_rr = statistics.median(t["rr_planned"] for t in trades)
    return (f"{name:16s} n={n:<4} win={len(wins):<3} stop={len(stops):<3} "
            f"open={n-len(wins)-len(stops):<3} "
            f"totalR={tot_r:+7.2f}  avgR={tot_r/n:+6.2f}  medianRR=1:{med_rr:.1f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("symbol", nargs="?", default="XAUUSD")
    ap.add_argument("--days", type=int, default=14)
    args = ap.parse_args()

    hours = min(args.days * 24, 720)
    bars = ct.fetch_ohlcv(args.symbol, "M_5", hours_back=hours)
    if not bars:
        print({"error": "data fetch failed", "detail": ct.last_error()})
        sys.exit(2)

    daily = ct.fetch_ohlcv(args.symbol, "D_1", hours_back=720)
    rng = [d["high"] - d["low"] for d in daily[-14:]] if daily else []
    adr = statistics.mean(rng) if rng else 0.0
    px = bars[-1]["close"]
    tol = max(px * 0.0006, (adr or px) * 0.03)

    print(f"symbol={args.symbol}  M5 bars={len(bars)}  "
          f"from {bars[0]['time']:%Y-%m-%d} to {bars[-1]['time']:%Y-%m-%d}")
    print(f"ADR14={adr:.2f}  tol={tol:.2f}  stop buffer={tol*BUFFER_FRAC:.2f}\n")

    days = sorted({b["time"].astimezone(timezone.utc).date() for b in bars})
    all_by_window = {w: [] for w in WINDOWS}

    for d in days:
        for wname, (tz, start, end) in WINDOWS.items():
            seg = [b for b in bars
                   if b["time"].astimezone(tz).date() == d
                   and in_window(b, tz, start, end)]
            if len(seg) > LOOKBACK + 2:
                all_by_window[wname] += replay(seg, tol)

    print("=" * 78)
    print(f"{'WINDOW':16s} results across {len(days)} calendar days")
    print("=" * 78)
    for wname in WINDOWS:
        print(summarise(wname, all_by_window[wname]))

    print("\nper-day setup counts")
    for wname in WINDOWS:
        by_day = {}
        for t in all_by_window[wname]:
            by_day[t["time"].date()] = by_day.get(t["time"].date(), 0) + 1
        print(f"  {wname:16s} {dict(sorted(by_day.items()))}")

    print("\nNOTE: entry is next-bar open, not a confirmed LB retest; bars that "
          "touch stop and target are scored as losses; no spread modelled. "
          "Small samples are anecdote, not evidence.")


if __name__ == "__main__":
    main()
