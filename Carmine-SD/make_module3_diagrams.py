# -*- coding: utf-8 -*-
"""Schematic diagrams for Module 3: the trigger (order flow).

Every diagram illustrates a rule stated in the module-3 transcripts (09-12).
Nothing here is invented technique - see 02-documentation for the sourcing.
"""
from sdplot import (plt, Rectangle, OUT, DEMAND, SUPPLY, INK, MUTE,
                    candle, finish, save)
from matplotlib.patches import FancyBboxPatch

BLUE = "#2d6cb3"
print("module 3 diagrams")

# ---------- 1. the CLC rule ----------
# "these three pillars ... I call these three pillars the CLC Rule ... when all
#  three align I know I'm going to have an A+ high-quality setup"
fig, ax = plt.subplots(figsize=(10.4, 5.6))
ROWS = [
 (7.05, "C  -  CONTEXT",
  "\"what is the trend? are we putting in higher highs and higher lows?\nhow is today's volume? are there buyers or sellers factored in at a high or low?\"",
  "read from the candlestick chart", "Module 2", MUTE),
 (4.05, "L  -  LOCATION",
  "\"is it at a level of interest? a support or resistance level, a supply\nor a demand zone - a location the auction should react to\"",
  "read from the candlestick chart", "Module 1", MUTE),
 (1.05, "C  -  CONFIRMATION",
  "\"are buyers willing to buy at my level - are buyers trapped?\nare sellers willing to sell at my level, or are sellers trapped?\"",
  "read from the volume, never the candles", "Module 3", BLUE),
]
for y, head, body, src, mod, col in ROWS:
    ax.add_patch(FancyBboxPatch((0.35, y), 6.95, 2.3,
                 boxstyle="round,pad=0.02,rounding_size=0.12",
                 facecolor="#f4f6f8" if col is MUTE else "#eaf1fa",
                 edgecolor=col, lw=1.4, zorder=2))
    ax.text(0.62, y + 1.92, head, fontsize=11.6, fontweight="bold",
            color=INK, va="top", zorder=3)
    ax.text(0.62, y + 1.44, body, fontsize=8.5, color="#333333", va="top",
            style="italic", zorder=3)
    ax.text(0.62, y + 0.26, src, fontsize=8.3, color=col, fontweight="bold",
            va="bottom", zorder=3)
    ax.text(7.6, y + 1.15, mod, fontsize=9.6, color=col, fontweight="bold",
            va="center", ha="left", zorder=3)
ax.annotate("", xy=(7.5, 2.2), xytext=(7.5, 8.35),
            arrowprops=dict(arrowstyle="-", color="#cccccc", lw=1.2))
ax.text(0.35, 0.52, "\"when all three align, I know I'm going to have an A+ high-quality setup\"",
        fontsize=9.6, color=INK, fontweight="bold", va="top")
ax.set_xlim(0, 10.1); ax.set_ylim(0, 9.9)
finish(ax, "THE CLC RULE",
       "his own name for it - and the reason this syllabus is shaped the way it is")
fig.tight_layout(); save(fig, "m3-01-clc-rule.png")

# ---------- 2. what actually moves price ----------
# "the market moves up simply because there is more aggressive buying than there
#  is passive selling - that's the only way the market could move up"
fig, axes = plt.subplots(1, 2, figsize=(10.6, 4.6))
ax = axes[0]
for i, w in enumerate([1.5, 1.3, 1.6, 1.2, 1.4]):
    ax.add_patch(Rectangle((2.55, 1.15 + i*1.5), w, 0.54, facecolor=SUPPLY,
                           alpha=0.5, edgecolor="none", zorder=2))
ax.annotate("", xy=(3.05, 8.6), xytext=(3.05, 0.7),
            arrowprops=dict(arrowstyle="-|>", color=DEMAND, lw=5.5, alpha=0.9),
            zorder=6)
ax.text(3.05, 8.8, "price", fontsize=9.2, color=DEMAND, fontweight="bold",
        ha="center", va="bottom")
ax.text(5.1, 6.9, "every resting sell order is small,\nso the aggressive buying\neats straight through them",
        fontsize=8.7, color=MUTE, fontweight="bold", va="top")
ax.set_xlim(1.4, 9.8); ax.set_ylim(0.2, 9.5)
finish(ax, "PRICE MOVES", "more aggressive buying than there is passive selling")

