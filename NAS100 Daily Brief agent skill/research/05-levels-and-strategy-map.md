# 05 — The Level Board: what to mark, and what each level means for YOUR two setups

This is the spec for the daily "mark these on your chart" section. Every level
is emitted in **NAS100 CFD price** (cTrader/Pepperstone), tagged with its
source, its distance from price, whether it is in reach today, and a one-line
reaction brief.

---

## Your two strategies, restated as machine-checkable gates

**Strategy 1 — Sweep → failed re-break → CISD reversal**
1. Price sweeps a key liquidity level (PDH/PDL/PWH/PWL/Asia H-L/London H-L/
   unmitigated swing).
2. Drop to 1m.
3. Wait for a retrace.
4. Price **fails to re-break** the swept level → lower high (after a bullish
   sweep) or higher low (after a bearish sweep).
5. Wait for **CISD** (change in state of delivery).
6. Enter the reversal. Stop beyond the sweep extreme or the recent swing.

**Strategy 2 — Reversal → CISD → HH/HL → fib OTE continuation**
1. Signs of reversal, 1m.
2. CISD.
3. Confirm a new **HH** (bullish) with a **HL** behind it.
4. Wait for a further new HH; mark the leg low→high with the fib tool.
5. Enter on the retrace into **OTE (0.62–0.79)**.
6. Stop below the fib (beyond the 0.79 / leg low); target above the previous
   swing high. Mirrored for shorts.

**What the brief must add to each:** which one is the *right tool today*, and
which specific levels are the highest-quality triggers.

---

## Tier 1 — Core liquidity levels (always marked)

| Level | Source | Why it matters | Strategy-1 reaction to look for |
|---|---|---|---|
| **PDH** | cTrader D_1 (day rolls 21:00 UTC) | Densest retail stop cluster above | Poke above → 1m lower high → CISD → short |
| **PDL** | cTrader D_1 | Densest cluster below | Poke below → 1m higher low → CISD → long |
| **PD mid** | (PDH+PDL)/2 | Prior-day equilibrium; strong magnet on inside days | Not a sweep level — a **target**. Price gravitates here on rangebound days |
| **PD close** | cTrader D_1 | Settlement reference; gap-fill magnet | Target, not a trigger |
| **PWH / PWL** | Prior calendar week H/L | Weekly liquidity; the biggest pools | High-quality sweep levels, especially Monday–Tuesday |
| **Asia High / Asia Low** | 23:00–07:00 UTC on M_5 | London routinely sweeps one of these to start the day | The most reliable strategy-1 trigger of the London session |
| **London High / London Low** | 07:00–12:30 UTC on M_5 | NY routinely sweeps the London extreme | The most reliable strategy-1 trigger of the NY open drive |
| **Today's H / L so far** | Running | Intraday liquidity | Live sweep candidates |
| **Unmitigated swing highs/lows** | Fractal swings (L/R=4) on M_5, filtered to those price has not traded through since | *Genuine* untouched liquidity — the only kind that has stops behind it | Prime triggers when clustered (see below) |

### Pool quality grading (this is what stops you trading a level with nothing behind it)
Calibrated on 6 days of NAS100 M_5 (1,379 bars, 2026-08-22):

| Cluster tolerance | Pools found above | of which "confirmed" (≥2 touches) |
|---|---|---|
| 5 pts | 21 | 1 |
| 10 pts | 17 | 4 |
| **15 pts** | 15 | **6** |
| 20 pts | 12 | 6 |
| 30 pts | 11 | 6 |

**Chosen default: `tol = max(12, ADR14 × 0.03)` ≈ 14 pts.** Below ~10 pts every
swing is its own "pool" and the confirmed-equal-highs signal disappears; above
~20 pts distinct levels start merging. NAS100 needs a much wider band than FX
because ADR14 is ~475 points.

Grading:
- **`confirmed` (≥2 touches / equal highs-lows)** — a real pool. Tradeable.
- **`single-touch`** — an incidental swing extreme. Context only. A sweep of a
  single-touch level is *not* the trap; it is noise.
- **`swept`** — price has already traded through it. **Zero liquidity left.**
  Never a target and never a trigger.

*Worked example 2026-08-22 (price 29,290.5):*
```
ABOVE   29,345.0  1 touch   54.5 away  intraday
        29,364.9  1 touch   74.4 away  intraday
        29,401.3  1 touch  110.8 away  intraday
        29,448.8  2 touches 158.3 away  swing     <- confirmed pool
        29,495.2  1 touch  204.7 away  swing
BELOW   29,274.6  2 touches  15.9 away  intraday  <- confirmed pool, very close
        29,133.6  1 touch  156.9 away  swing
```

---

