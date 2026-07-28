"""
London Range Breakout backtest engine (US30 / NAS100, M5).

Rule set (parametrised):
  1. London range = [min low, max high] of M5 bars inside a London-local window.
  2. After the NY cash open (09:30 ET), scan M5 bars in a breakout window.
  3. First bar that CLOSES beyond the range (+ optional buffer) AND passes the
     volume filter -> entry at that bar's close.
  4. Stop / target per config; simulate forward bar-by-bar to resolution.
  5. First qualifying breakout per day only (configurable).

Outcome per trade: TP / SL / TIMEOUT (session close), with R, points, MAE/MFE,
time-to-resolution and the breakout candle's volume stats.
"""
from dataclasses import dataclass, field, asdict
import pandas as pd
import numpy as np


@dataclass
class Config:
    instrument: str = "US30"
    # range window [start, end) in the hours of `range_ref` timezone
    range_ref: str = "london"      # "london" -> use lon_hour; "ny" -> use ny_hour
    lon_start: float = 3.0
    lon_end: float = 8.0
    # breakout scan window in NY local hours [start, end)
    bo_start: float = 9.5          # 09:30 NY open
    bo_end: float = 11.0
    entry_buffer_pts: float = 0.0  # close must exceed range by this many pts
    # volume filter
    vol_method: str = "none"       # none | trailing | premarket | zscore
    vol_lookback: int = 20
    vol_mult: float = 1.0          # for trailing/premarket: vol >= mult*avg
    vol_z: float = 1.0             # for zscore: z >= vol_z
    # stop method
    stop_method: str = "fixed"     # fixed | atr | range_edge
    stop_pts: float = 50.0         # fixed
    atr_mult: float = 1.0          # atr: stop = atr_mult * ATR14(M5)
    atr_len: int = 14
    range_buffer_pts: float = 0.0  # range_edge: stop = opposite range side +/- buffer
    # target
    rr: float = 2.0                # TP distance = rr * stop distance
    # session force-close (NY local hour) if unresolved
    session_end: float = 16.0
    one_per_day: bool = True
    same_bar_pessimistic: bool = True  # if a bar spans SL & TP, assume SL first
    # stop management (all levels expressed in R, 1R = initial stop distance)
    trail_mode: str = "none"      # none | be | step
    trail_step: float = 1.0       # step size in R (step mode): SL ratchets to (k-1)*step at k*step MFE
    be_trigger: float = 1.0       # R at which SL jumps to breakeven (be mode)


def _atr_m5(day_bars, idx, length):
    """ATR over the `length` M5 bars ending at position idx (in day_bars)."""
    lo = max(0, idx - length)
    seg = day_bars.iloc[lo:idx]
    if len(seg) < 2:
        return None
    tr = (seg["high"] - seg["low"]).values
    return float(np.mean(tr)) if len(tr) else None


def _passes_volume(cfg, day_bars, idx, premarket_avg):
    if cfg.vol_method == "none":
        return True, np.nan
    v = day_bars.iloc[idx]["volume"]
    if cfg.vol_method == "trailing":
        lo = max(0, idx - cfg.vol_lookback)
        seg = day_bars.iloc[lo:idx]["volume"]
        avg = seg.mean() if len(seg) else np.nan
        rel = v / avg if avg else np.nan
        return (avg is not np.nan and v >= cfg.vol_mult * avg), rel
    if cfg.vol_method == "premarket":
        rel = v / premarket_avg if premarket_avg else np.nan
        return (premarket_avg and v >= cfg.vol_mult * premarket_avg), rel
    if cfg.vol_method == "zscore":
        lo = max(0, idx - cfg.vol_lookback)
        seg = day_bars.iloc[lo:idx]["volume"]
        if len(seg) < 5:
            return False, np.nan
        z = (v - seg.mean()) / (seg.std(ddof=0) + 1e-9)
        return z >= cfg.vol_z, z
    return True, np.nan


