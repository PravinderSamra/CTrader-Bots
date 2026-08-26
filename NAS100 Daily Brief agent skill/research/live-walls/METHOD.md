# Estimating today's open interest from today's volume

**Status: research. Nothing here feeds the brief.** It writes to `research/`
and is graded against reality every morning. It gets promoted into the scan
only when the accuracy log earns it.

---

## 1. Why this exists

Every gamma level in the brief is built on **yesterday's** open interest. The
OCC settles OI after the close and publishes it the next morning; it does not
change again until the following morning. That is not a limitation of our free
data — it is how the options market clears, and it constrains every vendor
equally.

Measured on 2026-08-26, the gap this leaves is real:

| Bucket | Volume ÷ prior OI |
|---|---|
| 0DTE | **9.93** |
| this week (0–3 dte) | 4.65 |
| 2–10 dte | 0.36 |
| full 45-day book | 0.95 |

And the strikes people traded were not the strikes holding the OI: **the top-6
strikes by OI overlapped the top-6 by volume in only 2 of 6 cases.** One
contract, `NDXP260826C29300000`, traded **3,039 contracts against an open
interest of 35**.

So positioning genuinely does build during the session that the walls cannot
see. This is an attempt to see some of it.

## 2. The accounting, exactly

This is the part most explanations skip, and it is the part that gives us
something for free.

For a single trade of size *q*, open interest moves by:

| Both parties | ΔOI |
|---|---|
| opening | **+q** |
| closing | **−q** |
| one opens, one closes | **0** |

So for a contract with prior open interest *OI* and today's volume *V*:

> **ΔOI ∈ [ max(−V, −OI) , +V ]**

**Those bounds need no model and are never wrong.** They do real work: you
cannot close more than exists, so when *V ≫ OI* the downside is capped at −OI
and heavy volume on a thin strike is *necessarily* position building. That one
inequality explains most of what a "live wall" tells you.

The estimator is therefore always reported **inside its bounds**, and the
grader records how often the truth landed inside them. If that figure is ever
below 100%, something is wrong with the *data*, not the model.

## 3. The estimator

Inside the bounds, one shrinkage factor:

```
ΔOI_est = clamp( V × k(dte_bucket, moneyness_bucket),  bounds )
```

`k` is the **net opening rate** — the share of volume that survives as new open
interest. k = 1 means every contract opened fresh positions on both sides;
k = 0 means the day's trading netted out entirely.

Buckets: DTE `0dte / 1-5d / 6-20d / 21d+` × moneyness `atm (≤1%) / near (≤3%) /
far`.

**0DTE gets a prior of 0.02 and that is not a modelling choice, it is the
calendar.** Those contracts expire tonight; almost nothing they trade survives
into tomorrow's open interest. This is also why the commercial write-ups note
that a large intraday OI build "can collapse nearly to zero by the close" on
high-0DTE days.

### Why not machine learning, yet

The published approach uses gradient-boosted trees to classify each volume
increment as opening or closing, from contract features, volume/OI ratio, vol
regime, calendar effects and microstructure. Reported accuracy: end-of-day OI
error typically under 15% of the day's net positioning move.

We cannot start there. That model needs a labelled history we do not have —
and we cannot manufacture one, because the labels only arrive one day at a
time. So we start with a bounded shrinkage estimate, record every prediction,
and let the history accumulate. If the simple version gets close, the ML is not
worth building. If it plateaus badly, we will have exactly the dataset needed to
train something better.

**We also have a structural disadvantage worth stating.** The vendors classify
from consolidated *trade-level* prints with bid/ask context — they can infer
which side initiated. CBOE's delayed chain gives us only an aggregate daily
volume per contract. We cannot see trade direction at all. That ceiling is real
and no amount of cleverness on our side removes it.

## 4. How it gets graded

`oi_accuracy.py` compares each snapshot against the OI published the next
morning and refits `k` per bucket:

```
k_fitted = Σ actual ΔOI  ÷  Σ volume      (within the bucket)
```

Two guards, both learned from this project's own mistakes:

- **Timing is enforced, not assumed.** OI published on D+1 reflects clearing
  through D. A snapshot from day D is gradeable *only* on D+1 — grade it on D+2
  and the "actual" already contains another session, and every error is charged
  to the wrong day. The tool refuses rather than silently mis-grading. This is
  the same class of defect as D1 and D3 in `HYPOTHESES.md`: **a guard written
  against the definition, not a proxy for it.**
- **Steps are damped** (`MAX_STEP = 0.15`) and thin buckets are held
  (`MIN_SAMPLE = 200`). One day is one day. A bucket that happened to see a
  large roll should not swing the model — the same discipline as the 3-session
  rule on hypotheses.

## 5. What "good" looks like

Targets, in the order they matter:

1. **Within hard bounds: 100%.** Anything less is a data bug.
2. **Net error < 25% of the day's positioning move**, then < 15% to match the
   published benchmark.
3. **Wall location stability** — the real test. If the estimated call/put wall
   lands on the same strike the next day's published data produces, the
   estimate is useful *even if the contract counts are off*. Wall location is
   what gets traded; the dollar figure is not.

Point 3 is the one to watch. Today's first snapshot already showed net GEX
moving +2.25bn → +4.01bn on the estimate while **both walls stayed on the same
strike**. If that holds, the honest conclusion may be that intraday OI changes
the *magnitude* and not the *levels* — which would make it interesting and not
very actionable, and that is a finding worth having either way.

## 6. Known limitations

- No trade-direction data, as above. Hard ceiling.
- Binary open/close framing cannot represent spreads, rolls or exercises.
- Assumes CBOE's `volume` field is a complete consolidated figure.
- NDX only. QQQ is excluded from the estimate for now to keep one clean
  measurement problem rather than two.
- High-volatility sessions are where the published models systematically
  overshoot — they read defensive position *reduction* as opening flow. We
  should expect the same and watch for it specifically.

## 7. Files

| Path | What |
|---|---|
| `scripts/intraday_oi.py` | Snapshot + estimate |
| `scripts/oi_accuracy.py` | Next-day grading + refit (`--fit`) |
| `research/live-walls/snapshots/*.json` | Every snapshot, never rewritten |
| `research/live-walls/calibration.json` | Current fitted k per bucket |
| `research/live-walls/ACCURACY-LOG.md` | Running record, appended each grading |
