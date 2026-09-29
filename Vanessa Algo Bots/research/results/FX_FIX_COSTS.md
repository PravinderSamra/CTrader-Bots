# Strategy C (London 4pm fix reversal) — FTMO cost check (2026-09-29)

## FTMO EURUSD costs
| Item | Figure | Source / confidence |
|---|---|---|
| Commission | $5.00 per lot round turn ($2.50 per side) | PropSpread published FTMO schedule, 8 Aug 2026 (MT5). One older source says $3. **Confirm in the FTMO cTrader symbol info.** |
| Spread | 0.2–0.7 pip typical | Secondary reviews only; no independent measured statistics published yet |
| Indices / metals commission | $0 / $5.81 per lot round turn | PropSpread, same schedule |

At EURUSD ≈ 1.17, one lot = about $117,000 notional, so $5 = **0.43 bp (≈0.5 pip)**.
Total round trip = 0.7–1.2 pips ≈ **0.6–1.0 bp** per trade.

## Against the edge in the paper (Krohn, Mueller & Whelan 2024, 1999–2018, before costs)
| Leg | Gross per day | Net at FTMO cost | Share kept |
|---|---|---|---|
| After the London fix: long EUR 16:00 → 21:00 UK | ≈2.9 bp (7.22% a year) | ≈1.9–2.3 bp | 65–80% |
| Before the fix: long USD 08:00 → 16:00 UK | ≈1.7 bp (dollar basket, not EUR-specific) | ≈0.7–1.1 bp | 40–65% |

The paper's cost-adjusted result for EUR around the London fix was Sharpe 0.65, using wider
indicative-quote spreads than a modern ECN feed. FTMO's costs are low enough that the post-fix
leg keeps most of its edge **if the 1999–2018 effect still exists**.

## Open question (the real test)
Has the effect survived after 2018? Strategies A and B both faded in recent data. Next step: test
both legs on 2019–2026 EURUSD H1 prices (enough, since entries/exits sit on the hour: 08:00, 16:00, 21:00 UK),
pre-registering the rules first, with 1.0 bp round-trip cost as the base case and 2.0 bp as the stress case.
