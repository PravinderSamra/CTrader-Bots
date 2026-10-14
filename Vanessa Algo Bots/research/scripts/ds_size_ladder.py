"""Daily Systems size ladder test (pre-registered 14 Oct 2026). Uses the bot's own tick-backtest trades (H| legs),
each leg's net P/L scaled by the size multiplier in force when it was opened. 2020-23 first, 2024-26 once.
FLAT: $13k per position. LADDER A (Umar): x1.25 after +$3,000 closed profit since the last step AND a new equity high;
one step down when the drawdown from the peak reaches $2,000; never below x1.0.
LADDER B: size proportional to balance (start $100k).
KEEP if profit / max drawdown does not fall and the worst day stays inside the $2,000 daily guard."""
import re
from collections import defaultdict
from datetime import date

UP = "/root/.claude/uploads/05dd4dd7-22e7-57bf-8cec-d6a0c9610eea/"
LOGS = {"2020-23": "3e7ac88f-DS_tick_data_20-23_log.txt", "2024-26": "6d9a4ab0-DS_tick_data_24-26_log.txt"}


def legs(f):
    out = []
    for line in open(UP + f):
        m = re.search(r"Info \| H\|(.*)", line)
        if m:
            p = m.group(1).split("|")
            out.append((date.fromisoformat(p[3]), date.fromisoformat(p[4]), float(p[11])))
    return sorted(out)


def run(L, mode):
    # events in time order: opens fix the multiplier, closes book the scaled P/L
    ev = [(d0, 0, i) for i, (d0, d1, _) in enumerate(L)] + [(d1, 1, i) for i, (d0, d1, _) in enumerate(L)]
    ev.sort()
    bal = 100000.0; peak = bal; lpeak = bal; mult = 1.0; last_step_bal = bal; m_at = {}; day = defaultdict(float); maxdd = 0.0; levels = set()
    for d, kind, i in ev:
        if kind == 0:
            if mode == "B": mult = bal / 100000.0
            m_at[i] = mult; levels.add(round(mult, 2))
        else:
            pnl = L[i][2] * m_at[i]; bal += pnl; day[d] += pnl
            peak = max(peak, bal); maxdd = max(maxdd, peak - bal); lpeak = max(lpeak, bal)
            if mode == "A":
                # true peak tracks drawdown; lpeak only times the next step-down (another $2k lower)
                if bal >= peak and bal - last_step_bal >= 3000: mult *= 1.25; last_step_bal = bal; lpeak = bal
                elif lpeak - bal >= 2000 and mult > 1.0: mult = max(1.0, mult / 1.25); last_step_bal = bal; lpeak = bal
    prof = bal - 100000
    return prof, maxdd, min(day.values()), max(levels)


if __name__ == "__main__":
    for per, f in LOGS.items():
        L = legs(f); print(f"== {per}: {len(L)} legs")
        base = None
        for mode, name in (("F", "Flat $13k"), ("A", "Ladder A (+25% per $3k, step down after $2k DD)"), ("B", "Ladder B (proportional to balance)")):
            p, dd, wd, mx = run(L, mode)
            ratio = p / dd if dd else 0
            if mode == "F": base = ratio
            verdict = "" if mode == "F" else ("KEEP" if ratio >= base and wd > -2000 else "REJECT")
            print(f"  {name:48s} profit ${p:+9,.0f}  max DD ${dd:6,.0f}  profit/DD {ratio:4.2f}  worst day ${wd:+7,.0f}  top size x{mx:.2f}  {verdict}")
