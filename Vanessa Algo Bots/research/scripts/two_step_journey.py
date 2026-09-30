"""FTMO 2-Step journey: Phase 1 from today's balance to $110k, then Phase 2 from $100k to $105k.

Both phases have the static $90k floor. Uses the real Trades-Only logs (run at $300 risk) in random
10-day blocks. NAS100 bot alone. Run from the repo root:
  python3 "Vanessa Algo Bots/research/scripts/two_step_journey.py"
"""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cushion_ladder_test as base  # noqa: E402
import growth_ladder_test as g  # noqa: E402

LADDERS = {"Current ladder": g.LADDERS["Current ladder"], "Your growth ladder": g.LADDERS["Growth, steps every $3k"]}
PHASES = [(96952.19, 110000.0), (100000.0, 105000.0)]
N = 5000


def phase(rng, rs, table, start, target):
    bal, losses, n = start, 0, 0
    for r in g.blocks(rng, rs):
        bal += r * g.risk(table, bal, losses)
        losses = losses + 1 if r <= 0 else 0
        n += 1
        if bal >= target:
            return True, n
        if bal <= g.FLOOR:
            return False, n


def main():
    out = ["# FTMO 2-Step journey — NAS100 bot alone\n",
           "Phase 1: $96,952 → $110,000. Phase 2: $100,000 → $105,000. $90,000 floor in both. "
           f"{N:,} simulated journeys from real 10-day blocks; about 9.2 trading days a month.\n",
           "| Size | Ladder | Pass phase 1 | Pass phase 2 (if phase 1 passed) | Reach funded | "
           "Typical time to funded | Fast (1 in 4) | Slow (1 in 4) |", "|---|---|---|---|---|---|---|---|"]
    for s, f in g.SIZES.items():
        rs = base.daily_r(f)
        for name, t in LADDERS.items():
            rng = random.Random(21)
            p1 = p2 = 0
            times = []
            for _ in range(N):
                ok1, n1 = phase(rng, rs, t, *PHASES[0])
                if not ok1:
                    continue
                p1 += 1
                ok2, n2 = phase(rng, rs, t, *PHASES[1])
                if ok2:
                    p2 += 1
                    times.append((n1 + n2) / g.DAYS_PER_MONTH)
            times.sort()
            q = lambda f: times[int(f * len(times))]
            line = (f"| {s} | {name} | {100*p1/N:.1f}% | {100*p2/p1:.1f}% | **{100*p2/N:.1f}%** | "
                    f"**{q(0.5):.1f} mo** | {q(0.25):.1f} mo | {q(0.75):.1f} mo |")
            out.append(line)
            print(line)
    (base.ROOT / "Vanessa Algo Bots/research/results/NAS100_TWO_STEP_JOURNEY.md").write_text("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
