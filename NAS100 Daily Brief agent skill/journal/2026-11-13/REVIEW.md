# 2026-11-13 (Friday) — review

_Written 2026-11-17, out of order, after the 11-17 brief was delivered. Nothing
here blocked, delayed or altered it. One scan graded: `1246-london.json` /
`.md`, `LONDON` 12:46:41Z, `is_trading_day: true`, **276 bars**, `review_day`
reports **0 test artefacts**. **No `prediction` block was touched. No scoring,
wall or grading code was edited.**_

**Why this is late.** The 11-16 runner cycle was cut short after the archive
step and no reviewer ran, so 11-13 and 11-16 were both unreviewed. 11-16 is the
primary grade and is in `journal/2026-11-16/REVIEW.md`; this file completes the
pair. **Shared infrastructure is reported once, in the 11-16 file** — `track.py`
(exit 0, 30 days / 30 scans, direction **13 right / 13 wrong / 4 no-call**, D26
gap **24**), the ID-allocation grep (**nothing allocated**; H28 · D32 · P-J · M8
all free), and the D6 offset census. **The D29 grading rule (G1–G4) was APPLIED
unchanged.**

---

## 1. Scoreboard

| | |
|---|---|
| call | **STRONGLY BEARISH −16** at 28279.5 (`LONDON`, NY cash +104 min), `PIN_THEN_EXPAND`, `MODERATE` |
| event gate | **non-null — *"STAND ASIDE, Core PPI in 0.7h"*** (3rd firing ever; graded below, a first) |
| session O/H/L/C | **28285.4 / 28503.5 / 27594.4 / 27938.9** |
| range · net | **909.1** (1.03× ADR14 885.7) · **−346.5** |
| direction, post-scan (P-H basis) | **−319.5 → CORRECT** |
| direction, day-net | **−346.5 → CORRECT** · bases **agree**, **no P-H deciding instance** |
| H17 deadband | post-scan move is **35.1%** of session range — outside the proposed 5% band, grade **survives** |
| levels | **21 published / 14 touched = 0.667** (read §2 before quoting this) |
| fuel | budget **524.9**, extension **548.3** → error **+23.4** (**1.04×**); traversal **888.3 = 1.69×** budget; `review_day` verdict *"about right"* |
| VXN-implied budget | **508.6**, the figure §3 told the reader to prefer — realised range beat it by **400.5** (**1.79×**) |
| H26 | score −16 (≥10 bucket), `|post|/ADR` **0.361**, **CORRECT** |
| offset | **−23.9**, basis `nq_implied` — **CLEAN**, inside the ±40 convention |
| bias blocks | macro −4 · vol −3 · rates −3 · news −3 · gamma −2 · breadth −1 (26 rows) |

**This is the best-calibrated fuel call in the 30-scan window bar four**
(+23.4 absolute, against a per-day mean of +103.7) and the direction was right on
both bases. The criticism below is therefore about *what the board and the prose
claimed*, not about the call.

## 2. What the levels actually did

**The 0.667 hit rate is mostly density, not skill.** Of the 21 rows, **13 sat
inside a 350-point band** (28476.1 → 28142.7) that price traversed twice, and
**10 of the 14 touched rows produced no reaction distinguishable from the day's
drift** — all 10 graded `lost`, with worst excursions of 26.2–84.5 on a day that
traversed **888.3**. That is the H6 density artefact in clean form: a board dense
enough that an 888-point traversal cannot miss.

