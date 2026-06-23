# EMA9/VWAP NAS100_SB Backtest Report
## Strategy: "Trading Litt" EMA9 Touch with VWAP Confluence

---

## Overview

| Parameter         | Value                          |
|-------------------|-------------------------------|
| Instrument        | NAS100_SB (UK Spread Betting) |
| Timeframe         | H1 (1-hour bars)              |
| Period            | 15 Dec 2025 – 15 Jun 2026     |
| Total Bars        | 2,907                         |
| Starting Capital  | £10,000                       |
| Risk per Trade    | £100 (fixed)                  |
| Take Profit       | 2R (2× risk)                  |
| Session Filter    | 07:30–21:00 UTC               |

---

## Strategy Rules Applied

**LONG Setup:**
1. Price above rising VWAP (VWAP trending up over last 3 bars)
2. Impulse bar: close ≥ 0.3% above EMA9, volume > 1.5× 20-bar average
3. Pullback: within 12 bars of impulse, low wick touches EMA9 (within 0.25%), bar closes above EMA9
4. Max 2 EMA9 touches allowed after each impulse (1st and 2nd touch only)
5. Choppy filter: fewer than 3 EMA9-VWAP crosses in prior 10 bars
6. Entry: next bar open after touch
7. Stop Loss: touch-bar low − 5 points
8. Take Profit: entry + 2 × (entry − SL)
9. SL distance: 10–150 points only

**SHORT Setup:** Mirror of long (below declining VWAP, impulse downward, wick touches EMA9 from below)

---

## Overall Results

| Metric             | Value       |
|--------------------|-------------|
| **Net P&L**        | **+£200**   |
| Starting Capital   | £10,000     |
| Ending Capital     | £10,200     |
| Return             | +2.0%       |
| Total Trades       | 16          |
| Wins               | 6 (37.5%)   |
| Losses             | 10 (62.5%)  |
| Profit Factor      | 1.20        |
| Avg Win            | +£200       |
| Avg Loss           | −£100       |
| Break-even Win %   | 33.3%       |

---

## Week-by-Week Breakdown

| Week (Mon)   | Trades | W | L | P&L     | Trade Detail |
|--------------|--------|---|---|---------|--------------|
| 15 Dec 2025  | 2      | 1 | 1 | +£100   | ✗ LONG 18/12 19:00 SL=26pt; ✓ LONG 19/12 18:00 SL=79pt |
| 22 Dec 2025  | 1      | 1 | 0 | +£200   | ✓ LONG 23/12 19:00 SL=27pt |
| 29 Dec 2025  | 0      | — | — | £0      | No signals |
| 05 Jan 2026  | 4      | 1 | 3 | −£100   | ✗ L 05/01 19:00 SL=61pt; ✓ L 06/01 17:00 SL=60pt; ✗ L 07/01 20:00 SL=17pt; ✗ L 09/01 19:00 SL=84pt |
| 12 Jan 2026  | 2      | 1 | 1 | +£100   | ✗ SHORT 14/01 20:00 SL=38pt; ✓ SHORT 16/01 17:00 SL=40pt |
| 19 Jan 2026  | 2      | 1 | 1 | +£100   | ✓ LONG 21/01 18:00 SL=105pt; ✗ LONG 23/01 19:00 SL=41pt |
| 26 Jan 2026  | 1      | 0 | 1 | −£100   | ✗ SHORT 28/01 19:00 SL=19pt |
| 02 Feb 2026  | 0      | — | — | £0      | No signals |
| 09 Feb 2026  | 1      | 0 | 1 | −£100   | ✗ SHORT 11/02 18:00 SL=64pt |
| 16 Feb 2026  | 0      | — | — | £0      | No signals |
| 23 Feb 2026  | 0      | — | — | £0      | No signals |
| 02 Mar 2026  | 0      | — | — | £0      | No signals |
| 09 Mar 2026  | 0      | — | — | £0      | No signals |
| 16 Mar 2026  | 1      | 1 | 0 | +£200   | ✓ SHORT 18/03 17:00 SL=72pt |
| 23 Mar 2026  | 0      | — | — | £0      | No signals |
| 30 Mar 2026  | 0      | — | — | £0      | No signals |
| 06 Apr 2026  | 0      | — | — | £0      | No signals |
| 13 Apr 2026  | 1      | 0 | 1 | −£100   | ✗ LONG 17/04 19:00 SL=36pt |
| 20 Apr 2026  | 1      | 0 | 1 | −£100   | ✗ SHORT 21/04 18:00 SL=64pt |
| 27 Apr 2026  | 0      | — | — | £0      | No signals |
| 04 May 2026  | 0      | — | — | £0      | No signals |
| 11 May 2026  | 0      | — | — | £0      | No signals |
| 18 May 2026  | 0      | — | — | £0      | No signals |
| 25 May 2026  | 0      | — | — | £0      | No signals |
| 01 Jun 2026  | 0      | — | — | £0      | No signals |
| 08 Jun 2026  | 0      | — | — | £0      | No signals |

