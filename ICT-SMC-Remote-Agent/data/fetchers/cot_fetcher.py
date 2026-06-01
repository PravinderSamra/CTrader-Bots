"""
CFTC Commitment of Traders (COT) Fetcher — Tier 3 Macro Data

Weekly data published every Friday by the US Commodity Futures Trading Commission.
~3-day lag (reports Tuesday positions, published Friday).
Use for weekly bias direction and extreme positioning alerts only.

Ranks current net position against the prior 8 weeks to identify:
  - Crowded longs/shorts (positioning at extremes = contrarian reversal risk)
  - Institutional accumulation/distribution shifts

Uses the CFTC Legacy Futures-Only report (resource 6dca-aqww).
Tracks Non-Commercial (speculative) positions — hedge funds, managed money, CTAs.
"""

import urllib.request
import urllib.parse
import json
from typing import Optional
from data.models import COTData

# CFTC API — Socrata open data endpoint (Legacy Futures-Only)
_BASE = "https://publicreporting.cftc.gov/resource/6dca-aqww.json"

# Exact 'market_and_exchange_names' values from the CFTC dataset
# These must match the dataset exactly — use LIKE searches to verify if adding new ones
_MARKET_MAP = {
    "EURUSD": "EURO FX - CHICAGO MERCANTILE EXCHANGE",
    "GBPUSD": "BRITISH POUND - CHICAGO MERCANTILE EXCHANGE",
    "USDJPY": "JAPANESE YEN - CHICAGO MERCANTILE EXCHANGE",
    "GBPJPY": "JAPANESE YEN - CHICAGO MERCANTILE EXCHANGE",
    "GOLD":   "GOLD - COMMODITY EXCHANGE INC.",
    "OIL":    "CRUDE OIL, LIGHT SWEET-WTI - ICE FUTURES EUROPE",
    "SPX":    "E-MINI S&P 500 STOCK INDEX - CHICAGO MERCANTILE EXCHANGE",
    "NDX":    "NASDAQ-100 Consolidated - CHICAGO MERCANTILE EXCHANGE",
    "US30":   "DJIA Consolidated - CHICAGO BOARD OF TRADE",
}


def _fetch_cot(market_name: str, weeks: int = 9) -> Optional[list]:
    # Socrata SoQL: $where/$order/$limit must remain literal in the URL;
    # only the market name value is encoded.
    name_enc = urllib.parse.quote(market_name, safe="")
    url = (
        f"{_BASE}"
        f"?$where=market_and_exchange_names=%27{name_enc}%27"
        f"&$order=report_date_as_yyyy_mm_dd%20DESC"
        f"&$limit={weeks}"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except Exception:
        return None


def fetch_cot(instrument: str) -> Optional[COTData]:
    market_name = _MARKET_MAP.get(instrument.upper())
    if not market_name:
        return None

    rows = _fetch_cot(market_name)
    if not rows or len(rows) < 2:
        return None

    latest = rows[0]
    try:
        # Non-Commercial = speculative positions (hedge funds, managed money, CTAs)
        # Available in the Legacy report — equivalent to COT speculator sentiment
        long_pos  = int(latest.get("noncomm_positions_long_all",  0) or 0)
        short_pos = int(latest.get("noncomm_positions_short_all", 0) or 0)
        net       = long_pos - short_pos
        oi        = int(latest.get("open_interest_all", 1) or 1)
        pct_of_oi = round(net / oi * 100, 1)
        date_str  = latest.get("report_date_as_yyyy_mm_dd", "")[:10]
        category  = "Non-Commercial (Speculative)"

        if pct_of_oi < -5:
            bias = "BEARISH"
        elif pct_of_oi > 5:
            bias = "BULLISH"
        else:
            bias = "NEUTRAL"

        # 8-week history for ranking
        history = []
        nets_8wk = []
        for row in rows[1:9]:
            l = int(row.get("noncomm_positions_long_all",  0) or 0)
            s = int(row.get("noncomm_positions_short_all", 0) or 0)
            n = l - s
            d = row.get("report_date_as_yyyy_mm_dd", "")[:10]
            history.append((d, n))
            nets_8wk.append(n)

        if nets_8wk:
            nets_sorted = sorted(nets_8wk)
            rank = int(sum(1 for x in nets_sorted if x <= net) / len(nets_sorted) * 100)
        else:
            rank = 50

        weekly_change = net - history[0][1] if history else 0

        return COTData(
            report_date=date_str,
            net_contracts=net,
            pct_of_oi=pct_of_oi,
            weekly_change=weekly_change,
            rank_8wk=rank,
            category=category,
            bias=bias,
            history=[(d, n) for d, n in [(date_str, net)] + history],
        )
    except (KeyError, ValueError, TypeError):
        return None
