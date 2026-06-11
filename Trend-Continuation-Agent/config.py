"""
/Trend-Continuation-Agent — Configuration

Spec: TrendContinuation_Agent_Spec_v1.pdf §12 "Config Constants (config.py)"

Two deliberate deviations from the literal spec values are flagged inline below
(see DEVIATION comments) — both were necessary for the scoring logic in §8 to
function correctly, and are documented in CLAUDE.md "Implementation Notes".
"""

import os

# ── Account / Connection ──────────────────────────────────────────────────────
ACCOUNT_TYPE = "SPREAD_BETTING"   # Change to 'CFD' when needed — all gate/scoring
                                   # logic is identical; only symbol resolution and
                                   # position sizing would need a CFD code path.
MCP_CONNECTION = "HTTP"

CTRADER_MCP_HOST = "mcp.ctrader.com"
CTRADER_MCP_PATH = "/trading/mcp"
CTRADER_MCP_TOKEN = os.environ.get(
    "CTRADER_MCP_TOKEN",
    # Demo Pepperstone UK Spread Betting token (from .mcp.json / ctrader-mcp-integration-guide.md)
    "eyJwbGFudCI6InBlcHBlcnN0b25ldWsiLCJlbnZpcm9ubWVudCI6ImRlbW8iLCJ0b2tlbiI6IkliMEJzUERzSXBpZUJnTEtUWTluRjRpMEJ6a3R4V0pvSm1ZNVB3a1lIb2c9In0",
)

# ── Bar fetch depth ────────────────────────────────────────────────────────────
# Spec: BARS_4H = 210 (fetch 210, use last 200) | BARS_1H = 110 (fetch 110, use last 100)
BARS_4H = 210
BARS_4H_USED = 200

# DEVIATION: spec sets BARS_1H = 110 / use last 100. §8 Signal S5 requires
# EMA(close_1H, 200) — a 200-period EMA cannot be computed from 100-110 bars
# (it would be `None` for the entire series, so S5 would always score 0).
# Bumped to 210/200 — identical to the 4H depth — so EMA200_1H is computable.
BARS_1H = 210
BARS_1H_USED = 200

# Day Trade Pipeline (v1.1 §2.4): 15M bars are fetched ONLY for instruments
# that pass the day trade gates (entry-timing only — never the full universe).
BARS_15M = 65
BARS_15M_USED = 60

# ── Indicator periods ──────────────────────────────────────────────────────────
ADX_PERIOD = 14
EMA_FAST = 21
EMA_MID = 50
EMA_SLOW = 200
RSI_PERIOD = 14
ATR_PERIOD = 14

# ── Swing / divergence detection ───────────────────────────────────────────────
SWING_N = 3          # bars each side for swing detection
SWING_LOOKBACK = 50  # max bars back for divergence check (4H, swing pipeline)

# Day Trade Pipeline (v1.1 §2.3): 1H divergence lookback — 50 bars on 1H spans
# >2 days, which isn't relevant to a same-day trade. SWING_N is unchanged.
SWING_LOOKBACK_1H = 30

# ── Gate thresholds ─────────────────────────────────────────────────────────────
GATE_ADX_MIN = 25

# Day Trade Pipeline (v1.1 §2.2): 1H ADX readings run structurally lower than
# 4H for the same instrument (more noise on the shorter timeframe) — a 25
# threshold on 1H would exclude valid intraday trends.
ADX_1H_MIN = 22

# ── Tiering ──────────────────────────────────────────────────────────────────────
TIER_A_MIN = 75
TIER_B_MIN = 50
TIER_C_MIN = 30

# Day Trade Pipeline (v1.1 §2.1/§3.2): tier thresholds above are unchanged —
# the 4H bias bonus lifts well-aligned setups above them, not the thresholds
# themselves. DAY_TIER_MAX = 100 (S1-S6) + DAY_BONUS_4H.
DAY_BONUS_4H = 10
DAY_TIER_MAX = 100 + DAY_BONUS_4H

# ── SL / TP ──────────────────────────────────────────────────────────────────────
SL_ATR_MULTIPLIER = 1.5
SL_SWING_BUFFER_ATR = 0.5   # buffer added beyond last swing high/low
TP1_R = 1.5
TP2_R = 2.5
TP3_R = 4.0

# ── Entry zone ───────────────────────────────────────────────────────────────────
# Spec §5/§9 show the "entry zone" as a tight band around the 1H EMA21 (e.g.
# EMA21≈8342.5 -> zone 8,340-8,345, a half-width of ~2.5, i.e. ~0.03% of
# price). Not given as an explicit formula — derived here as 1/10th of S2's
# "tight" 0.3% proximity threshold (spec §8 S2), which reproduces the
# worked examples. See CLAUDE.md "Implementation Notes".
ENTRY_ZONE_HALFWIDTH_PCT = 0.0003

# Day Trade Pipeline (v1.1 §3.4): entry zone around the 15M EMA21. Wider than
# the swing zone (±0.03%) to account for 15M noise — ±0.1% per spec.
DAY_ENTRY_ZONE_HALFWIDTH_PCT = 0.001

# ── Position sizing (Spread Betting) ─────────────────────────────────────────────
# Spec §6: "Round down to nearest £0.50/pt increment for clean sizing"
SPEC_STAKE_ROUND_INCREMENT = 0.5

