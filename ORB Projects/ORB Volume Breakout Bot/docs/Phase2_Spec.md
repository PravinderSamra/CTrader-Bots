# ORB Volume Breakout Bot — Phase 2 Implementation Spec

**Author:** Fable 5 (spec/design) · **Implementer:** Opus · **Date:** 2026-07-18
**Base:** `ORB Projects/ORB Bot/ORB_Bot.cs` (v2.0 + Phase 1.5 fixes — the reviewed file)
**Deliverable:** `ORB Projects/ORB Volume Breakout Bot/ORB_Volume_Breakout_Bot.cs`

## Purpose

A second bot variant implementing the **premarket-range + volume breakout** strategy from
the `US30 London Range Breakout` research study, reusing the v2.0 core unchanged. The
research findings this encodes:
- Breakout candle must show **high tick volume** — ≥1.2× the trailing-20 average of
  confirm-TF bars was the robust threshold (NAS100 marginally better at 1.3×; >2× starves).
- Research stops were **fixed points from entry** (NAS100 40pt / US30 75pt), not %-of-ORB.
- Static stops beat trailing on NAS100; only loose (~2.5R step) trailing helped US30 —
  handled by existing Dynamic Stop parameters, defaults off.

The owner explicitly requires **both new features to be adjustable in cTrader parameters**
so they can be swept in backtesting/optimization.

## Changes vs the v2.0 base (ONLY these; everything else identical)

### 1. Identity
- New file `ORB_Volume_Breakout_Bot.cs`; class renamed `OrbVolumeBreakoutBot` (so both
  bots can be installed side-by-side); header comment retitled
  "ORB Volume Breakout cBot — v1.0 (Premarket Range + Volume Breakout)" with its own short
  changelog referencing this spec.
- `Bot Label Prefix` parameter **default** changed `"ORB"` → `"ORBV"` (identifier
  unchanged) so positions/labels/history never collide with the base bot on the same
  symbol.

### 2. Volume filter — new parameter group **"Volume Filter"** (owner requirement)
New parameters (place the group directly after "Breakout"):

| Display name | Identifier | Type | Default | Constraints |
|---|---|---|---|---|
| Enable Volume Filter | `EnableVolumeFilter` | bool | **true** | |
| Volume Multiplier | `VolumeMultiplier` | double | **1.2** | MinValue 0.1 |
| Volume Lookback Bars | `VolumeLookbackBars` | int | **20** | MinValue 1, MaxValue 200 |

**Semantics (must match the research backtest):**
- Uses **confirmation-TF** bars' `TickVolumes`.
- Trailing average = mean tick volume of the `VolumeLookbackBars` closed bars
  **immediately before** the evaluation bar (exclusive of it): indices
  `[evalBarIndex - VolumeLookbackBars, evalBarIndex)`, clipped at 0; require ≥1 bar of
  history else the filter fails (no signal).
- Pass condition: `TickVolumes[evalBarIndex] >= VolumeMultiplier × trailingAvg`.
- **The filter is part of SIGNAL QUALIFICATION, not an entry gate.** A close-beyond bar
  with insufficient volume produces **no signal** (so a later, higher-volume breakout bar
  can still trigger that day — "first *qualifying* breakout"). Implement inside
  `EvaluateEntryAtConfirmBar` immediately after `longSignal`/`shortSignal` are determined
  and direction-filtered: if a signal exists but the evaluation bar fails the volume
  check, log (see below) and return as no-signal. Applies identically to the
  BodyCross-multi-bar path (check the evaluation bar).
- **Intrabar mode:** the forming bar's accumulated tick volume is used as-is. Document in
  a comment that this is conservative (volume only grows during the bar), so an intrabar
  signal may initially fail and later pass within the same bar — acceptable.
- **Post-lock replay:** works unchanged — replayed bars evaluate through the same
  qualification, so volume is enforced there too.
- **Catch-up entry:** NOT volume-filtered (it joins an established move, not a breakout
  candle; research has no analogue). Add one comment line stating this explicitly.
- **Diagnostics:** when a would-be signal fails on volume, log via `Log(...)`:
  `VOLUME FILTER: {side} breakout at {bar time} rejected. vol={v} < required {mult}x avg({n})={req}`.
  When it passes and a trade signal proceeds, include `vol=… avg=… ratio=…` in the
  existing `SIGNAL:` log line. This makes threshold tuning in backtest logs easy.

