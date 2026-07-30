# FROZEN CONFIGURATION V4 — committed BEFORE the holdout is scored

Development finished. This file is committed before `23_v4_holdout.py` is ever run.
Nothing below may change after holdout results are seen.

**Dev set:** 2021-07-18 → 2025-07-16. **Holdout:** 2025-07-17 → 2026-07-16 (untouched).
**Dev configurations evaluated:** ~75 (scripts 20, 21, 22). Multiple-testing haircut applies.

## Module 1 — "NYX" (NY opening-range expansion)
| Element | Rule |
|---|---|
| Opening range | high/low of **13:30–14:00 UTC** |
| Width gate | trade only if 0.04 ≤ OR width / ATR20 ≤ 0.50 |
| Context filter | profile gap-trap: if the day opened **above** prior value, no short; **below**, no long |
| Entry | stop order at each OR edge, first fill cancels the other |
| **Stop** | **0.25 × ATR20** (a fixed volatility unit, NOT the OR far side) |
| Partial | at **+1R** take **33%**, then move stop to break-even |
| Exit | runner flat **20:55 UTC** |
| Max | one trade per day |

## Module 2 — "CARRY" (overnight flow drift)
| Element | Rule |
|---|---|
| Entry | long at **20:00 UTC**, **Mon–Thu** only |
| Stop | 0.50 × ATR20 |
| Exit | **02:00 UTC** next dealing day. No target. |

## Sizing (both variants scored on holdout)
- **Variant A** — 1.0% of equity per trade, both modules.
- **Variant B** — 1.0% NYX, 0.5% CARRY (risk-weighted: CARRY's dev return/DD was 2.53 vs NYX 5.17).

## Costs
$0.30 spread + $0.07 commission + $0.10 slippage = **$0.47/oz** round trip, every trade.

## Dev-set results (for comparison against holdout)
| | n | Win% | Expectancy | PF | Sharpe | maxDD | return/DD |
|---|---|---|---|---|---|---|---|
| NYX | 694 | 53.6% | +0.086R | 1.21 | 1.01 | −11.6R | 5.17 |
| CARRY | 802 | 47.5% | +0.098R | 1.22 | 1.16 | −31.0R | 2.53 |
| **Portfolio** | 1,496 | 50.3% | +0.093R | 1.22 | **1.54** | −28.4R | 4.87 |

Dev account (Variant A, $100k @1%): final $360,995, CAGR +38.8%, max equity DD −25.7%.
Module daily-R correlation: **+0.003** (genuine diversification).

## Pre-declared pass/fail criteria for the holdout
The system is called validated only if, on the untouched holdout:
1. Portfolio expectancy > 0 after full costs;
2. Portfolio expectancy ≥ 50% of the dev figure (i.e. ≥ +0.047R) — some decay is expected, collapse is not;
3. NYX individually > 0 (the module that passed the random-entry null);
4. Max equity drawdown ≤ 1.5× the dev figure.

If it fails, the result is reported as a failure. No re-tuning.
