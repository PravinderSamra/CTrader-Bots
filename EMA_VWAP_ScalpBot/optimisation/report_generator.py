"""
Report generator — Section 12 of specification.
Produces WFO summary charts, MC charts, and acceptance criteria table.
Outputs PNG files in results/mc/ and results/reports/.
PDF generation requires fpdf2 (pip install fpdf2) — falls back to text if unavailable.
"""

import json
import math
import os
import csv
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

from config import (
    ACCEPTANCE_CRITERIA, WFO_DIR, MC_DIR, REPORT_DIR, DATA_START, DATA_END,
)


# ── WFO Report Charts ─────────────────────────────────────────────────────────

def generate_wfo_report(wfo_results: dict):
    """Generate all WFO report charts from Section 12.1."""
    passes = [p for p in wfo_results.get("windows", []) if p.get("status") == "OK"]

    if not passes:
        print("No valid WFO passes to report on.")
        return

    _plot_combined_oos_equity(wfo_results)
    _plot_is_oos_degradation(passes)
    _plot_parameter_stability_heatmap(passes)
    _plot_exit_type_analysis(wfo_results.get("oos_trades", []))
    _plot_time_of_day_analysis(wfo_results.get("oos_trades", []))
    _generate_acceptance_table(wfo_results)
    _generate_text_report(wfo_results)

    print(f"WFO report charts saved → {REPORT_DIR}")


def _plot_combined_oos_equity(wfo_results: dict):
    trades = [t for t in wfo_results.get("oos_trades", []) if t.get("exit_type")]
    if not trades:
        return

    eq  = 10_000.0
    curve = [eq]
    dd_curve = [0.0]
    peak = eq

    for t in trades:
        eq += t.get("pnl_r", 0) * 100
        if eq > peak:
            peak = eq
        dd = (peak - eq) / peak if peak > 0 else 0
        curve.append(eq)
        dd_curve.append(dd * 100)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True,
                                    gridspec_kw={"height_ratios": [3, 1]})

    x = range(len(curve))
    ax1.plot(x, curve, color="steelblue", linewidth=1.5)
    ax1.fill_between(x, min(curve), curve, alpha=0.1, color="steelblue")
    ax1.axhline(10_000, color="grey", linewidth=0.8, linestyle=":")
    ax1.set_title(f"Combined OOS Equity Curve — {DATA_START.year}–{DATA_END.year}")
    ax1.set_ylabel("Equity (£ normalised)")
    ax1.grid(True, alpha=0.3)

    ax2.fill_between(range(len(dd_curve)), dd_curve, 0, alpha=0.6, color="red")
    ax2.set_ylabel("Drawdown (%)")
    ax2.set_xlabel("Trade Number (OOS only, chronological)")
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(REPORT_DIR, "wfo_combined_oos_equity.png"), dpi=150)
    plt.close()


def _plot_is_oos_degradation(passes: list):
    labels = [f"P{p['pass']}" for p in passes]
    is_pf  = [p.get("is_profit_factor",  0) for p in passes]
    oos_pf = [p.get("oos_profit_factor", 0) for p in passes]
    ratios = [(i / o if o > 0 else 0) for i, o in zip(is_pf, oos_pf)]

    x = np.arange(len(labels))
    width = 0.35

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

    bars1 = ax1.bar(x - width/2, is_pf,  width, label="IS PF",  color="steelblue", alpha=0.8)
    bars2 = ax1.bar(x + width/2, oos_pf, width, label="OOS PF", color="coral",     alpha=0.8)
    ax1.axhline(1.30, color="green", linewidth=1, linestyle="--", label="Min PF 1.30")
    ax1.set_title("IS vs OOS Profit Factor per WFO Pass")
    ax1.set_xticks(x); ax1.set_xticklabels(labels)
    ax1.set_ylabel("Profit Factor")
    ax1.legend(); ax1.grid(True, alpha=0.3, axis="y")

    bar_colors = ["red" if r > 2.0 else "steelblue" for r in ratios]
    ax2.bar(x, ratios, color=bar_colors, alpha=0.8)
    ax2.axhline(2.0, color="red",    linewidth=1, linestyle="--", label="Max ratio 2.0×")
    ax2.axhline(1.5, color="orange", linewidth=1, linestyle="--", label="Target ratio 1.5×")
    ax2.set_title("IS/OOS Profit Factor Degradation Ratio")
    ax2.set_xticks(x); ax2.set_xticklabels(labels)
    ax2.set_ylabel("IS PF / OOS PF")
    ax2.legend(); ax2.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    plt.savefig(os.path.join(REPORT_DIR, "wfo_is_oos_degradation.png"), dpi=150)
    plt.close()


