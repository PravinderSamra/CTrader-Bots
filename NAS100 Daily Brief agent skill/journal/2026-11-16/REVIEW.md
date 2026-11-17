# 2026-11-16 (Monday) — review

_Written 2026-11-17 after the 11-17 brief was delivered. Nothing here blocked,
delayed or altered it. One scan graded: `1246-london.json` / `.md`, `LONDON`
12:46:55Z, `is_trading_day: true`, **264 bars**, `review_day` reports **0 test
artefacts**. **No `prediction` block was touched. No scoring, wall or grading
code was edited.**_

**Two days were unreviewed, not one.** The 11-16 runner cycle was cut short
after the archive step, so no reviewer ran. **2026-11-13 is graded in
`journal/2026-11-13/REVIEW.md`, written in the same pass as this file.** Neither
day is left on the record ungraded.

**`track.py` COMPLETED (exit 0, ~37 min)** — 30 trading days / 30 scans.
**This build emits no `actionable: YES/NO` string** (flagged on 11-12 and still
true); the equivalent header line was used and is quoted rather than silently
substituted: *"30 of 3 days for the 3-day hypotheses — threshold met, read the
evidence before proposing"*. **Direction crosses back to exactly 50%: 13 right /
13 wrong / 4 no-call**, against the carried 11/14/6 = 44.0% — and that is **not
new data**: 10-01 and 10-02 aged out of the 45-day bar window on this run while
11-13 and 11-16 entered, both CORRECT. **D26's gap WIDENS to 24** (30 graded bar
sets against **54** finished trading-day directories).

**ID allocation: NOTHING allocated.** Next free confirmed by `grep -c` on
2026-11-17: `^## H28` 0 · `^## D32` 0 · `^## P-J` 0 · `^## M8` 0. Everything
below lands on an existing entry, as an observation or as a correction to a live
proposal. **The D29 grading rule (G1–G4) was APPLIED unchanged, not
re-decided**; G1 is applied to the session-context instance in §2.

---

## 1. Scoreboard

| | |
|---|---|
| call | **STRONGLY BEARISH −15** at 27602.8 (`LONDON`, NY cash +103 min), `COHERENT_SHORT`, `LOW_FUEL` |
| session O/H/L/C | **28030.4 / 28188.6 / 27146.5 / 27204.3** |
| range · net | **1042.1** (1.14× ADR14 911.7) · **−826.1** |
| direction, post-scan (P-H basis) | **−379.8 → CORRECT** |
| direction, day-net | **−826.1 → CORRECT** · bases **agree**, **no P-H deciding instance** |
| H17 deadband | post-scan move is **36.4%** of session range — far outside the proposed 5% band, so the CORRECT **survives** H17 |
| levels | **8 published / 3 touched = 0.375** |
| fuel | budget **188.2**, extension **318.6** → error **+130.4** (**1.69×**); traversal **478.5 = 2.54×** budget; `review_day` verdict *"UNDER-estimated"* |
| VXN-implied budget | **510.9**, the figure §3 told the reader to prefer — realised range beat it by **531.2** (**2.04×**) |
| H26 | score −15 (≥10 bucket), `|post|/ADR` **0.417**, **CORRECT** |
| bias blocks | macro −4 · gamma −3 · breadth −3 · news −3 · vol −1 · rates −1 (26 rows) |

Right-signed rows: `gamma −3`, `vol −1/−1`, `rates −1`, `macro −3/−1`,
`breadth −2/−1`, `news −3`, `structure −1`. Wrong-signed: **`gamma +2`**,
**`structure +1`**, **`vol +1`**. The three wrong-signed rows total **+4** on a
**−826** day; the score would have been −19 without them.

## 2. What the levels actually did

**Three of eight touched, and all three were already in play before the scan.**
The five never-reached rows were all above price: four were correctly tagged
_(stretch)_ against a 188pt budget, and the fifth — **London High (today)
27764.8** at +162, the only reachable row above price — was missed by **139.8**
(post-scan high 27625.0 at 14:45Z).

| level | brief said | what happened | verdict |
|---|---|---|---|
| **27594.4** PDL (−8) | *"the biggest pile of stops below us. Sweep it, wait for a higher low on the 1m, then **CISD = long**"* | already 8.4 below price at the scan; settled below from 14:40 for 375 min; **close 390.1 below** | **the instruction lost.** A long trigger on a day §1 and §2 both said not to fade |
| **27569.0** Asia Low + **PUT WALL ●●●●● 0.61bn** (−34) | *"Heaviest floor this week (31k contracts) … the **strongest floor on the board**"* — **with** the regime caveat *"if it breaks, expect it to speed UP, not bounce. Don't buy the break"* | **already broken 41 min before the scan** (first 5-min bar below at **12:05Z**, pre-scan low **27465.1 at 12:30Z = 101.7 through**); after the scan price ran to **422.5 below** it | **the caveat was right, the floor framing was already false when it was printed** |
| **27465.1** London Low (today) (−138) | *"the next session usually runs the stops below it"* | ran **318.6** below it; once lost, held as resistance 260 min (worst +22.0) | **right** |

