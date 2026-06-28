"""
Python backtesting engine implementing the EMA+VWAP strategy exactly as specified.
Operates on pre-fetched OHLCV data (list of dicts from data_fetcher.py).

Note on 1M entry tier: the Python engine uses 5M data only.
Entry is assumed at the NEXT 5M bar's open after a valid signal,
approximating the 1M precision tier. This slightly understates performance
since the actual 1M entry provides a marginally better price.
This is documented as a known limitation of the Python simulation layer.

All times are UTC in the data. Session gate converts to UK time internally.
"""

import bisect
import math
from datetime import datetime, timezone, timedelta
from typing import Optional

# ── Session gate (mirrors SessionGate.cs) ─────────────────────────────────────

def _to_uk(utc: datetime) -> datetime:
    """Convert UTC datetime to UK wall-clock time (approximate DST: GMT+1 Apr–Oct)."""
    month = utc.month
    offset = 1 if 4 <= month <= 10 else 0
    return utc + timedelta(hours=offset)


def _in_trading_window_ger40(utc: datetime) -> bool:
    t = _to_uk(utc).time()
    from datetime import time as dtime
    w1 = dtime(8, 0) <= t < dtime(11, 30)
    w2 = dtime(13, 0) <= t < dtime(16, 0)
    return w1 or w2


def _in_trading_window_us500(utc: datetime) -> bool:
    t = _to_uk(utc).time()
    from datetime import time as dtime
    return dtime(14, 0) <= t < dtime(17, 30)


def _past_session_close_ger40(utc: datetime) -> bool:
    from datetime import time as dtime
    return _to_uk(utc).time() >= dtime(16, 30)


def _past_session_close_us500(utc: datetime) -> bool:
    from datetime import time as dtime
    return _to_uk(utc).time() >= dtime(18, 0)


# ── VWAP (mirrors VwapCalculator.cs) ─────────────────────────────────────────

class VwapState:
    __slots__ = ("cum_tpv", "cum_sq_tpv", "cum_vol", "vwap",
                 "sd1u", "sd1l", "sd2u", "sd2l", "session_date")

    def __init__(self):
        self.cum_tpv = self.cum_sq_tpv = self.cum_vol = 0.0
        self.vwap = self.sd1u = self.sd1l = self.sd2u = self.sd2l = 0.0
        self.session_date = None

    def update(self, bar_date, high, low, close, volume):
        if bar_date != self.session_date:
            self.cum_tpv = self.cum_sq_tpv = self.cum_vol = 0.0
            self.session_date = bar_date

        if volume <= 0:
            return

        tp = (high + low + close) / 3.0
        self.cum_tpv    += tp * volume
        self.cum_sq_tpv += tp * tp * volume
        self.cum_vol    += volume

        vwap    = self.cum_tpv / self.cum_vol
        variance = max(0.0, self.cum_sq_tpv / self.cum_vol - vwap ** 2)
        std     = math.sqrt(variance)

        self.vwap = vwap
        self.sd1u = vwap + std
        self.sd1l = vwap - std
        self.sd2u = vwap + 2 * std
        self.sd2l = vwap - 2 * std

    @property
    def is_valid(self):
        return self.cum_vol > 0


# ── EMA ────────────────────────────────────────────────────────────────────────

def calc_ema_series(values: list[float], period: int) -> list[float]:
    """Standard EMA with alpha = 2/(period+1). Returns same-length list (NaN-padded)."""
    alpha  = 2.0 / (period + 1)
    result = [float("nan")] * len(values)
    started = False
    ema = 0.0
    for i, v in enumerate(values):
        if math.isnan(v):
            continue
        if not started:
            ema = v
            started = True
        else:
            ema = alpha * v + (1 - alpha) * ema
        result[i] = ema
    return result


# ── ATR ─────────────────────────────────────────────────────────────────────────

def calc_atr_series(bars: list[dict], period: int) -> list[float]:
    """Wilder's ATR (alpha = 1/period)."""
    alpha = 1.0 / period
    n = len(bars)
    result = [float("nan")] * n
    atr = float("nan")

    for i in range(1, n):
        h, l, pc = bars[i]["high"], bars[i]["low"], bars[i - 1]["close"]
        tr = max(h - l, abs(h - pc), abs(l - pc))
        if math.isnan(atr):
            atr = tr
        else:
            atr = alpha * tr + (1 - alpha) * atr
        result[i] = atr

    return result


