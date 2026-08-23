# 06 — Range & Fuel: how much move is left, and when to manage the stop

Mirrors the Liquidity Trap model (`references/03-expansion-volume-and-scope.md`)
and the UK100 ORB range-budget rule, recalibrated for NAS100 — which has a much
larger ADR and a very different intraday shape.

The purpose, in your words: *"so I can understand if I need to actively manage
my stop loss as price moves, because it would only have a limited amount of
fuel left for the move."*

---

## 1. The gauge

```
ADR14            = mean(High − Low) over the last 14 completed daily bars
today_range      = today_high − today_low   (bucketed on the 21:00 UTC roll)
adr_used_pct     = today_range / ADR14 × 100
remaining_budget = max(0, ADR14 − today_range)
```

*Measured 2026-08-22: ADR14 = **474.7 pts**, day range 318.6 → **67.1% used**,
**156.1 pts of budget left** → `MODERATE`.*

| State | Trigger | What it means for you |
|---|---|---|
| `ROOM_TO_EXPAND` | ≤ 40% used | Full tank. Strategy-2 continuation is on. Far pools are reachable. Let winners run; trail on structure, not on ticks |
| `MODERATE` | 40–70% | Normal. Target the nearest in-reach pool. Standard management |
| `LOW_FUEL` | 70–90% | Little left for a fresh breakout. **Favour fades over chases.** Tighten targets to the nearest pool. **Start actively trailing** — this is the zone where a winner gives back |
| `EXHAUSTED` | ≥ 90% | Range spent. New continuation is low-probability. Prefer no-trade or a small mean-reversion back into the range. If already in a trade, **move to break-even or take partials** |

### Volume, the second half of the gauge
`exec_relative` = mean tick volume of the last 12 M_5 bars ÷ the prior baseline.

- **≥ 1.25 `expanding`** — participation is behind the move. A sweep here is
  more likely a real trap with follow-through. Confidence up.
- **~1.0 `normal`** — neutral.
- **≤ 0.70 `drying_up`** — running on fumes. Sweeps may not follow through.
  Downgrade, especially into the 15:30–17:30 lull.

*Measured 2026-08-22: relative 0.71 → `normal`, right at the edge of drying.*

**Best setups = `ROOM_TO_EXPAND`/`MODERATE` + expanding volume in the bias
direction. Worst = `EXHAUSTED` + drying → stand down.**

---

## 2. NAS100-specific calibration (this is where it differs from gold/UK100)

Three adjustments the generic model gets wrong on NAS100:

### a) Time-of-day fuel, not just total fuel
NAS100 does not spend its range evenly. Roughly:

| Window (US Eastern) | Typical share of the day's range consumed |
|---|---|
| Asia 19:00–03:00 ET | ~15% |
| London 03:00–09:30 ET | ~25% |
| **NY open 09:30–12:00 ET** | **~45%** |
| NY afternoon 12:00–17:00 ET | ~15% |

Keyed to **Eastern time, not UTC** — the curve tracks the session, and the
session moves an hour against UTC twice a year. `bias_engine.expected_consumed()`
resolves it with `zoneinfo`.

So "67% of ADR used" at **08:00 ET** is a genuinely exhausted day — the biggest
window has not even opened and the tank is nearly empty, which usually means a
reversal day. The same 67% at **13:00 ET** is completely normal.

**The brief must therefore report `adr_used_pct` *against the expected
consumption for the current time of day*, not against 100%:**

```
expected_used_by_now = cumulative share for the current EASTERN hour
fuel_ratio           = adr_used_pct / expected_used_by_now
```
- `fuel_ratio > 1.4` → **burning hot.** The day is trending or has already had
  its event. Expect ADR to be exceeded (trend day) *or* an exhaustion reversal.
  Either way: trail actively.
- `fuel_ratio ≈ 1.0` → normal day, standard targets.
- `fuel_ratio < 0.6` → **coiled.** Range is compressed relative to normal;
  expect an expansion later. Do not fade the eventual break.

### b) VXN-implied range as a cross-check on ADR
ADR is backward-looking. VXN is the market's *forward* estimate.

