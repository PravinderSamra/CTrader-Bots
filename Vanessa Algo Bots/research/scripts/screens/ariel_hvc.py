"""Real Simple Ariel (Chart Fanatics) 'delayed high volume close' on FTMO's US stock CFDs, Yahoo daily 2017-26. Screening.
HVC day: gap up >= g% on volume >= 3x its 50-day average (an earnings-type episodic pivot).
Entry: within 20 days, the first day after at least one day that stays at or below the HVC day's close, buy a stop at the
HVC close (or the open if it gaps above). Stop: that day's low (his 'low of day'). Exit: first close below the 10-day SMA
(or 20-day), checked from the next day; max 60 days. Variant: trim half at +3R? not modelled; full position.
Costs 0.1% + 8%/yr long swap per calendar night. Results in R. Run: python3 -I ariel_hvc.py <scratchpad>/ep"""
import glob, json, os, statistics as st, sys
from collections import defaultdict
from datetime import datetime, timezone

D = sys.argv[1]
data = {}
for f in sorted(glob.glob(os.path.join(D, "*.json"))):
    s = os.path.basename(f)[:-5]
    if s != s.upper(): continue
    r = json.load(open(f))["chart"]["result"][0]; q = r["indicators"]["quote"][0]
    data[s] = [(datetime.fromtimestamp(t, timezone.utc).date(), o, h, l, c, v)
               for t, o, h, l, c, v in zip(r["timestamp"], q["open"], q["high"], q["low"], q["close"], q["volume"])
               if None not in (o, h, l, c, v) and v > 0]


def sma(b, i, n):
    return sum(x[4] for x in b[i - n + 1:i + 1]) / n


def run(g, ma):
    out = []
    for s, b in data.items():
        i = 60
        while i < len(b) - 2:
            av = st.mean(x[5] for x in b[i - 50:i])
            if b[i][1] / b[i - 1][4] - 1 >= g and b[i][5] >= 3 * av:
                lvl = b[i][4]; below = False; done = False
                for j in range(i + 1, min(i + 21, len(b) - 1)):
                    d, o, h, l, c, v = b[j]
                    if below and h >= lvl:
                        e = max(o, lvl); stop = l
                        if e <= stop: break
                        R = e - stop
                        x = None
                        for k in range(j + 1, min(j + 61, len(b))):
                            if b[k][3] <= stop: x = min(stop, b[k][1]); break
                            if b[k][4] < sma(b, k, ma): x = b[k][4]; break
                        if x is None: k = min(j + 60, len(b) - 1); x = b[k][4]
                        nights = (b[k][0] - d).days
                        cost = e * (0.001 + 0.08 * nights / 365)
                        out.append((d, s, (x - e - cost) / R, (x - e - cost) / e))
                        done = True; break
                    if h <= lvl: below = True
                i = j + 1 if done else i + 1
            else:
                i += 1
    return sorted(out)


for g in (0.05, 0.08):
    for ma in (10, 20):
        t = run(g, ma)
        rs = [x[2] for x in t]; ps = [x[3] for x in t]
        yr = defaultdict(float)
        for d, s, r, p in t: yr[d.year] += r
        by = defaultdict(float)
        for d, s, r, p in t: by[s] += r
        top = sorted(by.items(), key=lambda x: -x[1])[:5]
        ex = [r for d, s, r, p in t if s not in dict(top)]
        print(f"gap>={g:.0%} exit<SMA{ma}: n={len(rs)} win={sum(r > 0 for r in rs)/len(rs):.0%} avg={st.mean(rs):+.2f}R "
              f"med={st.median(rs):+.2f}R avg%={st.mean(ps)*100:+.2f} | 2022+: {st.mean([r for d,s,r,p in t if d.year>=2022]):+.2f}R "
              f"| without top5 {[k for k,_ in top]}: {st.mean(ex):+.2f}R")
        print("   years:", " ".join(f"{y%100:02d}:{v:+.0f}" for y, v in sorted(yr.items())))
