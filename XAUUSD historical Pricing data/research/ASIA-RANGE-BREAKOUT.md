# Asia Range Breakout — Conditional Research

Scripts: `25_asia_range_study.py` (descriptive), `26_asia_strategy.py` (strategy build). Costs $0.25/oz (your Razor account). Asia range = **22:00–06:59 UTC** (11pm–8am UK summer). Breakout scan 07:00–16:00.

---

## 1. The number that frames everything

After the first break of the Asia range, price travels **+1.0 × range before retracing −0.5 × range only 26.1% of the time**. A 2:1 payoff needs **33.3%** just to break even before costs.

**So the naive Asia breakout is a losing proposition.** The job is to find conditions that lift it above 33.3%.

Equally important: **median MFE after a break is only 0.49 × range.** Most breakouts run about half the range and stop. Any plan targeting a full range-width is aiming at something that happens roughly a quarter of the time.

## 2. Your first hypothesis — range size — is CONFIRMED, and it's the biggest effect found

| Asia range (× ATR20) | Days | Sustain rate |
|---|---|---|
| < 0.25 | 101 | **33.7%** |
| 0.25 – 0.35 | 283 | **31.4%** |
| 0.35 – 0.45 | 249 | 24.9% |
| 0.45 – 0.60 | 181 | 26.0% |
| 0.60 – 0.80 | 109 | **16.5%** |
| > 0.80 | 59 | **10.2%** |

Clean, monotonic, and large: small ranges sustain **three times** better than large ones. Your reasoning was right — a wide Asia range means the move has largely happened already, and breaking it leads nowhere. Median range is 0.39 × ATR20, so "small" means roughly under $40 when gold's daily range is $100.

## 3. Your second hypothesis — PDH/PDL magnets — is CONFIRMED, but inverted from the usual belief

| Prior-day level position | Days | Sustain |
|---|---|---|
| Already cleared, >0.5R behind | 100 | **21.0%** |
| Already cleared, 0–0.5R behind | 173 | 22.0% |
| **Ahead 0–0.5 range** | 201 | **32.8%** |
| Ahead 0.5–1 range | 176 | 25.6% |
| Ahead 1–2 ranges | 204 | 27.0% |
| Ahead > 2 ranges | 128 | 24.2% |

**The magnet works — but only when it's close.** A prior-day high sitting just above your upside break (within half a range) is the best condition in the table. And the common belief that "breaking into open space runs furthest" is **backwards on gold**: when PDH/PDL has already been cleared, sustain drops to 21–22%, the worst cells in the study.

**Combined with range size (your exact combined hypothesis):**

| | Level 0–1R ahead | Level >1R ahead | Level already cleared |
|---|---|---|---|
| **Small range <0.35** | **37.0%** (n=146) | 29.5% (n=183) | 27.3% (n=55) |
| Mid 0.35–0.60 | 28.7% (n=181) | 22.9% (n=118) | 22.9% (n=131) |
| Large >0.60 | 9.8% (n=51) | 16.1% (n=31) | 16.3% (n=86) |

Best cell 37.0%, worst 9.8%. Your combined thesis is correct — small range **plus** a prior-day magnet ahead is genuinely the best setup, and it clears the 33.3% break-even bar.

## 4. Other anomalies found

| Condition | Sustain | vs 26.1% baseline |
|---|---|---|
| Asia range sits entirely **inside** the prior day's range | **30.0%** (n=523) | +3.9pp |
| Asia range **outside/overlapping** prior day | 21.6% (n=459) | −4.5pp |
| Break occurs 10:00–12:00 UTC | **33.3%** | +7.2pp |
| Break occurs 12:00–16:00 UTC | 15.8–16.8% | **−9 to −10pp** |
| **Sunday** session | **17.9%** | −8.2pp (worst day) |
| Monday | 30.0% | +3.9pp |
| Short breaks | 28.7% | +2.6pp |
| Long breaks | 23.8% | −2.3pp |
| Asia closed in its **top third**, then breaks UP | 23.3% | already extended |
| Asia closed in its **bottom third**, then breaks UP | **13.8%** | worst structure cell |

The timing result matters: **late breaks are worthless.** If the Asia range is still intact at midday, the day has already told you it isn't a breakout day.

## 5. Your entry idea — tested, and it's worse than the simple version

You proposed: wait for the break, wait for a retrace that doesn't re-enter the range, then enter with the stop below the pre-breakout swing.

| Entry model | n | Win% | Expectancy |
|---|---|---|---|
| **Enter immediately at the break** | 982 | 51.4% | **+0.004R** |
| Wait for the retrace | 936 | 49.4% | −0.037R |
| Retrace + confirmation close | 793 | 49.7% | −0.021R |

