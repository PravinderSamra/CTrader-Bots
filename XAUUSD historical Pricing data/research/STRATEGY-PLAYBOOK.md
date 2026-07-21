# XAUUSD Day-Trader Playbook — Actionable Strategies Ranked by Edge

Companion to `REPORT.md`. Every stat below is out of 1,290 trading days (Jul 2021 – Jul 2026), net of $0.40/oz round-trip cost, sized in ATR units (ATR = prior 20-day average daily range). All times **UTC**.

**Golden rule for all of them: position size = fixed risk ÷ ATR20. Re-compute weekly.** ATR went $17 → $205 over this sample.

---

## ⭐ A. The Overnight Drift (primary edge — systematic)

**Why it works:** essentially 100% of gold's net drift over 5 years accrued 22:00→02:00 UTC (t = 5.45, positive all 6 years). NY session contributed nothing net. Asia physical demand + short-covering into the close is the standing explanation; it has persisted for decades in the literature and through both regimes in this data.

**Rules**
- Mon–Thu only. **Long** at 20:00 UTC (or at the 22:00 reopen with a limit to dodge reopen spread).
- Exit at 02:00 UTC. No take-profit.
- Disaster stop: entry − 0.5 × ATR20.
- Optional filter: only when close > 20-day SMA (fewer trades, higher quality).

**Stats (with 0.5-ATR stop):** 1,017 trades · 53.6% win · +2.30% ATR/trade · Sharpe ≈ 1.6 · maxDD −5.9R · one flat-to-losing year (2022).

**⚠️ Check before trading:** overnight swap. Long-XAUUSD swap on CFD accounts runs ≈ −$0.3 to −0.8/oz/night (3× Wed). Gross edge is +$1.5–1.8/oz/trade, so a high-swap account can halve or kill it. On bad swap terms trade the 22:00→02:00 variant (some brokers charge swap at 22:00 cut — verify) or express it in micro futures.

---

## ⭐ B. NY Opening Range Breakout (primary edge — active)

**Why it works:** 13:00–15:00 UTC is the highest-energy window of the day (COMEX open 13:30, US data, NYSE open, PM fix) and 34% of daily extremes form 12:00–17:00. Trend days launch here.

**Rules**
- Opening range = high/low of **13:30–14:00 UTC**.
- Stop-orders both sides; first fill wins, cancel the other.
- Stop-loss = far side of the opening range (structural — do NOT tighten it).
- **No take-profit.** Exit 20:00 UTC or at stop. (A 2R TP cut expectancy by ⅓ in test — the money is in the ~15% of days that trend all afternoon.)

**Stats:** 1,252 trades · 42.3% win · +0.083 R-on-risk/trade · +2.05% ATR/trade · Sharpe ≈ 1.0 · maxDD −4.9R. Expect losing streaks of 6–10; the tail days pay the month. Weak years: 2021, 2026-H1 (extreme-chop opens).

**Enhancements to explore:** skip days whose Asian+London range already exceeded 1.2× ATR (day's fuel spent); size up on NFP/CPI/FOMC days rather than skipping them.

---

## ⭐ C. Asian Range Map (the framework for every 5m/1m decision)

Not a signal by itself — the highest-value *conditioning* information in the data. Mark Asia = 22:00–06:59 high/low every morning.

| Fact | Number | How to use it |
|------|--------|---------------|
| Day breaks ≥1 side of Asia | 96.7% | never assume the range holds |
| Day breaks only ONE side | 62% | these are the trend days |
| One-side days close beyond the break | **69–70%** | after a clean break, buy/sell 5m pullbacks toward the broken level; hold runners into the close |
| London breaks a side first → day closes through it | ~50% | continuation is the base case |
| → closes back past range mid (reversal) | ~32% | fade ONLY on confirmed displacement back inside |
| → full sweep-through to opposite side ("Judas") | 18–23% | the exception, not the rule — demand proof |
| Both sides broken | 35% | range/chop day → fade extremes to the mid, cut targets |

**Practical daily routine:** at 07:00 note Asia H/L. First London/NY break with displacement = directional bias for the day. If price is back inside the range after 12:00 with both sides swept → switch to range-day tactics.

---

## B+. Prior-Day Levels (target framework)

- PDH or PDL gets touched **85.6%** of days (inside days only 14.4%) → they are your default intraday targets from anywhere in the middle of yesterday's range.
- Resolution at the level is a coin flip (≈50% close-through) → **always take partials into PDH/PDL**, hold rest only with a trend-day context (one-side Asia break in that direction).

---

## Graded out — tested and NOT worth trading

| Idea | Result | Lesson |
|------|--------|--------|
| Bar-level momentum or mean-reversion (1m–1h) | autocorr ≈ 0 every year | edge must come from context, not the last bar |
| Fading/chasing 3σ 5m spikes | 46.9% continuation, ≈0 net | leave spikes alone |
| Asian breakout with **tight** (0.33 ATR) stop | −0.55% ATR/trade | tight stops turn a positive system negative; stops must be structural |
| NYSE-open ORB (14:30) | +0.11% ATR, Sharpe 0.06 | the tradeable open is COMEX 13:30, not 14:30 |
| Midday continuation entry (12:00, after extension) | ≈0, longs negative | if you missed the level, you missed the trade |
| Weekend gap fade | 89% fill overall BUT only 60% for gaps >15% ATR | only the untradeably-small gaps fill reliably |
| $100 round-number strategies | no magnet/barrier effect | use for order placement psychology only |
| Maintenance-gap (21:00→22:00) direction | pure macro-trend proxy | not an independent edge |

---

## Suggested combined book (how I'd run it)

| Sleeve | Risk/trade | Frequency | Role |
|--------|-----------|-----------|------|
| A Overnight drift | 0.25–0.5% | 4 nights/wk | steady anomaly collection |
| B NY ORB | 0.5–1% | ~5 days/wk | convex trend capture |
| C/B+ Discretionary 5m trades inside the Asia-range map, targeting PDH/PDL | 0.25–0.5% | 0–3/day | skill expression, capped |

Portfolio note: A and B are nearly uncorrelated (different hours, different mechanism). The combined ~Sharpe of A+B in-sample exceeds either alone. Kill-switch: any sleeve down 8R on rolling 60 trades gets halved until it makes a new equity high.

**Re-validation:** re-run `scripts/03–05` quarterly on refreshed data (fetch runbook in parent folder). The overnight edge weakening below +1% ATR/trade for two consecutive quarters = retire sleeve A.
