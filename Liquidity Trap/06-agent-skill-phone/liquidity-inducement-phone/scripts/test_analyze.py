#!/usr/bin/env python3
"""
test_analyze.py — regression suite for the liquidity analyzer.

Every check here corresponds to a defect found during live use, where the
analyzer returned a read that was wrong or unusable. They exist so those
defects cannot come back silently in a later session.

Run:  python3 test_analyze.py        (no token, no network — synthetic bars)
"""

import sys
from datetime import datetime, timezone, timedelta

import analyze as A

BASE = datetime(2026, 7, 27, tzinfo=timezone.utc)
_passed = 0
_failed = []


def bar(i, o, h, l, c, v=100):
    return {"time": BASE + timedelta(minutes=5 * i), "open": o, "high": h,
            "low": l, "close": c, "volume": v}


def daily(low, close):
    """20 closed daily bars + today's forming bar."""
    out = [{"time": BASE - timedelta(days=n), "open": 4050, "high": 4100,
            "low": 4020, "close": 4060, "volume": 1000}
           for n in range(20, 0, -1)]
    out.append({"time": BASE, "open": 4089, "high": 4106, "low": low,
                "close": close, "volume": 900})
    return out


def check(name, cond):
    global _passed
    if cond:
        _passed += 1
        print(f"PASS  {name}")
    else:
        _failed.append(name)
        print(f"FAIL  {name}")


# ── session context: NY open moves with DST ─────────────────────────────────
# Was computed by hand with the winter offset, so a move after the NY open was
# reported as pre-open drift.
check("session: summer NY open is 13:30 UTC",
      A._session(datetime(2026, 7, 27, 13, 57, tzinfo=timezone.utc))
      ["ny_open_utc"] == "13:30")
check("session: winter NY open is 14:30 UTC",
      A._session(datetime(2026, 1, 27, 13, 57, tzinfo=timezone.utc))
      ["ny_open_utc"] == "14:30")
check("session: NY lunch closes the trade window",
      A._session(datetime(2026, 7, 27, 16, 22, tzinfo=timezone.utc))
      ["in_trade_window"] is False)

# ── sweep detection: must see a sweep older than the current bar ────────────
# The reference extreme used to include the candidate bars, so only a sweep on
# the newest bar could ever fire.
_ex = ([bar(i, 4090, 4092, 4088, 4090) for i in range(30)]
       + [bar(30, 4089, 4090, 4075.47, 4089),
          bar(31, 4089, 4091, 4088.5, 4090),
          bar(32, 4090, 4092, 4089, 4091),
          bar(33, 4091, 4093, 4090, 4092)])
_d = daily(4075.47, 4092)
_o = A.analyze("X", "M_5", d1=_d, h1=_d, ex=_ex, live=(4092, 4093))
check("sweep: a 3-bar-old sweep is detected",
      _o["recent_sweep"] and _o["recent_sweep"]["bars_ago"] == 3)
check("sweep: live reclaim keeps still_valid true",
      _o["recent_sweep"]["still_valid"] is True)
check("sweep: names the pool it consumed",
      _o["recent_sweep"]["pool_taken"] is not None)

# ── sweep invalidation: a dead trap must not read like a live one ───────────
_ex2 = _ex[:31] + [bar(31, 4089, 4090, 4086, 4087),
                   bar(32, 4087, 4088, 4080, 4081),
                   bar(33, 4081, 4082, 4074.5, 4074.8)]
_d2 = daily(4074.5, 4074.8)
_o2 = A.analyze("X", "M_5", d1=_d2, h1=_d2, ex=_ex2, live=(4074.7, 4074.9))
check("sweep: price back through the level -> still_valid false",
      _o2["recent_sweep"]["still_valid"] is False)
check("sweep: invalidated trap is labelled in the note",
      "INVALIDATED" in _o2["recent_sweep"]["note"])

_d3 = daily(4088, 4090)
check("sweep: flat data produces no false positive",
      A.analyze("X", "M_5", d1=_d3, h1=_d3,
                ex=[bar(i, 4090, 4092, 4088, 4090) for i in range(34)],
                live=(4090, 4091))["recent_sweep"] is None)