def _plot_parameter_stability_heatmap(passes: list):
    """Heatmap of OOS PF vs EMA Fast × EMA Slow combinations (across all passes)."""
    data = {}
    for p in passes:
        params = p.get("selected_params", {})
        ef = params.get("ema_fast", 0)
        es = params.get("ema_slow", 0)
        pf = p.get("oos_profit_factor", 0)
        key = (ef, es)
        if key not in data or pf > data[key]:
            data[key] = pf

    if not data:
        return

    ema_fasts = sorted(set(k[0] for k in data))
    ema_slows = sorted(set(k[1] for k in data))

    matrix = np.zeros((len(ema_slows), len(ema_fasts)))
    for i, es in enumerate(ema_slows):
        for j, ef in enumerate(ema_fasts):
            matrix[i, j] = data.get((ef, es), 0)

    fig, ax = plt.subplots(figsize=(10, 7))
    im = ax.imshow(matrix, cmap="RdYlGn", aspect="auto",
                   vmin=0.8, vmax=max(1.8, np.max(matrix)))
    ax.set_xticks(range(len(ema_fasts)));  ax.set_xticklabels(ema_fasts)
    ax.set_yticks(range(len(ema_slows)));  ax.set_yticklabels(ema_slows)
    ax.set_xlabel("EMA Fast Period")
    ax.set_ylabel("EMA Slow Period")
    ax.set_title("Parameter Stability Heatmap — OOS Profit Factor")
    plt.colorbar(im, ax=ax, label="OOS Profit Factor")
    plt.tight_layout()
    plt.savefig(os.path.join(REPORT_DIR, "wfo_stability_heatmap.png"), dpi=150)
    plt.close()


def _plot_exit_type_analysis(oos_trades: list):
    types = {}
    for t in oos_trades:
        et = t.get("exit_type", "UNKNOWN")
        if not et:
            continue
        types[et] = types.get(et, 0) + 1

    if not types:
        return

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Pie chart — trade count by exit type
    labels = list(types.keys())
    sizes  = list(types.values())
    colors = ["#2ecc71", "#3498db", "#e74c3c", "#f39c12", "#9b59b6"]
    ax1.pie(sizes, labels=labels, colors=colors[:len(labels)],
            autopct="%1.1f%%", startangle=140)
    ax1.set_title("Exit Type Distribution")

    # Bar chart — average PnL by exit type
    avg_pnl = {}
    for et in types:
        exit_trades = [t for t in oos_trades if t.get("exit_type") == et]
        if exit_trades:
            avg_pnl[et] = sum(t.get("pnl_r", 0) for t in exit_trades) / len(exit_trades)

    et_labels = list(avg_pnl.keys())
    et_vals   = [avg_pnl[l] for l in et_labels]
    bar_colors = ["green" if v > 0 else "red" for v in et_vals]
    ax2.bar(et_labels, et_vals, color=bar_colors, alpha=0.8)
    ax2.axhline(0, color="black", linewidth=0.8)
    ax2.set_title("Average P&L (R) by Exit Type")
    ax2.set_ylabel("Average R-Multiple")
    ax2.tick_params(axis="x", rotation=30)
    ax2.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    plt.savefig(os.path.join(REPORT_DIR, "wfo_exit_analysis.png"), dpi=150)
    plt.close()


