import re, datetime as dt, statistics as st
ENT=re.compile(r"TRADE ENTERED: (\w+) \S+ vol=([\d.]+) entry=([\d.]+) SL=([\d.]+) TP=([\d.]+) riskPips=([\d.]+)")
CLS=re.compile(r"POSITION CLOSED: \S+ reason=(\S+) P/L=(-?[\d.]+) pips=(-?[\d.]+)")
TS=re.compile(r"^(\d{2})/(\d{2})/(\d{4})")
def parse(path):
    E=[];C=[]
    for line in open(path,encoding="utf-8",errors="replace"):
        if "TRADE ENTERED:" in line:
            m=ENT.search(line); d=TS.match(line)
            if m and d:
                g=d.groups()
                E.append(dict(date=dt.date(int(g[2]),int(g[1]),int(g[0])),
                              side=m.group(1), vol=float(m.group(2)), riskpips=float(m.group(6))))
        elif "POSITION CLOSED:" in line:
            m=CLS.search(line)
            if m: C.append(dict(reason=m.group(1), net=float(m.group(2)), pips=float(m.group(3))))
    out=[]
    for e,c in zip(E,C):
        risk=e["vol"]*e["riskpips"]
        out.append(dict(list(e.items())+list(c.items()), risk=risk, r=(c["net"]/risk if risk else 0)))
    return out
def maxdd(s):
    peak=cum=0.0;w=0.0
    for x in s: cum+=x;peak=max(peak,cum);w=min(w,cum-peak)
    return -w
A=parse("cA/1.1 log with clamp.txt"); B=parse("cB/1.1 log clamp off.txt")
print(f"{'':<12}{'trades':>7}{'net $':>10}{'medRisk$':>10}{'totR':>8}{'expR':>9}{'win%':>7}{'PF':>7}{'DD$':>9}{'DD_R':>7}")
for nm,g in (("clamp ON",A),("clamp OFF",B)):
    R=[x["r"] for x in g]; N=[x["net"] for x in g]
    wins=[x for x in N if x>0]; los=[x for x in N if x<=0]
    pf=sum(wins)/abs(sum(los)) if los else 0
    print(f"{nm:<12}{len(g):>7}{sum(N):>10,.0f}{st.median([x['risk'] for x in g]):>10,.0f}"
          f"{sum(R):>8.1f}{sum(R)/len(R):>9.4f}{100*len(wins)/len(g):>6.1f}%{pf:>7.3f}"
          f"{maxdd(N):>9,.0f}{maxdd(R):>7.1f}")
print(f"\nidentical entry dates: {[x['date'] for x in A]==[x['date'] for x in B]}")
print(f"identical riskPips:    {[x['riskpips'] for x in A]==[x['riskpips'] for x in B]}")
va=[x['vol'] for x in A]; vb=[x['vol'] for x in B]
print(f"volume ON  : median {st.median(va):.2f}  min {min(va):.2f}  max {max(va):.2f}")
print(f"volume OFF : median {st.median(vb):.2f}  min {min(vb):.2f}  max {max(vb):.2f}")
same=sum(1 for a,b in zip(va,vb) if abs(a-b)<1e-9)
print(f"trades sized identically: {same}/{len(va)}  -> clamp bound on {len(va)-same}")
print(f"\nnet P&L ratio OFF/ON: {sum(x['net'] for x in B)/sum(x['net'] for x in A):.2f}x")
print(f"R-expectancy    ON: {sum(x['r'] for x in A)/len(A):+.4f}   OFF: {sum(x['r'] for x in B)/len(B):+.4f}")
print("\n=== BY YEAR (net $) ===")
for y in (2022,2023,2024):
    a=[x for x in A if x['date'].year==y]; b=[x for x in B if x['date'].year==y]
    print(f"  {y}  n={len(a):>3}   ON {sum(x['net'] for x in a):>9,.0f}   OFF {sum(x['net'] for x in b):>9,.0f}")

import random, collections
print("\n" + "="*66)
print("IS THE EDGE DISTINGUISHABLE FROM ZERO? (clamp is irrelevant here - R is identical)")
print("="*66)
R=[x["r"] for x in B]; n=len(R); e=sum(R)/n; sd=st.stdev(R)
print(f"  n={n}  expectancy {e:+.4f}R  sd {sd:.2f}  t = {e/(sd/n**0.5):+.2f}")
random.seed(3)
boot=sorted(sum(random.choices(R,k=n))/n for _ in range(20000))
print(f"  bootstrap 90% CI: {boot[1000]:+.4f}R .. {boot[19000]:+.4f}R")
print(f"  -> {'NOT distinguishable from zero' if boot[1000]<0<boot[19000] else 'significantly non-zero'}")

print("\n=== EXIT REASONS ===")
for reason,c in collections.Counter(x['reason'] for x in B).most_common():
    sub=[x for x in B if x['reason']==reason]
    print(f"  {reason:<14}{c:>5} ({100*c/len(B):4.1f}%)  avg {sum(x['r'] for x in sub)/c:+.2f}R  "
          f"total {sum(x['r'] for x in sub):+7.1f}R")

print("\n=== WHERE DOES THE MONEY GO? ===")
wins=[x['r'] for x in B if x['net']>0]; los=[x['r'] for x in B if x['net']<=0]
print(f"  win rate {100*len(wins)/len(B):.1f}%   avg win {sum(wins)/len(wins):+.2f}R   "
      f"avg loss {sum(los)/len(los):+.2f}R")
print(f"  breakeven win rate needed at this payoff: "
      f"{100*abs(sum(los)/len(los))/(sum(wins)/len(wins)+abs(sum(los)/len(los))):.1f}%")
big=[x for x in B if x['r']>=2.5]
print(f"  trades reaching 2.5R+: {len(big)} ({100*len(big)/len(B):.1f}%)  "
      f"contributing {sum(x['r'] for x in big):+.1f}R")

print("\n=== DID THE 3R TARGET EVER GET HIT? ===")
tp=[x for x in B if x['reason']=='TakeProfit']
print(f"  TakeProfit exits: {len(tp)}/{len(B)} = {100*len(tp)/len(B):.1f}%")