# ── liquidity block: a shallow stab must stay workable ─────────────────────
_exd = ([bar(i, 4078, 4080, 4075.92, 4078) for i in range(30)]
        + [bar(30, 4077, 4078, 4075.47, 4078),
           bar(31, 4078, 4082, 4077, 4081),
           bar(32, 4081, 4086, 4080, 4085)])
_d4 = daily(4075.47, 4083)
_o4 = A.analyze("X", "M_5", d1=_d4, h1=_d4, ex=_exd, live=(4085, 4086))
_sw = _o4["recent_sweep"]
check("LB: a sub-noise-width block is flagged thin", _sw["thin_lb"] is True)
check("LB: entry_zone is widened past the raw block",
      (_sw["entry_zone"][1] - _sw["entry_zone"][0]) > _sw["lb_width"])
check("LB: stop stays behind the true extreme, not the widened zone",
      _sw["stop_beyond"] < _sw["lb_zone"][0])
# A sell-side sweep is a LONG: the extreme is the low, so the entry band must
# widen upward and never dip below the extreme (which is where the stop lives).
check("LB: long entry_zone never crosses below the swept extreme",
      _sw["entry_zone"][0] >= _sw["lb_zone"][0])
check("LB: long entry_zone sits entirely above the stop",
      _sw["entry_zone"][0] > _sw["stop_beyond"])

# Mirror case: a buy-side sweep is a SHORT — the extreme is the high, so the
# band must widen downward and stay under the stop.
_exu = ([bar(i, 4086, 4088.05, 4084, 4086) for i in range(30)]
        + [bar(30, 4087, 4093.93, 4086, 4087.5),   # stabs high, CLOSES back below
           bar(31, 4087, 4088, 4085, 4086),
           bar(32, 4086, 4087, 4085, 4086)])
_d7 = daily(4065.33, 4086)
_o7 = A.analyze("X", "M_5", d1=_d7, h1=_d7, ex=_exu, live=(4086, 4086.1))
_sw7 = _o7["recent_sweep"]
check("LB: buy-side sweep detected", _sw7 is not None and _sw7["side"] == "buy_side")
if _sw7:
    check("LB: short entry_zone never crosses above the swept extreme",
          _sw7["entry_zone"][1] <= _sw7["lb_zone"][1])
    check("LB: short entry_zone sits entirely below the stop",
          _sw7["entry_zone"][1] < _sw7["stop_beyond"])

# ── targets: spent liquidity must not be offered as a draw ─────────────────
# Two pools, deliberately on opposite sides of the day's extreme:
#   ~4069  formed EARLY (bars 3 and 8), then taken out by the 4065.33 spike
#   ~4076  formed LATE  (bar 16), after the spike, and never traded through
# The early one must read swept, the late one must not — which is the whole
# reason "swept" is measured from each pool's last touch rather than naively
# against the session low.
_LOWS = [4072, 4071, 4070, 4069, 4070, 4072, 4073, 4070, 4069, 4070,
         4072, 4074, 4065.33, 4074, 4078, 4077, 4076, 4077, 4079, 4080,
         4081, 4080]
_exs = [bar(i, l + 2, l + 4, l, l + 3) for i, l in enumerate(_LOWS)]
_d5 = daily(4065.33, 4082.48)
_o5 = A.analyze("X", "M_5", d1=_d5, h1=_d5, ex=_exs, live=(4082.4, 4082.6))
check("targets: a pool price traded through is marked swept",
      any(p["swept"] for p in _o5["pools_below"]))
check("targets: the draw is never a swept pool",
      _o5["draw_down"]["swept"] is False)
check("targets: session_low counts as a confirmed day-frame pool",
      all(p["confirmed"] for p in _o5["pools_below"]
          if p["name"] == "session_low"))
check("targets: a single-touch swing level is not confirmed",
      all(not p["confirmed"] for p in _o5["pools_below"]
          if p["kind"] == "equal_level" and p["touches"] < 2))

