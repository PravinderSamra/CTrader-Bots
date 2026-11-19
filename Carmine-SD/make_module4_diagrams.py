# -*- coding: utf-8 -*-
"""Schematic diagrams for Module 4: the complete method, and risk.

Every diagram illustrates a rule stated in transcripts 13-16. Nothing invented.
"""
from sdplot import (plt, Rectangle, OUT, DEMAND, SUPPLY, INK, MUTE,
                    candle, finish, save)
from matplotlib.patches import FancyBboxPatch

BLUE = "#2d6cb3"
print("module 4 diagrams")

# ---------- 1. the whole method, in order ----------
fig, ax = plt.subplots(figsize=(10.4, 7.6))
STEPS = [
 ("BEFORE THE OPEN  -  context",
  "trend, today's volume, how zones behaved yesterday, related markets, the events calendar", MUTE),
 ("BEFORE THE OPEN  -  the plan",
  "one key level (or two). BOTH scenarios written, each with its own trigger and target", MUTE),
 ("AT THE LEVEL  -  location",
  "is price actually at a level of interest? if not, there is no trade - order flow elsewhere is noise", BLUE),
 ("IN THE NOW  -  confirmation",
  "heaviest aggression of the session arrives and price will not move: the passive side is winning", BLUE),
 ("ENTRY",
  "the moment that prints - not after the candle closes, not after the move", DEMAND),
 ("STOP",
  "\"always based on where my analysis is incorrect\" - under the large volume, or past the high", SUPPLY),
 ("TARGET",
  "high or low of day, VWAP, the next zone, the next support or resistance. no home runs", DEMAND),
 ("AFTER THE CLOSE",
  "record the screen, review what you did, dissect the losers for a common pattern", MUTE),
]
y = 9.25
for i, (head, body, col) in enumerate(STEPS):
    ax.add_patch(FancyBboxPatch((0.9, y - 0.86), 9.0, 0.86,
                 boxstyle="round,pad=0.015,rounding_size=0.08",
                 facecolor="#eaf1fa" if col is BLUE else "#f5f6f7",
                 edgecolor=col, lw=1.2, zorder=2))
    ax.add_patch(plt.Circle((0.52, y - 0.43), 0.26, facecolor=col, alpha=0.9,
                            edgecolor="none", zorder=3))
    ax.text(0.52, y - 0.43, str(i + 1), fontsize=9, color="white",
            fontweight="bold", ha="center", va="center", zorder=4)
    ax.text(1.15, y - 0.26, head, fontsize=9.6, fontweight="bold", color=INK,
            va="top", zorder=4)
    ax.text(1.15, y - 0.58, body, fontsize=8.1, color="#444444", va="top",
            zorder=4)
    if i < len(STEPS) - 1:
        ax.annotate("", xy=(0.52, y - 1.12), xytext=(0.52, y - 0.70),
                    arrowprops=dict(arrowstyle="-", color="#cfcfcf", lw=1.3))
    y -= 1.12
ax.text(0.9, 0.28, "\"do I skip days because I don't see a setup? 100%.  100%.\"",
        fontsize=9.4, color=INK, fontweight="bold", va="bottom")
ax.set_xlim(0, 10.2); ax.set_ylim(-0.2, 9.9)
finish(ax, "THE WHOLE METHOD, IN ORDER",
       "nothing here is new - it is modules 1 to 3 in the sequence he actually runs them")
fig.tight_layout(); save(fig, "m4-01-the-stack.png")

# ---------- 2. balanced market rules ----------
# "my rule of thumb is to trade around the edges. It is to what I call fade the
#  extremes ... trading in the middle of this range, no good"
fig, ax = plt.subplots(figsize=(10.4, 5.0))
BAL = [(0,6.05,5.86,6.10,5.80),(1,5.86,5.70,5.90,5.66),(2,5.70,5.84,5.92,5.68),
       (3,5.84,6.02,6.10,5.80),(4,6.02,6.16,6.22,5.98),(5,6.16,5.98,6.20,5.92),
       (6,5.98,5.82,6.02,5.74),(7,5.82,5.70,5.88,5.66),(8,5.70,5.88,5.94,5.68),
       (9,5.88,6.06,6.14,5.84),(10,6.06,6.18,6.23,6.02),(11,6.18,6.00,6.21,5.94)]
