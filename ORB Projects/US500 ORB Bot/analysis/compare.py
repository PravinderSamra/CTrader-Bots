import re, csv, collections, datetime as dt, statistics as st, random
ent_re=re.compile(r"TRADE ENTERED: (?P<side>\w+) \S+ vol=(?P<vol>[\d.]+) entry=(?P<entry>[\d.]+) SL=(?P<sl>[\d.]+) TP=(?P<tp>[\d.]+) riskPips=(?P<riskpips>[\d.]+) label=(?P<label>\S+)")
cls_re=re.compile(r"CLOSE_DIAG label=(?P<label>\S+) reason=(?P<reason>\S+) net=(?P<net>-?[\d.]+) gross=(?P<gross>-?[\d.]+) commission=(?P<comm>-?[\d.]+)")
ts_re=re.compile(r"^(\d{2})/(\d{2})/(\d{4}) (\d{2}):(\d{2}):(\d{2})")
def parse(path):
    E=[];C=[]
    for line in open(path,encoding="utf-8",errors="replace"):
        if "TRADE ENTERED:" in line:
            m=ent_re.search(line)
            if m:
                g=m.groupdict(); t=ts_re.match(line).groups()
                g["t"]=dt.datetime(int(t[2]),int(t[1]),int(t[0]),int(t[3]),int(t[4]),int(t[5])); E.append(g)
        elif "CLOSE_DIAG" in line:
            m=cls_re.search(line)
            if m: C.append(m.groupdict())
    out=[]
    for e,c in zip(E,C):
        risk=float(e["riskpips"])*float(e["vol"])
        out.append(dict(t=e["t"], r=float(c["net"])/risk, net=float(c["net"]),
                        comm=float(c["comm"]), reason=c["reason"]))
    return out
A=parse("us500log/US500 2022-26log.txt"); B=parse("log3r/3R log.txt")

def maxdd(seq):
    peak=cum=0.0;w=0.0
    for x in seq: cum+=x;peak=max(peak,cum);w=min(w,cum-peak)
    return -w
def stats(rows,name):
    R=[x["r"] for x in rows]; n=len(R)
    wins=[x for x in R if x>0]; los=[x for x in R if x<=0]
    srt=sorted(R,reverse=True)
    e=sum(R)/n; sd=st.stdev(R)
    print(f"{name:<10}{n:>6}{sum(x['net'] for x in rows):>10,.0f}{sum(R):>9.1f}"
          f"{e:>9.4f}{100*len(wins)/n:>7.1f}%{sum(wins)/len(wins):>8.2f}{sum(los)/len(los):>8.2f}"
          f"{sum(wins)/abs(sum(los)):>7.3f}{maxdd(R):>8.1f}{e/(sd/n**0.5):>7.2f}")
    return R
print(f"{'config':<10}{'n':>6}{'net $':>10}{'total R':>9}{'exp R':>9}{'win%':>8}{'avgW':>8}{'avgL':>8}{'PF':>7}{'maxDD':>8}{'t':>7}")
RA=stats(A,"20R"); RB=stats(B,"3R")

print("\n=== OUTLIER DEPENDENCE — the reason for the switch ===")
print(f"{'strip top':>10}{'20R total':>12}{'3R total':>11}")
for k in (0,3,5,10,20,30):
    a=sorted(RA,reverse=True)[k:]; b=sorted(RB,reverse=True)[k:]
    print(f"{k:>10}{sum(a):>+11.1f}R{sum(b):>+10.1f}R")
for nm,R in (("20R",RA),("3R",RB)):
    s=sorted(R,reverse=True)
    print(f"  {nm}: top 10 trades = {100*sum(s[:10])/sum(R):.0f}% of all profit; best trade {max(R):+.2f}R")

print("\n=== BY YEAR (net $) ===")
print(f"{'year':<6}{'20R':>9}{'3R':>9}{'diff':>8}")
for y in range(2022,2027):
    a=sum(x['net'] for x in A if x['t'].year==y); b=sum(x['net'] for x in B if x['t'].year==y)
    print(f"{y:<6}{a:>9,.0f}{b:>9,.0f}{b-a:>+8,.0f}")
print(f"{'ALL':<6}{sum(x['net'] for x in A):>9,.0f}{sum(x['net'] for x in B):>9,.0f}"
      f"{sum(x['net'] for x in B)-sum(x['net'] for x in A):>+8,.0f}")

print("\n=== MONTHLY CONSISTENCY ===")
for nm,rows in (("20R",A),("3R",B)):
    m=collections.defaultdict(float)
    for x in rows: m[(x['t'].year,x['t'].month)]+=x['r']
    v=list(m.values())
    print(f"  {nm:<4} profitable months {100*sum(1 for q in v if q>0)/len(v):4.0f}%   "
          f"worst {min(v):+.1f}R   best {max(v):+.1f}R   median {st.median(v):+.2f}R   sd {st.stdev(v):.2f}R")

print("\n=== EXIT REASONS (3R) ===")
for reason,n in collections.Counter(x['reason'] for x in B).most_common():
    sub=[x for x in B if x['reason']==reason]
    print(f"  {reason:<14}{n:>5} ({100*n/len(B):4.1f}%)  avg {sum(x['r'] for x in sub)/n:+.2f}R  total {sum(x['net'] for x in sub):>+8,.0f}")
