# 01 — Strategy Core (the condensed rule brain)

The rule set every other step leans on. This is a reference sheet, not a course —
the "why" behind each rule lives in `Liquidity Trap/02-documentation/` (cited as
"doc NN §…") and `04-official-playbook/` (cited as "Playbook §…").

---

## 1. The liquidity premise

- **Liquidity = resting orders, above all stop losses.** Traders who buy at/near
  a low leave sell stops *below* it; traders who short at/near a high leave buy
  stops *above* it. Those clusters are pools, and price is driven into them
  (doc 01 §1–2).
- Liquidity supplies **everything**: direction, bias, entry, invalidation,
  target ("Liquidity is everything for me… A to Z", doc 01 §1; Playbook p.01).
- Retail concepts (BOS, OB, FVG, S/R, fibs) are kept only as a **map of where
  others get trapped** — they temporarily work *in order to* build liquidity
  (doc 01 §3). You never trade them as entries.
- The model is **fractal** — same grammar from weekly to 1m. HTF identifies the
  draw; LTF supplies the entry (doc 01 §8).
- **Never predict pools. Let the market communicate them** ("We are not
  guessing", doc 01 §5a). Reactive marking only.

## 2. The core discrimination: real liquidity vs no-liquidity extremes

The single most load-bearing rule (doc 01 §5; doc 05 §3 item 1):

- A level **HAS liquidity** when it was **respected and price moved away** (or
  it is equal/relative-equal highs/lows). Respect = a wick terminating at/into
  the prior level's zone without closing through — a touch is not required;
  observed undershoot tolerance ≈ 0.1–0.3% of price (doc 02 §B.1).
- A level has **NO liquidity** when it *itself swept* liquidity and has not
  since been respected — that is a **liquidity block (LB)** (doc 01 §5b).
- **"Not every high and every low has liquidity."** A high/low broken straight
  through with no respect is nothing. A lone retail POI is nothing.
- LBs **re-acquire** liquidity the moment price later respects them and moves
  away — update their status then (doc 01 §5b caveat).

## 3. Buy below lows, sell above highs — after the sweep only

- Operating slogan: **buy below lows, sell above highs** (doc 01 §2;
  Playbook p.01). Never enter before the pool is run; **execute after liquidity
  is taken, not before** (Playbook §Execution).
- Reactions **inside the trap zone** (above the lows / below the highs, at
  retail POIs) are pre-classified **false and short-lived** — they only build
  the pool. Never take longs above the lows, never sells below the highs
  (doc 01 §6; Playbook §Buy/Sell Setup Rules "never above / never below").

## 4. The induce → trap → enter grammar

The three-step loop, sell-side version; buys are the exact mirror (doc 09 §1.1;
doc 03 §0):

1. **Induce.** A sweep of an *internal* level in the direction of the (false)
   move pulls participants in (retail reads it as a BOS). Their stops deposit
   the next pool. Mark "buyers/sellers induced"; **never trade this leg** —
   but you want to see it: it is confluence.
2. **Trap.** Price runs the level where the induced participants live — the
   stab of their pool. "We must only trade once the early traders are trapped.
   No ifs, ands, or buts" (doc 09 §6).
3. **Enter.** Entry fires the moment the trap completes — at the stab, no
   over-refinement. Stop beyond the LB; targets at the opposing pools.

**Engineered liquidity** is the arming condition on the target side: as price
first approaches the target pool it must print a swing that *respects* it and
retraces — sellers (buyers) entering in front of your target, refreshing the
pool and supplying the reason for price to go there. "No engineered liquidity,
no model" (doc 03 §1.3).

## 5. Inducement vs a plain sweep

A sweep **by itself is nothing** — trading it is pattern trading, which is
forbidden (doc 01 §9; doc 09 §1.2). The discriminator is the sweep's role in
the grammar:

| Sweep type | What it does | Your action |
|---|---|---|
| **Inducing sweep** | Takes an *internal* level with a confirmed pool still intact beyond; *creates* participants + their stops | **Mark it, never trade it** |
| **Trapping sweep** | *Consumes* the pool a prior inducement built, into/near an LB, with a confirmed target opposite | **This is the entry trigger** |
| **Bare sweep** | No confirmed early participants on the swept side, or no target beyond, or no LB | **No trade — it's a pattern, not logic** |

## 6. Liquidity blocks and the hard entry gate

- The LB's whole job: **it provides the level for your stop loss.**
  **"No liquidity block, no stop loss… no liquidity block, no entry"** — a hard
  gate, even when every other condition is met (doc 09 §2.2, §7 item 1).
  Fallback when no LB exists: drop to a lower timeframe and wait for the same
  model to print fractally there with its own LB (doc 03 §2.3; doc 09 §7.1).
- Priority order: **liquidity first, LB second.** The LB is entry plumbing,
  subordinate to bias/target logic — build the story first (doc 09 §2.3).
- **Not every LB is traded.** Untraded LBs still matter: they mark spots where
  counter-moves can stall without invalidating the bias (doc 09 §2.4).
  Anticipating a reaction ≠ taking a trade (doc 09 §7 item 9).
- The sweep's **imbalance** can be used to box the LB zone; FX limit entries
  are parked "right in the imbalance" (doc 09 §2.6).

## 7. Bias lockout (trade permission)

The strict sequencing rule (doc 02 §D):

> Once a **high** is taken, **no buys** until the paired **low** is swept —
> and vice versa. "It doesn't matter what happens anywhere in between."

- If the market respects the pool and runs without sweeping it: "this is not a
  move I was supposed to be in." No chasing; the unswept pool remains a future
  target (doc 03 §5.2).
- IET refinement: against-sequence trades are "**automatically lower
  probability**" rather than absolutely banned, and are licensed **only with a
  session-time confluence** (stock open / 10:00 H4 roll) (doc 09 §3.3, §7
  item 5). **Default to the absolute lockout; the time-qualified exception is
  an advanced overlay** (doc 05 §2.6 item 3).
- **Bias holds only while the target pool survives.** "As long as the highs
  stay intact… buys are valid. Cuz that's the target." Target consumed → that
  direction is off the cards until new liquidity builds (doc 09 §3.3).

## 8. Targets: opposing pools only — never arbitrary R

- **Target = the opposing confirmed pool.** "We're not guessing where to
  target — the market communicated that to us" (doc 03 §4.1; Playbook §Buy/Sell
  rule 6).
