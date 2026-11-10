# REVIEW — 2026-11-09 (Mon, LONDON scan 12:47:13Z)

Graded 2026-11-10 from `review_day.py 2026-11-09 --json`. One scan,
`is_trading_day: true`, 264 bars, `test_artefacts: 0`. No prediction block was
touched.

## 1. Scoreboard

| | |
|---|---|
| Session O / H / L / C | 26847.1 / 28017.9 / 26640.2 / 27892.6 |
| Session range / net | 1377.7 / **+1045.5** (direction **+1**) |
| Call | **MILDLY BEARISH −3**, `expected_direction −1`, `PIN_THEN_EXPAND`, `LOW_FUEL` |
| Direction | **0 right / 1 wrong** |
| Post-scan move | **+652.7** (direction +1) |
| Budget vs realised | budget **228.1** · extension **772.8** → **UNDER by +544.7**, **3.39×** |
| Traversal vs budget | 894.0 → **3.92×** |
| Range vs ADR14 | 1377.7 vs 795.6 → **1.73× ADR** |
| VXN-implied range | **582.0** published as *"below ADR — use the smaller budget"* → realised 1377.7, **under by 795.7** |
| ATM straddle band | ±427 → 26729..27583; close **27892.6 OUTSIDE above by 309.6** |
| Levels | **12 published / 4 touched = 0.33** |

`+544.7` is the **second-largest budget error in the record** behind 11-05's
`+1261.2`, and the **fourth consecutive** under-estimate (11-04 +305.9, 11-05
+1261.2, 11-06 +174.0, 11-09 +544.7) — five of the last six.

## 2. What the levels actually did

**Only 4 of 12 rows were touched, and all four were within 194pts above the
scan price.** The day travelled **862 points above the scan price** and the
board's resolution above +194 was: nothing until +931.

### The four touched rows

| level | published claim | what happened | verdict |
|---|---|---|---|
| **27350.0** CALL WALL ●●●●○ + shelf ⭐ | *"Heaviest ceiling this week — desks must SELL as price rises into it, so rallies stall. Take profit into it."* | touched 14:30, then **+391.3 further up**; close **542.6 ABOVE it**; high **667.9 above it** | **FALSIFIED as a ceiling.** `review_day` grades it *"stalled at it — held as support for 385min, worst −2.0pts"* — a verdict about a claim the brief never made. |
| **27301.7** PDH | *"the biggest pile of stops above us. Sweep it, wait for a lower high on the 1m, then CISD = short"* | swept at 14:30, ran **+716.2** to the high, closed **590.9 above** | **FALSIFIED, and it is the one row that carried an executable instruction.** The published trade was a short at the launch point of a 700pt rally. `review_day` reports *"broke DOWN through it — lost by 94.7pts"* / `acted_as: lost` on a level price finished 591 above. |
| **27207.7** Asia High (today) | *"the next session usually runs the stops above it"* | run, held as support 395min, worst −12.7 | **RIGHT** |
| **27170.5** London High (today) | *"the next session usually runs the stops above it"* | run, held 455min, worst −26.3 | **RIGHT** |

The only two level notes that described the day are the two
session-extreme stop-run rows. Both gamma/liquidity rows that asserted a *brake*
were sliced.

### The 8 untouched rows, and the dead half of the board

- **5 of 12 rows (42%) sat below the scan price — 27100, 27050, 27000 (STRUCTURAL
  PUT WALL ●●●●● 1.14bn), 26968.7 (PD close), 26550 — and price never traded a
  single point below the scan price after the scan.** The entire downside board,
  including the chain's largest single concentration and §3's named downside
  brake, was published into a side that did not occur. That is not a level
  failure; it is the board being laid out for the call rather than for the tape.
- **3 of 12 rows were marked `(stretch)` / "not an intraday trigger" — and they
  are the rows the day actually aimed at.** The high **28017.9** finished **69.7
  below GAMMA FLIP 28087.6** and **132.1 below MAX PAIN 28150.0**, both flagged
  beyond the 228pt budget. The budget's `stretch` flag suppressed exactly the two
  levels that would have framed the close.
- **The empty middle, again.** Between CALL WALL 27350 and GAMMA FLIP 28087.6
  there is a **737-point gap with no published row**, and the session high landed
  in it. The §7-adjacent secondary table's only upside entries (27400, 27450)
  were both inside the first 300pts and both crossed.

