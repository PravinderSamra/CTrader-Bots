#!/usr/bin/env python3
"""
EMA9/VWAP NAS100_SB Backtest
Strategy: EMA9 touch after VWAP breakout impulse
Account: £10,000 | Risk: £100/trade | TP: 2R
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timezone

DATA_DIR = "/home/user/CTrader-Bots/EMA9-VWAP-Backtest/data"

# ── 1. LOAD ALL DATA ─────────────────────────────────────────────────────────

def load_csv(path):
    df = pd.read_csv(path)
    return df[['timestamp_ms','datetime_utc','open','high','low','close','volume']]

def load_json_bars(path):
    with open(path) as f:
        d = json.load(f)
    bars = d['trendbars']
    rows = []
    for b in bars:
        ts = b['timestamp']
        dt = datetime.fromtimestamp(ts/1000, tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        rows.append({
            'timestamp_ms': ts,
            'datetime_utc': dt,
            'open':   b['open']  / 100000,
            'high':   b['high']  / 100000,
            'low':    b['low']   / 100000,
            'close':  b['close'] / 100000,
            'volume': b['volume']
        })
    return pd.DataFrame(rows)

frames = []

# CSV parts
for part in ['part1','part2','part3','part4','part5','part6']:
    p = f"{DATA_DIR}/{part}.csv"
    if os.path.exists(p):
        frames.append(load_csv(p))

# Gap A (Jan 14 – Feb 3)
for chunk in ['chunk_01','chunk_02','chunk_03','chunk_04']:
    p = f"{DATA_DIR}/raw/gap_a/{chunk}.json"
    if os.path.exists(p):
        frames.append(load_json_bars(p))

# Gap B (Mar 13 – Mar 15)
for chunk in ['chunk_01']:
    p = f"{DATA_DIR}/raw/gap_b/{chunk}.json"
    if os.path.exists(p):
        frames.append(load_json_bars(p))

# Gap C (May 13 – Jun 5)
for chunk in ['chunk_01','chunk_02','chunk_03','chunk_04']:
    p = f"{DATA_DIR}/raw/gap_c/{chunk}.json"
    if os.path.exists(p):
        frames.append(load_json_bars(p))

df = pd.concat(frames, ignore_index=True)
df = df.drop_duplicates(subset='timestamp_ms')
df = df.sort_values('timestamp_ms').reset_index(drop=True)

print(f"Loaded {len(df)} bars  |  {df['datetime_utc'].iloc[0]}  →  {df['datetime_utc'].iloc[-1]}")

# ── 2. COMPUTE INDICATORS ────────────────────────────────────────────────────

# EMA9 on close
def compute_ema(series, n=9):
    k = 2 / (n + 1)
    result = np.full(len(series), np.nan)
    for i in range(len(series)):
        if i < n - 1:
            continue
        elif i == n - 1:
            result[i] = series[i - n + 1:i + 1].mean()
        else:
            result[i] = series[i] * k + result[i - 1] * (1 - k)
    return result

df['ema9'] = compute_ema(df['close'].values)

# Daily VWAP (reset at UTC midnight)
df['dt'] = pd.to_datetime(df['timestamp_ms'], unit='ms', utc=True)
df['date'] = df['dt'].dt.date
df['typical_price'] = (df['high'] + df['low'] + df['close']) / 3
df['tp_vol'] = df['typical_price'] * df['volume']
df['cum_tp_vol'] = df.groupby('date')['tp_vol'].cumsum()
df['cum_vol']    = df.groupby('date')['volume'].cumsum()
df['vwap'] = df['cum_tp_vol'] / df['cum_vol']

# 20-bar volume MA
df['vol_ma20'] = df['volume'].rolling(20).mean()

df = df.reset_index(drop=True)
arr = df.to_dict('records')

# ── 3. BACKTEST ENGINE ───────────────────────────────────────────────────────

RISK_GBP   = 100.0   # £ per trade
TP_MULTIPLE = 2.0    # 2R take profit
SL_BUFFER   = 5.0    # points beyond touch-bar extreme

# Session filter: only trade 07:30–21:00 UTC (London open → NY close)
SESSION_START_H = 7
SESSION_START_M = 30
SESSION_END_H   = 21
SESSION_END_M   = 0

# Impulse: close deviates from EMA9 by ≥0.3% with volume > 1.5× avg
IMPULSE_EMA_PCT  = 0.003
IMPULSE_VOL_MULT = 1.5

# EMA9 touch: bar extreme within 0.25% of EMA9
TOUCH_THRESHOLD = 0.0025

# Max EMA9-VWAP crosses in last 10 bars before trade = choppy filter
CHOP_CROSSES_MAX = 2
CHOP_LOOKBACK    = 10

# Only 1st or 2nd touch after impulse
MAX_TOUCHES = 2

# Min bars between impulse bar and touch (impulse needs at least 1 bar to confirm)
MIN_IMPULSE_AGE = 1
MAX_IMPULSE_AGE = 12   # touches after 12 bars from impulse are stale

# Min/max SL distance in points
MIN_SL_DIST = 10.0
MAX_SL_DIST = 150.0

trades = []
account = 10_000.0

# State per direction
class SetupState:
    def __init__(self):
        self.impulse_bar   = None   # index of impulse bar
        self.touch_count   = 0
        self.touch_bar     = None
        self.in_trade      = False
        self.entry_price   = None
        self.sl_price      = None
        self.tp_price      = None
        self.trade_dir     = None
        self.entry_bar     = None
        self.stake         = None

long_st  = SetupState()
short_st = SetupState()

def in_session(bar):
    """Only trade during liquid London/NY hours 07:30–21:00 UTC."""
    dt = datetime.fromtimestamp(bar['timestamp_ms'] / 1000, tz=timezone.utc)
    minutes = dt.hour * 60 + dt.minute
    start = SESSION_START_H * 60 + SESSION_START_M
    end   = SESSION_END_H   * 60 + SESSION_END_M
    return start <= minutes < end

def count_crosses(arr, i, n=CHOP_LOOKBACK):
    """Count how many times EMA9 crossed VWAP in last n bars."""
    crosses = 0
    start = max(0, i - n)
    for j in range(start + 1, i + 1):
        prev = arr[j-1]
        curr = arr[j]
        if (prev['ema9'] < prev['vwap'] and curr['ema9'] >= curr['vwap']) or \
           (prev['ema9'] > prev['vwap'] and curr['ema9'] <= curr['vwap']):
            crosses += 1
    return crosses

def vwap_rising(arr, i, lookback=3):
    if i < lookback:
        return None
    return arr[i]['vwap'] > arr[i - lookback]['vwap']

def is_impulse_long(bar, prev_ema9, vol_ma20):
    """Strong bar up: close significantly above EMA9, high volume."""
    if np.isnan(prev_ema9) or vol_ma20 == 0 or np.isnan(vol_ma20):
        return False
    pct_above = (bar['close'] - prev_ema9) / prev_ema9
    high_vol   = bar['volume'] > IMPULSE_VOL_MULT * vol_ma20
    return pct_above >= IMPULSE_EMA_PCT and high_vol

def is_impulse_short(bar, prev_ema9, vol_ma20):
    if np.isnan(prev_ema9) or vol_ma20 == 0 or np.isnan(vol_ma20):
        return False
    pct_below = (prev_ema9 - bar['close']) / prev_ema9
    high_vol   = bar['volume'] > IMPULSE_VOL_MULT * vol_ma20
    return pct_below >= IMPULSE_EMA_PCT and high_vol

def touch_ema9_long(bar):
    """Wick touches EMA9 from above: low ≤ EMA9 + threshold, close > EMA9."""
    e = bar['ema9']
    if np.isnan(e):
        return False
    return bar['low'] <= e * (1 + TOUCH_THRESHOLD) and bar['close'] > e * (1 - 0.001)

def touch_ema9_short(bar):
    """Wick touches EMA9 from below: high ≥ EMA9 - threshold, close < EMA9."""
    e = bar['ema9']
    if np.isnan(e):
        return False
    return bar['high'] >= e * (1 - TOUCH_THRESHOLD) and bar['close'] < e * (1 + 0.001)

N = len(arr)

for i in range(25, N):
    bar  = arr[i]
    prev = arr[i - 1]

    e9     = bar['ema9']
    vwap   = bar['vwap']
    vm20   = bar['vol_ma20']

    if np.isnan(e9) or np.isnan(vwap) or np.isnan(vm20):
        continue

    # ── Manage open long trade ──────────────────────────────────────────────
    if long_st.in_trade:
        # Check TP / SL hit (use high/low of current bar)
        hit_tp = bar['high'] >= long_st.tp_price
        hit_sl = bar['low']  <= long_st.sl_price
        if hit_tp or hit_sl:
            # Determine which was hit first by comparing proximity to open
            if hit_tp and hit_sl:
                # Both hit same bar — conservative: SL wins
                result = 'loss'
            elif hit_tp:
                result = 'win'
            else:
                result = 'loss'
            pnl = RISK_GBP * TP_MULTIPLE if result == 'win' else -RISK_GBP
            account += pnl
            trades.append({
                'direction': 'long',
                'entry_bar': long_st.entry_bar,
                'exit_bar':  i,
                'entry_dt':  arr[long_st.entry_bar]['datetime_utc'],
                'exit_dt':   bar['datetime_utc'],
                'entry_px':  long_st.entry_price,
                'sl_px':     long_st.sl_price,
                'tp_px':     long_st.tp_price,
                'sl_dist':   long_st.entry_price - long_st.sl_price,
                'stake':     long_st.stake,
                'result':    result,
                'pnl':       pnl,
                'account':   account
            })
            long_st.in_trade = False
            long_st.impulse_bar  = None
            long_st.touch_count  = 0

    # ── Manage open short trade ─────────────────────────────────────────────
    if short_st.in_trade:
        hit_tp = bar['low']  <= short_st.tp_price
        hit_sl = bar['high'] >= short_st.sl_price
        if hit_tp or hit_sl:
            if hit_tp and hit_sl:
                result = 'loss'
            elif hit_tp:
                result = 'win'
            else:
                result = 'loss'
            pnl = RISK_GBP * TP_MULTIPLE if result == 'win' else -RISK_GBP
            account += pnl
            trades.append({
                'direction': 'short',
                'entry_bar': short_st.entry_bar,
                'exit_bar':  i,
                'entry_dt':  arr[short_st.entry_bar]['datetime_utc'],
                'exit_dt':   bar['datetime_utc'],
                'entry_px':  short_st.entry_price,
                'sl_px':     short_st.sl_price,
                'tp_px':     short_st.tp_price,
                'sl_dist':   short_st.sl_price - short_st.entry_price,
                'stake':     short_st.stake,
                'result':    result,
                'pnl':       pnl,
                'account':   account
            })
            short_st.in_trade = False
            short_st.impulse_bar  = None
            short_st.touch_count  = 0

    # Skip signal detection if in trade (no pyramiding)
    if long_st.in_trade and short_st.in_trade:
        continue

    rising = vwap_rising(arr, i)

    # ── LONG SIDE ───────────────────────────────────────────────────────────
    if not long_st.in_trade:
        # Detect / renew impulse (price above VWAP and VWAP rising)
        if bar['close'] > vwap and rising:
            if is_impulse_long(bar, prev['ema9'] if not np.isnan(prev['ema9']) else e9, vm20):
                long_st.impulse_bar = i
                long_st.touch_count = 0   # reset touch count on new impulse

        # Looking for touch after impulse
        if long_st.impulse_bar is not None and not long_st.in_trade:
            age = i - long_st.impulse_bar
            if MIN_IMPULSE_AGE <= age <= MAX_IMPULSE_AGE:
                # Conditions: above VWAP, VWAP rising, not choppy
                if bar['close'] > vwap and rising:
                    if count_crosses(arr, i) <= CHOP_CROSSES_MAX:
                        if touch_ema9_long(bar) and long_st.touch_count < MAX_TOUCHES:
                            long_st.touch_count += 1
                            long_st.touch_bar = i

        # Entry on next bar after touch signal
        if long_st.touch_bar == i - 1 and not long_st.in_trade and in_session(bar):
            touch = arr[long_st.touch_bar]
            entry_px = bar['open']
            sl_px    = touch['low'] - SL_BUFFER
            sl_dist  = entry_px - sl_px
            if MIN_SL_DIST <= sl_dist <= MAX_SL_DIST:
                tp_px    = entry_px + TP_MULTIPLE * sl_dist
                stake    = RISK_GBP / sl_dist
                long_st.in_trade    = True
                long_st.entry_price = entry_px
                long_st.sl_price    = sl_px
                long_st.tp_price    = tp_px
                long_st.entry_bar   = i
                long_st.stake       = stake

    # ── SHORT SIDE ──────────────────────────────────────────────────────────
    if not short_st.in_trade:
        if bar['close'] < vwap and rising is False:
            prev_e9 = prev['ema9'] if not np.isnan(prev['ema9']) else e9
            if is_impulse_short(bar, prev_e9, vm20):
                short_st.impulse_bar = i
                short_st.touch_count = 0

        if short_st.impulse_bar is not None and not short_st.in_trade:
            age = i - short_st.impulse_bar
            if MIN_IMPULSE_AGE <= age <= MAX_IMPULSE_AGE:
                if bar['close'] < vwap and rising is False:
                    if count_crosses(arr, i) <= CHOP_CROSSES_MAX:
                        if touch_ema9_short(bar) and short_st.touch_count < MAX_TOUCHES:
                            short_st.touch_count += 1
                            short_st.touch_bar = i

        if short_st.touch_bar == i - 1 and not short_st.in_trade and in_session(bar):
            touch = arr[short_st.touch_bar]
            entry_px = bar['open']
            sl_px    = touch['high'] + SL_BUFFER
            sl_dist  = sl_px - entry_px
            if MIN_SL_DIST <= sl_dist <= MAX_SL_DIST:
                tp_px    = entry_px - TP_MULTIPLE * sl_dist
                stake    = RISK_GBP / sl_dist
                short_st.in_trade    = True
                short_st.entry_price = entry_px
                short_st.sl_price    = sl_px
                short_st.tp_price    = tp_px
                short_st.entry_bar   = i
                short_st.stake       = stake

# ── 4. RESULTS ───────────────────────────────────────────────────────────────

trades_df = pd.DataFrame(trades)

if len(trades_df) == 0:
    print("\nNo trades generated. Check parameters.")
else:
    total   = len(trades_df)
    wins    = (trades_df['result'] == 'win').sum()
    losses  = (trades_df['result'] == 'loss').sum()
    win_pct = wins / total * 100
    total_pnl = trades_df['pnl'].sum()
    gross_win = trades_df[trades_df['result']=='win']['pnl'].sum()
    gross_loss = abs(trades_df[trades_df['result']=='loss']['pnl'].sum())
    pf = gross_win / gross_loss if gross_loss > 0 else float('inf')

    print("\n" + "═"*60)
    print("  EMA9/VWAP NAS100_SB BACKTEST — 6-MONTH RESULTS")
    print("  Dec 2025 – Jun 2026  |  H1 bars  |  2:1 R:R")
    print("═"*60)
    print(f"  Starting capital : £10,000.00")
    print(f"  Ending capital   : £{account:,.2f}")
    print(f"  Net P&L          : £{total_pnl:+,.2f}")
    print(f"  Total trades     : {total}")
    print(f"  Wins             : {wins}  ({win_pct:.1f}%)")
    print(f"  Losses           : {losses}  ({100-win_pct:.1f}%)")
    print(f"  Profit factor    : {pf:.2f}")
    print(f"  Risk/trade       : £{RISK_GBP:.0f}")
    print(f"  Avg win          : £{gross_win/wins:.2f}" if wins > 0 else "  Avg win         : N/A")
    print(f"  Avg loss         : -£{gross_loss/losses:.2f}" if losses > 0 else "  Avg loss        : N/A")
    print("═"*60)

    # Week-by-week breakdown
    trades_df['entry_dt_parsed'] = pd.to_datetime(trades_df['entry_dt'], utc=True)
    trades_df['week'] = trades_df['entry_dt_parsed'].dt.to_period('W')
    trades_df['week_start'] = trades_df['entry_dt_parsed'].dt.to_period('W').apply(lambda p: p.start_time)

    print("\n  WEEK-BY-WEEK BREAKDOWN")
    print(f"  {'Week Starting':<15} {'Trades':>7} {'W':>4} {'L':>4} {'P&L':>10}  Trades")
    print("  " + "-"*70)

    for week, wdf in trades_df.groupby('week'):
        ws    = wdf['week_start'].iloc[0].strftime('%d %b %Y')
        wt    = len(wdf)
        ww    = (wdf['result']=='win').sum()
        wl    = (wdf['result']=='loss').sum()
        wpnl  = wdf['pnl'].sum()
        # Compact trade list
        tlist = []
        for _, t in wdf.iterrows():
            entry_time = pd.to_datetime(t['entry_dt']).strftime('%d/%m %H:%M')
            sym = '✓' if t['result'] == 'win' else '✗'
            tlist.append(f"{sym} {t['direction'].upper()[0]} {entry_time} SL={t['sl_dist']:.0f}pt")
        print(f"  {ws:<15} {wt:>7} {ww:>4} {wl:>4}  £{wpnl:>+8.0f}  |  {'; '.join(tlist)}")

    print("═"*60)

    # Save trade log
    trades_df['entry_dt_parsed'] = trades_df['entry_dt_parsed'].astype(str)
    trades_df.drop(columns=['week','week_start','entry_bar','exit_bar'], errors='ignore').to_csv(
        f"{DATA_DIR}/../results/trade_log.csv", index=False
    )
    print(f"\n  Trade log saved to results/trade_log.csv")
