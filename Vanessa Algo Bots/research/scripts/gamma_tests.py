"""Gamma tests - see ../GAMMA_TEST_PLAN.md (pre-registered).

Run from the repo root:  python3 "Vanessa Algo Bots/research/scripts/gamma_tests.py"
Needs only the Python standard library.
"""
import bisect
import csv
import datetime as dt
import math
import random
import statistics as st
from collections import defaultdict
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
GEX_CSV = ROOT / "Vanessa Algo Bots/research/data/squeezemetrics_dix_gex.csv"
ORB_CSV = ROOT / "ORB Projects/US500 ORB Bot/analysis/us500_trades.csv"
M5 = {"NAS100": (ROOT / "US30 London Range Breakout/data/NAS100/nas100_m5.csv", 1.5),
      "US30": (ROOT / "US30 London Range Breakout/data/US30/us30_m5.csv", 2.5)}
NY = ZoneInfo("America/New_York")
RNG = random.Random(20260929)
PERMS = 10000


# ---------- gamma regime (uses GEX dated D-1 only) ----------
def load_gex():
    rows = [(dt.date.fromisoformat(r["date"]), float(r["gex"])) for r in csv.DictReader(open(GEX_CSV))]
    rows.sort()
    dates = [d for d, _ in rows]
    vals = [g for _, g in rows]
    return dates, vals


GEX_DATES, GEX_VALS = load_gex()


def regime(day):
    """(tercile, sign) from the last GEX value strictly before `day`; None if not enough history."""
    i = bisect.bisect_left(GEX_DATES, day) - 1          # index of D-1 (last value before day)
    if i < 251:
        return None
    window = GEX_VALS[i - 251:i + 1]                    # 252 values ending at D-1
    g = GEX_VALS[i]
    pct = sum(1 for v in window if v < g) / len(window)
    terc = "low" if pct < 1 / 3 else ("high" if pct > 2 / 3 else "mid")
    return terc, ("neg" if g < 0 else "pos")


# ---------- stats helpers ----------
def summary(xs):
    n = len(xs)
    if n < 2:
        return n, (xs[0] if xs else float("nan")), float("nan")
    m = st.mean(xs)
    return n, m, m / (st.stdev(xs) / math.sqrt(n))


def perm_p(low, high):
    """One-sided p that mean(low) - mean(high) is this large by chance."""
    obs = st.mean(low) - st.mean(high)
    pool, k = low + high, len(low)
    hits = 0
    for _ in range(PERMS):
        RNG.shuffle(pool)
        if st.mean(pool[:k]) - st.mean(pool[k:]) >= obs:
            hits += 1
    return obs, (hits + 1) / (PERMS + 1)


def fmt_row(label, xs, unit):
    n, m, t = summary(xs)
    hit = 100 * sum(1 for x in xs if x > 0) / n if n else float("nan")
    return f"| {label} | {n} | {m:+.3f} {unit} | {t:+.2f} | {hit:.0f}% |"


out = []
P = out.append


# ---------- Test 1: US500 ORB ----------
def test1():
    rows = list(csv.DictReader(open(ORB_CSV)))
    rows.sort(key=lambda r: r["entry_time"])
    seen, first, allt = set(), [], []
    for r in rows:
        d = dt.datetime.fromisoformat(r["entry_time"]).replace(tzinfo=dt.timezone.utc).astimezone(NY).date()
        rec = (d, float(r["r"]))
        allt.append(rec)
        if d not in seen:
            seen.add(d)
            first.append(rec)

    P("## Test 1 - US500 15m ORB vs gamma regime\n")
    for name, book in (("First trade per day (primary)", first), ("All trades (secondary)", allt)):
        groups, years = defaultdict(list), defaultdict(lambda: defaultdict(list))
        for d, r in book:
            reg = regime(d)
            if reg is None:
                continue
            groups[reg[0]].append(r)
            groups[reg[1]].append(r)
            years[d.year][reg[0]].append(r)
        P(f"### {name}\n")
        P("| Regime | Trades | Mean R | t | Win % |\n|---|---|---|---|---|")
        for k in ("low", "mid", "high", "neg", "pos"):
            P(fmt_row({"low": "Low gamma tercile", "mid": "Mid", "high": "High gamma tercile",
                       "neg": "GEX negative", "pos": "GEX positive"}[k], groups[k], "R"))
        obs, p = perm_p(groups["low"], groups["high"])
        P(f"\nLow minus high: **{obs:+.3f} R per trade**, one-sided permutation p = **{p:.4f}**\n")
        P("| Year | Low: n, mean R | High: n, mean R | Low > high? |\n|---|---|---|---|")
        wins = 0
        for y in sorted(years):
            lo, hi = years[y]["low"], years[y]["high"]
            ok = bool(lo and hi and st.mean(lo) > st.mean(hi))
            wins += ok
            P(f"| {y} | {len(lo)}, {st.mean(lo) if lo else float('nan'):+.3f} | "
              f"{len(hi)}, {st.mean(hi) if hi else float('nan'):+.3f} | {'yes' if ok else 'no'} |")
        P(f"\nYears where low beat high: {wins} of {len(years)}\n")


