# XAUUSD Through the Eyes of a Mathematician / Physicist

Scripts: `08_math_physics.py` (process diagnostics), `09_physics_strategies.py` (strategies derived from them). Raw output in `output/`. All costs $0.40/oz RT.

The brief: find the methodology for "regular and sustained R:R returns daily — moving the needle, not a low profit factor averaging out." This document answers that honestly, from the measurements.

---

## 1. What kind of physical system is this? (measured, not assumed)

| Property | Measurement | Interpretation |
|---|---|---|
| Hurst exponent (5m base) | **H = 0.497** (0.49–0.50 every year) | Price is a near-perfect random walk in *direction*. No memory. |
| Variance ratios VR(q), 10min–10h | 0.97–1.01 everywhere | Same verdict at every intraday scale. No exploitable trend/reversion in raw returns. |
| Runs test | P(continuation after k same-sign bars) = **47.6–49.2%** for all k=2..5, at 15m and 1h | Streaks mean nothing. "Three green candles" carries zero information. |
| Daily range autocorrelation | **0.79** (lag 1), 0.48 at lag 20 | Volatility has *massive* memory. |
| Next-day range forecastability | **R² = 0.58** from ATR5+ATR20 | Tomorrow's *movement size* is ~58% predictable. Tomorrow's *direction* ~0%. |
| Tail exponent (Hill, 5m) | **α ≈ 2.8** both tails | Fat tails: variance barely finite, 4th moment infinite. Rare huge bars dominate long-run P&L. |
| Jump frequency | 4σ 1m jumps on 0.55% of bars (Gaussian: 0.006%) — **90× Gaussian** | This is a jump-diffusion process, not Brownian motion. |
| Jump clustering | **P(another jump within 60min) = 67.5%** vs 33% baseline | Jumps arrive in bursts (Hawkes-like self-excitation). Vol events are aftershock sequences. |
| Jump timing | 52% of all jumps in 12:00–14:59 UTC | The "earthquakes" are scheduled: US data + COMEX open. |
| Session anisotropy | Asia VR(8)=1.06 (mildly trending), **London VR(32)=0.90 (mean-reverting)**, NY ≈ 1.0 | The medium is not isotropic: London stretches and snaps back; NY propagates. |
| Drift localisation | All 5-year drift in **22:00–02:00 UTC** (t=5.45); NY net zero | The only persistent directional force is a *time-of-day* flow, not a price pattern. |
| Compression→expansion? | After a <0.6×ATR day: next day 0.89×ATR (below avg). NR4 → 0.97×ATR (≈avg) | **The folk theorem is false at daily scale.** Quiet begets quiet (vol persistence), not explosions. |

## 2. The first-principles conclusion (read this before the strategies)

The direction process is a **martingale**: H = 0.5, VR = 1, runs at chance, autocorr ≈ 0. Mathematically, that means **no function of past prices alone predicts the sign of the next move** — at any intraday horizon, in any year of this sample. This is the strongest and most repeatable result in the entire dataset.

Therefore the request for "regular sustained R:R daily, moving the needle every day" has a precise mathematical answer: **it is not on offer from this price series.** Any daily-certainty method is either curve-fit noise or hidden risk (short-vol behaviour: many small wins, occasional catastrophic loss — exactly what the fat tails punish). A trader's daily P&L here is irreducibly ~95% noise; **edge only becomes visible through aggregation** (law of large numbers over 30–100+ trades). That's not pessimism, it's the measured structure of the medium.

What the physics *does* offer — and these are genuinely strong — are three exploitable asymmetries:

1. **Volatility is predictable even though direction is not** (R²=0.58 vs ~0). → You can know *when the market will move big* with useful accuracy. Trade expansion, size by forecast.
2. **The tails are fat and jumps self-excite.** → Payoff convexity beats win rate. Structures that risk 1 to make an *unbounded* right tail align with the medium; anything that caps winners (TPs) fights it. Empirically confirmed three independent times in this project: ORB with 2R TP lost a third of its edge; the Asia-scalp TP variants underperformed; the post-jump straddle only works with no TP.
3. **Time-of-day is not homogeneous.** Drift lives at 22:00–02:00; variance lives at 12:00–16:00; London overextends and reverts. The clock is a real coordinate of this system — most retail analysis ignores it.

## 3. Strategies derived from the physics — with test results

### ✅ C3. Post-jump expansion ride ("aftershock trade") — new, works

