"""Trader Kane TradeZella playbook WITH the SMT filter (NQ vs ES -> NAS100 vs US500 CFD, Pepperstone m5, same feed).
Base rules = rajan_jade.kane_tz (10:00 hour sweeps the 09:00 hour extreme, 5m close back through the 10:00 open,
target 50% of the H1 dealing range, break-even on the 11:00 flip, flat 12:00, daily EMA21 trend).
SMT (short): by the trigger bar, NAS100 has traded above its 09:00-hour high but US500 has NOT traded above its own
09:00-hour high. Longs mirror. Also tests the reverse (trade US500 when US500 sweeps and NAS doesn't)."""
import sys
from collections import defaultdict
from rajan_jade import load, ema, summ, NY, kane_tz

B = sys.argv[1] if len(sys.argv) > 1 else "US500/us500_m5.csv"


def smt_filter(trades, a, b, side_of):
    """keep trades on `a` where `b` did not confirm the sweep by the trigger time"""
    bi = {t: i for i, (t, *_ ) in enumerate(b)}
    byd = defaultdict(list)
    for i, (t, *_ ) in enumerate(b):
        byd[t.astimezone(NY).date()].append(i)
    keep, conf = [], []
    for t, r, side in trades:
        d = t.astimezone(NY).date(); idx = byd.get(d, [])
        h9 = [i for i in idx if b[i][0].astimezone(NY).hour == 9]
        h10 = [i for i in idx if b[i][0].astimezone(NY).hour == 10 and b[i][0] <= t]
        if len(h9) < 10 or not h10: continue
        if side == -1:
            swept = max(b[i][2] for i in h10) > max(b[i][2] for i in h9)
        else:
            swept = min(b[i][3] for i in h10) < min(b[i][3] for i in h9)
        (conf if swept else keep).append((t, r))
    return keep, conf


if __name__ == "__main__":
    nas = load("NAS100/nas100_m5.csv"); spx = load(B)
    import rajan_jade as rj
    # kane_tz doesn't return side; recover it: re-run with side attached
    def with_side(bars, cost):
        out = []
        orig = rj.kane_tz(bars, cost)
        # side = sign of the trend rule used inside kane_tz (yesterday close vs daily EMA21)
        by = defaultdict(list)
        for i, (t, *_ ) in enumerate(bars): by[t.astimezone(NY).date()].append(i)
        days = sorted(by); dc = {}
        for d in days:
            c = [i for i in by[d] if bars[i][0].astimezone(NY).hour < 16]
            if c: dc[d] = bars[c[-1]][4]
        dl = [d for d in days if d in dc]; e = dict(zip(dl, ema([dc[d] for d in dl], 21)))
        prev = {dl[k]: dl[k - 1] for k in range(1, len(dl))}
        for t, r in orig:
            p = prev[t.astimezone(NY).date()]
            out.append((t, r, -1 if dc[p] < e[p] else 1))
        return out
    for name, a, b, cost in (("NAS100", nas, spx, 1.5), ("US500", spx, nas, 0.6)):
        tr = with_side(a, cost)
        keep, conf = smt_filter(tr, a, b, None)
        print(f"== {name} (other index = SMT check)")
        summ("all (no SMT)", [(t, r) for t, r, _ in tr])
        summ("SMT divergence (other did NOT sweep)", keep)
        summ("no divergence (both swept)", conf)
