# GEXBot — evaluation and integration plan

Tested 2026-09-05 (Saturday). **Every figure below is Friday 4 Sep's 19:59:59
UTC close, frozen for the weekend.** Nothing about intraday behaviour or
refresh rate could be tested today; the items marked UNVERIFIED need an RTH
session.

Client: `scripts/gexbot.py`. Token read from `GEX_BOT_API_TOKEN`, never logged.

---

## 1. What the account has

Base `https://api.gexbot.com`, package **classic**, categories
`gex_full` / `gex_zero` (0DTE) / `gex_one` (1DTE).

Coverage includes everything we care about: **NDX**, **QQQ**, and futures
**`NQ_NDX`** and `ES_SPX`.

Per response: `spot`, `zero_gamma`, `major_pos_vol`, `major_pos_oi`,
`major_neg_vol`, `major_neg_oi`, `sum_gex_vol`, `sum_gex_oi`,
`delta_risk_reversal`, `max_priors`, and a **142-strike ladder** where each row
is `[strike, gex_vol, gex_oi, [5 prior samples]]`.

## 2. The three things we genuinely cannot build

**a) Volume-weighted GEX, signed.** The one thing the CBOE pipeline cannot do
honestly — volume carries no side, so weighting walls by it stacks an
assumption on an assumption. GEXBot sees the trades and signs them.

It is not a marginal difference. On Friday's close, near spot:

| Strike | Ours (OI, $bn) | Theirs OI | **Theirs VOLUME** |
|---|---|---|---|
| 29,500 | +0.197 | 2,635 | **25,523** |
| **29,525** | **−0.016** | 346 | **83,936** |
| 29,550 | +0.444 | 671 | **56,278** |

**Price closed at 29,542.65.** The volume lens put its heaviest concentration
at 29,525–29,550, exactly where price pinned. Our OI-only view showed 29,525 as
approximately nothing.

**b) Per-strike priors.** Five prior samples of GEX at *every* strike — walls
building and unwinding through the session. This is precisely the question
`research/live-walls/` was built to *estimate*.

Worth being exact about the relationship: our estimator infers **ΔOI**;
GEXBot's priors show **ΔGEX**, which moves with price and greeks as well as
positioning. They are not the same quantity. But for the practical question —
*is this wall growing or being taken off?* — the priors answer it directly and
ours only approximates it.

**c) `NQ_NDX`** — the NDX levels plus a constant (+30.82 on this snapshot),
i.e. already in futures space. That removes the stale-cash-roll-forward
workaround (`_nq_implied_cash`) that has bitten us before.

## 3. Where they disagree with us — and it is not small

Anchored to their spot, 25pt bins, ±400 around price:

**Sign agreement on the OI ladder: 25 of 32 strikes (78%).** The seven
disagreements cluster at 29,150–29,600 — around spot, where it matters.

Headline levels, same snapshot:

| | GEXBot | Ours (week) | Ours (45d) |
|---|---|---|---|
| Flip / zero-gamma | 29,542.7 | **29,323.2** | — |
| Major +GEX (OI) | 29,500 | 29,700 | 30,000 |
| Major −GEX (OI) | 29,600 | 29,050 | 28,800 |

**The −GEX row is not a disagreement, it is a different question.** Their
`major_neg` is the most negative strike *anywhere*; our put wall is *the most
put-dominated strike below spot*. Their answer sits **above** spot. Treating
those as the same level is exactly the confusion that produced D4, and the
client deliberately does not rename their fields into our vocabulary.

**Spot itself differs by 42 points** (29,542.65 theirs vs 29,584.70 ours, which
was running `nq_implied`). On a frozen weekend both cannot be right.

## 4. Two things that must be verified before use

**`zero_gamma` equalled `spot` EXACTLY** — 29,542.65 — for both `gex_full` and
`gex_zero`. It differed for `gex_one` (29,470), which argues it is genuinely
computed rather than a fallback, and Friday was an expiry with heavy pinning.
But "computed value happens to land exactly on spot to two decimals" deserves
suspicion, and **our flip is the number that decides which of the two strategies
to trade**. Verify across several RTH samples before it replaces ours.

**The `priors` array ordering is undocumented** and cannot be established from a
frozen snapshot — newest-first and oldest-first give opposite trend readings.
Sample twice during RTH and compare before reading any direction from it.

## 5. Recommendation: additive now, replacement only on evidence

**Do not swap the gamma engine.** Three reasons, all consistent with how every
other change here has been handled:

1. Their flip is unverified and ours is properly computed by repricing the book
   across a spot grid. Swapping an unverified number into the field that picks
   the strategy is the largest single-point risk available.
2. 78% sign agreement means they disagree with us on roughly one strike in five
   near spot. **One of us is wrong there and we do not yet know which.**
3. Their wall definitions are not ours. Reconciling is real work, not a config
   change.

**What to do instead**, in order:

1. **Add the volume lens as new information** — it is additive, cannot be
   replicated, and needs no reconciliation. Nothing existing changes.
2. **Run both ladders in parallel** and grade them with the machinery already
   built: `gex_retro.py --ladder` plus `role_reversal()`. Persist a GEXBot
   ladder beside ours on every scan.
3. **Let the evidence decide the swap**, per the 3-session rule.

Opened as hypotheses rather than assumptions:

- **H12 — does the volume-weighted wall hold better than the OI-weighted one?**
  Threshold 5 sessions. Grade both with `role_reversal()`. This is the question
  that decides whether GEXBot replaces the ladder or merely enriches it.
- **H13 — is GEXBot's `zero_gamma` a real flip or a fallback to spot?**
  Threshold 5 RTH samples. Record `zero_gamma`, `spot`, and our own flip each
  scan. If it tracks spot within a point every time, it is not a flip.

## 6. What this does NOT replace

The brief's value is synthesis, and GEXBot supplies none of it: no liquidity
levels (PDH/PDL, session highs/lows, equal highs/lows), no range/fuel model, no
macro, no news, no event gating, no bias engine, no QQQ blending, and no
CFD-space conversion for the specific broker feed being traded.

**GEXBot is a better gamma input, not a replacement brief.** The correct framing
is that it may replace `cboe_gex` + part of `gex_levels`, and only once H12 and
H13 have answered.

## 7. Cost/benefit against the earlier tick-stream evaluation

The tick-stream review concluded the most valuable purchase would be a
**historical GEX archive**, because the register is rate-limited by the calendar
— 4 trading days on record against thresholds of 5 and 10.

**GEXBot as configured does not solve that.** It is a live feed with 5 prior
samples, not a backtestable history. It makes each future day richer; it does
not make past days available. Both observations stand, and they are answers to
different problems.