# The discriminating case: the SAME run must mark the pre-extreme pool swept
# and the post-extreme pool live. A naive check against the session low would
# wrongly condemn both.
_eq = [p for p in _o5["pools_below"] if p["kind"] == "equal_level"]
check("targets: pre-extreme pool is swept",
      any(p["swept"] for p in _eq))
check("targets: pool re-formed after the extreme stays unswept",
      any(not p["swept"] for p in _eq))

# ── end-to-end ─────────────────────────────────────────────────────────────
_d6, _h6, _ex6, _live = A._synthetic()
_o6 = A.analyze("XAUUSD", "M_5", d1=_d6, h1=_h6, ex=_ex6, live=_live)
check("end-to-end: dry-run analysis returns no error", "error" not in _o6)
for _f in ("session", "daily_bias", "range", "volume", "pools_above",
           "pools_below", "draw_up", "draw_down", "no_mans_land"):
    check(f"end-to-end: output contains '{_f}'", _f in _o6)


# ── cluster chaining must not produce a pool wider than a real stop shelf ───
# Single-linkage joined on distance-to-previous only, so levels each just
# inside tol chained into a 17-point "23-touch pool" on gold — a range, not a
# pool. Span is now capped at 2x tol.
_chain = [(BASE, 4080 + 2.0 * i) for i in range(12)]   # 2.0 apart, tol ~2.5
_cl = A._cluster(_chain, 2.5)
check("cluster: chained levels do not form one giant pool",
      max(c["high"] - c["low"] for c in _cl) <= 2.5 * 2 + 1e-6)
check("cluster: chaining splits into several pools", len(_cl) > 1)
# Genuinely tight levels must still cluster together.
_tight = [(BASE, 4080 + 0.2 * i) for i in range(6)]
check("cluster: tight levels still form a single pool",
      len(A._cluster(_tight, 2.5)) == 1)

# ── pool_taken must see pools the sweep bar cleared, not just its reference ──
_exp = ([bar(i, 4086, 4088.05, 4084, 4086) for i in range(20)]
        + [bar(20 + i, 4090, 4092.0, 4089, 4091) for i in range(6)]  # shelf ~4092
        + [bar(26, 4091, 4099.0, 4090, 4089.5),   # clears the shelf, closes back
           bar(27, 4089, 4090, 4087, 4088),
           bar(28, 4088, 4089, 4086, 4087)])
_d8 = daily(4065.33, 4087)
_o8 = A.analyze("X", "M_5", d1=_d8, h1=_d8, ex=_exp, live=(4087, 4087.1))
_sw8 = _o8["recent_sweep"]
check("pool_taken: buy-side sweep detected", _sw8 is not None)
if _sw8:
    check("pool_taken: reports the pool the bar cleared",
          _sw8["pool_taken"] is not None)
    check("pool_taken: counts how many pools were cleared",
          _sw8.get("pools_cleared", 0) >= 1)


# ── management path: the structure a trade travels through ─────────────────
# too_close pools are useless as targets but are exactly the trail/partial
# checkpoints (reference 05), so they must be surfaced in order.
check("path: draw_up path contains only pools nearer than the draw",
      all(p["dist"] < _o5["draw_up"]["dist"] for p in _o5["path_up"])
      if _o5.get("draw_up") else True)
check("path: draw_down path contains only pools nearer than the draw",
      all(p["dist"] < _o5["draw_down"]["dist"] for p in _o5["path_down"])
      if _o5.get("draw_down") else True)
check("path: entries carry a zone and touch count",
      all("zone" in p and "touches" in p
          for p in _o5["path_up"] + _o5["path_down"]))
check("end-to-end: output contains 'path_up'", "path_up" in _o6)
check("end-to-end: output contains 'path_down'", "path_down" in _o6)
# A swept level is a block, never a trail checkpoint.
_allpaths = _o5["path_up"] + _o5["path_down"]
_swept_zones = [p["zone"] for p in _o5["pools_below"] + _o5["pools_above"]
                if p["swept"]]
check("path: never includes a swept pool",
      all(p["zone"] not in _swept_zones for p in _allpaths))


print(f"\n{_passed} passed, {len(_failed)} failed")
if _failed:
    for _n in _failed:
        print("  failed:", _n)
    sys.exit(1)
