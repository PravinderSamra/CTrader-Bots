# REVIEW — 2026-09-10 (Thu)

Reviewed 2026-09-11 post-roll. Source: `review_day.py 2026-09-10 --json`, `track.py`.
2 gradeable scans (08:12:05Z LONDON, 15:07:09Z NY_MIDDAY). 0 test artefacts.
Journal clean — no fabricated or backfilled entries. 11 `is_trading_day: false`
PREP scans (2026-08-23) excluded from every statistic below.

**Reconciliation with the provisional review.** Commit `22e9c1c` graded this day
at 20:23Z, *before* the 21:00Z roll, and reported O 29,437.9 / C 29,126.8. The
final figures are O **29,429.3** / C **29,108.0**. Its headline — *"walls 7/7,
the best single-day level result recorded"* — counted secondary-table and chart-
ladder levels; `review_day.py`'s board-only count is **7 of 19**. §2 below
retracts the "best result recorded" reading on different grounds.

---

## 1. Scoreboard

**Session (NAS100 CFD, 21:00Z roll, 276 M5 bars)**

| | |
|---|---|
| Open / High / Low / Close | 29429.3 / 29482.2 / 29018.3 / **29108.0** |
| Range / Net | **463.9** / **−321.3** |
| Range vs ADR14 (349.3) | **132.8%** — largest range of the 8 graded days |

**The scans**

| | 08:12Z LONDON | 15:07Z NY_MIDDAY |
|---|---|---|
| Bias | −1 NEUTRAL / TWO-WAY | **−10 STRONGLY BEARISH** |
| Shape | FRONT_FLAT_BACK_LONG | COHERENT_SHORT |
| Post-scan move | **−298.9** | −91.2 |
| Direction | **no call** | **CORRECT** |
| Fuel state / budget | MODERATE / 206.2 | EXHAUSTED / 0.0 |
| Actual extension | **320.8** → **UNDER by +114.6** (1.56×) | **0.0** → **exact** (err 0.0) |
| Traversal | 412.7 (2.0× budget) | 147.8 |
| Levels published / touched | 19 / 7 = **0.37** | 2 / 0 = **0.00** |

**Direction calls: 1 right / 0 wrong / 1 no-call.**
**Mean level hit rate 0.18 — the lowest of all 8 graded days** (range 0.18–1.00).

**Cumulative after this day** — 8 trading days, 15 deduped scans: direction
**5 right / 5 wrong / 5 no-call**; H1 per-day budget error mean **−19.2**
(+61.2, −11.6, −73.0, −86.4, −10.7, −26.2, −64.0, **+57.3**).

---

## 2. What the levels actually did

All 7 touched levels came from the 08:12 board. Every one of them graded
identically: *"stalled at it — held as resistance"*, `held: true`,
`settled_side: below`.

| Level | brief said | actually did | verdict |
|---|---|---|---|
| 29429.3 PD close | "price often comes back to fill a gap from here" | broke DOWN at 08:20, settled below for 765min, worst **+1.7** | held — but published **+10** from spot, so it cannot discriminate |
| 29397.2 **PUT WALL** ●●●○○ | "**Heaviest floor this week — expect a bounce and a good long-sweep here**" | never floored anything. Became the ceiling for 715min, worst +6.4 | **the day's worst instruction.** A long here sat through a **379pt** drawdown |
| 29392.0 London Low | "the next session usually runs the stops below it" | ran, then never recovered it; worst +11.6 over 715min | level worked; the text assumed a sweep-and-reclaim that never came |
| 29371.5 **GAMMA FLIP** | "We're ABOVE it: they're damping, so fades work. Lose this and hold below and that reverses — **stop fading**" | lost by **10:00Z**, settled below 655min, 11 rejected re-tests, worst +24.5 | **the single most useful line in the brief.** The condition fired 108 minutes in and the rest of the day obeyed it |
| 29339.7 Equal lows ×3 ⭐ | "a real stop cluster. **Prime S1 sweep trigger**" | swept and gone — 600min below, worst +10.4 | level worked as a break, not as the fade the strategy attached to it |
| 29332.0 NY Low (prev-day) | "runs the stops below it" | worst excursion **+0.3pts** over 560min | cleanest rejection on the board |
| 29308.4 PDL ⭐ | "**Sweep it, wait for a higher low on the 1m, then CISD = long**" | chopped both sides (up 41.7 / down 68.8), then 555min below | **sweep-reversal setup did not exist.** Price continued 290pts lower |

