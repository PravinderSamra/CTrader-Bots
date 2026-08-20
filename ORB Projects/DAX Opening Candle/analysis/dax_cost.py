import datetime as dt, statistics as st, collections
exec(open("dax_ec.py").read().split("print(f\"GER40")[0])

# How big is the risk in actual DAX points at each ATR multiple?
sample=[]
for d in sorted(byday):
    day=byday[d]
    sig=next((i for i,b in enumerate(day) if b[1].hour==9 and b[1].minute==0), None)
    if sig is None or sig<14: continue
    a=atr(day,sig)
    if a: sample.append(a)
sample.sort()
print(f"ATR14 on M5 at the Frankfurt open: median {sample[len(sample)//2]:.1f} pts, "
      f"10th pct {sample[len(sample)//10]:.1f}, 90th {sample[9*len(sample)//10]:.1f}")
for m in (0.5,1.0,1.5,2.0):
    med=sample[len(sample)//2]*m
    print(f"  ATR x{m}: median risk {med:5.1f} pts   "
          f"-> a 1.5pt round-trip cost is {100*1.5/med:4.1f}% of risk")

def run_cost(atr_mult, trail_mult, cost_pts, ema_len=12, close_min=(17,30)):
    """Same logic, but pay `cost_pts` (spread+slippage, round trip) per trade."""
    out=[]
    for d in sorted(byday):
        day=byday[d]
        if len(day)<40: continue
        sig=next((i for i,b in enumerate(day) if b[1].hour==9 and b[1].minute==0), None)
        if sig is None or sig<ema_len or sig+2>=len(day): continue
        closes=[x[5] for x in day[max(0,sig-ema_len*3):sig+1]]
        if len(closes)<ema_len: continue
        e=ema(closes,ema_len); a=atr(day,sig)
        if not a or a<=0: continue
        side=1 if day[sig][5]>e else -1
        entry=day[sig+1][2]; risk=atr_mult*a
        stop=entry-side*risk; best=entry; exit_px=None
        for b in day[sig+1:]:
            if b[1].hour>close_min[0] or (b[1].hour==close_min[0] and b[1].minute>=close_min[1]):
                exit_px=b[2]; break
            if (b[4]<=stop) if side>0 else (b[3]>=stop): exit_px=stop; break
            best=max(best,b[3]) if side>0 else min(best,b[4])
            ns=best-side*trail_mult*risk
            stop=max(stop,ns) if side>0 else min(stop,ns)
        if exit_px is None: exit_px=day[-1][5]
        pnl=side*(exit_px-entry)-cost_pts          # pay the cost in points
        out.append(dict(date=d, r=pnl/risk))
    return out

OS_A=dt.date(2025,4,1)
print(f"\n=== OUT-OF-SAMPLE ({OS_A} onwards) WITH REALISTIC COSTS ===")
print(f"{'variant':<22}" + "".join(f"{f'{c}pt':>10}" for c in (0.0,1.0,1.5,2.5,4.0)))
for am,tm in ((0.5,0.5),(1.0,0.5),(1.5,0.5),(2.0,0.5),(1.0,1.0),(2.0,2.0)):
    cells=[]
    for c in (0.0,1.0,1.5,2.5,4.0):
        tr=[t for t in run_cost(am,tm,c) if t["date"]>=OS_A]
        R=[t["r"] for t in tr]
        cells.append(f"{sum(R):>+9.1f}R")
    print(f"ATR x{am}, trail {tm}   " + "".join(cells))
