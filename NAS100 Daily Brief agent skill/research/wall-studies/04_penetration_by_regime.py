"""Wall reaction split by GAMMA REGIME.

Model's premise: above the flip (long/positive gamma) dealers damp -> sweeps
fail -> Strategy 1 (fade) works. Below the flip (short/negative gamma) dealers
amplify -> price runs -> Strategy 2 (continuation).

Test: for every published gamma level touched in RTH, measure PENETRATION =
how far past the level price travelled after first touch. Continuous, so it
does not inherit the held/lost tolerance defect (M6/P-B).
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

events=[]
print(f"{'day':<12}{'regime':>10}{'strat':>7}{'adr':>7}  levels touched -> penetration pts (% ADR)")
for day in sorted(per_day):
    t_scan,d=per_day[day]
    p=d["prediction"]
    px=p.get("price_at_scan"); flip=p.get("gamma_flip"); adr=p.get("adr14") or 0
    if px is None or flip is None: continue
    regime = "positive" if px > flip else "negative"
    strat = (p.get("strategy") or "")[:10]
    rth=[b for b in byday.get(day,[]) if str(u(b).date())==day and OPEN_UTC<=u(b).time()<CLOSE_UTC]
    if len(rth)<20: continue
    lv=[x for x in (p.get("levels") or []) if x.get("kind") in GK]
    out=[]
    for x in lv:
        L=x["price"]
        # first touch and the side it was approached from
        prev=rth[0]["open"]; idx=None
        for i,b in enumerate(rth):
            if b["low"]-TOUCH <= L <= b["high"]+TOUCH:
                idx=i; break
            prev=b["close"]
        if idx is None: continue
        post=rth[idx:]
        if prev <= L:   # approached from below -> resistance; penetration = above
            pen = max(b["high"] for b in post) - L
        else:
            pen = L - min(b["low"] for b in post)
        pen = max(pen, 0.0)
        events.append(dict(day=day, regime=regime, strat=strat, level=L,
                           pen=pen, pen_adr=(pen/adr if adr else None),
                           name=x.get("name","")[:26]))
        out.append(f"{pen:.0f}")
    print(f"{day:<12}{regime:>10}{strat:>7}{adr:>7.0f}  {len(out)} touched: {' '.join(out)}")

def summ(tag, ev):
    if not ev: 
        print(f"{tag:<26} n=0"); return
    pen=[e["pen"] for e in ev]; pa=[e["pen_adr"] for e in ev if e["pen_adr"] is not None]
    print(f"{tag:<26} n={len(pen):>3}  median {st.median(pen):>6.1f}pts  mean {st.mean(pen):>6.1f}  "
          f"| median %ADR {100*st.median(pa):>5.1f}%  | <=25pts {100*sum(1 for v in pen if v<=25)/len(pen):>4.0f}%  "
          f">=100pts {100*sum(1 for v in pen if v>=100)/len(pen):>4.0f}%")

pos=[e for e in events if e["regime"]=="positive"]
neg=[e for e in events if e["regime"]=="negative"]
print(f"\n{'':<26} PENETRATION past the level after first touch")
summ("POSITIVE gamma (above flip)", pos)
summ("NEGATIVE gamma (below flip)", neg)
print()
print(f"days: positive {len({e['day'] for e in pos})}  negative {len({e['day'] for e in neg})}")
json.dump(events, open("/tmp/claude-0/-home-user-CTrader-Bots/d223cf12-f6c6-532d-a07d-b1099eb082ee/scratchpad/study5.json","w"), indent=1)

# --- normalise penetration by the day's OWN realised RTH range ---
print("\n=== penetration as a share of that day's realised RTH range ===")
rng = {}
for day in sorted(per_day):
    rth=[b for b in byday.get(day,[]) if str(u(b).date())==day and OPEN_UTC<=u(b).time()<CLOSE_UTC]
    if len(rth)>=20:
        rng[day]=max(b["high"] for b in rth)-min(b["low"] for b in rth)
for e in events:
    e["pen_rng"] = e["pen"]/rng[e["day"]] if rng.get(e["day"]) else None
def s2(tag, ev):
    v=[100*e["pen_rng"] for e in ev if e["pen_rng"] is not None]
    if not v: print(f"{tag:<46} n=0"); return
    print(f"{tag:<46} n={len(v):>2}  median {st.median(v):>5.1f}%  mean {st.mean(v):>5.1f}%  of day range")
rally={'2026-09-21','2026-09-22','2026-09-23'}
s2("POSITIVE gamma - all", [e for e in events if e["regime"]=="positive"])
s2("POSITIVE gamma - excluding the rally days", [e for e in events if e["regime"]=="positive" and e["day"] not in rally])
s2("NEGATIVE gamma - all", [e for e in events if e["regime"]=="negative"])
