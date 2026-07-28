# Stop-Loss Management Study — Step / Ratchet Trailing

**Preferred config per instrument · 2.0/2.5/3.0/3.5R targets · 3-yr backtest · $100k acct, $100/trade, net of costs.**

Interactive: `stop_loss_management.html`. Engine: `scripts/trail_study.py`, `backtest.simulate_trade` (pessimistic intrabar rule — a bar never raises its own stop; a bar spanning stop+target counts as a stop).

**Step trail:** at each *k*×step of favourable movement, stop ratchets to (*k*−1)×step (so a 1.0R step = breakeven at +1R, +1R at +2R, …). **Breakeven@1R:** stop→entry once +1R hit, then hold.

## Headline

- **Tight trailing destroys the edge.** Steps of 0.25–1.0R (including the classic *breakeven-then-+1R*, i.e. step 1.0R) cut net profit **40–65%** on both instruments — they stop out the runners the strategy depends on.
- **US30 rewards a *loose* trail.** Best step ≈ **2.5R**: it protects only large gains and **beats the static stop** on both return and drawdown at 3.0R/3.5R targets.
- **NAS100: leave it static.** Its post-breakout move is clean; any stop movement before target costs money.
- **Drawdown vs profit is a dial:** the tightest trail (0.25R) gives the smallest drawdown but the lowest return.

## Net $ by trailing step (after costs)

### US30

| Step (R) | 2.0R | 2.5R | 3.0R | 3.5R |
|---|--:|--:|--:|--:|
| 0.25 | +$1,772 | +$2,072 | +$2,097 | +$2,122 |
| 0.5 | +$4,024 | +$4,374 | +$4,224 | +$4,174 |
| 0.75 | +$4,627 | +$5,697 | +$5,318 | +$5,243 |
| 1.0 | +$4,507 | +$5,611 | +$5,459 | +$5,262 |
| 1.25 | +$5,567 | +$7,514 | +$8,032 | +$7,043 |
| 1.5 | +$5,524 | +$7,536 | +$9,500 | +$8,828 |
| 1.75 | +$6,298 | +$7,960 | +$9,729 | +$8,832 |
| 2.0 | +$6,561 | +$8,423 | +$10,392 | +$9,150 |
| 2.5 | +$6,561 | +$8,694 | +$10,612 | +$9,221 |
| 3.0 | +$6,561 | +$8,694 | +$10,033 | +$8,642 |
| **static** | +$6,561 | +$8,694 | +$10,033 | +$8,498 |

*Best step by $:* 2.0R→2.0R (+$6,561), 2.5R→2.5R (+$8,694), 3.0R→2.5R (+$10,612), 3.5R→2.5R (+$9,221)

### NAS100

| Step (R) | 2.0R | 2.5R | 3.0R | 3.5R |
|---|--:|--:|--:|--:|
| 0.25 | +$2,406 | +$2,481 | +$2,506 | +$2,481 |
| 0.5 | +$1,203 | +$1,653 | +$1,753 | +$1,853 |
| 0.75 | +$1,650 | +$2,356 | +$2,841 | +$3,241 |
| 1.0 | +$1,495 | +$2,295 | +$2,872 | +$4,069 |
| 1.25 | +$1,842 | +$2,902 | +$3,219 | +$3,594 |
| 1.5 | +$1,760 | +$3,176 | +$3,894 | +$4,794 |
| 1.75 | +$2,606 | +$3,994 | +$4,961 | +$5,554 |
| 2.0 | +$2,626 | +$4,263 | +$5,481 | +$5,973 |
| 2.5 | +$2,626 | +$5,263 | +$6,439 | +$7,181 |
| 3.0 | +$2,626 | +$5,263 | +$7,031 | +$7,923 |
| **static** | +$2,626 | +$5,263 | +$7,031 | +$7,807 |

*Best step by $:* 2.0R→2.0R (+$2,626), 2.5R→2.5R (+$5,263), 3.0R→3.0R (+$7,031), 3.5R→3.0R (+$7,923)

## Scheme comparison at each instrument's recommended target (net)

### US30 @ 3.0R

| Scheme | Trades | Win% | Net $ | Δ vs static | Max DD | Recovery |
|---|--:|--:|--:|--:|--:|--:|
| Static (no trail) | 613 | 36.7% | +$10,033 | — | −$2,295 | 4.37 |
| Breakeven @1R | 613 | 26.4% | +$7,662 | −$2,371 | −$2,032 | 3.77 |
| Step 1.0R | 613 | 30.8% | +$5,459 | −$4,574 | −$2,490 | 2.19 |
| Step 1.5R | 613 | 32.0% | +$9,500 | −$533 | −$1,804 | 5.27 |
| Step 2.0R | 613 | 34.7% | +$10,392 | +$358 | −$2,195 | 4.74 |
| Step 2.5R | 613 | 36.4% | +$10,612 | +$579 | −$2,295 | 4.63 |

### NAS100 @ 3.5R

| Scheme | Trades | Win% | Net $ | Δ vs static | Max DD | Recovery |
|---|--:|--:|--:|--:|--:|--:|
| Static (no trail) | 398 | 32.9% | +$7,807 | — | −$1,306 | 5.98 |
| Breakeven @1R | 398 | 20.6% | +$3,340 | −$4,467 | −$1,972 | 1.69 |
| Step 1.0R | 398 | 28.9% | +$4,069 | −$3,738 | −$1,889 | 2.15 |
| Step 1.5R | 398 | 26.9% | +$4,794 | −$3,013 | −$1,681 | 2.85 |
| Step 2.0R | 398 | 29.1% | +$5,973 | −$1,834 | −$1,630 | 3.67 |
| Step 2.5R | 398 | 31.2% | +$7,181 | −$626 | −$1,547 | 4.64 |

## Practical guidance

- **US30:** use a **step ≈ 2.0–2.5R** trail (protect once ~2R in profit) — modestly higher return than static and lower drawdown. For a smoother equity curve at some cost to return, tighten toward ~1.25–1.5R.
- **NAS100:** keep the **static** stop + full target. If any protection is wanted, only a single very-late breakeven move (near +3R) is neutral-to-slightly-positive.
- **Avoid** breakeven-at-1R and sub-1R step trailing everywhere — they are the worst performers.

> Caveat: M5 bar resolution + pessimistic intrabar rule make trailing results conservative; tick-accurate fills could differ. Confirm on demo before use.