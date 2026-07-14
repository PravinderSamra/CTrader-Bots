#!/usr/bin/env python3
"""
Simulates a pending-order straddle around CPI releases:
  - 2 minutes before release, place a Buy Stop `trigger_dist` points above spot
    and a Sell Stop `trigger_dist` points below spot.
  - Whichever triggers first cancels the other (OCO).
  - Fixed stop-loss `sl_dist` points against entry, take-profit at `rr` x sl_dist
    (default 3RR) in favor. No trailing.
  - Resolved by scanning forward 1-min candles' high/low.

Tie-break rules (documented, not hidden):
  - If a single candle's range touches BOTH stop-entry levels: assume the
    level closer to that candle's OPEN triggers first (nearer level = more
    likely reached first from a standing start).
  - If a single candle's range touches BOTH the SL and TP of an open trade:
    assume SL hits first (conservative bias, standard backtest convention).
  - If neither SL nor TP is hit by the end of the available window
    (release + 45min), the trade is marked OPEN and mark-to-market at the
    last close is reported separately, excluded from win-rate stats.

Runs on the same 23 saved CPI-release NAS100/US500 candle files used by the
main CPI study -- no new data pulled.
"""
import json, os, sys, csv, datetime as dt

BASE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(BASE, "raw_candles")
sys.path.insert(0, BASE)
from simulate_confirmation_trail import RELEASE_UTC, to_ms, px

def load_candles(month, instrument):
    path = os.path.join(RAW, f"{month}_{instrument}.json")
    with open(path) as f:
        return {b["timestamp"]: b for b in json.load(f)["trendbars"]}

def simulate_event(month, instrument, trigger_dist, sl_dist, rr=3.0):
    bars = load_candles(month, instrument)
    release_ms = to_ms(RELEASE_UTC[month])
    entry_check_ms = release_ms - 2 * 60000  # order placed here

    b_spot = bars.get(entry_check_ms)
    if b_spot is None:
        closest = min(bars.keys(), key=lambda t: abs(t - entry_check_ms))
        if abs(closest - entry_check_ms) > 120000:
            return {"status": "no_data"}
        b_spot = bars[closest]
    S = px(b_spot, "open")

    buy_stop = S + trigger_dist
    sell_stop = S - trigger_dist

    sorted_ts = sorted(t for t in bars if t > entry_check_ms)
    entry_ts, direction, entry_price = None, None, None
    for t in sorted_ts:
        b = bars[t]
        hi, lo, op = px(b, "high"), px(b, "low"), px(b, "open")
        hit_buy = hi >= buy_stop
        hit_sell = lo <= sell_stop
        if hit_buy and hit_sell:
            # both touched in same candle -> nearer to open triggers first
            if abs(buy_stop - op) <= abs(op - sell_stop):
                direction, entry_price = 1, buy_stop
            else:
                direction, entry_price = -1, sell_stop
        elif hit_buy:
            direction, entry_price = 1, buy_stop
        elif hit_sell:
            direction, entry_price = -1, sell_stop
        if direction is not None:
            entry_ts = t
            break

    if direction is None:
        return {"status": "no_trigger", "spot": S}

    sl_price = entry_price - direction * sl_dist
    tp_price = entry_price + direction * sl_dist * rr

    resolve_ts = sorted(t for t in bars if t > entry_ts)
    outcome, exit_price = None, None
    for t in resolve_ts:
        b = bars[t]
        hi, lo = px(b, "high"), px(b, "low")
        if direction == 1:
            hit_sl = lo <= sl_price
            hit_tp = hi >= tp_price
        else:
            hit_sl = hi >= sl_price
            hit_tp = lo <= tp_price
        if hit_sl and hit_tp:
            outcome, exit_price = "loss", sl_price  # conservative: SL first
        elif hit_sl:
            outcome, exit_price = "loss", sl_price
        elif hit_tp:
            outcome, exit_price = "win", tp_price
        if outcome:
            break

    if outcome is None:
        last_bar = bars[resolve_ts[-1]] if resolve_ts else bars[entry_ts]
        last_close = px(last_bar, "close")
        r_multiple = (last_close - entry_price) * direction / sl_dist
        return {"status": "open", "direction": "Long" if direction == 1 else "Short",
                "entry": entry_price, "mtm_close": last_close, "r_multiple": r_multiple}

    r_multiple = rr if outcome == "win" else -1.0
    points = (exit_price - entry_price) * direction
    return {"status": outcome, "direction": "Long" if direction == 1 else "Short",
            "entry": entry_price, "exit": exit_price, "r_multiple": r_multiple, "points": points}

def run_full_sim(instrument, trigger_dist, sl_dist, rr=3.0, verbose=False):
    months = sorted(RELEASE_UTC.keys())
    results = [(m, simulate_event(m, instrument, trigger_dist, sl_dist, rr)) for m in months]
    wins = [r for m, r in results if r["status"] == "win"]
    losses = [r for m, r in results if r["status"] == "loss"]
    opens = [r for m, r in results if r["status"] == "open"]
    no_trig = [r for m, r in results if r["status"] == "no_trigger"]
    total_r = sum(r["r_multiple"] for r in wins + losses)
    n_resolved = len(wins) + len(losses)
    if verbose:
        print(f"\n=== {instrument}: trigger={trigger_dist}pts, SL={sl_dist}pts, TP={sl_dist*rr:.0f}pts (RR={rr}) ===")
        print(f"Events: {len(months)} | No-trigger (price never moved {trigger_dist}pts either way in time): {len(no_trig)} | "
              f"Still-open at window end: {len(opens)} | Resolved trades: {n_resolved}")
        print(f"Wins: {len(wins)} | Losses: {len(losses)} | Win rate: {100*len(wins)/n_resolved:.1f}%" if n_resolved else "No resolved trades")
        print(f"Total R: {total_r:+.2f} | Expectancy/trade: {total_r/n_resolved:+.3f}R" if n_resolved else "")
        total_pts = sum(r["points"] for r in wins + losses)
        print(f"Total points: {total_pts:+.1f} | Avg points/trade: {total_pts/n_resolved:+.1f}" if n_resolved else "")
        for m, r in results:
            if r["status"] in ("win", "loss"):
                print(f"  {m}: {r['direction']:5s} entry={r['entry']:.1f} exit={r['exit']:.1f} "
                      f"-> {r['status'].upper():4s} {r['r_multiple']:+.1f}R ({r['points']:+.1f}pts)")
            elif r["status"] == "open":
                print(f"  {m}: {r['direction']:5s} entry={r['entry']:.1f} -> OPEN at window end, mtm {r['r_multiple']:+.2f}R")
            elif r["status"] == "no_trigger":
                print(f"  {m}: NO TRIGGER (spot {r['spot']:.1f}, never moved {trigger_dist}pts)")
    return {"wins": len(wins), "losses": len(losses), "opens": len(opens), "no_trigger": len(no_trig),
            "total_r": total_r, "n_resolved": n_resolved,
            "expectancy": total_r / n_resolved if n_resolved else None}

if __name__ == "__main__":
    # Part 1: the user's exact requested setup
    for instrument in ("NAS100", "US500"):
        run_full_sim(instrument, trigger_dist=20, sl_dist=15, rr=3.0, verbose=True)