ax = axes[1]
for i, w in enumerate([1.3, 1.2, 1.4]):
    ax.add_patch(Rectangle((2.55, 1.15 + i*1.5), w, 0.54, facecolor=SUPPLY,
                           alpha=0.5, edgecolor="none", zorder=2))
ax.add_patch(Rectangle((2.55, 5.55), 5.7, 0.78, facecolor=SUPPLY, alpha=0.8,
                       edgecolor=SUPPLY, lw=1.4, zorder=3))
ax.text(2.7, 6.52, "THE WALL", fontsize=9.4, color=SUPPLY, fontweight="bold",
        ha="left", va="bottom", zorder=5)
ax.annotate("", xy=(3.05, 5.46), xytext=(3.05, 0.7),
            arrowprops=dict(arrowstyle="-|>", color=DEMAND, lw=5.5, alpha=0.9),
            zorder=6)
ax.text(5.1, 9.3, "one resting seller is bigger than\nevery aggressive buyer put together,\nso price cannot pass",
        fontsize=8.7, color=MUTE, fontweight="bold", va="top")
ax.set_xlim(1.4, 9.8); ax.set_ylim(0.2, 9.5)
finish(ax, "PRICE STALLS", "\"what proves resistance to be resistance is strong passive sellers\"")
fig.tight_layout(w_pad=2.4); save(fig, "m3-02-what-moves-price.png")

# ---------- 3. the one signal: biggest effort, no reward ----------
# "despite the selling the market didn't sell off, in fact it started moving up -
#  when I see this right now I am comfortable getting long"
fig, axes = plt.subplots(2, 2, figsize=(10.6, 5.8),
                         gridspec_kw={"height_ratios": [2.35, 1]})
LO = [(0,6.22,6.10,6.26,6.06),(1,6.10,5.98,6.14,5.94),(2,5.98,5.86,6.02,5.82),
      (3,5.86,5.76,5.90,5.70),(4,5.76,5.70,5.80,5.62),(5,5.70,5.74,5.80,5.60),
      (6,5.74,5.92,5.98,5.72),(7,5.92,6.10,6.16,5.88)]
ax = axes[0][0]
ax.add_patch(Rectangle((-0.8,5.58),9.4,0.22,facecolor=DEMAND,alpha=0.16,
                       edgecolor=DEMAND,lw=1.2,zorder=1))
for s in LO: candle(ax, *s)
ax.text(-0.7,5.52,"demand",fontsize=8.2,color=DEMAND,fontweight="bold",
        ha="left",va="top")
ax.annotate("biggest selling of the day,\nand price will not go down",xy=(5,5.58),
            xytext=(6.0,6.26),ha="right",va="top",fontsize=8.4,color=MUTE,
            fontweight="bold",arrowprops=dict(arrowstyle="->",color=MUTE,lw=1.2))
ax.text(7.8,5.42,"LONG",fontsize=10,color=DEMAND,fontweight="bold",ha="right")
ax.set_xlim(-0.9,7.9); ax.set_ylim(5.34,6.46)
finish(ax,"A PASSIVE BUYER AT A LOW")
ax = axes[1][0]
ax.bar(range(8), [-180,-240,-320,-410,-735,-1171,120,260],
       color=[SUPPLY]*6+[DEMAND]*2, width=0.52)
ax.axhline(0, color="#cccccc", lw=1)
ax.text(5, -1230, "-1171", fontsize=8.6, color=SUPPLY, fontweight="bold",
        ha="center", va="top")
ax.set_xlim(-0.9,7.9); ax.set_ylim(-1700, 560)
finish(ax, "", "delta on each bar - how much hit the bid against the offer")

HI = [(0,5.88,6.00,6.04,5.84),(1,6.00,6.12,6.18,5.96),(2,6.12,6.24,6.30,6.08),
      (3,6.24,6.34,6.40,6.20),(4,6.34,6.40,6.46,6.30),(5,6.40,6.36,6.46,6.28),
      (6,6.36,6.18,6.40,6.12),(7,6.18,6.00,6.22,5.94)]
ax = axes[0][1]
ax.add_patch(Rectangle((-0.8,6.38),9.4,0.22,facecolor=SUPPLY,alpha=0.16,
                       edgecolor=SUPPLY,lw=1.2,zorder=1))
