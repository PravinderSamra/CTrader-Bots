# Review — trading day 2026-11-19 (graded 2026-11-20)

One scan: `1247-london.json`, `is_trading_day: true`, `outcome: null`, 276 bars,
`review_day` reports **0 test artefacts**. Exactly **one commit**
(`f213b72`, *"NAS100 archive: 4 file(s) from a scan/review"*) touches both the
`.json` and the `.md` — written once, never edited; no `prediction` block was
touched by this review. No `is_trading_day: false` scan entered any statistic
below.

**TODAY'S 2026-11-20 SCAN DID NOT RUN AND IS NOT GRADED HERE.** `brief.py`
exited 1 on an unhandled `HTTPError` out of `gex_levels.build()`. There is no
11-20 brief, chart, journal entry or archive commit; `journal/2026-11-20/` does
not exist, `index.json` ends at `2026-11-19/1247-london.json` (88 entries), and
`find` returns no file named for 11-20 anywhere in the repo. The absence is a
**hard data-source failure, not a missed scan and not a mystery** — it is
written up as **D33** in §4 and in the register header, with the outage verified
independently below. **Nothing in this review needed CBOE:** `review_day.py`
reads the stored `prediction` block and cTrader M5 bars and ran clean, so the
11-19 grading is complete. The one item left open for an unrelated reason is
`track.py`, noted in §1.

---

## 1. Scoreboard

| | |
|---|---|
| session O / H / L / C | 27107.0 / 27756.0 / 26478.5 / **26510.0** |
| range · net | **1277.5** · **−597.0** (DOWN day) |
| call | **+5 MILDLY BULLISH**, `expected_direction +1`, `COHERENT_LONG`, Strategy 1 |
| price at scan (12:47Z) | 27654.0 — **+547.0 above the open, 102.0 below the eventual high** |
| post-scan move | **−1148.0** → **WRONG** |
| day-net basis | **−597.0** → also **WRONG** — bases AGREE, **no P-H deciding instance** |
| H17 noise test | post-scan is **89.9%** of session range — far outside the 5% band and at the opposite pole from H17's 0.2–3.89% cases (no claim made about the all-time maximum) |
| levels published · touched | 16 · 12 → hit rate **0.75** |
| of the 12 touched, settled verdict | **3 held · 9 lost · 0 ungraded** |
| side of the board that was used | all **9** rows below the scan price were touched, plus the **3 nearest above** (within 103pts); the **4 rows never reached are the 4 highest on the board**, 134–734pts up |
| **12 of 12 touched rows sit above the close** | so 12 of 12 verdicts were decided by `bars[-1]["close"]` — M6 at full scale |
| budget · extension · error | 271.8 · 581.1 · **+309.3** (2.14×) — **UNDER-estimated** |
| traversal vs budget | 1277.5 · **4.70×** |
| realised ÷ ADR14 | 1277.5 / 968.2 = **1.319×** |
| realised ÷ VXN-implied | 1277.5 / 577.0 = **2.214×** (D31 supporting) |
| straddle band (§3) | close-to-close ±563 → 27091 .. 28217; close **26510.0 = 581.0 BELOW the band** |
| gamma flip | scored 27352.4 / board row 27356.6 → close **842.4 below** the scored flip |
| CFD/index offset | **−11.8**, basis `nq_implied` (D23 clean; D6 breach census stays **SEVEN**) |
| `track.py` after this day | 31 days / 31 scans · **13 R / 14 W / 4 no-call = 48.1%** · H1 per-day mean **105.7** · fleet levels-touched **0.50** |

`track.py` **completed, exit 0**, after ~27 minutes. **Direction crosses back
below 50%: 13 R / 14 W / 4 no-call = 48.1%**, from 14/13/4 = 51.9%. **That is
not one data point, and its composition is exactly what yesterday predicted:**
11-19 enters as a **WRONG** *and* **2026-10-05 has now fully aged out of the
45-day bar window** (the table starts 10-07), taking a **CORRECT** with it — two
changes, same direction. **D26 again:** `2026-10-06` is reported under *"HELD
BACK — day not finished"* at **97 bars**, a session six weeks past, conflating
*aged out of the fetch window* with *unfinished* — the third consecutive review
to see this (09-28 on 11-12, 10-05 on 11-19, 10-06 today). **D26's gap widens to
26**: 31 full bar sets against **57** finished trading-day directories, counted
from disk by `is_trading_day`.

