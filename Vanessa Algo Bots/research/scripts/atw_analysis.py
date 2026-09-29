"""Add To Winner analysis from Trades-Only logs.

Each log line of interest looks like:
  T|open time|close time|label|side|volume|entry|net P/L|pips|reason|balance
Main trades have labels like ORBV_US100.cash_20210104; adds end in _ADD1.

Usage (from the repo root):
  python3 "Vanessa Algo Bots/research/scripts/atw_analysis.py" CONTROL.log RUN1.log RUN2.log ...
The first file is the control (Add To Winner off). Writes a Markdown report next to the logs.
"""
import math
import random
import re
import statistics as st
import sys
from collections import OrderedDict, defaultdict
from pathlib import Path

START_BALANCE = 100000.0
FTMO_FLOOR = 90000.0
CURRENT_BALANCE = 96952.19
RISK_NOW, RISK_LATER = 300.0, 500.0
T_RE = re.compile(r"T\|([\d\- :]+)\|([\d\- :]+)\|([^|]+)\|(\w+)\|([\d.]+)\|([\d.]+)\|(-?[\d.]+)\|(-?[\d.]+)\|(\w+)\|(-?[\d.]+)")


def load(path):
    trades = []
    for line in Path(path).read_text(errors="replace").splitlines():
        m = T_RE.search(line)
        if m:
            label = m.group(3)
            day = re.search(r"_(\d{8})", label).group(1)
            trades.append({"open": m.group(1), "close": m.group(2), "label": label, "day": day,
                           "is_add": "_ADD" in label, "pl": float(m.group(7)), "reason": m.group(9)})
    trades.sort(key=lambda t: t["close"])
    return trades


def daily(trades):
    d = OrderedDict()
    for t in sorted(trades, key=lambda t: t["day"]):
        d[t["day"]] = d.get(t["day"], 0.0) + t["pl"]
    return d


def max_drawdown(pls):
    bal = peak = START_BALANCE
    worst = 0.0
    for p in pls:
        bal += p
        peak = max(peak, bal)
        worst = max(worst, peak - bal)
    return worst


def streaks(day_pls):
    out, c = [], 0
    for v in day_pls:
        if v <= 0:
            c += 1
        else:
            if c:
                out.append(c)
            c = 0
    if c:
        out.append(c)
    return out


def worst_run_cost(day_pls):
    """Largest peak-to-trough loss over consecutive days (same as drawdown on daily totals)."""
    return max_drawdown(day_pls)


BLOCK = 10   # resample blocks of 10 consecutive trading days, so real losing streaks stay intact


def _path(rng, vals, horizon):
    """One simulated future of `horizon` trading days built from random blocks of real consecutive days."""
    out = []
    while len(out) < horizon:
        i = rng.randrange(0, max(1, len(vals) - BLOCK))
        out.extend(vals[i:i + BLOCK])
    return out[:horizon]


def monte_carlo(day_pls, scale, horizon_days, start_balance, floor, n=5000, seed=1):
    """Probability of falling to `floor` within `horizon_days` trading days (block bootstrap)."""
    rng = random.Random(seed)
    vals = [v * scale for v in day_pls]
    hits = 0
    for _ in range(n):
        bal = start_balance
        for v in _path(rng, vals, horizon_days):
            bal += v
            if bal <= floor:
                hits += 1
                break
    return hits / n


def mc_drawdown(day_pls, scale, horizon_days, dd_pct, n=5000, seed=2):
    rng = random.Random(seed)
    vals = [v * scale for v in day_pls]
    limit = START_BALANCE * dd_pct / 100
    hits = 0
    for _ in range(n):
        bal = peak = START_BALANCE
        for v in _path(rng, vals, horizon_days):
            bal += v
            peak = max(peak, bal)
            if peak - bal >= limit:
                hits += 1
                break
    return hits / n


