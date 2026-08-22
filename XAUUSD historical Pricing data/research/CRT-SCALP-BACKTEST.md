# CRT Gold Scalp — Backtest Report vs Specification v1.0

**Scripts:** `18_crt_scalp.py` (engine), `19_crt_gates.py` (acceptance gates, sensitivity, account report). Raw output in `output/18_*.txt`, `output/19_*.txt`.
**Data:** 1,762,482 M1 bars, 2021-07-18 → 2026-07-16. H1/H4 resampled from the same series, as the spec requires.
**Account:** $100,000, risking 1% per trade.

---

## 1. Headline result

| | |
|---|---|
| Trades | 2,722 (≈10.4/week) |
| Win rate | 28.8% |
| **Expectancy** | **−0.3092 R/trade** |
| Profit factor | **0.66** |
| Avg win / avg loss | +2.11R / −1.29R |
| Max drawdown | −861R |
| Longest losing run | 21 |
| **$100k @ 1% risk** | **account destroyed** |

**In real terms:** risking a fixed $1,000/trade (1% of the starting balance), the account is **bust inside 9 months** — down $30,519 in the worst month. With compounding 1% risk (position shrinks as equity falls), $100,000 decays to **$13** over the five years, a −100.0% return with a −100% peak-to-trough drawdown.

**Weekly / monthly breakdown** (compounding, so later figures shrink with the account):

| | Mean | Median | Best | Worst | % positive |
|---|---|---|---|---|---|
| **Weekly** | −$383 | −$7 | +$9,053 | −$11,508 | 24% of 261 weeks |
| **Monthly** | −$1,639 | −$54 | +$7,275 | −$17,264 | 15% of 61 months |

Fixed-$1,000-risk monthly P&L before the account died: Aug 2021 +$5,836 · Sep −$15,367 · Oct −$6,012 · Nov −$2,489 · Dec −$19,257 · Jan 2022 −$30,519 · Feb −$26,254 · Mar −$4,892 → **account gone**.

## 2. Acceptance gates (spec §07)

| Gate | Result | Detail |
|---|---|---|
| **1 · Random-entry null** | ❌ **FAIL** | Null distribution (1,000 runs, identical geometry/sessions/costs): p5 = −0.366R, **median = −0.318R**, p95 = −0.270R. Strategy = **−0.309R** — sits *inside* the null, indistinguishable from random entry. |
| 2 · Direction test | ✅ pass (hollow) | Fade −0.309R vs continuation −0.347R. Reversion beats continuation, but **both are catastrophic** — this gate only shows which way to lose more slowly. |
| 3 · Session ablation | ✅ pass (hollow) | Killzones on −0.309R vs all-day −0.417R. The filter reduces the bleed rate; it does not create edge. |
| **4 · Out-of-sample** | ❌ **FAIL** | IS (2021-07→2024-06) −0.329R; OOS (2024-06→2026-07) −0.280R. Negative in both halves. |
| **5 · Cost stress** | ❌ **FAIL** | Zero cost **+0.0246R** · 1× cost −0.3092R · 2× cost −0.6431R. |
| 6 · Multiple-testing haircut | n/a | 23 combinations evaluated; **none positive**, so there is nothing to deflate. |

**Gate 1 is the verdict.** Random entries taken in the same killzones, with the same stop distances and the same 2.5:1 target geometry, produce a median expectancy of −0.318R. The CRT signal produces −0.309R. **The sweep-and-fail pattern contributes essentially nothing** — the outcome is determined by the stop/target geometry and the cost, not by the setup.

## 3. Why it fails — the arithmetic

The spec's **Lever 2** ("tight structural stop → small stop against range-width target = high reward:risk. This is the real profit engine") is precisely the mechanism that destroys it.

| Stop width | Cost as % of the risk unit |
|---|---|
| p25 — $1.09/oz | **43.1%** |
| median — $1.88/oz | **24.9%** |
| p75 — $3.44/oz | 13.7% |

A tighter stop does improve the R:R ratio on paper — but R shrinks in dollars, so a fixed $0.47/oz round-trip cost eats a *larger fraction of every R*. Expectancy by stop-width quintile proves the drag is mechanical, not behavioural:

| Stop quintile | Gross expectancy | Cost drag | Net |
|---|---|---|---|
| Q1 (tightest) | +0.294R | **−0.795R** | −0.501R |
| Q3 | +0.011R | −0.251R | −0.240R |
| Q5 (widest) | +0.006R | −0.075R | −0.069R |

**Where the money went** (fixed $1,000 risk, 2,722 trades):

