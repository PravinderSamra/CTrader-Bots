# REVIEW — 2026-09-16 (FOMC, rate HIKE 3.75% -> 4.00%)

Graded 2026-09-17 from `review_day.py 2026-09-16 --json`. 1 scan, 0 test artefacts.
History context from `track.py`: 12 trading days, 21 deduped scans.

---

## 1. Scoreboard

| | |
|---|---|
| Session O / H / L / C | 28970.0 / 29251.3 / **28757.3** / 28971.0 |
| Range / net | **494.0** / **+1.0** (net = 0.2% of range) |
| ADR14 | 357.6 -> range was **1.38x ADR** |
| Bars | 276 |

**Direction** — 0 right / 1 wrong / 0 no-call.
Scan 12:46Z PRE_NY, bias **+4 MILDLY BULLISH**, expected direction **+1**.
Post-scan move **-129.5** (26.2% of range) -> **WRONG**.
Running record: 9 right / 7 wrong / 5 no-call.

**Levels** — 19 published, **18 touched, hit rate 0.95** (12-day mean 0.54).
Of the 18 touched, **2 held** (11%): 29190.2 max pain, 28930.6 Asia low.
16 were lost.

**Fuel** — budget 145.6, actual extension **282.0**, error **+136.4**, ratio **1.94x**.
Traversal 494.0 = **3.39x** budget. This is the **largest fuel error in the
12-day record**; the next largest is +79.4 (09-14). 12-day per-day mean is +2.1.

---

## 2. What the levels actually did

**Everything on the board flipped side between 18:05 and 18:45 UTC.** That is the
FOMC statement (18:00) and the press conference (18:30). Of the 16 levels that
were lost, every `settled_from` timestamp falls in that 40-minute window. This was
not 19 independent level tests; it was one event that invalidated the whole board
at once, and the 0.95 hit rate should be read that way.

| Level | Brief said | Actually did |
|---|---|---|
| **29290.2 CALL WALL** 3.19bn | "rallies stall... take profit into it... strongest ceiling on the board" | **Never reached.** High 29251.3 stopped 39.0pts (0.13%) short. Untested — 0.13% is inside noise and this is evidence neither way. |
| **29190.2 MAX PAIN + PDH** | "price drifts toward it... **weak on a Monday, strong by Thursday/Friday**" | **Held as resistance, 170min, worst excursion 22.6pts.** The single best level on the board — on a **Wednesday**. The day-of-week qualifier said this should have been a middling level and it was the day's ceiling. |
| **29040.9 GAMMA FLIP** | "We're ABOVE it: they're damping, so fades work. Lose this and hold below and that reverses — stop fading." | **Lost**, settled below from 18:05, worst 59.5pts. The conditional rule fired correctly, but only *at* the FOMC. Anyone following the headline advice ("this is your fade day") for the five hours before 18:00 was fading into the event. |
| **28990.2 PUT WALL** 2.29bn | "Heaviest floor this week — **expect a bounce and a good long-sweep here**... strongest floor on the board" | **Sliced.** `acted_as: lost`, settled **below** from 18:50. Price traded **232.9pts below it** to the day's low. This is the headline failure. |
| **28930.6 Asia Low (today)** | (unranked liquidity) | **Held as support, 70min, worst -9.2pts.** The second-best level of the day was a plain session low, not a gamma level. |
| 29184.2 / 29147.2 / 29142.6 / 29134.8 (equal highs, NY/London highs) | day-frame liquidity | All four lost, worst 28.6-50.3pts. A 13pt-wide cluster of four separately-published levels that behaved as one. |
| 29049.6 PD mid, 29035.1, 29029.7, 29018.3 PWL, 29005.8 | day-frame liquidity | All lost, worst 50.8-94.6pts. |
| 28983.4 PD close / 28925.8 / 28909.8 PDL | day-frame liquidity | All lost. |

