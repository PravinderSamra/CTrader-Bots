"""
Walk-Forward Optimisation engine — Section 9 of specification.

Process:
  For each IS/OOS window pair:
    1. Run full parameter grid on IS period
    2. Score and rank qualifying parameter sets
    3. Stability surface check on top-ranked set
    4. Apply selected set to OOS period
    5. Record all metrics

  After all passes:
    - Concatenate OOS trades chronologically
    - Count parameter selection frequency → consensus set
    - Evaluate combined OOS metrics against acceptance criteria
"""

import bisect
import csv
import json
import math
import multiprocessing
import os
from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Optional

from config import (
    WFO_IS_MONTHS, WFO_OOS_MONTHS, WFO_STEP_MONTHS,
    WFO_MIN_IS_TRADES, WFO_MIN_OOS_TRADES,
    IS_MIN_PROFIT_FACTOR, IS_MIN_WIN_RATE, IS_MAX_DRAWDOWN,
    COMPOSITE_WEIGHTS, STABILITY_SPIKE_PF_THRESHOLD,
    STABILITY_MAX_FAILING_NEIGHBOURS, WFO_DIR, DATA_START, DATA_END,
)
from parameter_grid import generate_grid, get_neighbours
from backtest_engine import run_backtest


# ── Multiprocessing pool state ────────────────────────────────────────────────

N_WORKERS = 4

# Module-level refs inherited by forked workers (set via _pool_setup before Pool())
_POOL_BARS5M:    list = []
_POOL_BARS1H:    list = []
_POOL_TIMES5M:   list = []
_POOL_TIMES1H:   list = []
_POOL_IS_START:  Optional[datetime] = None
_POOL_IS_END:    Optional[datetime] = None
_POOL_INSTRUMENT: str = ""


def _pool_setup(b5m, b1h, t5m, t1h, is_start, is_end, instrument) -> None:
    global _POOL_BARS5M, _POOL_BARS1H, _POOL_TIMES5M, _POOL_TIMES1H
    global _POOL_IS_START, _POOL_IS_END, _POOL_INSTRUMENT
    _POOL_BARS5M     = b5m
    _POOL_BARS1H     = b1h
    _POOL_TIMES5M    = t5m
    _POOL_TIMES1H    = t1h
    _POOL_IS_START   = is_start
    _POOL_IS_END     = is_end
    _POOL_INSTRUMENT = instrument


def _pool_eval(params: dict) -> tuple:
    result = run_backtest(
        _POOL_BARS5M, _POOL_BARS1H,
        _POOL_IS_START, _POOL_IS_END,
        params, _POOL_INSTRUMENT,
        _5m_times=_POOL_TIMES5M, _1h_times=_POOL_TIMES1H,
    )
    return params, result


# ── Window schedule ───────────────────────────────────────────────────────────

def _add_months(dt: datetime, months: int) -> datetime:
    m = dt.month - 1 + months
    year = dt.year + m // 12
    month = m % 12 + 1
    day = min(dt.day, [31,28,29,30,31,30,31,31,30,31,30,31][month-1])
    return dt.replace(year=year, month=month, day=day)


def build_window_schedule(data_start: datetime, data_end: datetime) -> list[dict]:
    """Generate all IS/OOS window pairs (rolling)."""
    windows = []
    is_start = data_start

    while True:
        is_end   = _add_months(is_start, WFO_IS_MONTHS)
        oos_start = is_end
        oos_end  = _add_months(oos_start, WFO_OOS_MONTHS)

        if oos_end > data_end:
            break

        windows.append({
            "pass":       len(windows) + 1,
            "is_start":   is_start,
            "is_end":     is_end,
            "oos_start":  oos_start,
            "oos_end":    oos_end,
        })

        is_start = _add_months(is_start, WFO_STEP_MONTHS)

    return windows


# ── Composite scoring ─────────────────────────────────────────────────────────

def _composite_score(result: dict) -> float:
    pf   = result.get("profit_factor",   0)
    sr   = result.get("sharpe_ratio",    0)
    wr   = result.get("win_rate",        0)
    rf   = result.get("recovery_factor", 0)

    # Cap extreme values to avoid score inflation
    pf  = min(pf, 10.0)
    sr  = min(sr, 5.0)
    wr  = min(wr, 1.0)
    rf  = min(rf, 20.0)

    return (pf  * COMPOSITE_WEIGHTS["profit_factor"]
          + sr  * COMPOSITE_WEIGHTS["sharpe_ratio"]
          + wr  * COMPOSITE_WEIGHTS["win_rate"]
          + rf  * COMPOSITE_WEIGHTS["recovery_factor"])


