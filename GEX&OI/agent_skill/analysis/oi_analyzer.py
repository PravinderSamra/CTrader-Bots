"""
Open Interest analyser.

OI reveals where the market's bets are concentrated.
High OI strikes act as magnetic price levels.
OI changes reveal whether positions are being built or unwound.
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass


@dataclass
class OIResult:
    symbol: str
    spot_price: float
    total_call_oi: int
    total_put_oi: int
    put_call_ratio: float               # > 1.0 = more puts = defensive/bearish sentiment
    max_pain: float
    nearest_expiry: str                 # Date of closest expiry
    weekly_expiry: str                  # This week's expiry
    top_call_strikes: list[dict]        # Highest OI call strikes (resistance)
    top_put_strikes: list[dict]         # Highest OI put strikes (support)
    oi_by_strike: pd.DataFrame
    sentiment: str                      # "BULLISH" / "NEUTRAL" / "BEARISH"
    sentiment_description: str


def _normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    """Map yfinance column names to expected format."""
    df = df.copy()
    if "strike_etf" in df.columns and "strike" not in df.columns:
        df["strike"] = df["strike_etf"]
    if "oi" in df.columns and "open_interest" not in df.columns:
        df["open_interest"] = df["oi"]
    if "expiration" in df.columns and not pd.api.types.is_datetime64_any_dtype(df["expiration"]):
        df["expiration"] = pd.to_datetime(df["expiration"])
    return df


def analyse_oi(options_df: pd.DataFrame, spot_price: float, symbol: str) -> OIResult:
    """
    Analyse open interest distribution and derive key price levels.
    """
    df = _normalize_df(options_df)
    df = df.dropna(subset=["strike", "open_interest"]).copy()
    df = df[df["open_interest"] > 0]

    today = pd.Timestamp.today().normalize()

    # Focus on front two expiries for most relevant positioning
    expiries = sorted(df["expiration"].dropna().unique())
    near_expiries = [e for e in expiries if pd.Timestamp(e) >= today][:4]
    df_near = df[df["expiration"].isin(near_expiries)]

    # OI by strike and type
    oi_pivot = df_near.groupby(["strike", "type"])["open_interest"].sum().unstack(fill_value=0)
    if "CALL" not in oi_pivot.columns:
        oi_pivot["CALL"] = 0
    if "PUT" not in oi_pivot.columns:
        oi_pivot["PUT"] = 0

    oi_pivot["total"] = oi_pivot["CALL"] + oi_pivot["PUT"]
    oi_pivot = oi_pivot.reset_index().sort_values("strike")

    # Totals
    total_call_oi = int(df_near[df_near["type"] == "CALL"]["open_interest"].sum())
    total_put_oi = int(df_near[df_near["type"] == "PUT"]["open_interest"].sum())
    put_call_ratio = round(total_put_oi / total_call_oi, 2) if total_call_oi > 0 else 0

    # Top strikes by OI
    calls = oi_pivot[oi_pivot["strike"] > spot_price].nlargest(5, "CALL")
    puts = oi_pivot[oi_pivot["strike"] < spot_price].nlargest(5, "PUT")

    top_call_strikes = [
        {"strike": row["strike"], "oi": int(row["CALL"]), "type": "resistance"}
        for _, row in calls.iterrows()
    ]
    top_put_strikes = [
        {"strike": row["strike"], "oi": int(row["PUT"]), "type": "support"}
        for _, row in puts.iterrows()
    ]

    # Max pain from nearest expiry
    nearest_df = df[df["expiration"] == near_expiries[0]] if near_expiries else df
    max_pain = _calculate_max_pain(nearest_df)

    # Expiry dates
    nearest_expiry = str(near_expiries[0].date()) if near_expiries else "N/A"

    # Next weekly expiry (Fridays)
    weekly_expiry = _next_weekly_expiry(near_expiries, today)

    # Sentiment from P/C ratio
    sentiment, sentiment_desc = _classify_sentiment(put_call_ratio, spot_price, top_call_strikes, top_put_strikes)

    return OIResult(
        symbol=symbol,
        spot_price=spot_price,
        total_call_oi=total_call_oi,
        total_put_oi=total_put_oi,
        put_call_ratio=put_call_ratio,
        max_pain=max_pain,
        nearest_expiry=nearest_expiry,
        weekly_expiry=weekly_expiry,
        top_call_strikes=top_call_strikes,
        top_put_strikes=top_put_strikes,
        oi_by_strike=oi_pivot,
        sentiment=sentiment,
        sentiment_description=sentiment_desc,
    )


def _calculate_max_pain(df: pd.DataFrame) -> float:
    """Strike at which total option holder pain (loss) is maximised."""
    strikes = df["strike"].unique()
    pain = {}

    for strike in strikes:
        call_pain = df[(df["type"] == "CALL") & (df["strike"] < strike)].apply(
            lambda r: (strike - r["strike"]) * r["open_interest"] * 100, axis=1
        ).sum()
        put_pain = df[(df["type"] == "PUT") & (df["strike"] > strike)].apply(
            lambda r: (r["strike"] - strike) * r["open_interest"] * 100, axis=1
        ).sum()
        pain[strike] = call_pain + put_pain

    return min(pain, key=pain.get) if pain else 0.0


def _next_weekly_expiry(expiries: list, today: pd.Timestamp) -> str:
    """Find the next Friday expiry in the list."""
    fridays = [e for e in expiries if pd.Timestamp(e).weekday() == 4]
    if fridays:
        return str(fridays[0].date())
    return str(expiries[0].date()) if expiries else "N/A"


def _classify_sentiment(pcr: float, spot: float, calls: list, puts: list) -> tuple[str, str]:
    """Classify market sentiment from put/call ratio and OI distribution."""
    if pcr > 1.5:
        sent = "BEARISH"
        desc = (f"Put/Call ratio {pcr:.2f} — significantly more puts than calls. "
                "Market participants are heavily hedged or directionally bearish. "
                "Watch for mean-reversion bounce if VIX spikes (over-hedged scenario).")
    elif pcr > 1.2:
        sent = "MILDLY BEARISH"
        desc = (f"Put/Call ratio {pcr:.2f} — modest put dominance. "
                "Cautious market tone. Bears have slight edge in positioning.")
    elif pcr > 0.8:
        sent = "NEUTRAL"
        desc = (f"Put/Call ratio {pcr:.2f} — balanced call and put positioning. "
                "Market is undecided. Price likely to follow the technical and macro narrative.")
    elif pcr > 0.6:
        sent = "MILDLY BULLISH"
        desc = (f"Put/Call ratio {pcr:.2f} — more calls than puts. "
                "Moderate bullish positioning. Watch for complacency — low hedging can precede sharp pullbacks.")
    else:
        sent = "BEARISH (contrarian)"
        desc = (f"Put/Call ratio {pcr:.2f} — very low, extreme call dominance. "
                "Contrarian warning: excessive bullishness. Market could be vulnerable to sharp pullback.")

    return sent, desc