- **Layered:** nearest opposing *internal* pool (engineered highs/lows,
  structural points, prior-day levels) = partial point; the HTF *external*
  pool = full target (doc 03 §4.2).
- **Never partial at fixed R-multiples** — "it's literally just a random point
  in the chart" (doc 03 §4.1; Playbook §Management).
- Engineered pools flip roles: the reaction that armed one leg becomes the
  liquidity the next leg runs (doc 03 §4.2 visual note).

## 9. The RR filter

- **Floor: minimum ≈ 1:3** to the analyzed target ("I perform the best… when my
  RR is minimum 1-to-3 minimum", doc 03 §4.3). If the structural stop makes RR
  worse: **skip, or refine to a lower timeframe** (the RR-rescue drop-down,
  doc 03 §2.3) — never widen the target or shrink the stop artificially.
- Also skip **small absolute moves** regardless of RR (doc 03 §4.3).
- **Partial only when the level pays ≈ 1:5+**: "I'm going break even. I'm not
  paying myself. Why? 1-to-2.5… [at 1-to-6] I am paying myself" (doc 09 §7
  item 3). Partial size when taken: small — ~20–25% of position, majority held
  to the full target (doc 04 §3; V1's 50–70% is the superseded earlier style,
  doc 05 §2.2).

## 10. Management — and the break-even reconciliation

- **Initial stop:** structural, beyond the LB / covering the last swept
  high-or-low. Always. Plus spread breathing room on CFD/FX (doc 03 §3;
  Playbook §Execution "always cover the last high/low with your stop").
- **Move the stop only after price moves in your favour** and forms a higher
  low (long) / lower high (short) (Playbook §Management; doc 04 §2.2).
- Optional futures trail: **behind freshly-minted LBs** — "This LB should
  protect my SL. If it runs it, I don't want to be in the trade no more"
  (doc 09 §7 item 4).
- **Never move the stop out of fear**; expect deep re-stabs into the LB before
  the move (doc 04 §2.4–2.5; doc 09 §2.5).

**Playbook-vs-practice break-even reconciliation** (doc 05 §2.6 item 1; doc 09
§7 item 3; doc 04 §2.3):

| Source | Rule |
|---|---|
| Playbook p.03 (stricter wording) | "**No break-even stops** unless partials have been taken" |
| Demonstrated practice (V2/V3/IET — Marco's current operation) | **BE / risk-off once the first opposing pool is consumed** in your favour (structure makes a higher low / lower high); partial decided *separately* by RR-at-that-level (≥ ~1:5 → pay yourself; below → BE only) |

**Default to practice** — the operative rule is *risk-off when a liquidity
level is consumed in your favour* — and read the playbook line as its guard
against **fear-BE** ("It has to make sense to break even your position"), not
as a ban. Note the stricter playbook wording to the user when it matters.

## 11. Invalidation and resets

- **Hard invalidation = stop hit** (price keeps running beyond the LB). This
  does **not** flip the bias while the target pool survives — it resets to the
  induce step: wait for early traders induced again, taken out again, then
  re-enter (doc 03 §5.1).
- **Stacking rule:** target intact = another opportunity; each stacked entry
  must independently satisfy the full model (own sweep + own LB). The stack
  dies when the shared target is consumed (doc 09 §5).
- **Behavioral invalidations** (rule-breaks that void the system): entering
  inside the trap zone because a reaction "looks strong"; entering on
  pattern-match without a target pool; trading a liquidity-void chart; trading
  outside the session window / before news (doc 03 §5.4).
- **Nothing is 100%.** Say so. A disciplined no-trade is a correct output
  (SKILL.md §2, §6).

## 12. The six gates (cross-reference)

Before "armed", every gate in SKILL.md §2 must pass: (1) confirmed target pool,
(2) trap completed, (3) LB behind the entry, (4) bias lockout satisfied,
(5) inside session window, (6) not no-man's-land. Any failure → wait/no-trade,
with the reason.