def _qualifies(result: dict) -> bool:
    """All four IS minimum thresholds must pass."""
    return (
        result.get("profit_factor", 0) > IS_MIN_PROFIT_FACTOR
        and result.get("win_rate",  0) > IS_MIN_WIN_RATE
        and result.get("max_drawdown", 1) < IS_MAX_DRAWDOWN
        and result.get("total_trades", 0) >= WFO_MIN_IS_TRADES
    )


# ── Stability check ───────────────────────────────────────────────────────────

def _stability_check(params: dict, bars_5m: list, bars_1h: list,
                     is_start: datetime, is_end: datetime,
                     instrument: str,
                     bars_5m_times: list = None, bars_1h_times: list = None) -> bool:
    """
    Returns True if the parameter set sits on a plateau (not a spike).
    A spike is detected when >= 2 neighbours have PF < threshold.
    """
    neighbours = get_neighbours(params)
    failing = 0

    for n_params in neighbours:
        result = run_backtest(bars_5m, bars_1h, is_start, is_end, n_params, instrument,
                              _5m_times=bars_5m_times, _1h_times=bars_1h_times)
        pf = result.get("profit_factor", 0)
        if pf < STABILITY_SPIKE_PF_THRESHOLD:
            failing += 1
        if failing >= STABILITY_MAX_FAILING_NEIGHBOURS:
            return False  # spike detected

    return True


# ── Main WFO engine ───────────────────────────────────────────────────────────

