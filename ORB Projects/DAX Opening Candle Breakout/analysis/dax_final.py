import datetime as dt, statistics as st, random
import io,contextlib
with contextlib.redirect_stdout(io.StringIO()):
    exec(open("dax_cost.py").read().split("\nOS_A=dt.date")[0])

COST=1.5                       # points, round trip (spread + slippage)
GRID=[(am,tm) for am in (1.0,1.5,2.0,2.5,3.0) for tm in (0.5,1.0,1.5,2.0,3.0)]
IS_B=dt.date(2025,3,31); OS_A=dt.date(2025,4,1)
cache={g:run_cost(g[0],g[1],COST) for g in GRID}
def stat(tr):
    R=[t["r"] for t in tr]; n=len(R)
    if n<20: return None
    e=sum(R)/n; sd=st.stdev(R); w=[x for x in R if x>0]
    peak=cum=0.0; dd=0.0
    for x in R: cum+=x;peak=max(peak,cum);dd=min(dd,cum-peak)
    return dict(n=n,tot=sum(R),exp=e,win=100*len(w)/n,dd=-dd,t=e/(sd/n**0.5))

print(f"Selection now includes a {COST}pt round-trip cost. {len(GRID)} variants.\n")
print("IN-SAMPLE (to 2025-03-31)          OUT-OF-SAMPLE (2025-04 on)")
print(f"{'atr':>5}{'trail':>7}{'totR':>9}{'expR':>9}{'t':>6}   |{'totR':>9}{'expR':>9}{'t':>6}{'maxDD':>8}")
best=None; rows=[]
for g in GRID:
    i=stat([t for t in cache[g] if t["date"]<=IS_B]); o=stat([t for t in cache[g] if t["date"]>=OS_A])
    if not i or not o: continue
    rows.append((g,i,o))
    if best is None or i['exp']>best[1]['exp']: best=(g,i,o)
for g,i,o in rows:
    mark=" <-- picked" if g==best[0] else ""
    print(f"{g[0]:>5}{g[1]:>7}{i['tot']:>9.1f}{i['exp']:>+9.4f}{i['t']:>6.2f}   |"
          f"{o['tot']:>9.1f}{o['exp']:>+9.4f}{o['t']:>6.2f}{o['dd']:>8.1f}{mark}")

g,i,o=best
print(f"\nPicked in-sample: ATR x{g[0]}, trail {g[1]}xATR")
print(f"  in-sample      {i['tot']:+.1f}R  exp {i['exp']:+.4f}R  t={i['t']:.2f}")
print(f"  OUT-OF-SAMPLE  {o['tot']:+.1f}R  exp {o['exp']:+.4f}R  t={o['t']:.2f}  win {o['win']:.0f}%  maxDD {o['dd']:.1f}R")
print(f"  degradation    {100*(o['exp']-i['exp'])/abs(i['exp']):+.0f}%")

pos=sum(1 for _,_,oo in rows if oo['exp']>0)
print(f"\n  sanity: {pos}/{len(rows)} variants positive out-of-sample "
      f"(coin-flip would give ~{len(rows)//2})")

random.seed(4)
R=[t["r"] for t in cache[g]]; n=len(R); e=sum(R)/n
hits=sum(1 for _ in range(4000)
         if max(sum(random.choice((1,-1))*x for x in random.sample(R,n))/n
                for _ in range(len(GRID))) >= e)
print(f"  best-of-{len(GRID)} permutation p = {hits/4000:.4f} "
      f"({'PASSES' if hits/4000<0.05 else 'FAILS'} at 5%)")
