"""Risk-ladder test for the NAS100 bot (with or without Add To Winner).

Takes Trades-Only logs (T|... lines, run at a fixed $300 risk). Because the bot risks a fixed dollar
amount, each day's result scales in proportion to the risk, so a day's P/L at risk X = P/L@300 * X/300.

Policies compared:
  fixed300, fixed500     - constant risk
  ladder                 - risk set each morning from the balance (LADDER below)
  ladder+streak          - as ladder, but one level lower after 4 losing days in a row,
                           until the next winning day

Usage (repo root):
  python3 "Vanessa Algo Bots/research/scripts/ladder_test.py" RUN1.log RUN2.log ...
"""
import random
import re
import sys
from collections import OrderedDict
from pathlib import Path

BASE_RISK = 300.0
START = 100000.0
FLOOR = 90000.0
NOW = 96952.19
# (minimum balance, risk per trade), highest first
LADDER = [(104000.0, 500.0), (98000.0, 400.0), (95000.0, 300.0), (0.0, 200.0)]
LEVELS = [r for _, r in LADDER]
STREAK = 4
BLOCK = 10
T_RE = re.compile(r"T\|[\d\- :]+\|[\d\- :]+\|([^|]+)\|\w+\|[\d.]+\|[\d.]+\|(-?[\d.]+)\|")


def daily_r(path):
    d = OrderedDict()
    for line in Path(path).read_text(errors="replace").splitlines():
        m = T_RE.search(line)
        if m:
            day = re.search(r"_(\d{8})", m.group(1)).group(1)
            d[day] = d.get(day, 0.0) + float(m.group(2))
    days = sorted(d)
    return days, [d[k] / BASE_RISK for k in days]


def ladder_level(balance):
    for i, (minimum, _) in enumerate(LADDER):
        if balance >= minimum:
            return i
    return len(LADDER) - 1


def run(rs, policy, start):
    bal = peak = start
    low = start
    worst_dd = 0.0
    losses = 0
    risks = []
    for r in rs:
        if policy == "fixed300":
            risk = 300.0
        elif policy == "fixed500":
            risk = 500.0
        else:
            lvl = ladder_level(bal)
            if policy == "ladder+streak" and losses >= STREAK:
                lvl = min(lvl + 1, len(LEVELS) - 1)
            risk = LEVELS[lvl]
        risks.append(risk)
        bal += r * risk
        losses = losses + 1 if r <= 0 else 0
        peak = max(peak, bal)
        low = min(low, bal)
        worst_dd = max(worst_dd, peak - bal)
    return {"final": bal, "low": low, "dd": worst_dd, "breach": low <= FLOOR,
            "avg_risk": sum(risks) / len(risks)}


def mc(rs, policy, start, horizon, n=5000, seed=7):
    rng = random.Random(seed)
    hits, profits = 0, []
    for _ in range(n):
        path = []
        while len(path) < horizon:
            i = rng.randrange(0, max(1, len(rs) - BLOCK))
            path.extend(rs[i:i + BLOCK])
        res = run(path[:horizon], policy, start)
        hits += res["breach"]
        profits.append(res["final"] - start)
    profits.sort()
    return hits / n, profits[len(profits) // 2]


def main(paths):
    policies = ["fixed300", "fixed500", "ladder", "ladder+streak"]
    out = ["# Risk-ladder test — NAS100\n",
           "Ladder: " + ", ".join(f"≥${m:,.0f} → ${r:.0f}" for m, r in LADDER) +
           f". Streak rule: one level lower after {STREAK} losing days in a row, until the next winning day.\n"]
    P = out.append
    for p in paths:
        name = Path(p).stem
        days, rs = daily_r(p)
        trading_days_per_year = len(rs) / 5.74   # 1 Jan 2021 - 28 Sep 2026
        horizon = int(trading_days_per_year)
        P(f"## {name}\n")
        P("### Replay of 2021–2026 from $100,000\n")
        P("| Policy | Final balance | Lowest balance | Room left above $90k at the low | Deepest drawdown | Average risk |")
        P("|---|---|---|---|---|---|")
        for pol in policies:
            r = run(rs, pol, START)
            P(f"| {pol} | ${r['final']:,.0f} | ${r['low']:,.0f} | ${r['low'] - FLOOR:,.0f} | "
              f"${r['dd']:,.0f} ({100*r['dd']/START:.1f}%) | ${r['avg_risk']:.0f} |")
        P(f"\n### Next 12 months from today's ${NOW:,.2f} (5,000 simulated futures, 10-day blocks)\n")
        P("| Policy | Chance of hitting $90k | Median 12-month profit |")
        P("|---|---|---|")
        for pol in policies:
            prob, med = mc(rs, pol, NOW, horizon)
            P(f"| {pol} | {100*prob:.1f}% | ${med:,.0f} |")
        P("")
    text = "\n".join(out)
    Path(paths[0]).with_name("LADDER_TEST.md").write_text(text + "\n")
    print(text)


if __name__ == "__main__":
    main(sys.argv[1:])
