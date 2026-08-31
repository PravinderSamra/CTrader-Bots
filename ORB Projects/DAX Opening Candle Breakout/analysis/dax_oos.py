import datetime as dt, statistics as st, random, collections
exec(open("dax_ec.py").read().split("print(f\"GER40")[0])   # reuse loader + run()

GRID=[(am,tm) for am in (0.5,1.0,1.5,2.0) for tm in (0.5,1.0,1.5,2.0)]
def seg(tr,a,b): return [t for t in tr if a<=t["date"]<=b]
def stat(tr):
    if len(tr)<20: return None
    R=[t["r"] for t in tr]; n=len(R); e=sum(R)/n
    sd=st.stdev(R); w=[x for x in R if x>0]
    peak=cum=0.0; dd=0.0
    for x in R: cum+=x;peak=max(peak,cum);dd=min(dd,cum-peak)
    return dict(n=n,tot=sum(R),exp=e,win=100*len(w)/n,dd=-dd,t=e/(sd/n**0.5))

IS_A,IS_B = dt.date(2023,12,1), dt.date(2025,3,31)
OS_A,OS_B = dt.date(2025,4,1),  dt.date(2026,12,31)
cache={g:run(atr_mult=g[0],trail=True,trail_mult=g[1]) for g in GRID}

print(f"IN-SAMPLE  {IS_A} .. {IS_B}   (pick the winner here)")
print(f"{'atr x':>7}{'trail x':>9}{'n':>6}{'totR':>9}{'expR':>9}{'t':>7}")
best=None
for g in GRID:
    s=stat(seg(cache[g],IS_A,IS_B))
    if not s: continue
    print(f"{g[0]:>7}{g[1]:>9}{s['n']:>6}{s['tot']:>9.1f}{s['exp']:>+9.4f}{s['t']:>7.2f}")
    if best is None or s['exp']>best[1]['exp']: best=(g,s)
print(f"\n  best in-sample: ATR x{best[0][0]}, trail {best[0][1]}xATR  (exp {best[1]['exp']:+.4f}R, t={best[1]['t']:.2f})")

print(f"\nOUT-OF-SAMPLE  {OS_A} .. {OS_B}   (the only number that counts)")
s=stat(seg(cache[best[0]],OS_A,OS_B))
print(f"  n={s['n']}  total {s['tot']:+.1f}R  exp {s['exp']:+.4f}R  win {s['win']:.1f}%  maxDD {s['dd']:.1f}R  t={s['t']:.2f}")
print(f"  degradation vs in-sample: {100*(s['exp']-best[1]['exp'])/abs(best[1]['exp']):+.0f}%")

print("\n  ...and every other variant out-of-sample, for context:")
for g in GRID:
    o=stat(seg(cache[g],OS_A,OS_B))
    if o: print(f"    ATR x{g[0]:<4} trail {g[1]:<4} n={o['n']:>4} total {o['tot']:>+7.1f}R exp {o['exp']:>+8.4f}R t={o['t']:>5.2f}")

print("\n=== MULTIPLE-TESTING CORRECTION ===")
full=stat(cache[best[0]])
print(f"  best variant on ALL data: t={full['t']:.2f}, exp {full['exp']:+.4f}R")
print(f"  variants tried: {len(GRID)}")
random.seed(9)
# how often does the BEST-OF-16 beat this by chance, if there is no edge?
R_all=[t["r"] for t in cache[best[0]]]
n=len(R_all)
hits=0; N=4000
for _ in range(N):
    mx=max(sum(random.choice((1,-1))*x for x in random.sample(R_all,n))/n for _ in range(len(GRID)))
    if mx>=full['exp']: hits+=1
print(f"  best-of-{len(GRID)} permutation p-value: {hits/N:.4f}  "
      f"({'PASSES' if hits/N<0.05 else 'FAILS'} at 5% after correction)")
