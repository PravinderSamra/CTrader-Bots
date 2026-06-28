"""
Monte Carlo Bootstrap Resampling engine — Section 10 of specification.
2,000 simulations sampling N trades WITH replacement from the OOS trade list.
Records equity paths, drawdowns, profit factors, and losing streaks.
"""

import math
import os
import json
import random
from typing import Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

from config import (
    MC_SIMULATIONS, MC_RANDOM_SEED, MC_DIR,
    MC_MIN_PROB_PROFIT, MC_MAX_RUIN_5PCT, MC_MAX_RUIN_10PCT,
    MC_MAX_MEDIAN_DD, MC_MAX_P95_DD, MC_MIN_MEDIAN_PF,
    MC_MAX_MEDIAN_STREAK, MC_MAX_P95_STREAK,
)

# ── Core simulation ───────────────────────────────────────────────────────────

def _run_one_simulation(pnl_r_list: list[float], rng: random.Random) -> dict:
    """Bootstrap resample and compute metrics for one simulation."""
    n      = len(pnl_r_list)
    sample = rng.choices(pnl_r_list, k=n)  # WITH replacement

    eq     = 100.0   # starting equity (R-normalised)
    peak   = eq
    max_dd = 0.0
    ruin_5  = False
    ruin_10 = False

    gross_pos = gross_neg = 0.0
    streak = cur_streak = 0

    for r in sample:
        eq += r
        if eq > peak:
            peak = eq
        dd = (peak - eq) / peak if peak > 0 else 0
        if dd > max_dd:
            max_dd = dd
        if dd >= 0.05:
            ruin_5  = True
        if dd >= 0.10:
            ruin_10 = True

        if r > 0:
            gross_pos += r
            cur_streak = 0
        elif r < 0:
            gross_neg += abs(r)
            cur_streak += 1
            if cur_streak > streak:
                streak = cur_streak
        else:
            cur_streak = 0

    pf = gross_pos / gross_neg if gross_neg > 0 else float("inf")
    pf = min(pf, 99.0)  # cap for display

    return {
        "final_equity":   eq,
        "max_drawdown":   max_dd,
        "profit_factor":  pf,
        "longest_streak": streak,
        "ruin_5pct":      ruin_5,
        "ruin_10pct":     ruin_10,
        "equity_path":    sample,  # keep for fan chart (subset of sims)
    }


# ── Main MC function ──────────────────────────────────────────────────────────