for s in HI: candle(ax, *s)
ax.text(-0.7,6.66,"supply",fontsize=8.2,color=SUPPLY,fontweight="bold",
        ha="left",va="bottom")
ax.annotate("biggest buying of the day,\nand price will not go up",xy=(5,6.40),
            xytext=(6.0,5.78),ha="right",va="bottom",fontsize=8.4,color=MUTE,
            fontweight="bold",arrowprops=dict(arrowstyle="->",color=MUTE,lw=1.2))
ax.text(7.8,6.72,"SHORT",fontsize=10,color=SUPPLY,fontweight="bold",ha="right")
ax.set_xlim(-0.9,7.9); ax.set_ylim(5.66,6.86)
finish(ax,"A PASSIVE SELLER AT A HIGH")
ax = axes[1][1]
ax.bar(range(8), [240,420,760,1024,1921,3300,-180,-320],
       color=[DEMAND]*6+[SUPPLY]*2, width=0.52)
ax.axhline(0, color="#cccccc", lw=1)
ax.text(5, 3420, "+3300", fontsize=8.6, color=DEMAND, fontweight="bold",
        ha="center", va="bottom")
ax.set_xlim(-0.9,7.9); ax.set_ylim(-1050, 4500)
finish(ax, "", "the same read, mirrored - his two worked examples")
fig.tight_layout(h_pad=1.4, w_pad=2.4); save(fig, "m3-03-effort-no-reward.png")

# ---------- 4. the delta outlier, and how it becomes tomorrow's level ----------
# "we call this a delta outlier ... keep in mind this is at 6575, the same exact
#  level where we're seeing it the following day"
fig, axes = plt.subplots(1, 2, figsize=(10.6, 4.6))
MON = [(0,6.10,6.00,6.14,5.96),(1,6.00,5.88,6.04,5.84),(2,5.88,5.78,5.92,5.74),
       (3,5.78,5.90,5.94,5.75),(4,5.90,5.98,6.02,5.86),(5,5.98,5.86,6.02,5.82),
       (6,5.86,5.78,5.90,5.74),(7,5.78,5.88,5.92,5.75),(8,5.88,5.80,5.92,5.76),
       (9,5.80,5.68,5.84,5.62)]
ax = axes[0]
ax.axhline(5.75, color=BLUE, lw=1.5, ls="--", zorder=1)
for s_ in MON: candle(ax, *s_)
ax.text(-0.7, 5.77, "6575", fontsize=8.4, color=BLUE, fontweight="bold",
        ha="left", va="bottom")
for x in (3, 7):
    ax.text(x, 5.71, "-550", fontsize=8.0, color=SUPPLY, fontweight="bold",
            ha="center", va="top")
ax.text(9.7, 6.22, "two big sell prints at one price -\nand both get bought",
        fontsize=8.5, color=MUTE, fontweight="bold", ha="right", va="top")
ax.set_xlim(-0.9, 9.9); ax.set_ylim(5.54, 6.28)
finish(ax, "MONDAY", "a delta outlier: heavy selling into a price that refuses to fall")

TUE = [(0,5.95,5.88,5.98,5.84),(1,5.88,5.80,5.92,5.78),(2,5.80,5.76,5.84,5.72),
       (3,5.76,5.70,5.78,5.68),(4,5.70,5.78,5.82,5.66),(5,5.78,5.90,5.94,5.76),
       (6,5.90,6.02,6.06,5.88),(7,6.02,6.14,6.18,6.00)]
ax = axes[1]
ax.axhline(5.75, color=BLUE, lw=1.5, ls="--", zorder=1)
ax.axhline(6.16, color=DEMAND, lw=1.2, zorder=1)
for s_ in TUE: candle(ax, *s_)
ax.text(-0.7, 5.77, "6575 - carried over", fontsize=8.4, color=BLUE,
        fontweight="bold", ha="left", va="bottom")
ax.text(7.7, 6.18, "target", fontsize=8.3, color=DEMAND, fontweight="bold",
        ha="right", va="bottom")
ax.text(3, 5.645, "-850", fontsize=8.0, color=SUPPLY, fontweight="bold",
        ha="center", va="top")
