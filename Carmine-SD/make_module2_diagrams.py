# -*- coding: utf-8 -*-
"""Schematic diagrams for Module 2: context and zone selection.

Every diagram illustrates a rule stated in the module-1 transcript set. Nothing
here is invented technique - see 02-documentation for the sourcing tags.
"""
from sdplot import (plt, Rectangle, OUT, DEMAND, SUPPLY, INK, MUTE,
                    candle, finish, save)

print("module 2 diagrams")

# ---------- 1. the pre-market plan: one key level, two scenarios ----------
# "my key level was 4107 to 4110 on the S P 500 futures ... I post these every
#  single day in the Discord levels and setups and SCENARIOS that I'm watching"
fig, ax = plt.subplots(figsize=(10.4, 4.8))
IN = [(0,5.52,5.66,5.70,5.48),(1,5.66,5.80,5.86,5.62),(2,5.80,5.96,6.02,5.76),
      (3,5.96,6.08,6.14,5.92),(4,6.08,6.18,6.24,6.04)]
for s_ in IN: candle(ax, *s_)
ax.add_patch(Rectangle((-0.8,6.16),12.6,0.20,facecolor="#2d6cb3",alpha=0.15,
                       edgecolor="#2d6cb3",lw=1.3,zorder=1))
ax.text(-0.7,6.40,"THE KEY LEVEL  -  written down before the open",fontsize=9,
        color="#2d6cb3",fontweight="bold",ha="left",va="bottom")
# bullish branch
ax.plot([4.6,6.4,8.2,10.6],[6.26,6.55,6.78,7.12],color=DEMAND,lw=1.7,ls=(0,(5,3)),zorder=5)
ax.plot([5.2,11.6],[7.30,7.30],color=DEMAND,lw=1.3,zorder=3)
ax.text(11.5,7.34,"target: next supply above",fontsize=8.3,color=DEMAND,
        fontweight="bold",ha="right",va="bottom")
ax.text(6.5,6.52,"SCENARIO 1  -  bullish",fontsize=8.8,color=DEMAND,
        fontweight="bold",ha="left",va="bottom")
ax.text(6.5,6.50,"it holds above, or new demand forms on it",fontsize=8.2,
        color=MUTE,ha="left",va="top")
# bearish branch
ax.plot([4.6,6.4,8.2,10.6],[6.08,5.80,5.58,5.26],color=SUPPLY,lw=1.7,ls=(0,(5,3)),zorder=5)
ax.plot([5.2,11.6],[5.06,5.06],color=SUPPLY,lw=1.3,zorder=3)
ax.text(11.5,5.02,"target: demand below",fontsize=8.3,color=SUPPLY,
        fontweight="bold",ha="right",va="top")
ax.text(6.5,6.02,"SCENARIO 2  -  bearish",fontsize=8.8,color=SUPPLY,
        fontweight="bold",ha="left",va="top")
ax.text(6.5,5.86,"it rejects, then loses the round number below",fontsize=8.2,
        color=MUTE,ha="left",va="top")
ax.text(-0.7,4.74,"he does not predict which one happens - he writes both, and lets price pick",
        fontsize=9.2,color=INK,fontweight="bold",ha="left",va="bottom")
ax.set_xlim(-0.9,12.0); ax.set_ylim(4.66,7.62)
finish(ax,"THE PRE-MARKET PLAN","one key level, two pre-written scenarios, each with its own trigger and target")
fig.tight_layout(); save(fig,"m2-01-two-scenarios.png")

# ---------- 2. the three ways he plays a level ----------
# "these are the three ways that I play support and resistance ... point number
#  one point number three are continuation setups and point number two is mainly
#  a reversal setup I use Point number two the most"
fig, axes = plt.subplots(3, 1, figsize=(10.4, 10.0))

A1 = [(0,5.55,5.65,5.70,5.50),(1,5.65,5.78,5.84,5.60),(2,5.78,5.92,5.98,5.74),
      (3,5.92,6.12,6.18,5.88),(4,6.12,6.22,6.28,6.08),(5,6.22,6.10,6.26,6.04),
      (6,6.10,6.02,6.14,5.97),(7,6.02,6.14,6.20,5.98),(8,6.14,6.30,6.36,6.10),
      (9,6.30,6.46,6.52,6.26),(10,6.46,6.60,6.66,6.42),(11,6.60,6.74,6.80,6.56)]