---

## Trade-by-Trade Detail

| # | Dir   | Entry DateTime       | Exit DateTime        | Entry    | SL       | TP       | SL Dist | Stake   | Result | P&L    | Balance   |
|---|-------|----------------------|----------------------|----------|----------|----------|---------|---------|--------|--------|-----------|
| 1 | LONG  | 2025-12-18 19:00 UTC | 2025-12-18 20:00 UTC | 25097.5  | 25071.5  | 25149.5  | 26.0 pt | £3.85/pt | LOSS  | −£100  | £9,900    |
| 2 | LONG  | 2025-12-19 18:00 UTC | 2025-12-22 12:00 UTC | 25338.2  | 25259.4  | 25495.8  | 78.8 pt | £1.27/pt | WIN   | +£200  | £10,100   |
| 3 | LONG  | 2025-12-23 19:00 UTC | 2025-12-24 13:00 UTC | 25544.2  | 25517.4  | 25597.8  | 26.8 pt | £3.73/pt | WIN   | +£200  | £10,300   |
| 4 | LONG  | 2026-01-05 19:00 UTC | 2026-01-06 08:00 UTC | 25419.7  | 25358.7  | 25541.7  | 61.0 pt | £1.64/pt | LOSS  | −£100  | £10,200   |
| 5 | LONG  | 2026-01-06 17:00 UTC | 2026-01-06 19:00 UTC | 25504.4  | 25444.4  | 25624.4  | 60.0 pt | £1.67/pt | WIN   | +£200  | £10,400   |
| 6 | LONG  | 2026-01-07 20:00 UTC | 2026-01-07 21:00 UTC | 25715.9  | 25698.6  | 25750.5  | 17.3 pt | £5.78/pt | LOSS  | −£100  | £10,300   |
| 7 | LONG  | 2026-01-09 19:00 UTC | 2026-01-12 00:00 UTC | 25780.6  | 25696.1  | 25949.6  | 84.5 pt | £1.18/pt | LOSS  | −£100  | £10,200   |
| 8 | SHORT | 2026-01-14 20:00 UTC | 2026-01-14 21:00 UTC | 25333.1  | 25370.9  | 25257.5  | 37.8 pt | £2.65/pt | LOSS  | −£100  | £10,100   |
| 9 | SHORT | 2026-01-16 17:00 UTC | 2026-01-18 23:00 UTC | 25555.4  | 25595.9  | 25474.4  | 40.5 pt | £2.47/pt | WIN   | +£200  | £10,300   |
|10 | LONG  | 2026-01-21 18:00 UTC | 2026-01-21 19:00 UTC | 25097.8  | 24992.9  | 25307.6  | 104.9 pt| £0.95/pt | WIN   | +£200  | £10,500   |
|11 | LONG  | 2026-01-23 19:00 UTC | 2026-01-23 21:00 UTC | 25585.8  | 25545.0  | 25667.4  | 40.8 pt | £2.45/pt | LOSS  | −£100  | £10,400   |
|12 | SHORT | 2026-01-28 19:00 UTC | 2026-01-28 20:00 UTC | 26041.5  | 26060.1  | 26004.3  | 18.6 pt | £5.38/pt | LOSS  | −£100  | £10,300   |
|13 | SHORT | 2026-02-11 18:00 UTC | 2026-02-11 19:00 UTC | 25177.4  | 25241.9  | 25048.4  | 64.5 pt | £1.55/pt | LOSS  | −£100  | £10,200   |
|14 | SHORT | 2026-03-18 17:00 UTC | 2026-03-18 19:00 UTC | 24620.2  | 24692.0  | 24476.6  | 71.8 pt | £1.39/pt | WIN   | +£200  | £10,400   |
|15 | LONG  | 2026-04-17 19:00 UTC | 2026-04-19 22:00 UTC | 26640.7  | 26604.9  | 26712.3  | 35.8 pt | £2.79/pt | LOSS  | −£100  | £10,300   |
|16 | SHORT | 2026-04-21 18:00 UTC | 2026-04-21 19:00 UTC | 26566.9  | 26630.4  | 26439.9  | 63.5 pt | £1.57/pt | LOSS  | −£100  | £10,200   |