ax.text(4, 5.635, "-1217", fontsize=8.0, color=SUPPLY, fontweight="bold",
        ha="center", va="top")
ax.annotate("LONG", xy=(4, 5.80), xytext=(4, 5.95), ha="center", va="bottom",
            fontsize=9.4, color=DEMAND, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=DEMAND, lw=1.3))
ax.text(7.7, 5.60, "he WANTS the break - it brings in\nthe sellers the big buyer needs to fill against",
        fontsize=8.5, color=MUTE, fontweight="bold", ha="right", va="top")
ax.set_xlim(-0.9, 7.9); ax.set_ylim(5.42, 6.28)
finish(ax, "TUESDAY", "the same price, the next session - that is what makes it a level")
fig.tight_layout(w_pad=2.4); save(fig, "m3-04-delta-outlier.png")

# ---------- 5. the trapped-participant playbook ----------
fig, ax = plt.subplots(figsize=(10.4, 5.2))
PB = [(0,5.80,5.90,5.94,5.76),(1,5.90,6.00,6.04,5.86),(2,6.00,6.08,6.12,5.96),
      (3,6.08,6.14,6.18,6.04),(4,6.14,6.08,6.18,6.04),(5,6.08,6.16,6.20,6.05),
      (6,6.16,6.24,6.28,6.14),(7,6.24,6.26,6.32,6.20),(8,6.26,6.20,6.30,6.16),
      (9,6.20,6.10,6.24,6.06),(10,6.10,5.98,6.14,5.94),(11,5.98,5.86,6.02,5.82),
      (12,5.86,5.74,5.90,5.70),(13,5.74,5.62,5.78,5.58),(14,5.62,5.52,5.66,5.48),
      (15,5.52,5.44,5.56,5.40)]
ax.axhline(6.18, color=MUTE, lw=1.3, ls="--", zorder=1)
ax.axhline(5.42, color=MUTE, lw=1.3, ls="--", zorder=1)
for s_ in PB: candle(ax, *s_)
ax.text(-0.8, 6.20, "high of day", fontsize=8.3, color=MUTE, fontweight="bold",
        ha="left", va="bottom")
ax.text(-0.8, 5.40, "low of day", fontsize=8.3, color=MUTE, fontweight="bold",
        ha="left", va="top")
ax.annotate("1.  strong buying breaks the high -\nthe longs are now on board",
            xy=(6, 6.30), xytext=(0.2, 6.60), ha="left", va="top", fontsize=8.6,
            color=DEMAND, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=DEMAND, lw=1.2))
ax.annotate("2.  the sellers step in and\nput the brakes on it",
            xy=(8.4, 6.30), xytext=(10.6, 6.60), ha="left", va="top",
            fontsize=8.6, color=SUPPLY, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=SUPPLY, lw=1.2))
ax.annotate("3.  those longs are trapped - where do they\nstop out? that pain point is the target",
            xy=(8.6, 5.44), xytext=(0.2, 5.72), ha="left", va="top",
            fontsize=8.6, color=INK, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=INK, lw=1.2))
ax.set_xlim(-0.9, 16.0); ax.set_ylim(5.28, 6.70)
finish(ax, "THE TRAPPED-PARTICIPANT PLAYBOOK",
       "\"where there is pain, there will be gain\" - his three steps, in order")
fig.tight_layout(); save(fig, "m3-05-playbook.png")

# ---------- 6. the entry decides the risk-to-reward ----------
# same stop, same target, three entries: 5:1, 2:1, 1.4:1
fig, axes = plt.subplots(1, 2, figsize=(10.6, 4.4),
                         gridspec_kw={"width_ratios": [1, 1.55]})
ax = axes[0]
ax.axhline(6595, color=DEMAND, lw=1.5, ls="--")
ax.axhline(6565, color=SUPPLY, lw=1.5, ls="--")
ax.text(0.1, 6595.6, "target  6595", fontsize=8.6, color=DEMAND,
        fontweight="bold", va="bottom")
ax.text(0.1, 6564.4, "stop  6565", fontsize=8.6, color=SUPPLY,
        fontweight="bold", va="top")
