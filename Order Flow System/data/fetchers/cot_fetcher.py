"""
CFTC Commitment of Traders (COT) Fetcher — Tier 3 Positioning Data

Source: CFTC Socrata public API (free, no API key required).
Updated: every Friday ~15:30 ET covering the prior Tuesday's positions.
Coverage: forex, commodities, equity index futures.

Data tier: 3 — macro positioning context, NOT real-time order flow.
  Use for: weekly bias, extreme positioning alerts, trend confirmation.
  Do NOT use for: entry timing, intraday decisions.

Trader categories:
  Managed Money     = hedge funds / CTAs (best speculative smart-money proxy)
  Dealer            = banks / primary dealers (often contrarian, fade extremes)
  Asset Manager     = pension funds / long-only (slow, trend-following)
  Non-commercial    = legacy label for speculators (forex/legacy dataset)
  Producer/Merchant = physical market hedgers (commodities, inverse proxy)

COT dataset IDs (CFTC Socrata):
  yw9f-hn96  — Legacy (forex: EUR, GBP, JPY, CHF, CAD, AUD)
  72hh-3qpy  — Disaggregated (commodities: Gold, WTI Oil, Silver, Copper)
  gpe5-46if  — Financial Futures (E-mini S&P, NASDAQ, Dow, T-Bonds)
"""

import urllib.request
import urllib.parse
import json
from datetime import datetime, timezone
from typing import Optional, List, Dict

BASE_URL = "https://publicreporting.cftc.gov/resource"

# ── Market registry ───────────────────────────────────────────────────────────
# Maps our symbol names to the exact CFTC market name + dataset

COT_MARKETS: Dict[str, dict] = {
    # Forex (Legacy dataset)
    "EURUSD": {
        "cftc_name": "EURO FX - CHICAGO MERCANTILE EXCHANGE",
        "dataset":   "yw9f-hn96",
        "schema":    "legacy",
        "description": "EUR/USD futures positioning",
    },
    "GBPUSD": {
        "cftc_name": "BRITISH POUND - CHICAGO MERCANTILE EXCHANGE",
        "dataset":   "yw9f-hn96",
        "schema":    "legacy",
        "description": "GBP/USD futures positioning",
    },
    "USDJPY": {
        "cftc_name": "JAPANESE YEN - CHICAGO MERCANTILE EXCHANGE",
        "dataset":   "yw9f-hn96",
        "schema":    "legacy",
        "description": "JPY/USD futures positioning (inverted — short JPY = long USDJPY)",
    },
    "USDCHF": {
        "cftc_name": "SWISS FRANC - CHICAGO MERCANTILE EXCHANGE",
        "dataset":   "yw9f-hn96",
        "schema":    "legacy",
        "description": "CHF/USD futures positioning",
    },
    "AUDUSD": {
        "cftc_name": "AUSTRALIAN DOLLAR - CHICAGO MERCANTILE EXCHANGE",
        "dataset":   "yw9f-hn96",
        "schema":    "legacy",
        "description": "AUD/USD futures positioning",
    },
    "USDCAD": {
        "cftc_name": "CANADIAN DOLLAR - CHICAGO MERCANTILE EXCHANGE",
        "dataset":   "yw9f-hn96",
        "schema":    "legacy",
        "description": "CAD/USD futures positioning",
    },

    # Commodities (Disaggregated dataset)
    "XAUUSD": {
        "cftc_name": "GOLD - COMMODITY EXCHANGE INC.",
        "dataset":   "72hh-3qpy",
        "schema":    "disaggregated",
        "description": "Gold futures positioning",
    },
    "XAGUSD": {
        "cftc_name": "SILVER - COMMODITY EXCHANGE INC.",
        "dataset":   "72hh-3qpy",
        "schema":    "disaggregated",
        "description": "Silver futures positioning",
    },
    "USOIL": {
        "cftc_name": "WTI-PHYSICAL - NEW YORK MERCANTILE EXCHANGE",
        "dataset":   "72hh-3qpy",
        "schema":    "disaggregated",
        "description": "WTI crude oil futures positioning",
    },
    "UKOIL": {
        "cftc_name": "BRENT CRUDE OIL LAST DAY - ICE FUTURES EUROPE",
        "dataset":   "72hh-3qpy",
        "schema":    "disaggregated",
        "description": "Brent crude oil futures positioning",
    },
    "COPPER": {
        "cftc_name": "COPPER- #1 - COMMODITY EXCHANGE INC.",
        "dataset":   "72hh-3qpy",
        "schema":    "disaggregated",
        "description": "Copper futures positioning",
    },

    # Equity index futures (Financial dataset)
    "SPX": {
        "cftc_name": "E-MINI S&P 500 - CHICAGO MERCANTILE EXCHANGE",
        "dataset":   "gpe5-46if",
        "schema":    "financial",
        "description": "E-mini S&P 500 futures positioning",
    },
    "NDX": {
        "cftc_name": "E-MINI NASDAQ-100 - CHICAGO MERCANTILE EXCHANGE",
        "dataset":   "gpe5-46if",
        "schema":    "financial",
        "description": "E-mini NASDAQ-100 futures positioning",
    },
    "DOW": {
        "cftc_name": "DJIA CONSOLIDATED - CHICAGO BOARD OF TRADE",
        "dataset":   "gpe5-46if",
        "schema":    "financial",
        "description": "Dow Jones futures positioning",
    },

    # Config aliases for watchlist names
    "BTCUSDT": None,   # no COT — on-exchange crypto
    "ETHUSDT": None,
    "SOLUSDT": None,
}

