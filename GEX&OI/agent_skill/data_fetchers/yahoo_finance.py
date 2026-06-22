"""
Yahoo Finance data fetcher (via TradingView MCP's yahoo_price tool).

This provides live index prices for instruments where we have no direct
options data — specifically UK100 (^FTSE) and GER40 (^GDAXI).

Also used as a fast backup price source for US500 (^GSPC) and Gold (GC=F).
"""

# Yahoo Finance symbol mapping for Pepperstone spread bet instruments
YAHOO_SYMBOLS = {
    "US500":  "^GSPC",    # S&P 500 Index
    "UK100":  "^FTSE",    # FTSE 100 Index
    "GER40":  "^GDAXI",   # DAX 40 Index
    "XAUUSD": "GC=F",     # Gold Futures (front month)
    "VIX":    "^VIX",     # CBOE Volatility Index
    "DXY":    "DX-Y.NYB", # US Dollar Index
    "US10Y":  "^TNX",     # US 10-Year Treasury Yield
    "SPY":    "SPY",      # S&P 500 ETF (options proxy)
    "GLD":    "GLD",      # Gold ETF (options proxy)
}

# Pepperstone spread: approximate pip spread per instrument
# Used to adjust GEX levels for realistic entry zones
PEPPERSTONE_SPREAD = {
    "US500":  0.4,    # ~0.4 index points
    "UK100":  1.0,    # ~1 index point
    "GER40":  1.2,    # ~1.2 index points
    "XAUUSD": 0.20,   # ~$0.20 per oz
}

# Cross-market correlation coefficients (SPX as base)
# Used when applying SPX GEX regime to correlated indices
CROSS_MARKET_CORRELATION = {
    "UK100": 0.78,   # FTSE 100 ↔ SPX
    "GER40": 0.87,   # DAX 40 ↔ SPX (higher due to export-heavy, risk-on character)
}


def get_yahoo_symbol(instrument: str) -> str:
    """Return Yahoo Finance symbol for a Pepperstone instrument."""
    return YAHOO_SYMBOLS.get(instrument, instrument)


def adjust_level_for_pepperstone(level: float, instrument: str) -> tuple[float, float]:
    """
    Adjust a GEX/OI level for Pepperstone spread.
    Returns (bid_equivalent, ask_equivalent) around the theoretical level.
    """
    spread = PEPPERSTONE_SPREAD.get(instrument, 0)
    return (level - spread / 2, level + spread / 2)


def gex_regime_applies(instrument: str, correlation_threshold: float = 0.70) -> bool:
    """
    Whether SPX GEX regime is meaningful as a proxy for this instrument.
    Returns True if correlation is above threshold.
    """
    corr = CROSS_MARKET_CORRELATION.get(instrument, 1.0)
    return corr >= correlation_threshold


def describe_cross_market_proxy(instrument: str, spx_regime: str, spx_gex: float) -> str:
    """
    Generate cross-market proxy commentary for UK100/GER40.
    """
    corr = CROSS_MARKET_CORRELATION.get(instrument, 0)
    corr_pct = int(corr * 100)

    if spx_regime == "PINNED":
        regime_implication = (
            f"SPX dealers are long gamma (PINNED, ${spx_gex:.1f}B GEX). "
            f"This suppresses volatility globally. {instrument} ({corr_pct}% corr with SPX) "
            f"likely also experiences range-bound, mean-reverting conditions. "
            f"Fade moves to extremes — avoid chasing breakouts without EU-specific catalyst."
        )
    elif spx_regime == "TRENDING":
        regime_implication = (
            f"SPX dealers are short gamma (TRENDING, ${spx_gex:.1f}B GEX). "
            f"This amplifies directional moves globally. {instrument} ({corr_pct}% corr with SPX) "
            f"likely also sees trending, momentum-driven behaviour. "
            f"Trade breakouts, not fades. Expect larger-than-average daily ranges."
        )
    else:
        regime_implication = (
            f"SPX GEX is near neutral (${spx_gex:.1f}B). "
            f"No strong dealer influence on global vol. {instrument} ({corr_pct}% corr with SPX) "
            f"free to move on its own EU fundamentals and technical structure."
        )

    return regime_implication
