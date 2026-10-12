"""Weinstein stage analysis as a weekly trend filter (Ted Zack, Chart Fanatics). Screening only.
Weekly closes (Friday). Stage 2 = close > SMA10 > SMA30 > SMA40 and SMA30 rising vs 4 weeks ago -> long.
Stage 4 = mirror -> short (optional). Otherwise flat. Decide at the Friday close, trade at the next week's open
(approximated by that close). Costs: spread per switch (in % of price) + swap per year held (long / short)."""
import csv
import glob
import statistics as st
from datetime import datetime, timezone

D = "/home/user/CTrader-Bots"
S = "/tmp/claude-0/-home-user-CTrader-Bots/05dd4dd7-22e7-57bf-8cec-d6a0c9610eea/scratchpad"


def weekly(rows):
    wk = {}
    for t, c in rows:
        k = t.isocalendar()[:2]
        wk[k] = (t, c)
    return [wk[k] for k in sorted(wk)]


def nas():
    rows = []
    for r in csv.DictReader(open(f"{D}/Vanessa Algo Bots/research/data/nas100_m30/nas100_m30_2021_2023.csv")):
        rows.append((datetime.fromtimestamp(int(r["timestamp_ms"]) / 1000, timezone.utc), float(r["close"])))
    last = rows[-1][0]
    for r in csv.DictReader(open(f"{D}/US30 London Range Breakout/data/NAS100/nas100_m5.csv")):
        t = datetime.fromtimestamp(int(r["timestamp_ms"]) / 1000, timezone.utc)
        if t > last: rows.append((t, float(r["close"])))
    return weekly(rows)


def iso(pattern):
    rows = []
    for f in sorted(glob.glob(pattern)):
        for line in open(f):
            if line[0] != "2": continue
            p = line.split(",")
            if p[0][14:16] not in ("00", "30"): continue  # sample twice an hour, enough for weekly closes
            rows.append((datetime.strptime(p[0][:19], "%Y-%m-%dT%H:%M:%S"), float(p[4])))
    return weekly(rows)


def sma(x, n, i):
    return sum(x[i - n + 1:i + 1]) / n


def run(w, spread_pct, swap_long, swap_short, shorts):
    c = [x[1] for x in w]
    pos, eq, peak, dd, trades, wk_in, out = 0, 1.0, 1.0, 0.0, 0, 0, []
    for i in range(44, len(c)):
        if pos:
            r = pos * (c[i] / c[i - 1] - 1) - (swap_long if pos > 0 else swap_short) / 52
            eq *= 1 + r; wk_in += 1
        peak = max(peak, eq); dd = max(dd, 1 - eq / peak)
        s10, s30, s40 = sma(c, 10, i), sma(c, 30, i), sma(c, 40, i)
        rising = s30 > sma(c, 30, i - 4)
        want = 0
        if c[i] > s10 > s30 > s40 and rising: want = 1
        elif shorts and c[i] < s10 < s30 < s40 and not rising: want = -1
        if want != pos:
            eq *= 1 - spread_pct * (abs(want - pos) > 0); trades += (want != 0)
            pos = want
        out.append((w[i][0], eq))
    bh = c[-1] / c[44] - 1
    return eq - 1, dd, trades, wk_in / (len(c) - 44), bh, w[44][0].date(), w[-1][0].date()


sets = {
    "NAS100": (nas(), 0.00006, 0.082, -0.03),
    "Gold": (iso(f"{D}/XAUUSD historical Pricing data/data/XAUUSD_M_1_*.csv"), 0.0001, 0.06, 0.0),
    "EURUSD": (iso(f"{S}/eurusd_m5/data/XAUUSD_M_5_*.csv"), 0.00005, 0.02, 0.0),
}
for name, (w, sp, sl, ss) in sets.items():
    for shorts in (False, True):
        tot, dd, n, inmkt, bh, a, b = run(w, sp, sl, ss, shorts)
        print(f"{name:7s} {'long+short' if shorts else 'long only '} {a}..{b}: {tot:+6.1%} maxDD {dd:5.1%} "
              f"entries {n:2d} in market {inmkt:4.0%} | buy&hold {bh:+6.1%}")
