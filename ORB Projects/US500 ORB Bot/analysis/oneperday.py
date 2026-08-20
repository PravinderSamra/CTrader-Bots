import collections, datetime as dt, statistics as st, random
exec(open("compare.py").read().split("A=parse")[0])
B=parse("log3r/3R log.txt")
B.sort(key=lambda x:x["t"])

first=[]; second=[]; seen=set()
for x in B:
    d=x["t"].date()
    (first if d not in seen else second).append(x); seen.add(d)
print(f"{'':<16}{'trades':>8}{'net $':>10}{'winners':>9}{'win%':>7}{'$/trade':>9}{'R/trade':>9}")
for nm,g in (("all (2/day)",B),("1st of day",first),("2nd of day",second)):
    w=sum(1 for x in g if x["net"]>0)
    print(f"{nm:<16}{len(g):>8}{sum(x['net'] for x in g):>10,.0f}{w:>9}"
          f"{100*w/len(g):>6.1f}%{sum(x['net'] for x in g)/len(g):>9.2f}"
          f"{sum(x['r'] for x in g)/len(g):>9.4f}")
print(f"\nyour figures: 2/day $7,862.25 / 1099 / 546 winners | 1/day $7,412 / 937 / 464")

R2=[x["r"] for x in second]; n=len(R2); e=sum(R2)/n; sd=st.stdev(R2)
print(f"\nIs the 2nd trade's edge real?  n={n}, exp {e:+.4f}R, t={e/(sd/n**0.5):.2f}")
print(f"  -> {'indistinguishable from zero' if abs(e/(sd/n**0.5))<1.96 else 'significant'}")

def maxdd(seq):
    peak=cum=0.0;w=0.0
    for x in seq: cum+=x;peak=max(peak,cum);w=min(w,cum-peak)
    return -w
byday_all=collections.defaultdict(float); byday_one=collections.defaultdict(float)
for x in B:     byday_all[x["t"].date()]+=x["r"]
for x in first: byday_one[x["t"].date()]+=x["r"]
days=sorted(byday_all)
A_=[byday_all[d] for d in days]; O_=[byday_one[d] for d in days]
print(f"\n{'':<16}{'total R':>10}{'maxDD':>9}{'ret/DD':>9}{'worst day':>11}{'sd/day':>9}")
for nm,s in (("2 per day",A_),("1 per day",O_)):
    print(f"{nm:<16}{sum(s):>10.1f}{maxdd(s):>9.1f}{sum(s)/maxdd(s):>9.2f}{min(s):>11.2f}{st.stdev(s):>9.3f}")

# The real test: sized for FTMO, which passes faster?
ACCT=100_000; random.seed(31)
PAIRS={"2 per day":[ [x["r"] for x in B if x["t"].date()==d] for d in days ],
       "1 per day":[ [x["r"] for x in first if x["t"].date()==d] for d in days ]}
def attempt(seq,risk,max_days=3000,block=20):
    eq=ACCT;floor=ACCT*0.90;tgt=ACCT*1.10;d=0;i=0;left=0
    while d<max_days:
        if left==0: i=random.randrange(len(seq)); left=block
        day=seq[i%len(seq)]; i+=1; left-=1; d+=1
        dfloor=eq*0.95
        for x in day:
            eq+=x*risk
            if eq<=dfloor or eq<=floor: return None
        if eq>=tgt: return d
    return -1
def solve(seq,want=0.90,n=3000):
    lo,hi=50,6000
    for _ in range(14):
        mid=(lo+hi)/2
        res=[attempt(seq,mid) for _ in range(n)]
        if sum(1 for r in res if r and r>0)/n>=want: lo=mid
        else: hi=mid
    res=[attempt(seq,lo) for _ in range(6000)]
    dd=sorted(r for r in res if r and r>0)
    return lo,(dd[len(dd)//2] if dd else None),sum(1 for r in res if r is None)/len(res)
print(f"\nFTMO Phase 1, risk sized for a ~90% pass rate:")
print(f"{'':<16}{'risk/trade':>12}{'median days':>13}{'~months':>9}{'bust':>7}")
for nm,seq in PAIRS.items():
    risk,md,bust=solve(seq)
    print(f"{nm:<16}{risk:>11,.0f}{md if md else '-':>13}{md/21 if md else 0:>8.1f}{100*bust:>6.1f}%")
