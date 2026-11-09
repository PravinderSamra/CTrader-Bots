# REVIEW — 2026-11-06 (Fri, NFP) — the record's near-max bearish call on a day that closed +331.9 UP, graded CORRECT by a 28-point drift

_Graded 2026-11-09 from `review_day.py --json` (1 scan, `LONDON` 12:47:49Z) and
`track.py` (**29 trading days, 29 scans, threshold met**; it ran for ~45 minutes
and exited 0 — the first completion in this reviewer's run, after the 6
consecutive failures recorded on 11-02). **D29's G1–G4 applied unchanged, not
re-decided**, per `journal/2026-11-02/REVIEW.md §0`._

**Two pre-registered thresholds were reached on this one scan, and they land on
the same grade: H17 (3 of 3) and P-H (6th deciding instance).** That is the
whole of §4. Nothing else is proposed and no ID is allocated.

## 0. Grading rules applied

- **(G1)** `PRE_NY`-keyed pre-scan censuses do **not** accrue. P-B(b) stays
  **23**, the session-context-field census stays **22**; the parallel
  `LONDON/EST (from 2026-11-02)` censuses go to **n=5**.
- **(G2)** The fuel-error series accepts this scan; the error **+174.0** is
  tagged `LONDON/EST`. Pre-scan market time is the Tue–Fri EST **14h45m**.
- **(G3)** Everything else grades normally.
- **(G4)** The post-close-hour census stays **CLOSED at n=2** (structural, D30).

---

## 1. Scoreboard

| | |
|---|---|
| call | **STRONGLY BEARISH −19** at 27005.0 (`LONDON`, NY cash +102 min), `COHERENT_SHORT` (confidence high), `EXHAUSTED`, Strategy 2 |
| session O / H / L / C | **26626.9 / 27301.7 / 26247.5 / 26958.8** (276 bars) |
| range · net | **1054.2** (**1.370× ADR14 769.4**) · **+331.9** |
| direction, post-scan (P-H basis) | **−28.0 → CORRECT** |
| direction, day-net | **+331.9 → WRONG** · bases **DISAGREE** → **P-H deciding instance #6** |
| post-scan move as share of session range | **2.66%** → **H17's 3rd sub-5% day: THRESHOLD MET** |
| \|post\|/ADR · range/ADR | **0.036** · **1.370** |
| levels | **5 published / 1 touched = 0.20** (`track.py` 29-day mean **0.5**) |
| …by side of the scan | **1 of 4 above price = 0.25** · **0 of 1 below = 0.00** |
| fuel | budget **0.0** vs extension **174.0** → error **+174.0**, `UNDER-estimated`; **every point of it UPSIDE** |
| traversal vs budget | **434.7**, against a budget of zero |
| VXN-implied range | **650.9** — the figure §3 told the reader to prefer — realised **1054.2**, under by **403.3** |
| ATM straddle band (rest of day) | ±**594** → 26411 .. 27599; close **26958.8 INSIDE** |
| offset | **−23.8** (`nq_implied`, `repriced_bs_at_current_spot`, NDX cash **933 min** stale) — **clean** |
| hygiene | 1 scan, `is_trading_day: true`, **0 test artefacts** |

**Which side extended, since it decides the whole review.** `review_day` reports
`range_at_scan` **880.2** and the touched call wall's `travel_up` as **125.5**,
which is exactly `27301.7 − 27176.2`. The session high is therefore **post-scan**,
the pre-scan high was **27127.7**, and the session low **26247.5** was already in
before the brief was written. **A `STRONGLY BEARISH −19` published at 12:47
produced no new low in the remaining eight hours, a 174-point extension of the
high, and a close 331.9 above the open.**

**`track.py`, 29 days (the window moved — see D26):**

| | carried (11-05 review, n=31) | this run (n=29) |
|---|---|---|
| H1/P4 per-day mean error | **+89.3** | **+104.4** |
| direction | 12/24 = 50.0% from source | **13 right / 11 wrong / 5 no-call = 13/24 = 54.2%** |
| mean level hit rate | 0.51 | **0.5** |

