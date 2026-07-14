#!/usr/bin/env python3
"""
Simulates the user's stated strategy on NAS100, mechanically, from saved raw candles:
  1. Only look for a trade when the CPI print has a directional bias (expected label
     != Whipsaw) -- an in-line print gives no direction to seek confluence with.
  2. Wait up to 2 minutes post-release for price to move in the SAME direction as the
     print's implied bias ("confluence"). If neither the +1min nor +2min candle
     confirms, no trade is taken.
  3. On confirmation, enter at that candle's close. Initial stop = that candle's
     low (long) / high (short).
  4. Trail the stop behind the low/high of each subsequently CLOSED candle (only
     ever tightens toward price, never loosens).
  5. Exit on a stop-out, or at a hard 15-minute time cap from entry (proxy for
     "in and out in a matter of minutes"), whichever comes first.
"""
import json, csv, os, datetime as dt

BASE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(BASE, "raw_candles")

RELEASE_UTC = {
    "2024-06": "2024-07-11T12:30:00Z", "2024-07": "2024-08-14T12:30:00Z",
    "2024-08": "2024-09-11T12:30:00Z", "2024-09": "2024-10-10T12:30:00Z",
    "2024-10": "2024-11-13T13:30:00Z", "2024-11": "2024-12-11T13:30:00Z",
    "2024-12": "2025-01-15T13:30:00Z", "2025-01": "2025-02-12T13:30:00Z",
    "2025-02": "2025-03-12T12:30:00Z", "2025-03": "2025-04-10T12:30:00Z",
    "2025-04": "2025-05-13T12:30:00Z", "2025-05": "2025-06-11T12:30:00Z",
    "2025-06": "2025-07-15T12:30:00Z", "2025-07": "2025-08-12T12:30:00Z",
    "2025-08": "2025-09-11T12:30:00Z", "2025-09": "2025-10-24T12:30:00Z",
    "2025-11": "2025-12-18T13:30:00Z", "2025-12": "2026-01-13T13:30:00Z",
    "2026-01": "2026-02-13T13:30:00Z", "2026-02": "2026-03-11T12:30:00Z",
    "2026-03": "2026-04-10T12:30:00Z", "2026-04": "2026-05-12T12:30:00Z",
    "2026-05": "2026-06-10T12:30:00Z",
}

def to_ms(iso):
    return int(dt.datetime.strptime(iso, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc).timestamp() * 1000)

def px(bar, f="open"):
    return bar[f] / 100000.0

def load_expected():
    out = {}
    with open(os.path.join(BASE, "price_reaction.csv")) as f:
        for row in csv.DictReader(f):
            if row["instrument"] == "NAS100":
                out[row["reference_month"]] = row["expected_label"]
    return out

def simulate_event(month, expected):
    path = os.path.join(RAW, f"{month}_NAS100.json")
    bars = {b["timestamp"]: b for b in json.load(open(path))["trendbars"]}
    release_ms = to_ms(RELEASE_UTC[month])
    if expected == "Whipsaw":
        return {"month": month, "status": "no_setup", "reason": "in-line print, no directional bias"}

    direction = 1 if expected == "Bullish" else -1
    P0 = px(bars.get(release_ms, list(bars.values())[0]), "open")
    noise_floor = 0.0002 * P0  # ignore sub-noise "confirmation"

    confirm_bar = None
    for mins in (1, 2):
        t = release_ms + mins * 60000
        b = bars.get(t)
        if b is None:
            continue
        move = px(b, "close") - P0
        if direction * move > noise_floor:
            confirm_bar = b
            confirm_min = mins
            break

    if confirm_bar is None:
        return {"month": month, "status": "no_confluence", "expected": expected}

    entry_price = px(confirm_bar, "close")
    entry_ts = confirm_bar["timestamp"]
    stop = px(confirm_bar, "low") if direction == 1 else px(confirm_bar, "high")

    sorted_ts = sorted(t for t in bars if t > entry_ts)
    exit_price, exit_reason = None, None
    for t in sorted_ts:
        if t - entry_ts > 15 * 60000:
            break
        b = bars[t]
        lo, hi, cl = px(b, "low"), px(b, "high"), px(b, "close")
        if direction == 1:
            if lo <= stop:
                exit_price, exit_reason = stop, "stopped"
                break
            stop = max(stop, lo)
        else:
            if hi >= stop:
                exit_price, exit_reason = stop, "stopped"
                break
            stop = min(stop, hi)
        last_close = cl
        last_ts = t

    if exit_price is None:
        # timed exit at 15-min cap (or end of data if shorter)
        exit_price = last_close if sorted_ts else entry_price
        exit_reason = "time_cap_15min"

    points = (exit_price - entry_price) * direction
    return {
        "month": month, "status": "trade", "expected": expected,
        "direction": "Long" if direction == 1 else "Short",
        "confirm_min": confirm_min, "entry_price": round(entry_price, 2),
        "exit_price": round(exit_price, 2), "points": round(points, 2),
        "exit_reason": exit_reason,
    }

def main():
    expected_map = load_expected()
    results = [simulate_event(m, expected_map[m]) for m in sorted(RELEASE_UTC)]

    no_setup = [r for r in results if r["status"] == "no_setup"]
    no_confluence = [r for r in results if r["status"] == "no_confluence"]
    trades = [r for r in results if r["status"] == "trade"]

    print(f"Total events: {len(results)}")
    print(f"No directional print (Whipsaw expected, no trade attempted): {len(no_setup)}")
    print(f"Directional print but NO confluence within 2min (no trade taken): {len(no_confluence)}")
    print(f"Trades actually taken: {len(trades)}\n")

    wins = [t for t in trades if t["points"] > 0]
    losses = [t for t in trades if t["points"] <= 0]
    print(f"Win rate on trades taken: {len(wins)}/{len(trades)} = {100*len(wins)/len(trades):.1f}%")
    if wins:
        print(f"Avg winning trade: {sum(w['points'] for w in wins)/len(wins):.1f} pts (n={len(wins)}, max={max(w['points'] for w in wins):.1f})")
    if losses:
        print(f"Avg losing trade: {sum(l['points'] for l in losses)/len(losses):.1f} pts (n={len(losses)}, min={min(l['points'] for l in losses):.1f})")
    total_pts = sum(t["points"] for t in trades)
    print(f"Total points across all {len(trades)} trades: {total_pts:.1f}")
    print(f"Expectancy per trade taken: {total_pts/len(trades):.1f} pts")
    print(f"Expectancy per calendar event (23, incl. no-trades as 0): {total_pts/len(results):.1f} pts\n")

    print("Per-event detail:")
    for r in results:
        if r["status"] == "trade":
            print(f"  {r['month']}: {r['direction']:5s} confirmed at +{r['confirm_min']}min, "
                  f"entry {r['entry_price']}, exit {r['exit_price']} ({r['exit_reason']}), "
                  f"{'+' if r['points']>=0 else ''}{r['points']} pts")
        elif r["status"] == "no_confluence":
            print(f"  {r['month']}: expected {r['expected']}, NO confluence -> no trade")
        else:
            print(f"  {r['month']}: {r['reason']} -> no trade")

if __name__ == "__main__":
    main()
