"""
cTrader Local MCP Data Fetcher — Local Agent

This module connects to the cTrader Local MCP server running on your Mac.
The Local MCP exposes significantly more capabilities than Remote:
  - Historical candles (all broker symbols, all timeframes)
  - Live price subscriptions
  - Depth of Market (DOM) — Level 2 order book (Phase 3)
  - Chart control (open/navigate charts, add indicators)
  - Trade execution with full order management

PREREQUISITES:
─────────────────────────────────────────────────────────────────
1. cTrader Windows or Mac desktop app installed and running
2. cTrader AI Agent Connect configured in cTrader settings
3. Local MCP server running (starts automatically with cTrader)
4. Claude Code configured to use local MCP:
   ~/.claude/settings.json:
   {
     "mcpServers": {
       "ctrader-local": {
         "type": "stdio",
         "command": "/path/to/ctrader-local-mcp-server"
       }
     }
   }
   (Exact path provided by cTrader after Local MCP setup)

5. For direct Open API connection (DOM data / Phase 3):
   pip install ctrader_open_api
   Set in .env:
     CTRADER_CLIENT_ID=your_client_id
     CTRADER_CLIENT_SECRET=your_client_secret
     CTRADER_ACCESS_TOKEN=your_access_token
     CTRADER_ACCOUNT_ID=your_account_id
     CTRADER_HOST=live.ctraderapi.com

PHASE 3 — DOM HEATMAP (Indices & Commodities):
─────────────────────────────────────────────────────────────────
When Open API credentials are set, this module will subscribe to
ProtoOADepthEvent and build a rolling heatmap of bid/ask liquidity
at each price level. Useful for:
  - Confirming FVG levels with DOM order walls
  - Detecting absorption (large order consumed = continuation)
  - Detecting rejection (large order holds = reversal)

DOM quality by asset class:
  US500/NAS100/US30 → HIGH (tracks CME E-mini futures depth)
  XAUUSD/USOIL      → HIGH (tracks COMEX/NYMEX futures depth)
  Forex pairs       → MODERATE (LP-aggregated, not exchange order book)
  Crypto            → Use OKX directly (exchange-level data already available)

STATUS: Placeholder — not yet active.
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

# cTrader broker symbol mapping (matches FTMO platform symbols)
CTRADER_SYMBOL_MAP = {
    "EURUSD":  "EURUSD",
    "GBPUSD":  "GBPUSD",
    "USDJPY":  "USDJPY",
    "GBPJPY":  "GBPJPY",
    "SPX":     "US500",     # S&P 500 CFD — 24/7, no overnight gap
    "NDX":     "US100",     # Nasdaq 100 CFD — 24/7
    "US30":    "US30",      # Dow Jones CFD — 24/7
    "DAX":     "GER40",     # German DAX CFD
    "UK100":   "UK100",     # FTSE 100 CFD
    "GOLD":    "XAUUSD",    # Gold spot
    "OIL":     "USOIL",     # WTI Oil CFD
    "BTCUSDT": "BTCUSD",
    "ETHUSDT": "ETHUSD",
    "SOLUSDT": "SOLUSD",
}

# cTrader period enum values
PERIOD_MAP = {
    "1m":  "M1",
    "5m":  "M5",
    "15m": "M15",
    "30m": "M30",
    "1h":  "H1",
    "4h":  "H4",
    "1d":  "D1",
    "1w":  "W1",
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
    Fetch historical candles via cTrader Open API (ProtoOAGetTrendbarsReq).

    Benefits over Yahoo Finance / Twelve Data:
      - 24/7 CFD data (no phantom overnight FVGs on US500/NAS100)
      - Exact Pepperstone price feed (matches TradingView Pepperstone chart)
      - All FTMO symbols available
      - Up to 5000 bars per request

    TODO: Implement using ctrader_open_api package once credentials are set.
    """
    if not is_available():
        raise NotImplementedError("cTrader credentials not configured.")

    # Implementation template (Phase 2):
    # ─────────────────────────────────
    # import asyncio
    # from ctrader_open_api import Client, Protobuf, TcpProtocol, EndPoints
    #
    # async def get_bars():
    #     client = Client(EndPoints.PROTOBUF_LIVE_HOST, EndPoints.PROTOBUF_PORT, TcpProtocol)
    #     await client.connect()
    #
    #     # Authenticate
    #     auth_req = ProtoOAApplicationAuthReq()
    #     auth_req.clientId = os.environ["CTRADER_CLIENT_ID"]
    #     auth_req.clientSecret = os.environ["CTRADER_CLIENT_SECRET"]
    #     await client.send(auth_req)
    #
    #     # Get symbol list to find symbolId
    #     symbols_req = ProtoOASymbolsListReq()
    #     symbols_req.ctidTraderAccountId = int(os.environ["CTRADER_ACCOUNT_ID"])
    #     symbols_res = await client.send(symbols_req)
    #
    #     symbol_id = next(s.symbolId for s in symbols_res.symbol
    #                      if s.symbolName == CTRADER_SYMBOL_MAP[symbol])
    #
    #     # Request trendbars
    #     bars_req = ProtoOAGetTrendbarsReq()
    #     bars_req.ctidTraderAccountId = int(os.environ["CTRADER_ACCOUNT_ID"])
    #     bars_req.symbolId = symbol_id
    #     bars_req.period = PERIOD_MAP[interval]
    #     bars_req.count = limit
    #     bars_res = await client.send(bars_req)
    #
    #     # Convert ProtoOATrendbar to Candle objects
    #     # Note: prices are in relative format — divide by 100000
    #     candles = []
    #     for bar in bars_res.trendbar:
    #         low   = bar.low / 100000
    #         high  = low + bar.deltaHigh / 100000
    #         open_ = low + bar.deltaOpen / 100000
    #         close = low + bar.deltaClose / 100000
    #         ts = datetime.fromtimestamp(bar.utcTimestampInMinutes * 60, tz=timezone.utc)
    #         candles.append(Candle(
    #             timestamp=ts, open=open_, high=high, low=low, close=close,
    #             volume=bar.volume / 100,
    #             timeframe=interval, symbol=symbol_label or symbol, data_tier=2
    #         ))
    #     return sorted(candles, key=lambda c: c.timestamp)
    #
    # return asyncio.run(get_bars())

    raise NotImplementedError("cTrader Open API fetcher not yet implemented.")


def subscribe_dom(symbol: str, callback) -> None:
    """
    Subscribe to live Depth of Market (Level 2) events for the given symbol.

    Phase 3 implementation — builds rolling heatmap from ProtoOADepthEvent.
    Each event contains newQuotes (orders added) and deletedQuotes (orders cancelled).

    callback: function(price_level: float, bid_size: float, ask_size: float) -> None
    Called on every DOM update for real-time heatmap rendering.

    TODO: Implement using ProtoOASubscribeDepthQuotesReq when Open API is set up.
    """
    raise NotImplementedError("DOM subscription — Phase 3, not yet implemented.")


def fetch_current_price(symbol: str) -> Optional[float]:
    if not is_available():
        return None
    raise NotImplementedError("cTrader fetcher not yet implemented.")