BANDS = [(6.04, 0.22, SUPPLY, "the TOP of the range",
          "look to SELL here first"),
         (5.82, 0.22, "#9a9a9a", "THE MIDDLE", "no trades - this is where you get chopped"),
         (5.60, 0.22, DEMAND, "the BOTTOM of the range", "look to BUY here first")]
for y0, h, col, head, body in BANDS:
    ax.add_patch(Rectangle((-0.8, y0), 12.6, h,
                           facecolor=col, alpha=0.20 if col != "#9a9a9a" else 0.14,
                           edgecolor="none", zorder=1))
    ax.text(12.3, y0 + h/2 + 0.025, head, fontsize=9, color=col if col != "#9a9a9a" else "#6b6b6b",
            fontweight="bold", ha="left", va="bottom")
    ax.text(12.3, y0 + h/2 - 0.015, body, fontsize=8.3, color=MUTE,
            ha="left", va="top")
for s_ in BAL: candle(ax, *s_)
ax.text(-0.8, 6.40, "\"I find my best setups come when it's like this\"",
        fontsize=9.6, color=INK, fontweight="bold", va="bottom")
ax.set_xlim(-0.9, 19.6); ax.set_ylim(5.48, 6.52)
finish(ax, "BALANCED MARKET RULES",
       "the framework he credits for most of his June profit - and the one most traders give up on")
fig.tight_layout(); save(fig, "m4-02-balance-rules.png")

# ---------- 3. initiative: let it break, then buy the pullback ----------
# "letting it break out and looking for a pull back into where the aggressive
#  buyers who initiated the market ... initiation above the balance range high"
fig, ax = plt.subplots(figsize=(10.4, 5.0))
INI = [(0,5.82,5.94,5.98,5.78),(1,5.94,6.04,6.10,5.90),(2,6.04,5.92,6.08,5.86),
       (3,5.92,6.02,6.08,5.88),(4,6.02,6.12,6.16,5.98),(5,6.12,6.26,6.32,6.08),
       (6,6.26,6.40,6.46,6.22),(7,6.40,6.34,6.44,6.28),(8,6.34,6.26,6.38,6.20),
       (9,6.26,6.36,6.42,6.22),(10,6.36,6.50,6.56,6.32),(11,6.50,6.64,6.70,6.46),
       (12,6.64,6.78,6.84,6.60)]
ax.axhline(6.14, color=MUTE, lw=1.3, ls="--", zorder=1)
ax.add_patch(Rectangle((5.5, 6.20), 10.2, 0.14, facecolor=DEMAND, alpha=0.22,
                       edgecolor=DEMAND, lw=1.3, zorder=1))
for s in INI: candle(ax, *s)
ax.text(-0.8, 6.10, "balance range high", fontsize=8.4, color=MUTE,
        fontweight="bold", ha="left", va="top")
ax.text(12.9, 6.17, "where the buyers initiated", fontsize=8.5, color=DEMAND,
        fontweight="bold", ha="right", va="top")
ax.annotate("most people buy HERE -\nan extended move, and a far-away stop",
            xy=(6, 6.49), xytext=(1.0, 6.78), ha="left", va="top", fontsize=8.5,
            color=SUPPLY, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=SUPPLY, lw=1.2))
ax.annotate("he buys HERE - the pullback into\nwhere the initiative actually showed up",
            xy=(8.5, 6.19), xytext=(8.0, 5.86), ha="center", va="top",
            fontsize=8.5, color=DEMAND, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=DEMAND, lw=1.3))
ax.set_xlim(-0.9, 13.0); ax.set_ylim(5.62, 7.02)
finish(ax, "INITIATIVE  -  AND WHY HE NEVER BUYS THE BREAK",
       "\"my entry is a reversal signal, but I'm going for a continuation setup\"")
fig.tight_layout(); save(fig, "m4-03-initiative.png")

# ---------- 4. the chain that cost him $30,000 ----------
fig, axes = plt.subplots(1, 2, figsize=(10.6, 5.6))
CHAIN = ["the pre-market plan is RIGHT",
         "the move happens without me -\nno confirmation, or it was too fast",
         "FOMO  /  regret",
         "I CREATE a trade in the\nopposite direction",
         "loss  -  then I try it again,\nand again, and again"]
