# REVIEW — 2026-09-17 (day after the FOMC hike)

Graded 2026-09-18 from `review_day.py 2026-09-17 --json`. 1 scan, **0 test
artefacts**. History context from `track.py`: 13 trading days, 22 deduped scans,
`actionable: YES` on the 3-day hypotheses.

---

## 1. Scoreboard

| | |
|---|---|
| Session O / H / L / C | 28983.4 / **29500.5** / 28955.7 / 29430.9 |
| Range / net | **544.8** / **+447.5** (net = 82% of range) |
| ADR14 | 371.2 → range was **1.47x ADR** |
| Bars | 276 |

**Direction** — 0 right / 0 wrong / **1 no-call**.
Scan 12:46Z PRE_NY, bias **−2 NEUTRAL / TWO-WAY**, `expected_direction` 0.
Post-scan move **+9.4** (1.7% of range). No call was made, so nothing is graded.
Running record: **9 right / 7 wrong / 6 no-call**.

**Levels** — 4 published, **1 touched, hit rate 0.25** (13-day mean 0.53). The
one touched level did not hold. 3 of 4 never reached.

**Fuel** — budget **0.0**, actual extension **40.0**, error **+40.0**,
`fuel_call: about right`. Traversal 186.6 inside the range. This is the
**largest zero-budget error on record** (previous: +26.6 on 09-14 17:23).

---

## 2. What the levels actually did

Only one of four levels was ever in play. That is the finding, and it is a
board-construction finding, not a market one — see §3.

