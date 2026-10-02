"""The Nth sweep of the SAME level on the SAME day.

Every other study treats each sweep as an independent event. In practice you
watch a level get swept, reclaimed, and swept again, and you have to decide
whether attempt two is a better or a worse trade than attempt one. The answer
is observable in real time, so a difference here would be tradeable.

Reads /tmp/sw_conf.json, written by 05_sweep_reversal.py.

Result (2026-10-02, 19 trading days): flat through three attempts
(53% / 53% / 50% reaching 1R), mild decay after. No signal. See H24.
"""
import json, collections, statistics as st

rows = json.load(open("/tmp/sw_conf.json"))
rows.sort(key=lambda r: (r["day"], r["level"], r["t"]))

seq = collections.defaultdict(int)
buck = collections.defaultdict(list)
for r in rows:
    k = (r["day"], r["level"], r["side"])
    seq[k] += 1
    r["_n"] = seq[k]
    buck[min(seq[k], 4)].append(r)      # 4 is "4th or later"

print(f"{'attempt':<10}{'rows':>6}{'pairs':>7}{'days':>6}"
      f"{'>=1R':>7}{'>=2R':>7}{'stop':>7}{'medR':>7}{'medmv':>8}")
for n in sorted(buck):
    v = buck[n]
    m = len(v)
    print(f"{('#%d%s' % (n, '+' if n == 4 else '')):<10}{m:>6}"
          f"{len({(r['day'], r['level']) for r in v}):>7}"
          f"{len({r['day'] for r in v}):>6}"
          f"{sum(1 for r in v if r['R'] >= 1) / m:>6.0%}"
          f"{sum(1 for r in v if r['R'] >= 2) / m:>7.0%}"
          f"{sum(1 for r in v if r['stopped']) / m:>7.0%}"
          f"{st.median(r['R'] for r in v):>7.2f}"
          f"{st.median(r['R'] * r['risk'] for r in v):>7.0f}p")

# Same-day control: a bucket can only be compared against the days it appears on.
days = {r["day"] for r in buck[1]} & {r["day"] for r in rows if r["_n"] > 1}
first = [r for r in rows if r["_n"] == 1 and r["day"] in days]
later = [r for r in rows if r["_n"] > 1 and r["day"] in days]
print(f"\nCONTROL on the {len(days)} days containing both:")
for tag, v in (("first sweep", first), ("later sweeps", later)):
    print(f"  {tag:<14}{len(v):>5} rows"
          f"  >=1R {sum(1 for r in v if r['R'] >= 1) / len(v):>4.0%}"
          f"  >=2R {sum(1 for r in v if r['R'] >= 2) / len(v):>4.0%}"
          f"  medR {st.median(r['R'] for r in v):>5.2f}"
          f"  med risk {st.median(r['risk'] for r in v):>5.0f}p")