ax = axes[0]
y = 9.1
for i, t in enumerate(CHAIN):
    last = i == len(CHAIN) - 1
    ax.add_patch(FancyBboxPatch((0.5, y - 1.28), 8.6, 1.28,
                 boxstyle="round,pad=0.02,rounding_size=0.1",
                 facecolor="#fdeeec" if i else "#f5f6f7",
                 edgecolor=SUPPLY if i else MUTE, lw=1.3, zorder=2))
    ax.text(4.8, y - 0.64, t, fontsize=8.8, color=INK if not i else SUPPLY,
            fontweight="bold", ha="center", va="center", zorder=3)
    if not last:
        ax.annotate("", xy=(4.8, y - 1.68), xytext=(4.8, y - 1.34),
                    arrowprops=dict(arrowstyle="-|>", color=SUPPLY, lw=1.6))
    y -= 1.68
ax.text(4.8, 0.52, "four days in February  =  over $30,000",
        fontsize=9.6, color=SUPPLY, fontweight="bold", ha="center")
ax.set_xlim(0, 9.6); ax.set_ylim(0.1, 9.5)
finish(ax, "THE CHAIN", "\"the analysis was right. This is a psychological problem.\"")

ax = axes[1]
FIX = [("THE RULE",
        "\"if I miss my planned entry, I do\nnot create a new trade in the\nopposite direction\"", DEMAND),
       ("THEN ONE OF TWO THINGS",
        "wait for new development that\nI can build a new thesis on -\nor sit on my hands", DEMAND),
       ("AND THE REFRAME",
        "a missed move is not a loss, it is\nCONTEXT. the rejection tells me\nsellers are in control - use it", BLUE)]
y = 8.6
for head, body, col in FIX:
    ax.add_patch(FancyBboxPatch((0.5, y - 2.0), 8.6, 2.0,
                 boxstyle="round,pad=0.02,rounding_size=0.1",
                 facecolor="#eef7f1" if col is DEMAND else "#eaf1fa",
                 edgecolor=col, lw=1.3, zorder=2))
    ax.text(0.85, y - 0.34, head, fontsize=9.4, color=col, fontweight="bold",
            va="top", zorder=3)
    ax.text(0.85, y - 0.78, body, fontsize=8.6, color="#333333", va="top",
            zorder=3)
    y -= 2.4
ax.text(4.8, 0.52, "\"our job is to LOCATE trading\nopportunities, not CREATE them\"",
        fontsize=9.6, color=INK, fontweight="bold", ha="center", va="bottom")
ax.set_xlim(0, 9.6); ax.set_ylim(0.1, 9.5)
finish(ax, "THE FIX", "one rule, and one change of mind about what a missed move is")
fig.tight_layout(w_pad=2.2); save(fig, "m4-04-the-chain.png")

# ---------- 5. the arithmetic of being wrong most of the time ----------
fig, ax = plt.subplots(figsize=(10.4, 4.8))
RS   = ["1 : 1", "2 : 1", "3 : 1", "4 : 1", "5 : 1"]
NEED = [50.0, 33.3, 25.0, 20.0, 16.7]
xs = list(range(len(RS)))
ax.bar(xs, NEED, color=BLUE, alpha=0.82, width=0.52, zorder=3)
for x, v, lab in zip(xs, NEED, RS):
    ax.text(x, v + 1.4, "%.0f%%" % v, fontsize=9.4, color=BLUE,
            fontweight="bold", ha="center", va="bottom", zorder=4)
    ax.text(x, -2.2, lab, fontsize=9.6, color=INK, fontweight="bold",
            ha="center", va="top", zorder=4)
ax.axhline(20, color=DEMAND, lw=1.5, ls="--", zorder=2)
ax.text(4.42, 47, "his own January:\n20% win rate, 5:1 average  -  a record month",
        fontsize=8.8, color=DEMAND, fontweight="bold", ha="right", va="top")
ax.text(-0.52, 61, "the win rate you need just to break even",
        fontsize=8.8, color=MUTE, fontweight="bold", va="top")
ax.text(-0.52, -7.6, "reward-to-risk on the trade", fontsize=8.4, color=MUTE,
        va="bottom")
ax.set_xlim(-0.62, 4.56); ax.set_ylim(-9, 63)
finish(ax, "WHY THE R MULTIPLE IS THE WHOLE GAME",
       "\"this is why win rates don't matter\" - but note what being wrong 75% of the time feels like")
fig.tight_layout(); save(fig, "m4-05-win-rate.png")

print("done")
