"""Kyle Williams 'first red day' short (Chart Fanatics), scaled from small caps to NAS100 and gold. Screening only.
Setup at the close of day D-1: at least `ng` consecutive green days (close > prior close) and the run (close D-1 vs
the close before the first green day) is at least `ext` x ATR(20). Optional: ranges expanding (last day's range >=
the run's average range). Day D: short the first time price trades below the prior close (gap-down open below it ->
enter at the open, skipped if the gap is >= 1 ATR, 'overextended gap down' rule). Stop: the run's high (incl. day D's
high so far) + buffer. Exit: day D's close (his intraday version), or hold up to 3 days with a 2R target.
Intraday bars resolve the order of events: NAS RTH (m30 2021-23, m5 after), gold 5-min samples of M1 (NY dates)."""
import csv, glob, json, statistics as st, sys
from collections import defaultdict
from datetime import datetime, timezone
from vlib import NY, nas_m5, report


def nas_days():
    rows = []
    for r in csv.DictReader(open("/home/user/CTrader-Bots/Vanessa Algo Bots/research/data/nas100_m30/nas100_m30_2021_2023.csv")):
        rows.append((datetime.fromtimestamp(int(r["timestamp_ms"]) / 1000, timezone.utc).astimezone(NY),
                     float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"])))
    last = rows[-1][0]; rows += [x for x in nas_m5() if x[0] > last]
    d = defaultdict(list)
    for x in rows:
        if (x[0].hour, x[0].minute) >= (9, 30) and x[0].hour < 16: d[x[0].date()].append(x)
    return [(k, d[k]) for k in sorted(d) if len(d[k]) >= 10]


def gold_days():
    d = defaultdict(list)
    for f in sorted(glob.glob("/home/user/CTrader-Bots/XAUUSD historical Pricing data/data/XAUUSD_M_1_*.csv")):
        for line in open(f):
            if line[0] != "2": continue
            p = line.split(",")
            if p[0][15] not in "05": continue
            t = datetime.strptime(p[0][:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc).astimezone(NY)
            d[t.date()].append((t, float(p[1]), float(p[2]), float(p[3]), float(p[4])))
    return [(k, d[k]) for k in sorted(d) if len(d[k]) >= 50]


def run(days, ng, ext, expand, hold, cost, buf_atr=0.05):
    D = [(k, b[0][1], max(x[2] for x in b), min(x[3] for x in b), b[-1][4]) for k, b in days]
    out = []; i = 22
    while i < len(D):
        tr = [max(D[j][2], D[j - 1][4]) - min(D[j][3], D[j - 1][4]) for j in range(i - 20, i)]
        atr = st.mean(tr); g = 0
        while g < i - 1 and D[i - 1 - g][4] > D[i - 2 - g][4]: g += 1
        if g < ng or D[i - 1][4] - D[i - 1 - g][4] < ext * atr: i += 1; continue
        if expand and D[i - 1][2] - D[i - 1][3] < st.mean(x[2] - x[3] for x in D[i - g:i]): i += 1; continue
        pc = D[i - 1][4]; hi = max(x[2] for x in D[i - g:i]); bars = days[i][1]
        if bars[0][1] <= pc - atr: i += 1; continue
        e = stop = None; tgt = None; res = None
        for k in range(i, min(i + hold, len(D))):
            for t, o, h, l, c in days[k][1]:
                if e is None:
                    if h > hi: hi = h
                    if l < pc:
                        e = min(o, pc); stop = hi + buf_atr * atr; tgt = e - 2 * (stop - e) if hold > 1 else None
                    continue
                if h >= stop: res = stop; break
                if tgt is not None and l <= tgt: res = tgt; break
            if res is not None or e is None: break
        if e is None: i += 1; continue
        if res is None: res = days[min(i + hold, len(D)) - 1][1][-1][4]
        out.append((D[i][0], (e - res - cost) / (stop - e)))
        i += max(hold, 1)
    return out


bot = dict(zip(*json.load(open(sys.argv[1])).values()))
for name, days, cost in (("NAS", nas_days(), 1.2), ("Gold", gold_days(), 0.3)):
    for ng, ext in ((2, 2.0), (3, 3.0), (3, 4.0), (4, 4.0), (5, 5.0)):
        for expand in (False, True):
            for hold in (1, 3):
                report(f"{name} g>={ng} ext>={ext}ATR exp={int(expand)} hold{hold}",
                       run(days, ng, ext, expand, hold, cost), bot if name == "NAS" else None)