ax = axes[0]
ax.axhline(6.00,color=MUTE,lw=1.4,ls="--",zorder=1)
for s in A1: candle(ax, *s)
ax.text(-0.75,6.04,"the obvious level",fontsize=8.4,color=MUTE,fontweight="bold",
        ha="left",va="bottom")
ax.annotate("LONG here",xy=(7,5.94),xytext=(7,5.62),ha="center",va="top",
            fontsize=8.8,color=DEMAND,fontweight="bold",
            arrowprops=dict(arrowstyle="->",color=DEMAND,lw=1.3))
ax.text(-0.75,7.16,"it breaks, comes back, and the old resistance holds as support",
        ha="left",va="top",fontsize=8.6,color=INK)
ax.set_xlim(-0.9,12.1); ax.set_ylim(5.32,7.20)
finish(ax,"1.  BREAK, THEN RETEST","a continuation setup - he waits for the retest rather than buying the break")

B1 = [(0,5.70,5.85,5.90,5.65),(1,5.85,6.00,6.06,5.80),(2,6.00,6.15,6.20,5.96),
      (3,6.15,6.30,6.36,6.10),(4,6.30,6.38,6.46,6.26),(5,6.38,6.26,6.44,6.20),
      (6,6.26,6.08,6.30,6.02),(7,6.08,5.90,6.12,5.85),(8,5.90,5.72,5.94,5.66),
      (9,5.72,5.55,5.76,5.50),(10,5.55,5.40,5.60,5.35),(11,5.40,5.26,5.44,5.20)]
ax = axes[1]
ax.axhline(6.42,color=MUTE,lw=1.4,ls="--",zorder=1)
for s in B1: candle(ax, *s)
ax.text(-0.75,6.46,"the obvious level",fontsize=8.4,color=MUTE,fontweight="bold",
        ha="left",va="bottom")
ax.annotate("SHORT here",xy=(5,6.50),xytext=(5,6.82),ha="center",va="bottom",
            fontsize=8.8,color=SUPPLY,fontweight="bold",
            arrowprops=dict(arrowstyle="->",color=SUPPLY,lw=1.3))
ax.text(11.8,6.78,"everyone is queued up to buy the breakout - he sells into them",
        ha="right",va="bottom",fontsize=8.6,color=INK)
ax.set_xlim(-0.9,12.1); ax.set_ylim(5.08,7.04)
finish(ax,"2.  REVERSAL AT THE LEVEL","the one he says he uses the most - the level is the entry")

C1 = [(0,5.95,5.80,5.98,5.76),(1,5.80,5.66,5.84,5.60),(2,5.66,5.56,5.70,5.50),
      (3,5.56,5.60,5.64,5.48),(4,5.60,5.74,5.80,5.56),(5,5.74,5.90,5.96,5.70),
      (6,5.90,6.06,6.12,5.86),(7,6.06,6.22,6.28,6.02),(8,6.22,6.38,6.44,6.18),
      (9,6.38,6.52,6.60,6.34),(10,6.52,6.44,6.58,6.38),(11,6.44,6.30,6.50,6.24)]
ax = axes[2]
ax.axhline(6.56,color=MUTE,lw=1.4,ls="--",zorder=1)
ax.add_patch(Rectangle((1.55,5.45),10.3,0.17,facecolor=DEMAND,alpha=0.16,
                       edgecolor=DEMAND,lw=1.2,zorder=1))
for s in C1: candle(ax, *s)
ax.text(11.8,6.60,"TARGET - sell into the breakout buyers",fontsize=8.6,
        color=MUTE,fontweight="bold",ha="right",va="bottom")
ax.annotate("LONG at demand,\nbefore the level",xy=(3,5.44),xytext=(3.4,5.24),
            ha="left",va="top",fontsize=8.8,color=DEMAND,fontweight="bold",
            arrowprops=dict(arrowstyle="->",color=DEMAND,lw=1.3))
ax.set_xlim(-0.9,12.1); ax.set_ylim(5.00,6.86)
finish(ax,"3.  IN BEFORE THE BREAK","the level is the exit, not the entry - the other continuation setup")
fig.tight_layout(h_pad=2.8); save(fig,"m2-02-three-ways.png")

