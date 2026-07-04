"""Phase 2 figures: strategy equity curve, filter comparison, walk-forward stability."""
import os
from collections import defaultdict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import gapfade_strategy as g

OUT = os.path.join(os.path.dirname(__file__), "..", "analysis")
INK, GRID = "#1b2733", "#d9dee3"
POS, NEG, ACC, ACC2 = "#2f7d5b", "#b3452f", "#2d5f8a", "#c98a2b"
plt.rcParams.update({"font.size": 10, "axes.edgecolor": INK, "text.color": INK,
                     "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
                     "figure.facecolor": "white", "axes.facecolor": "white"})


def equity(trades):
    cum, x, y = 0.0, [], []
    for i, t in enumerate(sorted(trades, key=lambda z: z["date"]), 1):
        cum += t["R"]; x.append(i); y.append(cum)
    return x, y


def main(m15="GER40_M15_2y.csv"):
    rows = g.load(os.path.join(os.path.dirname(__file__), "..", "data", m15))

    def bt(mg, weekday):
        p = dict(g.DEFAULTS); p["MIN_GAP_PCT"] = mg
        tr = g.backtest(rows, p)
        return [t for t in tr if not t["weekend"]] if weekday else tr

    rec = bt(0.25, True)          # recommended
    allg = bt(0.15, False)        # naive all gaps
    wknd = [t for t in bt(0.15, False) if t["weekend"]]

    fig, ax = plt.subplots(2, 2, figsize=(13, 9))
    fig.suptitle("GER40 gap-fade strategy — 2-year walk-forward (M15, 2pt cost)",
                 fontsize=14, fontweight="bold", y=0.98)

    # (a) equity curves
    for tr, lab, col in [(rec, "RECOMMENDED: weekday-only, gap≥0.25%", POS),
                         (allg, "naive: all gaps ≥0.15%", ACC),
                         (wknd, "weekend gaps only (avoid)", NEG)]:
        x, y = equity(tr)
        ax[0,0].plot(x, y, label=f"{lab}  ({g.summ(tr)['tot']:+.0f}R)", color=col, lw=2)
    ax[0,0].axhline(0, color=INK, lw=0.8)
    ax[0,0].set_title("(a) Cumulative R by trade sequence", fontweight="bold")
    ax[0,0].set_xlabel("trade #"); ax[0,0].set_ylabel("cumulative R"); ax[0,0].legend(fontsize=8.5)

    # (b) filter comparison expectancy
    cfgs = [("all\n≥0.15%", bt(0.15, False)), ("all\n≥0.25%", bt(0.25, False)),
            ("weekday\n≥0.25%", bt(0.25, True)), ("weekend\n≥0.15%", wknd)]
    exps = [g.summ(t)["exp"] for _, t in cfgs]
    ns = [g.summ(t)["n"] for _, t in cfgs]
    bars = ax[0,1].bar([c[0] for c in cfgs], exps, color=[POS if e > 0 else NEG for e in exps])
    for b, n, e in zip(bars, ns, exps):
        ax[0,1].text(b.get_x()+b.get_width()/2, e + (0.012 if e >= 0 else -0.012),
                     f"{e:+.2f}R\nn={n}", ha="center", fontsize=8.5,
                     va="bottom" if e >= 0 else "top")
    ax[0,1].axhline(0, color=INK, lw=0.8)
    ax[0,1].set_ylim(-0.17, 0.33)
    ax[0,1].set_title("(b) Expectancy by filter", fontweight="bold")
    ax[0,1].set_ylabel("expectancy (R/trade)")

    # (c) quarter-by-quarter total R (recommended)
    byq = defaultdict(float)
    for t in rec:
        byq[f"{t['date'].year}Q{(t['date'].month-1)//3+1}"] += t["R"]
    qs = sorted(byq)
    vals = [byq[q] for q in qs]
    ax[1,0].bar(qs, vals, color=[POS if v > 0 else NEG for v in vals])
    ax[1,0].axhline(0, color=INK, lw=0.8)
    ax[1,0].set_title("(c) Recommended config — total R by calendar quarter", fontweight="bold")
    ax[1,0].set_ylabel("R"); plt.setp(ax[1,0].get_xticklabels(), rotation=45, ha="right")

    # (d) win% by day-of-week (context, note small samples)
    dows = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    byd = defaultdict(list)
    for t in bt(0.25, False):
        if t["dow"] < 5:
            byd[t["dow"]].append(t)
    wr = [g.summ(byd[d])["win"] if byd[d] else 0 for d in range(5)]
    nn = [len(byd[d]) for d in range(5)]
    bars = ax[1,1].bar(dows, wr, color=[NEG if d == 0 else POS for d in range(5)])
    for b, n in zip(bars, nn):
        ax[1,1].text(b.get_x()+b.get_width()/2, b.get_height()+1, f"n={n}", ha="center", fontsize=8.5)
    ax[1,1].axhline(50, color=INK, ls="--", lw=1)
    ax[1,1].set_title("(d) Win% by weekday (Mon=weekend gap, weakest)", fontweight="bold")
    ax[1,1].set_ylabel("win %"); ax[1,1].set_ylim(0, 100)

    fig.tight_layout(rect=[0, 0, 1, 0.96])
    p = os.path.join(OUT, "fig3_strategy_walkforward.png")
    fig.savefig(p, dpi=130); plt.close(fig); print("wrote", p)


if __name__ == "__main__":
    main()