# Allow watchlist aliases
SYMBOL_ALIASES = {
    "GOLD":  "XAUUSD",
    "OIL":   "USOIL",
    "SPY":   "SPX",
    "QQQ":   "NDX",
    "EUR":   "EURUSD",
    "GBP":   "GBPUSD",
    "JPY":   "USDJPY",
}


def _fetch_cot_rows(dataset: str, cftc_name: str, lookback: int = 8) -> list:
    """Fetch `lookback` most recent COT rows for the given market name."""
    where = f"market_and_exchange_names='{cftc_name}'"
    params = {
        "$limit": lookback,
        "$where": where,
        "$order": "report_date_as_yyyy_mm_dd DESC",
    }
    query = "&".join(f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items())
    url = f"{BASE_URL}/{dataset}.json?{query}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def _parse_row_legacy(row: dict) -> Optional[dict]:
    """
    Parse a COT row from the legacy/financial dataset (forex, indices).
    The API uses leveraged money (hedge funds/CTAs) as the speculative category.
    Fields confirmed from live API: lev_money_positions_long/short (no _all suffix).
    """
    try:
        date = row.get("report_date_as_yyyy_mm_dd", "")[:10]
        oi   = float(row.get("open_interest_all", 0))

        # Leveraged money = hedge funds / CTAs — best speculative proxy
        lm_long  = float(row.get("lev_money_positions_long",  0))
        lm_short = float(row.get("lev_money_positions_short", 0))
        lm_net   = lm_long - lm_short
        lm_pct   = lm_net / oi if oi > 0 else 0

        ch_long  = float(row.get("change_in_lev_money_long",  0))
        ch_short = float(row.get("change_in_lev_money_short", 0))
        ch_net   = ch_long - ch_short

        # Asset managers (pension funds) — slow trend-following context
        am_long  = float(row.get("asset_mgr_positions_long",  0))
        am_short = float(row.get("asset_mgr_positions_short", 0))
        am_net   = am_long - am_short

        # Dealers (banks) — often act as counterparty / contrarian signal
        dl_long  = float(row.get("dealer_positions_long_all",  0))
        dl_short = float(row.get("dealer_positions_short_all", 0))
        dl_net   = dl_long - dl_short

        return {
            "date":           date,
            "open_interest":  int(oi),
            "smart_money":    "leveraged_money",
            "long":           int(lm_long),
            "short":          int(lm_short),
            "net":            int(lm_net),
            "net_pct_oi":     round(lm_pct * 100, 2),
            "week_change":    int(ch_net),
            "asset_mgr_net":  int(am_net),
            "dealer_net":     int(dl_net),   # contrarian — dealers are often on the other side
        }
    except (ValueError, TypeError):
        return None


