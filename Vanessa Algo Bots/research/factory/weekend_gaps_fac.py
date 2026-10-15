import sys, numpy as np
from collections import defaultdict
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import factory_d1 as F
IDX = ["us500","nas100","us30","ger40","uk100","fra40","eustx50","aus200","hk50"]
gaps=[]; per_wk=defaultdict(float); trades=0; held=0; costR=[]
for nm in IDX:
    dates,o,h,l,c = F.load(nm)
    n=len(c); tr=np.maximum(h-l, np.maximum(abs(h-np.roll(c,1)), abs(l-np.roll(c,1)))); tr[0]=h[0]-l[0]
    atr=np.convolve(tr,np.ones(20)/20,'full')[:n]; atr[:19]=np.nan
    sma=np.convolve(c,np.ones(20)/20,'full')[:n]; sma[:19]=np.nan
    sd=np.array([np.std(c[i-19:i+1]) if i>=19 else np.nan for i in range(n)])
    sig=c < sma-2.5*sd
    nxt=0
    for s in np.flatnonzero(sig):
        if s<nxt or s+5>=n or not atr[s]>0: continue
        trades+=1; A=atr[s]; anyw=False
        for j in range(s+2, s+6):
            if (dates[j]-dates[j-1]).days>=3:
                g=(o[j]-c[j-1])/(2*A); gaps.append((g,nm,dates[j],(o[j]/c[j-1]-1)*100)); per_wk[dates[j]]+=g; anyw=True
                costR.append(0.00025*c[j]/(2*A))
        held+=anyw; nxt=s+6
g=np.array([x[0] for x in gaps])
print("trades",trades,"held over a weekend",held, f"{held/trades:.0%}")
print("weekend gaps",len(g),"mean R %.3f"%g.mean(),"sum R %.1f"%g.sum(),"median cost to split R %.3f"%np.median(costR),"sum cost R %.1f"%sum(costR))
for x in sorted(gaps)[:8]: print("worst %.2fR %s %s %.1f%%"%x)
w=sorted(per_wk.items(), key=lambda z:z[1])[:5]; print("worst weekends all positions:", [(str(d),round(v,2)) for d,v in w])
print("share gaps < -1R", (g<-1).mean(), "< -0.5R", (g<-0.5).mean())
print("std %.3f t %.2f"%(g.std(), g.mean()/g.std()*len(g)**.5))
pos=[x for x in gaps if x[0]>0]; print("best", sorted(gaps)[-3:])
