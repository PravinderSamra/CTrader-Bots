# ORB Volume Breakout cBot — v1.0

A variant of the reviewed **ORB Breakout cBot v2.0** (Phase 1.5 core) that implements the
**premarket-range + volume breakout** strategy from the *US30 London Range Breakout* research
study. It reuses the v2.0 core unchanged and adds only two research-driven features, both
adjustable in cTrader parameters so they can be swept in backtesting / optimization:

1. **Volume Filter** — the breakout candle must show high tick volume relative to a trailing
   average, otherwise it does not count as a signal.
2. **Fixed-Point Stop** (optional) — an initial stop measured as a fixed number of points from
   the estimated entry, instead of a percentage of the ORB range.

Both bots (`OrbBreakoutBot` and `OrbVolumeBreakoutBot`) can be installed and run side by side on
the same symbol: this variant's default **Bot Label Prefix** is `ORBV`, so positions, labels and
history never collide with the base bot.

---

## What's different from the base v2.0 bot

| Area | Base (ORB Breakout) | This bot (ORB Volume Breakout) |
|---|---|---|
| Class name | `OrbBreakoutBot` | `OrbVolumeBreakoutBot` |
| Bot Label Prefix default | `ORB` | `ORBV` |
| Volume filter | none | **Volume Filter** group (below) |
| Stop options | ORB-percent only | ORB-percent **or** optional **Fixed-Point Stop** |

Everything else — session/ORB building, breakout confirmation, sizing, R-based TP, multi-TP,
dynamic stop, early risk reduction, catch-up entry, all safety/execution-risk logic — is
identical to the reviewed v2.0 core.

---

## New parameters

### Volume Filter (new group, placed after "Breakout")

| Display name | Default | Constraints | Meaning |
|---|---|---|---|
| Enable Volume Filter | `true` | | Turn the volume qualification on/off. |
| Volume Multiplier | `1.2` | Min 0.1 | Breakout bar must have `TickVolume >= Multiplier x trailingAvg`. |
| Volume Lookback Bars | `20` | Min 1, Max 200 | Number of confirmation-TF bars in the trailing average. |

**How it works (signal qualification, not an entry gate):**
- Uses the **confirmation-TF** bars' tick volumes.
- The trailing average is the mean tick volume of the `Volume Lookback Bars` closed bars
  **immediately before** the breakout (evaluation) bar — **exclusive** of the eval bar itself,
  window `[evalBar - Lookback, evalBar)`, clipped at 0. At least 1 bar of history is required,
  otherwise the filter fails (no signal).
- Pass condition: `TickVolume[evalBar] >= Volume Multiplier x trailingAvg`.
- A close-beyond bar that **fails** the volume check produces **no signal** — it does *not* stand
  the day down. A later, higher-volume breakout bar can still trigger that day (the "first
  *qualifying* breakout"). This applies identically to multi-bar / BodyCross confirmation (the
  evaluation bar is checked) and to post-lock replay bars.
- **Catch-up entry is exempt** — it joins an established move rather than a specific breakout
  candle, so the research volume-on-breakout finding has no analogue there.
- **Intrabar mode:** the forming bar's accumulated tick volume is used as-is. This is
  conservative (tick volume only grows during a bar), so an intrabar signal may initially fail
  and later pass within the same bar.
- **Diagnostics:** rejected breakouts log
  `VOLUME FILTER: {side} breakout at {time} rejected. vol=... < required {mult}x avg({n})=...`,
  and a qualifying signal appends `vol=... avg=... ratio=...` to the existing `SIGNAL:` line, so
  threshold tuning from backtest logs is easy.

> **Note:** cTrader *tick volume* is the number of price updates in a bar, **not** exchange
> (contract) volume. It is a proxy for activity and is what the research study used.

### Fixed-Point Stop (added to "Stops & Targets")

| Display name | Default | Constraints | Meaning |
|---|---|---|---|
| Enable Fixed Point Stop | `false` | | When on, use a fixed-point stop instead of ORB-percent. |
| Fixed Stop Points | `40` | Min 0.1 | Stop distance from the estimated entry, in **Point-Unit** units. |

