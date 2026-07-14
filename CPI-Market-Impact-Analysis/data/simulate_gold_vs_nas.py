#!/usr/bin/env python3
"""Runs the identical confirmation-entry + trailing-stop simulation (3 trail styles)
on XAUUSD (gold) and prints it alongside the existing NAS100 results, for a direct
apples-to-apples comparison of the user's strategy across instruments.
Also computes the plain 30-min "expected vs actual" hit rate for gold, matching
the original US500/NAS100 price_reaction.csv methodology.
"""
import json, csv, os, sys, datetime as dt

BASE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(BASE, "raw_candles")
sys.path.insert(0, BASE)
from simulate_confirmation_trail import RELEASE_UTC, to_ms, px, load_expected
FIXED_DIST_GOLD = 1.5  # dollars; gold's own typical spike scale (see 30-min classifier threshold discussion)

def load_candles(month, instrument):
    path = os.path.join(RAW, f"{month}_{instrument}.json")
    with open(path) as f:
        return {b["timestamp"]: b for b in json.load(f)["trendbars"]}

def nearest_bar(bars, target_ms, search_ms=(0, -60000, 60000, -120000, 120000)):
    for offset in search_ms:
        t = target_ms + offset
        if t in bars:
            return bars[t]
    closest = min(bars.keys(), key=lambda t: abs(t - target_ms))
    return bars[closest] if abs(closest - target_ms) <= 180000 else None

def classify_30min(month, instrument, expected):
    bars = load_candles(month, instrument)
    release_ms = to_ms(RELEASE_UTC[month])
    b0 = nearest_bar(bars, release_ms)
    b30 = nearest_bar(bars, release_ms + 30 * 60000)
    b5 = nearest_bar(bars, release_ms + 5 * 60000)
    if not all([b0, b30, b5]):
        return None
    P0, P30, P5 = px(b0), px(b30), px(b5)
    net_move, initial_move = P30 - P0, P5 - P0
    threshold = 0.0005 * P0
    window_bars = [b for t, b in bars.items() if release_ms <= t <= release_ms + 30 * 60000]
    high_30m = max(px(b, "high") for b in window_bars)
    low_30m = min(px(b, "low") for b in window_bars)
    if abs(net_move) < threshold:
        label = "Whipsaw"
    elif (initial_move > 0) != (net_move > 0):
        adverse = (P0 - low_30m) if net_move > 0 else (high_30m - P0)
        label = "Whipsaw" if adverse > threshold else ("Bullish" if net_move > 0 else "Bearish")
    else:
        label = "Bullish" if net_move > 0 else "Bearish"
    points = round(abs(net_move), 2)
    hit = (label == expected) if expected != "Unknown" else None
    return {"label": label, "points": points, "hit": hit}

def simulate_event(month, expected, instrument, style, fixed_dist):
    bars = load_candles(month, instrument)
    release_ms = to_ms(RELEASE_UTC[month])
    if expected == "Whipsaw":
        return {"status": "no_setup"}
    direction = 1 if expected == "Bullish" else -1
    b0 = nearest_bar(bars, release_ms)
    P0 = px(b0, "open")
    noise_floor = 0.0002 * P0

    confirm_bar = None
    for mins in (1, 2):
        b = nearest_bar(bars, release_ms + mins * 60000, search_ms=(0,))
        if b is None:
            continue
        move = px(b, "close") - P0
        if direction * move > noise_floor:
            confirm_bar = b
            break
    if confirm_bar is None:
        return {"status": "no_confluence"}

    entry_price = px(confirm_bar, "close")
    entry_ts = confirm_bar["timestamp"]
    stop = px(confirm_bar, "low") if direction == 1 else px(confirm_bar, "high")
    best_price = entry_price
    recent = []
    sorted_ts = sorted(t for t in bars if t > entry_ts)
    exit_price, last_close = None, entry_price
    for t in sorted_ts:
        if t - entry_ts > 15 * 60000:
            break
        b = bars[t]
        lo, hi, cl = px(b, "low"), px(b, "high"), px(b, "close")
        if direction == 1:
            if lo <= stop:
                exit_price = stop
                break
            best_price = max(best_price, hi)
            if style == "tight":
                stop = max(stop, lo)
            elif style == "swing":
                recent.append(lo); recent = recent[-3:]
                stop = max(stop, min(recent))
            elif style == "fixed":
                stop = max(stop, best_price - fixed_dist)
        else:
            if hi >= stop:
                exit_price = stop
                break
            best_price = min(best_price, lo)
            if style == "tight":
                stop = min(stop, hi)
            elif style == "swing":
                recent.append(hi); recent = recent[-3:]
                stop = min(stop, max(recent))
            elif style == "fixed":
                stop = min(stop, best_price + fixed_dist)
        last_close = cl
    if exit_price is None:
        exit_price = last_close
    points = (exit_price - entry_price) * direction
    return {"status": "trade", "points": round(points, 2)}

def run_trail(instrument, style, fixed_dist=15.0):
    expected_map = load_expected()  # keyed off NAS100 rows but expected_label is instrument-independent (calendar-only)
    results = [simulate_event(m, expected_map[m], instrument, style, fixed_dist) for m in sorted(RELEASE_UTC)]
    trades = [r for r in results if r["status"] == "trade"]
    wins = [t for t in trades if t["points"] > 0]
    total = sum(t["points"] for t in trades)
    return len(trades), len(wins), total, (total / len(trades) if trades else 0)

def main():
    expected_map = load_expected()

    print("=== 30-min expected-vs-actual hit rate (matches original methodology) ===")
    for instrument in ("NAS100", "XAUUSD"):
        results = [classify_30min(m, instrument, expected_map[m]) for m in sorted(RELEASE_UTC)]
        results = [r for r in results if r is not None]
        hits = [r for r in results if r["hit"]]
        bulls = [r["points"] for r in results if r["label"] == "Bullish"]
        bears = [r["points"] for r in results if r["label"] == "Bearish"]
        print(f"{instrument}: hit rate {len(hits)}/{len(results)} = {100*len(hits)/len(results):.1f}%  "
              f"| Bullish avg {sum(bulls)/len(bulls) if bulls else 0:.1f}pts (n={len(bulls)})  "
              f"| Bearish avg {sum(bears)/len(bears) if bears else 0:.1f}pts (n={len(bears)})")

    print("\n=== Confirmation-entry + trailing-stop simulation (same rules, both instruments) ===")
    for instrument, fixed_dist in (("NAS100", 15.0), ("XAUUSD", 1.5)):
        print(f"\n--- {instrument} (fixed trail = {fixed_dist} {'pts' if instrument=='NAS100' else 'USD'}) ---")
        for style in ("tight", "swing", "fixed"):
            n, w, total, exp = run_trail(instrument, style, fixed_dist)
            print(f"  {style:6s}: trades={n:2d}  win_rate={100*w/n if n else 0:5.1f}%  "
                  f"total={total:8.2f}  expectancy/trade={exp:7.2f}")

if __name__ == "__main__":
    main()
