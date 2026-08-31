import csv, collections, datetime as dt, statistics as st
rows = list(csv.DictReader(open("us500_trades.csv")))
for r in rows:
    r["r"]=float(r["r"]); r["entry_time"]=dt.datetime.fromisoformat(r["entry_time"])
rows.sort(key=lambda r:r["entry_time"])

byday = collections.defaultdict(float)
cnt   = collections.Counter()
for r in rows:
    d = r["entry_time"].date()
    byday[d] += r["r"]; cnt[d] += 1
days = sorted(byday)
vals = [byday[d] for d in days]

print(f"trading days: {len(days)}   trades: {len(rows)}   trades/day avg {len(rows)/len(days):.2f}")
print(f"days with 1 trade: {sum(1 for d in days if cnt[d]==1)}, "
      f"2: {sum(1 for d in days if cnt[d]==2)}, "
      f"3+: {sum(1 for d in days if cnt[d]>=3)}  (max {max(cnt.values())})")

print("\n=== WORST DAYS (this is what the 5% daily limit bites on) ===")
worst = sorted(days, key=lambda d: byday[d])[:12]
for d in worst:
    print(f"  {d}  {byday[d]:+6.2f}R  ({cnt[d]} trade{'s' if cnt[d]>1 else ''})")
lo = [byday[d] for d in days]
lo.sort()
print(f"\n  worst day        {lo[0]:+.2f}R")
print(f"  1st percentile   {lo[int(0.01*len(lo))]:+.2f}R")
print(f"  5th percentile   {lo[int(0.05*len(lo))]:+.2f}R")
print(f"  median day       {st.median(vals):+.2f}R")
print(f"  losing days      {100*sum(1 for v in vals if v<0)/len(vals):.0f}%")

print("\n=== WHAT RISK SIZE KEEPS THE WORST DAY INSIDE FTMO's 5% DAILY LIMIT? ===")
for acct in (100000,):
    daily_budget = 0.05*acct
    for label, dloss in (("worst day seen", -lo[0]), ("1.5x worst day", -lo[0]*1.5)):
        risk = daily_budget/dloss
        print(f"  {label:<16} = {dloss:5.2f}R  ->  max risk ${risk:6.0f}/trade "
              f"({100*risk/acct:.2f}% of a ${acct:,} account)")
