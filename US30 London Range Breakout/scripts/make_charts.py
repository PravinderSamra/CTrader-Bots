"""
Charts for the London Range Breakout study. Reads analysis CSVs + regenerates
equity curves for chosen configs. Writes PNGs to ../charts/.
"""
import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sessions
import backtest as bt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANALYSIS = os.path.join(ROOT, "analysis")
CHARTS = os.path.join(ROOT, "charts")
os.makedirs(CHARTS, exist_ok=True)

C = {"US30": "#2563eb", "NAS100": "#e0803a", "win": "#3fae5a", "loss": "#d9524e",
     "grid": "#d0d0d0", "ink": "#1a1a1a"}
plt.rcParams.update({"figure.dpi": 130, "font.size": 10, "axes.edgecolor": "#888",
                     "axes.grid": True, "grid.color": C["grid"], "grid.alpha": 0.5,
                     "axes.axisbelow": True})


def _trades(inst, cfg):
    df = sessions.load_m5(os.path.join(ROOT, "data", inst, f"{inst.lower()}_m5.csv"))
    tdf, s = bt.run(df, cfg)
    return tdf, s


def equity_curve(configs):
    """configs: {inst: (label, Config)}"""
    fig, ax = plt.subplots(figsize=(9, 5))
    for inst, (label, cfg) in configs.items():
        tdf, s = _trades(inst, cfg)
        if not len(tdf):
            continue
        eq = tdf["R"].cumsum().values
        ax.plot(range(len(eq)), eq, color=C.get(inst, "#666"), lw=1.8,
                label=f"{inst} — {label}  (exp {s['expectancy_R']:+.2f}R, PF {s['profit_factor']}, n={s['trades']})")
    ax.axhline(0, color=C["ink"], lw=0.8)
    ax.set_xlabel("trade #"); ax.set_ylabel("cumulative R")
    ax.set_title("Equity curve (R-multiples)")
    ax.legend(fontsize=8, loc="upper left")
    fig.tight_layout(); fig.savefig(os.path.join(CHARTS, "equity_curve.png")); plt.close(fig)


def risk_heatmap(inst):
    p = os.path.join(ANALYSIS, f"{inst}_stage2_risk.csv")
    if not os.path.exists(p):
        return
    d = pd.read_csv(p)
    d = d[d["stop_method"] == "fixed"]
    piv = d.pivot(index="stop_param", columns="rr", values="expectancy_R")
    fig, ax = plt.subplots(figsize=(7, 4.5))
    im = ax.imshow(piv.values, cmap="RdYlGn", aspect="auto",
                   vmin=-abs(np.nanmax(np.abs(piv.values))), vmax=abs(np.nanmax(np.abs(piv.values))))
    ax.set_xticks(range(len(piv.columns))); ax.set_xticklabels(piv.columns)
    ax.set_yticks(range(len(piv.index))); ax.set_yticklabels(piv.index)
    ax.set_xlabel("RR target"); ax.set_ylabel("fixed stop (pts)")
    ax.set_title(f"{inst} — expectancy (R) by stop x RR")
    for i in range(len(piv.index)):
        for j in range(len(piv.columns)):
            v = piv.values[i, j]
            if not np.isnan(v):
                ax.text(j, i, f"{v:+.2f}", ha="center", va="center", fontsize=8)
    fig.colorbar(im, label="expectancy R")
    fig.tight_layout(); fig.savefig(os.path.join(CHARTS, f"{inst}_risk_heatmap.png")); plt.close(fig)


def volume_bars(inst):
    p = os.path.join(ANALYSIS, f"{inst}_outcome_by_vol_trail_rel.csv")
    if not os.path.exists(p):
        return
    d = pd.read_csv(p)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    x = range(len(d))
    ax.bar(x, d["win_rate"], color=C.get(inst, "#666"), alpha=0.85)
    ax.set_xticks(list(x)); ax.set_xticklabels([str(b) for b in d["bucket"]], fontsize=7, rotation=15)
    ax.set_ylabel("win rate"); ax.set_title(f"{inst} — win rate by breakout-candle volume (× trailing-20)")
    ax2 = ax.twinx(); ax2.plot(x, d["expectancy_R"], color=C["ink"], marker="o", lw=1.5)
    ax2.set_ylabel("expectancy R"); ax2.axhline(0, color="#999", lw=0.7, ls="--")
    fig.tight_layout(); fig.savefig(os.path.join(CHARTS, f"{inst}_volume_winrate.png")); plt.close(fig)


if __name__ == "__main__":
    base = {i: ("base 50/100 (2R)", bt.Config(instrument=i, stop_pts=50, rr=2.0)) for i in ["US30", "NAS100"]}
    equity_curve(base)
    for inst in ["US30", "NAS100"]:
        risk_heatmap(inst); volume_bars(inst)
    print("charts written to", CHARTS)
