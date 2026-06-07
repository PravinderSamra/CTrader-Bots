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

---

### 2026-06-07 — Walk-forward backtest log (XAUUSD_SB, simulated daily NY-KZ scans, 2026-05-04 → 2026-06-05)

Hand-replicated `/smc-prob XAUUSD_SB` once per sampled trading day at simulated NY KZ open (11:00 UTC), walking forward through ~5 weeks of historical H4/H1/M15 data with strict no-lookahead discipline (only bars closed at-or-before the scan timestamp informed each verdict; subsequent bars used only to grade outcomes). Where Step 2/3 produced "bias present, no entry yet," the setup was followed forward (capped ~5 trading days) rather than re-scored as a fresh independent signal each day. See BUILD-LOG.md 2026-06-07 entry ("Walk-forward backtest") for full methodology and aggregate analysis.

| Date | Instrument | Direction | Confidence (X/14) | Grade | Entry | Stop | Target 1 | Result | R Achieved | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-05-04 | XAUUSD_SB | — | n/a (no-bias) | — | — | — | — | Stand-aside — correct | n/a | Ranging 4560–4660, no clear BOS/CHoCH on 4H/1H. Price chopped lower into 4500.79 then reversed into a huge rally — no clean directional entry was visible at scan time either way; standing aside was right call given the genuine ambiguity. |
| 2026-05-06 | XAUUSD_SB | LONG (bias only) | n/a (no-entry-yet) | — | watch: pullback to ~4577 (discount of 4500.79–4653 leg) | — | — | Expired — never triggered | n/a | Clean bullish BOS off 4500.79 low, but price had already run into premium (~4700) by scan time — correctly refused to chase. The planned discount-pullback never came; price kept trending straight to 4773 without offering the entry. Calibration note: in strong impulsive trends the "wait for discount" entry can simply not arrive. |
| 2026-05-08 | XAUUSD_SB | LONG | ~9/14 (est.) | B | 4648–4670 (OB/sweep zone, touched 05-10/11) | ~4640 (struct., below sweep low) | ~4750 (next BSL/prior high zone) | TP1 + far beyond hit | ~+5R | HTF bias present 05-08 (bullish, BSL 4764 swept, pullback to 4686–4716), no clean LTF entry at scan time — flagged "watch 4660–4690 OB on deeper pullback." Price swept down into that exact zone 05-10/11 with bullish structure fully intact, then rallied to a new high of 4773.31 — clean trigger, large win. |
| 2026-05-12 | XAUUSD_SB | — | n/a (no-bias) | — | — | — | — | Stand-aside — correct | n/a | Sharp, persistent pullback off the new 4773 high broke the most recent higher-low (4648) — early CHoCH signs, structure genuinely unclear (4H still technically bullish, 1H showing reversal). Correctly stood aside rather than buying the "discount" of a possibly-broken trend; price went on to fall ~150pts to 4531 by 05-15 — a long here would have been crushed. |
| 2026-05-14 | XAUUSD_SB | — | n/a (no-bias) | — | — | — | — | Stand-aside — correct but late | n/a | Tight 4668–4719 range, genuinely conflicting 4H/1H signals at scan time. The bearish breakdown began later that same session (4705→4630, continuing to 4531 next day). Avoided a wrong-side long, but the CHoCH evidence (break below ~4648 on 05-12) arguably should have resolved the bias a session earlier — possible sign Step 2's CHoCH-confirmation threshold lags real structural shifts by up to a day. |
| 2026-05-18 | XAUUSD_SB | SHORT (bias only) | n/a (no-entry-yet) | — | watch: bearish OB/FVG ~4570–4600 (premium of 4480–4589 leg) | — | — | → Triggered, see below | — | HTF bias bearish (clean BOS/CHoCH down from 4773 to 4480.27 swing low), price consolidating 4530–4574 — correctly waited for a premium-zone retrace rather than shorting mid-range. |
| 2026-05-19 (follow-through of 05-18 setup) | XAUUSD_SB | SHORT | ~12/14 (est.) | A | ~4580–4589 (premium OB, touched 05-18 21:00) | ~4595 (struct., above OB high) | ~4480 (SSL — prior swing low) | TP1 + far beyond hit | ~+6R | Price reached the watch zone (high 4589.01) the same evening with bearish bias fully intact, then broke decisively below 4480 SSL to 4465, continuing the broader downtrend toward 4401 over the following week. Clean A-grade trigger from a patient "no entry yet" call — exactly the walk-forward refinement this backtest is testing for. |
| 2026-05-22 | XAUUSD_SB | — | n/a (no-bias) | — | — | — | — | Stand-aside — correct | n/a | Choppy consolidation 4490–4580 after the bearish leg exhausted near 4453 — genuine ranging, no clear resolution either way. Price chopped sideways for several days (through 05-25/26) — a directional trade either way would have been hurt; standing aside was right. |
| 2026-05-26 | XAUUSD_SB | SHORT (bias forming) | n/a (no-entry-yet) | — | watch: confirmed break/sweep below ~4490–4500 with bearish OB on retest | — | — | → Triggered, see below | — | Fresh bearish CHoCH forming as price rolled over from the 4580 high and tested range support — correctly flagged as "forming, not yet confirmed" rather than shorting the test of support pre-emptively. |
| 2026-05-27 (follow-through of 05-26 setup) | XAUUSD_SB | SHORT | ~10/14 (est.) | B | ~4490 (breakdown retest/OB) | ~4520 (struct., above OB/range high) | ~4400 (round-number SSL / prior structure) | TP1 hit, then violent V-reversal stopped remainder | ~+1.5R blended (+3R on TP1 half, ~breakeven/-0.5R on runner) | Confirmed breakdown below 4497 swept to 4401 (T1 hit, ~+3R on the 50%-close portion) before an extreme V-shaped reversal (4366→4511 in ~12h) would have stopped the remaining runner. Net positive but a good illustration of why "close 50% at T1" matters — the full-size hold would have round-tripped to a loss. |
| 2026-05-28 | XAUUSD_SB | — | n/a (no-bias) | — | — | — | — | Stand-aside — correct | n/a | Chaotic post-sweep V-reversal in progress (fresh SSL grab at 4366.73, ripping back to 4433 within hours) — genuinely unresolved structure, classic whipsaw conditions. Neither a long nor a short offered a clean low-risk entry; price round-tripped (bounced to 4595, then reversed back to new lows by 06-05). Correctly avoided the chop. |
| 2026-06-01 | XAUUSD_SB | SHORT (bias only) | n/a (no-entry-yet) | — | watch: bearish OB/FVG ~4540–4575 (premium retrace zone) | — | — | → Triggered, see below | — | HTF bias bearish (clean lower-high at 4595, breaking support through 4517→4490), but price had already driven into discount by scan time — correctly refused to chase a counter-zone short and flagged the premium retrace to watch for instead. |
| 2026-06-02 (follow-through of 06-01 setup) | XAUUSD_SB | SHORT | ~12/14 (est.) | A | ~4535–4541 (premium retrace high, touched 06-02 ~05:00–09:00) | ~4550 (struct., above retrace high) | ~4400 (round-number SSL) | TP1 + far beyond hit | ~+9R | Price retraced cleanly into the watch zone (high 4541.54) with the bearish structure fully intact (no break of the 4595 lower-high), reversed hard, and continued straight through 4400 to a new swing low of 4311.80 by 06-05 — by far the largest winner of the sample, and the clearest illustration of the walk-forward refinement paying off (a same-day scan would have flagged "no entry," but following the setup forward caught an A-grade trigger two sessions later). |
