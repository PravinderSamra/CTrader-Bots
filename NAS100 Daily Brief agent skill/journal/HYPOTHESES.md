# Open hypotheses — evidence register

**Rule: nothing here changes the model until it has ≥3 trading days of evidence
pointing the same way.** One session is noise, and tuning on noise is how a
model gets worse. This file is the memory that makes that discipline survive
between sessions.

Run `python3 track.py` (in the skill's `scripts/`) to regenerate the evidence
table. Append observations below; do not rewrite history.

## ID allocation — CHECK THIS BEFORE OPENING ANY NEW ENTRY

Three collisions happened in one week because each reviewer picked "the next
free number" from the entries it could see, while other entries were being
added between runs. H12/H13 were each opened twice for unrelated claims
(corrected 09-15); P-A was opened for what was already D16 (cross-referenced
09-17); D19 was opened for a `freshness` defect hours after D19 had been taken
by the VIX9D null-guard (renumbered to D20/D21 here, 09-21).

**Highest allocated as of 2026-10-26: H27 · D27 · P5 and P-H · M7.**
(H24/H25 opened in the 2026-10-02 research block; D24 opened 2026-10-05 for the
forward-only events renderer; **D25** opened 2026-10-07 for the unguarded
`drift` sentence in section 7 of `brief.py` — D14's 09-16 fix guarded
`gexbot.levels()` and never covered this render. **D26** opened 2026-10-08
(grading 10-07) for `track.py` filing a day that has aged out of the 45-day bar
window as *"not finished"* — D16's failure mode at the new boundary, and the one
D16's own fix note pre-registered. **P-H** opened 2026-10-08 (grading 10-07) for
the direction-grading convention, after the post-scan vs day-net split reached
n=3 and decided the verdict on a −10 for the first time.
**The 2026-10-09 review (grading 10-08) allocated nothing**: its one substantive
proposal is the measured answer to **H1** and belongs to the existing **P4**
(*"stop quoting a point-precise budget above zero"*), which was grepped for
first — so nothing was opened under a new number for a claim the register
already holds.
**The 2026-10-12 review (grading 10-09) allocated nothing either**: its one
substantive proposal — rank `path_read()`'s named brake by gamma force rather
than by distance — is the mechanism behind **H23** (*"does the fuel section's
named brake ever brake?"*), which was grepped for first, and it is also the
third `brief.py` prose defect in the **D24/D25** family rather than a new one, so
no number was taken for a claim the register already holds.
**The 2026-10-14 review (grading 10-12) allocated nothing either**: its one
proposal — attach the measured run-through distance and reclaim base rate to the
put-wall break rider — is the **empirical half of H14**, which that entry's own
fix note left open pending two more sessions, and which was grepped for first.
The two threshold-reached items it reports (*"gamma right, outvoted into a
no-call"*, n=3; the `gamma +2` bottom-of-band branch, 4 firings) are **null or
mechanism-only and nothing is proposed on either**, so neither took a number.
**The 2026-10-15 review (grading 10-14) allocated ONE number: H26**, for the
claim that the bias score's *magnitude* is a range forecast rather than a
direction forecast (|score| against realised move, n=22 days). It was grepped
for first — D16 concerns a rider that *enlarges* conviction, **H3** asks whether
to *cap* it, **H17** is a deadband on the direction grade, and none of them
measures what the magnitude buys; `grep -n "^## "` confirmed H26 unused before
it was written. Its two companion items took no number: the corridor-terminus
proposal is **H23**'s own corridor branch (grepped first), and the board-offset
work ends in a **falsified** hypothesis with nothing proposed.
**The 2026-10-16 review (grading 10-15) allocated NOTHING.** Every item it
reports is an existing entry gaining a data point, or an existing entry reaching
a threshold and resolving to *no model change*: **H8** reached its pre-registered
10 observations and is **ANSWERED-POSITIVE** (8 closes inside the straddle band
of 10); **P-H** took its 4th deciding instance; **H26**'s 6–9 bucket took its
first miss; **H23**'s brake and corridor branches both took instances and are
already PROPOSED; the board-offset work again ends with **nothing proposed**.
Two claims it had to correct were found by grepping the file rather than by
opening a number for them — the HY OAS "dead weight" claim (the row has scored
on 25 of 31 scans) and the *"08-25 13:04"* citation (see below).
**Pointer, because the file is append-only below this block and a grep for
`## H3` is misleading: H3 is CLOSED-NEGATIVE, superseded by H26**, recommended in
the 2026-10-15 appended block; H3's own heading still reads *"Status: OBSERVING"*
and cannot be edited. **Do not re-open a number for "cap the conviction at range
extremes" — that is H3, and it is closed.** Related: the *"08-25 13:04"*
citation is **wrong only where it is cited as a max-conviction bearish call**
(the H3 bearish list, so that branch is **0 for 3, not 0 for 4**); the same
citation is **legitimate** as a fuel/EXHAUSTED instance and in W1.
**The 2026-10-19 review (grading 10-16) allocated NOTHING.** Its one material
item is a **correction to a live proposal, not a new claim**: the 10-15
corridor-terminus proposal should not be actioned as written, because
`brief.py:520` sets `corridor_end = span[-1]`, the far end of the shelf list
within 1.2x ADR, so the terminus is not a barrier — grepped to **H23**, whose
corridor branch owns it. Everything else is an existing entry taking a data
point (**H26** n=24 and the rank correlation FALLS; **P-H** 11/17 vs 13/17 with
**no 5th deciding instance**; **H23** instance 13; **P4/H1** n=28; **M6** session
26; **P-B(b)** 15th; **P-G** #22/#23; **D23** 13th residual; **D25** 26th;
**H18/P1** instance 20, duplication 25/25; **H19**, **H22** n=10, **H10**
7th firing). Two items took no number by existing precedent: the
**`PIN_THEN_EXPAND` pre-registration** follows the 10-05 `SPIKE_THEN_REVERT`
pre-registration, which is recorded under a prose heading with no ID; and the
**two-opposite-instructions re-specification** belongs to the suspended census,
which is a measurement defect in the register rather than a model item.
**The 2026-10-20 review (grading 10-19) allocated NOTHING.** It carries three
material proposals and **every one of them lands on an entry that already
exists**, each grepped for before it was written:
(1) the fade-vs-continue census, **re-derived from scratch at n=7 under the
10-16 specification and now lifted on axis 1**, is the empirical content of
**H2** (*"At LOW_FUEL / EXHAUSTED, does fading the extremes beat
continuation?"*) — H2's own threshold was 3+ instances and it is met at 7, with
the claim **FALSIFIED** (5 of 7 fades lost outright, 7 of 7 if ties are scored
against the fade); **axis 3 remains SUSPENDED and its specification is itself
the defect** (the specified metric fires on 9 of 9 conflict days *and* 15 of 16
control days, so it is a near-constant — delete the column, do not re-score it);
(2) **closing H23's force-ranking branch** acts on that entry's **own
pre-registration** at the third consecutive distance-first/force-first
agreement, so it takes no number;
(3) *"stop quoting the signed Spearman until its derivation is written down"* is
a **correction to H26's own published figures**, not a new claim — the |post|/ADR
and range/ADR statistics reproduce the register exactly at n=24 (+0.577 /
+0.198) while the signed one reproduces under **no** available convention
(+0.220 counting no-calls as 0, +0.102 excluding them, vs the published +0.157).
Everything else is an existing entry taking a data point (**H26** n=25 and the
correlation falls for a second consecutive session; **P-H** 12/18 vs 13/18 with
the **5th** deciding instance, which **halves** the convention's cost from 11.8
to 5.5 points; **H17** 2 of 3; **H23** instances 14 and 15; **P4/H1** n=29;
**M6** session 27; **P-B(b)** 16th; **D23** 14th residual; **D25** 27th;
**H18/P1** instance 21, duplication 26/26; **P-E** instance 14; **P5**;
**H19**; **H22** n=11; **D22**; **H8** post-closure; the **session-context
field** 16th). Two items took no number by existing precedent: the
**`PIN_THEN_EXPAND`** result is **observation 1 of 3** under the 10-19
pre-registration, whose own clause 5 forbids concluding anything, and the
**board-offset** work again ends with **nothing proposed** (the
offset-vs-options-proximity tabulation it was asked to run is **NULL** at n=5).
The one input that would have changed 10-19 — a live rather than Friday-close
vol read, the four stale vol rows casting −6 of a −5 score — is **1 day of
evidence**, is **not proposed**, and maps to **D22** rather than to a new
number.
**The 2026-10-21 review (grading 2026-10-20) allocated NOTHING.** Its one new
*measurement* — collapsing the DFII10/DGS10 pair to one row and duplicate
headlines to one event across all 26 graded days — is the empirical content of
**H18 / P1** and **H19**, both grepped for first, and it ends by **supporting
H18/P1's existing RENDERING proposal and refuting a weight change** (minimal
dedup: 13/18 against the published 13/19, one day's difference; dropping the
pair outright: **13/20, worse**). Three further items that look new are existing
cells gaining their second or fourth instance and are recorded there:
*"gamma outvoted"* (**4th instance, and the first that produced a call rather
than a no-call — the outvote was right**); *"the direction call and the strategy
block pointed opposite ways"* (**n=2**, which is the 10-14 entry's own request to
extend rather than re-derive, now with one instance on each side of the flip);
and the **MODERATE ∩ below-flip fade**, which is **deliberately NOT entered into
H2's census** — H2's cell is `LOW_FUEL`/`EXHAUSTED` ∩ below the flip and its
sample is pre-registered — but which is logged as a **caution against
generalising H2's live proposal beyond that cell**. Everything else is an
existing entry taking a data point (**H26** n=26, the correlation falling for a
**third** consecutive session while the bucket means stay monotonic; **P-H**
13/19 vs 14/19 with **no 6th deciding instance** and the convention's cost
5.5 → 5.3; **H22** direction re-run at n=26 and **unchanged at 58%**, range
label wrong at n=12; **P4/H1** n=30; **M6** session 28, a **counter-instance to
session 27's travel-scaling claim**; **P-E** instance 15 and the **second**
"middle" observation; **P-E(b)** 15th; **P5** 3 of 5; **D23** 15th residual;
**D25** 28th; **D18** 8th day / 14th headline, a **category** error rather than
a negation one; **D22**; **P-G** #24/#25; **P-B(b)** 17th; the
**session-context field** 17th; the **realised-basis log** observation 5; the
**dead-weight audit** at n=34). Two items took no number by existing precedent:
the **board-offset** work again ends with **nothing proposed** (the proximity
hypothesis stays **NULL** and is not revived), and *"the whole move was over by
10:30 ET"* is a **watch item with no ID at n=2**, kept out of the
`PIN_THEN_EXPAND` sample on purpose.
**The 2026-10-22 review (grading 2026-10-21) allocated NOTHING.** `grep -n "^## "`
was run first and confirms **H27 · D27 · P-I** are all still unused. Four items
looked like candidates for a number and every one of them was grepped to an
entry that already exists:
(1) the **`PIN_THEN_EXPAND`** result is **observation 2 of 3** under the 10-19
pre-registration, whose clause 5 forbids a verdict — falsified on the same
clause as observation 1, and by precedent (the 10-05 `SPIKE_THEN_REVERT`
pre-registration) it carries **no ID**;
(2) the **UK CPI headline scoring the Nasdaq** is **D9** (*"the news tagger
reads a keyword without its subject"*), grepped for before it was written —
**instance 2, and the first that actually scored**, D9's own entry having asked
for exactly that count;
(3) the **gexbot HTTP 401** is a **data-source failure with no register entry of
its own**, and deliberately takes no number at n=1: **H12/H13** are claims about
gexbot's data rather than failure modes, and **D17** is a CBOE **429**, a
different and transient condition. It is recorded in the 10-21 review's
carry-forward block, with the side effects that the lost archive files are
**both** ladders (one `gex_full` call feeds both, `gexbot.py:219`) and that
**D25's false sentence was suppressed by the outage rather than fixed**;
(4) the **third instance of a board level printing inside its own offset** (the
29665.4 structural call wall at **+1.2** on a **−34.6** offset) belongs to the
existing 10-12/10-16 series and to **P3 / H6**, whose structural census again
**cannot take the day**.
Everything else is an existing entry taking a data point (**H18/P1** instance
23, duplication **28/28**, and the first graded day where the **headline** half
of the dedup measurement applies — **−7 → −5, label changes, side and verdict do
not**; **P-H** 13/20 vs 14/20 with **no 6th deciding instance** and the
convention's cost 5.3 → 5.0; **H26** n=27 and the 6–9 bucket's **second** miss;
**H23** instances 16 and 17, the **first session with both named brakes
reachable**, and they **split** — census 11 sliced / 3 capped / 3 never-reached;
**M6** session 29, a **new record 13.75x ratio** and the travel-scaling claim
failing a **second** consecutive session; **P4/H1** n=31; **P5** 0 of 1
gradeable and **P-E(b)** instance #16; **D23** 16th residual and a **sixth**
consecutive sign disagreement; the **realised-basis log** observation 6, in
which 10-20's impossibility **recurs mirrored** and points at the cash anchor
rather than the roll; **D26** reporting gap with a **changed symptom** —
aged-out days are now silently invisible rather than filed *"not finished"*;
**D25** 29th; **H22** range label **right** at n=13 with the direction half not
re-run; **P-G** #26/#27; **P-B(b)** 18th; **H8** post-closure; the
**session-context field** 18th). Two further claims were checked and **killed on
the spot rather than proposed** — *"big budgets systematically over-read"*
(no separation across the eight budget≥200 scans) and *"use the VXN-implied
range as the budget"* (over on some sessions, under by 400–500 on others). The
*"whole move was over by 10:30 ET"* watch item takes a **counter-instance** and
does not extend.
**The 2026-10-23 review (grading 2026-10-22) allocated ONE number: D27**, for
the **gexbot HTTP 401 on `/v2/NDX/classic/gex_full`**. `grep -n "^## "` was run
first and confirmed **H27 · D27 · P-I** all unused. The 10-22 review withheld a
number *"deliberately at n=1"* on the grounds the 401 might be transient; it
recurred on the **2026-10-23** scan, so at **n=2 consecutive** it is an
auth/endpoint failure mode. **D17** (CBOE **429**) is the precedent for a
data-source failure taking a number and **H12/H13** are claims about gexbot's
*data* rather than its failure modes, so neither covers it. **D27 records the
mode and its two measured side effects — one 401 costs BOTH ladder files
(`gexbot.py:219`) while the printed message names only the volume-weighted view,
and D25's false sentence is SUPPRESSED rather than fixed, so its counter resumes
when the feed returns — and proposes NOTHING**: no credential change, no code
change, no retry policy.
Four further items looked like candidates for a number and every one was grepped
to an entry that already exists:
(1) the **footnote truncating by PRICE rather than by distance**
(`far_line`, `brief.py:146–159`, fed by the descending sort at `brief.py:373`) is
a **second limb of D7's unfinished second half**, grepped for by file and line
before it was written — PDL 29550.0 at **+189**, named by the brief's own
`structure −1` row, appeared **neither on the board nor in the footnote** while
rows **+321 to +1718** away were kept;
(2) the **two opposite instructions landing four lines apart inside §3** (path
read *"Do not fade it"* against stop management *"Fading the extremes… is the
higher-probability side"*) is **H2's own census**, which owns the
two-opposite-instructions measurement — a tighter radius, not a new claim;
(3) the **`gamma +2` band rider at 245.3 from its own put wall on a 1300pt
band** is **D21's width defect** at its extreme (a **260pt = 0.50x ADR** trigger
window against **20pt = 0.04x ADR** on 09-18), and it is **NOT proposed** for
D21's own standing reason: the only evidence a normalised version performs
better is the absolute-distance re-cut, which was found **after** looking at
outcomes;
(4) **"grade the secondary table's two claims separately"** is a refinement of
**P5**, which already owns the table.
Everything else is an existing entry taking a data point (**H2** instance 8, the
falsification extending to **6–2 / 8–0**, the first in-cell day since the census
was re-derived; the **gamma-outvoted** cell's **5th** instance and **2nd**
directional one, the outvote **WRONG** this time and the pre-registered quantity
still not ordering the outcome; **P-F** advanced on a **4th same-signed**
treatment instance that **kills the one-tail-point caveat**; **M6** session 30
and a **third** consecutive counter-instance to travel-scaling; **H26** n=28, a
3–5 bucket instance, bucket means monotonic a 6th time and **no Spearman
quoted**; **P-H** 13/21 vs 14/21 with **no 6th deciding instance**, cost
5.0 → 4.8; **H18/P1** instance 24, duplication **29/29**, HY OAS undated 17th
session; **D18/H19** instances 15 and 16 with the **polarity reversed**, which
**prices the partial fix as harmful**; **H10** proximity gap instance 2; **D23**
with **no residual available** — section 7 did not render, and the series is
**not** extended with an inferred figure; the **realised-basis log** observation
7, which **cannot discriminate** the 10-20 suspicion because the roll is a
down-roll; **P3/H6** 2nd structural-put-wall touch and the **first safely
gradeable** one; **P5** 3/3 with **one row VOID** inside its own offset;
**P-B(b)** 19th and **inflation 1.00x for the wrong reason**; **H8**
post-closure; **H14** 2nd consecutive confirmation; **H22** range label right at
n=14; **H23** no instance, trap re-flagged with today as its **control**;
**D25** interrupted at 29; the **session-context field** 19th; the
**D7-shaped contract-count** item n=3). **P-E/P-E(b), P-G, H3, H4, H7, H17, H20,
D9, D24 and `PIN_THEN_EXPAND` all take no instance**; `PIN_THEN_EXPAND` stays at
**observation 2 of 3** and is **not graded or revised** here. **P4/H1's day count
did NOT advance** — see D26: 09-08 left `track.py`'s sample as 10-22 entered it,
so **+45.4 (n=31)** and **+58.6 (n=31)** are **not two points in one series**.
Next free: H27 · D28 · P-I.)
**The 2026-10-26 review (grading 2026-10-23) allocated ONE number: H27**, for
the claim that the bias score's **blocks are not independent** — across all 33
PRE_NY `is_trading_day` scans, `vol ↔ breadth` correlate at **+0.533** and
`structure ↔ gamma` at **+0.555** while every other pair sits at |r| ≤ 0.22, so
a *"broad-based"* score can be two correlated pairs. On **10-23** those two
pairs carried **−13 of a −16** and the independent remainder (**−3**) was inside
the engine's own deadband. `grep -n "^## "` was run first and confirmed **H27 ·
D28 · P-I** all unused; the claim was then grepped for by wording — *collinear*,
*common cause*, *correlated component*, *double-count* — and by family.
**H18/P1** is the DFII10/DGS10 pair and its rendering fix, **H19** is duplicate
headlines, and the 10-21 whole-record duplication-collapse measurement covers
only those two; none of them reaches across blocks. **H3** is CLOSED-NEGATIVE
and is not this. **H26** is the magnitude-versus-direction claim, and H27 is the
**mechanism** behind it, which is why it is separable rather than a second name
for the same thing. **H27's weight-change limb is ANSWERED-NEGATIVE on arrival
and PROPOSES NOTHING**: the collapse was pre-registered in writing and then run,
and it takes the record from **13/22 = 59.1%** to **10/19 = 52.6%** (3 hurts
against 2 helps). The entry exists so the fix is not re-proposed by the next
reviewer who notices the correlation. Its one open limb — that the §1
*"Driven by:"* line renders correlated rows as independent contributors — is a
**rendering** claim in the H18/P1 family, sits at **n=1**, and is not proposed.
Everything else is an existing entry taking a data point (**H26** n=29, the
bucket table **re-derived from source** for the first time since n=25 — magnitude
monotonicity **survives** a 7th session at 0.181/0.339/0.532/0.704, the **≥10
bucket's direction falls to 3/7 = 42.9%, below a coin flip and below every other
bucket**, and **two published 6–9 figures are shown to have drifted**, with the
**range/ADR bucket form NOT monotonic from source**; **P-H** 13/22 vs 14/22 with
**no 6th deciding instance**, cost 4.8 → 4.5; **M6** session 31, **4 of 7
verdicts inverted** and the **driver shown NOT to be window placement** — the
12-bar window captured the true excursion on 7 of 7 rows — which **corrects
session 30**; **D7** a **clean CONTROL on both limbs**, `far` holding 5 rows
against a cap of 6 so nothing was truncated; **D26** the held-back set rotating
**again** with the sample **shrinking 31 → 29 days** and the P4/H1 figure
conflict now at **four numbers under one series name**; **P4/H1** n=29 and the
**largest over-estimate in the record on the largest budget in the record**;
**H10**'s −3 branch 2-for-8 with the **prose right and the score wrong**, and a
**third** proximity-gap instance; the **`gamma +2`** band rider's **6th** firing,
**RIGHT**, census 3–3, prose contradiction **6 of 6**, and **still zero sign
changes in six firings**; **H2** a **control** that localises the
two-opposite-instructions contradiction to the LOW_FUEL/EXHAUSTED branch; the
**realised-basis log** observation 8, which **DOES discriminate** the 10-20
suspicion because 10-23 supplies the **up-roll** 10-22 could not and its gap is
ordinary; **H18/P1** instance 25, duplication **30/30**, HY OAS undated **18th**
session and scoring **0** after six sessions of widening, with the age gate a
**clean null**; **H23** no brake instance but the **clear-path read graded and
SPLIT**, n=2; **P5** 1/1 and 1/2 with **no void row**; **P-B(b)** 20th and a
guaranteed window that **FIRED**, inflation **1.40x**; **P3/H6** with the
structural call wall at **0 gradeable touches ever** and `TOUCH_TOL = 8.0`
filing the day's best level as *"never reached"*; **P-E(b)** #17 and its **first
split**; **P-G** #28–#30; **D18/H19** instance 17 and **coverage 0.75%, the
lowest in the record**; **P-C** 2nd Medium-cluster instance; **H22** range label
**wrong** at n=15; **H8** post-closure with a **4th** counter-instance to the
VXN-implied budget; **D23** with **no residual** for a second session; **D27**
3rd consecutive 401; **D25** interrupted at 29; the **session-context field**
20th; the **dead-weight audit** refreshed **from source at n=33** and **failing
to reconcile** with the register's hand-maintained n=34). Four items took no
number by existing precedent: **P-F** is **not a treatment instance** (price
inside the PD range) and is logged as a single inside-control observation; the
**four-Medium-event gate pass-through** is **P-C**, grepped by file and line
(`bias_engine.py:255`); the **`settled_read` origin defect** behind M6's
inversions is already recorded at lines ~5535 / ~6061 / ~7054 and is **not**
reopened; and **`PIN_THEN_EXPAND` stays at observation 2 of 3** for 10-23 and is
**not graded or revised** — **its 3rd and final observation fired on the 10-26
scan, so the pre-registered verdict is DUE at the next review.**
Next free: H28 · D28 · P-I.)

Opening an entry: take the next number above those, then
`grep -n "^## " HYPOTHESES.md` to confirm it is unused before you write it.
Proposals continue the **lettered** series (next: P-H) — see the proposal index
lower in this file for why two series coexist.

Before opening a defect, also grep for the **file and line** it concerns, not
just the wording you would use: D16 and P-A were the same four lines of
`bias_engine.py` found twice under different names, three days apart.

This block is the only part of the file that is meant to be edited in place.
Everything below is append-only.


**Status:** 3 trading days on record (24, 25, 26 Aug). Only **H1** has actually
reached its own threshold, and its evidence is a trend rather than a level, so
nothing is proposed. H9 and H10 opened 27 Aug.

---

## H1 — The budget forecasts range EXTENSION, and does it accurately?

**Claim.** `remaining_budget` predicts how much further the day's high-low range
will grow. It does *not* predict how far price will travel.

**Why it matters.** It changes what the number is *for*. Read as "movement
left", `EXHAUSTED` says stand down. Read correctly it says the extremes are
probably in — expect movement *between* them.

**Evidence so far (1 day).**

| Scan | Budget | Extension | Traversal | Error |
|---|---|---|---|---|
| 24 Aug 13:45 NY_OPEN | 0.0 | **5.3** | 284.4 | **+5.3** |
| 24 Aug 12:40 PRE_NY | 88.7 | 168.5 | 290.9 | +79.8 |
| 24 Aug 09:37 LONDON | 88.7 | 168.5 | 334.7 | +79.8 |
| 24 Aug 08:28 LONDON | 88.7 | 168.5 | 334.7 | +79.8 |
| **25 Aug 13:04 PRE_NY** | 12.0 | **0.4** | 256.5 | **−11.6** |
| 26 Aug 13:12 PRE_NY | 186.2 | 113.2 | 268.2 | −73.0 |
| **27 Aug 13:23 PRE_NY** | **132.6** | **46.2** | 281.3 | **−86.4** |

**Per DAY** (the weighting to read for a claim about the model — see M1):
**+61.2 → −11.6 → −73.0 → −86.4**, mean **−27.5**.

**THRESHOLD MET at 4 days, and still no change proposed.** Three consecutive
over-reads, each larger than the last, after one large under-read. Four points
running monotonically in one direction describe a *trend*, not a level: a
multiplier fitted to them would fit the slope and be wrong at both ends.

What it does justify is a specific question rather than a tuning: **all three
over-read days were long-gamma or pinning sessions; the single under-read day
was not.** Record the gamma regime alongside the error from here, and get an
unpinned day before touching the model.

Mean error **+46.6pts** (range grew more than budgeted).

**Read.** At the exhausted point the forecast was near-exact — twice now. On 25
Aug the budget said 12pts of extension remained; price ran to a marginal new
high **0.4pts** above the London high, reversed, and closed 130pts lower. The
range did not extend. Meanwhile price travelled **256.5pts inside** it. Early
LONDON scans still run ~1.9× light. Traversal exceeded the budget every time —
which is the point: they measure different things.

*Fuel excluded:* the scan of **24 Aug 21:56Z** (trading day 25 Aug), budget 0.0
vs extension 371.0. Its fuel was
measured across the 21:00 UTC rollover and described the *previous* day's
finished range — a corrupt input, not a failed forecast. Counting it would have
dragged the mean from 46.6 to 100.7 and invented a systematic bias out of a bug.
See D1 below. Its *direction* call is still counted — see D3 on why only the
fuel fields are quarantined.

**Naming convention (adopted 26 Aug).** A scan is named by its **scan timestamp
in UTC**, with the trading day in brackets where it differs. This register
previously called one scan "25 Aug 21:56" in one place and "24 Aug 21:56" in
another — one scan, two names, in the file whose entire job is to prevent
double-counting.

**Threshold.** 3+ days. If the exhausted-point accuracy holds and early-session
error persists, the fix is a time-of-day correction, not a blanket multiplier.

**Status: OBSERVING — 2 of 3 days.** The exhausted-point claim is now 2-for-2
and looking strong; one more clean session decides it.

---

## H2 — At LOW_FUEL / EXHAUSTED, does fading the extremes beat continuation?

**Claim.** If the range will not extend, price must turn at the extremes, so the
higher-probability trade is a fade back into the range — even when the gamma
regime favours continuation.

**Why it matters.** This directly contradicts the gamma-regime strategy call in
those conditions, and the brief now says so in words. If it is wrong, the brief
is actively misleading on exhausted days.

**Evidence so far (1 day).** 24 Aug 13:45: `EXHAUSTED`, 0pt budget, price at the
day's low, bias **−12 STRONGLY BEARISH** (continuation). Price fell 30.6pts
further, bottomed, then rallied 253.8 and closed +147 above the scan. **The fade
was the trade.** One observation.

**25 Aug 13:04:** `EXHAUSTED`, 12pt budget, bias **0 / NEUTRAL** (no call). Price
made a 0.4pt new high, then sold off 256pts to 29,086 and closed mid-range at
29,212.9. Fading the extreme was again the trade; the engine issued no
directional call, so this is evidence for the *fuel* claim but not against the
bias engine. Two observations.

**Threshold.** 3+ instances of `LOW_FUEL`/`EXHAUSTED`-at-extreme. Record each
time: did price extend, or reverse?

**Status: OBSERVING.** The wording change was made because it is a *definitional*
consequence of H1, not a calibration — but the empirical claim still needs proving.

---

## H3 — Does the bias engine over-commit at range extremes?

**Claim.** With fuel exhausted and price at the day's extreme, a continuation
score should be capped rather than allowed to reach ±12.

**Evidence so far (1 day).** The −12 above was the strongest reading of the
session, produced at the exact low. Follows from the documented design choice
that fuel "reports, never votes".

**Threshold.** 3+ instances. If H2 confirms, this may be redundant — the fuel
wording may already do the work without touching the score.

**Status: OBSERVING. Do not implement.**

---

## H4 — Is the gamma flip a reliable magnet / settlement level?

**Claim.** Price gravitates back to the flip, making it useful as a target and
as trade invalidation.

**Evidence so far (1 day).** 24 Aug: flip published at 29,049.6 on the 13:45
scan; session closed **29,050.7 — 1.1 points away**, after trading well below it
and reversing.

**25 Aug:** flip published at 28,976.3 on the 13:04 scan; session closed
**29,212.9 — 236.6 points away**, and price never traded down to it (session low
29,086.1, still 110pts above). Clearly *not* a magnet on this day. One hit, one
miss.

**Threshold.** 5+ days (this is a distributional claim, so it needs more).
Record the close-to-flip distance each day.

**26 Aug:** flip 29,098.5, close 29,353.7 — **255.2pts away**. Miss.
**27 Aug:** flip 28,966.9, close 29,566.7 — **599.8pts away**. Clear miss.

**Status: OBSERVING — 4 of 5, and looking weak.** One hit, three misses, the
misses widening. 24 Aug's 1.1pt finish now looks firmly like the coincidence it
was warned to be. **Do not use the flip as a target.**

---

## H5 — Does the budget under-read early in the session and self-correct?

**Claim.** Error is largest early and shrinks as the day progresses.

**Evidence so far (2 days).** Early (4 scans) mean error **+56.9**; late (1 scan)
**+5.3**. The 25 Aug PRE_NY scan came in at **−11.6** — the first *over*-read on
record, and it arrived late in the range's life rather than early, which is
consistent with the claim.

**Threshold.** 3+ days. If it holds, the fix is a time-of-day term on the
budget — not a flat multiplier, which would break the accurate late reads.

**Status: OBSERVING.**

---

## H6 — Is the level board producing clean reactions?

**Claim.** Published levels are reaction points, not just descriptive lines.

**Evidence so far (2 days).** Hit rate **0.58** across 5 graded scans. On 25 Aug
both published levels (29,299.6 structural call wall, 29,249.6 options shelf)
graded "traded both sides — chopped around it". That is now the dominant
outcome, and it has a plausible cause: both days were long-gamma/pinning
regimes, where chop *is* the correct behaviour at a level. Worth splitting the
eventual breakdown by gamma regime as well as by level type.

**Threshold.** 5+ days, then break it down by level *type* — if session
extremes react cleanly and, say, PD-mid never does, the board should drop the
latter.

**Status: OBSERVING.**

---

## H7 — Is the overnight gamma flip stable enough to trade off?

**Claim.** The flip published on an overnight/pre-London scan is unreliable,
because the chain reprices and rolls before the session that would use it.

**Why it matters.** The flip decides the *regime label*, which decides which of
the two strategies the brief recommends. If it moves several hundred points
overnight, an overnight regime call is close to worthless.

**First observation.** The scan of 24 Aug 21:56Z published flip **29,271.0** with price
29,051.2 → "BELOW flip, SHORT gamma, dealers amplify" and **−3** on the bias
score, the single largest bearish component. By 25 Aug 13:04 the flip was
**28,976.3** with price 29,252.8 → "ABOVE flip, LONG gamma". The regime label
**inverted overnight**, and it inverted because the flip moved **295 points**,
not because price moved. The strategy recommendation inverted with it
(Strategy 2 → Strategy 1). The overnight scan's direction call was WRONG (−15
STRONGLY BEARISH, day closed +140).

**Second observation.** 25 Aug 22:11Z flip **29,098.5** → 26 Aug 13:12Z flip
**29,207.2**: drift **+108.7pts**, and the regime label inverted again (long →
short gamma). Weaker evidence than the first, because price also moved 153pts
over the same window, so the inversion is not purely flip drift. **2 of 3.**

**Anomaly that widens the scope.** On 24 Aug the flip moved **192 points between
the 08:28 and 08:30 scans** — 120 seconds apart, on a chain that cannot have
repriced in that time — while price moved 8.9pts. The regime label inverted.
The other four short-interval scan pairs in the journal drift only 0.4–23.5pts,
so this is a single anomalous observation, possibly a cold-start artefact on the
session's first scan (08:28's flip of 29,049.9 nearly matches 13:45's 29,049.6,
while everything between sits 200–390pts higher).

H7 was framed as "the chain reprices and rolls **overnight**". That mechanism
does not explain a 192pt move in two minutes. **Widen H7 from overnight
staleness to flip stability generally**, and record consecutive-scan drift, not
just overnight drift. One data point — no proposal.

**Third observation, and the sharpest yet.** Between 25 Aug 21:43Z and 22:11Z —
**28 minutes** — the flip moved **+167.4pts** while spot moved about **12.7**.
Drift was **13× price movement**. That is the second large short-interval move
after the 192pt/2min anomaly; the other five consecutive-scan pairs on record
drift only 0.4–23.5pts.

Related, and it quantifies the cost: the `gamma` component swung **+2 → −3**
overnight on a 108.7pt flip move. A **5-point swing** — larger than the entire
net score of −4 that produced the wrong 26 Aug call — driven by the least stable
input in the model.

**Threshold.** 3+ days. Record the overnight flip and the next-day pre-NY flip;
measure the drift. Also log flip drift between any two consecutive scans.

**Status: OBSERVING. Do not implement.** If the drift is consistently large the
fix is to *widen the confidence band* on overnight regime calls, or suppress the
gamma component before the cash open — not to change the flip maths, which is
sound.

---

## H8 — Is the ATM-straddle expected move a useful boundary?

**Claim.** The ±EM band from the nearest-expiry ATM straddle marks where price
is likely to *close*, and is a better forecast than the VXN-derived daily range
the brief already prints.

**Why it matters.** It is the only forward-looking, market-priced range measure
in the brief. Everything else (ADR, fuel budget) is derived from realised
history.

**Cannot be backtested.** CBOE serves a live snapshot only — there is no
historical straddle price to test against. So this goes in as observation-only
and must be tracked forward.

**First observation (25 Aug, for the 26 Aug session).** Straddle 191pts → EM
**±162** → band **29,065 .. 29,390**. Close **29,353.7 — inside**, 36pts below
the top. *(Logged initially as 4.9pts outside, off the pre-roll close; the final
close was higher and landed inside.)*

**Second observation (27 Aug).** Straddle 306pts → EM **±260** → band
**29,221 .. 29,741**. Close **29,566.7 — inside**. Intraday high 29,642.1, also
inside.

**2 of 2 closes inside. 2 of 10 observations.** Far too early to mean anything,
but nothing has gone wrong yet.

**The trap to avoid.** EM prices a **close-to-close** move; ADR measures a
**high-low** range, which is always larger. Reading "EM 162 vs ADR 399" as "the
market expects a quiet day" is the same category error as reading the range
budget as price travel. The brief says so in words at the point of use.

**Threshold.** 10+ sessions (a 68% claim needs a distribution, not a handful).
Record: did the close land inside the band? Did price trade outside it intraday?

**Status: OBSERVING.**

---

## H9 — Do same-day index-defining earnings suppress the expansion signal?

**Claim.** When a same-day, index-defining earnings event is on the calendar,
the range comes in contained regardless of what expiry structure says — so a
`COHERENT_SHORT` "expect expansion" read should be discounted, not followed.

**Why it matters.** The two signals are computed independently and neither
defers to the other. On the day it mattered the brief printed the earnings line
and the expansion call side by side and let them contradict each other.

**Evidence so far (1 day).** 26 Aug, NVDA after the close. Expiry structure said
`COHERENT_SHORT`, confidence high: *"expect range expansion and trends that
persist. Today's ADR can be exceeded — don't cap the target too early."* Actual
range **325.7 against ADR14 398.7 — 82%**. No expansion, no persistent trend.

*Corrected 27 Aug:* the first write-up of this cited 286.0 / 72%, taken from a
grading run at 20:42 before the session had finished. The day's high and close
were both set in the final bars. 82% is contained but materially less dramatic
than 72%, and it weakens this observation accordingly.

**Threshold.** 3+ index-defining earnings days. NVDA is the most extreme
possible case, so a single observation from it generalises poorly.

**Status: OBSERVING. Do not implement.**

---

## H10 — The prior-week-range rule has no reclaim condition

**Claim.** `structure −3` ("price is BELOW the entire prior-week range; PWL is
now resistance") scores a *state* and has no term for price reclaiming that
range. So the penalty neither decays nor inverts when the premise stops holding.

**Why it matters.** It is one of the largest single components in the engine,
and on 26 Aug it was one of two inputs behind a call that was wrong by 249.8
points.

**Evidence so far (1 day).** 26 Aug 13:12, the rule fired on PWL 29,115.9.
Within the same hour:

| Level | Travel up | Travel down | Graded |
|---|---|---|---|
| 29,118.1 (London Low + PWL) | 145.8 | 29.4 | chopped |
| 29,086.1 (NY Low prev-day) | **177.8** | **0.5** | broke UP through it |

Price touched 29,086.1 and never traded half a point below it. The "resistance"
was reclaimed almost immediately and the −3 stayed on the books.

**Threshold.** 3+ instances where price is outside the prior-week range at scan
time. Record whether the range was reclaimed within the session, and whether the
call went the way the penalty implied.

**Status: OBSERVING. Do not implement.** The fix, if the evidence supports one,
is a reclaim term — not a smaller constant.

---

## H11 — Do the chart's ranked walls produce in-range levels?

**Claim.** C1–C3 / P1–P3 rank by gamma force with no proximity filter, so they
may sit outside the day's range and be useless as day-trade levels.

### ⚠️ The first observation was INVALID and is withdrawn

It reported *"1 of 7 reached, 6 never reached, ranked walls spanned 600pts"* and
concluded the ranks do not produce tradeable levels. **Every part of that rested
on grading the wrong ladder.** Caught by the trader, who noticed a level in it
(29,599) that had never appeared in any ladder he was given.

Three independent faults, any one of which invalidates it:

1. **Wrong ladder.** `--ladder auto` picked the 26 Aug 22:12Z file. That ladder
   was never delivered in a scan — it was generated while building the
   persistence feature.
2. **Pre-fix code.** It carries `book: None, dte_max: 45` — built on the 45-day
   book, *before* the book mismatch and the wall-dominance fixes. Grading it
   measures the version with the bugs in.
3. **Post-spike anchor.** Built at spot 29,492.8 in the post-NVDA move after the
   roll, so its ranks were spread across 600pts of a book anchored to a price
   the next session never returned to.

### The correct first observation

The ladder actually delivered with the 27 Aug scan (13:58Z, week book,
post-fix), graded from publication forward:

| Rank | Level | First-touch grade | **After it settled** |
|---|---|---|---|
| C3 | 29,514 | CHOP | held 120min, worst **−11.2** → support |
| C1 | 29,464 | CHOP | held **310min**, worst **−4.7** → support |
| C2 | 29,414 | BROKE | held 420min, worst **+1.6** → support |

**All three C-ranks were in range and all three were touched.** They span 100
points, not 600. The corrected result points the opposite way to the withdrawn
one.

**Status: OBSERVING, 1 valid observation of 3.** The concern is still live —
one week-book ladder is not proof the ranks are always in range — but there is
now no evidence for the original claim.

**Lesson.** `--ladder auto` picking "the newest file older than the target" is
not the same as "the ladder the trader was given". Ladders written by
development runs sit in the same directory as real ones. The auto-pick needs to
prefer a ladder that accompanied a delivered scan, and to refuse a pre-fix
`book: None` file outright.

---

## D5 — the level grader scores the first touch and nothing else

*Found by the trader 2026-08-27.* He read C1 29,464 as: swept once, reclaimed,
then support for the rest of the session, never broken again. `grade_level`
called it **CHOP**. He was right and the tool was wrong.

Three faults in the rule:

1. **Only the first touch counts.** `grade_level` looks at `REACT_BARS` after
   the first touch and stops. On a news-driven open the first touch is the
   worst possible sample — it grades the noise and discards everything after.
2. **No concept of role reversal.** A call wall that caps price, is reclaimed,
   and then acts as support is a level working well. First-touch scoring calls
   that "chopped".
3. **"broke UP through it" counts as a failure** even when the level sits below
   price and is simply never revisited. For a call wall in a rally that is the
   normal, successful outcome.

Measured properly on 27 Aug, C1 had **exactly one bar close below it** in the
whole post-publication session, then held for **310 minutes** with a worst
excursion of **4.7 points**.

`gex_retro.role_reversal()` now reports, for every touched level: which side
price settled on, from when, how long it held, how many times it was retested,
and the worst excursion through it. It is **additive** — `grade_level` is
unchanged, so the written review and the chart still agree, and the first-touch
grade sits beside the settled-behaviour read rather than being replaced by it.

Two guards learned building it: a level price never came near returns nothing
(a strike 650pts away was scoring as SUPPORT with a +651.6 "excursion"), and
the ladder retro now clips bars to **after the ladder was published** — it was
grading a mid-session ladder against the morning that preceded it, pure
look-ahead that survived only because the first test used a prior-evening
ladder against a whole next day.

**The general point, and it is the important one: the trader read the level
better than the tool did.** The measurement was wrong, not just the conclusion.

---

## H12 — Does the VOLUME-weighted wall hold better than the OI-weighted one?

**Claim.** GEXBot's volume-weighted GEX identifies levels price respects better
than our open-interest-weighted walls do.

**Why it matters.** It is the question that decides whether GEXBot *replaces*
the ladder or merely enriches it — and the volume lens is the one thing the
CBOE pipeline cannot build honestly, because volume carries no side.

**Evidence so far (0 sessions).** None. The only snapshot available at the time
of writing was Friday 4 Sep's close, frozen, so nothing could be graded.

What that snapshot *suggests*, and it is suggestion only: price closed at
29,542.65; the volume lens put its heaviest concentration at 29,525–29,550,
while our OI view showed 29,525 at approximately zero. One frozen observation,
after the fact, on an expiry day. **It proves nothing** — it is the reason to
run the test, not the result of it.

### The archive splits this hypothesis in two — verified 2026-09-05

The sibling recorder stores the **compact record only**: the per-strike ladder
goes to `gex_latest` (overwritten each poll) and is deliberately never appended
to `gex_snapshots`, because doing so would cost roughly 1 GB/month.

| Sub-question | Retro-answerable from the archive? |
|---|---|
| Does the **volume wall** hold better than the **OI wall**? | **Yes** — `major_pos_vol` / `major_neg_vol` / `major_pos_oi` / `major_neg_oi` are in every record |
| Do the two lenses disagree, and when? | **Yes** — `regimes_agree` / `walls_agree` are precomputed |
| Does the ranked **C1–C3 / P1–P3 ladder** hold? | **No, and never will** — per-strike history is not retained, by permanent design |

The headline claim is the first row, so the archive is sufficient for H12 *as
written*. The trap is that `gex_retro.py --ladder` grades a **ranked ladder
file**; pointing it at the archive would silently promise a comparison the data
cannot support. Any archive reader must use a separate path that marks its
output walls-only, so the limit is enforced rather than remembered.

**Threshold.** 5 sessions. For live scans, persist a GEXBot ladder alongside
ours and grade both with `gex_retro.py --ladder` and `role_reversal()` — same
rule for both, so they cannot drift. For archived days, walls only.

**Count UNCHANGED at 0 of 5.** Nothing has been recorded since the single
manual run against a frozen Friday feed; the cron is Mon–Fri and 5 Sep was a
Saturday. **Four documents per poll are two observations**, not four —
`NQ_NDX` is `NDX` plus a constant 30.82 and `ES_SPX` is `SPX` plus 6.13,
verified exact across every wall field, so the futures rows carry no
independent information.

**Update 2026-09-05 — the archive was read directly, not inferred.** The
sibling recorder's Firestore archive became readable from a Claude session and
was read field by field (`research/gexbot/EVALUATION.md` §11); the split above
is verified against the stored documents rather than against the recorder's
code. It changes no count: the archive held that one frozen Friday poll and
nothing else. A design for the walls-only reader — the one that must not reuse
`--ladder` — is in `research/gexbot/PROPOSAL-ARCHIVE-RETRO.md`, unbuilt until
Monday's data exists to test it against.

**Status: OBSERVING. Do not swap the engine.**

---

## H13 — Is GEXBot's `zero_gamma` a real flip, or a fallback to spot?

**Claim.** `zero_gamma` may not be an independently computed flip.

**Why it matters.** The flip decides which of the two entry models the brief
recommends. It is the single highest-consequence number in the scan, and H7
already established that our own flip is unstable enough to be the largest
contributor to a wrong call.

**Evidence so far (1 frozen snapshot).** On 2026-09-04's close `zero_gamma`
equalled `spot` **exactly** (29,542.65) for both `gex_full` and `gex_zero`. It
differed for `gex_one` (29,470.0), which argues it is computed rather than
stubbed, and Friday was an expiry with heavy pinning — so equality is
plausible. But a computed value landing exactly on spot to two decimals earns
suspicion, not the benefit of the doubt.

For reference, our own flip on the same snapshot was **29,323.2 — 219 points
away**.

**The stub theory is dead — verified 2026-09-05.** On the *same feed at the same
instant*, `zero_gamma` differs from `spot` on three of four symbols:

| | spot | zero_gamma | diff |
|---|---|---|---|
| **NDX** | 29,542.65 | 29,542.65 | **0.00** |
| SPX | 7,717.85 | 7,712.50 | −5.35 |
| RUT | 2,975.32 | 2,970.08 | −5.24 |
| QQQ | 718.95 | 717.34 | −1.61 |

**A field stubbed to spot could not differ on SPX, RUT and QQQ.** So it is
computed. QQQ matters most here: it is the *same underlying* as NDX and still
returns −1.61, which rules out "their Nasdaq calculation degenerates" as the
explanation.

**This does not rehabilitate the number.** It reframes the question from *"is it
a stub?"* (answered: no) to *"why does the one symbol we trade land exactly on
spot?"* — for which coincidence on a heavily pinned expiry Friday remains the
leading explanation, and one snapshot cannot distinguish it from anything else.
A computed flip sitting on spot is just as unusable as a stubbed one.

**Update 2026-09-08 15:39Z — second observation, and the pattern does not hold.
Count 1 -> 2 of 5.** Read live during the RTH scan, off the same feed:

| | spot | zero_gamma | diff |
|---|---|---|---|
| **NDX** (`gex_full`) | 29,582.66 | 29,532.36 | **-50.30** |
| **NDX** (`gex_zero`) | 29,583.02 | 29,491.02 | -92.00 |
| **QQQ** | 720.06 | 717.59 | -2.47 |

On 4 Sep NDX's `zero_gamma` sat **exactly** on spot. On a live RTH feed it does
not -- it is 50pts below, and the two books disagree with each other (-50.30 vs
-92.00), which a spot fallback could not do on either count.

**This is evidence FOR the coincidence reading, not merely absence of evidence
against it.** 4 Sep was a heavily pinned expiry Friday; the equality did not
survive the first non-expiry session. Nothing structural about the Nasdaq
calculation degenerating -- it computes, and today it computed away from spot.

It is still not usable as a flip, and the reason is unchanged: on the same
snapshot ours read 29,405 and theirs 29,525, **119pts apart**, and the board
uses ours. Two of five. Three more RTH samples before this says anything.

*Earlier framing, kept because it was the reasoning at the time:* a working
credential and a cleaner argument both read like progress; neither was a second
observation.

**Threshold.** 5 RTH samples. Record `zero_gamma`, their `spot`, and our flip on
every scan — **and record it for QQQ alongside NDX**, since a same-underlying
control is now known to be informative.

*Provenance: the four-symbol table above was read out of the archived 4 Sep
record field by field (`research/gexbot/EVALUATION.md` §11), on one feed at one
instant — which is what makes the cross-symbol comparison valid. It is still
that same single snapshot.*

**Status: OBSERVING. Do not use as the flip.**

---

## Rejected after testing (recorded so they are not re-proposed)

**R1 — Separate 0DTE-only gamma walls.** *Tested and rejected 2026-08-25.*
Hypothesis: since 0DTE carried 5,582,029 contracts of volume against 650,147 on
the next expiry, its walls should be published separately from the blended
this-week bucket. Measured on the live chain, the two rankings are nearly
identical:

| | 0DTE only | blended dte 0-3 |
|---|---|---|
| 1st | 29,233.5 CALL 2.52bn | 29,233.5 CALL 2.80bn |
| 2nd | 29,183.5 CALL 0.87bn | 29,183.5 CALL 1.08bn |
| 3rd | 29,283.5 CALL 0.86bn | 29,283.5 CALL 0.99bn |

Same strikes, same order. Gamma explodes as expiry approaches, so 0DTE already
*dominates* the blended sum — separating it out would add chart lines without
adding information. **Do not re-propose without new evidence.**

**R3 — Session VWAP in the level board.** *Rejected 2026-08-25 by the trader.*
Tested and it works — computable from bars already fetched, and 25 Aug's NY
VWAP (29,185.4) landed within 2 points of the 0DTE call-gamma pivot (29,183.5),
which is genuine cross-mechanism confluence. Not added: **it is already on the
chart.** The brief's job is to supply what the chart cannot, and duplicating a
line the platform draws natively is clutter, not enrichment.

Keep this in mind when weighing future candidates: "is it material?" is only
half the test — the other half is "is it already in front of him?"

**R2 — Vanna and charm as chart levels.** *Rejected 2026-08-25 on design
grounds.* Both are computable from the chain, and both are real forces (charm
drives the end-of-day pin, vanna drives vol-crush rallies). But neither is a
*price level* — they are flows that vary continuously with spot and vol. There
is nothing to draw. If they earn a place later it is as a one-line regime flag
in the bias engine, never as a marking.

---

## Resolved / withdrawn

**W1 — "Fuel is systematically too tight; recalibrate."** *Withdrawn 2026-08-24.*
Rested on grading the budget against price traversal instead of range extension,
which manufactured a 3.8× under-estimate from an accurate forecast. The review
engine was fixed; the proposal was wrong.

**W2 — The 2026-08-20 data point.** *Withdrawn 2026-08-24.* It came from a
backdated journal entry created to test the review loop and deleted immediately
after. It was then cited as one of "three independent sessions" — exactly the
archive corruption this process exists to prevent. Never cite a synthetic entry.

---

## Defects found and fixed (not hypotheses — these were bugs)

**D1 — Fuel measured across the 21:00 UTC day rollover.** *Found and fixed
2026-08-25.* The feed goes quiet over the daily roll, so a scan in that window
found zero bars for the new trading day. `levels_fuel.run()` silently fell back
to the last completed **daily** bar — i.e. it served yesterday's finished range
as today's. The 24 Aug 21:56 scan therefore printed *"range 530.9, 117.7% used,
EXHAUSTED, 0.0 budget"* **56 minutes into a session that went on to build a
397pt range**, telling the reader the day was over before it had begun.

Not a calibration question and so not subject to the 3-day rule — a range that
does not exist yet is *unknowable*, not *exhausted*. `levels_fuel` now reports a
new `SESSION_PENDING` state with the full ADR as budget, and the brief says in
words that there is no fuel read yet. `track.py` quarantines any pre-fix scan
carrying the signature (>100% ADR used within 90 minutes of the roll) so it
cannot enter the statistics.

It did **not** affect the direction call: fuel reports and never votes, so the
bias score was untouched. The two failures on 24–25 Aug overnight are
independent — this one and H7.

**D2 — Secondary-walls table described put strikes backwards.** *Found and fixed
2026-08-26, on the first live scan that contained any.* Under this repo's stated
dealer convention (long calls, short puts) a put-dominant strike means dealers
are **short** gamma there: they amplify, so price accelerates through rather
than stalling. The table called every put-dominant strike below spot *"a genuine
floor while we stay in long gamma"* — the opposite behaviour, carrying a
long-gamma caveat, on a session trading BELOW the flip in short gamma.

The result was two "genuine floors" printed below spot on the same page as the
brief's own *"DOWNSIDE path: clear … nothing structural to slow a breakdown. Do
not fade it."* Contradictory guidance in one document, on the side the trader
would have been managing a short from.

Moneyness was wrong too: a put struck **above** spot is in-the-money, not out.
The label read *"out-of-the-money put gamma above spot — thin, expect little
reaction"* while attached to the single largest force in the table (1.02bn
across 18,551 contracts).

Behaviour is now derived from the **sign of dealer gamma** at the strike rather
than from which side of spot it sits, and is regime-aware.

*Lesson.* The bug survived a full build, a render check and a docs pass because
every one of those confirmed the table *appeared*. Nothing checked it against
the regime read on the same page. **A new panel needs one test that it does not
contradict the rest of the brief**, not just that it renders.

**D4 — the put wall was not required to be put-dominated.** *Found by the trader
2026-08-27, from the chart contradicting itself.*

`max(below, key=put_gex)` returns the strike carrying the most put gamma below
spot — but never checked whether puts actually **dominate** that strike. On
2026-08-27 it returned **29,291**, which held:

| | |
|---|---|
| Call open interest | **45,880** |
| Put open interest | 10,432 |
| Ratio | **4.4 : 1 calls** |
| Net gamma | **+0.742bn** — the 3rd-largest POSITIVE strike on the board |

The brief called it *"heaviest floor this week — expect a bounce and a good
long-sweep here."* The chart stamped **C3** on the same row. One strike, two
labels that cannot both be true, and a long recommended off what is actually a
call-gamma brake.

**NDX makes this the normal case, not an edge case.** The index carries far less
protective put open interest than SPX, so on many days **no strike below spot is
put-dominated at all** — on 27 Aug only 4 of the strikes below spot had negative
net gamma and the largest was −0.029bn. The honest answer on such a day is *there
is no put wall on this chain*, not to promote whichever call-heavy strike happens
to hold the most puts.

Both walls now require dominance (`call_gex > put_gex` / `put_gex > call_gex`),
fixed in `gex_levels.build()` so the brief and the chart inherit it together. The
chart says in words when no put wall exists.

*This is the third time the same root cause has produced a bug* — D2 (secondary
walls), the C/P rank inversion in `gex_chart`, and now this. **Naming a level
after a side without checking which side actually dominates it.**

**And the guard that catches it now existed only as a lesson.** D2's write-up
said: *"a new panel needs one test that it does not contradict the rest of the
brief."* That was written down and never implemented. `gex_chart.consistency_check()`
now runs on every render and refuses to stay silent when a strike carries a PUT
WALL label and a C rank, a CALL WALL label and a P rank, or a wall whose net
gamma has the wrong sign. **A lesson recorded but not built is not a fix.**

**D3 — `track.py` graded an unfinished trading day.** *Found by the reviewer and
fixed 2026-08-26.* The completeness guard tested `bars < 150`. That does not
work: the trading day starts at 21:00 UTC the **previous evening**, so 150 M_5
bars accumulate by 09:30 UTC — four hours before NY opens. At 13:23 UTC on
26 Aug it admitted a day with 185 bars (complete days have 276), whose "close"
was the last tick and whose range had not finished extending.

That single unfinished day flipped **H1's mean error from +46.6 to −19.9 — a
sign change** — and turned `actionable` to **YES** while HYPOTHESES.md still
correctly said nothing was actionable. Fixed to test the wall clock
(`now_utc >= 21:00 UTC on the day's own date`), with the bar count kept only as
a secondary guard against a gappy feed.

The same pass fixed an **over-exclusion**: the rollover quarantine dropped whole
rows, but the corruption is field-level. D1 establishes that fuel reports and
never votes, so those scans' direction calls are sound. Dropping them made the
scoreboard read 1 right / 1 wrong when the honest tally was **1 right / 2
wrong**, and the `SESSION_PENDING` branch would have done that to every future
overnight scan — exactly the population H7 exists to study. Fuel fields are now
quarantined; direction and level statistics keep the row, marked `*`.

*Lesson.* Both D1 and D3 are the same shape: **a guard written against the
symptom rather than the definition.** "Not enough bars" and "over 100% ADR" are
proxies; "the day has not ended" and "this field was measured across a
rollover" are the actual conditions. Proxy guards fail silently and in the
flattering direction.

---

## Regression test — the invariants today's bugs violated

`scripts/test_consistency.py` (24 checks; `--offline` skips the live half).

Every check corresponds to a bug that actually shipped. The point is not to
prove the code works — it is to make **these particular failures loud**, because
every one of them was silent. A brief and a chart that disagreed still rendered.
A put wall on a call-dominated strike still printed. An unfinished day still
produced a number.

Structural: wall dominance at source and in the chart · chart defaults to the
brief's book · `brief.py --chart` builds both files from one `gather()` ·
`--no-journal` exists · both graders honour `test_artefact` · day-completeness by
clock not bar count · held-back days printed · H1 reported per day · ladder retro
clips to post-publication · auto-pick refuses pre-fix ladders · `role_reversal`
ignores untouched levels · one grader shared by `track` and `gex_retro` · every
ladder records its book or is marked `pre_fix`.

Live, from a single build: chart flip == brief flip · both walls agree within bin
rounding · no strike carries contradictory labels · each wall is dominated by its
own side · every C rank is net positive and every P rank net negative.

**It found a real file on its first run** — the 27 Aug 13:23 ladder, written
before the book fix, still sitting in the directory where the auto-pick looks.
Marked `pre_fix` rather than deleted, and the retro now refuses it explicitly.

**Latent, left in place deliberately:** `max_call_oi` / `max_put_oi` in
`gex_levels` carry no dominance test. They are honestly named — they are the
strike with the most open interest on that side, nothing more — and nothing
consumes them but a debug printer. They are annotated with a warning, because
they are exactly the field someone reaches for when building a "floor" and would
reproduce D4 verbatim.

## Housekeeping carried forward

- **Deduplicate near-identical scans.** Four landed within five minutes during
  testing. `track.py` now collapses scans inside a 15-minute window; the raw
  journal keeps them all.
- **Exclude incomplete sessions.** A scan 56 minutes into a new trading day was
  being graded "extension 0.0, traversal 26.1". `track.py` now requires ~12.5h
  of bars before a day enters the evidence.
- **Weekend PREP scans** never enter statistics (`is_trading_day: false`).
- **Verification re-runs are marked, not deleted.** On 2026-08-27 five journal
  entries were written for one real scan — four came from re-running the brief
  while fixing the put-wall dominance bug. The 15-minute dedupe collapses only
  the closest pair, so three would have entered the evidence as independent
  observations of a market state that was sampled once. Exactly the inflation
  the dedupe exists to prevent, caused this time from the inside.
  `brief.py --no-journal` prevents it going forward; the four already written
  carry `test_artefact: true` and `track.py` excludes them and says how many.
  **Marked rather than deleted, deliberately** — the archive's job is to record
  what happened, and a silent deletion is indistinguishable from the synthetic
  entry that produced W2.
- **Quarantine corrupt inputs, don't grade them.** A scan whose *input* was
  wrong is not a forecast that failed. `track.py` now prints an EXCLUDED block
  so the exclusions stay visible rather than silent.

---

# Observations appended 2026-08-27 (trading day 2026-08-26, graded post-roll)

Full working: `journal/2026-08-26/REVIEW.md`. Nothing below is a proposal.

**Status update:** **3 trading days on record** (24, 25, 26 Aug). `track.py`
prints `actionable: YES` on the *day count*, but per-hypothesis only **H1** and
(nominally) **H5** have reached threshold, and neither supports a change.

**H1 — threshold reached; no change supported.** Per-day mean error is
**+61.2 → −11.6 → −73.0**. The sign reverses and the magnitude is still moving,
so there is no stable bias to correct. Note the 26 Aug figure was **−112.7** when
measured last night at 20:42 UTC and is **−73.0** post-roll: the session high
was set in the final bar (20:55), adding 39.7 pts of extension to every scan on
the day. The reversal is real but 35% smaller than it looked. *Keep observing.*

**H2 — no new instance.** 26 Aug produced no LOW_FUEL/EXHAUSTED-at-extreme scan
(MODERATE / ROOM_TO_EXPAND / SESSION_PENDING). Still **2 of 3**.

**H3 — no new instance.** Still 1.

**H4 — third data point, a miss.** Close 29353.7 vs published flips 29207.2
(13:12), 29230.7 (13:14), 29098.5 (22:11) → **123–255 pts away**. Running
1 hit / 2 miss over 3 days. Needs 5. *Do not use the flip as a target.*

**H5 — day count reached, evidence not.** The late-session bucket still holds
exactly **one** scan (24 Aug 13:45, +5.3). A time-of-day term cannot be fitted to
one late observation. Insufficient despite the day count.

**H6 — third day.** Hit rate 0.71 (mean of 4 scans); running mean 0.56. "Traded
both sides — chopped" remains the dominant outcome. Two cull candidates now
have a track record worth watching: **MAX PAIN** was touched on 3 of 4 scans and
never stalled price once (chopped, chopped, broke down through), and **PD mid
29144.0** chopped on all 4. Needs 5 days. *Logged, not proposed.*

**H7 — strongest data point yet, but the pair count did not advance.** No
overnight scan was taken on the evening of 26 Aug, so there is still no third
overnight→pre-NY pair (**2 of 3**). However, the *widened* H7 (drift between any
two consecutive scans) gained a sharp observation: between **25 Aug 21:43Z and
22:11Z — 28 minutes apart — the flip moved 28931.1 → 29098.5 (+167.4 pts) while
spot moved ~12.7 pts** (29213.5 → 29226.2). Flip drift was **13× price
movement**. That is the second large short-interval drift on record after the
192 pt / 2 min anomaly of 24 Aug; the other five short-interval pairs drift
0.4–23.5 pts. Related: on 26 Aug the `gamma` component swung **+2 → −3** between
the 22:11Z and 13:12Z scans on a **+108.7 pt** flip move — a 5-point swing, larger
than the whole net score of −4, on the least stable input in the model.

**H8 — first outcome recorded (1 of 10).** Band **29,064 .. 29,388** (EM ±162
from the 25 Aug ATM straddle at 191 pts, ATM IV 15.5%). 26 Aug close **29353.7 →
INSIDE the band**. Intraday **low 29028.1 → 36 pts BELOW** the lower bound; high
29353.8 stayed inside. Result: **close inside / low breached**.

**H-new (opened, 1 day) — the prior-week displacement rule has no reclaim
condition.** On 26 Aug `structure −3` fired for *"price is BELOW the entire
prior-week range (29115.9–30245.8); PWL 29115.9 is now resistance, not
support"*, and it was half the bearish weight behind two WRONG −4 PRE_NY calls
(price then ran +249.8). Within the same hour `29118.1 London Low + PWL` graded
*traded both sides* at **145.8 up / 29.4 down**, and `29086.1 NY Low (prev-day)`
graded ***broke UP through it*** at **177.8 up / 0.5 down** — price touched it and
never traded 0.5 pts lower. The prior-week low was reclaimed and held, and the
rule scores a **state** with no term for reclaim, so the −3 neither decays nor
inverts. **Threshold: 3 days.** Record each time price is below the prior-week
range at scan time and whether it reclaims intraday. *One observation — no
proposal.*

**D2 did not regress.** `2211-overnight.md`'s secondary-walls table
("28993.0 … a genuine floor while we stay in long gamma") was written 22:11 on
25 Aug, *before* the D2 fix landed. It is a **pre-fix artefact and must not be
graded as a forecast.** The 27 Aug brief carries the corrected regime-aware
wording.

## Two methodology items awaiting a decision (not calibration, so not 3-day gated)

**M1 — `track.py`'s H1 mean pools scans, not days; 24 Aug is counted 4×.** Its
08:28, 09:37 and 12:40 rows carry the **identical** budget 88.7 against the
**identical** extension 168.5. Verified against bars: the live range really was
362.4 at all three timestamps, so this is genuine market behaviour, **not** a
stale-fuel defect — but it is still one budget reading graded three times. The
15-minute dedupe window does not catch it. Pooled by scan the H1 mean is
**+12.4**; weighted one-vote-per-day it is **−7.8**. Which weighting H1 should use
is a decision for the trader, not a tuning.

**M2 — the unfinished-day exclusion is silent.** `track.py` stores
`_excluded: "session not finished"` in `per_day` but never prints it; only the
fuel quarantine gets a visible EXCLUDED block. 2026-08-27 was correctly held out
and the reader is told nothing. Same shape as **D3**: a guard that fails quietly
and in the flattering direction. The housekeeping rule already says exclusions
must stay visible.

**Register gap: there is no H9.** This file runs H1–H8. A review task referred to
"H9 needs 3 days". Flagged, not created — inventing one would corrupt the count.

### Resolved 2026-08-27

**M1 — RESOLVED.** `track.py` now reports H1 **both ways**: per-scan and
per-day, and labels the per-day figure as the one to read for claims about the
model. It does not pick a weighting silently. Per-day the series is
**+61.2 → −11.6 → −73.0, mean −7.8** — monotonic, which is a clearer picture
than either pooled number gave.

**M2 — RESOLVED.** `track.py` now prints a `HELD BACK — day not finished` block
naming each day and its bar count, alongside the existing fuel-quarantine block.

**Also fixed: the `actionable: YES` banner.** It was a global day-count gate and
read far more permissively than the individual thresholds — shouting YES at 3
days while H4/H6 need 5 and H8 needs 10. It now names which hypotheses the day
count applies to and states that day count alone is not evidence.

**The H9 gap was mine.** The 26 Aug review told the trader "opening as H9" and
then never wrote it down — the claim lived only in a chat message. That is
precisely the failure this register exists to prevent, and it is worse than
forgetting, because H9 was subsequently referenced in a review task as though it
existed. **A hypothesis is opened by writing it here, not by saying so.** It is
created properly below.

---

# Observations appended 2026-09-08 (trading day 2026-08-28 — NOT GRADED)

Full working: `journal/2026-08-28/REVIEW.md`. **Nothing below is a calibration
proposal, and no hypothesis count advances.**

**Status: the evidence base did not move.** `track.py` still reads **4 trading
days / 10 scans (24–27 Aug)**. 2026-08-28's only journal entry carries
`test_artefact: true` ("Run to verify sync_archive.py self-commits a scan"), so
`review_day.py` correctly returns *no journal entries*. Today's 2026-09-08 scan
is correctly `HELD BACK — day not finished` (D3's fix working as intended; it
was not graded).

**The binding constraint is not calibration, it is observation rate.** 08-28 has
no real scan, and **31 Aug and 1–4 Sep have none at all** — confirmed against
`research/chart-ladders/`, which jumps `2026-08-27-2233` → `2026-09-08-1539`.
Nothing was lost; nothing was run. Eleven calendar days have passed since the
last graded session and H4/H6 (5 days) and H8 (10 days) are exactly where they
were. No amount of analysis substitutes for sessions.

**H1 — no new point.** Per-day series unchanged: `+61.2 → −11.6 → −73.0 → −86.4`,
mean −27.5. Still a monotonic trend, still no multiplier proposed. Still waiting
on an unpinned / short-gamma day.

**H4 — no countable point.** The 08-28 flip 29145.6 sat **231 pts below** the
session low (29376.4) and was never approached. Consistent with 1 hit / 2 miss,
but **excluded**; the register stays at 3 of 5 days.

**H6 — do not let this reach threshold on the current instrument.** See M4 below.
PD mid chopped again on 08-28 (`up 258.1 / dn 46.1`), a fourth consecutive
session — **not counted**.

**H10 — not testable on 08-28.** The scan read `structure 0, price inside the
prior-week range (29115.9–30245.8)`. Still **1 of 3**.

**Checked and found to be nothing (recorded so it is not re-proposed).**
Across all graded scans the `fuel` component scores 0 points in **25 of 25**
instances and `events` in **14 of 14**. That is not dead weight — D1 already
states *"fuel reports and never votes"*, and `bias_engine.py:176,181,239`
hard-codes `add(..., 0, ...)`. **No proposal.** Every other component is live:
gamma 64% nonzero, vol 63%, breadth 60%, macro 58%, structure 53%, rates 47%,
news 26%. The only residue is presentational — non-voting rows sit inside
`bias_components` carrying a `points` field alongside the rows that do vote,
which invites a reader (or a reviewer agent) to infer they contribute.

**Not opened, 1 instance, recorded so the count is honest.** On the 08-28
artefact `breadth +2` came from *"mega-cap avg +3.83%, NVDA +8.74%"* — a
post-earnings pop read as forward direction, on a day that closed −115.6. One
instance is not a hypothesis. It is **not** being opened here; if it recurs
twice more, write it up properly. (Per the H9 lesson: a hypothesis is opened by
writing it in this register, not by mentioning it.)

## Methodology items awaiting a decision (not calibration, so not 3-day gated)

**M3 — `latest_unreviewed()` returns a day it then refuses to grade, and calls
the refusal an error.** `review_day.py:204` filters on `is_trading_day` but not
on `test_artefact`, unlike the matching filters at `review_day.py:75` and
`track.py:82`. It returns `2026-08-28`; `review()` then answers `{"error": ...}`
instead of the `{"status": "skipped"}` shape that exists for non-gradeable days,
so a caller distinguishing *skip* from *failure* sees a failure. Separately,
nothing in the codebase reads `REVIEW.md` — `grep -rn "REVIEW.md" --include=*.py`
returns nothing — so "unreviewed" is a misnomer: it returns the most recent
trading day whether or not it has been reviewed. Same shape as D1/D3: **a filter
written in three places and kept consistent in only two.**

**M4 — H6 is being tallied off a label D5 already established is unreliable.**
D5 recorded that `grade_level` scores the first touch only, has no concept of
role reversal, and that *"broke UP through it counts as a failure"*. Its fix was
deliberately **additive**: `gex_retro.role_reversal()` was added and
`grade_level` left unchanged. But `review_day.py` still emits the `grade_level`
string, and H6's evidence (*"traded both sides — chopped remains the dominant
outcome"*, hit rate 0.56–0.58) is tallied from exactly that string. Two
sub-faults, each verifiable from a single row:

1. **Near-misses count as touches, and then as breaks.** `TOUCH_TOL = 8.0`
   admits bars whose high never reached the level; the reaction string then
   reports the direction of subsequent travel. Instances in the graded archive:
   08-24 08:28 `MAX PAIN 29099.3` (`travel_down −5.1`, "broke UP through it");
   08-24 08:30/32/33 `PWL 29115.9` (`−0.9`); 08-27 13:23 `PDH 29353.8` (`−7.0`);
   and, unmasked but not counted, 08-28 `CALL WALL 29645.0` (`travel_up −4.5`).
   **Two graded days plus one excluded day.** This is already inside an open
   hypothesis: H6's cull case against MAX PAIN (*"touched on 3 of 4 scans and
   never stalled price once"*) rests partly on a 5.1-pt near-miss.
2. **First-touch blindness is still in the published output.** On 08-28 the
   heaviest level on the board — `29645 CALL WALL ●●●●● 1.30bn` — graded
   *"broke DOWN through it"* off a 02:15 UTC near-miss, while price traded
   **above it for 14 bars (14:35–15:40 UTC) to a high 103.3 pts through it**.
   The output says the wall broke downward on a day price broke it upward.

*Decision needed before H6 reaches 5 days:* is H6 tallied from
`role_reversal()` or from `grade_level`, and should `travel_up < 0` /
`travel_down < 0` report a near-miss rather than a touch-and-break? Re-deriving
after the threshold is hit would mean culling levels on a polluted statistic.

**M5 — `test_artefact` is one flag doing two different jobs.** On 27 Aug it
marked **verification re-runs**: one market state journalled five times, where
exclusion is unarguably right because counting them turns one observation into
five. On 28 Aug it marks a **plumbing test that produced a unique, live,
uncontaminated forecast** — a market state sampled exactly once, on a real
trading day, `prediction` written before the outcome was known. Excluding the
first prevents inflation; excluding the second **discards a real observation**,
and here it discarded a **wrong** one (bias +4 MILDLY BULLISH; the session closed
−115.6), i.e. it failed in the flattering direction — the precise shape of the
D1/D3 lesson. **Not proposed and not counted.** But the flag needs two names —
`duplicate_of` vs `provenance: plumbing-test` — and which one 28 Aug carries is
the trader's call, not the reviewer's.

---

# Defects found 2026-09-09 (during the live scan, before delivery)

## D6 — a FRESH timestamp on a STALE price inverted the regime call

**What happened.** The 15:13Z build published `CFD/index offset -131.3`, from
`NDX reference 29498.6` against a CFD at 29367.3. The true offset was about
**-3**. Every options level on the board — call wall, put wall, max pain, the
flip, every secondary concentration — was **~128pts too low**.

**Why it mattered more than a shift.** The flip published at 29281.8 with price
85.5pts above it, so the brief called **long gamma, Strategy 1, "this is your
fade day"**. Corrected, the flip sat at ~29,409 with price at ~29,371 —
**below** it. The regime was inverted, and with it the entry model.

**How it got through.** `_cash_is_stale()` checks the quote's *timestamp*.
CBOE's `_NDX` returned `last_trade_time` 16 minutes old — inside the 30-minute
tolerance — alongside `current_price` 29,510.7 while the index was actually at
29,376. On a later poll the timestamp advanced by a minute and the price did
not move at all: the feed was ticking its clock, not its value. The quote's own
reported session low (29,393) was already above the live index, which is
internally impossible and was the tell.

**The root cause is one already in this register:** a guard written against a
**proxy** (recency of the timestamp) rather than the **definition** (is this
price current?). Same family as D3's `bars < 150` and D4's missing dominance
test. The docstring on `_nq_implied_cash` records the *previous* time this bug
bit — a -200.7 offset from a stale Monday pre-market close — and the fix then
was the very timestamp check that failed here.

**Two independent confirmations, which is what made this safe to act on:** live
`^NDX` read 29,376.2 and GEXBot's own `spot` read 29,372.72. CBOE alone
disagreed.

**Fix.** `_ndx_live_yahoo()` provides an independent live print;
`gex_levels.build()` compares it against CBOE's and, past
`CASH_DIVERGENCE_TOL = 25.0` pts, anchors to the independent print and labels
the basis `live_cash_divergence_corrected`. The divergence is now always
recorded in `basis` even when it passes, so the check is visible rather than
silent. The timestamp path is unchanged and still handles the closed-market
case, where both sources agree on the same close and the value check correctly
does not fire.

**What this does NOT fix.** Both sources could lag together. The check proves
disagreement, never freshness.

## D7 — the strongest ceiling on the chain appeared nowhere in the brief

Found while verifying D6's fix: the corrected 15:16Z board carried **no CALL
WALL row at all**, though the wall existed (29,500 NDX, 1.32bn, 18,832
contracts, and the 45-day call wall too).

Two filters compounded:

1. `keep()` in `brief.py` drops a CORE level beyond `budget * 1.75`. Against a
   64pt budget the cap was 112pts. The call wall at +140 was dropped; the put
   wall at -110 survived **by two points**. The asymmetry was accidental — it
   tracked where price happened to sit, not anything about the walls.
2. The footnote then rendered `far[:6]`. Six liquidity levels sorted ahead of
   the call wall, so it was truncated out of the fallback as well.

Dropped from the board *and* from the footnote, the level ceased to exist in
the output — with no warning, because each filter did what it was written to do.
This breaks the skill's own contract (*"Never invent a level. Everything
markable comes from the level board"*): a level absent from the board cannot be
marked. It defeats the wall-to-wall strategy this chart was built to serve.

**Fix.** `far_line()` partitions the footnote so `CALL WALL`, `PUT WALL`,
`GAMMA FLIP` and `MAX PAIN` are never truncated; the 6-item cap now applies to
what remains. **`keep()` is deliberately unchanged** — altering it would change
which levels get marked and their stretch tags, which is model behaviour and
belongs behind the evidence gate. This fix only guarantees that a wall the
budget filter rejects still gets *said*, in the footnote, where it always
should have been.

**Open question for the register, not acted on:** whether a wall should be
subject to the range-budget filter at all. It is a dealer-hedging boundary, not
a distance-from-price forecast, and the stated strategy is to trade from one
wall to the next. Needs evidence, not a same-day edit.

## Journal hygiene for 2026-09-09

Three entries exist for one scan (1513, 1517, 1520). **1520 is the record.**
1513 is marked `test_artefact` with `artefact_reason: defective_build` (D6),
1517 with `artefact_reason: verification_rerun`. `track.py` reads 5 trading
days / 11 scans and holds today back as unfinished, which is correct.

`artefact_reason` is the discriminator **M5** asks for — the same flag was
doing two jobs. It is written here but **no reader consumes it yet**; the M3/M5
decision should settle how all three sites filter, rather than a fourth
condition being bolted on mid-scan.

---

# Observations added 2026-09-08 review (written 2026-09-09)

Source: `review_day.py 2026-09-08 --json`, `track.py`, plus a live FRED read.
One gradeable scan (15:39Z NY_MIDDAY), 0 test artefacts. Full write-up in
`journal/2026-09-08/REVIEW.md`. **One item proposed (P1, a defect). Everything
else is an observation appended to an existing open item.**

## P1 — FRED observations carry an age and nothing reads it; the brief says "today"

**PROPOSED — defect, not calibration.** The 09-08 call was bias **+4 MILDLY
BULLISH**; price fell 83.3 and the session closed −82.6. Bucket decomposition:
`gamma +2, vol −3, rates 0, macro +6, breadth +1, fuel 0, structure −1,
news −1`. **Strip macro and the score is −2 — the correct sign.** Macro alone
flipped the call.

Inside macro: `real_yields` **+3**, `yield_decomp` +1, `credit` +2, rest 0.
`real_yields` is the **heaviest single term in the whole engine**
(`bias_engine.py:136`, `_W["real_yields"] = 3`) and it read DFII10 as *"down 3bp
**today**"*. DFII10's latest observation available on 2026-09-08 was
**2026-09-03** — a Thursday value printed as "today" on a Tuesday, **3 business
days stale**. `bias_engine.py:132-133` justifies the macro weight with *"FRED
publishes with a 1-2 day lag"*. Nothing enforces it.

The staleness was visible **in the same brief**: `yield_decomp` honestly printed
*"(2026-09-02 to 2026-09-03)"* directly under a "today" that contradicted it.

**Structural aggravator.** `aligned_change()` exists precisely to stop
cross-series lag mismatches — and only `yield_decomp` (weight 1) uses it.
`real_yields` (weight 3) takes DFII10's own `chg_1`, unaligned and unaged. **The
heaviest term is fed by the stalest series, by construction.** Verified live
2026-09-09: `T10YIE` and `BAMLH0A0HYM2` current to 09-08 while `DFII10`/`DGS10`
stop at **09-04** — a 4-day spread across series the engine mixes.

**Systemic — decomp interval vs scan date, all 6 gradeable days:** 08-24 uses
08-19→08-20 (4d) · 08-25 uses 08-20→08-21 (4d) · 08-26 uses 08-21→08-24 (2d) ·
08-27 uses 08-24→08-25 (2d) · **09-08 uses 09-02→09-03 (5d)** · 09-09 uses
09-03→09-04 (5d).

**Why this is not gated:** same family as **D6** — a component justified in a
comment by an assumed freshness that no code enforces. D6/D7 precedent is that
defects are fixed on discovery. **No new data point is needed:** `series()`
already returns the observation `date`; `interpret()` never reads it.

*What to change (user's call, nothing edited):* render the observation date
instead of "today", and damp or zero a FRED item older than N business days.
**N is deliberately unspecified — that is calibration and needs its own
evidence.** Expected effect on 09-08: `real_yields +3` does not fire, bias lands
at +1 or −2 instead of +4, direction call goes from WRONG to neutral-or-correct.

**What was right and got outvoted:** the engine already held −6 of same-day,
tech-specific bearish evidence — `gamma −2` (price **84.8%** up the
29402.2–29602.2 wall band; it turned within 43pts), `vol −3` (VXN 21.68 **+8.2%**,
VXN/VIX 1.4), `structure −1` (below PD mid). All three correct, all outvoted by
last week's rates data.

## NOT proposed — new watch items opened 2026-09-08

**W1 — macro block weight.** `|macro| ≥ 5` on the **last 5 consecutive deduped scans**
(08-26 13:12 onward), and on 5 of 11 scans overall. Macro alone flipped the sign
of the bias on **2 of the 5 gradeable days**: 08-25 13:04
(bullish→neutral, directionally **right**) and 09-08 (bearish→bullish,
**wrong**). **1–1 is not evidence.** Watching: how often macro alone determines
the sign, and its hit rate when it does. **Do not touch `_W`.**

**W2 — `credit` scores a level, not a change.** `fred_probe.py:187` is
`signal = 1 if hyv < 3.0`, weighted 2. HY OAS has been below 3.0 on **every day
on record** (2.65% on 09-08) — a standing +2 to the bull side rather than a
signal. This is the "component is dead weight" test, but there is no session yet
where HY OAS was above 3.0 or widened >15bp/5d, so what it does when it *moves*
is unknown. Watching: the first such session.

**W3 — PD mid / PD close may be noise.** On 09-08 they were published at
**+3.1** and **−1.5** from spot. A level 2–3pts from price cannot be a reaction
point. One scan. Watching: distance-from-spot at publication, and reaction
grade, across 3+ scans before any cull is argued.

**W4 — level hit rate is not independent of the fuel budget.** `brief.py:359`
sizes the board by `budget * 1.75`, so an EXHAUSTED day publishes a narrow board
and scores a high hit rate almost by construction. 09-08: budget 26.2 → board
span **84.2pts**, post-scan traversal **146.6pts**, hit rate **1.00** (0.86 on
strict touches). **H6 should normalise hit rate by board span ÷ traversal**, or
it will read "levels are working" hardest on the days the board says least.

## Evidence appended to existing items

**M4 — third graded day, and its worst instance yet.** 3 of 7 published levels
were admitted by `TOUCH_TOL = 8.0` without price reaching them: **29614.9**
(`travel_up −0.8` — **never touched at all**, post-scan high 29614.1, yet graded
*"broke DOWN through it"*), 29574.9 (1.9 short), 29570.3 (6.5 short).

**For the first time the tolerance changed the VERDICT, not just the
timestamp.** Starting the 12-bar window at 15:40 instead of the true first touch
at 15:55 gives PD mid `travel_up 39.2` and PD close `43.8` → *"traded both sides
— chopped"*. From the true touch they are **16.5** and **21.1**, both under
`REJECT_PTS = 25` → *"broke DOWN through it"*. H6's headline result is *"chopped
is the dominant outcome"*; on this day **2 of its 3 chop verdicts are tolerance
artefacts**, and they mask clean downside breaks on a day that closed −82.6.
**The M4 decision should be made before H6 reaches 5 days.**

**H2 — the sample does not match the claim.** `track.py:208` selects on
`fuel_state in ("LOW_FUEL","EXHAUSTED")` only; H2's own text requires
`LOW_FUEL`/`EXHAUSTED`-**at-extreme**. Position within the range-so-far at scan,
for the 6 rows the tracker lists: **18%, 33%, 29%, 5%, 77%, 52%** (09-08 is the
52%). Only 08-24 13:45 (5%) qualifies. **H2 stands at 1 valid observation of 3,
not 6.** Same shape as M3/M4 — a statistic tallied off a filter that does not
implement the definition it is labelled with. **09-08 must NOT be counted toward
H2.** Recorded; not proposed.

**H1 — 5th point breaks the monotone run.** Per-day errors: +61.2, −11.6, −73.0,
−86.4, **−26.2** (mean −27.2). The four-point slope H1 refused to fit a
multiplier to is gone; the series now reads as noise around −27.2 rather than a
trend, which **strengthens** H1's existing "do not fit a multiplier" conclusion.
Caveat: the 09-08 point is **low-information** — a NY_MIDDAY scan at 92.8% ADR
with both extremes already in can only score near-zero extension. Fuel was in
fact the model's best call of the day: budget 26.2, extension **exactly 0.0**.

**H4 — 5 of 5 days recorded, still weak.** Flip 29405.3, close 29496.0 →
**90.7pts**. Series: 1.1 / 236.6 / 255.2 / 599.8 / 90.7 — one hit, four misses.
Do not use the flip as a target.

**H12 — first live trading-day observation (1 of 5).** GEXBot volume lens
29,452–29,592; OI lens 28,992–29,267. Post-scan range **29,467.5–29,614.1**. The
volume band bracketed the actual range to within **16–22pts**; the **OI band sat
entirely outside the day**, ~200pts below the session low. Our own CBOE call
wall (29,602.2) agreed with the volume lens to 10pts and marked the post-scan
high. One session, graded post-hoc, with the OI book mid-roll — **it proves
nothing**. Count 1 of 5.

**D7's open question — second instance, one day EARLIER than D7 itself.** On
09-08 `keep()`'s `budget * 1.75` cap was **45.8pts** against a 26.2pt EXHAUSTED
budget, so the board was a ±46pt window while the day's range was **339.3**.
**PUT WALL 29402.2, MAX PAIN 29427.2 and GAMMA FLIP 29405.3 were all dropped.**
The session low was **29394.8 — 7.4pts below the put wall, 10.5pts below the
flip** — and the 177pt bounce that carried price up to the scan started there.
The brief's own text called 29402.2 *"dealers are SHORT gamma here… price
accelerates THROUGH rather than stall. **Not a floor**"*. It was the floor. Not
forward-gradeable (the low was pre-scan), and D7's footnote fix landed 09-09, so
this is evidence for the **open question** — should a wall be subject to a
range-budget filter at all — not for the fix.

## One more thing worth recording: the prose contradicted the score, and the prose won

§3 of the 09-08 brief said *"The day's range is set… Fading the extremes back
into the range is the higher-probability side here, **even when the gamma regime
favours continuation**."* That was exactly right — extension 0.0, and the
post-scan high at 29614.1 was faded 147pts. The headline said **MILDLY
BULLISH**. Two outputs of the same document disagreed, neither acknowledged the
other, and a reader following the headline lost while a reader following the
fuel paragraph won. Not a hypothesis and not proposed — but if it recurs twice
more it should be written up as one.

## P1 — the heaviest macro term is fed by the stalest series, by construction

Raised by the 2026-09-08 review; the structural half verified independently
2026-09-09.

**The day.** 08-09 scored `+4 MILDLY BULLISH`; the session closed **-82.6**.
Component split: `gamma +2, vol -3, rates 0, macro +6, breadth +1, fuel 0,
structure -1, news -1`. **Strip macro and the score is -2 — the correct sign.**
Macro alone flipped it, and -6 of correct same-day evidence (price 84.8% up the
wall band, VXN +8.2%, below PD mid) was outvoted by it.

**Where the +6 came from.** `real_yields` contributed +3 — the heaviest single
term in the engine — off DFII10 reading "down 3bp **today**". DFII10's latest
observation available that day was **2026-09-03**, three business days old.

**Verified live on 2026-09-09**, independently of the review: DFII10's latest
observation is `2026-09-04`, three business days stale, and the rendered line
said "up 1bp **today**". The `date` field is present in the payload and gated
nothing.

**The structural fault.** `fred_probe.aligned_change()` exists precisely to stop
this — its own docstring says *"FRED series publish on different lags"*. It is
used at `fred_probe.py:164` by `yield_decomp`, **weight 1**. `real_yields`,
**weight 3**, takes DFII10's raw `chg_1` at `fred_probe.py:145`. And
`bias_engine.py:130-131` justifies the macro weights with *"FRED publishes with
a 1-2 day lag"* — a constraint asserted in a comment with nothing enforcing it.

**Same family as D6**, one day apart: a rule stated in prose rather than code.
D6 was a guard against a proxy; this is a guard that was never written at all.

**Done now (correctness, not calibration):** the line no longer says "today"
about an older observation. It prints the observation date, warns when FRED has
not published in more than one business day, and carries `obs_date` and
`obs_age_business_days` in the payload. This makes the staleness visible on
every scan.

**NOT done, and deliberately: a stale reading still VOTES at full weight.**
Whether it should — decay the weight, gate the signal past N business days, or
route `real_yields` through `aligned_change()` like `yield_decomp` — is
calibration and belongs behind the evidence gate. One day is one day, however
cleanly the arithmetic reads. **The user's call.**

## Additional evidence on M4, from the 2026-09-08 review

**First case where the touch tolerance changed a VERDICT, not just a label.**
29,614.9 was never touched — the post-scan high was 29,614.1 — yet it graded
*"broke DOWN through it"* off `travel_up -0.8`. Separately, starting the window
at 15:40 instead of the true 15:55 touch turned PD mid / PD close from
`travel_up 16.5 / 21.1` ("broke DOWN") into `39.2 / 43.8` ("chopped").

**H6's headline result is "chop is dominant". Two of this day's three chop
verdicts are artefacts of the tolerance**, and they masked clean downside breaks
on a -82.6 day. **The M4 decision needs making before H6 reaches 5 days**, or
the hypothesis gets settled by its instrument rather than by the market.

## H2's sample does not implement H2's definition

`track.py:208` filters on **fuel state alone**; H2 is defined as *at-extreme*
fading. Position-in-range for its six listed rows: 18%, 33%, 29%, **5%**, 77%,
52% — only one qualifies. **H2 is at 1 of 3, not 6**, and 2026-09-08 should not
count toward it. Recorded, not fixed: changing the filter changes the sample.

## The 7/7 level hit rate is close to tautological

`keep()` sizes the board by `budget * 1.75`, so 08-09's 26.2pt budget produced a
±46pt board inside a 147pt traversal — levels that near price are almost
guaranteed to be touched. Strict-touch scoring gives **6/7 (0.86)**, not 1.00.

Meanwhile the same filter dropped the put wall, max pain and the flip — and the
session low (29,394.8) landed **7.4pts below the put wall and 10.5 below the
flip**, which is where the 177pt bounce began. **This is a second instance of
D7's open question, observed the day before D7 was found.** Two instances, not
three. Still observing.

---

# Retrospective 2026-09-09: the gamma engine against 12 days of price

Ran on request. Method: `fetch_ohlcv_paged` 16 days of M5 (3,263 bars, 08-25 to
09-09), every post-fix ladder graded against the next trading day, and each
published flip/strategy cross-tabbed against what the day actually did.

**Ladders EXCLUDED as invalid, per H11's withdrawal:** `2026-08-26-2212` and
`2026-08-27-1323`, both `pre_fix: True` (45-day book, before the book-mismatch
and wall-dominance fixes). The first draft of this retrospective used both and
had to be thrown away — the same error H11 already records. Valid pairs:
`08-27-1358 -> 08-27` (clipped to post-publication bars), `08-27-2233 -> 08-28`,
`09-08-1539 -> 09-09`. 18 rungs.

## H11 — the ranked walls WORK, and the grader was hiding it

**9 of 18 rungs were touched. Of the 8 with a settled read, 7 HELD.**

| rung | day | worst excursion | held for | re-tests | settled verdict |
|---|---|---|---|---|---|
| C3 29,602 | 09-09 | **+0.8** | 870 min | 2 | HELD as resistance |
| C2 29,414 | 08-27 | +1.6 | 540 min | 1 | HELD as support |
| C1 29,464 | 08-27 | **-4.7** | 430 min | 2 | HELD as support |
| C3 29,514 | 08-27 | -11.2 | 240 min | 2 | HELD as support |
| C1 29,495 | 08-28 | +12.6 | 280 min | 1 | HELD as resistance |
| C3 29,645 | 08-28 | +14.9 | 315 min | 1 | HELD as resistance |
| P1 29,352 | 09-09 | -18.2 | 325 min | 1 | HELD as support |
| P2 29,402 | 09-09 | -30.4 | 260 min | 8 | **LOST** |

**The same 8 rungs under the shipped first-touch grader: FOUR "chopped", TWO
"broke DOWN", ONE "broke UP", ZERO recorded as holding.**

**0 of 8 versus 7 of 8, on identical data.** This is no longer an argument about
M4 — it is a measurement. Two cases carry it on their own:

- **C3 29,602 on 09-09.** First touch at 02:40 says *"broke DOWN, 79pts"*. The
  settled read: worst excursion **0.8 points**, held **870 minutes**, re-tested
  twice and rejected both times. That is close to a perfect ceiling and the tool
  called it broken.
- **C1 29,464 on 08-27.** Worst excursion **-4.7pts** over 430 minutes. This is
  the level the trader described as *"swept through and reversed back above it
  soon after and never broke through again and worked as support"* — his reading
  reproduced to the point. The tool said CHOP.

**H6's headline finding ("chop is dominant") is an artefact of its instrument.**
Under the settled read, chop is not dominant; holding is, 7 to 1.

### The put ladder is the half that does not work

Split by side, the picture is completely different:

| | rungs | touched | held |
|---|---|---|---|
| Calls (C1-C3) | 9 | 6 | **6 of 6** |
| Puts (P1-P3) | 9 | **2** | 1 of 2 |

Six of nine put rungs were **never reached** — 08-27's P1 sat 331pts below spot
and P2 631pts below; 08-28's P1 was 479pts below. **The put side is ranked by
gamma force with no proximity filter and lands outside any tradeable distance.**
That is precisely H11's original claim, now with valid evidence behind it, and it
is a *side-specific* failure rather than the whole-ladder failure the withdrawn
observation asserted.

The one put failure is also the one rung with **8 re-tests** — repeated tapping
looks like distribution rather than defence, and may be a usable tell. One
instance; noted, not proposed.

**Count: 3 valid ladder-days.** The 5-day threshold is not met. Nothing changes.

## H7 — the overnight flip is worse than unreliable; it inverts the strategy

Strategy recommendation against what each day actually paid (day shape = where
price closed in its range; >=75% or <=25% means the move RAN and Strategy 2 was
right; 35-65% means it FAILED BACK and Strategy 1 was right):

| day | shape | close@ | scans -> strategy |
|---|---|---|---|
| 08-25 | FAILED BACK (S1) | 50% | 13:04 **S1 ✓** · 21:56 S2 ✗ |
| 08-26 | RAN (S2) | 99% | 13:12 **S2 ✓** · 13:14 **S2 ✓** · 21:43 S1 ✗ · 22:11 S1 ✗ |
| 08-27 | mixed | 65% | 13:23 S1 ~ |
| 09-08 | RAN (S2) | 23% | 15:39 S1 ✗ |
| 09-09 | FAILED BACK (S1) | 40% | 15:20 **S1 ✓** |

**Overall 4 right / 4 wrong — the same coin flip as the direction call. But it
separates cleanly by session:**

- **In-session scans (PRE_NY, NY_MIDDAY): 4 right, 1 wrong, 1 mixed.**
- **OVERNIGHT scans: 0 right, 3 wrong.**

Every overnight scan called the wrong strategy, and did so by naming the wrong
regime. The mechanism is measurable in the published numbers:

| day | flip range across the day's scans | price moved | regime label |
|---|---|---|---|
| 08-24 | **389.1pts** over 8 scans | 258.7 | ABOVE *and* BELOW — **contradicted itself** |
| 08-25 | 294.7pts over 2 scans | 201.6 | ABOVE *and* BELOW — **contradicted itself** |
| 08-26 | 299.6pts over 4 scans | 153.2 | ABOVE *and* BELOW — **contradicted itself** |

On 08-24 the flip moved **389 points while price moved 259** — the flip is more
volatile than the thing it is measuring. Two scans **two minutes apart** (08:28
and 08:30, price 9pts apart) published flips 192pts apart and *opposite* regime
labels, which means opposite strategies.

**This is 3 of 3 on the overnight sub-claim and 3 of 3 on self-contradiction —
the threshold is met and the evidence points one way.** It is now the
best-supported finding in this register. Reading it, not acting on it, per the
rule: a proposal belongs in its own entry with a stated mechanism, and the
obvious candidate (suppress the regime label and the strategy recommendation on
OVERNIGHT scans, keep the levels) needs writing up as one rather than being
slipped in through a retrospective.

**What this does NOT say.** The direction call from overnight scans was 2 right /
1 wrong — it is specifically the *flip*, and therefore the strategy selection,
that overnight gets wrong. Do not generalise it into "overnight scans are
useless".

---

# Decisions taken 2026-09-09 (trader's call, three of them)

## 1. The settled read is now the OFFICIAL verdict, and history is re-graded

`review_day.grade_level` now takes its verdict from `settled_read()`; the
first-touch rule is retained as `_first_touch()` and reported on every level as
`first_touch_reaction`, so nothing is quietly overwritten. `role_reversal()` in
`gex_retro.py` delegates to it — **one implementation, one grader**, which is
what the invariant always claimed.

### The re-grade, 7 trading days, 122 levels price actually reached

| outcome | NEW (settled) | OLD (first touch) |
|---|---|---|
| respected / held | **75** | 8 |
| chopped | **0** | 70 |
| broke | 21 | 44 |
| unsettled (no read) | 26 | 0 |
| untouched | 45 | 45 |

**Held: 61% under the new grader, 7% under the old. 112 verdicts changed.**

### Read this before quoting the reversal

**"Chop went from 70 to 0" is NOT evidence that chop was disproved.** The
settled read has no chop category *by construction* — it asks which side price
settled on and measures the worst excursion from there, so "traded both sides"
cannot be an answer it gives. The honest comparison is narrower and still
decisive: of the levels the old grader called broken or chopped, the settled read
finds most were **poked and then respected**, with worst excursions in the
4–15pt range. Examples from 08-24 alone: `Asia Low + CALL WALL 29,200.6` broke →
held, worst **7.0pts**; `London High + PDL 29,136.4` broke → held, worst
**12.4pts**; `MAX PAIN 29,099.3` broke → held, worst **11.8pts**.

**The new grader also abstains more: 26 of 122 are "unsettled"** — touched, but
price never held one side long enough to judge. That is a real cost of the
change. It shrinks the judged sample in exchange for not manufacturing verdicts
out of near-misses. `classify()` maps it to its own bucket and **never to
"broke"**, because counting an absent verdict as a failure is exactly how the
old instrument produced 44 breaks.

**It did not flatter everything.** `PUT WALL 28,999.3` on 08-24 went
chopped → **broke**, worst excursion **−34.2pts**. The settled read is harder on
genuine failures, not softer.

**H6 must be re-read from scratch.** Its recorded finding ("chop is dominant,
hit rate 0.56") was produced by the superseded instrument and no longer stands.
It is not replaced by "levels held 61%" either — that is one re-grade of 7 days,
not 5 fresh sessions under the new rule.

## 2. 2026-08-28 counts as an observation

`test_artefact` set to `false`, `artefact_reason:
counted_by_decision_2026-09-09`. It was a genuine forecast on a real trading day
off live data. The 2026-08-27 exclusion stands and is a different thing — one
market state journalled five times.

**Effect, and it went the unflattering way, as expected:** `track.py` moves from
5 trading days / 11 scans to **7 / 13** (09-09 also completed), and the direction
record from **4 right / 4 wrong** to **4 right / 5 wrong**. Excluding it had been
flattering the model. H1 per-day is now **−30.1pts over 7 days, negative on 6 of
7** — the strongest signal in the register and stronger for the extra day.

## 3. Overnight scans no longer name a regime or pick a strategy

Implemented in `brief.py`. On an `OVERNIGHT` window the strategy line is
replaced with an explicit refusal, the section-2 regime prose is replaced with a
warning, and the withheld pick is preserved as `strategy_call_withheld` for the
record. Verified live on the 2026-09-09 22:08 BST build, which is an overnight
scan and rendered both.

**Deliberately NOT changed:**

- **The direction call.** Overnight direction was 2 right / 1 wrong. This is a
  finding about the *flip*, not about overnight scans in general.
- **The levels, walls, max pain and fuel.** All still published — they come from
  strike data, not from the flip's position relative to spot.
- **The `gamma` bias components**, which still vote off the same unstable flip
  (`above flip by Npts` was +2 on the 09-09 build). That is an inconsistency and
  it is recorded as one: suppressing the label while the number still votes is
  half a fix. It is left alone because changing a scoring weight is calibration
  and there is no evidence for a specific replacement — the flip's *instability*
  is measured, the right weight for it is not. **Next open question.**

## 4. M3 fixed — no decision needed, it was a bug

`review_day.latest_unreviewed()` now filters `test_artefact` as well as
`is_trading_day`, matching `review_day():75` and `track.py:82`. It had returned a
day that `review()` then refused with `"error"` instead of the `"skipped"` shape
built for it. Listing this as a decision for the trader was a mistake on my part.

## 5. The consistency test that would have caught the wrong thing

`test_consistency.py`'s "role_reversal ignores levels price never reached" check
was a **grep of `gex_retro.py`'s source text**. When the implementation moved to
`review_day.py`, the string vanished and the check failed — but had the move gone
the other way it would have kept passing against a file that no longer held the
logic. Replaced with four behavioural checks that call the functions: the
untested-level guard, a level that was reached, that the verdict comes from the
settled read, that the first-touch verdict is still reported, and that
`unsettled` is not classified as a break. 20 checks, all passing.

This is the same lesson as D6 and P1 in a third costume: **a rule asserted about
code is not a rule enforced on code.**

## 3b. The gamma weight, made consistent (2026-09-09, same evening)

The half-fix above is closed. `bias_engine.score()` takes a `session` argument
and, on `OVERNIGHT`, **withholds the flip-derived votes** — the `+2 above flip /
-3 below flip` pair and the `+1 straddling` rider. It emits an explicit `+0` row
saying so, rather than silently omitting them, so the scoring table shows the
withholding instead of hiding it.

**This introduced no new calibration number.** It applies the rule already in
force for the regime label to the same input. The alternative — decaying the
weight — would have required inventing a figure the evidence does not supply:
the flip's *instability* is measured, the correct discounted weight for it is
not.

**Only the flip-derived votes are withheld.** The net-GEX vote reads the option
book and the wall-band vote reads the strikes; neither depends on the flip's
position relative to spot, and nothing measured says either is unstable
overnight. They still count.

Verified on the live 22:18 BST overnight build: gamma went **-5 to -2**, headline
**BEARISH (-7) to MILDLY BEARISH (-4)**, with the withheld row visible in the
breakdown and the book/wall rows untouched. The direction call still stands on
its own evidence (overnight direction was 2 right / 1 wrong).

**The invariant is now enforced, not just intended.** Three checks in
`test_consistency.py` assert the flip contributes 0 overnight, non-zero
in-session, and that non-flip gamma rows survive the suppression. The two
suppressions shipped a commit apart and the gap was worth -5 points on a live
brief; a test is the only thing that stops them drifting apart again. The stub
is a minimal REAL payload rather than an auto-filling mock, deliberately: if
`bias_engine` grows a required field this test should fail loudly rather than
pass against a fiction.

**Still open, and not addressed by this:** whether the flip should carry its
current in-session weight at all. In-session strategy selection was 4 right / 1
wrong / 1 mixed, so there is no evidence against it — but that is 6 observations.
Nothing proposed.

---

# Defects found in the 2026-09-10 08:11Z scan (recorded, NOT fixed mid-scan)

Neither was fixed on the spot, deliberately: re-running `brief.py` to ship a fix
would journal the same market state twice, which is the inflation problem the
`artefact_reason` split exists to prevent. Recorded now, fixed on the next code
pass.

## D8 — "Straddling the flip" is printed when price is not straddling the flip

Today's brief published **"Straddling the flip — reduce size and let the regime
resolve"** with price 29,419.5 and flip 29,371.5 — **48pts apart, 0.163%**. The
engine's own straddle threshold is **0.15%**, so by its own definition this is
not a straddle, and the scoring table agrees: it printed
`+2 above flip 29371.5 by 48.0pts` with **no** straddling rider.

The cause is the strategy selector's `else` branch at `bias_engine.py:249`:

```
if   gf and px > gf and (net or 0) > 0:   -> Strategy 1
elif gf and px < gf:                      -> Strategy 2
else:                                     -> "Straddling the flip"
```

Price above the flip with `net <= 0` satisfies neither arm, so it lands in a
catch-all that names a condition it did not test. Today `net = -0.058`.

**The advice is defensible; the stated reason is false.** "Above the flip but the
week's book is net short gamma" is a genuine conflict and reducing size is
reasonable — but a trader who checks the distance, sees 48pts, and finds no
straddle has been given a wrong reason, which costs more trust than saying
nothing. This is the same failure mode as the FRED line saying "today" about a
three-day-old print.

**Fix when next touching the file:** name the real state — flip and book
disagreeing — and reserve the straddle wording for the case that actually meets
the 0.15% test.

## D9 — the news tagger reads a keyword without its subject

`"US stocks fall as oil prices jump above $100 a barrel"` was tagged **`risk_on`**.
The `risk_on` pattern at `news_scorer.py:109` matches `\bjump\b`; the thing
jumping is **oil**, and the sentence's actual subject is **US stocks falling**.
Oil through $100 is risk-off and inflationary — the exact opposite of the tag,
and doubly wrong on a PPI morning.

**No damage today**: it fell into NEEDS_JUDGEMENT and never scored, so the +0 in
the table is correct. The tag was still backwards, and the pre-filter is the
thing that decides what a future scorer might auto-score.

**Scope, stated honestly:** this is one instance of the general problem the
NEEDS_JUDGEMENT queue exists for — keyword matching without a subject. It is not
a case for more regex. Recorded so that if it recurs it can be counted rather
than rediscovered.

## What WORKED on this scan, recorded because near-misses should be too

- **D6's guard chain behaved correctly on the pre-market path.** NDX cash was
  717 min stale (it does not print outside US hours), the `nq_implied` fallback
  rolled it forward by the NQ move to 29,422.3, greeks were repriced at current
  spot, and the offset came out at **-2.8**. The value cross-check did not fire
  because it had no live cash print to disagree with — which is the designed
  behaviour, not a gap.
- **P1's staleness warning fired and cost the score nothing it should not have.**
  DFII10 is 2 business days old, the line said so, and `real_yields` contributed
  **+0** rather than the +3 that flipped 08 Sep.
- **The GEXBot offset was matched to feed time** (-12.3 at 2026-09-09 20:00Z)
  rather than taken against the live price, and the 732-minute feed age is
  stated at the top of the section.

---

## D10 — the scheduled scan had no repository, and the Routine called it a success

**2026-09-10 12:45:40Z.** The first scheduled run fired, ran for **85 seconds**,
and produced nothing. No journal entry for 12:45 exists; today's only entry is
the manual 08:12Z scan.

**Cause, confirmed by comparing the two session records rather than inferred:**

| | `sources` |
|---|---|
| This (interactive) session | `[{git_repository: {url: .../CTrader-Bots, revision: refs/heads/main}}]` |
| The Routine's fired session | **`[]`** |

A scheduled session starts with **no repository cloned**. The prompt's step 1 was
`git -C /home/user/CTrader-Bots pull` against a path that did not exist, so the
run died on its first command and every later step was unreachable.

**`create_trigger` has no `sources` parameter** — only `create_session` does. So
the Routine could not have been given the checkout at creation time through the
tool that made it. The `mcp_connections: []` warning at creation was visible and
I read it as connectors-only; the empty `sources` beside it was the real problem
and I did not check it.

### The part that matters more than the bug

**`last_run.status` was `ROUTINE_RUN_STATUS_SUCCEEDED`.** The scheduler reports
success when the session *fires and exits*, regardless of whether the work
happened. A push notification went out saying it ran.

Left alone, this fails **silently every weekday**: the trigger reports green, the
notification arrives, and no observation accumulates — while the whole point of
the automation is observation count. It would have been discovered weeks later by
noticing the register had not grown, which is the same shape as D3 (a day graded
as complete when it was not) and D1 (a range read as used when the session had
not started). **A green status is not evidence of work.**

### Fix

The prompt now opens with a **Step 0** that tests for
`scripts/brief.py`, and if it is absent calls `add_repo` (owner
`PravinderSamra`, repo `CTrader-Bots`, **access `push`** — a read-only clone
would lose the journal commit, which is the observation), clones, and calls
`register_repo_root`. If `add_repo` refuses it must STOP and relay the refusal
verbatim rather than improvising.

**Verified by a manual test fire rather than by reasoning**, because the previous
failure came from assuming an environment behaved a certain way. The test fire is
instructed to state as its first line whether the repo was already present or had
to be cloned.

### Monitoring gap left open, deliberately

Nothing yet checks that a scheduled run actually *journalled* anything. The
honest check is not the trigger's status but the artefact: **does
`journal/<today>/` contain an entry near 12:45Z?** Worth adding to `track.py` as
a "scheduled run missing" line, so a silent no-op announces itself. Not built
today — one instance, and the fix above may make it moot. Recorded so it is not
rediscovered.

## D7 instance 3 — the level board emptied itself on the day it mattered most

**2026-09-10 15:06Z.** Range 463.9 = **132.8% of ADR**, `EXHAUSTED`, remaining
budget **0.0**. `keep()` sizes the board by `budget * 1.75`, so the cap was
**zero** and every non-structural level was pushed to the footnote. The board
shipped **two rows**, both 45-day structural walls (+78 and -472).

Sent to the footnote and labelled *"context only, don't mark"*:

- **PUT WALL ●●●●● 0.69bn at 29,194 — 22 points below spot.**
- GAMMA FLIP 29,339 (+122), the level deciding the strategy the brief recommends.
- MAX PAIN 29,444, CALL WALL 29,494, PDH, PWH.

The strongest put wall on the week's chain, 22pts from price, on a day the brief
calls STRONGLY BEARISH in short gamma — filtered off the board as unreachable,
because a range-budget rule was applied to a dealer-hedging boundary.

**D7's fix is why they were visible at all.** Before it they would have vanished
from board and footnote together. The fix works; the underlying rule is still
wrong.

**Third instance, so the 3-day threshold is MET:**

| date | dropped | consequence |
|---|---|---|
| 09-08 | put wall, max pain, flip | session low landed **7.4pts below the put wall**, where the 177pt bounce began |
| 09-09 | call wall (+140 vs a 112 cap) | put wall survived by **2pts**; the asymmetry tracked where price sat, nothing about the walls |
| 09-10 | **everything except two structural walls** | budget 0 -> cap 0 |

**The mechanism, stated plainly:** the range budget forecasts how far the day's
RANGE can still grow. A wall is a price at which dealers must hedge. These are
unrelated quantities. An exhausted budget says nothing about whether price will
*reach* a level — H1 shows the budget over-forecasts extension on 6 of 7 days,
and today price travelled 463.9pts on a day that opened with 206pts of budget.
Filtering walls by it is a category error, and it fails hardest exactly when the
day is most volatile, because that is when the budget is most exhausted.

**Proposal (threshold met, NOT yet applied):** exempt `CALL WALL`, `PUT WALL`,
`GAMMA FLIP` and `MAX PAIN` from the budget filter the way `structural` already
is, and keep the `_(stretch)_` tag to mark distance. Session extremes and PD/PW
levels keep the budget rule — those ARE reachability claims, so the rule fits
them. This changes what gets marked, so it is the trader's call.
---

## D11 — the scan ran, wrote the journal, and pushed nothing

**2026-09-10, found while diagnosing why a scheduled run did minutes of work and
left no commit.** The scan itself was never the problem. `sync_archive.py`'s
`PATHS` list carried three archive directories:

```
journal/ · research/chart-ladders/ · research/live-walls/
```

but every scan also writes **`research/gexbot/ladders/<stamp>-oi.json`** and
`-vol.json`, and that directory **is tracked in git** (22 files at the time).
It was simply absent from the list. So each scan left two tracked-directory
files permanently unstaged.

That alone loses data quietly. The second-order effect lost the whole scan:

1. The scan commits the journal, pushes, and loses the race — `main` takes
   commits from `xauusd-data-bot` and `GEX Agent Bot` on their own schedules, so
   losing a push race is the **normal** case on this branch, not an error case.
2. The recovery was `git rebase origin/main`, which refuses outright when
   untracked files in the tree would be overwritten by the incoming commits.
   The stale gexbot ladders were exactly those files.
3. `rebase --abort` ran, `sync()` returned `pushed=False`, and the observation
   stayed in a container that was about to be reclaimed.

**The reporting made it invisible.** A failed push printed as `pushed=False` at
the tail of an otherwise successful-looking `archive: N file(s) committed` line.
Nothing shouted. Same shape as D10: *the run looked like it worked.*

Worse, `sync()` reported `pushed=True` **whenever the push command returned 0**,
which is not the same claim. Observed on this date: a scan pushed successfully,
a later `rebase --abort` rewound the local branch off the commit it had just
pushed, and the local repo then disagreed with origin in both directions with no
warning.

### Fix

- `research/gexbot/ladders` added to `PATHS`. Writing a path the archive does not
  carry is the same defect as not writing it.
- Rebase recovery uses `--autostash`, and a conflict now retries instead of
  giving up on the first one — a conflict is usually a concurrent scan touching
  `index.json`, and the next attempt re-fetches a settled origin. Only a
  conflict surviving every attempt is real.
- **`pushed` is no longer inferred from the push command's exit code.** After the
  loop, `sync()` fetches and asks whether `origin/<branch>` actually contains
  `HEAD`. It reports that, and nothing else.
- `brief.py` prints `ARCHIVE NOT PUSHED … This scan is lost unless you push it by
  hand` on its own line when the commit did not land.

### Also fixed alongside

**`brief.py` ignored unknown arguments.** `brief.py --help` did not print help —
it ran a full scan and recorded a journal entry, and so did any typo of
`--no-journal`. Found by doing exactly that while diagnosing this. A flag the
program does not understand must never fall through into recording an
observation; unknown options now exit 2 before any network call.

**Three files pinned paths to `/home/user/CTrader-Bots`** (`wall_retro.py`
absolutely; `levels_fuel.py` and `review_day.py` via `~/CTrader-Bots`). A
scheduled session's checkout is named by `add_repo`, which returns the
**lower-cased** `/home/user/ctrader-bots` and instructs cloning there — so a
session that follows its instruction literally lands somewhere none of those
paths exist. All three now derive from `__file__`.

---

## D12 — the brief and the chart disagree about the put wall by ~200pts

**Root cause found, fixed and verified 2026-09-10. Applied on the owner's
decision after the A/B below; the 3-day rule was waived deliberately because
this is not a model preference — it is one board carrying two sets of greeks.**

The two are meant to be one computation delivered as two files. The flip agrees
exactly, build after build. The put wall disagreed on roughly two builds in
three, always with the brief **above** the chart, always by a clean multiple of
the 50pt bin.

### The cause: two different sets of greeks on one board

Both paths bin identically (`bin_pts=50` in each). Both use the same formula.
They differ in **one argument**:

| | call |
|---|---|
| `gex_chart.collect()` | `gl.bucket(rows, S_ndx, dte_max, bin_pts=50, reprice=True)` |
| `gex_levels.build()`  | `bucket(rows, S_ndx, dte, reprice=stale)` |

`reprice=True` recomputes gamma with Black-Scholes at the **current** spot.
`reprice=False` trusts **CBOE's published greeks**, which carry the timestamp of
the last chain recompute. So on any day the cash quote is not stale — that is,
on a normal live session — the brief selects its walls from published greeks
while the chart reprices.

**And `gamma_flip()` reprices unconditionally.** It has no `reprice` parameter
and always calls `bs_gamma`. So the brief prints a **repriced flip beside
published-greek walls**: two numbers on one board, computed at two different
spots. That is precisely the mixing `bucket()`'s own docstring was written about
— *"the figure was being printed beside a flip that WAS repriced."* The fix was
generalised to net GEX and to the chart, and this call was left conditional.

`reprice=stale` also guards the wrong clock. `_cash_is_stale()` ages the **cash
quote** (30-minute threshold); it says nothing about when CBOE last recomputed
the **greeks**. Measured mid-session on 2026-09-10 with `stale=False` and
`basis.greeks = cboe_published`:

```
current NDX spot            29132.2
spot stamped on CBOE greeks 29161.6   (n=1501 contracts)
drift                          -29.4 pts
```

A fresh cash quote, and greeks 29pts out of date.

### Why 29pts moves a wall 200pts

Published greeks put the gamma peak at the spot CBOE last used, inflating the
strike nearest *that* spot. It turns wall selection into a near-tie, and the tie
lands differently as the drift changes:

```
published greeks (what the brief uses)   repriced BS (what the chart uses)
  NDX 29000   0.858bn   <- winner          NDX 29000   1.008bn   <- winner
  NDX 29100   0.764bn                      NDX 29100   0.547bn
  margin over 2nd: 0.094bn                 margin over 2nd: 0.461bn
```

The brief decides its put wall by a **0.094bn** margin; the chart by **0.461bn**,
five times wider. A near-tie decided by stale greeks is why the answer moved
between builds while the chart's stayed put, and why the loser was always the
bin nearer spot — that is the one published greeks over-weight.

### A/B, same market, minutes apart

`bucket(rows, S_ndx, dte, reprice=stale)` -> `reprice=True`, one line:

| | run 1 | run 2 | run 3 |
|---|---|---|---|
| `reprice=stale` (current) | FAIL 28951 vs 29101.3 | FAIL 28925 vs 29125.2 | FAIL 28939 vs 29039.2 |
| `reprice=True` (proposed) | PASS 31/31 | PASS 31/31 | PASS 31/31 |

Six consecutive builds on the same live chain. The change also makes `build()`
consistent with `gamma_flip()`, which already reprices unconditionally, and with
`gex_chart`, which already passes `reprice=True`.

### Applied

`gex_levels.build()` now passes `reprice=True` unconditionally. Verified over
three further builds after the change: 31/31 each time.

`basis["greeks"]` was conditional on the same `stale` flag and had to go with it
— left alone it would have printed `cboe_published` over repriced walls, which is
the same defect as D12 itself: a label describing a computation that no longer
happens. It is now unconditionally `repriced_bs_at_current_spot`, which is what
every number on the board is.

**What changed in the output.** Put walls move, typically to a bin 100-200pts
below where the brief used to put them — the bin the chart has been drawing all
along. Nothing else on the board is touched: `keep()`, the scoring, the wall
ranks and the grader are all unchanged. The flip does not move, because it was
always repriced.

**Worth grading over the coming days:** whether price respects the repriced wall
better than the published-greek one did. The argument for it is internal
consistency, not a measured hit rate, and the two are not the same claim.

### An earlier version of this entry reasoned wrongly — corrected

It claimed the brief selected among **raw strikes** while the chart binned, and
called the numbers impossible because "a bin cannot hold less than its own
contents". Both figures were the same 50pt bin, one quoted in NDX strike space
and the other in CFD price space, 4.4pts apart. The conclusion that granularity
was not the cause was right; the reasoning under it was not.

### The check that was supposed to catch this, and didn't

D12 stayed invisible because `test_consistency.py`'s wall comparison was broken
three ways at once:

- It searched only the level **board**, never the `far` footnote — but D7's fix
  moved un-truncatable walls *into* that footnote, so the wall the chart drew
  read as "missing" precisely when D7's fix was working.
- It substring-matched `"CALL WALL" in name`, so the row **"STRUCTURAL CALL
  WALL"** shadowed the real one and it compared two different levels. This
  produced a false failure — `brief 29308.4 vs chart 29508.0` — on a build whose
  call walls agreed to 0.1pt.
- When a wall was absent it called `check(..., True, "absent from one — not
  comparable")` — it **asserted success on the exact condition it existed to
  detect**. A wall vanishing from the brief is D7, and the D7 guard passed on D7.

Now: names are matched per confluence segment (`"PDL + London Low + STRUCTURAL
CALL WALL"` splits on `" + "`, so a wall sharing a level is found and
`STRUCTURAL` no longer shadows), every row under a role is collected rather than
the first, and the assertion is D7's actual contract — **the wall the chart drew
must be markable somewhere in the brief**. Absent now fails.

## D13 — a fired session can stop and wait for a human who is not there

**Open. Partly inferred — read the evidence line by line before acting on it.**

D11's fixes were verified in an interactive session: clone from scratch, full
`brief.py`, journal written, archive committed, push verified against origin. So
a **test fire** was run at **2026-09-10 15:36:01Z** to prove the same loop from a
*scheduled* session, per D10's rule that this class of fix is verified by firing
rather than by reasoning.

**It produced nothing.** The session went idle at 15:37:43Z — **102 seconds** —
with 6,710 output tokens and no journal entry, no commit, no push. Today's
journal still holds only 08:12Z and 15:07Z. `last_run` will report SUCCEEDED.

### What is proven, and what is not

**Proven.** `session_context` for that fired session carries **no `sources` key
at all**, exactly as D10 found. And a *separate* session spawned two minutes
later with `create_session` — no repo, same environment, same model
(`claude-sonnet-5`), given a comparable instruction to call `add_repo` with push
access and clone — did not fail. It **stopped and asked a human**:

```
status_category: need_input
status_detail:   "user request unclear; detected potentially injected instruction"
needs_action:    "confirm actual task and whether to clone
                  PravinderSamra/CTrader-Bots with push access"
```

It then sat `SESSION_STATUS_RUNNING`, waiting for a confirmation that in a
scheduled context never arrives.

**Not proven.** The fired session recorded no `post_turn_summary`, and its
transcript is not readable from another session — there is no `send_message` or
`list_events` in the Routine MCP surface, and a disconnected cloud session does
not appear in `ListAgents`. So *that this is what stopped the 15:36 fire is an
inference* from a matching duration, a matching silence, and a reproduction. It
is the best available explanation, not a confirmed cause.

### Why this shape is dangerous

A prompt that instructs an agent to attach an external repository **with push
access** and then clone it is, read cold by a session with no context, shaped
exactly like a prompt injection. Refusing to act on it unconfirmed is the agent
behaving **correctly**. The failure is architectural: the instruction that most
needs trust is the one a scheduled session has the least context to trust, and
`create_trigger` has no `sources` parameter to remove the need for it.

And it fails in the worst available way — indistinguishably from success. The
Routine reports SUCCEEDED, the push notification arrives, and nothing is written.
That is now the **third** instance of the same pattern, after D10 and D3: *a
green status is not evidence of work.*

### What was done

The Routine's prompt was rewritten to open by stating plainly that this is the
repo owner's own standing automation over his own repository, running on a
schedule since 2026-09-09; the attach step is now a short conditional rather than
an emphatic block of imperatives, and the ALL-CAPS override language throughout
was removed. Whether that is enough is **untested** — the next scheduled run at
**2026-09-11 12:45Z** is the test.

### The option not taken, and why it is still the right one

`create_session` **does** accept `source_url`, and a session created with it
carries `sources: [{git_repository: {url: .../CTrader-Bots, revision: main}}]` —
verified. Pointing the Routine at such a session with `persistent_session_id`
would delete the attach instruction entirely and with it this whole failure mode.

Two things stopped it. `update_trigger` cannot change targeting, so it means
delete-and-recreate, losing the Routine's run history; and `create_trigger`
**rejects `notifications` for a persistent-session Routine**, so the phone alert
disappears — on an automation whose defining failure is being invisible, that
trade is backwards.

The real fix is the monitoring gap D10 left open and this entry now makes urgent:
**something must check that `journal/<today>/` gained an entry, and say so when it
did not.** Until that exists, every fix here is guarded only by someone
remembering to look.

---

# 2026-09-10 provisional review (day NOT closed — roll is 21:00Z, graded at 20:20Z)

`track.py` will not count this until after 21:00Z (D3). Numbers below are the
cash session plus the first 20 minutes after; the final hour of CFD trade could
still move the close. **Provisional.**

Session: O 29,437.9 · H 29,482.2 · L 29,018.3 · C 29,126.8 · **range 463.9
(132.8% of ADR14)**. Hot PPI; US10y +1.59% to 4.914%.

## Every put-side level that price reached HELD — and every one held as RESISTANCE

| level (from) | price | worst excursion | held | re-tests | role |
|---|---|---|---|---|---|
| PUT WALL ●●●○○ 3k (08:12) | 29,397.2 | **+6.4** | 680 min | 7 | resistance |
| GAMMA FLIP (08:12) | 29,371.5 | +24.5 | 620 min | 11 | resistance |
| PUT WALL ●●●●● 9.5k (15:07) | 29,194.4 | **+4.8** | 185 min | 3 | resistance |
| 2nd put concentration 18.5k (15:07) | 29,144.4 | +5.5 | 85 min | 8 | resistance |

Ranked ladder rungs agree: P1 29,397 (+6.6, 7 re-tests) and P3 29,197 (+2.2)
from the 08:12 ladder, P3 29,194 (+5.2, 3 re-tests) from the 15:07 ladder — all
**HELD as resistance**. Four named levels and three ranked rungs, **7 for 7**,
worst excursions of 2 to 25 points on a 464-point day.

**As levels, this is the best single-day result recorded.** As *labels*, the put
side was wrong every time.

## H14 (new) — the level board's wall notes are REGIME-BLIND, and the secondary table is not

The board printed, for both put walls: *"Heaviest floor this week — expect a
bounce and a good long-sweep here."* Neither floored anything. Price went
through both and each became the ceiling on every subsequent bounce. **A long
taken on that instruction at 29,397 would have sat through a 379-point
drawdown** to the 29,018 low.

The wording is fixed text attached to the PUT WALL row. It says the same thing
whether the book is long or short gamma.

**The secondary-walls table in the SAME brief got it right**, because its note is
generated from dominance and regime: for 29,194 and 29,144 it printed *"dealers
are SHORT gamma here, so they amplify: price tends to accelerate THROUGH rather
than stall. **Not a floor**"* — which is exactly what happened. On 2026-09-09,
with a net-long book, the same generator softened it to *"treat it as a
speed-bump rather than an accelerant."*

**So the brief contains both a regime-aware and a regime-blind description of the
same class of level, and the regime-blind one is the headline.** That is the same
family as D2 (put labels inverted) and D4 (a wall named for a side without
checking dominance) — naming a level by what it is called rather than by what the
book says it will do.

**Mechanism, and why it should be believed:** a put wall is put-dominant, so
dealers are short gamma there. Short gamma amplifies. In a downtrend it cannot be
a floor — it is the next ceiling once lost. The "bounce and long-sweep" reading
only fits a long-gamma book.

**Evidence: 1 session, 4 of 4 put-side levels.** Below the 3-day threshold.
Nothing changed. The candidate fix is to generate the board's wall note the way
the secondary table already does, from dominance and net regime, rather than from
fixed text — which needs no new calibration, only reuse of a generator that is
already correct in the same file.

## Fuel — the asymmetry held, and today was its sharpest test

| scan | state | budget | actual extension | error |
|---|---|---|---|---|
| 08:12Z | MODERATE | 206.2 | **320.8** | **+114.6** |
| 15:06Z | **EXHAUSTED** | 0.0 | **0.0** | **0.0** |

The EXHAUSTED read was **exact**. The MODERATE read under-forecast by 115pts on a
hot-PPI day — and note the sign: H1 is negative on 6 of 7 prior days (budget
over-forecasts), so a **+114.6** is a genuine outlier, not more of the same. A
news day is where the budget breaks, and it breaks in the direction that hurts a
fade.

This strengthens what was said to the trader on 2026-09-09: the **low** readings
are the reliable half. Three EXHAUSTED/LOW_FUEL observations now (08-25: 12.0 vs
0.4; 09-08: 26.2 vs 0.0; 09-10: 0.0 vs 0.0).

## Direction

| scan | call | move to close | verdict |
|---|---|---|---|
| 08:12Z | NEUTRAL / TWO-WAY (-1) | -279.8 | no call — no credit either way |
| 15:06Z | **STRONGLY BEARISH (-10)** | -72.7 | **CORRECT** |

The morning brief called nothing on a day that fell 280 points. Its *warning* was
right — it flagged the downside path as clear with nothing structural until
29,197, and price ran to 29,018 — but the score sat at -1 and the board's
strategy was Strategy 1 (fade), which was the wrong model for what followed. The
15:06 rebuild had the regime, the model and the direction right.

---

## ⚠️ H14's first statement was WRONG and is withdrawn

The 2026-09-10 review claimed *"the level board's wall notes are REGIME-BLIND,
and the secondary table is not"*. **That is false.** `brief.py` already carried a
correct short-gamma branch for the put wall — *"BUT today the desks are pushing
moves along — if it breaks, expect it to speed UP, not bounce. Don't buy the
break."* It simply was not taken, because at 08:12 price was 29,419.5 against a
flip of 29,371.5, so `long_gamma` was True and the confident branch was correct
*for the regime as the code computed it*.

I asserted an internal contradiction without reading the branch I was accusing.
Same failure as the withdrawn H11 observation: a conclusion stated before the
artefact behind it was checked.

## H14 restated — two definitions of "long gamma" in one document

The real inconsistency is narrower and does exist:

| | test used |
|---|---|
| `brief.py` level board | `px > flip` |
| `bias_engine.py` strategy selector | `px > flip` **AND** `net_gex > 0` |

On 2026-09-10 08:12 they disagreed. Price was **48pts above the flip** with week
net GEX at **-0.058**. The strategy selector's Strategy-1 arm failed its
`net > 0` condition and fell through; the board, needing only `px > flip`, told
the reader to *"expect a bounce and a good long-sweep"* at the put wall.

Neither put wall floored anything that day. Both became resistance. **A long at
29,397 on the board's instruction would have sat through a 379-point drawdown.**

**Fix (applied):** the board now uses the selector's test. Where they disagree
the state is named `conflicted`, and the put wall note reads *"the book is
CONFLICTED — price is above the flip while the week's net gamma is negative. Do
not treat this as a reliable floor: if it goes, it can accelerate. Wait for a
reaction rather than buying into it."*

**No new calibration.** One document, one definition — the stricter one, already
in use for the decision that matters most. Guarded by two consistency checks.

**What remains genuinely open, and is NOT settled by this:** whether a put wall
acts as resistance-after-break in short gamma as a *general* rule. That is 1
session, 4 of 4, and stays below the gate. Today's fix is about internal
consistency; the empirical claim still needs 2 more sessions.

## D7 applied — walls exempt from the range-budget filter

`CALL WALL`, `PUT WALL`, `GAMMA FLIP` and `MAX PAIN` now always reach the board,
tagged `_(stretch)_` by distance, exactly as `structural` already was. Session
extremes and PD/PW levels keep the budget rule, since those are genuine
reachability claims and the rule fits them.

Verified on a live post-close build: the board carries MAX PAIN at +652, the CALL
WALL at +602 and the GAMMA FLIP at +590, all correctly tagged. Before this they
would have been dropped and, on a six-item footnote, possibly truncated out
entirely.

The argument was already written down inside `secondary_walls()` — *"the budget
forecasts how much further the RANGE can grow; these are levels price can still
REACH inside the range, which is a different question and the one that matters
when fuel is exhausted but price is still travelling 250pts."* The board never
got it. Three instances to notice that the reasoning existed one function away.

## D13 resolved — the Routine fires into a bound runner that already has the repo

The clone instruction was the problem, so it was removed rather than reworded.

`session_01M7sro1DKMp5T7EBDusm6pM` was created with `source_url` set, so its
`sources` attach permanently. Trigger `trig_01ANoKamVDbvjvzpb1S5Dgza` fires into
it weekdays at 12:45Z; `trig_01SYwS3WnQJfHbSzVHWSFiuP` (fresh-session-per-fire)
is deleted.

**Readiness verified before rebinding**, per D10's rule that this class of fix is
proven by running it and not by reasoning: repo present, pull works, 29 checks
pass — **48 seconds, no clone, no injection refusal.**

**Why rewording was rejected.** D13's refusal was not a wording accident: an
instruction to call `add_repo` and clone a repository with push access is
injection-shaped, and no phrasing makes it less so. Removing the need for it is
the only fix that does not depend on a model's judgement call going the right way
every weekday.

**The cost, stated plainly.** The runner resumes one conversation daily, so its
context grows — which cuts against the trader's stated preference for fresh
sessions. Accepted deliberately in exchange for a scan that runs. Mitigation:
recreate the runner about monthly (new session with `source_url`, then delete and
recreate the trigger — `update_trigger` cannot repoint a bound trigger and cannot
edit its prompt from another session at all, which is itself worth knowing before
relying on being able to tune it later).

**Three ways this failed in one day, all reporting SUCCEEDED:** no repo (D10),
the archive not carrying every path it wrote so the observation died with the
container (D11), and the session stalling on an injection-shaped instruction
(D13). The common thread is the one already recorded against D10 — **a green
status is not evidence of work**, and the artefact on origin is the only check
that means anything.

**Not yet proven.** No scheduled run has produced an observation. 2026-09-11
12:45Z is the first test of the bound runner, and until one lands this is a fix
that has passed its readiness check and nothing more.

---

## H15 — `credit` is a constant, not a signal (22 of 22 observations)

**Opened 2026-09-11** from the 2026-09-10 final review. **Threshold met at 8
trading days.** Proposed as **P4**; the user decides.

**Claim.** `credit` has contributed **+2 on every scan ever recorded** — 22 of 22,
including the non-trading PREP runs. A term with one observed value is an offset,
not a signal, and it makes the engine's effective neutral point +2 rather than 0.

**Mechanism** (`fred_probe.py:220`):

```python
wide = (hy5 or 0) > 0.15
"signal": -2 if wide else (1 if hyv < 3.0 else 0)
```

The bear branch is a **change** test needing +15bp over 5 days. The bull branch is
a **level** test needing only HY OAS < 3.0. Observed across 8 graded days: level
**2.65–2.75%** (never near 3.0), 5-day change **+4, +3, −1, −5, −6, +2, +2, +5 bp**
(never within a third of +15). In a calm-credit regime only one branch can fire.

**The sibling term is the control.** `fin_conditions` in the same function scores
the *change* in NFCI and therefore printed **0** on 2026-09-10 while its prose
called the *level* a tailwind. One function, two conventions; the wrong one is on
the weight-2 term.

**Regraded across all 15 deduped scans** (signed score minus the credit
contribution, relabelled through `bias_engine.py:271`):

| | now | credit centred at 0 |
|---|---|---|
| CORRECT | 5 | **7** |
| WRONG | 5 | **3** |
| no call | 5 | 5 |

Changed: 08-24 09:37 and **09-10 08:12** no-call → CORRECT; 08-28 22:33 and
09-08 15:39 WRONG → no-call. **Zero correct calls broken.** 4 of 8 days improve,
0 degrade.

**On 2026-09-10 08:12 it was the whole difference.** Score −1; macro's only
positive content was credit +2; `bias_engine.py:271` calls −3 MILDLY BEARISH. The
brief called **nothing** on a day that fell **321 points**.

**Interaction that must not be ignored.** 08-28 and 09-08 are days **P1** (FRED
staleness) also claims — the two proposals overlap and must be judged together.
**2026-09-10 is clean of it:** `real_yields` scored 0 that day, so the result is
attributable to credit alone. That is the day to decide on.

**Not a deletion.** The fix is to make the bull side a change test symmetric with
the widening branch, keeping `-2` intact, so a real credit event still fires hard.
`chg_5` is already fetched. **No new data point needed.**

---

## M6 — the grader's verdict is a function of the session close

**Opened 2026-09-11** from the 2026-09-10 final review. Proposed; not edited.

`review_day.py:73` sets the settled side from **`bars[-1]["close"]`**, and line 94
derives `acted_as` from it. For any level price crossed once on a day that closed
far beyond it and never returned, `worst_excursion` is small **by construction**
and `held` is `True` **necessarily**. The metric measures "price crossed this once
and did not come back" — a property of the day's trend, not of the level.

**Evidence: 8 sessions, near-total separation by day sign.**

| | resistance | support |
|---|---|---|
| 5 down days (08-24, 08-28, 09-08, 09-09, 09-10) | **37** | 5 |
| 3 up days (08-25, 08-26, 08-27) | 3 | **37** |

**2026-09-10 is the extreme case**: the largest-range day on record (463.9,
132.8% of ADR, net −321.3) produced a **100% hold rate (7/7)** and the **lowest
level hit rate of all 8 days (0.18)** simultaneously. Those are the same fact
reported twice, and neither is about the levels.

**What this invalidates until fixed.**

1. **The provisional commit `22e9c1c`'s headline** — *"walls 7/7… the best
   single-day level result recorded"*. **Withdrawn.** 7/7 was not available to be
   otherwise on a day that closed 90pts below its lowest touched level.
2. **H6** ("is the level board producing clean reactions") is measuring drift.
3. **H14's remaining empirical claim** — does a put wall act as
   resistance-after-break in short gamma. The 7 recorded put-wall touches split
   **4 resistance / 1 support / 2 lost**, which looks supportive and **is not
   evidence**, because the split is derived from the close side. H14's empirical
   half cannot advance until M6 is resolved, regardless of how many sessions
   accumulate.

**Fix direction.** Grade against the **direction of approach** and a reversal
threshold measured from the touch; report `acted_as` only where a reaction is
distinguishable from the day's drift. No threshold is being tuned — a verdict is
being made independent of a variable it should not depend on.

---

## Observations appended 2026-09-11 (no proposal attached)

- **H1 gains its 8th point, +57.3**, and the series (+61.2, −11.6, −73.0, −86.4,
  −10.7, −26.2, −64.0, +57.3; mean −19.2) still flips sign. "Do not fit a
  multiplier" stands. **New angle:** day error correlates with realised session
  range at **r = 0.951**, slope **0.648** — the only two under-reads are the two
  largest-range days (530.9, 463.9). That is the signature of too little
  *dispersion*, which an offset or multiplier cannot fix. **But error-vs-outcome
  correlation is also what regression to the mean produces mechanically, so this
  is not a finding yet.** What would settle it: regress `budget` directly on
  realised extension and read *that* slope. Nothing proposed.
- **The fuel model's low end is 3 for 3 exact** (08-25 12.0 vs 0.4; 09-08 26.2 vs
  0.0; 09-10 **0.0 vs 0.0**). Whatever happens to H1, do not touch it.
- **Unmitigated-pool term: 3 right / 3 wrong over 6 firings across 5 days**, zero
  on 16 of 22 scans. 09-10 08:12 scored **+1** *"6 above / 4 below — draw higher"*
  on a day that ignored all six above and swept all four below. Day gate met, but
  3–3 on n=6 is chance, and chance is not a demonstrated absence of skill.
  *Watching the next 4 firings.* Do not touch `_W`.
- **Wall-band position term: 2 non-zero observations.** 09-10 15:07 gave **+2**
  (*"bottom 20% — poor risk/reward for shorts"*) on a scan that then fell 91pts
  to the close, having already made its low 198pts lower; 09-10 08:12 gave **0**
  at 22% up the band, 2 points the wrong side of its own threshold; 09-08 gave a
  correct −2 at the top. Far too few. *Watching the next 3 firings.*
- **New watch item — gamma's flip term is a step function with no proximity
  scaling.** 09-10 08:12 awarded the full **+2** for being **48pts** above the
  flip — **14% of ADR14**, inside one bar's noise on a day that ran 464 — and the
  flip broke by **10:00Z**, then held as resistance for 655 minutes with 11
  rejected re-tests. Same family as **H10** (a displacement rule with no reclaim
  condition) on a different term. **1 session.** *Watching:* distance-from-flip at
  scan versus whether the flip survived, for the next 3 scans scoring non-zero
  gamma within 0.25 ADR of the flip.
- **D7 — third recorded instance, and the fix post-dates it.** The 09-10 **15:07**
  board published exactly **2 levels, both self-disclaimed** (*"Mark it and leave
  it… not an intraday trigger"*), and **neither was touched — hit rate 0.00**.
  The level that actually mattered, **PUT WALL 29,194.4 at 22pts from spot**, was
  pushed into the *"context only, don't mark"* footnote by `budget * 1.75` against
  a **0pt** budget — carrying, in the secondary table, the **correct** short-gamma
  note (*"accelerate THROUGH rather than stall. Not a floor"*), which is exactly
  what price did on its way to 29,018.3. D7's fix landed in `113a5a1`, **after**
  this scan. Logged as confirmation; no new proposal.
- **PD close is noise for the third time** — published **+10.0** from spot on a
  464pt day, worst excursion +1.7. Tally of distance-at-publication: 09-08 +3.1,
  −1.5; 09-10 +10.0. Still 2 days. Note this **cannot be settled before M6**,
  because the reaction grade is the contaminated variable.
- **Journal hygiene.** 11 `is_trading_day: false` PREP scans (2026-08-23) and 6
  `test_artefact` entries excluded from every statistic above. No fabricated or
  backfilled entries found.
- **Provisional-vs-final drift, for the record.** `22e9c1c` graded 09-10 at 20:23Z
  pre-roll as O 29,437.9 / C 29,126.8; the final post-roll figures are O
  **29,429.3** / C **29,108.0**, a 18.8pt difference in the close. Pre-roll
  grading is a convenience, not a record — D3 already holds the day until 21:00Z,
  and provisional numbers should not be cited in a threshold count.

---

## D14 — a zero meaning "no data yet" was published as a price

**2026-09-11 13:23Z**, six minutes before the US open. Section 7 printed:

| | by OPEN INTEREST | by VOLUME (today) |
|---|---|---|
| Heaviest positive gamma | 29,458 | **183** |
| Heaviest negative gamma | 29,183 | **183** |
| 0DTE heaviest positive | 29,623 | **183** |

and *"Flip cross-check: ours 29,034, theirs **183** (-28,852pts apart)"*, and
*"The dominant strike is stable at **0** across 6 samples — positioning is
settled there."*

**Cause, confirmed by reading the feed directly:**

```
full | spot= 29105.7 | zero_gamma= 0 | major_pos_vol= 0 | major_pos_oi= 29275
zero | spot= 29105.7 | zero_gamma= 0 | major_pos_vol= 0 | major_pos_oi= 29440
one  | spot= 29105.7 | zero_gamma= 0 | major_pos_vol= 0 | major_pos_oi= 29100
```

The OI fields are healthy. The **volume-weighted** fields are `0` — correctly, because
**no volume has traded yet today**. The code then applied the CFD offset
(`+182.6`) to that zero and published **183** as a strike price.

**This is not a vendor outage.** It is a sentinel — 0 meaning *"nothing yet"* —
being arithmetic'd into a price. `zero_gamma` was 0 too, which is also an H13
data point: the field can read 0 pre-RTH, so a `zero_gamma` of 0 must never be
counted as an observation of where the flip is.

**Root cause is the family already in this register**: no guard between a value
and the claim made of it. D6 was a fresh timestamp on a stale price; this is a
zero on a live feed. A strike 28,852 points from our flip, and a "dominant strike
stable at 0", are both self-evidently impossible and were rendered anyway.

**Damage: none to the call, the board or the fuel model** — section 7 is
research-only and says so. But it was printed as if meaningful, and H12 counts
observations out of exactly these fields, so a 0 must not enter that count.

**Fix when next touching the file** — not applied mid-scan, since re-running
would journal this market state twice:

1. Treat a volume-weighted field of `0`, or any value more than ~5% from the
   feed's own `spot`, as **absent**. Print "no volume yet today (pre-open)"
   rather than a converted number.
2. Never convert an absent value through the offset — the offset is what turned
   0 into a plausible-looking 183.
3. Suppress the flip cross-check when either side is absent. A -28,852pt
   disagreement is not a disagreement, it is a missing value.
4. **H12 and H13 must not count a scan whose volume fields are 0.**

## D15 — a zero budget degenerates the path read, the same way it emptied the board

Same brief. With `budget = 0.0` (EXHAUSTED at 127.2% of ADR), the path text read:

> **DOWNSIDE path: mostly clear.** First real brake is 29398.0 (**6pts away**),
> which is **beyond today's 0pt budget** — so inside today's range there is
> little to stop a breakdown.

Every distance is "beyond" a zero budget, so the comparison stops carrying
information and the sentence asserts a clear path to a brake **six points away**.

Worse, the secondary table in the same brief lists that exact level —
**29,398, 1.55bn, 55,906 contracts** — as *"in-the-money call gamma… dealers are
LONG gamma here… expect a stall and dip-buying, it acts as **support**"*. The
largest single concentration on the page, six points below spot, described as
clear air by one section and as support by another.

**This is D7's defect in a second location.** D7 was fixed for the level board on
2026-09-10; the path read takes the same budget and degenerates the same way.
Fixing one instance of a category error does not fix the category — the same
question ("can price REACH this?") is still being answered with the range budget
("how much further can the range GROW?").

**Candidate fix:** window the path read on ADR as `secondary_walls()` already
does, not on the remaining budget. No new calibration — the same substitution
already made twice.

---

# ⚠️ H7's headline statistic was contaminated. "Overnight 0 of 3" is WITHDRAWN.

Found 2026-09-11 while grading the day. **This matters because the overnight
strategy suppression was shipped on the strength of it.**

## The flaw

The 2026-09-09 retrospective scored strategy selection with **day shape** — where
price closed within **the whole session's** range. For a scan published at 12:47,
that statistic includes the move from 04:00 onward: **hours of price action that
predate the forecast.** A forecast graded against data older than itself is the
look-ahead error of D5 turned around, and M4's window fault in a third costume.

Today made it visible. 2026-09-11 closed at **77% of the day's range → "RAN",
Strategy 2**, so both scans would score WRONG. But the low was set at **04:00Z**
and the high at **13:00Z**. Measured from each scan forward, post-scan close sits
at **36% of the post-scan range → "FAILED BACK", Strategy 1** — which is what
both briefs recommended. **Both correct, scored wrong by the old statistic.**

## Re-graded, 22 scans

| statistic | result |
|---|---|
| whole-day (what the 09-09 retro used) | 6 right / 7 wrong |
| **post-scan (graded from publication)** | **9 right / 12 wrong** |

By session window, post-scan:

| window | right / wrong |
|---|---|
| PRE_NY | **5 / 3** |
| LONDON | 2 / 4 |
| NY_MIDDAY | 1 / 2 |
| **OVERNIGHT** | **1 / 2** |
| NY_OPEN | 0 / 1 |

**OVERNIGHT is 1 right / 2 wrong, not 0 of 3.** On three observations that is
noise. **The threshold is not met and the claim is withdrawn.**

## What survives, and what does not

**Withdrawn:** *"every overnight scan called the wrong strategy"*. It rested on a
statistic that graded forecasts against pre-forecast price.

**Still standing, because it was never measured this way:** the flip's raw
instability. Those figures came from the published flip values themselves —
**389pts of movement while price moved 259 on 08-24; two scans two minutes apart
with price 9pts apart publishing flips 192pts apart with opposite regime labels;
all three multi-scan days contradicting their own regime label.** None of that
depends on day shape.

So the overnight suppression still has a justification — *the number is too
unstable across the roll to name a regime from* — but **it is no longer the
justification it was shipped with**, and the trader approved it on the withdrawn
one. That is his call to revisit and he has been told.

## Also true, and worse than previously reported

Overall strategy selection is **9 right / 12 wrong** — below a coin flip, not the
4-and-4 reported on 09-09. Two caveats, neither of which rescues it: 08-24
contributes 8 scans, several within minutes of each other, so it is over-weighted
(`track.py` dedups; this ad-hoc count did not), and 21 graded observations is
thin.

## The rule this should have followed

**Never grade a forecast against a window that starts before it was published.**
`gex_retro.py` already clips bars to `b["time"] >= born` for exactly this reason
(D5). The strategy cross-tab was written fresh and did not reuse it — the fourth
time a correct guard existed somewhere in this repo and the new code did not call
it (see also D7's board filter vs `secondary_walls()`).

**Action taken:** none to the model. This is a measurement correction, and the
decision it undermines belongs to the trader.

---

# From the 2026-09-11 review (written 2026-09-14)

## D16 — the straddle rider's ternary is a no-op, and above the flip it INCREASES conviction

`bias_engine.py:86-89`:

```python
if abs(dist_pct) < 0.15:
    add("gamma", +1 if px > gf else +1,
        "but price is straddling the flip (<0.15%) — regime unstable, "
        "reduce conviction")
```

`+1 if px > gf else +1` — both branches are `+1`. Above the flip this is added to
the `+2 above flip` vote, so gamma reads **+3**: the rider that says "reduce
conviction" makes the bullish vote **50% larger**. Below the flip it softens
`−3` to `−2`, which is what the text promises. The intent is almost certainly
`-1 if px > gf else +1` — pull the magnitude toward zero from either side.

**Every firing on record is above the flip, so every firing has the wrong sign:**

```
2026-09-09 15:17  px 29397.5  flip 29392.5  above  +1
2026-09-09 15:20  px 29418.8  flip 29403.1  above  +1
2026-09-11 12:47  px 29336.2  flip 29312.4  above  +1   (0.081%)
```

3 firings, 2 distinct trading days. On 2026-09-11 12:47 gamma totalled **+5**
while straddling the flip by 23.8pts, against **+4** on the 13:24 scan sitting
cleanly 370pts above it — *less* certain scored *more*. No label was changed on
any firing (09-11 would have been −8 rather than −7), so the measured impact is
conviction magnitude, not direction.

This is a code defect, not a calibration preference, so it is not gated on the
3-session rule — same class as D8, D14, D15. **Not fixed by the reviewer.
Decision belongs to the owner.** Same family as D8: a printed rationale that
describes a computation the code does not perform.

---

## H7 — fourth observation, and the first one with a measurable cost

**2026-09-11, 12:47Z → 13:24Z, 37 minutes: flip moved −277.9pts (29312.4 →
29034.5) while price moved +68.3. The largest sub-hour flip move in the
journal**, exceeding the 192pt/2min anomaly. Ratio 4.1×.

Full consecutive-scan drift table, all days, pairs under 16h:

```
08-24 08:28→08:30    2min   dPrice   +8.9   dFlip +192.0   21.6x
08-24 08:30→08:32    2min   dPrice   +6.9   dFlip  +16.0    2.3x
08-24 08:32→08:33    1min   dPrice   -6.7   dFlip   -0.4    0.1x
08-24 08:33→09:37   64min   dPrice  +44.9   dFlip +181.2    4.0x
08-24 09:37→12:40  183min   dPrice  -14.7   dFlip  -42.1    2.9x
08-24 12:40→12:46    7min   dPrice  -14.7   dFlip  +12.4    0.8x
08-24 12:46→13:45   59min   dPrice -229.3   dFlip -359.4    1.6x
08-26 13:12→13:14    2min   dPrice  +22.7   dFlip  +23.5    1.0x
08-26 21:43→22:11   28min   dPrice  +12.7   dFlip +167.4   13.2x
09-10 08:12→15:07  415min   dPrice -202.7   dFlip  -35.3    0.2x
09-11 12:47→13:24   37min   dPrice  +68.3   dFlip -277.9    4.1x
```

**What is new is not the instability — it is that the revision destroyed a
working level.** The 12:47 flip (29312.4) held as support for **485 minutes with
a worst excursion of −0.9pts**. The 13:24 revision put it at 29034.5, 370pts
below spot, **never touched**. H7 has so far argued the flip is too unstable to
name a regime from; this is the first day showing the later reading is not
merely different but *worse* than the one it replaced.

**Status unchanged: OBSERVING.** The remedy now most likely sits under the
completeness gate below rather than in H7 itself.

---

## H16 (new) — the gamma block has a freshness gate and no COMPLETENESS gate

**Claim.** Pre-cash-open CBOE chain pulls return a *fresh timestamp* over a
*materially incomplete book*, and the entire gamma block — flip, walls, max
pain, net GEX — is computed and voted on as though the book were whole.

**Evidence — 3 distinct trading days.** Every early scan in the journal reports
a 45DTE net GEX an order of magnitude below the same day's later scan:

| day | early | 45DTE GEX | later | 45DTE GEX |
|---|---|---|---|---|
| 2026-08-24 | 08:28–08:33 (×4) | **0.024**, byte-identical ×4 | 09:37 | −5.48 |
| 2026-09-10 | 08:12 | **1.114** (wk −0.058) | 15:07 | −4.645 |
| 2026-09-11 | 12:47 | **0.599** (wk 1.81) | 13:24 | **8.131** (wk 8.119) |

Scans from ~13:00Z onward are stable against each other same-day
(08-27 13:23 / 13:41 / 13:43 → 11.925 / 11.773 / 11.817).

2026-09-11's pair in full, 37 minutes apart, both chains timestamped fresh
(`12:40:23`, `13:23:05`):

```
flip            29312.4 -> 29034.5   (-277.9)
call wall       29466.2 -> 29648.0   (+181.8)
put wall        29016.2 -> 28998.0
net GEX 0-2DTE    0.643 ->   3.887   ( 6.0x)
net GEX week       1.81 ->   8.119   ( 4.5x)
net GEX 45DTE     0.599 ->   8.131   (13.6x)
45d call-wall contracts  59k -> 120k ( 2.0x)
CFD/index offset  +16.2 ->    -2.0
```

A 45-day book cannot change 13.6× in 37 minutes, and its call wall cannot take
on 61k contracts pre-open.

**It subsumes two open items rather than adding a third.**

- **H7's headline anomaly gets a mechanism.** On 08-24 08:28→08:30 the 45DTE GEX
  is identical to three decimals (0.024) while the flip moves 192pts on 8.9pts of
  spot. Same chain, different spot, wildly different flip — a repriced
  zero-crossing on a near-empty book is ill-conditioned, because the gamma
  profile is flat and the root is unconstrained. H7 calls this "possibly a
  cold-start artefact"; this is what the artefact *is*.
- **D8's trigger was itself an artefact.** D8 fired on 2026-09-10 08:12 because
  `net = -0.058` fell into the strategy selector's `net <= 0` catch-all. That
  −0.058 is the empty-chain reading; the same day at 15:07 it was −3.795. D8's
  stated condition was not a market state.

**Proposed change (owner's decision, not implemented).** Add a completeness
check beside the existing age check — total 45DTE contract count, or
`abs(full_45dte)`, against a trailing median for the symbol. On failure, withhold
the flip-derived votes and mark the walls provisional, reusing the
`flip_unreliable` mechanism already in `bias_engine.py:70-77` for OVERNIGHT
rather than inventing a new weight.

**Counter-evidence, recorded deliberately.** On 2026-09-11 the *thin* 12:47 board
was the better one: its call wall held the session high to **9.6pts** and its
flip held as support to **0.9pts**, while the fuller 13:24 board missed the high
by 172pts and had **0 of 4** levels touched. One day does not settle which
snapshot is truer. The proposal is therefore *not* "the early board is wrong" —
it is "a quantity that moves 13.6× in 37 minutes is not a measurement the model
should vote on as though it were", and the gate should suppress **votes and
regime labels, not the level board**.

**Threshold.** Met on the GEX-jump evidence (3 days). Not met on whether gating
improves outcomes — that needs the gate built and run. Do not implement without
the owner.

---

## H17 (new, OBSERVING) — the direction grade has no magnitude deadband

`review_day.py:204` takes the sign of the post-scan move:

```python
call = ("no call (neutral)" if exp == 0 else
        "CORRECT" if exp == dir_after else "WRONG")
```

**2026-09-11 12:47 is graded CORRECT on a −1.1pt move — 0.2% of the day's
457.5pt range.** Post-scan move as a share of session range, every graded scan:

```
08-26 13:12  76.7%   08-26 21:43  37.4%   08-26 22:11  39.4%
08-27 13:23  30.1%   08-28 22:33  31.8%   09-08 15:39  24.6%
09-09 15:20  29.8%   09-10 08:12  64.4%   09-10 15:07  19.7%
09-11 12:47   0.2%   09-11 13:24   7.2%
```

The two smallest are both from 2026-09-11 — **one trading day**. One session is
noise and nothing is proposed. The day-level irony worth recording: the index
closed **+252.1** and the scoreboard reads **2/2 correct BEARISH**, because both
scans landed near the high.

**Watching:** whether graded calls under ~5% of range recur on further sessions.
If they do, the grade should read `no call (inside noise)` rather than CORRECT,
and the direction statistic should be restated. **Threshold: 3 days with at
least one sub-5% graded call.** 1 of 3.

---

## M7 (new) — track.py and review_day.py disagree about which days are gradeable

Not calibration — a bookkeeping defect that contaminates the statistic H1 is
quoted from. `track.py` reports "**7 trading day(s), 11 scans (deduped)**" and
"6 entries marked test_artefact". Only **2** journal files carry an artefact
flag (09-09 1513 `defective_build`, 09-09 1517 `verification_rerun`).

**Gap 1 — 2026-08-24 is permanently ungradeable and silently absent.** 8 clean
scans, `is_trading_day: true`, no artefact flag, and `review_day.py 2026-08-24`
returns `{"error": "no NAS100 bars for 2026-08-24", "scans_found": 8}`. The M5
history aged out of the broker feed. This is the day that produced H7's
192pt/2min anomaly and part of D12's evidence, and no future analysis can ever
re-grade it. **Snapshot the graded session's M5 bars into the journal at grade
time**, or every day quietly expires on the same clock. Local, free, no new
external dependency.

**Gap 2 — 2026-08-25 is held back by one grader and graded by the other.**
track.py: "HELD BACK - day not finished (grades after 21:00 UTC on its own date):
2026-08-25 98 bars so far". review_day.py grades it complete:
`O 29260.9 H 29342.6 L 29086.1 C 29212.9`, range 256.5, net −48.0, 430-minute
level holds, direction 1 right / 0 wrong / 1 no-call.

**Why it is material.** 08-25 13:04's fuel error is **+219.8** (budget 12.0 vs
extension 231.8) — larger in magnitude than any of the seven days currently in
H1's per-day mean of **−22.7**, and of the opposite sign. Admitting one day of
that size to a seven-day mean is capable of flipping H1's headline from "the
model over-budgets" to "the model under-budgets".

**Deliberately NOT recomputed here.** The reviewer recomputing H1 by hand is how
a second disputed number gets created. track.py must recompute once the
held-back day is admitted. **Until it does, H1's −22.7 should not be quoted as
settled.** Note also that the 2026-09-10 review's "8 trading days, 15 deduped
scans" does not reconcile with today's "7 / 11" either.

---

## Zero-budget scans score a free bullseye (evidence appended, no proposal)

When a scan fires after the session high and low are both already set,
`range_at_scan` equals the full session range, so extension is necessarily 0.0.
With budget also 0.0, `review_day.py` grades "about right" and track.py logs
`err 0.0` — indistinguishable from a genuine bullseye, on an observation that
carries no information.

Instances: **2026-09-11 13:24** (budget 0.0, extension 0.0, range_at_scan 457.5
= session range), 2026-09-10 15:07, 2026-09-09 15:20, 2026-09-08 15:39.

Entangled with M7 — both change H1's denominator, and acting on either alone
would produce a mean that is wrong in a new way. **No proposal until M7 is
resolved.**

---

## P1 — third consecutive session (evidence appended)

`macro −3` from **DFII10** was again the largest single component in both
2026-09-11 scans, and again carried the brief's own warning: *"FRED has not
published since 2026-09-09 (2 business days ago) — this is last week's reading,
not today's."* The item is already open; nothing new proposed.

## D14 confirmed pre-open-specific; H14's fix confirmed working (2026-09-14 17:22Z)

**D14 did not recur.** Mid-RTH, section 7 returned real strikes (29,307 / 29,087 /
29,307) rather than the offset-converted zeros of 2026-09-11 13:23Z. That matches
the diagnosis exactly: the volume-weighted fields are 0 only while no volume has
traded, i.e. before the US open. The guard is still needed — the 12:45Z scheduled
run lands 45 minutes pre-open every weekday and will keep hitting it.

**H14's fix produced the correct label on its first short-gamma day.** Price
29,246.7 below the flip 29,351.2, so the put wall note read *"Heaviest floor this
week (62k contracts), BUT today the desks are pushing moves along — if it breaks,
expect it to speed UP, not bounce. Don't buy the break."* That is the branch that
did not fire on 2026-09-10, when both put walls were called reliable floors and
neither floored anything.

**D7's fix likewise.** Budget 0.0 again (129.8% of ADR) and the board carried five
rows — flip, call wall, max pain, put wall, structural put wall — all tagged
`_(stretch)_`. Pre-fix that board would have held one row.

**D15 is still live and unfixed**, as recorded: *"UPSIDE path: mostly clear. First
real brake is 29317.4 (71pts away), which is beyond today's 0pt budget."* Every
distance is beyond a zero budget. Second observation.

---

# Observations appended 2026-09-15 (grading the 2026-09-14 session)

Source: `review_day.py 2026-09-14 --json`, `track.py`, and `review_day.py`
re-runs across 08-27 … 09-11. Full write-up in `2026-09-14/REVIEW.md`.
Session: O 29053.7 / H 29291.4 / L 28804.7 / C 29183.0, range 486.7 (137.3% of
ADR14 354.5), net +129.3. Two scans, 1 direction right / 1 wrong.

## H1 — budget vs range extension: the split that matters is zero vs non-zero

**Seventh trading day.** 13:04 PRE_NY budget 61.9 → extension **194.1**
(**+132.2**, the largest under-read on record). 17:23 NY_MIDDAY budget 0.0 →
extension 26.6 (+26.6). Per-day error now **−86.4, −10.7, −26.2, −64.0, +57.3,
+44.3, +79.4**; mean **−0.9**.

The per-day mean sitting on zero is the point. Four over-reads followed by three
under-reads is not a bias a multiplier can fix. But splitting on the budget
value is sharp:

| budget | scans | errors | MAE |
|---|---|---|---|
| **= 0.0** | 3 | 0.0, 0.0, +26.6 | **8.9** |
| **> 0.0** | 7 | −86.4, −10.7, −26.2, −64.0, +114.6, +88.7, +132.2 | **74.7** |

Mean budget when > 0 is 147pts; MAE is **51% of it**. The exhausted-point claim
is now **4-for-4 across four days** (counting 24 Aug 13:45's +5.3). Proposed in
REVIEW §4 P4: keep the number when it is zero, print a band when it is not.

**Negative result, recorded so it is not re-run.** I tested whether `fuel_ratio`
("burning hot") predicts the under-read. It does not: ratio 2.75 → err −10.7;
1.06 → −64.0; 2.17 → +88.7; 1.65 → +132.2; 1.32 → −86.4. No relationship.

## H2 / H3 — third instance, and the sample is directionally contaminated

13:04 PRE_NY: `LOW_FUEL`, 82.5% of ADR already spent, price **26.0pts above the
session low which was already in from London**, bias **−11 STRONGLY BEARISH**
(continuation). Price ran **+352.1** and closed +129.3 on the day. **The fade
was the trade, for the third time** (after 24 Aug 13:45 and 25 Aug 13:04).

Threshold met on count. **Still not proposing**, for a reason worth writing
down: all three instances are *bearish* calls printed at *lows*. That is
consistent with over-commitment at extremes (H3) and equally consistent with a
plain bearish skew in the engine. One instance of a max-conviction *bullish*
call at a session *high* would separate them. Until then a cap would be fitted
to a one-sided sample.

## H4 — flip as magnet: threshold long met, claim fails

Close-to-flip distance, all days on record: 1.1, 236.6, 255.2, 599.8, 309.2,
26.2, −263.5, 57.7 / 335.6, **−408.3 / −168.2**. **Nine days: three near, six
far.** Both of 09-14's flips were misses and neither was reached intraday
(29591.3 published **761pts** from spot on a day budgeted at 61.9). The standing
verdict — *do not use the flip as a target* — is confirmed and needs no new
proposal, since the flip is not published as a target.

**New sub-observation for H7, not H4.** The `gamma −3` penalty is awarded in
full at 760.6pts below the flip exactly as it would be at 5pts below. Distance
does not scale it. One clean instance; logged, not proposed.

## H6 — the hit-rate denominator is polluted by structural walls

**5 publications across 3 trading days (09-09, 09-10 ×2, 09-14), 0 touches** —
and that is correct behaviour, because the brief labels them *"the floor for the
WEEK/MONTH… mark it and leave it, not an intraday trigger."* Grading a
deliberately multi-day level on intraday touch is a measurement error.

Corpus: **0.544 all levels → 0.581 excluding `kind: structural`.** Proposed in
REVIEW §4 P3: exclude them from the statistic, keep publishing them. This should
land *before* H6 is read at its 5-day threshold, or H6 will be read off a biased
denominator.

## H10 — prior-week-range rule: now 0-for-4

Fourth firing. 13:04 PRE_NY: `structure −3`, *"price is BELOW the entire
prior-week range (29018.3-29734.1) — PWL 29018.3 is now resistance."* Price
reclaimed it and **closed 164.7pts above it**. The engine's own 17:23 scan
prints `structure 0 — "price inside the prior-week range"` — the premise died
within **4h19m** and the −3 was live for all of it.

Record to date, every firing on a graded day:

| Firing | Score | Outcome |
|---|---|---|
| 24 Aug 13:45 | −12 | WRONG, closed +147 above the scan |
| 25 Aug 21:56Z (26 Aug session) | −15 | WRONG, closed +140 |
| 26 Aug 13:12 | −4 | WRONG by 249.8pts; reclaimed within the hour |
| **14 Sep 13:04** | **−11** | **WRONG by 352.1pts; reclaimed within 4h19m** |

**0-for-4.** Proposed in REVIEW §4 P2 as a reclaim term — not a smaller
constant. Caveat kept on the record: three of the four sit in one cluster of
consecutive August sessions and may be one market condition rather than four
independent tests. The proposal rests on the visible absence of a reclaim term,
not on the count reaching four.

**Honest limit.** Removing this −3 gives −8 on 09-14 — still STRONGLY BEARISH.
This fix does not rescue the day on its own.

---

## H18 (NEW, opened 2026-09-15) — a stale FRED series still moves the score

**Claim.** When a FRED series stops publishing, the macro component keeps
scoring it at full weight, and — worse — the score *changes* while the data does
not, because the 5-day comparison window rolls forward past a frozen endpoint.

**Why it matters.** `DFII10` (10y real yield) carries **±3**, the largest single
macro weight in the engine. The engine already *detects* staleness and prints
the warning in the `why` string. It just does not act on it.

**Evidence (4 trading days).** DFII10 frozen at the 2026-09-10 print since
2026-09-10. Scores over the stale window, in order:

`09-10 0, 09-10 0, 09-11 −3, 09-11 −3, 09-14 −3, 09-14 −3, 09-15 −3`

**The score moved from 0 to −3 with no new data.** On 09-14 13:04 that −3 was
27% of a −11 call that was wrong by 352 points.

**Threshold.** Already met on mechanism — this is a defect, not a distributional
claim. Proposed in REVIEW §4 P1: scale the points toward 0 when the series is
≥1 business day stale. Recorded here because the general form (any FRED-derived
component, not just DFII10) still needs watching across more series.

## H19 (NEW, opened 2026-09-15) — is the news auto-scorer sampling-biased bearish?

**Claim.** The keyword patterns that make a headline auto-scorable skew toward
alarm, so the `news` component reads bearish regardless of the actual tape.

**Why it matters.** `news` is the most negative block in the engine: **sum −19
across 10 graded scans**, against structure −5, rates −8, vol −8. It is a large
weight derived from a tiny, non-random subset.

**Evidence (11 days, 32 scans).** Sign of the auto-scored reading: **20 bearish,
4 bullish, 7 flat** — and all four bullish readings fall on a single day
(24 Aug). Coverage is the other half: median ~2 headlines counted, median ~47
left uncounted. On 09-14 13:04 it was **5 counted of 52** — a −3 block set by a
9.6% sample.

Either the news genuinely has been bearish for eleven straight days, or the
sampling is biased. Nothing here distinguishes the two yet.

**Threshold / what would settle it.** Hand-score the *uncounted* headlines on
three separate days and compare the sign of the full set to the auto-scored
subset. Free, no new data source, no API. **Record every scan:** counted count,
uncounted count, sign.

**Status: OBSERVING. Do not implement.** No weight change until the hand-score
test is run.

---

## Numbering collision, corrected 2026-09-15

The 09-14 review opened two new hypotheses as **H12** and **H13**. Both numbers
were already taken — H12 is the volume-weighted wall question (line ~431) and
H13 is GEXBot's `zero_gamma` (line ~491), and the brief itself prints "Research
only — H12 and H13 are open" in its volume-weighted gamma section, meaning the
generated output would have pointed at two different claims under one ID.

Renumbered to **H18** (stale FRED series) and **H19** (news sampling bias);
H14–H17 were already in use. Only the two new headings changed — no evidence,
no counts and no history were touched.

This is the same class of error as the 26 Aug naming fix recorded under H1: one
object, two names, in the file whose entire job is to stop double-counting. The
open IDs now run H1–H19 with D1–D16 alongside; a new entry takes the next free
number, and reviewers should grep the headings before assigning one.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

---

# Observations appended 2026-09-16 (grading the 2026-09-15 session)

Source: `review_day.py --json` (resolved to 2026-09-15), `track.py`, and the
`prediction` block of `2026-09-15/1246-preny.json`. Full write-up in
`2026-09-15/REVIEW.md`. Session: O 29174.2 / H 29189.4 / L 28909.8 / C 28983.4,
range 279.6 (77.5% of ADR14 360.9), net −190.8. One gradeable scan, direction
**CORRECT**. Integrity clean (commit `2f3a37e`, authored 4s after `scan_utc`).

## H1 — eighth trading day; the zero/non-zero split holds, the bias does not exist

12:46 PRE_NY budget **97.3** → extension **16.0** (**−81.3**, second-largest
over-read on record after 08-27's −86.4). Traversal 269.3 (2.77×).

| budget | scans | MAE |
|---|---|---|
| **= 0.0** | 3 | **8.9** |
| **> 0.0** | **8** | **75.5** |

Mean budget when >0 is ~147pts; MAE is **51% of it** — the same ratio reported at
7 scans. Per-DAY error across 7 days: −10.7, −26.2, −64.0, +57.3, +44.3, +79.4,
**−81.3**; mean **−0.2**. Dispersion without bias. **P4 (print a band when the
budget is non-zero) strengthened; no new proposal.**

## H1 sub-observation — the budget's correct reading is not reaching the prose

New, and the sharpest instance so far of H1's own claim block ("the extremes are
probably in — expect movement *between* them").

At scan, price was 29119.3 and the session low **28925.8 was already in**
(inferred: `range_at_scan` 263.6 below a high of 29189.4, and "Asia High (today)
29189.4" grades as never-reached post-scan). So **193.5pts of pure retracement
to an existing low** was available at zero range-extension cost — and the day's
actual new low was **16.0pts**, matching `range_extension` exactly.

Result: the fuel block printed `LOW_FUEL` and *"this dampens CONVICTION"*, and
the brief wrote *"nothing structural to slow a breakdown… If it goes, it has
room. Do not fade it."* It had 16pts of room. The trade was worth **−209.5** from
the scan price anyway, because of where price sat in the range.

**Mechanism.** The fuel block reports `remaining_budget`, `adr_used_pct` and
`expansion_state`, and **reports no distance to the existing session extremes**.
The prose therefore has no field with which to say "the available move is back to
the low, not beyond it". Logged under H1. **No proposal** — one instance, and the
right fix is a reporting field, which should wait for a second observation.

## H18 — the clincher, on the next scan

DFII10 froze at the 09-10 print. Score over the freeze and its release:

`09-10 0, 09-10 0, 09-11 −3, 09-11 −3, 09-14 −3, 09-14 −3, 09-15 −3, **09-16 0**`

On **2026-09-16 12:46Z** FRED published through 09-14 and the same series scored
**0**, with the 5-day move essentially unchanged (**18bp → 17bp**). **The series
moved 1bp; the score moved 3 points twice.** The −3 existed only inside the stale
window and died when real data arrived — which is precisely H18's claim, now
demonstrated end-to-end on one series rather than inferred from a drifting
window.

On 09-15 that −3 was **25% of a −12** call. It pointed the right way. That is
luck; a component scoring data it knows it does not have is a defect whether the
day agrees with it or not. **P1 (scale toward 0 when the series is stale) should
be prioritised.** No new proposal — P1 already covers it.

## H19 — the news score's magnitude tracks MATCH COUNT, not sentiment

New mechanism observation; the sampling-bias question is untouched.

| scan | counted | uncounted | sign of counted | score |
|---|---|---|---|---|
| 2026-09-15 12:46 | 4 (0 bull / 4 bear) | 53 | **100% bearish** | **−3** |
| 2026-09-16 12:46 | 1 (0 bull / 1 bear) | 49 | **100% bearish** | **0** (NEUTRAL) |

Both days were unanimously bearish among the headlines the scorer could read.
The scores differ by 3 points, and the only thing that differed is **how many
headlines happened to trip a keyword**. A minimum-count floor is a defensible
design; the consequence is that −3 and 0 here are not two readings of the news,
they are two sample sizes — on 7.0% and 2.0% coverage respectively.

**Status: OBSERVING, unchanged. No weight change.** The hand-score test (score
the *uncounted* headlines on three days, compare the sign of the full set to the
subset) has still not been run, and nothing below it should move the weight.
**Record `counted`, `uncounted` and `sign` every scan** — now also record the
resulting score, because this table is what made the mechanism visible.

## M6 — ninth session, and the cleanest instance yet

A −190.8 day. Of 9 touched levels, **8 graded "held as resistance" and 1 "held as
support"** — and the 1 is the only level below the close. The close (28983.4)
sits between 28963.1 (support) and 29005.8 (resistance), and the verdicts
partition exactly there. `minutes_held` reads 385–490 for nearly every level:
the whole session, because price crossed once and never returned.

Day-sign separation now: **6 down days** against 3 up days, with the same
near-total split reported at 8 sessions. Nothing has changed except the count.

**M6 is the blocker on every level statistic** — H6, H14's empirical half, and
any `acted_as` tally. Its fix direction (grade against direction of approach and
a reversal threshold measured from the touch, not from the close) is already
written up and needs a decision, not more evidence. I am not re-proposing it.

## H6 — the density artefact, quantified again

Hit rate 0.64 (9/14); **0.69 (9/13) excluding the one `kind: structural` level**.
The nine touched levels span **219.9pts** inside a **269.3pt** traversal — the
board is denser than the path, so touching most of it is close to arithmetic.

`first_touch_reaction` is the only non-degenerate column, and it reads: 3 broke
down through, 6 chopped both sides, **0 clean rejections** on a 279.6-point trend
day. Watching whether a clean rejection ever appears.

**STRUCTURAL PUT WALL: 6th publication across 4 trading days, 0 touches** — and
correct behaviour, since its own note reads *"the floor for the WEEK/MONTH… mark
it and leave it, not an intraday trigger."* **P3 strengthened.**

## H14 — the regime-aware wall note worked, second recorded time

29019.4 published as *"Heaviest floor this week… BUT today the desks are pushing
moves along — if it breaks, expect it to speed UP, not bounce. Don't buy the
break."* Price chopped around it, broke, and ran 109.6pts to the low without a
bounce. It did not act as a floor.

This is the *label* half of H14, which is decidable from first-touch behaviour.
**H14's empirical half — does a put wall act as resistance-after-break in short
gamma — remains blocked by M6** and gains nothing today, because today's
"resistance" verdict is close-derived like all the others.

## H3 / H2 — the missing cell arrived and does not settle anything

Bias **−12** printed at 29119.3 — **73% up the range already established at
scan** (28925.8–29189.4), 70.1pts below the session high. **CORRECT.**

All three contaminating H3 instances (24 Aug 13:45, 25 Aug 13:04, 14 Sep 13:04)
were max-conviction bearish calls printed at *lows*, all wrong. This is the first
printed near a *high*, and it was right.

**It is not the separator.** A plain bearish skew predicts today exactly as well
as H3 does: the engine printed −12 and the day fell. Nothing distinguishes
"correctly read the top of the range" from "is always bearish and met a down
day". The separator remains **one max-conviction BULLISH call**, and after 8
graded days there has not been one. **No cap proposed.**

## H10 — did not fire

`structure 0 — "price inside the prior-week range (29018.3–29734.1)"`. The
prior-week-range rule stays **0-for-4**; today adds no observation to it.

---

## P5 (NEW proposal) — the secondary gamma table is published and never graded

**Claim.** The brief's *"Other gamma concentrations in range"* table publishes
strikes with explicit behavioural claims in their own words — "call-dominant
strikes brake a move, put-dominant strikes speed it up… They are not all
support" — and **none of those strikes is written into `prediction.levels`**, so
`review_day.py` has never scored one.

**Evidence, whole journal.** The table appears in **every brief**. Across all
trading-day scans with a paired `.md`: **107 strike-publications, 22 scans, 10
separate trading days, 0 graded.**

| day | scans | secondary strikes | graded |
|---|---|---|---|
| 08-26 … 08-28 | 10 | 46 | 0 |
| 09-08 … 09-11 | 8 | 45 | 0 |
| 09-14 … 09-16 | 4 | 16 | 0 |

(09-16 is not a graded day; it is counted here as a *publication*, which is what
this proposal measures, not as an outcome observation.)

**Today's ungraded near-miss.** 28919.4 was published as *"dealers are SHORT
gamma here, so they amplify: price tends to accelerate THROUGH rather than stall.
**Not a floor.**"* The session low was **28909.8** — 9.6pts through it — and price
closed **73.6pts back above**. It acted as a floor. n=1 and ungraded, which is
the point.

**Why this clears the bar as a new proposal.** It changes no scoring logic and
tunes nothing; it converts an unmeasured published output into a measured one.
The 3-session rule exists to stop fitting to noise — this adds observations
rather than spending them.

**Expected effect.** First evidence on whether the put-dominant "accelerates
through, not a floor" note is true, which is currently asserted in every brief on
no data.

**Sequencing caveat.** It enlarges the hit-rate denominator, so it must land
**with or after P3**, and before H6 is read at its 5-day threshold — otherwise
H6 is read off a denominator that moved underneath it.

## No new data point is warranted

Every gap found today is in data the engine already holds and does not read:
FRED's own staleness (P1), the fuel block's distance to the existing session
extremes (H1 sub-observation), the news scorer's uncounted headlines (H19), and
strikes the brief already computes and prints (P5). Nothing here argues for a new
feed.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

---

## D17 — the chart re-downloaded the chain it already had, and 429 was fatal

**2026-09-15 and 2026-09-16: the brief succeeded and the chart died, both days,
with `chart FAILED: HTTPError: HTTP Error 429`.** Two scans delivered a brief
and no picture. The cause is two defects that only bite together.

**1. The chain cache could never hit for the chart.** `load_combined` is keyed
by `max_dte`. `build()` takes the **45**-day book; `gex_chart.collect()` draws
the **week** book and asks for **7**. Different key, guaranteed miss, every
scan — so drawing the picture meant a second full download of both the NDX and
QQQ chains plus two quote calls. The cache docstring says it exists to stop
"four HTTP round trips to CBOE for one picture, and enough to earn a 429";
it did not stop them, because the two callers in one scan never share a key.

**2. `cboe_gex._get` was a bare `urlopen`.** One 429 anywhere killed the
caller. CBOE sits behind Cloudflare and rate-limits by source IP (`error code:
1015`), and this host shares that IP with the other bots scanning on their own
schedules — so 429 is a *normal* condition here and was being treated as fatal.
On 09-14 it cost four attempts and ~40 minutes to get any brief at all.

Measured 2026-09-16: one request per 45s cleared the limit in ~90 seconds, and
a full scan's burst re-tripped it immediately. The budget is small and shared.

### Fix

- **`load_combined` serves a cached superset.** A 45-day book contains every
  row a 7-day load returns (`load_chain` drops only `dte > max_dte`), so a
  wider fresh entry is filtered rather than re-fetched. Verified equal to a
  genuine 7-day fetch: 3497 rows both ways, identical `(src, exp, cp, strike,
  oi)` tuples, max dte served 7. Chart fetches for a scan: **1 -> 0.**
- **TTL 90s -> 900s.** The chart is drawn mid-scan; a 90-second window could
  lapse before it ran, reintroducing the fetch the cache exists to prevent.
- **`_get` retries 429/5xx** at 2/5/12s, honouring `Retry-After` when sent.
  404 still fails immediately — it is a real answer about a symbol, not a
  transient. Exhausting the retries re-raises the original error.
- **The chart is drawn BEFORE the journal write and the archive commit.** It
  writes `research/chart-ladders/<stamp>.json`, which `sync_archive` carries;
  drawn last, that file was created *after* the commit and was left untracked
  every scan (hand-committed 09-11 and 09-14). This is D11's rule — writing a
  path the archive does not carry is the same defect as not writing it.

### Not fixed here, still open

`--no-journal` suppresses the journal but **not** the research ladders, so a
verification run still writes `chart-ladders/` and `gexbot/ladders/` entries.
Three were written while verifying this fix and deleted by hand. Same family as
the 2026-08-27 problem, where verification runs entered the evidence as real
observations.

The archive push still fails on every scheduled run: the container checks out a
**detached HEAD**, and `sync_archive` derives the branch with `rev-parse
--abbrev-ref HEAD`, which returns the literal string `"HEAD"`, so it pushes and
rebases against a ref that is not `main`. The `or "main"` fallback never fires
because `"HEAD"` is non-empty. Hand-pushed daily since 09-11. Left alone here
because this change set is about the chart.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

---

# D16 — the evidence base was silently eroding, and every quoted figure moved with it

**2026-09-16.** `track.py` read **7 trading days / 10 scans**. Five days earlier
it read **9 / 17**. No data was added and none was deleted.

`review_day.fetch_day_bars` fetched `days=min(days_back, 20)`. Today minus 20 days
is 2026-08-27, so 08-24, 08-25 and 08-26 fell off the back and 08-27 returned
**16 bars**. The broker still serves them — a `days=30` fetch returns 08-20 onward
— so this was self-inflicted and invisible.

**Why it matters more than a stale number.** This project's only real constraint
is observation count. A cap that quietly drops the oldest days means the register
**loses evidence faster than scanning adds it** on any week with fewer than ~3
scans, and every figure quoted off it silently gets worse over time. H1's per-day
mean read -12.1 on 09-11, -0.2 today, and **-10.1 after the fix** — three
different numbers for the same underlying data.

**Fixed:** cap raised to 45 days, `max_calls=300`. Restored to **11 trading days /
20 scans**.

**Not fixed, and the durable answer:** graded outcomes should be **persisted**
rather than re-derived from bars on every run. No broker keeps M5 forever, so this
recurs at 45 days instead of 20 unless the outcome of a graded day is written down
once and kept. Recorded, not built — it is a storage design, not a one-line cap.

**Family:** a limit asserted in code with no report when it binds. The same shape
as D10's SUCCEEDED-on-nothing and D11's `pushed=True` from an exit code. **Silence
on a failed assumption is the recurring defect in this project, not any individual
miscalculation.**

# Analysis 2026-09-16 — 11 trading days, 20 scans

## The walls are the product. Everything else is still noise.

Every post-fix ladder graded from its own publication, deduped to one observation
per (day, side, 25pt bucket):

**17 reached and judgeable. 17 HELD. Zero lost.** Median worst excursion
**8.2pts**, worst case 24.1pts. Spread across six days (08-27, 09-08, 09-09,
09-10, 09-11, 09-14).

**The binding limitation is reach, not accuracy:**

| | rungs | reached |
|---|---|---|
| C1–C3 | 40 | 11 (**28%**) |
| P1–P3 | 41 | 6 (**15%**) |

A level that holds 100% of the time but is reached once in four is a good signal
with a distribution problem. **H11's proximity claim is the live issue, and it is
worse on the put side** — which is also where D7's budget filter used to drop
levels, so the two compounded.

**Role, once reached:** C rungs split 6 support / 5 resistance; **P rungs went
resistance 4 of 6.** That is the direction H14 predicted, now at 6 observations
rather than 4, but it remains a side-note rather than a finding.

## Direction: 9 right / 6 wrong / 5 no-call

Marginally positive for the first time. 15 committed calls across 11 days is still
too few to separate from chance, and the 5 no-calls are not free — a NEUTRAL
printed on a day that moves 280pts (09-10 08:12) is a miss the scoreboard does not
charge for.

## Strategy selection, on the corrected post-scan statistic

Graded from each scan forward, never against price that predates it (the flaw that
withdrew H7's headline):

**Overall 10 right / 12 wrong** across 22 judgeable scans — below a coin flip.
By day, which dedups the eight near-identical 08-24 scans: **4 right / 3 wrong**.

**The split by date is the interesting part:**

| period | scans | right | wrong |
|---|---|---|---|
| 08-24 → 09-09 (pre-fix) | 17 | 5 | 12 |
| **09-10 → 09-14 (post-fix)** | **5** | **5** | **0** |

**Do not read that as proof.** Five scans over three days, and two more days
(09-14 13:04, 09-15) came back `mixed` and were excluded. But there is a plausible
mechanism rather than pure coincidence: **D12** made the board reprice greeks at
current spot on 09-10, which changes the flip, and the flip is what selects the
strategy. If the pre-fix flip was being computed from stale greeks, a bad strategy
pick is exactly what that would produce.

**This needs two more clean weeks before it means anything.** Recorded as the
thing to watch, proposed as nothing.

## Fuel

H1 per-day **-10.1pts over 11 days** — the budget still over-forecasts range
extension, but the effect has weakened as the sample grew (it read -30.1 at 7
days). The low-reading asymmetry holds at **4 of 5**: EXHAUSTED/LOW_FUEL calls
were near-exact on 08-25, 09-08, 09-10 and 09-11 13:24, and wrong by 89 on
09-11 12:47.

## What this says about where the effort should go

1. **Stop tuning the direction score.** 15 committed calls cannot distinguish a
   +4 from a -4 weighting, and every hour spent there is an hour not spent on
   the one thing that measurably works.
2. **The walls need REACH, not accuracy.** 100% held is not improvable; 22%
   reached is. That is H11, and it is the highest-value open question in the
   register.
3. **Persist graded outcomes** (D16's durable half), or this analysis cannot be
   reproduced in six weeks.

## The 17/17 needs a large qualifier: 12 of them were PIERCED first

Measured 2026-09-16, and it changes what the walls can be used for.

`settled_read()` judges a level **after price has chosen a side**. It says nothing
about what happened on the way there. Splitting the same 17 observations by
whether price ever *closed* through the level first:

| | count | detail |
|---|---|---|
| held cleanly — never closed through | **5** | tradeable at the touch |
| **pierced, then reclaimed** | **12** | **median pierce 65pts, max 223.7pts** |

So the honest statement is **not** "these levels hold". It is:

> **Once price settles a side, the level defends it to a median wick of 8.2pts
> (75th 11.5, max 24.1). Getting to that point often costs a 65-point excursion
> through the level first.**

**This makes the walls a CONFIRMATION signal, not an entry-at-touch signal.**
Buying a put wall on first touch with a 25pt stop would have been stopped out on
12 of 17 occasions before the level did its work. That is exactly the mistake the
old board text invited ("expect a bounce and a good long-sweep here") and which
H14 half-corrected.

**Geometry for anyone building a rule on this:**

- adjacent ranked walls sit a **median 150pts apart** (min 50, max 400)
- spot to the nearest wall is a **median 71pts above / 79pts below**
- the retest wick after settling is **median 8.2pts, max 24.1pts**

So a retest entry with a ~30pt stop targeting the next wall is roughly **5:1** on
the full gap, ~2.5:1 to the nearest one. **That arithmetic is not a backtest** —
it has no entry timing, no slippage, no account of the setup failing to appear —
and the setup only appears because a rung is reached, which happens 28% of the
time on the call side and 15% on the put side.

**What 17/17 does establish:** the *location* is real. **What it does not:** that
a trade at that location wins.

## D14 and D15 fixed (2026-09-16)

**D15 — the path read no longer measures reachability with the range budget.**
`path_read()` compared each brake's distance against `remaining_budget`, so on an
EXHAUSTED day every distance was "beyond" a budget of zero and the comparison
stopped carrying information. It is now floored:

```
reach = max(budget, adr * 0.25)
```

No new model, and the constant is evidenced rather than chosen: the smallest
full-session traversal recorded is about **0.35× ADR**, and on 2026-09-10 price
travelled **463pts against a 206pt budget**. A quarter of ADR is deliberately
conservative against that. The renderer no longer cites the budget as a distance
at all — "beyond today's 0pt budget" was the phrase that made the nonsense
visible.

Verified on a live build with `budget 0.0`, `ADR 357.6` → reach 89.4: a brake
305pts away still reads *mostly clear* (correct), where a brake 6pts away now
reads *has friction* instead of clear (the 09-11 failure).

**D14 — a zero is treated as absent, not as a price.** `gexbot.levels()` runs
every strike field through a `strike()` helper that returns `None` for a falsy
value **or** for anything more than 20% from the feed's own spot. Absent figures
render as "—", the section says *"No volume has traded yet today"* out loud, and
the flip cross-check skips itself because it already guarded on truthiness.
`volume_fields_absent` is exported so **H12 and H13 can refuse to count a scan
with no volume in it**.

This mattered daily, not occasionally: the scheduled 12:45Z scan lands 45 minutes
before the US open every weekday, which is exactly the window that produces the
zeros.

Five consistency checks added across the two. **36 offline checks passing.**

## H11 acted on — ranked rungs are now chosen from within reach

The measurement that settled it, across 102 post-fix rungs on 6 sessions —
hit rate against distance from spot at publication:

| distance | as ADR | reached |
|---|---|---|
| 0–50pts | 0.14 | **92%** |
| 50–100 | 0.28 | **58%** |
| 100–150 | 0.42 | 22% |
| 150–200 | 0.56 | 33% |
| 200–300 | 0.85 | 6% |
| 300–500 | 1.41 | 8% |
| 500+ | — | **0% (0 of 19)** |

**Inside 0.6× ADR: 22 of 39 reached (56%). Outside it: 3 of 63 (5%).** The window
is that cliff. It is measured, not chosen.

`gex_chart.collect()` now ranks C1–C3 / P1–P3 among bars within `adr * 0.6`.
Expected effect on the headline number: the ladder went from **25% of ranked
rungs reachable to roughly 56%**.

**Far heavy strikes are DEMOTED, not dropped** — they ride in `context_far` with
no C/P rank, because a rank is a promise about tradeability. That is D7's lesson
applied before the mistake rather than after it.

Verified on the 2026-09-16 20:26Z build (spot 28,946.5, reach 215pts):

- **old C1 would have been 29,301 at +354pts** (net +2.190bn) — the heaviest bar
  on the chain, in a band with an 8% historical hit rate
- **new C1 is 29,151 at +204pts** (net +0.083bn), inside the window
- 29,301 / 29,451 / 29,551 demoted to context, still visible

### The honest tension this creates, recorded rather than papered over

**Reachability is now guaranteed; significance is not.** Today's C1 carries
**0.083bn against the demoted strike's 2.190bn — 26× weaker.** On a day when all
the force sits far away, the C-rungs will be thin, and the ladder will rank
something barely worth the name.

No minimum-force threshold was added, deliberately: that would be an invented
number, and it would mean some days produce no ranks at all. The `$bn` figure and
the ●●●○○ rating are both already on the board, so the strength is visible and the
trader can judge it.

**New open question:** does a weak-but-near rung behave like a strong one? Every
observation so far is of rungs that were heavy AND near. **Unknown, and the new
ranking will start generating exactly the data needed to answer it.** Nothing
proposed.

Four consistency checks added. 40 offline checks passing.

## H11 REVERTED the same day — the reach window now runs as a shadow

**The trader called this, and he was right.** The published ranking is back to
force-across-the-chain, exactly as it was before 2026-09-16. The reach-window
scheme is computed on every build and persisted under `shadow`, rendered nowhere.

### Why the revert is correct and the original change was not

The *reach* measurement is solid — 22 of 39 rungs reached inside 0.6× ADR against
3 of 63 outside. What was never measured is **the consequence**: whether a rung
that is near but weak defends its level the way a rung that is heavy and near
does.

**Every one of the 17 observations behind the playbook is of a rung that was
heavy AND near.** The playbook's numbers — median retest wick 8.2pts, worst 24.1,
which is what makes a 30pt stop viable — are calibrated on that population. A
reach-ranked C1 is a different population. On 2026-09-16 it would have carried
**0.139bn against the 2.131bn strike it displaced, 15× weaker.**

So the change swapped the levels he trades for levels whose behaviour is unknown,
on the strength of an argument rather than an observation. **That is precisely
what the 3-day evidence gate exists to prevent, and I walked through it** —
having spent the same session writing that walls need REACH not accuracy, which
made the argument feel like evidence. It was not.

### What runs now

| | ranking | rendered | purpose |
|---|---|---|---|
| `ranked_positive` / `ranked_negative` | heaviest within sign, whole chain | board + chart | what he trades |
| `shadow.ranked_*` | heaviest within sign, inside 0.6× ADR | **nowhere** | graded later |

Both come from **one build on one set of bars**, so they can be graded against
identical price action — no drift, no separate fetch, none of the 16-second
divergence that caused the earlier chart/brief mismatch.

Verified on the 20:38Z build (spot 28,951.5, reach 215pts): published C1 is
29,306 at +354pts / 2.131bn, shadow C1 is 29,156 at +204pts / 0.139bn, and
`shadow` appears nowhere in the rendered brief.

### How to settle it

After ~3 weeks of ladders carrying both, grade each with `wall_retro.py` on the
same days and compare on **two** axes, because they trade against each other:

1. **reach** — what fraction of ranked rungs price actually touched
2. **quality** — of those touched, the held rate and the retest wick

The reach window is expected to win axis 1 by construction. **It only wins
overall if axis 2 holds up**, and that is the open question. If the wick widens
materially past ~25pts, the window buys setups that cannot carry a 30pt stop, and
the current ranking stays.

**Do not read a shadow-vs-published comparison before 3 weeks**, and do not
switch on axis 1 alone.

## Does gamma sign change how a wall behaves? Measured 2026-09-16

Two different things get called "gamma" here and they must not be merged:

1. **The rung's own sign** — a C rung is call-dominant (dealers long gamma, a
   brake); a P rung is put-dominant (dealers short gamma, an accelerant).
   Per-strike.
2. **The day's regime** — price above or below the flip. Whole-session.

Split the 17 observations both ways:

| split | n | pierced | median pierce | median wick after settling |
|---|---|---|---|---|
| **C rung** (positive) | 11 | 64% | **53pts** | 8.2 |
| **P rung** (negative) | 6 | 67% | **119pts** | 7.9 |
| **LONG gamma day** | 13 | 62% | **59pts** | 8.2 |
| **SHORT gamma day** | 4 | 75% | **116pts** | 6.5 |

### Three findings, in descending order of confidence

**1. The retest wick is flat everywhere — and this is the strongest claim.**
Across all eight cells it sits between 3.4 and 9.2pts. Once price settles a side,
the level defends it just as tightly in negative gamma as positive. **The 30pt
stop survives in every regime.** This is what makes the playbook's procedure
regime-independent.

**2. Pierce DEPTH roughly doubles in negative gamma — 53 → 119pts by rung sign,
59 → 116pts by day regime.** It shows on both splits independently, which is weak
corroboration rather than one artefact counted twice. The mechanism agrees:
short-gamma dealers amplify, so an excursion through the level runs further.

**3. Pierce RATE barely moves — 64% vs 67%, 62% vs 75%.** No detectable effect,
and with n=17 none would be detectable unless it were large. **Gamma does not
appear to change WHETHER a wall holds. It changes how far price travels while
deciding.**

### The practical consequence

**The procedure is unchanged — arrive, hands off, wait for the settle, trade the
retest.** What changes is the geometry of the wait: in negative gamma expect to
sit through roughly **twice the excursion** before the level becomes tradeable,
so the retest arrives from further away and later.

That argues for *patience*, not for a different play, and explicitly **not** for a
wider stop — the wick data says the stop stays at 30.

### Caveats

n=17, and the three-way cells are n=1 to n=10. The eye-catching cell — **P rung
on a SHORT gamma day pierced 3 of 3 at a median 116pts**, the trapdoor
combination — is **three observations**. Mechanistically it is the case where
rung and regime both amplify, so it should be the worst, but it is not evidence
yet. Only 4 of 17 observations are short-gamma days at all, which is the binding
limit on findings 2 and 3.

**Nothing proposed. The playbook stands as written** — its procedure is confirmed
regime-independent, which is the useful result here.

---

# Observations appended 2026-09-17 (grading the 2026-09-16 session — FOMC, hike 3.75% -> 4.00%)

Full grade: `journal/2026-09-16/REVIEW.md`. Three proposals were made there
(P-A straddle-rider sign, P-B held/lost tolerance, P-C event gate), all at
>=3 sessions. What follows is the material that did **not** reach threshold.

## H20 (NEW, OBSERVING) — do scheduled High-impact events blow the fuel budget?

The 12:46Z PRE_NY scan budgeted 145.6pts of extension with FOMC 5.2h away.
Actual extension 282.0, error **+136.4** — the largest in the record. The only
other scan in the journal with a High-impact print inside its own forecast
session is 2026-09-10 08:12Z LONDON (PPI 4.3h away), error **+114.6** per scan.

**These are the two largest positive fuel errors in the whole 12-day record.**
Next largest is +79.4 (09-14, no event). Per-day mean is +2.1.

**n = 2. Nothing proposed.** This is deliberately kept separate from P-C, which
proposes a prose/gating change on the "gate has never fired in 21 scans"
evidence and explicitly proposes **no** score or budget change.

**Watching:** the fuel error on every session containing a scheduled High-impact
event. **Threshold: 3 such days.** 2 of 3. If it reaches 3 in the same direction,
the candidate change is a budget multiplier on event days — and note in advance
that a multiplier fitted to 3 points that are all large-positive will fit the
tail, not the level (the H1 lesson).

## H21 (NEW, CLOSED-NEGATIVE) — VIX9D/VIX does not predict the fuel error

Worth recording precisely because 09-16 makes the opposite look obvious: the
backwardation row (`vol -2`, "expect range expansion") was the **only** component
that called the 494pt day, and it was outvoted +4 to -2 by two gamma pinning rows.

The tempting change is to let term structure scale the fuel budget. The data
says no:

| VIX9D/VIX (first scan) | fuel error (per day) |
|---|---|
| 0.790 | +61.2 | 
| 0.817 | +79.4 |
| 0.834 | -10.7 |
| 0.855 | -73.0 |
| 0.887 | -86.4 |
| 0.888 | -11.6 |
| 0.931 | -26.2 |
| 0.950 | -64.0 |
| 0.954 | +57.3 |
| 0.992 | -81.3 |
| 1.043 | +44.3 |
| 1.001 | +136.4 |

**Pearson r = 0.053 over 12 days. No relationship.** The three backwardated /
near-flat days are +44.3, **-81.3**, +136.4 — opposite signs.

**Closed negative.** Do not connect term structure to the budget. If this is
revisited, it needs a mechanism and a fresh sample, not these 12 points.

## Unarbitrated conflict: two gamma rows vs one vol row

Not yet a hypothesis, recorded so it can become one. On 09-16 the table contained
both `gamma +2 "week net GEX 3.111 -> pinning likely"` and
`vol -2 "BACKWARDATED — expect range expansion"`. These are direct contradictions
about the same quantity (how far price will travel), and the engine simply sums
them. The pinning rows won on points and produced the headline
*"Expect a tight, pinned range... breakouts mostly fail"* on a 1.38x-ADR day.

**Watching:** how often net-GEX-pinning and vol-expansion rows co-occur, and who
is right when they do. **Threshold: 3 co-occurrences.** 1 of 3 (09-16).

## H17 — no new data point

Sub-5%-of-range graded direction calls: **still 1 of 3 days** (both instances
remain 2026-09-11). 09-16's post-scan move was -129.5 = **26.2%** of range and
does not add.

**Related but distinct, n=1, opened here only as a note:** 09-16 closed **+1.0**
on a 494pt range — |net|/range = **0.00**, by far the flattest in the record
(every other day is 0.24-0.69). The scan was graded WRONG on the scan-relative
move, which is the right grade; a close-to-close grade would have scored it
CORRECT on a one-point move. **No change proposed and no threshold set** — this is
an argument *for* the current scan-relative grading, recorded so the next flat day
is not mistaken for a new finding.

## Max pain's day-of-week qualifier — one instance against

The brief prints max pain as *"weak on a Monday, strong by Thursday/Friday"*. On
**Wednesday** 09-16, max pain 29190.2 was the **best level on the board**: held as
resistance 170 minutes, worst excursion 22.6pts, and the only level above spot
that held anything. Everything else on the board lost.

**n = 1. Nothing proposed.** Watching whether the qualifier's midweek prediction
keeps failing. **Threshold: 3 days where max pain is touched.** Across the record
max pain has been touched on only 2 of the 6 days it was published, so this will
accumulate slowly.

## Level-kind touch rates, 12 days (context for P-B, not a proposal)

Unique (day, price) published levels, deduped within a day:

| kind | published | touched | rate | held / touched |
|---|---|---|---|---|
| liquidity | 83 | 60 | 0.72 | 0.57 |
| gamma | 63 | 34 | 0.54 | 0.74 |
| structural | 18 | 5 | **0.28** | 0.60 |
| magnet | 11 | 10 | 0.91 | 0.70 |
| gamma-shelf | 10 | 8 | 0.80 | 0.50 |

Structural walls have the lowest touch rate by a wide margin. **This is not
proposed for removal** — a far outer boundary is supposed to be rarely touched,
and 3 of the 5 touches held. Recorded because it is the single biggest drag on
the headline hit-rate denominator (H6), and because P-B's clustering proposal
would change all five of these numbers; re-measure after P-B, not before.

## The `events` component has never scored

14 rows across the journal, **all 0 points** — it is hard-coded
`add("events", 0, ...)` and only ever lists earnings. Combined with the event
gate never firing (P-C), the model has no channel at all through which a
scheduled macro event reaches the output. Noted as the mechanism behind P-C, not
as a separate proposal: adding points for events would be a scoring change on
n=2 outcome evidence (see H20).

---

## P-A is D16, re-found — cross-reference added 2026-09-17

The 09-16 review raised **P-A**, "the straddle rider adds +1 on both ternary
branches at `bias_engine.py:86-89`". That is **D16**, filed 2026-09-15 from the
09-11 review: same file, same lines, same `+1 if px > gf else +1`, same reading
that a row captioned "reduce conviction" enlarges the vote above the flip.

Recorded here rather than by editing either entry, because the two were reached
independently and the second one **adds evidence**: three dated firings
(09-09, 09-11, 09-16), and the note that 09-16 lands exactly on the +3 boundary
where a label could flip. That evidence belongs to D16.

**It is not a second defect, and must not be counted as one.** D16 has one
instance count, not two. Anyone reading the register for how many scoring
defects are open should count this once.

Same failure mode as the H12/H13 collision corrected on 09-15: an entry arriving
under a fresh name for something the register already holds. The register's own
rule from H1 applies — one object, one name. A reviewer opening an item should
grep the existing D- and H- entries for the file and line it is about, not only
for the wording it would use.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

---

# Observations appended 2026-09-18 (grading the 2026-09-17 session — day after the FOMC hike)

Source: `review_day.py 2026-09-17 --json`, 1 scan, 0 test artefacts. `track.py`
at 13 trading days / 22 deduped scans. The session was O 28983.4 / H 29500.5 /
L 28955.7 / C 29430.9, range 544.8 (1.47x ADR), net +447.5 — but **the whole
move was pre-scan** (`range_at_scan` 504.8 of 544.8; post-scan +9.4), so this day
grades almost nothing about direction. Bias was −2 NEUTRAL, no call.

## D18 (NEW) — the news scorer cannot read a bullish headline that contains a bearish keyword

**Two independent defects in `news_scorer.py` that compound.** Reproduced from
source on 2026-09-18:

```
'Nasdaq, S&P 500 Futures Rebound After Fed Rate Hike...'           rule=hawkish  dir=-1  conf=HIGH  flags=[]
'S&P 500, Nasdaq, Dow Futures Inch Higher As Investors Digest...'  rule=hawkish  dir=-1  conf=HIGH  flags=[]
'Stock Market Today: Dow Rises On Surprise Inflation Data; ...'    rule=cpi_hot  dir=-1  conf=HIGH  flags=[]
'Nasdaq, S&P 500 Futures Surge As Wall Street Cheers US-Iran...'   rule=hawkish  dir=-1  conf=HIGH  flags=[]
```

Every one of these headlines states, in its own text, that the index went **up**.
All four were **counted**, at **HIGH** confidence, with **no flags**, each voting
**−1**.

1. **First-match-wins over an ordered rule list.** `score_item` iterates `RULES`
   and **returns on the first regex hit**. `hawkish` sits at **line 71**;
   `risk_on` (`rally|surge|soar|jump|rebound|…`) at **line 109**. A headline
   holding both "rate hike" and "rebound" is structurally incapable of being read
   as anything but hawkish — the competing evidence in the same sentence is never
   examined.
2. **`HIGH_CONFIDENCE` is asymmetric.** It contains `hawkish`, `cpi_hot`,
   `cpi_cool`, `dovish`, `jobs_strong`, both tariff rules, `earnings_beat/miss`,
   `capex_up/down`, `credit_stress`, `shutdown` — and **not `risk_on`**. The
   bearish reading wins the race *and* is the only one permitted to vote.

The flag machinery does not help: `REVERSAL_UP`, `CONTRAST`, `MODAL` and
`HYPOTHETICAL` are all empty on "Futures Rebound After Fed Rate Hike" — "after"
is not a contrast token.

**Evidence: 3 trading days, 5 headline instances.**

| day | scan | headline (truncated) | rule | counted? |
|---|---|---|---|---|
| 2026-08-24 | 08:28–08:33 | "Nasdaq, S&P 500 Futures **Surge** As Wall Street Cheers US-Iran Deal, **Brushes Off** Hawkish Fed" | `hawkish` | yes, −1 (net that scan was +1, offset by `cpi_cool`) |
| 2026-09-11 | 12:47 | "Dow **Rises** On Surprise Inflation Data; AI Name Oracle **Jumps** On Earnings" | `cpi_hot` | yes, −1 (scan block −4, 0 bull / 4 bear) |
| 2026-09-11 | 13:24 | "Dow **Rallies** On Surprise Inflation Data; Nvidia **Rebounds**, Oracle Jumps" | `cpi_hot` | yes, −1 (scan block −4, 0 bull / 10 bear) |
| 2026-09-17 | 12:46 | "Nasdaq, S&P 500 Futures **Rebound** After Fed Rate Hike" | `hawkish` | yes, −1 (scan block −2, 0 bull / 4 bear) |
| 2026-09-17 | 12:46 | "S&P 500, Nasdaq, Dow Futures **Inch Higher** As Investors Digest First Rate Hike Since 2023" | `hawkish` | yes, −1 (same block) |

**Relationship to existing entries — this is neither of them.**

- **Not D9.** D9 is the same family ("a keyword without its subject") but the
  **opposite sign and zero damage**: there a bearish headline took a bullish tag
  and fell into NEEDS_JUDGEMENT, scoring 0. D9's closing line asked that a
  recurrence be *counted rather than rediscovered* — D18 is that count, and
  unlike D9 these votes were cast at full weight.
- **Not H19.** H19 concerns which headlines get **sampled**. D18 concerns the
  **sampled subset being misread**, which H19 assumes away. H19's hand-score test
  is unaffected and still unrun.

**Status: FILED, deliberately NOT PROPOSED FOR IMMEDIATE FIX.** Threshold is met
and the change is small, but it alters a **scoring input**, and H19's unrun
hand-score test needs the current scorer as its baseline. Fix when H19 resolves
or when `news_scorer.py` is next opened, whichever is first. Candidate fix:
evaluate **all** matching rules rather than returning on the first, and demote to
NEEDS_JUDGEMENT when a bearish-regime rule and a market-direction rule both match
the same headline — the honest answer there is "a human should read this", not a
guess at the sign.

## H18 — fifth instance; sequence extended, no damage this time

DFII10 again scored **−3** on 09-17 with the `why` string itself saying *"FRED has
not published since 2026-09-15 (2 business days ago) — this is last week's
reading, not today's."*

`09-10 0, 09-10 0, 09-11 −3, 09-11 −3, 09-14 −3, 09-14 −3, 09-15 −3, 09-16 0, 09-17 −3`

**Damage today: none.** Total −2; without the stale −3 it is +1, and both are
`NEUTRAL / TWO-WAY`. No label flipped, no call changed. Recorded because a
component that votes on data it has itself flagged as missing is a defect
independent of whether the day punishes it. **P1 already covers it. No new
proposal.**

## H1 — zero-budget bucket doubles its MAE, and the estimator is one-sided

09-17: budget **0.0** → extension **40.0**, error **+40.0**. This is the
**largest zero-budget error on record**, beating 09-14 17:23's +26.6.

| budget | scans | errors | MAE |
|---|---|---|---|
| **= 0.0** | **4** | 0.0, 0.0, +26.6, **+40.0** | **16.7** (was 8.9 at n=3) |
| **> 0.0** | 8 | −86.4, −10.7, −26.2, −64.0, +114.6, +88.7, +132.2, −81.3 | ~75.5 |

The zero/non-zero split survives — 16.7 against 75.5 is still a factor of 4.5 —
but the "keep the number when it is zero" half of **P4** is weaker than it looked
at n=3, and the trend is one-way.

**The structural point, which should be written down before P4 is decided:** when
the budget is 0.0 the error is `extension − 0 = extension`, and extension cannot
be negative. **A zero budget can only ever be wrong in one direction.** Its MAE
is therefore a biased estimator that can only rise as the sample grows, and the
8.9 → 16.7 move is partly the sample filling in, not the model degrading. The
zero bucket's low MAE is **not** evidence that a zero budget is a good forecast;
it is evidence that days which exhaust their budget usually do not extend much
further. Those are different claims and P4 currently rests on the first one.

Per-DAY error across 13 days now: mean **+5.0** (`track.py`). Dispersion without
bias, unchanged. **No new proposal.**

## The gamma-pinning vs vol-expansion conflict now has one instance on each side

Logged 2026-09-17 as an unarbitrated conflict. Both sides now have a day:

| day | `gamma` pinning rows | `vol` backwardation row | outcome | who was right |
|---|---|---|---|---|
| 09-16 | +2 "pinning likely" | −2 "expect range expansion" | 1.38x ADR, largest traversal on record | **vol** |
| 09-17 | +2 "pinning likely" | −2 "expect range expansion" | extension 40.0 on a 0pt budget, price traversed 186.6 **inside** | **gamma** |

One each. **n=2, nothing proposed.** Recorded because the conflict is real and
neither row is reliably the better one — which is an argument for arbitration
rather than for deleting either. What would settle it: whether the *combination*
(positive net GEX **and** backwardated VIX9D/VIX) resolves toward expansion or
pinning across ≥3 more instances. Record both values every scan.

## Max pain's day-of-week qualifier — second instance against, in the opposite direction

The qualifier reads *"weak on a Monday, strong by Thursday/Friday"*.

- **09-16 (Wednesday):** max pain was the **single best level on the board** —
  held as resistance 170min, worst excursion 22.6pts.
- **09-17 (Thursday):** max pain was **never reached**, nearest approach 245.8pts.

Two instances, both contradicting the qualifier, in **opposite directions** —
which is weaker evidence than two in the same direction, and consistent with the
qualifier simply carrying no information. **n=2 of the 3 required** (threshold:
3 days on which max pain is published; touched is not required, since a miss on a
Thursday is itself evidence against). Nothing proposed.

## `events` has now scored 0 on 15 of 15 rows

Including **the day after an FOMC rate hike**. Unchanged mechanism
(`add("events", 0, ...)`, earnings only), unchanged status: this is the mechanism
behind **P-C**, not a separate proposal.

## New observation — the board has no field for "price already tested this today"

The 09-17 brief presented the 29451.5 call wall as **"+26 away"** and offered
*"a held close above flips that selling to buying and it becomes a launchpad"* as
a forward scenario. Inferred from the graded numbers (`range_at_scan` 504.8 above
a session low of 28955.7, and the low is provably pre-scan because post-scan
traversal was only 186.6), **the pre-scan high was 29460.5 — 9.0pts above that
wall.** The level had already been tested and rejected that morning.

The level board carries `dist`, `reach`, `stretch` and `confluence`, and **no
field for prior-session interaction with the level**. Same shape as the H1
sub-observation of 09-16 (the fuel block reports no distance to existing session
extremes, so the prose cannot say "the move available is back to the low"): the
generator lacks the field it would need to say the true thing. **n=1. Logged, not
proposed** — and if it recurs, it and the H1 sub-observation are probably one
proposal about session-context fields, not two.


---

## Proposal index, reconciled 2026-09-18

The register now carries **two parallel proposal series** and they are not the
same sequence: **P1–P5** (numeric, opened by the 09-14 and 09-15 reviews) and
**P-A–P-D** (lettered, opened by the 09-16 and 09-17 reviews). "P1" and "P-A"
are different proposals about different code. Nothing is mis-numbered, but the
two schemes cannot be read as one list, and anyone asking "how many proposals
are open" gets no answer from a grep.

Left in place rather than renamed: both series are already referenced by name
inside committed REVIEW.md files, and renaming would break those citations to
fix a cosmetic problem. The index is the fix.

| id | claim | status |
|---|---|---|
| P1 | FRED staleness — macro scores a frozen series at full weight (= H18) | standing, strengthened 5 sessions |
| P2 | prior-week-range rule needs a reclaim term (H10) | 0-for-4, did not fire 09-15 |
| P3 | exclude `kind: structural` from the level hit rate | standing |
| P4 | stop quoting a point-precise budget above zero | standing; see the one-sided-estimator caveat below |
| P5 | grade the secondary gamma table (107 publications, 0 graded) | standing, must land with/after P3 |
| P-A | straddle-rider ternary sign | **NOT a separate item — this is D16**, see the 09-17 cross-reference |
| P-B | held/lost verdict unstable inside the grader's tolerances | standing, measurement only |
| P-C | event gate unreachable — 0 fires in 21 scans | standing |
| P-D | board filter inverts at zero budget | standing, overlaps P-B(b), re-measure together |

Sequencing already recorded across the reviews, repeated here because it is
scattered: **P3 before P5** (P5 enlarges the hit-rate denominator), **P-B and
P-D together** (both move the same numbers), and **H6 read only after both**.
P-A is not a fifth lettered proposal; D16 holds that evidence.

A future review opening a proposal should continue the **lettered** series from
P-E, and grep this index first.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

---

## D19 — one absent vol series took down the whole brief

**2026-09-21, found while re-running the scan to answer "the walls are all below
price".** `brief.py:906` rendered the volatility header with

```python
f"VIX9D/VIX **{term}** -> {v['term_read'].split(' — ')[0]} · "
```

`macro_probe` sets `term_read` to `None` whenever the VIX9D/VIX ratio cannot be
formed — a deliberate, correct null. `.split()` on it raises AttributeError and
kills the entire brief: no call, no levels, no fuel, no journal entry, exit 1.

**Twelve lines below, the same value is already guarded** (`if term is not
None:`). The None case was anticipated for the prose paragraph and missed on the
header line, so the document died for the one clause that could have read "n/a".

Seen twice. 2026-09-14: a 429 lost `_VIX9D` mid-scan. 2026-09-21: CBOE served
`_VIX9D` with `last: None` and **`error: None`** — a successful fetch of an
empty value, which no retry logic would have caught, because nothing failed.

It was first identified on 09-14 and **left unfixed**, on the reasoning that the
day's other failures were rate-limit crashes a null-guard would not have saved.
That reasoning was about that day, not about the defect, and it cost the 09-21
scan as well.

### Fix

The header degrades to `VIX9D/VIX **n/a** -> n/a (VIX9D unavailable)` and the
brief renders in full. One absent optional series now costs one clause.

### Note on the intermittency

The direct probe returned `last: None` and the scan two minutes later returned
0.827, so the gap is **intermittent, not a sustained outage**. When this was
diagnosed live the conclusion "a retry will not help" was stated and was wrong:
a retry would have helped that minute. The guard is still the right fix — it
holds whether the gap lasts two minutes or all day, and D17's retry logic cannot
see this case at all, since the HTTP call succeeds.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

---

# 2026-09-18 (graded 2026-09-21) — observations appended

## D18 — fourth trading day, eighth headline instance

Reproduced from source again on 2026-09-18's own three scored headlines. Two of
the three contain an explicit upward direction word in their own title:

```
'Stock Market Today (Sept. 18, 2026): Nasdaq futures RISE after Fed rate hike lifts stocks'
   -> rule=hawkish  dir=-1  conf=HIGH  flags=[]  weighted=-1.8
"What the Fed's interest rate hike reveals about Warsh, Trump and inflation"
   -> rule=hawkish  dir=-1  conf=HIGH  flags=[]  weighted=-1.8
'Exchange-Traded Funds, Equity Futures HIGHER Pre-Bell Thursday ... Fed Rate Hike'
   -> rule=hawkish  dir=-1  conf=HIGH  flags=[]  weighted=-1.8
```

Day count **4** (08-24, 09-11, 09-17, 09-18); headline instances **8**.
Component reported "0 bull / 3 bear -> MILDLY BEARISH", worth **-1**.

**Damage on 09-18: conviction, not label sign.** Net +4 MILDLY BULLISH; without
the news -1 and the stale macro -3 it is +8 BULLISH. Day closed **+234.9 (68% of
range) in the called direction**. So the defect suppressed a correct call by one
label notch rather than flipping a wrong one.

**Status unchanged: FILED, NOT PROPOSED.** The blocker was never the evidence
count — it is that this is a **scoring input** and **H19's hand-score test is
still unrun**, so a fix now destroys H19's baseline. More days do not unblock it.

## D20 (NEW) — `freshness` scores yesterday's headline at full weight

Separate defect, same 09-18 news block, **opposite axis to D18** (D18 is sign,
this is age). Headline 3's own title reads *"Pre-Bell **Thursday**"*. It was
scored on **Friday 09-18** with **`freshness: 1.0`** — full weight, no decay.

A headline that names its own weekday, one day stale, should not carry the same
weight as a same-session print. **n=1. Watching only.** If it recurs twice more
it is a one-line change in the freshness computation. Not proposed.

## H18 — sixth instance; first time the stale row cost conviction on a CORRECT call

DFII10 scored **-3** on 09-18 with its own `why` string reading *"FRED has not
published since 2026-09-16 (2 business days ago) — this is last week's reading,
not today's."*

`09-10 0, 09-10 0, 09-11 -3, 09-11 -3, 09-14 -3, 09-14 -3, 09-15 -3, 09-16 0, 09-17 -3, 09-18 -3`

**Damage: one label notch, on a day the engine got right.** Every prior instance
either did no damage or sat on a day that was already wrong. This is the first
where removing the stale row would have produced a *stronger and more accurate*
call (+8 BULLISH vs +4 MILDLY BULLISH; actual +234.9). Worth recording because it
answers the standing objection that the stale row is harmless when it happens to
agree with the eventual outcome — here it disagreed with a correct call.
**P1 already covers it. No new proposal.**

## D21 (NEW) — `gamma -2` "top 20% of the wall band": first instance AGAINST

Record was unbroken: correct and outvoted 08-28, correct 09-08, *"the sharpest
row on the page"* 09-17.

**09-18 it was wrong.** Price sat in the top 20% of the band 29419.3-29519.3 and,
instead of poor risk/reward for longs, **left the band upward and never returned**
— the band's ceiling became the day's floor (call wall held as *support* 130min,
worst excursion -17.3). Session high **+185pts above** the band top.

Record **3 for / 1 against**. One counter-instance does not overturn three.
Logged so the row stops being treated as infallible. **Not proposed.**

## P-E (NEW, PROPOSED) — the call wall is bimodal; the prose asserts a lid

**Prose and board construction only. No scoring change.**

7 tested call-wall instances over 14 trading days (figures from prior REVIEW.md,
not recomputed):

| day | outcome | overshoot / run-through |
|---|---|---|
| 08-26 | capped | "best call of the day" |
| 09-08 | capped | +11.9 through, failed, fell 70.3 |
| 09-11 | capped | **+9.6**, held 485min |
| 09-14 | capped | **+3.6**, held 475min |
| 08-27 | **sliced** | closed +79 above, traded +154 above |
| 08-28 | **sliced** | ran +103 through |
| 09-18 | **sliced** | ran +185 through, closed +151 above |
| 09-15, 09-16 | never reached | untested, excluded |

**4 capped / 3 sliced, and the distribution has no middle:** capped overshoot
3.6-11.9pts, sliced run-through 103-185pts. **No instance between 12 and 103.**
The board describes this with one unconditional sentence — *"rallies stall. Take
profit into it"* — plus, on 09-18, an explicit *"CISD = short"* at the PDH. On
the 3 failure days that instruction sat on the wrong side of 103, 154 and 185pt
moves.

Not new analysis: the **08-27** review already wrote *"in a long-gamma regime a
call wall is a brake, not a lid… I described it as though it would stop one."*
That was never given a count. It has one now, and 09-18 is its largest instance.

**Explicitly NOT proposed: a discriminator for which mode.** Breadth is the
obvious candidate (09-18 was `breadth +3`, mega-caps 4/4, NDX leading ES, and it
sliced) but 09-08 capped on a positive bias too. Fitting a predictor to 7 points
split 4/3 is the noise-tuning the standing rule forbids. Named as the thing to
watch.

## H1 — n=14; the per-day aggregate is now essentially zero

09-18: budget 65.6, extension 26.7, error **-38.9**, `about right`.
Per-day mean moves to **+1.9 (n=14)**.

The series `+61.2 -11.6 -73.0 -86.4 -10.7 -26.2 -64.0 +57.3 +44.3 +79.4 -81.3
+136.4 +40.0 -38.9` has a mean of ~2 and a spread of over 200. **This is the
strongest argument yet against any global multiplier** — there is no bias to
correct, only variance. P4 not re-proposed.

## Negative result — "pinned range" does NOT predict chop

Worth recording so it is not rediscovered. 09-18's brief led with *"tight, pinned
range… breakouts mostly fail"*; range came in at **0.90x ADR** (correct) but net
move was **68% of range** — a trend day, every sweep succeeded.

Tested across all graded days, range-ratio -> |net|/range:
`0.78->38%  0.78->68%  0.90->68%  0.97->35%  1.27->55%  1.33->69%  1.37->27%
1.38->0.2%  1.47->82%`

Mean ~52% for sub-ADR days vs ~47% for above-ADR days. **No relationship in
either direction.** Pinning constrains the *range*; it says nothing about whether
the day is directional. The prose conflates the two, but the fix is not a new
rule — there is no signal here to build one from. **Rejected, not proposed.**

## Level clustering — clean instance for P-B(b)

09-18 published 9 levels, **5 inside the 100pt band 29419.3-29519.3**. With
`TOUCH_TOL` 8pts, one move at ~13:00 registered as "touching" three separate
levels within five minutes (12:55, 13:00, 13:25). `Options shelf 2.36bn` (29469.3)
sits 9.6pts from London Low and 12.3pts from the PUT WALL pair.

The 0.78 hit rate and the 7/7 held rate are therefore **not 9 independent
observations**. Folded into **P-B(b)** (cluster within `TOUCH_TOL` before
grading); not raised separately.

## Standing caution recorded — hit rate measures placement, not quality

09-18: hit rate **0.78**, 7/7 touched levels held. 09-16: hit rate **0.95**, 16 of
18 levels **lost**. On 09-18 every published level was at or below the scan price
on a +174pt day — the board was not tested, it was outrun.

**`level_hit_rate` and the held-rate are functions of where the levels sat
relative to price, not of whether the levels were good.** Both days' headline
numbers are uninformative about board quality in opposite directions. No claim
should be built on either without conditioning on side. n=2 clear instances.

---

# Observations appended 2026-09-22 (grading the 2026-09-21 session)

**The largest-range day in the journal: 958.4pts = 2.46x ADR14, net +847.7 =
88% of range.** Both are records by a wide margin — the entire prior
distribution of range ratios was 0.77–1.47. Every figure below is from
`review_day.py --json` / `track.py`; 1 gradeable scan, 0 test artefacts,
`is_trading_day: true`. The 2026-09-22 scan is excluded everywhere (incomplete,
179 bars, held back by track.py).

## P-F (NEW, PROPOSED) — the budget has no term for price already being outside the prior day's range

**Prose and strategy selection only. No score change, no multiplier.**

When `price_at_scan` sits >~150pts outside the prior day's high/low, the
`EXHAUSTED`/`LOW_FUEL` block should print the budget as unreliable in that state
and must not emit *"the day's range is set"*, *"continuation into new highs/lows
is the low-probability trade"*, or a fade-first strategy.

| day | price at scan vs prior day | budget | extension | per-day error |
|---|---|---|---|---|
| 09-14 | **−187.6 below PDL** 29018.3 | 61.9 | 194.1 | **+79.4** |
| 09-17 | **+174.5 above PDH** 29251.3 | 0.0 | 40.0 | **+40.0** |
| 09-21 | **+259.0 above PDH** 29704.2 | 18.7 | 587.9 | **+569.2** |

Three unambiguous instances, **all positive, on both sides of the range**. Plus a
marginal fourth: 08-24 (first scan 25pts below PDL, back inside by the PRE_NY
scan), **+61.2**.

**Control — the 11 days where price was inside the prior day's range at scan:**
3 of 11 positive, mean **−14.0**, median **−26.2**. The split is
`4/4 positive outside` vs `3/11 positive inside`.

**On 09-21 this is what the failure looked like.** ADR14 389.2, today_range
370.5, `adr_used_pct 95.2`, budget 18.7, `EXHAUSTED` — while price stood 259pts
above PDH and above the entire prior-week range. The brief printed *"this is your
fade day"* and `STRATEGY 1 — sweep -> failed re-break -> CISD reversal`. The range
extended 587.9 further and every sweep succeeded.

**Explicitly NOT proposed: a multiplier for this state.** Fitted to
+40 / +79 / +569 it would fit the tail, not the level. That is the H1 lesson.

## H22 (NEW, OPENED) — weekly net GEX does not predict realised range

The 2nd-highest net GEX on record produced the largest range expansion on record.
All 15 complete days, `inputs.gamma.this_week` vs realised range / ADR14:

| wkGEX | ratio | | wkGEX | ratio |
|---|---|---|---|---|
| 16.106 (09-17) | **1.47** | | 1.810 (09-11) | 1.27 |
| 9.693 (09-21) | **2.46** | | 0.557 (09-09) | 0.82 |
| 9.223 (08-27) | 0.78 | | 0.067 (08-24) | 1.18 |
| 7.980 (08-28) | 0.97 | | −0.058 (09-10) | 1.33 |
| 7.697 (09-18) | 0.90 | | −1.461 (09-15) | 0.77 |
| 5.225 (08-25) | 0.97 | | −2.103 (08-26) | 0.82 |
| 3.407 (09-08) | 0.93 | | −6.295 (09-14) | 1.37 |
| 3.111 (09-16) | 1.38 | | | |

**Pearson r = 0.269 (n=15); 0.052 without 09-21.** Mean ratio for GEX ≥ 5 is 1.26
vs 1.10 below — but the **medians invert** (0.97 vs 1.18). No relationship. Same
shape as H21 (VIX9D/VIX vs fuel error, r = 0.053, closed negative).

The `gamma +2 "pinning likely"` row scores a *direction* claim, which is not in
question; the issue is that its text drives *range* prose. The candidate change is
to strip the range language from it. **Deliberately not proposed this cycle** —
P-F is a prose change to the same block, and shipping two at once makes neither
measurable. **Status: OPEN, one change at a time.**

## H3 — THE SEPARATOR ARRIVED, and it points the other way

The register has asked since 09-15 for *"one max-conviction BULLISH call printed
at a session high"* to separate over-commitment-at-extremes from a plain bearish
skew. **2026-09-21 is it.**

`+13 STRONGLY BULLISH` printed at 29963.2 — ~92% up the range established at
scan, 31pts under the session high (London High 29994.0), in the top 20% of the
wall band, on `EXHAUSTED` fuel with an 18.7pt budget. **CORRECT by +537.9**, on a
day that closed +847.7.

All three contaminating instances (24 Aug 13:45, 25 Aug 13:04, 14 Sep 13:04) were
max-conviction **bearish** calls printed at **lows**, all wrong. The first
max-conviction **bullish** call printed at a **high** is right, and emphatically.

**A conviction cap at extremes would have blunted the single best call in the
record.** H3 should not be implemented as written; it should be **re-scoped to
the bearish branch**, and that re-scoping needs its own evidence. Watching: one
more max-conviction bullish call, anywhere.

## H2 — first counter-instance, and it is the largest one available

`EXHAUSTED`, 95.2% of ADR spent, price at the top of the session range, bias +13
(continuation). **Continuation was the trade by +537.9.** A fade at the extreme
was run over by 573pts of run-through on the call wall alone.

Record: **3 for the fade (08-24 13:45, 08-25 13:04, 09-14 13:04) / 1 against
(09-21)** — and the one against is an order of magnitude larger in magnitude than
any of the three for. Note also that all three "for" instances are the same
directionally-contaminated sample H3 flagged: bearish calls at lows. **H2's
empirical claim is now unproven in both directions. Nothing proposed.**

## H1 — n=15; one session moved the per-day mean from +1.9 to +39.7

09-21: budget 18.7, extension 587.9, error **+569.2** — the largest in the record
**by 4.2x** (prior max +136.4). Extension/budget **31.4x**; traversal 659.8 =
35.3x budget.

Series: `+61.2 −11.6 −73.0 −86.4 −10.7 −26.2 −64.0 +57.3 +44.3 +79.4 −81.3
+136.4 +40.0 −38.9 +569.2`. **Mean +39.7 (n=15), +1.9 (n=14).** One point moving
a 15-day mean by 38 points is the definition of a tail. The 09-18 conclusion — no
bias to correct, only variance — **stands**. No multiplier. The structure in the
error is conditional (see P-F), not a level.

## H20 — stays 2 of 3, and its mechanism is now weaker

`events_24h: []`, `event_gate: null`, brief text *"No High/Medium US events in the
next 24h"* — and this was **the largest fuel error ever recorded**. The two
largest errors before today (09-16 FOMC +136.4, 09-10 PPI +114.6) both had a
scheduled print; the largest of all has an empty calendar. An event-day budget
multiplier would not have caught the worst miss in the journal. **No new
observation for H20** (no event), but its plausibility is reduced.

## Rejected on test — "hot early pace predicts expansion"

The tempting inference from 09-21 (95.2% of ADR burned before the US open → a
2.46x day). It does not survive the other nine PRE_NY days.

`adr_used_pct at scan` vs per-day fuel error, PRE_NY first-scans, complete days:
`97.1→−11.6 · 53.3→−73.0 · 66.0→−86.4 · 97.7→+44.3 · 82.5→+79.4 · 73.0→−81.3 ·
59.3→+136.4 · 136.0→+40.0 · 82.9→−38.9 · 95.2→+569.2`

**Pearson r = 0.238 (n=10), and 0.239 with 09-21 removed.** 09-16 burned only
59.3% and still under-read by +136.4. **No signal. Rejected, recorded so it is not
rediscovered.** What *does* separate the days is the prior-day-range condition in
P-F, not the pace.

## D21 — second consecutive counter-instance, same failure mode

`gamma −2` "price sits in the top 20% of the wall band (29258.8–30008.8) — poor
risk/reward for longs". Price **left the band upward and never returned**; session
high **+573.1 above the band top**, close +486.8 above. Word for word the 09-18
outcome.

Record **3 for / 2 against**. Both counter-instances share a condition the row
does not test: **price was already outside the prior day's range, so the band it
measures against is stale.** n=2 on that mechanism — recorded, not proposed. If a
third arrives, it merges with P-F rather than becoming its own fix.

## P-E — 8th instance; 4 capped / 4 sliced, and the gap widened

09-21 CALL WALL 30008.8 (0.98bn, *"the strongest ceiling on the board … rallies
stall. Take profit into it"*): first touch 13:35, **53.5pts** of retest, then
**+573.1 above** and a close **+486.8 above**.

| mode | instances | magnitude |
|---|---|---|
| capped | 08-26, 09-08, 09-11, 09-14 | overshoot **3.6 – 11.9** |
| sliced | 08-27, 08-28, 09-18, **09-21** | run-through **103 / 154 / 185 / 573** |

**Still nothing between 12 and 103.** The distribution has no middle and now has a
573pt tail. A discriminator fitted to 8 points split 4/4 is noise-tuning. **No
change proposed**; the prose claim remains the thing to fix, not the level.

## M6 — 10th session, and a wording inversion on top of the classification defect

`review_day.py` graded the CALL WALL 30008.8 as *"broke DOWN through it — lost by
53.5pts"* and London High 29994.0 as *"broke DOWN through it — lost by 38.7pts"*,
on a day that closed **487 and 502 points above them**. Both were broken
**upward** and then held as support on a retest.

M6 has been recorded as a mis-classification (verdict derived from
`bars[-1]["close"]`). This is the first instance where the emitted **English is
the opposite of the event**: a reader taking the grade at face value records two
levels breaking down on the biggest up day in the journal. M6's written fix —
grade against direction of approach, reversal measured from the touch — covers
it. **Not re-proposed; it needs a decision, not more evidence.**

**Sub-note, n=2, not proposed:** `SETTLE_TOL = 25.0` is absolute. That is 5.6% of
09-21's range and 5.0% of 09-18's, and near-identical *relative* excursions on
the same call wall graded **"lost"** (09-21, −53.5 of 958.4) and **"held"**
(09-18, −17.3 of 344.6). Scaling the tolerance to ADR or realised range is
probably subsumed by M6's fix; flagged here so it is not lost if M6 ships
narrowly.

## Dead-weight audit — four rows have never scored a point

Across **16 trading days** (first scan of each, `is_trading_day: true`):

| row | days it scored ≠ 0 |
|---|---|
| `macro` NFCI financial conditions | **0 / 16** |
| `macro` yield curve 10y–2y | **0 / 16** |
| `vol` VVIX | **1 / 16** |
| `rates` DXY | **1 / 16** |
| `macro` WALCL / RRP | 5 / 16 |
| (contrast) `macro` HY OAS | **16 / 16** — W2's standing +2 |

They are not distorting the score; they are padding a table that advertises "26
checks" when 22 of them can ever move. **Cosmetic, no proposal.** The interesting
half is the contrast: on the strongest call in the record, `macro` supplied +6 of
+13, of which **+3 came from a 2-business-day-stale DFII10** (H18, another
instance — this time on the *right* side, which is exactly why H18 must not start
being treated as harmless) and **+2 from HY OAS**, the level-test that has now
fired 16 of 16 days (W2).

## D18 — fifth trading day, ninth headline instance

`news −2` on the biggest up day in the record, from **2 auto-scored headlines out
of 53** (`scored_high_confidence: 2`, `needs_model_judgement: 51`). One of the two
is *"Hawkish Federal Reserve **Steadied Stocks** and Pulled Bond Yields Lower"* —
a bullish headline scored bearish on the keyword "hawkish". Textbook D18. It cost
2 points off a correct call rather than causing a wrong one, so no new severity
claim; the instance count is what is being added.

## H10 — the mirror image fired, and it was right

The −3 branch (*"price is BELOW the entire prior-week range"*, no reclaim
condition) stays **0-for-4** and did not fire. The **+3 branch** fired for the
first time on record — *"price is ABOVE the entire prior-week range — the weekly
draw has flipped bullish; PWH 29704.2 is now support"* — and it was the single
largest **correct** component of a +13 call. Price never came within 250pts of
PWH all day. **n=1 for the positive branch.** It does not rehabilitate the
negative branch, and it is logged so the two are not scored as one rule.

---

# Observations appended 2026-09-23 (grading the 2026-09-22 session)

Session 30510.8 / **30788.1** / 30394.0 / **30728.1**, range 394.1 = **0.94x
ADR14**, net +217.3 = 55% of range. 1 gradeable scan (12:47:09Z PRE_NY), 0 test
artefacts, `is_trading_day: true`. The 2026-09-23 scan is excluded everywhere
(179 bars, held back by `track.py`). Direction **CORRECT** (+6 BULLISH).

**No new IDs opened. Highest allocated is unchanged: H22 · D21 · P5 and P-F · M7.**
Everything below appends to an existing item, deliberately.

## D21 — THIRD consecutive counter-instance, and the planned merge into P-F is dead

`gamma −2` *"price sits in the top 20% of the wall band (30273.4–30523.4) — poor
risk/reward for longs"*. Price left the band upward and never returned: high
**+264.7 above the band top**, close **+204.7 above**. Word for word 09-18 and
09-21.

Record **3 for (08-28, 09-08, 09-17) / 3 against (09-18, 09-21, 09-22)**.

The 09-21 entry said *"both counter-instances share a condition the row does not
test: price was already outside the prior day's range, so the band is stale… if a
third arrives, it merges with P-F."* **It does not.** On 09-22 `price_at_scan`
30492.5 was **inside** the prior day's range (PDH 30581.9 / PDL 29623.5). The
stale-band mechanism explains 2 of 3 counter-instances, not 3.

**The obvious fix was tested and fails its own ledger.** Demoting the ±2 to
prose, across all **8 firings** on record (published score -> score without the
row, vs actual direction):

`08-27 +7->+9 (+1) · 08-28 +4->+6 (-1) · 09-08 +4->+6 (-1) · 09-09 -2->0 (-1) ·
09-17 -2->0 (+1) · 09-18 +4->+6 (+1) · 09-21 +13->+15 (+1) · 09-22 +6->+8 (+1)`

**The row has never flipped a direction call's sign in 8 firings.** It moves
conviction only: 5 days more conviction in the correct direction, **2 days
(08-28, 09-08) more conviction in a wrong one** — on both it is the only bearish
row on a wrong bullish call — and 2 days (09-09, 09-17) lose their sign to zero.
**No label sign changes at all.** Demoting it therefore cannot be argued as an
accuracy fix; it is conviction scaling. **Evidence appended, NOT proposed.** What
breaks the 3/3 tie is a discriminator (breadth is the candidate); 6 tested
instances will not support fitting one.

## M6 — 11th session; three inverted verdicts in one grade, and the cheap fix is falsified

`review_day.py` graded PDH + NY High *"broke DOWN through it — lost by 90.9pts"*,
shelf 0.43bn + London High *"lost by 82.4"*, and the CALL WALL *"lost by 32.4"* —
on a day that closed **146.2, 154.7 and 204.7 points ABOVE them**. All three were
broken **upward** and held as support into the bell. In all three objects
`settled_side: "above"` sits next to `held: false`: the field and the English
contradict each other inside the same record.

**The `SETTLE_TOL` rescaling sub-note (opened 09-21, n=2) is now falsified.** The
three excursions are **8.2%, 21% and 23% of the 394.1pt range** — all above the
5.0% (09-18, graded held) / 5.6% (09-21, graded lost) band that motivated scaling
the tolerance. A range-relative tolerance would have graded all three "lost" too.
**Only M6's written fix — grade against direction of approach, reversal measured
from the touch — addresses this.** Recorded so the cheaper alternative is not
re-proposed. M6 still needs a decision, not more evidence.

## P-E — 9th instance: 4 capped / 5 sliced, and three consecutive slices

CALL WALL 30523.4 (1.50bn, *"the strongest ceiling on the board … rallies stall.
Take profit into it"*): 32.4pts of retest, high **+264.7 above**, close **+204.7
above**.

| mode | instances | magnitude |
|---|---|---|
| capped | 08-26, 09-08, 09-11, 09-14 | overshoot **3.6 – 11.9** |
| sliced | 08-27, 08-28, 09-18, 09-21, **09-22** | run-through **103 / 154 / 185 / 573 / 205** |

**Still nothing between 12 and 103, in nine observations.** The last three
sessions are all slices. The brief's own escape clause (*"a held close above flips
that selling to buying and it becomes a launchpad"*) described the outcome
correctly on all three and is the sentence a reader is least likely to act on,
because the unconditional lid is stated first. P-E already proposed as prose;
no discriminator proposed. **Watching for one instance between 12 and 103** — an
empty middle in nine observations is either real bimodality or an artefact of
`SETTLE_TOL`, and a middle observation separates those.

## P-F — sub-note, n=2: the fade-first strategy also misfires INSIDE the prior-day range

`STRATEGY 1 — sweep → failed re-break → CISD reversal`, justified as *"positive
gamma above the flip: dealers fade extensions, so sweeps genuinely fail."* Four
liquidity sweeps above price (Asia High, equal highs ×3, London High, PDH) were
all taken and all held; the PDH note's explicit *"CISD = short"* sat under a
146.2pt close-above.

By the register's own grading rule (net ≥75% or ≤25% of range) **55% is not
judgeable**, so no right/wrong is claimed for the selector. The *premise sentence*
was false on every level it applied to, and this is the **4th consecutive session
above the flip** where that held (09-17, 09-18, 09-21, 09-22). **09-18 and 09-22
were inside the prior-day range**, so P-F's condition would not have suppressed
the fade-first prose on either. n=2 on that sub-mechanism. **Recorded, not
proposed** — P-F is already the one prose change queued for this block and
shipping a second makes neither measurable (H22's reasoning).

## P3 / H6 — structural wall: 0 touches on 9 publications across 8 trading days

08-24, 08-25, 08-26, 09-10, 09-14, 09-15, 09-21, 09-22. Today at **−1469pts =
3.52x ADR14**, the largest distance recorded. Still correct behaviour for a level
whose own note reads *"mark it and leave it"*. **P3 strengthened** (exclude
`kind: structural` from the hit-rate denominator, keep publishing it).

## P-B(b) — the cleanest clustering instance in the record

16 levels published occupy **10 distinct price zones**. 9 levels graded "touched"
resolve to **4 independent events**:

| zone | levels | first touches |
|---|---|---|
| 30639.6 / 30629.5 / 30623.4 (16.2pt band) | Asia High · Equal highs ×3 · shelf 0.62bn | 13:35, 13:40, 13:40 |
| 30581.9 / 30573.4 (8.5pt) | PDH + NY High · shelf 0.43bn + London High | 13:30, 13:30 |
| 30523.4 | CALL WALL | 13:30 |
| 30495.6 / 30489.8 / 30473.4 (22.2pt) | PD close · Asia Low · shelf 0.36bn | 13:00, 12:50, 12:50 |

**Published hit rate 0.56; zone hit rate 0.40** (0.44 excluding the structural
wall). The three levels reported as "held support for 255–270min" are one level
counted three times. Same object as the 09-18 instance; folded into P-B(b).

## H18 / P1 — seventh instance, second consecutive on a CORRECT call

DFII10 scored **−3** with its own `why` string reading *"FRED has not published
since 2026-09-18 (2 business days ago) — this is last week's reading, not
today's."* Removing it gives **+9 vs the published +6** — stronger and more
accurate on a day that closed +217.3. P1 covers it; still blocked on H19's
unrun hand-score baseline. **No new proposal.**

## News sampling bias — standing record

| scan | counted | uncounted | coverage | sign of counted | score |
|---|---|---|---|---|---|
| 2026-09-22 12:47 | 2 (0 bull / 2 bear) | 51 | **3.8%** | 100% bearish | **−1** |

**Not a D18 sign instance:** both counted headlines are genuinely hawkish-Fed
("says inflation persistence led her to support interest rate hike"). This is the
sample-size mechanism only — 4 counted scored −3 on 09-15, 2 counted scored −1
today, on an identical 100%-bearish subset sign.

## H10 — the `+3` branch fired a second time and was right again

*"price is ABOVE the entire prior-week range (28757.3–29704.2) — the weekly draw
has flipped bullish; PWH 29704.2 is now support"* — the largest correct component
of a correct +6. Price never came within 690pts of PWH. **n=2 for the positive
branch.** The `−3` branch stays **0-for-4** and did not fire. The two branches
must not be scored as one rule on the strength of the positive one.

## D7-shaped instance — the high was set by contract count, not dollar gamma

Session high 30788.1 stopped **14.7pts** above the secondary table's **30773.4
(0.52bn but 25,732 contracts — the largest contract count anywhere on the page)**.
The headline CALL WALL (1.50bn, 22k contracts) was **264.7pts** below the high.
The strike that marked the extreme appeared only in a table the brief labels
*"context only, don't mark"*.

**n=1 and, as things stand, permanently n=1: the secondary gamma table is not
persisted in the journal JSON**, so this claim cannot be counted historically. The
prerequisite for ever testing it is persisting that table. Recorded as the
prerequisite, not as a proposal.

## H1 — n=16, mean +39.7 → +35.8

09-22: budget 171.5, extension 148.5, error **−23.0**, `about right` (0.87x);
traversal 317.0 = 1.85x budget. Series unchanged in character: one tail point
(09-21 +569.2) still carries the entire mean. **No multiplier. P4 not
re-proposed.**

---

## P-E — a mechanism for the empty middle: the wall sits on a fixed round-number grid

**Raised 2026-09-23 from a user observation** — that C1/C2/C3 are repeatedly
100pts apart (30,833 / 30,733 / 30,633) — and checked against the chain and the
whole journal. It proposes no change. It reframes what P-E's 4-capped/5-sliced
split is measuring, and it is falsifiable.

### The walls are not placed by the market; they are placed on a grid

Three measurements, today's `_NDX` week book (`dte<=7`) unless stated:

1. **NDX lists strikes every 10pts** in the near book — 565 call strikes, gaps
   of 10 and 5. The 100pt spacing is **not** the listing grid.
2. **Open interest clusters on round hundreds.** 65.2% of near-dated call OI
   sits on strikes divisible by 100, which are only 163 of those 565 strikes.
   A further 17.9% is on the ...50s; 16.9% is spread over everything else.
3. **The board buckets at `bin_pts=50`**, so the bins alternate heavy/light:

   | NDX bin | call OI | | NDX bin | call OI |
   |---|---|---|---|---|
   | 30,600 | **21,873** (C2) | | 30,650 | 5,203 |
   | 30,700 | **16,526** (C3) | | 30,750 | 4,104 |
   | 30,800 | **29,185** (C1) | | 30,850 | 4,117 |
   | 31,000 | **26,697** | | 31,050 | 3,925 |

   Round-hundred bins carry **4-7x** the contracts of the ...50 bins between
   them. Ranking picks the heavy ones, so the ranked walls are ~100 apart by
   construction.

**Census of every call wall ever published** (parsed from the journal briefs,
strike = published wall - that scan's CFD offset; deduped to one row per day per
strike): **19 walls over 16 trading days — 14 on a round-100 NDX strike, 5 on a
round-50, 0 on anything else.** The wall has never once landed off the grid.

The `...33`/`...3.4`/`...8.8` endings readers notice are only the CFD offset:
30,832.9 is NDX 30,800 + 32.9, exactly as 30,523.4 was 30,500 + 23.4 and
30,008.8 was 30,000 + 8.8.

### Why this bears on P-E

P-E records **no instance between 12 and 103pts** of run-through in nine
observations, and asks whether that is real bimodality or a `SETTLE_TOL`
artefact. The grid offers a third explanation, and a simpler one:

- A **cap** is price failing at the wall's own bin. The bin is 50pts wide, so a
  cap cannot overshoot by much more than its half-width, 25pts. Observed caps:
  **3.6 / 9.6 / 11.9** — all inside it.
- A **slice** is price leaving that bin, and the next place with enough OI to
  slow it is the next round hundred. So the smallest possible slice is about
  **100pts**. Observed minimum slice: **103**.

The empty middle is then not a fact about dealer behaviour at all. It is the
distance between two adjacent pools on a fixed grid, and **no outcome can land
there because there is nothing there to stop at.**

This explains the *gap*; it does **not** explain the *tail*. Slices of
103/154/185/205/573 are 1 to ~6 grid steps, so the grid says where price can
next rest, not how far it goes.

### What would falsify it

1. **A wall on a ...50 strike should show a ~50pt gap, not ~100.** Five such
   walls already exist (08-26, 08-28, 09-11 x2, 09-17). Their caps and slices
   have never been segregated by grid step. **This is measurable today from the
   existing record and is the first thing to do.**
2. **Any run-through between 12 and 103 on a round-100 wall** falsifies it —
   the same observation P-E is already watching for, now with a reason to
   expect its absence.
3. If the concentration is an artefact of one chain, the whole thing collapses.
   **The 65.2% figure is n=1, measured on 2026-09-23 only**, and must be
   re-measured across days before anything leans on it.

### Consequences if it holds

- *"The call wall is 150 away"* is then partly an arithmetic statement about
  the grid, not a market-derived distance, and the board should not imply that
  a nearer wall is a stronger one.
- It raises the same question for the **put** side and the **flip**, neither of
  which has been censused.
- It sharpens the 09-22 finding that the session high was set 14.7pts above the
  heaviest strike by **contract count** while the dollar-gamma wall sat 264.7pts
  below: if pools sit on a grid, which pool matters is a ranking question, and
  the ranking currently uses dollar gamma alone. That comparison still cannot be
  tested historically, because the secondary table is not persisted in the
  journal JSON.

**Nothing proposed.** Falsification test 1 costs nothing and uses data already
in the record; it should run before P-E's prose change is written, because if
the grid explains the bimodality then the prose should describe the grid, not
a dealer behaviour.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

---

## P-E — the opening-bar tag: fading it loses, and the break is NOT the mirror trade

**2026-09-23, user-initiated.** Scripts in `research/wall-studies/`; all figures
re-derivable. Levels are each day's `prediction.levels` (`kind` in `gamma`,
`gamma-shelf`) from the last scan **before 13:30Z**, so no lookahead. 14 days
have a pre-open scan and full RTH bars.

### 1. The day's extreme lands on a level about as often as chance

| tol | high on a level | low | either | **null** |
|---|---|---|---|---|
| ±8 | 2/14 (14%) | 0/14 | 2/14 (14%) | 8% |
| ±15 | 3/14 (21%) | 0/14 | 3/14 (21%) | 15% |
| ±25 | 3/14 (21%) | 2/14 | 5/14 (36%) | 24% |

The null is per-day: the fraction of that day's own RTH range lying within tol
of some level — the chance a uniformly-placed extreme looks like a hit. **2 vs
1.1 expected is noise.** Lows essentially never land on a level, consistent with
the put side being far and thin all month.

2026-09-23 is one of the two hits: RTH open 30,737.1, **high 30,737.4 in the
opening 5 minutes**, 4.5pts above the 30,732.9 shelf, then -368 to the low. The
phenomenon is real; it is not frequent.

### 2. Fading the first post-open tag loses, and the level adds nothing

n=12, 5 wins, mean **-77.7**, total **-932.7**. A control taking the same trade
at the same bar 50pts away — the empty half of the grid — did **better**
(-332.7, 6/12). The level location contributes nothing.

Split by when the tag happened:

| | n | wins | mean | drop-one worst |
|---|---|---|---|---|
| tag in the **opening bar** | 8 | 2/8 | **-152.2** | still -95.9 |
| tag later in the session | 4 | 3/4 | +71.2 | +18.4 |

The opening-bar result is sign-stable under drop-one **including** dropping the
-546 on 09-21. The later-tag result is not robust: drop 09-16 and it falls to
+18.4, so it rests on one trade.

### 3. The break is not the answer either

"Wait for a 5-minute bar to CLOSE beyond the level, then go with it":

| | n | wins | mean | median | total |
|---|---|---|---|---|---|
| all | 12 | 7 | +47.5 | +10.9 | +569.7 |
| **excl. 09-21/22/23** | 9 | 4 | **-44.6** | -11.6 | -401.7 |

**09-21 alone is +94% of the total**; drop it and the mean is +3.1. The apparent
edge is three days of the strongest directional run in the record. Mean adverse
excursion after entry is **136.4pts** (worst 444.7) against a median gain of
10.9 — unusable even if the sign were real.

Note also that confirmation costs ~40% of the idealised number (+79.5 entering
at the level vs +47.5 on confirmation). **Sign-flipping a losing rule does not
produce a winning one**: A and C are the same 12 events, and the middle outcome
— chop around the level — loses both ways.

### What this supports

One claim, and it is a **negative** one: **an OI level tagged in the opening bar
should not be faded.** It is robust to drop-one, independent of the rally days,
and it contradicts the board's standing prose (*"rallies stall. Take profit into
it"*), which has now been wrong on 6 of 8 opening-bar tags.

**Nothing proposed as an entry rule.** 12 events, and the timing split was found
after looking at the data.

---

## H14 / P-E — the gamma REGIME does not predict how price reacts at a wall

**Same date and dataset.** This is the sharper finding, because **strategy
selection is a deterministic function of regime** (S1 above the flip, S2 below;
09-10 the lone exception, suppressed as straddling). Cutting by strategy and
cutting by regime are the same cut, so this tests the selector itself.

Metric is **penetration**: how far past the level price travelled after first
touch. Continuous and measured to the post-touch extreme, deliberately, so it
does not inherit the held/lost tolerance instability of M6 and P-B.

| | n | median pts | %ADR | >=100pts | **% of that day's realised range** |
|---|---|---|---|---|---|
| POSITIVE gamma (S1), all | 16 | 164.0 | 39.1% | 69% | **53.9%** |
| POSITIVE gamma, excl. 09-21/22/23 | 9 | 97.8 | 25.5% | 44% | **36.3%** |
| NEGATIVE gamma (S2) | 6 | 85.1 | 21.3% | 50% | **39.5%** |

Raw, positive gamma looks *worse* — walls penetrated twice as far in the regime
the brief says is damped. That is the rally again. Normalised by each day's own
realised range and with those three days out: **36.3% vs 39.5%. No difference.**

**The single hardest fact: 0 of 16 positive-gamma wall touches held within
25pts.** Not one. Strategy 1's stated premise — *"Positive gamma above the flip:
dealers fade extensions, so sweeps genuinely fail"* — has **zero supporting
instances**. Negative gamma managed 1 of 6, no better but not a clean zero.

This is consistent with P-E (4 capped / 5 sliced, no middle), with the
opening-tag result above, and with H14's original complaint that the wall notes
are regime-blind — the notes may be regime-blind because **the regime does not
carry the information the notes assume it does.**

### The confound, stated plainly

Positive-gamma days in this window (08-25, 08-27, 09-16 … 09-23) are almost
exactly the days the index rallied; negative-gamma days (08-24, 08-26, 09-14,
09-15) are the down days. Late September was one sustained advance, so **"positive
gamma" and "the market went up" are nearly the same variable here.** 22 events,
12 days, only 6 events on 4 days in negative gamma.

**Nothing proposed.** The selector cannot be judged until the record contains a
long-gamma, range-bound stretch. What can be said now is narrower and does not
depend on the confound: the *prose* asserting that sweeps fail in positive gamma
is unsupported at 0/16 and should stop being stated as fact.

### Falsifiable from here

1. A long-gamma chop stretch: if walls hold there, the regime claim survives and
   the confound was the whole story.
2. Any positive-gamma wall touch holding within 25pts — the first one moves this
   off zero.
3. Re-run `04_penetration_by_regime.py` at n>=40 events before any weight change.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

---

## D22 (NEW, OPENED) — `yahoo_series` percent-changes are not guaranteed to be prior-session, and the NDX/ES legs cover different windows

**Graded 2026-09-24 from the 2026-09-23 session.** Two parts, separated by how
well each is evidenced. `bias_engine.py:186-192` reads
`macro["index"]["ndx_daily"]` and `breadth_proxy["es_sp500"]`, both produced by
`macro_probe.yahoo_series` (`macro_probe.py:207, 224`).

### (a) Window mismatch — certain from the code, present on every PRE_NY scan

`^NDX` is fetched with the default `range=10d`; it does not print pre-market, so
`last` (= `regularMarketPrice`) is yesterday's cash close and `chg_pct` is
**yesterday's cash session**. `ES=F` is fetched `range=5d` and trades overnight,
so its `chg_pct` is **this morning's globex move**. The two legs of
*"NDX x% vs ES y% — tech leading / lagging"* are offset by one session, always,
on every pre-NY scan (11 on record).

09-23 concretely: *"NDX +3.67% vs ES −0.10% — tech leading, genuine risk
appetite"*, `+1`, printed 42 minutes before the index began a 232pt slide.

**Worth nothing on accuracy.** Recomputed with both legs on the overnight window
(NQ −0.15% vs ES −0.10% → *"in line"*, 0), 09-23 goes **+13 → +12, same label,
same direction call**. Not proposed this cycle: P-G is already a prose change
into the same board and the 09-21 "one change at a time" rule applies.

### (b) Two-session skip on the NDX leg — n=2, OBSERVING, NOTHING PROPOSED

Reported `ndx_daily.chg_pct` reconciled against the journal's own close series
(closes from `review_day.py`, not recomputed):

| scan | reported | actual prior session | error |
|---|---|---|---|
| 09-10 | −0.29% | −0.23% | ok |
| 09-11 | −1.08% | −1.09% | ok |
| 09-15 | −0.82% | −0.64% | ok |
| 09-16 | −0.65% | −0.68% | ok |
| 09-17 | +0.03% | −0.04% | ok |
| 09-18 | +1.73% | +1.59% | ok |
| 09-21 | +0.67% | +0.81% | ok |
| 09-22 | +2.83% | +2.78% | ok |
| **09-23** | **+3.67%** | **+0.76%** | **+2.91pp** |
| **09-24** | **−0.04%** | **−0.75%** | **+0.71pp, sign flip** |

Baseline noise is ±0.15pp (CFD-vs-cash offset). The two failures are
categorically different: 09-23's figure matches the **09-18 → 09-22** two-session
move (+3.57%), 09-24's matches the **09-21 → 09-23** two-session move (+0.01%).
Suspected mechanism, `macro_probe.py:55`:

```python
closes = [c for c in q["close"] if c is not None]
prev = closes[-2] if len(closes) > 1 else last
```

Null-stripping collapses date gaps, so `closes[-2]` need not be the prior
session — the same class of bug as the `chartPreviousClose` error the code's own
comment at lines 59-63 records fixing.

**Two sessions is below the three-session bar. Nothing proposed.** Blast radius
if confirmed is wider than the ±1 row: the same derivation feeds `rates` (US10y,
DXY) and `breadth` (four mega-caps) — 6 of 24 rows and ±8 points on 09-23. Those
were **not** shown to be wrong and are not claimed to be.

**Settles in one call:** print the dated closes `yahoo_series("^NDX")` returns
and compare the last four against the journal's PD-close series. A missing date
confirms (b); no missing date closes it negative. Free, reliable, no new data
source.

---

## P-G (NEW, PROPOSED) — session-extreme prose is chosen by level kind, not by which side price is on

**Prose only. No score, no board membership, no hit-rate change.** Choose the
note for `Asia/London/NY High|Low` from `sign(level − price_at_scan)` with a
±25pt "sitting on it" band. A session high **below** current price has already
had its stops run.

**9 instances across 5 of 11 PRE_NY scans**, from `prediction.levels` and
`price_at_scan`:

| day | level | offset vs price | published note |
|---|---|---|---|
| 09-15 | London High (prev-day) | **−145.0** | *"stops run above it"* |
| 09-23 | London High (prev-day) | **−110.7** | *"stops run above it"* |
| 09-18 | London High (prev-day) + PD close | **−70.4** | *"stops run above it"* |
| 09-23 | Equal lows ×2 + Asia High (prev-day) | −40.8 | *"stops run above it"* |
| 09-15 | Asia High (prev-day) + Equal lows ×2 | −29.6 | *"stops run above it"* |
| 09-23 | Asia Low (today) | +26.7 | *"stops run below it"* |
| 09-11 | Asia Low (prev-day) | +2.9 | *"stops run below it"* |
| 09-16 | Asia High (today) | −2.3 | *"stops run above it"* |
| 09-18 | PDH + NY High (prev-day) | −1.5 | *"stops run above it"* |

Four are inside 3pts and any tolerance catches them. **Three are 70–145pts** —
a directional instruction for an event already past, twice on a ⭐ level.

Distinct from the standing item *"the board has no field for 'price already
tested this today'"*: that is about intraday tests, this is about the side price
occupies at scan, which the generator already knows exactly.

---

## P-E(b) — the shelves are what should replace the call wall's top line

P-E proposes stripping *"rallies stall. Take profit into it"*. It has never said
what to mark instead. **Folded into P-E, not a competing proposal.**

| family | sessions | instances | worst penetration |
|---|---|---|---|
| Options shelf | 09-18, 09-21, 09-22, 09-23 | 7 | −5.0, −21.3, −9.1, −2.3, +4.5, +12.9, +10.3 — **all inside 22pts** |
| CALL WALL ●●●●● | 08-27 … 09-22 | 9 | capped 3.6–11.9 **or** sliced 103 / 154 / 185 / 205 / 573 |

**Caveats.** M6 applies to "held as support/resistance"; the worst-excursion
figures do not depend on it and are what the table uses. 09-18's shelf sat 9.6pts
from the call wall and that review called it redundant — treat as clustered,
leaving **6 independent holds over 4 sessions**. Board ordering and emphasis
only; no `gex_levels.py` change proposed.

---

## D21 — 9th firing, and the width defect that explains why the tally reads as noise

The row fires on **percent of the wall band with no normalisation for band
width**. Across 15 firings the band spans **100 → 800pts**, so "top 20%" is a
trigger window of **20 to 160pts** — 4.7% to 37% of ADR14. The same `−2` is
awarded for *17pts under the call wall* (09-18) and *150pts under it* (09-23).
**The 9 graded firings D21 has been tallying are a mixture of two physically
different conditions.**

Band widths: 08-24 200 · 08-27 200/300 · 08-28 800 · 09-08 200 · 09-09 100 ·
09-10 300 · 09-14 500 · 09-17 450 · 09-18 100 · 09-21 750 · 09-22 250 ·
09-23 800 · 09-24 500.

Re-cut by **absolute distance to the call wall**, the 8 graded firings invert:

| bucket | firings (dist to call wall) | realised direction |
|---|---|---|
| within 50pts | 08-27 +7, 09-18 +17, 09-17 +26, 09-08 +30, 09-22 +31, 09-21 +46 | **5 up / 1 down** — claim wrong 5 of 6 |
| beyond 50pts | 08-28 +71, 09-23 +150 | **2 down / 0 up** — claim right 2 of 2 |

**NOT PROPOSED.** n=8, and the cut was found after looking at the outcomes —
exactly the procedure the standing rule forbids acting on. Logged as a
**pre-registered test**: 09-24 fired TOP at **+30 (within 50)**, so the cut
predicts an **UP day on 09-24**. Written here, not into any `prediction` block.

---

## H10 — `+3` branch fails on its third firing, and the missing term is distance

Four consecutive firings off the **identical** prior-week range
(28757.3–29704.2), with price walking away from it:

| day | distance above PWH | graded direction |
|---|---|---|
| 09-21 | +259 | ✓ |
| 09-22 | +788 | ✓ |
| **09-23** | **+979** | **✗** |
| 09-24 | +490 | ungraded |

A reclaim three sessions and 979pts old scores exactly like one made this
morning. `+3` branch **2-for-3**; with the `−3` branch at 0-for-4 the row is
**2-for-7** while carrying the largest single weight in the structure block.
**No decay proposed** — the failure sits at the largest distance on n=3.
Falsification: the next `+3` firing at >700pts above PWH.

---

## Tested and rejected — "price below the prior close at the PRE_NY scan predicts a down day"

The tempting post-hoc story for 09-23 (price 45pts under PD close, structure
scored `+1` for "above PD mid"). Tested on the 9 recoverable PRE_NY scans:
**5 right, 4 wrong** — ✓ 09-15, 09-17, 09-18, 09-21, 09-23 · ✗ 09-11, 09-14,
09-16, 09-22. A coin flip. **Not proposed, and the 09-23 narrative it would have
supported is retired.**

---

## 2026-09-23 — the day nothing on the register would have caught

`+13 STRONGLY BULLISH` against a −232.3 close; a bearish call needed −14. Every
register proposal plus both new ones, applied together, reaches roughly **+9**.
The engine's only bearish information was `rates −3` and one mis-specified
`gamma −2`. Recording that plainly, because manufacturing a fix that reaches −14
would be fitting a single session.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01M7sro1DKMp5T7EBDusm6pM

---

## D23 — CBOE served a TWO-SESSION-STALE chain and the brief published a full board off it

**2026-09-24 12:47Z.** The scan completed, the chart drew, the archive pushed,
and every number on the options side was built on Tuesday's book.

Probed directly at 12:48Z, minutes after the scan:

```
_NDX option chain timestamp : 2026-09-23 03:44:16   (~33 hours old)
QQQ  option chain timestamp : 2026-09-23 03:56:14
_NDX quote last_trade_time  : 2026-09-22T16:14:59   (Tuesday's close)
now                         : 2026-09-24T12:48:31Z
```

CBOE's delayed feed had not advanced through Wednesday's session at all. The
CFD meanwhile had moved ~490pts from Wednesday's scan (30,683 -> 30,194).

### What it produced

`CFD/index offset **-276.3**` — **~7x the ~40pt D6 threshold** — with basis
`live_cash_divergence_corrected`. The guard fired and did what it could, but it
corrects a stale *cash price*; nothing checks the age of the *chain*. So the
call wall, put wall, flip, max pain, every shelf, and `gamma +2` of a `+3` call
were all derived from a two-session-old option book and then converted onto the
live chart through a 276pt fudge.

**The brief printed the stale timestamp in its own data-ages block and scored,
ranked and published as normal.** Staleness was visible and inert — the same
shape as D6, D10 and D11: the run looked like it worked.

### What was NOT affected

Fuel and range come from cTrader: ADR14 420.8, range 441.9, 105.0% used,
budget 0.0, `EXHAUSTED`, fuel_ratio 2.33. Rates, breadth and news are
independent of CBOE. The only trustworthy reading on the page is that the day's
range was already spent.

### The second-order problem, which is the bigger one

The scan sits in the journal as an ordinary observation. Graded as-is it feeds
corrupt levels into P-E, P-E(b), H6, M6, the hit-rate series and the wall
census — manufacturing conclusions out of a feed outage, which is what W1/W2
were withdrawn for.

**Precedent exists and points the right way.** D1 quarantined corrupt *fuel*
fields on the rollover scans while keeping the direction call, because the
corruption was field-level. This is the mirror image: quarantine the *options*
fields, keep fuel. Direction is contaminated here too — gamma supplied +2 of
the +3 — so unlike D1 the call itself should not be graded either.

**Also void: the pre-registered D21 test from the 09-23 review.** It states
"09-24 fired TOP at +30, so the cut predicts an UP day on 09-24". That trigger
was computed from this stale chain, so the prediction was never a real one.
It must not be scored either way — scoring it would put a coin-flip into the
register dressed as a pre-registration.

### Not fixed here, and why

Two changes are needed and both are off-limits on a scheduled run: the
quarantine lives in `track.py` (grading code) and the age gate belongs in
`gex_levels` / `brief.py` (wall code).

Proposed when someone has the go-ahead:

1. **A chain-age gate.** If the option chain timestamp is older than roughly one
   session, refuse to publish the levels and say so at the top, rather than
   printing an age nobody reads. The cash-staleness guard already has this
   shape; the chain has no equivalent.
2. **A D6 hard stop.** An offset beyond ~40pts should abort the options block
   outright. Today it printed -276.3 and carried on. Note 2026-08-26 already
   recorded a -177.5 offset in the wall census, so this is the second occurrence.
3. **Field-level quarantine** for 2026-09-24, on the D1 pattern, excluding the
   options fields AND the direction call.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

---

## D23 CORRECTED — the fault was the CONVERSION, not the chain; and the offset was 305pts wrong

**Supersedes the D23 entry above, which is wrong in two places.** Left in place
rather than rewritten, per append-only; this is the account to use.

### Correction 1 — the chain was ONE session stale, not two

The chain was stamped `2026-09-23 03:44:16`, i.e. before Wednesday's session, so
its open interest was **Tuesday's close**. On a Thursday scan the right book is
Wednesday's close. That is **one** session stale. The *quote* (`last_trade_time
2026-09-22T16:14:59`) was two sessions stale. D23 conflated the two.

A one-session-old OI book is a mild defect. It is not what broke the board.

### Correction 2 — the -276.3 offset was not "a guard doing what it could"

It was a **305-point error**, and it is the whole story.

`NQ=F` had rolled to the **December contract**, which carries a **+291.2**
premium over cash (measured at Wednesday's close: NQ 30,761.5 vs NDX 30,470.3).
The brief anchored its NDX reference to Wednesday's frozen cash close instead of
rolling forward, so it read the futures premium as a collapse in the CFD basis.

The arithmetic, from the live feeds that afternoon:

```
CFD 30,245.0   NQ 30,507.5   CFD-NQ  -262.5
premium P                            +291.2
strike -> chart offset = P + (CFD-NQ) = +28.7      <- correct
published offset                      -276.3      <- what shipped
error                                  305.0 pts
```

**+28.7 is the ordinary basis** — the same 8-33pt range seen every other day
that week. Nothing unusual happened to the CFD at all. Every published level was
~305pts too low: the CALL WALL printed at 30,223.7 actually sat at **30,526**,
and the session high of 30,542.8 came within **14pts** of it. The wall was
tested and the board pointed 300pts away from it.

### The real lesson: D6 fired and was talked out of it

The 40pt tripwire **did** trigger at -276.3. It was overridden because the basis
label read `live_cash_divergence_corrected`, which sounds like a guard that
handled it. A label is not a check.

**The check that works, and it is cheap.** Compare the brief's NDX reference
against futures-minus-premium:

| date | brief ref | futures-implied | gap | verdict |
|---|---|---|---|---|
| 2026-09-24 | 30,470.3 | ~30,214 | **+256** | broken |
| 2026-09-28 | 30,427.9 | 30,420.0 | **+7.9** | fine, despite a 45.9pt offset |

Run live on 09-28, when the offset was 45.9 and past the D6 line: the
cross-check cleared it in one call. **It separates a genuine large basis from a
broken conversion, which a fixed threshold cannot.** Propose it as the D6
replacement: gate on reference-vs-futures agreement, not on offset magnitude.

Caveat: the premium is measured at the last cash close and decays toward expiry,
so it needs re-measuring rather than hard-coding, and it will shift at each
quarterly roll — which is exactly the event that caused this.

### Quarantine still required for 2026-09-24

Unchanged from D23 and now better justified: the options fields AND the
direction call must be excluded. Every level was 305pts out, and gamma supplied
+2 of the +3 score. Fuel, rates, breadth and news are independent of CBOE and
stand. The 09-23 review's pre-registered D21 test remains void — its trigger was
computed from this board.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

---

# Observations appended 2026-09-29 (grading the 2026-09-28 session)

1 gradeable PRE_NY scan, `is_trading_day: true`, 0 test artefacts, 276 bars.
O 30646.0 / H 30663.7 / L 30101.2 / C 30310.0, range **562.5 = 1.25x** ADR14
448.6, net **−336.0** (37.1% close position). Direction **CORRECT**. Fuel budget
65.5 vs extension 179.4 → **+113.9, 2.74x under**; traversal 400.7 = 6.12x.
Hit rate 0.57 (4/7).

**2026-09-24 is excluded from every options and direction statistic here**, per
*D23 CORRECTED*; its fuel figure (+13.6) is kept, on the D1 precedent. The
09-23 review's pre-registered D21 test is treated as void and is **not** scored.

**2026-09-25 had never been graded** — no `REVIEW.md` and no entry in this file.
It is graded below and folded into the counts. A silently skipped session biases
every session-count threshold in this register downward, so the gap matters more
than the day did. 09-25: O 30460.9 / H 30728.2 / L 30415.7 / C 30650.2, range
312.5 (0.70x ADR), net +189.3, bias **+1 NEUTRAL — no direction call**, budget
124.4 vs extension **0.0** (err −124.4), hit rate 0.50 (7/14). MAX PAIN 30110.1
never reached, 340pts below spot, on a **Friday**.

## D7 is unfinished — the CORE branch still filters by the range budget, and the footnote is ordered by PRICE

**Two halves, both code-certain, with 16 sessions of measurement on the first.**

`keep()` in `brief.py` exempts `CALL WALL / PUT WALL / GAMMA FLIP / MAX PAIN`
from the budget filter — the D7 fix, met at three instances on 09-10. **Session
extremes and PD/PW levels were left under `abs(dist) <= budget * 1.75`**, with
the comment *"those are genuine reachability claims, so the rule fits them"*.

Tested as a reachability claim: did price stay inside `price_at_scan ±
budget*1.75`? All 16 complete PRE_NY days:

| day | budget | ±1.75x | breach below | breach above |
|---|---|---|---|---|
| 08-24 | 88.7 | 155.2 | +119.4 | +101.1 |
| 08-25 | 12.0 | 21.0 | **+286.3** | +68.8 |
| 08-26 | 186.2 | 325.8 | — | — |
| 08-27 | 132.6 | 232.0 | — | — |
| 09-11 | 8.4 | 14.7 | **+303.2** | +124.9 |
| 09-14 | 61.9 | 108.3 | — | **+352.4** |
| 09-15 | 97.3 | 170.3 | +39.2 | — |
| 09-16 | 145.6 | 254.8 | +65.4 | — |
| 09-17 | 0.0 | 0.0 | **+470.1** | +74.7 |
| 09-18 | 65.6 | 114.8 | +27.6 | +87.4 |
| 09-21 | 18.7 | 32.7 | **+307.0** | **+586.0** |
| 09-22 | 171.5 | 300.1 | — | — |
| 09-23 | 242.4 | 424.2 | — | — |
| 09-24 | 0.0 | 0.0 | +93.1 | **+362.4** |
| 09-25 | 124.4 | 217.7 | — | — |
| 09-28 | 65.5 | 114.6 | **+258.0** | +75.3 |

**Breached below on 10 of 16, above on 9 of 16, either side on 11 of 16.** Split
by budget: **budget < 70 → breached on 8 of 8 days; budget ≥ 88 → 3 of 8.** The
rule is wrong on every low-budget day and mostly right on high-budget ones — it
fails hardest exactly when it prunes the most. That is D7's mechanism, now
measured rather than argued.

**Second half — the footnote cannot be relied on to catch what the filter drops.**
`far_line()` protects the four walls (`NEVER_DROP`) and then takes `rest[:6]`
from a list sorted `key=lambda r: -r["level"]` — **descending price**. So the
footnote prints the six *highest* far levels, not the six nearest, and anything
dropped *below* price disappears entirely once six far levels sit above it.

**2026-09-28 is that case, exactly.** At the 12:47Z scan both the Asia and London
windows were complete and `levels_fuel.session_levels` held:

```
asia    H 30641.6   L 30324.8
london  H 30479.1   L 30280.6     (spot 30473.8, budget 65.5 -> cap 114.6)
```

Only **London High** survived the cap. Asia High (+167.8), Asia Low (−149.0) and
London Low (−193.2) went to `far` — and the footnote then printed
`30820 PWH · 30762 · 30733 · 30728 · 30684 · 30666`, i.e. the six **farthest
upside** rows. PWH at +346 survived because it is highest; Asia High at +168, the
nearest far level, was truncated out; **every downside level was dropped.**

The lowest price the brief told the reader to mark was MAX PAIN 30245.9. Price
traded to **30101.2**, 144.7pts below it, through **both** of its own discarded
session lows. On a correctly called BEARISH day in short gamma the document
contained no downside reference beyond max pain.

**PROPOSED.** (a) Size the session-extreme/PD/PW cap off ADR14, or drop the cap
and tag `(stretch)`, as D7 already does for walls. (b) Order or partition
`far_line` by `abs(dist)` with a floor of two levels per side. Board composition
and footnote ordering only — no score change, no change to the hit-rate
definition. **H6 and P-B re-measure after this, not before.**

## The fuel block and the gamma block give opposite trade instructions — 3 sessions

`_FUEL_MEANING["LOW_FUEL"]` prints *"favour fades over chasing breaks"*
unconditionally. Below the flip the regime block prints *"Fading is the wrong
trade today — Strategy 2 (go with the move)"*, and `COHERENT_SHORT` adds
*"Today's ADR can be exceeded — don't cap the target too early"*.

Census of all **41** `is_trading_day` scans for both strings present:

| day | fuel state | budget | side of flip | extension vs budget | who was right |
|---|---|---|---|---|---|
| 09-14 | LOW_FUEL | 61.9 | BELOW | 194.1 (3.1x) | **gamma** |
| 09-15 | LOW_FUEL | 97.3 | BELOW | 16.0 (0.16x) | **fuel** |
| 09-28 | LOW_FUEL | 65.5 | BELOW | 179.4 (2.7x) | **gamma** |

Exactly 3 of 41, in exactly one cell: `LOW_FUEL`/`EXHAUSTED` **and** below the
flip. **2-1 to the gamma block, which settles nothing about accuracy.**

**PROPOSED as a coherence fix, prose only.** In short gamma the fuel block must
not recommend fades and must present the budget as likely to be exceeded; or the
brief must name which block is live. **Explicitly not an accuracy claim** —
09-15 shows the fuel side can be right.

**Distinct from the logged pinning-vs-expansion conflict**, which is two scoring
rows disagreeing about *range*. This is two blocks giving the reader opposite
*instructions*, and only one of the two is sensitive to the gamma regime.

## The published −7 was right by cancellation of two defective rows

| row | pts | defect | remove it |
|---|---|---|---|
| breadth (mega-caps +1.53% 4/4, NDX +0.42% vs ES −0.35%) | **+3** | **D22(a)** — both legs are Friday's cash session, printed present-tense as *"genuine risk appetite"* | −10 **STRONGLY BEARISH** — one notch stronger, more accurate |
| macro DFII10 2.85% | **−3** | **H18** — its own `why` says *"FRED has not published since 2026-09-24"* | −4 **MILDLY BEARISH** — one notch weaker |
| both | | | **−7 — exactly what shipped** |

Two stale rows, equal and opposite. The correct label was produced by
coincidence, not by either row being right.

**This is a counter-instance to P1 as written.** H18's 6th and 7th instances were
*"the stale row cost conviction on a CORRECT call"*; this is the first where the
stale row **bought** conviction on a correct call. Down-weighting stale rows
alone would have degraded 09-28 unless **D22(a) ships in the same change**.
P1 and D22(a) are therefore coupled and should not be sequenced apart.

**D22(a) also gets its first accuracy instance.** 09-23's write-up recorded it as
*"worth nothing on accuracy"* (+13 → +12, same label). On 09-28 the like-for-like
overnight window is NQ **−0.58%** (spot 30473.8 vs PD close 30650.2) against ES
−0.35% — tech **lagging**. The row scored **+1 for tech leading**; corrected it is
0 or −1, on a day that fell 336pts.

## D22(b) — SETTLED NEGATIVE as specified, and the specified test is void

The register's one-call test was *"print the dated closes `yahoo_series("^NDX")`
returns and compare the last four; a missing date confirms (b)"*. Run today:

```
09-15 28937.84 · 09-16 28945.06 · 09-17 29446.98 · 09-18 29644.17
09-21 30482.35 · 09-22 30732.40 · 09-23 30470.29 · 09-24 30478.86
09-25 30608.13 · 09-28 30276.81
```

**No missing dates, no nulls.** By the stated rule that closes (b) negative.

**It should not be closed, because the test cannot work.** The mechanism is
confirmed arithmetically from these very closes:

- 09-23 reported **+3.67%** = 30732.40 / 29644.17 − 1 = **09-18 → 09-22** exactly.
  Requires **09-21** to have been absent at that scan.
- 09-24 reported **−0.04%** = 30470.29 / 30482.35 − 1 = **09-21 → 09-23** exactly.
  Requires **09-22** to have been absent at that scan.

A *different* interior close was missing on each of two consecutive days, and
**both are present now** — Yahoo backfills. So the nulls are transient and no
post-hoc fetch can confirm or deny; `closes[-2]` is unsafe regardless of what a
later fetch shows. **Status: mechanism CONFIRMED, register's test RETIRED.** The
check must run live at scan time and the dated series must be persisted. 09-28's
own leg is clean: +0.42% = 30608.13 / 30478.86 ✓.

## M6 — 12th session, and a new way for the verdict to hide a violation

MAX PAIN 30245.9 graded *"stalled at it — held as support for 310min, worst
**−24.3**pts"*, in a record whose own `travel_down` field reads **144.7**.

`settled_read()` takes `side_above` from the **last** bar's close and starts the
window at the last bar closing on the other side (15:45Z). `worst_excursion` is
therefore measured only inside the final settled window; the 144.7pt break at
14:45Z — **32% of ADR14, in the same session** — does not reach the verdict.

Distinct from the 09-22 instances (field and English contradicting each other);
here the English is internally consistent and simply describes the last two
hours of the day. Same root cause and the same written fix: grade against
direction of approach, measure reversal from the touch. **M6 needs a decision,
not more evidence — this is the 12th session.**

## Max pain's day-of-week qualifier — threshold met on a technicality, so tighten the threshold

Evidence days now 4 (threshold was *"3 days on which max pain is published"*):

| day | dow | outcome | fair test? |
|---|---|---|---|
| 09-16 | Wed | best level on the board, held 170min, worst 22.6 | yes — against |
| 09-17 | Thu | never reached, nearest approach 245.8 | **no — distance** |
| 09-25 | Fri | never reached, **340pts** below spot | **no — distance** |
| 09-28 | **Mon** | the level that held the close, 310min support | **ambiguous** |

Two of the four are misses at 246 and 340pts. A level that far away cannot be
strong on any weekday, so *"strong by Thursday/Friday"* was never tested on
either. And 09-28 **flips with the grading convention**: under M6's proposed
direction-of-approach rule max pain was *lost by 144.7pts* on a Monday, which
**supports** *"weak on a Monday"*.

**2 fair tests, 1 ambiguous. NOTHING PROPOSED**, and the qualifier cannot be
graded at all until M6 is decided, because the reaction verdict is the
contaminated variable — the same dependency already recorded for PD close.

**The threshold as written should be tightened** to *3 days on which max pain is
within reach* (≤ ~0.5 ADR, or inside the realised range), otherwise it keeps
accruing distance-confounded observations and will read as "met" without ever
testing the claim.

## P-F rebuilt with 09-22 … 09-28 — sign holds, magnitude does not

`price_at_scan` vs prior-day range, parsed from the `structure` row's own
`PDH x / PDL y` string, against per-day fuel error:

| >150pts outside PD range | error |
|---|---|
| 09-14 (−187.6 below PDL) | +79.4 |
| 09-17 (+174.5 above PDH) | +40.0 |
| 09-21 (+259.0 above PDH) | +569.2 |
| 09-24 (−175.5 below PDL) | +13.6 |

**4 of 4 positive** (09-24's fuel is not quarantined). Inside/marginal control is
now **16 days: 6 positive, mean −6.3, median −17.3** (was 3/11, mean −14.0,
median −26.2).

**The split still holds in sign and is weaker than the 09-22 write-up implies.**
09-28 **+113.9** and 09-16 **+136.4** are both inside-range days larger than
**three of the four** outside instances. Drop 09-21 and outside mean is +44.3
against inside +6.3. P-F's discriminating power is carried by one tail point.
**Ship P-F as prose if it ships; never as a multiplier.** H1 lesson, unchanged.

## H1 — n=20

09-28: budget 65.5, extension 179.4, error **+113.9** — second largest positive
in the record. Series: `+61.2 −11.6 −73.0 −86.4 −10.7 −26.2 −64.0 +57.3 +44.3
+79.4 −81.3 +136.4 +40.0 −38.9 +569.2 −23.0 +25.9 +13.6 −124.4 +113.9`.
**Mean +30.1 (n=20), +1.7 without 09-21.** Nineteen of twenty days still average
to zero. **No multiplier. P4 not re-proposed.**

## P-G — instance #10, and the merge picks the wrong note

| day | level | offset vs price | published note |
|---|---|---|---|
| 09-28 | **PD mid + London Low (prev-day)** ⭐ | **+98.2** | *"the next session usually runs the stops below it"* |

Price sat 98.2pts **below** a prior-day London low all session and never returned
to it. **10 instances across 6 of 12 PRE_NY scans**; second-largest low-side
offset, and the third on a ⭐ row.

**New wrinkle, same row.** It was a merged level (`PD mid` + `London Low`), and
the merge picks the note by `rank` — `liquidity` 3 beats `magnet` 1 — so the
wrong-sided session note **replaced** the PD-mid note (*"a target to aim AT, not
a trigger"*), which was the accurate one for a level 98pts overhead. P-G's fix
covers this only if it runs after the merge.

## "No field for price already tested this today" — n=2

PUT WALL 30345.9 published at −127.9 with *"**if** it breaks, expect it to speed
UP, not bounce. Don't buy the break."* It had already broken: the London low of
**30280.6 at 09:15Z** was 65.3pts through it, 3.5 hours before the scan — and
that break **bounced 193pts** back to the scan price. The NY break then did
accelerate, 244.7pts to 30101.2.

So the short-gamma acceleration claim was **1-for-2 within a single session**,
and the brief presented the resolved half as a forward scenario. First instance
was 09-17 (call wall tested pre-scan and presented as *"+26 away"*). **n=2.**
If a third arrives, this and the H1 session-context sub-observation should be one
proposal about session-context fields, not two.

## No instance today

- **P-E** — CALL WALL untouched, 162pts short of the high. Still 4 capped / 5
  sliced; still nothing between 12 and 103.
- **H6 / P3** — no `structural` level was published.
- **D21** — `gamma` scored `+0` "price mid-band, 32% up the range"; the row did
  not fire.
- **P-B(b)** — clean control: 7 levels, all ≥60pts apart, no clustering, so
  0.57 is an honest published hit rate. It remains uninformative about quality —
  the 3 untouched levels were all upside stretch on a correctly called down day.
- **`events`** — 0 points again, 16 of 16 rows.

## Journal hygiene

No fabricated or backfilled entries. 09-24 quarantined as directed and its
`prediction` block untouched. 09-25's ungraded session is the one hygiene defect
found: it is a completed trading day that entered `track.py` but never this
register. **Worth a guard** — a review that skips a day silently shifts every
session-count threshold here, and every proposal in this file is gated on those
counts.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

---

# Observations appended 2026-09-30 (grading the 2026-09-29 session)

1 gradeable PRE_NY scan, `is_trading_day: true`, 0 test artefacts, 276 bars.
O 30315.9 / H 30471.8 / L 30119.5 / C 30404.6, range **352.3 = 0.76x** ADR14
464.5, net **+88.7** (80.9% close position). Direction **CORRECT** (BULLISH +6).
Post-scan move **+12.9** on traversal 218.8 — right by 5.9% of the distance
travelled. Fuel budget 118.6 vs extension **6.4** → **−112.2, 18.5x OVER**;
traversal 1.84x. Hit rate 0.67 (10/15) as published, **0.53** strict, **0.47** on
distinct touch events.

**2026-09-24 remains excluded** from the options fields, the direction tally and
the hit-rate series, per *D23 CORRECTED*; its fuel error (+13.6) is kept on the
D1 precedent and is inside the H1 series below. `track.py` has no quarantine and
still prints it CORRECT, so the counts here are carried by hand off its per-scan
table, as the 09-28 review did. **09-25's figures are cited from the 09-28
review's entry above**, not re-derived; no review file was back-dated for either
day. PRE_NY record, 09-24 excluded: **9 right / 4 wrong / 3 no-call over 16
days**. All sessions: **14 / 8 / 7**.

## P-B(b) — the cause is now quantified: `merge_tol` is less than half `TOUCH_TOL`

`brief.py` merges board lines at `merge_tol = max(3.0, adr14 * 0.008)` = **3.72**
on an ADR14 of 464.5. `review_day.py` grades a touch at `TOUCH_TOL = 8.0`. **Any
two levels between 3.72 and 8.0 apart are structurally guaranteed to publish as
two lines and grade as two touches off one bar.** It fired today: London Low
(prev-day) 30280.6 and London Low (today) 30275.8, **4.8pts apart**, both graded
touched at bar 209, and the second was **never actually reached**
(`travel_down −4.4`).

Measured across 7 graded PRE_NY sessions:

| day | published | touched | distinct touch bars | published rate | distinct-event rate |
|---|---|---|---|---|---|
| 09-18 | 9 | 7 | 7 | 0.78 | 0.78 |
| 09-21 | 7 | 3 | **2** | 0.43 | 0.29 |
| 09-22 | 16 | 9 | **5** | 0.56 | 0.31 |
| 09-23 | 21 | 12 | **7** | 0.57 | 0.33 |
| 09-25 | 14 | 7 | 6 | 0.50 | 0.42 |
| 09-28 | 7 | 4 | 4 | 0.57 | 0.57 |
| **09-29** | 15 | 10 | **7** | **0.67** | **0.47** |

**Inflated 1.4x–1.8x on 4 of 7 sessions and exactly 1.0x on the unclustered
ones.** Today three levels — 30479.1, 30465.4 and 30359.2 — were all resolved by
`bar_index 186`, the **13:30Z NY cash-open bar**, which therefore spanned ≥103.9
pts and held the day's high.

**PROPOSED.** (a) `merge_tol >= TOUCH_TOL`. (b) Report distinct-touch-events
beside the raw rate and never quote the raw rate alone. No score change, no call
change; the hit-rate series stops being a function of how many lines the board
printed. Supersedes the 09-18 and 09-22 clustering instances as the reference
write-up for P-B(b).

**Sub-finding: tolerance-only touches.** A level counts as touched within 8.0pts
even when price never reached it. `travel_up < 0` or `travel_down < 0` detects it.
09-29: **2 of 10** (30479.1 at −7.3, 30275.8 at −4.4). 09-25: 2 of 7, but both
trivial (−1.4, −1.6). **n=2 sessions — below threshold, nothing proposed here**;
folded into (b) above, which reports it for free.

## Session-context field — n=3, threshold met exactly as pre-registered

The register said: *"if a third arrives, this and the H1 session-context
sub-observation should be one proposal about session-context fields, not two."*

| day | level | what the brief said | what had already happened |
|---|---|---|---|
| 09-17 | CALL WALL 29451.5 | *"+26 away"*, launchpad offered as a forward scenario | pre-scan high 29460.5, **9.0pts through it**, rejected |
| 09-28 | PUT WALL 30345.9 | *"**if** it breaks, expect it to speed UP"* | London low 30280.6 at 09:15Z, **65.3pts through it**, bounced **193pts** |
| 09-29 | Asia Low (today) + PUT WALL 30119.5 ⭐ | *"expect a bounce and a good long-sweep here"* | **it is the session low**, made pre-scan, and had already bounced **274pts** |

**And the grader has the same blindness.** `review_day.grade_level` slices
`bars[i_from:]` from the scan bar, so it reported 30119.5 as **"never reached"** —
about a level that equals the session low to the point. A reader of the review
would file the put wall as untested.

**PROPOSED, one change covering both.** Add `tested_today` (time, direction of
approach, reaction) to each `prediction.levels` entry, built from the session
windows the scan already holds; and have `review_day` grade published levels
against the whole session, reporting pre-scan interaction separately instead of
dropping it. No score change. Three of three instances would have printed
"already tested at HH:MM, bounced N" instead of a forward scenario.

## M6 — session #13, and the first instance that INVENTS a violation

Asia Low (prev-day) 30324.8: `settled_side: above`, `minutes_held: 170`,
`worst_excursion: −28.0`, `held: false`, `acted_as: lost`, rendered **"broke DOWN
through it — lost by 28.0pts"**. Price **closed 79.8pts above it**. The 28.0pt
excursion is a wick inside the final settled window.

Every prior instance hid a real violation inside a benign verdict (09-28: a
144.7pt break invisible to a *"held"*). **This one is the mirror: it manufactures
a break out of a wick on a level the day closed 80pts above.** Same root cause,
same written fix (grade against direction of approach, measure reversal from the
touch). **13 sessions. M6 needs a decision, not a 14th instance.**

## P-B — the cleanest `SETTLE_TOL` instance in the record

Two levels, **14.8pts apart**, graded from the **same** settled window (both
`settled_from 18:05`), opposite verdicts:

| level | worst excursion | verdict |
|---|---|---|
| 30324.8 Asia Low (prev-day) | **−28.0** | `held: false` → **lost** |
| 30310.0 PD close | **−13.2** | `held: true` → **support, 170min** |

`SETTLE_TOL = 25.0` sits between them. The verdict is decided by level spacing
against a fixed tolerance, not by behaviour. **Entangled with M6** — fixing the
tolerance without fixing the measurement window just moves the coin-flip.

## H18 / D22(a) — 8th and 3rd instances, and they now pull OPPOSITE ways

| row | pts | defect |
|---|---|---|
| macro DFII10 2.83% | **+3** | own `why`: *"FRED has not published since 2026-09-25 (2 business days ago) — this is last week's reading"*. Largest single row in the model |
| macro DGS10 −1bp | **+1** | dated **09-24 → 09-25**, a **1bp** move, and **the same variable** as the live `rates +1 "US10y 5.217 (−0.44%)"`. The 10-year is scored twice, once stale |
| breadth NDX −1.08% vs ES +0.14% | **−1** | **D22(a)**, code-certain: 30276.81 / 30608.13 − 1 = **−1.0825%** = the **09-25 → 09-28** cash session, i.e. **Monday**, printed present-tense Tuesday pre-market as *"rotation out of tech"*. Like-for-like overnight is CFD 30393.5 / PD close 30310.0 = **+0.28%** vs ES +0.14% — tech **leading**. Sign wrong by 1.36pp |

Corrected: **+5** (drop DFII10, fix breadth) or **+4** (also drop the duplicate
DGS10). Both are `MILDLY BULLISH` — **one notch weaker, direction and verdict
unchanged.**

**This is the counterpart to 09-28 and it completes the P1 argument.** On 09-28
the stale rows cancelled and *bought* the correct label; on 09-29 they pull in
opposite directions and the label survives only because the FRED block is net
+2. **H18 and D22(a) are confirmed coupled in both signs and must not be
sequenced apart.** New, code-certain sub-finding: **DGS10 duplicates the live
US10y row**, so "yields fell" is worth +2 in the model whenever FRED is stale.

## The structure row has no tolerance band — n=2

`structure +1 "price above PD mid 30382.5"` was true by **11.0pts** at the scan
and false from 13:30Z to **20:15Z** — 6.75 of the next 8 hours (per PD mid's own
`settled_from`). All 21 PRE_NY scans, `price_at_scan − PD mid`:

```
-416.3 -400.9 -160.1 -145.4 -98.2 -71.0 -48.3 +11.0 +27.9 +71.2 +86.0 +92.0
+114.5 +154.3 +165.6 +273.9 +290.3 +297.8 +389.8 +421.5 +431.3
```

Only two days inside 30pts: **09-29 (+11.0)** — row +1, price below PD mid for
6.75h, day CORRECT — and **09-16 (+27.9)** — row +1, and that review recorded PD
mid *"lost, worst 50.8–94.6pts"*, day WRONG. **n=2 of 3. NOTHING PROPOSED.** The
third instance test: a PRE_NY scan inside 30pts of PD mid, graded on whether
price holds the scored side through the NY session.

## P-E(b) — first counter-instance: the shelves did not cap, a session extreme did

| upside level | published claim | outcome |
|---|---|---|
| Options shelf 30418.2 | *"expect price to stall, take partials rather than push through"* | **sliced by 53.6** |
| Options shelf 30368.2 | same | held as support, worst **−5.7**, 4 retests |
| London High (today) 30465.4 | *"the next session usually runs the stops above it"* | ran **6.4** above, failed, **capped 490min** |

The day's high 30471.8 landed **inside the 13.7pt band** between London High
(prev-day) 30479.1 and London High (today) 30465.4. The CALL WALL was 46.4pts
away and untested. With 09-28 (London High today ran 22.8 then capped 480min)
that is **2 sessions** where a prior London high was the true lid and the wall was
irrelevant. **Third instance and P-E(b) flips from "shelves replace the wall's top
line" to "session extremes do".** The shelf family's "all inside 22pts" record
also takes its first breach at 53.6.

**P-E census rule, separately.** The wall stalled price 46.4 below itself without
a touch — inside the "empty middle" band (12–103) the census calls empty. The
census requires a touch, so near-misses can never populate that band. **The empty
middle may be partly an artefact of the counting rule, not only of `SETTLE_TOL`.**

## H1 — n=21, and the ratio that closes the multiplier question

09-29: budget 118.6, extension 6.4, error **−112.2**. Series: `+61.2 −11.6 −73.0
−86.4 −10.7 −26.2 −64.0 +57.3 +44.3 +79.4 −81.3 +136.4 +40.0 −38.9 +569.2 −23.0
+25.9 +13.6 −124.4 +113.9 −112.2`. **Mean +23.3 (n=21); −4.0 without 09-21** —
which flips the sign of the 09-28 figure (+1.7), confirming that number was
carried by one tail point.

**The new figure is MAE 85.4 against a mean budget of 103.6 — the typical error
is 82% of the typical budget.** Last three sessions: −124.4, +113.9, −112.2. The
estimator is unbiased and carries essentially no per-day information, and **no
multiplier can repair that ratio** — a multiplier corrects bias, and there is no
bias to correct. **RECOMMEND CLOSING H1's multiplier branch as SETTLED-NEGATIVE**
and keeping only the qualitative state, which was right today: LOW_FUEL called
*"the range is close to done"* and the range grew **6.4pts**.

## H2 — first agreement instance in the LOW_FUEL / gamma conflict cell

09-29 is **LOW_FUEL and ABOVE the flip**, so the logged conflict does not arise:
the fuel block said *"favour fades over chasing breaks"* and the gamma block said
*"sweeps genuinely fail — this is your fade day."* **Both were right.** Both
extremes failed (upside by 6.4, downside by 0.4), traversal 218.8 with 6.4pts of
new range, close 80.9% up the range.

**This supports the logged coherence fix rather than weakening it:** all 3
recorded conflict instances (09-14, 09-15, 09-28) are **short**-gamma days, and
the one long-gamma LOW_FUEL day produces no conflict at all. The fix is correctly
scoped to the short-gamma branch.

## D7 — the breach table's convention is itself a defect

09-29: budget 118.6 → ±1.75x cap **207.6**. Forward-only (post-scan extremes
30471.8 / 30271.4): **no breach either side** (+78.3, −122.1). Under the
session-extreme convention the 09-28 table used: breach below **+66.4**, from the
**pre-scan** Asia low.

**09-28's breach was post-scan; today's would be pre-scan. The table conflates
them**, and the cap is a forward reachability claim, so forward-only is the
correct reading. Under forward-only the high-budget bucket becomes **3 of 9**;
under the 09-28 convention, 4 of 9. **The split holds either way** and the D7
proposal is unaffected — but the table should be re-stated forward-only before it
is quoted again.

## D23 — second clean day, and a caveat on the proposed cross-check

Offset **+18.2**, `nq_implied`: cash close **30276.81** + NQ move **+98.5** =
**30375.3**, which reconciles exactly. Ordinary basis, D23's roll-forward working.

**But the proposed cross-check is near-vacuous on days like this one.** It
compares the brief's NDX reference against futures-minus-premium — and on 09-29
the reference *was derived from* the futures delta, so the check is comparing a
number to its own construction. It retains power only through premium drift
between the cash close and the scan. **It must compare against an independently
measured NQ-minus-premium level**, not against the roll, or it clears roll-path
days by construction. It would still have caught 09-24, where the roll was absent.

**New instance of the same family, second code path.** The document published
**two conversion offsets 150.1pts apart for the same NDX option grid**: the level
board at **+18.2**, and section 7 at **+168.3** (`brief.py` ~line 95: CFD bar
close at the GEXBot feed time minus GEXBot's own spot). One of those two index
references is wrong by ~150pts. Section 7 is explicitly excluded from the call, so
**no damage today** — but this is the D23 mechanism in a second path, again behind
a reassuring label (*"matched to feed time"*). The D6-replacement cross-check
should run on **every** conversion path, not only the CBOE one.

## P-C / `events` — the row was ABSENT, and the census was measuring a constant

23 components today and **no `events` row at all**: the component is
`add("events", 0, ...)` over `heavyweight_earnings_next_5d` only, and there were
no heavyweight earnings. The macro calendar never reaches the score; the gate
requires `impact == "High"` within 1.5h. Today: two **Medium** prints **72 minutes
after the scan** (CB Consumer Confidence, JOLTS), a **High** Core PCE 23.7h out,
`event_gate: None`.

The census now reads **16 of 17 rows present, all zero — because zero is a
literal in the source.** Recording that the census was never testing a
hypothesis. Mechanism already logged as P-C; no new proposal. The day's largest
move began in the **13:30Z** open bar, before the 14:00Z prints, so no H20
instance either.

## P-G — instance #11

| day | level | offset vs price | published note |
|---|---|---|---|
| 09-29 | Asia High (today) 30359.2 | **−34.3** | *"the next session usually runs the stops **above** it"* |

Price was already 34pts above it; the stops above it were taken before the scan.
**11 instances.** Also worth noting that the two *correctly*-sided session-low
notes today (30280.6, 30275.8) were wrong in a different way — price came 0.4pts
below one and never reached the other, so *"usually runs the stops below it"* was
the wrong forecast even on the right side. P-G's fix addresses sidedness only.

## Max pain — third distance-confounded miss

30168.2, never reached, **103.2pts** short of the post-scan low, on a **Tuesday**.
Evidence days now 5, of which **3 are distance misses** (246, 340, 103). The
register's own recommendation — tighten the threshold to *"3 days on which max
pain is within reach"* — is reinforced. Still ungradeable until M6 is decided,
since the reaction verdict is the contaminated variable.

## No instance today

- **P-E** — CALL WALL untouched, 46.4 short. Still 4 capped / 5 sliced.
- **H6 / P3** — no `structural` level published.
- **D21** — `gamma +0` *"price mid-band, 69% up the range"*; the row did not fire.
- **P-F** — price was inside the prior-day range at the scan (+11.0 vs PD mid,
  well inside PDH/PDL), so this is an inside-range control: error **−112.2**.
  Inside/marginal control becomes **17 days**.
- **H22** — week net GEX 4.259 with realised range 0.76x ADR; logged, no claim.

## Journal hygiene

No fabricated or backfilled entries; no `prediction` block touched. 09-24
quarantined as directed. 09-25 not re-graded — figures cited from the 09-28 entry.

**`track.py` has no quarantine mechanism and still counts 09-24 as CORRECT**, so
every review from here must carry the exclusion by hand or the tally drifts
silently. That is the second hand-carried correction in this register (the other
being 09-25's late grading, already flagged as *"worth a guard"*). **Both want the
same fix: a `quarantine` field in the journal schema that `track.py` and
`review_day.py` read**, so the exclusion is data rather than prose in a review
file that a future reader may not open.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01M7sro1DKMp5T7EBDusm6pM

---

# Observations appended 2026-10-01 (grading the 2026-09-30 session)

1 gradeable PRE_NY scan, `is_trading_day: true`, 0 test artefacts, 276 M5 bars
(09-29 22:00Z → 09-30 20:55Z). O 30412.5 / H 30655.2 / L 30262.0 / C 30469.1,
range **393.2 = 0.84x** ADR14 468.4, net **+56.6** (52.7% close position).
Direction **WRONG** (MILDLY BEARISH −3). Post-scan move **+24.0** on traversal
267.9 — wrong by 9.0% of the distance travelled. Fuel budget 203.4 vs extension
128.2 → **−75.2, 1.59x over**; traversal 1.32x. Hit rate **0.47** published
(8/17), **0.24** on distinct touch events (4/17). High 15:50Z post-scan, **low
11:20Z pre-scan**; pre-scan H/L 30527.0 / 30262.0, post-scan 30655.2 / 30387.3.

**2026-09-24 remains excluded** from the options fields, the direction tally and
the hit-rate series per *D23 CORRECTED*; its fuel error (+13.6) is kept on the D1
precedent and is inside the H1 series below. `track.py` has no quarantine and
still prints it CORRECT, so the counts here are carried by hand off its per-scan
table, as the 09-28 and 09-29 reviews did. **09-25's row (bias +1, no-call) is
taken from `track.py`'s table and agrees with the 09-28 review's entry**; it was
not re-derived, and no review file was back-dated for either day. The 09-23
review's pre-registered D21 test stays void.

Record, 09-24 excluded: PRE_NY **9 right / 5 wrong / 3 no-call over 17 days**.
All sessions **14 / 9 / 7**. (`track.py` raw: 15 / 9 / 7.)

## H18 / P1 — 9th instance, and the FIRST where a stale row is the sole margin of a WRONG call

The score was **−3, exactly on the threshold** (`bias_engine.py:271`,
`total <= -3`), carried entirely by **macro −6**.

| row | pts | its own words |
|---|---|---|
| macro DFII10 2.9% | **−3** | *"FRED has not published since 2026-09-28 (2 business days ago) — this is last week's reading, not today's"*. Largest single row in the model |
| macro DGS10 | **−1** | *"moved 7bp **up** (2026-09-25 to 2026-09-28)"* — Friday→Monday |
| rates US10y | **+1** | *"5.207 (−0.91%) — yields **down**, BULLISH tech"* |

**Dropping DFII10 alone → score 0 → `NEUTRAL / TWO-WAY`, no direction call, and
the WRONG disappears.** Dropping the stale DGS10 as well → +1, also neutral.
H18's 6th, 7th and 8th instances all landed on *correct* calls, which is why the
register kept saying H18 must not be fixed on accuracy grounds alone. **This one
is the damage instance the sequence was missing.**

**New: the DGS10 duplication is now observed in both sign configurations.** On
09-29 the stale DGS10 and the live US10y row pointed the same way and "yields
fell" was worth +2; on 09-30 they carry **opposite signs on the same instrument**
and cancel through two rows. Code-certain either way.

**Textual sub-defect, code-certain.** DFII10's `why` renders *"this is last
week's reading"* unconditionally. The observation date is **2026-09-28, the
Monday of the same week.** The phrase was correct on 09-29 (09-25 reading) and is
wrong today.

**`news −2` was independently sufficient to flip the call** — at news 0 the score
is −1, also neutral. So two separate degraded blocks each carried the whole
margin on the same day.

**PROPOSED (shipping, not observing).** Age-gate the FRED block: zero or halve
any row whose observation is more than one business day old; suppress DGS10
whenever a live US10y read exists. Expected effect: 09-30 → no-call, PRE_NY
record 9/5/3 → **9/4/4**, 09-28 and 09-29 labels unchanged. **Must ship with
D22(a)**, per the 09-28 and 09-29 entries — H18 alone would have degraded 09-28.

**D22(a) did not fire today.** Breadth read NDX +0.21% vs ES +0.40% — the 09-29
cash session, the correct latest — and both breadth rows scored 0. The coupling
above is carried from 09-28/09-29, not from this session.

## P-B(b) — 8th session, and the worst inflation ratio in the series

| day | published | touched | distinct touch bars | published rate | distinct-event rate |
|---|---|---|---|---|---|
| 09-18 | 9 | 7 | 7 | 0.78 | 0.78 |
| 09-21 | 7 | 3 | 2 | 0.43 | 0.29 |
| 09-22 | 16 | 9 | 5 | 0.56 | 0.31 |
| 09-23 | 21 | 12 | 7 | 0.57 | 0.33 |
| 09-25 | 14 | 7 | 6 | 0.50 | 0.42 |
| 09-28 | 7 | 4 | 4 | 0.57 | 0.57 |
| 09-29 | 15 | 10 | 7 | 0.67 | 0.47 |
| **09-30** | **17** | **8** | **4** | **0.47** | **0.24** |

**1.96x — the worst recorded.** Four levels — Asia High (today) 30486.8, PDH
30471.8, London High (prev) 30465.4, London High (today) 30457.3 — were all
resolved by `bar_index 178`, **the 12:50Z scan bar itself**, so the first graded
bar settled four of the eight touches. 30471.8 / 30465.4 are **6.4pts apart**,
inside the structural gap between `merge_tol = max(3.0, 468.4*0.008) = 3.747` and
`TOUCH_TOL = 8.0`. Second code-certain instance of that pair after 09-29.

**Tolerance-only touches: 0 of 8 today** (no negative `travel_up`/`travel_down`).
Series now 09-25 2/7, 09-29 2/10, 09-30 0/8 — **n=3 sessions, and it is
intermittent**. Still folded into P-B(b)(b), which reports it for free; nothing
separate proposed.

## Session-context field — 4th session, and the census that should end the argument

Already **PROPOSED** on 09-29 (`tested_today` on each `prediction.levels` entry;
`review_day` to grade against the whole session). Today is the largest single-day
instance count in the record.

Pre-scan range **30262.0–30527.0 already contained 12 of the 17 published
levels**, and **6 of the 9 levels the grader reports as "never reached" were
reached — before the scan**:

| level | published as | what had already happened |
|---|---|---|
| PUT WALL 30337.7 ⭐ | *"expect a bounce and a good long-sweep here"*, −124 away | **below it for 39 bars, 02:30Z→12:25Z, 75.7pts through**, reclaimed **22 minutes before the brief was written**. Graded *"never reached"* |
| London Low (today) 30262.0 | *"the next session usually runs the stops below it"*, −199 | **it is the session low, to the point** (11:20Z). Graded *"never reached"* |
| PDH + NY High 30471.8 ⭐ | *"Sweep it, wait for a lower high, CISD = short"* | above it from **00:00Z**, 103 bars. Swept pre-scan; post-scan it ran **+183.4** and the CISD short was the losing side |
| Asia High (today) 30486.8, London High (prev) 30465.4, London High (today) 30457.3 | *"the next session usually runs the stops above it"* | all three **already exceeded** by the pre-scan high 30527.0; post-scan they ran +168 to +198 |
| Asia High (prev) 30359.2, PD mid 30295.7, Asia Low (today) 30291.1, London Low (prev) 30275.8 | forward levels | all inside the pre-scan range; PD mid broken 06:45Z–12:15Z |

With 09-17, 09-28 and 09-29 that is **4 sessions**. The proposal is unchanged.

## M6 — instances 14 and 15, both of the "benign number hides the real breach" type

Code-certain mechanism, restated: `settled_read` sets `last_far` to the last bar
on the far side and measures `worst_excursion` only over bars **after** it, so
**every excursion before the final settle is invisible by construction.**

| level | verdict rendered | what the bars show |
|---|---|---|
| CALL WALL 30537.7 | *"broke UP through it — **lost by 39.2pts**"*, `settled_from 19:45` | **73 bars above it, 13:30Z→19:50Z, +117.5 through** — a 6h20 hold, 3.0x the reported figure |
| Options shelf 30637.7 | *"stalled at it — held as resistance 285min, **worst +5.6pts**"*, `settled_from 16:10` | **6 bars above it, 14:05Z→16:15Z, +17.5 through** — 3.1x the reported figure |

Both rows also contradict their own `first_touch_reaction` ("broke DOWN through
it" on the shelf the day's high exceeded; "traded both sides" on the wall the
reaction field calls a clean break up). **15 sessions. M6 needs a decision.**

## P-E — 10th instance; 4 capped / 6 sliced, and the middle is still empty

CALL WALL 30537.7 touched and **sliced by 117.5**. Slice mode now
103 / 117.5 / 154 / 185 / 205 / 573; cap mode still 3.6–11.9. **The 12–103 band
remains empty at n=10.** Note today's 117.5 is the smallest slice on record and
sits just outside the band — the bimodality is holding but the gap is narrowing
from the top.

## P-E(b) — today CONTRADICTS 09-29's session-extreme reading

| lid theory | sessions | today |
|---|---|---|
| an options **shelf** is the lid | 09-18, 09-21, 09-22, 09-23, **09-30** | shelf 30637.7 capped the high at **+17.5** |
| a prior **session extreme** is the lid | 09-28, 09-29 | **fails** — all four upside session extremes sliced by **168–198** |

Shelf family: 8th instance at +17.5, back **inside 22pts** after 09-29's first
breach at 53.6 (7 of 8 inside 22). **The lid question is now unstable at 5 vs 2
and NOTHING is proposed beyond what P-E already proposes** — the 09-29 entry's
flip from "shelves" to "session extremes" was made on 2 sessions and should be
read as withdrawn rather than confirmed.

**Counter-evidence inside the same document, and it is the nearest shelf that
failed.** Section 3 named **30487.7** as *"Expect a stall (26pts away) — take
partials into it"*. Price **sliced it by +167.5**. So on one day the shelf
+150 away capped the session and the shelf +26 away did nothing. The P-E(b)
census has only ever counted **board-published** shelves, so it has been
selecting on distance without saying so.

## H23 (NEW, opened 2026-10-01) — does the fuel section's named brake ever brake?

**Claim.** `path_read()`'s *"UPSIDE/DOWNSIDE path"* sentence names a single
strike as the stall, chosen by `reach = max(budget, adr*0.25)` (D15's fix). That
strike is a **forecast about a specific price** and has never been graded.

**Why it matters.** It is the only place the brief tells the trader to take
partials at a level that is **on no table in the document**. 30487.7 appears
neither on the level board (shelves there: 30637.7, 30537.7) nor in the
secondary-concentrations table (30737.7, 30437.7, 30787.7, 30237.7, 30587.7).
The trader cannot mark it, and the reviewer never scores it.

**Evidence: n=1.** 09-30, upside brake 30487.7 at +26, *has friction* — **sliced
by +167.5**, 0.36x ADR.

**Threshold / what would settle it.** Three sessions on which the path sentence
names a brake and price reaches it; record penetration in points and in ADR, and
whether the named strike also appears on the board.

**Status: OBSERVING. Nothing proposed.** D15's reach fix is working as designed —
this is about the accuracy of the claim it gates, not the gate.

## H1 — n=22, and a fourth consecutive large error

09-30: budget 203.4, extension 128.2, error **−75.2**. Series: `+61.2 −11.6
−73.0 −86.4 −10.7 −26.2 −64.0 +57.3 +44.3 +79.4 −81.3 +136.4 +40.0 −38.9 +569.2
−23.0 +25.9 +13.6 −124.4 +113.9 −112.2 −75.2`. **Mean +18.8 (n=22); −7.4 without
09-21.** MAE **84.9** against a mean budget of **108.1** — the typical error is
**79% of the typical budget**, essentially unchanged from 09-29's 82%.

Last four: **−124.4, +113.9, −112.2, −75.2.** The 09-29 recommendation to close
H1's **multiplier branch as SETTLED-NEGATIVE** is reinforced by a fourth point:
the estimator is unbiased and carries no per-day information, and a multiplier
corrects bias. The **qualitative** state was again serviceable — MODERATE said
*"the range has room but not unlimited room… don't plan on a third leg"* and the
range grew 128.2 of 203.4 (0.63x), which `review_day` grades *"about right"*.

## H19 — mandated per-scan record

| scan | counted | uncounted | sign of counted | score | coverage |
|---|---|---|---|---|---|
| 2026-09-30 12:47 | 2 (0 bull / 2 bear) | 51 | **100% bearish** | **−2** | **3.8%** of 53 relevant |

One concrete item for the unrun hand-score test: the uncounted pile contained
*"Fed's preferred gauge showed core inflation at 3.0% in August, **much lighter
than expected**"* — unambiguously bullish and of the same `cpi_*` family the
scorer does read — while *"U.S. inflation rises again"* voted −1 at HIGH
confidence from the same pile. **This is one headline, not the hand-score test,
and the weight does not move.** Status: **OBSERVING**.

**No D18 instance today.** Checked both scored headlines: neither contains a
`risk_on` token, and *"A hawkish Federal Reserve won't deliver bullish hikes"* is
defensibly bearish despite containing "bullish" in a negated construction. The
first-match-wins defect did not fire.

## H4 — the cleanest row on the board

GAMMA FLIP 30391.7 held as **support, worst −4.4, 490min**, and the post-scan low
30387.3 undercut it by 4.4 at 20:00Z before closing 77.4 above. The `gamma +2`
row (*"above flip — dips supported, upside grinds"*) was **the only directionally
correct component in a −3 score.**

**But the same block's strategy text was wrong on the day's dominant leg.**
`STRATEGY 1` read *"dealers fade extensions, so sweeps genuinely fail — this is
your fade day"* on a session that ran **+193.9 from the scan**, through four
session-extreme levels and **117.5pts through the call wall**, before reverting.
The logged coherence fix is scoped to the **short-gamma** branch; this is the
**long-gamma / MODERATE-fuel** cell. **n=1, nothing proposed** — recorded so a
second instance is counted rather than rediscovered.

## D23 — third clean offset, and the caveat is live, not cleared

Offset **+37.7**: NDX reference **30423.6** (cash close rolled forward by the NQ
move **+84.2**) against CFD 30461.3. Ordinary basis, in the 8–46pt range.

**This is an `nq_implied` roll-path day, so the proposed cross-check reports
nothing.** Per the 09-29 entry, comparing the brief's reference against
futures-minus-premium is circular when the reference *is* the futures delta. It
is **not validated by today** and must still be re-specified against an
independently measured NQ-minus-premium level before it replaces D6.

**Two offsets for one grid — 2nd instance.** Level board **+37.7**, section 7
**−20.3**: **58.0pts apart** (09-29: 150.1). Section 7 printed *"No volume has
traded yet today"* and is excluded from the call, so **no damage** — but this is
the second consecutive session in which the second conversion path disagrees with
the board behind a reassuring label (*"matched to feed time"*).

## Max pain — 4th distance-confounded miss

30212.7, never reached, **174.6pts** short of the post-scan low 30387.3, on a
**Wednesday** (the brief's own text: *"weak on a Monday, strong by
Thursday/Friday"*). Evidence days now 6, of which **4 are distance misses** (246,
340, 103, 175). The register's recommendation to tighten the threshold to *"3 days
on which max pain is within reach"* stands, and remains ungradeable until M6 is
decided.

## No instance today

- **H6 / P3** — no `structural` level published.
- **D21** — `gamma +0` *"price mid-band (30337.7–30537.7), 62% up the range"*; the
  row did not fire. The 09-23 pre-registered test stays void per *D23 CORRECTED*.
- **The structure row's tolerance band** — `price_at_scan − PD mid = +165.6`, far
  outside the 30pt window. Stays **2 of 3**; the third-instance test is unchanged.
- **P-F** — price inside the prior-day range at the scan (10.5 below PDH, 165.6
  above PD mid): inside-range control, error **−75.2**. Control becomes **18
  days**.
- **D7** — budget 203.4 → ±1.75x cap **355.95**. Forward-only (post-scan extremes
  30655.2 / 30387.3 vs price_at_scan 30461.3): **no breach** either side (+193.9,
  −74.0). High-budget bucket **3 of 10** on the forward-only convention the 09-29
  entry fixed. No level was filtered out — the furthest published row, PDL
  30119.5 at −341.8, is inside the cap.
- **P-C / `events`** — **no `events` row at all** again (24 components, none
  `events`): the component is `add("events", 0, …)` over
  `heavyweight_earnings_next_5d` only, and there were none. Three **Medium**
  calendar items (19:30Z Trump, 22:00Z Kashkari, 12:30Z+23.7h Claims),
  `event_gate: None`. The day's dominant leg topped at **15:50Z**, well before
  the 19:30Z item, so **no H20 instance** either.
- **H22** — week net GEX **0.036 $bn/1%** → *"pinning likely"*; realised range
  0.84x ADR, net +56.6, close 52.7% up the range. Mildly consistent; logged, no
  claim.
- **P-G** — the four *"runs the stops above it"* notes today are session-context
  failures rather than sidedness failures (each was correctly sided and already
  exceeded), so they are counted under the session-context entry above, **not**
  as P-G instances. P-G stays at 11.

## Journal hygiene

No fabricated or backfilled entries; no `prediction` block touched. 09-24
quarantined as directed. 09-25 cited from the 09-28 entry, not re-derived; no
review file back-dated for 09-24 or 09-25.

**Third consecutive review to carry the 09-24 exclusion by hand.** The 09-29
entry proposed a `quarantine` field in the journal schema that `track.py` and
`review_day.py` read; today adds nothing to the argument except another
opportunity for the correction to be dropped silently. **Reaffirmed.**

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01M7sro1DKMp5T7EBDusm6pM

---

# Observations appended 2026-10-02 (grading the 2026-10-01 session)

1 gradeable PRE_NY scan (12:47:53Z), `is_trading_day: true`, 0 test artefacts,
276 M5 bars (09-30 22:00Z → 10-01 20:55Z). O 30462.5 / H 30903.4 / L 30285.5 /
C 30526.8, range **617.9 = 1.33x** ADR14 463.3, net **+64.3** (39.1% close
position). Bias **+2 NEUTRAL — no direction call**; post-scan move **−74.7**
(direction −1) on traversal 351.8. Fuel budget **0.0** vs extension **153.7** →
**+153.7, UNDER**. Hit rate **0.67** published (2/3), **0.67** distinct. Scan bar
178 of 276. Pre-scan H **30903.4 (06:10Z)** / L 30439.2 (the opening bar);
post-scan H 30637.3 (17:45Z) / L **30285.5 (15:10Z)** — the extension was
**entirely downside**.

**2026-09-24 remains excluded** from the options fields, the direction tally,
the hit-rate series, P-E, P-E(b), H6 and M6 per *D23 CORRECTED*; its fuel error
(+13.6) is kept on the D1 precedent and sits inside `track.py`'s H1 series, so
H1 needs no hand correction. `track.py` has no quarantine and still prints
09-24 CORRECT, so the direction counts are carried by hand off its per-scan
table, as the 09-28, 09-29 and 09-30 reviews did. **09-25's row is cited from the
09-28 review's register entry**, not re-derived; no review file was back-dated
for 09-24 or 09-25. The 09-23 pre-registered D21 test stays void.

Record, 09-24 excluded: PRE_NY **9 right / 5 wrong / 4 no-call over 18 days**.
All sessions **14 / 9 / 8**. (`track.py` raw: 15 / 9 / 8.)

## H18 / P1 — 10th instance, and it REVERSES the 09-30 proposal's sign

Score **+2**; `bias_engine.py` labels `MILDLY BULLISH if total >= 3`.

| row | pts | its own words |
|---|---|---|
| macro HY OAS 3.08% | **−2** | *"+40bp over 5 days… the bond market is getting nervous"* — **no observation date rendered at all** |
| macro DGS10 | **−1** | *"moved 2bp up (2026-09-28 to 2026-09-29)"* — stale AND duplicated |
| rates US10y | **0** | *"5.283 (−0.19%) — yields flat"* — the live read on the same instrument |
| macro DFII10 2.91% | **0** | observation 2026-09-29; scored zero, no damage |

The 09-30 entry PROPOSED, as shipping, (a) an age-gate zeroing FRED rows more
than one business day old and (b) suppressing DGS10 whenever a live US10y read
exists. DGS10's observation is 09-29, two business days back, so **either half
zeroes it → score +3 → `MILDLY BULLISH` → a long call into a −74.7 post-scan
move. Yesterday's fix manufactures a WRONG call on the very next session.**

**Across its only two damage instances the fix is accuracy-neutral: it removes
one WRONG (09-30) and creates one (10-01).** The 6th/7th/8th instances landed on
correct calls. **PROPOSED → the accuracy case is RETRACTED.** The duplication and
the stale rows are code-certain and should be fixed on **correctness** grounds
only, coupling to D22(a) unchanged.

**Blocker found for the age-gate.** `HY OAS` is now the largest surviving macro
row (−2 of macro −3) and renders **no observation date**. Whether it can be
age-gated at all is unverified; if it cannot, the gate silently exempts the
biggest contributor. Resolve before shipping.

**DGS10 duplication, third sign configuration.** 09-29 stale and live agreed
(+2 between them); 09-30 opposite signs cancelling; 10-01 stale **−1** against
live **0**, so the stale row is the entire net. Code-certain in all three.

**DFII10 textual sub-defect, 2nd consecutive instance.** *"this is last week's
reading, not today's"* renders unconditionally; the observation date is
**2026-09-29, Tuesday of the current week** (Mon 09-28 / Tue 09-29 / Wed 09-30 /
Thu 10-01). Scored 0, so no damage. Wrong on 09-30 and wrong again today.

## D7 — the degenerate case, and it is the clean instance the register lacked

`keep()` filters session-extreme and PD/PW levels by `abs(dist) <= budget*1.75`.
With **`budget = 0.0` the cap is 0.0**, so the predicate passes only at
`dist == 0` and **every non-exempt level is rejected regardless of distance.**

That is what collapsed the board to **3 gamma rows** — the smallest in the record
— and pushed six real levels into the footnote *"Beyond today's range (context
only, don't mark)"*:

| demoted level | dist from scan | what happened |
|---|---|---|
| 30903 Asia High (today) | +300 | **it is the session high, to 0.4pt** (06:10Z) |
| 30512 London Low (today) | **−91.5** | first touched 13:30Z, penetrated by **226.5** |
| 30487 Asia High (prev-day) | **−116.5** | first touched 13:30Z, penetrated by **201.5** |
| 30655 PDH+NY High / 30797 London High / 30820 PWH | +52 to +217 | not reached post-scan |

Forward-only breach of the ±0.0 cap: **+33.8 above, +318.0 below.** 09-17 is the
only other zero-budget PRE_NY day and breached +470.1. **D7's second half is
re-proposed with the mechanism named: exempt session-extreme and PD/PW levels as
the gamma levels already are, or floor the cap at a fraction of ADR so a zero
budget cannot reject the whole board.**

**Side effect worth recording: H6/P3 cannot accumulate evidence on low-budget
days**, because no `structural` level survives to be published.

## P-B(b) — 9th session, inflation 1.00x, and the mechanism is now proven

3 published / 2 touched / **2 distinct → 1.00x**, the first session in the series
with no inflation at all, immediately after 09-30's worst-ever **1.96x**. The
only difference is that D7's zero budget stripped the dense structural cluster
and left three levels 400 and 28pts apart. **The inflation is caused by
publishing clustered structural levels, not by `TOUCH_TOL`.**

| day | published | touched | distinct | pub rate | distinct rate |
|---|---|---|---|---|---|
| 09-18 | 9 | 7 | 7 | 0.78 | 0.78 |
| 09-21 | 7 | 3 | 2 | 0.43 | 0.29 |
| 09-22 | 16 | 9 | 5 | 0.56 | 0.31 |
| 09-23 | 21 | 12 | 7 | 0.57 | 0.33 |
| 09-25 | 14 | 7 | 6 | 0.50 | 0.42 |
| 09-28 | 7 | 4 | 4 | 0.57 | 0.57 |
| 09-29 | 15 | 10 | 7 | 0.67 | 0.47 |
| 09-30 | 17 | 8 | 4 | 0.47 | 0.24 |
| **10-01** | **3** | **2** | **2** | **0.67** | **0.67** |

**Warning about the scoreboard itself: 0.67 is above the 0.53 series mean and was
bought by publishing almost nothing**, on a board that missed the session high by
167pts. Hit rate alone is not a quality measure — it is trivially gamed by
shrinking the board, and D7's zero-budget branch does exactly that automatically.

## Session-context field — 5th session, and the strongest instance yet

Already PROPOSED on 09-29 (`tested_today` per `prediction.levels`; grade against
the whole session). Today the **headline level on the board** is the instance.

**CALL WALL 30736.0**, published at 12:47Z as *"Heaviest ceiling this week…
rallies stall. Take profit into it… the strongest ceiling on the board"*, under a
banner reading *"everything below is fresh"*. In the same graded session,
**29 bars printed highs above it and 27 bars CLOSED above it, 04:50Z → 07:10Z,
reaching 30903.4 = 167.4pts through** — a 2h20 hold ending six hours before the
brief was written. `review_day` grades it **"never reached."** Forward-only that
is correct: the post-scan high 30637.3 sat 98.7 below it.

With 09-17, 09-28, 09-29 and 09-30 that is **5 sessions**. The proposal is
unchanged.

## H23 — instance 2 of 3, and yesterday's framing needs a correction

| session | brake | dist | outcome |
|---|---|---|---|
| 09-30 | 30487.7 upside | +26 | **sliced +167.5** (0.36x ADR); on **no** table |
| 10-01 | 30586.0 downside | −18 | **sliced 300.5** (0.65x ADR); on the secondary table |
| 10-01 | 30636.0 upside | +32 | **capped at +1.3** — it *is* the post-scan high; on the secondary table |

**n=2 sessions against a 3-session threshold → NOT actionable, nothing
proposed.** Two corrections to the 09-30 opening entry: both of today's named
strikes **do** appear on the secondary-concentrations table, so *"the trader
cannot mark it"* is day-dependent rather than structural; and the brake aligned
**with** the day's dominant leg was sliced 300.5 while the one **against** it
capped at 1.3 (n=1, recorded only so a second instance is counted).

## P-E — no forward-only instance; the empty middle survives either way

The CALL WALL was **untouched post-scan**, so there is no 11th instance on the
forward-only convention. Census unchanged: **4 capped / 6 sliced**, cap mode
3.6–11.9, slice mode 103/117.5/154/185/205/573. Were the pre-scan penetration
counted it would be **+167.4**, which lands inside the existing slice mode, so
**the empty 12–103 band is not disturbed on either convention.**

## P-E(b) — shelf family 9th instance at +1.3, and distance is non-monotonic

The lid was the options shelf **30636.0**, which capped the post-scan high at
**+1.3**. Shelf family now **8 of 9 inside 22pts**.

Today again contradicts the 09-29 *"session extreme is the lid"* reading — all
four upside session extremes were pre-scan and never revisited. **The 09-29 flip
stays WITHDRAWN, per the 09-30 entry; it is not re-flipped back.** 5 vs 2 is not
a resolution.

**The census's undeclared selection on distance is now demonstrably
non-monotonic:** 09-30's nearest shelf (+26) failed while the far one (+150)
capped; 10-01's nearest (+32) capped. **Which** shelf will cap remains
unpredicted. Caveat live. Nothing proposed beyond what P-E already proposes.

## M6 — 16 sessions; an understatement and an inversion on the day's best call

**`review_day` mislabels the single best call in the document as a failure.**

PUT WALL 30336.0, published *"expect a bounce and a good long-sweep here"*:
first touch 14:05Z, swept **50.5pts through** to the session low 30285.5 at
15:10Z, reclaimed, settled above from 15:50Z, closed **+190.8 above** after a
**+241.3** reversal. Rendered *"broke DOWN through it — **lost by 25.3pts**"*,
`acted_as: "lost"`, `held: false` — while `first_touch_reaction` on the **same
row** says *"broke UP through it"*.

- **Understatement, the standing mechanism:** reported 25.3 vs actual **50.5** —
  **2.0x**, because `settled_read` measures `worst_excursion` only over bars
  after the final settle.
- **English inversion:** *"broke DOWN"* on a level that closed 190.8 above.
- GAMMA FLIP 30307.8's figure is **accurate** today (reported −22.3 = 30307.8 −
  30285.5), because its `last_far` falls early. The defect is intermittent in its
  visible effect, not in its mechanism.

**16 sessions. M6 needs a decision, not more evidence. Not re-proposed.**

## H1 — n=23, a fifth consecutive large error, and the mean is now ~zero

10-01: budget **0.0**, extension **153.7**, error **+153.7**. Series: `+61.2
−11.6 −73.0 −86.4 −10.7 −26.2 −64.0 +57.3 +44.3 +79.4 −81.3 +136.4 +40.0 −38.9
+569.2 −23.0 +25.9 +13.6 −124.4 +113.9 −112.2 −75.2 +153.7`. Mean **+24.7**
(n=23); **−0.08 without 09-21**. MAE **87.9** against a mean budget of **103.5**
— the typical error is **85% of the typical budget**, up from 82% (09-29) and
79% (09-30).

Last five: **−124.4, +113.9, −112.2, −75.2, +153.7.**

**The multiplier branch should be closed SETTLED-NEGATIVE.** At n=22 excluding
the 09-21 outlier the mean error is **−0.08** — an unbiased estimator carrying no
per-day information. A multiplier corrects bias; there is none left to correct.
Third consecutive entry making this recommendation.

**The qualitative state was wrong on its specific claim and right on its
advice.** `EXHAUSTED` text: *"the day's range is set… expect real movement still,
just **within** the extremes rather than beyond them. Continuation into new
highs/lows is the low-probability trade."* Price made a **new session low**,
153.7 beyond the pre-scan low. The *"Stop management"* paragraph — fade the
extremes back into the range — then caught the +241.3 reversal off that low.

## H4 — 2nd consecutive clean flip read, and STRATEGY 1 was right this time

GAMMA FLIP 30307.8 held as **support**, worst **−22.3**, 490min, closed **+219.0**
above; the `gamma +2` row was the most useful line in the document. 09-30's worst
was −4.4.

**Counter-instance to the 09-30 strategy-text failure.** *"Dealers fade
extensions… this is your fade day"* was **correct** post-scan: the sweep of the
put wall and the flip failed and reversed +241.3, and the overhead shelf capped
at +1.3. Note the cell differs — 09-30 was long-gamma / **MODERATE** fuel, today
is long-gamma / **EXHAUSTED** — so this does not settle 09-30's n=1. Both stand.

## D23 — 4th clean offset; cross-check still circular; 3rd consecutive split grid

Offset **+36.0**: reference **30567.5** (cash close rolled forward by the NQ move
**+159.0**) against CFD 30603.5. Ordinary basis, 8–46pt range.

**Again an `nq_implied` roll-path day, so the proposed cross-check reports
nothing and is NOT validated.** Per the 09-29 and 09-30 entries, comparing the
brief's reference against futures-minus-premium is circular when the reference
*is* the futures delta. It still needs re-specifying against an independently
measured NQ-minus-premium level before it can replace D6.

**Two offsets for one grid — 3rd CONSECUTIVE instance, threshold met.** Level
board **+36.0**, section 7 **+194.0**: **158.0pts apart** (09-29: 150.1; 09-30:
58.0). All three are damage-free only because section 7 is research-only and had
no volume (*"No volume has traded yet today"*), and all three sit behind the
label *"matched to feed time"*. **PROPOSED: derive both grids from one
conversion, or make section 7 reuse the board's offset and print the feed-time
delta separately.** Expected effect: no change to any call today; removes a 158pt
latent error that becomes live the first time H12/H13 promote section 7.

## Dead-weight audit — refreshed counts, and they are decisive

Measured across the first scan of every `is_trading_day: true` entry (**24 scans,
23 completed days**):

| row | days it scored ≠ 0 |
|---|---|
| `macro` NFCI financial conditions | **0 / 24** |
| `macro` yield curve 10y–2y | **0 / 24** |
| `macro` WALCL / RRP | **5 / 24**, all 08-24…08-28 — **0 of the last 19** |

For contrast, on the same basis: DGS10 **23 / 23**, DFII10 18 / 24, pools
13 / 24, prior-week range 9 / 24.

**PROPOSED: drop or replace NFCI, the yield curve and WALCL/RRP.** Expected
effect: no score changes on any day in the record, a shorter macro block, and the
audit's stale *"0 / 16"* figure retired.

## H19 — lowest coverage recorded

| scan | counted | uncounted | sign | raw | score | coverage |
|---|---|---|---|---|---|---|
| 2026-10-01 12:47 | 1 (1 bull / 0 bear) | 55 | 100% bullish | +0.66 | **0** | **1.8%** of 56 relevant |

The single scored headline was bullish and was then **rounded to 0** by the
`NEUTRAL` label threshold, so news contributed nothing. The uncounted pile held
*"Broadcom to lend Anthropic up to $42 billion to lease its chips, filing says"*
and *"These 5 AI chip stocks are must-own into Q4, BofA says"* — both NDX-
material. Previous low was 3.8% (09-30). Status **OBSERVING**; the weight does
not move without the hand-score test.

**No D18 instance.** The one scored headline matched `cpi_cool` and contains no
`risk_on` token (`rally|surge|soar|jump|record high|all-?time high|rebound`);
*"hold gains"* is not in the pattern. First-match-wins did not fire.

## Max pain — a hit, and it is unusable

30306.0 was **touched and held as support** (worst −22.3, 490min) on a
**Thursday**, consistent with the brief's own *"weak on a Monday, strong by
Thursday/Friday"*. **But it sat 1.8pts from the gamma flip**, so the hold cannot
be attributed to max pain rather than to the flip. **Confounded — not counted as
max pain's first clean in-reach success.** Evidence days now 7, of which 4 are
distance misses (246, 340, 103, 175) and 1 is confounded. The recommendation to
tighten the threshold to *"3 days on which max pain is within reach"* stands and
remains ungradeable until M6 is decided.

## H22 — the label is not discriminating

Week net GEX **5.58 $bn/1%** → *"pinning likely"*. **09-30 printed the same words
at 0.036.** A 155x difference in the input, the same output label, and the larger
reading produced the **wider** realised range (1.33x vs 0.84x ADR). Graded
forward-only the pin claim is defensible — price reverted 241 of 318 and the
overhead shelf capped at +1.3; graded on the session it is not. n=2, logged, no
claim, and the session-context confound applies here too.

## No instance today

- **D21** — `gamma +0` *"price mid-band (30336.0–30736.0), 67% up the range"*;
  the row did not fire. The 09-23 pre-registered test stays void per
  *D23 CORRECTED*.
- **H6 / P3** — no `structural` level published, because D7 stripped them all.
- **P-C / `events`** — **no `events` row at all** again (24 components, none
  `events`): the component is `add("events", 0, …)` over
  `heavyweight_earnings_next_5d` only, and there were none. Two **Medium** items
  1.2h out (14:00Z Waller, 14:00Z ISM Manufacturing) and three **High** items at
  +23.7h (NFP, AHE, U-rate), `event_gate: None`. The day's low landed **15:10Z,
  1h10 after** the 14:00Z pair, so **no H20 instance**.
- **P-F** — price inside the prior-day range at the scan (51.7 below PDH, 341.5
  above PDL): inside-range control, error **+153.7**. Control becomes **19 days**.
- **The structure row's tolerance band** — `price_at_scan − PD mid = +144.9`, far
  outside the 30pt window. Stays **2 of 3**; the third-instance test unchanged.
- **P-G** — no sidedness failure; the demoted footnote levels are counted under
  D7 and the session-context entry, not here. P-G stays at **11**.
- **18 of 24 scored rows were 0**; the +2 came from 6 rows.

## Journal hygiene

No fabricated or backfilled entries; no `prediction` block touched. 09-24
quarantined as directed. 09-25 cited from the 09-28 entry, not re-derived; no
review file back-dated for 09-24 or 09-25. 2026-10-02's scan exists and is
correctly **held back** by `track.py` (179 bars so far) — it is counted only in
the dead-weight component census, where its scan-time values are valid and its
outcome is irrelevant.

**Fourth consecutive review to carry the 09-24 exclusion by hand.** The 09-29
entry's proposed `quarantine` field in the journal schema, read by `track.py` and
`review_day.py`, is **reaffirmed** — today adds only another opportunity for the
correction to be dropped silently.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01M7sro1DKMp5T7EBDusm6pM

---

# Sweep → failed re-break → reversal, measured. 2026-10-02

First quantitative test of **Strategy 1 itself** rather than of the levels it
uses. 19 trading days of M5 (2026-09-08 → 10-02), every level the brief
published, every sweep of every level.

**Method.** A sweep of level P: price below P trades beyond P+2pts, then CLOSES
back inside within 24 bars. Entry = that reclaiming close. Stop = sweep extreme
+ 8pts. Graded on **closes, not wicks** — a setup "reaches 1R" only if a bar
CLOSES at the target before the stop is touched, which is the difference between
a number and a fill. Run to the end of the trading day.

## H15 — the lower-high confirmation earns its keep

The trader's own refinement: after the reclaim, wait for a **lower high**
(bearish) or **higher low** (bullish) before entering. It costs entry price. Does
it pay?

| | n | ≥1R | ≥2R | ≥3R | stopped | median R |
|---|---|---|---|---|---|---|
| plain reclaim | 1631 | 41% | 25% | 17% | 72% | 0.69 |
| **+ LH/HL confirmation** | **822** | **50%** | **31%** | **20%** | **63%** | **0.98** |

**+9pp on 1R, +6pp on 2R, −9pp on stop-outs, and median R from 0.69 to 0.98 —
for half the setups.** That is the correct trade: fewer, better. **Confirmed, and
it is his instinct that was being tested, not mine.**

## The risk-size effect is ARITHMETIC, not predictive — checked before reporting

By R, tight setups look overwhelming: risk ≤25pts → 72% ≥1R and median R 2.94,
against 33% and 0.65 for risk >70pts. **That result does not survive the obvious
check.** Measured in absolute points instead:

| risk bucket | n | med risk | med MFE pts | reached +50pts | reached +80pts |
|---|---|---|---|---|---|
| ≤25 | 87 | 19 | 60 | 54% | 36% |
| 25–40 | 201 | 32 | 48 | 48% | 36% |
| 40–70 | 222 | 52 | 64 | 59% | 46% |
| >70 | 312 | 102 | 70 | **64%** | **45%** |

**The move is the same size regardless — if anything slightly larger on wide
setups.** A tight stop does not predict a better move; it makes the same move
worth more R.

**That still matters, but the reason is different from the one the R table
implies.** It is not "tight setups work better" — it is **"your R is set almost
entirely by your stop distance, because the move is ~60–70pts either way."** The
response to a wide sweep is therefore to find a tighter entry, not to skip the
level and not to widen the target.

## Level type — this one IS real, it survives the points test

| level | n | med risk | med MFE | +50pts | +80pts | med R |
|---|---|---|---|---|---|---|
| **equal highs/lows** | 73 | 40 | **90** | 63% | **53%** | **2.26** |
| prev-day H/L | 51 | **91** | 79 | 67% | 49% | 1.05 |
| London H/L | 112 | 62 | 81 | 62% | 51% | 1.15 |
| max pain | 35 | 42 | 71 | 60% | 31% | 1.35 |
| Asia H/L | 140 | 46 | 61 | 57% | 36% | 0.88 |
| gamma flip | 53 | 46 | 60 | 57% | 43% | 1.06 |
| **gamma wall** | 107 | 61 | **54** | 53% | 36% | 0.89 |
| options shelf | 107 | 52 | 58 | 50% | 38% | 0.86 |
| NY H/L | 27 | 76 | **43** | 41% | 26% | 0.41 |

**Equal highs/lows wins on both axes** — the largest median move (90pts) at the
second-tightest structure (40pts). That is a genuine edge, not a denominator
artefact. Mechanically unsurprising: equal highs are where resting stops actually
sit.

**Gamma walls are middling as SWEEP levels (54pts median move), which is not a
contradiction of the wall playbook.** The playbook measures whether a wall holds
once price settles a side; this measures the move available from sweeping it.
Different questions, and a wall can be an excellent barrier while being a
mediocre sweep trigger.

**prev-day H/L is the "right level, wrong stop" case** — 79pts of move, but 91pts
of structure, so the R dies. That argues for a tighter entry technique at PDH/PDL
rather than avoiding them.

## Session — NY morning is structurally WIDE

| session | n | med risk | med MFE | +50pts |
|---|---|---|---|---|
| Asia 22–06 | 190 | 48 | 68 | 60% |
| London 06–12 | 241 | 42 | 70 | 60% |
| **NY am 12–16** | 235 | **90** | 65 | 58% |
| NY pm 16–21 | 156 | 50 | 50 | 50% |

**The NY morning move is the same size as everyone else's (65pts). Its structure
is twice as wide (90 vs 42).** That is why NY-am R looked bad in the first cut —
not a worse market, a wider sweep. Same remedy: tighter entry, not avoidance.

## Today as the worked example

2026-10-02. Published `CALL WALL 31,046.7`. **Day high 31,037.1 at 14:27 — the
wall was never touched, missed by 9.6pts.** Then four consecutive lower highs on
the 1m: 31,028.8 → 31,007.5 → 30,957.5 → 30,850.0, and **283.5pts of downside**
to 30,753.6. A 30,984 entry with the stop above the wall is ~71pts of risk →
**3.3R.**

Also exact on the board: the trader's chart C1 and C2 are the published
`Options shelf 1.42bn` at 30,846.7 and `Options shelf 1.27bn + London High
(prev-day)` at 30,797.1.

**The brief's directional call was NEUTRAL (+1) and gave no help.** The *levels*
did all the work — which is the same conclusion as every previous review, now
with a 3.3R example attached.

## What this is NOT

No spread, no slippage, no partials. MFE is the best close before the stop, which
assumes an exit nobody achieves. Levels cluster, so one price move can register
as several setups — the 822 are **not independent**. These numbers rank setups
against each other; they do not predict account return.

## Equal highs/lows — how they actually form (measured 2026-10-02)

The brief's definition, for the record: **4-bar M5 pivots, unmitigated, clustered
within `max(12, ADR×0.03)` = ~14pts, over a 6-day lookback**
(`levels_fuel.swing_points` → `unmitigated` → `cluster`). 93 confirmed pools
(2+ touches) found across 27 days by replaying the detector day by day.

**Touches per pool:** 2 → 57, 3 → 21, 4 → 12, 5 → 3.

**Gap between consecutive touches:**

| | |
|---|---|
| min | **5 min** |
| p25 | 40 min |
| **median** | **85 min** |
| p75 | 7.2 h |
| max | **101 h (4.2 days)** |

**Whole pool, first touch to last:** median **3.2 h**, p90 35.7 h, max 101 h.

**Formation window:**

| span | share |
|---|---|
| within 1 hour | 28% |
| 1–4 hours | 34% |
| 4–12 hours | 6% |
| 12–24 hours | 15% |
| 1–3 days | 15% |
| 3–6 days | 1% |

**So it is both, and the split matters for charting: ~62% form inside 4 hours
(same session), but ~31% take over 12 hours and span days.** A trader marking
only intraday equal highs misses a third of them; one scanning weeks finds
nothing extra, since only 1% exceed 3 days.

### Performance within the type

| | n | ≥1R | ≥2R | med move | med risk | med R |
|---|---|---|---|---|---|---|
| 2 touches | 65 | 58% | 49% | 81pts | 39 | 1.99 |
| 3 touches | 8 | 75% | 75% | 143pts | 45 | 3.55 |
| equal **HIGHS** swept → short | 35 | 54% | — | 63pts | — | 1.84 |
| equal **LOWS** swept → long | 38 | **66%** | — | **95pts** | — | **2.59** |

The 3-touch row is **n=8 — not a finding**, though it points the way the
mechanism would predict. The high/low asymmetry (38 vs 35 observations) is worth
watching but is one month of a rising tape, which is exactly the condition that
would flatter equal lows.

**Nothing proposed.** This is charting guidance, not a model change.

---

## H24 — searching for an overlooked high-probability setup: three candidates, none established

**Asked:** having measured the levels price touches, is there a higher-probability
setup in the data we have never looked at? Three candidates were tested against
the 822 confirmed sweep → lower-high/higher-low setups (`sw_conf.json`, 19 trading
days, close-based grading, stop 8pts beyond the sweep extreme).

### Candidate 1 — the NEAR MISS. **Rejected.**

Every prior analysis required price to *touch* a level. On 2026-10-02 the day high
was set 9.6pts short of the call wall, which no touch-based measure can see. So:
a swing extreme lands inside a band below (above) a level, never trades through it,
and turns. Observable at the turn, therefore not hindsight. `research/wall-studies/06_near_miss.py`.

| band | n | ≥1R | ≥2R | stop | med R | med move | med risk |
|---|---|---|---|---|---|---|---|
| within 10pts | 44 | 48% | 32% | 77% | 0.88 | 29pts | 30pts |
| within 20pts | 91 | 41% | 25% | 85% | 0.72 | 22pts | 31pts |
| within 35pts | 169 | 41% | 24% | 86% | 0.84 | 24pts | 31pts |
| **baseline** swept + LH/HL | 822 | 50% | 31% | 63% | 0.98 | **63pts** | — |

Worse on every measure and the move is less than half the size. The mechanism is
visible in the stop column: with no sweep there is no liquidation extreme to hide
the stop behind, so the stop sits inside noise and 77–86% of them are taken. The
2026-10-02 call wall was a good observation and a bad generalisation. **Recorded so
it is not proposed again.**

### Candidate 2 — CONFLUENCE as an entry filter. **Not established.**

Do two *different kinds* of level stacked on one price reverse better? Families:
`gamma` (walls, flip, shelf, max pain), `pool` (equal highs/lows), `session`
(Asia/London/NY H-L), `day/week` (PDH/PDL/PWH/PWL/PD mid/close).
`research/wall-studies/07_confluence.py`.

Tolerance sensitivity, ≥1R:

| bucket | 5pts | 12pts | 25pts | 40pts |
|---|---|---|---|---|
| gamma + structure | 75% (6 pairs) | 55% (36) | 48% (72) | 48% (87) |
| structure + structure | 65% (7) | 61% (18) | 65% (27) | 64% (24) |
| pool alone | 60% (10) | 63% (5) | 70% (2) | 70% (2) |
| gamma alone | 46% (50) | 44% (37) | 39% (26) | 41% (18) |

`gamma + structure` is the headline that does not survive: 75% at 5pts rests on
**six distinct day/level pairs**, and the rate decays monotonically to 48% as the
band widens — the signature of a bucket absorbing everything, not of an edge.

`structure + structure` looked like the real one — stable 61–65% at every
tolerance. It fails the **same-day control**: on the 6 days that contain it,
61% ≥1R against 54% for every other level on those same days, and per day it beat
the other levels on that same day on only **3 of 5** days carrying ≥4 such
setups. 18 distinct pairs. Suggestive, not evidence.

### Candidate 3 — the Nth sweep of the same level. **Rejected, no signal.**

| attempt | rows | pairs | ≥1R | ≥2R | med R | med move |
|---|---|---|---|---|---|---|
| 1st | 240 | 139 | 53% | 32% | 1.06 | 78pts |
| 2nd | 181 | 113 | 53% | 39% | 1.18 | 66pts |
| 3rd | 147 | 94 | 50% | 27% | 0.98 | 60pts |
| 4th+ | 254 | 74 | 44% | 27% | 0.88 | 58pts |

Flat through three attempts with a mild decay after. On the 19 days holding both,
first 53% vs later 48%. Nothing to trade.

### Candidate 2b — and the gamma-alone gap is **pooled only**. Also not established.

The first write-up of this entry claimed gamma-alone "survives the same-day
control" on 12 of 16 days. **That was wrong** — the per-day loop had a fallback
that counted a day with no comparison set as an underperformance, inflating it.
Corrected, with the control being *other levels on the same day*:

| | rows | pairs | ≥1R | ≥2R | med R | med move | beat its own day |
|---|---|---|---|---|---|---|---|
| gamma alone, 5pt band | 291 | 50 | 46% | 29% | 0.93 | 57pts | **6 of 14 days** |
| other levels, same days | 531 | 89 | 51% | 33% | 1.05 | 69pts | — |
| gamma alone, 12pt band | 209 | 37 | 44% | 24% | 0.86 | 49pts | **4 of 11 days** |
| other levels, same days | 504 | 84 | 51% | 30% | 1.03 | 66pts | — |

So: the **pooled** gap is consistent and points the same way at every tolerance
(5/12/25/40pts: 46/44/39/41% against a 50% all-setups baseline), and the
**magnitude** gap is the larger of the two — the move after a gamma sweep is
~25% smaller, 49–57pts against 66–69pts. But **per day it is a coin flip**:
gamma-alone was the better half of the day on 6 of 14 and 4 of 11 eligible days.
A pooled gap with no per-day consistency is what you get when a few days carry
it, and on this sample it cannot be separated from that.

### Verdict: no overlooked high-probability setup was found.

Three candidates, none established. That is the finding, and it is worth as much
as a positive one would have been: the near miss and the repeat sweep are dead,
confluence does not survive its control, and the gamma-alone weakness is pooled
only.

What the search *did* confirm is that the strongest thing in this dataset is
still the one already on the board — **equal highs/lows**, which tops the ≥1R
ranking at every tolerance (60–70%) and carries the largest median move
(98–113pts). It does so on 2–10 distinct pairs, which is why H23 called it
charting guidance rather than a model change, and nothing here changes that.

The direction worth noting for the playbook, short of a claim: a wall is
measured as a **magnet and a brake** — that is what the 8.2pt retest wick is —
and nothing in this dataset shows it is also a good **sweep-reversal entry
trigger**. Those are two different uses of the same line and the project has
been treating them as one. **No change proposed; this needs more days before it
is worth acting on.**

**Open watch items:** `structure + structure` (3 of 5 days, 18 pairs) and the
gamma-alone magnitude gap. Re-run `07_confluence.py` after another 10–15 trading
days; either becomes real if the same-day control holds up, and both are
currently one month of a rising tape.

---

## H25 — the realistic target is a DISTANCE, not an R multiple, so the exit rule has to change with the stop

**Asked (trader, 2026-10-04):** "my trades may not always hit 1 or 2R because
realistically price may not move in my direction long enough. If my stop is
30pts, 1R may be acceptable; if it is 70pts, maybe only half an R is realistic.
I need a table of probability for each target against varying stop sizes."

Measured on the 822 confirmed sweep → lower-high/higher-low setups, 19 trading
days. `research/wall-studies/09_target_by_stop_size.py` and `10_exit_rules.py`.

### The intuition is right, and the mechanism is the reverse of the obvious one

| stop size | n | pairs | median stop | **median run** | p75 run | P ≥50pts | P ≥100pts |
|---|---|---|---|---|---|---|---|
| ≤25pts | 87 | 51 | 19pts | **60pts** | 137pts | 54% | 33% |
| 26–40 | 201 | 88 | 32pts | **48pts** | 151pts | 48% | 31% |
| 41–55 | 126 | 64 | 46pts | **60pts** | 135pts | 55% | 39% |
| 56–75 | 124 | 82 | 64pts | **65pts** | 156pts | 59% | 39% |
| 76–100 | 117 | 69 | 89pts | **79pts** | 127pts | 64% | 44% |
| >100 | 167 | 94 | 134pts | **70pts** | 118pts | 67% | 37% |

**The run is flat — 48 to 79pts of median favourable close whatever the stop
was.** A wider stop does not buy a longer move; it buys a smaller R multiple for
the same move. P(≥100pts) sits in a 31–44% band across every bucket. So R is a
unit of risk, not a unit of distance, and a fixed "take 1R" rule is six
different bets depending on which setup presented.

The practical conversion: **target in R ≈ 55 / stop in points.**

### Probability of reaching each target

| stop size | 0.5R | 0.75R | 1R | 1.5R | 2R | 3R | med R |
|---|---|---|---|---|---|---|---|
| ≤25pts | 85% | 79% | 72% | 66% | 56% | 49% | 2.94 |
| 26–40 | 76% | 69% | 59% | 50% | 45% | 33% | 1.45 |
| 41–55 | 75% | 61% | 56% | 45% | 39% | 25% | 1.21 |
| 56–75 | 69% | 59% | 52% | 41% | 32% | 14% | 1.05 |
| 76–100 | 67% | 57% | 44% | 21% | 15% | 4% | 0.88 |
| >100 | 56% | 37% | 25% | 9% | 6% | 1% | 0.54 |

Max favourable excursion on CLOSES before the stop was touched. Not an
achievable exit: no spread, slippage, commission or partials anywhere in this.

### Which exit rule wins, per stop size

`10_exit_rules.py` re-derives each setup from the M5 bars so stop MOVEMENT can
be tested, which 09 cannot do. Resting orders fill on the wick; within one bar
the stop is checked BEFORE the target, so a bar that does both books the loss.
Expectancy in R per trade:

| stop size | med stop | best rule | E(R) | runner-up | E(R) |
|---|---|---|---|---|---|
| ≤25pts | 19pts | hard 3R | **+1.41** | 3R, BE@1R | +1.19 |
| 26–40 | 32pts | trail 1R | **+0.59** | 3R, BE@1R | +0.55 |
| 41–55 | 46pts | hard 3R | **+0.39** | hard 2R | +0.33 |
| 56–75 | 64pts | trail 0.5R | **+0.41** | 2R, BE@1R | +0.36 |
| 76–100 | 89pts | 1R, BE@0.5R | **+0.21** | hard 1R | +0.14 |
| >100 | 134pts | hard 0.5R | **+0.14** | 1R, BE@0.5R | +0.12 |

**So the trader's rule is directionally correct but stops short of the real
conclusion.** On a 76–100pt stop, 1.5R and 2R targets are NEGATIVE (−0.05,
−0.08) and only a 1R cap with an early breakeven stays positive. On a >100pt
stop every rule tested is between −0.15 and +0.14 — the answer there is not
"take half an R", it is **do not take the setup**.

### What the breakeven stop trades away (target 2R, BE at 1R)

| stop size | 2R hit, hard | 2R hit, with BE | scratched | full loss, hard | full loss, with BE |
|---|---|---|---|---|---|
| ≤25pts | 62% | 60% | 18% | 32% | **20%** |
| 26–40 | 48% | 39% | 31% | 46% | **25%** |
| 41–55 | 42% | 30% | 28% | 51% | **35%** |
| 56–75 | 36% | 31% | 19% | 46% | **34%** |
| 76–100 | 17% | 16% | 24% | 58% | **38%** |
| >100 | 6% | 6% | 22% | 33% | **29%** |

The breakeven stop is a good trade on **wide** stops and a bad one on
**mid-size** stops. On 76–100pts it costs one 2R winner in seventeen and
removes a fifth of the full losses. On 26–40pts it costs nine 2R winners in a
hundred to remove twenty-one full losses — which still nets positive, but it is
the bucket where it takes the most from the upside, and trailing beats it there
(+0.59 vs +0.55).

### Caveats, and one that reorders nothing but shrinks everything

**Spread and commission are absent and they do not fall equally.** Cost in R is
`spread / stop`, so a 2pt spread is 0.11R on a 19pt stop and 0.015R on a 134pt
stop. Applying it: ≤25pts +1.41 → +1.30, 26–40 +0.59 → +0.53, 41–55 +0.39 →
+0.35, 56–75 +0.41 → +0.38, 76–100 +0.21 → +0.19, >100 +0.14 → +0.12. The
ranking survives; the tight-stop advantage is the most overstated of the six.

**The ≤25pt bucket is the least trustworthy row despite the best numbers.** A
19pt stop only exists when the sweep was tiny, so the bucket selects for quiet
conditions, and 87 rows over 51 pairs is the second-smallest sample here.

**The >100pt rows are the next least trustworthy.** In 09's outcome model 33–66%
of those setups neither hit the target nor the stop before the day ended, against
1–8% in the tight buckets — so their expectancies rest mostly on a mark-out, not
on a resolved trade.

**19 trading days of a rising tape**, 822 rows but 139 distinct day/level pairs.
Every long-biased setup is flattered.

**Proposed:** publish the stop-size → target mapping as desk guidance, and add
the stop size at entry to the brief's management note. **Nothing coded yet —
the trader's call.** The one change with evidence behind it independent of the
tape direction is the negative: a >100pt stop on this setup has no exit rule
that pays, which argues for a position-size or skip rule rather than a target.

---

# Observations appended 2026-10-05 (grading the 2026-10-02 session)

1 gradeable PRE_NY scan (12:47:44Z), `is_trading_day: true`, 0 test artefacts,
275 M5 bars (10-01 22:00Z → 10-02 20:50Z). O 30520.6 / H **31037.1 (14:25Z)** /
L 30520.6 (the opening bar) / C 30809.0, range **516.5 = 1.09x** ADR14 474.8,
net **+288.4** (55.8% close position). Bias **+1 NEUTRAL — no direction call**;
post-scan move **−75.2** (direction −1) on traversal 292.9. Fuel budget **93.7**
vs extension **135.4** → **+41.7, 1.45x over**. Hit rate **0.55** published
(6/11), **0.27** distinct. Scan bar 178 of 275. Pre-scan H **30901.7 (12:35Z)** /
L 30520.6; post-scan H **31037.1 (14:25Z)** / L **30744.2 (15:25Z)** — the
extension was **entirely upside**, and the day then gave back **228.1** from the
high into the close.

**2026-09-24 remains excluded** from the options fields, the direction tally,
the hit-rate series, P-E, P-E(b), H6 and M6 per *D23 CORRECTED*; its fuel error
(+13.6) is kept on the D1 precedent and sits inside `track.py`'s H1 series, so H1
needs no hand correction. `track.py` has no quarantine and still prints 09-24
CORRECT, so the direction counts are carried by hand off its per-scan table, as
the 09-28, 09-29, 09-30 and 10-02 reviews did. **09-25's row stays cited from the
09-28 entry**, not re-derived; no review file back-dated for 09-24 or 09-25. The
09-23 pre-registered D21 test stays void. This version of `track.py` prints no
`actionable: YES/NO` line — it prints *"threshold met, read the evidence before
proposing"* — so the 3-session rule is applied by hand per entry below.

Record, 09-24 excluded: PRE_NY **9 right / 5 wrong / 5 no-call over 19 days**.
All sessions **14 / 9 / 9**. (`track.py` raw: 15 / 9 / 9.)

## D24 (NEW, PROPOSED) — the events renderer is forward-only, so a release minutes before the scan is invisible

NFP, Average Hourly Earnings and the Unemployment Rate printed at
**12:30:00Z**. The scan ran at **12:47:44Z**, 17m44s later. Section 5 of the
brief reads **"No High/Medium US events in the next 24h"**, `event_gate: None`,
`events_24h: []`. Forward-looking that is *correct*, which is why it has never
been caught.

The impulse is unmistakable in the bars:

| M5 bar | O | H | L | C |
|---|---|---|---|---|
| 12:25Z | 30708.2 | 30748.4 | 30706.5 | 30747.2 |
| **12:30Z** | 30748.0 | **30874.0** | 30745.9 | 30872.5 | 
| 12:35Z | 30875.2 | **30901.7** | 30863.5 | 30885.0 |

**+126.0pts in one five-minute bar**, and the pre-scan high 12:35Z. The fuel
section's entire premise — *"ADR14 474.8, **80.3% used** vs ~45% normal by 08:47
ET -> fuel_ratio **1.78 (burning hot)**"*, hence `LOW_FUEL` and a 93.7 budget —
**is that spike**, and the document cannot say so. The news scorer caught none of
it either (H19 below: **0 of 47**, with *"…Jobs Due"* still in the judgement
pile, i.e. a pre-release headline).

**Census — every `is_trading_day` first scan, High/Medium events that fired in
the 6h before the scan, taken from the union of all `events_24h` lists in the
journal (so the source is the pipeline's own data, not an outside feed):**

| day | scan | High items already fired | section 5 showed | bias | graded |
|---|---|---|---|---|---|
| 08-26 | 13:12Z | Core PCE m/m, Prelim GDP q/q (12:30Z) | future only | −4 | **WRONG** |
| 09-11 | 12:47Z | CPI m/m, CPI y/y, Core CPI m/m, Core CPI y/y (12:30Z) | future only | −7 | CORRECT |
| 09-30 | 12:47Z | Core PCE m/m, Final GDP q/q (12:30Z) | future only | −3 | **WRONG** |
| **10-02** | 12:47Z | **NFP, AHE, U-rate (12:30Z)** | *"No High/Medium… next 24h"* | +1 | no-call |

Medium-only pre-scan fires also occurred on 08-27, 09-16, 09-17, 09-24 and
10-01 and are not counted here.

**4 sessions — threshold met. PROPOSED:** render a *"released in the last 6h"*
block in section 5, and never print *"No High/Medium US events in the next 24h"*
on a day one has already fired. **The data is already in the pipeline** — all
three 10-02 items sat in **10-01's own `events_24h`** at `+23.7h`, so this is
free and as reliable as the existing feed. **Expected effect: no score change**
(the `events` component is `add("events", 0, …)` over
`heavyweight_earnings_next_5d` only, per P-C), and the `burning hot` fuel
reading becomes attributable instead of mysterious.

**Explicitly NOT proposed:** any score term. The called split on these days is
**1 right / 2 wrong** against an overall PRE_NY 9/5/5 — n=3 called, which is
the exact situation the standing rule forbids tuning on. Recorded so a fifth
instance can be added rather than re-derived.

## M6 — 17 sessions, and the worst instance in the record: 5 of 5 understated, 3 of 3 "held" verdicts inverted

`settled_read` measures `worst_excursion` only over bars after the **final**
side change. 10-02 is the pathological shape for that: price held above all five
settled levels for the first 2h35 of the post-scan window (post-scan high 14:25Z)
and only then fell through them, so the leg that mattered is excluded **by
construction**.

| level | `review_day` verdict | reported worst | true post-scan excursion through it | ratio |
|---|---|---|---|---|
| 30846.7 shelf | *"stalled at it — **held as resistance** for 255min, worst +17.3"* | +17.3 | **+190.4** | **11.0x — INVERTED** |
| 30790.0 London High | *"**held as support** for 105min, worst −7.0"* | −7.0 | −45.8 | 6.5x — INVERTED |
| 30797.1 London High + shelf | *"**held as support** for 100min, worst −9.4"* | −9.4 | −52.9 | 5.6x — INVERTED |
| 30903.4 PDH | *"broke UP through it — lost by 33.1pts"* | +33.1 | +133.7 | 4.0x |
| 30896.7 shelf | *"broke UP through it — lost by 39.8pts"* | +39.8 | +140.4 | 3.5x |

All three *"held"* verdicts breach `SETTLE_TOL = 25`; 30846.7 breaches it by
**7.6x** and is reported as a success. Previous worst understatement in the
series was **2.0x** (10-01). **17 sessions. Re-proposed for a decision:**
compute `worst_excursion` over the whole post-scan window, or report both
figures. No call changes; today's board would read 3 lost / 3 inverted-held
rather than 3 lost / 3 held.

## P-B(b) — 10th session, worst inflation in the series (2.00x), and the first board with TWO guaranteed double-counts

`merge_tol = max(3.0, 474.8*0.008) = **3.80**` against `TOUCH_TOL = **8.0**`.
Two published pairs sit in the 3.80–8.0 window that is *structurally guaranteed*
to publish as two lines and grade as two touches off one bar, and **both fired**:

- **30903.4 PDH + Asia High / 30896.7 shelf — 6.7pt gap**, both graded touched at
  **bar 178**;
- **30797.1 London High (prev-day) + shelf / 30790.0 London High (today) —
  7.1pt gap**, both graded touched at **bar 206**.

6 touched levels resolve to **3 distinct touch bars (178, 186, 206)**.

| day | published | touched | distinct | pub rate | distinct rate |
|---|---|---|---|---|---|
| 09-18 | 9 | 7 | 7 | 0.78 | 0.78 |
| 09-21 | 7 | 3 | 2 | 0.43 | 0.29 |
| 09-22 | 16 | 9 | 5 | 0.56 | 0.31 |
| 09-23 | 21 | 12 | 7 | 0.57 | 0.33 |
| 09-25 | 14 | 7 | 6 | 0.50 | 0.42 |
| 09-28 | 7 | 4 | 4 | 0.57 | 0.57 |
| 09-29 | 15 | 10 | 7 | 0.67 | 0.47 |
| 09-30 | 17 | 8 | 4 | 0.47 | 0.24 |
| 10-01 | 3 | 2 | 2 | 0.67 | 0.67 |
| **10-02** | **11** | **6** | **3** | **0.55** | **0.27** |

**No tolerance-only touches today** (every `travel_up`/`travel_down` positive),
so the 2.00x is pure clustering — the cleanest demonstration of the mechanism
yet. Proposal unchanged: (a) `merge_tol >= TOUCH_TOL`, (b) always report
distinct-touch-events beside the raw rate.

**And the rate is wrong in the OTHER direction simultaneously.** Four published
rows sat at **−522 (gamma flip), −589 (max pain), −819 (put wall), −1269
(structural put wall)** = 1.1x–2.7x ADR14, on a **94pt** budget — unreachable,
and they dilute the denominator. On the 7 reachable rows the board was
**6/7 = 0.86**. **0.55 is the sum of a 2.00x inflation and a 4-row dilution**,
which is a second reason never to quote it alone.

## P3 / H6 — structural wall: 0 touches on 9 publications, and it has never been within 200pts

Full first-scan census, distance from scan price:

| day | dist | ADR14 | x ADR | budget |
|---|---|---|---|---|
| 08-24 | −609 | 451.1 | 1.35 | 88.7 |
| 08-25 | −703 | 408.7 | 1.72 | 12.0 |
| 09-10 | −672 | 349.3 | 1.92 | 206.2 |
| 09-15 | **−350** | 360.9 | **0.97** | 97.3 |
| 09-21 | −1454 | 389.2 | 3.74 | 18.7 |
| 09-22 | −1469 | 417.1 | 3.52 | 171.5 |
| 09-23 | −1900 | 424.9 | 4.47 | 242.4 |
| 09-24* | −1720 | 420.8 | 4.09 | 0.0 |
| **10-02** | **−1269** | 474.8 | **2.67** | 93.7 |

**0 within 200pts · 0 within `budget*1.75` · 0 touches · 9 publications**
(*09-24's options fields are quarantined, so 8 are usable — the finding does not
depend on it). The nearest it has ever been is **0.97x ADR14**.

**PROPOSED (strengthening P3):** exclude `kind: structural` from the hit-rate
denominator **and move the row out of the table headed *"Level board — mark
these"* into the context footnote** — its own note already reads *"Mark it and
leave it… not an intraday trigger"*, so the table it sits in contradicts its own
text. Expected effect: +0.05 on today's rate, and no call change on any day in
the record.

## H23 — THRESHOLD MET at 3 sessions: the named brake is sliced 4 times in 5, and it is the control P-E(b) lacked

| session | brake | dist | outcome | x ADR |
|---|---|---|---|---|
| 09-30 | 30487.7 upside | +26 | **sliced +167.5** | 0.36 |
| 10-01 | 30586.0 downside | −18 | **sliced 300.5** | 0.65 |
| 10-01 | 30636.0 upside | +32 | capped at +1.3 | 0.00 |
| **10-02** | **30846.7 downside** | **−19** | **sliced 102.5** (post-scan low 30744.2) | **0.22** |
| **10-02** | **30896.7 upside** | **+31** | **sliced 140.4** (post-scan high 31037.1) | **0.30** |

**4 sliced / 1 capped**, slices 0.22x–0.65x ADR. The fuel section asserts, as
fact, *"**DOWNSIDE path: has friction.** Expect a stall at 30846.7 (19pts away)
— take partials into it rather than assuming a clean breakdown"* and the mirror
sentence upside. **PROPOSED: drop the assertion or print the measured base rate
beside it.** Expected effect: removes a specific, actionable instruction with a
1-in-5 hit rate; no score or level change.

**Today kills the 10-01 sub-reading.** That entry floated *"the brake aligned
with the day's dominant leg was sliced 300.5 while the one against it capped at
1.3"*. Today the counter-leg brake was **sliced 102.5**. n=2, 1 for / 1 against
— **dead, not observing.**

**The corollary is the valuable part: H23 is the pre-registered control for
P-E(b).** Shelves selected *after* the fact are the lid 8 of 9 times inside
22pts; shelves **named in advance by the brief itself** are sliced 4 times in 5.
That is the same shelf population under two sampling rules, and it quantifies
the undeclared selection the 10-01 entry flagged. **P-E(b) must not be used to
ship a "the nearest shelf caps" claim.** Its distance selection remains
non-monotonic and the caveat stays live.

## H18 / P1 — 11th instance; on the register's own convention the age gate now manufactures a SECOND consecutive wrong call

Score **+1**; `bias_engine.py` labels `MILDLY BULLISH if total >= 3`.
Components: macro **−6** · structure +5 · rates +3 · breadth −3 · gamma +2.

| row | pts | its own words |
|---|---|---|
| macro DFII10 2.93% | **−3** | observation **2026-09-30**, *"FRED has not published since 2026-09-30 (2 business days ago)"* — **largest single row in the document** |
| macro HY OAS 3.12% | −2 | *"+39bp over 5 days"* — **no observation date rendered at all**, 2nd consecutive session |
| macro DGS10 | −1 | *"moved 3bp up (2026-09-29 to 2026-09-30)"* — stale AND duplicated |
| rates US10y | **+3** | *"5.159 (−1.49%) — yields down, BULLISH tech"* — live, same instrument, **opposite sign to the stale DGS10 row** |

**Zeroing DFII10 alone → +4 → `MILDLY BULLISH` → a long call.** Post-scan move
**−75.2 → WRONG.** On **day net (+288.4)** the same call is **right**.

**Accuracy ledger on the post-scan convention this register and `track.py` use:
09-30 removes one WRONG · 10-01 creates one · 10-02 creates one → 1 removed / 2
created, net NEGATIVE.** On day-net it would read 10-01 right and 10-02 right.
**The verdict is convention-dependent, which is itself the reason not to
re-open it: the retraction made on 10-01 stands and the duplication and stale
rows should be fixed on CORRECTNESS grounds only.** Coupling to D22(a)
unchanged.

**Age-gate blocker unchanged and now 2 sessions old.** `HY OAS` renders **no
observation date** again (−2, second-largest macro row). Until that is resolved
the gate silently exempts a row it cannot measure.

**DFII10 textual sub-defect, 3rd consecutive instance, and the first with
damage.** *"this is last week's reading, not today's"* renders unconditionally;
the observation is **2026-09-30, Wednesday of the current week** (Mon 09-28 /
Tue 09-29 / Wed 09-30 / Thu 10-01 / **Fri 10-02**). Wrong on 09-30, 10-01 and
today — and today, unlike the first two, the row scored **−3** and was the sole
margin between no-call and a call.

**DGS10 duplication, 4th sign configuration:** stale **−1** against live **+3**,
opposite signs, live the larger. Code-certain in all four.

## P-G — instance #12, and both rows were wrong-sided on levels that then worked

Session-extreme prose is chosen by level kind, not by which side price is on:

- **30797.1 London High (prev-day) + shelf**, **68pts BELOW** the scan price:
  *"High of the London session — the next session usually **runs the stops above
  it**"*. It acted as **support** for 100min.
- **30790.0 London High (today)**, **76pts BELOW**: identical sentence. Acted as
  **support** for 105min.

The adjacent PWH row got it right in the same table (*"we're trading ABOVE the
whole of last week, so it has flipped to SUPPORT"*), which is the sidedness
logic the session-extreme rows lack. P-G → **12**.

## D23 — 5th clean offset; the "two offsets" instance CONTRADICTS the 10-01 framing

Offset **−3.3** (NDX reference 30868.8 rolled forward by the NQ move +367.2,
against CFD 30865.5, basis `nq_implied`). Ordinary basis.

**Again an `nq_implied` roll-path day, so the proposed cross-check reports
nothing and is NOT validated** — comparing the brief's reference against
futures-minus-premium is circular when the reference *is* the futures delta. It
still needs re-specifying against an independently measured NQ-minus-premium
level before it can replace D6. Per the 09-29, 09-30 and 10-01 entries, and
unchanged.

**Two offsets for one grid — 4th consecutive instance by magnitude, but today
the gap is explained.** Board **−3.3** vs section 7 **+168.7** = **172.0 apart**
(09-29: 150.1 · 09-30: 58.0 · 10-01: 158.0). Section 7 is labelled *"matched to
feed time 2026-10-02 11:59Z"*, and **the CFD moved from 30677.5 at 11:59Z to
30865.5 at the 12:47Z scan — +188.0pts, which accounts for ~92% of the 172.0
gap.** On this instance the two offsets differ **by design and correctly**; the
10-01 entry's framing (*"a 158pt latent error that becomes live the first time
H12/H13 promote section 7"*) **does not hold here.**

**Recommendation before shipping "derive both grids from one conversion":
measure the 11:59Z→scan CFD move on 09-29, 09-30 and 10-01 and subtract it.**
If those gaps are also ≈ the intervening move, the defect is cosmetic — two
numbers shown with no stated reconciliation — and the right fix is to **print
the feed-time delta**, not to re-derive the grid. All four instances stay
damage-free: section 7 is research-only and had **no volume** (*"No volume has
traded yet today"*). This correction is recorded against the 10-01 proposal,
which should not ship on its current evidence.

## P-E — no instance; the call wall was missed by 9.6pts and the prose was right

CALL WALL **31046.7**: *"Heaviest ceiling this week (42k contracts) — desks must
SELL as price rises into it, so rallies stall. Take profit into it… the
strongest ceiling on the board."* The session high was **31037.1 at 14:25Z —
9.6pts short** — and the day then lost **228.1** into the close. `review_day`
grades it **"never reached"**, identically to the structural put wall 1269pts
away.

Census **unchanged at 4 capped / 6 sliced**: a 9.6pt near miss is not a touch at
`TOUCH_TOL = 8.0`. Worth noting that 9.6 sits **inside the existing cap mode
(3.6–11.9)**, so counting it would not disturb the empty 12–103 band either.
**Nothing proposed.** The *trade* generalisation of the near miss is already
**rejected** under H24 Candidate 1 (44 instances, worse than baseline on every
measure) and must not be re-proposed; the open question is only whether the
grader should report a near-miss distance so that "missed by 9.6" and "missed by
1269" stop reading the same. **n=1 on that, logged, not proposed.**

## H1 — n=24, and the multiplier branch should be closed

10-02: budget **93.7**, extension **135.4**, error **+41.7**. `track.py` per-day
mean **+25.4** (n=24); **+1.74** excluding the 09-21 outlier (was −0.08 at n=22).
MAE **86.0** against a mean budget of **103.1** — the typical error is **83% of
the typical budget** (85% at 09-29, 79% at 09-30).

Last five: **+113.9, −112.2, −75.2, +153.7, +41.7.**

**Fourth consecutive entry recommending the multiplier branch be closed
SETTLED-NEGATIVE.** Excluding the single outlier the estimator is unbiased at
n=23; a multiplier corrects bias and there is none left to correct.

**The qualitative text was right today.** *"The range is close to done. Expect
price to keep MOVING but mostly inside the extremes… favour fades over chasing
breaks"* — the range grew 135.4 (1.45x the budget, the smallest error in the
last five) and the fade off the 14:25Z high took 228.1. Note the caveat under
D24: the budget was small **because** of an NFP spike the model cannot see.

## H22 — n=3, and the GEX reading does not order the realised range

| day | week net GEX $bn/1% | label printed | realised range / ADR14 |
|---|---|---|---|
| 09-30 | **0.036** | *"pinning likely"* | 0.84x |
| 10-01 | 5.58 | *"pinning likely"* | **1.33x** |
| **10-02** | **9.526** | *"pinning likely"* | 1.09x |

A **265x** spread in the input, the identical output label, and **no ordering**
in the outcome — the largest reading produced the middle range. n=3 and the
session-context confound applies (10-02's own high was pre-scan-adjacent).
**Logged, no claim, nothing proposed** — three points cannot separate "the label
is non-discriminating" from "the input does not predict range".

## No instance today

- **H4** — GAMMA FLIP 30343.9 was **522pts away** and never reached; no flip
  read. The `gamma +2` *"above flip… dips supported"* row was correct on the day
  net and had no level to be tested at.
- **H20** — no scheduled event *ahead* of the scan (`events_24h: []`). The
  relevant event had already fired; see **D24**, which is a different defect.
- **H6 / P3** — one `structural` level published and untouched; counted in the
  P3 census above.
- **P-C / `events`** — **no `events` row at all** again (24 components, none
  `events`). `add("events", 0, …)` over `heavyweight_earnings_next_5d` only, and
  there were none.
- **P-F** — price inside the prior-day range at the scan (37.9 below PDH 30903.4,
  580.0 above PDL 30285.5): inside-range control, error **+41.7**. Control
  becomes **20 days**.
- **The structure row's tolerance band** — `price_at_scan − PD mid = +271.0`, far
  outside the 30pt window. Stays **2 of 3**.
- **D7 — a COUNTER-instance, and it argues for the narrow fix.** Budget 93.7 →
  `keep()` cap **164.0**, which functioned: the 6 demoted footnote levels
  (30690 / 30637 / 30623 / 30594 / 30548 / 30527, i.e. −176 to −339) were **all
  untouched** — the post-scan low was 30744.2. Forward-only breach of the ±164.0
  cap: **+7.6 above** (the session high at +171.6), **0 below**. So 10-01's
  degenerate zero-budget case is the real defect and the **narrow fix (floor the
  cap at a fraction of ADR) is supported; the broad fix (exempt all
  session-extreme and PD/PW levels) would have added 6 rows that went
  nowhere** and made today's dilution worse. Recorded against the 10-01
  re-proposal.
- **D21 — 10th firing, widest band in the record.** `gamma −2` *"price sits in
  the top 20% of the wall band (30046.7–31046.7)"*: band **1000pts** (previous
  widest 800), so *"top 20%"* is a **200pt** trigger window = 42% of ADR14 —
  the width defect at its most extreme. Distance to the call wall **+181**, i.e.
  the post-hoc *"beyond 50pts"* bucket, which predicts DOWN; post-scan direction
  was **−1**, so that bucket is now **3 down / 0 up** while *"within 50pts"*
  stays at **5 up / 1 down** (claim wrong 5 of 6). **STILL NOT PROPOSED** — the cut was found after looking at outcomes,
  and day-net (+288.4) disagrees with post-scan on this very instance.
- **Breadth** — *"index up while mega-caps are down — narrow, tail-carried
  rally; **these fade into the close**"* (−2). The day **did** fade 228.1 from
  its 14:25Z high, and closed **+288.4 up**. The row was right about the shape
  and wrong as a direction input. n=1, logged.
- **Post-scan direction vs day-net direction disagreed** (−75.2 vs +288.4) —
  **second consecutive session** (10-01: −74.7 vs +64.3). Below threshold, but
  it now affects the verdict on H18/P1 and D21 above, so it is flagged: the
  register grades direction post-scan while `bias_label` reads as a day call.
  **n=2, nothing proposed.**

## H19 — coverage 0.0%, the lowest possible, on NFP day

| scan | counted | uncounted | raw | score | coverage |
|---|---|---|---|---|---|
| 2026-10-02 12:47 | **0** | 47 | 0.00 | 0 | **0.0%** of 47 relevant |

138 headlines → 47 relevant → **0 auto-scored**. Previous low 1.8% (10-01), and
before that 3.8% (09-30). The judgement pile contained *"Dow Jones Futures Rise,
Oil Prices Tumble With Tesla, **Jobs Due**"* — a **pre-release** headline on a
day the release had already happened 17 minutes earlier. Status **OBSERVING**;
the weight does not move without the hand-score test. **No D18 instance** — no
headline matched any pattern, so first-match-wins could not fire.

## Max pain — 5th distance miss, and the largest yet

**30276.7 at −589pts = 1.24x ADR14**, never reached. Distance misses now
**246, 340, 103, 175, 589**; evidence days 8, of which 5 are distance misses and
1 is confounded (10-01, 1.8pts from the flip). Full first-scan census: published
on **20 of 25 days**, within 200pts on **7**. The recommendation to tighten the
threshold to *"3 days on which max pain is within reach"* stands and remains
ungradeable until M6 is decided.

## Session-context field — 6th session, and today the stale level is 12 MINUTES old

Already PROPOSED on 09-29 (`tested_today` per `prediction.levels`; grade against
the whole session). Previous instances: 09-17, 09-28, 09-29, 09-30, 10-01 — all
of them levels tested *hours* before the brief. Today's is the degenerate
version:

- **30896.7 Options shelf**, board row *"expect price to stall. Good place to
  take partials rather than **push through**"*, and section 3 *"**UPSIDE path:
  has friction.** Expect a stall at 30896.7 (31pts away)"*. Price printed
  **30901.7 at 12:35Z — 5.0pts above it, 12 minutes before the scan.**
- **30903.4 PDH + Asia High**, *"+38 … the biggest pile of stops above us.
  Sweep it, wait for a lower high, then CISD = short"*. Price had been within
  **1.7pts** of it at the same 12:35Z bar.

Both under the banner *"**New trading day.** … everything below is fresh"*. The
whole table is converted from a scan price that a **+126pt five-minute NFP bar**
had just moved (see **D24**), and nothing in the document says a level was
touched on that bar. **6 sessions. Proposal unchanged.**

## H10 — the `+3` branch failed at the SMALLEST distance on record, which inverts its proposed fix

`structure +3`: *"price is ABOVE the entire prior-week range (29623.5–30820.3) —
weekly draw has flipped bullish; **PWH 30820.3 is now support, not
resistance**"*. Distance above PWH at the scan: **+45.2 — the smallest firing in
the series.**

| day | distance above PWH | post-scan direction |
|---|---|---|
| 09-21 | +259 | ✓ |
| 09-22 | +788 | ✓ |
| 09-23 | +979 | ✗ |
| 09-24 | +490 | quarantined, ungraded |
| **10-02** | **+45.2** | **✗** |

`+3` branch now **2-for-4** graded. The row's own claim was falsified by the
close: price **fell 76.1 through PWH to 30744.2 with no stall** and **closed
30809.0, i.e. 11.3 BELOW PWH — back inside the prior-week range**. The brief's
*"Sweep it and buy"* instruction on that row lost.

**This cuts against the decay fix H10 itself floated.** The hypothesis was that
the branch fails because *"a reclaim three sessions and 979pts old scores
exactly like one made this morning"* — i.e. failure at **large** distance.
Today's failure is at **+45**, the nearest firing on record, with the reclaim
fresh. **A distance decay would not have helped here. No decay proposed; the
falsification test (the next `+3` firing at >700pts above PWH) is unchanged,
and a second small-distance failure would retire the decay idea outright.**
On day-net (+288.4) this instance reads ✓ — see the post-scan/day-net note
above, which is now load-bearing on three entries.

## Journal hygiene

No fabricated or backfilled entries; no `prediction` block touched. 09-24
quarantined as directed; 09-25 cited from the 09-28 entry, not re-derived; no
review file back-dated for 09-24 or 09-25. 2026-10-05's scan exists
(`is_trading_day: true`, bias +9 BULLISH) and is correctly **held back** by
`track.py` (179 bars) — it enters only the publication censuses above, where its
scan-time values are valid and its outcome is irrelevant.

**Fifth consecutive review to carry the 09-24 exclusion by hand.** The 09-29
entry's proposed `quarantine` field in the journal schema, read by `track.py`
and `review_day.py`, is **reaffirmed** — five hand corrections is five chances
for the correction to be dropped silently.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01M7sro1DKMp5T7EBDusm6pM

# Observations appended 2026-10-06 (grading the 2026-10-05 session)

1 gradeable PRE_NY scan (12:47:11Z), `is_trading_day: true`, 0 test artefacts,
276 M5 bars (10-04 22:00Z → 10-05 20:55Z). O 30856.4 / H **31137.3 (19:15Z)** /
L 30726.9 (09:40Z, pre-scan) / C 31110.3, range **410.4 = 0.86x** ADR14 476.9,
net **+253.9** (**93.4%** close position — eight consecutive rising hourly
closes). Bias **+9 BULLISH**; post-scan move **+369.8** (direction +1) on
traversal 400.7 → **CORRECT**. Fuel budget **216.2** vs extension **149.7** →
**−66.5, 0.69x under**. Hit rate **0.56** published (10/18), **0.39** distinct
(7 bars). Scan bar 178 of 276. Pre-scan H **30987.6 (01:40Z)** / L 30726.9;
post-scan H 31137.3 / L **30736.6 (12:50Z)** — the extension was **entirely
upside**, and price traveled **+386.5 above the scan price** on a 216.2 budget.

**2026-09-24 remains excluded** from the options fields, the direction call, the
hit-rate series, P-E, P-E(b), H6 and M6 per *D23 CORRECTED*; its fuel error
(+13.6) is kept on the D1 precedent and sits inside `track.py`'s H1 series, so
H1 needs no hand correction. `track.py` has no quarantine and still prints 09-24
CORRECT, so the direction counts are carried by hand off its per-scan table, as
the 09-28, 09-29, 09-30, 10-02 and 10-05 reviews did. **09-25's row stays cited
from the 09-28 entry.** No review file back-dated for 09-24 or 09-25. The 09-23
pre-registered D21 test stays void. `track.py` prints *"threshold met, read the
evidence before proposing"*, not `actionable: YES/NO`, so the 3-session rule is
applied by hand per entry.

Record, 09-24 excluded: PRE_NY **10 right / 5 wrong / 5 no-call over 20 days**.
All sessions **15 / 9 / 9**. (`track.py` raw: 16 / 9 / 9.)

## The structure row's tolerance band — THRESHOLD MET, 3 of 3, and PROPOSED

The 09-30 entry pre-registered the test: *"a PRE_NY scan inside 30pts of PD mid,
graded on whether price holds the scored side through the NY session."* Today is
that scan.

`structure −1 "price below PD mid 30778.8"`. `price_at_scan − PD mid` =
**−28.0**. Price **reclaimed PD mid at 12:55Z — 8 minutes after the scan** — and
held above it for **455 of the 490 post-scan minutes** (`settled_from 13:20`,
worst excursion −1.5 reported, −22.7 true), closing **+331.5 above**.

| day | price − PD mid | row | what price did | row right? |
|---|---|---|---|---|
| 09-16 | +27.9 | +1 | PD mid *"lost, worst 50.8–94.6pts"* | ✗ |
| 09-29 | +11.0 | +1 | below PD mid for 6.75 of the next 8h | ✗ |
| **10-05** | **−28.0** | **−1** | **above PD mid for 455 of 490min, closed +331.5 above** | ✗ |

**3 of 3 wrong about the side. PROPOSED:** score the PD-mid structure row **0**
when `|price_at_scan − PD mid| < 30` (equivalently `0.06 × ADR14`, 28.6 today —
either form passes all three). **Expected effect: no label change and no
direction-call change on any day in the record.** 09-16 +4→+3 stays MILDLY
BULLISH (WRONG either way); 09-29 +6→+5 stays MILDLY BULLISH (CORRECT either
way); 10-05 +9→+10 stays BULLISH (CORRECT either way). The row is a coin flip
inside its own measurement error, and this is the first fix on the register that
is pre-registered, threshold-met and provably call-neutral.

## The direction call and the strategy block pointed opposite ways, and direction won

`+9 BULLISH` (gamma +4 · vol +3 · breadth +3 · macro +2 · structure −2 ·
news −1) and, in the same document:

- **STRATEGY 1** — *"Positive gamma above the flip: dealers fade extensions, so
  sweeps genuinely fail… **This is your fade day**"*;
- **`expiry_shape: SPIKE_THEN_REVERT`** — *"Expect a sharp move that then
  mean-reverts. **Fade the extremes**… don't hold for continuation"*;
- **fuel MODERATE** — *"Continuation is fine to the nearest pool; **don't plan
  on a third leg**"*.

The day closed **93.4% up its range**, 27.0pts off the high, after eight
consecutive rising hourly closes, and the only concrete setup named — *"Sweep
[PDH 31037.1], wait for a lower high on the 1m, then CISD = short"* — **lost**:
price held above the PDH for **220min** with a maximum give-back of **35.3** and
closed **+73.2 above**.

**Two separate things recorded here, neither proposed.**

1. **`SPIKE_THEN_REVERT` has never been graded and this is n=2.** Full census of
   the field over all `is_trading_day` first scans: it has fired on **09-30 and
   10-05 only** (every other scan is `COHERENT_LONG`, `COHERENT_SHORT` or
   `FRONT_FLAT_BACK_LONG`). 10-05 is the clean counter-instance — the
   mean-reversion never came. **n=2, below threshold. The test:** the next
   `SPIKE_THEN_REVERT` day, graded on close position within the day's range
   (>80% or <20% falsifies it) rather than on direction.
2. **The registered "two blocks give opposite instructions" entry needs a second
   cell.** That entry is specified on `LOW_FUEL`/`EXHAUSTED` **and below the
   flip** (3 of 41 scans, 2-1 to gamma). Today is `MODERATE` and **above** the
   flip, and the conflict is sharper: the *bias* block and the *strategy* block
   disagree, not the fuel and gamma blocks. **The fade instruction is not gated
   on the sign of the bias score at all** — a +9 long call and "this is your fade
   day" are structurally free to co-occur. n=1 in this cell; recorded so a second
   instance can be added rather than re-derived.

## Session-context field — 7th session, and by far the largest instance

Already PROPOSED on 09-29 (`tested_today` per `prediction.levels`; grade against
the whole session). Previous instances touched one or two rows. Today, with
pre-scan H **30987.6** / L **30726.9**, **8 of the 18 published rows had already
been traded through in the same session**, under the banner *"**New trading
day.** … everything below is fresh"*:

| row | pre-scan touches | pre-scan bars with high above it | last |
|---|---|---|---|
| 30987.6 Asia High (today), published **+237 _(stretch)_** | 4 | 0 (it *is* the pre-scan high) | 01:45Z |
| 30908.1 shelf 0.37bn | 23 | **52** | 02:55Z |
| 30865.7 London High (today) | 11 | **72** | 08:15Z |
| **30858.1 CALL WALL ●●●●●** | **16** | **73** | **08:25Z** |
| 30809.0 PD close + shelf | 42 | 126 | 12:05Z |
| 30790.0 London High (prev-day) | 45 | 150 | 12:15Z |
| 30778.8 PD mid | 33 | 156 | 12:20Z |
| 30770.2 Asia Low (today) | 32 | 159 | 12:45Z |

**The strongest ceiling on the board had already been exceeded for 73 of 178
pre-scan bars** and is published at +107 as an untested lid. **6 of 18 rows (not
counting the Asia high/low, which are session extremes by construction) carry
behavioural prose that today's own price action had already answered.**
Proposal unchanged. **New argument for it: it also cleans P-E's denominator** —
see below.

## P-E — instance 11, and the first one we can show is pre-scan-contaminated

CALL WALL **30858.1** (*"Heaviest ceiling this week (31k contracts) — desks must
SELL as price rises into it, so rallies stall. Take profit into it… the
strongest ceiling on the board"*). Price **crossed it inside the single 13:30Z
M5 bar (O 30825.6 → H 30925.4)**, together with London High 30865.7 and the
0.37bn shelf 30908.1 — **three "expect a stall" claims falsified in five
minutes** — ran **+279.2** and closed **+252.2 above**.

Census **4 capped / 7 sliced**. Slice mode now
**103 / 117.5 / 154 / 185 / 205 / 279.2 / 573**; cap mode still 3.6–11.9. **The
12–103 band remains empty at n=11.**

**The contamination, which is new and applies retrospectively.** This wall was
not a fresh test: price was above it in **73 of 178 pre-scan bars**, last at
08:25Z. The board's unconditional *"rallies stall"* was asserted about a level
the session had already broken. The brief's own conditional was the correct
branch — *"A held close above flips that selling to buying and it becomes a
launchpad"* — and that is exactly what happened; it is printed as the exception.
**P-E's 11 instances have never been checked for pre-scan breach**, and it is
checkable from the bars for every one of them. **Nothing proposed beyond the
session-context field already on the table**, which would record it as a field;
but *P-E's bimodality should not be interpreted further until each instance is
labelled fresh / already-broken.* That is a sampling question, not a tuning one,
and it may be the mechanism behind the empty middle.

## D7-shaped, contract count vs dollar gamma — n=2, and 09-23's "permanently n=1" is wrong

Session high **31137.3** and close **31110.3** sit **+29.2 / +2.2** above
**31108.1**, which appears **only** in the research-only *"Other gamma
concentrations"* table: **0.45bn force but 34,453 contracts — the largest
contract count on the page** — with the note *"dealers are LONG gamma here… so
they damp moves: expect a stall — rallies lose momentum into it"*. **That note
was the most accurate forecast in the document.** The headline force-ranked CALL
WALL (1.34bn, 31k contracts) was **279.2 below the high**.

- 09-23: high stopped **14.7** above a 0.52bn / 25,732-contract secondary strike;
  headline wall 264.7 below the high.
- **10-05: high stopped 29.2 above a 0.45bn / 34,453-contract secondary strike;
  headline wall 279.2 below the high.**

**n=2.** And **31108.1 was +357 from the scan, inside `keep()`'s cap of
`216.2 × 1.75 = 378.4`** — it was not excluded by the range filter, it is simply
not board-eligible.

**Correction to the 09-23 entry.** It recorded this as *"n=1 and, as things
stand, permanently n=1: the secondary gamma table is not persisted in the journal
JSON"*. The **`.md` is in the journal** and the table is in it, so a **hand
census is possible for every day in the record** — it is automation that is
blocked, not measurement. Nothing proposed here; this is the strongest evidence
yet for **P5** (persist and grade the table), which already has a sequencing
caveat to land with or after P3.

## H23 — 6th instance; 5 sliced / 1 capped, and the largest slice in the series

| session | brake | dist | outcome | x ADR |
|---|---|---|---|---|
| 09-30 | 30487.7 upside | +26 | sliced +167.5 | 0.36 |
| 10-01 | 30586.0 downside | −18 | sliced 300.5 | 0.65 |
| 10-01 | 30636.0 upside | +32 | capped at +1.3 | 0.00 |
| 10-02 | 30846.7 downside | −19 | sliced 102.5 | 0.22 |
| 10-02 | 30896.7 upside | +31 | sliced 140.4 | 0.30 |
| **10-05** | **30808.1 upside** | **+57** | **sliced +328.3** | **0.69** |

*"**UPSIDE path: has friction.** Expect a stall at 30808.1 (57pts away) — take
partials into it rather than assuming a clean breakout."* Price closed **+301.3
above it**. The mirror sentence — *"**DOWNSIDE path: clear.** Every options shelf
from here to 30458.1 is negative gamma — nothing structural to slow a
breakdown… If it goes, it has room. Do not fade it"* — was never tested (post-scan
low 30736.6, 14.4 below the scan).

**Variation worth recording: today the named brake WAS on the board** (30809.0,
**0.9pts** away), so H23's original *"a level that is on no table in the
document"* complaint does not hold on this instance. The accuracy finding is
unaffected. **Already-PROPOSED fix unchanged** (drop the assertion or print the
measured base rate beside it), now at **1-in-6**.

## M6 — session 18, 3 of 6 "held" verdicts inverted, plus a 4-row wording inversion

| level | verdict | reported | true, first touch → close | ratio |
|---|---|---|---|---|
| 31037.1 | *"held as **support** 220min, worst −3.8"* | −3.8 | **−35.3** | **9.29x — breaches `SETTLE_TOL`** |
| 30987.6 | *"held as **support** 280min, worst −20.0"* | −20.0 | **−104.7** | **5.23x — breaches** |
| 30770.2 | *"held as **support** 475min, worst −14.1"* | −14.1 | **−33.6** | **2.38x — breaches** |
| 30778.8 | *"held as support, worst −1.5"* | −1.5 | −22.7 | 15.13x (survives tol) |
| 30790.0 | *"held as support, worst −12.7"* | −12.7 | −19.7 | 1.55x (survives) |
| 30908.1 / 30865.7 / 30858.1 / 30809.0 | *"lost"* | exact | exact | 1.00x |

**New sub-shape: the four "lost" rows print the wrong DIRECTION.** Each reads
*"broke **DOWN** through it — lost by Npts"* with `settled_side: above`, on a day
price closed **+202.2 / +245.9 / +252.2 / +301.3 ABOVE** them. The string is
generated as `broke {'DOWN' if settled_side == 'above' else 'UP'}`, which is
correct for a level that loses *downward* after settling above — but when the
breach is the pre-settlement leg and the day ends far above, it reports the
opposite of what happened. **Read cold, `review_day` says today's call wall
failed downward by 46.5. It failed upward by 279.2.** Previous worst
understatement 11.0x (10-02); today's worst is 15.13x but benign, and the worst
*inverting* one is 9.29x. **18 sessions. Re-proposed for a decision:** compute
`worst_excursion` over the whole post-touch window, or report both figures, and
derive the DOWN/UP word from the side the breach was on rather than from
`settled_side`.

## D18 — 6th trading day, 12th headline instance, and a sub-shape first-match-wins cannot explain

Reproduced from `news_scorer.py` on 10-05's own headlines:

```
'Traders slash bets on October Fed rate hike'                      rule=hawkish dir=-1 conf=HIGH flags=[] weighted=-1.8
'Asian shares are higher as easing worries over inflation reduce
 odds for a rate hike'                                             rule=hawkish dir=-1 conf=HIGH flags=[] weighted=-1.8
'S&P 500, Nasdaq, Dow End Week Higher As Weak Jobs Report Cools
 Rate Hike Bets'                                                   rule=hawkish dir=-1 conf=HIGH flags=[] weighted=-1.8
```

Component reported *"7 auto-scored (3 bull / 4 bear) -> MILDLY BEARISH"*, worth
**−1**, raw −1.74. Day count **6** (08-24, 09-11, 09-17, 09-18, 09-22, 10-05);
headline instances **12**.

**The new part.** *"Traders slash bets on October Fed rate hike"* contains **no
market-direction word**, so the documented *first-match-wins* mechanism cannot
produce it. The `hawkish` regex (`news_scorer.py:71`,
`\b(hawkish|rate hike|raise rates|tighten|…)\b`) matches the **noun phrase**
"rate hike" with **no reading of the verb acting on it** — *slash bets on*,
*cools … bets*, *reduce odds for* all vote −1 at HIGH confidence with empty
flags. This is a **missing-negation / missing-attenuation** defect, distinct from
both D18's ordering defect and D9's subject defect, and the candidate fix D18
proposes (*evaluate all matching rules*) **would not fix it** — only one rule
matches. Any eventual fix needs an attenuator list
(`slash|cool|reduce|ease|trim|pare|fade … bets/odds`) or a demotion to
NEEDS_JUDGEMENT when a rates-regime keyword is governed by one.

**Damage today: conviction only.** Correcting all three leaves BULLISH and the
call CORRECT (+9 → ~+11/+12). **Status unchanged: FILED, NOT PROPOSED** — it is a
scoring input and **H19's hand-score test is still unrun**, so the baseline must
not move. Recorded so the sub-shape is in the spec when it is fixed.

## H19 — coverage 12.7%, the best in the recent series

| scan | counted | uncounted | raw | score | coverage |
|---|---|---|---|---|---|
| 2026-10-05 12:47 | **7** | 48 | −1.74 | −1 | **12.7%** of 55 relevant |

136 headlines → 55 relevant → 7 auto-scored. Series: 3.8% (09-30), 1.8%
(10-01), 0.0% (10-02), **12.7%** (10-05). The judgement pile contained
*"**Nasdaq 100 Tests 52-Week Highs Above 31,100** on Semiconductor Strength"*,
*"Nvidia Stock Chases Record…"* and *"Nvidia Gets Another AI Demand Signal As
Foxconn Sales Hit Record High"* (the last tagged `risk_on` → NEEDS_JUDGEMENT,
D18's documented asymmetry) — i.e. the bullish semiconductor theme that carried
the day was **sampled and then not counted**, while three mis-signed hawkish
votes were. Status **OBSERVING**; weight does not move without the hand-score
test.

## H1 — n=25, and the multiplier branch should be closed, 5th consecutive entry

10-05: budget **216.2**, extension **149.7**, error **−66.5**. `track.py`
per-day mean **+21.7** (n=25); **−1.08** excluding the 09-21 outlier (n=24, was
+1.74 at n=23). MAE **85.2** against mean budget **107.6** — the typical error
is **79% of the typical budget**.

Last five: **−75.2, +153.7, +41.7, −66.5** (and +113.9 before them). Excluding
one outlier the estimator is **unbiased at n=24 and the mean has now crossed
zero**; a multiplier corrects a bias that does not exist.

**The qualitative text was wrong today, in the direction that matters.** *"The
range has room but not unlimited room. Continuation is fine to the nearest pool;
**don't plan on a third leg**"* — price traveled **+386.5 above the scan**
through **nine** published levels (every row between +19.4 and +286.3).
The budget itself was fine (0.69x used); it
was the prose gloss that mis-stated it. Cross-reference the H1 sub-observation
*"the budget's correct reading is not reaching the prose"* (09-16).

## D23 — 6th clean offset, and the 10-02 "it's just the intervening move" reading FAILS on 3 of 5 days

Offset **+8.1** (NDX reference 30742.7 rolled forward by the NQ move −65.2,
against CFD 30750.8, basis `nq_implied`, greeks `repriced_bs_at_current_spot`).
Ordinary basis. **Again an `nq_implied` roll-path day, so the proposed
cross-check reports nothing and is NOT validated** — unchanged from 09-29,
09-30, 10-01 and 10-02.

**The measurement the 10-02 entry asked for, done.** Gap = §7 offset − board
offset, against the CFD move from §7's 11:59Z feed time to the scan (11:55Z M5
bar **open** as the proxy; the register's own 10-02 figure of +188.0 corresponds
to +179.3 here, so the proxy is good to ~10pts):

| day | board | §7 | gap | CFD move 11:59Z→scan | residual |
|---|---|---|---|---|---|
| 09-29 | +18.2 | +168.3 | +150.1 | −40.4 | **+190.5** |
| 09-30 | +37.7 | −20.3 | −58.0 | +143.3 | **−201.3** |
| 10-01 | +36.0 | +194.0 | +158.0 | −45.8 | **+203.8** |
| 10-02 | −3.3 | +168.7 | +172.0 | +179.3 | −7.3 |
| **10-05** | **+8.1** | **−13.5** | **−21.6** | **−24.5** | **+2.9** |

**The intervening move explains the gap on 2 of 5 days — 10-02 (the day the
10-02 entry generalised from) and today. On the other three the gap and the move
have OPPOSITE signs and a residual of ≈ ±200pts survives.** All five days are
`nq_implied`, so the basis does not split them.

**Consequences.** (a) The 10-02 recommendation that the defect is *"cosmetic —
two numbers shown with no stated reconciliation"* **is not supported**; the
10-01 framing of a latent error survives on 3 of 5 days. (b) *"Derive both grids
from one conversion"* still must not ship — not because the gap is cosmetic but
because **the residual is unexplained**. (c) Before any promotion of section 7,
print the feed-time delta **and** the residual, and reconcile the residual in
code. (d) The ±200 magnitude is noted as a **lead** toward D12's ~200pt
greeks-mismatch family — a lead, not a claim; three points with alternating sign
are not a mechanism. All instances remain damage-free: section 7 is
research-only and had **no volume** today (*"No volume has traded yet today"*).

## P-B(b) — 11th session; inflation 1.43x and the guaranteed window fired once

`merge_tol = max(3.0, 476.9 × 0.008) = **3.82**` against `TOUCH_TOL = **8.0**`.
One published pair sits in the structurally-guaranteed 3.82–8.0 window and it
fired: **30865.7 London High (today) / 30858.1 CALL WALL + shelf — 7.6pt gap**,
both graded touched at **bar 186**. Three rows (30908.1, 30865.7, 30858.1) all
graded touched on that one bar.

| day | published | touched | distinct | pub rate | distinct rate |
|---|---|---|---|---|---|
| 09-30 | 17 | 8 | 4 | 0.47 | 0.24 |
| 10-01 | 3 | 2 | 2 | 0.67 | 0.67 |
| 10-02 | 11 | 6 | 3 | 0.55 | 0.27 |
| **10-05** | **18** | **10** | **7** | **0.56** | **0.39** |

10 touches → **7 distinct bars** (178, 179, 182, 185, 186, 189, 224), inflation
**1.43x**. Proposal unchanged: (a) `merge_tol >= TOUCH_TOL`, (b) always report
distinct touch events beside the raw rate. **Today's rate is also diluted the
other way**: 8 untouched rows, all below price, on a day whose entire extension
was upside — the denominator is measuring board placement against a one-way
session, not level quality. Standing caution (09-21) applies.

## P-G — instance #13, and the second row is the mirror of it

Session-extreme prose chosen by level kind, not by which side price is on:

- **30770.2 Asia Low (today)**, **+19.4 ABOVE** the scan price: *"Low of the
  Asia session — the next session usually **runs the stops below it**"*. Price
  was already below it; it then acted as **support** for 475min.
- **30689.8 Asia High (prev-day)**, **−61.0 BELOW** the scan price: *"High of the
  Asia session — the next session usually **runs the stops above it**"*. Price
  was already above it. Untouched.

Both rows describe a sweep that had already happened. P-G → **13**.

## Dead-weight audit — refreshed to 25 scans

| row | days it scored ≠ 0 |
|---|---|
| `macro` NFCI financial conditions | **0 / 25** |
| `macro` yield curve 10y–2y | **0 / 25** |
| `macro` WALCL / RRP | **5 / 25**, all 08-24…08-28 — **0 of the last 20** |

PROPOSED, unchanged: drop or replace all three. Also unscored today, consistent
with the audit: `vol` VXN/VIX, `vol` VVIX, both `rates` rows, the gamma
band-position row, `fuel`, and the prior-week-range structure row.

## H8 — observation 3 of 10, and the first close OUTSIDE the band

Straddle **256pts** (ATM IV 11.2%) → EM **±218** → band **30533 .. 30968**.
Close **31110.3 — OUTSIDE by +142.3**; price traded outside from **14:20Z**
onward and never came back. Record: **2 inside / 1 outside, 3 of 10**. H8 has
been dormant since 08-27 and should be appended to every review, since it cannot
be backtested and only accrues forward.

**H8's own claim text pits EM against the VXN range, and today the VXN range
won.** VXN-implied daily range **410.7** vs realised range **410.4** — **0.3pts**
— while the straddle close-band was breached by 142.3. **They are different
objects** (high-low vs close-to-close) and the brief says so at the point of
use, so this settles nothing. **n=1, logged, no claim.** If the comparison is
ever to be made, it needs the VXN range graded against the *range* and the EM
graded against the *close*, both recorded every day.

## H22 — n=4, and still no ordering

| day | week net GEX $bn/1% | label | realised range / ADR14 |
|---|---|---|---|
| 09-30 | 0.036 | *"pinning likely"* | 0.84x |
| 10-01 | 5.58 | *"pinning likely"* | 1.33x |
| 10-02 | 9.526 | *"pinning likely"* | 1.09x |
| **10-05** | **0.463** | *"pinning likely"* | **0.86x** |

A 265x spread in the input, one label, no ordering in the outcome. Today the
label said *"pinning likely"* on a day that closed **93.4% up its range** after
eight rising hourly closes — qualitatively wrong for the 4th time. **n=4,
logged, nothing proposed**; four points cannot separate "the label is
non-discriminating" from "the input does not predict range".

## H18 / P1 — 12th instance, and today the stale rows pushed the score UP

| row | pts | its own words |
|---|---|---|
| macro DFII10 2.88% | **+3** | observation **2026-10-01**, *"FRED has not published since 2026-10-01 (2 business days ago) — this is last week's reading, not today's"* |
| macro DGS10 | +1 | *"moved 5bp down (2026-09-30 to 2026-10-01)"* — stale AND duplicated |
| macro HY OAS 3.24% | −2 | *"+44bp over 5 days"* — **no observation date rendered at all, 3rd consecutive session** |
| rates US10y | 0 | *"5.273 (−0.08%) — yields flat"* — live, same instrument, no conflict today |

**Damage: none.** Zeroing DFII10 → **+6, still BULLISH, still CORRECT**; zeroing
both stale macro rows → **+5**, same. First instance in the series where the
stale rows favoured the eventual direction.

**The DFII10 textual sub-defect did NOT fire** — a first in four sessions. Today
is **Monday 10-05**, so *"this is last week's reading"* is **true** of a 10-01
(Thursday) observation. The string is still unconditional, so this is luck, not
a fix.

**DGS10 duplication, 5th configuration:** stale **+1** against live **0** — same
sign family, no conflict, still a duplicate of the same instrument.
**Age-gate blocker now 3 sessions old**: HY OAS renders no observation date, so
the gate cannot measure the second-largest macro row. H18/P1's ACCURACY case
stays retracted (10-01); correctness grounds only.

## No instance today

- **H4** — GAMMA FLIP 30631.4 was **119.4 below** the scan and the post-scan low
  (30736.6) came no closer than **105.2**. No flip read. The `gamma +2` *"above
  flip… dips supported, **upside grinds**"* row was right, and "grinds" is a
  literal description of the day.
- **H10** — did not fire; `structure 0`, *"price inside the prior-week range
  (30101.2–31037.1)"*. Price closed **+73.2 above PWH 31037.1**, i.e. it left the
  range in the direction the row declined to call. The `+3` branch's record stays
  **2-for-4**; its falsification test (next firing at >700pts above PWH) is
  unchanged.
- **H20 / D24** — one **Medium** event *ahead* of the scan (ISM Services PMI,
  14:00Z, +1.2h; `event_gate: None`), and **nothing fired in the 6h before the
  scan** on the pipeline's own `events_24h` union. No instance of either.
- **H2 / H3** — fuel `MODERATE`, not LOW_FUEL/EXHAUSTED; price mid-band (73% up
  a 400pt wall band), not an extreme. Neither cell.
- **P3 / H6** — **no `structural` row published today** (18 rows: liquidity ×11,
  gamma ×4, gamma-shelf ×2, magnet ×1). The 0-touch-on-9-publications census is
  unchanged.
- **P-C / `events`** — **no `events` row at all** again (24 components, none
  `events`), per `add("events", 0, …)` over `heavyweight_earnings_next_5d`.
- **P-F** — price inside the prior-day range at the scan (286.3 below PDH,
  230.2 above PDL): inside-range control, error **−66.5**. Control becomes **21
  days**.
- **D21** — **did not fire.** Wall band 30458.1–30858.1 = **400pts**, price **73%
  up it**, so the *"top 20%"* `gamma −2` branch stayed silent, and its silence
  was right on a day that then ran 279.2 above the band. Tally unchanged at
  5 up / 1 down *within* 50pts and 3 down / 0 up *beyond*; **still not
  proposed**, the cut was found after looking at outcomes.
- **Max pain** — **30408.1 at −342.7 = 0.72x ADR14**, never reached. Distance
  misses now **246, 340, 103, 175, 589, 343**; evidence days 9, of which 6 are
  distance misses. The recommendation to tighten the threshold to *"3 days on
  which max pain is within reach"* stands and stays ungradeable until M6 is
  decided. The row's own qualifier (*"Weak on a Monday"*) was right on a Monday.
- **Post-scan direction vs day-net direction AGREED today** (+369.8 and +253.9,
  both +1). The 10-02 flag stays at **n=2** — **today is explicitly NOT the third
  instance** it pre-registered. The three entries whose verdicts flip with the
  convention (H18/P1, D21, H10) are unaffected this session.

## Journal hygiene

No fabricated or backfilled entries; no `prediction` block touched. One scan file
for 10-05 (`1247-preny.json` + `.md`), `is_trading_day: true`, 0 test artefacts.
09-24 quarantined by hand as directed — **sixth consecutive review to carry it**;
the 09-29 proposal for a `quarantine` field in the journal schema, read by
`track.py` and `review_day.py`, is **reaffirmed**. 09-25 cited from the 09-28
entry, not re-derived; no review file back-dated for 09-24 or 09-25. 2026-10-06's
scan exists (`is_trading_day: true`, bias +3, `COHERENT_LONG`) and is correctly
**held back** by `track.py` (179 bars).

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01M7sro1DKMp5T7EBDusm6pM

---

# Observations appended 2026-10-07 (grading the 2026-10-06 session)

Source: `review_day.py 2026-10-06 --json`, `track.py`, and the 10-06 scan's own
`.json`/`.md`. Full write-up in `2026-10-06/REVIEW.md`.
Session: O **31117.9** / H **31385.1** / L **31078.9** / C **31270.8**, range
**306.2** (0.63x ADR14 486.2), net **+152.9**, 276 bars. One scan
(12:48:24Z PRE_NY), **1 direction right / 0 wrong**, 19 levels / 3 touched
(0.16). 09-24 excluded by hand from every statistic, as directed.

## P-E — instance 12, and THE EMPTY MIDDLE IS NO LONGER EMPTY

CALL WALL **31309.0** (merged row: London High (today) + CALL WALL ●●●●● 1.12bn
+ Options shelf 1.11bn; the unmerged wall is **31307.6**), published at **+66**
with *"Heaviest ceiling this week (13k contracts) — desks must SELL as price
rises into it, so rallies stall. Take profit into it… the strongest ceiling on
the board."*

Sequence: first post-scan touch **13:30Z**, crossed **inside that single M5 bar**
(O 31284.0 → H 31334.9) and closed the bar back at **31257.5** — the first break
failed. Re-broke, ran to **31385.1 at 15:15Z**, settled below from 18:10, closed
**31270.8**.

**Overshoot +76.1 against the published row (+77.5 against 31307.6).**

| mode | instances | magnitude |
|---|---|---|
| capped | 08-26, 09-08, 09-11, 09-14 | overshoot **3.6 – 11.9** |
| **middle** | **10-06** | **76.1** |
| sliced | 08-27, 08-28, 09-18, 09-21, 09-22, 09-30, 10-05 | 103 / 117.5 / 154 / 185 / 205 / 279.2 / 573 |

The 09-22 entry pre-registered this exactly: *"Watching for one instance between
12 and 103 — an empty middle in nine observations is either real bimodality or an
artefact of `SETTLE_TOL`, and a middle observation separates those."* **It has
arrived at n=12.**

**And it is clean on the contamination axis** (per the 10-05 caveat and the
standing instruction to state it): the wall **is the pre-scan high to the point**
— pre-scan H = 31309.0 — with **5 pre-scan bars within `TOUCH_TOL` and 0 pre-scan
bars strictly above it**. Unlike 10-05's 30858.1, this level had never been
broken when the board was published. The overshoot was earned entirely
post-scan.

**Second first: a material overshoot that closed BELOW the wall.** Close 31270.8
is **−38.2** under it. Every slice in the census that quotes a close closed
*above* the wall (+79, +151, +486.8, +204.7, +252.2). So today splits what the
census has been conflating: **intraday penetration and close-side control are
different outcomes**, and on this day they disagreed.

**Consequence: stop reading P-E as bimodal.** Two modes in eleven observations
with an empty middle is now a continuum with a thin middle. Do **not** extend the
two-mode framing and do **not** resume the search for a mode discriminator — the
09-18/09-08 breadth candidate stays rejected. **Nothing new proposed.** P-E's
existing **prose** proposal (lead with the conditional *"a held close above flips
that selling to buying"*; drop the unconditional *"rallies stall. Take profit
into it… the strongest ceiling on the board"*; print the measured run-through
distribution if a number is printed at all) is unchanged and is now better
supported, because today both sentences were true four hours apart and the
document orders them worst-first.

## P-E(b) — 12th instance, the FIRST that is not pre-scan-contaminated, and the shelf family falls outside 22pts

Stating it explicitly as directed: **the level was published before the move it
is credited with.** Shelf **31357.6** (0.97bn) was on the 12:48Z board at **+115**
and had **0 pre-scan bars within `TOUCH_TOL`**; first touch **14:10Z**. No
selection on pre-scan history is possible here.

The lid: session high **31385.1**, i.e. **+27.5 above 31357.6** and **22.5 below
the next shelf up, 31407.6** (untouched). Shelf family, on the register's own
convention (the nearest shelf the high exceeded): the last recorded figure was
**8 of 9 inside 22pts** at the 9th instance (10-01, +1.3), and the register logs
**no shelf instance on 10-02 or 10-05**, so today is the **10th → 8 of 10 inside
22pts**. Today's **+27.5** is the **second breach**, after 09-29's 53.6.
(Headlined as P-E(b) **instance 12** on the whole-series numbering of 11 prior
instances; the two counts differ because the series pools shelf and
session-extreme observations while the shelf sub-count does not. **That
ambiguity should be resolved before any P-E(b) figure is quoted again** — it is
exactly the double-naming the ID-allocation block exists to prevent.)

**The undeclared selection on distance is still live and still non-monotonic.**
Today the shelf at +115 located the high to 27pts while the shelf at **+15**
(31257.6) was sliced by **127.5** and the shelf at **+165** was never reached.
Which shelf caps remains unpredicted. **Nothing proposed beyond what P-E already
proposes.**

## H23 — 7th instance; 6 sliced / 1 capped, and both named brakes were pre-traversed

| session | brake | dist | outcome | x ADR |
|---|---|---|---|---|
| 09-30 | 30487.7 upside | +26 | sliced +167.5 | 0.36 |
| 10-01 | 30586.0 downside | −18 | sliced 300.5 | 0.65 |
| 10-01 | 30636.0 upside | +32 | capped at +1.3 | 0.00 |
| 10-02 | 30846.7 downside | −19 | sliced 102.5 | 0.22 |
| 10-02 | 30896.7 upside | +31 | sliced 140.4 | 0.30 |
| 10-05 | 30808.1 upside | +57 | sliced +328.3 | 0.69 |
| **10-06** | **31257.6 upside** | **+15** | **sliced +127.5** | **0.26** |

*"**UPSIDE path: has friction.** Expect a stall at 31257.6 (15pts away) — take
partials into it rather than assuming a clean breakout."* High **31385.1**.
The mirror sentence — *"**DOWNSIDE path: has friction.** Expect a stall at
31207.6 (35pts away)"* — was **never tested**: the post-scan low never came below
≈31247.

**Variation worth recording: both named brakes were levels the same session had
already traversed.** 31207.6 had **153 of 178 pre-scan bars with lows below it**
(148 entirely below); 31257.6 had 162 pre-scan bars entirely below it and 7
pre-scan touches. The brake is being named from a static grid, not from what
price has done to it today. **Already-PROPOSED fix unchanged** (drop the
assertion or print the measured base rate beside it), now at **1-in-7**.

## D25 (NEW, OPENED and PROPOSED) — D14's fix never covered the `drift` sentence, and the same false claim has printed on 20 consecutive pre-NY scans

Section 7 of the 10-06 brief:

> **The dominant strike is stable** at 0 across 6 samples — positioning is settled there.

`grep -c` over the journal: that string is **byte-identical in 20 scan files** —
09-11 (both scans), 09-14 1304-preny, and every pre-NY scan from 09-15 through
10-07. Excluding the quarantined 09-24 and the unfinished 10-07 that is
**19 scans across 17 completed trading days**. **No day in the record prints a
different number.**

**It is the exact sentence D14 named as its own symptom.** `gexbot.py`'s
`strike()` docstring quotes it verbatim. The 09-16 fix guarded the strike
*fields* returned by `gexbot.levels()` — which works, today's volume column
correctly renders `—` and the section says *"No volume has traded yet today"*
out loud — but `brief.py`'s drift block reads

```
dr['distinct_strikes'][0]
```

with **no guard at all**, so the absent dominant strike still renders as `0` and
is then asserted to be settled positioning.

**Proof it is absence, not data.** The only mid-RTH scan in the record —
**09-14 17:23Z**, volume present — printed *"**The dominant strike is MOVING** —
over the last 6 samples it has sat at 29,050, 29,100, 29,250, 29,300, 29,350 (a
300pt spread)"*. Every pre-open scan prints 0. This is the scheduled 12:45Z run
hitting the no-volume window every weekday, precisely as the D14 entry predicted.

**Damage: none.** Section 7 is research-only and says so. That is what makes this
a clean defect rather than a calibration question: **the page contradicts itself
in writing**, three lines apart.

**PROPOSED.** Suppress the drift sentence when `volume_fields_absent`, or route
`distinct_strikes` through the existing `strike()` guard and render `—`.
Expected effect: removes a constant false assertion from every scheduled brief,
and closes the last place a volume-absent `0` survives as a *claim* — which
matters because D14's own fix note says *"H12 and H13 must not count a scan whose
volume fields are 0."*

## Session-context field — 8th session, and a row that asserts the opposite of its own session

Already PROPOSED on 09-29 (`tested_today` per `prediction.levels`; grade against
the whole session). Previous instances: 09-17, 09-28, 09-29, 09-30, 10-01, 10-02,
10-05. **8 of 19 published rows had already been interacted with in the same
graded session**, under the banner *"**New trading day.** … everything below is
fresh"*:

| row | pre-scan touches | pre-scan bars on the far side | prose it carries |
|---|---|---|---|
| **31309.0** CALL WALL + London High + shelf | **5** | **0 above** | *"rallies stall… strongest ceiling on the board"* |
| 31257.6 shelf 0.58bn | 7 | 162 below | *"+15 … expect price to stall"* + §3 upside brake |
| 31207.6 shelf 1.08bn | 10 | 153 below | §3 downside brake, *"assume no clean breakdown"* |
| 31181.0 Asia High (today) | 20 | 146 below | *"the next session usually runs the stops above it"* |
| 31157.6 shelf 1.22bn | 44 | 130 below | *"expect price to stall"* |
| 31137.3 PDH + NY High (prev-day) | 67 | 97 below | *"the biggest pile of stops **above us**"* |
| **31115.8 Equal lows ×4** | **64** | **44 below** | *"**never traded through**"* |
| 31110.7 London Low + PD close + shelf | 51 | 32 below | *"runs the stops below it"* |

**New sub-shape, and the strongest instance in the series: a row whose prose is
falsified by its own session.** 31115.8 is published as *"4 touches at this
price, **never traded through** — a real stop cluster. Prime S1 sweep trigger."*
In this same graded session price traded below it in **44 bars, 22:35Z → 07:05Z,
20 of them entirely below**, bottoming **36.9pts through it** at the Asia low
31078.9. The sweep it offers as a forward trigger had already happened, already
failed, and the day never returned. **Proposal unchanged**; this is the first
instance where the missing field would have changed a factual claim rather than a
behavioural expectation.

## M6 — session 19, 3 of 3 touched rows understated and 3 of 3 "held" verdicts inverted

`SETTLE_TOL = 25.0`. Reported `worst_excursion` is measured from the settled
point; true worst excursion measured first touch → close:

| level | verdict | reported | true, first touch → close | ratio | verdict if measured properly |
|---|---|---|---|---|---|
| 31357.6 | *"held as **resistance** 330min, worst +5.2"* | +5.2 | **+27.5** | **5.29x** | **lost** (>25) |
| 31309.0 | *"held as **resistance** 165min, worst +10.0"* | +10.0 | **+76.1** | **7.61x** | **lost** (>25) |
| 31257.6 | *"held as **support** 60min, worst −10.6"* | −10.6 | **−28.9** | **2.73x** | **lost** (>25) |

**3 of 3 graded rows invert**, where 10-05 was 3 of 6 and 10-02 was 3 of 3. The
DOWN/UP wording sub-shape did **not** fire today — no row graded *"lost"*, so the
`broke {'DOWN' if settled_side == 'above' else 'UP'}` string was never reached.
**19 sessions. Re-proposed for a decision, unchanged:** compute
`worst_excursion` over the whole post-touch window, or report both figures, and
derive the DOWN/UP word from the side the breach was on rather than from
`settled_side`.

**Read cold, `review_day` says today's call wall "held as resistance". It gave up
76.1pts and the day's high was 76.1 above it.**

## H18 / P1 — 13th instance, and the stale and live rows now say OPPOSITE things about the same instrument

| row | pts | its own words |
|---|---|---|
| macro DFII10 2.92% | **−3** | observation **2026-10-02**, *"FRED has not published since 2026-10-02 (2 business days ago) — this is last week's reading"* |
| macro DGS10 | −1 | *"moved 4bp up (2026-10-01 to 2026-10-02)"* — stale AND a duplicate of the same instrument |
| macro HY OAS 3.1% | −2 | *"+17bp over 5 days"* — **no observation date rendered at all, 4th consecutive session** |
| rates US10y | **+1** | *"5.277 (−0.64%) — **yields down, BULLISH tech**"* — live |

**The conflict the 10-05 entry said was absent is present today.** The stale
DFII10/DGS10 pair reads *yields UP, bearish* for **−4**; the live US10y row reads
*yields DOWN, bullish* for **+1**. Same instrument family, opposite signs, and
the stale side carries four times the weight.

**Damage: none to the sign.** Zeroing DFII10 → **+6**; zeroing all three stale
macro rows → **+9**. Both still bullish, both still CORRECT. The cost is **6
points of conviction on a correct call** — second instance of that shape
(09-18 was the first).

**The DFII10 textual sub-defect did NOT fire** — second time in five sessions.
Today is **Tuesday 10-06** and the observation is **Friday 10-02**, so *"this is
last week's reading"* is true. The string is still unconditional; still luck.

**Age-gate blocker now 4 sessions old**: HY OAS renders no observation date, so
the gate cannot measure the second-largest macro row. **H18/P1's ACCURACY case
stays retracted (10-01) and must not be revived until that blocker is fixed.**
Correctness grounds only.

## D21 — 10th firing, and the FIRST counter-instance in the "beyond 50pts" bucket

`gamma −2` *"price sits in the top 20% of the wall band (30707.6–31307.6) — poor
risk/reward for longs"*. Price **31243.0 = 89.2% up a 600pt band**, **64.6 below
the call wall**. Outcome: price **left the band upward** (high **+77.5** above the
band top) and closed back **inside** it at 31270.8. Day direction **UP**.

On the register's current convention (absolute distance to the call wall, adopted
09-23 because band percentage mixes physically different conditions):

| bucket | was | now |
|---|---|---|
| within 50pts | 5 up / 1 down | unchanged |
| **beyond 50pts** | **3 down / 0 up** | **3 down / 1 up** (10-06 at +64.6) |

**This is the first counter-instance in the bucket that made the re-cut look
clean**, and the re-cut was itself found after looking at outcomes — the
procedure the standing rule forbids acting on. **Still NOT proposed**, and the
for/against tally is deliberately not restated: the register switched conventions
on 09-23 and reviving the old one now would be picking whichever reads better.

**Width defect, 10th firing:** "top 20%" of a 600pt band is a **120pt trigger
window = 0.25x ADR14**, against 20pts on 09-18. Unchanged and unproposed.

## H22 — n=5, and the near-replicate the register asked for has arrived

| day | week net GEX $bn/1% | label | realised range / ADR14 |
|---|---|---|---|
| 09-30 | 0.036 | *"pinning likely"* | 0.84x |
| 10-01 | 5.58 | *"pinning likely"* | 1.33x |
| 10-02 | 9.526 | *"pinning likely"* | 1.09x |
| 10-05 | 0.463 | *"pinning likely"* | 0.86x |
| **10-06** | **9.084** | *"pinning likely"* | **0.63x** |

**10-02 (9.526 → 1.09x) and 10-06 (9.084 → 0.63x) are a near-replicate pair: a
4.6% difference in the input, a 0.46x difference in the outcome.** Across n=5 the
input spans 0.036 → 9.526 with no ordering at either end, and one label for all
five. The 10-05 entry said four points could not separate *"the label is
non-discriminating"* from *"the input does not predict range"*; the replicate pair
speaks to the second — nearly identical input, very different realised range.

**NOTHING PROPOSED, and the reason is specific.** The row carries **+2 of
DIRECTION score**, and five *range* observations are not evidence about
direction. Proposing against a directional row on range evidence is exactly the
mis-targeting that D21's own 8-firing ledger exposed. **The test that would
settle it needs no new data:** grade the `week net GEX → pinning likely` row
against realised **direction** across the 26 days already on record. Logged as
the next thing to measure, not as a change.

## H1 — n=26, the largest single-day over-read in the record, and the multiplier branch should be closed (6th consecutive entry)

10-06: budget **256.2**, extension **76.1**, error **−180.1** — **the largest
negative per-day error in the whole record** (previous worst −124.4 on 09-25).
`track.py` per-DAY mean **+14.0** (n=26), per-scan **+19.8** (n=33); **−8.2**
excluding the 09-21 outlier (n=25, was −1.08 at n=24). MAE **88.9** against a
mean per-day budget of **110.8** — **the typical error is 80% of the typical
budget**. H5: early (26) **+30.6** vs late (5) **−11.7**, sign unchanged.

Last six per-day: **+153.7, +41.7, −66.5, −180.1** (and −75.2, −112.2 before
them). The estimator is **unbiased and the dispersion is the entire problem**. A
multiplier corrects a bias that does not exist; nothing in 26 days identifies a
term that explains the spread.

**The qualitative text was FINE today, which is the finding.** *"The range has
room but not unlimited room. Continuation is fine to the nearest pool; don't plan
on a third leg"* — the range used **30% of its budget** and there was no third
leg. On 10-05 the identical sentence was badly wrong (price traveled +386.5
through nine levels). **The sentence is unanchored, not consistently wrong**, so
the 09-16 sub-observation (*"the budget's correct reading is not reaching the
prose"*) cannot be fixed by inverting it — it needs to be derived from the
number or dropped.

## P-B(b) — 12th session; inflation 1.00x and the guaranteed window did not fire

`merge_tol = max(3.0, 486.2 × 0.008) = **3.89**` against `TOUCH_TOL = **8.0**`.
**One published pair sits in the structurally-guaranteed 3.89–8.0 window**
(31115.8 Equal lows ×4 / 31110.7 London Low + PD close + shelf 1.43bn, **5.1pt
gap**) and it did **not** fire — both rows were untouched post-scan.

| day | published | touched | distinct | pub rate | distinct rate |
|---|---|---|---|---|---|
| 09-30 | 17 | 8 | 4 | 0.47 | 0.24 |
| 10-01 | 3 | 2 | 2 | 0.67 | 0.67 |
| 10-02 | 11 | 6 | 3 | 0.55 | 0.27 |
| 10-05 | 18 | 10 | 7 | 0.56 | 0.39 |
| **10-06** | **19** | **3** | **3** | **0.16** | **0.16** |

3 touches → **3 distinct bars** (178, 186, 194), inflation **1.00x**. Proposal
unchanged: (a) `merge_tol >= TOUCH_TOL`, (b) always report distinct touch events
beside the raw rate.

**Today's rate is diluted the other way, and worse than on 10-05.** Of 19 rows,
**15 sat below the scan price on a day whose entire post-scan extension was
upside** — those 15 were never going to be tested. **Rows above the scan went 3
of 4 (0.75); rows below went 0 of 15.** The published 0.16 measures board
placement against a one-way session, not level quality. Standing caution (09-21)
applies and is now quantifiable: the all-time `track.py` mean hit rate is
**0.52**, and a day like today pulls it for reasons that have nothing to do with
whether the levels work.

## P-G — instance #14, and a PDH row that says "above us" while 106 below

Session-extreme and sweep prose chosen by level kind, not by which side price is
on:

- **31137.3 PDH + NY High (prev-day)**, **−105.7 BELOW** the scan price:
  *"Yesterday's high — the biggest pile of stops **above us**. Sweep it, wait for
  a lower high on the 1m, then CISD = short."* It is not above us. This is the
  strongest row in the P-G series so far, because it issues a **short trigger**
  off a sweep that had already completed upward.
- **31181.0 Asia High (today)**, **−62.0 below**: *"the next session usually runs
  the stops **above it**"* — price was already above it.
- **30987.6 Asia High (prev-day)**, **−255.4 below**: same string, same
  wrong-sidedness.
- **30865.7 London High (prev-day)**, **−377.3 below** *(stretch)*: same.

Four wrong-sided rows in one document. P-G → **14**. Already PROPOSED.

## H8 — observation 4 of 10, and back inside the band

Straddle **215pts** (ATM IV 13.8%) → EM **±182** → band **31060 .. 31426**.
Close **31270.8 — INSIDE**. Record: **3 inside / 1 outside, 4 of 10**.

**The VXN-vs-EM comparison the 10-05 entry opened goes the other way today.**
VXN-implied daily range **427.1** vs realised range **306.2** — VXN **over by
120.9** (realised 0.72x) — while the straddle close-band held. Yesterday VXN was
accurate to 0.3pts and the band broke. **n=2 on the comparison, the two
observations disagree, nothing claimed.** The register's own requirement stands:
grade the VXN range against the *range* and the EM against the *close*, every
day, before anything is read from either.

## No instance today

- **H4** — GAMMA FLIP **30786.4** was **457 below** the scan and the session low
  (31078.9, set pre-scan) came no closer than **292.5**. No flip read. The
  `gamma +2` *"above flip… dips supported, **upside grinds**"* row was right, and
  "grinds" describes a +152.9 net on a 0.63x-ADR range exactly.
- **H10 — the `+3` branch FIRED and was RIGHT.** *"price is ABOVE the entire
  prior-week range (30101.2–31037.1) — weekly draw has flipped bullish; PWH
  31037.1 is now support"*, at **+205.9 above PWH**. Day closed **+233.7 above
  PWH** and the low (31078.9) never came within 41.8 of it. Branch record now
  **3-for-5**. Its pre-registered falsification test (next firing at **>700pts**
  above PWH) is unchanged and was not met today.
- **H17** — post-scan move **+37.5 = 12.2% of session range**. Above the 5%
  deadband, so **no instance**; still **1 of 3 days**, both instances 09-11. It
  is the smallest share since 09-11's 7.2% and worth noting that a **+3 call
  earned a CORRECT on a 37.5pt move while the day itself ran +152.9** — the grade
  is right on its own definition, but it is a thin one.
- **H2 / H3** — fuel **MODERATE**, not LOW_FUEL/EXHAUSTED; price 89% up the wall
  band but mid-session, not at a range extreme. Neither cell.
- **H20 / D24** — `inputs.events_24h` is **empty** and the brief says *"No
  High/Medium US events in the next 24h"*. Nothing ahead of the scan and nothing
  behind it. No instance of either.
- **P3 / H6** — one `structural` row published (30257.6 STRUCTURAL PUT WALL,
  −985 = **2.03x ADR14**), untouched. Census → **0 touches on 10 publications
  across 9 trading days**, and it **has still never been within 200pts of
  price**.
- **P-C / `events`** — **no `events` row at all** in 23 components, per
  `add("events", 0, …)` over `heavyweight_earnings_next_5d`. The row has now
  been absent or zero on every session in the record.
- **P-F** — price at scan was **+105.7 above PDH 31137.3**, i.e. **inside the
  ±150pt marginal band**, so this is a **control** day, not a treatment
  instance. Error **−180.1**, negative, consistent with the inside control.
  Control becomes **22 days**.
- **Max pain** — **30607.6 at −635.4 = 1.31x ADR14**, never reached. Distance
  misses now **246, 340, 103, 175, 589, 343, 635** — the **largest yet**;
  evidence days 10, of which **7** are distance misses. The recommendation to
  tighten the threshold to *"3 days on which max pain is within reach"* stands
  and stays ungradeable until M6 is decided. The row's own qualifier (*"Weak on a
  Monday"*) is uninformative on a Tuesday.
- **D7-shaped, contract count vs dollar gamma** — **no instance.** The headline
  CALL WALL is 1.12bn on **13k contracts** while the research-only secondary
  table carries **31507.6 at 0.65bn / 13,958 contracts** — more contracts than the
  headline wall — but the session high stopped **122.5 below** 31507.6, so the
  secondary strike forecast nothing today. Census stays at **n=2** (09-23,
  10-05).
- **D18 / D20 / H19** — 108 headlines → 37 relevant → **1 auto-scored**:
  coverage **2.7%**. The single scored headline is *"S&P 500, Nasdaq, Dow End
  Week Higher As **Weak Jobs Report Cools Rate Hike Bets**"*, tagged
  **hawkish → bearish, −180pts**. *Cooling* rate-hike bets is dovish, and the
  headline's own subject is a market that closed **higher** — this is **D18's
  keyword-without-its-subject shape, 7th trading day, 13th headline instance**,
  and **D20's freshness shape** on top (it describes *last week*). **Damage:
  none** — `news` scored **0** (NEUTRAL −0.18) and 36 headlines went uncounted.
  H19 coverage 2.7%, among the lowest in the series.
- **D23 — 7th clean offset.** Board offset **+7.6** (NDX reference 31235.4 rolled
  forward by the NQ move +159.0 against CFD 31243.0, basis `nq_implied`, greeks
  `repriced_bs_at_current_spot`). Section 7's own offset **+214.9**, gap
  **+207.3**; CFD move 11:59Z→scan (11:55Z M5 bar open 31282.3 → scan 31243.0) =
  **−39.3**; **residual +246.6**. Added as a new data point to the measured
  series, **not a re-run of it**: residuals are now
  **+190.5 / −201.3 / +203.8 / −7.3 / +2.9 / +246.6** — the intervening move
  explains **2 of 6** days and a **±200–250pt residual survives**, with today the
  largest. The 10-02 *"cosmetic"* reading stays **reversed** and the
  NEGATIVE result stands. All instances remain damage-free: section 7 is
  research-only and had **no volume** today.
- **The fuel-block / gamma-block conflict** — no instance. Fuel `MODERATE`, not
  LOW_FUEL/EXHAUSTED, so the two blocks were not in the cell where they give
  opposite instructions. Worth one line anyway: `STRATEGY 1`'s *"this is your
  fade day… sweeps genuinely fail"* was **right on the 13:30Z sweep of 31309.0**
  (failed, −77 back) and **wrong on the second attempt 40 minutes later** (ran to
  the high; the day closed +152.9 net up). One level, two sweeps, one of each,
  and the document offers no way to tell them apart. **n=1, logged, nothing
  proposed.**
- **Post-scan direction vs day-net direction AGREED** (+37.5 and +152.9, both
  +1). The 10-02 flag stays at **n=2** — today is explicitly **NOT** the third
  instance it pre-registered, and it is reported here rather than folded into the
  scoreboard, as directed.
- **Dead-weight audit, refreshed to 26 scans:** `macro` NFCI **0 / 26** ·
  `macro` yield curve 10y–2y **0 / 26** · `macro` WALCL/RRP **5 / 26**, all
  08-24…08-28, **0 of the last 21**. All three scored **+0** again today.
  PROPOSED, unchanged: drop or replace all three. Also unscored today and
  consistent with the audit: `vol` VXN, `vol` VVIX, `rates` DXY, `fuel`. Not
  dead today: `vol` VXN/VIX (−1) and `rates` US10y (+1).

## Journal hygiene

No fabricated or backfilled entries; **no `prediction` block touched**. One scan
file for 10-06 (`1248-preny.json` + `.md`), `is_trading_day: true`,
`review_day` reports **0 test artefacts** for the day (`track.py` excludes 6
across the whole record). 09-24 quarantined by hand as directed — **seventh
consecutive review to carry it**; the 09-29 proposal for a `quarantine` field in
the journal schema, read by `track.py` and `review_day.py`, is **reaffirmed, and
the hand-exclusion is now the single most-repeated manual step in this process**.
09-09 and 09-25 still have **no `REVIEW.md`** and none was created or
back-dated; nothing was graded for them here. 2026-10-07's scan exists
(`1250-preny.json`, `is_trading_day: true`) and is correctly **held back** by
`track.py` (181 bars).

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01M7sro1DKMp5T7EBDusm6pM

---

# Observations appended 2026-10-08 (grading the 2026-10-07 session)

Source: `review_day.py 2026-10-07 --json`, `track.py`, and the 10-07 scan's own
`.json`/`.md`. Full write-up in `2026-10-07/REVIEW.md`.
Session: O **31280.1** / H **31293.0** / L **30918.0** / C **31172.6**, range
**375.0** (0.79x ADR14 472.8), net **−107.5**, 276 bars. One scan (12:50:43Z
PRE_NY, **STRONGLY BEARISH −10**), **0 direction right / 1 wrong** on the
post-scan convention, 15 levels / 7 touched (0.47). 09-24 excluded by hand from
every statistic, as directed.

## P-H (NEW, OPENED and PROPOSED) — the direction-grading convention now decides a verdict, and n=3 is reached

The 10-02 entry pre-registered this: *"the register grades direction post-scan
while `bias_label` reads as a day call. n=2, nothing proposed."*

| day | post-scan move | day net | bias | did the split matter? |
|---|---|---|---|---|
| 10-01 | −74.7 | +64.3 | +2 | no — *no call* either way |
| 10-02 | −75.2 | +288.4 | +1 | no — *no call* either way |
| **10-07** | **+137.8** | **−107.5** | **−10** | **YES — WRONG post-scan, CORRECT day-net** |

**Third instance, threshold met, and the first one that is not free.** It is also
the first with the signs the other way round (post-scan up against a down day;
both earlier instances were post-scan down against an up day), so this is not a
one-sided artefact of a trending fortnight.

**PROPOSED, and it is a reporting change, not a model change:** emit both
`post_scan_move` and `day_net_move` from `review_day` plus an explicit
`direction_call_basis` field, and state the basis in the printed output.
**Recommended basis: post-scan** — the brief is published at the scan and can
only be traded forward; a day-net grade credits a move that was already over when
the user read the document. 10-07 is the worked example: the entire −107.5 of
day-net decline happened **before** the scan (session open 31280.1 → pre-scan low
30979.1), and the brief was issued 52.6 above that low.

**Expected effect:** no change to any score, level or budget. It unblocks three
register entries whose verdicts flip with the convention and which the register
has already flagged as convention-dependent — **H3**, **D21**, **H10** — and it
makes the all-time scoreboard (15 right / 9 wrong / 7 no-call ex-09-24) mean one
definite thing.

## H3 — 4th max-conviction bearish call at a session low, 4th wrong, and BLOCKED by P-H

`−10 STRONGLY BEARISH` printed at **31031.7**, **17.0% up the pre-scan range**
(31293.0–30979.1), **52.6 above the pre-scan low**, **5.9 above the heaviest put
wall on the board**, with **66.4% of ADR14 already spent** and `fuel_ratio 1.48`.
Post-scan move **+137.8 — WRONG**.

The bearish branch the 09-21 entry asked to be re-scoped is now **0 for 4**
(08-24 13:45, 08-25 13:04, 09-14 13:04, 10-07 12:50), against **1 for 1** on the
bullish-at-a-high branch (09-21, correct by +537.9).

**NOT PROPOSED, and the reason is P-H, not the count.** On the day-net convention
this instance is **CORRECT**, so the 4th data point for a conviction cap exists
only under one of two live grading conventions. Proposing a cap now would be
fitting a rule to a convention that has not been chosen. **H3's bearish branch is
threshold-met and formally blocked on P-H.** Re-grade all four instances the
moment P-H is decided.

## H18 / P1 — 14th instance, and the duplication is now CODE-CERTAIN across 22 days

| row | pts | its own words |
|---|---|---|
| macro DFII10 2.95% | **−3** | observation **2026-10-05**, *"FRED has not published since 2026-10-05 (2 business days ago) — this is last week's reading"* |
| macro DGS10 | **−1** | *"moved 3bp up (2026-10-02 to 2026-10-05)"* — same instrument, same window |
| macro HY OAS 3.12% | 0 | *"+10bp over 5 days"* — **no observation date rendered at all, 5th consecutive session** |
| rates US10y | **−3** | *"5.337 (+1.29%) — yields up, multiple compression, BEARISH tech"* — live |

**Stale and live AGREED today** — both read *yields up, bearish*. That answers the
question the task set: there was **no conflict**, so an age gate would have
changed nothing. **The defect on this day is duplication, not staleness.**

**New census, run over every graded pre-NY scan in the record (22 days, 09-24
excluded, 10-08 ungraded):**
- **Whenever `macro` DFII10 scores non-zero, `macro` DGS10 scores the same sign —
  20 of 20.** The macro block therefore carries a guaranteed **±4 off a single
  FRED observation**, with no condition that can break the lock.
- The live `rates` US10y row agrees with DFII10's sign on only **7 of the 16 days
  both are non-zero** (9 disagreements: 08-25, 08-26, 09-11, 09-17, 09-22, 09-23,
  09-30, 10-02, 10-06). **A coin flip, with the stale side carrying four times
  the weight.**

**Damage, and it is the largest in the series: the label.** The 09-30 proposal
(suppress DGS10 when a live US10y read exists) takes **−10 → −9 = BEARISH** —
**the first day in the record on which that fix removes the published STRONGLY
tag.** Zeroing DFII10 as well gives **−6 = BEARISH**. Direction is −1 in every
variant, so the fix stays provably call-neutral; what the duplication bought was
**4 points of conviction, and the conviction is the thing the user acted on.**

The DFII10 textual sub-defect **did NOT fire** (today Wed 10-07, observation Mon
10-05 — *"last week's reading"* is **false**; the string is unconditional, so this
is a miss, not luck in the other direction). **Age-gate blocker now 5 sessions
old**: HY OAS renders no observation date. **H18/P1's accuracy case stays
retracted (10-01) and must not be revived until that blocker is fixed.**
Correctness and duplication grounds only.

## D26 (NEW, OPENED and PROPOSED) — a day that aged out of the bar window is filed as "not finished"

`track.py` printed, on 2026-10-08:

> HELD BACK - day not finished (grades after 21:00 UTC on its own date):
>   2026-08-24  99 bars so far

**2026-08-24 finished 45 days ago.** `review_day.fetch_day_bars` computes
`days=min(days_back, 45)`, so from 10-08 the broker is only asked for bars back
to 08-24 and serves a partial day; `_day_complete(day, bars, min_bars=240)`
returns False on 99 bars; the day lands in the `unfinished` bucket under a label
that reads as *pending*.

**Measured damage, today:** H1's per-scan n went **33 → 30** while one scan was
**added** — 08-24's four graded rows left the sample — and the per-day mean moved
**+14.0 → +7.9**. Nothing was deleted and nothing was found; a figure the register
quotes changed because the calendar advanced.

**This is D16 exactly, at the new boundary, and D16's own fix note pre-registered
it:** *"Raised to 45; beyond that the honest fix is to persist graded outcomes
rather than re-derive them from bars that will not exist forever."* The 45 is not
the bug — the silence is. D16's whole complaint was *"the cap is invisible and it
EATS THE EVIDENCE BASE as time passes"*, and the current code now reports that
erosion as a day we are still waiting on.

**PROPOSED.** (a) Split the bucket: `day < today − 45d` → *"aged out of the bar
window (N bars served)"*, never *"not finished"*. (b) Persist graded per-day
outcomes (budget / extension / traversal / call / hit rate) to disk and read them
in preference to re-deriving from bars. **Expected effect:** the evidence base
stops shrinking, and every statistic the register quotes becomes reproducible
after the bars are gone. Defect with one clean, fully-traced instance — not
calibration, so not 3-session gated.

## M6 — session 20, and the worst instance in the record by a factor of two

`SETTLE_TOL = 25.0`. Reported `worst_excursion` is measured from the settled
point; true worst excursion measured first touch → close:

| level | verdict | reported | true, first touch → close | ratio | verdict if measured properly |
|---|---|---|---|---|---|
| 31181.0 | *"held as **resistance** 485min, worst +6.5"* | +6.5 | **+6.5** | 1.00x | held ✓ |
| 31114.3 | *"held as **support** 240min, worst −23.4"* | −23.4 | **−47.2** | **2.02x** | **lost** |
| 31078.9 | *"held as **support** 325min, worst −11.8"* | −11.8 | **−43.8** | **3.71x** | **lost** |
| 31037.1 | *"held as **support** 355min, worst −18.6"* | −18.6 | **−119.1** | **6.40x** | **lost** |
| **31025.8** | *"held as **support** 355min, worst −7.3"* | **−7.3** | **−107.8** | **14.77x** | **lost** |
| 30979.1 | *"held as **support** 415min, worst −13.3"* | −13.3 | **−61.1** | **4.59x** | **lost** |
| 30973.1 | *"broke DOWN through it — **lost** by 25.6"* | −25.6 | **−55.1** | 2.15x | lost ✓ (magnitude understated) |

**6 of 7 understate; 5 of 6 "held" verdicts invert to "lost".** The **14.77x** on
the PUT WALL is nearly double the previous worst in the series (7.61x, 10-06) and
it lands on the single most load-bearing row of the day: read cold, `review_day`
says the 1.15bn dual-expiry put wall *held as support for 355 minutes*, on a day
price sliced it by **107.8pts = 0.23x ADR14**.

**New sub-shape, first recorded instance.** Row 31181.0 is reported
`settled_side: "below"`, `settled_from: "open"`, `minutes_held: 485`. **At the
session open price was 31280.1 — 99.1 ABOVE that level**, and the first post-scan
touch was 19:55Z. The `settled_from: "open"` branch asserts a side the open
contradicts. This is distinct from the understatement defect and from the 10-06
DOWN/UP wording inversion.

**20 sessions. Re-proposed for a decision, unchanged:** compute
`worst_excursion` over the whole post-touch window, or report both figures;
derive the DOWN/UP word from the side the breach was on rather than from
`settled_side`; and do not seed the settled read from `"open"` when the open is
on the other side of the level.

## The put wall question — structure won, but the regime was right for 15 minutes

Recorded as its own entry because the task asked it directly and because the
answer is time-dependent, which the register has no field for.

PUT WALL **31025.8**, published at **−6**, ●●●●● 1.15bn, *"ALSO the 45-day put
wall (28k contracts) — defended across expiries, so it is the strongest floor on
the board"*, carrying the regime rider *"BUT today the desks are pushing moves
along — if it breaks, expect it to speed UP, not bounce. **Don't buy the
break.**"*

| time | what happened |
|---|---|
| 12:50Z | scan, price 31031.7, −10 STRONGLY BEARISH |
| 12:55Z | first post-scan touch of the wall (and of PWH 31037.1) |
| 13:30Z | NY cash open; bar sweeps to 30988.0, **closes back above at 31028.0 — first break fails** |
| **13:35Z** | one M5 bar: **31027.8 → 30922.4, −105.4** |
| **13:45Z** | session low **30918.0** — **107.8 below the wall**, and price never traded lower |
| 14:55Z | **back at 31025.8** — wall reclaimed 70 min after the low |
| 15:35Z | GAMMA FLIP 31114.3 reclaimed, held to the close |
| 20:55Z | close **31172.6 = +146.8 above the put wall** |

**The acceleration claim was mechanically correct and economically irrelevant:**
the break ran 107.8pts in 15 minutes, which is **0.23x ADR14** and **68% of the
entire remaining range budget**, and that was the whole of the downside. The
regime rider won the first hour; the structural weight won the day. **The level
the document told the user not to buy was the day's floor, and the trade that
worked was the S1 fade the same document said had *"a materially lower hit rate
here — only take them at the far walls"*** — which the put wall was. The right
answer was present, in a subordinate clause, with no way to prefer it.

**n=1. Nothing proposed.** What would make this measurable is a field the board
does not have: for each wall, the *distance* it has run through on prior breaks
in the same gamma regime. Logged as the thing to measure, not as a change.

## H20 — n=3, THRESHOLD MET, and the sign does NOT hold

| day | event | hours out | budget | extension | error |
|---|---|---|---|---|---|
| 09-10 | PPI (LONDON scan) | 4.3 | 206.2 | 320.8 | **+114.6** |
| 09-16 | FOMC decision | 5.2 | 145.6 | 282.0 | **+136.4** |
| **10-07** | **FOMC Minutes** | **5.2** | **158.9** | **61.1** | **−97.8** |

The threshold (3 event days) is met and **the direction reverses on the third
point**. The candidate change named in the 09-17 entry — a budget multiplier on
event days — would have been fitted to two tail observations; the 09-17 entry
warned of exactly that (*"a multiplier fitted to 3 points that are all
large-positive will fit the tail, not the level — the H1 lesson"*).
**H20 is CLOSED-NEGATIVE: scheduled High-impact events do not systematically
blow the fuel budget. Nothing proposed, and the multiplier branch is closed.**

**And the event did not move this day.** Low 30918.0 at 13:45Z, flip reclaimed
15:35Z; the minutes landed at **18:00Z** with price already **+196 off the low**,
and the 18:00–19:00Z hour ranged **31114.2–31165.6 — 51.4pts**, the quietest hour
of the NY session. `event_gate: None` on a High-impact print is a real gap in the
document, but it is **not** what made this call wrong, and the register should
stop reaching for it first.

## H1 — n=25 (ex-09-24), 4th consecutive entry saying the same thing, and the day count is now shrinking

10-07: budget **158.9**, extension **61.1**, error **−97.8** (0.38x of budget);
traversal 269.5 = **1.70x** budget.

`track.py` raw: per-DAY **+7.9** (n=26), per-scan **+10.4** (n=30). **Corrected
by hand for 09-24:** per-day **+7.62** (n=25); **−15.78** excluding the 09-21
outlier (n=24); **MAE 93.3** against a mean per-day budget of **118.9** — **the
typical error is 78% of the typical budget**, and MAE has risen from 88.9.

Last seven per-day: **−112.2, −75.2, +153.7, +41.7, −66.5, −180.1, −97.8** —
three consecutive negatives, and the two largest over-reads in the record are now
consecutive sessions. **The estimator remains unbiased and the dispersion remains
the entire problem; the multiplier branch should be closed — 7th consecutive
entry saying so.**

**The qualitative text was right again, for the second day running, and still
for no reason.** *"The range has room but not unlimited room. Continuation is
fine to the nearest pool; don't plan on a third leg"* — the range used **38% of
its budget** and there was no third leg. Identical sentence, badly wrong on
10-05. **Unanchored, not consistently wrong**; it must be derived from the number
or dropped.

**See D26** for why the n in this entry is not comparable to the n in the 10-07
entry: 08-24's four rows aged out of the bar window today.

## P-B(b) — 13th session; inflation 1.40x and TWO guaranteed windows, one of which fired

`merge_tol = max(3.0, 472.8 × 0.008) = **3.78**` against `TOUCH_TOL = **8.0**`.
**Two published pairs sit in the structurally-guaranteed 3.78–8.0 window:**
**31232.0 / 31225.8 (6.2pt gap)** — both untouched — and **30979.1 / 30973.1
(6.0pt gap)** — **both touched, on the same M5 bar (187), and graded with
opposite verdicts** (*"held as support 415min"* / *"broke DOWN through it — lost
by 25.6"*). Two readings of one price, disagreeing.

| day | published | touched | distinct | pub rate | distinct rate |
|---|---|---|---|---|---|
| 10-01 | 3 | 2 | 2 | 0.67 | 0.67 |
| 10-02 | 11 | 6 | 3 | 0.55 | 0.27 |
| 10-05 | 18 | 10 | 7 | 0.56 | 0.39 |
| 10-06 | 19 | 3 | 3 | 0.16 | 0.16 |
| **10-07** | **15** | **7** | **5** | **0.47** | **0.33** |

7 touches → 5 distinct bars (179, 187, 206, 211, 263), inflation **1.40x**.
Proposal unchanged: (a) `merge_tol >= TOUCH_TOL`, (b) always report distinct
touch events beside the raw rate.

**Placement note, the mirror of 10-06's.** Rows **above** the scan went **4 of
11 (0.36)**, rows **below** went **3 of 4 (0.75)** — a two-way day, so today's
0.47 is a less distorted reading than 10-06's 0.16. The standing caution (09-21)
still applies: the rate measures placement against the session's shape.

## P-G — instance #15, and the PDL row is the exact mirror of #14's PDH row

Session-extreme and sweep prose chosen by level kind, not by which side price is
on. Three wrong-sided rows:

- **31078.9 PDL + Asia Low (prev-day)**, **+47 ABOVE** the scan price:
  *"Yesterday's low — the biggest pile of stops **below us**. Sweep it, wait for
  a higher low on the 1m, then CISD = **long**."* It is not below us, and the
  sweep had already completed **pre-scan** (5 pre-scan touches; 23 pre-scan bars
  entirely below it). **This is the precise mirror of 10-06's PDH row**, which
  issued a short trigger off a completed upward sweep from 105.7 below. Two
  consecutive sessions, opposite directions, same renderer.
- **31232.0 PD mid + NY Low (prev-day)**, **+200 above**: *"Low of the NY
  session — the next session usually runs the stops **below it**"*.
- **31203.2 Asia Low (today)**, **+172 above**: same string, same
  wrong-sidedness, and the sweep below it had already happened (54 pre-scan bars
  entirely below).

P-G → **15**. Already PROPOSED.

## Session-context field — 9th session, and 12 of 15 rows had already been traded

Already PROPOSED on 09-29 (`tested_today` per `prediction.levels`; grade against
the whole session). Previous instances: 09-17, 09-28, 09-29, 09-30, 10-01, 10-02,
10-05, 10-06. **12 of 15 published rows had been interacted with pre-scan**
(within `TOUCH_TOL`), under the banner *"**New trading day.** … everything below
is fresh"* — **80%, the highest share in the series** (10-06 was 8 of 19 = 42%).

Worst offender: **CALL WALL 31225.8**, published at +194 with *"Heaviest ceiling
this week — desks must SELL as price rises into it, so rallies stall. Take profit
into it"*, had **36 pre-scan touches and 94 of the 179 pre-scan bars entirely
ABOVE it**. The session had spent its first eight hours living above that
ceiling. Also: **30979.1 "London Low (today)" IS the pre-scan low to the point**,
and **31025.8 / 31037.1** carried 20 and 16 pre-scan touches each.

## D23 — 7th residual, and the ±200pt residual survives at 4 of 7

Board offset **+25.8**: NDX reference **31005.9** (cash last traded
2026-10-06T16:14:59, rolled forward by the NQ move **−218.8**) against CFD
**31031.7**, basis `nq_implied`, greeks `repriced_bs_at_current_spot`.
Section 7's own offset **−184.7**, matched to feed time **2026-10-07 11:59Z**.
Gap **210.5**. CFD move 11:59Z → scan (11:55Z M5 bar open **31024.8** → scan
**31031.7**) = **+6.9**. **Residual +203.6.**

Added as a **new data point** to the measured series, **not a re-run of it**:
residuals are now **+190.5 / −201.3 / +203.8 / −7.3 / +2.9 / +246.6 / +203.6**.
**Four of seven sit in 190–250**; the intervening move explains 2 of 7. The 10-02
*"cosmetic"* reading stays reversed and the **measured NEGATIVE result stands**.
First instance where the two offsets have **opposite signs** (+25.8 vs −184.7),
which rules out a shared sign error and leaves a magnitude offset. Damage **none**
— section 7 is research-only and had **no volume** today.

## H22 — n=6, and the label finally VARIED without becoming informative

| day | week net GEX $bn/1% | label | realised range / ADR14 |
|---|---|---|---|
| 09-30 | 0.036 | *"pinning likely"* | 0.84x |
| 10-01 | 5.58 | *"pinning likely"* | 1.33x |
| 10-02 | 9.526 | *"pinning likely"* | 1.09x |
| 10-05 | 0.463 | *"pinning likely"* | 0.86x |
| 10-06 | 9.084 | *"pinning likely"* | 0.63x |
| **10-07** | **−4.447** | ***"expansion likely"*** | **0.79x** |

**The 10-05/10-06 complaint that there is "one label for all five" is now
answered, and it does not help.** The first *"expansion likely"* day in the
series produced **0.79x ADR** — squarely inside the span the five *"pinning
likely"* days produced (0.63x–1.33x), and **below four of them**. The input now
spans −4.447 → +9.526 with no ordering anywhere in it.

**NOTHING PROPOSED, same reason as 10-06 and it is the binding one:** the row
carries **−2 of DIRECTION score** and six *range* observations are not evidence
about direction. The pre-registered test needs no new data — grade
`week net GEX → pinning/expansion` against realised **direction** across the days
already on record. Still the next thing to measure, still not a change.

## Max pain — the FIRST within-reach test since 09-16, and it failed

**30825.8 at −206 = 0.44x ADR14** — inside the ≤0.5 ADR criterion the 09-28 entry
asked for, and the first row to meet it since 09-16. **Never reached; nearest
approach 92.2** (low 30918.0). *"Where the most options expire worthless — price
drifts toward it as the week goes on"* on a **Wednesday**, with the level inside
half an ADR, and price finished **346.8 above it** having turned 92.2 short.

Under the tightened threshold (*"3 days on which max pain is within reach"*):
**2 of 3** (09-16 against, 10-07 against) plus 09-28 ambiguous. The seven
distance-confounded misses (246, 340, 103, 175, 589, 343, 635) stay excluded and
the day-of-week qualifier stays ungradeable until **M6** is decided, because the
reaction verdict is the contaminated variable.

## Dead-weight audit — refreshed to 27 scans, and NFCI broke its duck

| row | scored / 27 | today |
|---|---|---|
| `macro` NFCI | **1 / 27** | **−1** |
| `macro` yield curve 10y–2y | 0 / 27 | +0 |
| `macro` WALCL / RRP | 5 / 27, **0 of the last 22** | +0 |

**`macro` NFCI scored for the first time in the record.** The standing PROPOSAL
to drop all three should therefore be **narrowed to the yield-curve row and
WALCL/RRP**, with NFCI returned to observation. Dropping a row on the one session
it fires is how a model loses a signal it never measured.

Also unscored today and consistent with the audit: `vol` VXN, `vol` VVIX,
`fuel`, `structure` prior-week, `structure` pools, `macro` HY OAS, `news`.
**Not dead today:** `vol` VIX9D/VIX (+1, and it was the only *vol* row pointing
the right way), `rates` DXY (−2), `rates` US10y (−3), `structure` PD mid (−1).

## The gamma component voted against its own location row

Recorded because the register already carries *"Unarbitrated conflict: two gamma
rows vs one vol row"* (09-17) and this is the same shape **inside one component**:

| row | pts | verdict |
|---|---|---|
| `gamma −3` below flip 31114.3 by 82.6 — *"downside accelerates, rallies unstable"* | −3 | wrong post-scan; price reclaimed the flip and closed +58.3 above |
| `gamma −2` week net GEX −4.447 — *"expansion likely"* | −2 | wrong — realised range 0.79x ADR (see H22) |
| `gamma +2` *"bottom 20% of the wall band (31025.8–31225.8) — poor risk/reward for shorts"* | **+2** | **right** — price was 2.9% up a 200pt band, 5.9 above the put wall, and shorts had 107.8pts in them before +254.6 of retracement |

Net **gamma −3**, outvoting the only row that read where price actually was,
5-to-2. **n=1 as a within-component conflict; nothing proposed** — the register's
own rule is that a vote-weighting change needs its own three sessions, and the
three rows measure different things.

## No instance today

- **P-E / P-E(b)** — **no instance, and stated explicitly as directed.** CALL
  WALL **31225.8** was published at **+194** and **never touched post-scan**
  (post-scan high 31187.5, missed by **38.3**), so there is **no intraday
  penetration and no close-side read**; the board named **no shelf brake** on
  either side. The 10-06 closure stands untouched: P-E is a **continuum**, the
  two-mode framing is not resumed, and no mode-discriminator search is reopened.
- **H23** — **no instance**: both paths were flagged *clear*, so no named brake
  existed to test. Record unchanged at **6 sliced / 1 capped, n=7**. One n=1
  observation alongside it: the clear-path sentence advertised *"every options
  shelf from here to 30625.8 (**406pts, 0.86x ADR**) is negative gamma — nothing
  structural to slow a breakdown… If it goes, it has room"* in the **same
  section** as a **158.9pt** range budget — a **2.6x internal disagreement** — and
  the realised downside extension was **61.1**. The D7 note says walls are
  deliberately exempt from the range-budget filter, so this may be by design;
  logged, nothing proposed.
- **H2** — fuel **MODERATE**, not LOW_FUEL/EXHAUSTED. Not the cell. The
  fuel-block / gamma-block conflict therefore has **no instance** either.
- **H4** — **a clean positive, and the cleanest row on the board.** GAMMA FLIP
  **31114.3** was **+82.6** above the scan, reached at **15:35Z**, settled
  **above** from 16:55, held **240min**, closed **+58.3 above**. The row's own
  stated reclaim condition (*"reclaim and hold above and fading becomes valid
  again"*) **fired mid-session** — and nothing in the document re-evaluates the
  −10 or STRATEGY 2 when it does. Needs 5 days; this is a positive observation,
  not a proposal.
- **H8** — straddle **281pts** (ATM IV 16.5%) → EM **±239** → band
  **30793 .. 31270**. Close **31172.6 — INSIDE**. Record **4 inside / 1 outside,
  obs 5 of 10**. VXN-implied daily range **413.4** vs realised **375.0** — VXN
  **over by 38.4** (realised 0.91x), the closest VXN read in the three-day
  comparison. n=3 on the VXN-vs-EM comparison, still no claim.
- **H10** — `structure 0` *"price inside the prior-week range
  (30101.2–31037.1)"*; neither ±3 branch fired, so the **3-for-5** record is
  unchanged and the pre-registered falsification test (next firing at >700pts
  above PWH) was not met. Logged without proposing: price at scan was **5.4 below
  PWH** and closed **+135.5 above** it, and the rule scores a mid-range and an
  edge-of-range position **identically** — a proximity gap distinct from the
  known reclaim gap.
- **H17** — post-scan move **+137.8 = 36.7% of session range**, far above the 5%
  deadband. **No instance**; still 1 of 3 days, both 09-11.
- **H19 / D18 / D20** — 95 headlines → **26 relevant → 0 auto-scored**, coverage
  **0.0%**, the lowest possible and the **second** such day (10-02 was 0.0% of
  47). Neither keyword defect could fire with nothing scored. **The cost is on
  the other side of the ledger today:** the judgement list carried *"10-year
  Treasury note yield hits highest level since 2002 as traders brace for key bond
  sale"* — unambiguous, directly on the day's dominant theme, **uncounted** —
  while a 3-day-old 3bp move in the same instrument was counted **twice** (see
  H18/P1). `news` scored **0** and 26 headlines went unread by the model.
- **D21** — today's firing is the **bottom**-of-band `+2` (*"poor risk/reward for
  shorts"*, price **2.9% up a 200pt band**, **5.9** from the put wall), **not**
  the top-of-band `−2` the census tracks. Outcome: price left the band **downward**
  by 107.8, closed back **inside** at 31172.6, and the row was **right** on the
  post-scan direction. **Deliberately kept out of the `−2` ledger** — merging two
  populations to make a tally read better is the procedure the register forbids.
  Width note, 11th firing: *"bottom 20%"* of a 200pt band is a **40pt** trigger
  window = 0.08x ADR14, against 120pt on 10-06. The window's width swings 3x with
  the wall spacing and nothing normalises it. Unchanged, unproposed.
- **P3 / H6** — one `structural` row published (**31475.8 STRUCTURAL CALL WALL
  ●●●●● 1.35bn**, **+444 = 0.94x ADR14**), untouched. Census → **0 touches on 11
  publications across 10 trading days**, and it **has still never been within
  200pts of price**. Eleventh consecutive null; the recommendation to stop
  publishing it is unchanged.
- **P-C / `events`** — **no `events` row at all** in 22 components, on a day
  carrying a **High-impact FOMC Minutes** release inside its own session. The row
  has now been absent or zero on every session in the record.
- **D24** — `inputs.events_24h` held 4 forward events and the renderer printed all
  four. No instance of the forward-only defect (nothing was released in the
  window behind the scan).
- **D25** — the drift sentence *"**The dominant strike is stable** at 0 across 6
  samples — positioning is settled there"* printed on this scan too, three lines
  below *"No volume has traded yet today"*. Instance appended, **not re-opened
  under a new ID**, as directed. Damage **none** (section 7 is research-only).
- **D7** — the beyond-range footnote again interleaves above- and below-price
  levels in a single price-ordered list (31385 · 31271 · 31260 · 30729 · 30101).
  Convention defect, unchanged, not re-opened.
- **Post-scan vs day-net direction DIVERGED — and this is the third instance.**
  Reported as its own entry (**P-H**, above) rather than folded into the
  scoreboard, as directed. The flag no longer stands at n=2.

## Journal hygiene

No fabricated or backfilled entries; **no `prediction` block touched**. One scan
file for 10-07 (`1250-preny.json` + `.md`), `is_trading_day: true`,
`review_day` reports **0 test artefacts** for the day (`track.py` excludes 6
across the whole record). **09-24 quarantined by hand — eighth consecutive review
to carry it**; the 09-29 proposal for a schema `quarantine` field read by
`track.py` and `review_day.py` is reaffirmed, and the specific cost is now
concrete: `track.py` **prints 09-24 inside every statistic it reports**, so every
figure quoted from it has to be hand-corrected first, and each review repeats the
same arithmetic. **09-09 and 09-25 still have no `REVIEW.md`, and none was
created or back-dated.** 2026-10-08's scan exists (`1248-preny.json`,
`is_trading_day: true`) and is **correctly** held back (179 bars);
**2026-08-24 is held back INCORRECTLY — see D26.**

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01M7sro1DKMp5T7EBDusm6pM

---

# Observations appended 2026-10-09 (grading the 2026-10-08 session)

Source: `review_day.py 2026-10-08 --json`, `track.py`, and the 10-08 scan's own
`.json`/`.md`. Full write-up in `2026-10-08/REVIEW.md`.
Session: O **31184.8** / H **31240.0** / L **30568.7** / C **30791.5**, range
**671.3** (**1.46x** ADR14 460.7), net **−393.3**, 276 bars. One scan (12:48:12Z
PRE_NY, **NEUTRAL / TWO-WAY −1**), **no call** (score inside the ±2 deadband),
12 levels / 10 touched (0.83). Direction graded on the **post-scan** basis per
P-H. 09-24 excluded by hand from every statistic, as directed.

`track.py` no longer prints the literal `actionable: YES/NO`; the field still
exists at `track.py:185` and renders as *"26 of 3 days … threshold met, read the
evidence before proposing"*.

## H1 — ANSWERED NEGATIVE: the budget loses to a constant, measured over 21 days

10-08: budget **115.6**, extension **326.2**, error **+210.6** (**2.82x** of
budget); traversal 576.4 = **4.99x** budget. **The three-day over-read streak did
not extend to four — it reversed**, and +210.6 is the **second-largest under-read
in the record** behind 09-21's +569.2. Last eight per-day: **−112.2, −75.2,
+153.7, +41.7, −66.5, −180.1, −97.8, +210.6**.

`track.py` raw: per-DAY **+16.4** (n=26), per-scan **+17.8** (n=30).
**Hand-corrected for 09-24:** per-day **+16.51** (n=25); **−6.52** ex-09-21
(n=24); **MAE 101.3** against a mean per-day budget of **124.8** — the typical
error is **81% of the typical budget** (78% yesterday).

**The new statistic, and it is the one H1 was opened to produce.** Over the 21
gradeable PRE_NY days (09-24 excluded; 08-24/08-25 aged out, see D26):

| forecast of range extension | MAE |
|---|---|
| **the published budget** | **117.7** |
| constant = sample median extension (128.2) | **92.5** |
| **honest leave-one-out median constant** | **98.0** |
| constant 120.0 | 92.9 |

- **`r(budget, extension) = −0.106`** (+0.175 ex-09-21). The budget carries **no
  information about the quantity it forecasts** and **loses to a constant by
  ~20pts of MAE**.
- `r(adr_used_pct, error) = +0.443` is **definitional**, not a signal: error =
  extension − budget and the budget is a linear function of the pace, hence
  `r(budget, error) = −0.562`. This is the 09-17 one-sided-estimator caveat,
  quantified.
- **The 09-21 rejection of "hot early pace predicts expansion" stands and is
  stronger:** `r(adr_used_pct, extension) = **0.008**` (n=21), −0.242 ex-09-21.
  Recorded again so it is not rediscovered.
- State-conditional means are contaminated by the same one-sidedness and are
  logged only to stop them being mistaken for a finding:
  LOW_FUEL/EXHAUSTED scans **+54.7** (n=17, mean budget 50.6) vs non-low-fuel
  **−34.1** (n=12, mean budget 219.7). The negative error is **floored at
  −budget**. **Do not fit a state-conditional multiplier to this.**
- Also killed before it reached a proposal: *"the three widest days in the record
  (09-21 2.46x, 09-17 1.47x, 10-08 1.46x) were all LOW_FUEL with budgets
  18.7 / 0.0 / 115.6"*. Realised range includes the already-spent portion, which
  is what sets the budget, so range/ADR and budget are mechanically
  anti-correlated. Use **extension**, where the correlation is ~0.

**This is P4, decided by measurement — no new ID was opened** (grepped first;
P4 = *"stop quoting a point-precise budget above zero"*, standing since 09-14,
and H1 is the hypothesis it rests on). **PROPOSED, consolidated:**
(1) stop deriving prose from `remaining_budget` as a forecast — specifically
`_FUEL_MEANING["LOW_FUEL"]`'s *"the range is close to done… favour fades over
chasing breaks"*; (2) if a number must print, print the sample's central value
with its error (median ≈128, MAE ≈98) and label the budget as the accounting
identity it is (`ADR14 − range used`); (3) add the constant baseline to
`track.py` so the skill test re-runs daily instead of being rediscovered.
**Expected effect:** zero change to any direction score (both `fuel` rows score 0
on every scan in the record). **Blast radius to check first:** the `_(stretch)_`
tag, the board's range filter (D7/D15/P-D) and `path_read()`'s reach all read the
same variable. **The multiplier branch stays closed** — this is a baseline
comparison at n=21, not a parameter fitted to a tail.

## The fuel block vs the gamma block — 4th instance, census now 3-1 to gamma, largest margin on record

| day | fuel state | budget | side of flip | extension vs budget | who was right |
|---|---|---|---|---|---|
| 09-14 | LOW_FUEL | 61.9 | BELOW | 194.1 (3.1x) | **gamma** |
| 09-15 | LOW_FUEL | 97.3 | BELOW | 16.0 (0.16x) | **fuel** |
| 09-28 | LOW_FUEL | 65.5 | BELOW | 179.4 (2.7x) | **gamma** |
| **10-08** | **LOW_FUEL** | **115.6** | **BELOW** | **326.2 (2.82x)** | **gamma** |

Regime block: *"Sweeps tend to keep running rather than fail. **Fading is the
wrong trade today**"* + `COHERENT_SHORT`'s *"Today's ADR can be exceeded — don't
cap the target too early"* → **right, 1.46x ADR and a 576.4pt one-way leg**.
Fuel block: *"The range is close to done… favour fades over chasing breaks"* →
**wrong by 2.82x**. The coherence fix (prose only: in short gamma the fuel block
must not recommend fades, or the brief must name which block is live) is
**re-affirmed unchanged** and this is its largest-margin instance.

**Third place in the same document had the right answer too, and it is n=2 now.**
The DOWNSIDE path sentence advertised *"clear… to 30559.6 (398pts, 0.86x ADR)…
If it goes, it has room"* three lines above a **115.6pt** budget — a **3.4x
internal disagreement** — and **the session low was 30568.7, 9.1pts short of the
larger number**. 10-07 was the first instance (2.6x, 406pts vs 158.9); on both
days the clear-path *distance* beat the budget as a forecast of reach. n=2,
logged, not proposed.

## H18 / P1 — instance 15, and today the AGE GATE alone flips the call, the exact reverse of 10-07

| row | pts | its own words |
|---|---|---|
| macro DFII10 2.91% | **+3** | observation **2026-10-06**, *"⚠️ FRED has not published since 2026-10-06 (2 business days ago) — this is last week's reading"* |
| macro DGS10 | **+1** | *"moved 4bp down (2026-10-05 to 2026-10-06)"* — same instrument, same window |
| macro HY OAS 3.03% | 0 | *"−5bp over 5 days"* — **no observation date rendered, 6th consecutive session** |
| rates US10y | **−1** | *"5.316 (+0.74%) — yields up, multiple compression, BEARISH tech"* — live |

**Stale and live pointed OPPOSITE ways and the live row was right** (yields up,
tech −393.3). Census updated: **whenever DFII10 scores non-zero, DGS10 scores the
same sign — 21 of 21**; the live `rates` row agrees with DFII10's sign on **7 of
the 17** days both are non-zero.

**Counterfactuals, computed exactly** (label bands: NEUTRAL is −2..+2,
`expected_direction` fires at |score| ≥ 3):

| variant | score | label | dir | grade |
|---|---|---|---|---|
| as published | **−1** | NEUTRAL / TWO-WAY | 0 | **no call** |
| de-duplicate only (drop DGS10 +1) | −2 | NEUTRAL / TWO-WAY | 0 | no call — **no change** |
| age-gate only (zero the 10-06 DFII10 +3) | −4 | MILDLY BEARISH | −1 | **CORRECT** |
| both | −5 | MILDLY BEARISH | −1 | **CORRECT** |
| gamma block alone | −5 | MILDLY BEARISH | −1 | **CORRECT** |

**This is the mirror image of 10-07**, where de-duplication changed the label and
the age gate changed nothing. Today de-duplication changes nothing and **the age
gate alone converts a no-call into a correct MILDLY BEARISH on the 2nd-widest day
in the record.** Per the standing retraction, **the accuracy case is NOT revived
and nothing is proposed on those grounds** — `HY OAS` still renders no
observation date (**6 sessions**). The cost of that blocker is now explicit: in
two consecutive sessions the age gate has decided the published call, in opposite
directions, and the register may not speak to it. The DFII10 textual sub-defect
**did fire correctly today by luck** (observation Mon 10-06, scan Thu 10-08, so
*"last week's reading"* is true); the string is still unconditional.

## The engine's best signal was outvoted 7-to-5 by rows the day falsified

Recorded as its own entry because it is the whole explanation of the no-call.

| row | pts | verdict on the day |
|---|---|---|
| gamma −3 below flip 31125.1 by 167.2, *"downside accelerates, rallies unstable"* | −3 | **right, and precisely** — rally died 20.0 above the flip, −123.8 in one M5 bar, 576.4 in three hours |
| gamma −2 week net GEX −5.945 → *"expansion likely"* | −2 | **right** — 1.46x ADR14 |
| macro +3 DFII10 (stale, 10-06) | +3 | wrong |
| macro +1 DGS10 (duplicate of the above) | +1 | wrong |
| vol +1 VIX9D/VIX 0.75, *"calm, mean-reversion favoured, mild upward drift"*, *"a calmer, more rangebound day"* | +1 | **wrong on both clauses** |
| breadth +1 *"NDX −0.21% vs ES −0.41% — tech leading, genuine risk appetite"* | +1 | wrong — both legs negative, printed as appetite (D22(a) shape); NDX then fell 1.27% |
| structure +1 *"3 pools above / 2 below — draw higher"* | +1 | **right for 97 minutes** — the upside pools were swept to 31145.1 first, then the day closed 393 lower. The only positive row the day validated at all. |

**Two of the four wrong positives are one stale FRED observation counted twice.**

## The put-wall break marked the day's low for the SECOND consecutive session

| | 10-07 | 10-08 |
|---|---|---|
| PUT WALL | 31025.8 (−6, ●●●●● 1.15bn) | 30709.6 (−248, ●●●●○ 0.65bn) |
| rider | *"if it breaks, expect it to speed UP, not bounce. Don't buy the break."* | identical |
| run-through | **107.8 = 0.23x ADR14**, in 15 min | **140.9 = 0.31x ADR14**, in 25 min |
| then | reclaimed in 70 min, closed **+146.8 above** | reclaimed in ~145 min, closed **+81.9 above** |
| the break was | **the session low** | **the session low** |

Timeline, 10-08: scan 12:48Z at 30957.9 → post-scan high **31145.1 at 14:25Z**
(gamma flip exceeded by 20.0, rejected) → 16:45Z bar **30968.5 → 30844.7
(−123.8)** → first put-wall touch **17:00Z** → low **30568.7 at 17:25Z** → back
above the wall by 19:40Z → close **30791.5**, above the put wall *and* the
structural put wall.

**n=2 on this shape, nothing proposed** — but it is the same wall family, the
same rider, the same outcome, and the two run-through distances (0.23x / 0.31x
ADR) are remarkably close. The missing field is unchanged from 10-07: for each
wall, **the distance it has run through on prior breaks in the same gamma
regime**. The acceleration claim keeps being mechanically right and economically
irrelevant, because it has **no horizon**.

## P3 / H6 — the FIRST structural touch in the record, and the census must be split by side

**STRUCTURAL PUT WALL 30659.6** at **−298 (0.65x ADR14)**: reached 17:20Z,
sliced **90.9**, reclaimed, closed **+131.9 above**. Every prior structural row in
the record was untouched.

| row | publications | touched | ever within 200pts |
|---|---|---|---|
| STRUCTURAL CALL WALL | **12** | **0** | **never** (today +502 = 1.09x ADR) |
| STRUCTURAL PUT WALL | 2 | **1** | yes, today |

**Proposed narrowing:** P3's exclusion of `kind: structural` from the hit-rate
denominator is unaffected, but the stronger *"stop publishing it"* recommendation
should now apply to the **structural CALL wall only**. The put side has one day
of evidence that it is a real, reachable level; dropping it on a census that was
measuring the other side is the mistake the 10-07 NFCI note warned about.

## M6 — session 21, the worst ratio in the record for the second day running, again on the PUT WALL

`SETTLE_TOL = 25.0`; reported `worst_excursion` measured from the settled point,
true excursion measured first touch → close:

| level | verdict | reported | true f.t.→close | ratio | verdict if measured properly |
|---|---|---|---|---|---|
| 31125.1 GAMMA FLIP | *"held as resistance 390min, worst +9.3"* | +9.3 | **+20.0** | 2.15x | held ✓ |
| 31064.0 London High | *"held as resistance 375min, worst +12.2"* | +12.2 | **+81.1** | **6.65x** | **lost** |
| 31037.1 PWH | *"broke UP — lost by 39.1"* | +39.1 | **+108.0** | 2.76x | lost ✓ |
| 31024.6 Asia Low | *"held as resistance 275min, worst +8.8"* | +8.8 | **+120.5** | **13.69x** | **lost** |
| 30979.1 London Low | *"broke UP — lost by 37.6"* | +37.6 | **+166.0** | 4.41x | lost ✓ |
| 30918.0 PDL ⭐ | *"broke UP — lost by 53.8"* | +53.8 | **+53.8** | 1.00x | lost ✓ |
| 30895.1 Equal lows ⭐ | *"broke UP — lost by 76.7"* | +76.7 | **+76.7** | 1.00x | lost ✓ |
| 30839.6 MAX PAIN | *"held as resistance 250min, worst +24.5"* | +24.5 | **+132.2** | **5.40x** | **lost** |
| **30709.6 PUT WALL** | *"held as **support** 75min, worst −9.4"* | **−9.4** | **−140.9** | **14.99x** | **lost** |
| 30659.6 STRUCTURAL PUT WALL | *"broke DOWN — lost by 30.0"* | −30.0 | **−90.9** | 3.03x | lost ✓ |

**8 of 10 understate; 4 of 5 "held" verdicts invert to "lost".** The **14.99x**
beats yesterday's 14.77x and is the worst in the series, and for the second
consecutive session it lands on the most load-bearing row of the day: read cold,
`review_day` says the 0.65bn put wall *held as support for 75 minutes* on a day
it was sliced by **140.9pts = 0.31x ADR14**. Five rows also print *"broke **UP**
through it"* on a day that closed −393.3 — the word is derived from
`settled_side`, not from the side the breach was on (the 10-06 inversion).
**Re-proposed unchanged, 21st session.**

## D26 — second consecutive day of eaten evidence, and a WRONG call left the record

`track.py` printed on 2026-10-09:

> HELD BACK - day not finished (grades after 21:00 UTC on its own date):
>   2026-08-25  98 bars so far
>   2026-10-09  180 bars so far

10-09 is held back **correctly**. **2026-08-25 finished 44 days ago** and is
served partial by `days=min(days_back, 45)`; 08-24 has now left the table
entirely. **Measured damage: two graded scans left the sample, one of them a
WRONG**, so the all-time direction record moved **15 / 9 / 7 → 15 / 8 / 7
(ex-09-24)** while a scan was *added*. **A wrong call was deleted from the record
by the calendar.** Yesterday's damage was H1's n (33 → 30 scans); today's is the
headline scoreboard.

**Free reinforcement for D26(b).** The place to persist graded outcomes already
exists: the schema carries an **`outcome`** block, `journal.py:106` writes it as
`None`, and it is `None` on **60 of 60** scan files in the journal. Nothing has
ever written to it. Proposal unchanged: (a) label aged-out days
*"aged out of the bar window (N bars served)"*, never *"not finished"*;
(b) persist graded per-day outcomes — into the field that is already there.

## H22 — the pre-registered DIRECTION test, run at last, and it is null

The 10-06 and 10-07 entries both said the binding objection is that the row
carries **−2/+2 of direction score** and range observations cannot settle it, and
both said the test *"needs no new data"*. Run now.

Grading `sign(week net GEX)` against **realised post-scan direction** (P-H's
recommended basis) on every gradeable PRE_NY day — 09-24 excluded, 09-17 and
09-25 unusable (no-calls with no recoverable post-scan sign):
**11 right / 8 wrong = 58%, n=19** (p≈0.32 against a coin flip).

Range side, n=7: Spearman(week net GEX, range/ADR14) = **−0.179** — the sign is
the one the row claims, the magnitude is noise. 10-08 extends the table:

| day | week net GEX | label | range / ADR14 |
|---|---|---|---|
| 10-07 | −4.447 | *"expansion likely"* | 0.79x |
| **10-08** | **−5.945** | ***"expansion likely"*** | **1.46x** |

**Counterfactual run before proposing anything:** zeroing the row across all 21
gradeable scans gives **9 right / 4 wrong / 8 no-call** against the published
**11 / 7 / 3** — it converts **3 wrongs and 2 rights** into no-calls, i.e. it
shrinks conviction near the deadband rather than fixing accuracy, and on 10-08
the row was **right**. **NOTHING PROPOSED.** The test the register asked for is
done; the answer is "no information about direction, and removing it is not
obviously an improvement".

## The gamma-vs-vol conflict — 3rd co-occurrence, first in the MIRRORED configuration, and the test as written cannot absorb it

| day | gamma row | vol row | outcome | who was right |
|---|---|---|---|---|
| 09-16 | +2 *"pinning likely"* | −2 *"expect range expansion"* | 1.38x ADR | **vol** |
| 09-17 | +2 *"pinning likely"* | −2 *"expect range expansion"* | extension 40.0 inside | **gamma** |
| **10-08** | **−2 *"expansion likely"*** | **+1 contango, *"a calmer, more rangebound day"*** | **1.46x ADR** | **gamma** |

The signs are **inverted** relative to the first two instances, so the
pre-registered test — *"whether the combination (positive net GEX **and**
backwardated VIX9D/VIX) resolves toward expansion or pinning"* — **cannot be fed
by this day**. Fix the test definition before more data is discarded: record both
values and the realised range every scan regardless of which way round the signs
fall. Also noted: **H21 closed the VIX9D/VIX→*fuel-error* claim; nothing is
watching its *direction* points**, and today they were wrong on both clauses.

## H2 — second counter-instance, and the fade was run over by 326pts

`LOW_FUEL`, budget 115.6, price **18.3% up the pre-scan range** (31240.0–30894.9)
and **63.0 above the pre-scan low**. The fade — long the extreme, expecting no
extension — met **326.2pts of new range**. Record: **3 for the fade (08-24,
08-25, 09-14) / 2 against (09-21, 10-08)**, and both "against" instances are an
order of magnitude larger than any "for". **Caveat preserved:** the engine issued
**no directional call**, so this is evidence about the *fuel* claim, not against
the bias engine. H2's empirical claim remains unproven in both directions.

## Was "NEUTRAL / TWO-WAY" the right description? Partly — it described the path and mis-described the opportunity

Post-scan the day traded **+187.2 above** the scan price (31145.1 at 14:25Z) and
**−389.2 below** it (30568.7 at 17:25Z), so *two-way* is literally what the path
did, and the ±219 straddle band (30739..31177) contained the close. But the
day's **character** was a single 576.4pt expansion out of a failed gamma-flip
test — which is exactly what the regime block, the `COHERENT_SHORT` shape and
both gamma rows said, and exactly what the −1 score denied. **A no-call on a
1.46x-ADR trend day is the most expensive kind of no-call: 671pts of range and no
instruction.** The strategy block did print STRATEGY 2 continuation, so the
document was not silent — the *score* was, and the score is the headline.

## No instance today

- **P-E / P-E(b)** — **no instance, stated explicitly as directed.** CALL WALL
  **31209.6** published at **+252** and **never touched post-scan** (post-scan
  high 31145.1, missed by **64.5**): no intraday penetration, no close-side read,
  and the board named **no shelf brake** on either side. With both walls 248–252
  out on a 116pt budget this was the expected outcome. The 10-06 closure stands:
  P-E is a **continuum**, the two-mode framing is not resumed and no
  discriminator search is reopened. Context worth recording separately: the row
  carried *"desks must SELL as price rises into it, so rallies stall"* with **37
  pre-scan touches and 19 pre-scan bars entirely above it** (open 31184.8,
  overnight high 31240.0).
- **H23** — **no instance**: both paths were flagged *clear*, so no named brake
  existed. Record unchanged at **6 sliced / 1 capped, n=7**. The clear-path
  *distance* observation is logged above with the coherence item (n=2).
- **H20** — **not an instance either way.** `inputs.events_24h` is **empty** and
  the brief printed *"No High/Medium US events in the next 24h"*. H20 stays
  **CLOSED-NEGATIVE** and is not revived.
- **D24** — **unfalsifiable today**: no forward events at all, so the
  forward-only renderer had nothing to hide or reveal.
- **D21** — **no instance.** The band row scored **0** (*"price mid-band
  (30709.6–31209.6), 50% up the range"*); neither the top-of-band −2 nor the
  bottom-of-band +2 branch fired. The `−2` census is unchanged.
- **D25** — the drift sentence *"**The dominant strike is stable** at 0 across 6
  samples — positioning is settled there"* printed again, three lines below
  *"No volume has traded yet today"*. **21st consecutive pre-NY scan.** Instance
  appended, **not re-opened**. Damage none (section 7 is research-only).
- **P-H** — **no 4th instance.** Post-scan **−166.5** and day net **−393.3** agree
  in sign, and the basis cannot matter on a no-call. Stays **n=3**, PROPOSED,
  recommended basis **post-scan**, applied and stated in the review.
- **H17** — post-scan move **−166.5 = 24.8%** of the session range, far above the
  5% deadband, and the scan was a no-call regardless. **No instance**; stays 1 of 3.
- **H4** — **third consecutive clean flip read.** GAMMA FLIP 31125.1 at +167 was
  reached at 14:25Z, exceeded by only **20.0**, never settled above, and the day
  closed **−333.6 below** it after a 576.4pt fall from the test. The row's own
  reclaim condition was tested and **failed**, and the failure was the trade of
  the day. Positive observation, not a proposal.
- **H8** — straddle **258pts** (ATM IV 14.4%) → EM **±219** → band
  **30739 .. 31177**. Close **30791.5 — INSIDE**; both intraday extremes outside,
  exactly as the caveat says. Record **5 inside / 1 outside, obs 6 of 10**.
  **VXN-implied daily range 409.5 vs realised 671.3 — under by 261.8** (realised
  **1.64x** the VXN read), the worst of the four-day comparison.
- **H10** — **did not fire.** `structure 0`, *"price inside the prior-week range
  (30101.2–31037.1)"*. Record unchanged at 3-for-5; the falsification test was not
  met. One line for the proximity gap logged on 10-07: price was **79.2 below
  PWH**, **cleared it by 108.0** intraday and closed **245.6 below** it, and the
  rule scores that identically to a mid-range day.
- **H19 / D18 / D20** — **coverage 1.9%**: 137 headlines → 53 relevant → **1
  auto-scored** (0 bull / 1 bear) → `news` **0**. The one scored headline
  (*"Federal Reserve officials expect another rate hike will be needed this
  year"*, hawkish, ~180pts/90min) was **directionally right on a −393.3 day and
  contributed nothing**, because the magnitude tracks match count. The judgement
  list carried *"Fed's Waller signals further rate hikes as inflation stalls"* —
  same theme, the day's dominant theme, **uncounted** — while a 2-day-old 4bp
  FRED move was counted **twice**. Second consecutive session in that shape.
  Neither keyword defect could fire with one headline scored.
- **P-B(b)** — **14th session.** `merge_tol = max(3.0, 460.7 × 0.008) = **3.69**`
  vs `TOUCH_TOL = **8.0**`; **no published pair falls in the guaranteed window**
  (smallest board gap **12.5**, 31037.1/31024.6), so no double-count fired.
  10 touches → **7 distinct M5 bars** (1, 6, 17, 19, 47, 50, 54), inflation
  **1.43x**. Proposal unchanged. **Placement note:** rows below the scan went
  **5/5**, rows above **5/7** — a genuinely two-way day, so **0.83 is the least
  distorted hit rate in the recent series and is not the board improving**.
- **Session-context field — 10th session.** Previous: 09-17, 09-28, 09-29, 09-30,
  10-01, 10-02, 10-05, 10-06, 10-07. **8 of 12 published rows had been interacted
  with pre-scan** under the banner *"New trading day… everything below is
  fresh"*: CALL WALL 31209.6 (**37** touches, 19 bars entirely above), Asia Low
  31024.6 (30), PWH 31037.1 (27), London Low 30979.1 (18), PDL 30918.0 (13),
  GAMMA FLIP 31125.1 (11), London High 31064.0 (7), Equal lows 30895.1 (3).
  **Costliest instance: the two ⭐ long triggers.** *"Sweep it, wait for a higher
  low on the 1m, then CISD = long"* (PDL 30918.0) and *"3 touches at this price,
  **never traded through** — a real stop cluster. Prime S1 sweep trigger"*
  (30895.1) — the **pre-scan low was 30894.9**, i.e. **23.1 through the PDL** and
  **0.2 through the "never traded through" level**. Both sweeps had already
  completed; both triggers were long, in a document whose top line says S1 fades
  have a materially lower hit rate here; and price ran a further **349.3 / 326.4**
  against them. Already PROPOSED 09-29.
- **P-G — instance #16.** `Asia Low (today) 31024.6`, **+66.7 above** the scan,
  published as *"the next session usually runs the stops **below it**"* — those
  stops had already been run by ~130pts in this same session. A second row,
  `London Low (prev-day) 30979.1` at **+21.2**, carries the same string and falls
  **inside** the ±25pt "sitting on it" band the proposal already specifies.
  Already PROPOSED.
- **H14 — the regime-aware wall note worked again.** Both put rows carried
  *"today the desks are pushing moves along — if it breaks, expect it to speed
  UP, not bounce"* and the break did accelerate (−140.9 in 25 min). The 09-10 fix
  is doing its job; the residual problem is the **missing horizon**, not
  regime-blindness.
- **Max pain — 3rd within-reach test and the FIRST hit.** 30839.6 at **−118.3 =
  0.26x ADR14** (inside the ≤0.5 ADR criterion), reached 16:45Z, and the close
  **30791.5 finished 48.1 below it = 0.10x ADR**. Within-reach record: 09-16
  against, 10-07 against, **10-08 for**; 09-28 ambiguous. It was a **Thursday**,
  the day the row's own qualifier calls strong. The seven distance-confounded
  misses stay excluded and the day-of-week claim stays ungradeable while **M6**
  contaminates the reaction verdict.
- **D23 — 8th residual.** Board offset **+9.6** (NDX reference 30948.3, cash last
  traded 2026-10-07T16:14:59 rolled forward by the NQ move **−211.8**, vs CFD
  30957.9; basis `nq_implied`, greeks `repriced_bs_at_current_spot`). Section 7
  offset **−187.8** at feed time 2026-10-08 11:59Z. Gap **197.4**; CFD move
  (11:55Z bar open **30970.0** → scan **30957.9**) = **−12.1**; **residual
  +209.5**. Series: `+190.5 / −201.3 / +203.8 / −7.3 / +2.9 / +246.6 / +203.6 /
  +209.5` — **five of eight in 190–250**, intervening move explains 2 of 8. The
  measured **negative** result stands. Damage **none** (research-only, no volume).
- **Dead-weight audit — refreshed to 28 scans.** `macro` NFCI **2 / 28** (−1
  again, **second consecutive firing** — the 10-07 decision to return it to
  observation rather than drop it is vindicated); `macro` yield curve 10y–2y
  **0 / 28**; `macro` WALCL/RRP **5 / 28, 0 of the last 23**. The standing
  proposal stays **narrowed to the yield-curve row and WALCL/RRP**. Also unscored
  today: `vol` VXN, `vol` VXN/VIX, `vol` VVIX, `rates` DXY, both `fuel` rows,
  `structure` prior-week, `macro` HY OAS, `news` (×2), `breadth` mega-cap, and
  **`events` absent again — P-C's row has never scored in the record**.
- **No level on the board was noise.** Every row price could reach, it reacted
  at; the only untouched rows are the two that are structurally out of range.

## Journal hygiene

No fabricated or backfilled entries; **no `prediction` block touched**, and no
`REVIEW.md` created for any day lacking a prediction. One scan file for 10-08
(`1248-preny.json` + `.md`), `is_trading_day: true`, `review_day` reports **0
test artefacts** for the day (`track.py` excludes 6 across the record).
**09-24 quarantined by hand — ninth consecutive review to carry it**; the 09-29
proposal for a schema `quarantine` field is reaffirmed, and the cost now
compounds with D26: `track.py` prints 09-24 inside every statistic **and** the
sample it prints them over changes with the calendar, so no quoted figure is
reproducible. **09-09 and 09-25 still have no `REVIEW.md`, and none was created
or back-dated.** 2026-10-09's scan exists (`1249-preny.json`,
`is_trading_day: true`) and is **correctly** held back (180 bars);
**2026-08-25 is held back INCORRECTLY — see D26.** **No new IDs allocated by this
review; next free remains H26 · D27 · P-I.**

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01M7sro1DKMp5T7EBDusm6pM

---

# Observations appended 2026-10-12 (grading the 2026-10-09 session)

Source: `review_day.py 2026-10-09 --json`, `track.py`, the 10-09 scan's own
`.json`/`.md`, and the M5 bar series. Full write-up in `2026-10-09/REVIEW.md`.
Session: O **30799.9** / H **31045.0** / L **30732.4** / C **30906.9**, range
**312.6** (**0.65x** ADR14 484.0), net **+107.0**, 275 bars. One scan (12:49:18Z
PRE_NY, **NEUTRAL / TWO-WAY −2**), **no call** (score inside the ±2 deadband),
16 levels / 7 touched (0.44). Direction graded on the **post-scan** basis per
P-H. 09-24 excluded by hand from every statistic, as directed.

Post-scan: O 30942.2 / H **31001.7** (13:15Z) / L **30772.2** (14:10Z) / C
30906.9; traversal **229.5**; **range extension 0.0** — the whole day's range was
set before the scan.

`track.py` still prints no literal `actionable: YES/NO`; the field at
`track.py:185` renders as *"24 of 3 days … threshold met, read the evidence
before proposing"*.

## H23 — instances 8 and 9, the MECHANISM is now code-certain, and 10-09 is the control the series lacked

Both paths were flagged *has friction* — the first time this week the brief did
not say *"nothing structural to slow it"* — and **both named brakes were
sliced**.

| session | brake | dist | outcome | x ADR |
|---|---|---|---|---|
| 09-30 | 30487.7 upside | +26 | sliced +167.5 | 0.36 |
| 10-01 | 30586.0 downside | −18 | sliced 300.5 | 0.65 |
| 10-01 | 30636.0 upside | +32 | capped at +1.3 | 0.00 |
| 10-02 | 30846.7 downside | −19 | sliced 102.5 | 0.22 |
| 10-02 | 30896.7 upside | +31 | sliced 140.4 | 0.30 |
| 10-05 | 30808.1 upside | +57 | sliced +328.3 | 0.69 |
| 10-06 | 31257.6 upside | +15 | sliced +127.5 | 0.26 |
| **10-09** | **30950.7 upside** | **+14** | **sliced +51.0** | **0.11** |
| **10-09** | **30900.7 downside** | **−36** | **sliced 128.5** | **0.27** |

**Record: 8 sliced / 1 capped, n=9 across 6 sessions.**

**What makes today the control.** On every prior instance there was no way to
show that a *better-chosen* brake would have worked. Today there was: the named
upside brake was the **0.78bn** shelf at +14, and the level **50pts beyond it** —
CALL WALL 31000.7, **2.62bn with a 2.17bn shelf co-located** — capped the move to
**1.0pt** and took the close 93.8 below it. The downside brake 30900.7 was sliced
by 128.5 and the level that actually held was **PD close 30791.5**, a magnet at
−145 (worst excursion −19.3, close +115.4). **In both directions the named brake
was ~3.5x too close and the real brake was heavier structure further out.**

**Mechanism, read from source (`brief.py:486`):**

```
brake = next((p_ for p_ in span if p_["sign"] == "+"), None)
```

`span` is sorted by **distance** (`span.sort(key=lambda p_: (p_["nas100"] - px) * sign)`)
and the selection applies **no size test whatsoever** — it takes the nearest
positive-gamma shelf in the corridor whether it is 0.1bn or 2.6bn. The level
board, by contrast, prints the **top six concentrations by gamma force**. On
10-09 those two rules disagreed on both sides: the named upside brake was the
4th-heaviest thing in its own corridor, and **the named downside brake, 30900.7,
appears nowhere on the level board or in the secondary gamma table — it occurs
exactly once in the entire document, in the fuel section** (`grep` of the brief:
line 105 only). A tradeable instruction at a price the brief never marks.

**PROPOSED** (and this is the one proposal of this review): choose `first_brake`
by **gamma force**, or print both (*"nearest 30950.7 (0.78bn), heaviest 31000.7
(2.62bn)"*); and never name a brake the board does not print. **Expected effect:
zero change to any direction score** — `path_read()` is prose-only and
`bias_engine.py` never imports it (checked); it renders at `brief.py:558` and
`brief.py:1024`, so a fix must cover **both** paths. This supersedes nothing: the
previously-proposed H23 fix (*drop the assertion or print the measured base
rate*) stays on the table and the two are compatible. **No new ID taken** — this
is H23's mechanism.

## P-E — instance 13: the strongest call wall ever published, and on the forward-only convention it CAPPED

CALL WALL **31000.7** at **+64**, *"Heaviest ceiling this week (91k contracts) —
desks must SELL as price rises into it, so rallies stall. Take profit into it…
It is ALSO the 45-day call wall (137k contracts) — defended across expiries, so
it is the strongest ceiling on the board."* **2.62bn with a 2.17bn options shelf
co-located at the same strike** — the largest published on the board in the
record.

**Stating the publication order explicitly, as directed.** The move credited to
the wall **is** post-publication: first post-scan touch **13:05Z**, 16 minutes
after the 12:49:18Z scan. But the **level's own history was not clean**: the wall
had **53 pre-scan touch-bars and 15 pre-scan bars entirely above it**, and the
pre-scan high **31045.0** cleared it by **44.3**.

**Intraday penetration and close-side control separated** (the 10-06 distinction,
applied):

| basis | overshoot | close-side |
|---|---|---|
| full session | **+44.3** (08:45Z, pre-scan) | — |
| **forward-only (the register's convention)** | **+1.0** | **close −93.8**, zero post-scan bars entirely above, 1 post-scan bar with a high above it at all |

On the forward-only convention this is a **cap, and the tightest in the census**:
cap mode moves from 3.6–11.9 to **1.0–11.9**. Census → **5 capped / 1 middle
(10-06, 76.1) / 7 sliced**. Note the full-session figure **+44.3** would have
landed in the 12–103 band, i.e. the thin middle — a second reason not to revive
the two-mode framing.

**New and useful: pre-scan breach does NOT predict the mode.** 10-05's 30858.1
was above-traded in 73 of 178 pre-scan bars and then **sliced by 279.2**; 10-09's
31000.7 was above-traded in 15 of 178 and then **capped at 1.0**. n=2, one each
way. The 10-07 sampling hypothesis (*"pre-scan breach may be the mechanism behind
the empty middle"*) is **not supported** by its own second observation.

**Caveat that must be recorded:** the test and rejection ran **13:05–13:15Z,
before the 13:30Z cash open**. The cap was earned in pre-market; the cash open
bar (13:30Z, O 30939.0) opened 62.7 below the high and the next bar fell to
30849.2. P-E's cap mode has never been checked for session-of-day.

**P-E stays a continuum (closed 10-06).** No two-mode framing, no discriminator
search, nothing new proposed. The existing **prose** proposal is unchanged and is
better supported: the conditional *"a held close above flips that selling to
buying"* was the irrelevant branch today and the unconditional *"rallies stall"*
was right — the reverse of 10-05, four days apart, from identically-worded rows.

## P-E(b) — 13th instance, and a counter-instance: the shelf was sliced, the wall capped

The standalone shelf **30950.7 (0.78bn)** at +14 was **sliced by 51.0** —
**outside** the 22pt band the shelf family has been quoted at (8 of 9 inside 22
as of 10-01). The only shelf that bounded the move, **2.17bn**, is **co-located
with the call wall at 31000.7**, so its +1.0 is indistinguishable from the wall's
and carries **no information independent of it**.

P-E(b) proposes the shelves should replace the call wall's top line. **Today
argues the opposite**, and it is the cleanest test available because both objects
were on the same board 50pts apart: the wall's own strike won. Second
caveat/counter in the series after 09-29. **Nothing proposed; the proposal is not
withdrawn on one day.**

## The regime call was the best thing in the document, and it is graded separately from the no-call

| claim | verdict |
|---|---|
| `gamma +2` *"above flip 30637.6 by 298.7 — long gamma, dips supported, upside grinds"* | **right** — the low stopped **134.6 above** the flip |
| `gamma +2` *"week net GEX 8.896 → pinning likely"* | **right** — 0.65x ADR14 and **zero** post-scan range extension |
| `COHERENT_LONG` high confidence, *"tight, pinned range… breakouts mostly fail"* | **right** — both extremes rejected; close **30906.9** vs PD mid **30904.3**, **+2.6** |
| STRATEGY 1 *"dealers fade extensions, sweeps genuinely fail — this is your fade day"* | **right, and the trade existed**: the 13:05–13:15Z sweep of 30950.7 / 30957.7 / 30995.5 / 31000.7 failed and paid **229.5**; fading 30772.2 paid **134.7** back |
| *"It stops working below 30637.6"* | **untested** — missed by 134.6 |

**First `COHERENT_LONG` after a run of `COHERENT_SHORT`, on a Friday expiry, and
it was correct on all three of regime, range and strategy.** Recorded as a
positive, with the two qualifiers below.

## H7 — the 487.5pt overnight flip move was RIGHT, and the series says such moves are routine

Flip **31125.1 (10-08) → 30637.6 (10-09) = −487.5**; week net GEX **−5.945 →
+8.896 = +14.841bn**; shape **COHERENT_SHORT → COHERENT_LONG**; strategy
**2 → 1**. The new reading was correct (above).

**But the magnitudes are not anomalies.** Consecutive-PRE_NY-scan changes across
the whole journal (29 scans, 28 transitions):

- **Flip:** −487.5 is the **6th largest absolute move of 28**; the median
  absolute overnight flip move is **~265pts**; 13 of 28 exceed 300pts; the record
  is **+811.2** (09-22).
- **Week net GEX:** **+14.841bn is the largest positive swing in the record**, and
  **2nd in absolute terms** behind 09-28's **−16.909bn**. 09-14 was −14.414bn.
- **Shape label:** sign changes on roughly **15 of 28 transitions**.

**H7's instability claim is unaffected.** The flip was not more stable on 10-09 —
it was differently located and happened to be right. And the confirmation
arrived immediately: the **10-12** scan reads **−1.074bn / COHERENT_SHORT**, a
**−9.970bn** reversal, so the *"high confidence"* `COHERENT_LONG` lasted **exactly
one session**. Positive observation on the call, **negative** observation on the
persistence of the label that produced it. Nothing proposed.

## The gamma block was right and outvoted into a no-call — second consecutive session

| block | pts | verdict on 10-09 |
|---|---|---|
| `gamma` | **+4** | **right on regime, range and strategy** |
| `breadth` | **−3** | no content. Mega-caps −1.88% and *"NDX −1.39% vs ES +0.32%"* are the **previous** session's closes; the day then ran ±0.1% net. Wrong on day net (+107.0), nominally right on post-scan (−35.3) at a magnitude indistinguishable from zero |
| `macro` | **−2** | DGS10 −1 off a **1bp** move in a 2-business-day-stale window; NFCI −1 |
| `news` | **−1** | a **September**-dated Fed-hike headline scored on **9 October** (D20) |
| `vol` | **0** | +1 contango *"calmer, more rangebound"* **right**; −1 VXN/VIX 1.45 *"tech-specific stress"* **wrong** — they cancelled |
| `structure` | **0** | +1 above PD mid **right**; −1 *"2 pools above / 3 below → draw lower"* **wrong on net**, right on path |

**On 10-08 this shape cost a 671pt trend day. On 10-09 it cost nothing**, because
the day was genuinely flat — so the no-call was the right label **by cancellation
of two blocks, one of which was right**. **n=2 on "gamma right, outvoted".**
Nothing proposed: the fix would be a weight change, and two sessions is not a
sample. Watched quantity named: **the sign and size of `gamma` minus the sum of
all other blocks, against realised |post-scan move| / ADR.**

## Was "NEUTRAL / TWO-WAY" the right description? Yes — and the no-call was CHEAP, unlike 10-08

Post-scan the day went **+65.4 above** the scan price and **−164.1 below** it and
closed **−35.3**; the ±219 straddle band (30717..31155) contained **every tick of
the session**, not just the close. **Range extension 0.0** — NY added no range at
all to a range set before 08:49 ET. There was no trend to miss, so the cost of the
no-call is **~0**. Stated plainly because the equivalent sentence on 10-08 was the
exact opposite, and the pair is the point: the deadband's cost is **entirely a
function of the day's character**, which is the thing `gamma` had right in both
cases.

## D20 / H19 / D18 — the September headline carried a real point and changed nothing, the exact reverse of 10-08

`news −1` from **one** auto-scored headline: *"PIMCO: Fed Rate Hike in September
and Future Outlook"* — **a September-dated item scored on 9 October**, hawkish,
~180pts / 90min. Coverage **1.7%**: 138 headlines → 58 relevant → **1 scored**
(0 bull / 1 bear), 57 for judgement. Neither D18 keyword defect could fire with
one headline scored.

**Counterfactuals, computed exactly** (bands: NEUTRAL −2..+2;
`expected_direction` fires at |score| ≥ 3):

| variant | score | label | dir | grade |
|---|---|---|---|---|
| as published | **−2** | NEUTRAL / TWO-WAY | 0 | **no call** |
| drop the September `news −1` (D20) | −1 | NEUTRAL / TWO-WAY | 0 | no call — **no change** |
| age-gate only (drop stale `macro DGS10 −1`) | −1 | NEUTRAL / TWO-WAY | 0 | no call — **no change** |
| both | 0 | NEUTRAL / TWO-WAY | 0 | no call — **no change** |
| `gamma` block alone | **+4** | MILDLY BULLISH | +1 | **the basis decides it**: WRONG post-scan (−35.3), CORRECT on day net (+107.0) |
| zero `breadth` | +1 | NEUTRAL / TWO-WAY | 0 | no change |
| zero `breadth` **and** `macro` | +3 | MILDLY BULLISH | +1 | same split as `gamma`-alone |

**No single defective row could move today's label** — it takes deleting an
entire block. This is the mirror of 10-08, where the age gate **alone** converted
a no-call into a correct call. Logged as an instance of D20 firing at zero cost;
**nothing is revived on these grounds.**

## H18 / P1 — instance 16, and the stale pair disagreed with ITSELF on the same 1bp move

| row | pts | its own words |
|---|---|---|
| macro DFII10 2.92% | **0** | observation **2026-10-07**, *"up 1bp as of 2026-10-07 and 1bp over 5 days. ⚠️ FRED has not published since 2026-10-07 (2 business days ago) — this is last week's reading… No change in that reading"* |
| macro DGS10 | **−1** | *"moved 1bp up (2026-10-06 to 2026-10-07). That was driven by real rates"* — same instrument pair, same window |
| macro HY OAS 3.09% | 0 | *"−3bp over 5 days"* — **no observation date rendered, 7th consecutive session** |
| rates US10y 5.236 | **0** | *"(+0.10%) — yields flat"* — live |

**Neither census takes a row today.** The duplication census (*whenever DFII10
scores non-zero, DGS10 scores the same sign — 21 of 21*) is conditioned on
DFII10 ≠ 0, and it was **0**; the stale-vs-live agreement census (7 of 17) needs
both non-zero, and the live row read **flat**. Both stand unchanged.

**New sub-observation, n=1:** the two rows read the **same 1bp move** and
**disagree in sensitivity** — DFII10 calls it *"no change"* and scores **0**,
DGS10 calls it a move and scores **−1**, and DGS10 then attributes it to *"real
rates — the harsher kind"*, i.e. to the series that just said nothing changed.
A 1bp move produced a directional point through one row and silence through the
other.

**The accuracy case stays RETRACTED** and nothing is proposed on those grounds.
The blocker is unchanged and is now **7 sessions** old: `HY OAS` renders **no
observation date at all**, so the age gate cannot be evaluated across the macro
block. Cost today: **zero** — the age gate changed no label (see the table
above). Two days ago it changed the call.

## M6 — session 22, and the mildest instance in a week; the record does not move

`SETTLE_TOL = 25.0`; reported `worst_excursion` measured from the settled point,
true excursion measured first touch → close:

| level | verdict | reported | true f.t.→close | ratio | verdict if measured properly |
|---|---|---|---|---|---|
| 31000.7 CALL WALL | *"held as resistance 485min, worst +1.0"* | +1.0 | **+1.0** | 1.00x | held ✓ |
| 30995.5 Asia High | *"held as resistance 485min, worst +6.2"* | +6.2 | **+6.2** | 1.00x | held ✓ |
| 30957.7 London Low | *"held as resistance 450min, worst +16.5"* | +16.5 | **+44.0** | **2.67x** | **lost** |
| 30950.7 Options shelf | *"held as resistance 450min, worst +23.5"* | +23.5 | **+51.0** | **2.17x** | **lost** |
| 30791.5 PD close | *"held as support 420min, worst −19.3"* | −19.3 | **−19.3** | 1.00x | held ✓ |

**2 of 5 understate; 2 of 4 "held as resistance" verdicts invert to "lost".**
Worst ratio **2.67x** — against 14.99x on 10-08 and 14.77x on 10-07, **this is
the mildest session in the recent series and it does not move the record.** The
reason is visible and worth recording: on a pinned day the settled point and the
first touch nearly coincide, so the defect's magnitude is a function of how far
the day travelled. **It understates most on exactly the days that matter most.**

**Separate wording inversion, same family as the 10-06 instance.** Both
31000.7 and 30995.5 print `first_touch_reaction: "broke DOWN through it"` for a
**rejection from below** — price approached from 30936.3, never settled above
either level, and was turned away. The word is derived from `settled_side`, not
from the side the breach was on. **Re-proposed unchanged, 22nd session.**

## D26 — third consecutive day of eaten evidence, and the worst instance yet: THREE days in one

`track.py` printed on 2026-10-12:

> HELD BACK - day not finished (grades after 21:00 UTC on its own date):
>   2026-08-28  97 bars so far
>   2026-10-12  180 bars so far

10-12 is held back **correctly**. **2026-08-28 finished 45 days ago** and is
served partial by `days=min(days_back, 45)`; **08-26 and 08-27 have left the
table entirely.** Measured damage, with 10-09 *added* on the same run:

| | 10-08 print | 10-12 print |
|---|---|---|
| days / scans | 26 / 30 | **24 / 27** |
| all-time direction | 15 / 9 / 7 (15 / 8 / 7 ex-09-24) | **13 / 6 / 8** (12 / 6 / 8 ex-09-24) |
| H1 per-day n | 26 (25 ex-09-24) | **24 (23 ex-09-24)** |

**Three graded days were deleted by the calendar in a single day, taking three
rights and two wrongs with them.** The headline hit rate moved from 15/23 = 65%
to 12/18 = 67% with no new information. This is the third consecutive session in
which D26 has rewritten the record, and it is now the **largest single-day
sample loss** since the defect was opened.

**D26(b), verified by count rather than assertion:** `outcome` is `None` on
**61 of 61** scan files (`journal.py:106` writes it as `None`; nothing has ever
written to it). Proposal unchanged: (a) label aged-out days *"aged out of the bar
window (N bars served)"*, never *"not finished"*; (b) persist graded per-day
outcomes into the field that already exists. **Appended, not re-opened.**

**Consequence that is now unavoidable and should be read as part of P4 and H22
below:** every n quoted in this register decays daily, so figures computed
yesterday are not reproducible today even with identical code and an unchanged
journal.

## P4 / H1 — n=24 per day; one new data point, and the statistic is NOT re-derived

10-09: budget **171.4**, extension **0.0**, error **−171.4**, traversal **229.5
= 1.34x** budget. A **zero-extension day**, so the error sits exactly at
**−budget**, its arithmetic floor — the maximum over-read this budget could
produce. It is the **2nd-largest over-read in the per-day record** behind 10-06's
−180.1. Last eight per-day: **+41.7, −66.5, −180.1, −97.8, +210.6, −171.4**
(and 09-29 −112.2, 09-30 −75.2 before them). `track.py` raw: per-DAY **+17.7**
(n=24), per-scan **+22.4** (n=27).

**The established finding stands and is not restated as something it is not.**
The budget has **no usable skill**, verified two ways: budget MAE **116.1** vs a
leave-one-out constant **98.3** (n=19), and **90.9** vs **75.5** ex-09-21
(n=18); above/below-mean **sign agreement 9 of 19**. The correlation sign is
**outlier-driven** — **−0.080** across all days, **+0.224** without 09-21 — so
the correct claim is **"no usable skill"**, *not* "inversely predictive", and it
must not be restated as a negative correlation. **H1's multiplier branch stays
closed.** P4 remains the live proposal, unchanged.

**New caveat, from D26 above:** the n=19 / n=18 samples those figures were
computed over **lost three more days today**. The direction of the conclusion is
unaffected — a constant beating the model by ~18pts of MAE does not reverse on
three days — but the figures themselves are no longer reproducible, which is the
third reason on file to persist graded outcomes.

## H22 — the row was RIGHT today, and a new persistence measurement cuts against it anyway

Week net GEX **+8.896** → *"pinning likely"* → realised **0.65x ADR14**, the
**smallest range/ADR in the recent table** and the **first positive-GEX row** in
it. On its own terms the row worked.

| day | week net GEX | label | range / ADR14 |
|---|---|---|---|
| 10-07 | −4.447 | *"expansion likely"* | 0.79x |
| 10-08 | −5.945 | *"expansion likely"* | 1.46x |
| **10-09** | **+8.896** | ***"pinning likely"*** | **0.65x** |

**The direction test's n cannot be extended: D26 shrank its own sample today**
(the 11 right / 8 wrong, n=19 figure was computed over a day set that no longer
exists). Recorded rather than recomputed.

**New, and it is about stability, not accuracy.** Across 28 consecutive-PRE_NY
transitions the sign of week net GEX changes on **roughly 15** of them, and
10-09 → **10-12** reversed by **−9.970bn** back to `COHERENT_SHORT`. So a row
carrying **±2 of direction score** flips sign about every other session while
the 10-08 test showed it orders neither direction nor range. **Still nothing
proposed** — the 10-08 counterfactual stands (zeroing the row converts **3 wrongs
and 2 rights** into no-calls, i.e. shrinks conviction rather than improving
accuracy) and **the row was right today**. This is the argument for re-weighting,
not for deleting, and re-weighting needs a counterfactual nobody has run.

## D23 — 9th residual, and the LARGEST in the series

Board offset **+0.7** (NDX reference 30935.6, cash last traded
2026-10-08T16:14:59 — **994 min** stale — rolled forward by the NQ move
**+209.8**, vs CFD 30936.3; basis `nq_implied`, greeks
`repriced_bs_at_current_spot`). Section 7 offset **+267.5**, matched to feed time
**2026-10-09 11:59Z**. Gap **266.8**; CFD move (11:55Z bar open **31014.9** →
scan **30936.3**) = **−78.6**; **residual +345.4**.

Series: `+190.5 / −201.3 / +203.8 / −7.3 / +2.9 / +246.6 / +203.6 / +209.5 /
**+345.4**` — the intervening move explains **2 of 9**, and five remain in the
190–250 band. **Today is the largest residual recorded and it is the day with the
SMALLEST board offset of the week (0.7)**, which is the cleanest demonstration
yet that the two offsets are not two measurements of one quantity. Extended as a
**new data point**; the measured negative result is **not re-measured**. Damage
**none** — section 7 is research-only and no volume had traded.

## D25 — 22nd consecutive pre-NY scan

*"**The dominant strike is stable** at 0 across 6 samples — positioning is
settled there"* printed three lines below *"⚠️ **No volume has traded yet
today**"*, and with the dominant strike rendered as the literal **0**. Instance
appended, **not re-opened**. Damage none (section 7 is research-only).

## No instance today

- **H20** — **not an instance either way.** `inputs.events_24h` is **None** and
  the brief printed *"No High/Medium US events in the next 24h"*. H20 stays
  **CLOSED-NEGATIVE** and is not revived.
- **D24** — **unfalsifiable**: no forward events at all, so the forward-only
  renderer had nothing to hide or reveal.
- **D21** — **no instance.** The band row scored **0** (*"price mid-band
  (30700.7–31000.7), 79% up the range"*); neither the top-of-band −2 nor the
  bottom-of-band +2 branch fired. Worth one line anyway: **79% up the band is the
  closest the row has come to firing without firing**, and the wall 64pts above
  it then capped the day — so the row that *would* have scored −2 would have been
  right, on a day the published score was a no-call.
- **D22** — **no D22(a) instance**: the legs were genuinely mixed (NDX −1.39% /
  ES +0.32%) and the prose read *"tech lagging, rotation out of tech"*, which is
  the correct shape. The **window** concern is unresolved and unverifiable from
  the journal, which is itself the defect: a −3 breadth block is the largest
  single input to today's score and its measurement window is not recorded.
- **P-H — no 4th deciding instance, but the two bases DISAGREED IN SIGN for the
  first time since the entry opened.** Post-scan **−35.3** vs day net **+107.0**.
  On a no-call the basis cannot decide a verdict, so the census stays **n=3**,
  PROPOSED, recommended basis **post-scan**, applied and stated in the review.
  The `gamma`-block counterfactual above is the worked example of what it would
  have cost: the same scan grades **WRONG** post-scan and **CORRECT** on day net.
- **H17** — post-scan move **−35.3 = 11.3%** of the session range, above the 5%
  deadband, and the scan was a no-call regardless. **No instance**; stays 1 of 3.
  Noted: 35.3pts is **0.11%** of price, which is the kind of move the deadband
  exists for, and the percent-of-range test does not catch it.
- **H4** — **no instance.** GAMMA FLIP 30637.6 at **−299** was never reached
  (post-scan low 30772.2, missed by **134.6**). The row's *"we are ABOVE it, so
  fades work"* branch was correct for the whole session, but that is the regime
  read graded above, not a level read.
- **H8 — observation 7 of 10.** Straddle **258pts** (ATM IV 15.7%) → EM **±219**
  → band **30717 .. 31155**. Close **30906.9 — INSIDE**, and **both intraday
  extremes were also inside** (H 31045.0, L 30732.4) — **the first time in the
  record**, against a caveat that says price *"routinely trades outside it
  intraday"*. Record **6 inside / 1 outside**. **VXN-implied daily range 428.3 vs
  realised 312.6 — over by 115.7** (realised **0.73x**), reversing 10-08's 261.8
  **under**-read: the VXN estimator has now missed by >100pts in both directions
  on consecutive sessions.
- **H10** — **did not fire.** `structure 0`, *"price inside the prior-week range
  (30101.2–31037.1)"*. Record unchanged at 3-for-5. Proximity gap, 3rd
  consecutive session: price was **100.8 below PWH 31037.1**, the pre-scan high
  **cleared it by 7.9**, the day closed **130.2 below** it, and the rule scores
  that identically to a mid-range day.
- **H2** — **no instance.** Fuel was **MODERATE**, not LOW_FUEL/EXHAUSTED, so the
  cell H2 is defined on was not entered. Record unchanged at 3 for / 2 against.
- **H3** — **no instance.** No max-conviction call; the score was −2.
- **P3 / H6 — structural rows absent from the board today**, so the census is
  unchanged (STRUCTURAL CALL WALL 12 publications / 0 touches; STRUCTURAL PUT
  WALL 2 / 1). The 10-08 narrowing — *"stop publishing it"* applies to the
  **call** side only — stands.
- **Max pain — 6th distance-confounded miss, and the qualifier's best day.**
  30200.7 at **−735.6 = 1.52x ADR14**, far outside the ≤0.5 ADR criterion, and it
  was a **Friday** — the day the row's own text calls *"strong by
  Thursday/Friday"*. The within-reach record stays 09-16 against, 10-07 against,
  10-08 for, 09-28 ambiguous. The day-of-week claim remains **ungradeable**, and
  it is now ungradeable on the two days a week it claims to be strongest.
- **P-G — instance #17.** Two *"Low"* rows published **above** the scan carrying
  *"the next session usually runs the stops **below it**"*: `London Low (today)
  30957.7` at **+21.4**, which falls **inside** the ±25pt *"sitting on it"* band
  the proposal already specifies, and `Asia Low (prev-day) 31024.6` at **+88.3**.
  **Unlike #14–#16 the day validated the direction of both claims** (30957.7 was
  lost by 178.5; 31024.6 was never revisited) — so this instance is about the
  prose being **wrong-sided**, not wrong. Already PROPOSED; recorded with that
  distinction so the census is not read as 17 bad calls.
- **Session-context field — 11th session. 11 of 16 published rows had been
  interacted with pre-scan**, under the banner *"New trading day… everything
  below is fresh"*: CALL WALL 31000.7 (**53** touch-bars, **15** bars entirely
  above), Asia High 30995.5 (51, 30 above), PD mid 30904.3 (18), PD close
  30791.5 (18), Asia Low (prev-day) 31024.6 (17), London Low (prev-day) 30894.9
  (16), Options shelf 30950.7 (12), London Low (today) 30957.7 (11), Equal highs
  31038.2 (4), London High (today) 31045.0 (1), Asia Low (today) 30732.4 (1).
  **Costliest instance, and it is the ⭐ row — identical in shape to 10-08's
  30895.1:** *"Equal highs ×2 + PWH ⭐ — 2 touches at this price, **never traded
  through** — a real stop cluster. Prime S1 sweep trigger"* at **31038.2**. The
  **pre-scan high was 31045.0** — the level had been traded through by **6.8pts**
  **four hours before** the board printed, and price never returned to it. Two
  consecutive sessions in which the *"never traded through"* string was false at
  publication. Already PROPOSED 09-29.
- **P-B(b) — 15th session; TWO guaranteed double-count windows and one FIRED.**
  `merge_tol = max(3.0, 484.0 × 0.008) = **3.87**` vs `TOUCH_TOL = **8.0**`.
  Published pairs inside the guaranteed window (gap > 3.87 but < 8.0):
  **31000.7 / 30995.5 (5.2)** and **30957.7 / 30950.7 (7.0)**. The first
  **fired** — both rows first-touched in the **same 13:05Z M5 bar**. 7 touches →
  **5 distinct M5 bars**, inflation **1.40x**. Proposal unchanged. **Placement
  note:** rows above the scan went **4/9**, rows below **3/7** — the 0.44 hit
  rate is low partly because **4 of the 9 untouched rows are levels the session
  had already traded through** and never revisited.
- **Dead-weight audit — refreshed on a stated denominator that does NOT
  reconcile with the register's "28 scans".** On PRE_NY scans with
  `is_trading_day: true`, 09-24 and 10-12 excluded (**n=27**): `macro` yield
  curve 10y–2y **0 / 27 — has never scored in the record**; `vol` VVIX **2 / 27**;
  `rates` DXY **3 / 27**; both `fuel` rows **0 / 27**; `events` **absent on 19 of
  27 and has never scored** (P-C). `macro` NFCI fired **−1 again — 3rd
  consecutive session**, further vindicating the 10-07 decision to return it to
  observation rather than drop it. The standing proposal stays **narrowed to the
  yield-curve row and WALCL/RRP**. **Also unscored today:** `macro` DFII10,
  `macro` HY OAS, `macro` WALCL/RRP, `macro` yield curve, `vol` VXN, `vol` VVIX,
  `rates` US10y, `rates` DXY, both `fuel` rows, `structure` prior-week, the
  second `news` row, and `events` (absent). **The denominator mismatch is itself
  the reproducibility complaint already on file**: `track.py` counts 09-24 inside
  every statistic **and** D26 changes the sample daily, so the register's own
  "N / 28" figures cannot be reconstructed from the journal. That is now a
  recurring cost of the missing `quarantine` field and the missing `outcome`
  persistence, not a one-off.
- **No level on the board was noise** — every row price could reach, it reacted
  at. But of the **9 untouched rows, 4 were not forecasts**: 31045.0, 31038.2,
  31024.6 and 30732.4 had all been traded pre-scan and were never revisited. The
  other 5 were never in play at all — 31145.1 and 31064.0 above the session high,
  the PUT WALL, GAMMA FLIP and MAX PAIN below the session low. The honest reading
  of 0.44 is **placement, not quality** (the standing 09-18 caution).

## Journal hygiene

No fabricated or backfilled entries; **no `prediction` block touched**, and no
`REVIEW.md` created for any day lacking a prediction. One scan file for 10-09
(`1249-preny.json` + `.md`), `is_trading_day: true`, `review_day` reports **0
test artefacts** for the day (6 across the record, excluded by `track.py`).
**09-24 quarantined by hand — 10th consecutive review to carry it**; the 09-29
proposal for a schema `quarantine` field is reaffirmed, and the cost compounds
with D26 exactly as predicted on 10-08: `track.py` prints 09-24 inside every
statistic **and** the sample it prints them over lost **three days** today, so no
quoted figure is reproducible. **09-09 and 09-25 still have no `REVIEW.md`, and
none was created or back-dated.** 2026-10-12's scan exists (`1248-preny.json`,
`is_trading_day: true`) and is **correctly** held back (180 bars);
**2026-08-28 is held back INCORRECTLY — see D26.** **No new IDs allocated by this
review; next free remains H26 · D27 · P-I.**

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01M7sro1DKMp5T7EBDusm6pM

---

# 2026-10-14 review — grading 2026-10-12 (Monday)

_Session O 30919.3 / H 31079.0 / L 30634.7 / C 30669.5 · range 444.3 (1.015x
ADR14 437.9) · net −249.8. One PRE_NY scan at 12:48:38Z / 30843.5, **+2 NEUTRAL /
TWO-WAY**, no call. Post-scan move **−181.3** (P-H basis), traversal 242.7, levels
6 / 17. **There is no 2026-10-13 directory — Tuesday's scan never ran; nothing was
created, back-dated or inferred, and the series skips the day.**_

## The regime call was formally undetermined and right anyway — 1 of 30 in the record

Price **30843.5**, flip **30876.7**, distance **33.2**. Board CFD/index offset
**43.1**. The regime test is a sign test on `price − flip`, and **33.2 < 43.1**:
at a zero basis the same scan reads **9.9 ABOVE** the flip and `bias_engine`
selects **STRATEGY 1 (fade)** instead of STRATEGY 2 — opposite instructions, and
STRATEGY 2 was worth ~180pts. The conversion arithmetic was independently
verified at scan time (Friday cash close 30883.15, NQ roll-forward, front
contract not rolled), so **43.1 is a real CFD-vs-cash basis, not a conversion
fault**.

**Census, all PRE_NY scans carrying both a flip and a board offset (n=30):**
`|px − flip| < |offset|` has occurred **once — 10-12**. Next closest: 09-30
(69.6 vs 37.7), 10-07 (82.6 vs 25.8). Every other scan clears its own conversion
uncertainty by 3x or more.

**Outcome:** the flip was touched at 13:00Z, exceeded by **0.7pts** across 490
minutes with 3 rejected re-tests, and price fell **149.9**. The read was right.
**Recorded as luck, not method** — a sign test whose input uncertainty exceeds
its margin is a coin flip that landed well. **n=1, nothing proposed.**
**Pre-registered test:** at the next occurrence of `|px − flip| < |offset|`,
record whether the regime read was right **before** looking at anything else.

## The put wall printed "at price" — and the day cannot grade its placement

PUT WALL **30843.1** against a price of **30843.5**. At a zero basis the same
strike converts to ≈**30800**, within **1.1pts** of `Equal lows ×3` at
**30798.9**. Both prices produced the same behaviour — chop with a ~24pt adverse
excursion, then a break (worst **+24.1** and **+23.6**). **The session does not
discriminate between the two placements**, and the wall is given no credit for
precision the day did not test.

## Board-offset drift — n=2, below threshold, nothing proposed

| 09-30 | 10-01 | 10-02 | 10-05 | 10-06 | 10-07 | 10-08 | 10-09 | **10-12** | **10-14** |
|---|---|---|---|---|---|---|---|---|---|
| 37.7 | 36.0 | −3.3 | 8.1 | 7.6 | 25.8 | 9.6 | 0.7 | **43.1** | **41.8** |

Two consecutive breaches of the D6 ~40pt line. **n=2, nothing proposed.**
Pre-registered: on a third consecutive >40 offset, measure it against the same
session's cash close before proposing anything.

## H14's open empirical half — ANSWERED at n=3, and the claim FAILS; one proposal

H14's 09-11 fix note left open *"whether a put wall acts as resistance-after-break
in short gamma … 1 session, 4 of 4, needs 2 more sessions"*. They have arrived.

| session | PUT WALL | run-through before any reclaim | x ADR14 | reclaimed same session? |
|---|---|---|---|---|
| 10-07 | 31025.8 (−6) | 107.8 | 0.23 | yes — closed **+146.8 above** |
| 10-08 | 30709.6 (−248) | 140.9 | 0.31 | yes — closed **+81.9 above** |
| **10-12** | **30843.1 (at price)** | **208.4** | **0.48** | **no — closed 173.6 below, never reclaimed** |

**Resistance-after-break: 1 for / 2 against** — and the one "for" (10-12) is a
close-side-derived `settled_read` verdict, i.e. M6-contaminated, so it is the
weakest of the three. **The claim fails.** What *is* stable across the three is
the **run-through distance, 0.23–0.48x ADR**.

**PROPOSED — the one proposal of this review.** `brief.py`'s put-wall rider
currently asserts *"if it breaks, expect it to speed UP, not bounce. Don't buy
the break."* with **no horizon and no base rate**. Print the measured record
beside it: run-through **0.23–0.48x ADR (n=3)**, reclaimed within the session
**2 of 3**. **Expected effect: zero on any score** — the note is prose and
`bias_engine.py` does not read it. Two things change for the reader: the
acceleration claim gains a target, and it stops implying a one-way outcome the
record does not support. This closes the "missing field" named without an ID on
10-07 and again on 10-08. **No new ID — this is H14's own open question.**

## "The gamma block was right and outvoted into a no-call" — n=3, and NOTHING is proposed

| day | `gamma` | all other blocks | `gamma` − rest | published | realised post-scan |
|---|---|---|---|---|---|
| 10-08 | **−5** | +4 | **−9** | NEUTRAL / TWO-WAY | 671pt trend day |
| 10-09 | **+4** | −6 | **+10** | NEUTRAL / TWO-WAY | **−35.3 = 0.07x ADR** |
| **10-12** | **−2** | **+4** | **−6** | NEUTRAL / TWO-WAY | **−181.3 = 0.41x ADR** |

Three consecutive no-calls in which the gamma block had the day's character
right. The quantity pre-registered on 10-09 — *the sign and size of `gamma`
minus the sum of all other blocks, against realised `|post-scan move| / ADR`* —
**does not order the outcome**: |g−rest| is 9, 10, 6 against 1.5x, 0.07x, 0.41x.
The count threshold is met; **the evidence is not**. The fix would be a **weight
change**, which three judgement-coded points cannot support. **Nothing proposed.**
Keep logging the pair exactly as specified.

## `gamma +2` bottom-of-band — 4 firings in the record, 4 of 4 in SHORT gamma, outcome NULL

The branch has fired **four times in 28 PRE_NY scans**, and **every one was below
the flip**:

| day | price | put wall | band | % up band | regime | outcome (post-scan convention) |
|---|---|---|---|---|---|---|
| 08-24 | 29132.8 | 29110.2 | 200pt | 11% | below flip by 276.2 | **WRONG** — closed 82.1 below the scan, day net −277.6 |
| 09-14 | 28830.7 | 28787.8 | 500pt | 9% | below flip by 760.6 | RIGHT — day net +129.3 |
| 10-07 | 31031.7 | 31025.8 | 200pt | 3% | below flip by 82.6 | RIGHT — post-scan +137.8 (wrong on day net −107.5) |
| **10-12** | **30843.5** | **30843.1** | **500pt** | **0.08%** | **below flip by 33.2** | **WRONG — post-scan −181.3, day net −249.8** |

**2 right / 2 wrong — null.** (08-24's bars are outside the 45-day window — D26 —
so its post-scan figure is the close minus the scan price, not `review_day`'s;
both bases are negative, so the verdict does not turn on it.)

**Mechanism, which is the part worth keeping.** The branch can essentially only
fire **near the put wall**, and in a negative-GEX book that is exactly where the
same brief's regime-aware wall note (H14's applied fix) says the floor **will
not hold**. On 10-12 the two printed four lines apart: `gamma +2` *"poor
risk/reward for shorts"* and the wall note *"if it breaks, expect it to speed UP,
not bounce. Don't buy the break."* **The score and the prose of the same component
give opposite instructions, 4 times out of 4.** Count threshold met, evidence
null, **nothing proposed** — recorded as a consistency observation with a
denominator.

This is also the **2nd instance** of *"the gamma component voted against its own
location row"* (opened 10-07 at n=1), and it is the **mirror**: on 10-07 the
location row was right and outvoted 5-to-2; on 10-12 the location row was
**wrong** and, with the **+1** straddle rider, cut the block from **−5 to −2**.
**1-1, nothing proposed.**

## The minimal counterfactual: two rows are the whole margin

Published **+2**. `MILDLY BEARISH` requires ≤ **−3**.

- remove the stale **DFII10 +3** → **−1**, still NEUTRAL
- remove **DFII10 +3 + DGS10 +1** (same observation date) → **−2**, still NEUTRAL
- remove **bottom-of-band +2 + straddle rider +1** → **−1**, still NEUTRAL
- **remove DFII10 +3 and bottom-of-band +2 → −4 → MILDLY BEARISH**, the correct side

**No single row flips the call.** That pair — one FRED series two business days
stale, one regime-blind location row — is the entire margin between a no-call and
a correct directional call on a day that moved 0.41x ADR post-scan.

## D18 — 7th trading day, 13th headline instance, and the clearest negation failure yet

The **sole** auto-scored headline: *"Fed officials want to **hold off** a rate
hike this month. Will this week's inflation data …"* → tagged **[hawkish] 🔴 bear,
"Hawkish repricing → bearish long-duration tech", −1.80, ~180pts / 90min**.
**Holding off a rate hike is dovish.** The scorer matched `rate hike` and never
read `hold off`. That one row **is** the whole `news −1` — and the day fell, so
the defect was **accidentally right-signed**. Logged with that emphasis because a
defect that pays is the hardest kind to retire.

**H19 — coverage 1.85%**: 139 headlines → 54 relevant → **1** scored, 53 left for
judgement.

## H18 / P1 — instance 17, duplication 22 of 22

`macro +3` DFII10 and `macro +1` DGS10 both resolve to observation date
**2026-10-08**, two business days stale, in a document headed *"today"*. The age
warning printed on DFII10 and **not** on DGS10. **HY OAS rendered no observation
date for the 8th consecutive session** (*"3.15% (−9bp over 5 days)"*). The
accuracy case stays **retracted**; the duplication census is now **22 of 22**.

## M6 — session 23, and the day gives the artefact its full scale

All **6** touched rows sit **above** the close (30669.5), so all 6 verdicts were
decided by `bars[-1]["close"]` before any level behaviour was consulted; **5 read
"held as resistance"**.

| level | worst excursion | distance below close | ratio |
|---|---|---|---|
| 30876.7 GAMMA FLIP | +0.7 | 207.2 | 0.003 |
| 30843.1 PUT WALL | +24.1 | 173.6 | 0.139 |
| 30820.8 London Low | +1.7 | 151.3 | 0.011 |
| 30798.9 Equal lows ×3 | +23.6 | 129.4 | 0.182 |
| 30772.2 NY Low prev | +50.3 | 102.7 | 0.490 |
| 30732.4 PDL ⭐ | +20.1 | 62.9 | 0.320 |

Mean ratio **0.19**. **Said explicitly as directed: M6's magnitude scales with
how far the day travelled, and this day travelled 444.3 (1.015x ADR) — so this is
the artefact at full scale, not the muted version a quiet day produces. A low
ratio here would be an understatement, not an improvement.**

The single **"lost"** verdict — **30772.2, *"broke UP through it — lost by
50.3pts"*** — is awarded to a level the day broke **downward** by 137.5 and closed
**102.7 below**. `settled_read` set `settled_side: below`, so the "loss" it
measures is the **retrace upward**. The wording is internally consistent with the
code (`review_day.py:160-162`) and plainly misleading in isolation. **Only the
GAMMA FLIP (+0.7 over 490min, 3 rejected re-tests) is a verdict the close did not
manufacture.**

## H23 — 10th instance, and it is "never reached"; the sub-claim reaches n=2

Named upside brake **30943.1** at +100. Post-scan high **30877.4** — missed by
**65.7**. No slice/cap data point, so the census **stays 8 sliced / 1 capped,
n=9 over 6 sessions**.

What it does add: **30943.1 appears exactly once in the entire document**
(`grep` of the brief: line 108, the fuel section) — **not on the level board, not
in the secondary gamma table**. That is the **2nd instance** of the sub-claim
opened on 10-09 with 30900.7: *a tradeable instruction at a price the brief never
marks*. The standing proposal (`brief.py:486` — choose `first_brake` by gamma
force, or print both; never name a brake the board does not print; render paths
at `:558` **and** `:1024`) is **unchanged and still live**.

**The complement branch was right, and is recorded so H23 is not read as "the
fuel paths are useless":** *"DOWNSIDE path: clear … every shelf to 30643.1 is
negative gamma — nothing structural to slow a breakdown. If it goes, it has room.
Do not fade it."* Price broke the put wall and ran **208.4 (0.48x ADR)**; the
named corridor terminus **30643.1** landed within **8.4pts** of the session low.

## P5 — the secondary gamma table, still graded by no tool, went 2 of 3

All three put-side shelves carried *"dealers are SHORT gamma here, so they
**amplify** … Not a floor"*.

| shelf | force | outcome |
|---|---|---|
| 30743.1 | 0.94bn | **sliced** (worst +9.4 after settling below) |
| 30693.1 | 0.85bn | **sliced** (worst +7.9, 13 re-tests) |
| **30643.1** | **0.70bn** | **NOT sliced — it floored the day.** Session low 30634.7 is **8.4 below** it; settled **above** for 110min, worst **−3.9**, closed **+26.4 above** |

**2 of 3 right, and the one that was wrong is the exact price the fuel section
named as the end of the "clear" corridor.** Both readings are defensible from the
same number, which is the argument for grading this table rather than publishing
it ungraded — **P5, unchanged, n+1.**

## P4 / H1 — n=25 days; the smallest error in the record, and it changes nothing

10-12 error **+6.4** (budget 169.5, extension 175.9) — the **smallest absolute
budget error in the whole 25-day series**. `track.py` per-day mean **+17.3**
(n=25, includes 09-24); **ex-09-24, n=24, +17.5**. **The statistic is NOT
re-derived.** P4's answer stands: MAE **116.1** vs leave-one-out constant **98.3**
(n=19); ex the 09-21 outlier **90.9 vs 75.5** (n=18); sign agreement **9 of 19**;
the correlation sign is outlier-driven (−0.080 all days, +0.224 without 09-21), so
the claim is **"no usable skill"**, **not** "inversely predictive". **H1's
multiplier branch stays closed.** A single bullseye on a question already answered
negative is **noise**, and is logged as noise. Traversal **242.7 = 1.43x** budget —
the standing reminder that the budget forecasts range extension, not travel.

## D26 — reporting bug, NOT data loss; the earlier claim is retracted

`track.py` today reports **25 trading days / 28 scans (deduped)**, window opening
**09-08**. On disk, counted directly:

| | |
|---|---|
| journal day directories | **32** |
| scan JSONs | **62** |
| days with a PRE_NY scan | **27** |
| days with a `REVIEW.md` | **26** |
| days with **both** | **23** |

The hidden August trading days — **08-24 (8 scan JSONs), 08-25 (2), 08-26 (4),
08-27 (5), 08-28 (1) = 20 files** — plus their **5** `REVIEW.md` are **all intact
on disk**. The 45-day bar window hides them from `track.py`; it does not eat
them. **The 10-09-review claim that the P4 sample "no longer exists" is WRONG and
is retracted here.** D26 remains a reporting defect and the gap (25 visible vs 23
fully-graded days on disk, over a 32-directory journal) is now stated explicitly
every review.

## D23 — 10th residual, and the two conversions disagreed in SIGN on the same scan

Board offset **+43.1** (NDX reference 30800.4, cash last traded
2026-10-09T16:14:59 — 3874 min stale — rolled forward by the NQ move **−82.8**,
vs CFD 30843.5; basis `nq_implied`, greeks `repriced_bs_at_current_spot`).
Section 7 offset **−40.7**, matched to feed time **2026-10-12 11:59Z**. Gap
**−83.8**; CFD move (11:55Z bar open **30859.3** → scan **30843.5**) = **−15.8**;
**residual −68.0**.

Series: `+190.5 / −201.3 / +203.8 / −7.3 / +2.9 / +246.6 / +203.6 / +209.5 /
+345.4 / **−68.0**`. Third-smallest |residual| in the series, arriving the day
after the largest — and the 9th (+345.4, 10-09) came on the day with the
**smallest** board offset of the week (0.7). **The two offsets are not two
measurements of one quantity, and today they do not even agree in sign.**
Extended as a **new data point**; the measured negative result is **not
re-measured**. Damage **none** — section 7 is research-only and no volume had
traded.

## D25 — 23rd consecutive pre-NY scan

*"**The dominant strike is stable** at 0 across 6 samples — positioning is
settled there"*, printed three lines below *"⚠️ **No volume has traded yet
today**"*, with the dominant strike rendered as the literal **0**. Instance
appended, **not re-opened**. Damage none.

## Dead-weight audit — refreshed to n=28 PRE_NY `is_trading_day` scans (09-24 excluded by hand)

`macro` yield curve 10y–2y **0 / 28 — has still never scored in the record**;
both `fuel` rows **0 / 28**; `vol` VVIX **2 / 28**; `rates` DXY **3 / 28**;
`events` absent or zero throughout (P-C). The standing proposal stays **narrowed
to the yield-curve row and WALCL/RRP**. `macro` NFCI fired **−1 for the 4th
consecutive graded session** (10-07, 10-08, 10-09, 10-12 — and again on the
ungraded 10-14), which continues to vindicate the 10-07 decision to return it to
observation rather than drop it. **Also unscored today:** HY OAS, WALCL/RRP, the
yield curve, VVIX, US10y, DXY, both fuel rows, the prior-week structure row, the
second `news` row, and `events`.

## No instance today

- **H2** — fuel **MODERATE**, not LOW_FUEL/EXHAUSTED; the cell H2 is defined on
  was not entered. Record unchanged at 3 for / 2 against.
- **H3** — no max-conviction call (score +2). No instance.
- **H7** — no overnight scan. No instance.
- **H10** — did **not** fire: `structure 0`, *"price inside the prior-week range
  (30568.7–31385.1)"*. Record unchanged. **Proximity gap, 4th consecutive
  session:** the session low came within **66.0** of PWL 30568.7 and the rule
  scores that identically to a mid-range day.
- **H17** — no instance (no-call). Post-scan move 181.3 = **40.8%** of the session
  range, far outside the 5% deadband. Stays 1 of 3.
- **H20** — `events_24h` empty, *"No High/Medium US events in the next 24h"*.
  **Stays CLOSED-NEGATIVE and is not revived.**
- **D24** — unfalsifiable: no forward events at all, so the forward-only renderer
  had nothing to hide or reveal.
- **D21** — the **top-of-band −2** branch did not fire. (The **bottom-of-band +2**
  did — graded above under its own census, which the register has not previously
  tracked separately.)
- **D22** — no D22(a) instance in the register's usual sense, but the **window
  complaint stands and cost a point today**: `breadth +1` *"NDX +0.51% vs ES
  +0.02% — tech leading, genuine risk appetite"* is the **previous** session's
  closes, published 41 minutes before a cash open that fell 249.8.
- **P-E / P-E(b)** — **no instance.** CALL WALL **31343.1** published **+500**,
  **466 above the session high**, never in play; the upside shelf 31143.1 the
  same. **P-E is a continuum, not bimodal** — no two-mode framing is attempted and
  no discriminator is sought.
- **P3 / H6** — no structural rows on the board. Census unchanged (STRUCTURAL CALL
  WALL 12 publications / 0 touches; STRUCTURAL PUT WALL 2 / 1).
- **H4** — **3rd consecutive clean flip read, and the best one in the record.**
  Touched 13:00Z, exceeded by **0.7pts** across 490 minutes with 3 rejected
  re-tests, then −149.9. STRATEGY 2 was the right strategy. (Graded separately
  from the no-call, per the 10-09 convention.)
- **H8 — observation 8 of 10.** Straddle **209pts** (ATM IV 8.9%) → EM **±178** →
  band **30666 .. 31021**. Close **30669.5 — INSIDE by 3.5pts**; high 31079.0 and
  low 30634.7 **both outside**. Record **7 inside / 1 outside**. **VXN-implied
  daily range 399.3 vs realised 444.3 — under by 45.0** (realised **1.11x**), the
  smallest of the last three misses (−261.8, +115.7, −45.0).
- **H22 — n=7.** Week net GEX **−1.074**, the **smallest magnitude in the series**,
  carrying *"expansion likely"*; realised range **1.015x ADR**, extension 1.04x
  budget. Mildly expansionary — the weakest reading produced a near-average day.
  **Still no ordering.**
- **Max pain — 7th distance-confounded miss**, **−800.4 = 1.83x ADR14**, the
  largest in the series, and on a **Monday** — the day the row's own text calls
  weak. The day-of-week claim remains **ungradeable**.
- **P-G — instance #18.** Two *"Low"* rows published **above** the scan carrying
  *"the next session usually runs the stops **below it**"*: **Asia Low (today)
  30948.3** at **+105**, and **London Low (prev-day)** merged into the 30958.7 row
  at **+115**. Both were already behind price and neither was revisited. Already
  PROPOSED.
- **Session-context field — 12th session. 11 of 17 published rows had been traded
  before the scan**, under the banner *"New trading day … everything below is
  fresh"*. Touch-bars pre-scan: London High (today) 31004.3 **35**, Asia High
  (prev) 30995.5 **32**, NY High (prev) 30958.7 **32**, PDH 31045.0 **25**, GAMMA
  FLIP 30876.7 **24**, PUT WALL 30843.1 **21**, Asia Low (today) 30948.3 **20**,
  PD mid 30888.7 **17**, London Low (today) 30820.8 **7**, PD close 30906.9 **4**,
  Asia High (today) 31079.0 **3**. **The sharpest form yet: the PUT WALL and the
  GAMMA FLIP — the two objects the entire regime call rests on — had each been
  traded for roughly two hours before the board printed them as forward-looking.**
  Already PROPOSED 09-29.
- **P-B(b) — 16th session; no instance.** `merge_tol = max(3.0, 437.9 × 0.008) =
  **3.50**` vs `TOUCH_TOL = **8.0**`. **No published pair fell in the guaranteed
  double-count window** (gap > 3.50 and < 8.0); the closest was **31004.3 /
  30995.5 at 8.8**, missing it by 0.8. Inflation **1.00x**. Proposal unchanged —
  today is simply a clean board, and that is worth recording as the control.
- **Placement note.** Of the 11 untouched rows, **8 were levels price had already
  traded through before the scan** and never revisited, and **3 were never in play
  at all** (CALL WALL 466 above the session high, PWL missed by 66.0, MAX PAIN
  800 below). **The honest reading of 0.35 is placement, not quality** — the
  standing 09-18 caution. **The one row that is genuinely noise is MAX PAIN**, on
  its 7th consecutive distance-confounded publication.
- **Pre-scan contamination, stated explicitly as directed.** Of the six levels
  that reacted, **three were published after price had already traded them today**
  (GAMMA FLIP 24 touch-bars, PUT WALL 21, London Low today 7) — the reaction
  credited to them is not a clean forward test. **Three are clean** (Equal lows ×3
  30798.9, NY Low prev 30772.2, PDL 30732.4 — all 0 pre-scan touch-bars), as are
  all three secondary shelves.

## Journal hygiene

One scan file for 10-12 (`1248-preny.json` + `.md`), `is_trading_day: true`,
`review_day` reports **0 test artefacts** for the day (6 across the record,
excluded by `track.py`). **09-24 quarantined by hand — 11th consecutive review to
carry it**; there is still no schema `quarantine` field and the 09-29 proposal for
one is reaffirmed, because `track.py` continues to print 09-24 inside every
statistic it reports (its direction line, 13 right / 6 wrong / 9 no-call, becomes
**12 / 6 / 9** once 09-24 is removed). **2026-10-13 has no journal directory — the
scheduled scan never ran. No entry was created, nothing was back-dated, and no
observation was inferred for it; the gap is recorded so the skip from 10-12 to
10-14 is not later mistaken for data.** **09-09 and 09-25 still have no
`REVIEW.md` and none was created.** No `prediction` block was touched. No scoring,
wall or grading code was edited. No fabricated or backfilled entries found.
**No new IDs allocated by this review; next free remains H26 · D27 · P-I.**

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01M7sro1DKMp5T7EBDusm6pM

# Observations appended 2026-10-15 (grading the 2026-10-14 session)

_Session O 30594.0 / H 30688.3 / L 29877.9 / C 29931.8 · range **810.4 (1.88x
ADR14 431.6 — the largest range/ADR in the graded record)** · net −662.2. One
PRE_NY scan at 12:47:54Z / 30406.0, **−18 STRONGLY BEARISH**, `COHERENT_SHORT`
high confidence. Post-scan move **−485.9** (P-H basis) — **CORRECT on both
bases** (day net −662.2), so **no P-H deciding instance; census stays n=3**.
Traversal 578.9, levels 5 / 10. **There is no 2026-10-13 directory — Tuesday's
scan never ran; nothing was created, back-dated or inferred. 2026-10-15 is on
disk but its session is unfinished (`track.py` holds it at 180 bars) and it is
excluded from every statistic below. 09-24 quarantined by hand, 12th
consecutive review._

## H26 (NEW, opened 2026-10-15) — the bias score's MAGNITUDE is a range forecast, not a direction forecast

**Grepped first:** no existing entry asks whether `|score|` orders the outcome.
D16 concerns a rider that enlarges conviction; H3 asks whether to **cap** it;
H17 is a deadband on the direction grade. None of them measures what the
magnitude buys. Taking **H26**; next free is now H27 · D27 · P-I.

Measured over every gradeable PRE_NY day, **09-24 and the unfinished 10-15
excluded, n=22 days**:

| score magnitude | n | correct | wrong | no-call | mean abs(post-scan move)/ADR | mean range/ADR |
|---|---|---|---|---|---|---|
| 0–2 | 7 | — | — | 7 | 0.18 | 1.10 |
| 3–5 | 4 | 2 | 2 | 0 | 0.24 | 0.94 |
| 6–9 | 5 | **5** | 0 | 0 | 0.35 | 1.02 |
| **≥10** | **6** | **3** | **3** | 0 | **0.78** | **1.39** |

- Spearman(|score|, |post-scan move|/ADR) = **+0.594**
- Spearman(|score|, *signed* move in the called direction / ADR) = **+0.221**
- Spearman(|score|, session range/ADR) = +0.190
- **Not a gamma proxy:** Spearman(|week net GEX|, |move|/ADR) = −0.138, and the
  partial rank correlation of |score| with |move| **controlling for |week GEX|**
  is **+0.610**.

Every max-conviction call in the record, on both grading bases:

| day | score | post-scan | day net | abs(move)/ADR | range/ADR |
|---|---|---|---|---|---|
| 09-14 | −11 | WRONG | +129.3 WRONG | 0.99 | 1.37 |
| 09-15 | −12 | CORRECT | −190.8 CORRECT | 0.47 | 0.77 |
| 09-21 | +13 | CORRECT | +847.7 CORRECT | 1.38 | 2.46 |
| 09-23 | +13 | WRONG | −232.3 WRONG | 0.43 | 1.06 |
| 10-07 | −10 | WRONG | −107.5 CORRECT | 0.29 | 0.79 |
| **10-14** | **−18** | **CORRECT** | **−662.2 CORRECT** | **1.13** | **1.88** |

**Hit rate at the extreme end: 3 of 6 post-scan (50%), 4 of 6 on day net, n=6 —
worse than the 6–9 bucket's 5 of 5 and indistinguishable from a coin flip.** The
two largest |score| readings ever printed (+13 on 09-21, −18 on 10-14) produced
the two largest ranges (2.46x, 1.88x ADR) and the two largest post-scan moves
(1.38x, 1.13x ADR) in the record. **−18 is not distinguishable from the −10s on
direction — one observation inside a 50% bucket — and is sharply distinguishable
on magnitude.**

**PROPOSED.** `bias_engine.py:268` saturates the label at ±10, so −18 and −10
print the identical words *"STRONGLY BEARISH"*: the brief's vocabulary discards
the only informative component of the score, and *"STRONGLY"* promises
directional reliability the record does not support. Print the measured base rate
beside the call (for |score| ≥ 10: *direction 3 of 6 in the record; such days have
averaged 1.4x ADR of range*), and let the expected-range language scale with
|score| rather than off the gamma block alone. **Expected effect: zero change to
any score, level, budget or strategy selection** — a label-and-prose change in
section 1. **Evidence: 22 sessions.**

**Consequence for H3 — recommend CLOSED-NEGATIVE, superseded by H26.** 10-14 is
the **5th max-conviction bearish call printed at a session low** (30406.0 sat
51.7 above the pre-scan low 30354.3, **15.5% up the pre-scan range** —
geometrically the same setup as 08-24, 09-14, 10-07) and **the first that was
right**, on both bases, so P-H does not block it. The branch is **1-for-5**. A
cap could not have fixed any of the four misses — it changes the adjective, not
the sign — and it would have suppressed the engine's correct and valuable *range*
call on the two biggest days in the record. (**Census correction:** the H3
bearish list carried *"08-25 13:04"*; the on-disk `2026-08-25/1304-preny.json`
scores **0 / NEUTRAL**, not a max-conviction call. The intended instance is
almost certainly the **08-25 21:56 OVERNIGHT −15**, which the 09-09 decision
removed from regime/strategy grading. The row is wrong as written and should not
be re-quoted.)

## H23 — 11th instance, and the corridor TERMINUS deserves the grading the brake does not

*"UPSIDE: mostly clear. First real brake is 30841.8 (436pts away)"* — **never
reached** (post-scan high 30456.8), so no slice/cap point: the census stays
**8 sliced / 1 capped, n=9 over 7 sessions**, never-reached now 2 (10-12, 10-14).
This instance is a **counter-example to the sub-claim**: 30841.8 is the CALL WALL
and is printed on the board. The **downside** sentence is a sub-claim instance:
*"every shelf to **29941.8** (464pts, 1.08x ADR) is negative gamma — nothing
structural to slow a breakdown"*, and `grep` finds **29941.8 exactly once in the
whole document** (line 107 — not on the board, not in the secondary table).
**Sub-claim n=3.**

**And the terminus was right again:**

| day | budget | realised extension | budget err | corridor terminus | realised extreme | terminus err |
|---|---|---|---|---|---|---|
| 10-07 | 158.9 | 61.1 | 2.6x internal disagreement (register's record, not re-measured) | — | — | — |
| 10-08 | 115.6 | 326.2 | 2.82x | 30559.6 (398pts) | low 30568.7 | **−9.1** |
| 10-12 | 169.5 | 175.9 | 1.04x | 30643.1 (200pts) | low 30634.7 | **+8.4** |
| **10-14** | **97.6** | **476.4** | **4.88x** | **29941.8 (464pts)** | **low 29877.9** | **+63.9** |

Three measured sessions where the terminus landed **within 0.15x ADR of the
session extreme** while the budget on the same page was out by **2.8x–4.9x**,
plus the 10-07 instance already logged. **Checked before reporting:** it is not a
disguised ADR multiple (0.86x / 0.46x / 1.08x of ADR on the three measured days).
**PROPOSED:** emit `corridor_terminus` and its distance to the realised extreme
from `review_day`, and print the terminus as the day's reach estimate beside the
budget instead of burying it in a prose bullet. **Expected effect: zero on any
score** — `path_read()` is prose-only, renders at `brief.py:558` **and** `:1024`.
**No new ID — H23's own corridor branch**, and it cuts the opposite way from the
brake sub-claim.

## Board offset — THE PRE-REGISTERED THIRD-BREACH TEST, RUN, AND THE SELL-OFF HYPOTHESIS IS FALSIFIED

The hypothesis under test: *the futures-implied cash reference is biased low in a
sell-off because futures lead and overshoot, so the offset widens as the market
falls.* **It does not survive the record.**

- **The drift table in the 10-14 review starts at 09-30 and therefore omits
  09-28's 45.9.** The breach series against the D6 ~40pt line is **09-28 45.9 ·
  10-12 43.1 · 10-14 41.8 · 10-15 77.6 — four, not three.**
- **Direction explains a little, magnitude explains nothing.** Across 27 PRE_NY
  days: down-roll days mean offset **+22.7** (median 23.4) vs up-roll days
  **+9.3** (median 8.8); r(offset, roll) = **−0.361**, R² 0.13. **Within the 13
  down-roll days, r(offset, |roll|) = +0.039.** The largest down roll in the
  record, **09-14 NQ −525.5**, produced offset **−12.2** — opposite sign, near the
  bottom of the series. A correction scaled to the overnight move would have
  pushed that conversion the wrong way by tens of points.
- **A time trend dominates:** r(offset, sequence) = **+0.607**, slope **+1.68
  pts/session**, R² 0.37; in a joint fit the roll coefficient halves (−0.034 →
  −0.023) and the trend survives. Staleness is not it either — the October
  breaches sit at the ordinary 992–993 min age (10-12's 3874 is the weekend).
- **The pre-registered test — measure the breach against the same session's cash
  close — is possible on exactly one of the four, and it fails.** NDX cash closed
  **29950.82** on 10-14; the CFD closed **29931.8**; realised CFD-minus-cash basis
  at the close **−19.0**, against a scan-time board offset of **+41.8** — opposite
  sign, gap **60.8**.
- **Extended to the record** (prior-day cash close recovered from each brief's own
  `implied − roll`, paired with that day's CFD close from `review_day`): scan-time
  offset vs same-day realised close basis is **uncorrelated, r = −0.076, n = 20,
  mean |gap| 27.4**. *Caveat: the CFD session close is ~45 min after the 16:15 ET
  cash print, so the realised basis is noisy and this r is attenuated — not noisy
  enough to hide an effect of the size claimed.*

**NOTHING PROPOSED.** The offset is not measuring a CFD-vs-cash basis and it is
not a sell-off effect; tuning the conversion on a 13-point sample with r = +0.04
is the failure this register exists to prevent. The arithmetic was verified
independently on all three October breaches and was correct each time, and there
is no contract roll (NQ and NDX day-over-day agree within ~10pts), so this is not
the 09-24 failure mode. **Damage on 10-14: none** — price was 206.7 below the
flip, **4.9x** the offset. **Pre-registered:** log the realised close basis every
day (free; the NDX close is already fetched for the next morning's roll) and
re-test the trend at n=10 clean observations. `|px − flip| < |offset|` stays
**n=1** (10-12).

## The fuel block vs the gamma block — 5th instance, census now 4-1 to gamma, and the largest margin yet

| day | fuel state | budget | side of flip | extension vs budget | who was right |
|---|---|---|---|---|---|
| 09-14 | LOW_FUEL | 61.9 | BELOW | 194.1 (3.1x) | **gamma** |
| 09-15 | LOW_FUEL | 97.3 | BELOW | 16.0 (0.16x) | fuel |
| 09-28 | LOW_FUEL | 65.5 | BELOW | 179.4 (2.7x) | **gamma** |
| 10-08 | LOW_FUEL | 115.6 | BELOW | 326.2 (2.82x) | **gamma** |
| **10-14** | **LOW_FUEL** | **97.6** | **BELOW** | **476.4 (4.88x)** | **gamma** |

*"The range is close to done … favour **fades** over chasing breaks"* four
sections below *"**Fading is the wrong trade today**"*. **The mechanism is at its
clearest here:** the 77.4% of ADR the budget counted as *spent* was the CPI
reaction (M5 bars 30600.7 at 12:05Z → 30354.3 at 12:40Z, −246 before the document
existed), so the model's response to a hot CPI print was to dampen conviction in
continuation and recommend fades 17 minutes later. The coherence fix (prose only:
in short gamma the fuel block must not recommend fades, or the brief must name
which block is live) is **re-affirmed unchanged**.

## D24 — the worked example it lacked: the day's dominant event was invisible to the events renderer

CPI (3.7%, hot) printed at **12:30Z, 17 minutes before the scan**, and moved the
index 246pts before the brief existed. **Section 5 lists only the six releases
23.7h away and TSM tomorrow**; the CPI appears nowhere in it, and `event_gate` is
**`None`** under a header reading *"The 08:30 ET data lands in here — check the
gate before anything else"*. The gate is forward-only for the same reason the
renderer is. **D24 unchanged and now has its instance.** (This is **not** H20,
which stays **CLOSED-NEGATIVE** — H20 is about *scheduled forward* events blowing
the budget.)

## News — the defect today is MAGNITUDE, not sign, and it belongs to H19

The sole auto-scored headline was correctly matched and correctly signed:
*[cpi_hot] "Inflation was hotter than expected in September, rising to 3.7%"* →
weighted **−2.50**, and `round(−2.50 / 2) = −1` (`news_scorer.py:380`). **One
point out of eighteen for the month's largest macro release** — the same weight a
single bearish keyword match earns on any quiet day — while **three further
headlines describing the same print** sat in `needs_model_judgement` (59 of 60
relevant). **This is H19's established finding (magnitude tracks match count, not
importance), appended as an instance; it is NOT a D18 instance** — today's sign
was right, so **D18 stays at 13 headline instances / 7 trading days**. Damage
none: the call was already −18 and correct.

## The gamma-vs-vol conflict — 4th co-occurrence, mirrored, gamma right by the largest margin

| day | gamma row | vol row | outcome | who was right |
|---|---|---|---|---|
| 09-16 | +2 *"pinning likely"* | −2 *"expect range expansion"* | 1.38x ADR | vol |
| 09-17 | +2 *"pinning likely"* | −2 *"expect range expansion"* | extension 40.0 inside | **gamma** |
| 10-08 | −2 *"expansion likely"* | +1 contango, *"calmer, more rangebound"* | 1.46x ADR | **gamma** |
| **10-14** | **−2 *"expansion likely"*** | **+1 contango, *"calmer, more rangebound day"*** | **1.88x ADR** | **gamma** |

Census **3–1 to gamma**. Also the **2nd instance** of the 10-08 note that nothing
is watching the VIX9D/VIX row's **direction** clause: *"mild upward drift"* on a
−662 day. Recorded; the test definition fix proposed on 10-09 (log both values and
the realised range every scan regardless of sign configuration) is unchanged.

## H18 / P1 — instance 18, duplication 23 of 23

`macro −3` DFII10 and `macro −1` DGS10 both resolve to observation date
**2026-10-09**, three business days stale, in a document headed *"today"*; the age
warning printed on DFII10 and **not** on DGS10. **HY OAS rendered no observation
date for the 9th consecutive session.** The accuracy case stays **retracted** —
the stale pair was right-signed today, and live US10y also read up. Worth stating
once: the heaviest block in the document took **4 of its 5 points from a single
stale observation** while the live driver of the day earned **1**.

## M6 — session 24, and the artefact at its maximum scale

All **5** touched rows sit above the close (29931.8), so all 5 verdicts were
decided by `bars[-1]["close"]`; **3 read "held as resistance"**.

| level | worst excursion | distance below close | ratio |
|---|---|---|---|
| 30423.1 London Low prev | +21.2 | 491.3 | 0.043 |
| 30402.6 Asia Low prev | +41.7 | 470.8 | 0.089 |
| 30386.7 PDL ⭐ | +57.6 | 454.9 | 0.127 |
| 30041.8 PUT WALL | +1.8 | 110.0 | 0.016 |
| 30011.8 MAX PAIN | +21.3 | 80.0 | 0.266 |

Mean ratio **0.108**. **Said explicitly as directed: M6's magnitude scales with
how far the day travelled, and this day travelled 810.4 = 1.88x ADR, the largest
in the record — this is the artefact at maximum scale.** On a far-travelling day
every touched row finishes hundreds of points above the close, so the ratios are
*small by construction*; the low mean is the signature, not an improvement.
**Two "lost" verdicts (30402.6 *"broke UP through it — lost by 41.7pts"*, 30386.7
*"…lost by 57.6pts"*) are awarded for upward retraces on levels the day broke
downward and closed 455–471 below.**

## P4 / H1 — n=26 days; the second-largest error in the record, and it changes nothing

10-14 error **+378.8** (budget 97.6, extension 476.4), second only to 09-21's
+569.2. `track.py` per-day mean **+17.3 → +31.2** (n=26, includes 09-24);
**ex-09-24, n=25, +31.9** (was +17.5) — **one day moved the ex-09-24 mean by
+14.4**. **The statistic is NOT re-derived:** MAE 116.1 vs leave-one-out constant
98.3 (n=19); ex the 09-21 outlier 90.9 vs 75.5 (n=18); sign agreement 9 of 19; the
correlation sign is outlier-driven, so the claim is **"no usable skill"**, not
"inversely predictive". **H1's multiplier branch stays closed.** Traversal
**578.9 = 5.93x** budget. A LOW_FUEL / 97.6pt budget on a 1.88x-ADR day is the
worst calibration instance in the record and answers nothing that was not already
answered.

## Appended without proposal

- **H2 — third counter-instance; record now 3 for the fade / 3 against.**
  LOW_FUEL below the flip, continuation won by 4.88x budget. The three "for"
  instances remain the directionally-contaminated Aug/Sep sample, so the claim is
  unproven in both directions.
- **H14 — run-through census n=4 and the band holds.** PUT WALL 30041.8 broke and
  ran **163.9 = 0.38x ADR** before any reclaim (0.23 / 0.31 / 0.48 / **0.38**);
  **not reclaimed**, closed 110.0 below; two re-tests capped at **+1.8** over
  225 min. Resistance-after-break **2 for / 2 against**, and today's "for" is the
  least close-contaminated of them. The 10-14-review proposal should now print
  *"run-through 0.23–0.48x ADR (n=4), reclaimed within the session 2 of 4"*.
- **H10 — the `−3` branch's FIRST win in five firings (1-for-5).** PWL 30568.7 was
  never reclaimed (never came within 155.9 of it) and the day closed **636.9
  below** it. No reclaim occurred, so the proposed reclaim term would not have
  changed today's call. `+3` branch unchanged at 2-for-4.
- **H22 — n=8.** Week net GEX −4.214 → *"expansion likely"* → **1.88x ADR**: the
  row was right. On the recent five-day table the ordering is now positive
  (Spearman +0.5, n=5); over the full graded sample Spearman(week GEX, range/ADR)
  = **−0.145, n=22**. The 10-08 counterfactual stands. Nothing proposed.
- **H8 — observation 9 of 10, and the worst in the series.** Straddle 326pts
  (ATM IV 21.7%) → EM ±277 → band 30129 .. 30683; **close 29931.8 OUTSIDE by
  197.2**, high outside by 5.3, low outside by 251.1. Record **7 inside / 2
  outside**. **VXN-implied range 404.9 vs realised 810.4 — under by 405.5
  (realised 2.00x), the largest miss recorded.**
- **P5 — the secondary gamma table went 4 of 4 where it was testable.** All six
  shelves carried *"dealers are SHORT gamma here … amplify … Not a floor"*.
  30441.8 (1.41bn, +36) was pierced by the post-scan high; 30341.8 / 30241.8 /
  30191.8 were all sliced; 30541.8 and 30641.8 never reached. No counter-instance.
  **P5 unchanged, n+1 — still graded by no tool.**
- **P-G — instances #19–#21.** Three *"Low"* rows published **above** price with
  *"the next session usually runs the stops below it"*: London Low (today) 30513.4
  at +107, Asia Low (today) 30504.5 at +98, London Low (prev-day) 30423.1 at +17.
  Already PROPOSED.
- **Session-context field — 13th session. 7 of 10 published rows lie inside the
  pre-scan range 30354.3–30688.3** and had therefore already been traded under the
  banner *"New trading day … everything below is fresh"*. **Only 3 rows were clean
  forward objects** (CALL WALL, PUT WALL, MAX PAIN). Already PROPOSED 09-29.
- **The PDL row told the reader to go long on a Strategy-2 day.** `30386.7 PDL +
  NY Low (prev) ⭐`: *"Sweep it, wait for a higher low on the 1m, then CISD =
  long"* — price swept it and fell a further **508.8**. Same shape as 10-12's PDL
  row; the instruction contradicts the document's own STRATEGY 2 header. Logged
  against P-G's family, n=2, nothing proposed separately.
- **Max pain — 2nd within-reach test in the record, 2nd failure.** 30011.8 at
  −394 was reached at 16:20Z on a **Wednesday**, **exceeded by 133.9**, closed
  **80.0 below**. *"Price drifts toward it as the week goes on"* — it drifted
  straight through. The day-of-week claim remains ungradeable.
- **D25 — 24th consecutive pre-NY scan.** *"The dominant strike is **stable** at 0
  across 6 samples"* three lines under *"⚠️ No volume has traded yet today"*.
  Instance appended, not re-opened. Damage none.
- **D23 — 11th residual.** Board offset **+41.8** (NDX reference 30364.2, cash last
  traded 2026-10-13T16:14:59, rolled by NQ −205.2) vs section-7 **+20.1** matched
  to feed time 11:59Z. Gap **+21.7**; CFD move (11:55Z bar open **30549.3** → scan
  30406.0) = **−143.3**; **residual +165.0**. Series: `+190.5 / −201.3 / +203.8 /
  −7.3 / +2.9 / +246.6 / +203.6 / +209.5 / +345.4 / −68.0 / **+165.0**`. The two
  conversions agree in **sign** today, unlike 10-12. Damage none — research-only,
  no volume traded.
- **D26 — reporting gap, NOT data loss; the 10-12 correction stands.** `track.py`
  reports **26 trading days / 29 scans (deduped)**; on disk: **33** day
  directories, **63** scan JSONs, **28** days with a PRE_NY scan, **27** with a
  `REVIEW.md`, **24** with both. The August days remain intact on disk and
  invisible only to the 45-day bar window.
- **Dead-weight audit — refreshed to n=29 PRE_NY `is_trading_day` scans (09-24
  excluded by hand).** `macro` yield curve 10y–2y **0 / 29 — has still never
  scored**; both `fuel` rows **0 / 29**; `vol` VVIX **2 / 29**; `rates` DXY scored
  today (**4 / 29**); `events` absent or zero throughout (P-C). `macro` NFCI fired
  −1 for the **5th consecutive graded session**. The standing proposal stays
  narrowed to the yield-curve row and WALCL/RRP. Also unscored today: the VXN
  level row, HY OAS, WALCL/RRP, both breadth rows, the in-reach-pools structure
  row, the second `news` row, `events`.
- **D22 family — the only rows pointing up were a day old.** `breadth +0` printed
  *"mega-cap avg +0.55% (4/4 up)"* and *"NDX −0.31% vs ES −0.34% — in line"* from
  the **previous** session's closes, 42 minutes before a cash open that fell
  further. Both scored 0, so **damage none**; recorded because the 4/4-green row
  was the single most bullish statement in a −18 document and it described
  yesterday.
- **H17** — no instance; the call was real and correct, post-scan move 485.9 =
  **60%** of the session range, far outside the 5% deadband. Stays 1 of 3.
- **No instance:** **H4** (flip never reached — never came within 155.9), **H7**
  (no overnight scan), **H20** (**stays CLOSED-NEGATIVE and is not revived**),
  **D21** (`gamma +0`, price 46% up the band — neither branch fired), **P-E /
  P-E(b)** (CALL WALL 436 away and 153.5 above the session high; never in play),
  **P3 / H6** (no structural rows on the board), **P-B(b)** (no published pair in
  the guaranteed double-count window).

## Journal hygiene

One scan file for 10-14 (`1247-preny.json` + `.md`), `is_trading_day: true`,
`review_day` reports **0 test artefacts** for the day (6 across the record,
excluded by `track.py`). **09-24 quarantined by hand — 12th consecutive review to
carry it**; there is still no schema `quarantine` field and the 09-29 proposal for
one is reaffirmed, because `track.py` keeps 09-24 inside every statistic it prints
(its direction line, **14 right / 6 wrong / 9 no-call**, becomes **13 / 6 / 9**
once 09-24 is removed). **2026-10-13 has no journal directory — the scheduled scan
never ran; nothing was created, back-dated or inferred, and the gap is recorded so
the skip from 10-12 to 10-14 is not later mistaken for data. 2026-10-15 is on disk
but unfinished and was excluded from every statistic above.** 09-09 and 09-25
still have no `REVIEW.md` and none was created. No `prediction` block was touched.
No scoring, wall or grading code was edited. No fabricated or backfilled entries
found. **One new ID allocated by this review: H26. Next free: H27 · D27 · P-I.**

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01M7sro1DKMp5T7EBDusm6pM

---

# Observations appended 2026-10-16 (grading the 2026-10-15 session)

_Session O 29945.8 / H 29996.8 / L 29423.7 / C 29885.3 · range **573.1 (1.25x
ADR14 457.0)** · net **−60.5**. One PRE_NY scan at 12:47:20Z / 29638.7,
**−7 BEARISH**, `COHERENT_SHORT` high confidence, `EXHAUSTED`, budget **11.5**.
Post-scan move **+283.7 → WRONG** (P-H basis); day net −60.5 → CORRECT, so this
**IS a P-H deciding instance**. Traversal 573.1, levels 2 / 6. **No 2026-10-13
directory — Tuesday's scan never ran; nothing created, back-dated or inferred.**
2026-10-16 is on disk, unfinished (180 bars), excluded from every statistic
below. **09-24 quarantined by hand, 13th consecutive review.**_

**Three corrections before anything is built on this day.** (1) The score is
**−7**, not −6 (`bias_score: -7`; the components sum to −7). (2) **10-15 is not
the most extreme fuel reading in the series** — 97.5% of ADR used ranks 6th
(09-17 136.0 / 09-11 127.2 / 09-24 105.0 / 10-01 100.2 / 09-11 97.7), the 11.5pt
budget ranks 6th smallest (four scans printed 0.0), `fuel_ratio` 2.17 ranks
5th-equal (3.02 / 2.54 / 2.33 / 2.23 / 2.17). (3) **HY OAS scoring −2 on 10-16 is
not a first** — see the dead-weight entry below.

## Board offset — the time trend SURVIVES arithmetically and EXPLAINS NOTHING; the mechanism is unknown

The 10-14 review's figures reproduce **exactly** (r = **+0.607**, slope
**+1.679**/session, R² **0.369**) on the sample it used: **n=27, first scan per
day, ex-09-24 — and already including 10-15's +77.6.** The trend was fitted on
the breach it was being used to explain. Extending the same sample:

| sample | n | r | R² | slope | resid SD |
|---|---|---|---|---|---|
| thru 10-14 | 26 | +0.541 | 0.293 | +1.310 | 15.9 |
| thru 10-15 (the register's figure) | 27 | **+0.607** | 0.369 | +1.679 | 17.8 |
| **thru 10-16** | **28** | **+0.572** | **0.328** | **+1.499** | **18.0** |
| thru 10-16, 10-15 removed | 27 | +0.517 | 0.267 | +1.181 | 15.8 |

**Stated plainly, as directed: the trend survives as a description and fails as
an explanation, and the mechanism is still unexplained.**

- **Out of sample it misses both new points in opposite directions.** Fitted
  through 10-14 it predicts **31.1** for 10-15 (actual **77.6**, residual
  **+46.5**) and **32.4** for 10-16 (actual **14.9**, residual **−17.5**).
- Residual SD **18.0** is larger than the series median offset.
- **As a correction rule it loses to a constant**: last 10 sessions MAE(trend)
  **18.8** vs MAE(constant 11.9) **18.0**.
- One point (10-15) supplies **~27% of the slope**.
- The breach series is **four**: 09-28 **45.9** · 10-12 **43.1** · 10-14 **41.8**
  · 10-15 **77.6** (the 09-28 omission is corrected and stays corrected).

The sell-off hypothesis was falsified on 10-14; staleness is ruled out (992 min,
ordinary); a contract roll is ruled out (NQ and NDX day-over-day agree within
~10pts); and a monotonic drift cannot produce 77.6 followed by 14.9. **We do not
know what causes it. NOTHING PROPOSED, and no third story is substituted.**
**Damage on 10-15: none to the regime** — price sat 987.3 below the flip, 12.7x
the offset — **but total to the structural put wall**, which printed at −11.1
(see below).

## The pre-registered realised-close-basis log — observation 2 of 10, and a scoping fix to the pre-registration

| day | scan offset | NDX cash close | CFD close | realised basis | gap | NQ roll |
|---|---|---|---|---|---|---|
| 10-14 | +41.8 | 29950.82 | 29931.8 | **−19.0** | **60.8** | −205.2 |
| **10-15** | **+77.6** | **29935.6** | **29885.3** | **−50.3** | **128.0** | **−389.8** |

(10-15's cash close is recovered from the 10-16 brief's own arithmetic:
implied 29863.1 − roll (−72.5) = 29935.6.) Both observations have the **same
shape** — a positive scan-time offset against a negative realised basis — and
the gap roughly doubled with the roll. **n=2. NOTHING PROPOSED and nothing may
be.**

**Scoping fix, recorded now so it cannot be invented later to fit:** the
quantity to regress on |roll| is the **gap** (scan offset minus realised close
basis), **not the offset**. The 10-14 review falsified r(offset, |roll|) = +0.039
within down-roll days; that is a different variable and the falsification does
**not** carry over to the gap. Re-test at **n=10 clean observations**.

## H8 — ANSWERED at its pre-registered 10 observations, POSITIVE, and nothing changes

Straddle 504pts (ATM IV 25.0%) → EM ±428 → band **29210 .. 30067**. Close
**29885.3 INSIDE** (high inside by 70.2, low inside by 213.7). **Record 8 inside
/ 2 outside, n=10 — the threshold H8 set for itself.** The claim under test was
*"price closes inside roughly two days in three"*; **80% of 10 cannot be
distinguished from 67%**, so the honest verdict is that the band is **correctly
advertised, possibly conservative**, and is the better-behaved of the two
forward range measures the brief prints: the same page's **VXN-implied range
423.8 under-read the realised 573.1 by 149.3 (realised 1.35x)**. **H8 moves
OBSERVING → ANSWERED-POSITIVE. Keep printing both; change neither.** No proposal
and no ID.

## P-H — 4th deciding instance, and the convention is now worth 12.5 points of headline accuracy

10-15 is the 4th day where the two bases disagree: **09-11, 09-16, 10-07,
10-15** (n=3 → **n=4**). Across the **16 graded calls** — one PRE_NY scan per day, ex-09-24, inside
`track.py`'s 45-day window, a different denominator from `track.py`'s own
scan-level **14 / 7 / 9** line:

| basis | right | wrong | rate |
|---|---|---|---|
| post-scan (P-H) | 10 | 6 | 62.5% |
| day net | 12 | 4 | 75.0% |

**P-H was already PROPOSED on 10-08.** This adds only the evidence that the
unchosen convention now moves the headline number, not merely a verdict. No new
proposal, no ID.

## H26 — 6–9 bucket takes its first miss; magnitude strengthens, direction weakens

|score| = 7 → the **6–9** bucket, which was **5 of 5**. Graded on the P-H
post-scan basis 10-15 is **WRONG**, so the bucket is **5 of 6**. **The ≥10
bucket is unchanged at 3 of 6.** n=22 → **23 days** (09-24 excluded; 10-16
unfinished).

| score magnitude | n | correct | wrong | no-call | mean abs(post-scan)/ADR | mean range/ADR |
|---|---|---|---|---|---|---|
| 0–2 | 7 | — | — | 7 | 0.18 | 1.10 |
| 3–5 | 4 | 2 | 2 | 0 | 0.24 | 0.94 |
| **6–9** | **6** | **5** | **1** | 0 | **0.394** (was 0.35) | **1.057** (was 1.02) |
| ≥10 | 6 | 3 | 3 | 0 | 0.783 | 1.390 |

- Spearman(|score|, |post-scan move|/ADR) **+0.594 → +0.612**
- Spearman(|score|, *signed* move in the called direction/ADR) **+0.221 → +0.165**
- Spearman(|score|, session range/ADR) +0.190 → **+0.196**

**10-15 is the shape H26 predicts:** a −7 delivered **0.62x ADR** of post-scan
movement, well above its bucket mean, **in the wrong direction**. The existing
H26 proposal (print the measured base rate; scale the range language with
|score|; change no score) is unchanged and now rests on 23 sessions.

## H23 — 12th instance: the brake was sliced, and this is the instance that WEAKENS the force-ranking fix

*"DOWNSIDE path: has friction. Expect a stall at **29577.6** (61pts away)"* —
touched 12:55Z, **153.9 points below it within 60 minutes**. Census **9 sliced /
1 capped, n=10 over 8 sessions**; never-reached stays 2.

**The proposed fix would have changed nothing today, and that is the finding.**
`brief.py:486` takes the first positive-sign shelf off a distance-sorted list
with no size test. On 10-15 that shelf carried **3.94bn — the largest gamma-force
figure in the series, off only 5,096 contracts** — and it was the **only**
positive-sign shelf within 1.2x ADR below price, so distance-ranking and
force-ranking had no choice to make between them. **The highest-force brake ever
published was sliced by 2.5x its own distance.** Logged as a counter-instance to
the mechanism behind the ranking proposal, not as support for it.

**Corridor terminus — 4th measured session, and the first on the UPSIDE.**

| day | budget | realised ext. | budget err | corridor terminus | realised extreme | terminus err | terminus / ADR |
|---|---|---|---|---|---|---|---|
| 10-08 | 115.6 | 326.2 | 2.82x | 30559.6 (398) | low 30568.7 | **−9.1** | 0.86x |
| 10-12 | 169.5 | 175.9 | 1.04x | 30643.1 (200) | low 30634.7 | **+8.4** | 0.46x |
| 10-14 | 97.6 | 476.4 | 4.88x | 29941.8 (464) | low 29877.9 | **+63.9** | 1.08x |
| **10-15** | **11.5** | **127.6** | **11.1x** | **29977.6 (339)** | **high 29996.8** | **+19.2** | **0.74x** |

All four inside **0.15x ADR**; the budget on the same four pages was out by
1.0x–11.1x. Still not a disguised ADR multiple. **Already PROPOSED on 10-15; not
re-proposed.**

**The sub-claim takes two counter-instances today** and is now n=3 with 2
against: the named brake **29577.6 is printed in the secondary table** (line
138), and the upside terminus **29977.6 is MAX PAIN on the main board**. The
claim that the corridor sentence names a level found nowhere else in the
document does not generalise.

## The fuel block vs the gamma block — 6th instance, and the census COLUMN and the census CLAIM have come apart

The most explicit instance available: *"Fading the extremes back into the range
is the higher-probability side here, **even when the gamma regime favours
continuation**"* (section 3) against *"**Fading is the wrong trade today** —
Strategy 2 (go with the move) is the right one"* (section 2).

| day | fuel state | budget | side of flip | extension vs budget | who was right (column) |
|---|---|---|---|---|---|
| 09-14 | LOW_FUEL | 61.9 | BELOW | 194.1 (3.1x) | **gamma** |
| 09-15 | LOW_FUEL | 97.3 | BELOW | 16.0 (0.16x) | fuel |
| 09-28 | LOW_FUEL | 65.5 | BELOW | 179.4 (2.7x) | **gamma** |
| 10-08 | LOW_FUEL | 115.6 | BELOW | 326.2 (2.82x) | **gamma** |
| 10-14 | LOW_FUEL | 97.6 | BELOW | 476.4 (4.88x) | **gamma** |
| **10-15** | **EXHAUSTED** | **11.5** | **BELOW** | **127.6 (11.1x)** | **gamma** |

**On the column as written the census is 5–1 to gamma. On what the two
sentences instruct a trader to do, the fuel block won outright today:**

- The pre-scan low 29512.7 was swept by **89.0** at 13:55Z and price reversed
  **+573.1**. Fading that break was the trade of the day; the gamma block's
  *"sweeps tend to keep running rather than fail"* failed.
- The pre-scan high 29958.2 was swept by **38.6** at 19:45Z and price closed
  **111.5 back inside**. Fading that break also won.
- Both of the gamma block's *other* statements were right: *"expect range
  expansion"* (1.25x ADR) and *"trends that persist"* (a 573pt one-way leg).

**This is the first instance where the column and the claim disagree, and it
means the census as printed cannot be cited as evidence for either side.** The
column measures range arithmetic (an H1/P4 quantity); the claim is about trade
selection. **Recorded as a measurement defect in the register, not as a model
change, and no number is taken** — the underlying coherence fix (in short gamma
the fuel block must not recommend fades, or the brief must name which block is
live) is **re-affirmed unchanged**, because today both blocks were half right
and the document still contained two opposite instructions.

## News — right sign on day net, WRONG sign on the grading basis, and six "headlines" are three events

Six auto-scored, raw **−2.55**, `round(−2.55 / 2) = −1` (`news_scorer.py:380`).
**Distinct events: three.**

| event | headlines | direction |
|---|---|---|
| the **10-14** CPI print (3.7%, hot) | *"CPI comes in hot, AI goes cold"*, *"US inflation heats up in September; Fed rate hike this month back on table"*, and *"Warsh Takes IMF Stage as Hot Inflation Spurs Rate Hike Bets"* derives from it | 3 bear |
| **TSMC** record Q profit | 2 headlines, same report | 2 bull |
| **CoreWeave** AI-debt | 1 | 1 bear |

- **Sign:** −1 is **wrong on the P-H post-scan basis** (+283.7) and right on day
  net (−60.5). The row contributed to a call graded WRONG.
- **Size:** 1 point out of 18 — the established **H19** finding that magnitude
  tracks **match count**, not importance. Here match count is inflated on *both*
  sides by duplicate coverage, so the defect partially cancels itself and the
  net is still 1 point.
- **Did cancelling TSMC against CPI lose information? Yes.** The TSMC beat was
  the only **new**, index-weighted, forward-looking item in the set; the CPI
  printed at **12:30Z the previous day**, was already scored in the 10-14 brief,
  and was in the price. The scorer has no way to express *"four headlines, one
  event, already traded"*. This is also the clearest **D20** (freshness) shape in
  the record, though D20's own wording is about a headline naming its weekday,
  so the entry stays below its *"twice more"* bar as written.
- **NOT a D18 instance — every sign was right**, including *"TSMC's CEO sees **no
  sign of a slowdown**"*, a bearish keyword inside a negation that was still
  classified bullish (first-match-wins on *"record profit"* happened to save it).
  **D18 stays at 13 headline instances / 7 trading days.**

## H18 / P1 — instance 19, duplication 24 of 24, and the age gate would have made the WRONG call BIGGER

`macro +3` DFII10 and `macro +1` DGS10 both resolve to observation date
**2026-10-13**, two business days stale, in a document headed *"today"*; the age
warning printed on DFII10 and **not** on DGS10. **HY OAS rendered no observation
date for the 11th consecutive session.**

**The consequence runs against the age-gate proposal.** `macro +4` and
`rates +3` were the only rows pointing up, and the day went up (+283.7
post-scan). Suppressing the stale pair takes the score from **−7 to −11**,
crossing `bias_engine.py:268`'s saturation point into *"STRONGLY BEARISH"* — a
**wrong call made bigger and louder**. That is the **2nd** time the gate would
have hurt (10-07 the first) against 2 where it would have helped. **The accuracy
case stays RETRACTED.**

## M6 — session 25, and the settle window opens AFTER the move it is meant to measure

Both touched rows were decided by `bars[-1]["close"]` (29885.3).

| level | review_day verdict | worst excursion reported | actual excursion | understatement |
|---|---|---|---|---|
| 29627.6 STRUCTURAL PUT WALL | *"broke DOWN through it — lost by 60.4pts"*, `settled_from 14:30` | **−60.4** | **−203.9** (low 29423.7) | **3.4x** |
| 29977.6 MAX PAIN | *"stalled at it — held as resistance 70min"* | −8.5 (travel_up 19.2) | +19.2 above | — |

**The session low was at 13:55 and the settle window opens at 14:30**, so the
breach the verdict is describing is outside the window that measures it.
**Said explicitly as directed: M6's magnitude scales with how far the day
travelled.** 10-15 travelled **573.1 = 1.25x ADR** — mid-scale — and still
produced a 3.4x understatement, which is worse *per unit of travel* than the
0.108 mean-ratio signature recorded at 1.88x ADR on 10-14.

## The structural put wall printed inside its own offset — the day CANNOT grade it

29627.6 at **−11.1** on a **+77.6** board offset: **the level's uncertainty is 7x
its published distance from price.** The only directly observable basis for the
same session is **−50.3**, so the wall's true CFD price could be ~**128pts** from
where it printed. A ±128pt box spans 29500–29756 and price traversed all of it
repeatedly in both directions. **No placement claim is graded and none should be
quoted from this day.** Second instance of a board level printing inside its own
offset (10-12's put wall was the first); **`|px − flip| < |offset|` stays n=1**
(10-12) — today the flip was 987.3 away, 12.7x the offset, so the **regime call
was formally determined and correct**.

For the same reason **P3 / H6's structural census cannot take this day**: it is
the 2nd structural touch in the record and it is ungradeable.

## P4 / H1 — n=27 days; one new data point, and the statistic is NOT re-derived

10-15 error **+116.1** (budget 11.5, extension 127.6). `track.py` per-day mean
**+31.2 → +34.3** (n=27, includes 09-24); **ex-09-24, n=26, +35.1** (was +31.9).
**The statistic is NOT re-derived:** MAE **116.1** vs leave-one-out constant
**98.3** (n=19); ex the 09-21 outlier **90.9** vs **75.5** (n=18); sign agreement
9 of 19. The claim is **"no usable skill"**, **not** "inversely predictive".
**H1's multiplier branch stays closed.** Traversal **573.1 = 49.83x** budget is
the largest finite traversal/budget ratio in the record and is a property of the
11.5pt denominator, not new information.

## P5 — the secondary gamma table's worst session on record, 2 of 6, and still graded by no tool

First post-scan touch (±8pt), then the next 60 minutes:

| shelf | force | printed claim | next 60 min | verdict |
|---|---|---|---|---|
| 29577.6 | 3.94bn | LONG gamma, *"damp… stall and dip-buying… acts as **support**"* | **−153.9** / +81.1, from above | **WRONG** |
| 29477.6 | 0.59bn | *"amplify… accelerate THROUGH… **Not a floor**"* | from above, only **−53.9** further (the session low) then **+193.4** | **WRONG — it was the floor** |
| 29827.6 | 0.72bn | *"accelerate THROUGH… not a floor"* | from below **+33.5** then **−80.4** | **WRONG — it stalled the rally** |
| 29877.6 | 1.11bn | *"accelerate THROUGH… not a floor"* | from below **+21.8** then **−134.3** | **WRONG — it capped** |
| 29677.6 | 0.88bn | *"accelerate THROUGH"* | from below **+157.1** | right |
| 29727.6 | 0.60bn | *"accelerate THROUGH"* | from below **+133.5** | right |

**Caveat stated before the number is used:** on a day with one 573pt directional
leg every shelf in the path is sliced almost by construction, so the two "right"
verdicts are nearly free. The informative rows are the three where price
**turned** — 29477.6, 29827.6, 29877.6 — and all three did the opposite of their
printed note. **P5 unchanged, n+1 — still graded by no tool.**

## Dead-weight audit — refreshed to n=31 PRE_NY `is_trading_day` scans (09-24 excluded by hand), and TWO standing claims corrected

| row | scored / present |
|---|---|
| `macro` Yield curve 10y–2y | **0 / 31 — has still never scored** |
| `fuel` ratio row | 0 / 31 |
| `fuel` conviction row | 0 / 18 |
| `events` | 0 / 15 (absent on the rest) |
| `vol` VVIX | 2 / 31 |
| `rates` DXY | 4 / 31 |
| `macro` NFCI | 5 / 31 |
| `macro` WALCL/RRP | 6 / 31 |
| `macro` HY OAS | **25 / 31** |

- **CORRECTION — HY OAS is not dead weight, and 10-16's −2 is not a first.** Full
  history: **+2 on 19 consecutive scans (08-24 → 09-28)**, **−2 on six (09-29 →
  10-06)**, **0 on six (10-07 → 10-15)**, **−2 again on 10-16** (3.25%, +16bp,
  *"widening — the bond market is getting nervous"*). What is real is that the
  row has printed **no observation date for 11 consecutive sessions**: that is an
  **H18/P1 rendering** item, **not** a dead-weight item, and it does **not**
  unblock H18/P1's retracted accuracy case — a row that scores on 81% of scans
  and carries no date is a *larger* freshness exposure, not evidence either way.
- **CORRECTION — NFCI's run ended.** It fired −1 on five consecutive scans
  (10-07 → 10-14) and scored **0 on both 10-15 and 10-16**. The 10-15 review's
  "5th consecutive graded session" was the last of the run.
- The standing narrowed proposal (drop the yield-curve row and WALCL/RRP) is
  **unchanged and still not actioned**.

## Appended without proposal

- **H2 — 4th counter-instance on the budget, and the 1st clean instance FOR the
  fade, on the same day.** EXHAUSTED below the flip: the range grew **11.1x** the
  budget (budget wrong) while fading **both** extremes won (+573.1 and +111.5).
  The two halves of H2 point opposite ways on one session; the claim stays
  unproven in both directions.
- **H10 — the `−3` branch's 6th firing, 1-for-6 on the post-scan basis.** PWL
  30568.7 was never approached within **571.3**, so no reclaim occurred and
  **the proposed reclaim term would not have changed today's call** — the same
  null as 10-14. `+3` branch unchanged at 2-for-4.
- **H22 — n=9.** Week net GEX −7.466 → *"expansion likely"* → **1.25x ADR**: the
  row was right. Nothing proposed.
- **H17 — no instance.** Post-scan move 283.7 = **49.5%** of the session range,
  far outside the 5% deadband. Stays 1 of 3.
- **H14 — no gradeable instance.** The only put-side break was the structural
  wall, which is ungradeable on placement (above); the PUT WALL 29377.6 was
  **missed by 46.1** on the session low and never broke. Run-through census
  stays n=4.
- **Max pain — 3rd within-reach test and the FIRST success, on a Thursday.**
  29977.6 at +339 was reached at 19:25Z, **exceeded by only 19.2**, held as
  resistance 70 min, closed **92.3 below**. It capped the day. The day-of-week
  qualifier (*"weak on a Monday, strong by Thursday/Friday"*) has **n=1** on
  Thursday against 2 Wednesday failures (09-16, 10-14). **Nothing proposed.**
- **P-E — no instance.** CALL WALL 30077.6 (+439) was **missed by 80.8** and
  never in play. Worth recording that it was **●●○○○ 0.38bn / 3k contracts** —
  near-vestigial — and the day's actual cap was MAX PAIN, which the board does
  not describe as a ceiling.
- **D22 — FIRST damage instance.** `breadth −2` (*"mega-cap avg −1.89%: NVDA
  −3.16%, AVGO −3.10%"*) and `breadth −1` (*"NDX −2.02% vs ES −0.37%"*) are
  **10-14 closes**, printed 43 min before a cash open the index then rallied
  573.1 off. **3 of the 7 net points described the previous session.** Not
  decisive on its own: the label threshold is −3, so removing breadth leaves −4
  (still BEARISH, still direction −1), and removing breadth **and** news leaves
  −3 (still a call). **Five of the fourteen bearish points must go before the
  call becomes a no-call — no open defect is worth five.**
- **D23 — 12th residual, and the largest in the series.** Board **+77.6** vs
  section-7 **−346.8** matched to feed time 11:59Z. Gap **+424.4**; CFD move
  (11:55Z bar open **29652.5** → scan **29638.7**) = **−13.8**; **residual
  +438.2**. Series: `+190.5 / −201.3 / +203.8 / −7.3 / +2.9 / +246.6 / +203.6 /
  +209.5 / +345.4 / −68.0 / +165.0 / **+438.2**`. The two conversions disagree in
  **sign**, as on 10-12. Damage none — research-only, no volume had traded.
- **D25 — 25th consecutive pre-NY scan.** *"The dominant strike is **stable** at
  0 across 6 samples"* three lines under *"⚠️ No volume has traded yet today"*.
  Instance appended, not re-opened. Damage none.
- **D24 — no instance.** TSM's pre-market earnings **were** listed in section 5
  and no release fell between the day's open and the scan; `event_gate: null` is
  correct here.
- **D17 — SUCCESS, logged as a success.** The 2026-10-16 scan hit a CBOE **429**
  and the retry recovered on **attempt 1 of 3**.
- **D26 — reporting gap, NOT data loss; the 10-12 correction stands.**
  `track.py` reports **27 trading days / 30 scans (deduped)**; on disk: **34** day
  directories, **64** scan JSONs, **29** days with a PRE_NY scan, **28** with a
  `REVIEW.md`, **25** with both. The August days are intact and invisible only to
  the 45-day bar window. Also recorded: **`track.py` no longer prints a literal
  `actionable: YES/NO` line**, so the threshold rule was applied by hand.
- **Session-context field — 14th session, and the mildest instance recorded.**
  Only **1 of 6** board rows (29627.6) lay inside the pre-scan range
  29512.7–29958.2. **P-G does not fire** (stays at #21): the *"Beyond today's
  range (context only, don't mark)"* footnote carried **London Low 30513.4** and
  **Asia Low 30504.5** at +875 / +866 **above** price, but it prints **no prose**,
  and P-G's defect is prose chosen by level kind.
- **P-B(b) — 14th session, inflation 1.00x, window did not fire.**
  `merge_tol` = max(3.0, 457.0 × 0.008) = **3.66** against `TOUCH_TOL` **8.0**,
  but the closest published pair is 50pts apart.
- **H3 — citation correction, narrower than the 10-15 flag.**
  `2026-08-25/1304-preny.json` scores **0 / NEUTRAL**, so *"08-25 13:04"* is
  wrong **only where it is cited as a max-conviction bearish call** — the list at
  line 8226, whose *"bearish branch is now **0 for 4**"* is really **0 for 3**,
  **which voids the 10-07 entry's claim that a 4th data point for a conviction
  cap exists**. The same citation is **legitimate** at line 2818 (a fuel error of
  +219.8 on a 12.0 budget — that scan really was EXHAUSTED at 97.1% used), at
  line 4301 (an H2 EXHAUSTED-fade instance) and at line 1234 (W1, where the claim
  *depends* on the score being 0). **H3's CLOSED-NEGATIVE is recorded in the
  10-15 block but H3's own heading still reads `Status: OBSERVING`** and cannot
  be edited — a pointer has been added to the ID-allocation block, the only
  in-place-editable region.
- **No instance:** **H4** (flip never approached within 571.3), **H7** (no
  overnight scan), **H20** (**stays CLOSED-NEGATIVE and is not revived**),
  **D21** (`gamma +0`, price 37% up the band — neither branch fired), **D18**
  (every sign right), **P-E(b)** (the shelf family is graded under P5 above).

## Journal hygiene

One scan file for 10-15 (`1247-preny.json` + `.md`), `is_trading_day: true`,
`review_day` reports **0 test artefacts** for the day (6 across the record,
excluded by `track.py`). **09-24 quarantined by hand — 13th consecutive review to
carry it**; there is still no schema `quarantine` field and the 09-29 proposal
for one is reaffirmed, because `track.py` keeps 09-24 inside every statistic it
prints (its direction line, **14 right / 7 wrong / 9 no-call**, becomes
**13 / 7 / 9** once 09-24 is removed). **2026-10-13 has no journal directory —
the scheduled scan never ran; nothing was created, back-dated or inferred, and
the gap is recorded so the skip from 10-12 to 10-14 is not later mistaken for
data. 2026-10-16 is on disk but unfinished (180 bars) and was excluded from every
statistic above.** 09-09 and 09-25 still have no `REVIEW.md` and none was
created. **No `prediction` block was touched. No scoring, wall or grading code
was edited.** No fabricated or backfilled entries found. **No new ID allocated by
this review. Next free: H27 · D27 · P-I.**

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01M7sro1DKMp5T7EBDusm6pM

---

# Observations appended 2026-10-19 (grading the 2026-10-16 session)

_Session O 29903.0 / H 30028.6 / L 29073.7 / C 29191.5 · range **954.9 (2.01x
ADR14 475.6)** · net **−711.5**, close 12.3% up the range. One PRE_NY scan at
12:48:42Z / 29878.0, **−6 BEARISH**, `COHERENT_SHORT` high confidence,
`MODERATE`, budget **210.8**, `fuel_ratio` **1.24 (normal)**. Post-scan move
**−688.1 → CORRECT**; day net −711.5 → **CORRECT**, so this is **NOT a P-H
deciding instance**. Traversal 816.0, levels 10 / 17. **09-24 quarantined by
hand, 14th consecutive review. No 2026-10-13 directory. 2026-10-19 on disk,
unfinished (180 bars), excluded from every statistic below.**_

**The one fact that governs the whole day: the session high 30028.6 was set at
05:05Z, 7h43m BEFORE the scan.** Pre-scan range 29763.8–30028.6 = 264.8, exactly
the `today_range` the fuel block used. Post-scan price rose **10.1** points
(high 29889.7 at 13:10Z) and then fell **806.0**. Every "never reached" below
means the day went the other way.

## The corridor terminus — 5th session, and the 4-for-4 claim DIES, with a mechanism

*"DOWNSIDE path: clear. Every options shelf from here to **29514.9** (363pts,
0.76x ADR) is negative gamma — nothing structural to slow a breakdown."* Price
went to **29073.7**.

| day | corridor terminus | realised extreme | terminus err | / ADR |
|---|---|---|---|---|
| 10-08 | 30559.6 (398) | low 30568.7 | −9.1 | 0.02x |
| 10-12 | 30643.1 (200) | low 30634.7 | +8.4 | 0.02x |
| 10-14 | 29941.8 (464) | low 29877.9 | +63.9 | 0.15x |
| 10-15 | 29977.6 (339) | high 29996.8 | +19.2 | 0.04x |
| **10-16** | **29514.9 (363)** | **low 29073.7** | **+441.2** | **0.93x** |

**The mechanism, read off the code rather than inferred:** `brief.py:520` sets
`corridor_end = span[-1]`, where `span` is every shelf within **1.2x ADR** on
that side, distance-sorted. **The terminus is where the shelf list runs out, not
a barrier.** The previous 4-for-4 inside 0.15x ADR was a property of the grid
happening to end near where price stopped; when price kept going the quantity
had nothing to say. **The 10-15 proposal to publish the terminus as a range
forecast should NOT be actioned as written.** Keep measuring; if it is ever
published, publish it as *"the last positioning we can see"*, never as *"how far
it can go"*. Qualitatively the read was perfect — nothing did slow the
breakdown — and that half stands.

## H23 — instance 13, "never reached", and the force-ranking fix is heading for unfalsifiable

*"UPSIDE path: has friction. Expect a stall at 30014.9 (137pts away)"* on a day
that fell 806. Census **9 sliced / 1 capped** unchanged; **never-reached 2 → 3**.

**The ranking fix would have published the same level, for the second session
running, and this time it was a genuine choice.** Four positive-sign shelves sat
above price — 30014.9 (**1.64bn**) · 30064.9 (0.38) · 30114.9 (1.02) · 30164.9
(0.72) — and the **nearest was also the heaviest**, so distance-first and
force-first agree. On 10-15 they could not differ (one candidate); on 10-16 they
could and did not. *(Read instead as "rank all in-range shelves by force
ignoring sign", it names 29914.9 at +37 / 1.58bn — also never reached.)*
**Pre-registered: a third consecutive agreement means the fix is unfalsifiable
in practice and H23's ranking branch should be CLOSED rather than carried.**

## H26 — n=24, and the magnitude claim WEAKENS; 10-15's "magnitude strengthens" does not survive

|score| = 6 → the **6–9** bucket, **CORRECT** on the P-H basis, so **5/6 → 6/7**.
**But the −6 delivered 1.447x ADR of post-scan movement — the LARGEST in the
sample, ahead of 10-14's −18 at 1.126x.** Bucket means stay monotonic; the rank
correlation falls.

| score magnitude | n | correct | wrong | no-call | mean abs(post-scan)/ADR | mean range/ADR |
|---|---|---|---|---|---|---|
| 0–2 | 7 | — | — | 7 | 0.181 | 1.103 |
| 3–5 | 4 | 2 | 2 | 0 | 0.236 | 0.937 |
| **6–9** | **7** | **6** | **1** | 0 | **0.545** (was 0.394) | **1.193** (was 1.057) |
| ≥10 | 6 | 3 | 3 | 0 | 0.783 | 1.390 |

- Spearman(|score|, |post-scan move|/ADR) **+0.612 → +0.577**
- Spearman(|score|, *signed* move in the called direction/ADR) **+0.165 → +0.157**
- Spearman(|score|, session range/ADR) +0.196 → **+0.198**

The n=23 sample reproduces the register's published figures **exactly**
(+0.612 / +0.165 / +0.196, buckets 7/4/6/6) before 10-16 is added, so the move is
real and not a sampling difference. H26's proposal is unchanged and now rests on
24 sessions **and a thinner correlation than the register currently states.**

## P-H — 17 graded calls, and 10-16 is NOT a 5th deciding instance

| basis | right | wrong | rate |
|---|---|---|---|
| post-scan (P-H) | **11** | 6 | **64.7%** (was 62.5%) |
| day net | **13** | 4 | **76.5%** (was 75.0%) |

Deciding set unchanged at **09-11, 09-16, 10-07, 10-15 (n=4)**. The convention is
now worth **11.8** points of headline accuracy, not 12.5. Already PROPOSED
on 10-08; no new proposal, no ID.

## P4 / H1 — n=28 days; one new data point, and the statistic is NOT re-derived

10-16 error **+479.3** (budget 210.8, extension 690.1 = **3.27x**; traversal
816.0 = 3.87x). **Second-largest signed error in the record** after 09-21's
+569.2. `track.py` per-day mean **+34.3 → +50.2** (n=28, includes 09-24);
per-scan +51.2 (n=31). **NOT re-derived:** MAE 116.1 vs leave-one-out constant
98.3 (n=19); ex-outlier 90.9 vs 75.5 (n=18). Claim stays **"no usable skill"**,
not "inversely predictive"; multiplier branch stays closed.

**Sub-observation, and it is the mirror of a rejected item.** `fuel_ratio` 1.24
was the **lowest reading in seven sessions** and the row is labelled *(normal)*.
The register already rejected *"hot early pace predicts expansion"* (10-14
block). **10-16 is the mirror: cool early pace did not predict a quiet day** — it
preceded the largest range in the 24-day graded sample. Pre-scan pace carried no
information in either direction.

## The two-opposite-instructions census — the suspension HOLDS, and here is why the column kept moving

**The suspension is not lifted and no score is quoted.** The reason the column
and the claim came apart on 10-15 is that **three different conflicts have been
counted as one object**:

1. **fuel vs gamma on *fade vs continue*** — the registered cell
   (`LOW_FUEL`/`EXHAUSTED`, below the flip). **10-16 is NOT an instance:**
   `MODERATE` prose recommends no fade.
2. **bias block vs strategy block** — 10-05, n=1 (recorded in the 10-06 block,
   which already asked for a second cell).
3. **fuel vs shape on *target size*** — **10-16 is an instance.** Section 3,
   `MODERATE`: *"Continuation is fine to the nearest pool; **don't plan on a
   third leg**"* + *"break-even at 1R or 50% of remaining budget"*. Section 2,
   `COHERENT_SHORT`: *"Today's ADR can be exceeded — **don't cap the target too
   early**."* There were at least three legs and the day ran 2.01x ADR. Gamma
   won by ~480 points.

**Proposed specification, to be re-derived from scratch before ANY score is
quoted for ANY axis:** one column per axis, each with a rule fixed in advance —
axis 1 graded by whether fading the first post-scan sweep of a pre-scan extreme
reached the next published level before the sweep level was reclaimed; axis 3
graded by whether realised post-scan traversal exceeded the budget-implied cap.
**No score, including today's, is carried forward.**

## M6 — session 26, the artefact at its largest absolute scale, and 3 of 3 inverted again

Travel **954.9 = 2.01x ADR**. **All 10 of 10 touched rows understate; mean 4.5x,
worst 8.2x.**

| level | `travel_down` | actual excursion below | ratio |
|---|---|---|---|
| 29664.9 PUT WALL | 72.5 | **591.2** | **8.2x** |
| 29699.5 London High (pd) | 107.1 | 625.8 | 5.8x |
| 29710.2 PD mid | 117.8 | 636.5 | 5.4x |
| 29848.9 Equal lows ×3 | 189.2 | 775.2 | 4.1x |
| 29856.4 London Low (today) | 196.7 | 782.7 | 4.0x |
| 29763.8 Asia Low (today) | 171.4 | 690.1 | 4.0x |
| 29885.3 PD close | 225.6 | 811.6 | 3.6x |
| 29549.7 London Low (pd) | 134.9 | 476.0 | 3.5x |
| 29831.7 Asia High (pd) | 239.3 | 758.0 | 3.2x |
| 29567.0 Asia Low (pd) | 152.2 | 493.3 | 3.2x |

**Said explicitly as directed: M6's magnitude scales with how far the day
travelled.** The wording inversion fires **3 of 3** again — 29885.3, 29763.8 and
**29664.9** are all reported *"held as resistance"*, three levels price collapsed
through by 591 to 812 points.

## The put wall did exactly what the regime-aware note said — and broke the "break marks the low" pattern

First post-scan touch 13:40Z. Next 60 min: only **72.5** below, then a bounce to
29749.1. Then it resumed: **run-through 591.2**, close **473.4 below**. The note
— *"BUT today the desks are pushing moves along — if it breaks, expect it to
speed UP, not bounce. Don't buy the break"* — **was the best line in the
document**. H14's regime-aware wall note, 3rd recorded success; run-through
census **n=4 → 5**.

**Counter-instance to a 2-session pattern.** The register recorded *"the
put-wall break marked the day's low for the SECOND consecutive session"* (10-07,
10-08). Today the break marked the **start** of the move. The pattern is **2 of
3** and should not be relied on.

## Session-context field — 15th session, and the strongest instance by consequence

**10 of 17 rows** lay inside the pre-scan range 29763.8–30028.6. The worst is the
headline: **CALL WALL ●●●●● 1.64bn + MAX PAIN + shelf ⭐ at 30014.9**, published
at +137 with *"desks must SELL as price rises into it, so rallies stall. Take
profit into it… the strongest ceiling on the board"* — **price had already
exceeded it by 13.7 points at 05:05Z, failed, and was 150 below by scan time.**
30030.8 was missed by 2.2 pre-scan. Already PROPOSED (09-30); this is evidence.

## P-E — NO forward-only instance, and this is the day to say so loudly

The call wall's **only** penetration was **pre-scan** (+13.7 at 05:05Z,
7h43m before publication). Post-scan high 29889.7 — the level was **never
reached**, missed by 125.2. **Separating the two as directed:** intraday
penetration **+13.7, pre-scan, uncreditable**; close-side control **823.4 below,
post-scan, and the level played no part in producing it**. **P-E takes no
instance; the capped/sliced census is unchanged.** The empty-middle question is
untouched by today.

## P5 — 5 of 6 shelves unreachable, and the one that graded was wrong

| shelf | force | printed claim | post-scan | verdict |
|---|---|---|---|---|
| 29614.9 | 0.87bn | *"amplify… accelerate THROUGH… **Not a floor**"* | touched 13:50Z, next 60 min **+134.2 up / −22.5 down** — it stalled the decline | **WRONG** |
| 29914.9 / 29964.9 / 30064.9 / 30114.9 / 30164.9 | 1.58 / 1.50 / 0.38 / 1.02 / 0.72bn | — | **never reached** | ungraded |

**1 of 1 graded, and wrong.** The structural problem is the 5 of 6: the table is
mostly published out of reach. **Still graded by no tool.**

## P-B(b) — 15th session; FOUR guaranteed windows, one fired, inflation 1.67x

`merge_tol = max(3.0, 475.6 × 0.008) = **3.805**` against `TOUCH_TOL = **8.0**`.
**Four published pairs sit in the structurally-guaranteed 3.805–8.0 window** —
(30014.9, 30008.9) 6.0 · (30008.9, 30004.2) 4.7 · (30004.2, 29996.8) 7.4 ·
(29856.4, 29848.9) 7.5 — **the most in the series**. **One fired**: 29856.4 and
29848.9 both graded touched at **bar 178**. Published rate **10/17 = 0.59**;
distinct touch bars **6** (178, 184, 186, 187, 188, 205) → distinct-event rate
**0.35**; **inflation 1.67x**. No tolerance-only touches — all ten rows have
positive travel on both sides. Proposal unchanged.

## P-G — instances #22 and #23

Two prev-day session-extreme rows sit **below** price and still print the
above-side note: **29831.7 Asia High (prev-day)** at −46 and **29699.5 London
High (prev-day)** at −178, both *"the next session usually runs the stops above
it"* — stops already behind the market. The four today-session rows (29856.4,
29763.8, 30004.2, 30030.8) were all correctly sided, which is the point: the
defect is **kind-driven, not side-driven**.

## H18 / P1 — instance 20, duplication 25 of 25, and the age gate would have HELPED this time

`macro +3` DFII10 and `macro +1` DGS10 both resolve to observation date
**2026-10-14**, in a document headed *"today"*; the age warning printed on
DFII10 and **not** on DGS10. **HY OAS rendered no observation date for the 12th
consecutive session** — and HY OAS (**−2**, 3.25%, +16bp) was the **only macro
row on the right side of the day**.

Suppressing the stale pair takes **−6 → −10**: a **correct** call made bigger.
That is the gate's **3rd helping instance against 2 hurting** (10-07, 10-15).
**A 3–2 split is not evidence. The accuracy case stays RETRACTED**, and the
live defect remains the **rendering** one. **Correction carried: HY OAS is not
dead weight and never was.**

## H10 — the `−3` branch's 7th firing, and it was RIGHT

Price below the entire prior-week range (30568.7–31385.1) → `structure −3`, and
the day fell 688.1 post-scan. **Branch now 2-for-7** on the post-scan basis.
**PWL 30568.7 was 690.7 above price and never approached within 678.9**, so no
reclaim occurred and the proposed reclaim term would again have changed nothing
— the same null as 10-14 and 10-15. `+3` branch unchanged at 2-for-4.

## D23 — 13th residual, and a third consecutive SIGN disagreement

Board **+14.9** vs section-7 **−24.5** matched to feed time 11:59Z. Gap **+39.4**;
CFD move (11:55Z bar open **29872.2** → scan **29878.0**) = **+5.8**; **residual
+33.6**. Series: `+190.5 / −201.3 / +203.8 / −7.3 / +2.9 / +246.6 / +203.6 /
+209.5 / +345.4 / −68.0 / +165.0 / +438.2 / **+33.6**` — third-smallest absolute
in the series, immediately after the largest. The two conversions **disagree in
sign** for the third consecutive session (10-12, 10-15, 10-16). Damage none —
research-only, no volume had traded.

## Dead-weight audit — refreshed to n=32 PRE_NY `is_trading_day` scans (09-24 excluded by hand)

| row | scored / present |
|---|---|
| `macro` Yield curve 10y–2y | **0 / 32 — has still never scored** |
| `fuel` ratio row | **0 / 32** |
| `events` | 0 / 13 (absent on the rest) |
| `vol` VVIX | 3 / 32 |
| `rates` DXY | 4 / 32 |
| `macro` NFCI | 5 / 32 |
| `macro` WALCL/RRP | 6 / 32 |
| `macro` HY OAS | **25 / 32** |

The narrowed standing proposal (drop the yield-curve row and WALCL/RRP) is
**unchanged and still not actioned**.

## Appended without proposal

- **H22 — n=10.** Week net GEX −5.172 → *"expansion likely"* → **2.01x ADR**,
  the second-largest range/ADR in the record (09-21 2.46x). The row was right.
- **H19 — mandated per-scan record.** 130 headlines / 10 feeds → 53 relevant →
  **0 auto-scored**; coverage **0.0%**, equal-lowest recorded.
  **A D18-shaped mis-tag with no damage:** *"S&P 500 Correction Risk Grows as
  Index Rally Lacks Broad Participation"* is tagged **`[risk_on]`**. It scored
  nothing, so **D18 stays at 13 headline instances / 7 trading days.**
- **H8 — ANSWERED-POSITIVE and NOT reopened; post-closure data only.** Straddle
  279 → band **29641..30115**; close **29191.5 OUTSIDE by 449.5**. Same page,
  for contrast: **VXN-implied range 430.8 under-read the realised 954.9 by
  524.1 (realised 2.22x)**. Both forward range measures failed; the straddle
  band failed by less, consistent with H8's verdict.
- **Max pain — 6th distance-confounded non-test.** Printed at the same price as
  the call wall (30014.9) and never within reach post-scan. Against one success
  (10-15). It contributes a ⭐ to a line it does not independently earn.
- **D25 — 26th consecutive pre-NY scan.** *"The dominant strike is **stable** at
  0 across 6 samples"*, three lines under *"⚠️ No volume has traded yet today"*.
  Damage none.
- **D26 — reporting gap, NOT data loss; the retraction stands.** `track.py`
  reports **28 trading days / 31 scans (deduped)**; on disk: **35** day
  directories, **65** scan JSONs, **30** days with a PRE_NY scan, **29** with a
  `REVIEW.md` (30 after this review), **26** with both. The four August PRE_NY
  days are intact and invisible only to the 45-day bar window — and they are why
  `track.py`'s per-day mean (n=28) and this review's H26 sample (n=24) have
  different denominators. `track.py` still prints no literal `actionable:
  YES/NO`; the threshold rule was applied by hand.
- **D17 — already logged, NOT double-counted.** The CBOE 429 on the 10-16 scan
  and its attempt-1 recovery were recorded as a D17 success in the register's
  **2026-10-16** block (written while grading 10-15). No second entry is made for
  the same event.
- **No instance:** **H4** (flip 30134.8 never approached within 245.1) ·
  **H7** (no overnight scan) · **H2** (`MODERATE`, outside the cell) ·
  **H20** (CLOSED-NEGATIVE, not revived; no High/Medium events) ·
  **D21** (`gamma +0`, price 61% up the band — neither branch) ·
  **D24** (section 5 forward-only; no release identified between open and scan;
  `event_gate: null` correct) · **P-F** (price inside the prior-day range) ·
  **H17** (post-scan move = 72.1% of the session range, far outside the 5%
  deadband; stays 1 of 3) · **P-E(b)** (shelf family graded under P5 above).
- **No new data point is warranted.** Every miss today is named by an open
  entry. The field that would have changed the document — *"price has already
  traded this level today"* — is the **session-context field**, proposed 09-30,
  free (the board already holds the pre-scan range), reliable (arithmetic on data
  already printed), and **still not actioned**. Nothing new should be added
  before it is.

## Carried forward from the 2026-10-19 scan — recorded, NOT graded

- **Board offset: 14.9 (10-16) then −3.9 (10-19).** Fitted through 10-14 the time
  trend predicted 32.4 for 10-16 (actual 14.9) and ~34 for 10-19 (actual −3.9) —
  **three consecutive out-of-sample misses, the last two both low.** The trend was
  already found to survive arithmetically and explain nothing; these add to that.
  **Mechanism remains unexplained. Nothing proposed, and no third story is
  substituted.**
- **The pre-registered realised-close-basis log — observation 3 of 10.** NDX cash
  close 10-16 = implied 29563.5 − roll (**+376.0**) = **29187.5**; CFD close
  **29191.5**.

  | day | scan offset | NDX close | CFD close | realised basis | gap | NQ roll |
  |---|---|---|---|---|---|---|
  | 10-14 | +41.8 | 29950.82 | 29931.8 | −19.0 | 60.8 | −205.2 |
  | 10-15 | +77.6 | 29935.6 | 29885.3 | −50.3 | 128.0 | −389.8 |
  | **10-16** | **+14.9** | **29187.5** | **29191.5** | **+4.0** | **+10.9** | **+376.0** |

  **The "same shape" reading breaks at n=3** — this is the first positive
  realised basis and the first up-roll in the log — and it already cuts against
  the scoping fix: **the largest |roll| in the log (376.0) produced the smallest
  gap (10.9)**. Re-test still at **n=10 clean observations**. **Nothing proposed.**
- **⚠️ DEFECT IN THE REGISTER'S OWN OFFSET ANALYSIS (not in model code).** The
  scratchpad extractor behind the 10-14/10-15/10-16 offset entries parses the
  roll as `NQ futures move \((-?[\d.]+)\)`, which **cannot match a positive
  roll** — the brief prints `(+376.0)`. **15 of 29 days have up-rolls and every
  one was silently recorded as `None`.** The published claim *"r(offset, |roll|)
  = +0.039 within down-roll days"* is correctly **scoped**, but the down-roll
  sample was never a choice and no up-roll day was ever visible to it. **Any
  future |roll| regression must be rebuilt with a sign-tolerant parse.** No
  scoring, wall or grading code is affected.
- **`expiry_shape: PIN_THEN_EXPAND` is NEW — confirmed against the whole
  journal.** Census of all **65** scan JSONs: `COHERENT_LONG` 27 ·
  `COHERENT_SHORT` 18 · `FRONT_FLAT_BACK_SHORT` 11 · `FRONT_FLAT_BACK_LONG` 6 ·
  `SPIKE_THEN_REVERT` 2 · **`PIN_THEN_EXPAND` 1 (2026-10-19, first ever)**.

  **PRE-REGISTERED TEST, written before the outcome is known.** No ID taken, by
  the precedent of the 10-05 `SPIKE_THEN_REVERT` pre-registration, which is
  recorded under a prose heading with no number. The shape makes a **timing**
  claim, not a direction claim: *"Chop early, resolve late… breakouts will fail
  while the pin holds. From roughly 13:00 ET the pin weakens and the move that
  has been building gets released."*

  1. **Split the session at 17:00 UTC (13:00 ET).** Measure range and absolute
     net move in 13:30–17:00 UTC (pre) and 17:00–20:55 UTC (post).
  2. **CONFIRMED if** post-13:00 ET range **>** pre-13:00 ET range **AND** the
     session extreme on the side the day closes is made **after** 17:00 UTC.
  3. **FALSIFIED if** the pre-13:00 ET window holds the larger range, **OR** both
     the day's high and low are set before 17:00 UTC.
  4. **Secondary, for the "breakouts will fail" half:** count post-scan sweeps of
     the pre-scan high/low before 17:00 UTC and whether price closed back inside
     within 30 minutes. ≥1 sweep that reverses supports it; a sweep that runs is
     against.
  5. **Threshold: 3 `PIN_THEN_EXPAND` days.** At the observed frequency that is
     months away. **Nothing may be concluded from 10-19 alone**, and the first
     observation is to be recorded **without a verdict attached**.

## Journal hygiene

One scan file for 10-16 (`1248-preny.json` + `.md`), `is_trading_day: true`,
`review_day` reports **0 test artefacts** for the day (6 across the record,
excluded by `track.py`). **09-24 quarantined by hand — 14th consecutive review
to carry it**; there is still no schema `quarantine` field and the 09-29 proposal
for one is reaffirmed, because `track.py` keeps 09-24 inside every statistic it
prints (direction **15 / 7 / 9** becomes **14 / 7 / 9** once 09-24 is removed).
**2026-10-13 has no journal directory — the scheduled scan never ran; nothing was
created, back-dated or inferred. 2026-10-19 is on disk but unfinished (180 bars),
correctly held back by `track.py`, and excluded from every statistic above.**
09-09 and 09-25 still have no `REVIEW.md` and none was created. **No `prediction`
block was touched. No scoring, wall or grading code was edited.** No fabricated or
backfilled entries found. **No new ID allocated by this review. Next free:
H27 · D27 · P-I.**

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01M7sro1DKMp5T7EBDusm6pM

---

# 2026-10-20 review (grading 2026-10-19) — observations

## H2 — THRESHOLD MET AT n=7, CLAIM FALSIFIED, and the census is lifted on axis 1

The suspended two-opposite-instructions census is **re-derived from scratch**
under the 10-16 specification. **Rules fixed in writing before any outcome was
inspected:**

> **Cell:** PRE_NY · `is_trading_day` · 09-24 excluded · `fuel_state ∈
> {LOW_FUEL, EXHAUSTED}` **and** price below the gamma flip. Both states carry a
> fade instruction (`brief.py:463–478`): `LOW_FUEL` *"favour fades over chasing
> breaks"*, `EXHAUSTED` *"Fading the extremes… is the higher-probability side
> here, even when the gamma regime favours continuation"*. Below the flip the
> board says *"they're pushing, so don't fade"*.
> **Grade:** first post-scan sweep of a pre-scan extreme → the fade engages on
> the first bar closing back inside → **FADE WINS** if the nearest published
> level inside is touched before the swept extreme is reclaimed; **LOSES** if
> reclaimed first, or if price never re-enters. **Ties scored to the fade.**

| day | state | sweep | target | result |
|---|---|---|---|---|
| 09-14 | LOW_FUEL | up 15:30 | 28804.7 | **fade LOSES** (never came back inside) |
| 09-15 | LOW_FUEL | down 14:50 | 28963.1 (+37.3) | fade wins — *engage bar, tie* |
| 09-28 | LOW_FUEL | down 14:10 | 30345.9 | **fade LOSES** (reclaimed) |
| 10-08 | LOW_FUEL | down 16:45 | 30895.1 | **fade LOSES** (never came back inside) |
| 10-14 | LOW_FUEL | down 12:55 | 30386.7 (+32.4) | fade wins — *engage bar, tie* |
| 10-15 | EXHAUSTED | down 13:30 | 29627.6 | **fade LOSES** (reclaimed) |
| **10-19** | **EXHAUSTED** | **up 14:15** | **29246.1** | **fade LOSES** (reclaimed) |

**5–2 to the gamma block; 7–0 if ties go against the fade** — both "wins"
resolved inside the single 5-minute engage bar at sub-40pt targets. 08-24 and
08-26 are in the cell but outside the 45-day bar window: **reported unavailable,
not excluded by choice.**

**PROPOSED:** when `fuel_state` is `LOW_FUEL`/`EXHAUSTED` **and** price is below
the gamma flip, suppress the fuel block's fade instruction or subordinate it
explicitly to the regime note. **H2's claim as written is FALSIFIED.**

## Axis 3 — STAYS SUSPENDED, and the 10-16 specification is itself the defect

Graded exactly as specified (*"realised post-scan traversal exceeded the
budget-implied cap"*), the COHERENT_SHORT conflict days read **9 of 9 to
shape/gamma** — and the **control reads 15 of 16 the same way on non-conflict
days**. The metric is a **near-constant, not a discriminator**, for the reason
`review_day.py:230–238` states in its own comment: the budget bounds range
**extension**; traversal is a different quantity. **Delete the axis-3 column; do
not re-score it. No axis-3 score is quoted, including today's.** A valid axis-3
test needs the fuel block's own target unit, which is an **R multiple**, not
points, so it cannot be graded at all until the R denominator is recorded.

## The pre-registered `PIN_THEN_EXPAND` test — RUN AS WRITTEN, FALSIFIED, observation 1 of 3

| window | range | abs net | high | low |
|---|---|---|---|---|
| **pre** 13:30–17:00Z | **329.7** | 14.3 | 29799.0 @15:35 | 29469.3 @14:00 |
| **post** 17:00–20:55Z | **139.5** | 48.7 | 29657.3 @19:25 | 29517.8 @20:00 |

Clause 2 fails (post range **139.5 < 329.7**). **Clause 3 fires twice:** the pre
window holds the larger range **and** both session extremes were set before
17:00Z (high 15:35Z, low 22:00Z on 10-18). The move was over at 11:35 ET, **85
minutes before** the pin was said to weaken. **Secondary ("breakouts will
fail"):** one sweep of the pre-scan high 29629.2 at 14:15Z, closed back inside
within 30 min (14:30Z close 29593.7) — **supports it by the letter**, but the
same level was then exceeded by **169.8** inside the same pre-17:00 window, so
the breakout ran. Pre-scan low never swept. **Per clause 5 this is observation 1
of 3, no verdict attaches, and nothing is proposed.**

## H23 — instances 14 and 15, and the pre-registration FIRES: close the force-ranking branch

Downside brake **29496.1** (−64): touched 13:55Z, only **26.8** below, then
**+302.9** — **CAPPED, the 2nd cap in 15**. Upside brake **29646.1** (+86):
touched 14:15Z, ran **+152.9** — **SLICED**. Census **9/1/3 → 10 sliced / 2
capped / 3 never-reached**.

**Third consecutive distance-first/force-first agreement.** Downside is a genuine
choice and they agree — positive shelves 29496.1 (**0.78bn**) · 29446.1 (0.63),
nearest is heaviest. Upside they agree **by tie** — heaviest is 0.75bn at both
29646.1 and 29896.1, broken by distance to 29646.1, which is what distance-first
published. **Per the 10-16 pre-registration this closes H23's ranking branch as
unfalsifiable in practice.** Corridor-terminus proposal remains **WITHDRAWN**
(10-16, `brief.py:520`) and is not revived.

**Trap flagged so no one opens a defect for it.** The secondary table lists a
positive shelf at **29596.1 (+36, 0.47bn)**, nearer than the published upside
brake. That is **not** a brake `path_read()` skipped: the table is built from
`walls_ranked` (`brief.py:647`), `path_read()` reads `largest_abs_gex`
(`brief.py:515`). **Different lists.**

## H26 — n=25, and one of its three published statistics CANNOT BE REPRODUCED

Re-derivation reproduces the register **exactly** at n=24 on Spearman(|score|,
|post-scan|/ADR) **+0.577** and Spearman(|score|, range/ADR) **+0.198**,
confirming the sample. The **signed** statistic reproduces under **no** available
convention: **+0.220** counting the 7 no-call days as 0, **+0.102** excluding
them, against the published **+0.157**. **PROPOSED: quote the signed figure with
its method or stop quoting it.**

10-19 is a **3–5** bucket instance, CORRECT on the P-H basis.

| \|score\| | n | C | W | no-call | mean \|post\|/ADR | mean range/ADR |
|---|---|---|---|---|---|---|
| 0–2 | 7 | — | — | 7 | 0.181 | 1.103 |
| **3–5** | **5** | **3** | 2 | 0 | **0.193** (was 0.236) | **1.023** (was 0.937) |
| 6–9 | 7 | 6 | 1 | 0 | 0.545 | 1.193 |
| ≥10 | 6 | 3 | 3 | 0 | 0.783 | 1.390 |

Spearman(|score|, |post|/ADR) **+0.577 → +0.548** · range/ADR **+0.198 →
+0.190**. **Is the magnitude claim still standing? In bucket form yes — the
|post|/ADR means remain monotonic (0.181 / 0.193 / 0.545 / 0.783) — in
correlation form it is eroding**, having now fallen on **two consecutive
sessions** (+0.612 → +0.577 → +0.548). 10-19 is the cause this time: the
**second-lowest |post|/ADR in the record (0.018)** at |score| 5. Direction half
unchanged and weak.

## P-H — the 5th deciding instance, and it HALVES the convention's cost

Post-scan **−9.3 CORRECT**; day net **+430.6 WRONG**. First deciding instance in
which the post-scan basis is the **right** one.

| basis | right | wrong | rate |
|---|---|---|---|
| post-scan (P-H) | **12** | 6 | **66.7%** (was 64.7%) |
| day net | **13** | 5 | **72.2%** (was 76.5%) |

Deciding set **09-11, 09-16, 10-07, 10-15, 10-19 (n=5)**. The convention is now
worth **5.5** points of headline accuracy, down from 11.8. Already PROPOSED
10-08; no new proposal, no ID.

## H17 — 2 of 3, and the instance decides a P-H deciding instance

Post-scan move **9.3** = **1.35%** of the 686.9pt session range — the second
sub-5% graded call in the record after 09-11's 0.2%, and the first on a
**different day**, which is what the threshold counts. **2 of 3. Nothing
proposed.** When it is reached it re-grades 10-19's `CORRECT` and the 5th P-H
deciding instance with it.

## The vol block is one reading counted four times, and it is the whole error

`vol −6`, the largest vol contribution in the record: VXN 27.13 (+18.5%) −2 ·
VIX9D/VIX 1.082 backwardated −2 · VXN/VIX 1.46 −1 · VVIX 109.91 −1. **Delete the
block and the score is +1 — the day's sign.** Four functions of one latent
variable, scored independently, outvoting every other block. The backwardation
row's *"expect range expansion"* was **right** (1.364x ADR) and its
*"downside skew"* was wrong; only the sign is scored. **n=1; nothing proposed.**

**Two range forecasts, opposite signs, and the wrong one is the scored one.**
Fuel: `EXHAUSTED`, **0.0** budget, 102.7% of ADR used pre-open, `fuel_ratio`
**2.28 (burning hot)** — wrong by **+169.8**. Four lines below: **VXN-implied
range 505.2 > ADR 503.6**, *"options market prices expansion, ADR understates"*
— **right** (realised 686.9), and it reaches no number. **First time this month
that line argued for expansion.**

## P4 / H1 — n=29 days; one new data point, and the statistic is NOT re-derived

10-19 error **+169.8** (budget **0.0 — the arithmetic floor — so the error is the
entire extension**, and the estimator was one-sided by construction; 7th such
entry). `track.py` per-day mean **+50.2 → +54.3** (n=29, incl. 09-24); per-scan
**+54.9** (n=32). **NOT re-derived:** MAE 116.1 vs leave-one-out constant 98.3
(n=19). Claim stays **"no usable skill"**, not "inversely predictive";
**multiplier branch stays closed.**

**The 10-16 sub-observation now has its counter-test, and the question closes.**
10-16: `fuel_ratio` **1.24 *(normal)*** → largest range in the sample. 10-19:
**2.28 *(burning hot)*** → **1.364x ADR** and a **+169.8** under-read. Hot pace
did not predict expansion (rejected 10-14); cool pace did not predict quiet
(10-16). **Pre-scan pace carries no information in either direction.**

## M6 — session 27, and the magnitude scales with travel, stated explicitly

Post-scan travel **329.7 = 0.65x ADR** against 10-16's 2.01x, and the
understatement is correspondingly milder: **mean 2.6x, worst 3.6x** (10-16: mean
4.5x, worst 8.2x). **Said as directed: M6's magnitude scales with how far the day
travelled.**

| level | grader travel | actual excursion | ratio |
|---|---|---|---|
| 29696.1 STRUCT CW | 49.5 down | 178.3 | **3.60x** |
| 29771.1 MAX PAIN | 103.0 down | 253.3 | 2.46x |
| 29646.1 CALL WALL | 67.6 up | 152.9 | 2.26x |
| 29638.9 FLIP | 74.8 up | 160.1 | 2.14x |

**The settle-window defect repeats:** all four rows read *"held as resistance"*
with `worst_excursion` 11.2–23.3 on levels price exceeded by **27.9–160.1**,
because the windows open at 15:40 / 16:10 / 19:20 / 19:35Z — **after** the
15:35Z high they are meant to measure.

## P-E — instance 14, SLICED, and the first clean forward-only instance in weeks

CALL WALL **29646.1** at +86, *"desks must SELL as price rises into it, so
rallies stall. Take profit into it."* Pre-scan high **29629.2** was **16.9
below** it, so there is **no pre-scan contamination**. First post-scan touch
14:15Z (87 min after the scan), overshoot **+152.9** — **slice mode, not the
12–103 middle**. Close **86.7 below**: close-side control held, the intraday lid
did not. Census → **5 capped / 1 middle (10-06) / 8 sliced**.

**P-E(b) — supporting instance.** The shelf **29746.1** stalled the rally at
**+52.9** while the wall was sliced by 152.9: the shelf located the session high
**100 points better** than the headline wall.

## P5 — 3 of 6 gradeable, 2 right / 1 wrong, and still graded by no tool

| shelf | printed claim | post-scan | verdict |
|---|---|---|---|
| 29496.1 (0.78bn) | *"stall and dip-buying… acts as **support**"* | 26.8 below, then **+302.9** | **RIGHT** |
| 29746.1 (0.41bn) | *"stall — rallies lose momentum into it"* | **+52.9**, then −228.3 | **RIGHT** |
| 29596.1 (0.47bn) | *"stall — rallies lose momentum into it"* | **+202.9** straight through | **WRONG** |
| 29896.1 / 29446.1 / 29196.1 | — | **never reached** | ungraded |

Better than 10-16's 2-of-6; the structural half-the-table-out-of-reach problem
persists (**3 of 6 unreachable**).

## H18 / P1 — instance 21, duplication 26 of 26, and the "help" is a 9.3pt move

`macro +3` DFII10 and `macro +1` DGS10 both resolve to observation date
**2026-10-15**; the age warning printed on DFII10 and **not** on DGS10. **HY OAS
rendered no observation date for the 13th consecutive session.** `macro +4` was
the **only block on the right side of the day**.

Suppressing the stale pair takes **−5 → −9**: a bigger call, and bigger in the
**wrong day-net direction**. On the post-scan convention that is the gate's
**4th helping instance against 2 hurting** — but the 4th help is a **9.3-point**
move, so on any basis that respects magnitude the record is **3 helped / 2
hurt**. **A 3–2 or 4–2 split is not evidence. The accuracy case stays
RETRACTED**; the live defect remains the **rendering** one. **HY OAS is not dead
weight; that correction holds.**

## D22 — the Monday instance, and the configuration where it matters most

`breadth −3` (mega-cap avg −1.86%; **NDX −2.50% vs ES +0.49%**) and all four vol
rows are **Friday-close** readings presented at a Monday 08:48 ET scan; the NDX
cash reference itself was **3873 minutes** stale. The NDX/ES comparison cannot be
a like-for-like window on a Monday pre-open. **−9 of the −5's input points
describe a session that had already finished.** Instance recorded; nothing
proposed at n=1.

## D23 — 14th residual, and a FOURTH consecutive SIGN disagreement

Board **−3.9** vs section-7 **+364.1**, matched to feed time 11:59Z. Gap
**−368.0**; CFD move (11:55Z bar open **29542.1** → scan 29559.6) = **+17.5**;
**residual −385.5** — second-largest absolute in the series after +438.2.
Series: `+190.5 / −201.3 / +203.8 / −7.3 / +2.9 / +246.6 / +203.6 / +209.5 /
+345.4 / −68.0 / +165.0 / +438.2 / +33.6 / **−385.5**`. Damage none — no volume
had traded.

## Session-context field — 16th session, and it is the put wall again

Only **1 of 5** rows lay inside the pre-scan range 29112.1–29629.2 — the mildest
count in the series — but it is the **PUT WALL 29246.1**, published at −314 as
*"the strongest floor on the board"* after price had traded **134 points below
it** overnight (session low 29112.1 at 22:00Z). Free, arithmetic on data already
on the page, **proposed 09-30, still not actioned.** Nothing new should be added
before it is.

## P-B(b) — 16th session; ONE guaranteed window and it FIRED; inflation 1.33x

`merge_tol = max(3.0, 503.6 × 0.008) = **4.029**` against `TOUCH_TOL = **8.0**`.
The pair **(29646.1, 29638.9)** is **7.2** apart — inside the
structurally-guaranteed window — and **both graded touched at bar 195**.
Published rate **4/5 = 0.80**; distinct touch bars **3** (195, 204, 209) →
distinct-event rate **0.60**; **inflation 1.33x**. Proposal unchanged.

## Dead-weight audit — refreshed to n=33 PRE_NY `is_trading_day` scans (09-24 excluded by hand)

| row | scored |
|---|---|
| `events` | **0 / 33** |
| `macro` yield curve (10y–2y) | **0 / 33** |
| `rates` DXY | 4 / 33 |
| `macro` NFCI | 5 / 33 |
| `macro` WALCL/RRP | 6 / 33 |
| `rates` US10y | 25 / 33 |
| `macro` HY OAS | **26 / 33** |

The narrowed standing proposal (drop the yield-curve row and WALCL/RRP) is
**unchanged and still not actioned**.

## Appended without proposal

- **H22 — n=11.** Week net GEX **+1.123** → *"pinning likely"* → realised
  **1.364x ADR**. **The label was wrong.** Still no ordering. Standing oddity
  reaffirmed for the record: the same page carried `gamma +2` *"pinning likely"*
  while price sat **79.3pts below** the flip with regime text reading *"short
  gamma, don't fade"*. **Neither happened** — nothing pinned, and the rally was
  not unstable; the only half that paid was *"don't fade"*.
- **H4** — flip **29638.9** touched 14:15Z, acted as a barrier for one bar,
  price traded **160.1 above** and closed **79.5 below**. Not a settlement
  magnet. Instance against; claim already failed 09-16.
- **Max pain — 2nd within-reach SUCCESS, against six distance-confounded
  non-tests.** Published at +212 with *"**weak on a Monday**"*, on a Monday, and
  the session high **29799.0** printed **27.9 above it** before a 253.3pt
  reversal. **The day-of-week qualifier was wrong and max pain was the best
  level on the board** — while the page hedged it with `(stretch)` and a 0pt
  budget. (10-15 the other success; 10-16 the 6th non-test.)
- **The structural call wall was wrong twice.** *"The ceiling for the WEEK/MONTH,
  **not today**… not an intraday trigger"* — touched **2h12m after the scan** and
  sliced by **+102.9**. **P3/H6: 2nd structural touch in the record** (10-08 the
  first); the census stays split by side.
- **H19** — 51 headlines, **2** auto-scored (1 bull / 1 bear → NEUTRAL), 49
  needing context. Coverage **3.9%**.
- **H8 — ANSWERED-POSITIVE, not reopened; post-closure data only.** Straddle
  band **29152..29967**, close **29559.4 INSIDE**. On the same page the
  VXN-implied range **under-read** the realised range by **181.7**. Consistent
  with H8's verdict.
- **D25 — 27th consecutive pre-NY scan.** *"The dominant strike is **stable** at
  0 across 6 samples"*, printed under *"No volume has traded yet today"*.
  Damage none.
- **D26 — reporting gap, NOT data loss; the retraction stands.** `track.py`
  reports **29 trading days / 32 scans (deduped)**; on disk **36** day
  directories, **66** scan JSONs, **31** days with a PRE_NY scan, **30** with a
  `REVIEW.md` (31 after this review), **27** with both. `track.py` still prints
  no literal `actionable: YES/NO`; the threshold rule was applied by hand.
- **D7 / D15 — the degenerate marker again.** With a 0.0 budget **4 of 5** rows
  are marked `(stretch)`, which makes the marker uninformative. D7's exemption
  **did** work: the structural wall is the one row not marked.
- **D21 — no instance**, and a near-miss worth one line: `gamma +0`, price
  **78%** up the band, 2 points under the 80% threshold, on the day price ran to
  the top of the band.
- **No instance:** **H7** (no overnight scan) · **H10** (price inside the
  prior-week range 29073.7–31079.0; neither branch) · **H20**
  (CLOSED-NEGATIVE, not revived; no High/Medium events) · **D24**
  (`event_gate: null` correct; NFLX/META/TSLA all after the session) ·
  **P-F** (price inside the prior-day range 29073.7–30028.6) · **P-G** (the
  board carries no session-extreme rows; prev-day extremes appear only in the
  context line, which has no side-prose) · **H3** (CLOSED-NEGATIVE, superseded
  by H26).
- **No new data point is warranted.** The input that would have changed 10-19 is
  a **live** rather than Friday-close vol read, since the four stale vol rows
  cast **−6 of a −5 score** — but that is **1 day of evidence**, so nothing is
  proposed, and it is **not a new number** either: *"percent-changes are not
  guaranteed to be prior-session and the legs cover different windows"* is
  **D22**. **Watch item, no ID, 3 sessions needed:** do the vol rows' staleness
  and the Monday configuration coincide, and is there a free, reliable intraday
  vol proxy at 08:48 ET? Neither question is answered today.

## Carried forward from the 2026-10-20 scan — recorded, NOT graded

- **Board offset 74.5 — a FIFTH breach**, immediately after two clean readings
  (14.9 on 10-16, −3.9 on 10-19). Arithmetic verified independently and correct:
  NDX cash close 10-19 **29529.35**, roll **−187.0**, implied **29342.3**, CFD
  **29416.8** → **+74.45**. Series: 09-28 45.9 · 10-12 43.1 · 10-14 41.8 ·
  10-15 77.6 · **10-20 74.5**, with clean days interleaved. **This is
  intermittent, not a trend** — the time-trend model has now missed **four**
  sessions out of sample. **Mechanism remains unexplained. Nothing proposed, and
  no third story is substituted.**
- **The offset-vs-options-proximity tabulation — RUN, and it is NULL.** Nearest
  options-derived level at scan time on the five breach days: **127.9 · 0.4 ·
  206.7 · 11.1 · 257.7** (mean 120.8) against **75.9** across the 26 clean days
  — but the breach sample spans both the near-smallest and the largest value in
  the record. **No separation at n=5. Nothing proposed.** The structural
  observation stands on its own and is worth keeping: on 10-20 every level within
  212pts of price is session-derived (cTrader-native, offset-immune) and every
  options-derived level is **≥258pts** away, so the practical damage is far
  smaller than on 10-15, where the structural put wall sat **11pts** from price.
- **The pre-registered realised-close-basis log — observation 4 of 10.** NDX
  cash close 10-19 = implied 29342.3 − roll (**−187.0**) = **29529.3**; CFD close
  **29559.4**.

  | day | scan offset | NDX close | CFD close | realised basis | gap | NQ roll |
  |---|---|---|---|---|---|---|
  | 10-14 | +41.8 | 29950.82 | 29931.8 | −19.0 | 60.8 | −205.2 |
  | 10-15 | +77.6 | 29935.6 | 29885.3 | −50.3 | 128.0 | −389.8 |
  | 10-16 | +14.9 | 29187.5 | 29191.5 | +4.0 | +10.9 | +376.0 |
  | **10-19** | **−3.9** | **29529.3** | **29559.4** | **+30.1** | **+34.0** | **−187.0** |

  Second consecutive **positive** realised basis, and |roll| cuts the same way as
  10-16: the **smallest** |roll| in the log (187.0) produced a mid-sized gap
  while the **largest** (376.0) produced the smallest. **Re-test still at n=10
  clean observations. Nothing proposed.**
- **⚠️ The roll-parser defect is CONFIRMED and independently verified.** The
  register's own scratchpad extractor matches
  `NQ futures move \((-?[\d.]+)\)`, which cannot match `(+376.0)`. Across every
  PRE_NY scan there are **16 up-rolls and 16 down-rolls**, and **all 16 up-rolls
  were silently recorded as `None`** — exactly half the sample. The published
  claim *"r(offset, |roll|) = +0.039 within down-roll days"* is correctly
  **scoped**, but the down-roll sample was never a choice. **Any |roll|
  regression must be rebuilt with a sign-tolerant parse before being quoted
  again.** No scoring, wall or grading code is affected.

## Journal hygiene

One scan file for 10-19 (`1248-preny.json` + `.md`), `is_trading_day: true`,
`review_day` reports **0 test artefacts** for the day (6 across the record,
excluded by `track.py`). **09-24 quarantined by hand — 15th consecutive review
to carry it**; there is still no schema `quarantine` field and the 09-29 proposal
for one is reaffirmed, because `track.py` keeps 09-24 inside every statistic it
prints (direction **16 / 7 / 9** becomes **15 / 7 / 9** once 09-24 is removed).
**2026-10-13 has no journal directory — the scheduled scan never ran; nothing was
created, back-dated or inferred. 2026-10-20 is on disk but unfinished (180
bars), correctly held back by `track.py`, and excluded from every statistic
above** — including the axis-3 control, where its in-progress 44.1pt traversal
would have been the only *"fuel wins"* row. 09-09 and 09-25 still have no
`REVIEW.md` and none was created. **No `prediction` block was touched. No
scoring, wall or grading code was edited.** No fabricated or backfilled entries
found. **No new ID allocated by this review. Next free: H27 · D27 · P-I.**

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01M7sro1DKMp5T7EBDusm6pM

# 2026-10-21 review (grading 2026-10-20) — observations

## The gamma block was WRONG and outvoted — the FIRST instance that produced a call, and the outvote was right

| day | `gamma` | all other blocks | `gamma` − rest | published | realised post-scan |
|---|---|---|---|---|---|
| 10-08 | −5 | +4 | −9 | NEUTRAL / TWO-WAY | 671pt trend day |
| 10-09 | +4 | −6 | +10 | NEUTRAL / TWO-WAY | −35.3 = 0.07x ADR |
| 10-12 | −2 | +4 | −6 | NEUTRAL / TWO-WAY | −181.3 = 0.41x ADR |
| **10-20** | **−5** | **+9** | **−14** | **MILDLY BULLISH +4** | **+295.0 = 0.56x ADR, CORRECT** |

The first three are *"gamma right, outvoted into a no-call"*. **10-20 is a
different cell: gamma wrong, outvoted into a directional call, and the outvote
was right.** The pre-registered quantity (sign and size of `gamma` minus the sum
of all other blocks, against `|post-scan|/ADR`) **still does not order the
outcome**: 9, 10, 6, **14** against 1.5x, 0.07x, 0.41x, **0.56x** — the largest
margin on record produced a mid-sized move. **n=1 in the directional cell.
Nothing proposed.**

**Decomposition of the −5, because only one half of it deserved to lose.**
`−3` location (*"below flip 30051.1 by 634.3pts — downside accelerates, rallies
unstable"*) was **half right**: the downside did accelerate (205.0pts through
three pools in 57 min) and the rally was **not** unstable (509.8pts in 45 min,
closed 18.4 off the high). One sign is scored for two claims. `−2` was the
**week net GEX** row — see H22. **The flip was 634.3pts = 1.20x ADR away**, so
the row's own escape clause (*"reclaim and hold above and fading becomes
valid"*) was unreachable by construction against a 202.9pt budget, and the board
still printed the flip as an actionable line.

## H22 — the pre-registered DIRECTION test re-run on the current sample, and it has not moved

Same specification as the 10-09 run (`sign(week net GEX)` against realised
post-scan direction, P-H basis, 09-24 excluded, one PRE_NY scan per day, zero-move
days unusable): **15 right / 11 wrong = 58%, n=26 days** — the same 58% reported
at n=19. More data has not moved it. **Range side, n=12:** week net GEX
**−5.81** → *"expansion likely"* → realised **0.966x ADR**. **The label was
wrong again.**

**The point of logging it today:** a row whose direction content is measured
**null** and whose range label is measured **non-discriminating** cast **−2 of
the −5** that lost the vote on 10-20. H22's own counterfactual (zeroing the row
converts wrongs *and* rights into no-calls) is still why **nothing is proposed**.

## The direction call and the strategy block pointed opposite ways again — n=2, opposite gamma regimes

`MILDLY BULLISH +4` with **STRATEGY 2** — *"sweeps run rather than fail…
Strategy-1 fades have a materially lower hit rate here — only take them at the
far walls"* — and §2's *"Fading is the wrong trade today."*

The day's only sweep (pre-scan low **29297.7** taken out by **85.9** at
13:40–13:45Z, through three published pools) **failed and reversed 509.8
points**. The winning trade was a **Strategy-1 fade at 29211.8**, which is **not
a far wall** — the nearest named wall was **187.3 lower**.

This is the **second instance** of the cell the 10-14 entry opened and asked to
have extended rather than re-derived. **10-14: above the flip, MODERATE,
Strategy 1, bias +9 right, strategy block wrong. 10-20: below the flip,
MODERATE, Strategy 2, bias +4 right, strategy block wrong.** **n=2 in opposite
gamma regimes, both with the bias score right. Below threshold, nothing
proposed.**

**It is a caution on a LIVE proposal, which is the reason to write it down.**
**10-20 is `MODERATE` and is therefore NOT an H2 cell instance** — `track.py`'s
low-fuel list omits it, and it is **not** entered into that census, whose
pre-registered cell is `LOW_FUEL`/`EXHAUSTED` ∩ below the flip and whose result
stays **5–2 to gamma, 7–0 if ties go against the fade, FALSIFIED**. But 10-20 is
a day **below the flip** on which the fade was the only winning trade, by 509.8
points. **The live H2 proposal must stay scoped to `LOW_FUEL`/`EXHAUSTED`;
today is evidence against generalising it to "below the flip" as such.**

## The duplication-collapse measurement, run across the whole record — and it does not support a weight change

Prompted by the 10-21 scan: **−7** with **−4 from a single FRED observation**
(DFII10 −3 + DGS10 −1) and **−2 from one UK CPI headline carried by two
outlets**, leaving **−1 of independent signal**. **Rules fixed in writing before
any outcome was inspected:** one PRE_NY `is_trading_day` scan per day, 09-24
excluded, 10-21 excluded as ungraded (**n=26 graded days / 19 calls**);
collapse (a) = DFII10/DGS10 become **one row, the larger |points| one kept**;
collapse (b) = duplicate scored headlines become **one event**, raw scaled by
`events / headlines`, `bias_points = clamp(round(raw/2), ±4)`.

| basis | C | W | no-call | rate | labels changed | sides changed |
|---|---|---|---|---|---|---|
| **published** | 13 | 6 | 7 | **68.4%** | — | — |
| **collapse pair → 1 row** | 13 | **5** | 8 | **72.2%** | **4 / 26** | **1 / 26** |
| **drop the pair entirely** | 13 | **7** | 6 | **65.0%** | **21 / 26** | **7 / 26** |

- **The double-count is structurally real and large:** the pair contributes
  exactly **±4 on 29 of 34 scans** and ±1 on the other five; **|pair| ≥ |score|
  on 9 of 26 graded days**; on 10-20 **|pair|/|score| = 1.00**, i.e. the pair is
  the entire margin of the call.
- **It is nearly inert on direction.** The minimal dedup moves the printed label
  on 4 of 26 days and the **side on one** (09-30, WRONG → no-call). The
  3.8-point gain is **one day** — not evidence, nothing proposed.
- **The aggressive version is WORSE: 13/20 = 65.0%**, 3 helps (09-25 and 10-08
  no-call→correct, 09-30 wrong→no-call) against **4 hurts** (09-29 and **10-20**
  correct→no-call, 10-01 and 10-02 no-call→wrong). **An independent whole-sample
  confirmation that H18/P1's accuracy case stays RETRACTED.**
- **The headline half has never yet touched a graded day.** Duplicate scored
  headlines occur on **2 of 35 PRE_NY scans in the record**: **09-24**
  (quarantined) and **10-21** (ungraded). On 10-21 the collapse takes news
  **−2 → −1** and the score **−7 → −5** (`BEARISH → MILDLY BEARISH`). **H19's
  match-count defect is confirmed in its purest form and is, so far, a
  label-only effect — on a UK CPI story scoring the Nasdaq.**
- **Limitation, stated rather than hidden:** on **2 of 35** scans the published
  news table holds fewer rows than were scored (09-11 13:24 **10 scored / 6
  shown**; 10-05 **7 / 6**) and the journal stores no per-headline list, so
  duplicate detection there is **incomplete and unrecoverable**.

**Where it lands:** the implied fix is the **rendering** one — one row per FRED
observation, observation date on every row — which is **already PROPOSED under
H18 / P1** and was grepped for before this was written. **No number taken, no
weight change proposed**, because the measurement says a weight change makes the
record worse.

## H18 / P1 — instance 22, duplication 27 of 27, and the age gate would have cost a 295-point call

`macro +3` DFII10 and `macro +1` DGS10 both resolve to observation date
**2026-10-16, two business days stale**; the age warning printed on DFII10 and
**not** on DGS10. **HY OAS rendered no observation date for the 14th consecutive
session.** Suppressing the stale pair takes **+4 → 0**: a **no-call** on a day
with a **+295.0** post-scan move. On the register's own convention the gate is
now **4 helped / 3 hurt**; on a magnitude-respecting basis **3 helped / 3
hurt**, today's hurt being **295pts** against a 4th help worth **9.3pts**.
**The accuracy case stays RETRACTED; the live defect remains the rendering
one.** **HY OAS is not dead weight** (27 of 34) — it was **wrong-signed** today
(3.31%, +20bp/5d, on a +295 day), which is a different complaint.

## H26 — n=26, bucket form holds, correlation form falls for a THIRD consecutive session

Method, stated per the 10-20 proposal: one PRE_NY scan per day,
`is_trading_day`, 09-24 excluded, no-call days **included** with their realised
values. **Reproduces the register exactly at n=25 (+0.548 / +0.190 and all four
bucket means)** before 10-20 is added.

| \|score\| | n | C | W | no-call | mean \|post\|/ADR | mean range/ADR |
|---|---|---|---|---|---|---|
| 0–2 | 7 | — | — | 7 | 0.181 | 1.103 |
| **3–5** | **6** | **4** | 2 | 0 | **0.254** (was 0.193) | **1.013** (was 1.023) |
| 6–9 | 7 | 6 | 1 | 0 | 0.545 | 1.193 |
| ≥10 | 6 | 3 | 3 | 0 | 0.783 | 1.390 |

Spearman(|score|, |post|/ADR) **+0.548 → +0.535** · range/ADR **+0.190 →
+0.191**. Means stay monotonic (0.181 / 0.254 / 0.545 / 0.783) for a 4th
consecutive session; the correlation has now fallen **three** sessions running
(+0.612 → +0.577 → +0.548 → +0.535). **10-20 is the cause: |score| 4 with
|post|/ADR 0.559**, a near-top-bucket move in the second-lowest bucket. 10-20 is
a **3–5 bucket instance, CORRECT** on the P-H basis. **The signed Spearman is
not quoted** — the live proposal (carry its method or stop quoting it) is
unactioned.

## P-H — 19 graded calls, and 10-20 is NOT a 6th deciding instance

Post-scan **+295.0 CORRECT**; day net **+138.9 CORRECT**. Both bases agree.

| basis | right | wrong | rate |
|---|---|---|---|
| post-scan (P-H) | **13** | 6 | **68.4%** (was 66.7%) |
| day net | **14** | 5 | **73.7%** (was 72.2%) |

Deciding set unchanged at **09-11, 09-16, 10-07, 10-15, 10-19 (n=5)**. The
convention's cost falls again, **5.5 → 5.3** points. Already PROPOSED 10-08; no
new proposal, no ID.

## P4 / H1 — n=30 days; one new data point, and the statistic is NOT re-derived

10-20 error **−17.7** (budget 202.9, extension 185.2) — the **5th-smallest
|error| in the record** and a **non-zero-budget** day, so not one of the seven
arithmetic-floor entries. `track.py` per-day mean **+54.3 → +51.9** (n=30, incl.
09-24); per-scan **+52.7** (n=33). **NOT re-derived:** claim stays **"no usable
skill"**, **multiplier branch closed**, and **pre-scan pace carries no
information in either direction — that question is closed** (today: `fuel_ratio`
**1.37 normal** → **0.966x ADR**, a third consecutive uninformative reading).
Traversal **509.8 = 2.51x** the budget, recorded once as the quantity the
deleted axis 3 was mis-measuring.

## M6 — session 28, and the "magnitude scales with travel" claim does NOT survive it

| level | grader travel | actual excursion | ratio | grader verdict |
|---|---|---|---|---|
| **29455.5 PD mid** | 27.8 up | **266.1** | **9.57x** | *"broke DOWN through it — **lost** by 32.5"* |
| 29395.0 Asia Low (today) | 56.8 up | **326.6** | 5.75x | *"**lost** by 55.8"* |
| 29384.3 Asia Low (prev-day) | 67.5 up | **337.3** | 5.00x | *"**lost** by 45.1"* |

**9.57x is the largest single-row ratio in the record** (10-16's worst was
8.2x), and all three rows closed **247.7–318.9 above** the level the grader says
they *lost*. **3 of 13 verdicts inverted.** The other ten rows read 1.00x up and
1.00–1.76x down.

**Session 27 said M6's magnitude scales with how far the day travelled; session
28 is a counter-instance with a mechanism.** Post-scan travel was **0.97x ADR**
against 10-16's **2.01x**, yet the worst ratio is larger. The driver is not
travel: these three rows were **first touched before the 13:45Z reversal**, so
the grader's window measured the leg that ended rather than the one that
mattered. Same family as the 10-19 settle-window finding, different direction.

## P5 — 5 of 6 gradeable, 3 right / 2 wrong, and the best level on the board was in this table

| shelf | force / contracts | printed claim | post-scan | verdict |
|---|---|---|---|---|
| 29424.5 (+8) | 0.85bn / 57,701 | *"amplify… accelerate THROUGH… Not a floor"* | through down, −212.7 then +297.1 | RIGHT (pre-scan contaminated, +8 from price) |
| 29374.5 (−42) | 0.32bn / 8,717 | same | through by 162.7 | **RIGHT** |
| 29574.5 (+158) | 0.43bn / 7,200 | same | sliced, **+147.1** | **RIGHT** |
| **29224.5 (−192)** | **0.42bn / 22,982** | same | **12.7 below it, then +497.1** | **WRONG** |
| 29274.5 (−142) | 0.46bn / 14,519 | same | 62.7 below, then +447.1 | **WRONG** |
| 29174.5 (−242) | 0.45bn / 5,599 | — | **never reached** (by 37.3) | ungraded |

**The 22,982-contract shelf located the session low to 12.7 points while its own
prose said it was not a floor** — and the named **PUT WALL 29024.5** was
**187.3 below the low**. **The secondary table beat the headline wall by 174.6
points on the side that mattered**, and it is still **graded by no tool**.
Census of gradeable sessions: 2/3 · 2/6 · 1/6 · 2/3 · **3/5**.

## P-E — instance 15, and the SECOND "middle" observation; P-E(b) 15th instance

**CALL WALL 29674.5** at **+258**, *"Heaviest ceiling this week (4k contracts) —
desks must SELL as price rises into it, so rallies stall. Take profit into it. A
held close above flips that selling to buying."* First post-scan touch
**14:25Z**, overshoot **+47.1** (high 29721.6 @14:30Z), then **−162.8** to
29511.7, then reclaimed; **closed +28.7 above**.

- **Clean on the contamination axis:** pre-scan high 29622.3 was **52.2 below**
  the wall.
- **Overshoot 47.1 is inside the 12–103 middle** → **second middle instance**
  after 10-06. Census → **5 capped / 2 middle / 8 sliced**. The two-mode framing
  stays retired; the continuum-with-a-thin-middle reading is now better
  supported.
- **Both sentences came true four hours apart, worst-first.** That is exactly
  what P-E's existing prose proposal asks to reorder. **Nothing new proposed.**
- **P-E(b) — 15th instance** (the 10-19 supporting instance was unnumbered and
  is counted as the 14th): the shelf family again located the extreme better
  than the headline wall, this time on the **put** side by **174.6 points**. See
  P5 above.

## D23 — 15th residual, and a FIFTH consecutive SIGN disagreement

Board **+74.5** vs section-7 **−191.3**, matched to feed time 11:59Z. Gap
**+265.8**; CFD move (11:55Z bar open **29345.1** → scan **29416.8**) =
**+71.7**; **residual +194.1** — back inside the ±200 band after the −385.5
excursion. Series: `+190.5 / −201.3 / +203.8 / −7.3 / +2.9 / +246.6 / +203.6 /
+209.5 / +345.4 / −68.0 / +165.0 / +438.2 / +33.6 / −385.5 / **+194.1**`.
**Damage none** — no volume had traded.

## The realised-close-basis log — observation 5 of 10, and it contains an impossibility

NDX cash close 10-20 = implied **29698.8** (10-21 scan) − roll (**+208.5**) =
**29490.3**; CFD close **29703.2**.

| day | scan offset | NDX close | CFD close | realised basis | gap | NQ roll |
|---|---|---|---|---|---|---|
| 10-14 | +41.8 | 29950.82 | 29931.8 | −19.0 | 60.8 | −205.2 |
| 10-15 | +77.6 | 29935.6 | 29885.3 | −50.3 | 128.0 | −389.8 |
| 10-16 | +14.9 | 29187.5 | 29191.5 | +4.0 | +10.9 | +376.0 |
| 10-19 | −3.9 | 29529.3 | 29559.4 | +30.1 | +34.0 | −187.0 |
| **10-20** | **+74.5** | **29490.3** | **29703.2** | **+212.9** | **+138.4** | **+208.5** |

**Third consecutive positive realised basis and by far the largest — and it
implies something that is not a market fact:** NDX cash **−39.1** on 10-20
while the CFD rose **+143.8** from the prior close, a **183-point one-session
divergence** between a cash index and a CFD that tracks it. **One of the two
inputs is wrong: the 16:14:59 cash print or the +208.5 roll.** This is the
second up-roll in the log, and the register's own extractor **cannot parse
up-rolls at all** (16 of 32 silently `None`), so **no |roll| regression may be
quoted until it is rebuilt sign-tolerant**. Re-test still at **n=10 clean
observations. Nothing proposed, and no mechanism is asserted at n=1.**

## Board offset — fifth breach, and for the first time it can be followed to the close

**74.5, verified independently and correct** (NDX cash 10-19 **29529.35**, roll
**−187.0**, implied **29342.3**, CFD **29416.8** → **+74.45**); **no contract
roll**. Series: 09-28 45.9 · 10-12 43.1 · 10-14 41.8 · 10-15 77.6 · **10-20
74.5**, with clean days interleaved — **intermittent, not a trend**; the
time-trend model has now missed **five** sessions out of sample. **The
offset-vs-options-proximity hypothesis was NULL at n=5 and is NOT revived.**

**The one new fact:** the breach **did not mean-revert intraday** — the realised
close basis was **+212.9**, nearly triple the scan figure. On the only other
breach day with a logged close (10-15, offset +77.6) the basis **crossed zero**
to **−50.3**. **Two breach days, gaps 128.0 and 138.4, opposite directions.
n=2, mechanism still unexplained, nothing proposed, no third story
substituted.** Practical damage small: every level within **212pts** of price
was session-derived (cTrader-native, offset-immune), every options-derived level
**≥258pts** away.

## Session-context field — 17th session, and the mildest-consequence instance in a while

**11 of 19** board rows lay inside the pre-scan range **29297.7–29622.3** — the
highest count in the series — but none of them was a wall, so the consequence is
clutter rather than a false claim. Free, arithmetic on data already on the page,
**proposed 09-29, still not actioned.**

## P-B(b) — 17th session; TWO guaranteed windows, one FIRED; inflation 1.44x

`merge_tol = max(3.0, 527.5 × 0.008) = **4.22**` against `TOUCH_TOL = **8.0**`.
**(29615.7, 29622.3)** is **6.6** apart — inside the structurally-guaranteed
window — and **both graded touched at bar 196: FIRED**. **(29622.3, 29629.2)**
is **6.9** apart, touched at bars 196 and 197, **did not fire**. Published
**13/19 = 0.684**; distinct touch bars **9** → distinct-event rate **0.474**;
**inflation 1.44x**, the second-worst in the series. Proposal unchanged.

## P-G — instances #24 and #25, the same mirror as #14/#15

**29480.8 London Low (prev-day)** at **+64.0** and **29469.3 NY Low (prev-day)**
at **+52.5**, both printed *"the next session usually runs the stops **below**
it"* while sitting **above** price. Both then **held as support for 415
minutes** on the way back up — right levels, wrong-sided prose. Prose only,
already PROPOSED, free, still not actioned.

## D18 — 8th trading day, 14th headline instance: a price target tagged as an earnings miss

The **sole** auto-scored headline: *"Apple Stock Escaped the AI Downturn. Now It
Faces a **27% Plunge**, Says **Analyst**"* → tagged **[earnings_miss]**,
rendered *"Mega-cap miss/warning → index-weighted drag"*, 🔴 bear, ~170pts /
180min, on a day that rose **295** post-scan. **It is an analyst price target,
not an earnings miss, and Apple had not reported.** The sub-shape is new: not a
negation failure (D18's usual form) but a **category** error. **Damage none** —
raw −0.51 → **0** points. **H19 coverage 1 / 133 = 0.75%**, the lowest non-zero
reading in the record (133 headlines → 44 relevant → 1 scored).

## The corridor read is gradeable, and it split — 6th session, nothing revived

*"DOWNSIDE path: clear to 29024.5 (392pts, 0.74x ADR) — nothing structural to
slow a breakdown… Do not fade it"*: the breakdown **stopped 187.3 short** of the
terminus and **reversed 509.8**. *"UPSIDE path: clear to 29624.5 (208pts)"*:
price ran **97.1 beyond** the terminus. Consistent with the **10-16 withdrawal**
(`brief.py:520` sets `corridor_end = span[-1]`, the far end of the shelf list,
not a barrier). **The corridor-terminus proposal stays WITHDRAWN and is not
revived.**

## Dead-weight audit — refreshed to n=34 PRE_NY `is_trading_day` scans (09-24 excluded by hand)

| row | scored |
|---|---|
| `events` | **0 / 34** |
| `macro` yield curve (10y–2y) | **0 / 34** |
| `rates` DXY | 4 / 34 |
| `macro` NFCI | 5 / 34 |
| `macro` WALCL/RRP | 6 / 34 |
| `rates` US10y | 26 / 34 |
| `macro` HY OAS | **27 / 34** |

The narrowed standing proposal (drop the yield-curve row and WALCL/RRP) is
**unchanged and still not actioned**. The count includes the **10-21** scan,
which is ungraded — this audit counts rows, not outcomes.

## Appended without proposal

- **H23 — NO instance.** Both paths were flagged **clear**, so `path_read()`
  named no brake. Census stays **10 sliced / 2 capped / 3 never-reached** and the
  **force-ranking branch stays CLOSED as unfalsifiable**. **Trap re-flagged so
  no one opens a defect:** the secondary table is built from `walls_ranked`
  (`brief.py:647`), `path_read()` reads `largest_abs_gex` (`brief.py:515`) —
  **different lists**.
- **No `PIN_THEN_EXPAND` instance:** `expiry_shape` was `COHERENT_SHORT`
  (confidence high, today −3.169 / week −5.81 / 45-day −10.804). The shape fired
  again on **10-21** — **observation 2 of 3**, to be graded tomorrow on the
  10-19 rules **as written and unrevised**.
- **Axis 3 — no score quoted, today's included.** The 10-16 specification is a
  near-constant (9 of 9 conflict days, 15 of 16 control days) and the column is
  to be **deleted, not re-scored**.
- **The whole realised move was over by 10:30 ET** (low 29211.8 @13:45Z, high
  29721.6 @14:30Z, then **390 minutes** inside 29511.7–29721.6, close 18.4 off
  the high, **96.4%** up the range). On 10-19 the move finished at **11:35 ET**.
  **n=2. Watch item, no ID, 3 sessions needed**, and it is deliberately **not**
  folded into the `PIN_THEN_EXPAND` test, whose sample is pre-registered.
- **The pool rows were the best part of the board.** All three published pools
  below price were run and reversed — Asia Low (today) by 55.8, Asia Low
  (prev-day) by 45.1, **London Low (today) by 89.5, which is the session low to
  the point**. **Equal highs ×2 at 29600.1**, printed as *"a real stop cluster.
  Prime S1 sweep trigger"*, was crossed inside the impulse, **never traded back
  down to**, and produced no stall: the named S1 trade there would have lost.
- **`structure`'s pool counter and the board disagree about what a pool is.**
  The row read *"in-reach unmitigated pools: **4 above / 0 below** — draw
  higher"* (**right**) while the board listed **three** pool rows below price,
  all three of which were then swept. Two definitions, one page. Noted, no
  number taken.
- **D22 — Tuesday instance, suspect row RIGHT.** `breadth +1` from **NDX +1.17%
  vs ES −0.29%**: the legs do not cover the same window even on a Tuesday. The
  row was on the right side of a +295 day. Logged so the census is not only
  populated by days the defect cost something.
- **H8 — ANSWERED-POSITIVE, not reopened; post-closure data only.** Straddle
  band **29132 .. 29701**, close **29703.2** — **outside by 2.2 points**, the
  narrowest miss available. On the same page the VXN-implied range **473.6**
  under-read the realised **509.8** by 36.2.
- **D25 — 28th consecutive pre-NY scan.** *"The dominant strike is **stable** at
  0 across 6 samples"*, four lines under *"No volume has traded yet today"*.
  Damage none.
- **D26 — reporting gap, NOT data loss; the retraction stands, and today it did
  NOT eat the day.** `track.py` reports **30 trading days / 33 scans (deduped)**
  and graded 10-20 on the same date `review_day` did — the **first session in
  four with no eaten evidence**. On disk: **37** day directories, **67** scan
  JSONs, **32** days with a PRE_NY scan, **31** with a `REVIEW.md` (**32** after
  this review), **28** with both. `track.py` still prints **no literal
  `actionable: YES/NO`**; the threshold rule was applied by hand.
- **Max pain** — published at **+397.7**, never reached: **7th
  distance-confounded non-test**, and the day-of-week qualifier was untested.
  **P3 / H6** — the structural call wall was **357.7** away and untouched;
  census unchanged.
- **No instance:** **H4** (flip 634.3 away, never reached) · **H7** (no
  overnight scan) · **H10** (price inside the prior-week range
  29073.7–31079.0; neither branch) · **H17** (post-scan 295.0 = **57.9%** of
  the session range; stays **2 of 3**) · **H20** (CLOSED-NEGATIVE, not revived;
  no High/Medium events) · **D21** (near-miss only: `gamma +0` at **60%** up the
  band, 20 points under the threshold, on a day price closed **above** the band
  top) · **D24** (`event_gate: null` correct; NFLX/META/TSLA all after the
  session) · **P-F** (price inside the prior-day range 29112.1–29799.0) ·
  **H3** (CLOSED-NEGATIVE, superseded by H26) · **the fuel-vs-gamma census**
  (`MODERATE`, outside the cell).
- **No new data point is warranted.** The call was **right**; what failed was the
  **weighting of rows already on the page** — a two-business-day-stale pair
  carrying the entire margin, a range row casting direction points, and a regime
  row whose escape clause sat 1.20x ADR away. No free, reliable feed fixes any of
  those, and proposing one to paper over a weighting problem is how the model
  gets worse.

## Journal hygiene

One scan file for 10-20 (`1248-preny.json` + `.md`), `is_trading_day: true`,
`review_day` reports **0 test artefacts** for the day (6 across the record,
excluded by `track.py`). **09-24 quarantined by hand — 16th consecutive review
to carry it**; there is still no schema `quarantine` field and the 09-29
proposal for one is reaffirmed, because `track.py` keeps 09-24 inside every
statistic it prints (direction **17/7/9** becomes **16/7/9** once 09-24 is
removed). **2026-10-13 has no journal directory — documented, not recreated.**
09-09 and 09-25 still have no `REVIEW.md` and none was created. **2026-10-21 is
on disk, `is_trading_day: true`, 180 bars, correctly held back by `track.py`,
and is excluded from every outcome statistic above.** **No `prediction` block
was touched. No scoring, wall or grading code was edited.** No fabricated or
backfilled entries found. **No new ID allocated by this review. Next free:
H27 · D27 · P-I.**

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01M7sro1DKMp5T7EBDusm6pM

---

# Appended 2026-10-22 — grading 2026-10-21 (Wednesday)

Full working in `journal/2026-10-21/REVIEW.md`. Call **BEARISH −7** at 29664.2;
post-scan **+172.7 WRONG**, day net **+90.1 WRONG**. Session O 29749.4 /
H 29936.0 / L 29550.0 / C 29839.5, range 386.0 = **0.720x** ADR14 535.8.
`track.py`: **31 trading days / 34 scans**, direction **17/8/9** → **16/8/9**
ex-09-24, levels touched **0.52**.

## The pre-registered `PIN_THEN_EXPAND` test — RUN AS WRITTEN, FALSIFIED, observation 2 of 3

| window | range | abs net | high | low |
|---|---|---|---|---|
| **pre** 13:30–17:00Z | **329.5** | 194.4 | 29924.7 @16:40 | 29595.2 @13:40 |
| **post** 17:00–20:55Z | **226.1** | 51.4 | 29936.0 @17:20 | 29709.9 @19:00 |

Clause 2 fails (post **226.1 < 329.5**); its second limb passes in isolation —
the day closed up and the high was set at 17:20Z, after the split — but clause 2
is an AND. **Clause 3 fires on its first limb** (pre window holds the larger
range); its second limb does not (low 10:15Z, high 17:20Z). **FALSIFIED.**
**Secondary:** one sweep of the pre-scan high **29832.5** at **15:35Z**
(**+33.8**), **not** closed back inside within 30 min and extended to **+92.2**
inside the same pre-17:00 window — **the breakout ran, against the claim**; the
pre-scan low was never swept (45.2 above it). **194.4 of the directional move
happened before the pin was said to weaken and the post window gave 51.4 back.**
**Observation 2 of 3; per clause 5 no verdict attaches and nothing is proposed.**
Difference worth carrying: 10-19 failed with both extremes early, 10-21 fails
with the **high late but the range early** — the shape's range claim and its
timing claim have now come apart twice in the same direction.

## Headline duplication — the FIRST graded instance, and it does not change the verdict

10-21 is the first **graded** day carrying duplicate scored headlines (09-24 is
quarantined). Graded directly; the 10-20 table is **not** re-derived.

| basis | news pts | score | label | direction | call |
|---|---|---|---|---|---|
| published | −2 | **−7** | BEARISH | −1 | **WRONG** |
| collapse (b) | −1 | **−5** | MILDLY BEARISH | −1 | **WRONG** |

**Label changes, side does not, verdict does not.** Duplicate scored headlines
now occur on **3 of 36** PRE_NY scans. **The headline half has touched one
graded day and bought nothing.** The weight change stays **refuted** (pair
collapse 72.2% vs 68.4% on one day's difference; dropping the pair 65.0%,
worse). The live item is the **rendering** proposal under **H18 / P1**.

## H18 / P1 — instance 23, duplication 28 of 28, and the stale pair outvoted the LIVE read of the same instrument 4-to-1

`macro −3` DFII10 (obs **2026-10-19**, two business days stale, ⚠️ printed) and
`macro −1` DGS10 (same **10-16 → 10-19** window, **no ⚠️**), against `rates +1`
*"US10y **5.094 (−0.45%)** — yields **down**, BULLISH tech"* — **opposite signs
on the same instrument, and the live one was right.** **HY OAS rendered no
observation date for the 16th consecutive session** and was wrong-signed.

**The standing proposal would not have saved the day, which is the finding:**
suppress DGS10 when a live US10y exists → **−6, still WRONG**; age-gate the
whole pair → **−3, still WRONG**; headline dedup alone → **−5, still WRONG**;
**dedup AND age gate together → −2, no-call.** Only the combination converts
it, and fitting a combination to one session is how the model gets worse.
Age gate running: raw **4 helped / 3 hurt / 1 no-change**; magnitude-respecting
**4 helped / 3 hurt**. **The accuracy case stays RETRACTED.**

## D9 — second instance, and the first that actually SCORED

Both auto-scored headlines are the same story — *"UK inflation rise to highest
in almost a year as Iran war drives fuel prices higher"* — tagged `cpi_hot` and
cast **−2** against the **Nasdaq 100**. The keyword matched without any test of
**whose** inflation it was. D9's 09-10 instance fell into NEEDS_JUDGEMENT and
cost nothing; this one cast 2 of the 7 points of a wrong call. **n=2, recorded
so it is counted rather than rediscovered. Nothing proposed** — D9's own entry
says this is not a case for more regex.

## The structural call wall printed inside its own offset — the day CANNOT grade it

**29665.4 at +1.2 on a −34.6 board offset: the level's uncertainty is 29x its
published distance from price.** The directly observable basis for the same
session is **+17.0**, so the true CFD location could be ~**51.6** away.
`review_day`'s *"stalled at it — held as support for 380min"* is **void and must
not be quoted.** **Third instance** of a board level printing inside its own
offset (10-12, 10-16) and the **second consecutive** one. **P3 / H6's structural
census cannot take this day** — 3rd structural touch in the record, 2nd
ungradeable in a row. `|px − flip| < |offset|` **stays n=1 (10-12)**: 38.6
against 34.6, outside by **4.0**, the closest approach since.

## H23 — instances 16 and 17, the first session with BOTH named brakes reachable, and they SPLIT

| brake | dist | first touch | run-through | verdict |
|---|---|---|---|---|
| **29615.4 MAX PAIN** | −49 | 13:40Z | only **20.2** beyond, then +320.6 | **CAPPED** |
| **29715.4 Options shelf 0.25bn** | +51 | 13:00Z | **+220.6** beyond | **SLICED** |

Census **10/2/3 → 11 sliced / 3 capped / 3 never-reached** (n=17). Force-ranking
branch stays **CLOSED as unfalsifiable**; corridor-terminus proposal stays
**WITHDRAWN** (`brief.py:520`). **Trap re-flagged:** the board prints options
shelves at **+51 / +151 / +201** and the secondary table prints **+101 / +301** —
`walls_ranked` (`brief.py:647`) vs `largest_abs_gex` (`brief.py:515`).
**Different lists; not a skipped brake.**

## M6 — session 29, the LARGEST ratio in the record, and travel-scaling fails a SECOND time

| level | grader travel | actual excursion | ratio | grader verdict |
|---|---|---|---|---|
| **29742.1 London High** | 14.1 up | **193.9** | **13.75x** | *"broke DOWN — **lost** by 32.2"* |
| 29730.1 Equal highs ×4 | 26.1 up | **205.9** | 7.89x | *"**lost** by 30.3"* |
| 29703.2 PD close + flip | 33.9 up | **232.8** | 6.87x | *"**lost** by 50.1"* |
| 29622.3 Asia High (prev-day) | 133.9 up | **313.7** | 2.34x | *"**lost** by 27.1"* |

**13.75x beats session 28's 9.57x.** All four closed **97.4–217.2 above** the
level they are said to have *lost*; **4 of 13 verdicts inverted**, the highest
count yet. Post-scan travel was **0.64x ADR**, *below* session 28's 0.97x and
far below 10-16's 2.01x — **so session 27's "magnitude scales with travel" claim
is NOT restated as established; it now has two consecutive counter-instances.**
The driver is **window placement**: all four rows were first touched
**13:25–13:40Z**, inside the 52-minute morning flush, so the 12-bar window closed
before the 13:40Z reversal. Control that proves it: **29715.4** carries a
**10.17x** up-ratio and its verdict (*"held as support"*) is **correct**.

## D23 — 16th residual, SIXTH consecutive sign disagreement, and a coincidence flagged

Board **−34.6** (NDX reference 29698.8 vs CFD 29664.2) vs section-7 **+194.1**,
matched to feed time 11:59Z. Gap **−228.7**; CFD move (11:55Z bar open
**29698.8** → scan **29664.2**) = **−34.6**; **residual −194.1**. Series:
`+190.5 / −201.3 / +203.8 / −7.3 / +2.9 / +246.6 / +203.6 / +209.5 / +345.4 /
−68.0 / +165.0 / +438.2 / +33.6 / −385.5 / +194.1 / **−194.1**`.
**⚠️ Today's residual is the exact negative of yesterday's only because the
11:55Z CFD bar opened at 29698.8, the same number to 0.1 as the NDX reference.
That is a coincidence, not a relationship.** Damage **none**. **Board offset
−34.6 is NOT a breach**; the breach series stays at five.

## The realised-close-basis log — observation 6 of 10, and 10-20's impossibility recurs MIRRORED

NDX cash close 10-21 = implied **29345.3** (10-22 scan) − roll (**−477.2**) =
**29822.5**; CFD close **29839.5**.

| day | scan offset | NDX close | CFD close | realised basis | gap | NQ roll |
|---|---|---|---|---|---|---|
| 10-14 | +41.8 | 29950.82 | 29931.8 | −19.0 | 60.8 | −205.2 |
| 10-15 | +77.6 | 29935.6 | 29885.3 | −50.3 | 128.0 | −389.8 |
| 10-16 | +14.9 | 29187.5 | 29191.5 | +4.0 | +10.9 | +376.0 |
| 10-19 | −3.9 | 29529.3 | 29559.4 | +30.1 | +34.0 | −187.0 |
| 10-20 | +74.5 | 29490.3 | 29703.2 | +212.9 | +138.4 | +208.5 |
| **10-21** | **−34.6** | **29822.5** | **29839.5** | **+17.0** | **+51.6** | **−477.2** |

10-20 implied NDX **−39.1** against CFD **+143.8** (−183 divergence); 10-21
implies NDX **+332.2** against CFD **+136.3** (**+195.9**). **They nearly
cancel.** A wrong *roll* would not self-reverse the next session; a single bad
**cash anchor on 10-20** produces exactly this ± pair, which points the
suspicion at the **16:14:59 print on 10-20** rather than at the roll — **n=2, no
mechanism asserted.** Re-test still at **n=10**. The register's roll parser is
still sign-blind; **no |roll| regression may be quoted.**

## H26 — n=27, and the 6–9 bucket takes its SECOND miss

|score| **7**, |post|/ADR **0.322**, range/ADR **0.720**, **WRONG**. Bucket 6–9
**6/7 → 6/8**; mean |post|/ADR **0.545 → 0.517**, range/ADR **1.193 → 1.134** —
**arithmetic off the published rounded means, NOT a re-derivation from source,
and flagged as such.** Means stay monotonic (0.181 / 0.254 / 0.517 / 0.783) for
a 5th session. **The Spearman statistics are not re-derived this session and the
signed one is still not quoted;** the live proposal (carry its derivation or stop
printing it) remains unactioned.

## P4 / H1 — n=31 days; one new data point, and the statistic is NOT re-derived

10-21 error **−149.8** (budget **253.3**, extension **103.5**) — **3rd-largest
over-estimate** in the record, on the **2nd-largest budget** ever published.
`track.py` per-day mean **+51.9 → +45.4** (n=31, incl. 09-24); per-scan **+46.7**
(n=34). Claim stays **"no usable skill"**, multiplier branch **closed**,
**pre-scan pace CLOSED** (`fuel_ratio` **1.17 normal** → **0.64x ADR**, a
**fourth** consecutive uninformative reading). **Two tempting stories checked and
killed rather than proposed:** (a) *"big budgets over-read"* — the eight
budget≥200 scans score +114.6 / +25.9 / −75.2 / −66.5 / −180.1 / **+479.3** /
−17.7 / −149.8, mean +16.3, both tails present, **no separation**; (b) *"use the
VXN-implied range as the budget"* — it would have halved today's error, but the
register's own log has it **over** (today +85.3) and **under by 405.5 and 524.1**
on other sessions. **Neither is a rule.**

## Appended without proposal

- **H8 — ANSWERED-POSITIVE, not reopened; post-closure data only.** Band
  **29422 .. 29906**, close **29839.5 INSIDE**. VXN-implied **471.3**
  **over-read** the realised **386.0** by **85.3** — first over-read in three
  sessions.
- **H22 — no re-run.** Week net GEX **+1.607 → *"pinning likely"***; realised
  **0.720x ADR**, the quietest session in five, so the **range label is RIGHT at
  n=13**, its first right reading in several. Direction half stays **15/11 = 58%
  at n=26, not re-derived.** The row cast **+2** inside a gamma block that netted
  **0**.
- **Score/prose contradiction in the gamma block — second consecutive day.**
  `gamma +2 "pinning likely"` (a range claim scored as direction) beside §2's
  *"short gamma… Fading is the wrong trade today."* Carried under **H22**, which
  owns the row. **No number, nothing proposed.**
- **`gamma +2` bottom-of-band branch did NOT fire on 10-21** (`gamma +0`, price
  **60% up the band** — the same near-miss value as 10-20, two sessions running
  20 points under the D21 threshold). **It fired on the 10-22 scan, 5th firing;
  carried forward, not graded.**
- **P5 — 0 of 1 gradeable, and P-E(b) instance #16.** **29765.4 (+101, 0.40bn)**
  promised a stall and was **sliced by +170.6**: **WRONG**. **29965.4 (+301)**
  never reached — yet it sat **29.4 above the session high** while the nearest
  *board* row above price was **70.6 below** it. **The secondary table beat the
  headline board on the side that mattered by 41.2 points, upside this time, and
  is still graded by no tool.** Census: 2/3 · 2/6 · 1/6 · 2/3 · 3/5 · **0/1**.
- **P-E — NO instance.** CALL WALL at **+401**, never reached, **129.4 above the
  session high**.
- **P-G — instances #26 and #27.** *"the next session usually runs the stops
  **above** it"* on **29622.3 Asia High (prev-day)** at **−42** and **29537.6
  London High (prev-day)** at **−127**, both **below** price. #26 held as support
  and closed **217.2 above** — right level, wrong-sided prose; #27 never reached.
  Prose only, already PROPOSED, free, still not actioned.
- **P-B(b) — 18th session; THREE guaranteed windows, one FIRED; inflation
  1.44x.** `merge_tol = max(3.0, 535.8 × 0.008) = **4.29**` vs `TOUCH_TOL =
  **8.0**`. **(29622.3, 29615.4)** 6.9 apart → both at **bar 188: FIRED**, the
  **same pair that fired on 10-20**; **(29822.3, 29815.4)** 6.9 apart → bars
  210/209, no; **(29721.6, 29715.4)** 6.2 apart → bars 185/180, no. Published
  **13/23 = 0.565**; distinct touch bars **9** → **0.391**; **inflation 1.44x**,
  identical to 10-20.
- **Session-context field — 18th session, highest count in the series.** **14 of
  23** rows inside the pre-scan range **29550.0–29832.5**, and unlike 10-20 **one
  of them is a structural wall** — the one that cannot be graded. Proposed 09-29,
  still not actioned.
- **Max pain — first properly reachable test in eight sessions.** Published at
  **−49**, reached, **located the post-scan low to 20.2 points**, then left by
  **320.6** to close **224.1 above**. **A floor, not the "drift magnet" its prose
  claims.** Day-of-week qualifier untested on a Wednesday. **n=1.**
- **The engine's best rows were outvoted 8-to-3.** `structure +1` *"in-reach
  unmitigated pools 4 above / 2 below — **draw higher**"*, `structure +1` *"above
  PD mid"* and `rates +1` were all correct. **This is NOT the *"gamma outvoted"*
  cell — gamma netted 0 and was not a voter.** `vol −1` (VXN/VIX) and
  `breadth −1` (NDX vs ES) were both wrong-signed, both measured on a pre-market
  tape the cash session reversed.
- **D25 — 29th consecutive pre-NY scan.** *"The dominant strike is **stable** at
  0 across 6 samples"*, two lines under *"No volume has traded yet today"*.
  Damage none.
- **D26 — reporting gap, NOT data loss; the retraction stands, with a CHANGED
  SYMPTOM.** `track.py` reports **31 trading days / 34 scans**, window opening
  **09-08**. On disk: **38** day directories, **68** scan JSONs, **33** days with
  a PRE_NY scan, **32** with a `REVIEW.md` (**33** after this review), **29** with
  both (**30** after). The six August directories (08-23 … 08-28) are aged out of
  the 45-day bar window and are **no longer filed as *"not finished"*** —
  `review_day` returns no `scans` key and `track.py:84` `continue`s, so they are
  now **silently invisible**: absent from the table, from `HELD BACK` and from
  `excluded`. 38 − 6 = 32 = 31 graded + 1 held back, which reconciles exactly.
  `track.py` still prints **no literal `actionable: YES/NO`**; the threshold rule
  was applied by hand.
- **No instance:** **H2** (`MODERATE`, correctly absent from `track.py`'s
  low-fuel list; **H2 stays FALSIFIED at n=7, its proposal stays scoped to
  `LOW_FUEL`/`EXHAUSTED`, axis 3 is deleted not scored**) · **H3**
  (CLOSED-NEGATIVE, superseded by H26) · **H4** (flip reached and broken, close
  **136.3** away — consistent with the existing negative verdict) · **H7** (no
  overnight scan) · **H10** (price inside the prior-week range; neither branch) ·
  **H17** (post-scan **44.7%** of session range; **stays 2 of 3**) · **H20**
  (CLOSED-NEGATIVE; no High/Medium events) · **D21** (near-miss, 60% up the
  band) · **D24** (`event_gate: null` correct; META and TSLA both after the
  close) · **P-F** (price inside the prior-day range) · **the fuel-vs-gamma
  census** (`MODERATE`) · **the *"direction right, strategy block wrong"* cell**
  (bias was wrong; **stays n=2**) · **the *"whole move over by 10:30 ET"* watch
  item** (**counter-instance** — the high landed at 13:20 ET; it does not extend).
- **No new data point is warranted.** The call failed on the **vintage and
  double-counting of rows already on the page** — a two-business-day-stale pair
  outvoting the live read of the same instrument 4-to-1, and one foreign CPI
  story counted twice. No free, reliable feed fixes either.

## Carried forward from the 2026-10-22 scan — recorded, NOT graded

- **⚠️ NEW FAILURE MODE: `gexbot` HTTP 401 on `/v2/NDX/classic/gex_full`.**
  Section 7 suppressed in full with *"[volume-weighted view unavailable: HTTP 401
  on /v2/NDX/classic/gex_full]"*. **Recorded as a SUCCESS: the brief degraded
  cleanly rather than fabricating a level.** **The register has no prior entry
  for a gexbot auth failure** — **H12/H13** are claims about gexbot's *data*, not
  failure modes, and **D17** is a CBOE **429**, transient and already fixed by
  retry. **A 401 is auth/endpoint and will recur.** Logged at **n=1**; **no fix
  to credentials or code is proposed.**
- **Side effect 1 — the archive lost TWO files, not one.** Commit `a7cf136`
  carries **4 files against the usual 6**; the missing pair is
  `research/gexbot/ladders/2026-10-22-1248-oi.json` **and** `-vol.json`.
  `gexbot.persist_ladder()` fetches `gex_full` for **both** weightings
  (`gexbot.py:219`), so one 401 costs the **open-interest** ladder too, while the
  printed message names only the *volume-weighted* view. **The degradation
  message under-reports what was lost.** n=1.
- **Side effect 2 — D25 did not print on 10-22, for the wrong reason.** The false
  *"dominant strike is stable at 0"* sentence was absent because the **whole
  section was suppressed**, not because the unguarded render was fixed. **D25 is
  interrupted by an outage, not resolved; the counter resumes, it does not reset.**
- **`gamma +2` bottom-of-the-wall-band branch fired again on 10-22 — 5th
  firing.** Prior four: all below the flip near the put wall, **2 right / 2
  wrong**, score and prose contradicting **4 of 4**. **For the next review.**
- **10-22 call `MILDLY BULLISH +3`** at 29361.0, board offset **+15.7** (NDX
  reference 29345.3, roll **−477.2**, the largest |roll| in the log).
  `track.py` correctly **HELD BACK** 10-22 at 180 bars.

## Journal hygiene

One scan file for 10-21 (`1248-preny.json` + `.md`), `is_trading_day: true`,
`review_day` reports **0 test artefacts** for the day (6 across the record,
excluded by `track.py`). **09-24 quarantined by hand — 17th consecutive review
to carry it**; there is still no schema `quarantine` field and the 09-29 proposal
for one is reaffirmed, because `track.py` keeps 09-24 inside every statistic it
prints (direction **17/8/9** becomes **16/8/9** once 09-24 is removed).
**2026-10-13 has no journal directory — documented, not recreated.** 09-09 and
09-25 still have no `REVIEW.md` and none was created. **2026-10-22 is on disk,
`is_trading_day: true`, 180 bars, correctly held back by `track.py`, and is
excluded from every outcome statistic above.** **No `prediction` block was
touched. No scoring, wall or grading code was edited.** No fabricated or
backfilled entries found. **No new ID allocated by this review. Next free:
H27 · D27 · P-I.**

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01M7sro1DKMp5T7EBDusm6pM

---

# Appended 2026-10-23 — grading 2026-10-22 (Thursday)

Full working in `journal/2026-10-22/REVIEW.md`. Call **MILDLY BULLISH +3** at
29361.0; post-scan **−441.6 WRONG**, day net **−883.2 WRONG**. Session
O 29804.2 / H 29817.9 / L 28860.5 / C 28921.0, range **957.4** = **1.844x**
ADR14 519.3, net −883.2, 276 bars. `track.py`: **31 trading days / 34 scans**,
direction **17/8/9** → **16/8/9** ex-09-24, levels touched **0.5**.
Board offset **+15.7**, `nq_implied`, roll **−477.2**. Section 7 absent (401).

## H2 — INSTANCE 8, the falsification EXTENDS, and the two instructions were four lines apart

In-cell under the 10-16 specification: PRE_NY, `is_trading_day`, `EXHAUSTED`,
price **921.0 below** the flip. `track.py`'s own low-fuel list carries it.

| day | state | sweep | target | result |
|---|---|---|---|---|
| **10-22** | **EXHAUSTED** | **down 14:20Z** of pre-scan low **29243.2** | n/a | **fade LOSES** (never came back inside) |

Price never closed back above 29243.2 in the remaining 98 bars (highest
subsequent close **29229.4**, highest subsequent high **29280.4**), so the grade
does not turn on the choice of target. Census **5–2 → 6–2 to the gamma block;
7–0 → 8–0 if ties go against the fade.** H2 stays **FALSIFIED**; its live
proposal (suppress or subordinate the fuel block's fade instruction below the
flip) gains an 8th supporting instance. **Axis 3 stays deleted, not scored.**

**New detail, no number taken.** On 10-19 and 10-21 the conflict was §2 regime
against §3 fuel. On 10-22 it is **inside §3, four lines apart**: the path read
*"DOWNSIDE path: clear… **Do not fade it**"* against stop management *"**Fading
the extremes** back into the range is the higher-probability side here."* Same
defect, tighter radius; grepped to H2, which owns the census.

## The gamma block was RIGHT and outvoted into a directional call — 5th instance of the cell, 2nd directional

| day | `gamma` | rest | g − rest | published | realised post-scan |
|---|---|---|---|---|---|
| 10-08 | −5 | +4 | −9 | NEUTRAL / TWO-WAY | 1.50x ADR |
| 10-09 | +4 | −6 | +10 | NEUTRAL / TWO-WAY | 0.07x ADR |
| 10-12 | −2 | +4 | −6 | NEUTRAL / TWO-WAY | 0.41x ADR |
| 10-20 | −5 | +9 | −14 | MILDLY BULLISH +4 | 0.56x, **outvote RIGHT** |
| **10-22** | **−3** | **+6** | **−9** | **MILDLY BULLISH +3** | **0.850x, outvote WRONG** |

The pre-registered quantity **still does not order the outcome**: the two
instances at **|9|** gave **1.50x** and **0.850x**, and the largest margin (14)
gave the second-smallest move. Directional sub-cell **1 right / 1 wrong, n=2.**
Both gamma limbs were right for once — location (*"downside accelerates, rallies
unstable"*) and week GEX (*"expansion likely"*, 1.844x ADR). **Nothing proposed;
the fix would be a weight change and five judgement-coded points cannot carry
one.**

**Counterfactual ledger, each row named, none fitted.** Age-gate the stale FRED
pair: **+3 → −1**, no-call. Drop the `gamma +2` band rider: **+3 → +1**,
no-call. Drop `breadth`: **+3 → 0**, no-call. Headline dedup: **no duplicates
today, no change.** **Three different single-row suppressions each produce a
no-call and none produces a correct call.**

## `gamma +2` bottom-of-band — 5th firing, the WIDEST band on record, and 5 of 5 on the prose contradiction

| day | price | put wall | band | % up band | dist to put wall | outcome |
|---|---|---|---|---|---|---|
| 08-24 | 29132.8 | 29110.2 | 200pt | 11% | +22.6 | WRONG |
| 09-14 | 28830.7 | 28787.8 | 500pt | 9% | +42.9 | RIGHT |
| 10-07 | 31031.7 | 31025.8 | 200pt | 3% | +5.9 | RIGHT |
| 10-12 | 30843.5 | 30843.1 | 500pt | 0.08% | +0.4 | WRONG |
| **10-22** | **29361.0** | **29115.7** | **1300pt** | **18.9%** | **+245.3** | **WRONG** |

**2 right / 3 wrong.** All five below the flip. **D21's width defect reaches its
extreme:** 1300pt band → *"bottom 20%"* is a **260pt trigger window = 0.50x
ADR14**, against **20pts = 0.04x ADR** on 09-18 — the same **±2** across a
**12.5x** spread, and 10-22 fired **5.7x further from the put wall than any
prior firing**. Score-versus-prose contradiction **5 of 5**: *"poor risk/reward
for shorts"* four rows above *"if it breaks, expect it to speed **UP**, not
bounce. Don't buy the break"* — and the wall broke and price ran **255.2**
further. **NOT PROPOSED**, for the reason D21 already records: the only evidence
that a normalised version performs better is the absolute-distance re-cut, which
was found **after** looking at outcomes, and the row has never flipped a
direction call's sign in any firing, so no accuracy case exists.

## P-F — 4th same-signed treatment instance, and the one-tail-point caveat is DEAD

Price at scan **29361.0 = 189.0 below PDL 29550.0**, past the >150pt trigger.
Budget **0.0**, extension **382.7**, per-day error **+382.7**.

| treatment day | price vs PD range | error |
|---|---|---|
| 09-14 | −187.6 below PDL | +79.4 |
| 09-17 | +174.5 above PDH | +40.0 |
| 09-21 | +259.0 above PDH | +569.2 |
| **10-22** | **−189.0 below PDL** | **+382.7** |
| (09-24, quarantined) | −175.5 below PDL | +13.6 |

**4 of 4 positive ex-09-24, mean +267.8, median +231.1**, on both sides of the
range. The 09-28 rebuild's caveat — *"drop 09-21 and outside mean is +44.3
against inside +6.3"* — **no longer holds**: drop 09-21 and the outside mean is
**+167.4**. **The inside control is NOT re-derived this session** and no control
figure is quoted. **P-F is ADVANCED as written** — prose and strategy selection
only, **never a multiplier** (fitted to +40 / +79 / +383 / +569 it fits the tail,
not the level; H1 lesson unchanged). On 10-22 it removes *"the day's range is
set"*, *"continuation into new highs/lows is the low-probability trade"* and the
fade-first stop-management line, all three falsified by 382.7pts of new range.

## D7's second half — 5th zero-budget day, and a SECOND code-certain limb: the footnote truncates by PRICE, not distance

`keep()` (`brief.py:431`) at budget **0.0** gives a cap of **0.0**, so every
non-exempt level is rejected regardless of distance. The board collapsed to
**6 rows, all options-derived** — no PDH, no PDL, no session extreme.
Zero-budget PRE_NY days: 09-17, 09-24, 10-01, 10-19, **10-22**.

**The new limb.** `rows.sort(key=lambda r: -r["level"])` (`brief.py:373`) leaves
`far` in **descending price** order; `far_line()` (`brief.py:146–159`) protects
only `CALL WALL / PUT WALL / GAMMA FLIP / MAX PAIN` and then takes `rest[:6]`.
With **no wall in `far`**, the footnote keeps the six **highest-priced** demoted
rows, which on a day price sits at the bottom of the level set is a
**distance-blind** cut. 10-22's footnote reads 31079 / 29936 / 29840 / 29832 /
29743 / 29682 — **+321 to +1718** away — while **PDL 29550.0 at +189, named by
the brief's own `structure −1` row, appears nowhere on the board and nowhere in
the footnote.** That is D7's original sentence reproduced for non-wall levels
after the 09-10 fix. **Cost:** the **pre-scan low 29243.2**, 117.8 below the scan
price, swept at 14:20Z, and the sweep that set up the whole afternoon, was absent
from a document whose strategy block reads *"sweeps run rather than fail."*
**Mechanism added to the existing proposal: rank `far_line`'s truncation by
`abs(dist)`.** No code edited.

## M6 — session 30; travel-scaling fails a THIRD consecutive session

| level | reported | true first-touch excursion | ratio | verdict |
|---|---|---|---|---|
| **29115.7 PUT WALL** | *"broke **UP** through it — lost by 49.1"* | **−255.2** | **5.20x** | **wording INVERTED** — closed 194.7 BELOW |
| 28915.7 STRUCTURAL PUT WALL | *"broke UP through it"* (no settled read), 14.8 | −55.2 | 3.73x | wording defensible — closed 5.3 above |

**2 of 2 understate; 1 of 2 inverted.** Post-scan travel **554.3 = 1.07x ADR**,
*higher* than session 29's 0.64x, yet the worst ratio **fell 13.75x → 5.20x**.
**Session 27's "magnitude scales with travel" claim now has three consecutive
counter-instances and is NOT restated as established.** The driver is again
**window placement**: first touch 14:30Z, the 12-bar window closed 15:25Z, and
the 255.2pt breach ran 16:30–19:45Z. **Re-proposed unchanged, 30th session.**

## D27 (NEW, OPENED) — gexbot auth failure is a data-source failure mode with no register home

**Opened 2026-10-23 at n=2.** `gexbot` returns **HTTP 401 on
`/v2/NDX/classic/gex_full`** on the **2026-10-22** scan and again on the
**2026-10-23** scan. The 10-21 review withheld a number *"deliberately at n=1"*
on the grounds that it might be transient; two consecutive sessions on an auth
endpoint settles that. **D17** (CBOE **429**) is the precedent for a
data-source failure taking a number; **H12/H13** are claims about gexbot's
*data*, not its failure modes, and neither covers this. `grep -n "^## "` run
first: **H27 · D27 · P-I** were all unused.

**Recorded as a partial success:** the brief degraded cleanly rather than
fabricating a level — *"[volume-weighted view unavailable: HTTP 401 on
/v2/NDX/classic/gex_full]"* — and section 7 was suppressed in full.

**Side effect 1, carried from the 10-21 review and re-confirmed.** The outage
costs **both** ladder files, because `persist_ladder()` fetches `gex_full` for
each weighting (`gexbot.py:219`); the printed message names only the
volume-weighted view, so **the degradation message under-reports the loss**.

**Side effect 2.** **D25's false sentence is suppressed, not fixed.** Section 7
did not render on 10-22, so the *"dominant strike is stable at 0"* line did not
print — the unguarded render is untouched and **D25's counter resumes when the
feed returns; it does not reset.** D25 is **interrupted at 29**, not resolved.

**NOTHING IS PROPOSED** — no credential change, no code change, no retry policy.
This entry exists so the mode is counted rather than rediscovered.

## H26 — n=28, a 3–5 bucket instance, and the bucket means stay monotonic

|score| **3**, |post|/ADR **0.850**, range/ADR **1.844**, **WRONG**. Bucket
**3–5**: **n 6 → 7**, **4C/2W → 4C/3W**; mean |post|/ADR **0.254 → 0.339**,
range/ADR **1.013 → 1.132**. Means **0.181 / 0.339 / 0.517 / 0.783** —
**monotonic for a 6th consecutive session**. **These are arithmetic off the
published rounded means, NOT a re-derivation from source, and are flagged as
such.** **The Spearman statistics are NOT re-derived and no number is quoted**;
directionally 10-22 is a **second consecutive large-move / low-|score| pair**,
which is the same shape that drove the three consecutive falls, so the
correlation form is likely to fall again — **stated as an expectation, not a
figure**. The live proposal (carry the signed form's derivation or stop printing
it) remains unactioned.

## P-H — 21 graded calls, and 10-22 is NOT a 6th deciding instance

Post-scan **−441.6 WRONG**; day net **−883.2 WRONG**. Both bases agree, so the
basis cannot matter. Post-scan **13/21 = 61.9%** vs day-net **14/21 = 66.7%**;
**deciding set stays n=5** and the convention's cost falls **5.0 → 4.8** points
purely on the larger denominator. PROPOSED, recommended basis **post-scan**,
applied throughout this review. These counts are maintained by hand over the
register's own sample and are **unaffected by the D26 rotation below**.

## H18 / P1 — instance 24, duplication 29 of 29, and the stale pair's margin was +4 of a +3 call

`macro +3` DFII10 (obs **2026-10-20**, two business days stale, ⚠️ printed) and
`macro +1` DGS10 (**2026-10-19 → 2026-10-20**, **no ⚠️**) — the same instrument
pair, the same window, one warning between them. **Duplication 29 of 29.**
**HY OAS rendered no observation date for the 17th consecutive session.**

**The pair carried +4 of a +3 call.** Age-gating it takes **+3 → −1**, inside
the deadband: a **no-call** on a day with a **−441.6** post-scan move. On the
register's raw convention that is a **help** (a wrong call removed): **4 → 5
helped / 3 hurt**. On the **magnitude-respecting** basis it is **not** a clean
help — it trades a wrong call for silence on a 0.850x-ADR directional day, the
most expensive kind of no-call — so that basis stays **3 helped / 3 hurt** and
this day is logged as **ambiguous rather than scored**. **The accuracy case
stays RETRACTED; the live defect is still the RENDERING one.**

**Direction-of-travel note.** `macro −2` HY OAS (*"3.33%, +17bp over 5 days…
the bond market is getting nervous"*) and `rates +3` US10y (*"5.036 (−2.14%) —
yields down, BULLISH tech"*) answered the same bond-market question with
opposite signs and a 3-to-2 weight. **HY OAS was the only right macro row and it
was outvoted 4-to-2 by the stale pair.** HY OAS is **not dead weight**; it was
**right-signed** today, which is the opposite of the 10-21 complaint.

## D18 / H19 — instances 15 and 16, polarity REVERSED, and the partial fix would have made it worse

Two judgement-list headlines tagged **`risk_on`** by first-match-wins:
*"Stock Market Today: Dow Falls As Oil Prices Jump; **Meta, Tesla Slide On
Earnings**"* and *"Gold hits over two-month low as oil **rally** fuels inflation
worries"*. **Bearish text, bullish tag** — the mirror of the 09-18 set, which was
bullish text with a bearish tag. **9th trading day, instances 15 and 16.**

**Damage zero, and only because `risk_on` is absent from `HIGH_CONFIDENCE`** —
the very asymmetry that did the damage on 09-18. **This is the first instance
that prices the partial fix: repairing the asymmetry alone, without repairing
first-match-wins, would have cast a BULLISH vote off *"Meta, Tesla Slide On
Earnings"* on an −883.2 day.** Recorded so the cheaper half-fix is not proposed.

**H19 coverage 2 / 128 = 1.6%** (128 headlines → 41 relevant → 2 scored, 39 for
judgement). The counted bullish row (*"Meta Stock Climbs After Q3 Results
Beat"*, ~150pts/180min) was **wrong-signed**; the headline that described what
actually happened sat **uncounted**. The counted bearish row (hawkish Fed) was
right and was cancelled to **news −1**.

## H10 — neither branch fired, and the proximity gap takes its SECOND instance

`structure 0`, *"price inside the prior-week range (29073.7–31079.0)"*, with
price **287.3 above the PWL**. The day **broke the PWL by 213.2** and **closed
152.7 below it**, and the rule scores that identically to a mid-range day.
Second proximity-gap instance after 10-07 (79.2 below PWH, cleared it by 108.0,
closed 245.6 below). The `−3` branch stays **2-for-7**, `+3` stays **2-for-4**,
and the proposed reclaim term would again have changed nothing.

## D23 — NO residual available, and the board offset is NOT a breach

**Section 7 did not render** (D27), so there is **no section-7 offset to match
against** and **no 17th residual exists**. The series stays at 16 entries and
**is not extended with a fabricated or inferred figure.** Board offset **+15.7**
(NDX reference 29345.3, roll **−477.2**, the largest |roll| in the log, vs CFD
29361.0): **not a breach**; the breach series stays at **five** (09-28 45.9 ·
10-12 43.1 · 10-14 41.8 · 10-15 77.6 · 10-20 74.5).

## The realised-close-basis log — observation 7 of 10, and it CANNOT discriminate the 10-20 suspicion

NDX cash close 10-22 = implied **28886.7** (10-23 scan) − roll (**−72.0**) =
**28958.7**; CFD close **28921.0**.

| day | scan offset | NDX close | CFD close | realised basis | gap | NQ roll |
|---|---|---|---|---|---|---|
| 10-14 | +41.8 | 29950.82 | 29931.8 | −19.0 | 60.8 | −205.2 |
| 10-15 | +77.6 | 29935.6 | 29885.3 | −50.3 | 128.0 | −389.8 |
| 10-16 | +14.9 | 29187.5 | 29191.5 | +4.0 | +10.9 | +376.0 |
| 10-19 | −3.9 | 29529.3 | 29559.4 | +30.1 | +34.0 | −187.0 |
| 10-20 | +74.5 | 29490.3 | 29703.2 | +212.9 | +138.4 | +208.5 |
| 10-21 | −34.6 | 29822.5 | 29839.5 | +17.0 | +51.6 | −477.2 |
| **10-22** | **+15.7** | **28958.7** | **28921.0** | **−37.7** | **53.4** | **−72.0** |

Implied NDX **−863.8** against CFD **−918.5**: divergence **+54.7**, an ordinary
reading after the −183 / +195.9 pair. **It does not clarify the 10-20 question.**
The bad-anchor story and the bad-roll story make the **same** prediction here,
because 10-22's roll is a **down-roll and the smallest |roll| in the log
(72.0)** — the up-roll condition the register's extractor cannot even parse is
absent. **n=2 on the mirrored pair, unchanged; no mechanism asserted; the roll
parser is still sign-blind and no |roll| regression may be quoted.** Re-test
still at **n=10 clean observations.**

## P3 / H6 — the SECOND structural put-wall touch, and the FIRST one that is safely gradeable

**STRUCTURAL PUT WALL 28915.7** at **−445 (0.86x ADR)**, 1.01bn / **174k
contracts**: touched 18:00Z, undercut by **55.2**, close **5.3 above it**. The
offset (+15.7) is **3.5%** of the published distance, so unlike 10-21's +1.2 row
**this grade is safe to quote**. **Its own prose argued against using it** —
*"the floor for the WEEK/MONTH. Mark it and leave it: where a multi-day sell-off
is defended, **not an intraday trigger**"* — and it located the session low to
55.2 and the close to 5.3. **STRUCTURAL CALL WALL 29715.7** at +355: untouched
again, still **0 gradeable touches** in its whole publication history. **The
10-08 narrowing is reinforced: *"stop publishing it"* applies to the structural
CALL wall only.**

## P5 — 3/3 on "not a floor", 2/3 on "accelerates", and ONE ROW IS VOID

Six secondary strikes published; **two never reached** (29515.7, 29565.7, both
above price on a down day). Of the four reached, **29365.7 is VOID and is not
graded**: published at **+5** against a **+15.7** board offset (realised basis
**−37.7**), so its location uncertainty is **3–11x** its published distance —
the **4th instance, third consecutive session**, of a board row printing inside
its own offset (10-12, 10-16, 10-21, 10-22).

| strike | dist | first touch | touches | min to a close 50 beyond | eventual penetration | close vs level |
|---|---|---|---|---|---|---|
| 29315.7 | −45 | 12:55Z | 15 | **85** | 455.2 | −394.7 |
| 29215.7 | −145 | 14:25Z | 1 | 5 | 355.2 | −294.7 |
| 29165.7 | −195 | 14:25Z | 11 | 20 | 305.2 | −244.7 |

**The *"Not a floor"* half is 3/3 RIGHT**; the *"accelerate THROUGH rather than
stall"* half is **2/3** — 29315.7 took 85 minutes and 15 touches. **The two
claims in one sentence came apart on the same session**, which is an argument
for grading them separately when P5 lands. Census: 2/3 · 2/6 · 1/6 · 2/3 · 3/5 ·
0/1 · **3/3**.

## P-B(b) — 19th session, inflation 1.00x, and D7 is why

`merge_tol = max(3.0, 519.3 × 0.008) = **4.15**` against `TOUCH_TOL = **8.0**`,
so the structurally-guaranteed window is **(4.15, 8.0]**. **The smallest gap on
the published board is 100.0** (29815.7 / 29715.7), so **no window exists and
none could fire**. Published **2/6 = 0.333**; distinct touch bars **2** →
**0.333**; **inflation 1.00x**, the cleanest reading since the 9th session.
**This is not the board improving — it is D7's zero-budget collapse removing the
density.** The two defects interact: over-pruning produces P-B(b)'s best number.
Proposal unchanged.

## Appended without proposal

- **H8 — ANSWERED-POSITIVE, not reopened; post-closure data only.** Straddle
  **496pts** (ATM IV 13.6%) → EM **±421** → band **28940 .. 29782**. Close
  **28921.0 — OUTSIDE by 19.0**, the second narrow miss in three sessions
  (10-20 was outside by 2.2). **VXN-implied range 451.7 under-read the realised
  957.4 by 505.7**, the **second-worst under-read in the log** (after 524.1), and
  the page recommended *"use the smaller budget"*. **Third counter-instance to
  the already-killed *"use the VXN-implied range as the budget"* idea; it is not
  revived.**
- **P4 / H1 — the day count did NOT advance; see D26.** `track.py` per-day mean
  prints **+58.6 (n=31)** against the 10-22 run's **+45.4 (n=31)**. **These are
  not two points in one series:** 09-08 left the sample as 10-22 entered it.
  10-22's own data point is **+382.7** (budget **0.0**, extension **382.7**), the
  **3rd-largest** positive error on record behind 09-21 (+569.2) and 10-16
  (+479.3). Claim stays **"no usable skill"**; multiplier branch **closed**;
  pre-scan pace **CLOSED**. **The budget was 0.0, the arithmetic floor, so the
  error is identically the whole extension and carries no information about
  calibration** — it is a P-F observation, logged above, not an H1 one.
- **H22 — range label RIGHT at n=14**, second consecutive right reading: week net
  GEX **−6.602 → *"expansion likely"*** → realised **1.844x ADR**, the largest
  expansion in five sessions. **Direction half not re-run** (stays 15/11 = 58%,
  n=26). The row cast **−2** inside a gamma block that netted **−3** and was
  right.
- **H23 — NO instance.** Both paths flagged **clear**, so `path_read()` named no
  brake. Census unchanged at **11 sliced / 3 capped / 3 never-reached, n=17**;
  force-ranking branch stays **CLOSED as unfalsifiable**; corridor-terminus
  proposal stays **WITHDRAWN** (`brief.py:520`). **The clear-path read was
  vindicated**: price ran **−500.5** through every shelf to the structural put
  wall and *"Do not fade it"* was correct. **Trap re-flagged, and today is its
  control:** the secondary table printed strikes at **+5 / +155 / +205** and
  **−45 / −145 / −195**, every one of them put-dominant, so **neither
  `walls_ranked` (`brief.py:647`) nor `largest_abs_gex` (`brief.py:515`) held a
  positive shelf** — the two lists can only disagree when one exists, and today
  neither did. **Different lists; not a skipped brake.**
- **D7-shaped, contract count vs dollar gamma — 3rd instance.** The headline
  **CALL WALL 30415.7** carries **●○○○○ 0.02bn** and the prose *"Heaviest ceiling
  this week (**15k contracts**)"*, while the **PUT WALL** carries **●●●●● 0.54bn
  on 3k contracts**. **Contract count for the superlative, dollar gamma for the
  stars, in the same table.** The row sat **2.03x ADR** away and was never within
  1000 points. n=3.
- **Max pain — 8th distance-confounded non-test.** Published **+455**, post-scan
  high missed it by **400.9**. The *"strong by Thursday/Friday"* qualifier went
  untested **on a Thursday**, which is the first time distance has killed the
  qualifier on a day the qualifier claims. It also sat **2.2 below the pre-scan
  high**.
- **Session-context field — 19th session.** Pre-scan range **29243.2–29817.9**.
  **2 of the 6 marked rows** lay inside it (MAX PAIN 29815.7 at **−2.2** from the
  pre-scan high, STRUCTURAL CALL WALL 29715.7) and **8 of 18** counting the
  footnote and secondary table, under the banner *"New trading day… everything
  below is fresh."* **Mildest-consequence instance in the series**: both marked
  rows are above price and neither is a ⭐ trigger — because D7's collapse
  removed every session-derived row that could have carried one. Proposed 09-29,
  still not actioned.
- **P-G — NO instance, for the first time in many sessions.** No session-derived
  row reached the marked board at all (D7), so the *"the next session usually
  runs the stops below/above it"* string had nowhere to print. Already PROPOSED.
- **P-E / P-E(b) — NO instance.** CALL WALL at **+1055**, never reached, **1000.9
  above the post-scan high**; no shelf brake named on either side.
- **H14 — the regime-aware wall note worked, 2nd consecutive confirmation.** Both
  put rows carried *"if it breaks, expect it to speed **UP**, not bounce. Don't
  buy the break"*; the put wall broke and price ran a further **255.2** in 3h15.
  The residual problem remains the **missing horizon**, not regime-blindness.
- **D25 — interrupted at 29, not resolved.** Section 7 suppressed by the 401
  (D27). **The counter resumes when the feed returns; it does not reset.**
- **No instance:** **H3** (CLOSED-NEGATIVE, superseded by H26) · **H4** (flip
  867.2 above the post-scan high) · **H7** (no overnight scan) · **H17**
  (post-scan **46.1%** of the session range, far outside the 5% deadband; stays
  **2 of 3**) · **H20** (CLOSED-NEGATIVE, not revived; `events_24h` empty) ·
  **D24** (`event_gate: null` correct; no forward High/Medium events, so the
  forward-only renderer had nothing to hide) · **D9** (both scored headlines
  carry their subject) · **`PIN_THEN_EXPAND`** (**did NOT fire** —
  `COHERENT_SHORT`, not the pinning shape; **still observation 2 of 3, no
  verdict, not revised**) · **the *"direction right, strategy block wrong"*
  cell** (the bias was wrong, so no instance; **stays n=2**) · **the *"whole move
  over by 10:30 ET"* watch item** (the low landed 15:45 ET; **counter-instance**,
  it does not extend).
- **No new data point is warranted.** Every failure traces to the **vintage or
  the measurement window of rows already on the page** — a two-business-day-stale
  FRED pair, a pre-market breadth read the cash session reversed, a band rider
  firing 245pts from its own wall, and a level set pruned to nothing by a zero
  budget. No free, reliable feed fixes any of those.

## Carried forward from the 2026-10-23 scan — recorded, NOT graded

- **STRONGLY BEARISH −16** at **28875.7**, down **485** from the prior scan and
  **below the entire prior-week range**. Second-most-extreme call in the record
  after 10-14's −18. **H26's relevant prior: the ≥10 bucket is 3/6 on direction
  while magnitude correlates — the defensible read is "expect a big move,
  direction uncertain", and it is written here before the outcome is known.**
- **VXN +17.6% to 28.72**, the highest in the series; ATM IV **33.9%**.
- **PUT WALL at −87 with 125k contracts this week and 211k on the 45-day book**,
  the heaviest in the series. **fuel_ratio 1.03**, the most normal pace recorded.
- **Four Medium events land 13:45–14:00 UTC**, inside the first half hour.
- **`gexbot` HTTP 401 again — the 2nd consecutive scan. This is the n=2 that
  opens D27 above.** Board offset **−11.0**, roll **−72.0** (smallest |roll| in
  the log).
- **`gamma +2` bottom-of-band fired a 6th time on the 10-23 scan. For the next
  review.**

## Journal hygiene

One scan file for 10-22 (`1248-preny.json` + `.md`), `is_trading_day: true`,
`review_day` reports **0 test artefacts** for the day (6 across the record,
excluded by `track.py`). **09-24 quarantined by hand — 18th consecutive review
to carry it**; there is still no schema `quarantine` field and the 09-29 proposal
for one is reaffirmed. **2026-10-13 has no journal directory — documented, not
recreated.** 09-09 and 09-25 still have no `REVIEW.md` and none was created or
back-dated. **2026-10-23 is on disk, `is_trading_day: true`, 180 bars, correctly
held back.** **No `prediction` block was touched. No scoring, wall or grading
code was edited.** No fabricated or backfilled entries found. **One new ID
allocated by this review: D27. Next free: H27 · D28 · P-I.**

**D26 — the symptom changed AGAIN, and this is the sharpest instance yet.**
`track.py` prints **31 trading days / 34 scans**, direction **17/8/9**, levels
touched **0.5** — *the identical headline figures the 10-22 run printed, over a
different 31 days*. **2026-09-08 has joined `HELD BACK` at 98 bars**: a day
completed six weeks ago, filed as *"day not finished"* because only part of its
bar series survives inside the 45-day fetch window. 09-08 left the sample as
10-22 entered it, the count did not move, and the H1 per-day mean went
**+45.4 → +58.6** on **one day in and one day out**, not on a day added. On disk:
**39** day directories, **69** scan JSONs, **34** days with a PRE_NY scan, **33**
with a `REVIEW.md` (**34** after this review), **30** with both (**31** after).
**The silently invisible set did NOT grow** — still the six August directories
(08-23 … 08-28), for which `review_day` returns no `scans` key and
`track.py:84` `continue`s. **39 − 6 = 33 = 31 graded + 09-08 held + 10-23 held**,
which reconciles exactly. `track.py` still prints **no literal
`actionable: YES/NO`**; the threshold rule was applied by hand.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01M7sro1DKMp5T7EBDusm6pM

---

# Appended 2026-10-26 — grading 2026-10-23 (Friday)

Full working in `journal/2026-10-23/REVIEW.md`. Call **STRONGLY BEARISH −16** at
28875.7; post-scan **+124.5 WRONG**, day net **+59.6 WRONG**. Session
O 28939.6 / H 29155.4 (14:50Z) / L 28820.4 (13:35Z) / C 28999.2, range 335.0 =
**0.608x** ADR14 550.8. `track.py`: **29 trading days / 30 scans**, direction
**14/9/7** → **13/9/7** ex-09-24, levels touched **0.52**.

## H27 (NEW, OPENED) — the score's components are not independent, and collapsing them makes the record WORSE

**Opened 2026-10-26.** `grep -n "^## "` run first: **H27 · D28 · P-I** all
unused. Grepped for by claim before the number was taken — *collinear*,
*common cause*, *correlated component*, *double-count* — and nothing in the file
owns it. **H18/P1** is the DFII10/DGS10 pair and the rendering fix; **H19** is
duplicate headlines; the 10-21 whole-record duplication-collapse measurement
covers only those two. **H3** is CLOSED-NEGATIVE (*cap the conviction at range
extremes*) and is not this. **H26** is the magnitude-versus-direction claim —
**this entry is the MECHANISM behind H26, and that is why it is separable.**

**Claim.** The published score presents its blocks as independent evidence
(*"Driven by: vol −4 · gamma −3 · breadth −3 · structure −3 · rates −1 ·
macro −1 · news −1"*). They are not. Across all **33** PRE_NY `is_trading_day`
scans (09-24 and the unfinished 10-26 excluded), the Pearson correlation of
block subtotals is near zero for every pair except two:

| pair | r |
|---|---|
| **vol ↔ breadth** | **+0.533** |
| **structure ↔ gamma** | **+0.555** |
| structure ↔ rates | +0.206 (next largest) |
| all others | \|r\| ≤ 0.22 |

On the **13** days where the breadth row's prior-day NDX figure is recoverable
from the journal text, **vol r = +0.698** and **breadth r = +0.713** against that
same number. They are two readings of one event.

**10-23 is the extreme case.** Thursday's **−2.90%** NDX session was scored three
times — `vol −4` (VXN 28.72 **+17.6%**, VXN/VIX 1.44, VVIX 107.94: all
*consequences* of it), `breadth −3` (*"NDX −2.90% vs ES −0.44%"*: literally it),
`structure −3` (*"BELOW the entire prior-week range"*: where it put price).
**−13 of −16 came from the two collinear pairs. The independent remainder was
−3** — rates −1, macro −1, news −1 — i.e. **inside the engine's own ±3 deadband,
a no-call.** The 10-23 carry-forward note read this score as *"notably
broad-based… unlike 10-21 this score is NOT a duplication artefact"*. **That
reading is wrong, and the register made it** — it is a duplication artefact of a
kind the file was not watching for, and the FRED pair really did contribute only
−1, which is why looking there found nothing.

**PRE-REGISTERED TEST, rules fixed in writing before any outcome was
inspected** (10-21 duplication-collapse is the precedent): one PRE_NY
`is_trading_day` scan per day, 09-24 excluded, 10-26 excluded as unfinished
(**n=29 days / 22 calls**, the H26 sample); within each collinear pair, if both
subtotals share a **strict** sign, drop the member with the smaller |subtotal|;
deadband unchanged at |score| ≥ 3; **post-scan** grading per P-H.

| basis | C | W | no-call | rate |
|---|---|---|---|---|
| **published** | 13 | 9 | 7 | **59.1%** |
| **collinearity-collapsed** | 10 | 9 | 10 | **52.6%** |

Scores changed on **23 of 29** days; the **call** changed on **5** — **3 hurts**
(09-18, 10-06, 10-19, all CORRECT → no-call) against **2 helps** (10-12 no-call →
CORRECT, 10-15 WRONG → no-call).

**STATUS: the weight-change limb is ANSWERED-NEGATIVE on arrival. NOTHING IS
PROPOSED.** The collinearity is structurally real and large, and acting on it
makes the record worse — the identical shape to the 10-21 result, and the second
time this file has priced a structurally-sound dedup as directionally harmful.
**This entry exists so the fix is not re-proposed by the next reviewer who
notices the correlation.**

**One limb stays OPEN at n=1 and is NOT proposed:** the §1 *"Driven by:"* line
renders correlated rows as a list of independent contributors, and the register
itself was misled by it on 10-23. That is a **rendering** claim in the
**H18/P1** family, not a weight claim. It needs 3 instances before anything is
said about it.

## H26 — n=29, the ≥10 bucket falls BELOW a coin flip, and the bucket table is RE-DERIVED FROM SOURCE

|score| **16**, |post|/ADR **0.226**, range/ADR **0.608**, **WRONG**. This is the
**7th** ≥10 instance and it is **the smallest on both measures**: the bucket
means are 0.783 and 1.390. **The prior written on the 10-23 scan before the
outcome was known — *"expect a big move, direction uncertain"* — is wrong on
both limbs.**

**Re-derived from source this session, not arithmetic off the published rounded
means.** Method as specified 10-20; it reproduces the register's n=28 bucket
**counts** exactly (7 / 7 / 8 / 6, same C/W) and three of the four |post|/ADR
means exactly.

| \|score\| | n | C | W | no-call | direction | mean \|post\|/ADR | mean range/ADR |
|---|---|---|---|---|---|---|---|
| 0–2 | 7 | — | — | 7 | — | 0.181 | 1.103 |
| 3–5 | 7 | 4 | 3 | 0 | 57.1% | 0.339 | 1.132 |
| 6–9 | 8 | 6 | 2 | 0 | **75.0%** | **0.532** | **1.032** |
| **≥10** | **7** | **3** | **4** | 0 | **42.9%** | **0.704** | **1.279** |

- **Magnitude monotonicity SURVIVES**: 0.181 / 0.339 / 0.532 / 0.704, **7th
  consecutive session**. The ≥10 mean fell **0.783 → 0.704**, its largest
  single-session fall.
- **Direction is INVERTED at the top.** The highest-conviction bucket is now the
  **worst** and is **below a coin flip**, while 6–9 is the best at 75%. H26's
  core claim — magnitude is a range forecast, not a direction forecast — is
  **strengthened**, not weakened.
- **Two published 6–9 figures have DRIFTED from source**: |post|/ADR **0.517 vs
  0.532**, range/ADR **1.134 vs 1.032**. On source figures the **range/ADR
  bucket form is NOT monotonic** (1.103 / 1.132 / **1.032** / 1.279) **and was
  not at n=28 either** — the published monotonicity of the range form is a
  rounding artefact and should stop being claimed.
- Spearman(|score|, |post|/ADR) **+0.525 → +0.479**; (|score|, range/ADR)
  **+0.085 → −0.007**. The signed form is still not quoted and its live proposal
  is unactioned.
- **Mechanism: see H27 above.**

## P-H — 22 graded calls, and 10-23 is NOT a 6th deciding instance

Post-scan **+124.5 WRONG**; day net **+59.6 WRONG**. Both bases agree, so the
basis cannot matter. Post-scan **13/22 = 59.1%** vs day-net **14/22 = 63.6%**;
**deciding set stays n=5** and the convention's cost falls **4.8 → 4.5** purely
on the larger denominator. PROPOSED, recommended basis **post-scan**, applied
throughout the 10-23 review.

## M6 — session 31, and the driver is NOT window placement

| level | reported | true excursion from first touch | ratio | close vs level | verdict |
|---|---|---|---|---|---|
| 28921.0 PD close | *"broke DOWN through it — **lost by 62.6**"*, `settled_side above`, `acted_as lost` | −100.6 | **1.61x** | **+78.2** | **INVERTED** |
| 28888.5 London Low | *"broke DOWN — lost by 30.1"*, `acted_as lost` | −68.1 | 2.26x | **+110.7** | **INVERTED** |
| 28860.5 PDL+NY Low | *"broke DOWN — lost by 40.1"*, `acted_as lost` | −40.1 | 1.00x | **+138.7** | **INVERTED** |
| 28853.1 Asia Low | *"broke DOWN — lost by 32.7"*, `acted_as lost` | −32.7 | 1.00x | **+146.1** | **INVERTED** |
| 28981.6 Equal highs | *"held as **support** 45min, worst −11.7"* | −73.2 | **6.26x** | +17.6 | close-determined |
| 29073.9 Asia High+PWL | *"held as resistance 245min, worst +24.0"* | +81.5 | 3.40x | −74.7 | defensible |
| 29109.3 London High | *"held as resistance 285min, worst +9.6"* | +46.1 | 4.80x | −110.1 | defensible |

**4 of 7 verdicts inverted** — the worst count since session 18 — and **5 of 7
excursions understated**, worst ratio **6.26x**. Every one of the four inverted
rows carries `settled_side: "above"` **and** `acted_as: "lost"` simultaneously,
because `acted_as` is `"lost"` whenever the excursion exceeds `SETTLE_TOL = 25`
regardless of which side price settled on.

**The new detail, and it corrects session 30.** The **12-bar `REACT_BARS` window
captured the TRUE excursion on 7 of 7 rows** here (46.1 / 81.5 / 73.2 / 100.6 /
68.1 / 40.1 / 32.7, all equal to the full-session figure in the relevant
direction). **Window placement contributed nothing on 10-23.** The entire
understatement comes from `settled_read` measuring `worst_excursion` only over
bars after `last_far`, which is already recorded (lines ~5535, ~6061, ~7054).
**Session 27's travel-scaling claim takes a FOURTH consecutive counter-instance
and session 30's "the driver is again window placement" does not generalise.**
Re-proposed unchanged, 31st session. No code edited.

## D7 — CONTROL, both limbs clean, and the second limb is confirmed non-firing

Budget **294.6** (the largest ever published), so `keep()`'s `budget * 1.75` cap
rejected nothing structural and the board shipped **15 rows** — no zero-budget
collapse. `far` held **5 rows against `far_line`'s cap of 6**, so
`rest[:cap − len(walls)]` **dropped nothing** and the descending-price sort at
`brief.py:373` had no victim. All five footnote rows (31079 PWH · 29818 PDH ·
29682 Asia High prev · 29415 NY High prev · 29339 PD mid) are **above** price;
**no below-price level was demoted at all.** Zero-budget PRE_NY days stay at
09-17, 09-24, 10-01, 10-19, 10-22. **Correction to the task framing: the 10-23
footnote has FIVE entries, not two, and the board was not short.**

## D26 — the held-back set rotated AGAIN and the sample SHRANK by two days

`track.py` prints **29 trading days / 30 scans** against the 10-23 run's **31 /
34**. Three calendar days elapsed, the 45-day bar window slid three days, and:
**09-08, 09-09 and 09-10 left visibility entirely** (`review_day` returns
`{error, detail, scans_found}`) while **09-11 joined `HELD BACK` at 96 bars** —
a day completed seven weeks ago, filed *"day not finished"*. **The silently
invisible set grew from six to nine** (08-23 … 08-28, 09-08, 09-09, 09-10).

On disk: **40** day directories, **70** scan JSONs, **35** days with a PRE_NY
scan (**all** `is_trading_day: true`), **34** with a `REVIEW.md` (**35** after
this review). **40 − 9 invisible − 2 held back (09-11, 10-26) = 29**, which
reconciles exactly.

**The P4/H1 figure conflict is now FOUR numbers under one series name.** Live
print **+53.9 (n=29 days) / +54.8 (n=30 scans)**; 10-23 live print **+58.6
(n=31)**; register **+45.4 (n=31)**; the runner's **+51.9 (n=30)**. The sample
beneath them changed three times. **Reported, flagged, and not averaged.**

## P4 / H1 — n=29; the day count went DOWN, and the error is the largest in the record

10-23: budget **294.6**, extension **78.8**, error **−215.8** — **the largest
over-estimate in the record, on the largest budget in the record**, and the
first time those two coincide. Claim stays **"no usable skill"**; multiplier
branch **closed**; pre-scan pace **CLOSED** (`fuel_ratio` **1.03 normal** →
**0.226x ADR**, a **fifth** consecutive uninformative reading).

**"Big budgets over-read" checked a third time and still fails.** The eight
visible budget≥200 scans: +25.9 / −75.2 / −66.5 / −180.1 / **+479.3** / −17.7 /
−149.8 / **−215.8**, mean **−25.0**, both tails intact. **The register's earlier
figure (+16.3, mean of a different eight) is NOT comparable — that set itself
rotated out from under the claim** (it contained a +114.6 that is no longer
visible). Nothing proposed.

## H10 — the −3 branch fires, goes 2-for-8, and the PROSE was right while the SCORE was wrong

`structure −3`, *"price is BELOW the entire prior-week range (29073.7–31079.0) —
PWL 29073.7 is now resistance, not support"*. Price was **198.0 below the PWL =
0.36x ADR**, and the rule scores that identically to 2000 points below.
Price then **reclaimed the PWL intraday by 81.7** (high 29155.4) before closing
**74.5 below** it.

- The **prose was RIGHT**: 29073.9 held as resistance for 245 minutes, worst
  excursion +24.0, and the session closed under it.
- The **−3 it justified was WRONG**: the day net **+59.6**. Branch **2-for-7 →
  2-for-8**.
- **Third proximity-gap instance** (10-07, 10-22, **10-23**) and the **first on
  the −3 branch**: all three are days the rule treated a near boundary as a far
  one. The proposed reclaim term would again have changed nothing — no reclaim
  existed at scan time. **It is the DISTANCE term, not the reclaim term, that
  this instance argues for; still not proposed at n=3 without an accuracy test.**

## `gamma +2` bottom-of-band — 6th firing, and the FIRST where it was the only right row in its own block

| day | price | put wall | band | % up band | dist to put wall | outcome |
|---|---|---|---|---|---|---|
| 08-24 | 29132.8 | 29110.2 | 200pt | 11% | +22.6 | WRONG |
| 09-14 | 28830.7 | 28787.8 | 500pt | 9% | +42.9 | RIGHT |
| 10-07 | 31031.7 | 31025.8 | 200pt | 3% | +5.9 | RIGHT |
| 10-12 | 30843.5 | 30843.1 | 500pt | 0.08% | +0.4 | WRONG |
| 10-22 | 29361.0 | 29115.7 | 1300pt | 18.9% | +245.3 | WRONG |
| **10-23** | **28875.7** | **28789.0** | **600pt** | **14.5%** | **+86.7** | **RIGHT** |

**3 right / 3 wrong.** All six below the flip. D21 width: a 600pt band makes
*"bottom 20%"* a **120pt trigger window = 0.218x ADR14** — mid-range against
10-22's 0.50x and 09-18's 0.04x. **Prose contradiction 6 of 6**: *"poor
risk/reward for shorts"* three rows above *"if it breaks, expect it to speed
**UP**, not bounce. Don't buy the break"*, plus §1's *"Strategy-1 fades have a
materially lower hit rate"*. **The contradiction went untested — the put wall
never broke** (low 28820.4, **31.4 above it**).

**Still NOT PROPOSED.** Six firings, **zero sign changes**: −16 would have been
−18 without it, same label, same side, same wrong verdict. The only evidence a
normalised version performs better is still the post-hoc absolute-distance
re-cut. No accuracy case exists.

## H2 — NO instance, and the cleanest control the census has had

Fuel **MODERATE**, `fuel_ratio` **1.03** — the most normal pace in the record —
and `track.py`'s own low-fuel list does **not** carry 10-23. Census unchanged at
**6–2 to the gamma block, 8–0 if ties go against the fade. FALSIFIED.**

**Mechanism confirmation worth having.** §3 stop management read *"structural
stop; break-even at 1R or 50% of remaining budget, whichever first"* — **no fade
instruction anywhere on the page**, so the two-opposite-instructions
contradiction that fired on 10-19, 10-21 and 10-22 **did not fire here**. That
localises the contradiction to the **LOW_FUEL/EXHAUSTED branch**, which is
exactly the cell H2's live proposal targets. A control day that narrows the
proposal is worth more than another in-cell loss.

## The realised-close-basis log — observation 8 of 10, and it DOES discriminate the 10-20 suspicion

NDX cash close 10-23 = implied **29108.5** (10-26 scan) − roll (**+151.0**) =
**28957.5**; CFD close **28999.2**.

| day | scan offset | NDX close | CFD close | realised basis | gap | NQ roll |
|---|---|---|---|---|---|---|
| 10-14 | +41.8 | 29950.82 | 29931.8 | −19.0 | 60.8 | −205.2 |
| 10-15 | +77.6 | 29935.6 | 29885.3 | −50.3 | 128.0 | −389.8 |
| 10-16 | +14.9 | 29187.5 | 29191.5 | +4.0 | +10.9 | +376.0 |
| 10-19 | −3.9 | 29529.3 | 29559.4 | +30.1 | +34.0 | −187.0 |
| 10-20 | +74.5 | 29490.3 | 29703.2 | +212.9 | 138.4 | **+208.5** |
| 10-21 | −34.6 | 29822.5 | 29839.5 | +17.0 | 51.6 | −477.2 |
| 10-22 | +15.7 | 28958.7 | 28921.0 | −37.7 | 53.4 | −72.0 |
| **10-23** | **−11.0** | **28957.5** | **28999.2** | **−41.7** | **30.7** | **+151.0** |

**This is the up-roll condition 10-22 could not supply.** 10-22 was a down-roll
and the smallest |roll| in the log, so it could not separate the bad-anchor story
from the bad-roll story. **10-23 is an UP-roll at 72% of 10-20's size, and its
gap is 30.7 — the second-smallest in the log — against 10-20's 138.4.** The
*"up-rolls break the basis"* story **does not survive it**; the anomaly
localises to **10-20 itself or to the anchor**, not to roll sign. **n=2 on
up-rolls.** The roll parser is still sign-blind and **no |roll| regression is
quoted.** Re-test still at **n=10 clean observations**.

## H18 / P1 — instance 25, duplication 30 of 30, and a CLEAN NULL on the age gate

`macro 0` DFII10 (obs **2026-10-21**, two business days stale, ⚠️ printed) and
`macro −1` DGS10 (**2026-10-20 → 2026-10-21**, **no ⚠️**) — same instrument pair,
same window, one warning between them. **Duplication 30 of 30.** **HY OAS
rendered no observation date for the 18th consecutive session.**

**The pair carried −1 of a −16 call.** Age-gating it gives **−15**: same label,
same side, same WRONG verdict. **A clean null on both conventions** — it is
neither a help nor a hurt, so the tallies are unchanged at **4 helped / 3 hurt**
(raw) and **3 / 3** (magnitude-respecting). The accuracy case stays
**RETRACTED**; the live defect is still the **RENDERING** one.

**HY OAS went quiet, not dead.** It scored **0** (*"3.27%, +2bp over 5 days —
middling"*) after **six consecutive sessions of widening** that had it at −2 on
10-22. It was also **the only macro row that did not cast a wrong-signed vote**
on a day the macro block went −1 and the day closed up. **It is not dead
weight** — the 25/33 scoring rate in this session's dead-weight refresh says the
same thing.

## Appended without proposal

- **H23 — NO brake instance; census unchanged at 11 sliced / 3 capped / 3
  never-reached, n=17.** Force-ranking branch stays **CLOSED as
  unfalsifiable**; corridor-terminus stays **WITHDRAWN** (`brief.py:520`).
  **The clear-path read is graded and it SPLIT.** The **downside** limb is
  untested (low 28820.4, **431 short** of the declared 28389.0 terminus). The
  **upside** limb **ran 279.7 of the 363 declared, stalled 84 short of 29239.0
  at 29073.9/29109.3 — two liquidity rows the options model says are nothing —
  and reversed**; *"Do not fade it"* was the losing instruction and the fade at
  the stall was the winning trade. **Clear-path sub-series n=2, 1 right (10-22)
  / 1 wrong (10-23).** It was the best thing on the page on 10-22 and the worst
  actionable line on the page here.
- **P5 — 1/1 on *"not a floor"*, 1/2 on *"accelerates through"*, and the
  separate-grading refinement earns its keep.** Four put-dominant strikes
  published; **28589.0 (−287) and 28689.0 (−187) never reached**. Board offset
  −11.0 is 5% and 17% of the two graded distances — **no row is void this
  session** (the 4-session run of inside-own-offset rows ends).

  | strike | dist | first touch | touches | min to a close 50 beyond | max penetration | close vs level |
  |---|---|---|---|---|---|---|
  | 29089.0 | +213 | 14:40Z | **21** | 130 | 156.6 | −89.8 |
  | 28939.0 | +63 | 13:40Z | 10 | **15** | 216.4 | +60.2 |

  **29089.0 stalled — 21 touches and 130 minutes — which is the direct negation
  of *"accelerate THROUGH rather than stall"*.** *"Not a floor"* is vacuous on a
  level above price and is **not graded** for 29089.0. Census: 2/3 · 2/6 · 1/6 ·
  2/3 · 3/5 · 0/1 · 3/3 · **1/2**.
- **P-B(b) — 20th session, and a guaranteed window FIRED.**
  `merge_tol = max(3.0, 550.8 × 0.008) = **4.41**` against `TOUCH_TOL = **8.0**`
  → structurally-guaranteed window **(4.41, 8.0]**. The board's smallest gap is
  **7.4** (28860.5 / 28853.1), **inside it**, and those two rows **plus 28888.5**
  all first-touched in the **same 12:50Z bar**. Published **7/15 = 0.467**;
  distinct touch bars **5** → **0.333**; **inflation 1.40x**. Unlike 10-22's
  1.00x, this is a real board with real density, so the reading is informative.
  Proposal unchanged: (a) `merge_tol >= TOUCH_TOL`, (b) report distinct touch
  events.
- **P3 / H6 — structural CALL wall untouched again, 533.6 away, still 0
  gradeable touches in its entire publication history.** The 10-08 narrowing
  (*"stop publishing it"* applies to the structural **call** wall only) is
  reinforced. No structural put wall was published. **Separately: `TOUCH_TOL =
  8.0` filed the day's single best level as *"never reached"*.** The **PUT WALL
  28789.0 ●●●●● 1.21bn / 125k this week / 211k on the 45-day book** — the
  heaviest in the series — stopped the session low at **31.4 above it (0.057x
  ADR)** and the day reversed **+335** off that low. The grader's binary loses
  it entirely. **Every one of the five options levels on the board was
  untouched, and four of the five were beyond the budget.**
- **P-E / P-E(b) — instance #17, and it SPLITS for the first time.** CALL WALL
  **+513**, never reached, **233.6 above the post-scan high** → no P-E instance.
  P-E(b): on the **downside the HEADLINE wall won** — put wall **31.4** from the
  low against the nearest secondary shelf's **131.4** — which is **the first
  downside counter-instance** to *"the shelf family locates the extreme better"*;
  on the **upside the shelf won** — 29089.0 at **66.4** from the high against the
  call wall's **233.6**.
- **P-G — instances #28, #29, #30.** *"the next session usually runs the stops
  **below** it"* printed on **29333.8** (+458), **29243.2** (+368) and
  **28888.5** (+13), all **above** price. The first two were never reached; on
  28888.5 the stops below it were in fact run. Prose only, already PROPOSED,
  free, still not actioned.
- **D18 / H19 — instance 17, 10th trading day.** `[risk_on]` on *"TSX futures
  **slip** as oil rally adds to inflation worries"* — bearish text, bullish tag,
  first-match-wins. **Damage zero only because `risk_on` is absent from
  `HIGH_CONFIDENCE`** (verified in `news_scorer.py:234`), the same asymmetry that
  did the damage on 09-18 and the same reason the half-fix stays priced as
  harmful. **H19 coverage 1 / 134 = 0.75%, the LOWEST in the record** (prior low
  2/128 = 1.6%). The single scored row was the hawkish-Fed headline, correctly
  tagged and wrong for the day, while *"10-year Treasury yield drops back to 5%
  this week"* and *"Bullish Outlook on the Nasdaq 100"* sat uncounted.
- **P-C — 2nd Medium-cluster instance.** The gate requires `impact == "High"`
  within 1.5h (`bias_engine.py:255`), so **four Medium prints at 13:45–14:00Z**
  gave `event_gate: null`. Correct per code — and **the session low landed
  13:35Z, ten minutes before the first print, and the high 14:50Z**. The entire
  335pt range was carved around data the gate ignores by construction. n=2
  (09-29 two Mediums, 10-23 four). Mechanism already logged as P-C; **nothing
  proposed at n=2.**
- **H22 — range label WRONG at n=15**, ending a two-session run of right reads.
  Week net GEX **−6.927** → *"expansion likely"* → realised **0.608x ADR**, a
  contraction, and the **smallest range/ADR of any ≥10-score day in the
  record**. The row cast **−2** inside a gamma block that netted −3 and it was
  wrong on both limbs. **Direction half not re-run** (stays 15/11 = 58%, n=26).
- **H8 — ANSWERED-POSITIVE, post-closure data only.** Straddle **414pts** (ATM
  IV 33.9%) → EM **±352** → band **28524 .. 29227**. Close **28999.2 INSIDE**,
  and the whole session H/L stayed inside the band. **VXN-implied range 522.4
  OVER-read the realised 335.0 by 187.4** — **4th counter-instance** to *"use the
  VXN-implied range as the budget"*, and the **opposite sign** to 10-22's 505.7
  under-read. Both tails present; **not revived**.
- **D23 — NO residual available for a second consecutive session.** Section 7
  did not render (D27), so there is **no section-7 offset** and **no 17th
  residual exists**. The series stays at **16** and **is not extended with an
  inferred figure**. Board offset **−11.0**: **not a breach**; the breach series
  stays at **five** (09-28 45.9 · 10-12 43.1 · 10-14 41.8 · 10-15 77.6 ·
  10-20 74.5).
- **D27 — 3rd consecutive session.** `gexbot` HTTP **401** on
  `/v2/NDX/classic/gex_full` on the 10-22, 10-23 **and 10-26** scans. The brief
  again degraded cleanly (*"[volume-weighted view unavailable: HTTP 401…]"*) and
  again lost **both** ladder files while naming only the volume-weighted view
  (`gexbot.py:219`). **NOTHING PROPOSED** — no credential change, no code
  change, no retry policy.
- **D25 — interrupted at 29, not resolved.** Section 7 suppressed by the 401
  (D27). The counter resumes when the feed returns; it does not reset.
- **Dead-weight audit — refreshed FROM SOURCE, n=33** PRE_NY `is_trading_day`
  scans (09-24 and the unfinished 10-26 excluded):

  | row | scored |
  |---|---|
  | `macro` yield curve (10y–2y) | **0 / 33** |
  | `events` | **0 / 24** (the row is ABSENT on 9 scans — P-C) |
  | `rates` DXY | 4 / 33 |
  | `macro` WALCL/RRP | 4 / 33 |
  | `macro` NFCI | 5 / 33 |
  | `rates` US10y | 25 / 33 |
  | `macro` HY OAS | 25 / 33 |

  **This does NOT reconcile with the register's hand-maintained n=34** and the
  discrepancy is flagged rather than papered over — it is the **third**
  hand-maintained counter this session that cannot be reproduced from disk (see
  D26). The substance is unchanged, so the narrowed standing proposal (drop the
  yield-curve row and WALCL/RRP) is **unchanged and still not actioned**.
- **Session-context field — 20th session.** Pre-scan range
  **28853.1–29109.3**. **7 of 15** marked rows lie inside it, **9 of 24**
  counting the footnote and secondary table, under the banner *"New trading
  day… everything below is fresh."* Higher consequence than 10-22's: the three
  rows that shared the 12:50Z touch bar are all pre-scan session extremes.
  Proposed 09-29, still not actioned.
- **P-F — NOT a treatment instance.** Price **28875.7** sat **15.2 ABOVE PDL
  28860.5** — inside the prior-day range — so the >150pt trigger did not fire.
  The treatment set stays **4 of 4 positive ex-09-24, mean +267.8**. Logged as a
  single **inside-control** observation (error **−215.8**, opposite-signed to
  every treatment instance); **the control is NOT re-derived and no control
  figure is quoted.**
- **D7-shaped, contract count vs dollar gamma — 4th instance.** PUT WALL
  **●●●●● 1.21bn** with the prose *"heaviest floor this week (**125k
  contracts**)"* against CALL WALL **●○○○○ 0.28bn** / *"heaviest ceiling this
  week (**8k contracts**)"*. Contract count for the superlative, dollar gamma for
  the stars, same table. Unlike the 10-22 instance the two agree in rank here,
  so **no damage**; n=4.
- **Max pain — 9th distance-confounded non-test.** Published **+613**, post-scan
  high missed it by **333.6**. The *"strong by Thursday/Friday"* qualifier went
  untested **on a Friday** — **second consecutive session** in which distance
  kills the qualifier on a day the qualifier claims.
- **No instance:** **H3** (CLOSED-NEGATIVE, superseded by H26) · **H4** (flip
  546.0 above the post-scan high) · **H7** (no overnight scan) · **H11** ·
  **H12 / H13** (volume ladder lost to the 401) · **H14** (the put wall never
  broke, so the regime-aware rider went untested) · **H17** (post-scan **37.2%**
  of the session range, far outside the 5% deadband; stays **2 of 3**) · **H20**
  (CLOSED-NEGATIVE, not revived) · **D9** (the one scored headline carries its
  subject) · **D24** (`event_gate: null` correct; all four events forward, none
  hidden) · **the gamma-outvoted cell** (gamma net −3 and the rest −13 agree —
  no outvote; stays **n=5**) · **the *"direction right, strategy block wrong"*
  cell** (both bearish; stays **n=2**).
- **`PIN_THEN_EXPAND` — did NOT fire on 10-23** (`COHERENT_SHORT`). **Stays
  observation 2 of 3; no verdict attached, rules not revised.**
- **The *"whole move over by 10:30 ET"* watch item — NEAR-instance, does not
  extend.** Low **09:35 ET**, high **10:50 ET**: the entire 335pt range was set
  in the first **80 minutes** of cash, and the remaining 6h10 traded inside it —
  but the high is **20 minutes past** the clause as written. Recorded as written;
  **n unchanged**, no re-specification to fit.
- **No new data point is warranted.** Every failure today traces to the
  **dependence structure** or the **vintage** of rows already on the page — two
  collinear pairs carrying −13 of −16, a prior-week rule with no distance term,
  a vol block with no mean-reversion term, and 0.75% news coverage. **No free,
  reliable feed fixes any of those**, and the one structural fix that suggests
  itself was tested above and makes the record worse.

## Carried forward from the 2026-10-26 scan — recorded, NOT graded

- **`PIN_THEN_EXPAND` FIRED AGAIN on the 10-26 scan. That is observation 3 of 3
  and it COMPLETES the pre-registered test** written in the 2026-10-19 block.
  Observations 1 (10-19) and 2 (10-21) both **FALSIFIED** it on the same clause.
  **Clause 5's threshold is met at n=3, so the next review MUST run clauses 1–4
  on the UNREVISED rules against 10-26's bars and then deliver the verdict.**
  10-26 is unfinished and is **not graded here**. **This is the one item that
  must not slip to the session after next.**
- **BEARISH −6** at **29138.0**; offset **+29.5** (clean), roll **+151.0** (an
  up-roll, which is what made this session's realised-basis observation
  discriminating), fuel **MODERATE** `fuel_ratio` **1.34**, budget 216.1, ADR14
  545.4, gamma flip **29489.2**, week net GEX **−2.141**, 45-day −4.755.
- **News relevance failure carrying −1 of a −2 news score.** *"Apple stock rally
  and Nvidia sell-off tighten race for world's most valuable company"* tagged
  **hawkish → bearish long-duration tech**. It is a **company-ranking story with
  no Fed content**. The judgement list separately holds **three genuine Fed-hike
  stories**, so the hawkish *theme* is real even though this *tag* is false —
  **grade the score and the printed reason separately.** This is a D9/D18-family
  candidate; **grep both before writing it up.**
- **`gexbot` HTTP 401 for the 3rd consecutive scan** (appended to D27 above).
  **`gamma +2` bottom-of-band fired a 7th time** — grade it next session.

## Journal hygiene

One scan file for 10-23 (`1248-preny.json` + `.md`), `is_trading_day: true`,
275 bars, `review_day` reports **0 test artefacts** for the day (6 across the
record, excluded by `track.py`). **09-24 quarantined by hand — 19th consecutive
review to carry it**; there is still no schema `quarantine` field and the 09-29
proposal for one is reaffirmed. **2026-10-13 has no journal directory —
documented, not recreated.** **09-09 and 09-25 still have no `REVIEW.md` and
none was created or back-dated.** **2026-10-26 is on disk, `is_trading_day:
true`, 181 bars, correctly held back and NOT graded.** **No `prediction` block
was touched. No scoring, wall or grading code was edited.** No fabricated or
backfilled entries found. **One new ID allocated by this review: H27. Next free:
H28 · D28 · P-I.** `track.py` prints **no literal `actionable: YES/NO`**; the
threshold rule was applied by hand.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01M7sro1DKMp5T7EBDusm6pM
