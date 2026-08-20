import csv, datetime as dt, collections, statistics as st
rows = list(csv.DictReader(open("us500_trades.csv")))
for r in rows:
    for k in ("net","r","pips","riskpips"): r[k]=float(r[k])
    r["entry_time"]=dt.datetime.fromisoformat(r["entry_time"])
    r["year"]=r["entry_time"].year
rows.sort(key=lambda r:-r["r"])
print("=== TOP 15 TRADES ===")
print(f"{'date':<12}{'side':>6}{'R':>7}{'net $':>9}{'reason':>12}")
for r in rows[:15]:
    print(f"{r['entry_time']:%Y-%m-%d}{r['side']:>6}{r['r']:>7.2f}{r['net']:>9.0f}{r['reason']:>12}")
yr = collections.Counter(r['year'] for r in rows[:20])
print(f"\ntop 20 winners by year: {dict(sorted(yr.items()))}")
tot_by_year = collections.Counter()
for r in rows: tot_by_year[r['year']] += 1
print(f"all trades by year:    {dict(sorted(tot_by_year.items()))}")

print("\n=== R DISTRIBUTION ===")
R=[r['r'] for r in rows]
buckets=[(-99,-0.9),(-0.9,-0.5),(-0.5,-0.05),(-0.05,0.05),(0.05,0.5),(0.5,1),(1,2),(2,3),(3,99)]
for lo,hi in buckets:
    g=[x for x in R if lo<=x<hi]
    if g: print(f"  {lo:>5.2f} to {hi:>5.2f}R : {len(g):>4} trades ({100*len(g)/len(R):4.1f}%)  sum {sum(g):>+7.1f}R")

print("\n=== WHAT RISK SIZE SURVIVES A PROP DRAWDOWN LIMIT? ===")
rows.sort(key=lambda r:r["entry_time"])
seq=[r['r'] for r in rows]
def maxdd(s):
    peak=cum=0.0; w=0.0
    for x in s:
        cum+=x; peak=max(peak,cum); w=min(w,cum-peak)
    return -w
hist=maxdd(seq)
print(f"  worst drawdown seen in 1,099 trades: {hist:.1f}R")
for mult,label in ((1.0,"as seen"),(1.5,"1.5x safety"),(2.0,"2x safety")):
    budget=hist*mult
    for acct,ddpct in ((100000,0.10),(100000,0.06)):
        risk = acct*ddpct/budget
        per_year = 0.0731*risk*239
        print(f"  {label:<12} plan for {budget:5.1f}R | ${acct:,} acct, {ddpct:.0%} max DD "
              f"-> risk ${risk:6.0f}/trade -> ~${per_year:7,.0f}/yr ({100*per_year/acct:4.1f}%)")
