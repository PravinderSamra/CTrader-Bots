import csv, collections, datetime as dt, statistics as st
from zoneinfo import ZoneInfo
UTC=ZoneInfo("UTC")
BASE="/home/user/CTrader-Bots/US30 London Range Breakout/data"
# instrument -> (file, local tz, cash-open hour:min local, typical spread pts)
INST={
 "GER40":  (f"{BASE}/GER40/ger40_m5.csv","Europe/Berlin",(9,0),  1.5),
 "UK100":  (f"{BASE}/UK100/uk100_m5.csv","Europe/London",(8,0),  1.5),
 "NAS100": (f"{BASE}/NAS100/nas100_m5.csv","America/New_York",(9,30),1.5),
 "US30":   (f"{BASE}/US30/us30_m5.csv","America/New_York",(9,30),2.0),
}
print(f"{'':<8}{'price':>9}{'OR15 pts':>10}{'1st hr':>9}{'OR15 %':>9}"
      f"{'cost/OR15':>11}{'cost/hr':>9}")
for name,(path,tzs,(oh,om),spread) in INST.items():
    tz=ZoneInfo(tzs); byday=collections.defaultdict(list)
    for r in csv.DictReader(open(path)):
        try: c=float(r["close"])
        except (TypeError,ValueError): continue
        t=dt.datetime.strptime(r["datetime_utc"],"%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC).astimezone(tz)
        byday[t.date()].append((t,float(r["open"]),float(r["high"]),float(r["low"]),c))
    ors=[]; hrs=[]; px=[]
    for d,day in byday.items():
        day.sort()
        op=[b for b in day if (b[0].hour,b[0].minute)>=(oh,om)]
        if len(op)<13: continue
        first3=op[:3]                       # 15 minutes
        hi=max(b[2] for b in first3); lo=min(b[3] for b in first3)
        ors.append(hi-lo)
        h=op[:12]                           # first hour
        hrs.append(max(b[2] for b in h)-min(b[3] for b in h))
        px.append(op[0][1])
    if not ors: print(f"{name:<8} no data"); continue
    ors.sort(); hrs.sort(); mo=ors[len(ors)//2]; mh=hrs[len(hrs)//2]; mp=st.median(px)
    print(f"{name:<8}{mp:>9,.0f}{mo:>10.1f}{mh:>9.1f}{100*mo/mp:>8.2f}%"
          f"{100*spread/mo:>10.1f}%{100*spread/mh:>8.1f}%")
print("\nOR15 = median high-low of the first 15 min after the cash open.")
print("cost/OR15 = a round-trip spread as a share of that range — the higher,")
print("the more of your edge friction eats before you start.")
