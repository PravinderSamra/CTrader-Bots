"""Vanessa's growth ladders: $500 at $100k, stepping up to $1,000 as the balance grows.

Uses the real Trades-Only logs (run at $300 risk); a day's P/L at risk X = P/L@300 * X/300.
All ladders drop one level after 4 losing days in a row, until the next winning day.
Run from the repo root:  python3 "Vanessa Algo Bots/research/scripts/growth_ladder_test.py"
"""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cushion_ladder_test as base  # noqa: E402

LADDERS = {
    "Current ladder": [(104000, 500), (98000, 400), (95000, 300), (0, 200)],
    "Growth, steps every $2k": [(110000, 1000), (108000, 900), (106000, 800), (104000, 700), (102000, 600),
                                (100000, 500), (97000, 400), (94000, 300), (0, 200)],
    "Growth, steps every $3k": [(115000, 1000), (112000, 900), (109000, 800), (106000, 700), (103000, 600),
                                (100000, 500), (97000, 400), (94000, 300), (0, 200)],
    "Growth $2k, $300 below $100k": [(110000, 1000), (108000, 900), (106000, 800), (104000, 700), (102000, 600),
                                     (100000, 500), (94000, 300), (0, 200)],
}
SIZES = {"Size 3": "ND_0.7_x3.trades.txt", "Size 5": "NG_0.7_x5.trades.txt", "Size 6.5": "NH_0.7_x6.5.trades.txt"}
NOW, TARGET, FLOOR, START = 96952.19, 110000.0, 90000.0, 100000.0
N, BLOCK, DAYS_PER_MONTH, PAYOUT_EVERY = 5000, 10, 9.2, 9


def risk(table, bal, losses):
    lvl = next(i for i, (m, _) in enumerate(table) if bal >= m)
    if losses >= 4:
        lvl = min(lvl + 1, len(table) - 1)
    return table[lvl][1]


def blocks(rng, rs):
    while True:
        i = rng.randrange(0, len(rs) - BLOCK)
        yield from rs[i:i + BLOCK]


def challenge(rs, table):
    rng = random.Random(9)
    win, days, worst = 0, [], 0.0
    for _ in range(N):
        bal, losses, n = NOW, 0, 0
        for r in blocks(rng, rs):
            pl = r * risk(table, bal, losses)
            worst = min(worst, pl)
            bal += pl
            losses = losses + 1 if r <= 0 else 0
            n += 1
            if bal >= TARGET:
                win += 1
                days.append(n)
                break
            if bal <= FLOOR:
                break
    days.sort()
    return win / N, days[len(days) // 4] / DAYS_PER_MONTH, days[len(days) // 2] / DAYS_PER_MONTH, \
        days[3 * len(days) // 4] / DAYS_PER_MONTH, worst


def funded(rs, table, horizon):
    rng = random.Random(5)
    hits, paid_all = 0, []
    for _ in range(N):
        bal, losses, paid = START, 0, 0.0
        g = blocks(rng, rs)
        for i in range(horizon):
            r = next(g)
            bal += r * risk(table, bal, losses)
            losses = losses + 1 if r <= 0 else 0
            if bal <= FLOOR:
                hits += 1
                break
            if (i + 1) % PAYOUT_EVERY == 0 and bal > START:
                paid += (bal - START) * 0.8
                bal = START
        paid_all.append(paid)
    paid_all.sort()
    return hits / N, paid_all[N // 2], paid_all[N // 10]


def main():
    out = ["# NAS100 — growth ladders ($500 at $100k, up to $1,000)\n",
           "Real cTrader logs (trigger 0.7). Every ladder drops one level after 4 losing days in a row. "
           "NAS100 bot alone — US500 will speed things up and add risk.\n", "## The ladders\n",
           "| Balance | " + " | ".join(LADDERS) + " |", "|---" * (len(LADDERS) + 1) + "|"]
    for b in (93000, 95000, 96952, 98000, 100000, 102000, 104000, 106000, 108000, 110000, 115000):
        out.append(f"| ${b:,} | " + " | ".join(f"${risk(t, b, 0):,}" for t in LADDERS.values()) + " |")
    out += ["", "## Current challenge: from $96,952 to $110,000 before $90,000\n",
            "| Size | Ladder | Pass | Fail | Fast (1 in 4) | Typical | Slow (1 in 4) | Worst single day |",
            "|---|---|---|---|---|---|---|---|"]
    fund = ["", "## Funded account: 12 months from $100,000, payout every month (80% to you)\n",
            "| Size | Ladder | Chance of hitting $90k | Typical payouts | Bad year (1 in 10) |", "|---|---|---|---|---|"]
    for s, f in SIZES.items():
        rs = base.daily_r(f)
        for name, t in LADDERS.items():
            p, q1, med, q3, worst = challenge(rs, t)
            out.append(f"| {s} | {name} | {100*p:.1f}% | {100*(1-p):.1f}% | {q1:.1f} mo | **{med:.1f} mo** | "
                       f"{q3:.1f} mo | -${-worst:,.0f} |")
            h, med_p, bad = funded(rs, t, int(len(rs) / base.YEARS))
            fund.append(f"| {s} | {name} | {100*h:.1f}% | ${med_p:,.0f} | ${bad:,.0f} |")
            print(f"{s:8} {name:30} pass {100*p:5.1f}% typical {med:4.1f} mo (fast {q1:.1f}, slow {q3:.1f}) worst day {worst:6.0f} | funded {100*h:4.1f}% payouts {med_p:6.0f} bad {bad:6.0f}")
    text = "\n".join(out + fund) + "\n"
    (base.ROOT / "Vanessa Algo Bots/research/results/NAS100_GROWTH_LADDER_TEST.md").write_text(text)


if __name__ == "__main__":
    main()
