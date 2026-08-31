"""Mirror of ComputeAtrStopPoints' completed-bar rule, run against the real D1 bars.

Confirms the rule never includes the bar covering the current session, for every
trading day in the data, across both DST conventions and over weekends.
"""
import csv, datetime as dt
from zoneinfo import ZoneInfo
UTC=ZoneInfo("UTC"); BER=ZoneInfo("Europe/Berlin")
bars=[]
for r in csv.DictReader(open("../../US30 London Range Breakout/data/GER40/ger40_d1.csv")):
    t=dt.datetime.strptime(r["datetime_utc"],"%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC)
    bars.append((t,float(r["high"]),float(r["low"]),float(r["close"])))
bars.sort()

def session_open_utc(d):                      # 09:00 Europe/Berlin -> UTC
    return dt.datetime.combine(d, dt.time(9,0), tzinfo=BER).astimezone(UTC)

ATR_DAYS=14
bad=0; atrs=[]; checked=0
for day in range(40, len(bars)):
    sess_date=(bars[day][0].astimezone(BER)+dt.timedelta(days=1)).date()
    open_utc=session_open_utc(sess_date)
    if open_utc.weekday()>=5: continue
    # the C# rule: last i where OpenTimes[i] + 1 day <= session open
    last=-1
    for i in range(len(bars)-1,-1,-1):
        if bars[i][0]+dt.timedelta(days=1) <= open_utc: last=i; break
    if last<1: continue
    checked+=1
    # the bar covering THIS session must never be selected
    covering=[i for i,b in enumerate(bars) if b[0] < open_utc <= b[0]+dt.timedelta(days=1)]
    if covering and last>=covering[0]:
        bad+=1
        if bad<4: print(f"  LEAK {sess_date}: selected idx {last} ({bars[last][0]}) covers the session")
    first=max(1,last-ATR_DAYS+1)
    trs=[]
    for i in range(first,last+1):
        h,l,pc=bars[i][1],bars[i][2],bars[i-1][3]
        trs.append(max(h-l,abs(h-pc),abs(l-pc)))
    if trs: atrs.append(sum(trs)/len(trs))

print(f"sessions checked: {checked}")
print(f"sessions where the rule leaked the current bar: {bad}  ->  {'PASS' if bad==0 else 'FAIL'}")
atrs.sort()
print(f"\nATR14 from the completed-bar window: median {atrs[len(atrs)//2]:.0f} pts "
      f"(10th {atrs[len(atrs)//10]:.0f}, 90th {atrs[9*len(atrs)//10]:.0f})")
print(f"10% stop -> median {0.10*atrs[len(atrs)//2]:.1f} pts, "
      f"range {0.10*atrs[0]:.1f} to {0.10*atrs[-1]:.1f} pts")
print(f"clamp [10,80] would bind on "
      f"{100*sum(1 for a in atrs if not (10<=0.10*a<=80))/len(atrs):.1f}% of sessions")
