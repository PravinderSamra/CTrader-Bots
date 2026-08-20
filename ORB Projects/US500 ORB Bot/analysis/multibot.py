import re,csv,collections,datetime as dt,random
exec(open("compare.py").read().split("A=parse")[0])   # reuse parser
B=parse("log3r/3R log.txt")
byday=collections.defaultdict(list)
for x in B: byday[x["t"].date()].append(x["r"])
DAYS=[byday[d] for d in sorted(byday)]
ACCT=100_000
random.seed(5)

def attempt(nbots, risk, rho, target=0.10, max_days=2000, block=20):
    """nbots independent-ish systems trading the same day. rho = P(all share the same day)."""
    eq=ACCT; floor=ACCT*0.90; target_eq=ACCT*(1+target)
    d=0; idx=[0]*nbots; left=0
    while d<max_days:
        if left==0:
            idx=[random.randrange(len(DAYS)) for _ in range(nbots)]; left=block
        shared = random.random()<rho
        if shared: idx=[idx[0]]*nbots
        d+=1; left-=1
        start=eq; dfloor=start*0.95
        todays=[]
        for b in range(nbots):
            todays += DAYS[idx[b]%len(DAYS)]
            idx[b]+=1
        random.shuffle(todays)
        for x in todays:
            eq += x*risk
            if eq<=dfloor or eq<=floor: return None
        if eq>=target_eq: return d
    return -1

def find_risk(nbots, rho, want_pass=0.90, n=3000):
    lo,hi=50,4000
    for _ in range(14):
        mid=(lo+hi)/2
        res=[attempt(nbots,mid,rho) for _ in range(n)]
        p=sum(1 for r in res if r and r>0)/n
        if p>=want_pass: lo=mid
        else: hi=mid
    risk=lo
    res=[attempt(nbots,risk,rho) for _ in range(6000)]
    days=sorted(r for r in res if r and r>0)
    busts=sum(1 for r in res if r is None)/len(res)
    return risk, (days[len(days)//2] if days else None), busts

print("Phase 1 (+10%), risk chosen so each configuration passes ~90% of the time")
print(f"{'bots':>5}{'correlation':>13}{'risk/trade':>12}{'total risk/day':>16}{'median days':>13}{'~months':>9}{'bust':>7}")
for nbots in (1,2,3,4):
    for rho,lbl in ((0.0,"uncorrelated"),(0.7,"correlated 0.7")):
        if nbots==1 and rho>0: continue
        risk,md,bust=find_risk(nbots,rho)
        print(f"{nbots:>5}{lbl:>13}{risk:>11,.0f}{risk*nbots*1.17:>15,.0f}"
              f"{md if md else '-':>13}{md/21 if md else 0:>8.1f}{100*bust:>6.1f}%")
