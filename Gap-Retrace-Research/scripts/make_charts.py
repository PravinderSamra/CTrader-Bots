"""Generate research figures into ../analysis/ from the saved data."""
import csv, glob, os
from datetime import datetime, timezone
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
OUT = os.path.join(os.path.dirname(__file__), "..", "analysis")
os.makedirs(OUT, exist_ok=True)

INK, GRID = "#1b2733", "#d9dee3"
UP, DOWN, ACC = "#2f7d5b", "#b3452f", "#2d5f8a"
plt.rcParams.update({"font.size": 10, "axes.edgecolor": INK, "axes.labelcolor": INK,
                     "text.color": INK, "xtick.color": INK, "ytick.color": INK,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
                     "figure.facecolor": "white", "axes.facecolor": "white"})


def load_daily(path):
    rows = []
    with open(path) as f:
        for r in csv.DictReader(f):
            rows.append({"dt": datetime.fromtimestamp(int(r["timestamp"]) / 1000, tz=timezone.utc),
                         "o": float(r["open"]), "h": float(r["high"]), "l": float(r["low"]), "c": float(r["close"])})
    rows.sort(key=lambda x: x["dt"]); return rows


def session_gaps(rows):
    g = []
    for i in range(1, len(rows)):
        a, b = rows[i-1], rows[i]
        if (b["dt"]-a["dt"]).total_seconds()/3600 <= 40:  # weekend/holiday only
            continue
        gp = b["o"]-a["c"]
        if gp == 0: continue
        up = gp > 0
        full = b["l"] <= a["c"] if up else b["h"] >= a["c"]
        g.append({"abs_pct": abs(gp/a["c"]*100), "full": full, "up": up,
                  "cont": (b["c"]-b["o"])*(1 if up else -1) > 0})
    return g


def fig1():
    files = sorted(glob.glob(os.path.join(DATA, "*_D1.csv")))
    data = {os.path.basename(p).replace("_D1.csv", ""): session_gaps(load_daily(p)) for p in files}
    order = ["GER40", "US500", "NAS100", "US30", "UK100", "XAUUSD"]
    order = [o for o in order if o in data]

    fig, ax = plt.subplots(2, 2, figsize=(13, 9))
    fig.suptitle("Weekend/holiday GAP-FILL statistics — cTrader/Pepperstone CFDs, 3 years",
                 fontsize=14, fontweight="bold", y=0.98)

    # (a) GER40 fill rate by gap-size bucket
    buckets = [(0, .25), (.25, .5), (.5, 1.0), (1.0, 99)]
    labels = ["<0.25%", "0.25-0.5%", "0.5-1.0%", ">1.0%"]
    ger = data["GER40"]
    rates, ns = [], []
    for lo, hi in buckets:
        sub = [x for x in ger if lo <= x["abs_pct"] < hi]
        rates.append(100*sum(x["full"] for x in sub)/len(sub) if sub else 0); ns.append(len(sub))
    bars = ax[0,0].bar(labels, rates, color=[UP if r >= 60 else DOWN for r in rates])
    for b, n, r in zip(bars, ns, rates):
        ax[0,0].text(b.get_x()+b.get_width()/2, r+1.5, f"{r:.0f}%\n(n={n})", ha="center", fontsize=9)
    ax[0,0].set_title("(a) GER40: gap-fill rate by gap size — small gaps fill, big gaps run", fontweight="bold")
    ax[0,0].set_ylabel("same-day full-fill rate (%)"); ax[0,0].set_ylim(0, 100)

    # (b) instrument comparison: fill rate (tradeable >=0.15%)
    fr, cnt = [], []
    for s in order:
        sub = [x for x in data[s] if x["abs_pct"] >= 0.15]
        fr.append(100*sum(x["full"] for x in sub)/len(sub) if sub else 0); cnt.append(len(sub))
    bars = ax[0,1].bar(order, fr, color=ACC)
    for b, c, r in zip(bars, cnt, fr):
        ax[0,1].text(b.get_x()+b.get_width()/2, r+1, f"{r:.0f}%\nn={c}", ha="center", fontsize=8.5)
    ax[0,1].set_title("(b) Same-day fill rate, gaps ≥0.15% (3y)", fontweight="bold")
    ax[0,1].set_ylabel("full-fill rate (%)"); ax[0,1].set_ylim(0, 90)
    ax[0,1].axhline(50, color=DOWN, ls="--", lw=1)

    # (c) GER40 intraday time-to-fill (from M15)
    tf = ttf_ger40()
    ax[1,0].hist(tf, bins=[0,30,60,90,120,180,240,360,600], color=UP, edgecolor="white")
    ax[1,0].set_title("(c) GER40 time-to-fill (M15, tradeable gaps) — most fills in first 1-2h",
                      fontweight="bold")
    ax[1,0].set_xlabel("minutes from session open to gap fill"); ax[1,0].set_ylabel("# gap days")

    # (d) fade vs go by instrument
    go = [100*sum(x["cont"] for x in [y for y in data[s] if y["abs_pct"] >= 0.15])/
          max(1, len([y for y in data[s] if y["abs_pct"] >= 0.15])) for s in order]
    fade = [100-g for g in go]
    x = range(len(order))
    ax[1,1].bar(x, go, label="closes WITH gap (go)", color=DOWN)
    ax[1,1].bar(x, fade, bottom=go, label="closes AGAINST gap (fade)", color=UP)
    ax[1,1].axhline(50, color=INK, ls=":", lw=1)
    ax[1,1].set_xticks(list(x)); ax[1,1].set_xticklabels(order)
    ax[1,1].set_title("(d) Directional close: most indices FADE the gap", fontweight="bold")
    ax[1,1].set_ylabel("% of gap days"); ax[1,1].legend(fontsize=8, loc="lower right"); ax[1,1].set_ylim(0, 100)

    fig.tight_layout(rect=[0, 0, 1, 0.96])
    p = os.path.join(OUT, "fig1_gap_statistics.png")
    fig.savefig(p, dpi=130); plt.close(fig); print("wrote", p)


