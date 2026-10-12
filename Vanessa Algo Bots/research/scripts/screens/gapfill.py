"""Gap fill on NAS100 m5 (Andrea Chimmy claim: ~70% of gaps fill, ~85% fill half). Gap = 9:30 open vs prior 16:00
(15:55 bar) close. Fade the gap at the open: target the prior close (full) or half; stop = open +/- gap size (1R = gap);
exit 15:55 if neither. Same-bar stop/target counted as stop. Cost 1.2 pts."""
import csv, json, statistics as st, sys
from collections import defaultdict
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
NY = ZoneInfo("America/New_York"); days = defaultdict(list)
for r in csv.DictReader(open("/home/user/CTrader-Bots/US30 London Range Breakout/data/NAS100/nas100_m5.csv")):
    t = datetime.fromtimestamp(int(r["timestamp_ms"]) / 1000, timezone.utc).astimezone(NY); m = t.hour*60+t.minute
    if 570 <= m < 960: days[t.date()].append((m, float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"])))
dl = [d for d in sorted(days) if len(days[d]) >= 75 and days[d][0][0] == 570]
bot = dict(zip(*json.load(open(sys.argv[1])).values()))
def run(minpct, maxpct, frac, cost=1.2):
    out = []; fills = 0; n = 0
    for k in range(1, len(dl)):
        pc = days[dl[k-1]][-1][4]; b = days[dl[k]]; o = b[0][1]; g = o - pc
        if not (minpct <= abs(g) / pc * 100 < maxpct): continue
        n += 1; side = -1 if g > 0 else 1; tgt = o - g * frac; stop = o + g; risk = abs(g)
        if any((x[3] <= pc) if g > 0 else (x[2] >= pc) for x in b): fills += 1
        r = None
        for m, bo, h, l, c in b:
            if (h >= stop) if side == -1 else (l <= stop): r = -risk; break
            if (l <= tgt) if side == -1 else (h >= tgt): r = abs(o - tgt); break
        if r is None: r = side * (b[-1][4] - o)
        out.append((dl[k], (r - cost) / risk))
    rs = [x[1] for x in out]
    if not rs: return
    yr = defaultdict(float)
    for x in out: yr[x[0].year] += x[1]
    dv = {x[0].strftime("%Y%m%d"): x[1] for x in out}; com = [k for k in dv if k in bot]
    corr = st.correlation([bot[k] for k in com], [dv[k] for k in com]) if len(com) > 5 else float("nan")
    print(f"gap {minpct}-{maxpct}% target {frac:.0%}: n={n} filled-any-time {fills/n:4.0%} | trade win {sum(r>0 for r in rs)/len(rs):4.0%} "
          f"avg {st.mean(rs):+.3f}R tot {sum(rs):+.1f}R corr {corr:+.2f} | " + " ".join(f"{y}:{v:+.0f}" for y, v in sorted(yr.items())))
for lo, hi in ((0.1, 0.5), (0.5, 1.0), (1.0, 5.0), (0.1, 5.0)):
    for frac in (1.0, 0.5): run(lo, hi, frac)