**How it works:**
- When **off** (default) the bot uses the existing `Stop Loss ORB Percent` logic, byte-for-byte.
- When **on**, the initial SL is anchored to the **estimated entry price**:
  `SL = entry - FixedStopPoints x _pointSize` (long) / `entry + ...` (short), then rounded to
  `Symbol.TickSize` exactly as the ORB-percent stop is.
- `Fixed Stop Points` is measured in the **Point Unit Mode** unit (`_pointSize`), the same unit as
  `Entry Offset Pips`. On US30/NAS100 spread-bet symbols **1 pip = 1 point**, so `40` means
  40 index points — matching the research.
- Everything downstream (risk pips, position sizing, R-based TP, multi-TP, dynamic stop, early
  risk reduction, attach-at-entry padded protection) keys off the **actual entry→SL distance**,
  so it works unchanged for both stop modes with no duplicated logic.
- The active stop mode is logged per trade in the `TRADE ENTERED` line as
  `stopMode=FixedPoints(40pt)` or `stopMode=OrbPercent(50%)`.

---

## Research presets

> **Disclaimer:** These are **starting points from the 3-year study, before costs** — re-verify
> in your own backtests before any live use. cTrader *tick volume* is not exchange volume, and all
> presets assume the **Phase 1.5 reviewed core** (this bot). Results depend on your broker's data,
> spreads, and fills.

### NAS100 preset

| Parameter | Value |
|---|---|
| Use Fixed UTC Times | `false` |
| Session Time Zone | `AmericaNewYork` |
| Range Start / End | `02:00` → `09:30` |
| Trading Start Time | `10:00` |
| Enable Kill Switch | `true` |
| Kill Switch Time | `11:00` (research execution window 10:00–11:00 ET) |
| Enable Close Positions Time | `true`, Close Positions `16:00` |
| Confirmation TimeFrame | `Minute5` |
| Breakout Cross Type | `CloseBeyond` |
| Entry Offset Pips | `0` |
| Max Trades Per Day | `1` |
| Enable Volume Filter | `true`, Multiplier `1.2`, Lookback `20` (try `1.3`) |
| Enable Fixed Point Stop | `true`, Fixed Stop Points `40` |
| Take Profit R | `3.5` |
| Enable Dynamic Stop | `false` |

*Balanced alternative:* Fixed Stop Points `60` with Take Profit R `2.0`.

### US30 preset

| Parameter | Value |
|---|---|
| Use Fixed UTC Times | `false` |
| Session Time Zone | `AmericaNewYork` |
| Range Start / End | `08:00` → `09:30` |
| Trading Start Time | `10:00` |
| Enable Kill Switch | `true` |
| Kill Switch Time | `13:00` (research execution window 10:00–13:00 ET) |
| Enable Close Positions Time | `true`, Close Positions `16:00` |
| Confirmation TimeFrame | `Minute5` |
| Breakout Cross Type | `CloseBeyond` |
| Entry Offset Pips | `0` |
| Max Trades Per Day | `1` |
| Enable Volume Filter | `true`, Multiplier `1.2`, Lookback `20` (strictly — higher multipliers hurt US30 per the study) |
| Enable Fixed Point Stop | `true`, Fixed Stop Points `75` |
| Take Profit R | `3.0` |
| Enable Dynamic Stop | *optional loose trail:* `true`, Break Even Trigger R `2.5`, Dynamic Step R `2.5` (slightly beat static in the study) |

### Notes on the research findings encoded here
- The breakout candle must show high tick volume — **≥1.2×** the trailing-20 average of
  confirmation-TF bars was the robust threshold (NAS100 marginally better at 1.3×; **>2× starves**
  the strategy of signals).
- Research stops were **fixed points from entry** (NAS100 40pt / US30 75pt), not %-of-ORB.
- Static stops beat trailing on NAS100; only a loose (~2.5R step) trailing helped US30 — handled
  by the existing Dynamic Stop parameters, defaults off.