**Physics:** jumps cluster (67.5% aftershock rate) and tails are fat → after the *first* 4σ jump, elevated probability of large follow-on movement in *some* direction within hours.

**Steps:**
1. Compute rolling 1-day σ of 1m returns. A 1m bar with |return| > 4σ between **13:00–16:30 UK** = trigger (typically the 13:30 data drop or COMEX open).
2. Wait 5 minutes after the jump bar. Note price P.
3. Place OCO brackets: buy-stop at P + 0.15×ATR20, sell-stop at P − 0.15×ATR20.
4. First fill wins; stop = the opposite bracket (risk = 0.30×ATR).
5. **No take-profit.** Exit after 4 hours or at 21:00 UK, whichever first.

**Result:** 870 trades · 43.8% win · **+0.057R/trade** · positive 5 of 6 years (only 2021 negative) · maxDD −33R. Take-profit versions of the same trade: ≈ 0 or negative — the entire edge is the uncapped tail.

### ✅ Vol-targeted sizing (applies to every strategy you run)

**Physics:** R²=0.58 range forecastability is the single most predictable thing in the data — use it where prediction actually works: **risk, not direction.**

**Steps:** position size = (fixed £ risk) ÷ (0.5 × forecast range), forecast range = 0.6×ATR5 + 0.4×ATR20. Recompute daily. This is why every backtest in this project is ATR-normalised; in £ terms it roughly doubles risk-adjusted return across a regime change like 2024→2026 versus fixed lots.

### ✅ Already-found strategies, now explained by the physics

- **Overnight drift (22:00–02:00)** = the drift-localisation result. It's a *flow* anomaly (Asian demand), not a price pattern — which is why it survives while chart patterns don't. Still the best Sharpe in the project (~1.6–1.9).
- **NY ORB, no TP** = expansion capture at the scheduled jump window with convex payoff. Its profits concentrate exactly where the jump statistics say they should.
- **NY-break Asia scalp** = same physics, conditioned on stored energy (range that survived London).

### ❌ Tested and failed — the diagnostics that did NOT convert to trades

- **Asia VWAP fade** (OU half-life 174min, pull of 13–17¢/5m toward VWAP — textbook mean reversion): **−0.45R/trade, loses every year.** The reversion is real *on average per bar*, but the deviations that reach 2σ are disproportionately the genuinely trending nights; costs plus the loss asymmetry destroy it. A perfect lesson: *a statistically significant process property is not a trade.*
- **London VWAP fade** (VR=0.90 says London mean-reverts): −0.20R/trade. Same failure mode, milder. (Only 2026 was positive — worth rechecking if the high-vol regime persists.)
- **Streak fading/following:** nothing at any k, any timeframe.
- **Compression breakout filters:** narrow days do *not* precede explosive days; vol clustering means the opposite.

## 4. The methodology (direct answer to the brief)

If the aim is "extract consistent profitability, moving the needle" — the mathematically defensible construction from this data is:

1. **Accept that daily consistency is impossible; engineer *monthly* consistency instead** by stacking independent small edges that trade different hours: overnight drift (22:00–02:00), NY ORB (13:30+), aftershock trade (event-triggered), NY-break Asia scalp (occasional). Their P&L streams are nearly non-overlapping in time → portfolio Sharpe adds roughly like √(sum of squares). Combined in-sample that's ~+4–5R/month average versus ~+1.7R for the best single sleeve. *(Note: ORB and aftershock can trigger on the same NY move — count them as one risk unit when both fire the same direction.)*
2. **Be always-convex:** no take-profits anywhere; structural stops; let every position own the fat tail. In an α≈2.8 medium, the trader who caps winners is systematically transferring the only free money to the trader who doesn't.
3. **Put the prediction where predictability exists:** size by forecast vol daily (R²=0.58), never by feel or fixed lots.
4. **Respect the clock:** drift hours for holding, jump hours for breakouts, London for nothing (it's the mean-reverting chop that killed every London strategy tested in this project).
5. **Judge performance on 50-trade blocks, never days.** With avg edge ≈ 0.06–0.13R/trade against per-trade σ ≈ 1R, the signal-to-noise of a single day is ~0.1 — mathematically invisible. Over 50 trades the edge is ~2σ visible; that's the shortest honest evaluation window.

The physicist's one-line summary: **you cannot predict where this system goes, but you can predict when it will move, how violently, and which way the standing flows lean — and the entire extractable edge lives in those three quantities plus payoff convexity.**