```
implied_daily_range ≈ Spot × (VXN / 100) / √252
```
*2026-08-22: 29,290 × 0.2198 / 15.87 = **405.7 pts** implied, vs ADR14 474.7.*

When implied < ADR (as now), the options market is pricing a **quieter** day
than the recent past — mean-reversion is favoured and ADR overstates the
budget. When implied > ADR, expect expansion and ADR *understates* it. The
brief should use `min(ADR14, implied)` as the conservative budget on
mean-reversion days and `max(...)` on expansion days.

### c) Gamma regime scales the budget
- **Positive gamma / above flip:** dealers suppress realised vol. Multiply the
  remaining budget by **~0.8**. Targets should be tighter than ADR suggests.
- **Negative gamma / below flip:** dealers amplify. Multiply by **~1.3**, and
  accept that ADR can be exceeded outright.
- **Backwardated vol (VIX9D/VIX > 1.0):** additional ×1.2.

---

## 3. Target scoping (the rule that keeps ideas day-sized)

Each candidate pool is tagged:
- **`intraday`** — distance from price ≤ adjusted remaining budget → a valid
  target today.
- **`swing`** — beyond it → **context only, never today's target.**

Rules:
1. Target = the nearest `intraday`, `confirmed`, un-swept pool in the bias
   direction.
2. A `swing` pool is mentioned as the bigger magnet but is not the target.
3. **Draw-beyond-fuel:** if the only pool in the bias direction is `swing`,
   either take a partial-only trade to the nearest in-reach internal level and
   be flat by session end, or **no-trade** ("right idea, wrong day").
4. Reach is a probability filter, not a guarantee — a strong trend day exceeds
   ADR. Note that as upside, never as the planned target.

---

## 4. Stop management driven by fuel — the practical output

This is the section that answers your actual question. The brief should emit an
explicit management plan per idea:

| Fuel state at entry | Stop management |
|---|---|
| `ROOM_TO_EXPAND` | Leave the structural stop alone (beyond the sweep extreme / fib low). Trail only on confirmed 1m structure breaks — HL for longs, LH for shorts. Do not touch it for noise |
| `MODERATE` | Structural stop. Move to break-even once price has travelled **1R** *or* reached 50% of remaining budget, whichever comes first |
| `LOW_FUEL` | **Active management from the start.** Break-even at 0.7R. Take 50% off at the first pool. Trail the remainder tightly on 1m structure. Expect to be trailed out rather than target-filled |
| `EXHAUSTED` | Don't initiate. If already in: take partials immediately, stop to break-even or better, and be flat before the close |

Additional triggers that force a management action regardless of state:

1. **Budget exhaustion mid-trade** — when `adr_used_pct` crosses 90% while you
   are in the trade, the remaining move is borrowed. Take partials.
2. **Gamma flip crossed against you** — if you are long in a mean-reversion
   (strategy-1) trade and price breaks *below* the flip, your edge has
   inverted. Tighten or exit; do not add.
3. **Volume drying while extended** — `drying_up` with `adr_used_pct > 70` is
   the classic pre-reversal signature. Tighten.
4. **Approaching a large `+GEX` shelf with the trade** — price will stall
   there. Take partials *into* the shelf rather than hoping through it.
5. **Approaching a large `−GEX` shelf with the trade** — price accelerates
   through. Give it room; this is where the trade pays.
6. **A High-impact print inside 15 minutes** — flatten or hard-stop to
   break-even. Neither of your models survives a data-print sweep.

---

## 5. What the brief prints

One paragraph, every run:

> **Fuel:** ADR14 474.7. Day range 318.6 = **67% used**, 156 pts of raw budget
> left. It is 05:50 ET — only ~34% of a normal day's range is usually spent by
> now, so the `fuel_ratio` is **1.7: burning hot**. VXN implies a 406-pt day
> (below ADR), and we are **below the gamma flip** (negative gamma, ×1.3), so
> the working budget is ~**165 pts**. Nearest in-reach pool above is 29,345
> (54 pts); the confirmed pool at 29,448.8 is 158 pts away — just inside budget
> but only as a stretch target, take partials before it. **Manage actively:
> LOW_FUEL rules from entry — break-even at 0.7R, 50% off at the first pool.**