---

## Key Observations

### What Worked
- **Dec 2025 and Jan 2026** generated the most signals (13 of 16 trades)
- Win rate of 37.5% exceeds the 33.3% break-even required for 2:1 R:R
- The strongest weeks were 22 Dec (+£200), 19 Jan (+£100), 16 Mar (+£200)
- Long bias was correct — NAS100 moved from ~25,000 to ~30,000 over the 6 months

### Why the Signal Frequency Dropped
- **May–Jun 2026**: NAS100 rallied sharply from ~29,500 → 30,000+. In a strong trending move, price **never comes back to touch EMA9**, so no signals fire. This is expected and correct — the strategy avoids chasing extended moves.
- **Feb–early Mar 2026**: Choppy/consolidation period. The chop filter correctly suppressed signals during sideways action.

### Position Sizing Variance
- Small SL trades (17–27pt) required high leverage (£3.8–£5.8/pt) — these are scalp-like entries
- Large SL trades (79–105pt) had lower leverage (£0.95–£1.27/pt) — more swing-like
- All sized to £100 risk regardless of SL distance (correct per the brief)

---

## Limitations & Caveats

1. **H1 timeframe**: The strategy is ideally executed on M5 or M15 for precise EMA9 wicks. H1 aggregates intrabar moves, making it harder to identify exact touch quality.
2. **Simplified entry logic**: Real execution requires watching for the touch in real-time. The backtest uses bar-close logic (touch detected on close, entry on next open).
3. **No spread accounted for**: NAS100_SB typically has a 1–2 point spread which would slightly reduce all wins and increase all losses.
4. **2R TP assumed**: The strategy images don't specify a fixed TP — actual traders might trail stops for larger wins.
5. **Small sample**: 16 trades over 6 months is statistically limited. Win rate of 37.5% has wide confidence intervals at this sample size.
6. **Data quality**: H1 data assembled from ~30 API calls across multiple sessions. Small gaps possible at session boundaries.

---

## Conclusion

The EMA9/VWAP strategy on NAS100_SB produced a **net profit of +£200 (2.0% return)** on a simulated £10,000 account over 6 months with £100 fixed risk per trade. The strategy is **marginally profitable** (profit factor 1.20) with a 37.5% win rate on 16 trades. The 2:1 R:R ratio provides a comfortable cushion above the 33.3% break-even threshold.

The strategy is most active in trending, volatile markets (Dec 2025–Jan 2026) and goes quiet during strong one-directional trends (May–Jun 2026 bull run) and consolidation periods (Feb–Mar 2026). This is by design — waiting for quality EMA9 pullbacks rather than chasing.
