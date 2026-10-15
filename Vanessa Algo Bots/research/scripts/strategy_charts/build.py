import csv, re, sys, statistics as st
from datetime import datetime, timezone, timedelta, date
sys.path.insert(0, "/tmp/claude-0/-home-user-CTrader-Bots/05dd4dd7-22e7-57bf-8cec-d6a0c9610eea/scratchpad/charts")
sys.path.insert(0, "/home/user/CTrader-Bots/Vanessa Algo Bots/research/ssrn")
from svgc import *
import fomc_drift as FD
V = "/home/user/CTrader-Bots/Vanessa Algo Bots"
UP = "/root/.claude/uploads/05dd4dd7-22e7-57bf-8cec-d6a0c9610eea/"
MON = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()

def hlines(f, label):
    out = []
    for l in open(UP + f):
        if "Info | H|" not in l: continue
        x = l.split("Info | ")[1].strip().split("|")
        if label not in x[2]: continue
        out.append(x)
    return out

def yearfrac(d):
    return d.year + (d.timetuple().tm_yday - 1) / 365.25

def equity(rows, dcol, fmt):
    pts = []
    for x in rows:
        d = datetime.strptime(x[dcol], fmt); pts.append((d, float(x[-1])))
    pts.sort(); cum = 0; xs = []; ys = []
    for d, v in pts:
        cum += v; xs.append(yearfrac(d)); ys.append(cum)
    return xs, ys

def yticks(xs):
    return [(y, str(y)) for y in range(int(xs[0]) + 1, int(xs[-1]) + 1)]

money = lambda v: ("−$" if v < 0 else "$") + f"{abs(v):,.0f}"

def inject(path, key, html, before):
    s = open(path).read()
    s = re.sub(rf"\n?<!--CHARTS:{key}-->.*?<!--/CHARTS:{key}-->\n?", "\n", s, flags=re.S)
    i = s.index(before)
    s = s[:i] + f"<!--CHARTS:{key}-->\n{html}\n<!--/CHARTS:{key}-->\n" + s[i:]
    open(path, "w").write(s)

# ---------- Bollinger ----------
def daily(m):
    rows = []
    for r in csv.DictReader(open(f"{V}/research/data/factory_d1/{m}_d1.csv")):
        t = datetime.fromtimestamp(int(r["timestamp_ms"]) / 1000, timezone.utc)
        sess = (t + timedelta(hours=5)).date()
        if sess.weekday() >= 5: continue
        rows.append((sess, float(r["open"]), float(r["close"])))
    return rows

us = daily("us500")
C = [r[2] for r in us]
def sma(i, n): return sum(C[i-n+1:i+1]) / n
def sd(i, n):
    m = sma(i, n); return (sum((c-m)**2 for c in C[i-n+1:i+1]) / n) ** 0.5
lo_i = next(i for i, r in enumerate(us) if r[0] >= date(2025, 10, 20))
hi_i = next(i for i, r in enumerate(us) if r[0] >= date(2025, 12, 10))
idx = list(range(lo_i, hi_i + 1))
close = [C[i] for i in idx]; mid = [sma(i, 20) for i in idx]; band = [sma(i, 20) - 2.5 * sd(i, 20) for i in idx]
pos = {us[i][0]: k for k, i in enumerate(idx)}
sig = [us[i][0] for i in idx if C[i] < sma(i, 20) - 2.5 * sd(i, 20)]
print("BB signals in window", sig)
k_in = pos[date(2025, 11, 21)]; k_re = pos[date(2025, 11, 24)]; k_out = pos[date(2025, 11, 28)]
xt = [(k, f"{us[i][0].day} {MON[us[i][0].month-1]}") for k, i in enumerate(idx) if us[i][0].weekday() == 0 and k % 2 == 0]
svg1 = chart([dict(xs=list(range(len(idx))), ys=close, color=BLUE, width=2),
              dict(xs=list(range(len(idx))), ys=mid, color=GREY, width=1.5, dash="5 4"),
              dict(xs=list(range(len(idx))), ys=band, color=ORANGE, width=2)],
             xticks=xt, title="US500 Bollinger example",
             bands=[(k_in + 0.15, k_re - 0.15, "weekend: flat")],
             markers=[(k_in, 6539.5, "buy", "Buy 6,540"), (k_re, 6638.3, "dot", "Reopen 6,638"),
                      (k_out, 6818.9, "sell", "Sell 6,819")])
f1 = figure("Example trade: US500, November 2025", svg1,
    "On 20 November US500 closed below its lower Bollinger band. The bot bought at the next open, closed for the weekend on Friday, "
    "reopened on Monday and sold 5 trading days after the entry: +$272 at $200 per R (+$136 at the live $100).",
    legend([("Daily close", BLUE, 0), ("Lower band (20-day average − 2.5 × std dev)", ORANGE, 0), ("20-day average", GREY, 1)]))
rows = hlines("4d460163-log.txt", "BOLL")
xs, ys = equity(rows, 6, "%Y-%m-%d %H:%M")
svg2 = chart([dict(xs=xs, ys=ys, color=BLUE, width=2)], xticks=yticks(xs), yfmt=money, zero=True,
             title="Bollinger backtest growth", hlines=[(0, "")])
f2 = figure("Backtest growth: all 9 indices, 2021 – Oct 2026", svg2,
    f"Running total of closed profit in your cTrader backtest (v1.3, flat over weekends, $200 per R, M1 bars, commission 30): "
    f"{money(ys[-1])} after {len(rows)} trade pieces. Live at $100 per R the dollar amounts halve.")
