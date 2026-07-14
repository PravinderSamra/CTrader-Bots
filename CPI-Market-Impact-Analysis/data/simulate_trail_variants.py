#!/usr/bin/env python3
"""Same entry logic as simulate_confirmation_trail.py, but compares 3 trailing-stop styles:
   A) tight  -- ratchet to the immediately preceding candle's low/high every candle (the literal
               "move my stop up as price trades up" reading)
   B) swing  -- ratchet to the lowest low / highest high of the last 3 CLOSED candles (gives
               normal 1-2min pullbacks room)
   C) fixed  -- ratchet to a fixed distance (15pts) behind the best price seen so far
"""
import json, csv, os, datetime as dt

BASE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(BASE, "raw_candles")
from importlib import import_module
import sys
sys.path.insert(0, BASE)
base_mod = import_module("simulate_confirmation_trail")
RELEASE_UTC = base_mod.RELEASE_UTC
to_ms = base_mod.to_ms
px = base_mod.px
load_expected = base_mod.load_expected

FIXED_DIST = 15.0

def simulate_event(month, expected, style):
    path = os.path.join(RAW, f"{month}_NAS100.json")
    bars = {b["timestamp"]: b for b in json.load(open(path))["trendbars"]}
    release_ms = to_ms(RELEASE_UTC[month])
    if expected == "Whipsaw":
        return {"month": month, "status": "no_setup"}

    direction = 1 if expected == "Bullish" else -1
    P0 = px(bars.get(release_ms, list(bars.values())[0]), "open")
    noise_floor = 0.0002 * P0

    confirm_bar, confirm_min = None, None
    for mins in (1, 2):
        t = release_ms + mins * 60000
        b = bars.get(t)
        if b is None:
            continue
        move = px(b, "close") - P0
        if direction * move > noise_floor:
            confirm_bar, confirm_min = b, mins
            break
    if confirm_bar is None:
        return {"month": month, "status": "no_confluence"}

    entry_price = px(confirm_bar, "close")
    entry_ts = confirm_bar["timestamp"]
    stop = px(confirm_bar, "low") if direction == 1 else px(confirm_bar, "high")
    best_price = entry_price
    recent_lows_highs = []  # for swing style

    sorted_ts = sorted(t for t in bars if t > entry_ts)
    exit_price, exit_reason = None, None
    last_close = entry_price
    for t in sorted_ts:
        if t - entry_ts > 15 * 60000:
            break
        b = bars[t]
        lo, hi, cl = px(b, "low"), px(b, "high"), px(b, "close")
        if direction == 1:
            if lo <= stop:
                exit_price, exit_reason = stop, "stopped"
                break
            best_price = max(best_price, hi)
            if style == "tight":
                stop = max(stop, lo)
            elif style == "swing":
                recent_lows_highs.append(lo)
                recent_lows_highs = recent_lows_highs[-3:]
                stop = max(stop, min(recent_lows_highs))
            elif style == "fixed":
                stop = max(stop, best_price - FIXED_DIST)
        else:
            if hi >= stop:
                exit_price, exit_reason = stop, "stopped"
                break
            best_price = min(best_price, lo)
            if style == "tight":
                stop = min(stop, hi)
            elif style == "swing":
                recent_lows_highs.append(hi)
                recent_lows_highs = recent_lows_highs[-3:]
                stop = min(stop, max(recent_lows_highs))
            elif style == "fixed":
                stop = min(stop, best_price + FIXED_DIST)
        last_close = cl

    if exit_price is None:
        exit_price = last_close
        exit_reason = "time_cap_15min"

    points = (exit_price - entry_price) * direction
    return {"month": month, "status": "trade", "direction": "Long" if direction == 1 else "Short",
            "points": round(points, 2), "exit_reason": exit_reason}

def run(style):
    expected_map = load_expected()
    results = [simulate_event(m, expected_map[m], style) for m in sorted(RELEASE_UTC)]
    trades = [r for r in results if r["status"] == "trade"]
    wins = [t for t in trades if t["points"] > 0]
    total = sum(t["points"] for t in trades)
    print(f"--- Trail style: {style} ---")
    print(f"Trades taken: {len(trades)} | Win rate: {len(wins)}/{len(trades)} = {100*len(wins)/len(trades):.1f}%")
    if wins:
        print(f"Avg win: {sum(w['points'] for w in wins)/len(wins):.1f} pts")
    losses = [t for t in trades if t["points"] <= 0]
    if losses:
        print(f"Avg loss: {sum(l['points'] for l in losses)/len(losses):.1f} pts")
    print(f"Total pts: {total:.1f} | Expectancy/trade: {total/len(trades):.1f} pts\n")

for style in ("tight", "swing", "fixed"):
    run(style)