**Candidate to stop publishing:** nothing yet. The structural put wall was
untouched for the 4th time and the strict P3/H6 count stays blocked, as carried.

## 3. What was wrong, and why

`gamma −5 · vol −2 · macro +2 · structure +2 · news −2 · rates +1 · breadth +1 = −3`.

**This is a near-exact replicate of 10-26** (`gamma −5 · vol −2 · macro +2 ·
structure +2 · news −2 · breadth −1 = −6`, WRONG, with `structure +2` the only
block that called the day). On 11-09 `structure +2` — *"price above PD mid"* and
*"in-reach unmitigated pools: 3 above / 2 below — draw higher"* — is **again the
only block that called the day**, and it was again outvoted 5-to-2 by `gamma`.

### `gamma −3` — amplitude spent as direction (instance 3 of the same shape)

> *"below flip 28087.6 by 931.4pts — SHORT gamma, dealers amplify: downside
> accelerates, rallies unstable"*

Short gamma is an **amplitude** statement. The amplification arrived — 1.73× ADR,
3.39× the budget — and **pointed up**, exactly as on 10-26 (+399 off the
post-scan low) and 11-04 (traversal 2.126× ADR). The branch still has no term
separating *falling away from the flip* from *grinding back toward it*, and
11-09 is the cleanest grind-back in the series: price closed **195.0 below the
flip** having started **931.4 below it**, i.e. it spent the session closing 79%
of the gap the −3 was sized on. **Routes to the unarbitrated two-gamma-rows
conflict; no number taken.** The brief's own §2 prose is direction-neutral
(*"sweeps tend to keep running rather than fail"*) while the score makes the
same fact −3 directional — the contradiction is internal to one document.

### `gamma −2` — a range claim carrying a direction

> *"week net GEX −0.446 $bn/1% -> expansion likely"*

**The content was RIGHT and the sign it contributed was WRONG.** Expansion
arrived at 1.73× ADR; it expanded upward. This is the cleanest isolable instance
of the shape in the record, because the row's own predicate was satisfied. H22
(n=19, *"label right and not discriminating"*) takes **n=20**; the
direction-vote limb belongs to the two-gamma conflict.

### The two gamma signs, one vote — again

`near_expiry_0_2dte = +0.329` (**positive**) drove `PIN_THEN_EXPAND`, while the
direction score consumed only the weekly **−0.446**. Same configuration as
10-26/10-27. No number taken; existing register item.

### `rates +1` and `breadth +1` — both legs measured on windows that do not match

**This is D22(a), and it is now confirmed from source AND quantified on the
`rates` row for the first time.** See §4 — the row was right-signed today, but
`rates`'s own two legs covered different sessions, and on a prior-session basis
`rates` inverts from `+1` to `−3`, taking the score from −3 to **−7, i.e. more
confidently wrong**. That matters for which fix is chosen and is the reason
§4 does not propose the obvious one.

### What was right, and should be said

- `vol +2` *"VXN 34.02 (−11.1%) — fear falling, bullish"* — **right**, and VXN
  fell a further −14.8% on the session.
- `structure +2` — **right on both limbs**, and the pool-draw row named the
  direction 862 points before the high.
- `macro +2` net — right-signed, on the stalest rows in the engine (H18/P1).
- §1's hedge *"Strategy-1 fades have a materially lower hit rate here — only take
  them at the far walls"* — **right**: the near fade (27350) lost by 667.9; no
  far wall was reached.
- §2's *"Chop early, resolve late… from roughly 13:00 ET the pin weakens"* —
  **wrong on timing in the direction that mattered**: the decisive break of
  27350/PDH came at **14:30Z = 09:30 ET**, the cash open, 3.5 hours before the
  named window. P-I (withdraw the `PIN_THEN_EXPAND` timing prose) takes a
  supporting instance.

## 4. Change proposals

`track.py` reports `actionable: YES`, but the flag is a **global day-count gate**
(`n_days >= MIN_SESSIONS`, `track.py:185`) whose own source comment warns it has
been *"read far more"* into than it supports. It licenses nothing on its own;
each item below carries its own count.

