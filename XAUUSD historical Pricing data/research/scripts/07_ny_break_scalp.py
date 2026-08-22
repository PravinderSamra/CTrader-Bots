"""NY-session Asia-break pullback scalp — the surviving variant of script 06.

Setup: Asia range (22:00-06:59 UTC) must be UNBROKEN through London (07:00-11:59).
First 1m close beyond either side during 12:00-15:59 UTC = break. Pullback = trade
back to the level within 120 min -> limit fill at level. Stop = far-side k*range.
Flat 20:55 UTC. Cost $0.40/oz. See 06_asia_pullback.py for the full (failing) grid.
"""
import numpy as np, pandas as pd
from importlib import import_module
import os
prep = import_module("00_prep")
OUT = os.path.join(os.path.dirname(__file__), "..", "output")
m1, m5, m15, h1, d1 = prep.load_all()
COST = 0.40
d1 = d1.copy(); d1["range"] = d1.high - d1.low
d1["atr20"] = d1["range"].rolling(20).mean().shift(1)
atr_map = pd.Series(d1["atr20"].values, index=(d1.index - pd.Timedelta(hours=22)).date)
g = m1.copy(); g["day"]=(g.index - pd.Timedelta(hours=22)).date; g["tod"]=g.index.hour*60+g.index.minute
FLAT = 20*60+55
lines=[]
def emit(s=""):
    print(s); lines.append(s)

def build(break_lo, break_hi):
    setups={}
    for day, seg in g.groupby("day"):
        atr = atr_map.get(day)
        if pd.isna(atr): continue
        tod=seg["tod"].to_numpy(); hi=seg["high"].to_numpy(); lo=seg["low"].to_numpy(); cl=seg["close"].to_numpy()
        am=(tod>=22*60)|(tod<7*60)
        if am.sum()<60: continue
        a_hi,a_lo = hi[am].max(), lo[am].min(); rng=a_hi-a_lo
        if rng<=0: continue
        win=(tod>=break_lo)&(tod<break_hi); iw=np.where(win)[0]
        if len(iw)<30: continue
        pre=(tod>=7*60)&(tod<break_lo); ip=np.where(pre)[0]
        if len(ip) and ((cl[ip]>a_hi).any() or (cl[ip]<a_lo).any()): continue
        up=iw[cl[iw]>a_hi]; dn=iw[cl[iw]<a_lo]
        iu=up[0] if len(up) else None; idn=dn[0] if len(dn) else None
        if iu is None and idn is None: continue
        if idn is None or (iu is not None and iu<idn): side,ib,level=1,iu,a_hi
        else: side,ib,level=-1,idn,a_lo
        setups[day]=dict(side=side,ib=ib,level=level,rng=rng,atr=atr,tod=tod,hi=hi,lo=lo,cl=cl)
    return setups

def run(setups, k, tp_mult, entry_mode, pull_max=120, entry_cutoff=18*60):
    rows=[]
    for day,s in setups.items():
        side,ib,level,rng = s["side"],s["ib"],s["level"],s["rng"]
        tod,hi,lo,cl = s["tod"],s["hi"],s["lo"],s["cl"]
        tb=tod[ib]; risk=k*rng; stop=level-side*risk
        j=None
        for i in range(ib+1,len(tod)):
            if tod[i]>=min(tb+pull_max,entry_cutoff) or tod[i]>=FLAT: break
            if (lo[i]<=level if side==1 else hi[i]>=level): j=i; break
        if j is None: continue
        if entry_mode=="limit":
            je, entry = j, level
        else:
            je=None
            for i in range(j,len(tod)):
                if tod[i]>=entry_cutoff or tod[i]>=FLAT: break
                if side==1 and lo[i]<=stop: break
                if side==-1 and hi[i]>=stop: break
                if (cl[i]>level if side==1 else cl[i]<level): je=i; break
            if je is None: continue
            entry=cl[je]; risk=abs(entry-stop)
            if risk<=0: continue
        tp = entry+side*tp_mult*risk if tp_mult else None
        pnl=None
        for i in range(je if entry_mode!="limit" else j, len(tod)):
            if tod[i]>=FLAT: break
            if side==1:
                if lo[i]<=stop: pnl=stop-entry-COST; break
                if tp and hi[i]>=tp: pnl=tp-entry-COST; break
            else:
                if hi[i]>=stop: pnl=entry-stop-COST; break
                if tp and lo[i]<=tp: pnl=entry-tp-COST; break
        if pnl is None:
            last=np.where(tod<FLAT)[0][-1]; pnl=side*(cl[last]-entry)-COST
        rows.append(dict(day=day,side=side,pnl=pnl,risk=risk))
    t=pd.DataFrame(rows)
    if len(t)==0: return t
    t["R"]=t.pnl/t.risk; t["date"]=pd.to_datetime(t.day.astype(str)); t["year"]=t.date.dt.year
    return t

