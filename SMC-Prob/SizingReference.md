# Position Sizing Reference — stake(£/point) → `create_order` volume

**Check this table before every `create_order` call.** The skills (`AgentSkill.md` Step 5,
`DayTradeSkill.md`) compute a target stake in **£ per point**, where "point" is defined by
the instrument's `get_symbols` `description` field (e.g. "bet in 1 GBP per (0.01)" → 1 point
= 0.01 price units).

Converting that stake into the integer `volume` field `create_order` expects requires a
**per-category multiplier K**:

```
volume = stake_per_point × K
```

**K is NOT universal across asset classes.** Assuming K=100 for every instrument is the
default trap (it happens to be correct for metals and indices, but is 100× too small for
energies) — see the 2026-06-12 Crude_SB incident in `BUILD-LOG.md` / `TradeLog.md`.

## Confirmed conversion factors (empirically verified via realized P/L on this account)

| symbolCategoryId | Asset class | Example symbols | K | Evidence |
|---|---|---|---|---|
| 67 | Metals | XAUUSD_SB | **100** | 2026-06-12: volume=2600 → realized profit £555.36 on a 21.36pt move = £26.00/pt exactly = 2600 ÷ 100 ✓ |
| 73 | Energies | Crude_SB, Brent_SB, NatGas_SB | **10,000** | 2026-06-12: volume=500 → realized profit £7.45 on a 149pt move = £0.05/pt exactly = 500 ÷ 10,000 ✓. Order was placed assuming K=100 (intended £5/pt) — resulting position was **100× undersized** (£0.05/pt actual, £4.05 risk instead of £405). |

## Unverified — confirm on first live trade in this category

| symbolCategoryId | Asset class | Example symbols | Best-guess K | Status |
|---|---|---|---|---|
| 50 | Indices | US500_SB, NAS100_SB, US30_SB, GER40_SB, UK100_SB | 100 | Per `ctrader-mcp-integration-guide.md` Lesson 5's US30 worked example (volume=1100 → £11/pt claimed) — NOT yet confirmed via this account's own realized P/L |
| 69 | Forex (USD-quoted majors) | EURUSD_SB, GBPUSD_SB, USDJPY_SB | 100 (guess) | UNVERIFIED — no trade of ours has closed in this category yet |
| 71 | Forex crosses | EURGBP_SB, GBPJPY_SB, GBPCAD_SB | 100 (guess) | UNVERIFIED — open EURGBP_SB/GBPCAD_SB positions on this account were placed externally, not sized by this skill, so can't be used to back-solve K |

## How to confirm a new category

1. After a position in an "Unverified" category closes, compute realized P/L ÷ points moved
   = actual £/point.
2. Compare to `volume ÷ best-guess K`.
3. If they match, move the category to "Confirmed" with that K and the evidence (date,
   volume, P/L, points moved).
4. If they don't match, solve `K = volume ÷ actual_£_per_point`, record the corrected K,
   and add a `BUILD-LOG.md` entry documenting the discrepancy (size and direction of the
   error) so past trades in that category can be re-checked.

## Process for the skills (`AgentSkill.md` / `DayTradeSkill.md`)

- After computing `stake_per_point` (Step 5), fetch the instrument's `symbolCategoryId` via
  `get_symbols` and look it up here before computing `volume`.
- **Confirmed category** → use the listed K, proceed normally.
- **Unverified category** → use the best-guess K, but:
  - Prefix the trade card's `Position size` line with `[SIZING UNVERIFIED for category N — see SizingReference.md]`.
  - After the position closes, compute the realized £/point from the balance change and
    update this table per the procedure above.
- **Brand-new category with no entry at all here** → size the first trade at the minimum
  volume (100) regardless of intended risk, confirm realized £/pt on close, then scale up
  on the next trade in that category.