### PROPOSED — D22(a), third limb: `yahoo_series` legs, and the choice of window

**No new ID allocated. H28 / D32 / P-J remain free.** This is D22(a) (opened
2026-09-24), whose own entry already named `rates`/DXY as unverified blast
radius — *"those were not shown to be wrong and are not claimed to be."* They
are now shown.

**Mechanism, confirmed in source.** `macro_probe.py:58` —
`last = meta.get("regularMarketPrice") or closes[-1]` — against
`macro_probe.py:64` `prev = closes[-2]`. For a ~24h symbol
`regularMarketPrice` at 12:47Z is **today's live price** and `closes[-1]` is
**today's partial bar**, so `chg_pct` is **today's intraday move**. For a cash
index that does not print pre-market, `regularMarketPrice` is the **stale prior
close**, so `chg_pct` is the **prior completed session**. The docstring at lines
59-63 records fixing precisely this class of bug for `chartPreviousClose` and
left the `last` line unfixed. `bias_engine.py:187-191` then differences two such
legs as though they shared a window.

**Blast radius, enumerated per symbol** (the open question D22 never answered).
Independent fetch at 2026-11-10 12:5xZ, `regularMarketPrice` compared against
the returned dated daily closes:

| symbol | has a dated bar for *today*? | `chg_pct` window | fed into |
|---|---|---|---|
| `^NDX` | no | **prior session** | `breadth` |
| `^VXN` | no | **prior session** | `vol` |
| `^TNX` `^FVX` `^IRX` | no | **prior session** | `rates` |
| `NVDA` `MSFT` `AAPL` `AVGO` | no (pre-market is a separate field) | **prior session** | `breadth` |
| **`ES=F`** | **yes** | **today, live intraday** | `breadth` |
| **`DX-Y.NYB`** | **yes** | **today, live intraday** | `rates` |

**Exactly two symbols are affected, and both are differenced against
prior-session legs inside the same component.** `rates` mixes a prior-session
`^TNX` with a live DXY; `breadth` mixes prior-session mega-caps and `^NDX` with
a live ES.

**Quantified point impact, five consecutive scans, all legs from independent
Yahoo daily closes (DX-Y.NYB: 11-03 101.87 · 11-04 101.51 · 11-05 101.55 ·
11-06 102.30 · 11-09 101.65; ES=F: 11-03 7596.75 · 11-04 7720.50 · 11-05
7383.00 · 11-06 7402.00 · 11-09 7574.25; `^NDX` matched the prior session to
2dp on all five, so the NDX leg is not at issue):**

| scan | printed DXY | pts | prior-session DXY | pts | printed NDX vs ES | pts | prior-session | pts |
|---|---|---|---|---|---|---|---|---|
| 11-04 | −0.55% | **+2** | +0.12% | 0 | +0.68 / +0.93 | **−1** | +0.68 / +0.29 | **+1** |
| 11-05 | +0.10% | 0 | −0.35% | 0 | +0.91 / +0.03 | **+1** | +0.91 / +1.63 | **−1** |
| 11-06 | +0.42% | **−2** | +0.04% | 0 | −6.36 / +0.22 | −1 | −6.36 / −4.37 | −1 |
| 11-09 | −0.41% | **+2** | +0.74% | **−2** | +1.35 / +0.67 | +1 | +1.35 / +0.26 | +1 |
| 11-10 | +0.12% | 0 | −0.64% | **+2** | +3.40 / −0.01 | +1 | +3.40 / +2.33 | +1 |

**DXY: 4 of 5 scans change points, one of them a full 4-point sign flip (11-09).
Breadth: 2 of 5 change sign, 2 points each.** DXY's `±0.4` gate
(`bias_engine.py:150`) also put 11-09 **0.01pp** from the threshold and 11-06
**0.02pp** over it — the mixed window is being read through a hair-trigger.

**Which leg to normalise — the evidence says LIVE, not prior-session, and it is
not the answer the correctness argument alone would give.** Recomputing the
breadth row with both legs on the overnight window, using the NQ roll the brief
**already computes and prints** (`nq_implied`, *"rolled forward by the NQ
futures move"*: 11-04 +128.0, 11-05 −229.0, 11-06 +399.0, 11-09 +166.2, 11-10
−106.8, against the prior cash close):