# ── Main backtest function ─────────────────────────────────────────────────────

def run_backtest(
    bars_5m: list[dict],
    bars_1h: list[dict],
    start_date: datetime,
    end_date:   datetime,
    params: dict,
    instrument: str = "GER40",
    _5m_times: list = None,
    _1h_times: list = None,
) -> dict:
    """
    Run one backtest on the given 5M and 1H data within [start_date, end_date].

    params keys:
        ema_fast (int), ema_slow (int), atr_period (int),
        atr_multiplier (float), min_body_pct (float),
        max_entry_dist_atr (float), max_trades_per_day (int)

    _5m_times / _1h_times: pre-computed time lists for O(log n) bisect slicing.
        Pass these from the WFO engine to avoid rebuilding them per call.

    Returns dict with: net_profit, profit_factor, sharpe_ratio, win_rate,
                       max_drawdown, total_trades, trades (list of dicts)
    """
    # ── Extract params ────────────────────────────────────────────────────────
    ema_fast            = int(params.get("ema_fast", 9))
    ema_slow            = int(params.get("ema_slow", 21))
    atr_period          = int(params.get("atr_period", 14))
    atr_multiplier      = float(params.get("atr_multiplier", 1.5))
    min_body_pct        = float(params.get("min_body_pct", 40.0))
    max_entry_dist_atr  = float(params.get("max_entry_dist_atr", 1.0))
    max_trades_per_day  = int(params.get("max_trades_per_day", 3))
    ema_bias_period     = 21  # fixed per spec

    in_window = _in_trading_window_ger40 if instrument == "GER40" else _in_trading_window_us500
    past_close = _past_session_close_ger40 if instrument == "GER40" else _past_session_close_us500

    # ── Filter 5M bars to [start_date, end_date] + lookback ─────────────────
    lookback_days = max(ema_slow, atr_period, ema_bias_period) * 2
    warmup_start  = start_date - timedelta(days=lookback_days)

    # Use bisect if time arrays provided (O(log n)); else fall back to list comprehension
    if _5m_times is not None:
        i0 = bisect.bisect_left(_5m_times, warmup_start)
        i1 = bisect.bisect_right(_5m_times, end_date)
        bars5 = bars_5m[i0:i1]
    else:
        bars5 = [b for b in bars_5m if warmup_start <= b["time"] <= end_date]

    ws1h = warmup_start - timedelta(days=5)
    if _1h_times is not None:
        j0 = bisect.bisect_left(_1h_times, ws1h)
        j1 = bisect.bisect_right(_1h_times, end_date)
        bars1h_all = bars_1h[j0:j1]
    else:
        bars1h_all = [b for b in bars_1h if ws1h <= b["time"] <= end_date]

    if not bars5 or not bars1h_all:
        return _empty_result()

    # ── Pre-calculate indicators on full arrays ───────────────────────────────
    closes5    = [b["close"] for b in bars5]
    ema9_arr   = calc_ema_series(closes5, ema_fast)
    ema21_arr  = calc_ema_series(closes5, ema_slow)
    atr_arr    = calc_atr_series(bars5, atr_period)

    closes1h   = [b["close"] for b in bars1h_all]
    ema21_1h   = calc_ema_series(closes1h, ema_bias_period)

    # ── Build 1H lookup: for each 5M bar time, find last completed 1H bar ────
    # A 1H bar at time T is complete at T + 1H; so last completed at 5M time X
    # is the most recent 1H bar whose open_time + 1H <= X

    h1_times  = [b["time"] for b in bars1h_all]
    h1_close_times = [t + timedelta(hours=1) for t in h1_times]

    def _last_completed_1h(bar5_time: datetime) -> Optional[int]:
        # Binary search: find rightmost close_time <= bar5_time
        lo, hi = 0, len(h1_close_times) - 1
        res = None
        while lo <= hi:
            mid = (lo + hi) // 2
            if h1_close_times[mid] <= bar5_time:
                res = mid
                lo = mid + 1
            else:
                hi = mid - 1
        return res

    # ── Simulation state ──────────────────────────────────────────────────────
    vwap_state   = VwapState()
    equity       = 10_000.0   # normalised starting equity (R-multiples internally)
    peak_equity  = equity
    trades       = []
    daily_trades: dict[str, int] = {}
    daily_equity: dict[str, float] = {}

    in_trade      = False
    direction     = None      # "long" or "short"
    entry_price   = 0.0
    sl_price      = 0.0       # moves to BE after TP1
    orig_sl_price = 0.0       # fixed at entry; used for all R calculations
    tp1_price     = 0.0
    tp2_price     = 0.0
    tp1_hit       = False
    risk_amount   = equity * 0.01   # 1% per trade (reset each trade from current equity)

    signal_pending     = False
    signal_direction   = None
    signal_vwap        = 0.0
    signal_atr         = 0.0
    signal_tp1         = 0.0
    signal_tp2         = 0.0
    bars_waited        = 0

    # ── Main loop ─────────────────────────────────────────────────────────────
    for i in range(1, len(bars5)):
        bar = bars5[i]
        if bar["time"] < start_date:
            # Warmup period: update VWAP and move on (do not trade)
            bar_date = bar["time"].date()
            vwap_state.update(bar_date, bar["high"], bar["low"], bar["close"], bar["volume"])
            continue

        if bar["time"] > end_date:
            break

        bar_date   = bar["time"].date()
        bar_date_s = str(bar_date)
        prev_bar   = bars5[i - 1]

        # Update VWAP with current bar
        vwap_state.update(bar_date, bar["high"], bar["low"], bar["close"], bar["volume"])

        # Reset daily trade count
        if bar_date_s not in daily_trades:
            daily_trades[bar_date_s] = 0
            daily_equity[bar_date_s] = equity

        # ── Session end: force-close all positions ────────────────────────────
        if past_close(bar["time"]):
            if in_trade:
                fraction = 0.5 if tp1_hit else 1.0
                pnl_r = _pnl_r(direction, bar["close"], entry_price, orig_sl_price, fraction)
                equity, peak_equity = _apply_pnl(equity, peak_equity, risk_amount, pnl_r, trades, bar,
                                                  entry_price, bar["close"], direction, "SESSION_END")
                in_trade = signal_pending = False
            continue

        # ── In-trade management ───────────────────────────────────────────────
        if in_trade:
            # Use bar's high/low to check TP/SL hits within bar
            sl_hit = (direction == "long"  and bar["low"]  <= sl_price) or \
                     (direction == "short" and bar["high"] >= sl_price)
            if sl_hit:
                # sl_price is either the original SL (-1R) or BE after TP1 (0R for remaining half)
                fraction = 0.5 if tp1_hit else 1.0
                pnl_r = _pnl_r(direction, sl_price, entry_price, orig_sl_price, fraction)
                equity, peak_equity = _apply_pnl(equity, peak_equity, risk_amount, pnl_r,
                                                  trades, bar, entry_price, sl_price, direction, "SL")
                in_trade = False
                signal_pending = False
                continue

            # Check TP1 (if not yet hit)
            if not tp1_hit:
                tp1_reached = (direction == "long"  and bar["high"] >= tp1_price) or \
                              (direction == "short" and bar["low"]  <= tp1_price)
                if tp1_reached:
                    tp1_hit = True
                    # Close 50%: compute actual R vs original stop, apply to equity
                    tp1_pnl_r = _pnl_r(direction, tp1_price, entry_price, orig_sl_price, 0.5)
                    equity, peak_equity = _apply_pnl(equity, peak_equity, risk_amount, tp1_pnl_r,
                                                      trades, bar, entry_price, tp1_price, direction, "TP1")
                    sl_price = entry_price   # move SL to break-even
                    continue

            # Check TP2
            tp2_reached = (direction == "long"  and bar["high"] >= tp2_price) or \
                          (direction == "short" and bar["low"]  <= tp2_price)
            if tp2_reached:
                # Remaining half (or full if TP1 not hit) at TP2 price
                fraction = 0.5 if tp1_hit else 1.0
                pnl_r = _pnl_r(direction, tp2_price, entry_price, orig_sl_price, fraction)
                equity, peak_equity = _apply_pnl(equity, peak_equity, risk_amount, pnl_r,
                                                  trades, bar, entry_price, tp2_price, direction, "TP2")
                in_trade = False
                continue

            # Check EMA/VWAP reversion (on this bar's close)
            ema9_now  = ema9_arr[i]
            vwap_now  = vwap_state.vwap
            reverted = (direction == "long"  and (bar["close"] < ema9_now or bar["close"] < vwap_now)) or \
                       (direction == "short" and (bar["close"] > ema9_now or bar["close"] > vwap_now))
            if reverted and math.isfinite(ema9_now):
                fraction = 0.5 if tp1_hit else 1.0
                pnl_r = _pnl_r(direction, bar["close"], entry_price, orig_sl_price, fraction)
                equity, peak_equity = _apply_pnl(equity, peak_equity, risk_amount, pnl_r,
                                                  trades, bar, entry_price, bar["close"], direction, "REVERSION")
                in_trade = False
                continue

            continue  # still in trade, no exit triggered

        # ── 1M-approximation: enter on next bar after pending signal ─────────
        if signal_pending:
            bars_waited += 1
            if bars_waited > 3:
                signal_pending = False
                continue

            # Entry condition: next 5M bar qualifies (price near VWAP)
            dist = abs(bar["open"] - signal_vwap)
            if dist <= max_entry_dist_atr * signal_atr:
                # Entry at bar open
                ep   = bar["open"]
                raw_sl = ep - atr_multiplier * signal_atr if signal_direction == "long" \
                        else ep + atr_multiplier * signal_atr
                sl_dist = abs(ep - raw_sl)
                if sl_dist < 0.5 * signal_atr or sl_dist > 2.5 * signal_atr:
                    signal_pending = False
                    continue

                in_trade      = True
                direction     = signal_direction
                entry_price   = ep
                sl_price      = raw_sl
                orig_sl_price = raw_sl   # fixed reference; sl_price may move to BE
                tp1_price     = signal_tp1
                tp2_price     = signal_tp2
                tp1_hit       = False
                risk_amount   = equity * 0.01  # 1% of current equity
                signal_pending = False
                daily_trades[bar_date_s] = daily_trades.get(bar_date_s, 0) + 1
            else:
                signal_pending = False
            continue

        # ── Signal evaluation (on completed bar[i]) ───────────────────────────
        if not vwap_state.is_valid:
            continue

        ema9  = ema9_arr[i]
        ema21 = ema21_arr[i]
        atr   = atr_arr[i]

        if math.isnan(ema9) or math.isnan(ema21) or math.isnan(atr):
            continue
        if not in_window(bar["time"]):
            continue
        if daily_trades.get(bar_date_s, 0) >= max_trades_per_day:
            continue

        # 1H bias gate
        h1_idx = _last_completed_1h(bar["time"])
        if h1_idx is None or math.isnan(ema21_1h[h1_idx]):
            continue

        c1h  = bars1h_all[h1_idx]["close"]
        e1h  = ema21_1h[h1_idx]
        flat = e1h * 0.0005

        long_bias  = c1h > e1h + flat
        short_bias = c1h < e1h - flat

        if not long_bias and not short_bias:
            continue

        # Body filter
        c5 = bar["close"]
        o5 = bar["open"]
        h5 = bar["high"]
        l5 = bar["low"]
        rng = h5 - l5
        if rng <= 0:
            continue
        body_pct = abs(c5 - o5) / rng * 100.0
        if body_pct < min_body_pct:
            continue

        vwap_v = vwap_state.vwap

        # Long signal (L1-L8)
        if long_bias and c5 > ema9 and c5 > ema21 and c5 > vwap_v and ema9 > ema21:
            signal_pending   = True
            signal_direction = "long"
            signal_vwap      = vwap_v
            signal_atr       = atr
            signal_tp1       = vwap_state.sd1u
            signal_tp2       = vwap_state.sd2u
            bars_waited      = 0
            continue

        # Short signal (S1-S8)
        if short_bias and c5 < ema9 and c5 < ema21 and c5 < vwap_v and ema9 < ema21:
            signal_pending   = True
            signal_direction = "short"
            signal_vwap      = vwap_v
            signal_atr       = atr
            signal_tp1       = vwap_state.sd1l
            signal_tp2       = vwap_state.sd2l
            bars_waited      = 0
            continue

    # Force-close any still-open position at end of period
    if in_trade and bars5:
        last_bar = bars5[-1]
        fraction = 0.5 if tp1_hit else 1.0
        pnl_r = _pnl_r(direction, last_bar["close"], entry_price, orig_sl_price, fraction)
        equity, peak_equity = _apply_pnl(equity, peak_equity, risk_amount, pnl_r,
                                          trades, last_bar, entry_price, last_bar["close"], direction, "PERIOD_END")

    return _calc_statistics(trades, equity, peak_equity)


