"""Darren Winters weekly watch lists: does UP beat DOWN afterwards? Pre-registered 16 Oct 2026.
Start = close of the first trading day after the email date (no look-ahead). Horizons 5 and 21 trading days.
Long-short = mean(UP) - mean(DOWN) - 0.2% (0.1% round trip per leg). Also each side vs its index."""
import json, sys, os, statistics as st
from datetime import datetime, timezone
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "watchlists.json")
D = sys.argv[1]
MAP = {"BTA": "BT-A", "ADN": "ABDN"}
def yt(k, t):
    if k.startswith("us"): return t.replace(".", "-")
    if k.startswith("uk"): return MAP.get(t, t) + ".L"
    return t + "=X" if not t.startswith("USD") else t[3:] + "=X"
cache = {}
def series(y):
    if y not in cache:
        r = json.load(open(os.path.join(D, y + ".json")))["chart"]["result"][0]
        ts = r["timestamp"]; c = r["indicators"]["quote"][0]["close"]
        cache[y] = [(datetime.fromtimestamp(a, timezone.utc).date(), b) for a, b in zip(ts, c) if b is not None]
    return cache[y]
def fwd(y, d0, h):
    s = series(y)
    i = next((k for k, (d, _) in enumerate(s) if d > d0), None)
    if i is None or i + h >= len(s): return None
    v = s[i + h][1] / s[i][1] - 1
    if y.endswith("=X") and y[:3] in ("TRY", "JPY", "CAD", "CHF") and len(y) == 5: pass
    return v
def fxret(t, d0, h):
    # pair return in quote terms: XXXYYY up = price up. Yahoo 'USDTRY' is 'TRY=X' (USD per... = TRY per USD) -> same direction
    return fwd(yt("fx", t), d0, h)
L = json.load(open(P))
rows = []
for l in L:
    d0 = datetime.strptime(l["date"], "%Y-%m-%d %H:%M").date()
    for h in (5, 21):
        out = {"date": str(d0), "h": h}
        for mk, idx in (("us", "SPY"), ("uk", "^FTSE")):
            up = [fwd(yt(mk, t), d0, h) for t in l[mk + "_up"].split()]
            dn = [fwd(yt(mk, t), d0, h) for t in l[mk + "_down"].split()]
            ix = fwd(idx, d0, h)
            up = [x for x in up if x is not None]; dn = [x for x in dn if x is not None]
            if not up or not dn or ix is None: continue
            out[mk] = (st.mean(up) - st.mean(dn) - 0.002, st.mean(up) - ix, ix - st.mean(dn),
                       sum(x > ix for x in up) / len(up), sum(x < ix for x in dn) / len(dn))
        fu = [fxret(t, d0, h) for t in l["fx_up"].split()]; fd = [fxret(t, d0, h) for t in l["fx_down"].split()]
        fu = [x for x in fu if x is not None]; fd = [x for x in fd if x is not None]
        if fu and fd: out["fx"] = (st.mean(fu) - st.mean(fd), st.mean(fu), -st.mean(fd))
        rows.append(out)
for h in (5, 21):
    print(f"\n=== {h} trading days after each list ===")
    print("date        US L-S   UP-SPY  SPY-DN  UPbeat DNlag |  UK L-S  UP-FTSE FTSE-DN UPbeat DNlag |  FX L-S")
    for r in [r for r in rows if r["h"] == h]:
        u = r.get("us"); k = r.get("uk"); f = r.get("fx")
        fmt = lambda z: f"{z[0]*100:+6.2f}% {z[1]*100:+6.2f}% {z[2]*100:+6.2f}%  {z[3]:4.0%}  {z[4]:4.0%}" if z else " " * 40
        print(f"{r['date']}  {fmt(u)} | {fmt(k)} | " + (f"{f[0]*100:+6.2f}%" if f else ""))
    for mk in ("us", "uk", "fx"):
        v = [r[mk][0] for r in rows if r["h"] == h and mk in r]
        if v: print(f"  {mk}: mean long-short {st.mean(v)*100:+.2f}%  positive {sum(x>0 for x in v)}/{len(v)}")