**H1 per-day mean 89.9 → 105.7** on 11-19's **+309.3**, with the distribution
still two-sided (the printed per-day list runs from **−283.9** to **+1261.2**).
**H2's low-fuel table now holds 12 in-window scans at 6 CORRECT / 5 WRONG / 1
no-call**, with 11-19 the largest traversal in it after 11-05 (**1277.5**).

This build still emits **no `actionable: YES/NO` string** (`grep` returns 0); the
header line — *"31 of 3 days for the 3-day hypotheses … threshold met, read the
evidence before proposing"* — was used and is quoted, not silently substituted.
Third consecutive review to report its absence.

Arithmetic above is `review_day.py --json` as published. Nothing was recomputed.

---

## 2. What the levels actually did

**The upside half of the board was never tested. The downside half was not
support — it was a list of prices the day went through.**

### The one that worked, and it is the best call in the brief

| row | published note | what happened |
|---|---|---|
| **27757.0** Equal highs ×2 + London High ⭐ | *"2 touches at this price, never traded through — a real stop cluster. **Prime S1 sweep trigger**"* | session high **27756.0** — **1.0 point** below the row. Price reversed off it at 14:35Z and fell **1277.5** points. |

The brief named the turn of the day to one point, on a **liquidity** row, and
named it as the Strategy-1 trigger. That is the product working. §3 traces why
the rest of the document stopped you using it.

### The strongest level on the board was sliced and never seen again

| row | published note | what happened |
|---|---|---|
| **27588.2** PUT WALL ●●●●● 1.04bn | *"Heaviest floor this week (79k contracts) — **expect a bounce and a good long-sweep here**. It is ALSO the 45-day put wall (182k contracts) — **defended across expiries, so it is the strongest floor on the board**"* | traded **1109.7 points** through it; closed **1078.2 below**. Graded *"broke UP through it — **lost by 27.7pts**"*. |

Two defects in one row. The verdict word is **inverted** (`review_day.py:160–161`
names the side price settled on, not the side it broke — M6), and the magnitude
is understated **40.1×** — larger than any ratio recorded in the M6 entries
checked for this review (prior maximum **5.7×**, 11-18) — because `settled_read` measures the excursion only
*after* the last bar that closed on the far side (`:87–98`). Worse: `held` is
false by **2.7 points** (excursion 27.7 against `SETTLE_TOL = 25.0`). Had the
retrace been 24.9, the strongest floor on the board — traded through by more
than an ADR — would have been published in the record as **`held: true`,
`acted_as: resistance`**. The verdict on the most important level of the day
hung on a 2.7-point margin of a quantity 40× too small.

### Everything else on the put side: nine rows, nine slices

27688.2 · 27616.9 · 27588.2 · 27546.5 · 27538.2 · 27526.5 · 27356.6 · 27343.4 ·
27244.5 — all `held: false`, all settled below, and **all nine print "broke UP
through it"** on a day where every one of them broke **down**. That is **+9
inverted rows** for M6 (increment only; the standing census is not restated).

The three `held: true` rows (27757.0 · 27738.2 · 27606.2) all read *"held as
**resistance**"*. They are true and near-tautological: every level above the
close "holds as resistance" when the close is 1200 points below it. **27606.2**
is the honest M6 instance of the three — `worst_excursion +9.7` against a
first-touch `travel_up` of **44.9**, understated **4.6×**, verdict `held: true`
on a level price traded 44.9 through. Same shape as 11-18's put wall, smaller.

### Four rows never reached, and all four were above

28388.2 (structural, +734, correctly framed as *"not an intraday trigger"*) ·
27888.2 · 27838.2 · **27788.2 CALL WALL ●●●○○ + MAX PAIN**. The call wall missed
by **32.2 points** — *"rallies stall, take profit into it"* was never tested,
and **max pain 27788.2 finished 1278.2 points from the close** on a Thursday of
expiry week. The adjacent liquidity row 31 points below it is what actually
caught the high.

