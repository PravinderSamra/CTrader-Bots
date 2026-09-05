#!/usr/bin/env python3
"""
gexbot.py — client for the GEXBot API (api.gexbot.com).

RESEARCH / OPTIONAL. The brief does not depend on this: if the token is absent
or the service is down, every caller gets None and the CBOE pipeline carries on
unchanged. That is deliberate — a paid feed becoming a hard dependency would
turn an outage into a missing scan.

What it adds that we cannot compute ourselves
---------------------------------------------
1. **Volume-weighted GEX, signed.** The single thing the CBOE pipeline cannot
   do honestly: volume has no side, so weighting walls by it stacks an
   assumption on an assumption (recorded when the idea was rejected). GEXBot
   sees the trades and can sign them. Measured on 2026-09-04's close the two
   lenses disagree completely near spot — 29,525 carried 83,936 by volume
   against essentially nothing by open interest, and it is where price pinned.
2. **Per-strike priors** — five prior samples of GEX at every strike, i.e.
   walls building and unwinding through the session. That is exactly the
   question `research/live-walls/` was set up to estimate.
3. **NQ futures-space levels** (`NQ_NDX`), which are the NDX levels plus a
   constant. Removes the stale-cash-roll-forward workaround entirely.
4. **0DTE / 1DTE splits** with the volume lens applied.

Known caveats — read before trusting a number
---------------------------------------------
- `zero_gamma` equalled `spot` EXACTLY on the 2026-09-04 snapshot for both
  gex_full and gex_zero, though not for gex_one. That is either genuine pinning
  into a Friday close or a fallback. **UNVERIFIED — check during RTH before
  using it as a flip.**
- The order of the `priors` array (newest-first vs oldest-first) is not
  documented and cannot be established from a frozen weekend snapshot. **Sample
  twice during RTH and compare before reading a trend from it.**
- Units on `gex_vol` / `gex_oi` are unstated and are NOT our $bn. Treat them as
  a relative scale within one response; never mix them with our figures.
- Their major_neg is the most-negative strike ANYWHERE, not "below spot". Our
  put wall is "most put gamma below spot, put-dominated". Different questions —
  do not compare them as though they were the same level (that confusion is
  exactly what produced D4).
"""
import json, os, ssl, time, urllib.error, urllib.request

BASE = "https://api.gexbot.com"
TICKERS = {"ndx": "NDX", "nq": "NQ_NDX", "qqq": "QQQ", "spx": "SPX"}
CATEGORIES = ("gex_full", "gex_zero", "gex_one")

_CACHE = {}
_TTL = 90
_last_error = None


def last_error():
    return _last_error


def available():
    return bool(os.environ.get("GEX_BOT_API_TOKEN"))


