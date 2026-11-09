"""NQ/ES SMT sweep into FVG, rules frozen in SMT_SWEEP_TEST_PLAN.md (9 Nov 2026). Usage: smt_sweep.py nas100_m5.csv us500_m5.csv"""
import csv, sys
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from collections import defaultdict
NY = ZoneInfo("America/New_York"); COST, RR, BUF = 1.5, 2.5, 2.0
def load(p):
    out = {}
    for r in csv.DictReader(open(p)):
        t = datetime.fromtimestamp(int(r["timestamp_ms"]) / 1000, timezone.utc).astimezone(NY)
        out[int(r["timestamp_ms"])] = (t, float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"]))
    return out
def sessions(bars):
    d = defaultdict(list)
    for k in sorted(bars):
        t = bars[k][0]; d[(t + timedelta(hours=6)).date()].append((k,) + bars[k])
    return d
NQ, ES = sessions(load(sys.argv[1])), sessions(load(sys.argv[2]))
mins = lambda t: t.hour * 60 + t.minute
def hl(rows, f):
    s = [r for r in rows if f(r[1])]
    return (max(r[3] for r in s), min(r[4] for r in s)) if s else None
def h4(rows):   # bucket -> (high, low); buckets 18,22,02,06,10,14
    b = defaultdict(list)
    for r in rows: b[((r[1].hour + 6) % 24) // 4].append(r)
    return {k: (max(x[3] for x in v), min(x[4] for x in v)) for k, v in b.items()}
def run(smt, bias):
    days = sorted(d for d in NQ if d in ES and d.weekday() < 5); trades = []
    for n in range(1, len(days)):
        d, p = days[n], days[n - 1]
        if (d - p).days > 4: continue
        q, e = NQ[d], ES[d]
        rth = lambda t: mins(t) >= 570 and t.hour < 17
        pre = lambda t: not (t.hour < 18 and mins(t) >= 570)          # session start 18:00 -> 09:30
        lv_q = {"pd": hl(NQ[p], lambda t: True), "on": hl(q, pre)}
        lv_e = {"pd": hl(ES[p], lambda t: True), "on": hl(e, pre)}
        if None in lv_q.values() or None in lv_e.values(): continue
        H4 = h4(q); allowed = {1, -1}
        if bias:
            asia = hl(q, lambda t: t.hour >= 20); lon = hl(q, lambda t: 2 <= t.hour < 5)
            lb = [r for r in q if 2 <= r[1].hour < 5]; o18 = q[0][2]
            op = [r for r in q if mins(r[1]) == 570]
            if not (asia and lon and lb and op): continue
            if lon[0] > asia[0] and lon[1] >= asia[1] and lb[-1][5] < asia[0]: allowed = {-1}
            elif lon[1] < asia[1] and lon[0] <= asia[0] and lb[-1][5] > asia[1]: allowed = {1}
            else: allowed = {-1} if op[0][2] > o18 else {1}
        W = [i for i, r in enumerate(q) if 570 <= mins(r[1]) < 630]
        if not W: continue
        emap = {r[0]: r for r in e}; cands = []
        for side in allowed:   # -1 short at highs, +1 long at lows
            for name in ("pd", "on"):
                L, LE = lv_q[name][0 if side < 0 else 1], lv_e[name][0 if side < 0 else 1]
                i = next((i for i in W if (q[i][3] > L if side < 0 else q[i][4] < L)), None)
                if i is None: continue
                if smt:
                    es_so_far = [r for r in e if r[0] <= q[i][0] and (name == "on" or True)]
                    if name == "pd": es_so_far = [r for r in e if r[0] <= q[i][0]]
                    else: es_so_far = [r for r in e if r[0] <= q[i][0] and mins(r[1]) >= 570 and r[1].hour < 17]
                    if not es_so_far or q[i][0] not in emap: continue
                    if (max(r[3] for r in es_so_far) > LE) if side < 0 else (min(r[4] for r in es_so_far) < LE): continue
                for j in range(i + 2, min(i + 7, len(q))):
                    a, c = q[j - 2], q[j]
                    if mins(c[1]) >= 630 or c[1].hour >= 17: break
                    gap = (c[3], a[4]) if side < 0 else (a[3], c[4])   # (bottom, top)
                    if gap[0] >= gap[1]: continue
                    k4 = ((c[1].hour + 6) % 24) // 4 - 1
                    if k4 not in H4: break
                    mid4 = (H4[k4][0] + H4[k4][1]) / 2; midg = (gap[0] + gap[1]) / 2
                    if (midg <= mid4) if side < 0 else (midg >= mid4): continue
                    ext = max(r[3] for r in q[i:j + 1]) if side < 0 else min(r[4] for r in q[i:j + 1])
                    entry = gap[0] if side < 0 else gap[1]; stop = ext + BUF if side < 0 else ext - BUF
                    risk = (stop - entry) * -side
                    if risk <= 0: break
                    cands.append((j, side, entry, stop, risk)); break
        res = []
        for j, side, entry, stop, risk in cands:
            tgt = entry + side * RR * risk; filled = None
            for m in range(j + 1, len(q)):
                r = q[m]
                if r[1].hour >= 12 and mins(r[1]) >= 720 or r[1].hour >= 17: break
                if filled is None:
                    if mins(r[1]) >= 630: break
                    if (r[3] >= entry) if side < 0 else (r[4] <= entry):
                        filled = m
                        if (r[3] >= stop) if side < 0 else (r[4] <= stop): res.append((m, -1.0)); break
                    continue
                if (r[3] >= stop) if side < 0 else (r[4] <= stop): res.append((filled, -1.0)); break
                if (r[4] <= tgt) if side < 0 else (r[3] >= tgt): res.append((filled, RR)); break
                last = r
            else:
                pass
            if filled is not None and (not res or res[-1][0] != filled):
                lastc = [r for r in q[filled:] if mins(r[1]) < 720 and r[1].hour < 17][-1][5]
                res.append((filled, (lastc - entry) * side / risk))
            if filled is not None: res[-1] = (res[-1][0], res[-1][1] - COST / risk)
        if res: trades.append((d, min(res)[1]))
    return trades
def show(name, t):
    R = [x for _, x in t]; w = [x for x in R if x > 0]; l = [x for x in R if x <= 0]
    per = {"2023H2-24": [x for d, x in t if d.year <= 2024], "2025": [x for d, x in t if d.year == 2025],
           "2026H1": [x for d, x in t if d.year == 2026]}
    print(f"{name}: n {len(R)} win {100*len(w)/max(1,len(R)):.0f}% avg {sum(R)/max(1,len(R)):+.3f}R total {sum(R):+.1f}R "
          f"PF {sum(w)/max(1e-9,-sum(l)):.2f} | " + "  ".join(f"{k} {sum(v):+.1f}R ({len(v)})" for k, v in per.items()))
show("T1 SMT", run(True, False)); show("T2 SMT+bias", run(True, True)); show("T3 no SMT", run(False, False))