def run_monte_carlo(trades: list[dict], n_sims: int = None, verbose: bool = True) -> dict:
    """
    Run Monte Carlo resampling on the OOS trade list.

    trades: list of trade dicts (must have pnl_r key)
    Returns full MC metrics and pass/fail evaluation.
    """
    if n_sims is None:
        n_sims = MC_SIMULATIONS

    # Extract R-multiples from all closed trade records
    pnl_r = [t["pnl_r"] for t in trades if "pnl_r" in t and t.get("exit_type")]

    if len(pnl_r) < 10:
        return {"error": f"Insufficient OOS trades for MC ({len(pnl_r)} trades, need ≥ 10)"}

    if verbose:
        print(f"\n{'='*60}")
        print(f"MONTE CARLO: {n_sims:,} simulations | {len(pnl_r)} OOS trades")
        print(f"{'='*60}")

    rng = random.Random(MC_RANDOM_SEED)

    # ── Run simulations ────────────────────────────────────────────────────
    results = []
    equity_paths = []   # store paths for fan chart (sample every 20th)

    for i in range(n_sims):
        if verbose and i % 500 == 0:
            print(f"  [{i:4d}/{n_sims}] {i/n_sims*100:.0f}%…")

        r = _run_one_simulation(pnl_r, rng)
        results.append(r)
        if i % 20 == 0:
            equity_paths.append(r["equity_path"])

    if verbose:
        print(f"  [{n_sims}/{n_sims}] 100% — complete")

    # ── Compute percentile distributions ──────────────────────────────────
    finals   = sorted(r["final_equity"]   for r in results)
    drawdowns = sorted(r["max_drawdown"]  for r in results)
    pfs       = sorted(r["profit_factor"] for r in results)
    streaks   = sorted(r["longest_streak"] for r in results)

    def pct(lst, p):
        idx = max(0, min(len(lst) - 1, int(len(lst) * p / 100)))
        return lst[idx]

    prob_profit  = sum(1 for r in results if r["final_equity"] > 100) / n_sims
    ruin_5_prob  = sum(1 for r in results if r["ruin_5pct"])  / n_sims
    ruin_10_prob = sum(1 for r in results if r["ruin_10pct"]) / n_sims

    metrics = {
        "n_trades":       len(pnl_r),
        "n_sims":         n_sims,
        "prob_profit":    round(prob_profit, 4),
        "ruin_prob_5pct": round(ruin_5_prob, 4),
        "ruin_prob_10pct":round(ruin_10_prob, 4),
        # Final equity percentiles
        "final_equity_5th":  round(pct(finals,   5),  4),
        "final_equity_25th": round(pct(finals,  25),  4),
        "final_equity_50th": round(pct(finals,  50),  4),
        "final_equity_75th": round(pct(finals,  75),  4),
        "final_equity_95th": round(pct(finals,  95),  4),
        # Drawdown percentiles
        "max_dd_50th":   round(pct(drawdowns, 50), 4),
        "max_dd_95th":   round(pct(drawdowns, 95), 4),
        # Profit factor percentiles
        "pf_25th":       round(pct(pfs, 25), 4),
        "pf_50th":       round(pct(pfs, 50), 4),
        "pf_75th":       round(pct(pfs, 75), 4),
        # Losing streak percentiles
        "streak_50th":   int(pct(streaks, 50)),
        "streak_95th":   int(pct(streaks, 95)),
    }

    # ── Pass/fail evaluation ───────────────────────────────────────────────
    pass_fail = {
        "prob_profit":    ("PASS" if metrics["prob_profit"]     > MC_MIN_PROB_PROFIT   else "FAIL",
                           MC_MIN_PROB_PROFIT, metrics["prob_profit"]),
        "ruin_5pct":      ("PASS" if metrics["ruin_prob_5pct"]  < MC_MAX_RUIN_5PCT     else "FAIL",
                           MC_MAX_RUIN_5PCT,   metrics["ruin_prob_5pct"]),
        "ruin_10pct":     ("PASS" if metrics["ruin_prob_10pct"] < MC_MAX_RUIN_10PCT    else "FAIL",
                           MC_MAX_RUIN_10PCT,  metrics["ruin_prob_10pct"]),
        "median_max_dd":  ("PASS" if metrics["max_dd_50th"]     < MC_MAX_MEDIAN_DD     else "FAIL",
                           MC_MAX_MEDIAN_DD,   metrics["max_dd_50th"]),
        "p95_max_dd":     ("PASS" if metrics["max_dd_95th"]     < MC_MAX_P95_DD        else "FAIL",
                           MC_MAX_P95_DD,      metrics["max_dd_95th"]),
        "median_pf":      ("PASS" if metrics["pf_50th"]         > MC_MIN_MEDIAN_PF     else "FAIL",
                           MC_MIN_MEDIAN_PF,   metrics["pf_50th"]),
        "5th_equity":     ("PASS" if metrics["final_equity_5th"] > 100                 else "FAIL",
                           100.0,              metrics["final_equity_5th"]),
        "median_streak":  ("PASS" if metrics["streak_50th"]     < MC_MAX_MEDIAN_STREAK else "FAIL",
                           MC_MAX_MEDIAN_STREAK, metrics["streak_50th"]),
        "p95_streak":     ("PASS" if metrics["streak_95th"]     < MC_MAX_P95_STREAK    else "FAIL",
                           MC_MAX_P95_STREAK,  metrics["streak_95th"]),
    }

    all_pass = all(v[0] == "PASS" for v in pass_fail.values())

    if verbose:
        print(f"\nMC RESULTS:")
        print(f"  P(profit):          {prob_profit:.1%}  {'✓' if prob_profit > MC_MIN_PROB_PROFIT else '✗'}")
        print(f"  Ruin@5%:            {ruin_5_prob:.2%} {'✓' if ruin_5_prob < MC_MAX_RUIN_5PCT else '✗'}")
        print(f"  Ruin@10%:           {ruin_10_prob:.2%} {'✓' if ruin_10_prob < MC_MAX_RUIN_10PCT else '✗'}")
        print(f"  Median MaxDD:       {metrics['max_dd_50th']:.1%}  {'✓' if metrics['max_dd_50th'] < MC_MAX_MEDIAN_DD else '✗'}")
        print(f"  95th pct MaxDD:     {metrics['max_dd_95th']:.1%}  {'✓' if metrics['max_dd_95th'] < MC_MAX_P95_DD else '✗'}")
        print(f"  Median PF:          {metrics['pf_50th']:.3f}  {'✓' if metrics['pf_50th'] > MC_MIN_MEDIAN_PF else '✗'}")
        print(f"  5th pct Equity:     {metrics['final_equity_5th']:.1f}  {'✓' if metrics['final_equity_5th'] > 100 else '✗'}")
        print(f"  Median Streak:      {metrics['streak_50th']}  {'✓' if metrics['streak_50th'] < MC_MAX_MEDIAN_STREAK else '✗'}")
        print(f"  95th pct Streak:    {metrics['streak_95th']}  {'✓' if metrics['streak_95th'] < MC_MAX_P95_STREAK else '✗'}")
        print(f"\n  OVERALL: {'✅ ALL PASS' if all_pass else '❌ ONE OR MORE FAIL'}")
        print(f"{'='*60}\n")

    # ── Generate charts ────────────────────────────────────────────────────
    _generate_charts(finals, drawdowns, pfs, streaks, equity_paths, pnl_r, metrics, pass_fail)

    # ── Save results ───────────────────────────────────────────────────────
    mc_output = {
        "metrics":   metrics,
        "pass_fail": {k: {"status": v[0], "threshold": v[1], "measured": v[2]}
                      for k, v in pass_fail.items()},
        "all_pass":  all_pass,
    }
    with open(os.path.join(MC_DIR, "mc_results.json"), "w") as f:
        json.dump(mc_output, f, indent=2)

    return mc_output


