"""Omar (MMBB trader, Chart Fanatics) market maker model + optimal trade entry (OTE), coded mechanically. Screening only.
Sell side (buys = same code on inverted prices):
  1. Key level: previous day's high (PDH). Day = 22:00 UTC rollover. The day must open within 0.5 x ADR(5) of PDH.
  2. Bias filter (variant): 'none', 'week' = previous week closed down, 'sma' = previous daily close below SMA20.
  3. 15-minute bars, setups only 07:00-16:00 UK. Price trades above PDH (the sweep). H = high since the sweep.
  4. Breaker / change of state: a 15m body close below the last confirmed 15m swing low (3-bar) formed before H.
  5. Leg low LL = lowest low since the break. Sell limit at LL + f x (H - LL), f = 0.5 or 0.62 (OTE).
     Stop at LL + 0.9 x (H - LL) (his 90% stop), target LL (the 0 level, his initial TP).
     Break-even once a 15m close is at or below the 0.2 level. A new high above H cancels the order.
  6. One trade per day per side. Flat 21:00 UK."""
import csv
import glob
import statistics as st
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

UK = ZoneInfo("Europe/London")
ROOT = "/home/user/CTrader-Bots"
COST = {"EURUSD": 0.00007, "NAS100": 1.5, "XAUUSD": 0.35}


def m15(rows):
    out = []
    for t, o, h, l, c in rows:
        k = t.replace(minute=t.minute - t.minute % 15, second=0)
        if out and out[-1][0] == k:
            out[-1][2] = max(out[-1][2], h); out[-1][3] = min(out[-1][3], l); out[-1][4] = c
        else:
            out.append([k, o, h, l, c])
    return [tuple(x) for x in out]


