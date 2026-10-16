"""Unseen test (pre-registered 16 Oct 2026 after seeing Jul-Aug only): lists dated before 1 Jul 2026.
Trial 1: UP minus DOWN > 0 (as intended). Trial 2: DOWN minus UP > 0 (reverse). Horizons 5 and 21 trading days.
Pass: mean > 0 after 0.2% costs, positive in both halves (Jan-Mar, Apr-Jun), and the 95% interval from a
bootstrap over calendar months (lists overlap, so months are resampled as blocks) above zero."""
import json, sys, os, random, statistics as st
from datetime import datetime, timezone
H = os.path.dirname(os.path.abspath(__file__)); D = sys.argv[1]
MAP = {"BTA": "BT-A", "ADN": "ABDN", "RMG": "IDS"}
def yt(k, t):
    if k.startswith("us"): return t.replace(".", "-")
    if k.startswith("uk"): return MAP.get(t, t) + ".L"
    return t + "=X" if not t.startswith("USD") else t[3:] + "=X"
cache = {}
def fwd(y, d0, h):
    f = os.path.join(D, y + ".json")
    if not os.path.exists(f): return None
    if y not in cache:
        try:
            r = json.load(open(f))["chart"]["result"][0]
            cache[y] = [(datetime.fromtimestamp(a, timezone.utc).date(), b) for a, b in
                        zip(r["timestamp"], r["indicators"]["quote"][0]["close"]) if b is not None]
        except Exception: cache[y] = []
    s = cache[y]
    i = next((k for k, (d, _) in enumerate(s) if d > d0), None)
    if i is None or i + h >= len(s): return None
    return s[i + h][1] / s[i][1] - 1
def spread(l, mk, d0, h):
    up = [x for x in (fwd(yt(mk, t), d0, h) for t in l[mk + "_up"].split()) if x is not None]
    dn = [x for x in (fwd(yt(mk, t), d0, h) for t in l[mk + "_down"].split()) if x is not None]
    if not up or not dn: return None
    return st.mean(up) - st.mean(dn)
L = [l for l in json.load(open(os.path.join(H, "watchlists.json"))) if l["date"] < "2026-07-01"]
print(f"unseen lists: {len(L)} ({L[0]['date'][:10]} .. {L[-1]['date'][:10]})")
random.seed(1)
for h in (5, 21):
    for mk in ("us", "uk", "fx"):
        obs = []
        for l in L:
            d0 = datetime.strptime(l["date"], "%Y-%m-%d %H:%M").date()
            v = spread(l, mk, d0, h)
            if v is not None: obs.append((d0, v))
        for trial, sign in (("as intended", 1), ("reversed", -1)):
            cost = 0.002 if mk != "fx" else 0.0005
            x = [(d, sign * v - cost) for d, v in obs]
            m = st.mean(v for _, v in x)
            h1 = [v for d, v in x if d.month <= 3]; h2 = [v for d, v in x if d.month >= 4]
            months = sorted({d.month for d, _ in x}); byM = {mm: [v for d, v in x if d.month == mm] for mm in months}
            bs = []
            for _ in range(5000):
                pick = [v for mm in random.choices(months, k=len(months)) for v in byM[mm]]
                bs.append(st.mean(pick))
            bs.sort(); lo, hi = bs[125], bs[4874]
            ok = m > 0 and st.mean(h1) > 0 and st.mean(h2) > 0 and lo > 0
            print(f"  {h:2d}d {mk} {trial:12s} mean {m*100:+6.2f}%  pos {sum(v>0 for _,v in x):2d}/{len(x)}  "
                  f"Jan-Mar {st.mean(h1)*100:+6.2f}%  Apr-Jun {st.mean(h2)*100:+6.2f}%  95% [{lo*100:+.2f}, {hi*100:+.2f}]  {'PASS' if ok else 'fail'}")
