"""Monte Carlo test of the live NAS100 bot (v3.2 Auto Ladder, TP 4.5R, trailing from 2.5R, size 5).

Source: the real ladder-on cTrader log (2021-01-01 .. 2026-09-28). Each trading day's result is turned into R
(the day's P/L divided by the risk the bot used that day, from its L| line), so the days can be replayed in a
different order and at any risk.

Tests (all with the live +33% ladder and the 4-loss rule):
  A. Reshuffle the whole 2021-26 history at a fixed $1 risk: worst drawdown (R) and longest losing run.
  B. The next 12 months from today's balance, no target: profit, worst drawdown, losing runs, $90k floor.
  C. The FTMO journey from today's balance: phase 1 to $110k, then phase 2 $100k -> $105k.
  D. Stress: B and C again with every winning day cut by 10% and by 20% (live worse than the backtest).
B-D use 10-day blocks of real days (keeps good and bad spells together) as well as single shuffled days.
Run from the repo root:  python3 "Vanessa Algo Bots/research/scripts/monte_carlo_test.py"
"""
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LOG = ROOT / "Vanessa Algo Bots/research/data/nas100_ladder_logs/DS4b_TP45_ladder.trades.txt"
OUT = ROOT / "Vanessa Algo Bots/research/results/NAS100_MONTE_CARLO.md"
NOW, FLOOR, DAILY_LIMIT = 98073.77, 90000.0, 5000.0
PHASES = [(NOW, 110000.0), (100000.0, 105000.0)]
LADDER = [(115000, 1350), (112000, 1200), (109000, 1050), (106000, 950), (103000, 800),
          (100000, 650), (97000, 550), (94000, 400), (0, 250)]
N, BLOCK, MONTHS_IN_LOG = 10000, 10, 68.9

T_RE = re.compile(r"\| T\|[^|]+\|[^|]+\|[^|]*_(\d{8})(?:_ADD\d+)?\|\w+\|[\d.]+\|[\d.]+\|(-?[\d.]+)\|")
L_RE = re.compile(r"\| L\|(\d{4})-(\d{2})-(\d{2})\|[\d.]+\|(\d+)\|")


def daily_r():
    risk, pl = {}, {}
    for line in LOG.read_text().splitlines():
        m = L_RE.search(line)
        if m:
            risk[m.group(1) + m.group(2) + m.group(3)] = float(m.group(4))
            continue
        m = T_RE.search(line)
        if m:
            pl[m.group(1)] = pl.get(m.group(1), 0.0) + float(m.group(2))
    return [pl[d] / risk[d] for d in sorted(pl)]


def risk(bal, losses):
    lvl = next(i for i, (m, _) in enumerate(LADDER) if bal >= m)
    if losses >= 4:
        lvl = min(lvl + 1, len(LADDER) - 1)
    return LADDER[lvl][1]


def stream(rng, rs, blocks):
    while True:
        if blocks:
            i = rng.randrange(0, len(rs) - BLOCK)
            yield from rs[i:i + BLOCK]
        else:
            yield rs[rng.randrange(len(rs))]


def pct(xs, q):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(q * len(xs)))]


def reshuffle(rs):
    """A: the same days in a random order, fixed risk. Drawdown in R, longest losing run."""
    rng = random.Random(1)
    dds, runs = [], []
    for _ in range(N):
        seq = rs[:]
        rng.shuffle(seq)
        eq = peak = dd = 0.0
        run = longest = 0
        for r in seq:
            eq += r
            peak = max(peak, eq)
            dd = max(dd, peak - eq)
            run = run + 1 if r <= 0 else 0
            longest = max(longest, run)
        dds.append(dd)
        runs.append(longest)
    return dds, runs


def actual(rs):
    eq = peak = dd = 0.0
    run = longest = 0
    for r in rs:
        eq += r
        peak = max(peak, eq)
        dd = max(dd, peak - eq)
        run = run + 1 if r <= 0 else 0
        longest = max(longest, run)
    return dd, longest


def year(rs, days, blocks, seed=2):
    """B: 12 months from today's balance with the ladder, no target."""
    rng = random.Random(seed)
    ends, dds, runs, floor, worst_day, limit = [], [], [], 0, 0.0, 0
    for _ in range(N):
        bal, peak, dd, losses, longest = NOW, NOW, 0.0, 0, 0
        g = stream(rng, rs, blocks)
        hit = False
        for _ in range(days):
            r = next(g)
            p = r * risk(bal, losses)
            worst_day = min(worst_day, p)
            if p <= -DAILY_LIMIT:
                limit += 1
            bal += p
            losses = losses + 1 if r <= 0 else 0
            longest = max(longest, losses)
            peak = max(peak, bal)
            dd = max(dd, (peak - bal) / peak)
            if bal <= FLOOR:
                hit = True
                break
        floor += hit
        ends.append(bal - NOW)
        dds.append(dd)
        runs.append(longest)
    return ends, dds, runs, floor / N, worst_day, limit


