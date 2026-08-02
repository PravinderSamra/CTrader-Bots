#!/usr/bin/env python3
"""
GOLD CONTEXT — real futures volume, real options positioning, mapped onto XAUUSD.

Why this exists
---------------
For UK100 the honest answer was "there is no free order flow". Gold is different,
and materially better:

  * COMEX gold futures (GC) publish **real traded contract volume**, free, hourly.
    That gives a genuine volume profile — actual POC / HVN / LVN — rather than the
    tick-count fiction you get from a CFD feed.
  * Gold has a large, liquid options market. Open interest by strike shows where
    size is committed, and dealer gamma shows where price is likely to be pinned
    or accelerated. Free from CBOE, greeks included.
  * CFTC publishes weekly positioning for COMEX gold — who is long, who is short.

None of these are a Bookmap heatmap. They are something arguably more useful for a
level-based day trader: they say *where size actually sits* on the instrument that
leads spot, rather than where a broker's LP is quoting right now.

The mapping problem — read this, it is the whole game
-----------------------------------------------------
Everything above is priced in something other than XAUUSD spot, and the offsets
are neither small nor constant.

**Futures basis.** GC trades at a premium to spot. Measured on this account over
30 days to 2026-08-01, the daily median basis ran:

    07-03  +12.74   →   07-28  +0.07      (August contract converging to expiry)
    07-29  +58.27                          ← ROLL to December
    07-31  +56.62                          (begins decaying again)

A GC volume node at 4100 was spot 4100 on 28 July and spot 4042 on 29 July. Using
a fixed offset — or none — puts every futures-derived level ~58 points wrong on
gold immediately after a roll. So the basis is **measured live** from overlapping
hourly bars, every run, and the roll is flagged when it jumps.

**GLD ratio.** GLD holds a decaying quantity of gold per share (expense ratio), so
spot/GLD drifts upward over time — it is ~10.89 as of 2026-08-01, not the 10.0 you
will see hardcoded in older code. At GLD 371.54 that is the difference between
mapping a strike to 3715 and to 4046: 331 points. Also measured live.

Usage
-----
    python3 "Gala Heatmap/src/gold_context.py"
    python3 "Gala Heatmap/src/gold_context.py" --days 30 --bins 90
    python3 "Gala Heatmap/src/gold_context.py" --levels 4020,4046,4103   # cross-reference
"""

from __future__ import annotations

import argparse
import json
import math
import os
import statistics as stats
import sys
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ctrader_http import CTraderClient, CTraderError, now_ms  # noqa: E402

UA = {"User-Agent": "Mozilla/5.0 (compatible; gala-heatmap/1.0)"}
# Fallback only. This account carries six XAUUSD variants; two track the FORWARD
# price and four are disabled, so the symbol is resolved at runtime by the
# broker's `enabled` flag (level_stats.resolve_symbol). 41 is the enabled spot
# CFD — this constant is used only if resolution fails entirely.
XAUUSD_SYMBOL_ID = 41
DAY_MS = 86_400_000


def range_days(rng: str) -> int:
    """'60d' / '1mo' / '3mo' → days, so the basis window can be made to cover it."""
    rng = (rng or "").strip().lower()
    try:
        if rng.endswith("d"):
            return int(rng[:-1])
        if rng.endswith("mo"):
            return int(rng[:-2]) * 31
        if rng.endswith("y"):
            return int(rng[:-1]) * 366
    except ValueError:
        pass
    return 30


def _get_json(url: str, timeout: int = 30, retries: int = 3) -> dict:
    """Yahoo and CBOE both drop connections intermittently — a bare
    'Connection reset by peer' silently removed the whole options layer from one
    run during testing. Retry with backoff rather than losing a scoring input to
    a transient blip."""
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode())
        except Exception as e:                      # noqa: BLE001 - retry anything transient
            last = e
            if attempt < retries - 1:
                time.sleep(1.5 * (attempt + 1))
    raise last


# ------------------------------------------------------------------- yahoo

def yahoo_ohlcv(symbol: str, rng: str = "1mo", interval: str = "1h") -> list[dict]:
    """Hourly/daily OHLCV with REAL contract volume for futures symbols."""
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/"
           f"{urllib.parse.quote(symbol)}?range={rng}&interval={interval}")
    d = _get_json(url)
    res = d["chart"]["result"][0]
    q = res["indicators"]["quote"][0]
    out = []
    for i, ts in enumerate(res["timestamp"]):
        c = q["close"][i]
        if c is None:
            continue
        out.append({
            "ts": int(ts) * 1000,
            "o": q["open"][i] or c, "h": q["high"][i] or c,
            "l": q["low"][i] or c, "c": c,
            "v": q["volume"][i] or 0,
        })
    return out