**Neither figure is averaged with the other.** The rise in H1 is not one data
point: **09-22, 09-23 and 09-24 all aged out of the 45-day bar window on this
run** (the sample now starts 09-28), and today's **+174.0** entered. **D26's gap
widened from 16 to 19** — 29 full bar sets against **48** finished trading-day
directories holding a live scan. One incidental consequence: **09-24, hand-quarantined
by 29 consecutive reviews, is no longer in the sample at all**, so there was
nothing to quarantine by hand this time.

---

## 2. What the levels actually did

**One of five rows was touched, and it is the only row that was ever going to
be.** On a −19 bearish call the board published **4 rows above price** (+171 to
+1396) and **one below** — a put wall at −679 that price had already traded
**78.7 points through** before the scan.

### The row that was touched, and it worked

| level | what the brief said | what happened | verdict |
|---|---|---|---|
| **27176.2** CALL WALL ●●●●○ 0.39bn | *"Heaviest ceiling this week (33k contracts) — desks must **SELL** as price rises into it, so **rallies stall. Take profit into it.**"* | touched 14:40Z, traded **125.5 through** to the session high, then settled **below** from 15:10 and held as **resistance for 345 min**, 7 further touches, worst excursion **+24.4**, close **217.4 below** | **RIGHT on the official (settled) basis.** The best call on the page |

**P-E — instance 12 on the settled convention: capped.** The overshoot
**125.5** sits inside the *sliced* band (103–185) on a first-touch read and
inside *capped* on the settled read, so this is the first instance that lands in
P-E's **empty middle** depending only on which convention is used. **The 09-09
decision (settled = official) resolves it as capped**; recorded explicitly
because P-E's whole finding is *"no instance between 12 and 103"* and today is
the first one that can be argued either way. Census on the official basis
**5 capped / 6 sliced**.

### The four rows that were not touched

- **28401.2 MAX PAIN (+1396)**, **28376.2 STRUCTURAL CALL WALL (+1371)**,
  **28046.9 GAMMA FLIP + Asia Low prev-day (+1042)** — never within 1074 points
  of the session high. **P3/H6 takes no instance** (the structural wall was
  unreachable again; strict count stays **2 clean / 1 confounded** and the
  *"stop publishing it"* narrowing stays blocked). **H4 no instance** (flip
  never approached). The max-pain **day-of-week** clause — *"strong by
  Thursday/Friday"*, printed on a **Friday** — went untested by 1100 points.
- **26326.2 PUT WALL ●●●●● 0.44bn (−679)**, published as *"the heaviest floor
  this week (95k contracts) … the strongest floor on the board"* with
  *"**if** it breaks, expect it to speed UP, not bounce. **Don't buy the
  break.**"* **It had already broken.** The session low **26247.5** was 78.7
  points beneath it, pre-scan, and price **bounced ~757 points** off that break
  to the scan price. The behaviour the row's own sentence forbids is the
  behaviour that had already happened, hours earlier, on the same tape.
  **H14 takes no post-scan census instance** (the wall was never re-approached);
  recorded **outside** the census, which is the second consecutive EST-era
  session to need that note — 11-04 was *"broken pre-scan by 138.2, bounced
  746.5"*. See §3.3.

### H23 — instance 25, and the named brake is sliced again