### The void below the board — instance 6, and the largest harm case yet

The lowest published row is **27244.5**. The session low is **26478.5** and the
close **26510.0**, i.e. **766.0 points below the bottom of the board**.
**66.7% of the post-scan move (766.0 of 1148.0) happened below every level the
brief published.** 11-18's harm case was a 337.5-point hole with the low inside
it; today the hole is open-ended and contains two thirds of the move. The board was
split **7 rows above the scan price / 9 below**; the three nearest above were
touched on the way to the high and the other four never were, so the day spent
its whole afternoon in unmarked space, below a board whose lowest row it had
already passed by 15:30Z.

### The secondary gamma table — four "support" calls, four failures, zero graded

| strike | published claim | what happened |
|---|---|---|
| 27488.2 | *"dealers are LONG gamma here… expect a stall and dip-buying, it acts as **support**"* | sliced, no stall |
| 27388.2 | same | sliced |
| 27188.2 | same | sliced |
| 26988.2 | same | sliced by **509.7** to the low |
| 27988.2 | *"they **amplify**… Not a floor"* | never reached |
| 28188.2 | *"rallies lose momentum into it"* | never reached |

Four explicit, in-range **support** assertions, all four wrong on the same day,
and **none of them is in `prediction.levels`, so `review_day.py` scored none of
them**. This is **P5**'s founding shape at its strongest: the first session with
a clean 4-of-4 failure. Instance **4**.

### The two named brakes in §3 — both reachable, both sliced, no split

- *"**DOWNSIDE path: has friction.** Expect a stall at 27538.2 (116pts away) —
  take partials into it rather than assuming a clean breakdown."* → sliced by
  **1059.7 = 1.094× ADR**.
- *"**UPSIDE path: has friction.** Expect a stall at 27688.2 (34pts away)."* →
  first-touched 13:00Z, exceeded, then lost; settled below.

**H23 instances +2.** The downside slice at **1.094× ADR** is larger than every
magnitude recorded in H23's own tables (series max **0.69×**, 10-05; the four
most recent increments are 0.18× / 0.294× / 0.33× / 0.358×). H23's threshold was
met on 10-02 and its proposal is still unshipped.

---

## 3. What was wrong, and why

### The direction call: the two blocks that were right were outvoted by two blocks that were stale or wrong

`inputs.bias_components` sums to +5 as published (gamma +4, vol −4, rates +1,
macro +4, breadth −1, fuel 0, structure +1, news 0). Traced:

| block | pts | was it right? |
|---|---|---|
| **vol** | **−4** | **RIGHT, and it was the only block that described the day.** *"VIX9D/VIX 1.076 BACKWARDATED — near-term stress, **expect range expansion, downside skew**"* (−2), VXN/VIX 1.49 tech-specific stress (−1), VVIX 118.37 active tail hedging (−1). The day delivered 1.319× ADR and −597. |
| **gamma** | **+4** | **WRONG on both rows.** *"above flip by 301.6pts — long-gamma, dips supported"* (+2) and *"week net GEX 2.866 $bn/1% → **pinning likely**"* (+2). Realised range 1.319× ADR is the opposite of pinning, and the dip was not supported — price lost the flip and accelerated. |
| **macro** | **+4** | **Not wrong so much as not about today.** +3 DFII10 and +1 DGS10 both resolve to **2026-11-17 observations** — the brief prints its own warning (*"FRED has not published since 2026-11-17… this is last week's reading"*) and scores it at full weight anyway. |
| rates | +1 | US10y −0.72%. Right-signed on the stated logic, 1 point. |
| breadth | −1 | *"NDX +0.42% vs ES +1.16% — tech lagging"*. Right-signed by accident: **yesterday's review established this row is inverted** (true prior-session ES −0.251%), so the correct row is **+1**. See the cost ledger below. |
| structure | +1 | price above PD mid. Closed **674.5 below** PD mid. |
| fuel | 0 | correctly carries no direction, and correctly flagged *"burning hot"*. |
| news | 0 | NEUTRAL from 2 scored headlines of 53 relevant (**3.8% coverage**) while *"Nvidia faces 2028 growth concerns as UBS cuts price target"* sat unscored in the judgement list on a −597 day. **H19 instance.** |