def main(paths):
    runs = OrderedDict((Path(p).stem, load(p)) for p in paths)
    names = list(runs)
    ctrl = runs[names[0]]
    out = []
    P = out.append
    P("# Add To Winner — NAS100 analysis\n")
    P(f"Runs: {', '.join(names)}. First run is the control. Figures at the backtest risk (${RISK_NOW:.0f}).\n")

    # Totals and drawdown
    P("## Totals\n")
    P("| Run | Positions | Net profit | vs control | Profit from adds | Max balance DD | Worst day |")
    P("|---|---|---|---|---|---|---|")
    ctrl_net = sum(t["pl"] for t in ctrl)
    for n in names:
        tr = runs[n]
        net = sum(t["pl"] for t in tr)
        adds = sum(t["pl"] for t in tr if t["is_add"])
        dd = max_drawdown([t["pl"] for t in tr])
        wd = min(daily(tr).values())
        P(f"| {n} | {len(tr)} | ${net:,.2f} | {100*(net/ctrl_net-1):+.1f}% | ${adds:,.2f} | "
          f"{100*dd/START_BALANCE:.2f}% | ${wd:,.2f} ({100*wd/START_BALANCE:.2f}%) |")
    rebuilt = sum(t["pl"] for t in runs[names[-1]] if not t["is_add"])
    P(f"\nCheck: control net ${ctrl_net:,.2f}; main trades only from the last run ${rebuilt:,.2f}.\n")

    # Year by year
    P("## Profit by year\n")
    years = sorted({t["day"][:4] for t in ctrl})
    P("| Year | " + " | ".join(names) + " |")
    P("|---" * (len(names) + 1) + "|")
    by = {n: defaultdict(float) for n in names}
    for n in names:
        for t in runs[n]:
            by[n][t["day"][:4]] += t["pl"]
    for y in years:
        P(f"| {y} | " + " | ".join(f"${by[n][y]:,.0f}" for n in names) + " |")
    P("| **Years better than control** | – | " + " | ".join(
        f"{sum(by[n][y] > by[names[0]][y] for y in years)} / {len(years)}" for n in names[1:]) + " |")
    P("| **Worst year vs control** | – | " + " | ".join(
        f"${min(by[n][y] - by[names[0]][y] for y in years):,.0f}" for n in names[1:]) + " |\n")

    # Daily win rate and streaks
    P("## Days (main trade + add counted as one result)\n")
    P("| Run | Trading days | Winning days | Win rate | Losses per win | Longest losing run | Runs of 4+ | Runs of 6+ | Costliest losing run |")
    P("|---|---|---|---|---|---|---|---|---|")
    for n in names:
        dv = list(daily(runs[n]).values())
        w = sum(v > 0 for v in dv)
        s = streaks(dv)
        P(f"| {n} | {len(dv)} | {w} | {100*w/len(dv):.0f}% | {(len(dv)-w)/w:.2f} | {max(s)} | "
          f"{sum(x >= 4 for x in s)} | {sum(x >= 6 for x in s)} | ${worst_run_cost(dv):,.0f} |")

    # Month of year
    P("\n## Month of year (control): is any month reliably worse?\n")
    months = defaultdict(list)
    for d, v in daily(ctrl).items():
        months[d[4:6]].append(v)
    allv = [v for vs in months.values() for v in vs]
    mu, sd = st.mean(allv), st.stdev(allv)
    P("| Month | Days | Net | Avg per day | t vs overall average |")
    P("|---|---|---|---|---|")
    for m in sorted(months):
        vs = months[m]
        t = (st.mean(vs) - mu) / (sd / math.sqrt(len(vs)))
        P(f"| {m} | {len(vs)} | ${sum(vs):,.0f} | ${st.mean(vs):,.0f} | {t:+.2f} |")
    P("\n|t| above ~2 would suggest a real seasonal effect; with 12 months tested, one reaching ~2 by chance is expected.\n")

    # Monte Carlo
    P("## Chance of hitting FTMO's $90,000 floor from today's balance "
      f"(${CURRENT_BALANCE:,.2f})\n")
    P("Resampled from each run's real daily results in blocks of 10 consecutive trading days, so losing streaks stay intact (5,000 simulated futures). ~21 trading days a month.\n")
    P("| Run | Risk | 3 months | 6 months | 12 months |")
    P("|---|---|---|---|---|")
    for n in names:
        dv = list(daily(runs[n]).values())
        per_day = len(dv) / (len({d[:6] for d in daily(runs[n])}) * 21.0)   # share of days with a trade
        for risk in (RISK_NOW, RISK_LATER):
            sc = risk / RISK_NOW
            cells = []
            for months_ahead in (3, 6, 12):
                horizon = max(1, int(months_ahead * 21 * per_day))
                cells.append(f"{100*monte_carlo(dv, sc, horizon, CURRENT_BALANCE, FTMO_FLOOR):.1f}%")
            P(f"| {n} | ${risk:.0f} | " + " | ".join(cells) + " |")

    P("\n## Chance of a drawdown of 6% / 8% / 10% within 12 months (from a fresh $100,000)\n")
    P("| Run | Risk | 6% | 8% | 10% |")
    P("|---|---|---|---|---|")
    for n in names:
        dv = list(daily(runs[n]).values())
        per_day = len(dv) / (len({d[:6] for d in daily(runs[n])}) * 21.0)
        horizon = int(12 * 21 * per_day)
        for risk in (RISK_NOW, RISK_LATER):
            sc = risk / RISK_NOW
            P(f"| {n} | ${risk:.0f} | " + " | ".join(
                f"{100*mc_drawdown(dv, sc, horizon, x):.1f}%" for x in (6, 8, 10)) + " |")

    text = "\n".join(out)
    dest = Path(paths[0]).with_name("ATW_ANALYSIS.md")
    dest.write_text(text + "\n")
    print(text)


if __name__ == "__main__":
    main(sys.argv[1:])