def _parse_row_disaggregated(row: dict) -> Optional[dict]:
    """
    Parse a Disaggregated COT row (commodities: gold, oil, silver).
    Field prefix confirmed from live API: m_money_ (not money_manager_).
    """
    try:
        date = row.get("report_date_as_yyyy_mm_dd", "")[:10]
        oi   = float(row.get("open_interest_all", 0))

        # Managed money (m_money) = hedge funds — smart money for commodities
        mm_long  = float(row.get("m_money_positions_long_all",  0))
        mm_short = float(row.get("m_money_positions_short_all", 0))
        mm_net   = mm_long - mm_short
        mm_pct   = mm_net / oi if oi > 0 else 0

        ch_long  = float(row.get("change_in_m_money_long_all",  0))
        ch_short = float(row.get("change_in_m_money_short_all", 0))
        ch_net   = ch_long - ch_short

        # Producer/merchant = physical market hedgers (inverse indicator)
        prod_long  = float(row.get("prod_merc_positions_long",  0))
        prod_short = float(row.get("prod_merc_positions_short", 0))
        prod_net   = prod_long - prod_short

        # Swap dealers (often banks managing client exposure)
        swap_long  = float(row.get("swap_positions_long_all",  0))
        swap_short = float(row.get("swap__positions_short_all", 0))   # note: double underscore in API
        swap_net   = swap_long - swap_short

        return {
            "date":           date,
            "open_interest":  int(oi),
            "smart_money":    "managed_money",
            "long":           int(mm_long),
            "short":          int(mm_short),
            "net":            int(mm_net),
            "net_pct_oi":     round(mm_pct * 100, 2),
            "week_change":    int(ch_net),
            "producer_net":   int(prod_net),  # hedgers — inverse price proxy
            "swap_net":       int(swap_net),
        }
    except (ValueError, TypeError):
        return None


def _parse_row_financial(row: dict) -> Optional[dict]:
    """
    Parse a Financial Futures COT row (E-mini S&P, NASDAQ, Dow).
    Uses same field structure as legacy — lev_money_ prefix (no _all suffix).
    """
    try:
        date = row.get("report_date_as_yyyy_mm_dd", "")[:10]
        oi   = float(row.get("open_interest_all", 0))

        lm_long  = float(row.get("lev_money_positions_long",  0))
        lm_short = float(row.get("lev_money_positions_short", 0))
        lm_net   = lm_long - lm_short
        lm_pct   = lm_net / oi if oi > 0 else 0

        ch_long  = float(row.get("change_in_lev_money_long",  0))
        ch_short = float(row.get("change_in_lev_money_short", 0))
        ch_net   = ch_long - ch_short

        am_long  = float(row.get("asset_mgr_positions_long",  0))
        am_short = float(row.get("asset_mgr_positions_short", 0))
        am_net   = am_long - am_short

        dl_long  = float(row.get("dealer_positions_long_all",  0))
        dl_short = float(row.get("dealer_positions_short_all", 0))
        dl_net   = dl_long - dl_short

        return {
            "date":           date,
            "open_interest":  int(oi),
            "smart_money":    "leveraged_money",
            "long":           int(lm_long),
            "short":          int(lm_short),
            "net":            int(lm_net),
            "net_pct_oi":     round(lm_pct * 100, 2),
            "week_change":    int(ch_net),
            "asset_mgr_net":  int(am_net),
            "dealer_net":     int(dl_net),
        }
    except (ValueError, TypeError):
        return None


PARSERS = {
    "legacy":        _parse_row_legacy,
    "disaggregated": _parse_row_disaggregated,
    "financial":     _parse_row_financial,
}


def fetch_cot(symbol: str, lookback: int = 8) -> List[dict]:
    """
    Fetch the last `lookback` weeks of COT data for the given symbol.

    Returns list of parsed dicts (newest first), or [] if unavailable.
    """
    sym = SYMBOL_ALIASES.get(symbol.upper(), symbol.upper())
    market = COT_MARKETS.get(sym)
    if not market:
        return []

    rows = _fetch_cot_rows(market["dataset"], market["cftc_name"], lookback)
    parser = PARSERS[market["schema"]]
    parsed = [r for r in (parser(row) for row in rows) if r is not None]
    return parsed  # newest first