**The arithmetic that matters: the only two blocks fed by same-day data were
`gamma +4` and `vol −4`, and they cancelled exactly.** The entire published +5
came from `macro +4` (two FRED rows two business days old), `rates +1`,
`structure +1` and `breadth −1`. Yesterday's review logged that configuration as
*"condition n=4, harm NOT established."* **Today establishes the harm, with a
counterfactual:** drop the two stale FRED rows and the score is **+1**, which is
inside `journal.py:68`'s `|score| >= 3` band → `expected_direction 0` → **NO
CALL**. The stale block is the difference between a wrong directional call and
no call at all on a 1148-point adverse move.

### The strategy was right and three separate instructions stopped you using it

This is the sharpest finding of the day, and it is not a scoring error.

- §1 picked **Strategy 1 — sweep → failed re-break → CISD reversal**.
- §2 said *"**Sweeps of a high or low tend to genuinely fail** — exactly what
  Strategy 1 needs. **This is your fade day.**"*
- §4 marked **27757.0** as *"**Prime S1 sweep trigger**"*.

Price swept that trigger to within **1.0 point** and reversed **1277.5**. The
mechanism fired exactly as written. What the document did with it:

1. **`expected_direction` is +1.** The graded call is the opposite side of the
   trade the strategy block had just described. The score and the strategy
   disagreed, and the strategy won.
2. **§3: *"The range is close to done. Expect price to keep MOVING but mostly
   inside the extremes rather than making new ones"*** — on a day that added
   **581.1** points of new range, 2.14× the stated budget.
3. **§2 `COHERENT_LONG`: *"Expect a tight, pinned range… **Keep targets
   modest**; breakouts mostly fail"*** and *"Today's remaining range budget is
   272pts — anything marked (stretch) is partials-only"*, which marked the
   gamma flip, the prev-day London high and the prev-day NY high — i.e. **every
   level in the direction price actually went** — as partials-only.

The brief contained the trade and three reasons to close it at ~272 points of a
1148-point move. The fuel block and the gamma block **agreed** today (both said
fade, pin, modest), so this is not a fuel-vs-gamma conflict instance — it is the
11-11 shape: every block agreed and the day falsified them together.

### The one conditional that was right, and it was the most valuable sentence in the document

§2 and the 27356.6 board row both carried: *"It stops working below **27352.4**.
If price loses that and holds below, they flip to pushing moves along instead —
**stop fading**."* Price lost the flip at 15:20Z and travelled a further
**874.1** points to the low. The flip failed completely as a magnet or
settlement level (**H4** stays failed; close 842.4 below it) and worked as a
**regime switch**. Recorded as a success instance for the flip-loss rider; n is
not restated here.

### The gamma-pinning vs vol-expansion conflict — 5th co-occurrence, and vol wins by the largest margin

| day | gamma row | vol row | outcome | right |
|---|---|---|---|---|
| 09-16 | +2 pinning | −2 expansion | 1.38× ADR | vol |
| 09-17 | +2 pinning | −2 expansion | extension 40.0 inside | gamma |
| 10-08 | −2 expansion | +1 *"rangebound"* | 1.46× ADR | gamma |
| 10-14 | −2 expansion | +1 *"rangebound"* | 1.88× ADR | gamma |
| **11-19** | **+2 pinning** | **−2 expansion** | **1.319× ADR, extension 2.14× budget** | **vol** |

Census **3–1 → 3–2 to gamma**. The **pre-registered** test (positive net GEX
**and** backwardated VIX9D/VIX) can only be fed by the three same-configuration
days — 09-16, 09-17, 11-19 — and those stand at **2–1 to vol**. The threshold of
3 is now met on the registered configuration for the first time, and the answer
is **split**, so nothing is proposed. The 10-09 ask (log both values and the
realised range every scan regardless of sign configuration) is unchanged and
still the right next step.

### Correction to a figure carried into yesterday's review

