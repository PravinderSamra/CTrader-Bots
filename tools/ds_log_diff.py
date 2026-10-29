"""Parse a Daily Systems backtest log, and diff two of them.

The bot prints its whole trade history at the end of a run as H| lines, so a
cTrader CSV export is not needed — the log IS the trade list:

    H|id|strategy|symbol|entry date|exit date|volume|entry px|exit px|
      gross|swap|commission|net

It also prints, at startup, how much daily history each symbol had in the
LOCAL cache (S| lines) — which is the first thing to compare between two
machines, because that is per-installation and nothing in the bot controls it.

Usage:  dslog.py <log>            summarise one run
        dslog.py <a> <b>          diff two runs, trade by trade
"""
import sys, re, collections

H = re.compile(r"\|\s*Info\s*\|\s*H\|(.*)$")
S = re.compile(r"\|\s*Info\s*\|\s*S\|(.*)$")
G = re.compile(r"\|\s*Info\s*\|\s*G\|(.*)$")
W = re.compile(r"\|\s*Info\s*\|\s*W\|(.*)$")
P = re.compile(r"\|\s*Info\s*\|\s*P\|(.*)$")
VER = re.compile(r"\|\s*Info\s*\|\s*(Daily Systems v[^\s]+.*)$")


def f(x):
    try:
        return float(x)
    except ValueError:
        return None


def load(path):
    trades, syms, guards, skips, days, ver = [], [], [], [], [], None
    for ln in open(path, encoding="utf-8", errors="replace"):
        m = H.search(ln)
        if m:
            p = m.group(1).split("|")
            if len(p) >= 12:
                trades.append({
                    "id": int(p[0]), "strat": p[1], "sym": p[2],
                    "in": p[3], "out": p[4], "vol": f(p[5]),
                    "px_in": f(p[6]), "px_out": f(p[7]),
                    "gross": f(p[8]), "swap": f(p[9]),
                    "comm": f(p[10]), "net": f(p[11])})
            continue
        m = S.search(ln)
        if m:
            p = m.group(1).split("|")
            syms.append({"sym": p[0], "bars": p[1], "first": p[2],
                         "pv": p[3] if len(p) > 3 else "", })
            continue
        m = G.search(ln)
        if m:
            guards.append(m.group(1))
            continue
        m = W.search(ln)
        if m:
            skips.append(m.group(1))
            continue
        m = P.search(ln)
        if m:
            days.append(m.group(1))
            continue
        m = VER.search(ln)
        if m and ver is None:
            ver = m.group(1).strip()
    return dict(trades=trades, syms=syms, guards=guards, skips=skips,
                days=days, ver=ver)


def summarise(d, name):
    t = d["trades"]
    print(f"===== {name}")
    print(f"  {d['ver']}")
    print("  symbol history in the LOCAL cache at startup:")
    for s in d["syms"]:
        print(f"    {s['sym']:<12} {s['bars']:<16} first {s['first']:<12} {s['pv']}")
    net = sum(x["net"] for x in t)
    print(f"  trades {len(t)}   net {net:,.2f}   "
          f"gross {sum(x['gross'] for x in t):,.2f}   "
          f"swap {sum(x['swap'] for x in t):,.2f}   "
          f"comm {sum(x['comm'] for x in t):,.2f}")
    print(f"  daily-guard events: {len(d['guards'])}")
    for g in d["guards"]:
        print(f"    {g}")
    by = collections.defaultdict(lambda: [0, 0.0])
    for x in t:
        k = (x["sym"], x["strat"])
        by[k][0] += 1
        by[k][1] += x["net"]
    print(f"  {'symbol':<13}{'strat':<8}{'n':>5}{'net':>12}")
    for (sym, st), (n, v) in sorted(by.items()):
        print(f"  {sym:<13}{st:<8}{n:>5}{v:>12,.2f}")
    skipr = collections.Counter(s.split("|")[-1] for s in d["skips"])
    print("  skip reasons:", dict(skipr))
    return t


def key(x):
    """Identity of a trade that should be stable across machines."""
    return (x["strat"], x["sym"], x["in"])


def diff(a, b, na, nb):
    ta, tb = a["trades"], b["trades"]
    print(f"\n===== DIFF  {na}  vs  {nb}")
    print(f"  trades {len(ta)} vs {len(tb)}   "
          f"net {sum(x['net'] for x in ta):,.2f} vs {sum(x['net'] for x in tb):,.2f}   "
          f"gap {sum(x['net'] for x in tb) - sum(x['net'] for x in ta):+,.2f}")

    for s1, s2 in zip(a["syms"], b["syms"]):
        if s1 != s2:
            print(f"  CACHE DIFFERS  {s1['sym']}: {s1['bars']} first {s1['first']} "
                  f"({s1['pv']})  vs  {s2['bars']} first {s2['first']} ({s2['pv']})")

    ka = {key(x): x for x in ta}
    kb = {key(x): x for x in tb}
    only_a = [ka[k] for k in ka.keys() - kb.keys()]
    only_b = [kb[k] for k in kb.keys() - ka.keys()]
    both = sorted(ka.keys() & kb.keys(), key=lambda k: k[2])

    print(f"\n  trades only in {na}: {len(only_a)}  "
          f"(net {sum(x['net'] for x in only_a):,.2f})")
    for x in sorted(only_a, key=lambda x: x["in"])[:25]:
        print(f"    {x['in']}  {x['strat']:<7}{x['sym']:<13}{x['net']:>10,.2f}")
    print(f"  trades only in {nb}: {len(only_b)}  "
          f"(net {sum(x['net'] for x in only_b):,.2f})")
    for x in sorted(only_b, key=lambda x: x["in"])[:25]:
        print(f"    {x['in']}  {x['strat']:<7}{x['sym']:<13}{x['net']:>10,.2f}")

    print(f"\n  shared trades whose numbers differ (first 30, by date):")
    print(f"    {'entry':<12}{'strat':<7}{'symbol':<13}"
          f"{'d vol':>8}{'d in':>10}{'d out':>10}{'d net':>10}")
    shown = tot = 0
    for k in both:
        x, y = ka[k], kb[k]
        dv, di, do, dn = (y["vol"] - x["vol"], y["px_in"] - x["px_in"],
                          y["px_out"] - x["px_out"], y["net"] - x["net"])
        if max(abs(dv), abs(di), abs(do), abs(dn)) < 0.005:
            continue
        tot += 1
        if shown < 30:
            shown += 1
            print(f"    {k[2]:<12}{k[0]:<7}{k[1]:<13}"
                  f"{dv:>+8.2f}{di:>+10.2f}{do:>+10.2f}{dn:>+10.2f}")
    print(f"    ({tot} shared trades differ in total; "
          f"net effect {sum(kb[k]['net'] - ka[k]['net'] for k in both):+,.2f})")

    ga, gb = set(a["guards"]), set(b["guards"])
    if ga != gb:
        print(f"\n  DAILY-GUARD events differ:")
        for g in sorted(ga - gb): print(f"    only {na}: {g}")
        for g in sorted(gb - ga): print(f"    only {nb}: {g}")


if __name__ == "__main__":
    if len(sys.argv) == 2:
        summarise(load(sys.argv[1]), sys.argv[1].split("/")[-1])
    elif len(sys.argv) == 3:
        A, B = load(sys.argv[1]), load(sys.argv[2])
        na, nb = sys.argv[1].split("/")[-1], sys.argv[2].split("/")[-1]
        summarise(A, na); print(); summarise(B, nb)
        diff(A, B, na, nb)
    else:
        print(__doc__)
