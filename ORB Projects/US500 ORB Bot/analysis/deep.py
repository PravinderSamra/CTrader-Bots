import csv, collections, datetime as dt, random, statistics as st
rows = list(csv.DictReader(open("us500_trades.csv")))
for r in rows:
    for k in ("net","gross","comm","r","risk_usd","pips"): r[k] = float(r[k])
    r["entry_time"] = dt.datetime.fromisoformat(r["entry_time"])
    r["year"] = r["entry_time"].year
rows.sort(key=lambda r: r["entry_time"])
R = [r["r"] for r in rows]
n = len(R)

def dd(seq):
    peak = cum = 0.0; worst = 0.0; 
    for x in seq:
        cum += x
        peak = max(peak, cum)
        worst = min(worst, cum - peak)
    return worst

print("="*68); print("OVERALL"); print("="*68)
exp = sum(R)/n
sd = st.stdev(R)
print(f"trades {n}   total {sum(R):+.1f}R (${sum(r['net'] for r in rows):+,.0f} net at $100 risk)")
print(f"expectancy {exp:+.4f}R/trade   sd {sd:.2f}R   t-stat {exp/(sd/n**0.5):.2f}")
wins=[x for x in R if x>0]; losses=[x for x in R if x<=0]
print(f"win rate {100*len(wins)/n:.1f}%   avg win {sum(wins)/len(wins):+.2f}R   avg loss {sum(losses)/len(losses):+.2f}R")
print(f"profit factor {sum(wins)/abs(sum(losses)):.3f}")
print(f"max drawdown (trade sequence) {dd(R):.1f}R  = ${dd(R)*100:,.0f} at $100 risk")

print("\n"+"="*68); print("IN-SAMPLE vs OUT-OF-SAMPLE  (tuned on 2025-01-01 .. 2026-03-31)"); print("="*68)
IS = [r for r in rows if dt.datetime(2025,1,1) <= r["entry_time"] <= dt.datetime(2026,3,31,23,59)]
OOS= [r for r in rows if r not in IS]
for name, g in (("IN-SAMPLE (tuned)", IS), ("OUT-OF-SAMPLE (clean)", OOS)):
    rr=[x["r"] for x in g]; w=[x for x in rr if x>0]
    e=sum(rr)/len(rr); s=st.stdev(rr)
    print(f"{name:<24} n={len(rr):>4}  total {sum(rr):>+7.1f}R  exp {e:+.4f}R  "
          f"win {100*len(w)/len(rr):4.1f}%  t={e/(s/len(rr)**0.5):5.2f}  maxDD {dd(rr):6.1f}R")

print("\n"+"="*68); print("OUT-OF-SAMPLE BROKEN DOWN"); print("="*68)
segs = [("2022", dt.datetime(2022,1,1), dt.datetime(2022,12,31,23,59)),
        ("2023", dt.datetime(2023,1,1), dt.datetime(2023,12,31,23,59)),
        ("2024", dt.datetime(2024,1,1), dt.datetime(2024,12,31,23,59)),
        ("2026 Apr-Aug", dt.datetime(2026,4,1), dt.datetime(2026,12,31,23,59))]
for nm,a,b in segs:
    g=[x["r"] for x in rows if a<=x["entry_time"]<=b]
    if not g: continue
    print(f"  {nm:<14} n={len(g):>4}  total {sum(g):>+7.1f}R  exp {sum(g)/len(g):+.4f}R  maxDD {dd(g):6.1f}R")

print("\n"+"="*68); print("OUTLIER DEPENDENCE (does a handful of trades carry it?)"); print("="*68)
srt = sorted(R, reverse=True)
for k in (0,1,3,5,10,20):
    rem = srt[k:]
    print(f"  strip top {k:>2} winners: total {sum(rem):+7.1f}R   exp {sum(rem)/len(rem):+.4f}R")
print(f"  best single trade {max(R):+.2f}R   top 10 trades = {sum(srt[:10]):.1f}R "
      f"({100*sum(srt[:10])/sum(R):.0f}% of all profit)")

print("\n"+"="*68); print("SIGNIFICANCE"); print("="*68)
random.seed(7)
# bootstrap CI on expectancy
boots = sorted(sum(random.choices(R, k=n))/n for _ in range(20000))
print(f"  bootstrap 90% CI on expectancy: {boots[1000]:+.4f}R .. {boots[19000]:+.4f}R")
print(f"  bootstrap 95% CI on expectancy: {boots[500]:+.4f}R .. {boots[19500]:+.4f}R")
# sign-flip permutation: is the mean distinguishable from zero?
worse = sum(1 for _ in range(20000)
            if sum(x*random.choice((1,-1)) for x in R)/n >= exp)
print(f"  permutation p-value (mean > 0): {worse/20000:.4f}")

print("\n"+"="*68); print("CONSISTENCY BY MONTH"); print("="*68)
bym = collections.defaultdict(float)
for r in rows: bym[(r['entry_time'].year, r['entry_time'].month)] += r['r']
vals=list(bym.values())
print(f"  months traded {len(vals)}   profitable {sum(1 for v in vals if v>0)} "
      f"({100*sum(1 for v in vals if v>0)/len(vals):.0f}%)")
print(f"  best month {max(vals):+.1f}R   worst month {min(vals):+.1f}R   median {st.median(vals):+.2f}R")
worst = sorted(bym.items(), key=lambda kv: kv[1])[:5]
print("  worst 5 months: " + ", ".join(f"{y}-{m:02d} {v:+.1f}R" for (y,m),v in worst))