# ---------- Test 2: last-half-hour momentum ----------
def load_prices(path):
    """{ny_date: {'10:00': p, '15:30': p, '16:00': p}} using closes of bars ENDING at those times."""
    want = {dt.time(9, 55): "10:00", dt.time(15, 25): "15:30", dt.time(15, 55): "16:00"}
    days = defaultdict(dict)
    with open(path) as f:
        for r in csv.DictReader(f):
            t = dt.datetime.fromtimestamp(int(r["timestamp_ms"]) / 1000, dt.timezone.utc).astimezone(NY)
            key = want.get(t.time())
            if key and t.weekday() < 5:
                days[t.date()][key] = float(r["close"])
    return days


def test2():
    P("## Test 2 - Last-half-hour momentum (strategy B)\n")
    P("Returns in basis points (bp) per trade; 1 bp = 0.01%. Net = after the assumed round-trip spread.\n")
    for sym, (path, cost_pts) in M5.items():
        days = load_prices(path)
        order = sorted(d for d in days if len(days[d]) == 3)
        trades = {"ROD": [], "ONFH": [], "BOTH": []}      # (date, gross_bp, cost_bp)
        for prev, d in zip(order, order[1:]):
            if (d - prev).days > 4:                        # skip gaps in the data
                continue
            pc, p = days[prev]["16:00"], days[d]
            rod = p["15:30"] / pc - 1
            onfh = p["10:00"] / pc - 1
            lh = (p["16:00"] / p["15:30"] - 1) * 1e4
            cost = cost_pts / p["15:30"] * 1e4
            s_rod, s_onfh = (1 if rod > 0 else -1), (1 if onfh > 0 else -1)
            trades["ROD"].append((d, s_rod * lh, cost))
            trades["ONFH"].append((d, s_onfh * lh, cost))
            if s_rod == s_onfh:
                trades["BOTH"].append((d, s_rod * lh, cost))

        P(f"### {sym} ({order[0]} .. {order[-1]}, assumed cost {cost_pts} pt round trip = "
          f"{st.mean(c for _, _, c in trades['ROD']):.2f} bp on average)\n")
        P("| Signal | Trades | Gross mean | Net mean | Net t | Win % (net) | Net Sharpe (annual) |\n|---|---|---|---|---|---|---|")
        for sig, book in trades.items():
            g = [x for _, x, _ in book]
            net = [x - c for _, x, c in book]
            n, m, t = summary(net)
            sharpe = m / st.stdev(net) * math.sqrt(252)
            win = 100 * sum(1 for x in net if x > 0) / n
            P(f"| {sig} | {n} | {st.mean(g):+.2f} bp | {m:+.2f} bp | {t:+.2f} | {win:.0f}% | {sharpe:+.2f} |")

        P("\nROD signal, cost sensitivity (net mean bp): " + ", ".join(
            f"{k}x cost {st.mean(x - k * c for _, x, c in trades['ROD']):+.2f}" for k in (0, 1, 2)) + "\n")

        P("| Year | ROD trades | Net mean | Net t |\n|---|---|---|---|")
        by_year = defaultdict(list)
        for d, x, c in trades["ROD"]:
            by_year[d.year].append(x - c)
        for y in sorted(by_year):
            n, m, t = summary(by_year[y])
            P(f"| {y} | {n} | {m:+.2f} bp | {t:+.2f} |")

        groups = defaultdict(list)
        for d, x, c in trades["ROD"]:
            reg = regime(d)
            if reg:
                groups[reg[0]].append(x - c)
                groups[reg[1]].append(x - c)
        P("\n| Gamma regime (ROD, net) | Trades | Mean | t | Win % |\n|---|---|---|---|---|")
        for k, lab in (("low", "Low tercile"), ("mid", "Mid"), ("high", "High tercile"),
                       ("neg", "GEX negative"), ("pos", "GEX positive")):
            if groups[k]:
                P(fmt_row(lab, groups[k], "bp"))
        obs, p = perm_p(groups["low"], groups["high"])
        P(f"\nLow minus high: **{obs:+.2f} bp per trade**, one-sided permutation p = **{p:.4f}**\n")


if __name__ == "__main__":
    P("# Gamma tests - results\n")
    P("Generated by `research/scripts/gamma_tests.py`. Plan: `research/GAMMA_TEST_PLAN.md`.\n")
    test1()
    test2()
    text = "\n".join(out)
    (ROOT / "Vanessa Algo Bots/research/results/GAMMA_TESTS_RAW.md").write_text(text + "\n")
    print(text)