def stats(t,label,yearly=True):
    if len(t)==0: emit(f"{label}: none"); return
    eq=t.R.cumsum(); dd=(eq-eq.cummax()).min()
    emit(f"{label}: n={len(t)} win%={(t.R>0).mean()*100:.1f} avgR={t.R.mean():+.3f} avgWin={t[t.R>0].R.mean():+.2f} avgLoss={t[t.R<=0].R.mean():+.2f} totR={t.R.sum():+.1f} maxDD={dd:.1f}R")
    if yearly:
        emit(t.groupby("year").agg(n=("R","size"),win=("R",lambda x:(x>0).mean()*100),totR=("R","sum"),avgR=("R","mean")).round(2).to_string())

ny = build(12*60, 16*60)
emit(f"pure NY-break days (Asia range survived London): {len(ny)}")
emit("\n--- variants ---")
for k,tp,mode in [(0.5,None,"limit"),(0.5,1.5,"limit"),(0.5,2.0,"limit"),(0.5,None,"confirm"),(0.5,2.0,"confirm"),(0.25,2.0,"confirm")]:
    stats(run(ny,k,tp,mode), f"k={k} tp={tp or 'none'} {mode}", yearly=False)
emit("\n--- primary: limit at level, k=0.5, no TP ---")
t_lim = run(ny,0.5,None,"limit"); stats(t_lim,"NY limit k=0.5 no-tp")
emit("\nby side:"); emit(t_lim.groupby("side").agg(n=("R","size"),win=("R",lambda x:(x>0).mean()*100),avgR=("R","mean")).round(3).to_string())
t_lim["ym"]=t_lim.date.dt.to_period("M")
mo=t_lim.groupby("ym")["R"].sum()
emit(f"\nmonthly R: mean={mo.mean():+.2f} med={mo.median():+.2f} best={mo.max():+.1f} worst={mo.min():+.1f} pos-months={(mo>0).mean()*100:.0f}% of {len(mo)}")
rs=t_lim.R.to_numpy(); np.random.seed(7)
NT=int(len(t_lim)/5.0)
sims=[];dds=[];streaks=[]
for _ in range(5000):
    p=np.random.choice(rs,NT,replace=True); eq=np.cumsum(p)
    sims.append(eq[-1]); dds.append((eq-np.maximum.accumulate(eq)).min())
    st=b=0
    for r in p:
        st = st+1 if r<=0 else 0; b=max(b,st)
    streaks.append(b)
sims=np.array(sims);dds=np.array(dds)
emit(f"\nMC 5000 sims, {NT}-trade years: annR p5={np.percentile(sims,5):+.0f} p25={np.percentile(sims,25):+.0f} med={np.percentile(sims,50):+.0f} p75={np.percentile(sims,75):+.0f} p95={np.percentile(sims,95):+.0f} P(neg year)={(sims<0).mean()*100:.0f}%")
emit(f"maxDD: med={np.percentile(dds,50):.1f}R p25={np.percentile(dds,25):.1f}R p5(worst)={np.percentile(dds,5):.1f}R | longest losing streak med={np.median(streaks):.0f} p95={np.percentile(streaks,95):.0f}")
lat = t_lim[t_lim.year>=2024]
stats(lat,"\n2024-2026 subset", yearly=False)
rs=lat.R.to_numpy(); NT=int(len(lat)/2.5); sims=[];dds=[]
for _ in range(5000):
    p=np.random.choice(rs,NT,replace=True); eq=np.cumsum(p)
    sims.append(eq[-1]); dds.append((eq-np.maximum.accumulate(eq)).min())
sims=np.array(sims);dds=np.array(dds)
emit(f"MC on 2024+ ({NT}/yr): annR p5={np.percentile(sims,5):+.0f} med={np.percentile(sims,50):+.0f} p95={np.percentile(sims,95):+.0f} P(neg)={(sims<0).mean()*100:.0f}% | maxDD med={np.percentile(dds,50):.1f}R p5={np.percentile(dds,5):.1f}R")
with open(os.path.join(OUT, "07_ny_break_scalp.txt"), "w") as f:
    f.write("\n".join(lines))
