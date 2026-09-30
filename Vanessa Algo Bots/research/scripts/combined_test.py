"""NAS100 + US500 on one FTMO account: how much US500 (if any) to add.

Daily P/L from the real Trades-Only logs (both run at $300 risk). On each day the ladder sets the NAS100
risk X from the balance; US500 risks f x X. Days are the union of both bots' trading days.
Journey = phase 1 from $96,952 to $110k, then phase 2 from $100k to $105k, $90k floor, growth ladder,
4-loss rule on combined days. Run from the repo root:
  python3 "Vanessa Algo Bots/research/scripts/combined_test.py"
"""
import random
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import growth_ladder_test as g  # noqa: E402

DATA = Path(__file__).resolve().parents[1] / "data"
T_RE = re.compile(r"T\|[\d\- :]+\|[\d\- :]+\|([^|]+)\|\w+\|[\d.]+\|[\d.]+\|(-?[\d.]+)\|")
LADDER = g.LADDERS["Growth, steps every $3k"]
N, BLOCK, YEARS = 5000, 10, 5.74


def daily(path, since="00000000"):
    d = defaultdict(float)
    for line in path.read_text().splitlines():
        m = T_RE.search(line)
        if m:
            day = re.search(r"_(\d{8})", m.group(1)).group(1)
            if day >= since:
                d[day] += float(m.group(2))
    return d


def combine(nas, us, f):
    days = sorted(set(nas) | set(us))
    return [((nas.get(d, 0.0) + f * us.get(d, 0.0)) / 300.0) for d in days]


def phase(rng, rs, start, target):
    bal, losses, n = start, 0, 0
    while True:
        i = rng.randrange(0, len(rs) - BLOCK)
        for r in rs[i:i + BLOCK]:
            bal += r * g.risk(LADDER, bal, losses)
            losses = losses + 1 if r <= 0 else 0
            n += 1
            if bal >= target:
                return True, n
            if bal <= 90000.0:
                return False, n


def journey(rs, days_per_month):
    rng = random.Random(21)
    ok, times = 0, []
    for _ in range(N):
        a, n1 = phase(rng, rs, 96952.19, 110000.0)
        if not a:
            continue
        b, n2 = phase(rng, rs, 100000.0, 105000.0)
        if b:
            ok += 1
            times.append((n1 + n2) / days_per_month)
    times.sort()
    return ok / N, times[len(times) // 2], times[len(times) // 4], times[3 * len(times) // 4]


def worst_day_at_top(rs):
    return min(rs) * 1000.0   # combined worst day if the ladder is at its $1,000 top level


def main():
    nas5 = daily(DATA / "nas100_atw_logs/NG_0.7_x5.trades.txt")
    nas65 = daily(DATA / "nas100_atw_logs/NH_0.7_x6.5.trades.txt")
    us = daily(DATA / "us500_atw_logs/U0_control.trades.txt")
    both = set(nas5) & set(us)
    same_loss = sum(1 for d in both if nas5[d] <= 0 and us[d] <= 0)
    out = ["# NAS100 + US500 on one account (US500 control, no adds)\n",
           f"Days both bots traded: {len(both)}. Both lost on the same day: {same_loss} "
           f"({100*same_loss/len(both):.0f}% of shared days).\n",
           "| Setup | Reach funded | Typical time | Fast (1 in 4) | Slow (1 in 4) | Worst day at $1,000 level |",
           "|---|---|---|---|---|---|"]
    setups = [("NAS100 size 5 alone", nas5, {}, 0.0), ("NAS100 size 6.5 alone", nas65, {}, 0.0)]
    for f in (0.25, 0.5, 1.0):
        setups.append((f"NAS100 size 5 + US500 at {int(f*100)}% of NAS risk", nas5, us, f))
    for name, nas, u, f in setups:
        rs = combine(nas, u, f)
        per_month = len(rs) / YEARS / 12.0
        p, med, q1, q3 = journey(rs, per_month)
        line = (f"| {name} | {100*p:.1f}% | **{med:.1f} mo** | {q1:.1f} mo | {q3:.1f} mo | "
                f"-${-worst_day_at_top(rs):,.0f} |")
        out.append(line)
        print(line)
    (DATA.parent / "results/COMBINED_NAS100_US500.md").write_text("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
