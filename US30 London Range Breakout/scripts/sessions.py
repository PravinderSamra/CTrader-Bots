"""DST-aware session helpers. cTrader timestamps are UTC; London/NY sessions
shift with daylight saving, so all windowing is done in exchange-local time."""
import pandas as pd
from zoneinfo import ZoneInfo

LONDON = ZoneInfo("Europe/London")
NY = ZoneInfo("America/New_York")


def load_m5(csv_path):
    """Load an M5 CSV into a tz-aware DataFrame with London/NY local columns."""
    df = pd.read_csv(csv_path)
    df["dt"] = pd.to_datetime(df["timestamp_ms"], unit="ms", utc=True)
    df = df.drop_duplicates("timestamp_ms").sort_values("dt").reset_index(drop=True)
    df["lon"] = df["dt"].dt.tz_convert(LONDON)
    df["ny"] = df["dt"].dt.tz_convert(NY)
    # session-day keyed to NY calendar date (the trading day of the US open)
    df["ny_date"] = df["ny"].dt.date
    df["lon_hour"] = df["lon"].dt.hour + df["lon"].dt.minute / 60.0
    df["ny_hour"] = df["ny"].dt.hour + df["ny"].dt.minute / 60.0
    df["dow"] = df["ny"].dt.dayofweek  # 0=Mon
    return df