def _get(path, timeout=25):
    """GET with the token in the header. The token is never logged or returned."""
    global _last_error
    tok = os.environ.get("GEX_BOT_API_TOKEN")
    if not tok:
        _last_error = "GEX_BOT_API_TOKEN not set"
        return None
    url = f"{BASE}/{path.lstrip('/')}"
    req = urllib.request.Request(url, headers={
        "Authorization": tok,
        "Accept": "application/json",
        "User-Agent": "nas100-daily-brief/1.0",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout,
                                    context=ssl.create_default_context()) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        _last_error = f"HTTP {e.code} on /{path.lstrip('/')}"
    except Exception as e:
        _last_error = f"{type(e).__name__} on /{path.lstrip('/')}"
    return None


def fetch(ticker="NDX", category="gex_full", cache=True):
    """Raw payload for one ticker/category, memoised for 90s."""
    key = (ticker, category)
    if cache and key in _CACHE:
        ts, payload = _CACHE[key]
        if time.time() - ts < _TTL:
            return payload
    d = _get(f"v2/{ticker}/classic/{category}")
    if d and "strikes" in d:
        _CACHE[key] = (time.time(), d)
    return d


def levels(ticker="NDX", category="gex_full", offset=0.0):
    """The headline levels, optionally shifted into another price space.

    `offset` is added to every price, so pass (CFD_price - gexbot_spot) to get
    levels on the trader's chart. Nothing here is renamed to match our own
    vocabulary — `major_neg` is THEIR definition (most negative anywhere), not
    our put wall, and calling it one would repeat D4.
    """
    d = fetch(ticker, category)
    if not d or "strikes" not in d:
        return None
    o = offset
    return {
        "source": "gexbot", "ticker": d.get("ticker", ticker),
        "category": category,
        "timestamp": d.get("timestamp"),
        "age_min": (round((time.time() - d["timestamp"]) / 60, 1)
                    if d.get("timestamp") else None),
        "spot": round(d["spot"] + o, 1),
        "zero_gamma": round(d["zero_gamma"] + o, 1),
        "zero_gamma_equals_spot": d["zero_gamma"] == d["spot"],
        "major_pos_vol": round(d["major_pos_vol"] + o, 1),
        "major_pos_oi": round(d["major_pos_oi"] + o, 1),
        "major_neg_vol": round(d["major_neg_vol"] + o, 1),
        "major_neg_oi": round(d["major_neg_oi"] + o, 1),
        "sum_gex_vol": d.get("sum_gex_vol"),
        "sum_gex_oi": d.get("sum_gex_oi"),
        "delta_risk_reversal": d.get("delta_risk_reversal"),
        "min_dte": d.get("min_dte"), "sec_min_dte": d.get("sec_min_dte"),
        "n_strikes": len(d["strikes"]),
    }


def ladder(ticker="NDX", category="gex_full", offset=0.0, span=None):
    """Per-strike rows: price, gex by volume, gex by OI, and the prior samples.

    Rows are [strike, gex_vol, gex_oi, priors[]]. `priors` ordering is NOT
    documented — see the module docstring before reading a trend from it.
    """
    d = fetch(ticker, category)
    if not d or "strikes" not in d:
        return None
    spot = d["spot"]
    out = []
    for r in d["strikes"]:
        if span is not None and abs(r[0] - spot) > span:
            continue
        out.append({
            "price": round(r[0] + offset, 1),
            "gex_vol": r[1], "gex_oi": r[2],
            "priors": r[3] if len(r) > 3 else [],
        })
    out.sort(key=lambda x: -x["price"])
    return out


def wall_drift(ticker="NDX", category="gex_full"):
    """`max_priors` — where the dominant strike has been over recent samples.

    Answers "is the biggest wall moving, and which way" without us having to
    store our own history. Ordering carries the same caveat as `priors`.
    """
    d = fetch(ticker, category)
    if not d or not d.get("max_priors"):
        return None
    mp = d["max_priors"]
    strikes = [r[0] for r in mp if isinstance(r, (list, tuple)) and r]
    return {
        "samples": mp,
        "distinct_strikes": sorted(set(strikes)),
        "moved": len(set(strikes)) > 1,
        "range_pts": (round(max(strikes) - min(strikes), 1) if strikes else None),
    }


if __name__ == "__main__":
    import sys
    if not available():
        print("GEX_BOT_API_TOKEN not set"); sys.exit(1)
    tick = sys.argv[1] if len(sys.argv) > 1 else "NDX"
    for cat in CATEGORIES:
        lv = levels(tick, cat)
        if not lv:
            print(f"{cat}: unavailable — {last_error()}"); continue
        print(f"\n{tick} / {cat}   spot {lv['spot']:,.1f}   "
              f"age {lv['age_min']}min   strikes {lv['n_strikes']}")
        print(f"   zero_gamma {lv['zero_gamma']:,.1f}"
              f"{'  <-- EQUALS SPOT, unverified' if lv['zero_gamma_equals_spot'] else ''}")
        print(f"   major +  vol {lv['major_pos_vol']:,.1f}   oi {lv['major_pos_oi']:,.1f}")
        print(f"   major -  vol {lv['major_neg_vol']:,.1f}   oi {lv['major_neg_oi']:,.1f}")
        print(f"   sum vol {lv['sum_gex_vol']:,.0f}   sum oi {lv['sum_gex_oi']:,.0f}"
              f"   dRR {lv['delta_risk_reversal']}")
        wd = wall_drift(tick, cat)
        if wd:
            print(f"   dominant strike over {len(wd['samples'])} samples: "
                  f"{wd['distinct_strikes']}  "
                  f"{'MOVED ' + str(wd['range_pts']) + 'pts' if wd['moved'] else 'stable'}")
