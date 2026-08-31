import csv, collections, datetime as dt, random
rows=list(csv.DictReader(open("us500_trades.csv")))
for r in rows:
    r["r"]=float(r["r"]); r["entry_time"]=dt.datetime.fromisoformat(r["entry_time"])
byday=collections.defaultdict(list)
for r in rows: byday[r["entry_time"].date()].append(r["r"])
DAYS=[byday[d] for d in sorted(byday)]          # each = list of trade Rs that day

ACCT=100_000; DAILY_LIM=0.05; TOTAL_LIM=0.10
random.seed(11)

def run(risk, target_pct, max_days, block=20):
    """One challenge attempt. Returns 'pass' / 'bust' / 'timeout' and days used."""
    eq=ACCT; floor=ACCT*(1-TOTAL_LIM); target=ACCT*(1+target_pct)
    d=0; i=random.randrange(len(DAYS)); left=0
    while d<max_days:
        if left==0: i=random.randrange(len(DAYS)); left=block   # block bootstrap
        day=DAYS[i % len(DAYS)]; i+=1; left-=1; d+=1
        start=eq; dfloor=start*(1-DAILY_LIM)
        for x in day:
            eq += x*risk
            if eq<=dfloor or eq<=floor: return "bust", d
        if eq>=target: return "pass", d
    return "timeout", d

def summarise(risk, target_pct, max_days, n=20000):
    out=collections.Counter(); days=[]
    for _ in range(n):
        res,d=run(risk,target_pct,max_days)
        out[res]+=1
        if res=="pass": days.append(d)
    days.sort()
    med = days[len(days)//2] if days else None
    return out["pass"]/n, out["bust"]/n, out["timeout"]/n, med

print("FTMO Phase 1  (+10% target, 10% max loss, 5% daily) — no time limit assumed")
print(f"{'risk/trade':>11}{'% of acct':>11}{'PASS':>8}{'BUST':>8}{'median days':>13}{'~months':>9}")
for risk in (200,300,400,500,600,800,1000):
    p,b,t,md = summarise(risk, 0.10, 2000)
    print(f"${risk:>10,}{100*risk/ACCT:>10.2f}%{100*p:>7.1f}%{100*b:>7.1f}%"
          f"{md if md else '-':>13}{md/21:>8.1f}" if md else "")

print("\nSame, but with a 6-month (126 trading day) practical patience limit")
print(f"{'risk/trade':>11}{'PASS':>8}{'BUST':>8}{'TOO SLOW':>10}")
for risk in (200,300,400,500,600,800,1000):
    p,b,t,md = summarise(risk, 0.10, 126)
    print(f"${risk:>10,}{100*p:>7.1f}%{100*b:>7.1f}%{100*t:>9.1f}%")

print("\nPhase 2 Verification (+5% target, same limits), no time limit")
print(f"{'risk/trade':>11}{'PASS':>8}{'BUST':>8}{'median days':>13}")
for risk in (300,500,600,800):
    p,b,t,md = summarise(risk, 0.05, 2000)
    print(f"${risk:>10,}{100*p:>7.1f}%{100*b:>7.1f}%{md if md else '-':>13}")

print("\nBOTH phases end-to-end (P1 then P2), no time limit")
for risk in (300,500,600,800):
    p1,_,_,d1 = summarise(risk,0.10,2000)
    p2,_,_,d2 = summarise(risk,0.05,2000)
    print(f"  ${risk:>5,}/trade -> P(fund) = {100*p1*p2:5.1f}%   "
          f"median ~{(d1 or 0)+(d2 or 0)} trading days (~{((d1 or 0)+(d2 or 0))/21:.0f} months)")