def run_wfo(
    bars_5m: list,
    bars_1h: list,
    instrument: str = "GER40",
    coarse_first: bool = True,
    verbose: bool = True,
) -> dict:
    """
    Run full Walk-Forward Optimisation.

    Returns:
        {
          "windows": [...],          # per-pass results
          "oos_trades": [...],       # all OOS trades concatenated
          "consensus_params": {...}, # most-frequently selected param set
          "oos_stats": {...},        # combined OOS statistics
          "param_frequencies": {},   # selection frequency per param set
        }
    """
    data_start = datetime(DATA_START.year, DATA_START.month, DATA_START.day, tzinfo=timezone.utc)
    data_end   = datetime(DATA_END.year,   DATA_END.month,   DATA_END.day,   tzinfo=timezone.utc)

    windows = build_window_schedule(data_start, data_end)

    if verbose:
        print(f"\n{'='*60}")
        print(f"WFO SCHEDULE: {len(windows)} passes | {instrument}")
        print(f"IS: {WFO_IS_MONTHS}M  OOS: {WFO_OOS_MONTHS}M  Step: {WFO_STEP_MONTHS}M")
        print(f"{'='*60}")
        for w in windows:
            print(f"  Pass {w['pass']}: IS {w['is_start'].date()}–{w['is_end'].date()} | "
                  f"OOS {w['oos_start'].date()}–{w['oos_end'].date()}")
        print()

    # Pre-compute time lists once for fast bisect slicing inside run_backtest
    bars_5m_times = [b["time"] for b in bars_5m]
    bars_1h_times = [b["time"] for b in bars_1h]

    all_oos_trades   = []
    pass_results     = []
    param_selections = []

    # Maximum possible lookback across all param combinations
    _MAX_LOOKBACK_DAYS = max(26, 18, 21) * 2 + 10   # 62 days

    for window in windows:
        pass_n    = window["pass"]
        is_start  = window["is_start"]
        is_end    = window["is_end"]
        oos_start = window["oos_start"]
        oos_end   = window["oos_end"]

        if verbose:
            print(f"\n{'─'*60}")
            print(f"PASS {pass_n}/{len(windows)} | IS: {is_start.date()}–{is_end.date()}")

        # Pre-slice bars to IS window + max lookback (once per pass, not per combo)
        is_warmup = is_start - timedelta(days=_MAX_LOOKBACK_DAYS)
        i0 = bisect.bisect_left(bars_5m_times, is_warmup)
        i1 = bisect.bisect_right(bars_5m_times, is_end)
        is_bars_5m   = bars_5m[i0:i1]
        is_times_5m  = bars_5m_times[i0:i1]

        j0 = bisect.bisect_left(bars_1h_times, is_warmup - timedelta(days=5))
        j1 = bisect.bisect_right(bars_1h_times, is_end)
        is_bars_1h   = bars_1h[j0:j1]
        is_times_1h  = bars_1h_times[j0:j1]

        # ── IS: Run parameter grid (parallel) ──────────────────────────────

        is_results = []
        grid = list(generate_grid(coarse=coarse_first))
        total = len(grid)

        if verbose:
            print(f"  Running {total:,} IS combinations on {N_WORKERS} workers…")

        # Set module-level state; workers inherit it via fork (Linux)
        _pool_setup(is_bars_5m, is_bars_1h, is_times_5m, is_times_1h,
                    is_start, is_end, instrument)

        with multiprocessing.Pool(N_WORKERS) as pool:
            batch = pool.map(_pool_eval, grid, chunksize=200)

        for params, result in batch:
            if _qualifies(result):
                score = _composite_score(result)
                is_results.append({
                    "params": params,
                    "score":  score,
                    **result,
                })

        if not is_results:
            if verbose:
                print(f"  PASS {pass_n}: No qualifying IS parameter sets. Skipping.")
            pass_results.append({
                "pass": pass_n, "is_start": is_start, "oos_start": oos_start,
                "status": "NO_QUALIFYING_SETS", "oos_stats": None,
            })
            continue

        # Sort by composite score descending
        is_results.sort(key=lambda r: r["score"], reverse=True)
        _save_is_results(pass_n, is_results)

        if verbose:
            print(f"  IS qualifying sets: {len(is_results)} | Top score: {is_results[0]['score']:.4f} "
                  f"| Best PF: {is_results[0]['profit_factor']:.3f}")

        # ── Stability surface check ─────────────────────────────────────────

        selected_params = None
        stability_passed = False

        for candidate in is_results[:10]:  # check top 10 only
            stable = _stability_check(
                candidate["params"], is_bars_5m, is_bars_1h, is_start, is_end, instrument,
                bars_5m_times=is_times_5m, bars_1h_times=is_times_1h,
            )
            if stable:
                selected_params = candidate["params"]
                stability_passed = True
                if verbose:
                    print(f"  Stability PASS: {_params_str(selected_params)}")
                break
            else:
                if verbose:
                    print(f"  Stability FAIL (spike): {_params_str(candidate['params'])}")

        if selected_params is None:
            if verbose:
                print(f"  PASS {pass_n}: No stable parameter set found. Using top-ranked anyway.")
            selected_params  = is_results[0]["params"]
            stability_passed = False

        param_selections.append(_params_key(selected_params))

        # ── OOS: Apply selected params to OOS period ────────────────────────

        if verbose:
            print(f"  Running OOS with: {_params_str(selected_params)}")

        # OOS: use full bars (OOS window is outside IS range)
        oos_warmup = oos_start - timedelta(days=_MAX_LOOKBACK_DAYS)
        oi0 = bisect.bisect_left(bars_5m_times, oos_warmup)
        oi1 = bisect.bisect_right(bars_5m_times, oos_end)
        oos_bars_5m  = bars_5m[oi0:oi1]
        oos_times_5m = bars_5m_times[oi0:oi1]
        oj0 = bisect.bisect_left(bars_1h_times, oos_warmup - timedelta(days=5))
        oj1 = bisect.bisect_right(bars_1h_times, oos_end)
        oos_bars_1h  = bars_1h[oj0:oj1]
        oos_times_1h = bars_1h_times[oj0:oj1]

        oos_result = run_backtest(oos_bars_5m, oos_bars_1h, oos_start, oos_end, selected_params, instrument,
                                  _5m_times=oos_times_5m, _1h_times=oos_times_1h)
        oos_trades = oos_result.get("trades", [])

        if verbose:
            nt = oos_result.get("total_trades", 0)
            pf = oos_result.get("profit_factor", 0)
            sr = oos_result.get("sharpe_ratio", 0)
            wr = oos_result.get("win_rate", 0)
            dd = oos_result.get("max_drawdown", 0)
            flag = " ⚠ LOW TRADES" if nt < WFO_MIN_OOS_TRADES else ""
            print(f"  OOS: {nt} trades | PF={pf:.3f} | Sharpe={sr:.3f} | WR={wr:.1%} | MaxDD={dd:.1%}{flag}")

        all_oos_trades.extend(oos_trades)

        is_top = is_results[0]
        pass_results.append({
            "pass":             pass_n,
            "is_start":         is_start.date().isoformat(),
            "is_end":           is_end.date().isoformat(),
            "oos_start":        oos_start.date().isoformat(),
            "oos_end":          oos_end.date().isoformat(),
            "selected_params":  selected_params,
            "stability_passed": stability_passed,
            "is_composite":     is_top["score"],
            "is_profit_factor": is_top["profit_factor"],
            "is_sharpe":        is_top["sharpe_ratio"],
            "is_win_rate":      is_top["win_rate"],
            "is_max_drawdown":  is_top["max_drawdown"],
            "is_trades":        is_top["total_trades"],
            "oos_profit_factor": oos_result.get("profit_factor", 0),
            "oos_sharpe":       oos_result.get("sharpe_ratio", 0),
            "oos_win_rate":     oos_result.get("win_rate", 0),
            "oos_max_drawdown": oos_result.get("max_drawdown", 0),
            "oos_trades":       oos_result.get("total_trades", 0),
            "status":           "OK",
        })

        # Save pass-level OOS results
        _save_oos_result(pass_n, oos_result)

    # ── Consensus parameter set ─────────────────────────────────────────────

    if not param_selections:
        return {"error": "No valid WFO passes", "windows": pass_results}

    freq         = Counter(param_selections)
    top_key      = freq.most_common(1)[0][0]
    top_count    = freq.most_common(1)[0][1]

    # Only use consensus if selected in > 1 pass (spec rule)
    if top_count == 1:
        if verbose:
            print("\n⚠ No parameter set selected more than once. Using most-common but flag as weak consensus.")

    # Reconstruct param dict from key
    consensus_params = _key_to_params(top_key)

    if verbose:
        print(f"\n{'='*60}")
        print(f"CONSENSUS PARAMS (selected {top_count}/{len(windows)} passes):")
        print(f"  {_params_str(consensus_params)}")

    # ── Combined OOS statistics ─────────────────────────────────────────────
    from backtest_engine import _calc_statistics, _empty_result
    oos_stats = _calc_statistics(all_oos_trades, 0, 0)

    if verbose:
        nt = oos_stats.get("total_trades", 0)
        pf = oos_stats.get("profit_factor", 0)
        sr = oos_stats.get("sharpe_ratio", 0)
        wr = oos_stats.get("win_rate", 0)
        dd = oos_stats.get("max_drawdown", 0)
        rf = oos_stats.get("recovery_factor", 0)
        print(f"COMBINED OOS: {nt} trades | PF={pf:.3f} | Sharpe={sr:.3f} | WR={wr:.1%} | MaxDD={dd:.1%} | RF={rf:.2f}")
        print(f"{'='*60}\n")

    _save_wfo_summary(pass_results, consensus_params, top_count, oos_stats, instrument)

    return {
        "windows":           pass_results,
        "oos_trades":        all_oos_trades,
        "consensus_params":  consensus_params,
        "consensus_count":   top_count,
        "oos_stats":         oos_stats,
        "param_frequencies": dict(freq),
    }