## Tier 2 — Gamma / OI levels (from doc 03)

Marked in a different colour. These are **structural**, not liquidity — price
reacts to dealer hedging, not to stop hunts. They tell you *how* price will
behave at Tier-1 levels.

| Level | Mark as | Reaction brief |
|---|---|---|
| **Gamma flip** | Dashed, full-width | The volatility switch. Above = pinned/mean-revert (strategy 1). Below = trending/expansive (strategy 2). Not S/R — a regime line |
| **Call wall** | Solid, above | Magnetic ceiling. Rallies stall. Best strategy-1 short-sweep level of the day. A held break above = gamma squeeze → strategy 2 long |
| **Put wall** | Solid, below | Defended floor **in positive gamma** — best strategy-1 long-sweep level. **In negative gamma it inverts**: a break is acceleration, not a bounce |
| **Max pain** | Dotted | Weak magnet Mon, strong magnet Thu/Fri. When it coincides with the call wall, treat as a hard pin |
| **Top ±GEX shelves** | Small ticks | `+` bins = expect a stall (good fade). `−` bins = expect a slice (don't fade, do continue) |

---

## Tier 3 — Situational levels (marked only when relevant that day)

These are the "things you might not spot yourself" the brief should surface:

1. **Post-data range H/L.** The high and low of the 30 minutes after a Tier-0
   print. Among the most reliably swept levels on the chart, and they only
   exist on data days.
2. **NY-open range (13:30–14:00) H/L.** Sweeps of this in the 15:30–17:30 lull
   are high-quality strategy-1 triggers because volume is thin and dealers pin.
3. **Overnight gap edge.** Friday 21:00 close vs. Sunday/Monday open. Unfilled
   gaps are magnets; the *gap edge* is where the sweep happens.
4. **Globex (NQ futures) high/low** where it differs from the CFD's Asia/London
   levels — because index futures stops sit there and the CFD follows.
   *2026-08-22 example: NQ Globex H 29,539 / L 29,220; Asia window 29,399.2 /
   29,274.2; London window 29,539.0 / 29,354.5.*
5. **Prior-day VWAP / session mid** on trend days — the standard retrace target.
6. **Round numbers at 250/500-point intervals** (29,000, 29,250, 29,500). On
   NAS100 these carry real option and stop interest, more than on FX.
7. **Big-mover reference:** if NVDA gapped, the index level implied by the
   NVDA move (weight × move) is where the index "should" open; a deviation from
   it is a fade opportunity.
8. **Weekly OPEX pin** (3rd Friday) and **the Monday after OPEX** — one of the
   most reliable range-expansion days in the calendar as the gamma rolls off.

---

## Confluence scoring — which level to actually take

Not all levels are equal. The brief should rank them:

| Confluence | Score |
|---|---|
| Confirmed pool (≥2 touches) | +2 |
| Day-frame level (PDH/PDL/PWH/PWL) | +2 |
| Session extreme (Asia/London H-L) | +2 |
| Within 15 pts of a gamma level (call/put wall, flip, max pain) | +3 |
| Within remaining fuel budget (`reach: intraday`) | +1 |
| Aligned with the day's directional bias | +2 |
| Single-touch only | −1 |
| Already swept | disqualify |
| Beyond remaining fuel (`reach: swing`) | −2 (context only, never today's target) |

**Take the highest-scoring level in the bias direction.** A level scoring ≥7 is
an A-setup; 4–6 is a B; below 4, wait.

The single most powerful configuration for you: **a confirmed day-frame or
session pool sitting within 15 points of the call wall or put wall**, in the
bias direction, inside the fuel budget. That is a Tier-1 stop cluster and a
Tier-2 dealer-hedging wall at the same price — retail stops and dealer flow
both pushing the same way. Those are the setups the brief should lead with.

---

## Strategy selection logic (the brief must state this explicitly)

```
if spot > gamma_flip and net_gex > 0 and vix9d/vix < 0.95:
        primary = STRATEGY 1 (sweep -> failed break -> CISD reversal)
        rationale: dealers actively fade extensions; sweeps genuinely fail
        best levels: call wall, put wall, PDH/PDL, session extremes
        targets: nearest opposing pool / PD mid — keep them tight

elif spot < gamma_flip and net_gex < 0:
        primary = STRATEGY 2 (CISD -> HH/HL -> OTE continuation)
        rationale: dealers amplify; sweeps run, retraces are shallow and hold
        best levels: OTE of the impulse leg after the first CISD
        targets: next unmitigated pool with the trend, trail on structure
        WARNING: strategy-1 fades here have a materially lower hit rate

else:   # straddling the flip
        primary = reduced size, wait for the flip to resolve
        the flip level itself is the decision line
```
