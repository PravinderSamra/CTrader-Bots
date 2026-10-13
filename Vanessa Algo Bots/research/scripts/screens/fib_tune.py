"""Deni Dantev Fibonacci 0.618 follow-up. Step 1 TUNE on in-sample only (gold 2021-07..2023-12, FX 2012..2023).
Step 2 (separate run, 'oos' arg): frozen settings on 2024-01..2026 once.
Short side shown (longs = inverted bars). Rules as tradingcafe.deni_fib with parameters:
  tf (H1/H4), look = bars for 'H is the highest high' (trend top), fib = entry retracement, tgt = 'ext' (-0.272) or
  an R multiple, wait = bars the limit order lives. Stop = H + 0.1 ATR. Max hold 120 bars.
Costs: spread per round trip + swap per night (gold 6%/yr, FX 2%/yr of price)."""
import sys, statistics as st
from collections import defaultdict
from datetime import datetime, timezone
from tradingcafe import load, agg, atr_of, fractals, inv, COST

SWAP = {"XAUUSD": 0.06 / 365, "GBPUSD": 0.02 / 365, "EURUSD": 0.02 / 365}
START = {"XAUUSD": datetime(2021, 7, 1, tzinfo=timezone.utc), "GBPUSD": datetime(2012, 1, 1, tzinfo=timezone.utc),
         "EURUSD": datetime(2012, 1, 1, tzinfo=timezone.utc)}
SPLIT = datetime(2024, 1, 1, tzinfo=timezone.utc)


def fib(b, cost, swap, look, f, tgt, wait):
    A = atr_of(b); hi, lo = fractals(b); tr = []; busy = -1
    for H in hi:
        if H <= busy or H < look or A[H] is None: continue
        if b[H][2] < max(x[2] for x in b[H - look:H]): continue
        prior = [j for j in lo if H - look < j < H]
        if not prior: continue
        sl = b[prior[-1]][3]; top = b[H][2]; brk = None
        for m in range(H + 1, min(H + 40, len(b))):
            if b[m][2] > top: break
            if b[m][4] < sl: brk = m; break
        if brk is None: continue
        L = min(x[3] for x in b[H:brk + 1]); fill = None
        for m in range(brk + 1, min(brk + 1 + wait, len(b))):
            if b[m][2] > top: break
            if b[m][2] >= L + f * (top - L): fill = m; break
            L = min(L, b[m][3])
        if fill is None: continue
        rng = top - L; e = max(L + f * rng, b[fill][1]); stop = top + 0.1 * A[H]; r = stop - e
        t_ = L - 0.272 * rng if tgt == "ext" else e - tgt * r
        x = None; xi = fill
        if b[fill][2] >= stop: x = stop
        else:
            for m in range(fill + 1, min(fill + 121, len(b))):
                xi = m
                if b[m][2] >= stop: x = stop; break
                if b[m][3] <= t_: x = t_; break
            if x is None: x = b[xi][4]
        nights = (b[xi][0] - b[fill][0]).days
        R = (e - x - cost - abs(e) * swap * nights) / r
        tr.append((b[fill][0], R, (b[xi][0] - b[fill][0]).total_seconds() / 3600)); busy = xi
    return tr


def run_both(b, m, **p):
    return sorted(fib(b, COST[m], SWAP[m], **p) + fib(inv(b), COST[m], SWAP[m], **p))


def summ(name, tr):
    if not tr: return f"  {name:34s} none"
    rs = [r for _, r, _ in tr]; yr = defaultdict(float)
    for t, r, _ in tr: yr[t.year] += r
    eq = pk = dd = 0.0
    for r in rs: eq += r; pk = max(pk, eq); dd = max(dd, pk - eq)
    return (f"  {name:34s} n={len(rs):4d} win={sum(r > 0 for r in rs)/len(rs):4.0%} avg={st.mean(rs):+.3f}R tot={sum(rs):+6.1f}R "
            f"dd={dd:5.1f}R hold={st.median(h for *_, h in tr):4.0f}h  " + " ".join(f"{y%100:02d}:{v:+.0f}" for y, v in sorted(yr.items())))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "tune"
    for m in ("XAUUSD", "GBPUSD", "EURUSD"):
        h1 = load(m); h4 = agg(h1, 4)
        for tfn, b in (("H1", h1), ("H4", h4)):
            if mode == "tune":
                b = [x for x in b if START[m] <= x[0] < SPLIT]
                print(f"== {m} {tfn} in-sample {b[0][0]:%Y-%m}..{b[-1][0]:%Y-%m}")
                for look in (50, 100):
                    for f in (0.5, 0.618, 0.705):
                        for tgt in ("ext", 1.0, 2.0):
                            print(summ(f"look={look} fib={f} tgt={tgt}", run_both(b, m, look=look, f=f, tgt=tgt, wait=30)))


FROZEN = dict(look=50, f=0.618, tgt="ext", wait=30)   # frozen 13 Oct 2026 after the in-sample tune: Deni's own rules, H1


def oos():
    import json
    out = {}
    for m in ("XAUUSD", "GBPUSD", "EURUSD"):
        b = load(m)
        ins = [x for x in b if START[m] <= x[0] < SPLIT]
        tr_in = run_both(ins, m, **FROZEN)
        tr_out = [t for t in run_both(b, m, **FROZEN) if t[0] >= SPLIT]
        print(f"== {m} H1 frozen {FROZEN}")
        print(summ("in-sample", tr_in)); print(summ("OUT-OF-SAMPLE 2024+", tr_out))
        out[m] = [(t.strftime("%Y-%m-%d"), r) for t, r, _ in tr_in + tr_out]
    json.dump(out, open("/home/user/CTrader-Bots/Vanessa Algo Bots/research/data/deni_fib_trades.json", "w"))


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "oos":
    oos()
