# Asia Range — Mean Reversion / Failed-Breakout Study

Script: `27_asia_mean_reversion.py`. Same methodology as the continuation study (`25`/`26`), inverted. Razor costs $0.25/oz. Dev set 2021-07 → 2025-07, n = 982 breaks.

**Direct answer to the question: no. There is no combination of confluences where a failed Asia breakout reverses with enough reliability and distance to pay.** The reasons are structural and worth understanding, because they explain several other failures in this project.

---

## 1. The single most important statistic

> **96.8% of Asia-range breakouts eventually have a bar close back inside the range.**

Almost every break, on almost every day, at some point "fails" and reclaims. That means **"failed breakout" is not a signal — it is the default state of the market.** A pattern that occurs on 97% of days carries essentially no information.

This is the same trap that killed the CRT strategy, the Asia pullback study, and the standalone failed-breakout-reversal test earlier in this project. On a chart, sweep-and-reclaim looks like a rare, high-conviction event. In the data it is what happens virtually every day.

## 2. Baseline reversion after a break

| Outcome | Probability |
|---|---|
| A bar closes back inside the range | **96.8%** |
| Price reaches the range **midpoint** | 66.7% |
| Price reaches the **opposite side** | 39.7% |
| **Median max extension beyond the level first** | **1.11 × range** |
| 75th percentile extension | 1.94 × range |

Two-thirds of breaks do return to the midpoint — which sounds tradeable until you see the extension column. **The median break runs 1.11 range-widths beyond the level before it turns.** To fade it and survive you need a stop wider than the move you are trying to capture. That is the whole problem in one line.

## 3. Why the confluences don't rescue it — the key structural finding

Here is the result that matters most, and it is the mirror image of what you'd hope for:

| Asia range size | Continuation sustains | **Reverts to mid** | Median extension first |
|---|---|---|---|
| < 0.30 ATR (small) | 33.7% | **79.0%** | **1.98 × range** |
| 0.30 – 0.45 | 31.4% | 73.3% | 1.16 × range |
| 0.45 – 0.60 | 26.0% | 55.8% | 0.91 × range |
| 0.60 – 0.80 | 16.5% | 46.8% | 0.73 × range |
| > 0.80 (large) | 10.2% | **42.4%** | 0.62 × range |

**The conditions that kill continuation also kill reversion.**

- **Small ranges** revert to the midpoint 79% of the time — but only after extending nearly **two full range-widths** against you first. You cannot fade that; the stop required is bigger than the target.
- **Large ranges** barely extend (0.62 range) — but they also barely revert (42.4% to mid). They neither trend nor snap back. They just chop.

There is no cell that combines "the break fails" with "it then travels far enough to pay you." Low directional energy produces sideways drift, not reversal.

The same pattern holds for every other condition:

| Condition | Continuation | Reverts to mid |
|---|---|---|
| Prior-day level already cleared | 21–22% (worst) | **57.1% (worst)** |
| Prior-day level >1 range ahead | 27.0% | 72.9% |
| Break 07:00–08:00 | 26.6% | 72.2% |
| Break 12:00–16:00 | 15.8% (worst) | **47.6% (worst)** |

Every condition that is bad for the breakout is *also* bad for the fade. That is a consistent, mechanistically sensible picture — these are simply low-energy days, and low-energy days pay nobody.

## 4. Fade strategies tested — all negative

| Approach | n | Win% | Expectancy |
|---|---|---|---|
| Extension fade (+0.2 range, target mid) | 702 | 29.3% | −0.085R |
| Reclaim fade (enter on close back inside) | 915 | 37.0% | −0.101R |
| Level fade (at PDH/PDL beyond the range) | 152 | 30.9% | −0.141R |
| Fade at +0.3 / +0.5 range | 566 / 355 | 28.3% / 25.9% | −0.041R / −0.028R |
| Target = broken level / mid / far side | 702 | 59.8% / 29.3% / 21.4% | −0.052R / −0.085R / −0.129R |

**Plus a structural cost penalty:** fading requires a tight stop relative to entry, so cost runs at **9.5% of the risk unit** versus 3.0–4.7% for the continuation trade. The fade starts every trade three times further in the hole.

### The confluence stack, and the micro-cells that looked promising

| Filter | n | Expectancy | What happened next |
|---|---|---|---|
| Large range >0.45 + PD level cleared + skip Sunday | 88 | +0.112R | dev years: −0.30, +0.72, +0.20, −0.13 — wildly unstable |
| Reclaim entry, large range >0.60 | 151 | +0.042R | **holdout −0.218R** (n=70) — fails out of sample |
| Large + cleared + late break | 30 | +0.232R | n=30 dev, **n=7 holdout** — meaningless |

Every positive cell is small, unstable across years, or fails out of sample. Combined with the continuation study I have now examined roughly **135 configurations** across these two Asia investigations — at that count, several will look profitable by chance alone, and these are exactly the ones that do.

## 5. Verdict and what to take from it

**Do not build an Asia mean-reversion strategy.** Not with range-size filters, not with magnet filters, not with reclaim confirmation. The failure is structural rather than a matter of tuning:

1. Failed breakouts are the norm (96.8%), so failure carries no information.
2. Where breaks do fail, they typically extend ~1.1 range-widths first, so the fade's stop must exceed its target.
3. The conditions that suppress continuation suppress reversion equally — they mark dead days, not reversal days.
4. Fading carries triple the cost burden of continuation because of the tighter stop.

**What this is genuinely useful for:** the extension statistics are excellent risk-management information for the trades you *do* take. If you are long from a validated setup and price is 1.1 range-widths beyond the Asia high, you are at the median turning point — that is a sensible place to take partials, and a terrible place to add.

And the finding that survives from both Asia studies remains the one about your working system: **a wide overnight range predicts a better 13:30 NY trade** (holdout +0.127R vs −0.254R on narrow-range days). The Asia range earns its place on your chart as context for that trade — not as a trade in itself, in either direction.
