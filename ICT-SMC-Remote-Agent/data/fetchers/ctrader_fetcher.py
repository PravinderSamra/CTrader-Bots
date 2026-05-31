"""
cTrader Remote MCP Data Fetcher — Phase 1 Placeholder

This module will replace Yahoo Finance and Twelve Data once the cTrader
Remote MCP is configured. It will provide:

  - 24/7 CFD candles (eliminates phantom overnight FVGs on US500/NAS100)
  - Exact Pepperstone price feed (matches your TradingView chart exactly)
  - All broker symbols including USDJPY, GBPJPY, UK100, US30
  - Historical bars via ProtoOAGetTrendbarsReq

SETUP INSTRUCTIONS:
─────────────────────────────────────────────────────────────────
1. In cTrader Web: Settings → Remote MCP → Copy configuration URL
2. Add to Claude Code MCP settings (~/.claude/settings.json):

   {
     "mcpServers": {
       "ctrader-remote": {
         "type": "sse",
         "url": "<your-ctrader-remote-mcp-url>"
       }
     }
   }

3. For cTrader Open API (direct Python connection — needed for this fetcher):
   - Register app at: https://openapi.ctrader.com/
   - Request credentials from Pepperstone support
   - Install: pip install ctrader_open_api
   - Set environment variables in .env:
       CTRADER_CLIENT_ID=your_client_id
       CTRADER_CLIENT_SECRET=your_client_secret
       CTRADER_ACCESS_TOKEN=your_access_token
       CTRADER_ACCOUNT_ID=your_account_id
       CTRADER_HOST=live.ctraderapi.com

SYMBOL MAPPING (cTrader → FTMO symbols):
─────────────────────────────────────────────────────────────────
  EURUSD   → EURUSD
  GBPUSD   → GBPUSD
  USDJPY   → USDJPY
  GBPJPY   → GBPJPY
  US500    → US500.cash  (S&P 500 CFD — 24/7)
  NAS100   → US100.cash  (Nasdaq 100 CFD — 24/7)
  GER40    → GER40.cash  (DAX CFD)
  US30     → US30.cash   (Dow Jones CFD — 24/7)
  UK100    → UK100.cash  (FTSE 100 CFD)
  XAUUSD   → XAUUSD      (Gold spot)
  USOIL    → USOIL.cash  (WTI Oil CFD)

STATUS: Placeholder — not yet active.
Current data sources: Yahoo Finance (indices), Twelve Data (forex), OKX (crypto)
─────────────────────────────────────────────────────────────────
"""

import os
from typing import List, Optional
from data.models import Candle

_CONFIGURED = (
    os.environ.get("CTRADER_CLIENT_ID")
    and os.environ.get("CTRADER_ACCESS_TOKEN")
    and os.environ.get("CTRADER_ACCOUNT_ID")
)

CTRADER_SYMBOL_MAP = {
    "EURUSD":  "EURUSD",
    "GBPUSD":  "GBPUSD",
    "USDJPY":  "USDJPY",
    "GBPJPY":  "GBPJPY",
    "SPX":     "US500",
    "NDX":     "US100",
    "DAX":     "GER40",
    "US30":    "US30",
    "UK100":   "UK100",
    "GOLD":    "XAUUSD",
    "OIL":     "USOIL",
    "BTCUSDT": "BTCUSD",
    "ETHUSDT": "ETHUSD",
    "SOLUSDT": "SOLUSD",
}

PERIOD_MAP = {
    "1m":  1,
    "5m":  5,
    "15m": 15,
    "30m": 30,
    "1h":  60,
    "4h":  240,
    "1d":  1440,
    "1w":  10080,
}


def is_available() -> bool:
    return bool(_CONFIGURED)


def fetch_klines(
    symbol: str,
    interval: str,
    limit: int = 200,
    symbol_label: Optional[str] = None,
) -> List[Candle]:
    """
    Fetch historical candles from cTrader Open API.

    TODO: Implement once credentials are configured.
    Until then this raises NotImplementedError.
    The calling code in main.py falls back to Yahoo/Twelve Data.
    """
    if not is_available():
        raise NotImplementedError("cTrader credentials not configured — using fallback data source.")

    # Phase 1 implementation placeholder
    # When credentials are set, implement using:
    #
    # from ctrader_open_api import Client, Protobuf, TcpProtocol, EndPoints
    # from ctrader_open_api.messages.OpenApiCommonMessages_pb2 import *
    # from ctrader_open_api.messages.OpenApiMessages_pb2 import *
    #
    # client = Client(EndPoints.PROTOBUF_LIVE_HOST, EndPoints.PROTOBUF_PORT, TcpProtocol)
    # ... (async WebSocket connection and ProtoOAGetTrendbarsReq)

    raise NotImplementedError("cTrader fetcher not yet implemented.")


def fetch_current_price(symbol: str) -> Optional[float]:
    if not is_available():
        return None
    raise NotImplementedError("cTrader fetcher not yet implemented.")