Yesterday's entry flagged D25's *"§7 non-render"* counter as *"not
reconciling"*. **Re-derived from disk, it reconciles, and the reason is
mechanical: §7 cannot render while the GEXBot 401 persists.**
`brief.py:723–730` returns the one-line
`_[volume-weighted view unavailable: …]_` **instead of** section 7 whenever
`gexbot` carries an error. Derived per trading-day scan brief: last §7 render
**2026-10-21**, and the 401 line appears on **every scan brief from 2026-10-22
through 2026-11-19 — 21 consecutive trading days, the identical window.** So the
21 non-renders are **21 D27 suppressions, not 21 D25 instances**, and D25's
instance counter is correct not to advance through them. The two numbers were
never measuring the same thing. (Noted for the record: the runner's *"20
consecutive days"* for the 401 is **21** on this derivation. Git shows **no
commit** to the skill's `scripts/` anywhere near 10-21, so the shared boundary
has no code explanation in this repo — it is a credential or upstream change,
flagged, not diagnosed.)

### The D22(a) repair now has a cost, and it is on this day

Yesterday established, from an independent fetch, that 11-19's breadth row is
inverted: corrected, `breadth −1 → +1`, score **+5 → +7**, and
`bias_engine.py:268` bands that as **BULLISH**, not MILDLY BULLISH.
**11-19 is now graded WRONG on both bases.** So the repair's effect on this day
is to make a wrong call **stronger**: it does not flip a direction grade — the
call is +1 either way — but it upgrades the label and the stated conviction on a
day price fell 1148 points post-scan. Yesterday's ledger read *"the cost is
zero"* on 11-18; **that sentence was specific to 11-18 and must not be
generalised.** The ledger now reads: **part 1 is grade-affecting on 2 days
(11-18 direction, 11-19 label); on 11-18 the cost is zero; on 11-19 it is
adverse.** This does not argue against shipping the repair — a correct input is
correct regardless of which way the day went — but the honest statement is that
the first graded test of the corrected row moved the score **away** from the
realised day, and the case for shipping rests on correctness, not on measured
improvement. Part 2 (the NDX overnight-window leg) is untouched by this.

### Other entries taking data points (no proposal attached)

- **H1** — error **+309.3** (budget 271.8, extension 581.1, 2.14×). This is a
  large **under**-estimate immediately after 11-18's **−283.9**, the largest
  over-estimate in the window. The sign is still unstable; **no rescale factor
  is proposable**, and today reinforces that rather than weakening it.
- **H2** — a clean instance, **for the fade**: `LOW_FUEL`, positive gamma,
  price at the top of the pre-scan range, and fading the extreme won by more
  than an ADR. It is also the instance where the engine's **direction call
  contradicted its own fade instruction**, so it must be read with the §3
  caveat above, not as a vindication of the score.
- **H6** — hit rate **0.75** on 16 rows, the highest in weeks, and it measures
  almost nothing: on a day that fell 1148 points, every row below the scan
  price was guaranteed a touch (9 of 9) and the only rows that could fail were
  the four furthest above (134–734pts up), which did. The density artefact
  again; the 5-minute-bar clustering is milder than 11-18 (two pairs share a
  bar: 186 and 208).
- **H8** — post-closure instance: the straddle band missed, close **581.0
  below** the lower bound. H8 stays **CLOSED**, not reopened.
- **D31** — supporting, **2.214×** (realised 1277.5 vs VXN-implied 577.0),
  above the 1.54 median and √(8/π) = 1.596. The gated instruction
  (*"options market prices a quieter day, **use the smaller budget**"*) was
  wrong by a factor of 2.2 on a day the smaller budget would have capped the
  best trade available.
- **D23** — offset **−11.8**, basis `nq_implied`, clean. **D6 breach census
  stays SEVEN.**
- **D27** — 401 on `/v2/NDX/classic/gex_full`, **21st consecutive trading-day
  scan** (10-22 → 11-19, derived from disk), and it degraded cleanly every one
  of them. That is the contrast D33 rests on.
- **D7 / D15** — **4 rows carry `stretch: true`** in `prediction.levels`
  (28388.2, 27356.6, 27343.4, 27244.5) and the board printed *(stretch)* on
  **3**: the **structural row is the unmarked one again**, as on every prior
  instance. Condition only, no tape harm.
