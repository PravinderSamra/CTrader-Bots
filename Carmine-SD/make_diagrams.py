"""Schematic diagrams for the Carmine Rosato supply & demand syllabus, Module 1.

Every diagram illustrates a rule stated in the module-1 transcripts. Nothing here
is invented technique - see 02-documentation/module-1.md for the sourcing.
"""
from sdplot import (plt, Rectangle, FancyArrow, OUT, UP, DN, DEMAND,
                    SUPPLY, INK, MUTE, candle, finish, save)


# ---------- 1. anatomy: demand and supply side by side ----------
fig, axes = plt.subplots(1, 2, figsize=(10.4, 3.9))

ax = axes[0]                                   # DEMAND
seq = [(0,5.9,5.6,6.0,5.5),(1,5.6,5.3,5.7,5.2),(2,5.3,5.05,5.35,4.95)]
base = [(3,5.05,5.1,5.2,4.95),(4,5.1,5.02,5.18,4.95),(5,5.02,5.12,5.2,4.96)]
dep  = [(6,5.12,6.1,6.2,5.1),(7,6.1,6.6,6.7,6.05),(8,6.6,6.9,7.0,6.5)]
ret  = [(9,6.9,6.4,6.95,6.3),(10,6.4,5.9,6.5,5.6),(11,5.9,5.3,6.0,5.08),
        (12,5.3,6.0,6.1,5.12),(13,6.0,6.6,6.7,5.95)]
for s in seq+base+dep+ret: candle(ax,*s)
ax.add_patch(Rectangle((2.55,4.95),11.1,0.27,facecolor=DEMAND,alpha=0.16,
                       edgecolor=DEMAND,lw=1.2,zorder=1))
ax.annotate("BASE\n(balance)",(4,4.72),ha="center",fontsize=8.5,color=INK,fontweight="bold")
ax.annotate("DEPARTURE\n(imbalance)",(7.6,7.15),ha="center",fontsize=8.5,color=INK,fontweight="bold")
ax.annotate("price returns -\nunfilled buy orders fill here",(11.4,4.45),ha="center",
            fontsize=8,color=MUTE)
ax.set_ylim(4.2,7.6); ax.set_xlim(-0.7,14)
finish(ax,"DEMAND ZONE","base, then a violent move UP")

ax = axes[1]                                   # SUPPLY
seq = [(0,5.1,5.4,5.5,5.0),(1,5.4,5.7,5.8,5.35),(2,5.7,5.95,6.05,5.65)]
base = [(3,5.95,5.9,6.05,5.85),(4,5.9,5.98,6.06,5.84),(5,5.98,5.88,6.04,5.82)]
dep  = [(6,5.88,4.9,5.9,4.8),(7,4.9,4.4,4.95,4.3),(8,4.4,4.1,4.5,4.0)]
ret  = [(9,4.1,4.6,4.7,4.05),(10,4.6,5.1,5.2,4.5),(11,5.1,5.7,5.92,5.05),
        (12,5.7,5.0,5.9,4.9),(13,5.0,4.4,5.1,4.3)]
for s in seq+base+dep+ret: candle(ax,*s)
ax.add_patch(Rectangle((2.55,5.82),11.1,0.26,facecolor=SUPPLY,alpha=0.16,
                       edgecolor=SUPPLY,lw=1.2,zorder=1))
ax.annotate("BASE\n(balance)",(4,6.35),ha="center",fontsize=8.5,color=INK,fontweight="bold")
ax.annotate("DEPARTURE\n(imbalance)",(7.6,3.6),ha="center",fontsize=8.5,color=INK,fontweight="bold")
ax.annotate("price returns -\nunfilled sell orders fill here",(11.4,6.6),ha="center",
            fontsize=8,color=MUTE)
ax.set_ylim(3.2,7.0); ax.set_xlim(-0.7,14)
finish(ax,"SUPPLY ZONE","base, then a violent move DOWN")
fig.tight_layout(); save(fig,"01-anatomy.png")


