import re,csv,collections,datetime as dt,statistics as st,glob,os
NAS_DIR="/home/user/CTrader-Bots/ORB Projects/ORB Volume Breakout Bot/optimisation/results/nas100"
ent=re.compile(r"TRADE ENTERED: (\w+) \S+ vol=([\d.]+) entry=[\d.]+ SL=[\d.]+ TP=[\d.]+ riskPips=([\d.]+) label=(\S+)")
clo=re.compile(r"POSITION CLOSED: (\S+) reason=(\S+) P/L=(-?[\d.]+) pips=(-?[\d.]+)")
ts=re.compile(r"^(\d{2})/(\d{2})/(\d{4})")

risk_by_label={}; nas=[]
files=[f"{NAS_DIR}/ex_{y}.txt" for y in (2022,2023,2024,2025)]+[f"{NAS_DIR}/ex_2026norm.txt"]
for path in files:
    for line in open(path,encoding="utf-8",errors="replace"):
        m=ent.search(line)
        if m:
            side,vol,rp,label=m.groups()
            risk_by_label[label]=float(rp)*float(vol); continue
        m=clo.search(line)
        if m:
            label,reason,pl,pips=m.groups()
            risk=risk_by_label.get(label)
            if not risk: continue
            d=ts.match(line).groups()
            nas.append((dt.date(int(d[2]),int(d[1]),int(d[0])), float(pl)/risk))
nas_day=collections.defaultdict(float)
for d,r in nas: nas_day[d]+=r
print(f"NAS100 London Range Breakout: {len(nas)} trades, {len(nas_day)} days, "
      f"{min(nas_day)} .. {max(nas_day)}, total {sum(nas_day.values()):+.1f}R")

exec(open("compare.py").read().split("A=parse")[0])
us=parse("log3r/3R log.txt")
us_day=collections.defaultdict(float)
for x in us: us_day[x["t"].date()]+=x["r"]
print(f"US500 15m ORB 3R:            {len(us)} trades, {len(us_day)} days, total {sum(us_day.values()):+.1f}R")

def pearson(x,y):
    mx,my=st.mean(x),st.mean(y)
    num=sum((p-mx)*(q-my) for p,q in zip(x,y))
    den=(sum((p-mx)**2 for p in x)*sum((q-my)**2 for q in y))**0.5
    return num/den if den else 0.0

common=sorted(set(us_day)&set(nas_day))
a=[us_day[d] for d in common]; b=[nas_day[d] for d in common]
r=pearson(a,b)
print(f"\n{'='*60}\nBOTH TRADED ON {len(common)} OF THE SAME DAYS")
print(f"daily-R correlation: {r:+.3f}")
n=len(common); se=(1-r*r)/ (n-2)**0.5
print(f"95% CI roughly {r-1.96*se:+.3f} .. {r+1.96*se:+.3f}")

ud=sum(1 for p in a if p<0); nd=sum(1 for q in b if q<0)
both=sum(1 for p,q in zip(a,b) if p<0 and q<0)
print(f"\nUS500 loses on {100*ud/n:.0f}% of shared days, NAS100 on {100*nd/n:.0f}%")
print(f"both lose together: {100*both/n:.0f}%   (independent would give {100*(ud/n)*(nd/n):.0f}%)")

# what matters: does combining them reduce drawdown per unit of return?
def maxdd(seq):
    peak=cum=0.0;w=0.0
    for x in seq: cum+=x;peak=max(peak,cum);w=min(w,cum-peak)
    return -w
allday=sorted(set(us_day)|set(nas_day))
solo_us=[us_day.get(d,0) for d in allday]; solo_nas=[nas_day.get(d,0) for d in allday]
combo=[us_day.get(d,0)+nas_day.get(d,0) for d in allday]
print(f"\n{'system':<22}{'total R':>10}{'maxDD R':>10}{'return/DD':>11}")
for nm,s in (("US500 alone",solo_us),("NAS100 alone",solo_nas),("BOTH combined",combo)):
    dd=maxdd(s)
    print(f"{nm:<22}{sum(s):>10.1f}{dd:>10.1f}{sum(s)/dd if dd else 0:>11.2f}")
best_solo=max(sum(solo_us)/maxdd(solo_us), sum(solo_nas)/maxdd(solo_nas))
print(f"\ncombining improves return-per-drawdown by "
      f"{100*((sum(combo)/maxdd(combo))/best_solo-1):+.0f}% over the better single bot")
