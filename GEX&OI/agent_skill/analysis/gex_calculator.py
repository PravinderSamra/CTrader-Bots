"""
Gamma Exposure (GEX) calculator.

GEX tells us how options market makers are positioned.
Positive GEX → dealers are long gamma → they stabilise price (sell rallies, buy dips).
Negative GEX → dealers are short gamma → they amplify price moves (buy rallies, sell dips).
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass


@dataclass
class GEXResult:
    symbol: str
    spot_price: float
    total_gex: float                    # Net GEX in $ billions
    call_gex: float
    put_gex: float
    max_gex_strike: float               # Strike with highest positive GEX (gravity level)
    zero_gex_strike: float              # Where net GEX crosses zero
    put_wall: float                     # Highest put OI cluster below spot
    call_wall: float                    # Highest call OI cluster above spot
    max_pain: float                     # Strike maximising option seller profit
    support_levels: list[float]         # GEX-derived support levels
    resistance_levels: list[float]      # GEX-derived resistance levels
    regime: str                         # "PINNED" / "NEUTRAL" / "TRENDING"
    regime_description: str
    gex_by_strike: pd.DataFrame         # Full breakdown for charting


def _normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    """Map yfinance column names (strike_etf, oi) to expected format (strike, open_interest)."""
    df = df.copy()
    if "strike_etf" in df.columns and "strike" not in df.columns:
        df["strike"] = df["strike_etf"]
    if "oi" in df.columns and "open_interest" not in df.columns:
        df["open_interest"] = df["oi"]
    if "expiration" in df.columns and not pd.api.types.is_datetime64_any_dtype(df["expiration"]):
        df["expiration"] = pd.to_datetime(df["expiration"])
    return df


def calculate_gex(options_df: pd.DataFrame, spot_price: float, symbol: str,
                  contract_multiplier: int = 100) -> GEXResult:
    """
    Calculate GEX from an options chain DataFrame.

    Parameters
    ----------
    options_df : DataFrame — accepts yfinance format (strike_etf, oi) or legacy format (strike, open_interest)
    spot_price : Current spot price of the underlying (ETF scale for yfinance data)
    symbol : Ticker symbol
    contract_multiplier : Number of shares/units per contract (default 100)
    """
    df = _normalize_df(options_df)
    df = df.dropna(subset=["strike", "gamma", "open_interest"]).copy()
    df = df[df["open_interest"] > 0]
    df = df[df["gamma"] > 0]

    # Focus on near-term expiries (next 45 days) — where dealer hedging is most active
    today = pd.Timestamp.today().normalize()
    df = df[df["expiration"] <= today + pd.Timedelta(days=45)]
    df = df[df["expiration"] >= today]

    # GEX per contract
    # Formula: gamma × open_interest × spot_price² × contract_multiplier
    df["gex"] = df["gamma"] * df["open_interest"] * (spot_price ** 2) * contract_multiplier

    # Calls add positive GEX, puts subtract (dealers short puts = long gamma)
    df.loc[df["type"] == "PUT", "gex"] *= -1

    # Aggregate by strike
    gex_by_strike = df.groupby("strike")["gex"].sum().reset_index()
    gex_by_strike.columns = ["strike", "net_gex"]
    gex_by_strike = gex_by_strike.sort_values("strike")

    # Scale to billions for readability
    gex_by_strike["net_gex_bn"] = gex_by_strike["net_gex"] / 1e9

    # Summary metrics
    call_df = df[df["type"] == "CALL"]
    put_df = df[df["type"] == "PUT"]
    total_call_gex = call_df["gex"].sum() / 1e9
    total_put_gex = abs(put_df["gex"].sum()) / 1e9
    total_gex = (call_df["gex"].sum() + put_df["gex"].sum()) / 1e9

    if gex_by_strike.empty:
        raise ValueError(
            f"Insufficient options data to calculate GEX for {symbol}. "
            "Options chain returned no contracts with valid OI, IV and gamma. "
            "This typically happens pre-market or when the data source has not updated yet."
        )

    # Max GEX strike (gravity / pin level)
    max_gex_strike = gex_by_strike.loc[gex_by_strike["net_gex"].idxmax(), "strike"]

    # Zero GEX crossover (where regime flips)
    zero_gex_strike = _find_zero_crossover(gex_by_strike, spot_price)

    # Put wall: strike below spot with highest put OI
    put_oi = df[df["type"] == "PUT"].groupby("strike")["open_interest"].sum()
    puts_below = put_oi[put_oi.index < spot_price]
    put_wall = puts_below.idxmax() if not puts_below.empty else spot_price * 0.95

    # Call wall: strike above spot with highest call OI
    call_oi = df[df["type"] == "CALL"].groupby("strike")["open_interest"].sum()
    calls_above = call_oi[call_oi.index > spot_price]
    call_wall = calls_above.idxmax() if not calls_above.empty else spot_price * 1.05

    # Max pain: strike minimising total option value (sellers' target)
    max_pain = _calculate_max_pain(df)

    # Key support/resistance levels from GEX
    support_levels = _find_support_levels(gex_by_strike, spot_price)
    resistance_levels = _find_resistance_levels(gex_by_strike, spot_price)

    # Regime determination
    regime, regime_desc = _determine_regime(total_gex)

    return GEXResult(
        symbol=symbol,
        spot_price=spot_price,
        total_gex=round(total_gex, 2),
        call_gex=round(total_call_gex, 2),
        put_gex=round(total_put_gex, 2),
        max_gex_strike=max_gex_strike,
        zero_gex_strike=zero_gex_strike,
        put_wall=put_wall,
        call_wall=call_wall,
        max_pain=max_pain,
        support_levels=support_levels,
        resistance_levels=resistance_levels,
        regime=regime,
        regime_description=regime_desc,
        gex_by_strike=gex_by_strike,
    )


def _find_zero_crossover(gex_by_strike: pd.DataFrame, spot_price: float) -> float:
    """Find the strike price where net GEX crosses zero."""
    above_spot = gex_by_strike[gex_by_strike["strike"] >= spot_price].copy()
    if above_spot.empty:
        return spot_price

    above_spot = above_spot.sort_values("strike")
    cumulative = above_spot["net_gex"].cumsum()

    # Find first strike where cumulative GEX changes sign
    sign_changes = cumulative[cumulative.diff().lt(0) | (cumulative == 0)]
    if not sign_changes.empty:
        idx = sign_changes.index[0]
        return above_spot.loc[idx, "strike"]

    return spot_price


def _calculate_max_pain(df: pd.DataFrame) -> float:
    """Max pain: the strike at which total option value is minimised."""
    strikes = df["strike"].unique()
    pain = {}

    for strike in strikes:
        # Value of calls expiring worthless (below strike)
        call_pain = df[(df["type"] == "CALL") & (df["strike"] < strike)].apply(
            lambda r: (strike - r["strike"]) * r["open_interest"] * 100, axis=1
        ).sum()

        # Value of puts expiring worthless (above strike)
        put_pain = df[(df["type"] == "PUT") & (df["strike"] > strike)].apply(
            lambda r: (r["strike"] - strike) * r["open_interest"] * 100, axis=1
        ).sum()

        pain[strike] = call_pain + put_pain

    if not pain:
        return 0.0

    return min(pain, key=pain.get)


def _find_support_levels(gex_by_strike: pd.DataFrame, spot_price: float, n: int = 3) -> list[float]:
    """Find top N positive GEX strikes below spot (dealer buying support)."""
    below = gex_by_strike[
        (gex_by_strike["strike"] < spot_price) & (gex_by_strike["net_gex"] > 0)
    ]
    top = below.nlargest(n, "net_gex")
    return sorted(top["strike"].tolist(), reverse=True)


def _find_resistance_levels(gex_by_strike: pd.DataFrame, spot_price: float, n: int = 3) -> list[float]:
    """Find top N positive GEX strikes above spot (dealer selling resistance)."""
    above = gex_by_strike[
        (gex_by_strike["strike"] > spot_price) & (gex_by_strike["net_gex"] > 0)
    ]
    top = above.nlargest(n, "net_gex")
    return sorted(top["strike"].tolist())


def _determine_regime(total_gex_bn: float) -> tuple[str, str]:
    """Classify the market regime based on net GEX."""
    if total_gex_bn > 1.0:
        return ("PINNED", f"Strong positive GEX (+${total_gex_bn:.1f}B): Dealers long gamma. "
                "Expect rangebound, mean-reverting price action. Fade moves to extremes. "
                "Volatility suppressed.")
    elif total_gex_bn > 0:
        return ("PINNED", f"Positive GEX (+${total_gex_bn:.1f}B): Mild dealer stabilisation. "
                "Slight mean-reversion bias but breakouts still possible on catalyst.")
    elif total_gex_bn > -1.0:
        return ("NEUTRAL", f"Near-zero GEX (${total_gex_bn:.1f}B): No strong dealer influence. "
                "Price can move freely. Follow momentum and structure.")
    else:
        return ("TRENDING", f"Negative GEX (${total_gex_bn:.1f}B): Dealers short gamma, amplifying moves. "
                "Expect trending, directional behaviour. Trade breakouts, not fades. "
                "Volatility elevated.")