# ---------- 2. strong vs weak departure ----------
fig, axes = plt.subplots(1,2,figsize=(10.4,3.5))
ax=axes[0]
for s in [(0,5.0,5.05,5.12,4.95),(1,5.05,4.98,5.1,4.92),(2,4.98,5.06,5.13,4.94)]: candle(ax,*s)
for s in [(3,5.06,6.3,6.45,5.02),(4,6.3,7.1,7.25,6.25),(5,7.1,7.6,7.7,7.0)]: candle(ax,*s)
ax.add_patch(Rectangle((-0.45,4.92),6.2,0.22,facecolor=DEMAND,alpha=0.16,edgecolor=DEMAND,lw=1.2))
ax.text(2.6,3.9,"big bodies, little overlap,\nprice leaves and does not come back",
        ha="center",fontsize=8.5,color=INK)
ax.text(5.6,7.75,"TRADE THIS",ha="right",fontsize=10,fontweight="bold",color=DEMAND)
ax.set_ylim(3.4,8.1); ax.set_xlim(-0.8,6.1)
finish(ax,"STRONG departure = strong zone")

ax=axes[1]
for s in [(0,5.0,5.05,5.12,4.95),(1,5.05,4.98,5.1,4.92),(2,4.98,5.06,5.13,4.94)]: candle(ax,*s)
for s in [(3,5.06,5.3,5.5,5.0),(4,5.3,5.2,5.45,5.08),(5,5.2,5.45,5.6,5.1)]: candle(ax,*s)
ax.add_patch(Rectangle((-0.45,4.92),6.2,0.22,facecolor=MUTE,alpha=0.14,edgecolor=MUTE,lw=1.2))
ax.text(2.6,3.9,"small bodies, heavy overlap,\nprice drifts rather than leaves",
        ha="center",fontsize=8.5,color=INK)
ax.text(5.6,7.75,"IGNORE THIS",ha="right",fontsize=10,fontweight="bold",color=MUTE)
ax.set_ylim(3.4,8.1); ax.set_xlim(-0.8,6.1)
finish(ax,"WEAK departure = no zone at all")
fig.tight_layout(); save(fig,"02-strength.png")


# ---------- 3. freshness ----------
fig,ax=plt.subplots(figsize=(10.4,3.6))
base=[(0,5.0,5.06,5.13,4.95),(1,5.06,4.99,5.11,4.93)]
dep =[(2,4.99,6.1,6.2,4.96),(3,6.1,6.8,6.9,6.05)]
t1  =[(4,6.8,6.2,6.85,6.1),(5,6.2,5.4,6.3,5.02),(6,5.4,6.3,6.4,5.1),(7,6.3,6.8,6.9,6.2)]
t2  =[(8,6.8,6.1,6.85,6.0),(9,6.1,5.3,6.2,4.98),(10,5.3,4.6,5.35,4.4),(11,4.6,4.1,4.7,4.0)]
for s in base+dep+t1+t2: candle(ax,*s)
ax.add_patch(Rectangle((-0.45,4.93),12.1,0.22,facecolor=DEMAND,alpha=0.16,edgecolor=DEMAND,lw=1.2))
ax.annotate("1st touch - FRESH\norders still sitting here,\nprice bounces",(5.5,6.9),
            ha="center",fontsize=8.5,color=DEMAND,fontweight="bold")
ax.annotate("2nd touch - USED\norders already filled,\nprice cuts straight through",(10,6.2),
            ha="center",fontsize=8.5,color=DN,fontweight="bold")
ax.set_ylim(3.7,7.6); ax.set_xlim(-0.9,12.3)
finish(ax,"FRESHNESS: a zone is ammunition, and it gets spent",
       "once price has been back into a zone, there are fewer unfilled orders left to turn it")
fig.tight_layout(); save(fig,"03-freshness.png")


# ---------- 4. the equation ----------
fig,ax=plt.subplots(figsize=(10.4,2.5))
def box(x,w,t,s,col):
    ax.add_patch(Rectangle((x,0.3),w,0.52,facecolor=col,alpha=0.14,edgecolor=col,lw=1.6))
    ax.text(x+w/2,0.66,t,ha="center",fontsize=10.5,fontweight="bold",color=INK)
    ax.text(x+w/2,0.44,s,ha="center",fontsize=8.3,color=MUTE)
