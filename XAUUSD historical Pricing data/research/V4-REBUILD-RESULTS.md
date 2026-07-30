# From CRT Failure to a Validated System — Rebuild Report

Scripts: `20_v2_engine.py` (diagnosis ladder), `21_v3_engineered.py` (signal swap), `22_v4_portfolio.py` (frozen config + gates), `23_v4_holdout.py` (single holdout score). Protocol: `HOLDOUT-PROTOCOL.md`, config: `FROZEN-CONFIG-V4.md` — both committed *before* the holdout was scored.

---

## 1. The method

1. **Split first.** Holdout (2025-07-17 → 2026-07-16) locked away and committed before any optimisation. All development on 2021-07 → 2025-07.
2. **Fix one thing at a time**, measuring each in isolation, so I could tell which change did what.
3. **Freeze in writing**, with pass/fail criteria declared in advance.
4. **Score the holdout once.** No re-tuning permitted afterwards.

~75 dev configurations were evaluated. The holdout is the protection against that multiple-testing exposure.

## 2. What was broken and what each fix bought

CRT v1: **−0.3092R/trade, 28.8% win, account destroyed in 9 months.** Three failures, addressed in order:

| Fix | Change | Result on dev |
|---|---|---|
| **1 · Cost drag** | Stop moved from "just beyond the wick" to a **volatility unit (× ATR20)** | cost/risk **26.7% → 5.9%**; expectancy −0.227R → −0.096R |
| **2 · Exit structure** | Partial at +1R, then **stop to break-even**, runner to time exit | win rate **31% → 47%**, drawdown roughly halved |
| **3 · The signal** | — | **stalled at −0.044R** |

**The critical finding.** After fixes 1 and 2, sweep-reversion sat at −0.044R — and the residual loss almost exactly equalled the residual cost. **Its gross edge is zero.** Engineering can stop a strategy bleeding; it cannot manufacture edge that was never there. This is why the honest move was to keep the engineering and replace the signal, rather than keep tuning CRT.

## 3. The rebuild

Kept: ATR-floored stops, partial + break-even + runner, one trade per day, volatility-scaled sizing.
Dropped: the sweep as a trigger (it survives only as a context flag, which tested at +0.001R — worthless).
Adopted: the two signals with demonstrable gross edge in this dataset.

**Progression:**

| Version | Signal | n | Win% | Expectancy | Verdict |
|---|---|---|---|---|---|
| CRT v1 | H4 sweep-fade, tight stop | 2,722 | 28.8% | **−0.309R** | account destroyed |
| V2 | same signal, fixed geometry | 511 | 47.2% | −0.044R | breakeven — signal is empty |
| V3 NYX | NY opening-range expansion | 694 | 53.6% | **+0.086R** | real edge |
| V4 portfolio | NYX + overnight CARRY | 1,496 | 50.3% | **+0.093R** | Sharpe 1.54 |

**Gates the final system passes that CRT failed:**
- **Random-entry null:** null p95 = −0.008R; NYX = **+0.087R**. Clears it decisively (CRT sat *inside* its null).
- **Cost stress 2×:** NYX +0.017R, CARRY +0.063R — both still positive at double costs.
- **Module correlation: +0.003** — genuine diversification, not two views of one trade.

## 4. Holdout result — the honest number

Scored once on 12 months never used in development, in the most violent regime in the sample (ATR $75 → $205):

| | Dev | **Holdout** | Decay |
|---|---|---|---|
| NYX expectancy | +0.086R | **+0.036R** | −58% |
| CARRY expectancy | +0.098R | **+0.073R** | −26% |
| **Portfolio expectancy** | +0.093R | **+0.055R** | −41% |
| Portfolio win rate | 50.3% | **49.4%** | stable |
| Portfolio Sharpe | 1.54 | **0.50** | −68% |
| Profit factor | 1.22 | **1.13** | −7% |

