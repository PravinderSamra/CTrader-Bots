"""
Central configuration for the EMA+VWAP WFO and Monte Carlo framework.
All date ranges, instrument IDs, and MCP credentials are defined here.
"""

import os
from datetime import date, datetime, timezone

# ── cTrader MCP connection ────────────────────────────────────────────────────
MCP_HOST  = "mcp.ctrader.com"
MCP_PATH  = "/trading/mcp"
MCP_TOKEN = os.environ.get(
    "CTRADER_MCP_TOKEN",
    "eyJwbGFudCI6InBlcHBlcnN0b25ldWsiLCJlbnZpcm9ubWVudCI6ImRlbW8iLCJ0b2tlbiI6IkliMEJzUERzSXBpZUJnTEtUWTluRjRpMEJ6a3R4V0pvSm1ZNVB3a1lIb2c9In0"
)

# ── Instruments ───────────────────────────────────────────────────────────────
SYMBOL_IDS = {
    "GER40": 200,   # GER40_SB — primary instrument
    "US500": 220,   # US500_SB — generalisation check only
}

# Price pip digits for display conversion (GER40 range 12000–30000 → N=7 for raw ~1800000000)
# Detect automatically from raw price; kept here as reference fallback
PIP_DIGITS_FALLBACK = {
    "GER40": 5,   # verified: 1961950000 / 10^5 = 19619.5
    "US500": 5,
}

# ── Data range ────────────────────────────────────────────────────────────────
DATA_START = date(2021, 1, 4)   # First trading day Jan 2021
DATA_END   = date(2024, 12, 31) # Last trading day Dec 2024

# ── WFO parameters (Section 9) ────────────────────────────────────────────────
WFO_IS_MONTHS  = 6   # In-sample window length
WFO_OOS_MONTHS = 2   # Out-of-sample window length
WFO_STEP_MONTHS = 2  # Roll-forward step (equal to OOS for non-overlapping)
WFO_MIN_IS_TRADES  = 40
WFO_MIN_OOS_TRADES = 15

# IS composite score weights
COMPOSITE_WEIGHTS = {
    "profit_factor":   0.35,
    "sharpe_ratio":    0.30,
    "win_rate":        0.15,
    "recovery_factor": 0.20,
}

# IS minimum qualification thresholds
IS_MIN_PROFIT_FACTOR = 1.30
IS_MIN_WIN_RATE      = 0.42   # 42%
IS_MAX_DRAWDOWN      = 0.15   # 15%

# Stability check: spike rejection threshold
STABILITY_SPIKE_PF_THRESHOLD = 1.10  # neighbour PF below this = spike
STABILITY_MAX_FAILING_NEIGHBOURS = 2  # if >= 2 neighbours fail → reject

# ── Monte Carlo parameters (Section 10) ──────────────────────────────────────
MC_SIMULATIONS = 2000
MC_RANDOM_SEED = 42   # for reproducibility in reports

# MC acceptance thresholds (minimum)
MC_MIN_PROB_PROFIT   = 0.85   # >85% sims end profitable
MC_MAX_RUIN_5PCT     = 0.05   # <5% sims hit -5% drawdown
MC_MAX_RUIN_10PCT    = 0.01   # <1% sims hit -10% drawdown
MC_MAX_MEDIAN_DD     = 0.10   # <10% median max drawdown
MC_MAX_P95_DD        = 0.20   # <20% 95th pct max drawdown
MC_MIN_MEDIAN_PF     = 1.30   # >1.30 median profit factor
MC_MAX_MEDIAN_STREAK = 8      # <8 median longest losing streak
MC_MAX_P95_STREAK    = 15     # <15 95th pct losing streak

# ── Acceptance criteria for live deployment (Section 13) ──────────────────────
ACCEPTANCE_CRITERIA = {
    "oos_profit_factor":    {"min": 1.30, "target": 1.50},
    "oos_sharpe_ratio":     {"min": 0.80, "target": 1.20},
    "oos_win_rate":         {"min": 0.42, "target": 0.50},
    "oos_max_drawdown":     {"min": 0.15, "target": 0.10},  # lower is better
    "oos_recovery_factor":  {"min": 1.50, "target": 2.50},
    "oos_total_trades":     {"min": 80,   "target": None},
    "is_oos_pf_degradation":{"min": 2.00, "target": 1.50},  # lower is better
    "mc_prob_profit":       {"min": 0.85, "target": 0.90},
    "mc_ruin_5pct":         {"min": 0.05, "target": 0.02},  # lower is better
    "mc_ruin_10pct":        {"min": 0.01, "target": 0.005}, # lower is better
    "mc_p95_max_dd":        {"min": 0.20, "target": 0.15},  # lower is better
    "mc_median_pf":         {"min": 1.30, "target": 1.50},
    "mc_5th_pct_equity":    {"min": 0.0,  "target": 1.05},  # multiple of start
    "stability_check":      {"min": True, "target": True},
    "min_oos_per_pass":     {"min": 15,   "target": None},
}

# ── Data file paths ───────────────────────────────────────────────────────────
import os as _os
_BASE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
DATA_DIR    = _os.path.join(_BASE, "data")
RESULTS_DIR = _os.path.join(_BASE, "results")
WFO_DIR     = _os.path.join(RESULTS_DIR, "wfo")
MC_DIR      = _os.path.join(RESULTS_DIR, "mc")
REPORT_DIR  = _os.path.join(RESULTS_DIR, "reports")

for _d in [DATA_DIR, RESULTS_DIR, WFO_DIR, MC_DIR, REPORT_DIR]:
    _os.makedirs(_d, exist_ok=True)
