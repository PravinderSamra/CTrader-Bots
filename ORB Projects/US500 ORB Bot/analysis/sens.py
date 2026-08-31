import csv, collections, datetime as dt, random
rows=list(csv.DictReader(open("us500_trades.csv")))
for r in rows:
    r["r"]=float(r["r"]); r["entry_time"]=dt.datetime.fromisoformat(r["entry_time"])
byday=collections.defaultdict(list)
for r in rows: byday[r["entry_time"].date()].append(r["r"])
DAYS=[byday[d] for d in sorted(byday)]
base=sum(x for d in DAYS for x in d)/sum(len(d) for d in DAYS)
ACCT=100_000
random.seed(3)

def run(risk,shift,target_pct,max_days,block=20):
    eq=ACCT; floor=ACCT*0.90; target=ACCT*(1+target_pct)
    d=0;i=0;left=0
    while d<max_days:
        if left==0: i=random.randrange(len(DAYS)); left=block
        day=DAYS[i%len(DAYS)]; i+=1; left-=1; d+=1
        dfloor=eq*0.95
        for x in day:
            eq += (x+shift)*risk
            if eq<=dfloor or eq<=floor: return "bust",d
        if eq>=target: return "pass",d
    return "timeout",d

print(f"observed expectancy {base:+.4f}R;  95% CI was +0.009R .. +0.140R")
print("\nIf the TRUE edge is at the bottom / middle / top of that range:")
print(f"{'true exp':>10}{'risk':>8}{'PASS P1':>9}{'BUST':>7}{'median days':>13}")
for true_exp in (0.009, 0.040, 0.073, 0.140):
    shift = true_exp - base
    for risk in (600, 800):
        res=collections.Counter(); days=[]
        for _ in range(8000):
            o,d=run(risk,shift,0.10,2000); res[o]+=1
            if o=="pass": days.append(d)
        days.sort(); md=days[len(days)//2] if days else None
        print(f"{true_exp:>+10.3f}{risk:>8}{100*res['pass']/8000:>8.1f}%"
              f"{100*res['bust']/8000:>6.1f}%{md if md else '-':>13}")