### Finding 1 — "7 of 7 held" and "worst hit rate on record" are the same fact, and neither is about the levels

`review_day.py:73` sets the settled side from **`bars[-1]["close"]`** — the
session close. `acted_as` is then `"support" if side_above else "resistance"`
(line 94). For any level price crossed once on a day that closed far beyond it
and never came back, `worst_excursion` is small by construction and `held` is
`True` **necessarily**.

This day fell 321 points and closed 90pts below its lowest touched level. **7 of
7 "held as resistance" was not available to be otherwise.** Across all 8 graded
days the grade tracks the sign of the day, not the level:

| | resistance | support |
|---|---|---|
| 5 down days (08-24, 08-28, 09-08, 09-09, 09-10) | **37** | 5 |
| 3 up days (08-25, 08-26, 08-27) | 3 | **37** |

Near-total separation by day sign, 8 sessions. See §4/M6 — this is the review
tooling, not the model, and it invalidates the provisional commit's headline.

### Finding 2 — the 15:07 board published only levels it told the reader not to trade

Two levels: STRUCTURAL CALL WALL 29,294.4 (*"Mark it and leave it… not an
intraday trigger"*) and STRUCTURAL PUT WALL 28,744.4 (same text). **Neither was
touched. Hit rate 0.00.**

Meanwhile **PUT WALL 29,194.4** — 22pts from spot, 0.69bn, and the level price
actually broke through on its way to 29,018.3 — was relegated to the *"Beyond
today's range (context only, **don't mark**)"* footnote by the `budget * 1.75`
filter against a **0pt** budget. Same for MAX PAIN 29,444 and GAMMA FLIP 29,339.

Credit where due: the secondary-walls table carried 29,194.4 with the **correct**
short-gamma note — *"dealers are SHORT gamma here… price tends to accelerate
THROUGH rather than stall. **Not a floor**"* — and that is exactly what happened.
The brief had the right read, in the table it tells the reader is research-
adjacent, while the board it tells the reader to mark held two levels it
disclaimed in the same sentence. **Third recorded instance of D7** (after 09-08
and the 09-10 provisional); D7's fix landed in `113a5a1`, *after* this scan.
Reported as confirmation, not as a new proposal.

### Finding 3 — PD close is noise for the third time

Published **+10.0** from spot at 08:12. Worst excursion +1.7pts. A level 10pts
from price on a 464pt day carries no information. Running tally of
distance-at-publication: 09-08 +3.1 and −1.5, 09-10 +10.0. Still 2 days — see §4.

---

## 3. What was wrong, and why

### The 08:12 no-call: the engine was 2 points short, and held exactly one term that has never been anything but +2

Bias **−1** by bucket (`inputs.bias_components`, 08:12):

```
gamma +2   vol −1   rates −1   macro +1   breadth −1   fuel 0   structure 0   news −1   = −1
```

`bias_engine.py:271` calls **−3** MILDLY BEARISH. At −1 the brief called nothing
on a day that fell 321 points.

**Inside macro:** `real_yields` 0, `yield_decomp` −1, `credit` **+2**,
`fin_conditions` 0, `liquidity` 0, `curve` 0. Macro's entire positive content was
`credit`. Strip it and the score is **−3 → MILDLY BEARISH → CORRECT.**

**`credit` has scored +2 on 22 of 22 scans ever recorded** — every scan of every
day, including the non-trading PREP runs. Mechanism (`fred_probe.py:220`):

```python
wide = (hy5 or 0) > 0.15
"signal": -2 if wide else (1 if hyv < 3.0 else 0)
```

signal `+1` × `_W["credit"] = 2` → **+2**. The bear branch needs HY OAS to widen
**15bp over 5 days**; observed 5-day changes across all 8 days are
+4, +3, −1, −5, −6, +2, +2, +5 bp — never within a third of the trigger. The
bull branch needs only a *level* below 3.0%; observed levels are **2.65–2.75%**,
never close to 3.0. **The bear side is a change test, the bull side is a level
test, and in a calm-credit regime only one of them can ever fire.** The engine's
effective neutral point is +2, not 0.

The sibling term in the same function already does it correctly —
`fin_conditions` scores the *change* in NFCI (`nf = g("NFCI")`, `chg_1`), which
is why it printed **0** points on 09-10 while its prose described the *level* as
*"a background tailwind for stocks"*. One function, two conventions; the one on
the weight-2 term is the wrong one.