**The retrace entry is worse**, and this is now the *second* independent time this dataset has said so (the earlier Asia-pullback study found the same). The reason is a selection effect: demanding a pullback filters you *into* the weak breaks. The strong breaks — the ones that produce the sustain statistic — mostly never come back to the level. You get a better price on a worse population of trades, and the second effect is larger.

**Stop placement — the swing-low idea is also not the best.** Tested with filters applied:

| Stop placement | Cost as % of risk | Expectancy |
|---|---|---|
| **Opposite side of the Asia range** | **3.0%** | **+0.107R** |
| Pre-break swing (60 min) | 4.7% | +0.083R |
| 0.25 × ATR20 | 3.9% | +0.049R |
| Pre-break swing (30 min) | 5.1% | −0.071R (unfiltered) |
| Range midpoint | 5.2–6.1% | negative |
| Fixed 0.35 × range | 7.3% | negative |

The pattern is identical to every other study in this project: **wider structural stops win because cost stops being a meaningful fraction of risk.** The tighter the swing stop, the more of your edge the spread eats. The far side of the Asia range is the best stop tested.

## 6. But it still does not become a tradeable system — here is the honest verdict

The best full configuration (break entry, stop at the far side of the range, range 0.15–0.45 ATR, prior-day level 0–0.5 range ahead) produces **+0.107R over 149 trades on the dev set**. That looks tradeable. Year by year it is not:

| Year | Trades | Expectancy |
|---|---|---|
| 2021 | 23 | **−0.479R** |
| 2022 | 40 | +0.064R |
| 2023 | 37 | −0.041R |
| 2024 | 41 | **+0.441R** |
| 2025 (part) | 8 | +0.531R |

**2024 alone contributes more than the entire five-year profit.** Two of five years are negative. The holdout gave n=27 trades — far too few to settle anything.

And the honesty check that matters most: across this study I examined roughly **110 combinations** of entry, stop, target and filter. With that many, about five would look profitable at p<0.05 by pure chance. A cell that is positive overall, negative in two of five years, and carried entirely by one year is exactly what mining noise looks like.

**Verdict: do not trade the Asia range breakout as a standalone system.** The conditional statistics in sections 2–4 are real and well-sampled. They just don't survive the journey from "this condition has a higher sustain rate" to "this makes money after costs, consistently, across regimes."

## 7. The genuinely useful discovery — and it runs the opposite way

I tested whether Asia-range size predicts the performance of your **validated 13:30 NYX system**. It does — **in the opposite direction**:

| Asia range | NYX expectancy (dev) | NYX expectancy (holdout) |
|---|---|---|
| Small < 0.30 ATR | +0.060R | **−0.254R** |
| 0.30 – 0.45 | +0.108R | +0.116R |
| 0.45 – 0.60 | +0.130R | +0.008R |
| **Large > 0.60 ATR** | **+0.306R** | **+0.127R** |

**A large Asia range is bad for the Asia breakout but good for the NY breakout** — and the direction holds on both dev and holdout. The mechanism is sensible: a wide overnight range means volatility is already switched on, and that volatility carries into the New York session where it fuels the 13:30 expansion. Meanwhile the Asia range itself is "spent," so breaking it leads nowhere.

I tested filtering NYX to *skip* large-Asia-range days and it made things **worse** (holdout +0.014R vs +0.047R unfiltered) — so the practical instruction is a negative one, and a useful one:

> **Never skip your NYX trade because the overnight range was wide. Those are your best days.**

I would stop short of sizing *up* on them — the sub-bucket samples are small (n=106 holdout) — but if you were looking for one place to lean, the evidence points there rather than at the Asia breakout.

## 8. What to actually do

1. **Don't run the Asia breakout as a system.** The best version fails the stability test.
2. **Keep the range on your chart as context**, and read it like this:
   - Wide overnight range (>0.6 × ATR20) → expect a good NY session; take your 13:30 trade with full confidence.
   - Narrow range, prior-day high/low sitting just beyond, still intact at 10am → the *only* configuration where an Asia break has a real edge (37%). If you want a discretionary trade, that's the one — with the stop at the opposite side of the range, entered on the break, not the retrace.
   - Range still unbroken after midday → forget it for the day.
   - Sunday → ignore Asia breaks entirely.
3. **Two rules confirmed for the third time in this project:** don't wait for retraces on breakouts (they select the weak ones), and put stops wider and structural (tight stops let costs eat the edge).