# ── Result helpers ────────────────────────────────────────────────────────────

def _pnl_r(direction: str, exit_price: float, entry_price: float,
           orig_sl_price: float, position_fraction: float = 1.0) -> float:
    """Compute P&L in R-multiples using the original (fixed) stop distance."""
    orig_risk = abs(entry_price - orig_sl_price)
    if orig_risk <= 0:
        return 0.0
    signed_move = (exit_price - entry_price) if direction == "long" else (entry_price - exit_price)
    return signed_move / orig_risk * position_fraction


def _apply_pnl(equity, peak_equity, risk_amount, pnl_r, trades, bar,
               entry_price, exit_price, direction, exit_type):
    trade_pnl = pnl_r * risk_amount
    equity += trade_pnl
    if equity > peak_equity:
        peak_equity = equity
    trades.append({
        "exit_time":   bar["time"],
        "exit_price":  exit_price,
        "direction":   direction,
        "entry_price": entry_price,
        "exit_type":   exit_type,
        "pnl_r":       pnl_r,
        "pnl_gbp":     trade_pnl,
    })
    return equity, peak_equity


def _calc_statistics(trades: list[dict], final_equity: float, peak_equity: float) -> dict:
    closed = [t for t in trades if t.get("exit_type")]
    if not closed:
        return _empty_result()

    pnls = [t["pnl_r"] for t in closed]
    n    = len(pnls)
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p < 0]

    gross_profit = sum(wins)
    gross_loss   = abs(sum(losses))
    net_profit   = gross_profit - gross_loss
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float("inf")
    win_rate     = len(wins) / n

    # Max drawdown from equity curve
    running_eq   = 10_000.0
    peak_eq      = running_eq
    max_dd       = 0.0
    for p in pnls:
        running_eq += p * 100  # 1% of 10k = 100
        if running_eq > peak_eq:
            peak_eq = running_eq
        dd = (peak_eq - running_eq) / peak_eq if peak_eq > 0 else 0
        if dd > max_dd:
            max_dd = dd

    # Annualised Sharpe (daily R-multiple returns)
    import statistics
    if n < 2:
        sharpe = 0.0
    else:
        try:
            mean_r  = statistics.mean(pnls)
            std_r   = statistics.stdev(pnls)
            sharpe  = (mean_r / std_r * math.sqrt(252)) if std_r > 0 else 0.0
        except Exception:
            sharpe = 0.0

    recovery_factor = net_profit / max_dd if max_dd > 0 else float("inf")

    return {
        "net_profit":      net_profit,
        "profit_factor":   profit_factor,
        "sharpe_ratio":    sharpe,
        "win_rate":        win_rate,
        "max_drawdown":    max_dd,
        "total_trades":    n,
        "recovery_factor": recovery_factor,
        "gross_profit":    gross_profit,
        "gross_loss":      gross_loss,
        "trades":          trades,
    }


def _empty_result() -> dict:
    return {
        "net_profit": 0, "profit_factor": 0, "sharpe_ratio": 0,
        "win_rate": 0, "max_drawdown": 0, "total_trades": 0,
        "recovery_factor": 0, "gross_profit": 0, "gross_loss": 0,
        "trades": [],
    }
