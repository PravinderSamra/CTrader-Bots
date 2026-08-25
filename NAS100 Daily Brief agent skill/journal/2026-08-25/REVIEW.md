# NAS100 — end-of-day review, Tuesday 25 August 2026

**Session:** O 29,072.9 · H 29,342.6 · L 28,945.5 · C 29,212.9
**Range 397.1pts** (ADR14 408.7 — a 97% day) · **net +140.0**

---

## 1. The headline: the fuel model called the top almost exactly

The 13:04 pre-NY scan published **12pts of range budget left**.

What happened: price ran into the NY open, made a new high at **29,342.6 — 0.4
points above the London high** — and reversed. The day's range extended by
**0.4pts against a 12pt forecast.**

Then it fell 256pts to 29,086.1 and closed mid-range.

This is the second consecutive session where the budget was near-exact at the
exhausted point (24 Aug: 0.0 forecast, 5.3 actual). It is also the cleanest
demonstration yet of the reframing we made last week:

> **The budget forecasts range EXTENSION, not price travel.**

The range grew 0.4pts. Price travelled 256.5pts inside it. Both numbers are
correct simultaneously, and only the first one was ever being forecast. Anyone
reading "12pts left" as "12pts of movement left" would have stood aside through
a 256pt move.

**H1 is now 2-for-2 at the exhausted point.** One more clean session and it
becomes actionable.

---

## 2. Live calls — how they graded

### ✅ Pre-open: "don't buy 29,249.6" — correct

You asked at ~13:15, 15 minutes before the open, whether to go long at 29,249.6.
I advised against: no sweep trigger for Strategy 1, mid-range in a pinning
regime, 42pts to first friction against 12pts of budget, pre-open volume at 76
vs ~1,000.

**Outcome: close 29,212.9 — 37pts below the proposed entry.**

Honest caveat: the path went *up* first, to 29,342.6, so a long there was +93
before it was wrong. If you had taken partials into the 29,270 shelf you would
have banked something. The reasoning held (mid-range chop, closed below), but
this was not a clean win — it was right on outcome via a route that would have
tested your patience.

### ⚠️ The 29,270 "upside stalls here" call — wrong

The board said upside stalls at 29,270.3. Price sliced through it by 72pts to
29,342.6. That shelf did not hold.

What *did* hold was the level 72pts higher — the prior day's high. The stall
call was directionally right (there was a top) but the *level* was wrong, and it
was wrong in the dangerous direction: it would have had you taking partials 72pts
early.

### ✅ The 29,183 call-wall question — thesis correct, stop number premature

You asked whether a sweep and close back above the 29,183 call wall was a valid
setup. I said: right structure, wrong trigger — 29,183 is a strike, not a stop
pool, so use it as the **reclaim confirmation** and take the **sweep** at the
29,135–29,141 confluence (London low / PD mid / 2-touch pool).

**Outcome — that is close to exactly what happened:**

| | |
|---|---|
| Sweep of the 29,135–29,141 zone | ✅ ran to **29,086.1** at 14:xx |
| Reclaim back above 29,183.5 | ✅ by 15:00, held into the close |
| Grind higher after the reclaim | ✅ closed **29,212.9** (+29 from the reclaim) |
| Max pain 29,223.5 as a magnet | ✅ **closed 10.6pts away** |
| 29,183 as an afternoon pivot | ✅ 16:00 low 29,181.2 · 18:00 close 29,183.6 |

**The one thing I got wrong: the stop.** I quoted "~29,128, below the sweep
wick". The actual wick was **29,086.1** — 42pts lower. A stop at 29,128 would
have been taken out *on the sweep itself*, immediately before the setup
triggered.

The *rule* was right ("below the sweep wick"). Quoting a **number** for it before
the sweep had happened was not — wick depth is unknowable in advance. Lesson
logged: give the rule, not a pre-computed level, for any stop that depends on a
move that has not occurred yet.

### ❌ Overnight 21:56: STRONGLY BEARISH (−15) — wrong

Day closed +140 above the scan price. Price *did* fall 127pts to 28,945.5 first
(2.5 hours later), then reversed for the rest of the session.

Same shape as 24 Aug's −12: **right for the next few hours, wrong for the day.**
Two instances now. See §3.

---

## 3. Two defects found — one fixed tonight, one logged

### D1 — Fuel was reading the *previous* day's range across the rollover · **FIXED**

The 21:56 scan reported:

> range 530.9 · **117.7% of ADR used** · `EXHAUSTED` · **0.0pts budget**

…**56 minutes into a trading day that went on to build a 397pt range.**

Cause: the feed goes quiet across the 21:00 UTC daily roll, so the scan found
zero bars for the new trading day. The code silently fell back to the last
completed *daily* bar — Monday's finished 530.9pt range — and presented it as
today's. Every scan in that window would have told you the day was over before
it started, and told you to fade extremes that did not exist yet.

**Fixed.** New `SESSION_PENDING` state. Verified live at 21:39 tonight:

```
Fuel: ADR14 408.7 · 0.0% used · 409pts budget left → SESSION_PENDING

The new trading day has not opened yet — the feed is quiet across the
21:00 UTC rollover, so there is no range to measure and no fuel read.
This is unknown, not exhausted.
```

This is a **bug, not a calibration question**, so it is not subject to the
3-session rule. A range that does not exist yet is unknowable, not exhausted.

