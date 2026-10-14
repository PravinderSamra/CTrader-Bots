"""Match the Deni Fib cTrader tick trades (H| lines) with the Python screen's trades, trade by trade."""
import re, sys
from datetime import datetime, timezone, timedelta
from tradingcafe import load, atr_of, fractals, inv, COST
from fib_tune import SWAP

LOG = sys.argv[1]


def py_trades(b, m, side):
    """same as fib_tune.fib but returns details. side -1 = sells on b, +1 = buys (b inverted)"""
    bb = b if side < 0 else inv(b)
    A = atr_of(bb); hi, lo = fractals(bb); out = []; busy = -1
    for H in hi:
        if H <= busy or H < 50 or A[H] is None: continue
        if bb[H][2] < max(x[2] for x in bb[H - 50:H]): continue
        prior = [j for j in lo if H - 50 < j < H]
        if not prior: continue
        sl = bb[prior[-1]][3]; top = bb[H][2]; brk = None
        for m_ in range(H + 1, min(H + 40, len(bb))):
            if bb[m_][2] > top: break
            if bb[m_][4] < sl: brk = m_; break
        if brk is None: continue
        L = min(x[3] for x in bb[H:brk + 1]); fill = None
        for m_ in range(brk + 1, min(brk + 31, len(bb))):
            if bb[m_][2] > top: break
            if bb[m_][2] >= L + 0.618 * (top - L): fill = m_; break
            L = min(L, bb[m_][3])
        if fill is None: continue
        rng = top - L; e = max(L + 0.618 * rng, bb[fill][1]); stop = top + 0.1 * A[H]; r = stop - e
        tgt = L - 0.272 * rng; x = None; xi = fill; how = "time"
        if bb[fill][2] >= stop: x = stop; how = "stop"
        else:
            for k in range(fill + 1, min(fill + 121, len(bb))):
                xi = k
                if bb[k][2] >= stop: x = stop; how = "stop"; break
                if bb[k][3] <= tgt: x = tgt; how = "target"; break
            if x is None: x = bb[xi][4]
        R = (e - x - COST[m]) / r
        sgn = -1 if side < 0 else 1
        out.append(dict(t=bb[fill][0], side="Sell" if side < 0 else "Buy", e=abs(e), stop=abs(stop), tgt=abs(tgt), R=R, how=how,
                        t1=bb[xi][0], H=bb[H][0], brk=bb[brk][0]))
        busy = xi
    return out


tick = []
for line in open(LOG):
    mm = re.search(r"Info \| H\|(.*)", line)
    if mm:
        p = mm.group(1).split("|")
        tick.append(dict(sym=p[2], side=p[3], t=datetime.strptime(p[4], "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc),
                         e=float(p[7]), x=float(p[8]), net=float(p[12]), vol=float(p[6])))

for m in ("GBPUSD", "XAUUSD"):
    b = [x for x in load(m) if x[0] >= datetime(2021, 6, 1, tzinfo=timezone.utc)]
    end = b[-1][0]
    py = [t for t in py_trades(b, m, -1) + py_trades(b, m, 1) if t["t"] >= datetime(2021, 7, 1, tzinfo=timezone.utc)]
    tk = [t for t in tick if t["sym"] == m and t["t"] <= end]
    used = set(); pairs = []; onlypy = []
    for p in py:
        best = None
        for i, t in enumerate(tk):
            if i in used or t["side"] != p["side"]: continue
            d = abs((t["t"] - p["t"]).total_seconds())
            if d <= 3 * 3600 and (best is None or d < best[0]): best = (d, i)
        if best: used.add(best[1]); pairs.append((p, tk[best[1]]))
        else: onlypy.append(p)
    onlytk = [t for i, t in enumerate(tk) if i not in used]
    Rp = sum(p["R"] for p, _ in pairs); Rt = sum(t["net"] for _, t in pairs) / 100
    print(f"== {m}: screen {len(py)} trades ({sum(p['R'] for p in py):+.1f}R), tick {len(tk)} trades ({sum(t['net'] for t in tk)/100:+.1f}R) up to {end:%Y-%m-%d}")
    print(f"  matched {len(pairs)}: screen {Rp:+.1f}R vs tick {Rt:+.1f}R")
    print(f"  only in screen {len(onlypy)}: {sum(p['R'] for p in onlypy):+.1f}R   only in tick {len(onlytk)}: {sum(t['net'] for t in onlytk)/100:+.1f}R")
    agree = sum((p["R"] > 0) == (t["net"] > 0) for p, t in pairs)
    print(f"  matched trades with the same win/loss outcome: {agree}/{len(pairs)}")
    ed = [abs(p["e"] - t["e"]) for p, t in pairs]
    print(f"  median entry price difference: {sorted(ed)[len(ed)//2]:.5f}")
    flips = [(p, t) for p, t in pairs if (p["R"] > 0) != (t["net"] > 0)]
    for p, t in flips[:8]:
        print(f"   {p['side']} screen {p['t']:%Y-%m-%d %H:%M} e={p['e']:.5f} stop={p['stop']:.5f} tgt={p['tgt']:.5f} {p['how']} R={p['R']:+.2f} | tick {t['t']:%m-%d %H:%M} e={t['e']} x={t['x']} net={t['net']}")


if len(sys.argv) > 2:
    import collections
    for m in ("GBPUSD", "XAUUSD"):
        b = [x for x in load(m) if x[0] >= datetime(2021, 6, 1, tzinfo=timezone.utc)]
        end = b[-1][0]
        py = [t for t in py_trades(b, m, -1) + py_trades(b, m, 1) if t["t"] >= datetime(2021, 7, 1, tzinfo=timezone.utc)]
        tk = [t for t in tick if t["sym"] == m and t["t"] <= end]
        used = set()
        for p in py:
            c = [(abs((t["t"] - p["t"]).total_seconds()), i) for i, t in enumerate(tk) if i not in used and t["side"] == p["side"]]
            c = [x for x in c if x[0] <= 3 * 3600]
            if c: used.add(min(c)[1])
        extra = [t for i, t in enumerate(tk) if i not in used]
        # nearest screen trade in time (same side) and whether a screen trade was open then
        print("==", m, "extra tick trades:", len(extra), "wins", sum(t["net"] > 0 for t in extra))
        for t in extra[:12]:
            near = min(py, key=lambda p: abs((p["t"] - t["t"]).total_seconds()) + (0 if p["side"] == t["side"] else 1e9))
            overl = [p for p in py if p["side"] == t["side"] and p["t"] <= t["t"] <= p["t1"]]
            print(f"  {t['side']} {t['t']:%Y-%m-%d %H:%M} e={t['e']} x={t['x']} net={t['net']:+.0f}  nearest screen {near['t']:%m-%d %H:%M} | screen trade open then: {bool(overl)}")