def journey(rs, blocks, dpm, seed=3):
    """C: phase 1 from today's balance to $110k, then phase 2 $100k -> $105k, $90k floor in both."""
    rng = random.Random(seed)
    p1 = p2 = 0
    times = []
    for _ in range(N):
        total, ok = 0, True
        for start, target in PHASES:
            bal, losses, n = start, 0, 0
            g = stream(rng, rs, blocks)
            while FLOOR < bal < target:
                r = next(g)
                bal += r * risk(bal, losses)
                losses = losses + 1 if r <= 0 else 0
                n += 1
            total += n
            if bal <= FLOOR:
                ok = False
                break
            if target == 110000.0:
                p1 += 1
        if ok:
            p2 += 1
            times.append(total / dpm)
    return p1 / N, p2 / N, times


def main():
    rs = daily_r()
    dpm = len(rs) / MONTHS_IN_LOG
    days = round(dpm * 12)
    wins = sum(r > 0 for r in rs)
    out = ["# NAS100 bot: Monte Carlo test\n",
           f"Live settings (size 5, trigger 0.7, TP 4.5R, trailing from 2.5R, step 0.1, +33% ladder, 4-loss rule). "
           f"Source: the real cTrader ladder log 2021-01-01 .. 2026-09-28: {len(rs)} trading days "
           f"({wins} winning, {100 * wins / len(rs):.0f}%), about {dpm:.1f} trading days a month. "
           f"Each day is converted to R using the risk the bot actually used that day. {N:,} simulations per test. "
           f"Starting balance ${NOW:,.2f}. The log includes a small commission (30 per million), so it is slightly "
           "conservative against FTMO's $0 index commission.\n",
           f"Average day {sum(rs) / len(rs):+.2f}R; best day {max(rs):+.2f}R; worst day {min(rs):+.2f}R.\n"]

    dd_a, run_a = actual(rs)
    dds, runs = reshuffle(rs)
    out += ["## A. Was the backtest's order of days lucky?\n",
            "The same days reshuffled into random orders, at a fixed risk.\n",
            "| | Actual backtest | Typical | Bad (1 in 20) | Very bad (1 in 100) |", "|---|---|---|---|---|",
            f"| Worst drawdown | {dd_a:.1f}R | {pct(dds, .5):.1f}R | {pct(dds, .95):.1f}R | {pct(dds, .99):.1f}R |",
            f"| Longest run of losing days | {run_a} | {pct(runs, .5)} | {pct(runs, .95)} | {pct(runs, .99)} |", ""]

    stress = [("Backtest as is", 1.0), ("Winning days 10% smaller", 0.9), ("Winning days 20% smaller", 0.8)]
    out += [f"## B. The next 12 months from ${NOW:,.0f} (about {days} trading days, ladder on, no target)\n",
            "| Scenario | Method | Typical profit | Bad year (1 in 10) | Very bad (1 in 20) | Chance of a losing year | "
            "Typical worst drawdown | Bad drawdown (1 in 20) | Longest losing run (1 in 20) | Chance of hitting $90k |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    worst_all, limit_all = 0.0, 0
    for name, f in stress:
        srs = [r * f if r > 0 else r for r in rs]
        for method, blocks in (("10-day blocks", True), ("single days", False)):
            ends, dd, run, fl, wd, lim = year(srs, days, blocks)
            worst_all, limit_all = min(worst_all, wd), limit_all + lim
            line = (f"| {name} | {method} | ${pct(ends, .5):+,.0f} | ${pct(ends, .1):+,.0f} | ${pct(ends, .05):+,.0f} | "
                    f"{100 * sum(e < 0 for e in ends) / N:.1f}% | {100 * pct(dd, .5):.1f}% | {100 * pct(dd, .95):.1f}% | "
                    f"{pct(run, .95)} days | {100 * fl:.2f}% |")
            out.append(line)
            print(line)
    out += ["", f"Worst single day in all the 12-month simulations: -${-worst_all:,.0f}. Days at or beyond FTMO's "
            f"$5,000 daily loss limit: {limit_all}. (Closing balances only; a trade's open loss is capped by its stop.)\n"]

    out += [f"## C. The FTMO journey from ${NOW:,.0f}: phase 1 to $110k, then phase 2 $100k to $105k\n",
            "| Scenario | Method | Pass phase 1 | Reach funded | Fast (1 in 4) | Typical time | Slow (1 in 4) |",
            "|---|---|---|---|---|---|---|"]
    for name, f in stress:
        srs = [r * f if r > 0 else r for r in rs]
        for method, blocks in (("10-day blocks", True), ("single days", False)):
            p1, p2, t = journey(srs, blocks, dpm)
            line = (f"| {name} | {method} | {100 * p1:.1f}% | **{100 * p2:.1f}%** | {pct(t, .25):.1f} mo | "
                    f"**{pct(t, .5):.1f} mo** | {pct(t, .75):.1f} mo |")
            out.append(line)
            print(line)
    OUT.write_text("\n".join(out) + "\n")
    print("\n".join(out[:12]))


if __name__ == "__main__":
    main()