# ── Chart generation ──────────────────────────────────────────────────────────

def _generate_charts(finals, drawdowns, pfs, streaks, equity_paths, pnl_r, metrics, pass_fail):
    """Generate all 5 required MC charts and save as PNGs."""
    n_trades = len(pnl_r)

    # 1. Equity Fan Chart
    _equity_fan_chart(equity_paths, metrics)

    # 2. Final Equity Histogram
    _histogram(finals, "Final Equity (R×100 normalised)", "mc_final_equity_hist.png",
               [metrics["final_equity_5th"], metrics["final_equity_95th"]],
               ["5th pct", "95th pct"], vline_ref=100, vline_label="Break-even (100)")

    # 3. Max Drawdown Histogram
    dd_pct = [d * 100 for d in drawdowns]
    _histogram(dd_pct, "Max Drawdown (%)", "mc_maxdd_hist.png",
               [metrics["max_dd_50th"] * 100, metrics["max_dd_95th"] * 100],
               ["Median", "95th pct"])

    # 4. Profit Factor Box Plot
    _boxplot(pfs, "Profit Factor (2,000 simulations)", "mc_pf_boxplot.png",
             threshold=1.30, threshold_label="Min threshold (1.30)")

    # 5. Ruin Probability Curve
    _ruin_curve(drawdowns)

    print(f"  MC charts saved → {MC_DIR}")


