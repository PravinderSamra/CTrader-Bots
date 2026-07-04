"""Figure for the entry-execution experiment (M15 vs M5, breakout vs retest)."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import compare_entries as C

OUT = os.path.join(os.path.dirname(__file__), "..", "analysis")
INK, GRID = "#1b2733", "#d9dee3"
C1, C2, C3, C4 = "#2f7d5b", "#7fb4a0", "#2d5f8a", "#8fb2d0"
plt.rcParams.update({"font.size": 10, "axes.edgecolor": INK, "text.color": INK,
                     "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
                     "figure.facecolor": "white", "axes.facecolor": "white"})

m15 = C.load(C.DATA + "/GER40_M15_2y.csv")
m5 = C.load(C.DATA + "/GER40_M5_12m.csv")
lo = m5[0]["dt"]
sessions = C.segment(m15)


def build(mg):
    out = []
    for i in range(1, len(sessions)):
        prev, s = sessions[i - 1], sessions[i]
        if s[0]["dt"] < lo:
            continue
        pc = prev[-1]["c"]; o = s[0]["o"]; g = o - pc
        if g == 0:
            continue
        gp = g / pc * 100
        if not (mg <= abs(gp) <= 1.0):
            continue
        if (s[0]["dt"] - prev[-1]["dt"]).total_seconds() / 3600 > 40:
            continue
        out.append((o, pc, g > 0, False, s, s[0]["dt"], s[-1]["dt"]))
    return out


def run(setups, style, tf):
    tr = [C.run_session(s if tf == "M15" else C.m5_slice(m5, t0, t1), o, pc, up, wk, style)
          for o, pc, up, wk, s, t0, t1 in setups]
    return [x for x in tr if x]


def stats(tr):
    n = len(tr)
    if not n:
        return 0, 0, 0, 0
    wins = [t for t in tr if t["R"] > 0]
    exp = sum(t["R"] for t in tr) / n
    wr = 100 * len(wins) / n
    aw = sum(t["R"] for t in wins) / len(wins) if wins else 0
    return exp, wr, aw, n


thresholds = [0.10, 0.15, 0.25]
variants = [("breakout", "M15", C1), ("breakout", "M5", C2),
            ("break-retest", "M15", C3), ("break-retest", "M5", C4)]

fig, ax = plt.subplots(1, 2, figsize=(13.5, 5.6))
fig.suptitle("GER40 entry-execution experiment — same weekday-gap setups, 12-month common window",
             fontsize=13, fontweight="bold", y=0.99)

# panel (a): expectancy vs threshold
import numpy as np
x = np.arange(len(thresholds))
w = 0.2
for k, (st, tf, col) in enumerate(variants):
    ys = [stats(run(build(mg), st, tf))[0] for mg in thresholds]
    ax[0].bar(x + (k - 1.5) * w, ys, w, label=f"{st} · {tf}", color=col)
ax[0].axhline(0, color=INK, lw=0.8)
ax[0].set_xticks(x); ax[0].set_xticklabels([f"≥{t}%" for t in thresholds])
ax[0].set_xlabel("gap-size filter"); ax[0].set_ylabel("expectancy (R/trade)")
ax[0].set_title("(a) Expectancy — M5 doesn't help breakout; retest is higher-variance", fontweight="bold")
ax[0].legend(fontsize=8, ncol=2)

# panel (b): win% vs avg-winner (risk profile), at gap>=0.15%
setups = build(0.15)
ax[1].axhline(0, color=INK, lw=0.4)
offsets = {("breakout", "M15"): (8, 8), ("breakout", "M5"): (8, -22),
           ("break-retest", "M15"): (-6, -30), ("break-retest", "M5"): (8, 6)}
for st, tf, col in variants:
    e, wr, aw, n = stats(run(setups, st, tf))
    ax[1].scatter(wr, aw, s=150, color=col, edgecolor=INK, zorder=3)
    ax[1].annotate(f"{st}·{tf}  (exp {e:+.2f}R, n={n})", (wr, aw),
                   xytext=offsets[(st, tf)], textcoords="offset points", fontsize=8)
ax[1].set_xlim(28, 74); ax[1].set_ylim(0.3, 3.5)
ax[1].set_xlabel("win rate (%)"); ax[1].set_ylabel("average winner (R)")
ax[1].set_title("(b) Risk profile @ gap≥0.15%: breakout=high-win/small-R, retest=low-win/big-R",
                fontweight="bold", fontsize=10.5)

fig.tight_layout(rect=[0, 0, 1, 0.95])
p = os.path.join(OUT, "fig4_entry_experiment.png")
fig.savefig(p, dpi=130); plt.close(fig)
print("wrote", p)