inject(f"{V}/bots/07_Factory/strategy.html", "boll", f1 + "\n" + f2, "<h2>Size</h2>")

# ---------- Daily Systems ----------
rows = hlines("0b1c53ca-log.txt", "DSY")
xs, ys = equity(rows, 5, "%Y-%m-%d")
xa, ya = equity([r for r in rows if r[2] == "DSY-A"], 5, "%Y-%m-%d")
xd, yd = equity([r for r in rows if r[2] == "DSY-D"], 5, "%Y-%m-%d")
svg3 = chart([dict(xs=xs, ys=ys, color=BLUE, width=2), dict(xs=xd, ys=yd, color=ORANGE, width=2, dash="6 4"),
              dict(xs=xa, ys=ya, color=AQUA, width=2, dash="2 3")],
             xticks=yticks(xs), yfmt=money, zero=True, title="Daily Systems backtest growth", hlines=[(0, "")])
f3 = figure("Backtest growth: 2024 – Oct 2026 (tick data)", svg3,
    f"Running total of closed profit in your v1.4 tick-data backtest ($13k per position, flat over weekends, commission 30): "
    f"{money(ys[-1])} in total, of which system D {money(yd[-1])} and system A {money(ya[-1])}. The dip in early "
    f"August 2024 includes the day the daily guard closed everything (5 Aug).",
    legend([("Both systems", BLUE, 0), ("D: RSI(2)", ORANGE, 1), ("A: mean reversion", AQUA, 1)]))
yr = {}
for x in rows: yr[x[5][:4]] = yr.get(x[5][:4], 0) + float(x[-1])
bars = "".join(f'<tr><td>{y}{" (to Oct)" if y=="2026" else ""}</td><td style="text-align:right">{money(v)}</td></tr>' for y, v in sorted(yr.items()))
f3 += f'<table style="width:auto;min-width:260px"><tr><th>Year</th><th>Profit</th></tr>{bars}</table>'
inject(f"{V}/bots/05_Daily_Systems/STRATEGY.html", "dsy", f3, '<p class="sub">Charts are an illustration')

# ---------- FOMC ----------
h1 = {}
for r in csv.DictReader(open(f"{V}/research/data/factory_h1/nas100_h1.csv")):
    t = datetime.fromtimestamp(int(r["timestamp_ms"]) / 1000, timezone.utc).replace(tzinfo=None)
    h1[t] = float(r["open"])
def path(d1):
    start = datetime(d1.year, d1.month, d1.day, 14) + timedelta(hours=FD.ny_offset(d1))
    if start not in h1: return None
    p0 = h1[start]; out = []; last = p0
    for k in range(25):
        t = start + timedelta(hours=k)
        if t in h1: last = h1[t]
        out.append((last / p0 - 1) * 100)
    return out
meet = {date.fromisoformat(s) for s in FD.MEET}
mp = [p for p in (path(d) for d in sorted(meet)) if p]
first = min(meet); others = []
d = first
while d <= date(2026, 10, 1):
    if d.weekday() <= 3 and d not in meet:
        p = path(d)
        if p: others.append(p)
    d += timedelta(days=1)
avg = lambda P: [st.mean(p[k] for p in P) for k in range(25)]
am, ao = avg(mp), avg(others)
print("FOMC n", len(mp), "others", len(others), "end", am[-1], ao[-1])
lab = {0: "Buy 14:00 meeting day 1", 6: "20:00", 12: "02:00", 18: "08:00", 24: "Sell 13:58 (statement 14:00)"}
svg5 = chart([dict(xs=list(range(25)), ys=am, color=BLUE, width=2.5), dict(xs=list(range(25)), ys=ao, color=GREY, width=2, dash="5 4")],
             xticks=[(k, v) for k, v in lab.items()], yfmt=lambda v: f"{v:+.2f}%", zero=True, hlines=[(0, "")],
             title="Average US100 move before the Fed", pad=(64, 30, 24, 34))
f5 = figure("Why it works: the average US100 move in the 24 hours before the Fed (2014 – 2026)", svg5,
    f"Blue: average of the {len(mp)} scheduled Fed meetings, measured from 14:00 New York on meeting day 1 (+{am[-1]:.2f}% by the statement). "
    f"Grey: the same 24 hours on every other Monday–Thursday ({len(others)} days, {ao[-1]:+.2f}%). Times are New York; before costs.",
    legend([("Fed meeting days", BLUE, 0), ("All other days", GREY, 1)]))
rows = hlines("95a5c5b9-log.txt", "FOMC")
xs, ys = equity(rows, 5, "%Y-%m-%d %H:%M")
svg6 = chart([dict(xs=xs, ys=ys, color=BLUE, width=2)], xticks=yticks(xs), yfmt=money, zero=True, hlines=[(0, "")],
             title="FOMC backtest growth")
f6 = figure("Backtest growth: 2021 – Oct 2026", svg6,
    f"Running total of closed profit in your cTrader backtest (US100 + US500, $20k each, M1 bars, commission 30): "
    f"{money(ys[-1])} from {len(rows)} trades. Each step is one Fed meeting.")
inject(f"{V}/bots/08_FOMC_Drift/strategy.html", "fomc", f5, "<h2>The rules</h2>")
inject(f"{V}/bots/08_FOMC_Drift/strategy.html", "fomc2", f6, "<h2>Running it</h2>")
