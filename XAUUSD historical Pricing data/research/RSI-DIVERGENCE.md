# Price vs RSI — The Complete Divergence Combination Matrix

Scripts: `15_rsi_divergence.py` (full matrix), `16_rsi_div_stress.py` (significance, magnitude, session, triple, costed backtest), `17_rsi_q3_verify.py` (verification of the one interesting cell). Raw output in `output/`.

---

## 1. Method — and the one thing most divergence studies get wrong

**Pivots are fractal:** bar *i* is a swing high if its high exceeds the *k* bars either side. Critically, **a pivot is not knowable until *k* bars after it forms.** Every probability below is measured from the close of the **confirmation bar** (*i+k*), not from the pivot itself. Studies that measure from the pivot bar report large fake edges — they are measuring a move that had already happened by the time you could have seen the signal.

RSI(14) is read at the pivot bar. Each pivot high is compared with the previous pivot high (and each low with the previous low), producing the full 2×2 matrix per side. Tested on **5m and 15m**, with k=3 and k=6, giving 22,000–66,000 pivot events.

**"Did it reverse?" is defined two ways:**
- **Barrier race** (the tradeable question): from the confirmation close, does price travel 1×ATR in the reversal direction *before* travelling 1×ATR against it?
- **Structure break** (the Dow-theory question): does price break the prior opposing swing before exceeding the signal pivot's extreme?

Every result is compared with the **base rate** of all pivots on that side — because a 55% reversal rate is worthless if the base rate is 55%.

## 2. The complete matrix (15-minute, k=3)

### At pivot HIGHS — P(1 ATR down before 1 ATR up). Base rate: **50.1%**

| Price | RSI | Name | N | Reversal % | Edge vs base | z | Verdict |
|---|---|---|---|---|---|---|---|
| HH | HH | Confirmed uptrend | 4,143 | 50.4% | +0.3pp | +0.41 | noise |
| **HH** | **LH** | **Regular bearish divergence** *(your example)* | 1,414 | **52.6%** | **+2.5pp** | +1.87 | not significant |
| LH | HH | Hidden bearish divergence | 1,329 | 47.6% | −2.4pp | −1.77 | not significant |
| LH | LH | Confirmed downtrend | 4,235 | 49.7% | −0.4pp | −0.49 | noise |

### At pivot LOWS — P(1 ATR up before 1 ATR down). Base rate: **50.5%**

| Price | RSI | Name | N | Reversal % | Edge vs base | z | Verdict |
|---|---|---|---|---|---|---|---|
| LL | LL | Confirmed downtrend | 4,097 | 49.1% | −1.4pp | −1.81 | not significant |
| **LL** | **HL** | **Regular bullish divergence** | 1,267 | **50.4%** | −0.1pp | −0.10 | noise |
| HL | LL | Hidden bullish divergence | 1,438 | 50.8% | +0.3pp | +0.25 | noise |
| HL | HL | Confirmed uptrend | 4,449 | 51.7% | +1.2pp | +1.65 | not significant |

**Not one cell in the matrix reaches statistical significance** (all |z| < 2.0, and with ~40 hypotheses tested the Bonferroni bar is |z| > 3.02). The 5-minute matrix is the same story with edges of ±0.7pp. Your specific scenario — uptrend intact, price makes a HH, RSI makes a LH — is the **best cell in the whole study at 52.6%**, i.e. it flips a coin that lands your way 52.6 times out of 100 instead of 50.

### Adding the trend-context requirement (your exact setup)

Requiring the prior structure to be a genuine uptrend (previous high > the one before **and** previous low > the one before) before the bearish divergence: **52.5%**, edge +2.4pp. On 5m it drops to 49.6% — *worse* than base. The context filter adds nothing.

### RSI overbought conditioning

Bearish divergence with RSI > 70 at the pivot: **50.6%** (n=156) — the "textbook perfect" setup performs *worse* than divergence alone. Bullish divergence with RSI < 30: **46.2%** (n=119), i.e. below base rate.

## 3. Why the "structure break" numbers look impressive but aren't

