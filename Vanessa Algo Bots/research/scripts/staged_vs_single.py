"""Staged adds (3 parts) vs a single add, compared at the same total profit.

Adds scale linearly with Add Size, so a run at size k = main trades + (k / 5) x the size-5 adds.
Each run uses its own main trades. NAS100 bot alone, trigger 0.7, $300 base risk.
Run from the repo root:  python3 "Vanessa Algo Bots/research/scripts/staged_vs_single.py"
"""
import random
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import growth_ladder_test as g  # noqa: E402
import two_step_journey as j  # noqa: E402

LOGS = Path(__file__).resolve().parents[1] / "data/nas100_atw_logs"
T_RE = re.compile(r"T\|[\d\- :]+\|[\d\- :]+\|([^|]+)\|\w+\|[\d.]+\|[\d.]+\|(-?[\d.]+)\|")


def split(name):
    main, adds = defaultdict(float), defaultdict(float)
    for line in (LOGS / name).read_text().splitlines():
        m = T_RE.search(line)
        if m:
            day = re.search(r"_(\d{8})", m.group(1)).group(1)
            (adds if "_ADD" in m.group(1) else main)[day] += float(m.group(2))
    return main, adds


def series(main, adds, k):
    days = sorted(set(main) | set(adds))
    return [main[d] + adds[d] * k / 5.0 for d in days]


def stats(vals):
    bal = peak = 100000.0
    dd = 0.0
    for v in vals:
        bal += v
        peak = max(peak, bal)
        dd = max(dd, peak - bal)
    return sum(vals), dd, min(vals)


def journey(rs, table):
    rng = random.Random(21)
    ok, times = 0, []
    for _ in range(j.N):
        a, n1 = j.phase(rng, rs, table, *j.PHASES[0])
        if not a:
            continue
        b, n2 = j.phase(rng, rs, table, *j.PHASES[1])
        if b:
            ok += 1
            times.append((n1 + n2) / g.DAYS_PER_MONTH)
    times.sort()
    return ok / j.N, times[len(times) // 2]


def main():
    sm, sa = split("NG_0.7_x5.trades.txt")
    tm, ta = split("NJ_0.7_x5_staged3.trades.txt")
    target = sum(sm.values()) + sum(sa.values())
    k_eq = 5 * (target - sum(tm.values())) / sum(ta.values())
    runs = [("Single add, size 5", series(sm, sa, 5)),
            ("Staged 3 parts, size 5", series(tm, ta, 5)),
            (f"Staged 3 parts, size {k_eq:.1f} (same profit)", series(tm, ta, k_eq))]
    ladder = g.LADDERS["Growth, steps every $3k"]
    out = ["# Staged adds vs single add — NAS100, trigger 0.7\n",
           "Real logs: single add size 5 and staged (3 parts, every 0.7R) size 5. Other staged sizes scale the add "
           "parts. Journey = FTMO phase 1 from $96,952 to $110k then phase 2 $100k to $105k, growth ladder, "
           f"{j.N:,} simulations.\n",
           "| Run | Net profit at $300 | Deepest drawdown (closed days) | Worst day | Reach funded | Typical time |",
           "|---|---|---|---|---|---|"]
    for name, vals in runs:
        net, dd, worst = stats(vals)
        rs = [v / 300.0 for v in vals]
        p, t = journey(rs, ladder)
        line = f"| {name} | ${net:,.0f} | ${dd:,.0f} ({dd/1000:.2f}%) | -${-worst:,.0f} | {100*p:.1f}% | {t:.1f} mo |"
        out.append(line)
        print(line)
    Path(__file__).resolve().parents[1].joinpath("results/NAS100_STAGED_VS_SINGLE.md").write_text("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
