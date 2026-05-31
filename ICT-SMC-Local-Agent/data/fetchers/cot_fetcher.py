"""
CFTC Commitment of Traders (COT) Fetcher — Tier 3 Macro Data

Weekly data published every Friday by the US Commodity Futures Trading Commission.
~3-day lag (reports Tuesday positions, published Friday).
Use for weekly bias direction and extreme positioning alerts only.

Ranks current net position against the prior 8 weeks to identify:
  - Crowded longs/shorts (positioning at extremes = contrarian reversal risk)
  - Institutional accumulation/distribution shifts
"""

import urllib.request
import json
import csv
import io
from typing import Optional
from data.models import COTData

# CFTC API — Socrata open data endpoint
_BASE = "https://publicreporting.cftc.gov/resource/6dca-aqww.json"

# CFTC 'market_and_exchange_names' values mapped to our instrument names
_MARKET_MAP = {
    "EURUSD": "EURO FX",
    "GBPUSD": "BRITISH POUND",
    "USDJPY": "JAPANESE YEN",
    "GBPJPY": "JAPANESE YEN",
    "GOLD":   "GOLD",
    "OIL":    "CRUDE OIL, LIGHT SWEET",
    "SPX":    "S&P 500 STOCK INDEX",
    "NDX":    "NASDAQ-100 STOCK INDEX",
    "US30":   "DOW JONES INDUSTRIAL AVERAGE",
}


def _fetch_cot(market_name: str, weeks: int = 9) -> Optional[list]:
    params = (
        f"?$where=market_and_exchange_names=%27{urllib.parse.quote(market_name)}%27"
        f"&$order=report_date_as_yyyy_mm_dd DESC"
        f"&$limit={weeks}"
    )
    url = _BASE + params
    import urllib.parse
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
        # Leveraged Money (hedge funds / managed money) positioning
        long_pos  = int(latest.get("lev_money_positions_long_all",  0) or 0)
        short_pos = int(latest.get("lev_money_positions_short_all", 0) or 0)
        net       = long_pos - short_pos
        oi        = int(latest.get("open_interest_all", 1) or 1)
        pct_of_oi = round(net / oi * 100, 1)
        date_str  = latest.get("report_date_as_yyyy_mm_dd", "")[:10]
        category  = "Leveraged Money"

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
            l = int(row.get("lev_money_positions_long_all",  0) or 0)
            s = int(row.get("lev_money_positions_short_all", 0) or 0)
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