# ── Persistence helpers ───────────────────────────────────────────────────────

def _params_key(params: dict) -> str:
    return json.dumps({k: params[k] for k in sorted(params.keys())}, sort_keys=True)


def _key_to_params(key: str) -> dict:
    return json.loads(key)


def _params_str(params: dict) -> str:
    return (f"EMA{params['ema_fast']}/{params['ema_slow']} "
            f"ATR{params['atr_period']}×{params['atr_multiplier']} "
            f"Body{params['min_body_pct']:.0f}% "
            f"EntryDist{params['max_entry_dist_atr']} "
            f"MaxTrades{params['max_trades_per_day']}")


def _save_is_results(pass_n: int, results: list) -> None:
    path = os.path.join(WFO_DIR, f"pass_{pass_n:02d}_is_results.csv")
    if not results:
        return
    keys = ["score", "profit_factor", "sharpe_ratio", "win_rate",
            "max_drawdown", "recovery_factor", "total_trades"]
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        param_keys = sorted(results[0]["params"].keys())
        w.writerow(keys + param_keys)
        for r in results[:500]:  # top 500 only
            row = [round(r.get(k, 0), 6) for k in keys]
            row += [r["params"][pk] for pk in param_keys]
            w.writerow(row)


def _save_oos_result(pass_n: int, result: dict) -> None:
    trades = result.get("trades", [])
    path   = os.path.join(WFO_DIR, f"pass_{pass_n:02d}_oos_trades.csv")
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["exit_time", "direction", "entry_price", "exit_price",
                    "exit_type", "pnl_r", "pnl_gbp"])
        for t in trades:
            w.writerow([t.get("exit_time", ""), t.get("direction", ""),
                        t.get("entry_price", 0), t.get("exit_price", 0),
                        t.get("exit_type", ""), round(t.get("pnl_r", 0), 4),
                        round(t.get("pnl_gbp", 0), 2)])


def _save_wfo_summary(pass_results: list, consensus_params: dict,
                      consensus_count: int, oos_stats: dict, instrument: str) -> None:
    path = os.path.join(WFO_DIR, "wfo_summary.json")
    with open(path, "w") as f:
        json.dump({
            "instrument":      instrument,
            "passes":          pass_results,
            "consensus_params": consensus_params,
            "consensus_count": consensus_count,
            "combined_oos":    {k: v for k, v in oos_stats.items() if k != "trades"},
        }, f, indent=2, default=str)
    print(f"WFO summary saved → {path}")