### That is not hindsight on one day — regraded across all 15 deduped scans

| | now | with `credit` centred at 0 |
|---|---|---|
| CORRECT | 5 | **7** |
| WRONG | 5 | **3** |
| no call | 5 | 5 |

Changed verdicts: 08-24 09:37 and **09-10 08:12** no-call → **CORRECT**; 08-28
22:33 and 09-08 15:39 **WRONG → no call**. **Zero correct calls broken**, 11 of
15 unchanged. 4 of 8 days improve, 0 of 8 degrade.

### The +2 that was true at the moment and false 108 minutes later

`gamma +2` read *"above flip 29371.5 by **48.0pts** — long-gamma, dips
supported, upside grinds"*. 48pts is **14% of ADR14** — inside a single bar's
noise on a day that ran 464. The term is a step function at the flip with no
proximity scaling, so a coin-flip position collected full weight. Price lost the
flip by **10:00Z** and, per the grader, spent the remaining **655 minutes** below
it with 11 rejected re-tests and a worst excursion of +24.5.

The brief's own prose stated the reversal condition explicitly and it fired
inside the London session. **The score had no mechanism to notice.** This is the
same shape as H10 (prior-week displacement with no reclaim condition) on a
different term — and it is now the second term found scoring a boundary as
though it were a regime.

### The structure term voted for the direction price actually swept

`structure +1` — *"in-reach unmitigated pools: **6 above / 4 below — draw
higher**"*. Price ignored all six above and took out all four below. Running
record of this term when it fires non-zero: **3 right / 3 wrong** over 6 firings
across 5 days (08-24 09:37 +1 ✗, 08-24 12:40 +1 ✗, 08-26 21:43 +1 ✓, 08-27 13:23
+1 ✓, 08-28 22:33 −1 ✓, 09-10 08:12 +1 ✗); zero on the other 16 scans. See §4.

### What was not wrong

- **The EXHAUSTED read was exact.** Budget 0.0, extension 0.0. Third consecutive
  accurate low-fuel call (08-25: 12.0 vs 0.4; 09-08: 26.2 vs 0.0; 09-10: 0.0 vs
  0.0). **Do not touch the low end of the fuel model.**
- **The 15:07 rebuild got everything right** — regime (short gamma, −119pts below
  flip), model, and direction, at −10 on a 3-bear-headline PPI print.
- **`gamma −2` for week net GEX −3.795** and **`rates −3`** for US10y +1.59% were
  the correct same-day, instrument-specific reads, and at 15:07 they were not
  outvoted.
- **The GAMMA FLIP line was the brief's best sentence of the day** and it was in
  the 08:12 brief, 108 minutes before it mattered.

---

## 4. Change proposals

`track.py` reports `actionable: True` at 8 days ≥ `MIN_SESSIONS = 3`. As
`track.py:222` itself warns, that is a day count and not evidence. Read per item.

### Proposed — P4: `credit` scores a level where its own bear branch scores a change

- **What to change (user decides — I have edited nothing).** Make the bull side
  of `credit` a change test, symmetric with the widening branch that already
  exists: a *tightening* HY OAS scores +1; calm-and-unchanged scores **0**.
  Keep the `-2` widening branch exactly as it is. This is **not** a deletion —
  in a genuine credit event the term should still fire hard.
- **Evidence.** +2 on **22 of 22** recorded scans, 8 graded trading days,
  HY OAS 2.65–2.75% throughout, 5-day change never beyond ±6bp against a +15bp
  trigger. A term with one observed value is a constant, and a constant in a
  signed score is an offset, not a signal.
- **Expected effect.** Across all 15 deduped scans: direction **5R/5W → 7R/3W**,
  no correct call broken. On **09-10 08:12** specifically, −1 → −3 → MILDLY
  BEARISH → **CORRECT** on a −321pt day. On 09-08 and 08-28 it converts a wrong
  call to a no-call.
- **No new data point needed.** `chg_5` for `BAMLH0A0HYM2` is already fetched and
  already used by the widening branch.
- **Caveat, stated plainly.** This is an in-sample counterfactual on 8 days, and
  it **interacts with the still-open P1** (FRED staleness): 08-28 and 09-08 are
  days P1 also claims. The two must be evaluated together, not stacked. **09-10
  is clean of that interaction** — `real_yields` scored 0 here, so this day's
  result is attributable to `credit` alone. That is why it is the day worth
  deciding on.