# ---------- 3. a broken zone stops existing ----------
# "so if we break above Supply I will remove the Zone ... buyers are finding
#  value at higher prices and this is a good sign of continuation to the upside"
fig, ax = plt.subplots(figsize=(10.4, 4.2))
Z = [(0,5.60,5.74,5.80,5.55),(1,5.74,5.88,5.94,5.70),(2,5.88,6.04,6.10,5.84),
     (3,6.04,6.24,6.30,6.00),(4,6.24,6.48,6.54,6.20),(5,6.48,6.66,6.72,6.44),
     (6,6.66,6.60,6.74,6.54),(7,6.60,6.78,6.84,6.56),(8,6.78,6.94,7.00,6.74),
     (9,6.94,7.10,7.16,6.90),(10,7.10,7.24,7.30,7.06)]
ax.add_patch(Rectangle((-0.75,6.18),11.6,0.26,facecolor=SUPPLY,alpha=0.07,
                       edgecolor="none",zorder=1))
ax.add_patch(Rectangle((-0.75,6.18),11.6,0.26,facecolor="none",
                       edgecolor="#b4b4b4",hatch="////",lw=1.1,ls="--",zorder=2))
for s in Z: candle(ax, *s)
ax.text(-0.7,6.02,"supply zone - deleted",fontsize=8.6,color=MUTE,
        fontweight="bold",ha="left",va="top")
ax.annotate("no rejection - it goes\nstraight through",xy=(4.4,6.40),
            xytext=(5.6,5.86),ha="left",va="top",fontsize=8.4,color=MUTE,
            fontweight="bold",arrowprops=dict(arrowstyle="->",color=MUTE,lw=1.2))
ax.text(10.8,7.52,"buyers found value ABOVE it, so the zone comes off the chart -",
        ha="right",va="top",fontsize=9,color=INK,fontweight="bold")
ax.text(10.8,7.37,"the break is a continuation signal, not resistance",
        ha="right",va="top",fontsize=9,color=INK,fontweight="bold")
ax.set_xlim(-0.9,11.0); ax.set_ylim(5.40,7.62)
finish(ax,"WHEN A ZONE STOPS EXISTING","\"if we break above supply I will remove the zone\"")
fig.tight_layout(); save(fig,"m2-03-zone-deleted.png")

# ---------- 4. zones as magnets ----------
# "use these levels as magnets to price ... there's no other support or there's
#  no other demand until 3675 and we can look to Target that level"
fig, ax = plt.subplots(figsize=(10.4, 4.6))
M = [(0,6.52,6.40,6.56,6.36),(1,6.40,6.28,6.44,6.22),(2,6.28,6.16,6.32,6.10),
     (3,6.16,6.06,6.20,6.00),(4,6.06,5.94,6.10,5.88),(5,5.94,5.74,5.98,5.68),
     (6,5.74,5.56,5.78,5.50),(7,5.56,5.38,5.60,5.32),(8,5.38,5.22,5.42,5.16),
     (9,5.22,5.10,5.26,5.02),(10,5.10,5.16,5.22,4.98)]
ax.add_patch(Rectangle((-0.75,5.94),4.4,0.22,facecolor=DEMAND,alpha=0.13,
                       edgecolor=DEMAND,lw=1.1,ls="--",zorder=1))
ax.add_patch(Rectangle((-0.75,4.88),11.6,0.24,facecolor=DEMAND,alpha=0.20,
                       edgecolor=DEMAND,lw=1.3,zorder=1))
ax.text(-0.7,6.22,"demand - broken",fontsize=8.5,color=MUTE,fontweight="bold",
        ha="left",va="bottom")
ax.text(-0.7,4.82,"the next demand below",fontsize=8.5,color=DEMAND,
        fontweight="bold",ha="left",va="top")
for s in M: candle(ax, *s)
ax.annotate("",xy=(9.9,5.16),xytext=(9.9,5.86),
            arrowprops=dict(arrowstyle="->",color=MUTE,lw=1.6))
ax.text(9.55,5.52,"nothing in between -\nso price travels to it",fontsize=8.5,
        color=MUTE,fontweight="bold",ha="right",va="center")
ax.text(10.8,6.60,"once demand breaks, the next zone down is not an entry -",
        ha="right",va="top",fontsize=9,color=INK,fontweight="bold")
ax.text(10.8,6.45,"it is the TARGET, and it pulls price toward it like a magnet",
        ha="right",va="top",fontsize=9,color=INK,fontweight="bold")
ax.set_xlim(-0.9,11.0); ax.set_ylim(4.62,6.72)
finish(ax,"ZONES AS MAGNETS","the other way he uses a zone - as a destination, not a trade")
fig.tight_layout(); save(fig,"m2-04-magnet.png")

