"""Risk sizing test: current ladder vs risk set from the room above FTMO's $90k floor.

Uses the real Trades-Only logs (run at $300 risk). A day's P/L at risk X = P/L@300 * X/300.
Policies (all use the 4-loss rule: after 4 losing days in a row, risk is cut until the next winning day):
  ladder     : >=104k $500, >=98k $400, >=95k $300, else $200; streak rule = one level lower
  room/25    : risk = (balance - 90k) / 25, min $100, max $1,500; streak rule = x0.75
  room/30    : risk = (balance - 90k) / 30, min $100, max $1,500; streak rule = x0.75
  steepA     : >=104k $500, >=100k $400, >=97k $300, >=94k $200, else $100; streak rule = one level lower
  steepB     : >=104k $500, >=100k $400, >=98k $300, >=96k $200, else $100; streak rule = one level lower
  ladder+    : the ladder, then +$100 for every extra $5k above $104k (109k $600, 114k $700 ...), max $1,000
Run from the repo root:  python3 "Vanessa Algo Bots/research/scripts/cushion_ladder_test.py"
"""
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LOGS = ROOT / "Vanessa Algo Bots/research/data/nas100_atw_logs"
OUT = ROOT / "Vanessa Algo Bots/research/results/NAS100_CUSHION_LADDER_TEST.md"
RUNS = {"Size 3": "ND_0.7_x3.trades.txt", "Size 5": "NG_0.7_x5.trades.txt",
        "Size 6.5": "NH_0.7_x6.5.trades.txt", "Size 10": "NI_0.7_x10.trades.txt"}
TOTAL_R = {"Size 3": 1.6, "Size 5": 2.2, "Size 6.5": 2.65, "Size 10": 3.7}
START, FLOOR, BASE = 100000.0, 90000.0, 300.0
LADDER = [(104000.0, 500.0), (98000.0, 400.0), (95000.0, 300.0), (0.0, 200.0)]
TABLES = {"ladder": LADDER,
          "steepA": [(104000.0, 500.0), (100000.0, 400.0), (97000.0, 300.0), (94000.0, 200.0), (0.0, 100.0)],
          "steepB": [(104000.0, 500.0), (100000.0, 400.0), (98000.0, 300.0), (96000.0, 200.0), (0.0, 100.0)]}
NOW = 96952.19
CAP, MIN_RISK, STREAK = 1500.0, 100.0, 4
YEARS = 5.74
PAYOUT_EVERY = 9          # the bot trades on ~110 days a year, so ~9 trading days is about a month
N, BLOCK = 5000, 10
T_RE = re.compile(r"T\|[\d\- :]+\|[\d\- :]+\|([^|]+)\|\w+\|[\d.]+\|[\d.]+\|(-?[\d.]+)\|")


def daily_r(name):
    d = {}
    for line in (LOGS / name).read_text().splitlines():
        m = T_RE.search(line)
        if m:
            day = re.search(r"_(\d{8})", m.group(1)).group(1)
            d[day] = d.get(day, 0.0) + float(m.group(2))
    return [d[k] / BASE for k in sorted(d)]


def risk_for(policy, bal, losses):
    cut = losses >= STREAK
    if policy in TABLES:
        table = TABLES[policy]
        levels = [r for _, r in table]
        lvl = next(i for i, (m, _) in enumerate(table) if bal >= m)
        if cut:
            lvl = min(lvl + 1, len(levels) - 1)
        return levels[lvl]
    if policy == "ladder+":
        steps = [(104000.0 + 5000.0 * k, min(500.0 + 100.0 * k, 1000.0)) for k in range(5, -1, -1)]
        table = steps + LADDER[1:]
        levels = [r for _, r in table]
        lvl = next(i for i, (m, _) in enumerate(table) if bal >= m)
        if cut:
            lvl = min(lvl + 1, len(levels) - 1)
        return levels[lvl]
    div = 25.0 if policy == "room/25" else 30.0
    r = min(CAP, max(MIN_RISK, (bal - FLOOR) / div))
    return r * 0.75 if cut else r