**The board had nothing where the day actually traded.** The lowest published row
was 27465.1. The session low was **27146.5 (−318.6)** and the **close 27204.3
(−260.8)**: the entire afternoon from 15:00Z onward traded below every level on
the board. This is the **level-board void** watch item, **instance 4**, and its
first instance where the *close* as well as the low sits inside the void
(11-11's was an upside void containing the session high).

**The void was covered — by the table that is never graded.** The *"Other gamma
concentrations"* rows **27366.8** and **27166.8** sat exactly in it, and
**27166.8** is **20.3 points** off the session low: price first reached it at
18:35Z, **never printed a single 5-min bar entirely below it**, and closed
**37.5 above** it. It was published as *"dealers are SHORT gamma here, so they
**amplify** … **Not a floor**"*. It was the floor. **P5 instance 2 of its own
founding shape** (the 08-26 case was identical: *"not a floor"*, 9.6 through,
closed back above) — still ungraded by `review_day`, still asserted in every
brief.

**M6, session 45, and the understatement is large.** All three touched rows
settled `below` on a day that closed 57.8 off its low, so `held`/`acted_as` are
close-side artefacts by construction. The put-wall row reports
`worst_excursion 56.0` on a level price finished **422.5** through — an
understatement of **366.5 points**. Reported as expected-by-identity
(`review_day.py:73/94`), no number taken.

**H23 is a non-instance**: both paths printed *clear*, so §3 named no brake.

## 3. What was wrong, and why

The direction was right. Three things were wrong, and two of them are the
*prose*, which is where this brief's remaining risk lives.

**(a) The fuel block told the reader to fade on the day the break ran — census
now 7–2 to gamma.** `fuel +0` scores nothing, but §3's *"The range is close to
done … favour **fades** over chasing breaks"* sat **four lines below** its own
*"DOWNSIDE path: clear … **Do not fade it**"* and ~40 lines below §2's
*"**Fading is the wrong trade today**"*. Realised: extension **1.69×** budget,
traversal **2.54×**, and a fade at any touched row lost **318.6–422.5** points.
Driver: `adr_used_pct 79.4` at 07:46 ET → `LOW_FUEL` → the fade prose, with no
gamma condition on it. Census (LOW_FUEL/EXHAUSTED ∩ below flip): **6–2 → 7–2 to
gamma**, and **11-16 is the second instance where the contradiction is inside
§3** (11-05 was the first).

This also answers an item the **11-12 review declined**: *both paths clear* was
declined there because it *"is not paired with a fade instruction"*. On 11-16 it
**is** — both-paths-clear and *"favour fades"* are in the same section, four
lines apart. The 11-06 resolution still looks right: propagate §1's *"only take
them at the far walls"* into §2 and §3 rather than pick a block. Note that on
11-16 the far-wall fade **would have won** — at **27166.8**, which is not on the
board (§2 above).

**(b) `gamma +2` — D21's gate fires a second time and is wrong a second time,
and the mechanism it was given does not cover this one.** *"Price sits in the
bottom 20% of the wall band (27566.8–28166.8) — poor risk/reward for shorts"*,
+2, at 6% up the band. Price left the band **downward** and never returned:
low **420.3** and close **362.5 below the band bottom**. Firings now **2, both
wrong, one on each branch** (11-11 top-of-band against longs, 11-16
bottom-of-band against shorts), same failure shape in both — price exits the
band in the direction the row says has poor risk/reward and does not come back.
**The condition D21 recorded at n=2 — *"price was already outside the prior
day's range, so the band is stale"* — is ABSENT here**: price at 27602.8 was
**inside** the prior day's range (PDL 27594.4), by 8.4 points. So the stale-band
explanation does not generalise. **2 firings is not 3 sessions: nothing
proposed.** It was also the largest single wrong-signed row in the score.

**(c) `structure +1` — the pool counter says "draw higher" exactly when
everything below has just been swept.** *"In-reach unmitigated pools: 2 above /
0 below — draw higher"*, on the largest down day in the window. The count is
**zero below** because the pre-scan session had already run 723.5 points and
mitigated them; the rule reads an exhausted downside as an absent one. The row
has been right on up days before (register, 3 prior observations), so this is
**two-sided and not a bias claim** — recorded, nothing proposed.

**Honest credit where the evidence gives it:** `news −3` came from **3 of 66
relevant headlines (4.5% coverage)** — H19's complaint — and was **right-signed
on an −826 day**, as it was on 11-13. `gamma −3` (below flip by 954.7, dealers
amplify) was the best row on the page: the amplification arrived and pointed
**down**, which is the branch H27's census has been waiting to see behave.

**(d) The D6 breach — established, not taken on trust.** See §4(b): the breach
is real and is the **seventh**, the reference was built **correctly**, and the
harm on this day is **nil** (every options row was ≥564 points from price except
the put wall, whose verdict is invariant to a ±66.8 shift — price finished 422.5
below it either way).

## 4. Change proposals — only material ones

### (a) PROPOSED, on an existing entry — D31's comparison has a known conversion constant, and it is measured

**What to change.** D31 already proposes deleting §3's instruction *"below ADR —
options market prices a quieter day, **use the smaller budget**"* because the
VXN-implied figure is a **1σ close-to-close** move (`brief.py:996`,
`px * vxn/100 / sqrt(252)`) compared against `adr14`, a **high-low** average.
Add the constant: a driftless random walk's expected high-low range is
**√(8/π) = 1.596σ**, so the two are not comparable until the implied figure is
multiplied by ~1.6.

**Evidence (new, from source, n=17 consecutive sessions 10-26 → 11-17).**
Realised range ÷ VXN-implied range: **15 of 17 above 1.0**, mean **1.70**,
median **1.54**. The median is within **3%** of the theoretical 1.596 — the
series is not noise around 1.0, it is a scale error with a known factor.
Same window, realised range ÷ `adr14`: median **1.05** — `adr14` is the
well-calibrated one, which is the opposite of what the instruction says.
11-13 (509 vs 909) and 11-16 (511 vs 1042) are the two most recent points.

**Expected effect.** Prose only, no scoring, no multiplier, nothing tuned: the
instruction that currently tells the reader to prefer the smaller number is
deleted, and the figure is either printed with the ×1.6 conversion or printed
with its existing caveat and no instruction attached. On the 17 days measured
this stops the brief recommending a budget that was too small on 15 of them.

### (b) CORRECTION to a live proposal — the D6 replacement check is an IDENTITY on the basis every current scan uses, and cannot fire

This is the substantive finding of the pass, and it is a correction, not a new ID.

**The breach is real and the count is SEVEN, not two.** From the printed
offsets, the `nq_implied` series beyond ±40 is: **09-28 +45.9 · 10-12 +43.1 ·
10-14 +41.8 · 10-15 +77.6 · 10-20 +74.5 · 11-04 −68.8 · 11-16 +66.8**. The
register already carried six (11-04 was logged as the sixth and the first
materially negative one) and already carried **10-29 +39.3 as the closest
near-breach without tripping**. 11-16 is the **seventh**, and the largest
positive since 10-15.

**The reference was built correctly — verified independently.** Yahoo `^NDX`
11-13 close **27943.74**; `NQ=F` 11-13 close **28034.75**; the brief's roll
**−407.8** gives **27535.94** against the published reference **27536.0**
(0.06pt). Not a stale feed.

**The premium hypothesis is dead, and for a stronger reason than a weak r.**
`gex_levels._nq_implied_cash()` returns `cash_close + (NQ_now − NQ_prev_close)`,
so the **level** of the NQ–NDX premium is differenced out by construction; only
a *change* in it can reach the offset. Substituting the code gives an exact
identity, which I verified on **50 of 50** `nq_implied` scans to within ±0.2
(rounding):

```
offset  =  (CFD_scan − NQ_scan)  +  (NQ_prev_close − NDX_prev_close)
             ^ broker CFD basis       ^ premium at the prior cash close
```

Both terms are **market basis quantities, not errors**. Across the 50 scans each
term has sd ≈ **90** and they very nearly cancel: the offset's sd is **27.3**.
So a ±40 line is **1.46σ** of ordinary basis residual and fires ~**14%** of the
time (7/50) with nothing broken. The runner's regression of the offset on the
premium **level** (r = +0.334) was testing a constant: correct conclusion,
wrong regressor. **I tested the other candidate available in the record and it
also fails** — offset vs the printed overnight NQ roll, n=50: **r = −0.365**
signed, **+0.009** on absolutes. Two mechanisms falsified; the residual
mechanism is the broker's pre-market CFD basis, which on 11-16 sat **24.2 below
NQ** against a prior-close premium of **91.0** (i.e. the CFD was ~60 rich
against its usual cash-tracking relation, and it converged: at the cash close
the CFD was **+7.1** vs NDX cash).

**Why this is a correction.** The register's standing D6 replacement (09-24
entry, repeated 09-29 / 09-30 / 10-01 and "awaiting an independently measured
NQ-minus-premium level") is: *gate on reference-vs-futures agreement, not on
offset magnitude*, i.e. compare `brief_ref` against `NQ_now − premium_prev_close`.
Substituting the construction:

```
NQ_now − premium_prev  =  (NQ_prev + roll) − (NQ_prev − NDX_prev)  =  NDX_prev + roll  =  brief_ref
```

**It is the same number.** On the `nq_implied` basis the proposed check returns
0 by algebra and can never fire — the same defect class as **D16** (the
straddle rider's no-op ternary) and the identity the 11-13 review found in
D22(a)'s DXY description. It remains valid on the **`live_cash`** path, which is
where 09-24 actually failed. **Since 50 of the last 50 London scans used
`nq_implied`, shipping it as written replaces a weak detector with a dead one.**
Re-scope it to `live_cash` / `live_cash_divergence_corrected` explicitly.

**One more structural fact, same family.** The only *implemented* guard,
`CASH_DIVERGENCE_TOL = 25.0` vs an independent Yahoo `^NDX` print, is
**structurally inert pre-market**: both sources return the same prior-session
close, so the divergence is ~0 and the check passes trivially before the
`nq_implied` branch is taken. D6's own closing caveat — *"both sources could lag
together"* — is therefore the standing condition on **every** London scan, not an
edge case.

**What I am NOT proposing, and why.** No new threshold, and specifically **not**
the register's *"abort the options block beyond ~40pts"* idea: across the seven
breaches there is **no demonstrated tape harm**, and on 11-16 the verdict is
invariant to the whole 66.8 (flip/max-pain/call-wall were 564–955 away; the put
wall is lost by 422.5 at either price). An abort would have deleted the options
block on seven harmless days. For the record, the *honest* magnitude test on this
basis is deviation from a trailing median rather than from zero — on a trailing-10
median it flags **10-15, 10-20, 10-21, 11-04, 11-16** (11-16 the largest in the
series at **+82.8**) and clears 09-28/10-12/10-14 as ordinary for their era. That
is a **measurement**, offered as evidence for the re-scoping, **not** a proposed gate.

### (c) Nothing else is proposed. What is being watched, with counts

- **Level-board void** — instance **4**, first with the close inside it. n=4 condition, harm not demonstrable (no trade instruction pointed into the void). Nothing proposed.
- **P5** — instance **2** of its founding shape (27166.8 *"not a floor"* was the floor, 20.3 through, closed 37.5 above). Already PROPOSED; this is evidence, not a new ask.
- **D21** — gate firings **2, wrong 2**, one per branch; the stale-band mechanism does **not** apply to 11-16. Below the 3-session bar.
- **Fuel-vs-gamma coherence** — census **7–2 to gamma**, second inside-§3 instance. The fix stays the 11-06 formulation (propagate *"only at the far walls"*).
- **The §3 "clear corridor" far end landed 20.3 (11-16) and 31.7 (11-13) from the session low** — the two closest in a 16-session census I built from source; the rest of the distribution runs −1047.8 to +795.8. **Two sessions is noise and the distribution says so**; recorded so it is not mistaken for a signal later.
- **Session-context field** (put wall published as an intact floor after the same session broke it by 101.7, 16 minutes earlier): **G1 applied unchanged** — the frozen `PRE_NY` denominator stays 22, and this accrues to the parallel `LONDON/EST` census only. That census now holds **3** harm-shaped instances in the EST era.
- **H2** — LOW_FUEL instance, **continuation won** decisively (break ran 390 past the PDL; every board-row fade lost 318.6–422.5). Census not restated; the instance is recorded.
- **H1** — error **+130.4**; `track.py` per-day mean **+103.7** (n=30), against the carried +103.0.
- **H10** — did not fire (price inside the prior-week range).
- **H19** — coverage **4.5%** (3 of 66), right-signed. **The news block's 0-of-63 on 11-17 is NOT a first**: `scored_high_confidence == 0` has occurred on **10 scans / 9 trading days** (08-26 ×2, 08-28, 09-29, 10-02, 10-07, 10-16, 10-27, 11-05, 11-17). Not a dead-component instance; the scorer found nothing matching, which it does roughly one day in eight.
- **The "(N checks)" count is explained and is not a defect.** 11-17's **22** against 25–26 is arithmetic: the news block emits **1** row instead of 4 when nothing scores (no per-headline bullets) and the fuel block emits **1** instead of 2 outside `LOW_FUEL`/`EXHAUSTED`. 26 − 3 − 1 = 22. Worth one cosmetic note, nothing proposed: the label *"checks"* counts rows that are not checks — the three `news +0` headline bullets inflate it on a normal day.
