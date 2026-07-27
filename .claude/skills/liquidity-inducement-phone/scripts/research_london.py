#!/usr/bin/env python3
"""
research_london.py — does the liquidity model produce tradeable setups in the
LONDON morning, not just the New York session?

The skill gates intraday setups to NY and its London run-in (SKILL.md gate 5).
This asks whether that gate costs a London-based trader real setups, by
replaying historical M5 bars under the SAME rules the live skill applies.

METHOD
  For each session window on each day, walk bars forward:
   1. Detect a sweep+reclaim: a bar trades beyond the prior swing extreme and
      CLOSES back through it (same rule as analyze.py).
   2. Require the sweep to have cleared a CONFIRMED pool — a level with >= 2
      touches formed before the sweep. An incidental swing extreme is not a
      trap, and the live skill refuses it.
   3. Entry is the LB retest, not the next bar: price must trade back into the
      entry band within RETEST_BARS or the setup expires untaken. This is the
      rule the live skill actually states.
   4. Stop = beyond the swept extreme + buffer. Target = the nearest opposing
      CONFIRMED, unswept pool at least MIN_TARGET_FRAC of ADR away.
   5. Reject anything below the RR floor before taking it.
   6. Walk forward to session end. A bar touching both stop and target is
      scored a LOSS (intrabar order is unknowable from OHLC).
   7. SPREAD is charged on entry and exit.

Trades still open at session end are reported SEPARATELY and excluded from
totalR — marking them to market flattered the earlier version of this study.

REMAINING LIMITS
  - Fills assumed at the band edge; no slippage beyond spread.
  - Pool detection uses this file's simplified pivot/cluster pass, close to but
    not identical with analyze.py's.
  - A few dozen trades is still a small sample. Judge frequency and shape, not
    the third decimal of expectancy.

Usage:  python3 research_london.py [SYMBOL] [--days N] [--spread X]
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

WINDOWS = {
    "LONDON_AM": (LONDON, (8, 0), (11, 0)),        # currently gated OUT
    "LONDON_PRE_NY": (LONDON, (11, 0), (14, 30)),  # run-in, currently allowed
    "NY_AM": (NY, (9, 30), (12, 0)),               # what the model targets
}

LOOKBACK = 12          # bars defining the prior swing extreme
PIVOT_K = 2            # bars either side for a swing pivot
RETEST_BARS = 6        # how long the LB retest may take before expiry
MIN_TARGET_FRAC = 0.10  # target must be >= 10% of ADR away (the noise floor)
RR_FLOOR = 3.0         # skip anything that cannot pay 1:3
BUFFER_FRAC = 0.5      # stop buffer as a fraction of tol


def in_window(bar, tz, start, end):
    t = bar["time"].astimezone(tz)
    return (start[0], start[1]) <= (t.hour, t.minute) < (end[0], end[1])


def pivots(bars, k=PIVOT_K):
    hi, lo = [], []
    for i in range(k, len(bars) - k):
        w = bars[i - k:i + k + 1]
        if all(bars[i]["high"] >= b["high"] for b in w):
            hi.append((i, bars[i]["high"]))
        if all(bars[i]["low"] <= b["low"] for b in w):
            lo.append((i, bars[i]["low"]))
    return hi, lo


def cluster(levels, tol):
    """levels: [(idx, price)] -> pools with price, low, high, touches, last_i.
    Span-capped exactly as analyze.py does, so chains cannot form fake pools."""
    if not levels:
        return []
    pts = sorted(levels, key=lambda x: x[1])
    out, cur = [], [pts[0]]
    for p in pts[1:]:
        if abs(p[1] - cur[-1][1]) <= tol and p[1] - cur[0][1] <= tol * 2:
            cur.append(p)
        else:
            out.append(cur)
            cur = [p]
    out.append(cur)
    return [{"price": statistics.mean(x[1] for x in c),
             "low": min(x[1] for x in c), "high": max(x[1] for x in c),
             "touches": len(c), "last_i": max(x[0] for x in c)} for c in out]


def replay(bars, tol, adr, spread):
    """Score sweep+reclaim setups under the live skill's rules."""
    trades = []
    buf = tol * BUFFER_FRAC
    min_dist = adr * MIN_TARGET_FRAC
    i = LOOKBACK
    while i < len(bars) - 2:
        b = bars[i]
        prior = bars[i - LOOKBACK:i]
        rmax = max(p["high"] for p in prior)
        rmin = min(p["low"] for p in prior)

        side = None
        if b["high"] > rmax and b["close"] < rmax:
            side, extreme = "short", b["high"]
        elif b["low"] < rmin and b["close"] > rmin:
            side, extreme = "long", b["low"]
        if side is None:
            i += 1
            continue

        # --- gate: the sweep must have cleared a CONFIRMED pool -------------
        hi_p, lo_p = pivots(bars[:i])
        pools_hi = cluster(hi_p, tol)
        pools_lo = cluster(lo_p, tol)
        src = pools_hi if side == "short" else pools_lo
        cleared = [p for p in src if p["touches"] >= 2
                   and (extreme > p["high"] if side == "short"
                        else extreme < p["low"])]
        if not cleared:
            i += 1
            continue

        # --- entry: the LB retest, or the setup expires --------------------
        if side == "short":
            band_lo, band_hi = extreme - tol, extreme
            stop = extreme + buf
        else:
            band_lo, band_hi = extreme, extreme + tol
            stop = extreme - buf

        entry_i = None
        for j in range(i + 1, min(i + 1 + RETEST_BARS, len(bars))):
            f = bars[j]
            if f["low"] <= band_hi and f["high"] >= band_lo:
                entry_i = j
                break
        if entry_i is None:
            trades.append({"time": b["time"], "side": side,
                           "outcome": "no_fill", "r": 0.0})
            i += LOOKBACK // 2
            continue

        entry = band_lo if side == "short" else band_hi
        entry = entry - spread / 2 if side == "short" else entry + spread / 2

        # --- target: nearest opposing confirmed, unswept pool --------------
        opp = pools_lo if side == "short" else pools_hi
        cands = [p for p in opp if p["touches"] >= 2
                 and (p["high"] < entry - min_dist if side == "short"
                      else p["low"] > entry + min_dist)]
        if not cands:
            i += LOOKBACK // 2
            continue
        tgt_pool = (max(cands, key=lambda p: p["high"]) if side == "short"
                    else min(cands, key=lambda p: p["low"]))
        target = tgt_pool["high"] if side == "short" else tgt_pool["low"]

        risk = abs(entry - stop)
        reward = abs(target - entry) - spread
        if risk <= 0 or reward <= 0 or reward / risk < RR_FLOOR:
            i += LOOKBACK // 2
            continue
        rr = reward / risk

        outcome, r_mult = "open", 0.0
        for f in bars[entry_i + 1:]:
            hit_stop = f["low"] <= stop if side == "long" else f["high"] >= stop
            hit_tgt = f["high"] >= target if side == "long" else f["low"] <= target
            if hit_stop:                       # pessimistic if both
                outcome, r_mult = "stop", -1.0
                break
            if hit_tgt:
                outcome, r_mult = "target", rr
                break

        trades.append({"time": b["time"], "side": side, "outcome": outcome,
                       "r": r_mult, "rr_planned": rr,
                       "pool_touches": max(p["touches"] for p in cleared)})
        i += LOOKBACK // 2
    return trades