def run(rs, policy, payouts=False, start=START):
    bal = peak = start
    worst_dd = worst_day = paid = 0.0
    losses = 0
    breached = False
    for i, r in enumerate(rs):
        risk = risk_for(policy, bal, losses)
        pl = r * risk
        bal += pl
        worst_day = min(worst_day, pl)
        losses = losses + 1 if r <= 0 else 0
        peak = max(peak, bal)
        worst_dd = max(worst_dd, peak - bal)
        if bal <= FLOOR:
            breached = True
            break
        if payouts and (i + 1) % PAYOUT_EVERY == 0 and bal > START:
            paid += (bal - START) * 0.8          # 80% split
            bal = peak = START
    return {"final": bal, "dd": worst_dd, "worst_day": worst_day, "breach": breached, "paid": paid}


def mc(rs, policy, horizon, payouts, seed=5, start=START):
    rng = random.Random(seed)
    hits, outs = 0, []
    for _ in range(N):
        path = []
        while len(path) < horizon:
            i = rng.randrange(0, len(rs) - BLOCK)
            path.extend(rs[i:i + BLOCK])
        res = run(path[:horizon], policy, payouts, start)
        hits += res["breach"]
        outs.append(res["paid"] if payouts else res["final"] - start)
    outs.sort()
    return hits / N, outs[N // 2], outs[N // 10]


def main():
    pols = ["ladder", "steepA", "steepB", "ladder+", "room/25", "room/30"]
    out = ["# NAS100 — risk ladder vs risk from the room above $90k\n",
           "Real cTrader logs, trigger 0.7, 2021-01-01 .. 2026-09-28. Every policy uses the 4-loss rule. "
           f"room/N = (balance − $90k) ÷ N, between ${MIN_RISK:.0f} and ${CAP:,.0f}. 12-month figures: "
           f"{N:,} simulated years from a fresh $100k, built from real 10-day blocks.\n"]
    P = out.append
    P("Risk per trade at different balances:\n")
    P("| Balance | " + " | ".join(pols) + " |\n|---" * 1 + "|---" * len(pols) + "|")
    for b in (93000, 95000, 96000, 97000, 98000, 100000, 104000, 110000, 120000, 130000):
        P(f"| ${b:,} | " + " | ".join(f"${risk_for(p, b, 0):,.0f}" for p in pols) + " |")
    P("")
    for name, f in RUNS.items():
        rs = daily_r(f)
        horizon = int(len(rs) / YEARS)
        P(f"## {name} (total risk after add {TOTAL_R[name]}R)\n")
        P("| Policy | Replay 2021–26 final balance (no payouts) | Replay deepest drawdown | Replay worst day | "
          "12 mo, no payouts: chance of $90k | typical profit | bad year (1 in 10) | "
          "12 mo, monthly payouts: chance of $90k | typical payouts to you (80%) | bad year payouts | "
          f"From ${NOW:,.0f}, monthly payouts: chance of $90k | typical payouts |")
        P("|---|---|---|---|---|---|---|---|---|---|---|---|")
        for p in pols:
            rp = run(rs, p)
            a = mc(rs, p, horizon, False)
            b = mc(rs, p, horizon, True)
            c = mc(rs, p, horizon, True, start=NOW)
            P(f"| {p} | ${rp['final']:,.0f} | ${rp['dd']:,.0f} | -${-rp['worst_day']:,.0f} | "
              f"{100*a[0]:.1f}% | ${a[1]:,.0f} | ${a[2]:,.0f} | {100*b[0]:.1f}% | ${b[1]:,.0f} | ${b[2]:,.0f} | "
              f"{100*c[0]:.1f}% | ${c[1]:,.0f} |")
            print(f"{name:8} {p:8} 12m-no-payout {100*a[0]:4.1f}% med {a[1]:7.0f} | payouts {100*b[0]:4.1f}% med {b[1]:6.0f} bad {b[2]:6.0f} | now {100*c[0]:4.1f}% med {c[1]:6.0f} | replay dd {rp['dd']:6.0f} worst day {rp['worst_day']:6.0f}")
        P("")
    OUT.write_text("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