- **Why it clears the gate.** 8 sessions, one direction, and the defect is
  structural rather than statistical: the asymmetry between a level test and a
  change test in the same expression is visible in the source without reference
  to any outcome. Same family as D6 — a component whose comment assumes a
  behaviour the code does not implement.

### Proposed — M6: the grader's verdict is a function of the session close, so "did the level hold" is currently unanswerable

- **What to change.** Grade a level against the **direction of approach** and a
  reversal threshold measured from the touch, not against `bars[-1]["close"]`.
  Report `acted_as` only where price approached, reacted, and the reaction can be
  distinguished from the day's drift. `review_day.py` is measurement, not scoring
  logic — but I am proposing rather than editing, per standing constraint.
- **Evidence.** 8 sessions: resistance:support is **37:5** on the 5 down days and
  **3:37** on the 3 up days. The mechanism is `review_day.py:73` and `:94`, read
  directly. 09-10 is the extreme case: the biggest trend day on record produced a
  **100% hold rate** and the **lowest hit rate** on record simultaneously.
- **Expected effect.** Three open items are currently measuring the wrong thing
  and would become testable: **H6** ("is the level board producing clean
  reactions"), **H14's remaining empirical claim** (does a put wall act as
  resistance-after-break in short gamma — the 7 put-wall touches on record split
  4 resistance / 1 support / 2 lost, but that split is *derived from the close
  side*, so it is not evidence either way), and the **"walls 7/7"** headline in
  `22e9c1c`, which should not be relied on until then.
- **Not calibration.** No threshold is being tuned; a verdict is being made
  independent of a variable it should not depend on.

### Not proposed — still observing

- **H1 — the budget's problem is dispersion, not bias.** Day errors now
  +61.2, −11.6, −73.0, −86.4, −10.7, −26.2, −64.0, **+57.3**; mean −19.2, sign
  flips. H1's "do not fit a multiplier" stands. **New observation:** day error
  correlates with realised range at **r = 0.951**, slope **0.648** — the two
  under-reads are the two largest-range days (530.9, 463.9) and the three worst
  over-reads are among the smallest. That is the signature of a forecast with too
  little *spread*, which would need a slope change rather than the offset H1
  already refused. **But error-vs-outcome correlation is also what regression to
  the mean produces mechanically, so this is not yet a finding.** What would
  settle it: regress `budget` on realised extension directly and read that slope.
  Do not touch the fuel model — and specifically not its low end, which is 3 for
  3 exact.
- **The unmitigated-pool term.** 3 right / 3 wrong over 6 firings, 5 days; zero
  on 16 of 22 scans. Meets the day gate, but 3–3 on n=6 is chance, and chance is
  not the same as a demonstrated absence of skill. *Watching:* the next 4
  firings. **Do not touch `_W`.**
- **The wall-band position term.** Gave **+2** at 15:07 (*"bottom 20% of the wall
  band — poor risk/reward for shorts"*) on a scan where price then fell a further
  91pts to the close and had already made its low 198pts lower; gave **0** at
  08:12 at 22% up the band, 2 percentage points the wrong side of its own
  threshold. With 09-08's correct −2 at the top of the band that is **2 non-zero
  observations**. Far too few. *Watching:* its next 3 firings, and whether the
  20% threshold is doing real work or just splitting noise.
- **Gamma's step function at the flip.** 09-10 is the first clean instance of
  full weight awarded 48pts (14% of ADR) from the boundary, followed by the
  boundary breaking. **1 session.** *Watching:* distance-from-flip at scan versus
  whether the flip survived the session, over the next 3 scans that score
  non-zero gamma within 0.25 ADR of the flip.
- **PD close / PD mid as noise.** Third uninformative instance (+10.0 from spot
  today), but still only 2 days. *Watching:* distance-at-publication and
  reaction grade — and note this cannot be settled before **M6**, since the
  reaction grade is the contaminated variable.
- **`fin_conditions` prose describes the level, scores the change.** Scored 0, so
  harmless today, and it is the *correct* convention. Noted only because it is
  the control that shows P4's convention is the outlier. No change proposed.

### Standing items unchanged

M3, M4, M5 and **P1** remain awaiting the user's decision. P4 above is the first
item that materially interacts with P1 and should not be decided independently of
it. H9, H10, H11, H12, H13 gained no evidence today. No scoring file was edited;
no `prediction` block was touched.
