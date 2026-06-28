"""
Master runner — executes all 7 phases in sequence.
Run from the optimisation/ directory:
    cd optimisation && python run_all.py

Phases:
  1+2  C# cBot already built in cTrader/
  3    Data fetching via cTrader MCP
  4    Walk-Forward Optimisation
  5    Monte Carlo Resampling
  6    Report generation
  7    Acceptance criteria evaluation + deployment verdict
"""

import sys
import os
import time

# Ensure the optimisation/ directory is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import DATA_START, DATA_END, MC_SIMULATIONS
from data_fetcher import ensure_data
from wfo_engine import run_wfo
from mc_engine import run_monte_carlo
from report_generator import generate_wfo_report, _generate_acceptance_table

INSTRUMENT    = "GER40"
COARSE_FIRST  = True   # two-phase optimisation (coarse grid → faster)
FORCE_REFRESH = False  # set True to re-download all data


def main():
    t0 = time.time()
    print("=" * 70)
    print("EMA + VWAP SCALPING BOT — FULL VALIDATION PIPELINE")
    print(f"Instrument: {INSTRUMENT}  |  Data: {DATA_START} → {DATA_END}")
    print("=" * 70)

    # ── Phase 3: Data fetching ────────────────────────────────────────────────
    print("\n[PHASE 3] Fetching historical data from cTrader MCP…")
    data = ensure_data(INSTRUMENT, periods=["5M", "1H"], force_refresh=FORCE_REFRESH)

    bars_5m = data["5M"]
    bars_1h = data["1H"]

    print(f"  5M bars: {len(bars_5m):,}  |  1H bars: {len(bars_1h):,}")

    if len(bars_5m) < 1000:
        print("ERROR: Insufficient 5M data. Check cTrader MCP connection and retry.")
        sys.exit(1)

    # ── Phase 3 QC Gate ───────────────────────────────────────────────────────
    # Verify 20-combination test before full WFO run
    print("\n[PHASE 3 QC] Running 20-combination grid test…")
    from parameter_grid import generate_grid
    from backtest_engine import run_backtest
    from datetime import datetime, timezone

    test_start = datetime(2023, 1, 2, tzinfo=timezone.utc)
    test_end   = datetime(2023, 3, 31, tzinfo=timezone.utc)

    _5m_t = [b["time"] for b in bars_5m]
    _1h_t = [b["time"] for b in bars_1h]
    grid = list(generate_grid(coarse=True))[:20]
    qc_results = []
    for params in grid:
        r = run_backtest(bars_5m, bars_1h, test_start, test_end, params, INSTRUMENT,
                         _5m_times=_5m_t, _1h_times=_1h_t)
        qc_results.append(r)

    trades_found = [r["total_trades"] for r in qc_results]
    pfs_found    = [r["profit_factor"] for r in qc_results if r["total_trades"] > 0]
    print(f"  QC: 20 combos run | Trades: {min(trades_found)}–{max(trades_found)} | "
          f"PF range: {min(pfs_found):.2f}–{max(pfs_found):.2f}" if pfs_found else "  QC: No profitable combos in test range")

    pfs_vary = len(set(round(p, 2) for p in pfs_found)) > 1 if pfs_found else False
    if not pfs_vary:
        print("  ⚠ QC Warning: PF values not varying — check data quality")
    else:
        print("  ✓ QC PASSED: Parameters produce varying results")

    # ── Phase 4: Walk-Forward Optimisation ───────────────────────────────────
    print("\n[PHASE 4] Running Walk-Forward Optimisation…")
    wfo_results = run_wfo(bars_5m, bars_1h, instrument=INSTRUMENT,
                          coarse_first=COARSE_FIRST, verbose=True)

    if "error" in wfo_results:
        print(f"ERROR: WFO failed — {wfo_results['error']}")
        sys.exit(1)

    oos_trades      = wfo_results["oos_trades"]
    consensus_params = wfo_results["consensus_params"]
    oos_stats        = wfo_results["oos_stats"]

    # Phase 4 QC Gate: minimum 80 OOS trades
    oos_n = oos_stats.get("total_trades", 0)
    if oos_n < 80:
        print(f"ESCALATION: Only {oos_n} OOS trades (minimum 80). Cannot proceed to MC.")
        print("Recommendation: Extend data range or review session gate effectiveness.")
        sys.exit(1)

    print(f"  ✓ WFO COMPLETE: {oos_n} OOS trades | Consensus: {consensus_params}")

    # ── Phase 5: Monte Carlo Resampling ───────────────────────────────────────
    print(f"\n[PHASE 5] Running Monte Carlo ({MC_SIMULATIONS:,} simulations)…")
    mc_results = run_monte_carlo(oos_trades, n_sims=MC_SIMULATIONS, verbose=True)

    if "error" in mc_results:
        print(f"ERROR: MC failed — {mc_results['error']}")
        sys.exit(1)

    # Phase 5 QC Gate: hard stop on extreme ruin probability
    ruin_5 = mc_results["metrics"].get("ruin_prob_5pct", 1.0)
    if ruin_5 > 0.10:
        print(f"HARD STOP: MC ruin probability at 5% level = {ruin_5:.1%} (maximum 10%).")
        print("Do NOT deploy. Investigate and re-optimise.")
        sys.exit(1)

    # ── Phase 6: Report generation ────────────────────────────────────────────
    print("\n[PHASE 6] Generating reports…")
    generate_wfo_report(wfo_results)

    # ── Phase 7: Acceptance criteria evaluation ────────────────────────────────
    print("\n[PHASE 7] Evaluating acceptance criteria…")
    all_pass, verdict = _generate_acceptance_table(wfo_results)

    elapsed = time.time() - t0
    print(f"\n{'='*70}")
    print(f"PIPELINE COMPLETE in {elapsed/60:.1f} minutes")
    print(f"DEPLOYMENT VERDICT: {verdict}")
    print(f"{'='*70}\n")

    if "GREEN" in verdict:
        print("Recommendation: Deploy at full risk (1.0% per trade).")
        print(f"Consensus parameters: {consensus_params}")
    elif "AMBER" in verdict:
        print("Recommendation: Deploy at half risk (0.5% per trade).")
        print("Run 30-day live trial before scaling to full risk.")
    else:
        print("Recommendation: DO NOT DEPLOY.")
        print("Review which acceptance criteria failed and re-optimise accordingly.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