def load_m15():
    rows = []
    with open(os.path.join(DATA, "GER40_M15.csv")) as f:
        for r in csv.DictReader(f):
            rows.append({"dt": datetime.fromtimestamp(int(r["timestamp"])/1000, tz=timezone.utc),
                         "o": float(r["open"]), "h": float(r["high"]), "l": float(r["low"]), "c": float(r["close"])})
    rows.sort(key=lambda x: x["dt"]); return rows


def seg(rows, void=60):
    ss, cur = [], [rows[0]]
    for i in range(1, len(rows)):
        if (rows[i]["dt"]-rows[i-1]["dt"]).total_seconds()/60 > void:
            ss.append(cur); cur = []
        cur.append(rows[i])
    if cur: ss.append(cur)
    return [s for s in ss if len(s) >= 10]


def ttf_ger40(min_gap=0.10):
    rows = load_m15(); ss = seg(rows); tf = []
    for i in range(1, len(ss)):
        pc = ss[i-1][-1]["c"]; s = ss[i]; o = s[0]["o"]; g = o-pc
        if g == 0 or abs(g)/pc*100 < min_gap: continue
        up = g > 0; t0 = s[0]["dt"]
        for b in s:
            if (up and b["l"] <= pc) or (not up and b["h"] >= pc):
                tf.append((b["dt"]-t0).total_seconds()/60); break
    return tf


def fig2_example():
    """Annotated real gap day: prior-day range + gap + fill on M15."""
    rows = load_m15(); ss = seg(rows)
    # find a clean weekday gap-up that filled, gap 0.2-0.5%, mid-dataset
    pick = None
    for i in range(2, len(ss)):
        pc = ss[i-1][-1]["c"]; s = ss[i]; o = s[0]["o"]; g = o-pc
        if g <= 0: continue
        gp = g/pc*100
        if not (0.20 <= gp <= 0.55): continue
        if s[0]["l"] > pc and any(b["l"] <= pc for b in s):  # opens above, later fills
            pick = (i, pc, s, ss[i-1]); break
    if not pick:
        print("no example found"); return
    i, pc, s, prev = pick
    ph = max(b["h"] for b in prev); pl = min(b["l"] for b in prev)
    o = s[0]["o"]
    fig, ax = plt.subplots(figsize=(13, 6.5))
    xs = [b["dt"] for b in s]
    for b in s:
        c = UP if b["c"] >= b["o"] else DOWN
        ax.plot([b["dt"], b["dt"]], [b["l"], b["h"]], color=c, lw=1)
        ax.plot([b["dt"], b["dt"]], [b["o"], b["c"]], color=c, lw=4, solid_capstyle="butt")
    slo = min(b["l"] for b in s); shi = max(b["h"] for b in s)
    lo = min(slo, pc); hi = max(shi, ph); pad = (hi - lo) * 0.12
    ax.set_ylim(lo - pad, hi + pad)
    ax.axhline(pc, color=ACC, lw=1.6, ls="--")
    ax.axhline(ph, color="#888", lw=1.1, ls=":")
    ax.axhspan(pc, o, color=UP, alpha=0.10)
    ax.annotate("prior-day CLOSE = gap-fill target", (xs[0], pc), xytext=(6, -14),
                textcoords="offset points", color=ACC, fontsize=10, fontweight="bold")
    ax.annotate(f"prior-day HIGH (wick)  |  prior-day LOW {pl:.0f} (below, range {ph-pl:.0f} pts)",
                (xs[-1], ph), xytext=(-330, 5), textcoords="offset points", color="#555", fontsize=9)
    ax.annotate(f"GAP UP  +{o-pc:.0f} pts ({(o-pc)/pc*100:.2f}%)\nopen", (xs[0], o),
                xytext=(10, 18), textcoords="offset points", fontsize=10, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=INK))
    ax.set_title(f"GER40 (DAX) — annotated gap-up day {s[0]['dt'].date()}  (M15): gap fills into prior-day close",
                 fontweight="bold")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M", tz=timezone.utc))
    ax.set_xlabel("time (UTC)"); ax.set_ylabel("price")
    fig.tight_layout()
    p = os.path.join(OUT, "fig2_example_gapday.png")
    fig.savefig(p, dpi=130); plt.close(fig); print("wrote", p, "date", s[0]["dt"].date())


if __name__ == "__main__":
    fig1()
    fig2_example()