# -------------------------------------------------------------------- basis

def compute_basis(fut: list[dict], spot: list[dict]) -> dict:
    """Measure the GC-minus-spot basis from overlapping hours, and spot the roll."""
    fmap = {b["ts"] // 3_600_000: b["c"] for b in fut}
    smap = {b["ts"] // 3_600_000: b["c"] for b in spot}
    common = sorted(set(fmap) & set(smap))
    if len(common) < 24:
        raise CTraderError(f"only {len(common)} overlapping hours — cannot measure basis")

    diffs = [fmap[h] - smap[h] for h in common]
    by_day: dict[str, list[float]] = defaultdict(list)
    for h in common:
        day = datetime.fromtimestamp(h * 3600, tz=timezone.utc).strftime("%Y-%m-%d")
        by_day[day].append(fmap[h] - smap[h])
    daily = [(d, stats.median(v)) for d, v in sorted(by_day.items())]

    # A roll shows up as a step change between consecutive days that dwarfs the
    # normal day-to-day drift (convergence is smooth, roughly a point a day).
    roll = None
    for i in range(1, len(daily)):
        jump = daily[i][1] - daily[i - 1][1]
        if abs(jump) > 15:
            roll = {"date": daily[i][0], "jump": jump,
                    "before": daily[i - 1][1], "after": daily[i][1]}

    recent = [fmap[h] - smap[h] for h in common[-24:]]
    return {
        "current": stats.median(recent),
        "median_30d": stats.median(diffs),
        "stdev_recent": stats.pstdev(recent) if len(recent) > 1 else 0.0,
        "daily": daily,
        "daily_map": dict(daily),
        "roll": roll,
        "n_hours": len(common),
    }


def futures_to_spot(fut: list[dict], basis: dict) -> list[dict]:
    """Convert futures bars to spot terms using **that day's** basis.

    A single current basis is wrong the moment the lookback spans a contract roll:
    on 2026-07-29 the GC basis stepped +58 points in one day, so pre-roll bars
    converted at the post-roll basis land ~58 points below where they belong —
    which on gold is the difference between a valid level and a blown stop.
    """
    dmap = basis["daily_map"]
    days = sorted(dmap)
    out = []
    uncovered = 0
    for b in fut:
        day = datetime.fromtimestamp(b["ts"] / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
        if day in dmap:
            off = dmap[day]
        elif days:
            # Nearest measured day — futures trade hours spot doesn't, and vice versa.
            nearest = min(days, key=lambda d: abs(
                (datetime.strptime(d, "%Y-%m-%d") - datetime.strptime(day, "%Y-%m-%d")).days))
            gap = abs((datetime.strptime(nearest, "%Y-%m-%d")
                       - datetime.strptime(day, "%Y-%m-%d")).days)
            # A weekend or holiday leaves a 2-4 day hole where futures traded and
            # XAUUSD didn't. Borrowing the adjacent day's basis costs ~1 pt/day of
            # drift, which beats discarding the volume. Beyond that it is a guess.
            roll_date = (basis.get("roll") or {}).get("date")
            crosses_roll = bool(roll_date) and (
                (day < roll_date) != (nearest < roll_date))
            if gap > 4 or crosses_roll:
                # Across a roll the basis steps ~58 points; borrowing would place
                # this bar's volume at a price it never traded at.
                uncovered += 1
                continue
            off = dmap[nearest]
        else:
            off = basis["current"]
        out.append({**{k: b[k] - off for k in ("o", "h", "l", "c")},
                    "ts": b["ts"], "v": b["v"], "basis": off})
    if uncovered:
        print(f"      note: dropped {uncovered:,} futures bars outside the measured "
              f"basis window ({days[0]} → {days[-1]}) — extend the basis lookback "
              f"to use them", file=sys.stderr)
    return out


def calibrate_ratio(etf: list[dict], spot: list[dict]) -> dict:
    """spot / ETF, measured from overlapping hours rather than assumed.

    Also returns how PRECISE that mapping is, which matters more than it looks.
    GLD and XAUUSD are sampled from different venues with different closing
    instants and GLD trades at an intraday premium/discount to NAV, so the ratio
    wobbles. Measured 2026-08-01: stdev 0.0206, which at GLD ~371 is **±7.7 spot
    points** — against a strike spacing of only 10.9 points.

    That means an individual GLD strike CANNOT be pinned to a single spot price.
    Treat mapped strikes as bands, not levels. By contrast the futures basis has
    stdev ~1.2 points, so volume-profile levels are ~6x more precisely placed.
    """
    emap = {b["ts"] // 3_600_000: b["c"] for b in etf}
    smap = {b["ts"] // 3_600_000: b["c"] for b in spot}
    common = sorted(set(emap) & set(smap))
    if len(common) < 12:
        return {"ratio": None, "n": len(common)}
    ratios = [smap[h] / emap[h] for h in common if emap[h]]
    recent = ratios[-24:] or ratios
    ratio = stats.median(recent)
    sd = stats.pstdev(ratios) if len(ratios) > 1 else 0.0
    etf_px = etf[-1]["c"] if etf else 0.0
    return {"ratio": ratio, "median_all": stats.median(ratios),
            "n": len(common), "spread": max(recent) - min(recent),
            "ratio_stdev": sd,
            # 1-sigma uncertainty on any strike→spot mapping, in spot points.
            "spot_uncertainty": sd * etf_px,
            "strike_spacing_spot": ratio}


# ----------------------------------------------------------- volume profile

def volume_profile(bars: list[dict], bins: int = 80) -> dict:
    """Real volume profile from GC contract volume.

    Each bar's volume is spread evenly across its high–low range. That is the
    standard OHLCV approximation — it cannot know where inside the bar the volume
    actually traded, so HVN/LVN placement is good to roughly a bar's range, not
    to the tick.
    """
    bars = [b for b in bars if b["v"] > 0 and b["h"] > b["l"]]
    if not bars:
        raise CTraderError("no volume-bearing bars")
    pmin = min(b["l"] for b in bars)
    pmax = max(b["h"] for b in bars)
    step = (pmax - pmin) / bins
    if step <= 0:
        raise CTraderError("degenerate price range")

    hist = [0.0] * bins

    def idx(p: float) -> int:
        return max(0, min(bins - 1, int((p - pmin) / step)))

    for b in bars:
        lo, hi = idx(b["l"]), idx(b["h"])
        span = hi - lo + 1
        share = b["v"] / span
        for i in range(lo, hi + 1):
            hist[i] += share

    total = sum(hist)
    poc_i = max(range(bins), key=lambda i: hist[i])

    # Value area: expand out from the POC until 70% of volume is enclosed.
    lo_i = hi_i = poc_i
    acc = hist[poc_i]
    while acc < total * 0.70 and (lo_i > 0 or hi_i < bins - 1):
        down = hist[lo_i - 1] if lo_i > 0 else -1
        up = hist[hi_i + 1] if hi_i < bins - 1 else -1
        if up >= down:
            hi_i += 1
            acc += hist[hi_i]
        else:
            lo_i -= 1
            acc += hist[lo_i]

    def price_of(i: int) -> float:
        return pmin + (i + 0.5) * step

    # Local extrema in the distribution, ignoring the noise floor.
    peak = max(hist)
    hvn, lvn = [], []
    for i in range(1, bins - 1):
        if hist[i] > hist[i - 1] and hist[i] > hist[i + 1] and hist[i] > peak * 0.35:
            hvn.append((price_of(i), hist[i]))
        if hist[i] < hist[i - 1] and hist[i] < hist[i + 1] and hist[i] < peak * 0.18 \
                and lo_i <= i <= hi_i:
            lvn.append((price_of(i), hist[i]))

    return {
        "poc": price_of(poc_i), "vah": price_of(hi_i), "val": price_of(lo_i),
        "pmin": pmin, "pmax": pmax, "step": step, "total": total,
        "n_bars": len(bars),
        "hist": [(price_of(i), hist[i]) for i in range(bins)],
        "hvn": sorted(hvn, key=lambda x: -x[1])[:8],
        "lvn": sorted(lvn, key=lambda x: x[1])[:8],
    }


# ------------------------------------------------------------------ options

def cboe_chain(ticker: str = "GLD") -> dict:
    """Full delayed option chain from CBOE — OI, volume, IV and greeks, free."""
    url = f"https://cdn.cboe.com/api/global/delayed_quotes/options/{ticker}.json"
    d = _get_json(url)
    return d["data"]


def parse_occ(sym: str, root: str) -> tuple[str, str, float] | None:
    """GLD260731C00205000 → ('2026-07-31', 'C', 205.0)"""
    body = sym[len(root):] if sym.startswith(root) else sym
    if len(body) < 15:
        return None
    ymd, cp, strike = body[:6], body[6], body[7:]
    try:
        exp = f"20{ymd[:2]}-{ymd[2:4]}-{ymd[4:6]}"
        return exp, cp, int(strike) / 1000.0
    except ValueError:
        return None


def options_levels(data: dict, ratio: float, root: str = "GLD",
                   max_exp: int = 3, band_pct: float = 0.10) -> dict:
    """Open-interest walls and dealer gamma by strike, translated to spot prices.

    GEX convention matches GEX&OI/agent_skill: dealers are taken long call gamma
    and short put gamma, so net = call GEX − put GEX. Positive net means dealers
    hedge against the move (pinning); negative means they hedge with it (trending).
    """
    und = data.get("close") or data.get("current_price") or 0.0
    opts = data.get("options") or []
    if not und:
        raise CTraderError("CBOE response missing underlying price")

    lo, hi = und * (1 - band_pct), und * (1 + band_pct)
    exps: dict[str, dict] = defaultdict(lambda: {"call_oi": 0.0, "put_oi": 0.0})
    by_strike: dict[float, dict] = defaultdict(
        lambda: {"call_oi": 0.0, "put_oi": 0.0, "call_gex": 0.0, "put_gex": 0.0,
                 "call_vol": 0.0, "put_vol": 0.0})

    all_exps = set()
    for o in opts:
        p = parse_occ(o.get("option", ""), root)
        if not p:
            continue
        exp, cp, k = p
        all_exps.add(exp)

    # CBOE keeps the just-expired series in the file; including it would put dead
    # open interest on the board as if it were live positioning.
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    keep = sorted(e for e in all_exps if e >= today)[:max_exp]
    if not keep:
        keep = sorted(all_exps)[-max_exp:]
    for o in opts:
        p = parse_occ(o.get("option", ""), root)
        if not p:
            continue
        exp, cp, k = p
        if exp not in keep or not (lo <= k <= hi):
            continue
        oi = float(o.get("open_interest") or 0)
        vol = float(o.get("volume") or 0)
        gam = float(o.get("gamma") or 0)
        if oi <= 0 and vol <= 0:
            continue
        # Dollar gamma per 1% move: gamma × OI × 100 shares × S² × 0.01
        gex = gam * oi * 100 * und * und * 0.01
        s = by_strike[k]
        if cp == "C":
            s["call_oi"] += oi; s["call_gex"] += gex; s["call_vol"] += vol
            exps[exp]["call_oi"] += oi
        else:
            s["put_oi"] += oi; s["put_gex"] += gex; s["put_vol"] += vol
            exps[exp]["put_oi"] += oi

    rows = []
    for k, s in sorted(by_strike.items()):
        net_gex = s["call_gex"] - s["put_gex"]
        rows.append({
            "strike": k, "spot": k * ratio,
            "call_oi": s["call_oi"], "put_oi": s["put_oi"],
            "total_oi": s["call_oi"] + s["put_oi"],
            "net_gex": net_gex,
            "call_vol": s["call_vol"], "put_vol": s["put_vol"],
        })

    net_total = sum(r["net_gex"] for r in rows)

    # Gamma flip: where cumulative net GEX crosses zero walking up the strikes.
    flip = None
    cum = 0.0
    for r in rows:
        prev = cum
        cum += r["net_gex"]
        if prev < 0 <= cum or prev > 0 >= cum:
            flip = r["spot"]

    return {
        "underlying": und, "underlying_spot": und * ratio, "ratio": ratio,
        "expiries": keep, "rows": rows, "net_gex": net_total, "gamma_flip": flip,
        "top_call_oi": sorted(rows, key=lambda r: -r["call_oi"])[:6],
        "top_put_oi": sorted(rows, key=lambda r: -r["put_oi"])[:6],
        # Raw OI clusters at far-out round strikes, which is irrelevant to a day
        # trade. These are the strikes price can actually reach in a session.
        "near": sorted([r for r in rows if abs(r["strike"] - und) <= und * 0.025],
                       key=lambda r: r["strike"]),
    }


# ---------------------------------------------------------------------- COT

def cftc_gold(limit: int = 4) -> list[dict]:
    """CFTC disaggregated COT for COMEX gold. Weekly, free, no key."""
    where = urllib.parse.quote("market_and_exchange_names like 'GOLD - COMMODITY EXCHANGE%'")
    url = (f"https://publicreporting.cftc.gov/resource/72hh-3qpy.json"
           f"?$where={where}&$order=report_date_as_yyyy_mm_dd DESC&$limit={limit}")
    url = url.replace(" ", "%20")
    rows = _get_json(url)
    # The Socrata column names for this dataset are not internally consistent —
    # some carry an `_all` suffix and some don't, and the swap columns have a
    # double underscore. Try candidates rather than assuming one convention.
    FIELDS = {
        "oi":         ("open_interest_all", "open_interest"),
        "mm_long":    ("m_money_positions_long_all", "m_money_positions_long"),
        "mm_short":   ("m_money_positions_short_all", "m_money_positions_short"),
        "prod_long":  ("prod_merc_positions_long_all", "prod_merc_positions_long"),
        "prod_short": ("prod_merc_positions_short_all", "prod_merc_positions_short"),
        "swap_long":  ("swap_positions_long_all", "swap__positions_long_all"),
        "swap_short": ("swap__positions_short_all", "swap_positions_short_all"),
    }
    out = []
    for r in rows:
        rec = {"date": (r.get("report_date_as_yyyy_mm_dd") or "")[:10]}
        for key, candidates in FIELDS.items():
            val = 0
            for c in candidates:
                if r.get(c) not in (None, ""):
                    try:
                        val = int(float(r[c]))
                        break
                    except (TypeError, ValueError):
                        pass
            rec[key] = val
        out.append(rec)
    return out


# ------------------------------------------------------------------- report

def _f(x: float, d: int = 2) -> str:
    return f"{x:,.{d}f}"


def build_report(spot_px: float, basis: dict, vp: dict, opts: dict | None,
                 cot: list[dict], user_levels: list[float], days: int) -> str:
    L: list[str] = []
    a = L.append
    b_now = basis["current"]

    def to_spot(fut_price: float) -> float:
        return fut_price - b_now

    a("# Gold Context — futures volume, options positioning, spot-mapped")
    a("")
    a(f"Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}Z · "
      f"XAUUSD spot {_f(spot_px)} · lookback {days}d")
    a("")

    # ---- basis
    a("## 1. Basis — how futures prices map to your chart")
    a("")
    a(f"- **Current basis: {b_now:+.2f} points** (GC front month − XAUUSD spot), "
      f"median of the last 24 overlapping hours")
    a(f"- 30-day median {basis['median_30d']:+.2f} · recent stdev {basis['stdev_recent']:.2f} · "
      f"{basis['n_hours']} aligned hours")
    a("")
    a(f"To convert a futures price yourself right now: `spot = futures − {b_now:.2f}`.")
    a("")
    if basis["roll"]:
        r = basis["roll"]
        a(f"> ⚠️ **Contract roll detected on {r['date']}** — the basis jumped "
          f"{r['jump']:+.2f} points ({r['before']:+.2f} → {r['after']:+.2f}) as GC rolled")
        a("> to the next active contract.")
        a(">")
        a("> **The volume profile below already accounts for this.** Each futures bar is")
        a("> converted to spot using *that day's* measured basis, not the current one, so")
        a("> pre-roll and post-roll volume land at the correct spot prices. Applying a single")
        a(f"> offset across the roll would misplace a month of volume by ~{abs(r['jump']):.0f} points.")
        a("")
    a("Recent daily basis:")
    a("")
    a("| Date | Median basis |")
    a("|---|---|")
    for d, v in basis["daily"][-8:]:
        a(f"| {d} | {v:+.2f} |")
    a("")

    # ---- volume profile
    a("## 2. Real volume profile — COMEX gold futures")
    a("")
    a("This is **actual traded contract volume**, not the tick-count that CFD feeds")
    a("report. It is the single biggest data upgrade gold has over an index CFD.")
    a("")
    a(f"Built from **{vp.get('n_bars', 0):,} volume-bearing bars** "
      f"({vp.get('total', 0):,.0f} contracts).")
    a("")
    a("All prices are **XAUUSD spot**, converted per bar at that day's measured basis.")
    a("")
    a("| Node | XAUUSD spot | Meaning |")
    a("|---|---|---|")
    a(f"| POC | **{_f(vp['poc'])}** | most volume traded here — magnet, and a level that grinds |")
    a(f"| VAH | **{_f(vp['vah'])}** | top of the 70% value area |")
    a(f"| VAL | **{_f(vp['val'])}** | bottom of the 70% value area |")
    a("")
    if vp["hvn"]:
        a("**High volume nodes** — price slows and chops here; good targets, poor breakout levels.")
        a("")
        a("| XAUUSD spot | Relative volume |")
        a("|---|---|")
        peak = max(v for _, v in vp["hvn"])
        for p, v in vp["hvn"]:
            bar = "█" * max(1, int(round(v / peak * 14)))
            a(f"| **{_f(p)}** | {bar} |")
        a("")
    if vp["lvn"]:
        a("**Low volume nodes** — price moves through these fast. A pivot sitting on an LVN")
        a("gives a cleaner run once it goes; one sitting on an HVN will grind.")
        a("")
        a("| XAUUSD spot |")
        a("|---|")
        for p, _v in vp["lvn"]:
            a(f"| **{_f(p)}** |")
        a("")

    # ---- options
    if opts:
        a("## 3. Options positioning — where size is committed")
        a("")
        a(f"Source: CBOE delayed GLD chain, {len(opts['expiries'])} nearest expiries "
          f"({', '.join(opts['expiries'])}). GLD {_f(opts['underlying'])} × "
          f"**{opts['ratio']:.3f}** (measured, not assumed) → spot {_f(opts['underlying_spot'])}.")
        a("")
        net = opts["net_gex"]
        a(f"- **Net dealer gamma: {net/1e6:+,.1f}M per 1% move**")
        if net > 0:
            a("  - Positive → dealers hedge *against* the move. Expect **pinning and mean")
            a("    reversion**: levels hold more often, breakouts fail more often. This is a")
            a("    good regime for fading your pivots.")
        else:
            a("  - Negative → dealers hedge *with* the move. Expect **acceleration**: levels")
            a("    break more easily and moves extend. Fading pivots is more dangerous here;")
            a("    favour the break-and-retest.")
        if opts["gamma_flip"]:
            a(f"- **Gamma flip ≈ {_f(opts['gamma_flip'])} spot** — regime changes across this level")
        a("")
        if opts.get("near"):
            a("### Strikes in intraday reach (±2.5% of spot)")
            a("")
            a("These are the ones that matter for a day trade. Larger OI = more hedging flow")
            a("anchored there = a stronger pin.")
            a("")
            a("| XAUUSD spot | Call OI | Put OI | Net gamma | |")
            a("|---|---|---|---|---|")
            pk = max((r["total_oi"] for r in opts["near"]), default=1) or 1
            for r in opts["near"]:
                bar = "█" * max(0, int(round(r["total_oi"] / pk * 12)))
                near_spot = " ← spot" if abs(r["spot"] - spot_px) <= 12 else ""
                a(f"| **{_f(r['spot'])}** | {r['call_oi']:,.0f} | {r['put_oi']:,.0f} | "
                  f"{r['net_gex']/1e6:+.1f}M | {bar}{near_spot} |")
            a("")

        a("**Largest open interest overall — call side** (overhead supply, incl. far strikes):")
        a("")
        a("| Strike | XAUUSD spot | Call OI |")
        a("|---|---|---|")
        for r in opts["top_call_oi"]:
            a(f"| {_f(r['strike'],1)} | **{_f(r['spot'])}** | {r['call_oi']:,.0f} |")
        a("")
        a("**Largest open interest — put side** (downside support / pinning magnets):")
        a("")
        a("| Strike | XAUUSD spot | Put OI |")
        a("|---|---|---|")
        for r in opts["top_put_oi"]:
            a(f"| {_f(r['strike'],1)} | **{_f(r['spot'])}** | {r['put_oi']:,.0f} |")
        a("")
        a("> GLD options are a **proxy**. They track gold closely but they are not options on")
        a("> COMEX gold futures (OG), whose strikes sit directly on the futures price. CME")
        a("> publishes OG open interest by strike daily — it was not reachable from this")
        a("> environment (403), but it is worth pulling locally if you lean on this layer.")
        a("")

    # ---- COT
    if cot:
        a("## 4. Positioning — CFTC Commitment of Traders")
        a("")
        a("Weekly, Tuesday snapshot published Friday. Macro context, not entry timing.")
        a("")
        a("| Week | Open interest | Managed money net | Producers net | Swap dealers net |")
        a("|---|---|---|---|---|")
        for c in cot:
            mm = c["mm_long"] - c["mm_short"]
            pr = c["prod_long"] - c["prod_short"]
            sw = c["swap_long"] - c["swap_short"]
            a(f"| {c['date']} | {c['oi']:,} | {mm:+,} | {pr:+,} | {sw:+,} |")
        a("")
        a("Producers and swap dealers are structurally short (they hedge physical and")
        a("dealer flow); managed money is the speculative side. The reading that matters is")
        a("the *change* and the extremes, not the sign.")
        a("")
        latest = cot[0]
        mm_net = latest["mm_long"] - latest["mm_short"]
        if len(cot) > 1:
            prev = cot[1]["mm_long"] - cot[1]["mm_short"]
            delta = mm_net - prev
            direction = "added to longs" if delta > 0 else "cut longs"
            a(f"Managed money is net **{mm_net:+,}** and {direction} by {abs(delta):,} "
              f"week over week.")
            if latest["mm_short"] and mm_net / max(1, latest["mm_short"]) > 6:
                a("Long/short ratio is stretched — crowded long. Fuel for a downside flush if")
                a("a support level fails, and a reason to respect resistance.")
        a("")

    # ---- confluence
    if user_levels:
        a("## 5. Your levels, cross-referenced")
        a("")
        a("A level with a volume node *and* committed options size behind it has a reason to")
        a("hold beyond the fact you drew a line there.")
        a("")
        a("| Your level | Nearest volume node | Nearest significant OI | Read |")
        a("|---|---|---|---|")
        nodes = [(vp["poc"], "POC")] + [(p, "HVN") for p, _v in vp["hvn"]] \
                + [(p, "LVN") for p, _v in vp["lvn"]]
        # Only strikes carrying real size count as confluence — otherwise the
        # "nearest strike" is always within a few points and means nothing.
        oi_rows = opts["rows"] if opts else []
        if oi_rows:
            cut = sorted((r["total_oi"] for r in oi_rows), reverse=True)
            cut = cut[max(0, len(cut) // 4)] if cut else 0
            big = [r for r in oi_rows if r["total_oi"] >= cut]
        else:
            big = []
        for lv in sorted(user_levels):
            nn = min(nodes, key=lambda n: abs(n[0] - lv)) if nodes else None
            oo = min(big, key=lambda r: abs(r["spot"] - lv)) if big else None
            near_node = nn and abs(nn[0] - lv) <= 8
            near_oi = oo and abs(oo["spot"] - lv) <= 15
            nd = f"{_f(nn[0])} ({nn[1]}, {nn[0]-lv:+.1f})" if nn else "—"
            od = (f"{_f(oo['spot'])} ({oo['total_oi']:,.0f} OI, {oo['spot']-lv:+.1f})"
                  if oo else "—")
            if near_node and near_oi:
                read = "**strong confluence**"
            elif near_node:
                read = f"volume confluence ({nn[1]})"
            elif near_oi:
                read = "options confluence"
            else:
                read = "price structure only"
            a(f"| **{_f(lv)}** | {nd} | {od} | {read} |")
        a("")

    a("---")
    a("")
    a("## How to use this with the level engine")
    a("")
    a("`level_stats.py` tells you how a level has behaved. This tells you *why* it might.")
    a("A pivot that also sits on the futures POC, inside a large call-OI strike, with")
    a("dealers long gamma, is a level with a reason to hold — and the historical hold rate")
    a("should confirm it. When the two disagree, trust the history and shrink the size.")
    a("")
    a("**Tiering.** Futures volume profile is real traded volume (Tier 1 for *where volume")
    a("happened*, though not aggressor-classified, so it is not delta). Options OI is real")
    a("committed size on a proxy instrument. COT is Tier 3 macro context. None of it is a")
    a("live order book.")
    return "\n".join(L)


# ---------------------------------------------------------------------- main

def main() -> int:
    p = argparse.ArgumentParser(description="Gold futures/options context mapped to XAUUSD")
    p.add_argument("--days", type=int, default=30, help="lookback for basis and volume profile")
    p.add_argument("--bins", type=int, default=120, help="volume profile resolution")
    p.add_argument("--vp-interval", default="5m",
                   help="futures bar interval for the volume profile. Hourly bars "
                        "smear an hour of gold (20+ pts) evenly across their range, "
                        "which is useless for a 1-2 minute strategy. 5m over 60d "
                        "gives ~13,700 volume-bearing bars against ~490 hourly.")
    p.add_argument("--vp-range", default="30d",
                   help="lookback for the volume profile. 30d keeps the window "
                        "comparable to the rest of the analysis; the gain here is "
                        "RESOLUTION (5m vs 1h), not a longer history. 60d spans a "
                        "235-pt range on gold and blurs what is relevant intraday.")
    p.add_argument("--futures", default="GC=F", help="Yahoo futures symbol")
    p.add_argument("--etf", default="GLD", help="options proxy ticker")
    p.add_argument("--levels", default="", help="comma-separated XAUUSD levels to cross-reference")
    p.add_argument("--no-options", action="store_true")
    p.add_argument("--out", default=None)
    args = p.parse_args()

    # The basis is measured from XAUUSD H1 vs hourly GC, and every profile bar
    # must fall inside that window or its volume lands at the wrong spot price.
    # So the basis lookback is driven by the PROFILE range, not by --days.
    basis_days = max(args.days, range_days(args.vp_range) + 2)
    rng = "1mo" if basis_days <= 30 else "3mo" if basis_days <= 90 else "6mo"

    print(f"[1/6] XAUUSD spot + H1 from cTrader ({basis_days}d for basis coverage)…",
          file=sys.stderr)
    cli = CTraderClient()
    end = now_ms()
    try:
        from level_stats import resolve_symbol
        sym_id, sym_name = resolve_symbol(cli, "XAUUSD")
    except Exception:
        sym_id, sym_name = XAUUSD_SYMBOL_ID, "XAUUSD_SB"
    print(f"      using {sym_name} (id {sym_id})", file=sys.stderr)
    spot_bars = cli.trendbars(sym_id, "H_1", end - basis_days * DAY_MS, end)
    sp = cli.spot([sym_id])
    q = (sp.get("prices") or sp.get("spotPrices") or [{}])[0]
    spot_px = ((q.get("bid", 0) + q.get("ask", 0)) / 2) / 1e5 or spot_bars[-1]["c"]
    print(f"      spot {spot_px:,.2f}, {len(spot_bars)} H1 bars", file=sys.stderr)

    # Two separate pulls, deliberately. The basis needs HOURLY bars because it is
    # measured against XAUUSD H1; the profile wants the finest bars available.
    print(f"[2/6] {args.futures} hourly (for basis) + {args.vp_interval} (for profile)…",
          file=sys.stderr)
    fut = yahoo_ohlcv(args.futures, rng, "1h")
    print(f"      hourly: {len(fut)} bars, volume {sum(b['v'] for b in fut):,}", file=sys.stderr)
    try:
        fut_fine = yahoo_ohlcv(args.futures, args.vp_range, args.vp_interval)
        print(f"      {args.vp_interval}: {len(fut_fine)} bars, "
              f"volume {sum(b['v'] for b in fut_fine):,}", file=sys.stderr)
    except Exception as e:
        print(f"      {args.vp_interval} unavailable ({str(e)[:60]}) — falling back to hourly",
              file=sys.stderr)
        fut_fine = fut

    print("[3/6] measuring basis…", file=sys.stderr)
    basis = compute_basis(fut, spot_bars)
    print(f"      current {basis['current']:+.2f}, roll={'yes' if basis['roll'] else 'no'}",
          file=sys.stderr)

    print("[4/6] volume profile (per-bar basis conversion)…", file=sys.stderr)
    fut_spot = futures_to_spot(fut_fine, basis)
    vp = volume_profile(fut_spot, args.bins)
    print(f"      POC {vp['poc']:,.2f} spot · VA {vp['val']:,.2f}–{vp['vah']:,.2f}",
          file=sys.stderr)

    opts = None
    if not args.no_options:
        try:
            print(f"[5/6] {args.etf} option chain from CBOE…", file=sys.stderr)
            etf_bars = yahoo_ohlcv(args.etf, rng, "1h")
            cal = calibrate_ratio(etf_bars, spot_bars)
            ratio = cal["ratio"] or (spot_px / (cboe_chain(args.etf).get("close") or 1))
            print(f"      spot/{args.etf} ratio {ratio:.4f} (from {cal['n']} hours)",
                  file=sys.stderr)
            opts = options_levels(cboe_chain(args.etf), ratio, root=args.etf)
            print(f"      {len(opts['rows'])} strikes, net GEX {opts['net_gex']/1e6:+,.1f}M",
                  file=sys.stderr)
        except Exception as e:
            print(f"      options layer unavailable: {str(e)[:120]}", file=sys.stderr)

    cot = []
    try:
        print("[6/6] CFTC COT…", file=sys.stderr)
        cot = cftc_gold()
        print(f"      latest {cot[0]['date']}", file=sys.stderr)
    except Exception as e:
        print(f"      COT unavailable: {str(e)[:120]}", file=sys.stderr)

    levels = [float(x) for x in args.levels.split(",") if x.strip()]
    report = build_report(spot_px, basis, vp, opts, cot, levels, args.days)

    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = args.out or os.path.join(here, "reports", "XAUUSD-gold-context.md")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        f.write(report + "\n")
    print(f"\nWrote {out}", file=sys.stderr)
    print(report)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except CTraderError as e:
        print(f"FAILED: {e}", file=sys.stderr)
        sys.exit(1)
