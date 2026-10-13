"""Marco liquidity strategy, TradeZella playbook version (NY open), coded mechanically. Screening only.
Levels: 30m swing highs/lows (2 bars each side) formed 00:00-09:30 NY that day ('respected, price moved away':
 price later traded at least 0.5 x ATR(30m,14) away from it before 09:30) and not yet traded through before 09:30.
Sell: 09:30-11:00 NY a 5m bar trades above the level, and a 5m close is back below it (the trap) within 3 bars ->
 short at that close; stop = highest high since the sweep + 0.5 cost; target = the nearest 30m swing low below
 (any from the previous 2 days, not yet taken) - or yesterday's NY-session low if none. Need reward >= MINR x risk.
 Single target (he only takes partials at liquidity). Flat 16:00 NY.
Buys mirror. One trade a day (first trigger). Costs: NAS100 1.5, US30 2.5, US500 0.6 points."""
import sys, statistics as st
from datetime import timedelta
from collections import defaultdict
from rajan_jade import load, summ, NY

def m30(b):
    out = []
    for t, o, h, l, c in b:
        k = t.replace(minute=t.minute - t.minute % 30)
        if out and out[-1][0] == k:
            out[-1][2] = max(out[-1][2], h); out[-1][3] = min(out[-1][3], l); out[-1][4] = c
        else: out.append([k, o, h, l, c])
    return out

def run(b, cost, minr, side_only=0):
    H = m30(b); n = len(H)
    atr = [None] * n
    for i in range(14, n): atr[i] = st.mean(x[2] - x[3] for x in H[i - 13:i + 1])
    swh = [(i, H[i][2]) for i in range(2, n - 2) if H[i][2] >= max(x[2] for x in H[i - 2:i + 3])]
    swl = [(i, H[i][3]) for i in range(2, n - 2) if H[i][3] <= min(x[3] for x in H[i - 2:i + 3])]
    hidx = {x[0]: i for i, x in enumerate(H)}
    by = defaultdict(list)
    for i, x in enumerate(b): by[x[0].astimezone(NY).date()].append(i)
    days = sorted(by); tr = []
    for d in days:
        idx = by[d]
        pre = [i for i in idx if b[i][0].astimezone(NY).hour < 9 or (b[i][0].astimezone(NY).hour == 9 and b[i][0].astimezone(NY).minute < 30)]
        win = [i for i in idx if (9, 30) <= (b[i][0].astimezone(NY).hour, b[i][0].astimezone(NY).minute) < (11, 0)]
        if len(pre) < 60 or len(win) < 15: continue
        t0 = b[pre[0]][0]; t930 = b[win[0]][0]
        h_open = hidx.get(b[win[0]][0].replace(minute=30)); 
        if h_open is None: continue
        lv = {}
        for side, sw in ((-1, swh), (1, swl)):
            cand = []
            for j, p in sw:
                if not (t0 <= H[j][0] and j + 2 < h_open) or atr[j] is None: continue
                after = H[j + 1:h_open]
                if side == -1:
                    if max(x[2] for x in after) > p: continue          # already taken pre-NY
                    if p - min(x[3] for x in after) < 0.5 * atr[j]: continue
                else:
                    if min(x[3] for x in after) < p: continue
                    if max(x[2] for x in after) - p < 0.5 * atr[j]: continue
                cand.append((j, p))
            lv[side] = cand
        done = False
        for k, i in enumerate(win):
            if done: break
            t, o, h, l, c = b[i]
            for side in (-1, 1):
                if side_only and side != side_only: continue
                for j, p in lv[side]:
                    # swept within the last 3 bars (incl. this one) and this bar closes back inside
                    seg = win[max(0, k - 2):k + 1]
                    if side == -1 and max(b[x][2] for x in seg) > p and c < p:
                        ext = max(b[x][2] for x in win[:k + 1]); stp = ext + 0.5 * cost
                        tg = [q for jj, q in swl if jj + 2 < h_open and H[jj][0] >= t0 - timedelta(days=3)
                              and q < c and min(x[3] for x in H[jj + 1:h_open]) > q]
                        tgt = max(tg) if tg else None
                    elif side == 1 and min(b[x][3] for x in seg) < p and c > p:
                        ext = min(b[x][3] for x in win[:k + 1]); stp = ext - 0.5 * cost
                        tg = [q for jj, q in swh if jj + 2 < h_open and H[jj][0] >= t0 - timedelta(days=3)
                              and q > c and max(x[2] for x in H[jj + 1:h_open]) < q]
                        tgt = min(tg) if tg else None
                    else: continue
                    if tgt is None: continue
                    e = c; r = abs(e - stp)
                    if r <= 0 or abs(tgt - e) < minr * r: continue
                    x = None
                    for m in range(i + 1, len(b)):
                        mt = b[m][0].astimezone(NY)
                        if mt.date() != d or mt.hour >= 16: x = b[m - 1][4]; break
                        if side == -1:
                            if b[m][2] >= stp: x = stp; break
                            if b[m][3] <= tgt: x = tgt; break
                        else:
                            if b[m][3] <= stp: x = stp; break
                            if b[m][2] >= tgt: x = tgt; break
                    if x is None: x = b[-1][4]
                    tr.append((t, side * (x - e) / r - cost / r)); done = True; break
                if done: break
    return tr

if __name__ == "__main__":
    for m, f, cost in (("NAS100", "NAS100/nas100_m5.csv", 1.5), ("US30", "US30/us30_m5.csv", 2.5)):
        b = load(f); print("==", m)
        for minr in (1.0, 2.0, 3.0):
            summ(f"NY-open sweep, target 30m liquidity, >= {minr}R", run(b, cost, minr))
