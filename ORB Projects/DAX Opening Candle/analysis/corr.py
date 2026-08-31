import csv,collections,datetime as dt,statistics as st,io,contextlib
with contextlib.redirect_stdout(io.StringIO()):
    exec(open("dax_cost.py").read().split("\nOS_A=dt.date")[0])

# US500 bot daily R (3R config)
import re
ent=re.compile(r"TRADE ENTERED:.* riskPips=(?P<rp>[\d.]+) label"); 
exec(open("compare.py").read().split("A=parse")[0])
us=parse("log3r/3R log.txt")
us_day=collections.defaultdict(float)
for x in us: us_day[x["t"].date()] += x["r"]

# DAX Frankfurt-open daily R (use a mid, cost-aware config)
dax=run_cost(2.0,2.0,1.5)
dax_day={t["date"]:t["r"] for t in dax}

common=sorted(set(us_day)&set(dax_day))
print(f"overlapping trading days: {len(common)}  ({common[0]} .. {common[-1]})")
a=[us_day[d] for d in common]; b=[dax_day[d] for d in common]
def pearson(x,y):
    mx,my=st.mean(x),st.mean(y)
    num=sum((p-mx)*(q-my) for p,q in zip(x,y))
    den=(sum((p-mx)**2 for p in x)*sum((q-my)**2 for q in y))**0.5
    return num/den if den else 0
print(f"\ndaily-return correlation US500(NY open) vs GER40(Frankfurt open): {pearson(a,b):+.3f}")

# also: how often do they lose together?
both_down=sum(1 for p,q in zip(a,b) if p<0 and q<0)
us_down=sum(1 for p in a if p<0); dx_down=sum(1 for q in b if q<0)
print(f"  US500 down {100*us_down/len(a):.0f}% of days, DAX down {100*dx_down/len(b):.0f}%")
print(f"  both down together {100*both_down/len(a):.0f}% of days "
      f"(if independent you'd expect {100*(us_down/len(a))*(dx_down/len(b)):.0f}%)")

# For contrast: correlation of the raw session moves (structural, strategy-free)
us_sess={}; 
print("\nFor contrast — correlation of the raw SESSION MOVES (no strategy involved):")
dax_move={}
for d,day in byday.items():
    o=next((x for x in day if x[1].hour==9 and x[1].minute==0),None)
    c=next((x for x in day if x[1].hour==11 and x[1].minute==0),None)
    if o and c: dax_move[d]=(c[5]-o[2])/o[2]
com2=sorted(set(dax_move)&set(us_day))
if len(com2)>50:
    x=[dax_move[d] for d in com2]; y=[us_day[d] for d in com2]
    print(f"  DAX 09:00-11:00 CET move vs US500 bot daily R: {pearson(x,y):+.3f}  (n={len(com2)})")