**All four pre-declared criteria: PASS.** The system is real. But the decay is substantial and the dev-set figures were optimistic — **treat +0.055R and Sharpe 0.50 as the honest forward expectation**, not the dev numbers.

### $100,000 account at 1% risk — holdout year

| | Variant A (1% both) | Variant B (1% NYX / 0.5% CARRY) |
|---|---|---|
| Final equity | **$121,542** | $113,997 |
| Net P&L | **+$21,542 (+21.5%)** | +$13,997 (+14.0%) |
| Max equity drawdown | **−16.2%** | −13.2% |
| Weekly | mean +$406, median +$196, best +$11,145, worst −$6,149, 51% positive | mean +$264, 53% positive |
| Monthly | mean +$1,657, median +$106, best +$17,098, worst −$9,686, 54% positive | mean +$1,077, 46% positive |
| Frequency | 7.5 trades/week (~30/month) | same |

**Month by month (Variant A):** Jul-25 −$1,046 · Aug +$4,501 · Sep **+$17,098** · Oct +$5,820 · Nov −$925 · Dec +$1,335 · Jan-26 +$9,923 · Feb −$555 · Mar +$6,952 · **Apr −$9,477 · May −$9,686 · Jun −$2,503** · Jul +$106.

## 5. What concerns me — read before trading this

1. **The last four months of the holdout are negative** (−$21.6k of the year's drawdown falls in Apr–Jul 2026). The whole year's profit was made in the first nine months. That could be normal variance for a Sharpe-0.5 system, or the start of decay — you cannot tell from 13 months. **This is the single biggest caveat in the report.**
2. **Median month is +$106.** The mean is carried by a few large months (Sep +$17k, Jan +$9.9k). Most months feel like nothing. This is not a steady income stream.
3. **Sharpe 0.50 means long flat periods are guaranteed.** 51% of weeks positive is barely better than a coin flip on any given week — only the aggregate has edge.
4. **CARRY carries financing risk not modelled here.** Long-XAUUSD swap of $0.3–0.8/oz/night can materially erode it; verify on your account before running it (see the earlier overnight-drift caveat).
5. **The 41% dev→holdout decay** is what ~75 configurations of selection buys you. Expect further decay live.

## 6. The system — mechanical steps (UK clock; −1h in winter)

**Module 1 — NYX (the workhorse, ~14.5 trades/month)**
1. **2:00pm** — mark the high/low of the **1:30–2:00pm** range (OR).
2. Skip the day unless **0.04 ≤ OR width ÷ ATR20 ≤ 0.50**.
3. Note where the day opened vs **yesterday's value area**. Opened above value → **buy order only**. Below value → **sell order only**. Inside value → both.
4. Place OCO **stop orders** at the OR edges; first fill cancels the other.
5. **Stop = 0.25 × ATR20 from entry** — a fixed volatility unit, *not* the opposite side of the range. This is the single most important change from CRT.
6. At **+1R take 33% off** and move the stop to break-even.
7. Runner flat at **9:55pm**. One trade per day.

**Module 2 — CARRY (~16.7 trades/month)**
1. **Mon–Thu at 9:00pm**, buy.
2. Stop 0.50 × ATR20 below entry. No target.
3. Exit **3:00am**.

**Sizing:** 1% of current equity per trade, risk measured to the initial stop. Position = (equity × 1%) ÷ stop distance in $/oz.

## 7. Recommendation

Run it, but with expectations set by the **holdout**, not the dev set: roughly **+15–20% a year on a ~15% drawdown**, delivered lumpily, with losing quarters. Start at **0.5% risk** for the first 100 live trades and compare realised expectancy against +0.055R before scaling to 1%.

Given the negative recent quarter, I would specifically **paper-trade NYX for 4–6 weeks first** to see whether the recent weakness continues. The kill criterion: rolling 50-trade expectancy below zero on either module for two consecutive checks → halve size and re-run `21`–`23` on refreshed data.

There remains ~2 years of unused validation potential: the next honest test is walk-forward on data *after* 2026-07-16 as it arrives, since the holdout is now spent.