box(0.02,0.27,"WHERE","the zone\n(the advertiser)",DEMAND)
ax.text(0.325,0.56,"+",ha="center",fontsize=17,color=INK)
box(0.35,0.30,"WHEN & WHY","price and volume\n(the validator)","#2d6cb3")
ax.text(0.685,0.56,"=",ha="center",fontsize=17,color=INK)
box(0.71,0.27,"A TRADE","both, or nothing",INK)
ax.text(0.5,0.13,'Missing either piece: "my edge is not present and I am a spectator on the sidelines"',
        ha="center",fontsize=8.6,style="italic",color=MUTE)
ax.set_xlim(0,1); ax.set_ylim(0.05,0.95)
finish(ax,"THE TWO-STEP EQUATION","a zone alone is never a reason to enter")
fig.tight_layout(); save(fig,"04-equation.png")


# ---------- 5. trend filter ----------
fig,ax=plt.subplots(figsize=(8.6,3.3))
cells=[(0,1,"UPTREND","DEMAND zones","reliable - look to BUY here",DEMAND,True),
       (1,1,"UPTREND","SUPPLY zones","weak - use as a TARGET, not an entry",MUTE,False),
       (0,0,"DOWNTREND","DEMAND zones","weak - use as a TARGET, not an entry",MUTE,False),
       (1,0,"DOWNTREND","SUPPLY zones","reliable - look to SELL here",SUPPLY,True)]
for cx,cy,trend,zone,verdict,col,strong in cells:
    ax.add_patch(Rectangle((cx*0.5+0.01,cy*0.5+0.01),0.47,0.46,
                 facecolor=col,alpha=0.17 if strong else 0.07,edgecolor=col,lw=1.5))
    ax.text(cx*0.5+0.245,cy*0.5+0.39,"%s  /  %s"%(trend,zone),ha="center",
            fontsize=9,fontweight="bold",color=INK)
    ax.text(cx*0.5+0.245,cy*0.5+0.19,verdict,ha="center",fontsize=8.6,color=INK if strong else MUTE)
ax.set_xlim(0,1); ax.set_ylim(0,1)
finish(ax,"THE TREND FILTER","it is a reversal strategy, so it only works with the trend behind it")
fig.tight_layout(); save(fig,"05-trend.png")


# ---------- 6. entry, stop, target ----------
fig,ax=plt.subplots(figsize=(10.4,4.2))
down=[(0,7.4,7.0,7.5,6.9),(1,7.0,6.6,7.1,6.5),(2,6.6,6.1,6.7,5.9),(3,6.1,5.6,6.2,5.4)]
inzone=[(4,5.6,5.25,5.7,5.08),(5,5.25,5.35,5.45,5.12),(6,5.35,5.2,5.45,5.1)]
turn=[(7,5.2,5.6,5.7,5.18),(8,5.6,5.55,5.75,5.4),(9,5.55,5.95,6.05,5.45),
      (10,5.95,6.4,6.5,5.9),(11,6.4,6.9,7.0,6.35),(12,6.9,7.3,7.45,6.85)]
for s in down+inzone+turn: candle(ax,*s)
ax.add_patch(Rectangle((-0.45,5.05),13.1,0.33,facecolor=DEMAND,alpha=0.16,edgecolor=DEMAND,lw=1.2))
ax.add_patch(Rectangle((-0.45,7.35),13.1,0.3,facecolor=SUPPLY,alpha=0.14,edgecolor=SUPPLY,lw=1.2))
ax.axhline(5.72,xmin=0.56,xmax=0.98,color="#2d6cb3",lw=1.3,ls="--")
ax.text(12.6,5.80,"ENTRY  on the structure break",ha="right",fontsize=8.6,
        color="#2d6cb3",fontweight="bold")
ax.axhline(5.00,xmin=0.56,xmax=0.98,color=DN,lw=1.3,ls="--")
ax.text(12.6,4.84,"STOP  below the swing low that made the turn",ha="right",
        fontsize=8.6,color=DN,fontweight="bold")
ax.text(12.6,7.70,"TARGET  the opposing zone",ha="right",fontsize=8.6,
        color=SUPPLY,fontweight="bold")