*"**UPSIDE path: has friction.** Expect a stall at **27026.2** (21pts away) —
take partials into it rather than assuming a clean breakout."* Price closed the
day **above** it and reached **27301.7 — 275.5 through, 0.358× ADR**. Census of
**named** brakes: **17 sliced / 3 capped / 4 never-reached**. The downside limb
named **no** brake at all (*"every options shelf from here to 26126.2 is negative
gamma — nothing structural to slow a breakdown"*) and went untested, because
there was no breakdown.

**And the brake was PRE-TRAVERSED, which is H23's own sub-claim.** The pre-scan
high **27127.7** was **101.5 above** the level the brief introduced as a stall
*"21pts away"*. The brake is named from a static gamma grid, not from what price
has done to it today — the 10-06 instance recorded exactly this and the
already-proposed fix (drop the assertion or print the measured base rate beside
it) is unchanged.

### D7 / D15 — the degenerate marker, quantified from source for the first time

With a **0.0** budget, **4 of 5** rows printed `_(stretch)_` — identical to
10-19, where this was last logged. The marker's legend says *"anything marked
_(stretch)_ is beyond that, so treat it as partials-only"*, so on a zero-budget
board the **one unmarked row reads as the only reachable one** — and it was the
**STRUCTURAL CALL WALL at +1371**, the second-farthest row on the page.

**Measured across the journal** (`prediction.levels`, 46 structural rows on 30
trading-day scans): **46 of 46 carry `stretch: true` in the record and 0 of 46
printed the tag**, because `brief.py:588` and `:1047` both read
`r.get("stretch") and r["kind"] != "structural"`. **The published document and
the graded record disagree on that field by construction, on every structural
row ever published.** In **8** scans (**7** excluding 09-24) every row was
`stretch` and the structural row was therefore the only unmarked one — 08-24,
08-25, 09-10, 09-14, 09-24, 10-19, 10-22, **11-06**, all at `remaining_budget
0.0`; today's is the farthest of the non-quarantined set at **+1371.2**.

**Nothing is proposed.** This belongs to **D7/D15**, whose 10-19 note reads
*"D7's exemption **did** work: the structural wall is the one row not marked"* —
i.e. the register already treats the suppression as intended, and the row's own
prose (*"the ceiling for the WEEK/MONTH, not today … Mark it and leave it"*)
carries the distance warning. What is new is only the count, and it is a
**condition** count, not a harm count: the row was never reached, so no harm is
demonstrable from the tape.

### M6 — session 41, and the settle-window defect in its textbook form

The call-wall row reads *"**stalled at it** — held as resistance for 345min,
**worst +24.4pts**"* on a level price exceeded by **125.5**. The settle window
opens at **15:10**, after the ~15:00 high it is meant to measure. **Reported as
expected-by-identity** (`review_day.py:159–161` plus the window), flagged only
because a human reading the grade cold would take the overshoot as 5× smaller
than it was. `_first_touch`'s 12-bar verdict — *"traded both sides — chopped
around it"* — is the one honest read on the board today, and it is the limb of
M6 still open.

### P-G — no instance, and the streak of 41 ends

The only session extreme on the board (`Asia Low (prev-day)`) was merged into
the gamma-flip row, where `brief.py:382–385`'s `rank` gives the note to `gamma`,
so **no side-prose was published for it at all**. The footnote rows (PWH, PDH,
equal highs, London Low, NY High, PWL) carry no prose by design. **No
wrong-sided session-extreme note printed today.** The merge limb is a
**condition** instance (a session-extreme note discarded) with **no harm** — the
discarded note (*"the next session usually runs the stops below it"*, on a level
**+1042 above** price) was wrong-sided anyway, so for once the merge threw away
the worse sentence.

---

## 3. What was wrong, and why

The post-scan sign was right by 28 points. **Everything that mattered was
wrong:** the day closed **+331.9**, the one-way downside the document described
never began, and the bearish score was the **largest in the 29-day window**.

### 3.1 Eight of the nineteen points are readings of a session that had already finished — and it is the exact mechanism that cost 11-05, with the sign reversed

| | rows | points |
|---|---|---|
| **forward-looking** (options chain, credit, Fed) | gamma −3 −2 +0 · macro +0 +1 −2 +0 +0 +0 | **−6** |
| **rear-view** (prior-session changes and closing vol prints) | vol −2 −2 −1 −1 · rates +3 −2 · breadth −2 −1 | **−8** |
| state / other | structure −1 −3 +0 · fuel 0 0 · news −1 | **−5** |
| **published** | | **−19** |

Every vol row is a **Thursday close**: CBOE's indices do not print before the
cash open, and the scan is at 12:47Z. Every breadth row is **Thursday's
percentage move** (mega-cap avg **−6.20%**, NDX **−6.36%**). Thursday was the
**2.832× ADR collapse** this reviewer graded yesterday. **The engine read the
crash and scored it as a forecast of more crash**, on the morning after, 43
minutes before NFP, for **−8** of a **−19**.

**This is D22(a)'s window mismatch at scale for the second consecutive session,
and the harm has now been observed in both signs.** On 11-05 the rear-view half
was **+8** and cancelled two thirds of a correct **−12**; today it is **−8** and
amplifies a call the day-net falsified. **n=2, opposite signs — so the rear-view
block is not biased, it is simply late.** D22(a) already owns the mechanism and
is code-certain; **no weight change is proposed**, and the two-sided evidence is
the reason I am not proposing one. A one-sided series would have been a tuning
argument; this one says the block carries a lag, not a bias.

### 3.2 `vol −6` is one latent variable counted four times — n=2, and today it does not change the label

VXN 38.26 (+52.6%) **−2** · VIX9D/VIX 1.226 backwardated **−2** · VXN/VIX 1.44
**−1** · VVIX 134.99 **−1**. The largest vol contribution in the record, tied
with 10-19, where this was first logged at n=1. **Four functions of one
Thursday-close reading, scored independently.**

**Reported against my own case: deleting the block gives −13, still
`STRONGLY BEARISH`, still the same direction call.** On 10-19 the same deletion
flipped the score's *sign* (−5 → +1). So the condition recurs (**n=2**) and
today's **harm is strictly smaller than the first instance**. Below threshold,
and the honest reading is that the block's redundancy only bites when the rest
of the score is near zero. **Nothing proposed.**

The backwardation row's two clauses split again, as they did on 10-19:
*"expect range expansion"* was **RIGHT** (1.370× ADR); *"downside skew"* was
**WRONG**. Only the sign is scored.

### 3.3 The session-context field — EST-era harm instance 2, and G1 is now suppressing a four-instance series

The put wall was published as an intact floor with a conditional
(*"**if** it breaks"*) describing an event that had already resolved the other
way on the same tape. The shape is identical to **11-04** (floor published 9h42m
after price traded 138.2 beneath it and bounced 746.5) and to **09-23** (put
wall published at −127.9 after a 65.3-point break that bounced 193) and
**09-17** (call wall presented as *"+26 away"* after a pre-scan high 9.0 above
it).

- **All-time harm: 4** (09-17, 09-23, 11-04, **11-06**).
- **EST-era harm, which is the census G1 permits: 2** (11-04, 11-06).
- Condition census stays at **22** (`PRE_NY`), parallel `LONDON/EST` at **n=5**.

**Nothing is proposed, and the reason is G1, not the evidence.** D29 fixed that
rule for ~93 sessions and this review applies it unchanged rather than
re-deciding it. **Flagged for the user as a decision, not as a finding:** G1 is
now holding back an item whose all-time harm count is 4 and whose harm shape is
identical across both eras. If a third EST-era instance arrives, the register's
own merge instruction fires — *"this and the H1 session-context sub-observation
should be one proposal about session-context fields, not two"* — and I am
pre-registering that here so the next reviewer does not have to re-derive it.

### 3.4 The three range forecasts on the page disagreed, and the one the brief told the reader to prefer was the worst

| forecast | printed | realised 1054.2 |
|---|---|---|
| remaining range budget | **0.0**, *"the day's range is set"* | extension **+174.0** |
| VXN-implied daily range | **650.9**, *"below ADR — options market prices a quieter day, **use the smaller budget**"* | **under by 403.3** |
| ATM straddle, rest of day | ±**594**, with its own close-to-close caveat | close **INSIDE** |

**D31 — counter-instance 11, and a fourth consecutive session in the same
direction** (11-04 802.8 under, 11-05 1504.0 under, **11-06 403.3 under**). The
mechanism is unchanged and code-certain (`brief.py:996` compares a 1-σ
close-to-close move to a high-low ADR). **D31 was allocated and proposed
yesterday; today adds a data point and no new ID.**

**H8 — post-closure instance 5, a HIT.** Band ±594 off the 11-06 ATM straddle
(699pts, ATM IV 55.5%); close inside. Post-closure **3 hits / 2 misses**; entry
stays **CLOSED ANSWERED-POSITIVE (8 of 10)** and is **not** re-opened. Worth one
line: the straddle band was the only one of the three that worked, and it is the
only one carrying its own unit caveat.

### 3.5 `events` has still never scored — and today the gate fired for the first time in 69 scans

`events_24h` carried **three High-impact rows at 13:30Z** (Average Hourly
Earnings, Non-Farm Employment Change, Unemployment Rate), 42 minutes after the
scan. **There is no `events` row in `bias_components` at all.** The dead-weight
audit's strongest possible instance: on NFP morning, with three High releases
inside the hour, the component contributed **nothing**. **P-C already owns this
and is already PROPOSED; no new ID.**

**Separately, and genuinely new: `prediction.event_gate` is non-null for the
first time in the record.** Measured from source across **69** trading-day
scans, **1** carries a gate, and it is this one: *"STAND ASIDE … no entries until
30min after the print; then use the post-print 30-min range H/L as the day's
sweep levels."* P-C's standing sentence is *"the gate has never fired"* — **it
has now, once, and it fired on the correct day.** The instruction kept the reader
out of the 13:30 print and pointed at a 13:30–14:00 window that preceded the
14:40 call-wall touch and the ~15:00 high. **Whether the post-print 30-min range
H/L were good sweep levels is not in `review_day`'s output and was NOT
recomputed.** **P-C's firing limb goes to n=1; nothing proposed** — one firing
cannot grade a gate, and the dead-weight claim about the *score* component is
untouched by it.

### 3.6 H10 — the −3 branch's 11th firing, from the farthest distance in the record, and its verdict depends on a convention P-H has not yet settled

`structure −3`, *"price is **BELOW** the entire prior-week range
(28084.6–30023.6) — PWL 28084.6 is now resistance"*, with price **1079.6 below
the boundary = 1.40× ADR14**. Every prior proximity-gap instance was about the
rule firing *near* its own edge (11-03 at **1.6 points**); today is the opposite
extreme and the register has no instance like it. **No reclaim** — the session
high stopped **783 points** short of the PWL, so the missing reclaim term would
not have fired and the *prose* was right all day.

**The branch's record is now convention-dependent in the open:** post-scan
**4-for-11**, day-net **3-for-11**. H10 is one of the three entries P-H says it
unblocks, and today is the first session where H10's own tally moves differently
on the two bases. **Declined for the sixth time, same stated reason: no accuracy
test for a normalised distance term exists.**

### 3.7 Two defects I went looking for and did not find

Recorded because a review that only reports confirmations is worthless.

- **`rates +3` reads *"US10y 4.837 (−1.17%)"*, and 11-05 printed the identical
  −1.17%.** That looked like a stale series. **It is not:** from the journal's
  own inputs, US10y is **4.952 → 4.894 → 4.837** on 11-04 / 11-05 / 11-06, which
  is −1.171% then −1.165%. **A coincidence, verified from source.** No D22(b)
  instance.
- **H18/P1 — duplication 39 of 39 by construction, but the sign-opposition
  streak ENDS at 2.** The stale FRED rows (DFII10 to 11-04, DGS10 11-03→11-04)
  and the live `rates` row point the **same** way today (yields down). Collapsing
  the stale macro rows moves the score from −19 to −18 — immaterial either way,
  so the **RENDERING** proposal stands unchanged and **no weight change is
  made**.

### 3.8 D22 — candidate instance 3, the largest divergence in the record, and still UNCONFIRMED

`breadth −1`: *"NDX **−6.36%** vs ES **+0.22%** — tech lagging, rotation out of
tech"* — a **6.58pp** divergence against a previous maximum of 3.78pp (10-30).
**The NDX leg checks out**: it reproduces the graded 11-05 cash session
(−1803.8 on 28443.0) to within rounding. **The ES leg is the implausible one** —
the whole US tape fell on 11-05, and `macro_probe.yahoo_series("ES=F","5d","1d")`
takes `last = meta["regularMarketPrice"]`, which for a 24-hour future is the
**live** price at scan time, against `prev = closes[-2]`, a completed daily bar.
That is D22(a)'s claim exactly.

**I tried to source ES independently and could not: Yahoo returned HTTP 429, and
I did not attempt to work around it.** So the claim is **not made**: candidate
count **n=3**, nothing proposed, and the next reviewer with a working quote
endpoint can close this in one fetch.

### 3.9 Everything else, one line each

- **H26 — a ≥10 bucket instance, and `|post|/ADR` 0.036 is below *every* bucket
  mean in the from-source table** (0.207 / 0.452 / 0.524 / 0.429) by at least
  5.7×, produced by the **strongest** call in the window. The ≥10 direction cell
  would go **2/7 → 3/8 = 37.5%** — **on a grade H17's threshold, met today, says
  should not count.** Carried and from-source figures reported, **neither
  averaged**; *"inverted at the top"* **stays SUSPENDED**. On consecutive
  sessions the scale now reads **−4 → 2.258× ADR** and **−19 → 0.036× ADR**:
  yesterday broke the ordering at the bottom, today breaks it at the top.
- **H2 — instance 13 (`track.py`'s own list), and the fade WON.** `EXHAUSTED`,
  budget 0.0, below the flip, negative week GEX — and the only touched level held
  as resistance for 345 minutes while the extension came to 0.23× ADR. **This is
  a counter-instance to the census's direction of travel and to §4.3 below.**
  Census stays **suspended**.
- **H22 — n=19.** Week net GEX **−1.02bn** → *"expansion likely"* → **1.370×
  ADR**. Against 11-05 (−5.219 → 2.832×), 11-04 (−1.305 → 2.126×) and 11-03
  (−3.083 → 0.610×), the series is **still not monotone**; today is correctly
  ordered against 11-05 and inverted against 11-03. Label **RIGHT**, **not
  discriminating**.
- **H19 — coverage 3.5%** (139 headlines, 10/10 feeds, 57 relevant, **2**
  auto-scored) → `news −1` **on a day that closed +331.9 up**. The 55-item
  judgement list contained *"US Stock Rout **Pauses** as **Dip Buyers Offer
  Support**"*, *"AI Stocks … **Bounce** After Nasdaq Dives"* and *"Chip stocks
  are the **cheapest** they've been in nearly seven years"* — the day's actual
  story, unscored, while two bearish headlines carried the row. **H19's
  established finding (magnitude tracks match count, not importance) is
  unchanged**; the sampling-bias-bearish limb takes a supporting instance.
- **D21 — NOT a firing, and near-miss #2.** `gamma +0`, price **79.9%** up the
  band (26326.2–27176.2, 850 wide = 1.10× ADR) — **0.85 points** under the 80%
  gate, against 10-19's 2-point near-miss. **Both near-misses were followed by
  price running to the top of the band**, so the `−2` would have been WRONG both
  times had it fired. The gate is a percentage of an unnormalised band, which is
  D21's width defect in its near-miss form. **n=2, nothing proposed.**
- **D23 — observation 18, NO residual.** Offset **−23.8**, `nq_implied`,
  `repriced_bs_at_current_spot`, cash **933 min** stale. **CLEAN — the D6 breach
  series stays at SIX.**
- **D25 / D27 — §7 did not render: 9th consecutive non-render, frozen at 29.**
  12th consecutive `gexbot` **401** on `/v2/NDX/classic/gex_full`;
  **H12/H13 untestable, D25 SUPPRESSED.**
- **H15 / HY OAS — scored −2** on an 18bp five-day widening. More evidence
  against the retired *"HY OAS is dead weight"* claim.
- **The board's side composition — n=2.** 11-05 spent 8 of 15 rows on the side
  its own §2 forbade; today spent **4 of 5 rows (80%)** on the side opposite its
  own direction call, and the single row on the call's side was already consumed.
  **Per-side hit rates are not in `review_day`'s output and were not recomputed
  for prior sessions.** n=2, nothing opened, explicitly **not** merged into P-B
  or P-G.
- **No instance:** H3 (CLOSED-NEGATIVE, superseded by H26; and price was **86%
  up** the pre-scan range, not at a low) · H4 · H5 (`late` n still **0**) · H7
  (no overnight scan) · H9 · H11 · H12/H13 (401) · H16 · H20/H21
  (CLOSED-NEGATIVE) · D8 · D14 · D15 · D24 (`event_gate` correctly populated,
  §5 printed all five rows) · D28 (three `events_24h` rows, all printed;
  condition stays n=2) · D30 · P-E(b) (no shelf row was reached) · P5 (§7 did
  not render) · P-F (price **inside** the prior-day range 26452.3–28542.5) ·
  P-I (`PIN_THEN_EXPAND` did not fire; `COHERENT_SHORT`) · P3/H6 · P-G (above).

---

## 4. Change proposals

**Two, both landing on existing entries, and they are the same grade seen from
two angles. No ID is allocated.** One live proposal is **corrected** and one
is **blocked**.

### 4.1 H17 — THRESHOLD MET at the pre-registered 3 days: the direction grade needs a magnitude deadband, and the direction statistic must be restated

**What to change.** In `review_day.py:204`, the three-way
`CORRECT / WRONG / no call (neutral)` becomes four-way: when
`|post_scan_move|` is below a deadband, emit **`no call (inside noise)`** rather
than a verdict. Re-grade the three instances, and restate every direction
statistic that quotes them. **Proposed, not applied — this is grading logic and
the threshold is the user's to set.** The register's own three instances all sit
under 2.7% of session range; the next clean gap in the data is 7.2%
(09-11 13:24), so **5% of the session range** is the value H17 pre-registered
and the value the evidence supports. An `|post|/ADR` form is the alternative and
is **not** proposed, because H17's own series is keyed to session range.

**Evidence — 3 distinct sessions, which is exactly the pre-registered
threshold, and they are the same shape every time:**

| day | call | post-scan move | % of session range | day net | graded |
|---|---|---|---|---|---|
| 09-11 | BEARISH | **−1.1** | **0.2%** | **+252.1** | CORRECT |
| 10-19 | −5 | **−9.3** | **1.35%** | **+430.6** | CORRECT |
| **11-06** | **−19** | **−28.0** | **2.66%** | **+331.9** | **CORRECT** |

**The shape is the finding, not the count.** All three are **bearish calls
graded CORRECT off a near-zero post-scan drift on days that closed sharply UP**,
and in all three the scan landed near the pre-scan high. This is not a cosmetic
grading nicety: **the grade is systematically crediting bearish calls on up
days**, and it has done so on the strongest bearish call in the window.

**Expected effect, quantified on the current window.** `track.py` reports
**13 right / 11 wrong / 5 no-call** = **13/24 = 54.2%**. 09-11 has aged out of
the bar window; 10-19 and 11-06 are both in it. Re-grading those two to
`no call (inside noise)` gives **11/22 = 50.0%** — the headline direction
statistic falls **4.2pp** and the model's measured edge over a coin flip
disappears entirely. **No score, level, budget or board change.**

**Grepped first:** `H17` (owns it), `P-H` (owns the *basis*, not the
*magnitude*), `H26` (owns magnitude as a *forecast*, not as a *grading gate*),
`H3` and `D21` (convention-dependent verdicts, which this improves rather than
decides). `^## H28`, `^## D32`, `^## P-J` all return **0** and stay free: **no
new ID.**

### 4.2 P-H — deciding instance 6, the first since 10-19, and it REFINES the recommended basis rather than merely adding a count

Post-scan **−28.0 CORRECT**; day-net **+331.9 WRONG**. The verdict flips on the
convention, so this is a **deciding** instance — the register has recorded *"no
6th deciding instance"* on **15 consecutive sessions**, and the census moves
**5 → 6**.

**The refinement, which is new and is the reason this is not just a tick.** P-H's
recommended basis is **post-scan**, and the reasoning is sound (the brief can
only be traded forward). But **2 of the 6 deciding instances — 10-19 and 11-06 —
are also H17 sub-5% noise cases, and in both the post-scan basis is what
manufactures the CORRECT.** On its own, P-H's recommended basis would convert two
near-zero drifts into two wins and discard two large, correctly-signed day-net
losses.

**So the two proposals must ship together or not at all:** emit
`post_scan_move`, `day_net_move` and `direction_call_basis`
**with the deadband applied to the chosen basis**. On 11-06 the composite grade
is **`no call (inside noise)`** and the day-net **WRONG** is suppressed with it
— which is the only grade that does not overstate what the brief achieved.
**No new ID; P-H is already PROPOSED and its text gains a dependency on H17.**

### 4.3 CORRECTION — yesterday's gamma-gating fix would have deleted the one instruction that was RIGHT today

The 11-05 review proposed gating §3's fade instruction on the **gamma regime**:
*"when price is below the gamma flip and weekly net GEX is negative, §3's closing
sentence must not read 'favour fades over chasing breaks'."* Its census was
**7 sessions, 6–1 to gamma**.

**Today satisfies that gate exactly — below the flip at −1042, week net GEX
−1.02bn, `EXHAUSTED`, budget 0.0 — and the fade was the correct trade.** The
only level the day reached was faded successfully: it held as resistance for 345
minutes and price closed 217.4 below it, while the range extended just
**174.0 = 0.23× ADR** against the gamma block's *"today's ADR can be exceeded —
don't cap the target too early"*. **Census: 6–2 to gamma.** Had the proposed fix
been shipped, it would have removed the right instruction from this document.

**What today says the resolution actually is, and it is already on the page.**
§1's strategy line is the one sentence that survives the session intact:

> *"Strategy-1 fades have a materially lower hit rate here — **only take them at
> the far walls**."*

The fade that won was **at the far wall**. §2's blanket *"fading is the wrong
trade today"* was wrong, §3's blanket *"fading the extremes is the
higher-probability side"* was right for the wrong reason, and §1's conditional
was right for the right reason. **The coherence fix should therefore propagate
§1's existing condition into §2 and §3, not pick a winner between them.** This
is a **correction to a live proposal, stated in its own words where possible**;
it allocates no ID and changes no score, and the 11-05 census is restated as
6–2 rather than re-derived.

### 4.4 BLOCKED — do not read 11-06 as evidence that the `budget == 0.0` trigger works

The 11-04 review proposed `remaining_budget == 0.0` as a disjunct to P-F's
trigger, on evidence of **4 of 4 positive errors, mean +253.0**. Today is a fifth
`budget == 0.0` session and its error is **+174.0**, positive again — so the
series reads **5 of 5, mean +237.2**. **That is not a licence to ship it**, for
the reason the 11-05 review already found: the largest instance of the harm the
proposal exists to prevent (+1261.2) occurred at a budget of **187.2**, where
the trigger does not fire. **Necessary, not sufficient, unchanged.** Recorded so
that a fifth consecutive positive does not get read as the missing evidence.

### Still observing — nothing proposed

- **The session-context field — EST-era harm n=2** (all-time 4). Watching for a
  third EST-era instance; the merge with the H1 session-context sub-observation
  is pre-registered in §3.3.
- **The rear-view block's lag — n=2, opposite signs** (11-05 +8 on a correct −12,
  11-06 −8 on a falsified −19). Watching whether the sign stays two-sided; if it
  does, this is a rendering/age question and never a weight question.
- **`vol` as one variable counted four times — condition n=2, harm shrinking.**
- **D22's ES leg — candidate n=3, unconfirmed.** One working quote fetch closes it.
- **D21's near-miss series — n=2**, both followed by price running to the top of
  the band.
- **P-E's empty middle — first convention-dependent instance.** Watching whether
  the 12–103 gap is real or an artefact of the settled-vs-first-touch choice.
- **P-C's firing limb — n=1.** The gate fired once in 69 scans and the day it
  chose was right.
- **The vol-collapse-as-setup claim — still n=1** (no instance today; vol rose).
- **H22's threshold effect at |week GEX| > 4bn — still n=1.**
- **M6's `_first_touch` 12-bar window** — the only limb of M6 still open.

### No new data point is warranted

Everything that decided 11-06 was on the page, and for once the page's own
hedges were the accurate parts: §1's *"only at the far walls"*, the event gate's
*"stand aside"*, and the straddle band's close-to-close caveat were all right,
while the three unhedged assertions — *"use the smaller budget"*, *"nothing
structural to slow a breakdown"*, *"expect a stall at 27026.2"* — were all
wrong. **No external source is proposed.** The one genuinely absent input
remains an **event-age** field for `news_scorer.py` — free, local, owned code —
and today adds to **neither** limb: the two scored headlines were same-day and
correctly dated. **n=2 on each limb, NOT proposed.**

## Journal hygiene

One scan file for 11-06 (`1247-london.json` + `.md`), `is_trading_day: true`,
**276 bars**, `review_day` reports **0 test artefacts**; `track.py` reports 6
artefact-marked entries elsewhere in the archive, excluded as always. **No
`prediction` block was modified. No scoring, wall or grading code was edited** —
`brief.py:588`, `:1047`, `:996`, `macro_probe.py:45–72` and `track.py` were read
to establish mechanisms and left unchanged. **No fabricated or backfilled entry
was found; none was created.** **09-24 needed no hand-quarantine for the first
time in 30 reviews — it has aged out of the bar window entirely** (recorded
under D26, not silently absorbed). **2026-10-13 still has no journal directory —
documented, not recreated.** **2026-09-09, 09-24 and 09-25 still have no
`REVIEW.md`; none was created and nothing was back-dated.** **2026-11-09 is on
disk, held back by `track.py` as unfinished (168 bars), and is NOT graded here.**