| scan | printed | prior-session | **live/overnight** | day went |
|---|---|---|---|---|
| 11-05 | +1 **wrong** | −1 right | **−1 right** | down hard |
| 11-06 | −1 **wrong** | −1 **wrong** | **+1 right** | +331.9 up |
| 11-09 | +1 right | +1 right | **0 neutral** | +1045.5 up |

**Live basis 2 right / 1 neutral / 0 wrong; printed 1 right / 2 wrong;
prior-session 2 right / 1 wrong.** The whole-score check points the same way:
"both prior-session" moves 11-09 from −3 to **−7** (more confidently wrong) and
11-06 from −19 to −17, while leaving 11-04 unchanged — it is **not** an accuracy
improvement. Live also leaves DXY as-is, which is the only self-consistent
choice given DXY cannot be made prior-session without discarding the overnight
FX move an intraday brief wants.

**Proposal, for the user to decide — two parts, the first unconditional:**

1. **Correctness (ship regardless of the window choice):** `yahoo_series` should
   return the window it measured, and every consumer should print it. The
   *"NDX x% vs ES y%"* and *"DXY n (±m%)"* sentences assert a shared present
   tense they do not have. **Evidence: 5 consecutive sessions, 10 of 10
   leg-pairs mis-windowed by construction, 6 of them point-changing, one a
   4-point sign flip.**
2. **Accuracy (the weaker claim, n=3, direction of travel only):** put the
   `breadth` NDX leg on the overnight window. Zero new data: `NQ=F` is already
   on the same Yahoo endpoint and returned a live quote on the fetch above, and
   the brief already derives the same number internally. **Expected effect:**
   `breadth` goes 1-right/2-wrong → 2-right/1-neutral on 11-05/11-06/11-09;
   score impact ±1 to ±2, no label change on any of the three.

**What would falsify part 2:** three further sessions in which the live-window
breadth row is wrong-signed while the printed row is right. **Record both
variants every scan.** The mega-cap average and `^TNX` stay prior-session under
this proposal and would then be the remaining mismatch inside `breadth` and
`rates` — named, not proposed.

### NOT PROPOSED — a new data point, named and deliberately declined

`ZN=F` (10-year note future) is **free and returned a live quote on the same
endpoint** (11-09 close 107.0625 → 11-10 live 106.828), so a live overnight
`US10y` leg is technically available. **It is declined:** I cannot say what it
would have changed on any specific day without three sessions of paired
readings, and the 09-21 *"one change at a time"* rule applies while part 1 above
is live. **n=0. Watching: the overnight ZN move against the printed `^TNX`
prior-session move, every scan.**

### NOTHING PROPOSED — data points appended to existing entries

- **H1 / P4 — REFRESHED, `track.py` completed (exit 0) after ~35 min.** Error
  **+544.7**, second-largest in the record behind 11-05's **+1261.2**; **4th
  consecutive under-estimate**, five of the last six. **n=30 days / 30 scans,
  and NOTHING aged out this run** — the sample still starts 09-28, exactly as on
  11-06. **Per-day mean +104.4 → +119.1**, and unlike 11-06's move this one **IS
  a single data point**: one session shifted the headline statistic of the model
  by **+14.7 points**, which is itself an argument about how thin the sample is.
  `H5` **`late` n is still 0** at 30 days — the early/late split remains
  untestable.
- **D31** — counter-instance **12, 5th consecutive session, same direction**:
  VXN-implied **582.0** published as *"use the smaller budget"* against realised
  **1377.7**, under by **795.7** (11-06 403.3, 11-05 1504.0, 11-04 802.8).
  Allocated and proposed on 11-06; data point only.
- **H8** — post-closure instance **6, a MISS**: band ±427 → 26729..27583, close
  **27892.6 outside above by 309.6**. Post-closure **3 hits / 3 misses**.
  **CLOSED ANSWERED-POSITIVE, not reopened** — but the post-closure record is
  now a coin flip and that is worth stating.
- **H23** — two brakes, and they **split**: upside **27350.0** at +194
  **sliced by 667.9 (0.839× ADR — the largest slice in the series)**; downside
  **27100.0** at −56 **never reached**. Census **17/3/4 → 18 sliced / 3 capped /
  5 never-reached**, n=27.