ax.annotate("",xy=(9.2,5.45),xytext=(9.2,5.1),
            arrowprops=dict(arrowstyle="<->",color=INK,lw=1.1))
ax.text(9.45,5.24,"risk",fontsize=8,color=INK)
ax.set_ylim(4.5,8.0); ax.set_xlim(-0.9,13.3)
finish(ax,"ENTRY, STOP, TARGET",
       "the zone is where you look; the structure break is when you act")
fig.tight_layout(); save(fig,"06-entry.png")


# ---------- 7. absorption vs exhaustion ----------
# Two DIFFERENT mechanisms that both end a move. They look opposite on a
# footprint: absorption is heavy volume going nowhere, exhaustion is almost no
# volume at all. Both are in the support/resistance transcript.
def vbar(ax, price, vol, maxvol, x0, col, label):
    w = 1.9 * vol / maxvol
    ax.add_patch(Rectangle((x0, price - 0.055), w, 0.11,
                           facecolor=col, alpha=0.75, edgecolor="none", zorder=5))
    ax.text(x0 + w + 0.12, price, label, va="center", fontsize=7.6, color=INK)

fig, axes = plt.subplots(1, 2, figsize=(10.6, 4.1))

# ---- ABSORPTION: heavy volume, no progress
ax = axes[0]
for s in [(0,5.2,5.7,5.78,5.15),(1,5.7,6.1,6.2,5.65),(2,6.1,6.42,6.55,6.05),
          (3,6.42,6.38,6.56,6.3),(4,6.38,6.44,6.57,6.32),(5,6.44,6.3,6.55,6.22),
          (6,6.3,5.8,6.4,5.7),(7,5.8,5.25,5.9,5.15)]:
    candle(ax, *s)
ax.axhline(6.58, color=SUPPLY, lw=1.4, ls="--")
ax.text(-0.75, 6.65, "resistance", fontsize=8.4, color=SUPPLY)
for pr, v, lab in [(6.50,1200,"+1200"),(6.40,980,"+980"),(6.30,760,"+760")]:
    vbar(ax, pr, v, 1200, 8.3, "#2d6cb3", lab)
ax.text(8.3, 6.05, "huge BUY delta\nat the level", fontsize=8.2,
        color="#2d6cb3", fontweight="bold", va="top")
ax.text(5.1, 4.72, "buyers are aggressive and keep coming -\n"
                   "passive sellers eat every one of them", ha="center",
        fontsize=8.4, color=INK)
ax.text(10.6, 4.72, "ABSORPTION", ha="right", va="top", fontsize=11,
        fontweight="bold", color=SUPPLY)
ax.set_ylim(4.4, 7.15); ax.set_xlim(-0.9, 10.8)
finish(ax, "Effort with NO reward", "volume is HEAVY and price still cannot advance")

# ---- EXHAUSTION: volume tail, nobody left
ax = axes[1]
for s in [(0,5.2,5.7,5.78,5.15),(1,5.7,6.1,6.2,5.65),(2,6.1,6.38,6.48,6.05),
          (3,6.38,6.46,6.60,6.34),(4,6.46,6.30,6.52,6.24),(5,6.3,5.95,6.38,5.85),
          (6,5.95,5.5,6.0,5.4),(7,5.5,5.1,5.6,5.0)]:
    candle(ax, *s)
ax.axhline(6.58, color=SUPPLY, lw=1.4, ls="--")
ax.text(-0.75, 6.65, "resistance", fontsize=8.4, color=SUPPLY)
for pr, v, lab in [(6.52,29,"29"),(6.42,96,"96"),(6.30,740,"+740")]:
    vbar(ax, pr, v, 1200, 8.3, "#2d6cb3", lab)
ax.annotate("volume TAIL - almost nothing traded up here", xy=(8.2,6.52),
            xytext=(4.6,6.98), fontsize=8.2, color=INK, fontweight="bold", ha="center",
            arrowprops=dict(arrowstyle="->", color=INK, lw=0.9))
ax.text(5.1, 4.72, "buying simply stops - nobody is willing\n"
                   "to pay these prices any more", ha="center",
        fontsize=8.4, color=INK)
