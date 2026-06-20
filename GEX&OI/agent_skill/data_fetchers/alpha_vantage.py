"""
Alpha Vantage data fetcher for options chains, GEX, and macro data.
"""

import requests
import pandas as pd
from typing import Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import ALPHA_VANTAGE_API_KEY

BASE_URL = "https://www.alphavantage.co/query"


def _get(params: dict) -> dict:
    params["apikey"] = ALPHA_VANTAGE_API_KEY
    resp = requests.get(BASE_URL, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def get_options_chain(symbol: str, date: Optional[str] = None) -> pd.DataFrame:
    """
    Fetch live options chain with Greeks for a symbol.
    Returns DataFrame with columns: strike, expiration, type, gamma, delta,
    open_interest, implied_volatility, bid, ask, last, volume
    """
    params = {"function": "REALTIME_OPTIONS", "symbol": symbol, "require_greeks": "true"}
    if date:
        params["date"] = date

    data = _get(params)

    if "data" not in data:
        raise ValueError(f"No options data returned for {symbol}: {data.get('Note', data.get('Information', 'Unknown error'))}")

    df = pd.DataFrame(data["data"])

    # Normalise types
    numeric_cols = ["strike", "gamma", "delta", "theta", "vega", "rho",
                    "open_interest", "implied_volatility", "bid", "ask", "last", "volume"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["expiration"] = pd.to_datetime(df["expiration"], errors="coerce")
    df["type"] = df["type"].str.upper()  # "CALL" or "PUT"

    return df


def get_historical_options(symbol: str, date: str) -> pd.DataFrame:
    """Fetch historical options chain for a specific past date (YYYY-MM-DD)."""
    params = {"function": "HISTORICAL_OPTIONS", "symbol": symbol, "date": date}
    data = _get(params)
    if "data" not in data:
        raise ValueError(f"No historical options data for {symbol} on {date}")
    df = pd.DataFrame(data["data"])
    numeric_cols = ["strike", "gamma", "delta", "open_interest", "implied_volatility", "bid", "ask"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df["expiration"] = pd.to_datetime(df["expiration"], errors="coerce")
    df["type"] = df["type"].str.upper()
    return df


def get_spot_price(symbol: str) -> dict:
    """Get latest quote for an equity/ETF/index."""
    params = {"function": "GLOBAL_QUOTE", "symbol": symbol}
    data = _get(params)
    quote = data.get("Global Quote", {})
    return {
        "symbol": symbol,
        "price": float(quote.get("05. price", 0)),
        "change": float(quote.get("09. change", 0)),
        "change_pct": quote.get("10. change percent", "0%"),
        "volume": int(quote.get("06. volume", 0)),
        "prev_close": float(quote.get("08. previous close", 0)),
    }


def get_gold_silver_spot() -> dict:
    """Get live gold and silver spot prices."""
    params = {"function": "GOLD_SILVER_SPOT"}
    data = _get(params)
    return data


def get_vix() -> float:
    """Get current VIX level."""
    quote = get_spot_price("VIX")
    return quote["price"]


def get_treasury_yield(maturity: str = "10year") -> dict:
    """
    Get US treasury yield.
    maturity options: 3month, 2year, 5year, 7year, 10year, 30year
    """
    params = {"function": "TREASURY_YIELD", "interval": "daily", "maturity": maturity}
    data = _get(params)
    series = data.get("data", [])
    if series:
        latest = series[0]
        return {"maturity": maturity, "yield_pct": float(latest.get("value", 0)), "date": latest.get("date")}
    return {"maturity": maturity, "yield_pct": None, "date": None}


def get_news_sentiment(tickers: str = "SPY,GLD", limit: int = 10) -> list[dict]:
    """
    Get news articles with AI sentiment scores.
    tickers: comma-separated ticker list
    Returns list of articles with: title, summary, sentiment_score, sentiment_label
    """
    params = {"function": "NEWS_SENTIMENT", "tickers": tickers, "limit": limit, "sort": "LATEST"}
    data = _get(params)
    articles = data.get("feed", [])
    results = []
    for art in articles:
        ticker_sentiment = {
            ts.get("ticker"): ts.get("ticker_sentiment_label")
            for ts in art.get("ticker_sentiment", [])
        }
        results.append({
            "title": art.get("title"),
            "summary": art.get("summary", "")[:200],
            "source": art.get("source"),
            "time": art.get("time_published"),
            "overall_sentiment": art.get("overall_sentiment_label"),
            "overall_score": float(art.get("overall_sentiment_score", 0)),
            "ticker_sentiment": ticker_sentiment,
        })
    return results


def get_market_status() -> dict:
    """Check which global markets are currently open."""
    params = {"function": "MARKET_STATUS"}
    data = _get(params)
    markets = data.get("markets", [])
    status = {}
    for m in markets:
        status[m.get("market_type", m.get("region"))] = {
            "region": m.get("region"),
            "status": m.get("current_status"),
            "open_time": m.get("local_open"),
            "close_time": m.get("local_close"),
        }
    return status
