# Review — trading day 2026-11-17 (graded 2026-11-18)

One scan: `1247-london.json`, `is_trading_day: true`, `outcome: null`, 276 bars,
`review_day` reports **0 test artefacts**. The file has exactly **one commit**
(`e5b3b57`) — written once, never edited; no `prediction` block was touched. No
`is_trading_day: false` scan entered any statistic below.

Also in scope, at the runner's request: **independent verification of four
claims about today's (11-18) undelivered-outcome scan.** Those are recorded as
scan-level observations, not graded outcomes.

---

## 1. Scoreboard

| | |
|---|---|
| session O / H / L / C | 27203.5 / 27413.2 / 26575.4 / **26997.8** |
| range · net | **837.8** · **−205.7** |
| call | **−17 STRONGLY BEARISH**, `expected_direction −1` |
| post-scan move | **−328.2** → **CORRECT** (day-net −205.7 also CORRECT) |
| direction, both bases | agree — **no P-H deciding instance** |
| H17 noise test | post-scan is **39.2%** of session range — far outside the 5% band |
| levels published · touched | 20 · 6 → hit rate **0.30** (fleet 0.48) |
| of the 6 touched, held | **0** — every one graded `lost` |
| budget · extension · error | 532.4 · 426.4 · **−106.0** (0.80×) |
| traversal vs budget | 772.1 · **1.45×** |
| fuel verdict | *about right* |
| realised ÷ ADR14 | 837.8 / 943.8 = **0.888×** |
| realised ÷ VXN-implied | 837.8 / 566.0 = **1.480×** |
| `track.py` after this day | 31 days / 31 scans · **14 R / 13 W / 4 no-call = 51.9%** · H1 per-day mean **96.9** |