def _equity_fan_chart(equity_paths: list, metrics: dict):
    """Fan chart showing 5th/25th/50th/75th/95th percentile equity paths."""
    if not equity_paths:
        return

    max_len = max(len(p) for p in equity_paths)
    # Build equity curves from R-multiple paths
    curves = []
    for path in equity_paths[:200]:  # limit to 200 paths for chart
        eq = 100.0
        curve = [eq]
        for r in path:
            eq += r
            curve.append(eq)
        curves.append(curve)

    # Pad shorter curves
    for c in curves:
        while len(c) < max_len + 1:
            c.append(c[-1])

    curves = np.array(curves)
    pcts = np.percentile(curves, [5, 25, 50, 75, 95], axis=0)
    x = np.arange(pcts.shape[1])

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.fill_between(x, pcts[0], pcts[4], alpha=0.15, color="steelblue", label="5th–95th pct")
    ax.fill_between(x, pcts[1], pcts[3], alpha=0.25, color="steelblue", label="25th–75th pct")
    ax.plot(x, pcts[2], color="steelblue", linewidth=2, label="Median")
    ax.plot(x, pcts[0], color="red",       linewidth=1, linestyle="--", label="5th pct")
    ax.plot(x, pcts[4], color="green",     linewidth=1, linestyle="--", label="95th pct")
    ax.axhline(100, color="grey", linestyle=":", linewidth=1, label="Starting equity")
    ax.set_title("Monte Carlo Equity Fan Chart (2,000 simulations)")
    ax.set_xlabel("Trade Number")
    ax.set_ylabel("Equity (R×100 normalised)")
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(MC_DIR, "mc_equity_fan.png"), dpi=150)
    plt.close()


def _histogram(data, xlabel: str, filename: str,
               vlines: list, labels: list, vline_ref=None, vline_label=None):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(data, bins=60, color="steelblue", edgecolor="white", alpha=0.8)
    colors = ["red", "orange", "purple", "green"]
    for val, lbl, col in zip(vlines, labels, colors):
        ax.axvline(val, color=col, linewidth=2, linestyle="--", label=f"{lbl}: {val:.2f}")
    if vline_ref is not None:
        ax.axvline(vline_ref, color="black", linewidth=1.5, linestyle="-", label=vline_label)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Count")
    ax.set_title(f"Distribution: {xlabel}")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(MC_DIR, filename), dpi=150)
    plt.close()


def _boxplot(data, title: str, filename: str, threshold=None, threshold_label=None):
    fig, ax = plt.subplots(figsize=(8, 6))
    bp = ax.boxplot(data, vert=True, patch_artist=True,
                    boxprops=dict(facecolor="steelblue", alpha=0.7),
                    medianprops=dict(color="red", linewidth=2))
    if threshold is not None:
        ax.axhline(threshold, color="orange", linewidth=2, linestyle="--", label=threshold_label)
        ax.legend()
    ax.set_title(title)
    ax.set_ylabel("Profit Factor")
    ax.set_xticks([])
    ax.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    plt.savefig(os.path.join(MC_DIR, filename), dpi=150)
    plt.close()


def _ruin_curve(drawdowns: list):
    """P(ruin) vs ruin level from 1% to 20%."""
    n = len(drawdowns)
    levels  = [x / 100 for x in range(1, 21)]
    probs   = [sum(1 for d in drawdowns if d >= lvl) / n for lvl in levels]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot([l * 100 for l in levels], [p * 100 for p in probs],
            color="red", linewidth=2, marker="o", markersize=4)
    ax.axhline(5,  color="orange", linewidth=1, linestyle="--", label="5% threshold")
    ax.axhline(1,  color="green",  linewidth=1, linestyle="--", label="1% threshold")
    ax.fill_between([l * 100 for l in levels], [p * 100 for p in probs], 0,
                    alpha=0.15, color="red")
    ax.set_title("Ruin Probability Curve")
    ax.set_xlabel("Ruin Level (% drawdown)")
    ax.set_ylabel("P(Ruin) %")
    ax.set_xlim(1, 20)
    ax.set_ylim(0, max(max(probs) * 100 * 1.2, 10))
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(MC_DIR, "mc_ruin_curve.png"), dpi=150)
    plt.close()
