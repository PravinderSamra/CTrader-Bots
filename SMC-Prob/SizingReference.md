# Position Sizing Reference — stake(£/point) → `create_order` volume

**Check this before every `create_order` call.** The skills (`AgentSkill.md` Step 5,
`DayTradeSkill.md`) compute a target stake in **£ per point**, where "point" is defined by
the instrument's `get_symbols` `description` field (e.g. "bet in 1 GBP per (0.0001)" → 1
point = 0.0001 price units; "bet in 1 GBP per (1.00)" → 1 point = 1.00 price units).

## Primary formula (derived from confirmed data, use this first)

```
volume = (stake_per_point ÷ point_size) × 100
```

`point_size` is the number in the instrument's `get_symbols` `description` — e.g. 0.0001
for EURUSD_SB/GBPCAD_SB, 0.01 for USDJPY_SB/GBPJPY_SB/Crude_SB/Brent_SB, 1.00 for
XAUUSD_SB and all indices.

Equivalently: **`volume / 100` = £ per 1.0 unit of *raw* price movement**, independent of
instrument — this is the standard cTrader "volume in cents of base, contract value scales
with volume" convention. A smaller `point_size` (e.g. 0.0001) means each "point" is a
smaller slice of raw price movement, so it takes a much larger `volume` to produce the
same £/point stake — hence K (= volume ÷ stake_per_point) grows as point_size shrinks.

### Confirmed against realized P/L on this account (n=2, both exact)

| Symbol | point_size | Predicted volume for £X/pt | Actual trade | Realized £/pt | Check |
|---|---|---|---|---|---|
| XAUUSD_SB | 1.00 | `volume = X × 100` | volume=2600 (intended £26/pt) | £26.00/pt exactly (£555.36 / 21.36pt) | `(26/1.00)×100=2600` ✓ |
| Crude_SB | 0.01 | `volume = X × 10,000` | volume=500 (intended £5/pt, but formula says should've been 50,000) | £0.05/pt exactly (£7.45 / 149pt) | `(0.05/0.01)×100 = 500` ✓ — confirms formula in reverse: the 100×-undersized order is *exactly* what the formula predicts for volume=500 |

### Derived predictions (NOT yet independently confirmed on this account — verify on first live trade)

| Asset class | Example symbols | point_size | K = volume ÷ stake_per_pt | Confidence |
|---|---|---|---|---|
| Indices | US500_SB, NAS100_SB, US30_SB, GER40_SB, UK100_SB | 1.00 | **100** | Medium — also matches `ctrader-mcp-integration-guide.md` Lesson 5's US30 example (volume=1100 → £11/pt) |
| JPY pairs / energies-like | USDJPY_SB, GBPJPY_SB | 0.01 | **10,000** | Low-medium — same point_size class as Crude (confirmed), but different `symbolCategoryId` |
| 4-decimal FX (majors/crosses) | EURUSD_SB, GBPUSD_SB, EURGBP_SB, GBPCAD_SB | 0.0001 | **1,000,000** | Low — large extrapolation (n=2 → predicts a 10,000× jump from metals' K). Treat K=100 (the old default) as actively wrong here, not just unverified. |

**⚠ Do not fall back to K=100 for forex.** If the formula above is right, K=100 for a
0.0001-point_size pair would mean `volume=100` → £0.01/pt — i.e. a forex order sized with
the old "volume=stake×100" assumption would be **10,000× undersized** (vs. 100× for
energies). Conversely, if you ever reach for K=1,000,000 by habit on an instrument with
point_size=1.00 (metals/indices), that's a 10,000×-**oversized** order. Always compute
`point_size` from the description first.

## How to confirm a new instrument

1. After a position closes, compute realized P/L ÷ points moved = actual £/point.
2. Compare to `volume ÷ (100 / point_size)` (the formula's prediction).
3. If they match, move the row to "Confirmed" with the evidence (date, volume, P/L, points
   moved, point_size).
4. If they don't match, record the actual K, add a `BUILD-LOG.md` entry, and re-derive the
   pattern (the point_size-inverse relationship may not hold universally).

## Process for the skills (`AgentSkill.md` / `DayTradeSkill.md`)

- After computing `stake_per_point` (Step 5), read `point_size` from the instrument's
  `get_symbols` `description`, then compute `volume = (stake_per_point ÷ point_size) × 100`.
- **For instrument classes with a "Confirmed" row above** → proceed normally.
- **For "Derived prediction" classes (indices, JPY pairs, 4-decimal FX)** → use the
  formula's prediction, but prefix the trade card's `Position size` line with
  `[SIZING UNVERIFIED — see SizingReference.md]`, and once the position closes compute
  realized £/point to confirm/correct.
- **Brand-new instrument with an unfamiliar `point_size`** → size the first trade at
  minimum volume (100) regardless of intended risk, confirm realized £/pt on close, then
  scale on the next trade.
