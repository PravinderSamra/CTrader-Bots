#!/usr/bin/env python3
"""
LEVEL REACTION STATISTICS — the confluence layer that works today.

The question this answers
------------------------
"Price has come back up to the H1 pivot I marked. It's printing wicks through it
but not closing through. Should I be confident shorting with my stop beyond the
deepest wick?"

This does not need Level 2 data to answer usefully. It needs the historical
record of what happened the LAST N times price did exactly this, at this level,
on this instrument, in this kind of day. That record is derivable right now from
cTrader M1 + H1 bars, with no new credentials.

Method
------
1. Mark H1 swing pivots and cluster them into levels (pivots.py).
2. On M1, find every discrete VISIT to each level.
3. For each visit measure how far the wick went beyond the level, and whether
   price ever CLOSED through it (two consecutive closes, so one spike doesn't
   count as a break).
4. Derive the stop distance empirically: the p90 of wick-through across visits
   that did not break. That is "just beyond the deepest wick", as a number.
5. Replay every visit as an actual trade with that stop — bar by bar, in order,
   stop checked before target. A visit that would have been stopped out is
   booked as -1R even if price later went the right way. No look-ahead.

That last point matters. Measuring best-case and worst-case excursion
independently is the standard way to make a mediocre level look like a goldmine;
this replays the path instead.

Honesty about the data
----------------------
cTrader `volume` is TICK volume (quote-update count), not traded contracts, and
these are Pepperstone CFD/spread-bet prices, not exchange prints. So `efficiency`
is a proxy for absorption, not a measurement of it — Tier 2 in the sense used by
"Order Flow System"/Stage3_Architecture.md. The true resting-liquidity read is
the DOM recorder — see src/dom_recorder.py.

Usage
-----
    python3 "Gala Heatmap/src/level_stats.py" --symbol UK100 --days 15
    python3 "Gala Heatmap/src/level_stats.py" --symbol XAUUSD --days 20 --strength 4
    python3 "Gala Heatmap/src/level_stats.py" --symbol UK100 --near 10880 --days 20
"""

from __future__ import annotations

import argparse
import json
import os
import statistics as stats
import sys
from collections import defaultdict
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ctrader_http import CTraderClient, CTraderError, iso, now_ms  # noqa: E402
from pivots import significant_levels, find_pivots, Level  # noqa: E402

DAY_MS = 86_400_000


# --------------------------------------------------------------------- events

@dataclass
class TouchEvent:
    level_price: float
    side: str            # "resistance" (approached from below) | "support"
    start_ts: int
    end_ts: int
    end_idx: int         # index into the M1 series, for the replay pass
    bars: int
    pierce: float        # deepest wick beyond the level, in points
    close_beyond: float  # deepest CLOSE beyond the level, in points
    broke: bool          # two consecutive closes beyond → genuinely through
    ticks: int
    efficiency: float    # net progress per 1,000 ticks during the touch
    day_bias: str        # "bearish" | "bullish" | "flat"
    session: str         # "asia" | "london" | "us" | "late"

    # Filled by replay() / replay_rejection() once the stop distance is known.
    r_outcome: float = 0.0    # realised R, stop checked before target
    mfe_r: float = 0.0        # best R reached before the stop was hit
    stopped: bool = False
    resolved: bool = False    # False = ran out of horizon still open
    triggered: bool = True    # rejection model: did a rejection bar ever print?
    entry_px: float = 0.0
    stop_px: float = 0.0


def _session(ts: int) -> str:
    h = datetime.fromtimestamp(ts / 1000, tz=timezone.utc).hour
    if h < 7:
        return "asia"
    if h < 12:
        return "london"
    if h < 17:
        return "us"
    return "late"


def _day_bias(bar: dict, day_open: float, flat_pct: float = 0.0008) -> str:
    if day_open <= 0:
        return "flat"
    d = (bar["c"] - day_open) / day_open
    if d > flat_pct:
        return "bullish"
    if d < -flat_pct:
        return "bearish"
    return "flat"