# ---------- 5. acceptance vs rejection ----------
# "when the market consolidates it's building volume at that price ... there's a
#  lot of ACCEPTANCE at that level and the chance of a high being formed here is
#  slim and this in fact is a bullish indication"
fig, axes = plt.subplots(1, 2, figsize=(10.6, 4.4))
REJ = [(0,5.70,5.86,5.90,5.66),(1,5.86,6.02,6.08,5.82),(2,6.02,6.18,6.24,5.98),
       (3,6.18,6.30,6.40,6.14),(4,6.30,6.12,6.36,6.08),(5,6.12,5.94,6.16,5.90),
       (6,5.94,5.76,5.98,5.70),(7,5.76,5.58,5.80,5.52),(8,5.58,5.42,5.62,5.36)]
ax = axes[0]
ax.add_patch(Rectangle((-0.8,6.30),10.4,0.14,facecolor="#2d6cb3",alpha=0.14,
                       edgecolor="#2d6cb3",lw=1.2,zorder=1))
for s_ in REJ: candle(ax, *s_)
ax.text(-0.7,6.48,"your level",fontsize=8.4,color="#2d6cb3",fontweight="bold",
        ha="left",va="bottom")
ax.annotate("one touch, then gone -\nalmost no volume trades there",xy=(3.2,6.42),
            xytext=(4.9,6.92),ha="right",va="top",fontsize=8.3,color=MUTE,
            fontweight="bold",arrowprops=dict(arrowstyle="->",color=MUTE,lw=1.1))
ax.text(8.7,5.22,"the level HELD  -  trade the reversal",ha="right",va="bottom",
        fontsize=9.2,color=SUPPLY,fontweight="bold")
ax.set_xlim(-0.9,8.9); ax.set_ylim(5.12,6.98)
finish(ax,"REJECTION","it tags the level and leaves again - nothing is built there")

ACC = [(0,5.70,5.86,5.90,5.66),(1,5.86,6.02,6.08,5.82),(2,6.02,6.18,6.24,5.98),
       (3,6.18,6.30,6.36,6.14),(4,6.30,6.34,6.42,6.26),(5,6.34,6.30,6.40,6.26),
       (6,6.30,6.36,6.43,6.27),(7,6.36,6.32,6.41,6.28),(8,6.32,6.52,6.58,6.30),
       (9,6.52,6.70,6.76,6.48)]
ax = axes[1]
ax.add_patch(Rectangle((-0.8,6.30),11.4,0.14,facecolor="#2d6cb3",alpha=0.14,
                       edgecolor="#2d6cb3",lw=1.2,zorder=1))
for s_ in ACC: candle(ax, *s_)
ax.text(-0.7,6.12,"the same level",fontsize=8.4,color="#2d6cb3",fontweight="bold",
        ha="left",va="top")
ax.annotate("it STAYS there - four bars\nof volume trading at the level",
            xy=(6,6.24),xytext=(1.0,5.62),ha="left",va="top",fontsize=8.3,
            color=MUTE,fontweight="bold",
            arrowprops=dict(arrowstyle="->",color=MUTE,lw=1.1))
ax.text(9.7,5.22,"ACCEPTANCE  -  expect it to fail, play continuation",
        ha="right",va="bottom",fontsize=9.2,color=DEMAND,fontweight="bold")
ax.set_xlim(-0.9,9.9); ax.set_ylim(5.12,6.98)
finish(ax,"ACCEPTANCE","buyers and sellers agree here, so \"the chance of a high being formed here is slim\"")
fig.tight_layout(w_pad=2.4); save(fig,"m2-05-acceptance.png")

# ---------- 6. same reaction, same result ----------
# "when there is a different reaction we're going to get a different result but
#  when there's the same reaction the odds are we're going to get the same result"
fig, axes = plt.subplots(1, 2, figsize=(10.6, 4.3))
YD = [(0,6.70,6.58,6.74,6.54),(1,6.58,6.42,6.62,6.38),(2,6.42,6.26,6.46,6.22),
      (3,6.26,6.10,6.30,6.06),(4,6.10,5.96,6.14,5.92),(5,5.96,5.82,6.00,5.78),
      (6,5.82,5.66,5.86,5.62),(7,5.66,5.50,5.70,5.46),(8,5.50,5.34,5.54,5.30),
      (9,5.34,5.18,5.38,5.14),(10,5.18,5.04,5.22,5.00)]