- **P-E** — instance **13** on the 11-06 numbering: **SLICED**, and by the
  largest margin the series holds. The *empty middle* claim takes a direct
  instance — a **737pt** unpopulated gap between the call wall and the flip, and
  the session high inside it.
- **H26** — a 3–5 bucket instance, **WRONG**; `|post|/ADR = 0.820`,
  `range/ADR = 1.732`. The magnitude-as-range-forecast limb is supported (a −3
  delivered 1.73× ADR); the direction limb falls.
- **H17 / P-H** — **no instance either way**: post-scan **+652.7 = 47.4% of the
  session range**, far outside the proposed 5% deadband, and day-net and
  post-scan agree (both +1, both WRONG). **Not** a deciding instance; P-H stays
  at 6.
- **H2** — instance **14**, `LOW_FUEL`, bias −3, **WRONG**; the fade at the only
  reachable wall **LOST by 667.9**. **Counter-instance to 11-06's fade win, and
  it cuts the other way on the live gating question:** the 11-05 gamma-gating
  proposal's conditions were all satisfied today (below flip −931.4, week GEX
  −0.446, `LOW_FUEL`) and the fade it would have deleted **LOST**, where on
  11-06 the same gate would have deleted the instruction that **WON**. The
  census is **split and I do not advance it**; the 11-06 resolution — propagate
  §1's existing *"only take them at the far walls"* condition into §2 and §3
  instead of picking a winner — is **directly supported** by today, because the
  near wall lost and no far wall was reached.
- **H10** — the −3 branch did **not** fire (price **inside** the prior-week range
  26247.5–28838.9). No instance; stays 4-for-11 / 3-for-11.
- **H22** — **n=20**, label right and still not discriminating; today it is the
  *expansion-claim-carrying-a-direction* instance described in §3.
- **H18 / P1** — duplication **40 of 40** by construction. `macro +2` from
  DFII10/DGS10 (both as of **2026-11-05**, 2 business days stale, and the brief
  said so) against a live `rates` row: **both pointed the same way and both were
  right-signed**; collapsing them moves −3 to −4, still WRONG. Sign-opposition
  streak stays at 0. **Rendering proposal stands; no weight change.**
- **H27** — observation **10**. Correlated pairs (`gamma −5`, `vol −2`) carry
  **−7 of a −3**; the *"independent"* remainder is **+4, opposite-signed and
  RIGHT**. **Falls AGAINST the founding claim**, after observation 9 was
  recorded INERT. Weight limb stays ANSWERED-NEGATIVE, nothing re-proposed.
- **H19 / `news`** — coverage **3 of 68 relevant = 4.4%**; `news −2` on a
  **+1045.5** day. All three scored headlines were bearish and all three were
  **already in the price** (the 11-05/11-06 Nvidia and Amazon/Intel stories),
  while the unscored list carried *"Dow futures rally 500 points"* **twice**.
  Supports both the sampling-bias-bearish limb and the already-in-the-price
  limb; the latter reaches **n=3** and is the strongest instance of it —
  **recorded, not proposed**, because the fix is an event-age field that is
  itself only at n=2.
- **P-I** — supporting instance: `PIN_THEN_EXPAND`'s *"from roughly 13:00 ET"*
  against a resolution at **09:30 ET**, the cash open.
- **M6** — session **42**, and a **new form**: the two inverted verdicts are
  inverted *about which claim was graded*, not about the window.
  `acted_as: support` / *"worst −2.0pts"* on **27350, published as a ceiling and
  exceeded by 667.9**; `acted_as: lost` / *"broke DOWN through it"* on **PDH,
  which the session closed 590.9 above**. The settle-window defect is present
  too, but the driver today is that `settled_read` has **no field for the side
  the brief claimed** — it grades every level as a two-sided pivot. That is a
  distinguishable limb and it is **n=1; nothing opened.**