def summarise(name, trades):
    if not trades:
        return f"{name:16s} no setups"
    resolved = [t for t in trades if t["outcome"] in ("target", "stop")]
    wins = [t for t in resolved if t["outcome"] == "target"]
    stops = [t for t in resolved if t["outcome"] == "stop"]
    no_fill = [t for t in trades if t["outcome"] == "no_fill"]
    still_open = [t for t in trades if t["outcome"] == "open"]
    tot = sum(t["r"] for t in resolved)
    wr = 100 * len(wins) / len(resolved) if resolved else 0.0
    avg = tot / len(resolved) if resolved else 0.0
    med = (statistics.median(t["rr_planned"] for t in resolved)
           if resolved else 0.0)
    return (f"{name:16s} signals={len(trades):<4} nofill={len(no_fill):<3} "
            f"open={len(still_open):<3} | resolved={len(resolved):<3} "
            f"win={len(wins):<3} ({wr:4.0f}%) totalR={tot:+7.2f} "
            f"avgR={avg:+5.2f} medRR=1:{med:.1f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("symbol", nargs="?", default="XAUUSD")
    ap.add_argument("--days", type=int, default=45)
    ap.add_argument("--spread", type=float, default=0.30)
    args = ap.parse_args()

    bars = ct.fetch_ohlcv_paged(args.symbol, "M_5", days=args.days)
    if not bars:
        print({"error": "data fetch failed", "detail": ct.last_error()})
        sys.exit(2)

    daily = ct.fetch_ohlcv(args.symbol, "D_1", hours_back=720)
    rng = [d["high"] - d["low"] for d in daily[-14:]] if daily else []
    adr = statistics.mean(rng) if rng else 0.0
    px = bars[-1]["close"]
    tol = max(px * 0.0006, (adr or px) * 0.03)

    print(f"symbol={args.symbol}  M5 bars={len(bars)}  "
          f"{bars[0]['time']:%Y-%m-%d} to {bars[-1]['time']:%Y-%m-%d}")
    print(f"ADR14={adr:.2f}  tol={tol:.2f}  spread={args.spread}  "
          f"RR floor=1:{RR_FLOOR}  retest window={RETEST_BARS} bars\n")

    days = sorted({b["time"].astimezone(timezone.utc).date() for b in bars})
    results = {w: [] for w in WINDOWS}
    for d in days:
        for wname, (tz, start, end) in WINDOWS.items():
            seg = [b for b in bars
                   if b["time"].astimezone(tz).date() == d
                   and in_window(b, tz, start, end)]
            if len(seg) > LOOKBACK + 3:
                results[wname] += replay(seg, tol, adr, args.spread)

    print("=" * 100)
    print(f"{'WINDOW':16s} across {len(days)} calendar days "
          f"(open trades excluded from totalR)")
    print("=" * 100)
    for wname in WINDOWS:
        print(summarise(wname, results[wname]))

    print("\ndays with at least one FILLED setup")
    for wname in WINDOWS:
        ds = {t["time"].date() for t in results[wname]
              if t["outcome"] != "no_fill"}
        print(f"  {wname:16s} {len(ds)}/{len(days)} days")

    print("\nNOTE: entry requires an actual LB retest; sweeps must clear a "
          ">=2-touch pool; targets are confirmed pools past the noise floor; "
          "RR floor enforced; spread charged both sides; bars touching stop "
          "and target score as losses.")


if __name__ == "__main__":
    main()