# DEVIATION / broker reality: ctrader-mcp-integration-guide.md Lesson 5
# ("volume = stake_£/pt * 100, min/step 100") only holds for point_size==1.0
# instruments (indices, XAU/XPD/XPT) — confirmed there with a live UK30/US30-
# style order. A live EURGBP order using that formula was REJECTED
# ("Order volume = 16.00 is smaller than minimum allowed volume = 1000.00")
# because cTrader `volume` is "cents of base asset"; for point_size != 1.0
# instruments it must be `(stake_£/pt / point_size) * 100` (CLAUDE.md item
# 14). These two constants remain the point_size==1.0 baseline — £1/pt
# minimum/step — and `calc_stake` scales them by 1/point_size for other
# instruments. A £0.50/pt stake is NOT placeable on indices either way; the
# execution agent rounds DOWN to the nearest whole £1/pt for the actual
# order, after first applying the spec's £0.50 rounding for display.
BROKER_MIN_VOLUME = 100        # = £1.00/pt (point_size == 1.0 baseline)
BROKER_VOLUME_STEP = 100       # = £1.00/pt increments (point_size == 1.0 baseline)

# ── Execution sanity checks (Day Trade Pipeline v1.1 §5.2) ───────────────────────
# Non-blocking warning if the broker-rounded stake exceeds this (£/pt) —
# flags unusually large positions for the user to confirm before placing.
MAX_STAKE_PER_POINT = 50.0

# Non-blocking warning if the current spread exceeds this fraction of the
# stop-loss distance (poor risk:reward once spread cost is accounted for).
SPREAD_TO_SL_WARN_PCT = 0.20

# DEVIATION (flagged for Pravinder — see CLAUDE.md): §5.2's margin check
# requires a per-symbol margin rate / leverage. get_symbols (cached in
# data/sb_symbols.json) returns only symbol_id, symbol_name, base_name,
# point_size and description — no margin-rate field is available. Approximated
# as a flat 1/30 (~3.33%, the standard ESMA retail FX/CFD leverage cap) applied
# to the notional position value (entry_price * volume / 100 / point_size).
ASSUMED_MARGIN_RATE = 1 / 30

# ── Scan universe ────────────────────────────────────────────────────────────────
# Spec §12: "33 configured instruments + full available SB symbol list scan"
#
# DEVIATION (flagged for Pravinder — see CLAUDE.md): the live SB symbol list
# returned by get_symbols contains 1,618 ENABLED instruments (mostly individual
# equities/ETFs). Sub-Agent 1 fetches 4H+200 bars AND 1H+200 bars sequentially
# per instrument (per spec, to preserve HTTP session stability) — scanning all
# 1,618 would take many hours and isn't a "scan", it's an overnight batch job.
#
# Default behaviour: scan CORE_INSTRUMENTS (the 33 pre-configured names below,
# resolved to their SB equivalents). Pass --full-universe to additionally scan
# EXTENDED_UNIVERSE (a curated set of additional liquid FX crosses/metals that
# are common continuation candidates but weren't in the original 33). True
# "scan all 1,618 SB symbols" is available via --full-universe-all but is not
# recommended for interactive use.

CORE_INSTRUMENTS = [
    "UK100", "GER40", "US500", "US30", "NAS100", "US2000",
    "AUS200", "JPN225", "FRA40", "EU50", "HK50", "XAUUSD",
    "XAGUSD", "USOIL", "UKOIL", "EURUSD", "GBPUSD", "USDJPY",
    "AUDUSD", "USDCAD", "USDCHF", "NZDUSD", "EURGBP", "EURJPY",
    "GBPJPY", "AUDJPY", "CADJPY", "BTCUSD", "ETHUSD", "XPDUSD",
    "XPTUSD", "NATGAS", "CORN",
]

# Curated additional liquid FX crosses / metals — used only with --full-universe.
EXTENDED_UNIVERSE = [
    "EURAUD", "EURCHF", "EURCAD", "EURNZD", "GBPAUD", "GBPCAD",
    "GBPCHF", "GBPNZD", "AUDCAD", "AUDCHF", "AUDNZD", "NZDCAD",
    "NZDCHF", "CADCHF", "EURUSD", "USDSEK", "USDNOK", "USDMXN",
]

# Day Trade Pipeline (v1.1 §2.4/§7): runs on every scan alongside the swing
# pipeline, on a narrower universe than CORE_INSTRUMENTS — illiquid/wide-spread
# names (CORN, NATGAS, XPDUSD, XPTUSD, XAGUSD, CADJPY) are excluded since 15M
# entry timing on these is unreliable. Swing pipeline universe is unchanged.
DAY_TRADE_UNIVERSE = [
    "UK100", "GER40", "US500", "US30", "NAS100", "US2000",
    "AUS200", "JPN225", "FRA40", "EU50", "HK50", "XAUUSD",
    "USOIL", "UKOIL", "EURUSD", "GBPUSD", "USDJPY",
    "AUDUSD", "USDCAD", "USDCHF", "NZDUSD", "EURGBP", "EURJPY",
    "GBPJPY", "AUDJPY", "BTCUSD", "ETHUSD",
]

# Known-disabled on this account (logged + skipped, not treated as errors).
KNOWN_UNAVAILABLE = {"BTCUSD", "ETHUSD"}

# Path to cached SB symbol map (refreshed by data_retrieval if missing/stale)
SB_SYMBOL_CACHE = os.path.join(os.path.dirname(__file__), "data", "sb_symbols.json")

# ── UK timezone ────────────────────────────────────────────────────────────────
UK_TZ = "Europe/London"
