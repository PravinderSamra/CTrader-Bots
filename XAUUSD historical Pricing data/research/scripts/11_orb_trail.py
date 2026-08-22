"""ORB exit-management comparison: static far-side stop vs chandelier ratchet.
Result: static stop + 20:00 time exit wins (+0.083R) over 2.5*ATR trail (+0.018R)
and 4.0*ATR trail (+0.059R). Adaptive tightening gives back the tail edge.
"""
import numpy as np, pandas as pd
from importlib import import_module
import os
prep = import_module("00_prep")
OUT = os.path.join(os.path.dirname(__file__), "..", "output")
m1, m5, m15, h1, d1 = prep.load_all()
COST = 0.40
d1 = d1.copy(); d1["range"]=d1.high-d1.low
d1["atr20"]=d1["range"].rolling(20).mean().shift(1)
atr_map = pd.Series(d1["atr20"].values, index=(d1.index - pd.Timedelta(hours=22)).date)
m5x = m5.copy()
tr = np.maximum(m5x.high-m5x.low, np.maximum((m5x.high-m5x.close.shift()).abs(),(m5x.low-m5x.close.shift()).abs()))
atr5 = tr.ewm(alpha=1/14).mean()
g = m1.copy(); g["day"]=(g.index-pd.Timedelta(hours=22)).date; g["tod"]=g.index.hour*60+g.index.minute
lines=[]
def emit(s=""):
    print(s); lines.append(s)

def orb(trail_mult, label):
    rows=[]
    for day, seg in g.groupby("day"):
        atr = atr_map.get(day)
        if pd.isna(atr): continue
        o_s=13*60+30
        orb_=seg[(seg.tod>=o_s)&(seg.tod<o_s+30)]; rest=seg[(seg.tod>=o_s+30)&(seg.tod<20*60)]
        if len(orb_)<28 or len(rest)<30: continue
        o_hi,o_lo=orb_.high.max(),orb_.low.min()
        hu=rest.index[rest.high>=o_hi]; hd=rest.index[rest.low<=o_lo]
        tu=hu[0] if len(hu) else pd.NaT; td=hd[0] if len(hd) else pd.NaT
        if pd.isna(tu) and pd.isna(td): continue
        if pd.isna(td) or (not pd.isna(tu) and tu<td): side,t0,entry,stop0 = 1,tu,o_hi,o_lo
        else: side,t0,entry,stop0 = -1,td,o_lo,o_hi
        risk = abs(entry-stop0)
        live = rest[rest.index>=t0]
        stop = stop0; peak = entry; pnl=None
        for ts,bar in live.iterrows():
            if side==1:
                if bar.low<=stop: pnl=stop-entry-COST; break
                peak=max(peak,bar.close)
                if trail_mult: stop = max(stop, peak - trail_mult*atr5.asof(ts))
            else:
                if bar.high>=stop: pnl=entry-stop-COST; break
                peak=min(peak,bar.close)
                if trail_mult: stop = min(stop, peak + trail_mult*atr5.asof(ts))
        if pnl is None: pnl = side*(live.iloc[-1].close-entry)-COST
        rows.append(dict(day=day,pnl=pnl,risk=risk))
    t=pd.DataFrame(rows); t["R"]=t.pnl/t.risk
    t["year"]=pd.to_datetime(t.day.astype(str)).dt.year
    eq=t.R.cumsum(); dd=(eq-eq.cummax()).min()
    emit(f"{label}: n={len(t)} win%={(t.R>0).mean()*100:.1f} avgR={t.R.mean():+.3f} totR={t.R.sum():+.1f} maxDD={dd:.1f}R")
    emit(t.groupby("year")["R"].agg(["size","mean"]).round(3).to_string())

orb(None, "ORB static far-side stop (baseline)")
orb(2.5, "ORB + chandelier ratchet 2.5*ATR5m")
orb(4.0, "ORB + chandelier ratchet 4.0*ATR5m")
with open(os.path.join(OUT, "11_orb_trail.txt"), "w") as f:
    f.write("\n".join(lines))
