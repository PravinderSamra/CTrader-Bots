# V5 — Intraday-Only Improvements

Script: `24_intraday_only.py` plus the FBR and cost-lever runs recorded in `output/24_intraday.txt`.
Constraint applied: **every position opens and closes the same day. No overnight holds.**

---

## 1. The constraint has a price — state it plainly

**CARRY (long 20:00 → 02:00) is an overnight hold and is therefore disqualified.** It was the larger contributor: on the holdout it produced +14.9R of the portfolio's +21.9R. Dropping it removes 78R of 138R dev profit.

So the intraday-only system is materially smaller than the V4 portfolio, and everything below is about clawing that back from inside the trading day.

## 2. What I tested, and what actually worked

### ✅ The one real improvement: allow the second side of the range to trade

Frozen V4 took one trade per day. Allowing the opposite side to trade after the first position has exited:

| | Dev | Holdout |
|---|---|---|
| NYX1 (V4 frozen) | +0.080R, 780 trades, Sharpe 1.01 | **+0.001R**, 225 trades, Sharpe 0.01 |
| **NYX2 (+ re-entry)** | **+0.103R**, 932 trades, **Sharpe 1.47**, DD −10.8R | **+0.047R**, 275 trades, Sharpe 0.39, DD −12.4R |

Better on both sets, on nearly every metric: more trades, higher win rate (54.9% dev / 52.4% holdout), higher expectancy, *lower* drawdown. Return/DD improves from 4.9 to 8.9. This is the change worth making.

### ❌ A near-miss I have to flag — and how it was caught

Decomposing NYX2 showed the *second* trade of the day looked spectacular: **dev +0.222R (n=152), holdout +0.253R at 62% win (n=50)** — while the first trade decayed to zero out-of-sample. That reads like "just trade the failed-breakout reversal" — and it is precisely your original CRT thesis.

**I built it standalone and it was flat: dev +0.021R, holdout +0.004R (n=493), and it FAILED the 2× cost stress at −0.049R.**

Why the gap: inside the engine, a "second trade" only exists on days where the *first* trade had already exited in time for the other side to break. That is a survivorship/timing condition, not an ex-ante rule. The unconditioned signal — "one side breaks, later the other side breaks" — has no edge. Had I skipped the standalone test and built a system on that +0.25R figure, it would have been the same class of error as the volume-profile bug earlier in this project.

**Conclusion:** keep re-entry as part of the combined NYX2 rule (it is implementable and causal), but do *not* believe the second trade is separately tradeable.

### ❌ Everything else tested and rejected

| Idea | Result |
|---|---|
| **More session ORBs** — London 07:00 / 08:00, pre-NY 12:00, NYSE 14:30, PM fix 15:00 | **All negative** (−0.004R to −0.060R). The 13:30 COMEX open is genuinely unique; you cannot add frequency by copying it to other hours. |
| Structural T2 (PDH/PDL/POC) instead of runner | +0.056R vs +0.080R — worse |
| Skip lowest-20% ATR days | +0.057R — worse |
| Skip Mondays / Fridays | worse or no effect |
| 1.5× size on inside-value opens | no effect |
| Earlier flat (17:00 / 19:00) | worse — the runner needs the full afternoon |
| Tighter width gate | worse |
| Asia-break continuation as a 3rd module | +0.051R, n=134, Sharpe 0.27 — *lowers* portfolio return/DD from 8.9 to 7.6. Rejected. |

## 3. The highest-leverage improvement is execution cost, not signal

Cost is ~7% of the risk unit, so every cent saved converts directly into expectancy. This is the single biggest lever available and needs no new research:

| Round-trip cost | Expectancy | Sharpe | vs modelled |
|---|---|---|---|
| $0.94 (wide retail / spread-bet) | +0.033R | 0.47 | **−68%** |
| $0.47 (modelled) | +0.103R | 1.47 | — |
| $0.37 (limit entries, no slippage) | +0.118R | 1.68 | **+14%** |
| $0.25 (tight ECN + commission) | +0.136R | 1.94 | **+32%** |
| $0.15 (institutional) | +0.151R | 2.15 | **+46%** |

**Moving from a typical spread-bet account to a tight ECN account roughly quadruples this system's expectancy.** No parameter I tested came close to that. Concretely:

1. **Trade a raw-spread/ECN account**, not a spread-bet one. Worth ~+32%.
2. **Use resting stop orders placed in advance** at the OR edges rather than reacting to the break — the order is in the book before the move, which is how you avoid paying the $0.10 slippage. Worth ~+14%.
3. **Never market-order into 13:30** — the OR ends at 14:00, so the design already avoids the data spike. Keep it that way.
4. **Check the 20:55 exit spread**; if it is wide on your broker, move the flat to 20:45.

## 4. Final intraday-only system

Identical to the frozen V4 NYX module, with one addition (step 8):

1. **2:00pm UK** — mark the high/low of the **1:30–2:00pm** range (OR).
2. Skip the day unless **0.04 ≤ OR width ÷ ATR20 ≤ 0.50**.
3. Opened **above** yesterday's value area → buy order only. **Below** → sell order only. **Inside** → both.
4. Resting **stop orders** at the OR edges; first fill cancels the other.
5. **Stop = 0.25 × ATR20** from entry.
6. At **+1R take 33%**, move stop to break-even.
7. Runner flat at **9:55pm UK**.
8. **NEW — if that position closes and the opposite OR edge is subsequently broken, take that trade too**, same rules. Maximum two trades per day, one per side.
9. Sizing: 1% of equity per trade.

### Honest expected performance (holdout, intraday-only, $100k @ 1%)

| | |
|---|---|
| Return | **+12.2%** for the year |
| Max equity drawdown | **−12.0%** |
| Frequency | 5.2 trades/week (~21/month) |
| Weekly | mean +$229, median +$145, best +$5,103, worst −$4,521, **55% positive** |
| Monthly | mean +$935, median +$260, best +$13,435, worst −$7,008, **54% positive** |

Dev-set equivalent was +26.1% CAGR at −10.4% DD — as before, **trust the holdout number, not the dev number.**

## 5. What I would do next (in order of expected value)

1. **Fix your cost base first.** +32% expectancy for an account change beats every strategy tweak in this document. Do this before anything else.
2. **Accept lower frequency.** The data is unambiguous: the COMEX open is the only intraday window with expansion edge on gold. Adding trades elsewhere in the day *lost* money in every test. Chasing daily activity is how this system gets destroyed.
3. **Revisit the overnight constraint.** CARRY was the better module and it is a 6-hour hold, not a swing trade — you enter at 9pm and exit at 3am. If your objection is to holding over *many days* rather than overnight, CARRY is worth reconsidering; it roughly doubles the system's return.
4. **Bank more data before further tuning.** The holdout is spent, the intraday edge is now measured at +0.047R, and I have run ~90 dev configurations. Further optimisation on this dataset will produce fitted noise, not improvement. The right next step is forward-testing: run NYX2 live-shadow at 0.25–0.5% risk and compare realised expectancy against +0.047R over 100+ trades.

**A realistic ceiling to have in mind:** intraday-only on one instrument, at retail costs, this is a ~10–15%/year system with ~12% drawdowns and long flat stretches. Getting meaningfully beyond that requires either better costs, more instruments, or relaxing the intraday constraint — not more parameters.