def _plot_time_of_day_analysis(oos_trades: list):
    from datetime import timedelta

    hourly_count = {}
    hourly_pnl   = {}

    for t in oos_trades:
        if not t.get("exit_type"):
            continue
        et = t.get("exit_time")
        if not et:
            continue
        if isinstance(et, str):
            try:
                et = datetime.fromisoformat(et)
            except Exception:
                continue
        # Convert UTC → UK (approx)
        month = et.month
        offset = 1 if 4 <= month <= 10 else 0
        uk_time = et + timedelta(hours=offset)
        hour = uk_time.hour
        hourly_count[hour] = hourly_count.get(hour, 0) + 1
        hourly_pnl[hour]   = hourly_pnl.get(hour, 0.0) + t.get("pnl_r", 0)

    if not hourly_count:
        return

    hours = sorted(hourly_count.keys())
    counts = [hourly_count[h] for h in hours]
    avg_pnl = [hourly_pnl[h] / hourly_count[h] if hourly_count[h] > 0 else 0 for h in hours]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

    ax1.bar(hours, counts, color="steelblue", alpha=0.8)
    ax1.set_title("Trade Count by Hour (UK Time)")
    ax1.set_ylabel("Number of Trades")
    ax1.set_xlabel("Hour (UK)")
    ax1.set_xticks(hours)
    ax1.grid(True, alpha=0.3, axis="y")

    bar_colors = ["green" if p > 0 else "red" for p in avg_pnl]
    ax2.bar(hours, avg_pnl, color=bar_colors, alpha=0.8)
    ax2.axhline(0, color="black", linewidth=0.8)
    ax2.set_title("Average P&L (R) by Hour (UK Time)")
    ax2.set_ylabel("Average R-Multiple")
    ax2.set_xlabel("Hour (UK)")
    ax2.set_xticks(hours)
    ax2.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    plt.savefig(os.path.join(REPORT_DIR, "wfo_time_of_day.png"), dpi=150)
    plt.close()


# ── Acceptance Criteria Table ─────────────────────────────────────────────────

def _generate_acceptance_table(wfo_results: dict):
    """Print and save the 15-criterion acceptance table."""
    oos = wfo_results.get("oos_stats", {})
    mc  = {}
    mc_path = os.path.join(MC_DIR, "mc_results.json")
    if os.path.exists(mc_path):
        with open(mc_path) as f:
            mc_data = json.load(f)
            mc = mc_data.get("metrics", {})

    passes = [p for p in wfo_results.get("windows", []) if p.get("status") == "OK"]
    avg_is_pf  = sum(p.get("is_profit_factor",  0) for p in passes) / max(len(passes), 1)
    avg_oos_pf = sum(p.get("oos_profit_factor", 0) for p in passes) / max(len(passes), 1)
    is_oos_ratio = avg_is_pf / avg_oos_pf if avg_oos_pf > 0 else 99
    min_oos_per_pass = min((p.get("oos_trades", 0) for p in passes), default=0)

    measured = {
        "oos_profit_factor":    oos.get("profit_factor",   0),
        "oos_sharpe_ratio":     oos.get("sharpe_ratio",    0),
        "oos_win_rate":         oos.get("win_rate",        0),
        "oos_max_drawdown":     oos.get("max_drawdown",    1),
        "oos_recovery_factor":  oos.get("recovery_factor", 0),
        "oos_total_trades":     oos.get("total_trades",    0),
        "is_oos_pf_degradation": is_oos_ratio,
        "mc_prob_profit":       mc.get("prob_profit",    0),
        "mc_ruin_5pct":         mc.get("ruin_prob_5pct", 1),
        "mc_ruin_10pct":        mc.get("ruin_prob_10pct", 1),
        "mc_p95_max_dd":        mc.get("max_dd_95th",   1),
        "mc_median_pf":         mc.get("pf_50th",       0),
        "mc_5th_pct_equity":    mc.get("final_equity_5th", 0) / 100,
        "stability_check":      all(p.get("stability_passed", False) for p in passes),
        "min_oos_per_pass":     min_oos_per_pass,
    }

    # Lower-is-better criteria
    lower_better = {
        "oos_max_drawdown", "is_oos_pf_degradation",
        "mc_ruin_5pct", "mc_ruin_10pct", "mc_p95_max_dd"
    }

    rows = []
    all_mins_pass   = True
    all_targets_met = True

    for i, (key, thresh) in enumerate(ACCEPTANCE_CRITERIA.items(), 1):
        val   = measured.get(key, "N/A")
        mn    = thresh["min"]
        tgt   = thresh["target"]

        if key == "stability_check":
            min_pass = bool(val)
            tgt_pass = bool(val) if tgt is not None else True
        elif key in lower_better:
            min_pass = isinstance(val, (int, float)) and val < mn
            tgt_pass = (isinstance(val, (int, float)) and val < tgt) if tgt is not None else True
        else:
            min_pass = isinstance(val, (int, float)) and val > mn
            tgt_pass = (isinstance(val, (int, float)) and val > tgt) if tgt is not None else True

        status = "PASS" if min_pass else "FAIL"
        if not min_pass:
            all_mins_pass = False
        if not tgt_pass:
            all_targets_met = False

        rows.append({
            "num":        i,
            "key":        key,
            "min":        mn,
            "target":     tgt,
            "measured":   val,
            "status":     status,
            "target_met": tgt_pass,
        })

    # Print table
    print(f"\n{'='*80}")
    print(f"ACCEPTANCE CRITERIA — 15 CRITERIA (Section 13)")
    print(f"{'='*80}")
    print(f"{'#':>3}  {'Criterion':<35} {'Minimum':>10} {'Measured':>10}  Status")
    print(f"{'─'*80}")
    for r in rows:
        val_fmt = f"{r['measured']:.3f}" if isinstance(r["measured"], float) else str(r["measured"])
        min_fmt = f"{r['min']:.3f}"       if isinstance(r["min"],      float) else str(r["min"])
        symbol  = "✓" if r["status"] == "PASS" else "✗"
        print(f"{r['num']:>3}  {r['key']:<35} {min_fmt:>10} {val_fmt:>10}  {symbol} {r['status']}")
    print(f"{'─'*80}")

    # GREEN = all minimums AND all defined targets met
    # AMBER = all minimums met but some targets missed
    # RED   = any minimum failed
    if all_mins_pass and all_targets_met:
        verdict = "🟢 GREEN — Full Deploy"
    elif all_mins_pass:
        verdict = "🟡 AMBER — Reduced Deploy"
    else:
        verdict = "🔴 RED — Do Not Deploy"

    print(f"\nVERDICT: {verdict}")
    print(f"{'='*80}\n")

    # Save CSV
    path = os.path.join(REPORT_DIR, "acceptance_criteria.csv")
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["#", "Criterion", "Minimum", "Target", "Measured", "Status", "TargetMet"])
        for r in rows:
            w.writerow([r["num"], r["key"], r["min"], r["target"], r["measured"],
                        r["status"], r.get("target_met", "N/A")])

    return all_mins_pass, verdict