ax = axes[0]
for y0 in (6.18, 5.80, 5.44):
    ax.add_patch(Rectangle((-0.75,y0),11.5,0.12,facecolor=DEMAND,alpha=0.13,
                           edgecolor=DEMAND,lw=1.0,ls="--",zorder=1))
for s_ in YD: candle(ax, *s_)
ax.text(10.7,6.78,"three demand zones, all cut straight through",ha="right",
        va="top",fontsize=8.6,color=MUTE,fontweight="bold")
ax.text(10.7,4.92,"buyers never showed up anywhere",ha="right",va="bottom",
        fontsize=9.2,color=INK,fontweight="bold")
ax.set_xlim(-0.9,10.9); ax.set_ylim(4.84,6.90)
finish(ax,"YESTERDAY","what actually happened at the zones - this is the context")

TD = [(0,6.40,6.26,6.44,6.22),(1,6.26,6.10,6.30,6.06),(2,6.10,5.96,6.14,5.92),
      (3,5.96,5.80,6.00,5.76),(4,5.80,5.66,5.84,5.62),(5,5.66,5.54,5.70,5.50)]
ax = axes[1]
ax.add_patch(Rectangle((-0.75,5.38),11.5,0.14,facecolor=DEMAND,alpha=0.18,
                       edgecolor=DEMAND,lw=1.2,zorder=1))
for s_ in TD: candle(ax, *s_)
ax.text(10.7,5.30,"a fresh demand zone - and the same selling into it",
        ha="right",va="top",fontsize=8.6,color=MUTE,fontweight="bold")
ax.text(10.7,4.92,"so: do NOT buy it on sight - make buyers prove themselves",
        ha="right",va="bottom",fontsize=9.2,color=INK,fontweight="bold")
ax.set_xlim(-0.9,10.9); ax.set_ylim(4.84,6.90)
finish(ax,"TODAY","\"the same reaction - the odds are we're going to get the same result\"")
fig.tight_layout(w_pad=2.4); save(fig,"m2-06-same-reaction.png")

# ---------- 7. related markets ----------
# "i want to see other equities also showing strength ... if related markets or
#  related instruments do not agree with our analysis"
IDX = [1.000,0.985,0.970,0.952,0.935,0.918,0.902,0.886,0.872,0.860,0.852,
       0.860,0.874,0.890,0.906,0.922,0.938,0.952,0.965,0.978,0.990]
CMP_OK = [0.998,0.980,0.964,0.946,0.928,0.911,0.895,0.880,0.866,0.855,0.847,
          0.857,0.872,0.889,0.906,0.923,0.939,0.954,0.967,0.980,0.993]
CMP_NO = [0.998,0.980,0.962,0.944,0.926,0.909,0.893,0.878,0.864,0.852,0.843,
          0.837,0.831,0.826,0.820,0.815,0.809,0.803,0.797,0.791,0.785]
fig, axes = plt.subplots(1, 2, figsize=(10.6, 4.3))
for ax, cmp_, ttl, sub, verdict, vcol in (
        (axes[0], CMP_OK, "THEY AGREE",
         "the index bounces and the names that make it up bounce with it",
         "odds are in your favour  -  take it", DEMAND),
        (axes[1], CMP_NO, "THEY DISAGREE",
         "the index bounces, but the names that drive it keep sliding",
         "your own chart is lying to you  -  skip it", SUPPLY)):
    ax.add_patch(Rectangle((-0.6,0.840),21.8,0.024,facecolor=DEMAND,alpha=0.16,
                           edgecolor=DEMAND,lw=1.2,zorder=1))
    ax.plot(range(21), IDX, color=INK, lw=2.0, zorder=4,
            label="the index you trade")
    ax.plot(range(21), cmp_, color="#2d6cb3", lw=1.8, ls=(0,(5,3)), zorder=4,
            label="its biggest components")
    ax.text(-0.5, 0.832, "demand", fontsize=8.2, color=DEMAND,
            fontweight="bold", ha="left", va="top")
    lg = ax.legend(loc="lower left", frameon=False, fontsize=8.4,
                   handlelength=2.4, borderaxespad=0.2)
    for t in lg.get_texts(): t.set_fontweight("bold")
    ax.text(10, 1.022, verdict, fontsize=9.4, color=vcol, fontweight="bold",
            ha="center", va="top")
    ax.set_xlim(-0.9, 21.4); ax.set_ylim(0.762, 1.030)
    finish(ax, ttl, sub)
fig.tight_layout(w_pad=2.4); save(fig,"m2-07-related-markets.png")


print("done")