**Internal contradiction in the brief itself.** Line 106 said: *"DOWNSIDE path:
clear. Every options shelf from here to 28790.2 is negative gamma — nothing
structural to slow a breakdown. If it goes, it has room. **Do not fade it.**"*
That call was **right** — price went to 28757.3. Fifteen lines later the level
table gave 28990.2 the strongest possible floor language ("expect a bounce and a
good long-sweep here"). The brief held the correct and the incorrect read
simultaneously, and gave the incorrect one the more emphatic wording and the
board position. Nothing in the generator reconciles the shelf-path narrative with
the wall-table narrative.

---

## 3. What was wrong, and why

`inputs.bias_components`, total +4:

| pts | component | verdict |
|---|---|---|
| **+2** | `gamma` — "above flip 29040.9 by 36.6pts — long-gamma, dips supported" | **Wrong by 18:05.** Held for 5h15m, then lost. The rule has no event condition. |
| **+1** | `gamma` — "straddling the flip (<0.15%) — regime unstable, **reduce conviction**" | **Sign defect — see P-A.** A row whose text says *reduce conviction* added +1 to an already-bullish score, making it more bullish. |
| **+2** | `gamma` — "week net GEX 3.111 -> **pinning likely**" | **Wrong.** The day ran 1.38x ADR, the largest traversal in the record. This row produced the "tight, pinned range / breakouts mostly fail" headline. |
| **-2** | `vol` — "VIX9D/VIX 1.001 BACKWARDATED — **expect range expansion**" | **Right about expansion**, and it was the only row that said so — outvoted +4 to -2 by the two gamma pinning rows. Nothing arbitrates between them. |
| **+2** | `macro` HY OAS, **+1** `rates` 10y | Not falsified intraday. |
| **-1** | `breadth` NDX vs ES, **-1** `structure` pools below | Directionally right, small. |
| **0** | `news` | 1 auto-scored headline, **49 unscored**. The one scored headline was *"Gaming the Fed Odds for a Rate Hike Wednesday"* — scored `[hawkish]`, **worth 0 points**. |

### The root cause: the event gate is unreachable

`bias_engine.py:254`:

```python
soon = [e for e in (cal.get("upcoming_next_24h") or []) if 0 <= e["hours_away"] <= 1.5]
hi   = [e for e in soon if e["impact"] == "High"]
```

At 12:46Z the calendar held **four High-impact FOMC entries at 5.2-5.7h away**,
including a Federal Funds Rate print with forecast 4.00% vs previous 3.75% — a
**hike**. `hours_away` 5.2 > 1.5, so `event_gate` was `None`, and the brief's
headline advice was *"This is your fade day"*, *"Expect a tight, pinned range"*,
*"Keep targets modest; breakouts mostly fail"*.

This is not a one-day miss. **The gate has fired 0 times in 12 trading days and
21 deduped scans.** It is structurally unreachable at the scan cadence actually
in use: PRE_NY scans run 12:40-13:25Z, US high-impact prints land at 12:30Z
(already past) or 18:00Z (4.6-5.2h out). A 1.5h window catches neither. The other
near-miss in the record is 2026-09-10 08:12Z LONDON with PPI **4.3h** away.

Compounding it, the `events` component has contributed **0 points on 14 of 14
rows across the whole journal** (it is hard-coded `add("events", 0, ...)`, earnings
only). So events cannot move the score *and* the gate never fires: **an FOMC
rate-decision day and a quiet Tuesday are indistinguishable to this model.**

### Why "WRONG" is the fair grade here despite a flat close

Session net was **+1.0** — the flattest day in the record (every other day is
0.24-0.69 of range). A close-to-close grade would score the +1 call CORRECT on a
1-point move. The scan-relative grade (-129.5, 26.2% of range) is the honest one.
Recorded, not proposed — n=1.

---

## 4. Change proposals

Three proposals, all with >=3 sessions of evidence. Two are code defects rather
than calibration, which is the safer kind. `track.py` prints `actionable: YES`
(12 days), with its own caveat that day count alone is not evidence — so each
claim below carries its own session count.

### P-A — the straddle rider adds +1 on both branches (3 days)

`bias_engine.py:86-89`:

```python
if abs(dist_pct) < 0.15:
    add("gamma", +1 if px > gf else +1,
        "but price is straddling the flip (<0.15%) — regime unstable, "
        "reduce conviction")
```

Both ternary branches are `+1`. A ternary written with identical arms is not a
deliberate choice; it is an unfinished edit. **A row that says "reduce conviction"
must move the score toward zero on both sides.** As written it moves *away* from
zero whenever the rest of the score is bullish.

**Evidence — 3 trading days, 4 scans, every instance price-above-flip:**

| day | scan | this row | total | label |
|---|---|---|---|---|
| 2026-09-09 | 15:17, 15:20 | +1 | 0 | NEUTRAL |
| 2026-09-11 | 12:47 | +1 | -7 | BEARISH (here +1 *did* reduce conviction, by luck of sign) |
| 2026-09-16 | 12:46 | +1 | **+4** | **MILDLY BULLISH** (here +1 *increased* it) |

**Honest caveat: no label has flipped yet.** 09-16 would be +3, still MILDLY
BULLISH — but +3 is exactly the label boundary, so the next instance plausibly
does flip one. The row's effect currently depends on the sign of everything else
in the table, which is the definition of an unintended interaction.

**Proposed:** make the rider signed toward zero (`-1 if px > gf else +1`), or
better, dampen the flip vote itself rather than adding a counter-row.
**Expected effect:** small — roughly 1 point on ~25% of scans — but it removes a
row that currently contradicts its own stated purpose.

### P-B — the held/lost verdict is not stable to a 5pt shift in the level (3-5 days)

`review_day.py:58` `SETTLE_TOL = 25.0`, against `TOUCH_TOL = 8.0`. Levels
published closer together than the touch tolerance are getting opposite verdicts.

**Two instances on 2026-09-16 alone:**
- 29190.2 worst **22.6** -> `held` vs 29184.2 worst **28.6** -> `lost`. Same
  `settled_from` (18:05), same side, 6.0pts apart. The 25pt line falls between them.
- 28930.6 worst **-9.2** -> `held` vs 28925.8 worst **-47.1** -> `lost`. 4.8pts
  apart, but `settled_from` differs by one bar (19:45 vs 19:40) and the excursion
  measured from that one earlier bar differs by **37.9pts**.

**Evidence across history — 11 such pairs on 5 of 12 trading days:**
- boundary type (identical settle start, verdict split by the 25pt line):
  **08-26, 08-28, 09-16** — 3 days.
- settle-start type (one-bar difference in detected settle, large excursion swing):
  **08-24, 08-26, 08-27, 09-16** — 4 days.

**Scale of the contamination: of 101 unique day-level settled verdicts, 30 (30%)
have a worst excursion within 8pts of the 25pt line** — they would flip on a
tolerance change smaller than one touch tolerance. Every `held`-based statistic in
`HYPOTHESES.md`, including the 17/17 wall claim, inherits this.

**Proposed:** (a) report `worst_excursion` alongside `held` everywhere a held-rate
is quoted, so a reader can see how many verdicts are near the line; (b) cluster
levels within `TOUCH_TOL` into one graded object before assigning a verdict, so a
13pt-wide cluster of four "levels" counts once rather than four times;
(c) make `settled_from` detection deterministic instead of first-bar-wins.
**Expected effect:** the level hit rate and held rate both drop and become
meaningful. Today's 19-published/18-touched becomes roughly 11 distinct objects.
**No scoring change — this is measurement only.**

### P-C — widen the event gate, or gate on session containment (12 days, 0 fires)

**Evidence: `event_gate` has fired 0 times in 12 trading days / 21 deduped scans,
including an FOMC rate-hike decision 5.2h out and a PPI print 4.3h out.** A
component that has never once fired across the entire record is dead weight by
the standing criterion, and here the dead component is the only thing in the
system that knows what a scheduled event is.

**Proposed:** replace `0 <= hours_away <= 1.5` with *"does a High-impact event
fall inside the session this brief is forecasting"*. The scan already has the
event list and its own session window; no new data source is needed. Keep the
existing 1.5h wording as the *imminent* tier and add an *ahead-of-event* tier
("a High-impact print lands at HH:MM, N.Nh from now — the levels below are valid
only until then").

**What it would have changed on 2026-09-16, specifically:** the brief would have
carried an FOMC banner, and the flip rule *"lose this and stop fading"* would have
been framed as an expected 18:00 event rather than a background caveat, instead of
leading with "this is your fade day" five hours before a rate hike.

**Deliberately NOT proposed:** any change to the *score* on event days. The
outcome evidence — that event days blow the fuel budget — is **n=2**
(09-10 +114.6 per-scan, 09-16 +136.4 per-day; the two largest positive errors in
the record). That is below threshold and is logged as an observation only. P-C
changes prose and gating, not points.

### Considered and rejected

- **Bolt VIX9D/VIX term structure onto the fuel budget.** Tempting after today —
  the backwardation row was the only one that called expansion. **Across 12 days
  the correlation between VIX9D/VIX and the fuel error is r = 0.053 — none.** The
  three highest-term days are +44.3, **-81.3**, +136.4. Opposite signs. Rejected.
- **Stop publishing structural walls** (touched 5/18, 28%, the lowest of any
  kind). A far outer boundary is *meant* to be rarely touched; low touch rate is
  not evidence of noise here. Recorded, not proposed.
- **Anything from the call wall not being reached.** 39pts / 0.13% short is inside
  noise. One day, and not even a clean one.
- **H17 (sub-5% graded direction calls)** — still **1 of 3**. 09-16's move was
  26.2% of range and does not add to it.

---

*Observations below threshold appended to `journal/HYPOTHESES.md` under
"Observations appended 2026-09-17".*
