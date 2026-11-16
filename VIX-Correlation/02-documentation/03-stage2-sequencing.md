# Stage 2a — the sequencing check

Run 2026-11-16. Intraday US500 bars (M15 for 7 days, M30 for 6) covering all
**13 VIX-weak events** from stage 1. Purpose: test the one bias flagged as
blocking — daily bars cannot tell whether the session low came BEFORE or AFTER
price reclaimed the previous day low.

## Method

For each event session, walking bars in order:
1. find the first bar whose low breaches the previous day low (PDL)
2. find the first LATER bar whose high reaches `PDL x 1.0014` → **entry**
3. **stop** = lowest low seen up to that point (the breach low)
4. scan the remainder of the session: does any later low touch the stop?

A day where step 4 hits is a trade the daily test scored as a winner and that
in reality was stopped out.

## Result

**8 of the 9 winners survive. One does not.**

| Date | PDL | entry | stop | risk | verdict |
|---|---|---|---|---|---|
| 2024-11-25 | 5967.00 | 5975.35 | 5961.20 | 14.2 | survives |
| 2025-01-20 | 5973.30 | 5981.66 | 5949.00 | 32.7 | survives |
| 2025-03-20 | 5630.30 | 5638.18 | 5599.70 | 38.5 | survives |
| **2025-04-23** | **5347.00** | **5354.49** | **5342.20** | **12.3** | **STOPPED — low 5341.70 after entry** |
| 2025-05-01 | 5576.20 | 5584.01 | 5575.90 | 8.1 | survives (4.3 pts spare) |
| 2025-05-06 | 5582.60 | 5590.42 | 5574.70 | 15.7 | survives |
| 2025-06-09 | 5986.60 | 5995.00 | 5986.20 | 8.8 | survives (5.2 pts spare) |
| 2025-08-05 | 6292.50 | 6301.31 | 6290.80 | 10.5 | survives |
| 2025-12-10 | 6825.70 | 6835.26 | 6813.10 | 22.2 | survives |

The four days stage 1 already scored as losses (2024-12-05, 2024-12-30,
2025-07-30, 2025-11-05) stay losses — sequencing cannot rescue a loser.

### Corrected arm B, 3R target

| | stage 1 (daily) | stage 2a (sequence-checked) |
|---|---|---|
| win rate | 9/13 = 69.2% | **8/13 = 61.5%** |
| avg R | +1.83 | **+1.46** |

## What this does and does not establish

**Does:** the headline arm is not an artefact of the sequencing blind spot.
The bias was real and it cost one trade in thirteen, not most of them.

**Does NOT:** the 55-event control arm has NOT been sequence-checked. It would
lose some winners too. So the corrected +1.46R cannot be compared directly
against the uncorrected control's +0.20R — the true gap is narrower than that
pairing suggests. **Correcting the control is the next job.** Until then the
direction holds but the size of the edge is not pinned down.

## The actionable finding: tight stops are where this breaks

The one failure had a **12.3-point stop (0.23% of price)**, and two survivors
cleared their stop by only 4.3 and 5.2 points. Risk on these events ranges
8.1 to 38.5 points — a 4.7x spread.

Every near-miss is a tight-stop setup. The breach low and the reclaim level
sit close together, so ordinary intraday noise retests it. That suggests a
**minimum stop distance** (or a stop placed some margin below the breach low)
would convert the fragile cases into either robust trades or no-trades. Worth
testing before anything is built — it is a change the source never specifies.

## Honest limits of this check

- **M15/M30 cannot resolve within-bar order.** On 2024-12-05, 2025-05-01,
  2025-05-06, 2025-06-09 and 2025-08-05 the breach and the reclaim fell in the
  same bar, or the session opened already below the PDL. Those were resolved by
  reading open/close position within the bar, which is inference, not fact.
  M5 or tick data would settle them.
- Entry assumes a fill at `PDL x 1.0014` with no slippage.
- After the entry session, subsequent days still use daily bars with the stop
  checked before the target (conservative).
- Still 13 events over 13 months, from a different broker feed than the live
  account.

## Next

1. Sequence-check the 55-event control arm, so the comparison is like-for-like.
2. Test a minimum stop distance.
3. Weekend-gap exposure.