for yy, lab, col in ((6570, "6570", BLUE), (6575, "6575", MUTE),
                     (6577.3, "6577", MUTE)):
    ax.plot([0.5, 3.4], [yy, yy], color=col, lw=2.2, solid_capstyle="round")
    ax.text(3.6, yy, lab, fontsize=8.6, color=col, fontweight="bold",
            va="center", ha="left")
ax.set_xlim(0, 4.6); ax.set_ylim(6562, 6598)
finish(ax, "ONE TRADE", "the stop and the target never move")

ax = axes[1]
ROWS = [(2.0, 5, 25, "5 : 1", "the moment the order flow prints", BLUE),
        (1.0, 10, 20, "2 : 1", "a few seconds later", MUTE),
        (0.0, 12.3, 17.7, "1.4 : 1", "after a 5-minute candle closes", MUTE)]
for y, risk, rew, ratio, lab, col in ROWS:
    ax.add_patch(Rectangle((-risk, y - 0.22), risk, 0.44, facecolor=SUPPLY,
                           alpha=0.82, edgecolor="none"))
    ax.add_patch(Rectangle((0, y - 0.22), rew, 0.44, facecolor=DEMAND,
                           alpha=0.82, edgecolor="none"))
    ax.text(-risk - 0.7, y, "risk %g" % risk, fontsize=8.2, color=SUPPLY,
            fontweight="bold", ha="right", va="center")
    ax.text(rew + 0.7, y, ratio, fontsize=10.4, color=INK, fontweight="bold",
            ha="left", va="center")
    ax.text(0.4, y + 0.42, lab, fontsize=8.4, color=col, fontweight="bold",
            ha="left", va="bottom")
ax.axvline(0, color="#999999", lw=1.1)
ax.set_xlim(-21, 34); ax.set_ylim(-0.55, 2.95)
finish(ax, "THREE ENTRIES",
       "only the entry moved - and it is the entry, not the target, that sets the R")
fig.tight_layout(w_pad=2.0); save(fig, "m3-06-entry-decides-r.png")

# ---------- 7. cumulative delta divergence ----------
# "the market basically puts in this double top, yet the cumulative delta puts
#  in a higher high ... indicating that potentially buyers are going to become
#  trapped here"
fig, axes = plt.subplots(2, 1, figsize=(10.4, 5.4),
                         gridspec_kw={"height_ratios": [2.1, 1]})
DT = [(0,5.80,5.92,5.96,5.76),(1,5.92,6.06,6.10,5.88),(2,6.06,6.18,6.24,6.02),
      (3,6.18,6.26,6.32,6.14),(4,6.26,6.14,6.30,6.10),(5,6.14,6.04,6.18,6.00),
      (6,6.04,6.14,6.18,6.00),(7,6.14,6.24,6.30,6.10),(8,6.24,6.28,6.33,6.20),
      (9,6.28,6.12,6.32,6.08),(10,6.12,5.96,6.16,5.92),(11,5.96,5.80,6.00,5.76)]
ax = axes[0]
for s_ in DT: candle(ax, *s_)
ax.plot([3, 8], [6.355, 6.365], color=MUTE, lw=1.3, ls="--")
ax.text(5.5, 6.40, "price: the same high twice", fontsize=8.8, color=MUTE,
        fontweight="bold", ha="center", va="bottom")
ax.set_xlim(-0.9, 11.9); ax.set_ylim(5.68, 6.56)
finish(ax, "CUMULATIVE DELTA DIVERGENCE")
ax = axes[1]
CD = [100,320,560,800,640,420,560,980,1500,900,420,-150]
ax.plot(range(12), CD, color=BLUE, lw=2.2, zorder=3)
ax.axhline(0, color="#cccccc", lw=1)
ax.plot([3, 8], [900, 1600], color=BLUE, lw=1.3, ls="--")
ax.text(5.5, 1760, "cumulative delta: a HIGHER high", fontsize=8.8, color=BLUE,
        fontweight="bold", ha="center", va="bottom")
ax.text(11.7, -620, "more and more aggressive buying bought - and no more price for it.\nthose buyers are trapped.",
        fontsize=9, color=INK, fontweight="bold", ha="right", va="top")
ax.set_xlim(-0.9, 11.9); ax.set_ylim(-1350, 2500)
finish(ax, "", "the buying got bigger while the high did not")
fig.tight_layout(h_pad=1.2); save(fig, "m3-07-cd-divergence.png")

print("done")
