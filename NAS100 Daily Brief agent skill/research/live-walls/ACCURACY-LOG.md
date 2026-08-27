# Intraday OI estimation — accuracy log

Appended at each end-of-day review. Never rewritten: a prediction that was
wrong stays on the record, exactly as `HYPOTHESES.md` keeps withdrawn claims.

**Grading rule.** A snapshot from day D is graded on **D+1 only**, against the
open interest the OCC publishes that morning. `oi_accuracy.py` enforces this and
refuses to grade anything older or newer.

**Targets:** within hard bounds 100% · net error < 25% of the day's positioning
move (then < 15%) · wall location matching next-day published.

---

## 2026-08-26 — first snapshot taken, nothing gradeable yet

Baseline recorded at 21:37 UTC, running on **prior** k (no fitted calibration
exists yet).

| | |
|---|---|
| Contracts near the money | 2,945 |
| Prior open interest | 56,919 |
| Today's volume | 84,667 |
| **Estimated net ΔOI** | **+8,559** |
| Hard bounds | −10,458 .. +84,667 |
| Net GEX, published → estimated | +2.25bn → **+4.01bn** |
| Call wall, published → estimated | 29,250 → 29,250 (**unchanged**) |
| Put wall, published → estimated | 29,200 → 29,200 (**unchanged**) |

**First read, on one snapshot and worth nothing yet:** the estimate moved the
*magnitude* substantially (+78% on net GEX) but did not move either *wall*.
If that pattern holds it is the central finding of this research — it would
mean live OI changes how hard dealers are hedging, not where. Watch it.

Graded tomorrow.

---

## Operational note — CBOE rate limits (2026-08-26)

Building the chart earned an **HTTP 429** from CBOE. Cause was not the request
rate as such: `gex_chart.py` called `build()` (which loads the chain) and then
loaded the chain *again* for the raw per-strike rows — four round trips for one
picture.

`gex_levels.load_combined()` now memoises on a 90-second TTL. The chain does not
change inside a single scan, so one fetch serves the whole run.

Worth carrying forward as this research adds more chain consumers: **every new
tool that reads the chain is another fetch unless it goes through the cache.**
`intraday_oi.py` deliberately uses its own raw `_get` because it needs the full
book including zero-OI strikes that `load_chain` filters out — that is one extra
fetch per snapshot, once a day, which is acceptable.

---

## 2026-08-27 — first graded result

The 26 Aug snapshot, graded against the open interest the OCC published this
morning. Running on **prior** k (no fitted calibration existed).

| | |
|---|---|
| Contracts matched | 2,533 |
| Volume | 17,475 |
| **Estimated ΔOI** | **+7,217** |
| **Actual ΔOI** | **+9,927** |
| Net error | −2,710 — **−24.2% of the day's positioning move** |
| Mean absolute error | 2.8 contracts |
| **Within hard bounds** | **98.9%** ⚠️ |
| Implied k overall | **0.568** |

**−24.2% on the first attempt with untuned priors is inside the 25% target** and
within reach of the 15% the published models claim. Better than expected this
early.

The priors were systematically too low, consistent with an implied k of 0.568:

```
1-5d/atm    0.35 -> 0.50  (raw 0.60, n=265)
1-5d/far    0.45 -> 0.60  (raw 0.65, n=246)
6-20d/atm   0.40 -> 0.25  (raw 0.23, n=216)
6-20d/near  0.45 -> 0.60  (raw 0.71, n=383)
6-20d/far   0.50 -> 0.65  (raw 0.80, n=319)
21d+/near   0.50 -> 0.65  (raw 0.87, n=249)
```

All six moves were damped by `MAX_STEP` — every raw fit was further from the
prior than the step allows, which is itself a signal that the priors were badly
placed rather than slightly off.

### ⚠️ OPEN DEFECT: within-hard-bounds is 98.9%, not 100%

`METHOD.md` §5 states this figure must be **100%** — the bounds
`[max(−V, −OI), +V]` are arithmetic, not modelled, and a correct dataset cannot
violate them. **1.1% of contracts did.** That means an input is not what it is
assumed to be.

Candidates, none yet tested:

1. **`volume` is not consolidated.** If CBOE reports only its own venue's
   volume, actual ΔOI can exceed the V we see. NDX index options are
   CBOE-listed, which argues against it, but it has not been checked.
2. **The snapshot preceded final volume.** Taken 21:37Z; if the field is still
   settling after the 20:00 close, V is understated.
3. **Contracts re-listed or adjusted** between the two fetches, so `oi_prev` and
   the graded OI are not the same series.

**Every accuracy number above rests on these bounds being sound, so this is the
next thing to fix — before any more calibration is fitted.** A model tuned on a
dataset with an unexplained 1.1% impossibility is a model tuned on noise.

### Second observation taken

27 Aug snapshot written at 21:21Z: 2,883 contracts, prior OI 58,515, volume
90,147, estimated net ΔOI **+8,689** (bounds −13,321 .. +90,147). Net GEX
published +7.34bn → estimated +10.53bn. **Both walls unchanged** at 29,650 and
28,650 — the second consecutive day where the estimate moves the magnitude but
not the levels. That pattern is now worth watching directly.