- **H10** — did **not** fire (price was inside the prior-week range, structure
  +0). Worth one line forward: the close **26510.0 is 130.2 below the
  prior-week low 26640.2**, so the −3 displacement branch is armed for the next
  session, and it still has **no reclaim condition**.
- **P-C / D32** — zero `events` rows for a **12th consecutive** scan while
  `events_24h` carried two Medium rows 42 minutes out. Unchanged by today;
  D32's third ask (route the host through a client it serves) is where this
  resolves.
- **H17** — not an instance. At **89.9% of range** this is the far end of the
  distribution and is recorded as the control: the deadband proposal must not
  touch days like this one.
- **P-H** — no deciding instance; both bases agree WRONG.
- **H26** — no instance (`|score| = 5`, below the ≥10 bucket).

---

## 4. Change proposals — only material ones

### D33 (NEW, OPENED) — `gex_levels.build()` is unguarded, so one CBOE error destroys the whole scan

**Mechanism, code-certain.** `brief.py:19–24`:

```python
lv = levels_fuel.run()
if "error" in lv:
    return {"error": "cTrader unavailable", "detail": lv}
mc = macro_probe.run()
gx = gex_levels.build(lv["price"])      # :24 — no guard
```

cTrader is guarded by an error dict (`:20–21`). GEXBot is guarded by
`try/except` under a comment that states the doctrine — *"A paid feed must never
be able to cost us a scan"* (`:47–50`). The chart is guarded (`:1163–1174`,
*"a failed picture still cannot cost us the brief"*). `macro_probe._json`
degrades to `{"_error": …}` throughout. **`gex_levels.build()` is the only
unguarded call in `gather()`, and it is the most load-bearing source in the
project.** `cboe_gex._get` retries only `(429, 500, 502, 503, 504)` (`:32`) and
re-raises everything else by design, so a 403 is fatal on the first attempt.

**The instance.** 2026-11-20, verified here rather than taken on trust:
`cdn.cboe.com` now **307-redirects** to `cdn-api.cboe.com`, urllib follows the
redirect, and the target answers **403 with a 4544-byte Cloudflare interstitial**
(`server: cloudflare`, `cf-ray: a5d795d52d1337b9-ORD`, `__cf_bm` cookie,
`<title>Attention Required! | Cloudflare</title>`). **All four paths the scan
uses** — `quotes/_NDX.json`, `options/_NDX.json`, `quotes/QQQ.json`,
`options/QQQ.json` — return 307 → 403 at 4544 bytes.

**It is upstream, not a client issue, and this is the difference from D32.**
Plain `curl` (HTTP/2, default UA) and plain `urllib` both get 403 on the same
URL in the same minute. **Honest limit on that claim:** the permission layer
refused the header/UA-variant probe, so *"no client swap fixes it"* is verified
for those two clients only; the runner's broader client sweep is relayed, not
reproduced. Yesterday's Nasdaq 403 was `curl 200 / urllib 403` — a client
problem with recoverable data. **Today's is the opposite and the two must not be
conflated in either direction.**

**Blast radius, from the code.** `cdn.cboe.com` is referenced at
`cboe_gex.py:24–25` (chains + quotes → flip, walls, max pain, the whole level
board, `COHERENT_*`, the strategy pick), `macro_probe.py:78` (`cboe_quote`,
called at `:196` and `:206–208` for `_VIX`, `_VIX9D`, `_VVIX`, `_NDX`, `QQQ` →
the entire `vol` block and the NDX cash reference) and `source_health.py:23`,
`:28–30`, `:32`, `:34–35`. The `macro_probe` half degrades; the `gex_levels`
half kills the process. On 11-19's own component table that fatal half carries
`gamma +4`, and the **fuel, rates, structure, news, events and the §4
day-frame liquidity rows — including the 27757.0 row that was the best call of
the day — need no CBOE data at all** and were lost with it.

**Second limb: the failure left no trace.** No journal directory, no
`index.json` entry, no commit, clean working tree. The only record that a scan
was attempted on 11-20 is an ephemeral terminal traceback. This is the inverse
of D10/D11 (*the run looked like it worked*): **the run did not look like
anything.** A missing day is indistinguishable from a day nobody ran, which is
exactly the kind of silence this register exists to prevent.