ax.text(10.6, 4.72, "EXHAUSTION", ha="right", va="top", fontsize=11,
        fontweight="bold", color=MUTE)
ax.set_ylim(4.4, 7.15); ax.set_xlim(-0.9, 10.8)
finish(ax, "The last buyer buys", "volume is THIN - the auction has finished at these prices")
fig.tight_layout(); save(fig, "07-absorption-exhaustion.png")


# ---------- 8. the trap ----------
fig,ax=plt.subplots(figsize=(10.4,3.8))
run=[(0,5.2,5.6,5.7,5.15),(1,5.6,5.95,6.05,5.55),(2,5.95,6.25,6.35,5.9),
     (3,6.25,6.35,6.45,6.2),(4,6.35,6.42,6.5,6.3)]
brk=[(5,6.42,6.62,6.75,6.38),(6,6.62,6.55,6.78,6.45)]
fail=[(7,6.55,6.1,6.6,6.0),(8,6.1,5.6,6.15,5.5),(9,5.6,5.05,5.65,4.95),(10,5.05,4.6,5.1,4.5)]
for s in run+brk+fail: candle(ax,*s)
ax.axhline(6.45,color=SUPPLY,lw=1.4,ls="--")
ax.text(-0.6,6.52,"the obvious resistance everyone can see",fontsize=8.5,color=SUPPLY)
ax.add_patch(Rectangle((4.55,6.38),2.5,0.42,facecolor=SUPPLY,alpha=0.14,
                       edgecolor=SUPPLY,lw=1.2))
ax.annotate("breakout buyers get long HERE",(6,7.0),ha="center",fontsize=8.6,
            color=INK,fontweight="bold")
ax.annotate("they are trapped - their stops\nfuel the move down",(9.4,6.35),ha="center",
            fontsize=8.6,color=DN,fontweight="bold")
ax.set_ylim(4.1,7.4); ax.set_xlim(-0.9,11)
finish(ax,"FADING THE OBVIOUS",
       '"if my 80-year-old grandmother could draw it, the reliability of it is slim"')
fig.tight_layout(); save(fig,"08-trap.png")

# ---------- 9. the trend filter, drawn on price ----------
# The matrix says WHICH zone works. This shows WHY: in an uptrend price keeps
# cutting through supply (that is what an uptrend IS) while demand keeps holding.
fig, axes = plt.subplots(2, 1, figsize=(10.4, 7.6))

UPTREND = [
 (0,5.00,5.25,5.30,4.95),(1,5.25,5.45,5.52,5.20),(2,5.45,5.58,5.65,5.42),
 (3,5.58,5.52,5.62,5.48),(4,5.52,5.57,5.63,5.47),(5,5.57,5.50,5.62,5.46),
 (6,5.50,5.95,6.00,5.48),(7,5.95,6.20,6.28,5.90),(8,6.20,6.32,6.40,6.15),
 (9,6.32,6.28,6.42,6.24),(10,6.28,6.34,6.43,6.22),(11,6.34,5.95,6.40,5.90),
 (12,5.95,5.75,6.00,5.70),(13,5.75,5.62,5.80,5.52),(14,5.62,5.85,5.92,5.50),
 (15,5.85,6.15,6.22,5.80),(16,6.15,6.40,6.48,6.10),(17,6.40,6.70,6.78,6.35),
 (18,6.70,6.95,7.02,6.65),(19,6.95,7.15,7.22,6.90)]
ax = axes[0]
for s in UPTREND: candle(ax, *s)
ax.add_patch(Rectangle((2.55,5.45),17.1,0.21,facecolor=DEMAND,alpha=0.18,
                       edgecolor=DEMAND,lw=1.3,zorder=1))
ax.add_patch(Rectangle((8.55,6.20),11.1,0.25,facecolor=SUPPLY,alpha=0.15,
                       edgecolor=SUPPLY,lw=1.3,zorder=1))
ax.text(2.45,5.28,"DEMAND",fontsize=8.6,color=DEMAND,fontweight="bold",
        ha="left",va="top")