**What actually worked — the options shelves above price, and the farthest one
best.** Three rows carried **identical** canned text (*"Heavy dealer hedging
parked here — expect price to stall. Good place to take partials rather than
push through"*):

| row | dist | outcome |
|---|---|---|
| **28476.1** 0.34bn | +197 | **capped the day.** Post-scan high 28482.7 — **6.6 points** through it; held as resistance **490 min** |
| **28426.1** 0.36bn | +147 | crossed, `lost` by 40.8 — the claim failed |
| **28376.1** 0.19bn | +97 | **sliced by 106.6** (0.12× ADR), then held as resistance 435 min |

One identical sentence, three different outcomes, and **the one that worked was
the farthest away**. That is a second instance supporting the 11-06 resolution
(**propagate §1's *"only take them at the far walls"*** into §2/§3) and it is
also P-E's bimodality showing up in shelves, not just call walls.

**§3's named upside brake (H23).** 28376.1 at +97, *"expect a stall … take
partials into it"*: **sliced by 106.6 = 0.12× ADR**, and it **did** appear on the
board, so the *"the trader cannot mark it"* limb does not apply. By my count this
takes H23 to **21 sliced / 3 capped / 5 never-reached (n=29)**.

**The put wall's "held as support" is an artefact, and a large one.**
27826.1 ●●●●● 0.82bn / 111k contracts, published as *"the strongest floor on the
board"* with the correct short-gamma caveat. `review_day` reports *"stalled at it
— held as **support** for 155min, worst **−24.7**"*. The session low was
**27594.4 = 231.7 points below it**. The settle window opens at 18:20Z, after the
penetration, so the verdict and the excursion are both close-side artefacts:
**M6, session 44, understating by 207.0 points**. The honest reading is that the
strongest floor on the board was **sliced by 0.26× ADR** and only then became
support (close 112.8 above). Reported as expected-by-identity
(`review_day.py:73/94`); no number taken.

**The gamma flip was reclaimed and then lost.** `PD close + GAMMA FLIP 28303.3`
at +24: price was 23.8 **below** it at the scan, which fired the straddle rider
(`gamma +1`, *"regime unstable, reduce conviction"*). Price then traded **179.4
above** the flip on the PPI spike before collapsing 888 points. The rider's
warning was **right** — the regime genuinely was unstable — and §2's unconditional
*"they're pushing, so don't fade"* was briefly false. Credit where it is due:
this is the straddle condition behaving as designed, which is not how H7's
earlier instances went.

**The PDL long instruction WON here, which is the counter-instance to 11-16.**
`PDL + London Low (prev-day) 27911.7` carried the same canned *"Sweep it, wait
for a higher low on the 1m, then CISD = long"* that **lost 390 points on
11-16**. On 11-13 price swept it by **317.3** and closed **27.2 above** it — the
instruction worked. **1–1 across two sessions: the regime-blindness of the
liquidity rows is a condition, not a demonstrated harm, and nothing is proposed
on it.**

**Seven never-reached rows, all above price** (28492.3 → 28838.9), including PWH,
the call wall, max pain and PDH. The nearest, `Equal highs ×3 28492.3`, was
missed by **9.6 on the post-scan high** (28482.7) — just outside the grader's
8.0 tolerance — and `Asia High (today) 28503.5` is the session high **exactly**, filed *"never
reached"* because it was made pre-scan. Both are the standing `TOUCH_TOL = 8.0`
item, and today adds a quantified reason it matters: see §4.

## 3. What was wrong, and why

**(a) `breadth −1` was right for the wrong reason, and D22(a) part 1 kills it.**
*"NDX −0.30% vs ES +0.26% — tech lagging, rotation out of tech"*. Verified from
source: NDX 11-11 28374.25 → 11-12 28289.19 = **−0.300%** (prior session,
matches). `ES=F` 11-11 7640.50 → 11-12 7615.25 = **−0.330%** — so the ES leg's
printed **+0.26%** is wrong by **0.59pp and flips sign**, because
`macro_probe.yahoo_series("ES=F","5d","1d")` takes `last = regularMarketPrice`,
a **live pre-market** print, while the NDX leg is a **prior-session** close.
Corrected to both-prior-session the gap is **+0.03pp**, inside the ±0.2 gate, and
the row becomes **`in line`, 0 points**. This reproduces the 11-13 runner's
finding exactly and agrees with the previous review's conclusion that **11-13
favours part 1, while the overnight basis (part 2) keeps the −1**. No new ask:
D22(a) owns it.

**(b) `breadth +0` averaged a 9.88pp spread to nothing.** *"mega-cap avg +0.34%
(2/4 up): NVDA −4.34%, MSFT +0.36%, AAPL −0.21%, AVGO +5.54%"*. The heaviest
index member fell 4.3% and the row scored **zero** because a smaller name rose
5.5%. This is the unnumbered **averaging-over-dispersion** watch item (register
lines 1714, 15617, plus the 11-05 condition instance) — **condition instance 4**.
Harm is not demonstrable on direction (the call was already right), so nothing is
proposed; but note the correction would have moved the score **toward** the
realised day, which is the opposite of the usual objection.

**(c) `structure +1` *"price above PD mid 28230.0"* was the wrong-signed row** on
a −346.5 day; price closed **291.1 below** that mid. Two-sided row, no claim made.

**(d) The event gate fired, and for the first time it can be GRADED — it
worked.** The gate said: no entries until **30 min after the 13:30Z Core PPI
print**, then *"use the post-print 30-min range H/L as the day's sweep levels"*.
From source, that window (13:30–13:55Z) was **H 28482.7 / L 28285.4**, range
197.3 — and the window itself whipsawed, so standing aside avoided it.
After 14:00Z:

- **H was never revisited** (post-14:00 high 28371.8, **110.9 short**);
- **L was swept at 14:30Z** and price fell a further **690.6 points** to 27594.4
  inside two hours (**0.78× ADR**).

The one directional instruction the gate gave was the correct one and it was
worth 690 points. Firings are now **4** (11-06, 11-10, 11-13, 11-17), **all at
exactly "0.7h"**, and this is the **first with its levels graded**. P-C's
*"the gate has never fired"* sentence is already superseded; this adds the first
outcome. **n=1 on the outcome — nothing proposed, and the ~42-minute window is
still the open question.**

## 4. Change proposals — only material ones

**Nothing new is proposed from 11-13.** Both material proposals from this pass
are in the 11-16 file (D31's measured ×1.596 conversion constant, n=17; and the
correction that the standing **D6 replacement check is an identity on the
`nq_implied` basis and cannot fire**). 11-13 contributes evidence to both: its
VXN-implied 508.6 against a realised 909.1 is counter-instance **16 of 17** in
that census, and its offset of **−23.9** is a clean observation in the D6 series.

**One quantification worth adding to an existing watch item.** `TOUCH_TOL = 8.0`
is read as feed jitter. On the `nq_implied` basis — which is what every current
London scan uses — the **published position of every options level carries a
basis residual with sd 27.3 points** (50-scan census, 11-16 review §4b). The
grader's touch tolerance is therefore **3.4× tighter than the publication noise
of the gamma rows it grades**, and the liquidity rows (price-derived, exact) are
graded on the same tolerance as the gamma rows (estimate-derived, ±27). 11-13
shows the cost in both directions: `Equal highs ×3 28492.3` missed by 9.6 (post-scan) and
`Options shelf 28476.1` credited with capping the day by 6.6 — a 16-point spread
decides one "miss" and one "cap" on levels whose own uncertainty is larger than
both. **Evidence is n=50 on the noise figure but n=2 on cases where it changed a
verdict (11-13 here, plus the 08-28 case already in the register), so this is an
observation appended to the existing item, not a proposal.**

**What is being watched from this session, with counts:**

- **H23** — instance 29, sliced by 0.12× ADR, strike on the board. Census 21/3/5.
- **M6** — session 44, understating by **207.0** points.
- **"Far walls" resolution** (11-06) — second supporting instance: of three identically-worded shelves, only the farthest capped.
- **PDL *"CISD = long"*** — **1 win (11-13) / 1 loss (11-16)**. Condition only.
- **Averaging-over-dispersion** — condition instance 4.
- **Event gate** — firing 3 of 4, first graded outcome, **positive**.
- **H1** — error +23.4. **H10** — did not fire (price inside the prior-week range). **H19** — coverage **6.2%** (5 of 81), right-signed on a −346.5 day.
- **P5** — 6 secondary strikes published, 0 graded. The 11-16 session supplies the strong instance; 11-13's go on the count.