`track.py` exit 0 (~31 min). No `actionable: YES/NO` string in this build; the
header line (*"31 of 3 days … threshold met, read the evidence before
proposing"*) was used and is quoted, not silently substituted. **No day aged out
of the 45-day window on this run**, so 13/13 → 14/13 is a genuine +1 and not a
window artefact. D26's gap: 31 full bar sets against 55 finished day
directories — **24**.

---

## 2. What the levels actually did

**The whole upper board was never tested.** 14 of 20 rows were published above
price; the post-scan high was **27347.5** — only 37.8 above the scan price and
**65.7 below** the session high. That high, 27413.2, was the Asia high, set
**9h12m before the scan**, so the nearest row above price (27381.6, +72) was
never reached either. Not a
failure of the levels — a failure to be in the right half of the chart.

The six that were touched, against what the brief said:

| level | brief said | what happened | verdict |
|---|---|---|---|
| **27193.1** PD close | *"price often comes back to fill a gap from here"* | came back at 14:30, chopped, settled below, 56.7 adverse | prose unfalsifiable; it did come back |
| **27146.5** PDL + NY Low ⭐ | *"sweep it, wait for a higher low, then CISD = **long**"* | swept, then **205.0 further down** inside the hour | **wrong, and it contradicted §1** |
| **27096.4** Asia Low | *"the next session usually runs the stops below it"* | ran **521.0** below | right |
| **27076.2** Equal lows ×2 | *"prime **S1** sweep trigger"* | sliced, **500.8** below | **wrong, and it contradicted §1** |
| **27006.0** PUT WALL ●●●●● | *"if it breaks, expect it to speed **UP**, not bounce. Don't buy the break."* | broke, accelerated **430.6** further, closed **8.2 below it** | **right — the best call on the board** |
| **26640.2** PWL *(stretch)* | *"big pool, best Mon–Tue"* | reached on a Tuesday, pierced by **64.8**, reclaimed, closed **357.6 above** | right in substance; graded `lost by 50.7` |

Three things worth naming:

**The put-wall row was the day.** In short gamma it told the reader not to buy
the break and to expect acceleration; price then ran 430.6 points. It is also
where the day settled — the close was 8.2 points under it.

**A 365.8-point hole swallowed the session.** Between the put wall 27006.0 and
the PWL 26640.2 there is no published level. **65 of 98 post-scan 5-min bars
(66.3%) closed inside that hole**, and 66 of 98 (67.3%) closed below everything
on the board except the PWL. The session low 26575.4 is **64.8 below the lowest
published row**. Meanwhile §3 named the clear-corridor far end at **26206.0** —
a price that appears nowhere on the board. This is **void instance 5**, and the
first where a *majority* of the post-scan session traded inside one void.

**The level board's liquidity rows are still regime-blind.** Two rows printed
Strategy-1 instructions (*"CISD = long"*, *"prime S1 sweep trigger"*) on a
document whose §1 says *"Strategy-1 fades have a materially lower hit rate here
— only take them at the far walls"* and whose §2 says *"fading is the wrong trade
today"*. Both lost by ~500 points. Census below.

---

## 3. What was wrong, and why

**Nothing about the direction was wrong.** −17 on a day that fell 328.2
post-scan is the grade the engine is built for, and the composition was
right-signed: `vol −6 · gamma −5 · macro −4 · breadth −3` against `rates +1`.
Removing any one block leaves the call intact (worst case `macro −4` out →
−13, still ≤ −3). So the findings here are about **rows that were right by
accident, rows that were stale, and verdicts that are artefacts of the grader.**

- **`macro −4` was entirely rear-view, and this time it amplified a correct
  call.** Both rows are a FRED print dated **2026-11-13**, two business days
  old at scan: `DFII10 −3` (*"up 5bp as of 2026-11-13"*) and `DGS10 −1`
  (*"moved 5bp up (11-12 → 11-13)"*) — **the same 5bp move counted twice**
  (H18/P1 duplication; collapsing them is −17 → −14). **Checked and NOT found:
  a repeat print.** DFII10's as-of date advanced one business day on each of
  11-12 / 11-13 / 11-16 / 11-17 (11-09 → 11-10 → 11-12 → 11-13), so the
  Veterans-Day repeat of 11-12 did not recur. The rear-view block stays
  **two-sided**: 11-05 cancel-a-correct, 11-06 amplify-a-wrong, 11-10
  cancel-a-correct, 11-11 amplify-a-wrong, **11-17 amplify-a-correct**. *Late,
  not biased* survives; no weight change proposed.
- **`breadth −1` compared two different windows again, and this time it did not
  matter.** Verified from source (and already logged by the 11-17 review as an
  ungraded-day observation, so **no new instance is claimed**): NDX **−2.672%**
  is the true prior session and matches the print; `ES=F` printed **−0.03%**
  against a true prior-session **−1.899%** (error 1.87pp) because
  `macro_probe.yahoo_series` takes `meta.regularMarketPrice` for a symbol that
  is still trading. Corrected to both-prior-session the gap is **−0.773pp**,
  still clears the −0.2 gate, row **survives at −1**. Point-changing on nothing.
- **`structure +1` was wrong-signed and said so in its own text.** *"In-reach
  unmitigated pools: 6 above / 3 below — draw higher"* on the day price went to
  the one pool it did not count. Two-sided row; nothing proposed.
- **`news +0` on 0-of-63 is not a dead component, but one miss is a defect.**
  The judgement list carried *"Fed's Musalem: US likely needs several **rate
  hikes** by spring to control inflation"*. `news_scorer.py:71`'s hawkish
  pattern is `\b(hawkish|rate hike|raise rates|…)\b` — **the plural fails the
  trailing `\b`**, and so does `rate cut` vs `rate cuts` in the dovish rule,
  while the same file writes `payrolls?`, `jobs?`, `tariffs?`, `rise[s]?`
  elsewhere. Verified by direct `re.search`. Right-signed on the day (a hawkish
  −1 on a −205.7 session) but **not grade-changing** (−17 → −18).
- **Two grader artefacts, both already owned.** **M6, session 46:** the put
  wall's verdict is *"broke UP through it — lost by 61.2"* for a level price
  finished **8.2 below** and traded **430.6 below** — the entire read hinges on
  an 8.2-point margin in the closing bar, and had the day closed 9 points
  higher the same level would have been graded against a 430.6-point excursion
  instead of 61.2. **Five of the six `lost` verdicts are 34.3–61.2 points**, i.e.
  0.036–0.065× ADR, against an absolute `SETTLE_TOL = 25.0`. The rescaling
  sub-note for that was opened 09-21 and **falsified** — it is not reopened, and
  it is recorded here that today's six verdicts are all inside the zone that
  falsified it.

---

## 4. Change proposals

### Proposed — **D32 (NEW ID)**: the heavyweight-earnings feed returns 403 and fails silently

`macro_probe.py:158` fetches
`https://api.nasdaq.com/api/calendar/earnings?date=…`. Probed live today for
11-17, 11-18 and 11-19: **HTTP 403 Forbidden on all three**, as is every other
`api.nasdaq.com` path tested (`economicevents`, `quote/NVDA/info`) — a host-wide
block. `_json` converts the error to `{"_error": …}`, and the caller's
`((j.get("data") or {}) or {}).get("rows") or []` turns that into an empty list.
There is no `_earnings_error` key (contrast `_ff_error`, which *is* recorded for
the Forex Factory calendar), nothing in the brief, and `source_health.py` —
which *does* carry a `nasdaq_earn_cal` probe — is not in the scan path at all.

**Evidence, 11 sessions:** the last scan with an `events` component row is
**2026-11-03** (*"AMD earnings 2026-11-03 time-after-hours (cons $1.68) —
sector-relevant"*). **Every scan from 11-04 to 11-18 inclusive — 11 trading days
— has zero `events` rows.** NVDA's quarterly report fell inside the 5-day window
on 11-12, 11-13, 11-16 and 11-17, and `bias_engine.py:262` holds a string
written specifically for it (*"INDEX-DEFINING event; day before pins, day after
expands"*) that **never printed on either side of the event**. 11-17 is the day
before and 11-18 the day after; both are silent.

**This also contaminates an existing entry.** P-C's census reads the empty list
as *"and there were none"* in nine separate places (lines 6396, 6721, 7054,
7550, 7818, 8387, 8810, 14373, 18136). For scans **up to 11-03 that reading is
sound** — rows did appear, 44 of 87 scans carry one. **From 11-04 onward it is a
swallowed failure, not an absence**, and P-C's *"dead weight"* framing cannot be
argued from that block.

**Proposed:** (a) record the fetch error (`out["_earnings_error"]`) and print one
line in the brief when the earnings feed is down, same as any other degraded
source; (b) re-scope P-C's census to end at 11-03. **Explicitly NOT proposed:** a
new data source, a scoring change, or any use of `events` as a direction term.
**Expected effect:** no score, level or gate change. The brief stops presenting
"no heavyweight earnings" as a fact when it has no idea.

### Proposed — **P-I, second limb** (prose only): `COHERENT_SHORT` asserts two things the classifier never tests

`gex_levels.py:493–495` prints, for every `COHERENT_SHORT` day: *"Every expiry
is short gamma **and it deepens with tenor** — the whole options book is
positioned for movement."* `expiry_structure` reads only `near` and `far`
(`:491`) and tests **neither** claim.

**Census from the journal, all 70 trading-day scans:**

- *"deepens with tenor"* is **false on 8 distinct trading days** — 09-14, 09-15,
  09-28, 10-07, 10-08, 10-12, 11-04, 11-18 — and on four of them the back book
  is *shallower* than the front by more than 1bn (09-28 −6.874 → −4.798, 10-07
  −4.447 → −1.522, 10-08 −5.945 → −3.787, 10-12 −3.092 → −1.268). The following
  `do` line (*"Today's ADR can be exceeded — don't cap the target too early"*)
  is reasoned off exactly the property that is absent.
- *"every expiry"* is false by the module's own `DEADBAND_BN = 0.05` on **1 of
  54** `COHERENT_*` firings — **today, 11-18** (`week −0.02` → `_sign = 0`).
  **n=1, logged, nothing proposed on that clause.**

**Proposed:** drop *"and it deepens with tenor"*, or gate it on
`abs(far) > abs(near)`. **Placement:** this is **P-I's second limb**, not a new
number — P-I already owns *prose in `expiry_structure` that asserts more than
the classifier computed* (it withdraws the `PIN_THEN_EXPAND` timing string in the
same function). Opening D32-for-prose alongside it is the collision pattern the
ID section exists to prevent. **Expected effect:** no score, shape, level or gate
change. **Honest limit: I did not establish outcome harm** — whether those 8 days
exceeded ADR is a separate question H22 already owns.

### Proposed — **D9, second limb** (false-negative side): the news rules miss plurals

`rate hikes` and `rate cuts` both fail `news_scorer.py:71/73`. Three sessions
carry an unscored plural in the *printed* judgement list — 10-08 (*"Fed's Waller
signals further rate hikes as inflation stalls"*), 10-26 (*"Fed rate hikes: What
borrowers should expect"*), 11-17 (*"Fed's Musalem … several rate hikes by
spring"*) — and 10-29 shows the gap being **masked** when `cpi_hot` catches the
same headline first. **The census is a lower bound**: the brief prints only 8 of
40–60 judgement items, so sessions with an unprinted plural cannot be counted.
**Proposed:** `hikes?` / `cuts?`. **Changed no grade on any of the three days**,
so this is a correctness fix; by the one-change-at-a-time rule it sequences
**behind** D22(a).

### Verified for the runner, nothing proposed — today's (11-18) scan

1. **D22(a) reproduces in full, and it is the strongest instance in the record.**
   Printed vs true prior session (11-16 → 11-17 close), own Yahoo fetch
   13:00–13:05Z, arithmetic reproduced through `yahoo_series`:
   NDX **−0.72%** printed vs **−0.718%** true (**match** — cash, closed) ·
   `ES=F` **+0.26%** printed vs **−1.075%** true (**sign flip, 1.335pp**) ·
   `DX-Y.NYB` **+0.32%** printed vs **−0.058%** true (**both inside ±0.4 →
   `rates +0` either way**, and the printed value sat **0.08pp** from the gate).
   The ES mechanism is code-certain: `meta.regularMarketPrice` is live for a
   future that is still trading, and the current fetch reproduces it exactly
   (regularMarketPrice 7370.0, `closes[-2]` 7359.0 → +0.149%).
   **The threshold reading is correct** — `journal.py:68` emits ±1 only at
   `|score| ≥ 3`. On corrected data the breadth row is **+1** (*tech leading*),
   the published **−3** becomes **−1**, and the brief's bearish call becomes
   **NO CALL**. Printed narrative *"tech lagging, rotation out of tech"* is
   exactly backwards: NDX outperformed ES by **0.357pp**.
   **Two corrections to the runner, both in its favour:**
   (i) the flip is **window-repair-agnostic** — on part 2's basis (both legs
   live: the brief's own `nq_implied` roll **+159.5 / +0.591%** against ES live
   **+0.26%**) the row is **also +1**, so part 1 and part 2 agree today and the
   instance does **not** discriminate between them; margins are **0.157pp**
   (part 1) and **0.131pp** (part 2) — both thin, which routes to the
   **bias-gate fragility** watch item.
   (ii) it is **part 1's FIRST grade-changing instance**, which matters more than
   part 2's second: the standing correction on the register is *"correcting to
   both-prior-session changes ZERO direction grades across all six scans"*, and
   **that sentence now needs restating.**
   **One thing the runner's framing overstates:** 11-18 is **ungraded** — the
   session closes at 21:00Z. Whether the no-call is an improvement or the loss of
   a correct call is **not yet knowable**, and it must not be counted as either.
2. **The prose/score mismatch reproduces verbatim and is placed, not opened.**
   `bias_engine.py:91–93` is exactly as quoted: points use `±0.2`, prose uses a
   bare `net < 0`. There are in fact **three** thresholds on the same number in
   one brief — points `±0.2`, prose `0.0`, and `gex_levels.DEADBAND_BN = 0.05`
   for the shape classifier. Today's `−0.02` is inside all of them except the
   prose's. **Instance count, from the journal: 9 of 70 scans have
   `|week| ≤ 0.2`** (so the row scores 0 while the sentence asserts a regime);
   H22's own founding table already contains one (09-10, −0.058) and never named
   the asymmetry. **Placement:** the *prose* half is **H22**, which owns this
   exact sentence and already carries the candidate fix (*strip the range
   language from the row*) deliberately unshipped; the *gate* half is the
   **bias-gate fragility** watch item, opened 11-11 after the register was
   grepped for exactly this. **No near-duplicate opened.** Today's `COHERENT_SHORT`
   on −0.089 / −0.02 / −2.265 is handled under P-I above. **No harm established
   on either limb.**
3. **Sanity checks confirmed clean.** `nq_implied` offset **−22.3** (reference
   27161.3 vs CFD 27139.0), well inside the ±40 band whose specification the
   11-17 review showed to be an algebraic identity on this basis — a clean
   D23 observation (run length not re-derived), **D6 breach census stays at
   seven**. `CALL WALL 27477.7` and
   `PUT WALL 26977.7` both present and converted. Archive **1d7a0ee** verified on
   `origin/main`, 12:47:03Z, 4 files; working tree clean.
4. **Context confirmed.** `event_gate: null` is correct per spec —
   `bias_engine.py:254` gates only on High-impact events `0 ≤ hours_away ≤ 1.5`,
   and FOMC Minutes are **6.2h** out (D24 clean control). `news +1` is the first
   positive news row in this run and it is driven by two NVDA beat-and-raise
   headlines auto-scored `earnings_beat`. **One thing to flag against it:** the
   `breadth` mega-cap leg printed **NVDA −0.44%**, the pre-earnings 11-17 cash
   session, while NVDA traded **159.7–160.3 pre-market against a 155.46 close
   (+2.7% to +3.1%)**. The window is the row's *intended* prior-session window,
   so this is not a D22(a) instance — it is the condition under which that
   window is actively misleading. **n=1, nothing proposed.**

### Existing entries taking data points (no numbers taken)

- **The level board — void instance 5**, described in §2: 365.8-point hole,
  **66.3% of post-scan bars closed inside it**, session low 64.8 below the
  lowest row, §3's corridor end 26206.0 unpublished. **n=5 condition; harm still
  not demonstrable** — the §3 instruction was *continuation, do not fade*, and
  the absence of marks did not stop that trade working.
- **P5 — instance 3, and it is weaker than instance 2.** Secondary strike
  **26606.0** (*"dealers are SHORT gamma here … **Not a floor**"*) finished
  **30.6 points off the session low**, with exactly **one** 5-min bar closing
  below it (26601.0 at 15:50Z) and the close **391.8 above**. But unlike 11-16,
  **the main board did have a row nearby** — PWL 26640.2, 64.8 off the low — so
  *"the main board had nothing within 300 points"* does **not** hold today. The
  other secondary, **26806.0**, had its *"amplify, not a floor"* prose **right**
  (7 bars closed below, price went 230 through). Secondary table **1 right / 1
  wrong** on the downside.
- **The §3 "clear corridor" far end — third data point, and it argues the other
  way.** 26206.0 landed **369.4 below** the session low, against 20.3 (11-16)
  and 31.7 (11-13). The 11-17 review's *"two sessions is noise and the
  distribution says so"* is confirmed; this is why the corridor end is **not**
  proposed as a board row.
- **PDL *"sweep it … CISD = long"* reaches n=3 — and the obvious discriminator
  is FALSIFIED.** Census **1 win / 2 losses** (11-13 win, 11-16 −390.1, 11-17
  −205.0 within the hour and −500.8 by the low). **All three scans were below
  the flip in short gamma** (`gamma −3` on each), so gating the row on regime
  would have deleted the one winner too. The only visible difference is distance
  to the flip — the winner was **21.8** below it, the two losers 954.7 and 590.8
  — which is **n=1 per side and is not a rule.** The condition reaches 3
  sessions; **nothing proposed**, because nothing separates them.
- **Event gate — outcome n=1 → n=2, and both worked identically.** 11-17's
  post-print 30-min window (13:30–13:55Z) was **H 27332.8 / L 27237.0**; after
  14:00Z the **H was never revisited** (16.2 short) and the **L was swept at
  14:30Z and ran 661.6 further = 0.701× ADR**. 11-13 was H never revisited
  (110.9 short), L swept **at 14:30Z**, ran 690.6 (0.78× ADR). **Both sweeps are
  at the NY cash open to the minute**, which raises a mechanism question the
  entry should carry: the gate may be measuring *"the pre-NY range is the sweep
  level"* rather than *"the post-print range is"*. **2 sessions, nothing
  proposed.** P-C.
- **H22 — label WRONG** (week net GEX **−1.985** → *"expansion likely"* →
  **0.888× ADR**), and the *"use the smaller budget"* instruction takes another
  counter-instance (VXN-implied 566.0 under a realised 837.8 by **271.8**).
  **The register's H22 counter is broken and I am not quoting a number:** it runs
  19 (11-03) → 20 (11-04) → 21 (11-05) → **19** (11-06) → 20 (11-09), then
  disappears from the 11-10 … 11-17 blocks. It silently reverted by 2 and nothing
  caught it. Flagged as hygiene; the per-session readings are all still on the
  record and recoverable.
- **D31 — supporting instance, not a counter.** Realised ÷ VXN-implied =
  **1.480**, against the carried *"15 of 17 above 1.0, median 1.54"* and the
  analytic √(8/π) = 1.596. Now **16 of 18 above 1.0**.
- **H1 — error −106.0**, the largest over-forecast since 11-10's −270.2;
  per-day mean **103.7 → 96.9** at n=31.
- **H23 — a never-reached instance.** The only named brake was the **upside**
  stall at 27556.0 (*"take partials into it"*); the post-scan high stopped
  **208.5** short. Downside read *"clear … nothing structural to slow a
  breakdown. If it goes, it has room. Do not fade it."* — **right**, 734.3 of
  post-scan downside travel. Census **21 sliced / 3 capped / 5 → 6
  never-reached**.
- **Fuel vs gamma — a clean control, census stays 7–2.** §3 carried no fade
  instruction on 11-17 (*"continuation is fine to the nearest pool; don't plan on
  a third leg"*), so the two blocks did not contradict. For the record price made
  two legs post-scan (−772, then +422 into the close), not three.
- **H2 — a non-instance** (`MODERATE` fuel, not LOW_FUEL/EXHAUSTED).
  **H10 — did not fire** (price inside the prior-week range at scan; it then
  pierced the PWL by 64.8 and reclaimed, which is the shape H10 is about, but
  the −3 branch never fired so it takes no instance).
  **H26 — a ≥10 instance, CORRECT**, `|post|/ADR` **0.348**.
  **H8 — post-closure hit:** the straddle band 26952–27667 contained the
  **26997.8** close; **closed and not reopened.**
  **H19 — coverage 0.0%** (0 of 63) with the plural defect above as its proximate
  cause on the one clearly tradeable headline; the 11-17 review established that
  `scored_high_confidence == 0` is **not a first** (10 scans / 9 days), so this is
  a coverage reading, not a dead-component instance.
  **H7/straddle rider — did not fire** (price 590.8 below the flip, 2.16% away,
  against the 0.15% trigger).
  **D21 — no firing** (`gamma +0`, price 61% up the band).
  **D7/D15 — the degenerate marker takes another instance.** 5 of 20 rows carry
  `stretch: true`; **4 printed the tag and the structural row 28656.0 did not**,
  the exemption at `brief.py:588/:1047`. The running total is hand-maintained
  (46 of 46 as of the 11-09 review) and I did **not** re-derive it.
  **D25 — §7 did not render** again (the brief ends at §6). Last counted at 9
  consecutive on 11-09; run length **not** re-derived.
  **D27 — the 401 again** (`[volume-weighted view unavailable: HTTP 401 on
  /v2/NDX/classic/gex_full]`). Last counted at 12 consecutive on 11-09; run
  length **not** re-derived.

---

## Journal hygiene

11-17: one scan, `is_trading_day: true`, `outcome: null`, 276 bars, 0 test
artefacts, single commit, no backfill, no fabricated entry, no `prediction` block
modified. 11-18: one scan, single commit (`1d7a0ee`), **excluded from every
statistic as unfinished** — `track.py` holds it back at 183 bars. 6 historical
`test_artefact` entries excluded by `track.py` as always.