- Gross P&L at zero cost: **+$66,922**
- Spread + commission + slippage paid: **−$908,685**
- Net: **−$841,763**

You pay roughly **$909,000 in transaction costs to harvest $67,000 of gross edge.**

**Break-even cost:** each $0.01/oz of round-trip cost drains 0.0071R per trade. Against a gross expectancy of +0.0246R, the strategy breaks even at **$0.035/oz round trip** — about 3½ cents. Realistic raw-ECN gold is $0.15–0.25/oz all-in; retail spread-betting is $0.30–0.50. **The strategy needs costs ~14× tighter than modelled just to reach zero**, before any profit. No broker relationship closes that gap.

And note the gross edge itself is only +0.0246R — statistically indistinguishable from zero. Even at literally zero cost this is not a business.

## 4. Parameter sensitivity — 23 combinations, none positive

| Variant | n | Win% | Expectancy |
|---|---|---|---|
| **Default (H4)** | 2,722 | 28.8 | −0.3092 |
| TF_R = H1 | 6,491 | 31.2 | −0.3705 |
| δ = 0.05 / 0.25 ATR | 2,738 / 2,636 | 28.7 / 30.2 | −0.3135 / −0.2743 |
| W = 5 / 30 | 2,720 / 2,702 | 28.0 / 29.1 | −0.3238 / −0.3137 |
| Confirm B (MSS) | 3,290 | 31.5 | −0.2341 |
| Entry limit_RL / limit_Q25 / FVG | 2,371 / 2,199 / 1,844 | 23.1 / 22.3 / 26.1 | −0.3743 / −0.6172 / −0.3365 |
| Target Q75 / RH single | 2,721 / 2,722 | 27.0 / 24.7 | −0.2919 / −0.2987 |
| rng_min = 0.8 | 1,572 | 26.7 | −0.2758 |
| Break-even after T1 | 2,722 | 31.8 | −0.3087 |
| **NY killzone only (best)** | 1,309 | 32.5 | **−0.2211** |
| LDN only | 1,413 | 25.3 | −0.3909 |

The best cell in the entire grid still loses 22% of risk per trade. Notably the limit entries — which pay *less* cost — perform *worse*, because they only fill when price keeps going against you (adverse selection).

## 5. Implementation notes (spec §06 compliance)

- **Causality:** the engine walks M1 forward inside each range candle's trading window. The sweep extreme, the return-inside close, and every exit are detected bar-by-bar on closed-bar data only. Range levels come from the *previous closed* H4/H1 bar and are active during the following period. No forming-candle inspection.
- **DST:** killzones are evaluated in `Europe/London` local time via timezone conversion, so 07:00–10:00 and 13:30–16:30 stay correct across BST/GMT rather than drifting an hour twice a year.
- **Costs:** spread $0.30 + commission $0.07 + slippage $0.10 = $0.47/oz for market entries; limit entries pay $0.37 and require a genuine through-trade to fill.
- **Fidelity:** all seven entry steps, all nine grid parameters, both confirmation models, all four entry models and all three target models implemented as specified. Intrabar ambiguity resolved adversely (stop assumed hit first).

## 6. Verdict

**CRT sweep-fade does not work on XAUUSD.** It fails the random-entry null, the out-of-sample test, and the cost stress. Its apparent virtue — a very tight structural stop — is the mechanism that kills it, because on gold the round-trip cost is a quarter to a half of that stop distance. The setup itself carries no measurable predictive information: identical geometry with random entry times performs the same.

To be fair to the specification: it is a genuinely well-built document, and **its own §09 predicted this outcome** ("cost drag from M1 gold spreads… expect the edge to be modest, conditional"). The failure is in the strategy, not in the spec — and the spec's insistence on a random-entry null is exactly what exposed it. Most CRT backtests circulating publicly skip that gate and report look-ahead-inflated results.

**What this shares with everything else in this project:** the tested pattern is a *chart shape*, and chart shapes carry no directional edge on an instrument with Hurst ≈ 0.5. The three things that did survive testing here — the 22:00–02:00 flow drift, scheduled-expansion breakouts, and stored structural energy — all share the property of *not* being pattern recognition.

**If you want to salvage the idea:** the only structurally sound direction is to keep the sweep as a *context flag* rather than a trigger, and attach it to a system whose stop is wide enough that cost is <5% of risk (e.g. an ATR-scaled stop of $8–15 on current gold). That is a different strategy, not a tuned CRT — and nothing in this data suggests the sweep flag would add to it.