### 3. Fixed-point stop option — additions to group **"Stops & Targets"** (owner requirement)
The existing `%`-of-ORB stop (`StopLossOrbPercent`) remains the default and is untouched.
New parameters:

| Display name | Identifier | Type | Default | Constraints |
|---|---|---|---|---|
| Enable Fixed Point Stop | `EnableFixedPointStop` | bool | **false** | |
| Fixed Stop Points | `FixedStopPoints` | double | **40** | MinValue 0.1 |

**Semantics:**
- When `EnableFixedPointStop = true`, the initial SL price is anchored to the **estimated
  entry price** (same `expectedEntry` already computed in `EnterTrade`):
  `slPrice = expectedEntry ∓ FixedStopPoints × _pointSize` (− for long, + for short),
  rounded to `Symbol.TickSize` exactly as the existing SL is.
- **Unit:** `FixedStopPoints` is measured in the **Point Unit Mode** unit (`_pointSize`),
  the same unit as `Entry Offset Pips` — on US30/NAS100 spread-bet symbols 1 pip = 1 point
  so `40` means 40 index points, matching the research. Add it to the A14 unit-semantics
  comment block under the Point-Unit list.
- When false: behaviour is byte-for-byte the current ORB-percent logic.
- Everything downstream (risk pips, sizing, R-based TP, multi-TP, dynamic stop, early
  risk reduction, attach-at-entry padded protection from A4) already keys off the actual
  entry→SL distance and needs **no changes** — verify this holds and do not duplicate
  logic.
- Log the active stop mode once per trade in the `TRADE ENTERED` line: append
  `stopMode=FixedPoints({X}pt)` or `stopMode=OrbPercent({Y}%)`.

### 4. README.md (new, in the bot folder)
Write a concise parameter guide plus the two research presets, clearly labelled
"starting points from the 3-year study, before costs — re-verify in your own backtests":

- **NAS100 preset:** UseFixedUtcTimes=false, SessionTimeZone=AmericaNewYork,
  Range 02:00→09:30, TradingStart 10:00, EnableKillSwitch=true KillSwitch 11:00 (research
  execution window 10:00–11:00 ET), ClosePositions 16:00, ConfirmationTF=Minute5,
  CloseBeyond, EntryOffset 0, MaxTradesPerDay 1, Volume 1.2×20 (try 1.3×),
  FixedPointStop ON 40pt, TakeProfitR 3.5 (balanced alt: 60pt / 2.0R), DynamicStop OFF.
- **US30 preset:** same shape with Range 08:00→09:30 ET, KillSwitch 13:00 (execution
  10:00–13:00 ET), FixedPointStop ON 75pt, TakeProfitR 3.0, Volume 1.2×20 strictly
  (higher multipliers hurt US30 per the study), DynamicStop optional loose trail
  (BreakEvenTriggerR 2.5 / DynamicStepR 2.5) which slightly beat static in the study.
- Note that tick volume ≠ exchange volume, and that all presets assume the Phase 1.5
  reviewed core.

## Implementation rules (same as Phase 1)
1. Start from the CURRENT `ORB Projects/ORB Bot/ORB_Bot.cs` (HEAD of branch — includes
   Phase 1.5 fixes). Do not regress any v2.0 change.
2. No cTrader compiler here: conservative, syntactically airtight edits; re-read the
   whole output file; verify brace/paren balance and single definitions.
3. Do not rename existing parameter identifiers. New identifiers exactly as tabled above.
4. Also write `IMPLEMENTATION_NOTES.md` in the bot folder mapping spec items → changes.
5. Commit to `claude/us30-london-range-breakout-lu3awm`, push with retries, no PR.

## Acceptance criteria (Fable 5 will verify)
- [ ] File/class/label identity per §1; base file unmodified.
- [ ] Volume Filter group with 3 parameters, defaults 1.2 / 20 / enabled; adjustable in
      cTrader; semantics exactly per §2 (exclusive trailing window, signal-qualification
      placement, no-signal-not-blocked behaviour, catch-up exempt, diagnostics logs).
- [ ] Fixed-point stop per §3: default OFF preserves current behaviour byte-for-byte;
      ON anchors to entry with `_pointSize` units; downstream risk/TP/management flows
      untouched; stop mode logged per trade; unit block updated.
- [ ] README with both presets + disclaimers.
- [ ] Structural verification (braces/parens/single-definition) passes.