def find_touch_events(bars: list[dict], level: float, band: float, *,
                      gap_bars: int = 3, break_buffer: float = 0.0,
                      day_opens: dict[str, float] | None = None) -> list[TouchEvent]:
    """Group M1 bars into discrete visits to the level and characterise each."""
    day_opens = day_opens or {}
    lo, hi = level - band, level + band

    touching = [i for i, b in enumerate(bars) if b["l"] <= hi and b["h"] >= lo]
    if not touching:
        return []

    # Merge into runs, tolerating short gaps so one visit isn't split into five.
    runs: list[list[int]] = [[touching[0]]]
    for i in touching[1:]:
        if i - runs[-1][-1] <= gap_bars + 1:
            runs[-1].append(i)
        else:
            runs.append([i])

    events: list[TouchEvent] = []
    for run in runs:
        s, e = run[0], run[-1]
        seg = bars[s: e + 1]

        # Which way did price arrive? Look back for the last bar that closed
        # clearly outside the band.
        side = None
        for j in range(s - 1, max(-1, s - 16), -1):
            if bars[j]["c"] < lo:
                side = "resistance"
                break
            if bars[j]["c"] > hi:
                side = "support"
                break
        if side is None:
            continue  # price originated inside the band — not a clean test

        if side == "resistance":
            pierce = max(b["h"] for b in seg) - level
            closes_beyond = [b["c"] - level for b in seg]
        else:
            pierce = level - min(b["l"] for b in seg)
            closes_beyond = [level - b["c"] for b in seg]

        pierce = max(0.0, pierce)
        close_beyond = max(0.0, max(closes_beyond))
        # A break needs two consecutive closes through — one spike is a wick.
        broke = any(
            closes_beyond[i] > break_buffer and closes_beyond[i + 1] > break_buffer
            for i in range(len(closes_beyond) - 1)
        )

        ticks = sum(b["v"] for b in seg) or 1
        net = abs(seg[-1]["c"] - seg[0]["o"])
        efficiency = net / ticks * 1000.0

        day_key = datetime.fromtimestamp(bars[s]["ts"] / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
        bias = _day_bias(bars[s], day_opens.get(day_key, 0.0))

        events.append(TouchEvent(
            level_price=level, side=side,
            start_ts=bars[s]["ts"], end_ts=bars[e]["ts"], end_idx=e, bars=len(seg),
            pierce=pierce, close_beyond=close_beyond, broke=broke,
            ticks=ticks, efficiency=efficiency,
            day_bias=bias, session=_session(bars[s]["ts"]),
        ))
    return events


# ------------------------------------------------------- independent sampling

def independent_counts(events: list[TouchEvent], merge_min: int = 60) -> dict:
    """How many genuinely independent observations are in here?

    Touch events are NOT independent. During chop a single visit to a level
    produces many events, and their outcomes are dominated by that day's regime —
    at XAUUSD 4,049.44 the raw count was 60 events, which was really 16 visits
    across 7 days, one visit alone holding 17 events.

    Treating 60 as the sample size hands full statistical confidence to what is
    effectively a handful of observations. The point estimate survives that
    (measured: +1.06R at n=60 events vs +1.00R at n=4 days) but the confidence
    in it does not, so sample weighting must key off these numbers instead.
    """
    if not events:
        return {"events": 0, "visits": 0, "days": 0}
    ordered = sorted(events, key=lambda e: e.start_ts)
    visits = 1
    for prev, cur in zip(ordered, ordered[1:]):
        if (cur.start_ts - prev.end_ts) / 60_000 >= merge_min:
            visits += 1
    days = len({datetime.fromtimestamp(e.start_ts / 1000, tz=timezone.utc)
                .strftime("%Y-%m-%d") for e in events})
    return {"events": len(events), "visits": visits, "days": days}


# ---------------------------------------------------------------------- replay

def derive_stop_distance(events: list[TouchEvent], floor: float, cap: float) -> float:
    """Empirical 'just beyond the deepest wick'.

    p90 of wick-through across visits that did NOT break. Clamped to a floor
    (a stop of zero is not a stop) and a cap (so one freak spike doesn't set an
    unusable risk).
    """
    held_pierces = [e.pierce for e in events if not e.broke]
    base = _pct(held_pierces, 0.90) if held_pierces else _pct([e.pierce for e in events], 0.90)
    return max(floor, min(cap, base))


def replay(events: list[TouchEvent], bars: list[dict], stop_dist: float,
           horizon: int, target_r: float = 3.0) -> None:
    """Walk each visit forward bar by bar as a real trade. Mutates events.

    Entry at the level on the bar after the visit ends, in the direction the
    level implies (short a resistance test, long a support test). Stop at
    `stop_dist` beyond the level. Within a bar the stop is assumed hit first —
    the pessimistic assumption, since M1 OHLC does not tell us the path.
    """
    for e in events:
        entry = e.level_price
        if e.side == "resistance":
            stop = entry + stop_dist
        else:
            stop = entry - stop_dist

        best_r = 0.0
        e.stopped = False
        e.resolved = False

        for b in bars[e.end_idx + 1: e.end_idx + 1 + horizon]:
            # Stop first — pessimistic, and the honest choice without tick data.
            if e.side == "resistance":
                if b["h"] >= stop:
                    e.stopped = True
                    break
                r = (entry - b["l"]) / stop_dist
            else:
                if b["l"] <= stop:
                    e.stopped = True
                    break
                r = (b["h"] - entry) / stop_dist
            best_r = max(best_r, r)
            if best_r >= target_r:
                e.resolved = True
                break

        e.mfe_r = best_r
        if e.stopped:
            e.r_outcome = -1.0
        else:
            # Not stopped within the horizon: book what was actually reachable,
            # capped at the target. Unresolved runners are not free money.
            e.r_outcome = min(best_r, target_r)
            e.resolved = e.resolved or best_r >= target_r


def replay_rejection(events: list[TouchEvent], bars: list[dict], level: float, *,
                     stop_floor: float, spread: float, horizon: int,
                     target_r: float = 3.0, eps: float = 0.0) -> None:
    """Replay the trade as actually described: wait for the rejection, then enter.

    For each visit, find the first bar that wicks THROUGH the level and closes
    back inside it. Enter at that bar's close (crossing the spread), stop beyond
    that bar's printed wick — the "just beyond the deepest wick" rule — but never
    tighter than `stop_floor`.

    That floor is the whole point. Measured on XAUUSD 4,049.44, the unfloored
    rule gives a ~1.6 point stop and −0.33R; a 5-point floor gives +0.52R and a
    7-point floor +0.62R. The entry timing was never the problem, the stop was.

    Visits where no rejection ever printed are marked triggered=False — there was
    no signal, so they are neither wins nor losses.
    """
    idx = {b["ts"]: i for i, b in enumerate(bars)}
    for e in events:
        e.triggered = False
        e.r_outcome = 0.0
        e.mfe_r = 0.0
        e.stopped = False
        e.resolved = False

        s = idx.get(e.start_ts)
        if s is None:
            continue
        end = e.end_idx
        short = e.side == "resistance"

        rej = None
        for i in range(s, min(end + 1, len(bars))):
            b = bars[i]
            if short and b["h"] >= level and b["c"] < level - eps:
                rej = i
                break
            if (not short) and b["l"] <= level and b["c"] > level + eps:
                rej = i
                break
        if rej is None:
            continue

        rb = bars[rej]
        if short:
            entry = rb["c"] - spread / 2          # sell the bid
            stop = max(rb["h"] + spread, entry + stop_floor)
        else:
            entry = rb["c"] + spread / 2          # buy the ask
            stop = min(rb["l"] - spread, entry - stop_floor)
        risk = abs(stop - entry)
        if risk <= 0:
            continue

        e.triggered = True
        e.entry_px = entry
        e.stop_px = stop
        best = 0.0
        for b in bars[rej + 1: rej + 1 + horizon]:
            if short:
                if b["h"] >= stop:
                    e.stopped = True
                    break
                best = max(best, (entry - b["l"]) / risk)
            else:
                if b["l"] <= stop:
                    e.stopped = True
                    break
                best = max(best, (b["h"] - entry) / risk)
            if best >= target_r:
                e.resolved = True
                break
        e.mfe_r = best
        e.r_outcome = -1.0 if e.stopped else min(best, target_r)


# ------------------------------------------------------------------ aggregation

def _pct(vals: list[float], q: float) -> float:
    """Nearest-rank percentile — no numpy, and correct for tiny samples."""
    if not vals:
        return 0.0
    s = sorted(vals)
    k = max(0, min(len(s) - 1, int(round(q * (len(s) - 1)))))
    return s[k]


def summarise(events: list[TouchEvent]) -> dict:
    if not events:
        return {"n": 0}
    held = [e for e in events if not e.broke]
    broke = [e for e in events if e.broke]
    pierces = [e.pierce for e in events]

    # Hold/break rate is a property of the LEVEL — every visit counts.
    # Win rate and expectancy are properties of the TRADE, so under the rejection
    # model only visits that actually produced a signal are eligible; averaging a
    # no-signal visit in as a zero would silently dilute the edge toward nothing.
    trig = [e for e in events if e.triggered]
    wins = [e for e in trig if e.r_outcome > 0]
    ind = independent_counts(events)

    return {
        "n": len(events),
        "n_visits": ind["visits"],
        "n_days": ind["days"],
        "n_triggered": len(trig),
        "hold_rate": len(held) / len(events),
        "break_rate": len(broke) / len(events),
        "pierce_median": stats.median(pierces),
        "pierce_p75": _pct(pierces, 0.75),
        "pierce_p90": _pct(pierces, 0.90),
        "pierce_max": max(pierces),
        "win_rate": (len(wins) / len(trig)) if trig else 0.0,
        "expectancy_r": stats.mean([e.r_outcome for e in trig]) if trig else 0.0,
        "median_r": stats.median([e.r_outcome for e in trig]) if trig else 0.0,
        "mfe_r_median": stats.median([e.mfe_r for e in trig]) if trig else 0.0,
        "stopped_rate": (sum(1 for e in trig if e.stopped) / len(trig)) if trig else 0.0,
        "efficiency_median": stats.median([e.efficiency for e in events]),
        "efficiency_median_on_hold": stats.median([e.efficiency for e in held]) if held else 0.0,
        "efficiency_median_on_break": stats.median([e.efficiency for e in broke]) if broke else 0.0,
    }


def summarise_by(events: list[TouchEvent], key) -> dict[str, dict]:
    buckets: dict[str, list[TouchEvent]] = defaultdict(list)
    for e in events:
        buckets[key(e)].append(e)
    return {k: summarise(v) for k, v in sorted(buckets.items())}


# ---------------------------------------------------------------------- report

def _fmt(x: float, d: int = 1) -> str:
    return f"{x:,.{d}f}"


def _confidence(s: dict) -> str:
    if s["n"] >= 10 and s["expectancy_r"] > 0.3:
        return "HIGH"
    if s["n"] >= 6 and s["expectancy_r"] > 0.0:
        return "MEDIUM"
    if s["n"] < 6:
        return "LOW (thin sample)"
    return "NEGATIVE EDGE"


def build_report(symbol: str, sym_id: int, days: int, spot: float,
                 per_level: list[tuple[Level, list[TouchEvent], dict, float]],
                 all_events: list[TouchEvent], cfg: dict) -> str:
    L: list[str] = []
    a = L.append
    a(f"# Level Reaction Report — {symbol}")
    a("")
    a(f"Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}Z · "
      f"symbolId {sym_id} · last {days} days · spot {_fmt(spot, 2)}")
    a("")
    a(f"Pivot strength {cfg['strength']} · cluster tol {cfg['tol_pct']*100:.3f}% · "
      f"touch band ±{_fmt(cfg['band'], 2)} pts · break buffer {_fmt(cfg['break_buffer'], 2)} pts "
      f"(needs 2 consecutive closes) · horizon {cfg['horizon']}m · target cap {cfg['target_r']:.0f}R")
    a("")
    a("> **Data note.** cTrader `volume` is TICK volume (quote updates), not traded contracts,")
    a("> and these are Pepperstone CFD/spread-bet prices, not exchange prints. `efficiency` is")
    a("> an absorption **proxy**, not a measurement. Every R figure below is a path-dependent")
    a("> replay with the stop checked before the target, so it is not inflated by trades that")
    a("> would have been stopped out first.")
    a("")

    o = summarise(all_events)
    a("## Overall — every level, every touch")
    a("")
    if not o["n"]:
        a("No qualifying touch events in the window.")
        return "\n".join(L)
    a(f"- **{o['n']} touch events** across {len([p for p in per_level if p[2]['n']])} levels")
    a(f"- Level held (no 2-close break): **{o['hold_rate']*100:.0f}%**")
    a(f"- Wick-through beyond the level: median {_fmt(o['pierce_median'],2)} · "
      f"p75 {_fmt(o['pierce_p75'],2)} · p90 {_fmt(o['pierce_p90'],2)} · max {_fmt(o['pierce_max'],2)}")
    a(f"- Trading it mechanically: win rate {o['win_rate']*100:.0f}%, "
      f"stopped {o['stopped_rate']*100:.0f}%, **expectancy {o['expectancy_r']:+.2f}R**")
    a("")
    if o["expectancy_r"] <= 0:
        a("⚠️ **Across all levels blindly, this is not an edge.** That is the expected result —")
        a("the edge is in level selection and day context, not in fading every level. Use the")
        a("breakdowns below to find where it is actually positive.")
        a("")

    a("### Absorption proxy — tick efficiency")
    a("")
    a("Net price progress per 1,000 ticks during the touch. Lower = more churn for less")
    a("movement = the signature you are looking for when wicks are being absorbed.")
    a("")
    a("| Outcome | Median efficiency |")
    a("|---|---|")
    a(f"| Touches that HELD | {o['efficiency_median_on_hold']:.3f} |")
    a(f"| Touches that BROKE | {o['efficiency_median_on_break']:.3f} |")
    a(f"| All touches | {o['efficiency_median']:.3f} |")
    a("")
    lo_e, hi_e = o["efficiency_median_on_hold"], o["efficiency_median_on_break"]
    if lo_e and hi_e:
        if lo_e < hi_e * 0.85:
            a(f"**Signal present.** Holds churn {(1-lo_e/hi_e)*100:.0f}% more per unit of progress "
              f"than breaks — low tick-efficiency at your level is evidence for absorption.")
        elif hi_e < lo_e * 0.85:
            a("**Inverted.** Breaks show *lower* efficiency than holds here — tick efficiency is "
              "not a usable absorption tell on this instrument/window. Do not lean on it.")
        else:
            a("**No separation.** Holds and breaks churn about the same. Tick efficiency adds "
              "nothing here; you need the DOM layer for a real absorption read.")
    a("")

    a("## Conditioned on day bias")
    a("")
    a("Day bias = price vs that day's opening print at the moment of the touch. A resistance")
    a("test on a bearish day is your short setup; a support test on a bullish day is your long.")
    a("")
    a("| Day bias | Side | n | Held | Win rate | Expectancy | p90 pierce |")
    a("|---|---|---|---|---|---|---|")
    for bias in ("bearish", "flat", "bullish"):
        for side in ("resistance", "support"):
            sub = [e for e in all_events if e.day_bias == bias and e.side == side]
            if len(sub) < 3:
                continue
            s = summarise(sub)
            aligned = " ←" if (bias == "bearish" and side == "resistance") or \
                              (bias == "bullish" and side == "support") else ""
            a(f"| {bias} | {side}{aligned} | {s['n']} | {s['hold_rate']*100:.0f}% | "
              f"{s['win_rate']*100:.0f}% | {s['expectancy_r']:+.2f}R | {_fmt(s['pierce_p90'],2)} |")
    a("")
    a("Rows marked ← are the with-bias setups: the ones your strategy actually takes.")
    a("")

    a("## Conditioned on session (UTC)")
    a("")
    a("| Session | n | Held | Win rate | Expectancy | p90 pierce |")
    a("|---|---|---|---|---|---|")
    for sess, s in summarise_by(all_events, lambda e: e.session).items():
        if s["n"] < 3:
            continue
        a(f"| {sess} | {s['n']} | {s['hold_rate']*100:.0f}% | {s['win_rate']*100:.0f}% | "
          f"{s['expectancy_r']:+.2f}R | {_fmt(s['pierce_p90'],2)} |")
    a("")

    a("## Per level")
    a("")
    a("Sorted by distance from spot — the ones near the top are the ones in play.")
    a("")
    a("| Level | Kind | H1 pivots | Touches | Held | Win rate | Expectancy | Stop (pts) | Dist from spot |")
    a("|---|---|---|---|---|---|---|---|---|")
    ranked = sorted(per_level, key=lambda t: abs(t[0].price - spot))
    for lv, evs, s, sd in ranked:
        if s["n"] == 0:
            continue
        a(f"| **{_fmt(lv.price,2)}** | {lv.kind} | {lv.touch_count} | {s['n']} | "
          f"{s['hold_rate']*100:.0f}% | {s['win_rate']*100:.0f}% | {s['expectancy_r']:+.2f}R | "
          f"{_fmt(sd,2)} | {_fmt(lv.price - spot,2)} |")
    a("")

    a("## Trade guidance — nearest levels")
    a("")
    shown = 0
    for lv, evs, s, sd in ranked:
        if s["n"] < (1 if cfg.get("explicit") else 4) or shown >= 5:
            continue
        shown += 1
        a(f"### {_fmt(lv.price,2)} ({lv.kind})")
        a("")
        a(f"- Sample: {s['n']} touches, held {s['hold_rate']*100:.0f}% — confidence **{_confidence(s)}**")
        a(f"- Stop: **{_fmt(sd,2)} pts beyond {_fmt(lv.price,2)}** "
          f"(p90 wick-through on non-break visits; deepest ever {_fmt(s['pierce_max'],2)})")
        a(f"- Mechanical result: win rate {s['win_rate']*100:.0f}%, "
          f"stopped {s['stopped_rate']*100:.0f}%, expectancy **{s['expectancy_r']:+.2f}R**, "
          f"median best-case {s['mfe_r_median']:.1f}R")
        if s["expectancy_r"] <= 0:
            a("- ⚠️ **Negative expectancy on this level.** Fading it blind has lost money over this")
            a("  window. Either wait for the break-and-retest, or require the DOM to show real")
            a("  resting size before taking it.")
        a("")
        recent = sorted(evs, key=lambda e: e.start_ts, reverse=True)[:6]
        a("| When (UTC) | Side | Day | Pierce | Closed thru | Broke | Result |")
        a("|---|---|---|---|---|---|---|")
        for e in recent:
            res = f"{e.r_outcome:+.1f}R" + (" (stopped)" if e.stopped else "")
            a(f"| {iso(e.start_ts)} | {e.side} | {e.day_bias} | {_fmt(e.pierce,2)} | "
              f"{_fmt(e.close_beyond,2)} | {'yes' if e.broke else 'no'} | {res} |")
        a("")

    a("---")
    a("")
    a("**How to use this live.** When price returns to one of these levels you already know")
    a("how often it has held, how deep the wicks normally go (so your stop is sized from")
    a("evidence rather than nerve), and what fading it has actually paid. What this cannot")
    a("tell you is whether sellers are stacked there *right now* — that is what the DOM")
    a("recorder in `src/dom_recorder.py` adds once you register a cTrader Open API app.")
    return "\n".join(L)


# ------------------------------------------------------------------------ main

def resolve_symbol(cli: CTraderClient, name: str) -> tuple[int, str]:
    """Resolve a symbol name to (id, name), deterministically.

    This account carries SIX instruments matching "XAUUSD", quoting two different
    underlyings, and only two of them are enabled:

        id    name            enabled   price     what it is
        41    XAUUSD          True      4046.31   spot CFD  ← the tradeable one
        241   XAUUSD_SB       False     4046.31   spread bet (disabled here)
        1711  XAUUSD_SBE      False     4046.32   spread bet, EUR
        2552  XAUUSD-F        True      4102.80   FORWARD, 25 Jul–20 Nov
        2586  XAUUSD-F_SB     False     4102.80   forward, spread bet
        5961  XAUUSD-F_SBE    False        0.00   not quoted

    Three things must not happen:

    1. Picking whichever matched first — that is undefined ordering, and it
       returned 41 while gold_context hardcoded 241.
    2. Preferring a name suffix. An earlier version preferred `_SB` on the
       assumption from ctrader-mcp-integration-guide.md that enabled symbols
       carry that suffix. On this CFD account `_SB` is *disabled* and the plain
       name is the live one, so the guess picked a dead instrument.
    3. Selecting an "-F" variant. Those track the FORWARD price (4102.80 vs spot
       4046.31 — which is the ~57pt basis this code measures and subtracts), so
       feeding one in would double-count the basis.

    So the broker's own `enabled` flag decides, not a naming convention. Exact
    base match only, which already excludes "-F".
    """
    data = cli.symbols()
    syms = data.get("symbols") or data.get("symbol") or []
    want = name.upper().replace("_SB", "").strip()

    def base_of(nm: str) -> str:
        return nm.upper().removesuffix("_SBE").removesuffix("_SB")

    exact, partial = [], []
    for s in syms:
        nm = (s.get("symbolName") or s.get("name") or "").upper()
        if base_of(nm) == want:
            exact.append(s)
        elif want in nm:
            partial.append(s)

    def rank(s) -> tuple:
        nm = (s.get("symbolName") or "").upper()
        # enabled first — the authoritative signal, and account-type agnostic.
        # Then the plain name, then anything else.
        return (0 if s.get("enabled") else 1, 0 if nm == want else 1, nm)

    pick = sorted(exact, key=rank) if exact else sorted(partial, key=rank)
    if not pick:
        avail = sorted({(s.get("symbolName") or "") for s in syms})[:40]
        raise CTraderError(f"symbol {name!r} not found. Sample of available: {avail}")

    s = pick[0]
    chosen = s.get("symbolName") or name
    if not s.get("enabled", True):
        print(f"WARNING: {chosen} is DISABLED on this account — no enabled instrument "
              f"matched {name!r}. Prices may be stale or unavailable.", file=sys.stderr)
    if "-F" in chosen.upper():
        # Only reachable if the user explicitly asked for an -F symbol.
        print(f"WARNING: {chosen} tracks the FUTURES price, not spot. The basis "
              f"logic assumes spot and will double-count. Use the spot symbol.",
              file=sys.stderr)
    return int(s.get("symbolId") or s.get("id")), chosen


def main() -> int:
    p = argparse.ArgumentParser(description="Level reaction statistics from cTrader data")
    p.add_argument("--symbol", default="UK100", help="e.g. UK100, XAUUSD, US30")
    p.add_argument("--days", type=int, default=15, help="lookback in calendar days")
    p.add_argument("--strength", type=int, default=3, help="H1 pivot fractal strength")
    p.add_argument("--tol-pct", type=float, default=0.0006, help="level cluster tolerance")
    p.add_argument("--band-pct", type=float, default=0.00035,
                   help="how close counts as touching, as a fraction of price")
    p.add_argument("--break-pct", type=float, default=0.00025,
                   help="close beyond by this much, twice running, = broken")
    p.add_argument("--horizon", type=int, default=60, help="minutes to replay each trade over")
    p.add_argument("--target-r", type=float, default=3.0, help="cap the replay at this R")
    p.add_argument("--min-touches", type=int, default=2, help="min H1 pivots to keep a level")
    p.add_argument("--level", action="append", type=float,
                   help="analyse THIS price level instead of auto-detecting "
                        "(repeatable, e.g. --level 4049.44)")
    p.add_argument("--near", type=float, default=None,
                   help="only report levels within --near-pct of this price")
    p.add_argument("--near-pct", type=float, default=0.01)
    p.add_argument("--out", default=None, help="output .md path")
    p.add_argument("--json", action="store_true", help="also write raw events as JSON")
    args = p.parse_args()

    cli = CTraderClient()
    sym_id, sym_name = resolve_symbol(cli, args.symbol)
    print(f"[1/5] {sym_name} → symbolId {sym_id}", file=sys.stderr)

    end = now_ms()
    start = end - args.days * DAY_MS

    h1 = cli.trendbars(sym_id, "H_1", start, end)
    print(f"[2/5] H1 bars: {len(h1)}", file=sys.stderr)
    if len(h1) < 20:
        raise CTraderError(f"only {len(h1)} H1 bars returned — widen --days")

    if args.level:
        # Analyse the levels YOU drew, not the ones the detector found. Any H1
        # pivots sitting within clustering tolerance are attached, so the report
        # also tells you whether your hand-drawn line matches a real swing.
        all_pivots = find_pivots(h1, args.strength)
        levels = []
        for px in args.level:
            near = [pv for pv in all_pivots if abs(pv.price - px) <= px * args.tol_pct]
            kinds = {pv.kind for pv in near}
            kind = ("both" if len(kinds) > 1 else
                    "resistance" if "high" in kinds else
                    "support" if "low" in kinds else "user-drawn (no H1 pivot)")
            levels.append(Level(price=px, kind=kind, pivots=near))
    else:
        levels = significant_levels(h1, args.strength, args.tol_pct, args.min_touches)
    spot_raw = cli.spot([sym_id])
    quotes = spot_raw.get("spotPrices") or spot_raw.get("prices") or []
    if quotes:
        q = quotes[0]
        bid = (q.get("bid") or 0) / 10 ** 5
        ask = (q.get("ask") or 0) / 10 ** 5
        spot = (bid + ask) / 2 if bid and ask else (bid or ask)
    else:
        spot = h1[-1]["c"]

    if args.near is not None and not args.level:
        lo, hi = args.near * (1 - args.near_pct), args.near * (1 + args.near_pct)
        levels = [lv for lv in levels if lo <= lv.price <= hi]
    print(f"[3/5] levels: {len(levels)} (spot {spot:,.2f})", file=sys.stderr)
    if not levels:
        raise CTraderError("no levels survived filtering — loosen --min-touches or --strength")

    print(f"[4/5] fetching M1 ({args.days}d, this is the slow part)…", file=sys.stderr)
    m1 = cli.trendbars(sym_id, "M_1", start, end, verbose=True)
    print(f"[4/5] M1 bars: {len(m1)}", file=sys.stderr)
    if len(m1) < 500:
        raise CTraderError(f"only {len(m1)} M1 bars — cannot build reliable statistics")

    day_opens: dict[str, float] = {}
    for b in m1:
        k = datetime.fromtimestamp(b["ts"] / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
        if k not in day_opens:
            day_opens[k] = b["o"]

    band = spot * args.band_pct
    brk = spot * args.break_pct
    # A stop can never be tighter than the touch band (you'd be stopped by noise
    # inside your own level) nor wider than 6x it (that is not "just beyond the
    # deepest wick" any more, it's a different trade).
    stop_floor, stop_cap = band, band * 6

    per_level, all_events = [], []
    for lv in levels:
        evs = find_touch_events(m1, lv.price, band, break_buffer=brk, day_opens=day_opens)
        if evs:
            sd = derive_stop_distance(evs, stop_floor, stop_cap)
            replay(evs, m1, sd, args.horizon, args.target_r)
        else:
            sd = stop_floor
        per_level.append((lv, evs, summarise(evs), sd))
        all_events.extend(evs)
    print(f"[5/5] touch events: {len(all_events)}", file=sys.stderr)

    cfg = {"strength": args.strength, "tol_pct": args.tol_pct, "band": band,
           "break_buffer": brk, "horizon": args.horizon, "target_r": args.target_r,
           "explicit": bool(args.level)}
    report = build_report(sym_name, sym_id, args.days, spot, per_level, all_events, cfg)

    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = args.out or os.path.join(here, "reports", f"{sym_name.replace('/','-')}-levels.md")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        f.write(report + "\n")
    print(f"\nWrote {out}", file=sys.stderr)

    if args.json:
        jout = out.rsplit(".", 1)[0] + "-events.json"
        with open(jout, "w") as f:
            json.dump([asdict(e) for e in all_events], f, indent=1)
        print(f"Wrote {jout}", file=sys.stderr)

    print(report)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except CTraderError as e:
        print(f"FAILED: {e}", file=sys.stderr)
        sys.exit(1)
