"""
Options chain fetcher using yfinance + Black-Scholes gamma.

Completely free — no API key, no rate limits.
Covers SPY (US500 proxy) and GLD (XAUUSD proxy).

GEX formula:
  GEX per contract = gamma × OI × spot² × contract_multiplier
  Net GEX = sum(call GEX) - sum(put GEX)
  Positive → dealers long gamma (PINNED / rangebound)
  Negative → dealers short gamma (TRENDING / amplified moves)
"""

import yfinance as yf
import pandas as pd
import numpy as np
from scipy.stats import norm
from datetime import datetime, date
import warnings
warnings.filterwarnings("ignore")

# Pepperstone spread bet instrument → options proxy ticker
INSTRUMENT_TO_TICKER = {
    "US500":  "SPY",   # SPY ≈ SPX/10; multiply strikes × 10 for US500 levels
    "XAUUSD": "GLD",   # GLD ≈ gold/10; multiply strikes × 10 for XAUUSD levels
}

# Conversion multiplier: ETF level → Pepperstone instrument level
MULTIPLIER = {
    "US500":  10,  # SPY $746 × 10 ≈ US500 7460
    "XAUUSD": 10,  # GLD $387 × 10 ≈ XAUUSD 3870  (approx — use CTrader spot)
}

RISK_FREE_RATE = 0.0445   # 10Y yield as of session
CONTRACT_MULT  = 100      # Both SPY and GLD options: 100 shares per contract
MAX_STRIKE_PCT = 0.12     # Only use strikes within ±12% of spot


def _bs_gamma(S: float, K: float, T: float, r: float, sigma: float) -> float:
    """Standard Black-Scholes gamma for a European option."""
    if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
        return 0.0
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    return float(norm.pdf(d1) / (S * sigma * np.sqrt(T)))


def fetch_options_for_gex(instrument: str, spot_live: float, max_expiry_days: int = 45) -> pd.DataFrame:
    """
    Fetch options chain and compute gamma for GEX calculation.

    Parameters
    ----------
    instrument   : 'US500' or 'XAUUSD'
    spot_live    : Current Pepperstone spot price (from CTrader)
    max_expiry_days : Maximum days to expiry to include

    Returns DataFrame with columns:
    type, strike_etf, strike_live, expiration, T, iv, oi, gamma
    """
    ticker_sym = INSTRUMENT_TO_TICKER.get(instrument)
    if not ticker_sym:
        raise ValueError(f"No options proxy for {instrument}")

    mult = MULTIPLIER.get(instrument, 1)
    tk = yf.Ticker(ticker_sym)
    etf_spot = tk.fast_info["last_price"]
    today = date.today()

    expiries = [
        e for e in tk.options
        if (datetime.strptime(e, "%Y-%m-%d").date() - today).days <= max_expiry_days
    ]

    rows = []
    for exp in expiries:
        chain = tk.option_chain(exp)
        T = max((datetime.strptime(exp, "%Y-%m-%d").date() - today).days / 365.0, 1 / 365)

        for opt_type, df_opts in [("CALL", chain.calls), ("PUT", chain.puts)]:
            for _, row in df_opts.iterrows():
                K   = float(row["strike"])
                iv  = float(row["impliedVolatility"]) if pd.notna(row["impliedVolatility"]) else 0
                oi  = int(row["openInterest"]) if pd.notna(row["openInterest"]) else 0

                if oi <= 0 or iv <= 0 or K <= 0:
                    continue
                if abs(K - etf_spot) / etf_spot > MAX_STRIKE_PCT:
                    continue

                g = _bs_gamma(etf_spot, K, T, RISK_FREE_RATE, iv)
                rows.append({
                    "type":        opt_type,
                    "strike_etf":  K,
                    "strike_live": round(K * mult, 0),
                    "expiration":  exp,
                    "T":           T,
                    "iv":          iv,
                    "oi":          oi,
                    "gamma":       g,
                    "etf_spot":    etf_spot,
                })

    return pd.DataFrame(rows) if rows else pd.DataFrame()
