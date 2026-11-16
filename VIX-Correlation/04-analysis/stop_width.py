"""
Minimum stop width, tested at M5 with the TRUE intraday simulation.

Stage 2a/6 finding: trades killed by sequencing have a median stop of 0.223%,
survivors 0.361%. So a stop that is too close to the reclaim level gets
retested by ordinary noise. Three candidate fixes:

  A  WIDEN  stop = min(breach low, entry*(1-floor))   - keeps every trade
  B  SKIP   drop the trade if (entry-breach low)/entry < floor
  C  BUFFER stop = breach low - buffer*entry          - always a little lower

Guard against fitting: the 3 years are split in half. Anything chosen on the
first half must hold up on the second.
"""
import csv, statistics as st, datetime as dt

SRC="US30 London Range Breakout/data/NAS100/nas100_m5.csv"
CUSHION,TARGET,MAXDAYS,SPREAD=0.0014,3.0,10,1.0
bars=[]
for r in csv.reader(open(SRC)):
    if r[0]=="timestamp_ms": continue
    bars.append((int(r[0]),float(r[2]),float(r[3]),float(r[4]),float(r[5])))
bars.sort()
sess,cur=[],[bars[0]]
for p,b in zip(bars,bars[1:]):
    if b[0]-p[0]>=3600_000: sess.append(cur); cur=[]
    cur.append(b)
sess.append(cur); sess=[s for s in sess if len(s)>=50]
D=[(s[0][1],max(b[2] for b in s),min(b[3] for b in s),s[-1][4]) for s in sess]
T=[s[0][0] for s in sess]
MID=len(D)//2

def fwd(i,entry,stop,sb):
    risk=entry-stop
    if risk<=0: return None
    tgt=entry+TARGET*risk
    for b in sess[i][sb:]:
        if b[3]<=stop: return -1.0
        if b[2]>=tgt: return TARGET
    for n in range(1,MAXDAYS+1):
        if i+n>=len(D): return None
        _,hi,lo,_=D[i+n]
        if lo<=stop: return -1.0
        if hi>=tgt: return TARGET
    return (D[min(i+MAXDAYS,len(D)-1)][3]-entry)/risk

# locate every event's entry and natural (breach) stop once
EV=[]
for i in range(1,len(D)):
    plo=D[i-1][2]; _,_,slo,scl=D[i]
    if not(slo<plo and scl>plo): continue
    entry=plo*(1+CUSHION)
    bi=next((k for k,b in enumerate(sess[i]) if b[3]<plo),None)
    if bi is None: continue
    fi=next((k for k in range(bi+1,len(sess[i])) if sess[i][k][2]>=entry),None)
    if fi is None: continue
    EV.append(dict(i=i,entry=entry,nat=min(b[3] for b in sess[i][:fi+1]),fi=fi,half=0 if i<MID else 1))

def run(mode,param,half=None):
    rs=[]
    for e in EV:
        if half is not None and e["half"]!=half: continue
        entry,nat=e["entry"],e["nat"]
        if mode=="A":   stop=min(nat, entry*(1-param))
        elif mode=="B":
            if (entry-nat)/entry < param: continue
            stop=nat
        elif mode=="C": stop=nat-param*entry
        else:           stop=nat
        r=fwd(e["i"],entry,stop,e["fi"]+1)
        if r is None: continue
        rs.append(r - 2*SPREAD/(entry-stop))      # spread drag in R
    if not rs: return None
    return len(rs),100*sum(1 for x in rs if x>0)/len(rs),sum(rs)/len(rs),sum(rs)

base=run(None,0)
print("BASELINE (no floor), full 3 years, spread included")
print("  n=%d  win %.1f%%  avgR %+.3f  total %+.1fR\n"%base)
print("%-6s %-8s | %-28s | %-28s"%("mode","param","FIRST HALF","SECOND HALF"))
print("%-6s %-8s | %5s %7s %8s %7s | %5s %7s %8s %7s"
      %("","", "n","win%","avgR","totR","n","win%","avgR","totR"))
rows=[]
for mode,params in (("A",(0.0020,0.0030,0.0040,0.0050,0.0060)),
                    ("B",(0.0020,0.0025,0.0030,0.0035)),
                    ("C",(0.0005,0.0010,0.0015,0.0020))):
    for p in params:
        a=run(mode,p,0); b=run(mode,p,1)
        if not a or not b: continue
        rows.append((mode,p,a,b))
        print("%-6s %-8s | %5d %6.1f%% %+8.3f %+7.1f | %5d %6.1f%% %+8.3f %+7.1f"
              %(mode,"%.2f%%"%(100*p),a[0],a[1],a[2],a[3],b[0],b[1],b[2],b[3]))
h0=run(None,0,0); h1=run(None,0,1)
print("%-6s %-8s | %5d %6.1f%% %+8.3f %+7.1f | %5d %6.1f%% %+8.3f %+7.1f"
      %("none","-",h0[0],h0[1],h0[2],h0[3],h1[0],h1[1],h1[2],h1[3]))
print("\nbest on FIRST half by avgR:")
best=max(rows,key=lambda r:r[2][2])
print("  %s %.2f%%  ->  first half %+.3fR, SECOND HALF %+.3fR  (baseline 2nd half %+.3fR)"
      %(best[0],100*best[1],best[2][2],best[3][2],h1[2]))
