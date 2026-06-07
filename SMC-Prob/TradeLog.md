# SMC-Prob — Trade Log

Live record of every signal `/smc-prob` outputs and its eventual outcome. This is what calibrates the Step 4 confluence-scoring weights over time — log every signal, win or lose, not just the wins.

After each trade card is output, log it here once the trade closes (or is invalidated before triggering).

---

## Log Format

| Date | Instrument | Direction | Confidence (X/14) | Grade | Entry | Stop | Target 1 | Result | R Achieved | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| _example_ | EURUSD | LONG | 12/14 | A | 1.0850–1.0855 | 1.0830 | 1.0900 | TP1 hit | +1.5R | Clean Asian sweep, NY KZ entry |

**Stand-asides ("no trade" verdicts) are logged too** — tracking *correct* stand-asides is just as important for calibration as tracking taken trades. A skill that finds confluence too eagerly is more dangerous than one that's appropriately disciplined; we need evidence of both behaviours to calibrate Step 4's weights honestly.

---

## Entries

### 2026-06-07 — XAUUSD_SB — NO TRADE (stand-aside)

| Field | Value |
|---|---|
| Data as of | 2026-06-05 ~20:55 UTC (Friday close — market closed at time of run, Sunday) |
| HTF Bias | Bearish — confirmed CHoCH/BOS on H4 (3 consecutive impulsive bearish candles, new swing low at 4311.80) |
| Zone | Discount (~8% above swing low; bias called for premium-zone shorts) |
| Verdict | **No qualifying setup** — bias and location contradicted each other; no LTF reversal confirmation for a counter-trend long either |
| What to watch | (1) Premium-zone short continuation near 4460–4515 with bearish OB; (2) sweep of 4311.80 + bullish 15M CHoCH for a counter-trend long |
| Outcome | _Pending — revisit at next London/NY session to see whether either watch condition plays out, and whether the "no trade" call was correct_ |
| Notes | First full end-to-end pipeline run. Also exposed a market-hours gap (data was stale weekend data, presented without a staleness caveat) — fixed in v1.2. See BUILD-LOG.md 2026-06-07 entry. |

_Revisit this entry once Monday's session opens — did the bearish bias play out from the premium zone as expected, or did price sweep the 4311.80 low and reverse? Either outcome is useful calibration data._
