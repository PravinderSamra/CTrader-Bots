import re, datetime as dt, statistics as st, random, collections, sys
ENT=re.compile(r"TRADE ENTERED: (\w+) \S+ vol=([\d.]+) entry=([\d.]+) SL=([\d.]+) TP=([\d.]+) riskPips=([\d.]+)")
CLS=re.compile(r"POSITION CLOSED: \S+ reason=(\S+) P/L=(-?[\d.]+) pips=(-?[\d.]+)")
TS=re.compile(r"^(\d{2})/(\d{2})/(\d{4})")
def parse(p):
    E=[];C=[]
    for line in open(p,encoding="utf-8",errors="replace"):
        if "TRADE ENTERED:" in line:
            m=ENT.search(line); d=TS.match(line)
            if m and d:
                g=d.groups()
                E.append(dict(date=dt.date(int(g[2]),int(g[1]),int(g[0])),
                              vol=float(m.group(2)),rp=float(m.group(6))))
        elif "POSITION CLOSED:" in line:
            m=CLS.search(line)
            if m: C.append(dict(reason=m.group(1),pl=float(m.group(2)),pips=float(m.group(3))))
    return [dict(list(e.items())+list(c.items()), r=c["pips"]/e["rp"]) for e,c in zip(E,C)]
def maxdd(s):
    peak=cum=0.0;w=0.0
    for x in s: cum+=x;peak=max(peak,cum);w=min(w,cum-peak)
    return -w
def cost_per_trade(T):
    L=[t for t in T if t["reason"]=="StopLoss" and abs(t["pips"])>.01]
    W=[t for t in T if t["reason"]=="TakeProfit" and abs(t["pips"])>.01]
    if not L or not W: return None,None
    rl=st.median([t["pl"]/(t["pips"]*t["vol"]) for t in L])
    rw=st.median([t["pl"]/(t["pips"]*t["vol"]) for t in W])
    dl=st.median([abs(t["pips"])*t["vol"] for t in L]); dw=st.median([abs(t["pips"])*t["vol"] for t in W])
    c=(rl-rw)/(1/dl+1/dw); fx=rw+c/dw
    return c,fx
for label,path in sys.argv[1:]:
    pass