`track.py` now quarantines pre-fix scans carrying the signature. That matters:
the corrupt scan alone was dragging H1's mean error from **46.6 → 100.7pts**,
i.e. it was about to invent a systematic model bias out of a bug. Same failure
class as W1/W2, caught this time before it reached a conclusion.

**It did not cause the wrong direction call** — fuel reports and never votes.

### D2 / H7 — The gamma flip moved 295pts overnight · **LOGGED, not fixed**

The overnight scan's largest bearish component was gamma −3: *"below flip
29,271.0 by 219.8pts — SHORT gamma, dealers amplify."*

By 13:04 the flip was **28,976.3**. Price was above it. Long gamma.

**The regime label inverted overnight — and it inverted because the flip moved
295 points, not because price moved.** The recommended strategy inverted with it
(Strategy 2 → Strategy 1).

Logged as **H7**. Not fixed, because one observation is one observation and the
flip maths itself is sound. If the drift proves consistent, the fix is to widen
the confidence band on overnight regime calls or suppress the gamma component
before the cash open — not to touch the calculation.

---

## 4. Built tonight: secondary walls

Your question — *"what are the other major put and call walls in this range"* —
exposed a real gap. The board publishes exactly **one** call wall and **one** put
wall, computed as `max(above, key=call_gex)` and `max(below, key=put_gex)`.

That structure makes one case invisible: **call gamma sitting below spot.** It
is not the call wall (that search only looks above spot) and it is not the put
wall (that search only reads put gamma). It cannot appear at all.

On Monday that invisible level was **1.29bn across 43,299 contracts at
29,171.9** — the single heaviest gamma concentration anywhere near price, and
the level price pivoted on for the entire afternoon. You would never have seen
it.

The board now carries a secondary-walls block:

| NAS100 | dist | force | contracts | what it does |
|---|---|---|---|---|
| **29122.5** | -91 | 0.50bn | 8,684 | in-the-money call gamma — dealers BUY dips into it, so it acts as **support**, not resistance |
| **28922.5** | -291 | 0.43bn | 11,493 | put gamma below — a genuine floor while we stay in long gamma |
| **29072.5** | -141 | 0.39bn | 14,235 | in-the-money call gamma — dealers BUY dips into it, so it acts as **support**, not resistance |
| **29372.5** | +159 | 0.26bn | 6,402 | call gamma overhead — dealers SELL into it, so rallies stall here |

Each strike is ranked by whichever side actually dominates it, and levels
already on the main board are de-duplicated out.

One deliberate design choice: the window is **±0.75 × ADR**, not the range
budget. The budget forecasts how far the *range* can grow; these are levels price
can still *reach inside* the range — which is precisely the distinction that
matters on an exhausted day when price is still travelling 250pts.

---

## 5. Evidence register — where we stand

```
EVIDENCE TO DATE — 2 trading day(s), 5 scans (deduped)
  actionable at 3+ days: NO — keep observing

day           time session     budget  extension  traversal    err   bias call
2026-08-24   08:28 LONDON        88.7      168.5      334.7   79.8     +1 no call
2026-08-24   09:37 LONDON        88.7      168.5      334.7   79.8     -1 no call
2026-08-24   12:40 PRE_NY        88.7      168.5      290.9   79.8     -4 CORRECT
2026-08-24   13:45 NY_OPEN        0.0        5.3      284.4    5.3    -12 WRONG
2026-08-25   13:04 PRE_NY        12.0        0.4      256.5  -11.6     +0 no call

H1 budget vs range EXTENSION: mean error 46.6 pts
H5 early (4) mean err 56.9  vs  late (1) mean err 5.3
direction: 1 right / 1 wrong / 3 no-call   levels touched 0.58

EXCLUDED (corrupt input, not a failed forecast):
  2026-08-25 21:56  fuel measured across the day rollover
```

| | Status | Days | Movement today |
|---|---|---|---|
| **H1** budget = range extension | OBSERVING | 2 / 3 | **2-for-2 at the exhausted point.** Strong. |
| **H2** fade beats continuation at low fuel | OBSERVING | 2 / 3 | Second confirmation. |
| **H3** bias over-commits at extremes | OBSERVING | 1 / 3 | No new evidence (engine was neutral). |
| **H4** flip as magnet | OBSERVING | 2 / 5 | **One hit, one clear miss** (236.6pts). Cooling. |
| **H5** budget under-reads early | OBSERVING | 2 / 3 | First over-read on record, arrived late. Consistent. |
| **H6** level board reaction quality | OBSERVING | 2 / 5 | Chop again. Both days long-gamma — split by regime. |
| **H7** overnight flip instability | **NEW** | 1 / 3 | 295pt overnight drift, regime inverted. |

**Nothing is actionable. No model behaviour changed tonight** — the only code
changes were the D1 bug fix, the quarantine, and the secondary-walls display.

---

## 6. What to watch tomorrow

1. **H1's decider.** If Wednesday's exhausted-point budget lands near-exact
   again, that is 3-for-3 and H1 becomes actionable.
2. **H7.** Compare tonight's overnight flip against tomorrow's pre-NY flip.
   Second data point on the 295pt drift.
3. **The secondary walls, live.** 29,122.5 and 29,072.5 are the in-the-money
   call-gamma supports. Watch whether dips into them get bought.
4. **The 29,135–29,141 pocket.** It has now acted as the session floor twice.
   Third touch tells you whether it is structure or coincidence.
