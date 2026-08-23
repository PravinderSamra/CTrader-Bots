# 04 — Which entry model today

```
above gamma flip AND net GEX positive AND VIX9D/VIX < 0.95
    -> STRATEGY 1 (sweep -> failed re-break -> CISD reversal)
       dealers actively fade extensions, so sweeps genuinely fail
       best levels: call wall, put wall, PDH/PDL, session extremes
       targets: nearest opposing pool / PD mid — keep them tight

below gamma flip AND net GEX negative
    -> STRATEGY 2 (CISD -> HH/HL -> fib OTE continuation)
       dealers amplify; sweeps run, retraces are shallow and hold
       entry: OTE 0.62-0.79 of the impulse leg after the first CISD
       targets: next unmitigated pool with trend, trail on structure
       WARNING: Strategy-1 fades have a materially lower hit rate here

straddling the flip (within ~0.15%)
    -> reduce size and let the regime resolve. The flip is the decision line
```

## Level confluence — which level to actually take

| Factor | Score |
|---|---|
| Confirmed pool (≥2 touches / equal highs-lows) | +2 |
| Day-frame level (PDH/PDL/PWH/PWL) | +2 |
| Session extreme (Asia/London/NY H-L) | +2 |
| Within 15pts of a gamma level | +3 |
| Inside the remaining fuel budget | +1 |
| Aligned with the day's bias | +2 |
| `(stretch)` — beyond budget | −2 (partials only, never the plan) |

**≥7 = A-setup. 4–6 = B. Below 4, wait.**

The strongest configuration: a confirmed day-frame or session pool sitting
within ~15pts of the call or put wall, in the bias direction, inside budget.
Retail stops and dealer hedging pushing the same way. Lead with those.

## Situational levels worth adding
- **Post-data range H/L** — the 30 minutes after a Tier-0 print. Among the most
  reliably swept levels on the chart, and they only exist on data days.
- **NY-open range (first 30 min) H/L** — sweeps of it during the midday lull are
  high quality, because volume is thin and dealers pin.
- **Overnight gap edge** — unfilled gaps are magnets; the edge is where the
  sweep happens.
- **Round numbers at 250/500 intervals** — these carry real option and stop
  interest on NAS100.
- **The session after OPEX** (Monday after the 3rd Friday) — gamma rolls off,
  one of the most reliable expansion days in the calendar.
