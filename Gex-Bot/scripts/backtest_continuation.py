#!/usr/bin/env python3
"""
Backtest the pierce-retest continuation trade with real exit rules and costs.

The signal came out of an MFE study -- the best point price reached, which is
an upper bound, not a result. This replaces that with exit rules you could
actually give a broker, charges a cost per trade, and refuses to hold more than
one position at a time, which is what a person trading this would do.

SETUP
  Price touches a level, pierces it by `--pierce`, then returns to it. Enter at
  the retest in the break direction. Stop `--stop` points back through the
  level, because a reclaim invalidates the premise.

EXITS, each run separately
  target-2R / target-3R   fixed target, stop at 1R
  breakeven-then-run      stop to entry once 1R is banked, exit at the horizon
  time-only               no target; exit at the horizon at whatever price is

REALISM, and its limits
  * One position at a time, in chronological order. Signals arriving while a
    trade is open are skipped, and the count of those is reported.
  * `--cost` points are charged per round trip.
  * The series is sampled spot every 15 seconds, NOT bar high/low. A spike that
    hit the stop between two samples is invisible, so stop-outs are UNDERSTATED
    and every result here is optimistic. This cannot be fixed from this data.
  * Entry is assumed filled at the level. In practice a retest is where the
    spread widens.

Usage:
    python3 backtest_continuation.py --sessions /tmp/sessions.json --levels majors
"""

from __future__ import annotations

import argparse
import json
import statistics

MAJORS = [("pv", "vol C1"), ("nv", "vol P1"), ("po", "OI C1"), ("no", "OI P1")]
RANKED = [(f"{t}{s}{i}", f"{t}{s}{i}")
          for t in ("v", "o") for s in ("c", "p") for i in (1, 2, 3)]


def signals(session, fields, tol, pierce, reclaim, scan_s, offset=0.0):
    """Every (entry time, level, direction) the setup produces, chronologically."""
    series = sorted(session["series"], key=lambda r: r["t"])
    out = []
    for field, name in fields:
        if not series or field not in series[0]:
            continue
        armed = 0
        for i, r in enumerate(series):
            base = r.get(field, 0)
            if not base or base <= 0 or r["t"] < armed:
                continue
            L = base + offset
            if abs(r["spot"] - L) > tol:
                continue
            side = 0
            for j in range(i - 1, -1, -1):
                g = series[j]["spot"] - L
                if abs(g) > tol:
                    side = 1 if g > 0 else -1
                    break
            if not side:
                continue
            armed = r["t"] + scan_s
            pierced = False
            for k in range(i, len(series)):
                rr = series[k]
                if rr["t"] > r["t"] + 1800:
                    break
                d = (rr["spot"] - L) * side
                if d <= -pierce:
                    pierced = True
                elif pierced and abs(d) <= reclaim:
                    # break direction is -side (through the level)
                    out.append({"t": rr["t"], "i": k, "L": L, "dir": -side,
                                "name": name})
                    break
    out.sort(key=lambda s: s["t"])
    return series, out


def run_trade(series, sig, stop, horizon_s, rule):
    """Walk the trade forward. Returns realised R before costs."""
    entry = series[sig["i"]]["spot"]
    d = sig["dir"]                       # +1 = long, -1 = short
    end = sig["t"] + horizon_s
    be = False
    for m in range(sig["i"], len(series)):
        r = series[m]
        if r["t"] > end:
            break
        pnl = (r["spot"] - entry) * d    # points in favour
        if rule == "breakeven" and be and pnl <= 0:
            return 0.0, r["t"]
        if pnl <= -stop:
            return -1.0, r["t"]
        if rule == "target2" and pnl >= 2 * stop:
            return 2.0, r["t"]
        if rule == "target3" and pnl >= 3 * stop:
            return 3.0, r["t"]
        if rule == "breakeven" and pnl >= stop:
            be = True
        last = r
    pnl = (last["spot"] - entry) * d
    return pnl / stop, last["t"]


