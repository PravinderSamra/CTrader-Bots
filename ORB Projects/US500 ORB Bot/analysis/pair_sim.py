import collections,datetime as dt,random,statistics as st,io,contextlib
with contextlib.redirect_stdout(io.StringIO()):
    exec(open("corr2.py").read().split("def pearson")[0])
allday=sorted(set(us_day)|set(nas_day))
PAIRS=[(us_day.get(d,0.0), nas_day.get(d,0.0)) for d in allday]   # real joint distribution
US=[p[0] for p in PAIRS]; NAS=[p[1] for p in PAIRS]
ACCT=100_000; random.seed(21)

def attempt(risk, mode, target=0.10, max_days=3000, block=20):
    eq=ACCT; floor=ACCT*0.90; tgt=ACCT*(1+target); d=0; i=0; left=0; j=0
    while d<max_days:
        if left==0:
            i=random.randrange(len(PAIRS)); j=random.randrange(len(PAIRS)); left=block
        if mode=="us":     day=[US[i%len(US)]]
        elif mode=="nas":  day=[NAS[i%len(NAS)]]
        elif mode=="both": day=[US[i%len(US)], NAS[i%len(NAS)]]          # real correlation
        else:              day=[US[i%len(US)], NAS[j%len(NAS)]]          # decorrelated
        i+=1; j+=1; left-=1; d+=1
        dfloor=eq*0.95
        for x in day:
            eq += x*risk
            if eq<=dfloor or eq<=floor: return None
        if eq>=tgt: return d
    return -1

def solve(mode, want=0.90, n=3000):
    lo,hi=50,5000
    for _ in range(14):
        mid=(lo+hi)/2
        res=[attempt(mid,mode) for _ in range(n)]
        p=sum(1 for r in res if r and r>0)/n
        if p>=want: lo=mid
        else: hi=mid
    res=[attempt(lo,mode) for _ in range(6000)]
    days=sorted(r for r in res if r and r>0)
    return lo, (days[len(days)//2] if days else None), sum(1 for r in res if r is None)/len(res)

print("FTMO Phase 1 (+10%), EAs allowed, no time limit.")
print("Risk sized so each setup passes ~90% of the time.\n")
print(f"{'setup':<34}{'risk/trade':>12}{'median days':>13}{'~months':>9}{'bust':>7}")
for mode,lbl in (("us","US500 3R alone"),("nas","NAS100 LRB alone"),
                 ("both","BOTH as they really are (r=+0.48)"),
                 ("indep","BOTH if truly uncorrelated (r=0)")):
    risk,md,bust=solve(mode)
    print(f"{lbl:<34}{risk:>11,.0f}{md if md else '-':>13}{md/21 if md else 0:>8.1f}{100*bust:>6.1f}%")
