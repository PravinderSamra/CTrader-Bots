"""
Chart generator for GEX and OI visualisations.
Produces matplotlib charts suitable for display in terminal or saving as PNG.
"""

import matplotlib
matplotlib.use("Agg")  # headless — no GUI required
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np
import os
from datetime import datetime


OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def plot_gex_by_strike(gex_result, save: bool = True) -> str:
    """
    Bar chart: Net GEX by strike.
    Green bars = positive GEX (dealer buying support)
    Red bars = negative GEX (dealer selling / amplifying moves)
    """
    df = gex_result.gex_by_strike.copy()
    spot = gex_result.spot_price

    # Focus on strikes within 5% of spot
    lower = spot * 0.94
    upper = spot * 1.06
    df = df[(df["strike"] >= lower) & (df["strike"] <= upper)]

    fig, ax = plt.subplots(figsize=(14, 7))

    colors = ["#00C851" if v >= 0 else "#FF4444" for v in df["net_gex_bn"]]
    bars = ax.bar(df["strike"], df["net_gex_bn"], color=colors, width=df["strike"].diff().median() * 0.8, alpha=0.85)

    # Spot price line
    ax.axvline(spot, color="white", linewidth=2, linestyle="--", label=f"Spot: {spot:,.0f}", zorder=5)

    # Max pain
    ax.axvline(gex_result.max_pain, color="#FFD700", linewidth=1.5, linestyle=":",
               label=f"Max Pain: {gex_result.max_pain:,.0f}", zorder=4)

    # Put wall / call wall
    if gex_result.put_wall:
        ax.axvline(gex_result.put_wall, color="#00BFFF", linewidth=1.5, linestyle="-.",
                   label=f"Put Wall: {gex_result.put_wall:,.0f}", zorder=4)
    if gex_result.call_wall:
        ax.axvline(gex_result.call_wall, color="#FF8C00", linewidth=1.5, linestyle="-.",
                   label=f"Call Wall: {gex_result.call_wall:,.0f}", zorder=4)

    # Zero line
    ax.axhline(0, color="white", linewidth=0.8, alpha=0.5)

    ax.set_facecolor("#1a1a2e")
    fig.patch.set_facecolor("#0f0f23")
    ax.tick_params(colors="white")
    ax.spines[:].set_color("#444")
    ax.title.set_color("white")
    ax.xaxis.label.set_color("white")
    ax.yaxis.label.set_color("white")

    regime_colour = {"PINNED": "#00C851", "NEUTRAL": "#FFD700", "TRENDING": "#FF4444"}
    colour = regime_colour.get(gex_result.regime, "white")

    ax.set_title(
        f"{gex_result.symbol} — Gamma Exposure by Strike\n"
        f"Total GEX: ${gex_result.total_gex:.2f}B  |  Regime: {gex_result.regime}",
        color="white", fontsize=13, pad=15
    )
    ax.set_xlabel("Strike Price", fontsize=10)
    ax.set_ylabel("Net GEX ($B)", fontsize=10)
    ax.set_xticks(df["strike"])
    ax.set_xticklabels([f"{k:,.0f}" for k in df["strike"]], rotation=90, ha="center", fontsize=7)
    ax.legend(loc="upper left", framealpha=0.3, labelcolor="white", fontsize=9)

    # Regime annotation
    ax.text(0.98, 0.96, gex_result.regime, transform=ax.transAxes,
            fontsize=14, color=colour, ha="right", va="top",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#1a1a2e", edgecolor=colour, alpha=0.8))

    plt.tight_layout()

    if save:
        filename = os.path.join(OUTPUT_DIR, f"gex_{gex_result.symbol}_{_timestamp()}.png")
        plt.savefig(filename, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
        plt.close()
        return filename
    plt.show()
    return ""


def plot_oi_distribution(oi_result, save: bool = True) -> str:
    """
    Stacked bar chart: Call OI (green) and Put OI (red) by strike.
    Spot price, max pain, and key levels marked.
    """
    df = oi_result.oi_by_strike.copy()
    spot = oi_result.spot_price

    lower = spot * 0.94
    upper = spot * 1.06
    df = df[(df["strike"] >= lower) & (df["strike"] <= upper)]

    if df.empty:
        return ""

    fig, ax = plt.subplots(figsize=(14, 7))
    width = df["strike"].diff().median() * 0.4

    ax.bar(df["strike"] - width / 2, df.get("CALL", 0) / 1000, width=width,
           color="#00C851", alpha=0.85, label="Call OI (×1000)")
    ax.bar(df["strike"] + width / 2, df.get("PUT", 0) / 1000, width=width,
           color="#FF4444", alpha=0.85, label="Put OI (×1000)")

    ax.axvline(spot, color="white", linewidth=2, linestyle="--", label=f"Spot: {spot:,.0f}", zorder=5)
    ax.axvline(oi_result.max_pain, color="#FFD700", linewidth=1.5, linestyle=":",
               label=f"Max Pain: {oi_result.max_pain:,.0f}", zorder=4)

    ax.set_facecolor("#1a1a2e")
    fig.patch.set_facecolor("#0f0f23")
    ax.tick_params(colors="white")
    ax.spines[:].set_color("#444")
    ax.title.set_color("white")
    ax.xaxis.label.set_color("white")
    ax.yaxis.label.set_color("white")

    pcr = oi_result.put_call_ratio
    pcr_colour = "#FF4444" if pcr > 1.2 else ("#FFD700" if pcr > 0.8 else "#00C851")

    ax.set_title(
        f"{oi_result.symbol} — Open Interest Distribution\n"
        f"P/C Ratio: {pcr:.2f}  |  Nearest Expiry: {oi_result.nearest_expiry}  |  Sentiment: {oi_result.sentiment}",
        color="white", fontsize=13, pad=15
    )
    ax.set_xlabel("Strike Price", fontsize=10)
    ax.set_ylabel("Open Interest (×1000 contracts)", fontsize=10)
    ax.set_xticks(df["strike"])
    ax.set_xticklabels([f"{k:,.0f}" for k in df["strike"]], rotation=90, ha="center", fontsize=7)
    ax.legend(loc="upper left", framealpha=0.3, labelcolor="white", fontsize=9)

    ax.text(0.98, 0.96, f"P/C: {pcr:.2f}", transform=ax.transAxes,
            fontsize=14, color=pcr_colour, ha="right", va="top",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#1a1a2e", edgecolor=pcr_colour, alpha=0.8))

    plt.tight_layout()

    if save:
        filename = os.path.join(OUTPUT_DIR, f"oi_{oi_result.symbol}_{_timestamp()}.png")
        plt.savefig(filename, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
        plt.close()
        return filename
    plt.show()
    return ""


def plot_combined_dashboard(gex_result, oi_result, macro: dict, save: bool = True) -> str:
    """
    2×2 dashboard: GEX chart, OI chart, macro data panel, and levels summary.
    """
    fig = plt.figure(figsize=(18, 12))
    fig.patch.set_facecolor("#0f0f23")

    # --- Subplot 1: GEX by strike ---
    ax1 = fig.add_subplot(2, 2, 1)
    df_gex = gex_result.gex_by_strike.copy()
    spot = gex_result.spot_price
    df_gex = df_gex[(df_gex["strike"] >= spot * 0.95) & (df_gex["strike"] <= spot * 1.05)]
    colors = ["#00C851" if v >= 0 else "#FF4444" for v in df_gex["net_gex_bn"]]
    ax1.bar(df_gex["strike"], df_gex["net_gex_bn"], color=colors,
            width=df_gex["strike"].diff().median() * 0.7, alpha=0.85)
    ax1.axvline(spot, color="white", linewidth=1.5, linestyle="--")
    if gex_result.put_wall:
        ax1.axvline(gex_result.put_wall, color="#00BFFF", linewidth=1, linestyle="-.")
    if gex_result.call_wall:
        ax1.axvline(gex_result.call_wall, color="#FF8C00", linewidth=1, linestyle="-.")
    ax1.axhline(0, color="white", linewidth=0.5, alpha=0.4)
    ax1.set_xticks(df_gex["strike"])
    ax1.set_xticklabels([f"{k:,.0f}" for k in df_gex["strike"]], rotation=90, ha="center", fontsize=6)
    _style_ax(ax1, f"{gex_result.symbol} — GEX by Strike (${gex_result.total_gex:.1f}B)", "Strike", "GEX ($B)")

    # --- Subplot 2: OI distribution ---
    ax2 = fig.add_subplot(2, 2, 2)
    df_oi = oi_result.oi_by_strike.copy()
    df_oi = df_oi[(df_oi["strike"] >= spot * 0.95) & (df_oi["strike"] <= spot * 1.05)]
    if not df_oi.empty:
        w = df_oi["strike"].diff().median() * 0.4
        ax2.bar(df_oi["strike"] - w / 2, df_oi.get("CALL", 0) / 1000, width=w, color="#00C851", alpha=0.85)
        ax2.bar(df_oi["strike"] + w / 2, df_oi.get("PUT", 0) / 1000, width=w, color="#FF4444", alpha=0.85)
    ax2.axvline(spot, color="white", linewidth=1.5, linestyle="--")
    ax2.axvline(oi_result.max_pain, color="#FFD700", linewidth=1, linestyle=":")
    if not df_oi.empty:
        ax2.set_xticks(df_oi["strike"])
        ax2.set_xticklabels([f"{k:,.0f}" for k in df_oi["strike"]], rotation=90, ha="center", fontsize=6)
    _style_ax(ax2, f"OI Distribution — P/C: {oi_result.put_call_ratio:.2f}  |  {oi_result.sentiment}", "Strike", "OI (×1000)")

    # --- Subplot 3: Macro panel ---
    ax3 = fig.add_subplot(2, 2, 3)
    ax3.set_facecolor("#1a1a2e")
    ax3.axis("off")
    vix = macro.get("vix", "N/A")
    yield_10y = macro.get("yield_10y", "N/A")
    gold = macro.get("gold_spot", "N/A")
    regime = gex_result.regime

    regime_colour = {"PINNED": "#00C851", "NEUTRAL": "#FFD700", "TRENDING": "#FF4444"}.get(regime, "white")
    vix_val = float(vix) if vix != "N/A" else 0
    vix_colour = "#00C851" if vix_val < 15 else ("#FFD700" if vix_val < 25 else "#FF4444")

    lines = [
        ("GEX Regime", regime, regime_colour),
        ("Net GEX", f"${gex_result.total_gex:.2f}B", "white"),
        ("VIX", f"{vix:.1f}" if isinstance(vix, float) else str(vix), vix_colour),
        ("10Y Yield", f"{yield_10y:.2f}%" if isinstance(yield_10y, float) else str(yield_10y), "white"),
        ("Gold Spot", f"${gold:,.2f}" if isinstance(gold, float) else str(gold), "#FFD700"),
        ("Put/Call", f"{oi_result.put_call_ratio:.2f}", "white"),
        ("Max Pain", f"{oi_result.max_pain:,.0f}", "#FFD700"),
        ("Put Wall", f"{gex_result.put_wall:,.0f}", "#00BFFF"),
        ("Call Wall", f"{gex_result.call_wall:,.0f}", "#FF8C00"),
    ]

    ax3.set_title("Macro Context", color="white", fontsize=11, pad=10)
    for i, (label, value, colour) in enumerate(lines):
        y_pos = 0.95 - i * 0.10
        ax3.text(0.05, y_pos, f"{label}:", transform=ax3.transAxes,
                 fontsize=11, color="#aaaaaa", va="top")
        ax3.text(0.55, y_pos, str(value), transform=ax3.transAxes,
                 fontsize=11, color=colour, va="top", fontweight="bold")

    # --- Subplot 4: Key levels summary ---
    ax4 = fig.add_subplot(2, 2, 4)
    ax4.set_facecolor("#1a1a2e")
    ax4.axis("off")
    ax4.set_title("Key Levels for Chart", color="white", fontsize=11, pad=10)

    level_lines = []
    for lvl in gex_result.resistance_levels[:3]:
        level_lines.append((f"R: {lvl:,.0f}", "#FF8C00", "⬆ Resistance (GEX)"))
    level_lines.append((f"Spot: {spot:,.0f}", "white", "Current Price"))
    for lvl in gex_result.support_levels[:3]:
        level_lines.append((f"S: {lvl:,.0f}", "#00BFFF", "⬇ Support (GEX)"))
    level_lines.append((f"Put Wall: {gex_result.put_wall:,.0f}", "#00BFFF", "Strong support"))
    level_lines.append((f"Call Wall: {gex_result.call_wall:,.0f}", "#FF8C00", "Strong resistance"))
    level_lines.append((f"Max Pain: {oi_result.max_pain:,.0f}", "#FFD700", "Expiry magnet"))

    for i, (label, colour, desc) in enumerate(level_lines):
        y_pos = 0.95 - i * 0.085
        ax4.text(0.05, y_pos, label, transform=ax4.transAxes,
                 fontsize=10, color=colour, va="top", fontweight="bold")
        ax4.text(0.40, y_pos, desc, transform=ax4.transAxes,
                 fontsize=9, color="#aaaaaa", va="top")

    plt.suptitle(
        f"GEX & OI Dashboard — {gex_result.symbol}  |  {datetime.now().strftime('%Y-%m-%d %H:%M')} UTC",
        color="white", fontsize=14, y=0.98
    )

    plt.tight_layout(rect=[0, 0, 1, 0.97])

    if save:
        filename = os.path.join(OUTPUT_DIR, f"dashboard_{gex_result.symbol}_{_timestamp()}.png")
        plt.savefig(filename, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
        plt.close()
        return filename
    plt.show()
    return ""


def _style_ax(ax, title: str, xlabel: str, ylabel: str):
    ax.set_facecolor("#1a1a2e")
    ax.tick_params(colors="white", labelsize=8)
    ax.spines[:].set_color("#444")
    ax.set_title(title, color="white", fontsize=10, pad=8)
    ax.set_xlabel(xlabel, color="white", fontsize=9)
    ax.set_ylabel(ylabel, color="white", fontsize=9)


def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M")