def backtest(sessions, fields, args, rule, offset=0.0):
    trades, skipped = [], 0
    for s in sessions:
        series, sigs = signals(s, fields, args.tol, args.pierce,
                               args.reclaim, args.cooldown * 60, offset)
        busy_until = 0
        for sig in sigs:
            if sig["t"] < busy_until:
                skipped += 1
                continue
            r, exit_t = run_trade(series, sig, args.stop,
                                  args.horizon * 60, rule)
            r -= args.cost / args.stop          # costs, in R
            trades.append(r)
            busy_until = exit_t
    return trades, skipped


def report(name, trades, skipped=None):
    if not trades:
        print(f"  {name:<20} no trades")
        return
    n = len(trades)
    wins = [t for t in trades if t > 0]
    tot = sum(trades)
    # worst peak-to-trough run of the equity curve, in R
    peak = eq = dd = 0.0
    for t in trades:
        eq += t
        peak = max(peak, eq)
        dd = min(dd, eq - peak)
    extra = f"{skipped:>8}" if skipped is not None else " " * 8
    print(f"  {name:<20} {n:>6} {100*len(wins)/n:>7.0f}% "
          f"{statistics.fmean(trades):>+8.2f} {tot:>+9.1f} {dd:>+9.1f}{extra}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sessions", default="/tmp/sessions.json")
    ap.add_argument("--ticker", default="NQ_NDX")
    ap.add_argument("--scope", default="gex_zero")
    ap.add_argument("--levels", default="majors", choices=["majors", "ranked"])
    ap.add_argument("--tol", type=float, default=15.0)
    ap.add_argument("--pierce", type=float, default=10.0)
    ap.add_argument("--reclaim", type=float, default=10.0)
    ap.add_argument("--stop", type=float, default=20.0)
    ap.add_argument("--horizon", type=float, default=90.0)
    ap.add_argument("--cooldown", type=float, default=20.0)
    ap.add_argument("--cost", type=float, default=2.0,
                    help="points per round trip (spread + slippage)")
    args = ap.parse_args()

    fields = MAJORS if args.levels == "majors" else RANKED
    sessions = [s for s in json.load(open(args.sessions))
                if s["ticker"] == args.ticker
                and s.get("scope", "gex_zero") == args.scope]
    if args.levels == "ranked":
        sessions = [s for s in sessions if s["series"] and "vc1" in s["series"][0]]
    sessions.sort(key=lambda s: s["date"])
    if not sessions:
        print("no sessions"); return 1

    rng = statistics.median([s["high"] - s["low"] for s in sessions])
    print(f"{args.ticker} {args.scope} [{args.levels}]: {len(sessions)} sessions "
          f"{sessions[0]['date']} to {sessions[-1]['date']}")
    print(f"stop {args.stop:g}pts, horizon {args.horizon:g}min, "
          f"cost {args.cost:g}pts/trade, one position at a time\n")
    print(f"  {'exit rule':<20} {'trades':>6} {'win%':>8} {'avg R':>8} "
          f"{'total R':>9} {'max DD':>9} {'skipped':>8}")
    for rule, label in (("target2", "target 2R"), ("target3", "target 3R"),
                        ("breakeven", "breakeven then run"), ("time", "time exit only")):
        t, sk = backtest(sessions, fields, args, rule)
        report(label, t, sk)

    print(f"\n  same rules on displaced (placebo) lines:")
    for rule, label in (("target2", "target 2R"), ("target3", "target 3R"),
                        ("breakeven", "breakeven then run"), ("time", "time exit only")):
        allt = []
        for f in (-0.55, -0.45, -0.35, -0.25, 0.25, 0.35, 0.45, 0.55):
            t, _ = backtest(sessions, fields, args, rule, round(rng * f))
            allt += t
        # scale total to a comparable number of trades
        report(label + " (placebo)", allt)
    print("\n  Placebo totals cover 8 displaced line sets, so read win% and\n"
          "  avg R, not total R. Stop-outs are understated throughout: the\n"
          "  series is 15-second sampled spot, not bar high/low.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
