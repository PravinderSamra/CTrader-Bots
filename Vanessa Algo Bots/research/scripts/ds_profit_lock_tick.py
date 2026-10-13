"""Profit-lock test on the bot's OWN 2020-23 tick-backtest trades (exact baseline = +$14,479).
Each trade (weekend split legs re-joined) is replayed day by day on daily bars (Pepperstone D1, session = bar open + 5h)
between its entry and its real exit. A switch can only close a trade EARLIER than the real exit:
  BE k: once a day's high >= first entry + k x ATR(20), the stop moves to the first entry price (from the next day).
  TRAIL k: stop = highest daily close since entry - k x ATR(20) (from the next day), never loosens.
Stop hit on a day: exit at the stop, or at the open if the day opened beyond it. The entry day and the real exit day
are not checked (the bot trades ~60 min after the open). Swap is cut pro rata to the days actually held."""
import csv, re, statistics as st, sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone, date

UP = "/root/.claude/uploads/05dd4dd7-22e7-57bf-8cec-d6a0c9610eea/3e7ac88f-DS_tick_data_20-23_log.txt"
D = "/home/user/CTrader-Bots/Vanessa Algo Bots/research/data/d1_2019_2023"
MAP = {"US500.cash": "us500", "US100.cash": "nas100", "US30.cash": "us30", "GER40.cash": "ger40", "XAUUSD": "xauusd"}


def bars(m):
    out = {}
    rows = []
    for r in csv.DictReader(open(f"{D}/{m}_d1.csv")):
        t = datetime.fromtimestamp(int(r["timestamp_ms"]) / 1000, timezone.utc)
        rows.append(((t + timedelta(hours=5)).date(), float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"])))
    # merge rows mapping to the same session date (Sunday stub + Monday)
    m2 = []
    for x in rows:
        if m2 and (m2[-1][0] == x[0] or x[0].weekday() == 6 or m2[-1][0].weekday() == 6 and x[0].weekday() == 0):
            p = m2.pop(); m2.append((x[0] if x[0].weekday() != 6 else p[0], p[1], max(p[2], x[2]), min(p[3], x[3]), x[4]))
        else:
            m2.append(x)
    atr = {}
    for i in range(21, len(m2)):
        atr[m2[i][0]] = st.mean(max(m2[j][2], m2[j - 1][4]) - min(m2[j][3], m2[j - 1][4]) for j in range(i - 19, i + 1))
    return m2, atr


def load_trades():
    legs = []
    for line in open(UP):
        m = re.search(r"Info \| H\|(.*)", line)
        if not m: continue
        f = m.group(1).split("|")
        legs.append(dict(lab=f[1], sym=f[2], d0=date.fromisoformat(f[3]), d1=date.fromisoformat(f[4]), u=float(f[5]),
                         e=float(f[6]), x=float(f[7]), gross=float(f[8]), swap=float(f[9]), net=float(f[11])))
    legs.sort(key=lambda l: (l["lab"], l["sym"], l["d0"]))
    chains = []
    for l in legs:
        c = chains[-1] if chains else None
        if c and c[-1]["lab"] == l["lab"] and c[-1]["sym"] == l["sym"] and c[-1]["d1"].weekday() == 4 and 0 < (l["d0"] - c[-1]["d1"]).days <= 3:
            c.append(l)
        else:
            chains.append([l])
    return chains


def replay(chain, B, A, mode, k):
    days, idx = B
    e0 = chain[0]["e"]; d0 = chain[0]["d0"]
    prev = [d for d in idx if d < d0]
    if not prev: return sum(l["net"] for l in chain), chain[-1]["d1"]
    a = A.get(prev[-1])
    if a is None: return sum(l["net"] for l in chain), chain[-1]["d1"]
    stop = -1e18; hc = e0; done = 0.0
    for li, l in enumerate(chain):
        for d in sorted(x for x in idx if l["d0"] <= x <= l["d1"]):
            o, h, lo, c = idx[d]
            if d != l["d0"] and d != chain[-1]["d1"] and d != l["d1"] and lo <= stop:
                px = min(o, stop) if o < stop else stop
                held = max(1, (d - l["d0"]).days); full = max(1, (l["d1"] - l["d0"]).days)
                return done + l["u"] * (px - l["e"]) + l["swap"] * held / full, d
            hc = max(hc, c)
            if mode == "be" and h >= e0 + k * a: stop = max(stop, e0)
            if mode == "trail": stop = max(stop, hc - k * a)
        done += l["net"]
    return done, chain[-1]["d1"]


if __name__ == "__main__":
    data = {}
    for s, m in MAP.items():
        rows, atr = bars(m); data[s] = ({r[0]: r[1:] for r in rows}, atr)
    chains = load_trades()
    print(f"{len(chains)} trades (weekend legs joined), {sum(len(c) for c in chains)} legs")
    for name, mode, k in [("baseline (live)", None, 0), ("BE at 1 ATR  [pre-registered]", "be", 1.0), ("TRAIL 2 ATR  [pre-registered]", "trail", 2.0),
                          ("sens: BE 0.5 ATR", "be", 0.5), ("sens: BE 1.5 ATR", "be", 1.5), ("sens: BE 2 ATR", "be", 2.0),
                          ("sens: TRAIL 1.5 ATR", "trail", 1.5), ("sens: TRAIL 3 ATR", "trail", 3.0)]:
        res = []
        for c in chains:
            B = data[c[0]["sym"]]
            if mode is None: res.append((c[-1]["d1"], sum(l["net"] for l in c)))
            else:
                p, d = replay(c, (None, B[0]), B[1], mode, k); res.append((d, p))
        res.sort(); eq = pk = dd = 0.0; daily = defaultdict(float)
        for d, p in res: eq += p; pk = max(pk, eq); dd = max(dd, pk - eq); daily[d] += p
        by = defaultdict(float)
        for d, p in res: by[d.year] += p
        n = len(res); w = sum(p > 0 for _, p in res) / n
        print(f"{name:32s} win={w:4.0%} total=${sum(p for _, p in res):+8,.0f} maxDD=${dd:6,.0f} worst trade=${min(p for _, p in res):+6,.0f}  "
              + " ".join(f"{y}:{v:+6,.0f}" for y, v in sorted(by.items())))
