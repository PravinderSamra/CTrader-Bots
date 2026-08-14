#!/usr/bin/env python3
"""
How much of the 2024-vs-2025 gap is signal, and how much is 37 coin flips?

The bot took 37 trades in 2024, 37 in 2025 and 20 in 2026 - 94 in total. That is
a very small sample for a strategy whose P/L is dominated by a handful of large
winners, and it governs how much any reoptimisation can be trusted. Three tests:

  1. PERMUTATION. Pool all 94 trades, reshuffle which year each belongs to, and
     ask how often chance alone produces a year-gap as large as the real one.
     This is the question "did 2024 really behave differently?".

  2. BOOTSTRAP. Resample the pooled trades with replacement into synthetic
     37-trade years to get a confidence interval on annual P/L. This answers
     "if the edge is constant, how wide is the range of plausible years?".

  3. ORDER SHUFFLE. Keep the trades, shuffle their sequence, and measure the
     distribution of peak-to-trough drawdown. Equity-curve shape is an accident
     of ordering; this shows the drawdown you should actually plan for.

    python monte_carlo.py results/trades.csv
"""
import argparse
import numpy as np
import pandas as pd

RNG = np.random.default_rng(20260814)
N_ITER = 100_000


def permutation_test(t):
    """Could the 2024 vs 2025 gap have arisen by chance from one pooled edge?"""
    a = t[t.year == 2024].pl.values
    b = t[t.year == 2025].pl.values
    observed = b.mean() - a.mean()
    pool = np.concatenate([a, b])
    n_a = len(a)

    diffs = np.empty(N_ITER)
    for i in range(N_ITER):
        p = RNG.permutation(pool)
        diffs[i] = p[n_a:].mean() - p[:n_a].mean()
    p_two = float(np.mean(np.abs(diffs) >= abs(observed)))

    print("1. PERMUTATION TEST - is 2024 genuinely different from 2025?")
    print("-" * 68)
    print(f"   2024 mean P/L per trade   {a.mean():+8.2f}  (n={n_a})")
    print(f"   2025 mean P/L per trade   {b.mean():+8.2f}  (n={len(b)})")
    print(f"   observed gap              {observed:+8.2f}")
    print(f"   p-value (two-sided)       {p_two:8.4f}")
    verdict = ("the gap IS larger than chance comfortably explains"
               if p_two < 0.05 else
               "chance alone reproduces a gap this large often enough that the\n"
               "   two years are NOT statistically distinguishable")
    print(f"   -> {verdict}\n")
    return p_two


def bootstrap_years(t):
    """If the pooled edge were constant, how variable would a 37-trade year be?"""
    pool = t.pl.values
    n = 37
    sims = RNG.choice(pool, size=(N_ITER, n), replace=True).sum(axis=1)
    qs = np.percentile(sims, [5, 25, 50, 75, 95])

    print("2. BOOTSTRAP - spread of a 37-trade year drawn from ONE constant edge")
    print("-" * 68)
    print(f"   pooled mean per trade     {pool.mean():+8.2f}   (n={len(pool)})")
    print(f"   5th percentile year       {qs[0]:+8.0f}")
    print(f"   25th                      {qs[1]:+8.0f}")
    print(f"   median                    {qs[2]:+8.0f}")
    print(f"   75th                      {qs[3]:+8.0f}")
    print(f"   95th percentile year      {qs[4]:+8.0f}")
    actual_2024 = t[t.year == 2024].pl.sum()
    pct = float(np.mean(sims <= actual_2024)) * 100
    print(f"\n   actual 2024 = {actual_2024:+.0f}, which sits at the {pct:.1f}th percentile")
    print(f"   -> a year at least this bad happens {pct:.1f}% of the time with NO")
    print("      change in edge at all\n")
    losing = float(np.mean(sims < 0)) * 100
    print(f"   probability any given year finishes negative: {losing:.1f}%\n")
    return sims


def drawdown_distribution(t):
    """Equity-curve shape is an accident of ordering. What DD should be planned for?"""
    pool = t.pl.values

    def max_dd(seq):
        eq = np.cumsum(seq)
        return float(np.min(eq - np.maximum.accumulate(eq)))

    actual = max_dd(pool)
    sims = np.array([max_dd(RNG.permutation(pool)) for _ in range(20_000)])
    qs = np.percentile(sims, [5, 50, 95])

    print("3. ORDER SHUFFLE - drawdown you should plan for, not the one you got")
    print("-" * 68)
    print(f"   actual max drawdown (as traded)   {actual:+8.0f}")
    print(f"   median shuffled                   {qs[1]:+8.0f}")
    print(f"   5th pct (bad luck ordering)       {qs[0]:+8.0f}")
    print(f"   worst simulated                   {sims.min():+8.0f}")
    print(f"   -> the sequence you happened to get was {'kinder' if actual > qs[1] else 'harsher'}")
    print("      than typical; size risk against the tail, not the realised curve\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("trades", nargs="?", default="results/trades.csv")
    a = ap.parse_args()

    t = pd.read_csv(a.trades, parse_dates=["date"])
    t["year"] = t.date.dt.year
    t = t.dropna(subset=["pl"])

    print()
    print("=" * 68)
    print(f"MONTE CARLO on {len(t)} actual trades  ({N_ITER:,} iterations)")
    print("=" * 68)
    print()
    permutation_test(t)
    bootstrap_years(t)
    drawdown_distribution(t)


if __name__ == "__main__":
    main()
