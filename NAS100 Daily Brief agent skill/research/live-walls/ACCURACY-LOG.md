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