def _trail_sl_R(cfg, mfe_R):
    """Candidate stop level in R given max favourable excursion so far.
    Returns None if the scheme does not move the stop yet."""
    if cfg.trail_mode == "be":
        return 0.0 if mfe_R >= cfg.be_trigger else None
    if cfg.trail_mode == "step":
        k = int(mfe_R // cfg.trail_step)     # steps reached
        return (k - 1) * cfg.trail_step if k >= 1 else None
    return None


def simulate_trade(day_bars, i, side, ep, sd, tp_dist, cfg):
    """Bar-by-bar to resolution with static or trailing stop.
    Pessimistic intrabar rule: the stop level in force during a bar is the one
    ratcheted from PRIOR bars (never raised by this bar's own extreme), and a bar
    that spans both stop and target is treated as a stop. Returns dict of outcome.
    1R = sd points; stop levels tracked in R and converted to price each bar."""
    tp = ep + tp_dist if side == "LONG" else ep - tp_dist
    sl_R = -1.0                                  # initial stop at -1R
    def sl_price(r): return ep + r * sd if side == "LONG" else ep - r * sd
    end_mask = day_bars["ny_hour"] <= cfg.session_end
    fut = day_bars.iloc[i + 1:][end_mask.iloc[i + 1:]]
    mfe_R = 0.0; mae_R = 0.0; bars_held = 0
    outcome = "TIMEOUT"; exit_R = None; moved = False
    for _, b in fut.iterrows():
        bars_held += 1
        sl = sl_price(sl_R)
        if side == "LONG":
            hit_sl = b["low"] <= sl; hit_tp = b["high"] >= tp
            bar_fav = b["high"] - ep; bar_adv = b["low"] - ep
        else:
            hit_sl = b["high"] >= sl; hit_tp = b["low"] <= tp
            bar_fav = ep - b["low"]; bar_adv = ep - b["high"]
        mae_R = min(mae_R, bar_adv / sd)
        if hit_sl and hit_tp:
            outcome = "SL" if cfg.same_bar_pessimistic else "TP"
            exit_R = sl_R if cfg.same_bar_pessimistic else cfg.rr
            break
        if hit_sl:
            outcome = "SL"; exit_R = sl_R; break
        if hit_tp:
            outcome = "TP"; exit_R = cfg.rr; break
        # no hit this bar -> register favourable excursion and ratchet stop
        mfe_R = max(mfe_R, bar_fav / sd)
        cand = _trail_sl_R(cfg, mfe_R)
        if cand is not None and cand > sl_R:
            sl_R = cand; moved = True
    if exit_R is None:  # timeout at last close
        last = fut.iloc[-1]["close"] if len(fut) else ep
        exit_R = ((last - ep) if side == "LONG" else (ep - last)) / sd
    # label: STOP that locked >= breakeven is a "TRAIL" exit
    if outcome == "SL" and sl_R > -1.0:
        outcome = "TRAIL"
    return dict(outcome=outcome, R=exit_R, bars_held=bars_held,
                mae_R=mae_R, mfe_R=mfe_R, moved=moved,
                final_sl_R=sl_R, exit_price=sl_price(exit_R) if outcome in ("SL", "TRAIL")
                else (tp if outcome == "TP" else ep + (exit_R * sd if side == "LONG" else -exit_R * sd)))


def run(df, cfg: Config):
    """df: output of sessions.load_m5. Returns (trades_df, summary dict)."""
    trades = []
    for day, day_bars in df.groupby("ny_date"):
        day_bars = day_bars.reset_index(drop=True)
        if cfg.dow_skip(day_bars):  # placeholder; see below
            pass
        # --- range (London-local or NY-anchored) ---
        rcol = "ny_hour" if cfg.range_ref == "ny" else "lon_hour"
        lon_mask = (day_bars[rcol] >= cfg.lon_start) & (day_bars[rcol] < cfg.lon_end)
        lr = day_bars[lon_mask]
        if len(lr) < 3:
            continue
        r_high = lr["high"].max()
        r_low = lr["low"].min()
        # premarket volume baseline: bars between range-end and breakout-scan start
        pm_mask = (day_bars["ny_hour"] < cfg.bo_start) & (day_bars[rcol] >= cfg.lon_end)
        pm_avg = day_bars[pm_mask]["volume"].mean() if pm_mask.any() else np.nan
        # --- breakout scan ---
        bo_mask = (day_bars["ny_hour"] >= cfg.bo_start) & (day_bars["ny_hour"] < cfg.bo_end)
        bo_idx = day_bars.index[bo_mask].tolist()
        entry = None
        for i in bo_idx:
            c = day_bars.iloc[i]["close"]
            side = None
            if c > r_high + cfg.entry_buffer_pts:
                side = "LONG"
            elif c < r_low - cfg.entry_buffer_pts:
                side = "SHORT"
            if side is None:
                continue
            ok, volrel = _passes_volume(cfg, day_bars, i, pm_avg)
            if not ok:
                continue
            # --- stop distance ---
            if cfg.stop_method == "fixed":
                stop_dist = cfg.stop_pts
            elif cfg.stop_method == "atr":
                a = _atr_m5(day_bars, i, cfg.atr_len)
                if not a:
                    continue
                stop_dist = cfg.atr_mult * a
            elif cfg.stop_method == "range_edge":
                stop_dist = (c - r_low + cfg.range_buffer_pts) if side == "LONG" \
                    else (r_high - c + cfg.range_buffer_pts)
                if stop_dist <= 0:
                    continue
            else:
                stop_dist = cfg.stop_pts
            # always-on volume features for the volume study (independent of filter)
            lo = max(0, i - 20)
            trail = day_bars.iloc[lo:i]["volume"]
            v = day_bars.iloc[i]["volume"]
            trail_rel = v / trail.mean() if len(trail) and trail.mean() else np.nan
            pm_rel = v / pm_avg if pm_avg and not np.isnan(pm_avg) else np.nan
            vz = (v - trail.mean()) / (trail.std(ddof=0) + 1e-9) if len(trail) >= 5 else np.nan
            entry = dict(i=i, side=side, price=c, stop_dist=stop_dist,
                         volrel=volrel, r_high=r_high, r_low=r_low,
                         range_w=r_high - r_low, pm_avg=pm_avg,
                         bo_vol=v, trail_rel=trail_rel, pm_rel=pm_rel, vz=vz)
            break  # first qualifying
        if entry is None:
            continue

        # --- simulate ---
        side = entry["side"]; ep = entry["price"]; sd = entry["stop_dist"]
        tp_dist = cfg.rr * sd
        sl0 = ep - sd if side == "LONG" else ep + sd
        tp = ep + tp_dist if side == "LONG" else ep - tp_dist
        sim = simulate_trade(day_bars, entry["i"], side, ep, sd, tp_dist, cfg)
        outcome = sim["outcome"]; r_mult = sim["R"]
        exit_price = sim["exit_price"]; bars_held = sim["bars_held"]
        pnl_pts = r_mult * sd
        trades.append({
            "date": str(day), "side": side, "entry_time_ny": str(day_bars.iloc[entry["i"]]["ny"]),
            "entry": round(ep, 2), "stop": round(sl0, 2), "target": round(tp, 2),
            "stop_dist": round(sd, 2), "tp_dist": round(tp_dist, 2),
            "outcome": outcome, "exit": round(exit_price, 2),
            "pnl_pts": round(pnl_pts, 2), "R": round(r_mult, 3),
            "bars_held": bars_held, "mins_held": bars_held * 5,
            "mae_pts": round(sim["mae_R"] * sd, 2), "mfe_pts": round(sim["mfe_R"] * sd, 2),
            "range_w": round(entry["range_w"], 2),
            "bo_vol": entry["bo_vol"],
            "vol_trail_rel": round(float(entry["trail_rel"]), 3) if pd.notna(entry["trail_rel"]) else np.nan,
            "vol_pm_rel": round(float(entry["pm_rel"]), 3) if pd.notna(entry["pm_rel"]) else np.nan,
            "vol_z": round(float(entry["vz"]), 3) if pd.notna(entry["vz"]) else np.nan,
            "pm_avg_vol": round(float(entry["pm_avg"]), 1) if pd.notna(entry["pm_avg"]) else np.nan,
            "dow": day_bars.iloc[entry["i"]]["dow"],
        })
    tdf = pd.DataFrame(trades)
    return tdf, summarize(tdf, cfg)


def summarize(tdf, cfg):
    if len(tdf) == 0:
        return {"trades": 0}
    wins = tdf[tdf["outcome"] == "TP"]
    losses = tdf[tdf["outcome"] == "SL"]
    timeouts = tdf[tdf["outcome"] == "TIMEOUT"]
    gross_win = tdf[tdf["R"] > 0]["R"].sum()
    gross_loss = -tdf[tdf["R"] < 0]["R"].sum()
    n = len(tdf)
    eq = tdf["R"].cumsum()
    dd = (eq - eq.cummax()).min()
    return {
        "instrument": cfg.instrument, "trades": n,
        "wins": len(wins), "losses": len(losses), "timeouts": len(timeouts),
        "win_rate": round(len(wins) / n, 4),
        "tp_rate": round(len(wins) / n, 4),
        "sl_rate": round(len(losses) / n, 4),
        "expectancy_R": round(tdf["R"].mean(), 4),
        "total_R": round(tdf["R"].sum(), 2),
        "profit_factor": round(gross_win / gross_loss, 3) if gross_loss else float("inf"),
        "avg_win_R": round(wins["R"].mean(), 3) if len(wins) else 0,
        "avg_loss_R": round(losses["R"].mean(), 3) if len(losses) else 0,
        "avg_mins_held": round(tdf["mins_held"].mean(), 1),
        "max_dd_R": round(float(dd), 2),
        "long_share": round((tdf["side"] == "LONG").mean(), 3),
    }


# convenience: allow cfg.dow_skip to be absent
Config.dow_skip = lambda self, day_bars: False