def interpret_cot(rows: List[dict]) -> dict:
    """
    Interpret the last N weeks of COT data and return a bias summary.

    Checks:
    - Current net position (bullish/bearish/neutral)
    - Whether positioning is at a historical extreme (contrarian warning)
    - Whether positioning momentum is increasing or reversing
    - Consecutive weeks in same direction
    """
    if not rows:
        return {"available": False}

    latest   = rows[0]
    net      = latest["net"]
    net_pct  = latest["net_pct_oi"]
    wk_chg   = latest["week_change"]

    # Historical range for extreme detection
    all_nets = [r["net"] for r in rows]
    net_max  = max(all_nets)
    net_min  = min(all_nets)
    net_range = net_max - net_min

    # Percentile of current net within recent range
    pct_rank = (net - net_min) / net_range if net_range != 0 else 0.5

    # Extreme positioning: crowded long = near top of range AND net positive
    #                      crowded short = near bottom of range AND net negative
    # (prevents false "crowded short" when bulls are merely trimming from a high base)
    extreme_long  = pct_rank >= 0.90 and net > 0
    extreme_short = pct_rank <= 0.10 and net < 0

    # Consecutive direction count
    consec = 1
    for i in range(1, len(rows)):
        if (rows[i]["week_change"] > 0) == (wk_chg > 0):
            consec += 1
        else:
            break

    # Bias label
    if net_pct > 5:
        bias = "BULLISH"
        bias_detail = f"Smart money net long {net:,} contracts ({net_pct:+.1f}% of OI)"
    elif net_pct < -5:
        bias = "BEARISH"
        bias_detail = f"Smart money net short {abs(net):,} contracts ({net_pct:+.1f}% of OI)"
    else:
        bias = "NEUTRAL"
        bias_detail = f"Smart money balanced — net {net:,} contracts ({net_pct:+.1f}% of OI)"

    # Momentum label
    if wk_chg > 0:
        momentum = f"Adding longs / covering shorts this week (+{wk_chg:,} net)"
    elif wk_chg < 0:
        momentum = f"Adding shorts / covering longs this week ({wk_chg:,} net)"
    else:
        momentum = "Flat week — no change in net positioning"

    # Warning flags
    warnings = []
    if extreme_long:
        warnings.append("CROWDED LONG — positioning at recent extreme, contrarian reversal risk")
    if extreme_short:
        warnings.append("CROWDED SHORT — positioning at recent extreme, contrarian squeeze risk")
    # Trimming warning: strong directional bias but momentum reversing
    if net > 0 and wk_chg < 0 and pct_rank <= 0.25:
        warnings.append("BULLS TRIMMING — long bias intact but reducing for 8-week low; watch for trend change")
    if net < 0 and wk_chg > 0 and pct_rank >= 0.75:
        warnings.append("BEARS COVERING — short bias intact but reducing from extreme; watch for squeeze")
    if consec >= 4 and wk_chg != 0:
        direction = "buying" if wk_chg > 0 else "selling"
        warnings.append(f"Persistent {direction}: {consec} consecutive weeks in same direction")

    return {
        "available":      True,
        "data_tier":      3,
        "source":         "CFTC Commitment of Traders (weekly)",
        "report_date":    latest["date"],
        "smart_money_category": latest["smart_money"],
        "open_interest":  latest["open_interest"],
        "net":            net,
        "net_pct_oi":     net_pct,
        "week_change":    wk_chg,
        "pct_rank_8w":    round(pct_rank * 100, 1),  # percentile within 8-week range
        "bias":           bias,
        "bias_detail":    bias_detail,
        "momentum":       momentum,
        "consecutive_weeks": consec,
        "extreme_long":   extreme_long,
        "extreme_short":  extreme_short,
        "warnings":       warnings,
        "history": [
            {
                "date":  r["date"],
                "net":   r["net"],
                "change": r["week_change"],
            }
            for r in rows[:6]
        ],
    }


def cot_bias_for_symbol(symbol: str) -> dict:
    """
    Convenience wrapper: fetch + interpret in one call.
    Returns a ready-to-use bias dict, or {"available": False} if no COT for symbol.
    """
    try:
        rows = fetch_cot(symbol, lookback=8)
        return interpret_cot(rows)
    except Exception:
        return {"available": False}


def format_cot_section(symbol: str) -> str:
    """Format COT data as a readable report section."""
    result = cot_bias_for_symbol(symbol)
    if not result.get("available"):
        return f"  COT: Not available for {symbol} (no futures market / crypto)"

    lines = [
        f"  COT ({result['report_date']}) | Tier 3 — weekly macro positioning",
        f"  Smart money ({result['smart_money_category']}): {result['bias']}",
        f"  {result['bias_detail']}",
        f"  {result['momentum']}",
        f"  8-week rank: {result['pct_rank_8w']:.0f}th percentile (0=max short, 100=max long)",
        f"  OI: {result['open_interest']:,} contracts",
    ]
    for w in result["warnings"]:
        lines.append(f"  ⚠  {w}")
    lines.append("  Net history (newest first):")
    for h in result["history"]:
        arrow = "▲" if h["change"] > 0 else ("▼" if h["change"] < 0 else "─")
        lines.append(f"    {h['date']}  net={h['net']:+,}  {arrow}{abs(h['change']):,}")
    return "\n".join(lines)