| Level | dist | Brief said | Actually did |
|---|---|---|---|
| **29451.5 CALL WALL** ●●●●● 3.03bn | +26 | "desks must SELL as price rises into it, so **rallies stall**. Take profit into it… the **strongest ceiling on the board**" | **Broadly vindicated, graded `lost`.** Price closed **20.6 below it**; session high exceeded it by only 49.0. But it leaked: `worst_excursion` **+31.2** inside the settled window, over the 25pt tolerance, so `held: false`. |
| **29201.5 MAX PAIN** | −224 | "price drifts toward it as the week goes on… strong by Thursday/Friday" | **Never reached** on a **Thursday**. Nearest approach was 245.8pts away. Second instance against the day-of-week qualifier (first: 09-16, where it was the day's best level on a Wednesday — opposite direction). |
| **29004.3 PD mid + PUT WALL** ●●○○○ | −422 | "Heaviest floor this week — expect a bounce and a good long-sweep here… strongest floor on the board" | **Never reached.** Published 422pts away against a **0pt** range budget. |
| **28930.6 Asia Low + GAMMA FLIP** | −495 | "Lose this and hold below and that reverses — stop fading" | **Never reached.** Published 495pts away. The conditional could not fire. |

**Two things worth recording about the call wall.**

1. **The wall had already been exceeded before the brief was written, and the
   brief did not know.** `range_at_scan` 504.8 against a session low of 28955.7
   (the low is provably pre-scan: post-scan traversal was only 186.6, so price
   could not have made a 470pt round trip) puts the **pre-scan high at 29460.5 —
   9.0pts above the call wall**. The brief presented 29451.5 as "+26 away" and
   offered "a held close above flips that selling to buying and it becomes a
   launchpad" as a forward scenario. It had already been tested and rejected
   that morning. The level board carries `dist` but no field for *"price has
   already traded through this today and failed"*.

2. **The verdict string is inverted relative to the close.** `review_day.py:161`
   renders `settled_side: below` + `held: false` as **"broke UP through it"**, on
   a day price closed **below** the level. The wording is defensible as a
   description of the *excursion*, but the day's one-line summary now reads as if
   price finished above the call wall when it finished 20.6 under it. This is not
   a new proposal — it is a wording addendum to **P-B**, filed 09-17, which
   already asks for `worst_excursion` to be printed wherever `held` is quoted.
   Today is exactly the case P-B predicted: a verdict decided by the 25pt line
   (31.2 vs 25.0) on only **65 minutes / 13 bars** of settled data, barely over
   the 6-bar minimum.

**Fade-day call: correct, and it should be said.** The brief led with *"This is
your fade day… expect a stall… the day's range is set"*. Range extended **40pts**
and price traversed **186.6 inside** it. The `gamma −2` row ("price sits in the
top 20% of the wall band — poor risk/reward for longs") was the sharpest row on
the page: price was 26pts under the call wall and went **+9.4** in the remaining
eight hours.

---

## 3. What was wrong, and why

No direction call was made, so there is no bad direction call to trace. The
failures are in the **board** and in two components that were wrong for
mechanical reasons.

`inputs.bias_components`, total **−2**:

| pts | component | verdict |
|---|---|---|
| **+2 / +2 / −2** | `gamma` — above flip / pinning likely / top of wall band | **All three right.** Pinning was right (40pt extension), the top-of-band penalty was right (+9.4 post-scan). |
| **−2 / −1** | `vol` — VIX9D/VIX 1.119 BACKWARDATED "expect range expansion"; VXN/VIX 1.44 | **Wrong, and outvoted correctly.** The day pinned. Mirror image of 09-16, where the same row was the only one that called expansion and was outvoted. Nothing arbitrates between the gamma-pinning rows and the vol-expansion row — the unarbitrated conflict logged 09-17 now has an instance on **each** side. |
| **+3** | `rates` — US10y 4.951 (−1.10%) "yields down, BULLISH tech" | Right on the day's direction (+447.5), untestable post-scan. |
| **−3** | `macro` — DFII10 real yield | **Scoring data it knows it does not have.** See below. |
| **−2** | `news` — "4 auto-scored (0 bull / 4 bear) → BEARISH" | **Two of the four headlines say the index went UP.** See below. |
| **−1** | `breadth` — NDX +0.03% vs ES +2.16% | Directionally wrong (NDX ran +447.5 from the open) but the row reads pre-scan cash, so it is not falsified by the session. |
| **0** | `fuel`, `events` | `events` scored 0 for the **15th consecutive row**. Day after an FOMC hike and the component is silent. |

### The `news −2` was set by headlines whose own text says equities rose

This is a defect, reproduced from source, not an inference:

```
$ python3 -c "import news_scorer as ns; ..."
'Nasdaq, S&P 500 Futures Rebound After Fed Rate Hike...'          rule=hawkish  dir=-1  conf=HIGH  flags=[]
'S&P 500, Nasdaq, Dow Futures Inch Higher As Investors Digest...' rule=hawkish  dir=-1  conf=HIGH  flags=[]
```

Both were **counted**, both at **HIGH** confidence with **zero flags**, both
scored **−1**. The component reported "0 bull / 4 bear". Two of those four bears
are headlines reporting a rally.

**Mechanism — two independent causes, both in `news_scorer.py`:**

1. **First-match-wins over an ordered rule list.** `score_item` runs
   `for name, pat, … in RULES: if not re.search(...): continue` and **returns on
   the first match**. `hawkish` is at **line 71**; `risk_on`
   (`rally|surge|soar|jump|rebound|…`) is at **line 109**. A headline containing
   both "rate hike" and "rebound" can only ever be read as `hawkish`. The
   competing evidence in the same sentence is never examined.
2. **The confidence set is asymmetric.** `HIGH_CONFIDENCE` (line 234) contains
   `hawkish`, `cpi_hot`, `cpi_cool`, `dovish`, `jobs_strong`, both tariff rules,
   `earnings_beat/miss`, `capex_up/down`, `credit_stress`, `shutdown` — and
   **not `risk_on`**. So the bearish reading is auto-scorable and the bullish
   reading, even if it were reached, is not. The two failures compound: the
   bearish rule wins the race *and* is the only one allowed to vote.

The existing flag machinery does not catch it. `REVERSAL_UP`, `CONTRAST`,
`MODAL` and `HYPOTHETICAL` all return empty on "Futures Rebound After Fed Rate
Hike" — "after" is not a contrast token.

**This is not D9.** D9 (*"the news tagger reads a keyword without its subject"*)
is the same family but the **opposite sign and no damage**: there a bearish
headline got a bullish tag and **fell into NEEDS_JUDGEMENT, scoring 0**. Here the
misread headlines were scored at full weight. D9's own closing line — *"recorded
so that if it recurs it can be counted rather than rediscovered"* — is now
satisfied, with damage.

**It is also not H19.** H19 is about the *sampling* (which headlines get counted).
This is about the *counted subset being misread*, which H19 explicitly assumes
away. H19's hand-score test is still unrun and is unaffected.

### `macro −3` from DFII10 — fifth instance of H18

The `why` string says it plainly: *"FRED has not published since 2026-09-15
(2 business days ago) — this is last week's reading, not today's."* Sequence
across the freeze, extending H18's table:

`09-10 0, 09-10 0, 09-11 −3, 09-11 −3, 09-14 −3, 09-14 −3, 09-15 −3, 09-16 0, **09-17 −3**`

**Honest accounting of the damage today: none.** Total was −2; without the stale
−3 it is +1, and both are `NEUTRAL / TWO-WAY`. No label flipped and no call
changed. Logged because a component that scores data it has flagged as absent is
a defect whether or not the day punishes it. **P1 already covers it; no new
proposal.**

---

## 4. Change proposals

One new proposal. Everything else below threshold, or already open, is logged and
not re-proposed.

### P-D — the board filter ran backwards: it footnoted a level 6pts away and published three at 224–495pts (5 days, 6 scans)

On 09-17 the board's two filter arms in `brief.py:414-432` produced a board of
four levels of which **three were 224–495pts away on a 0pt budget**, while
**"29432 London High (today)", 6.2pts from spot, was sent to the
"Beyond today's range (context only, don't mark)" footnote.**

Both arms are individually defensible and together they invert:

- The `ALWAYS` exemption (`CALL WALL`, `PUT WALL`, `GAMMA FLIP`, `MAX PAIN`) is
  **unbounded** — *"Distance is information, not grounds for removal."* This is
  **D7 applied, 2026-09-10**, and D7 was right about the cases it was fixing.
- The `CORE` arm (session extremes, PD/PW) still keeps
  `abs(dist) <= budget * 1.75`. D7 deliberately left it: *"those are genuine
  reachability claims, so the rule fits them."* **When `budget` is 0.0 the rule
  says nothing at any distance is reachable — including 6pts.** That is the same
  category error D7 named, surviving in the branch D7 chose not to touch. It is
  also **D15**, which found it a third time in the *path read*, and whose stated
  candidate fix is the one below.

**Evidence, arm 1 — far walls are not levels.** Touch rate of published levels by
distance-at-scan, all trading-day scans on record:

| dist at scan | published | touched | rate |
|---|---|---|---|
| ≤100 | 143 | 116 | **0.81** |
| 100–200 | 69 | 44 | **0.64** |
| 200–400 | 26 | 4 | **0.15** |
| >400 | 15 | 2 | **0.13** |

Past 200pts the touch rate collapses to **6 of 41 (0.15)**. 09-17's board had
three such rows and all three missed.

**Evidence, arm 2 — the zero-budget footnote hides levels that get hit.** Every
scan on record where the budget was ≤12pts banished a level within ~50pts to the
"don't mark" footnote, and **all six landed inside the session's realised range**:

| day | scan | budget | closest footnoted level | dist | reached? |
|---|---|---|---|---|---|
| 08-25 | 13:04 | 12.0 | 29237 Equal lows ×2 | 15.8 | inside range (H 29342.6 / L 28945.5); touch timing not separated |
| 09-10 | 15:07 | 0.0 | 29194 PUT WALL | 22.8 | **yes** — D7's own record: *"respected to 4.8pts across three re-tests"* |
| 09-11 | 12:47 | 8.4 | 29370 London High (today) | 33.8 | **yes**, H 29475.8 |
| 09-11 | 13:24 | 0.0 | 29451 London High (prev-day) | 46.5 | **yes**, H 29475.8 |
| 09-14 | 17:23 | 0.0 | 29265 NY High (today) | 18.3 | **yes**, H 29291.4 |
| 09-17 | 12:46 | 0.0 | 29432 London High (today) | **6.2** | **yes**, H 29500.5 — and already exceeded pre-scan |

**5 distinct trading days, 6 scans, 5 confirmed post-scan touches.** Threshold met
on both arms.

**Proposed** — apply **D15's already-written candidate fix to both arms of
`keep()`**, which is the substitution `secondary_walls()` has always made and the
board has now failed to make four times (D7 ×3, D15, this):

- **(a)** Replace `abs(dist) <= budget * 1.75` on the `CORE` arm with an
  **ADR-based window** (`secondary_walls()`'s own window). A session extreme 6pts
  away is on the board regardless of the budget. **No new calibration** — reuse
  the existing constant.
- **(b)** Keep `ALWAYS` walls in the brief, but move those outside the same ADR
  window into a clearly separated **"out of reach today"** block rather than the
  numbered board. They stay visible — *distance is information* — but they stop
  occupying board rows and stop entering the hit-rate denominator.

**Expected effect.** 09-17's board becomes roughly two actionable rows
(29451.5 call wall, 29432 London High) plus a three-row out-of-reach block, in
place of four rows of which three were unreachable. The headline level hit rate
**rises** (0.25 → ~0.5 on this day) and becomes meaningful, because the
denominator stops containing levels the model itself scored as unreachable. This
also removes the largest remaining source of H6's denominator pollution, and it
interacts with **P-B(b)** (cluster within `TOUCH_TOL` before grading) — both
change the same statistic and should be judged and re-measured together, not
sequentially.

**No scoring change.** P-D touches board construction and prose only.

### Logged, not proposed

- **News scorer rule-order + confidence asymmetry (§3).** 3 trading days
  (08-24, 09-11, 09-17), 5 headline instances, reproducible from source.
  Threshold is met and the fix is small — but **it is a scoring-input change and
  H19's hand-score test is still unrun.** Changing the scorer now would destroy
  the baseline H19 needs. Filed as **D18** in `HYPOTHESES.md` with the
  reproduction, so it is a one-line change whenever H19 resolves or whenever
  `news_scorer.py` is next opened. **Recommend it be fixed then, not now.**
- **H18 / P1, fifth instance.** No damage today (−2 vs +1, same label). P1 open.
- **H1, zero-budget bucket.** 09-17's **+40.0** is the largest zero-budget error
  on record and takes that bucket's MAE from **8.9 (n=3) to 16.7 (n=4)** while
  `>0` stays near 75. The zero/non-zero split survives but the "keep the number
  when it is zero" half of **P4** is weaker than at n=3. Note the structural
  point: **a zero budget can only ever err in one direction**, so its MAE is a
  biased estimator and will only rise. Appended to H1; P4 not re-proposed.
- **Max pain's day-of-week qualifier**, second instance against — missed entirely
  on a Thursday, having been the day's best level on a Wednesday (09-16). Both
  instances contradict the qualifier in **opposite directions**, which is weaker
  evidence than two in the same direction. n=2 of the 3 required.
- **The unarbitrated gamma-pinning vs vol-expansion conflict** now has one
  instance on each side (09-16 expansion, 09-17 pinning). n=2. Watching.
- **`events` has scored 0 on 15 of 15 rows**, including the day after a rate
  hike. Mechanism behind **P-C**; not a separate proposal.
- **"Price has already tested this level today"** — no such field exists, and its
  absence made the call wall's "a held close above becomes a launchpad" text
  misleading. n=1. Watching.

### Considered and rejected

- **Widening `SETTLE_TOL` so the call wall grades `held`.** 31.2 vs 25.0 is
  exactly the near-the-line case **P-B** exists to expose; tuning the constant to
  make today's verdict read better is fitting the instrument to one day. P-B's
  answer (report the excursion, cluster the levels) is the right one.
- **Dropping the backwardation vol row** after it called expansion on a pinned
  day. It was *right* on 09-16 and outvoted. One instance each way.
- **Any claim from the +447.5 day move.** The entire move was pre-scan
  (`range_at_scan` 504.8 of 544.8). Post-scan was **+9.4**. Grading the neutral
  call against +447.5 would be dishonest.

---

*Observations below threshold appended to `journal/HYPOTHESES.md` under
"Observations appended 2026-09-18".*