The structure-break column shows bearish divergence breaking the prior low **55.5%** vs a 51.0% base, and the LH+RSI_LH class at **60.5%**. This is **definitional confounding, not predictive power**: a pattern that already contains a lower high is by construction closer to a lower low. The barrier race — which measures from an actual entry price with symmetric targets — removes this artifact, and the effect evaporates.

## 4. Everything else tested

| Test | Result |
|---|---|
| **Divergence magnitude** (RSI gap quartiles) | Non-monotonic. Q1 small −1.5pp, Q2 −1.3pp, **Q3 +9.2pp**, Q4 large +3.6pp — the largest divergences do *not* work best |
| **Session** (Asia / London / NY) | Asia +4.0pp (z=1.77), London +1.7pp, NY +1.5pp — all noise |
| **Triple divergence** (3 diverging pivots) | 52.1% vs 52.6% for double — the third swing adds **nothing** |
| **Timeframe** | 5m worse than 15m; wider swings (k=6) worse than k=3 |

## 5. The one interesting cell — and why it still doesn't pay

**15m bearish divergence with a *moderate* RSI gap (3.8–7.3 points)** raced 1 ATR down-first **59.2%** of the time (n=353, z=+3.44 — the only cell that clears Bonferroni). It survived every robustness check I threw at it:

- By year: 54%, 56%, 69%, 64%, 49%, 70% — positive in 5 of 6 years
- Split-half: 60.5% (2021–23) vs 58.1% (2024–26) — stable
- Re-binning at 3/5/6/10 quantiles: the middle-gap bin keeps showing 59–61%

There's even a plausible mechanism: a *tiny* RSI gap is measurement noise, while a *huge* gap usually means the rally already failed and you're late. A moderate gap is the genuine "momentum quietly leaving while price grinds one more high" case.

**And it still loses money.** The costed backtest (entry at confirmation close, stop where it structurally must go — just beyond the pivot high):

| Take-profit | n | Win% | avgR | Consistency |
|---|---|---|---|---|
| 1.0 R | 319 | 52.4% | **−0.082** | 3 of 6 years positive |
| 1.5 R | 319 | 43.9% | −0.045 | 3 of 6 |
| 2.0 R | 319 | 37.0% | −0.032 | 3 of 6 |
| 3.0 R | 319 | 29.2% | +0.023 | 3 of 6 — noise-level |
| No TP (timeout) | 319 | 10.3% | −0.163 | 2 of 6 |

**The reason is geometry, not prediction.** The stop must sit beyond the pivot high, which is a **median 1.51 ATR away**, while the reversal target is 1 ATR. You are right 59% of the time and still lose, because you risk 1.5 to make 1. This is the single most instructive result in the study: *being right more often than chance is not an edge — the payoff structure decides.*

## 6. Verdict and practical guidance

**RSI divergence is not an early reversal indicator on XAUUSD.** Across ~66,000 pivot events, every combination — regular bearish, regular bullish, hidden bearish, hidden bullish, with and without trend context, with and without overbought/oversold confirmation, double and triple, on 5m and 15m — sits within ±2.5pp of a coin flip, none significantly, and the one cell that clears the significance bar is unprofitable because of stop geometry.

This is exactly what the process diagnostics predicted (`MATH-PHYSICS-VIEW.md`): RSI is a deterministic function of past closes, and Hurst = 0.497 means **no function of past prices predicts the sign of the next move**. A divergence is a re-description of recent price history, not new information.

**What to do with this practically:**

1. **Do not take entries from divergence.** Not with confirmation, not with trend context, not at RSI extremes.
2. **If you use it at all, use it as a size modifier, never a signal** — e.g. if you are already long from a validated event (NY ORB, aftershock) and a 15m bearish divergence with a moderate RSI gap prints, that is weak justification to take partials early. It is worth roughly 2–9pp of probability, which is real but far too small to originate risk.
3. **The general law this confirms for the fourth time in this project:** indicator-derived patterns (RSI divergence, trend/reversal states, profile levels, streaks) carry no directional edge on this instrument. Edges live in **scheduled flows** (overnight drift), **expansion events** (ORB, post-jump aftershocks), and **stored structural energy** (the London-respected Asia range).
