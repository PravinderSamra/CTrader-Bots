"""Trade the CONFIRMED pierce: wait for a bar to CLOSE beyond the level, then go with it.

Compares three entries on the same first-touch events:
  A  fade at the level          (what the brief's prose implies)
  B  break at the level         (sign-flip of A - NOT a real entry, shown for reference)
  C  break on CONFIRMATION      (enter at the close of the first bar closing beyond)
Exit: RTH close. MAE reported so a stop can be judged.
"""
import json, glob, sys, statistics as st
from datetime import datetime, timezone, time as dtime
sys.path.insert(0, "/home/user/CTrader-Bots/.claude/skills/nas100-daily-brief/scripts")
import ctrader_http as ct, levels_fuel as LF

OPEN_UTC, CLOSE_UTC = dtime(13,30), dtime(20,0)
GK = {"gamma","gamma-shelf"}; TOUCH = 8.0

def u(b):
    t=b["time"]
    if not isinstance(t,datetime): t=datetime.fromtimestamp(t/1000,timezone.utc)
    return t if t.tzinfo else t.replace(tzinfo=timezone.utc)

bars_all = ct.fetch_ohlcv_paged("NAS100","M_5",days=45,max_calls=300)
byday={}
for b in bars_all: byday.setdefault(str(LF.trading_day(b["time"])),[]).append(b)

per_day={}
for f in sorted(glob.glob("/home/user/CTrader-Bots/NAS100 Daily Brief agent skill/journal/2026-*/[0-9]*.json")):
    d=json.load(open(f))
    if not d.get("is_trading_day") or not d.get("scan_utc"): continue
    t=datetime.fromisoformat(d["scan_utc"].replace("Z","+00:00")).astimezone(timezone.utc)
    if t.time()>=OPEN_UTC: continue
    day=d["trading_day"]
    if day not in per_day or t>per_day[day][0]: per_day[day]=(t,d)

A=[];B=[];C=[]
print(f"{'day':<12}{'tag t':>7}{'level':>10}{'appr':>6} | {'A fade':>8}{'B brk@lvl':>10} | {'conf t':>7}{'entry':>9}{'C pnl':>8}{'C MAE':>7}")
for day in sorted(per_day):
    t_scan,d=per_day[day]
    rth=[b for b in byday.get(day,[]) if str(u(b).date())==day and OPEN_UTC<=u(b).time()<CLOSE_UTC]
    if len(rth)<20: continue
    lv=sorted({x["price"] for x in (d["prediction"].get("levels") or []) if x.get("kind") in GK})
    if not lv: continue
    prev=rth[0]["open"]; hit=None
    for i,b in enumerate(rth):
        h=[p for p in lv if b["low"]-TOUCH<=p<=b["high"]+TOUCH]
        if h:
            p=min(h,key=lambda q:abs(q-prev))
            hit=(i,p,"from_below" if p>=prev else "from_above"); break
        prev=b["close"]
    if not hit: continue
    i,p,appr=hit
    post=rth[i:]; cl=post[-1]["close"]
    hi=max(b["high"] for b in post); lo=min(b["low"] for b in post)
    # A: fade  (from_below -> short at level ; from_above -> long at level)
    a = (p-cl) if appr=="from_below" else (cl-p)
    A.append(a); B.append(-a)
    # C: confirmed break — first bar CLOSING beyond the level in the break direction
    conf=None
    for j,b in enumerate(post):
        if appr=="from_below" and b["close"] > p + TOUCH: conf=(j,b); break
        if appr=="from_above" and b["close"] < p - TOUCH: conf=(j,b); break
    if conf:
        j,b=conf; e=b["close"]; after=post[j:]
        if appr=="from_below":
            c=cl-e; mae=e-min(x["low"] for x in after)
        else:
            c=e-cl; mae=max(x["high"] for x in after)-e
        C.append((c,mae))
        print(f"{day:<12}{u(rth[i]).strftime('%H:%M'):>7}{p:>10.1f}{appr[5:]:>6} | {a:>+8.1f}{-a:>+10.1f} | "
              f"{u(b).strftime('%H:%M'):>7}{e:>9.1f}{c:>+8.1f}{mae:>7.1f}")
    else:
        print(f"{day:<12}{u(rth[i]).strftime('%H:%M'):>7}{p:>10.1f}{appr[5:]:>6} | {a:>+8.1f}{-a:>+10.1f} |   never closed beyond")

def s(n,p):
    w=sum(1 for v in p if v>0)
    print(f"{n:<40} n={len(p):>2}  wins {w}/{len(p)}  mean {st.mean(p):+7.1f}  median {st.median(p):+7.1f}  total {sum(p):+8.1f}")
print()
s("A  fade at the level", A)
s("B  break at level (sign-flip, not real)", B)
s("C  break on CONFIRMED close beyond", [c for c,_ in C])
if C: print(f"{'   C mean adverse excursion after entry':<40} {st.mean(m for _,m in C):.1f} pts   worst {max(m for _,m in C):.1f}")