def load(m):
    rows = []
    if m == "NAS100":
        for r in csv.DictReader(open(f"{ROOT}/US30 London Range Breakout/data/NAS100/nas100_m5.csv")):
            rows.append((datetime.fromtimestamp(int(r["timestamp_ms"]) / 1000, timezone.utc),
                         float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"])))
    else:
        pat = (f"{ROOT}/Vanessa Algo Bots/research/data/eurusd_m5/EURUSD_M_5_*.csv" if m == "EURUSD"
               else f"{ROOT}/XAUUSD historical Pricing data/data/XAUUSD_M_1_*.csv")
        for f in sorted(glob.glob(pat)):
            for r in csv.DictReader(open(f)):
                t = datetime.strptime(r["datetime"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                rows.append((t, float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"])))
    return m15(rows)


def dkey(t):
    return (t + timedelta(hours=2)).date()


def run(bars, cost, bias, f, sl=0.9):
    days = defaultdict(lambda: [None, -1e18, 1e18, None])   # o h l c
    order = []
    for t, o, h, l, c in bars:
        k = dkey(t)
        d = days[k]
        if d[0] is None:
            d[0] = o; order.append(k)
        d[1] = max(d[1], h); d[2] = min(d[2], l); d[3] = c
    di = {k: i for i, k in enumerate(order)}
    trades = []
    st_ = None
    pos = None
    cur = None
    sw_lows = []
    for i, (t, o, h, l, c) in enumerate(bars):
        k = dkey(t)
        uk = t.astimezone(UK)
        if pos:
            if h >= pos["stop"]:
                trades.append((t, (pos["e"] - pos["stop"] - cost) / pos["r"])); pos = None
            elif l <= pos["tp"]:
                trades.append((t, (pos["e"] - pos["tp"] - cost) / pos["r"])); pos = None
            else:
                if c <= pos["be_lvl"]:
                    pos["stop"] = min(pos["stop"], pos["e"])
                if uk.hour >= 21:
                    trades.append((t, (pos["e"] - c - cost) / pos["r"])); pos = None
        if k != cur:
            cur = k; st_ = None; sw_lows = []
            j = di[k]
            ok = False
            if j >= 6:
                p = days[order[j - 1]]
                adr = st.mean(days[order[x]][1] - days[order[x]][2] for x in range(j - 5, j))
                ok = abs(p[1] - days[k][0]) <= 0.5 * adr and days[k][0] < p[1]
                if ok and bias == "week":
                    wk = [days[order[x]] for x in range(max(0, j - 10), j)
                          if order[x].isocalendar()[1] == (k - timedelta(days=7)).isocalendar()[1]]
                    ok = bool(wk) and wk[-1][3] < wk[0][0]
                if ok and bias == "both" and j >= 21:
                    wk = [days[order[x]] for x in range(max(0, j - 10), j)
                          if order[x].isocalendar()[1] == (k - timedelta(days=7)).isocalendar()[1]]
                    ok = bool(wk) and wk[-1][3] < wk[0][0] and p[3] < st.mean(days[order[x]][3] for x in range(j - 20, j))
                elif ok and bias == "both":
                    ok = False
                if ok and bias == "sma" and j >= 21:
                    ok = p[3] < st.mean(days[order[x]][3] for x in range(j - 20, j))
                elif ok and bias == "sma":
                    ok = False
            st_ = {"pdh": p[1], "H": None, "brk": False, "LL": None, "done": False} if ok else None
        if i >= 2:
            a, b, cc = bars[i - 2], bars[i - 1], bars[i]
            if b[3] < a[3] and b[3] < cc[3]:
                sw_lows.append((b[0], b[3]))
        if not st_ or st_["done"] or pos:
            continue
        s = st_
        in_win = 7 <= uk.hour < 16
        if s["brk"] and s["LL"] is not None:
            # pending sell limit from the leg so far
            rng = s["H"] - s["LL"]
            ent = s["LL"] + f * rng
            if h > s["H"]:
                s["brk"] = False; s["LL"] = None; s["H"] = h
            elif h >= ent and in_win:
                e = max(ent, o)
                stop = s["LL"] + sl * rng
                if e < stop:
                    pos = {"e": e, "stop": stop, "tp": s["LL"], "r": stop - e, "be_lvl": s["LL"] + 0.2 * rng}
                    s["done"] = True
                    if h >= stop:
                        trades.append((t, (e - stop - cost) / pos["r"])); pos = None
                continue
            else:
                s["LL"] = min(s["LL"], l)
                continue
        if s["H"] is None:
            if h > s["pdh"] and in_win:
                s["H"] = h
            continue
        if h > s["H"]:
            s["H"] = h
            continue
        if not in_win:
            continue
        prior = [lv for tt, lv in sw_lows if tt < t and lv < s["H"]]
        if prior and c < prior[-1] and c < o:
            s["brk"] = True; s["LL"] = l
    return trades


def inv(b):
    return [(t, -o, -l, -h, -c) for t, o, h, l, c in b]


def summ(name, tr):
    if not tr:
        print(f"{name:34s} no trades"); return
    rs = [r for _, r in tr]
    yr = defaultdict(float)
    for t, r in tr:
        yr[t.year] += r
    print(f"{name:34s} n={len(rs):4d} win={sum(r > 0 for r in rs) / len(rs):4.0%} avg={st.mean(rs):+.2f}R tot={sum(rs):+7.1f}R  "
          + " ".join(f"{y % 100:02d}:{v:+.0f}" for y, v in sorted(yr.items())))


if __name__ == "__main__":
    for m in sys.argv[1:] or ["EURUSD", "NAS100", "XAUUSD"]:
        b = load(m)
        print(f"== {m} {b[0][0]:%Y-%m} .. {b[-1][0]:%Y-%m}")
        ib = inv(b)
        for bias in ("none", "week", "sma"):
            for f in (0.5, 0.62):
                sh = run(b, COST[m], bias, f)
                lg = run(ib, COST[m], bias, f)
                summ(f"{bias} f={f} sells", sh)
                summ(f"{bias} f={f} buys", lg)
                summ(f"{bias} f={f} both", sorted(sh + lg))