- **D30** — the brief's `fuel.today_range` **567.5** against `review_day`'s
  `range_at_scan` **604.9**: a **37.4pt** disagreement about the same pre-scan
  window, on the high side only (both share the low 26640.2, and 567.5 is
  exactly the brief's own Asia-High-minus-low). **Condition instance, mechanism
  not asserted** — the two figures may differ by bar feed rather than by the
  21:00Z roll. The proposal is unaffected.
- **D23** — observation **19, CLEAN**: offset **−0.0**, `nq_implied`,
  `repriced_bs_at_current_spot`, cash **3812 min** stale and the staleness was
  disclosed in §4. D6 breach series stays at **six**.
- **D25 / D27** — §7 **10th consecutive non-render** (`HTTP 401` on
  `/v2/NDX/classic/gex_full`), **13th consecutive `gexbot` 401**. H12/H13
  untestable, D25 SUPPRESSED, P5 no instance.
- **D21** — **no firing**: `gamma +0`, price **76%** up an 800pt band, 4 points
  under the 80% gate. Not a near-miss by the 10-19/11-06 standard. The band was
  **800 points = 1.01× ADR** and the day ran **1.73× ADR**, so the percentile
  the gate reads was measured on a container smaller than the move — D21's
  width defect again, in non-firing form.
- **D7 / D15** — the structural rows (28600, 27000) again carry `stretch: true`
  in `prediction.levels` with the tag unprinted; **48 of 48**. Condition only.
- **P-C / `events`** — `events` row **absent from `bias_components` again**;
  `event_gate: null` with one **Medium** row 20.2h out, which is correct. The
  11-06 firing stays the only one in 70 scans.
- **P-F** — **no instance**: price **inside** the prior-day range
  (26247.5–27301.7) at scan. Stays 5 same-signed.
- **Board side-composition — condition n=3, and it is a BENEFIT case.** 7 of 12
  rows (58%) sat on the side opposite the direction call (11-05: 8 of 15;
  11-06: 4 of 5). **On 11-09 that helped** — the day went the way of the
  majority side. Three conditions, and the harm count does **not** advance.
  **This argues the item should be reframed as "the board is laid out for the
  call" rather than treated as a harm series, and it stays unopened.** Per-side
  rates for prior sessions are not in `review_day`'s output and were **not**
  recomputed.
- **No instance:** H3 (CLOSED-NEGATIVE) · H4 (flip never reached, nearest
  **69.7**) · H5 (`late` n still **0**) · H6/P3 (no reachable structural row;
  strict count stays 2 clean / 1 confounded) · H7 · H9 · H11 · H12/H13 (401) ·
  H14 (put wall never approached post-scan) · H15 (HY OAS scored **−2**, more
  evidence against the retired dead-weight claim) · H16 · H20/H21
  (CLOSED-NEGATIVE) · H24 · H25 · D8 · D9 · D14 · D15 · D18 · D20 · D22(b)
  (`^NDX` matched the prior session to 2dp on all five scans checked — **no
  two-session skip**) · D24 (clean control) · D26 (see hygiene) · D28 (one
  `events_24h` row, printed; condition stays n=2) · D29 G1–G4 **applied
  unchanged**, `LONDON` census n=6 · P-B / P-B(b) · P-E(b) · P-G (the two
  session-extreme rows printed the *correct* side-prose, both above price and
  both run — a **clean control**, the first since 11-05) · the max-pain
  day-of-week clause (*"weak on a Monday"*, printed on a Monday, **untested** —
  never reached by 132.1).

## Journal hygiene

One scan file for 11-09 (`1247-london.json` + `.md`), `is_trading_day: true`,
**264 bars**, `review_day` reports **0 test artefacts**, `outcome: null` (not
back-written — correct). **No fabricated or backfilled entry found.** The
`prediction` block was read and not modified.

**`track.py` COMPLETED (exit 0)** — after being killed by a 300s timeout on the
first attempt, the second run finished in ~35 minutes. **30 trading days / 30
scans, 6 `test_artefact` entries excluded as always, and 09-25 is held back no
longer: it has aged out of the window entirely, so no hand-quarantine was needed
for the second consecutive review.** Only **11-10** is held back (181 bars, not
finished).

**D26 — the gap is UNCHANGED at 19, and my pre-completion hedge was wrong in
direction.** 51 journal directories hold a scan, 50 hold an
`is_trading_day: true` scan, **49** of those are finished trading days, against
**30** full bar sets. The 11-06 run was 48 against 29 — also 19. Before the run
completed this review guessed *"at least 20 and widening"*; **it is 19 and flat,
and the guess is retracted.** It is recorded here rather than quietly fixed.
