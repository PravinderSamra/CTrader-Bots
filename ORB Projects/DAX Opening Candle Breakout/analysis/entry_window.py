"""When do qualifying breakouts actually occur after the 09:00-09:05 CET range?

Deliberately measures the TIMING DISTRIBUTION, not returns. Choosing a cutoff from
when breakouts happen is descriptive; choosing it from which hours were profitable
would be selecting on the thing we are trying to test, and would burn the reserve
years. Restricted to the in-sample window (<= 2024-12-31).
"""
import csv, collections, datetime as dt
from zoneinfo import ZoneInfo
UTC=ZoneInfo("UTC"); BER=ZoneInfo("Europe/Berlin")
IS_END=dt.date(2024,12,31)
OFFSET=10.0     # entry offset in points, matching the bot default

byday=collections.defaultdict(list)
for r in csv.DictReader(open("../../US30 London Range Breakout/data/GER40/ger40_m5.csv")):
    try: o,h,l,c=(float(r[k]) for k in ("open","high","low","close"))
    except (TypeError,ValueError): continue
    t=dt.datetime.strptime(r["datetime_utc"],"%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC).astimezone(BER)
    if t.date()<=IS_END: byday[t.date()].append((t,o,h,l,c))

mins=[]; nobreak=0; days=0
for d in sorted(byday):
    day=sorted(byday[d])
    op=[b for b in day if (b[0].hour,b[0].minute)>=(9,0)]
    if len(op)<20: continue
    rng=op[0]                      # the single 09:00-09:05 bar
    hi,lo=rng[2],rng[3]
    days+=1
    hit=None
    for b in op[1:]:               # confirmation bars after the range
        if b[4]>hi+OFFSET or b[4]<lo-OFFSET:
            hit=b[0]; break
    if hit is None: nobreak+=1
    else: mins.append(int((hit-rng[0]).total_seconds()//60))

mins.sort()
print(f"in-sample days: {days}   qualifying breakout occurred on {len(mins)} "
      f"({100*len(mins)/days:.1f}%)   no breakout: {nobreak}")
print(f"\nminutes from 09:00 to the first close {OFFSET:.0f}pts beyond the range:")
for p in (10,25,50,75,80,85,90,95,99):
    v=mins[min(int(p/100*len(mins)), len(mins)-1)]
    clock=(dt.datetime(2024,1,1,9,0)+dt.timedelta(minutes=v)).strftime("%H:%M")
    print(f"   {p:>2}th pct  {v:>4} min  -> {clock} CET")
print("\ncumulative share of all breakouts captured by each cutoff:")
for cut in ("10:00","10:30","11:00","11:30","12:00","13:00","14:00","15:30","17:30"):
    hh,mm=map(int,cut.split(":"))
    lim=(hh-9)*60+mm
    n=sum(1 for m in mins if m<=lim)
    print(f"   last entry {cut}  captures {n:>4}/{len(mins)}  = {100*n/len(mins):5.1f}% "
          f"({100*n/days:5.1f}% of all days)")
