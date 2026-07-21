"""Load all yearly 1-minute CSVs, clean, and cache resampled frames for the
analysis suite. Caches go to a scratch dir (not the repo) as pickle files.

Outputs: m1, m5, m15, h1, d1 (daily built on a 22:00 UTC session boundary so a
"trading day" matches the XAUUSD dealing day: 22:00 UTC open -> 21:00 UTC close).
"""
import glob
import os
import sys

import numpy as np
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
CACHE = os.environ.get(
    "XAU_CACHE",
    "/tmp/claude-0/-home-user-CTrader-Bots/952eda8c-76b6-5df8-9ee5-680db4472e55/scratchpad/xau_cache",
)
os.makedirs(CACHE, exist_ok=True)

OHLC = {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}


def load_m1() -> pd.DataFrame:
    pkl = os.path.join(CACHE, "m1.pkl")
    if os.path.exists(pkl):
        return pd.read_pickle(pkl)
    files = sorted(glob.glob(os.path.join(DATA_DIR, "XAUUSD_M_1_*.csv")))
    frames = [pd.read_csv(f, parse_dates=["datetime"]) for f in files]
    m1 = pd.concat(frames, ignore_index=True)
    m1 = m1.drop_duplicates(subset="datetime").sort_values("datetime")
    m1 = m1.set_index("datetime")
    m1.index = m1.index.tz_convert("UTC")
    # sanity: drop rows with non-positive prices or high<low
    bad = (m1[["open", "high", "low", "close"]] <= 0).any(axis=1) | (m1.high < m1.low)
    m1 = m1[~bad]
    m1.to_pickle(pkl)
    return m1


def resample(m1: pd.DataFrame, rule: str, name: str, offset: str | None = None) -> pd.DataFrame:
    pkl = os.path.join(CACHE, f"{name}.pkl")
    if os.path.exists(pkl):
        return pd.read_pickle(pkl)
    kw = {"offset": offset} if offset else {}
    df = m1.resample(rule, **kw).agg(OHLC).dropna(subset=["open"])
    df.to_pickle(pkl)
    return df


def load_all():
    m1 = load_m1()
    m5 = resample(m1, "5min", "m5")
    m15 = resample(m1, "15min", "m15")
    h1 = resample(m1, "1h", "h1")
    # dealing day: 22:00 UTC -> 22:00 UTC (label by the calendar date of the close side)
    d1 = resample(m1, "24h", "d1", offset="22h")
    return m1, m5, m15, h1, d1


if __name__ == "__main__":
    m1, m5, m15, h1, d1 = load_all()
    print(f"M1 bars : {len(m1):,}  {m1.index[0]} -> {m1.index[-1]}")
    print(f"M5 bars : {len(m5):,}")
    print(f"D1 bars : {len(d1):,}")
    # gap audit: minutes with no bar during weekdays
    diffs = m1.index.to_series().diff().dt.total_seconds().div(60)
    gaps = diffs[diffs > 1]
    weekend = gaps[gaps > 2000]
    print(f"gaps >1min: {len(gaps):,} | >5min: {(gaps > 5).sum():,} | >60min: {(gaps > 60).sum():,} | weekend-sized: {len(weekend)}")
    print("largest non-weekend gaps (minutes):")
    print(gaps[gaps <= 2000].sort_values(ascending=False).head(10).to_string())
    print("\nyearly close/range summary:")
    d1x = d1.copy()
    d1x["year"] = d1x.index.year
    d1x["range"] = d1x.high - d1x.low
    print(d1x.groupby("year").agg(days=("close", "size"), first_close=("close", "first"),
                                  last_close=("close", "last"), avg_range=("range", "mean"),
                                  med_range=("range", "median")).round(2).to_string())