ax.text(8.45,6.52,"SUPPLY",fontsize=8.6,color=SUPPLY,fontweight="bold",
        ha="left",va="bottom")
ax.text(14,5.16,"price comes back,\nbuyers show up,\nit HOLDS",ha="center",
        va="top",fontsize=8.3,color=DEMAND,fontweight="bold")
ax.annotate("",xy=(14,5.50),xytext=(14,5.22),
            arrowprops=dict(arrowstyle="->",color=DEMAND,lw=1.3))
ax.annotate("price returns and\ncuts straight through it",xy=(16.4,6.52),
            xytext=(12.3,7.02),ha="center",va="bottom",fontsize=8.3,
            color=MUTE,fontweight="bold",
            arrowprops=dict(arrowstyle="->",color=MUTE,lw=1.3))
ax.text(-0.5,7.54,"so: BUY demand, and use supply only as a TARGET",ha="left",
        va="top",fontsize=9.4,color=INK,fontweight="bold")
ax.set_ylim(4.20,7.70); ax.set_xlim(-0.9,20.3)
finish(ax,"UPTREND - higher highs, higher lows",
       "an uptrend is price overcoming supply, so supply zones are the ones that fail")

DOWNTREND = [
 (0,7.15,6.90,7.20,6.85),(1,6.90,6.70,6.95,6.62),(2,6.70,6.56,6.75,6.50),
 (3,6.56,6.62,6.68,6.52),(4,6.62,6.57,6.67,6.51),(5,6.57,6.64,6.70,6.53),
 (6,6.64,6.20,6.68,6.15),(7,6.20,5.95,6.25,5.88),(8,5.95,5.83,6.00,5.75),
 (9,5.83,5.88,5.95,5.78),(10,5.88,5.81,5.93,5.72),(11,5.81,6.20,6.25,5.78),
 (12,6.20,6.40,6.45,6.15),(13,6.40,6.55,6.68,6.35),(14,6.55,6.30,6.70,6.25),
 (15,6.30,6.00,6.35,5.95),(16,6.00,5.70,6.05,5.62),(17,5.70,5.45,5.75,5.38),
 (18,5.45,5.20,5.50,5.15),(19,5.20,5.00,5.25,4.95)]
ax = axes[1]
for s in DOWNTREND: candle(ax, *s)
ax.add_patch(Rectangle((2.55,6.50),17.1,0.22,facecolor=SUPPLY,alpha=0.18,
                       edgecolor=SUPPLY,lw=1.3,zorder=1))
ax.add_patch(Rectangle((8.55,5.70),11.1,0.26,facecolor=DEMAND,alpha=0.15,
                       edgecolor=DEMAND,lw=1.3,zorder=1))
ax.text(2.45,6.79,"SUPPLY",fontsize=8.6,color=SUPPLY,fontweight="bold",
        ha="left",va="bottom")
ax.text(8.45,5.62,"DEMAND",fontsize=8.6,color=DEMAND,fontweight="bold",
        ha="left",va="top")
ax.text(14,7.84,"price comes back,\nsellers show up,\nit HOLDS",ha="center",
        va="top",fontsize=8.3,color=SUPPLY,fontweight="bold")
ax.annotate("",xy=(14,6.72),xytext=(14,7.00),
            arrowprops=dict(arrowstyle="->",color=SUPPLY,lw=1.3))
ax.annotate("price returns and\ncuts straight through it",xy=(16.5,5.66),
            xytext=(11.4,5.30),ha="center",va="top",fontsize=8.3,
            color=MUTE,fontweight="bold",
            arrowprops=dict(arrowstyle="->",color=MUTE,lw=1.3))
ax.text(-0.5,4.52,"so: SELL supply, and use demand only as a TARGET",ha="left",
        va="bottom",fontsize=9.4,color=INK,fontweight="bold")
ax.set_ylim(4.35,8.00); ax.set_xlim(-0.9,20.3)
finish(ax,"DOWNTREND - lower highs, lower lows",
       "a downtrend is price overcoming demand, so demand zones are the ones that fail")
fig.tight_layout(h_pad=2.6); save(fig,"09-trend-on-price.png")

print("done")