def _generate_text_report(wfo_results: dict):
    """Write a text summary report."""
    path = os.path.join(REPORT_DIR, "wfo_report.txt")
    oos  = wfo_results.get("oos_stats", {})
    cp   = wfo_results.get("consensus_params", {})

    with open(path, "w") as f:
        f.write("EMA + VWAP SCALPING BOT — WALK-FORWARD OPTIMISATION REPORT\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"Data Range: {DATA_START} to {DATA_END}\n\n")

        f.write("CONSENSUS PARAMETERS\n")
        f.write("─" * 40 + "\n")
        for k, v in cp.items():
            f.write(f"  {k}: {v}\n")
        f.write(f"  Selected in {wfo_results.get('consensus_count', 0)} of "
                f"{len(wfo_results.get('windows', []))} passes\n\n")

        f.write("COMBINED OOS PERFORMANCE\n")
        f.write("─" * 40 + "\n")
        f.write(f"  Total trades:    {oos.get('total_trades', 0)}\n")
        f.write(f"  Net Profit (R):  {oos.get('net_profit', 0):.4f}\n")
        f.write(f"  Profit Factor:   {oos.get('profit_factor', 0):.4f}\n")
        f.write(f"  Sharpe Ratio:    {oos.get('sharpe_ratio', 0):.4f}\n")
        f.write(f"  Win Rate:        {oos.get('win_rate', 0):.1%}\n")
        f.write(f"  Max Drawdown:    {oos.get('max_drawdown', 0):.1%}\n")
        f.write(f"  Recovery Factor: {oos.get('recovery_factor', 0):.4f}\n\n")

        f.write("WFO PASS SUMMARY\n")
        f.write("─" * 40 + "\n")
        for p in wfo_results.get("windows", []):
            if p.get("status") != "OK":
                f.write(f"  Pass {p['pass']}: {p.get('status', 'UNKNOWN')}\n")
                continue
            f.write(f"  Pass {p['pass']}: IS PF={p.get('is_profit_factor', 0):.3f} → "
                    f"OOS PF={p.get('oos_profit_factor', 0):.3f} | "
                    f"OOS trades={p.get('oos_trades', 0)} | "
                    f"Stable={p.get('stability_passed', False)}\n")

    print(f"Text report saved → {path}")