**PROPOSED** (two changes, neither touching scoring logic):
1. Guard `gex_levels.build()` the way GEXBot and the chart are already guarded:
   on failure, carry an error marker, suppress §2's gamma read, §4's gamma rows
   and the secondary table, print one degraded-source line naming the status and
   host, and **deliver the brief** with fuel, levels, macro, rates, structure,
   news and the day-frame liquidity board intact. The bias score must drop the
   gamma rows rather than score them as 0 — a missing block is not a neutral
   block (D14/D15's rule).
2. Write a failure breadcrumb when a scan aborts — a `SCAN-FAILED` record
   carrying the timestamp, the exception and the host. **It must not be a
   `prediction` block and must never enter a statistic**, for the same reason
   `is_trading_day: false` scans do not: a fabricated or inferred entry corrupts
   every future analysis.

**Also needed, and it is not new:** the host constant moves to
`cdn-api.cboe.com` and **`source_health.py` still is not in the scan path** —
D32 already owns that second point and today is its second instance, so it
accrues there and takes no number.

**Expected effect.** No score, level, budget or gate change on any day CBOE is
up. On a CBOE outage the brief is delivered degraded instead of not at all, and
the day is on the record either way. **Scope note:** this is a defect with a
code-certain mechanism and one demonstrated total-loss instance, not a
calibration change — the 3-session rule governs tuning, and nothing here is
tuned.

### H23 — existing proposal, re-raised on the largest magnitude in its series

**No new entry.** H23's threshold was met on 10-02 and the proposal (*"drop the
assertion or print the measured base rate beside it"*) has not shipped. Today
both named brakes were reachable and **both were sliced**, the downside one by
**1059.7 = 1.094× ADR**, against a series maximum of **0.69×** and four recent
increments of 0.18×–0.358×. *"Expect a stall at 27538.2 — take partials into it
rather than assuming a clean breakdown"* preceded a 1059.7-point breakdown
through that exact price. **Expected effect:** removes a specific, false,
actionable instruction; no score or level change.

### P5 — existing proposal, re-raised on its first clean 4-of-4 failure

**No new entry.** The secondary table published four in-range *"acts as
**support**"* strikes (27488.2 · 27388.2 · 27188.2 · 26988.2) and the day went
through all four, the deepest by **509.7** points. None is in
`prediction.levels`, so none was graded. Instance **4** of P5's founding shape
and the strongest so far: a whole table of behavioural claims, falsified in one
session, invisible to every statistic the project keeps. P5 adds observations
rather than spending them; its sequencing caveat (land with/after P3, before H6
is read at threshold) is unchanged.

### Nothing proposed, and the observation is the output

Appended to `HYPOTHESES.md`, no proposal attached:

- **The stale-`macro` re-partition reaches its first demonstrable harm case**
  (counterfactual: **+5 → +1 → NO CALL** by `journal.py:68`), but one harm case
  is one harm case. Condition **n=5**, harm **n=1**. **Nothing proposed.** What
  is being watched: how often `gamma + vol` cancels to zero or near-zero while
  a ±3 FRED row older than one session carries the margin, and whether the
  no-call counterfactual is right more often than the published call.
- **The gamma-pinning vs vol-expansion test** is feedable at **n=3** in its
  registered configuration and the answer is **2–1 to vol** — split, so
  **nothing proposed**.
- **H1** takes **+309.3** immediately after **−283.9**. **No rescale.**
- **The level-board void** reaches instance **6** with its largest harm case
  (766.0 points, 66.7% of the post-scan move, below the lowest published row).
  **No spacing rule proposed on two harm cases** — the next question is whether
  the hole is a *selection* failure (rows exist and were filtered out by the
  range-budget/reach window) or a *generation* failure (nothing to publish down
  there), and that is answerable from `gex_levels` without new data.

### No new data point is warranted

The one candidate today is a **fallback index/options source** for when CBOE is
blocked. It is declined as a proposal: D33 restores the *brief*, which is the
actual loss, and adding a second vendor is a larger change than the evidence
(one outage, one day) supports. Re-examine if the 403 persists past three
trading days — at that point the question changes from robustness to data
availability, and the right answer may be a paid or authenticated CBOE path
rather than a scrape.
