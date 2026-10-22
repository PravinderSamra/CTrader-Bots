"""Daily Systems A + D: exit at the daily close vs exit after the reopen (pre-registered 22 Oct 2026)."""
import csv, sys, statistics as st
from datetime import datetime, timezone, timedelta, date
R0 = "/home/user/CTrader-Bots/Vanessa Algo Bots/research/data/factory_h1"
MK = {"us500": "US500", "nas100": "US100", "us30": "US30", "ger40": "GER40", "xauusd": "XAU"}
N, COST, SWAP = 13000.0, 0.00025, 0.05 / 365
START, END = date(2020, 11, 8), date(2023, 12, 31)
if len(sys.argv) > 1 and sys.argv[1] == "all": START, END = date(2014, 9, 1), date(2026, 10, 13)

def nyoff(d):
    mar = date(d.year, 3, 1); s = mar + timedelta(days=(6 - mar.weekday()) % 7 + 7)
    nov = date(d.year, 11, 1); e = nov + timedelta(days=(6 - nov.weekday()) % 7)
    return 4 if s <= d < e else 5

def days(m):
    D = {}
    for r in csv.DictReader(open(f"{R0}/{m}_h1.csv")):
        t = datetime.fromtimestamp(int(r["timestamp_ms"]) / 1000, timezone.utc).replace(tzinfo=None)
        ny = t - timedelta(hours=nyoff(t.date()))
        sess = (ny + timedelta(hours=7)).date()          # 17:00 New York rollover
        if sess.weekday() >= 5: continue
        o, h, l, c = (float(r[k]) for k in ("open", "high", "low", "close"))
        d = D.setdefault(sess, {"bars": [], "c16": None}); d["bars"].append((t, o, h, l, c))
        if ny.hour == 15: d["c16"] = c
    out = []
    for s in sorted(D):
        b = D[s]["bars"]
        if len(b) < 5: continue
        # order price: open of the 2nd H1 bar of the session (~1 hour after the daily open)
        out.append(dict(d=s, o=b[0][1], h=max(x[2] for x in b), l=min(x[3] for x in b), c=b[-1][4],
                        px=b[1][1] if len(b) > 1 else b[0][4], c16=D[s]["c16"]))
    return out

def sma(a, i, n): return sum(a[i - n + 1:i + 1]) / n
def rsi2(c, keep=None):
    r = [50.0] * len(c); g = l = None; G = [0] * len(c); Lw = [0] * len(c)
    for i in range(1, len(c)):
        ch = c[i] - c[i - 1]; up, dn = max(ch, 0), max(-ch, 0)
        if g is None: g, l = up, dn
        else: g = (g + up) / 2; l = (l + dn) / 2
        r[i] = 100 if l == 0 else 100 - 100 / (1 + g / l); G[i], Lw[i] = g, l
    if keep is not None: keep.extend([G, Lw])
    return r

def run(m, at_close):
    B = days(m); C = [b["c"] for b in B]; GL = []; R = rsi2(C, GL)
    TR = [B[0]["h"] - B[0]["l"]] + [max(B[i]["h"], C[i-1]) - min(B[i]["l"], C[i-1]) for i in range(1, len(B))]
    trades = []
    for sysn in "AD":
        i = 210; pos = None
        while i < len(B) - 1:
            if pos is None:
                ok = False
                if sysn == "A":
                    s5 = sma(C, i, 5); dev = abs(C[i] - s5)
                    avg = sum(abs(C[k] - sma(C, k, 5)) for k in range(i - 20, i)) / 20
                    ok = C[i] < s5 and dev > 2.5 * avg and C[i] > sma(C, i, 200)
                else:
                    ok = C[i] > sma(C, i, 200) and R[i] < 20
                if ok and START <= B[i + 1]["d"] <= END:
                    e = B[i + 1]["px"]; atr = sum(TR[i - 19:i + 1]) / 20
                    pos = dict(sig=i, e=e, stop=e - 3 * atr, ent=i + 1)
                i += 1; continue
            j = i  # day being evaluated (position open)
            if j >= pos["ent"] and B[j]["l"] <= pos["stop"]:
                x = min(pos["stop"], B[j]["o"]) if j > pos["ent"] else pos["stop"]; xd = j
            else:
                held = j - pos["sig"]; early = False
                if at_close == "16" and B[j]["c16"] is not None:
                    p = B[j]["c16"]; s5 = (sum(C[j - 4:j]) + p) / 5
                    ch = p - C[j - 1]; g = (GL[0][j - 1] + max(ch, 0)) / 2; l = (GL[1][j - 1] + max(-ch, 0)) / 2
                    r16 = 100 if l == 0 else 100 - 100 / (1 + g / l)
                    early = (p > s5 or held >= 4) if sysn == "A" else r16 > 70
                    if early: x, xd = p, j
                if not early:
                    ex = (C[j] > sma(C, j, 5) or held >= 4) if sysn == "A" else R[j] > 70
                    if not ex: i += 1; continue
                    if at_close is True: x, xd = C[j], j
                    else: x, xd = B[j + 1]["px"], j + 1
            nights = (B[xd]["d"] - B[pos["ent"]]["d"]).days
            pnl = N * ((x - pos["e"]) / pos["e"] - COST - SWAP * nights)
            trades.append((B[xd]["d"], pnl, sysn, m)); pos = None; i = xd + 1
    return trades

for label, ac in (("baseline: exit after reopen", False), ("exit at 17:00 NY close", True),
                  ("exit 15:55 NY (8:55pm UK)", "16")):
    T = sorted(t for m in MK for t in run(m, ac))
    pn = [t[1] for t in T]; eq = 0; pk = 0; dd = 0
    for p in pn: eq += p; pk = max(pk, eq); dd = max(dd, pk - eq)
    by = {s: sum(t[1] for t in T if t[2] == s) for s in "AD"}
    print(f"{label:30s} trades {len(T)} net ${sum(pn):9,.0f}  win {sum(p>0 for p in pn)/len(pn):.0%}  "
          f"avg ${st.mean(pn):6.0f}  maxDD ${dd:7,.0f}  A ${by['A']:8,.0f}  D ${by['D']:8,.0f}")
