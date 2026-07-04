# News Straddle Bot — Architecture & Build Specification

For: Claude Code implementation | Platform: cTrader Algo (cBot, C#) | Repo: CTraderBots

This is a Markdown transcription of the original build spec PDF supplied for this bot. It is the source of truth for `NewsStraddleBot.cs`; see `README.md` for the as-built implementation notes and any deliberate deviations.

## 1. Executive Summary

This bot automates the pre-news volatility straddle: two pending stop (or stop-limit) orders placed symmetrically around spot price shortly before a scheduled economic release, designed to capture the directional spike that follows, with the untriggered side cancelled the instant the other fills. The bot is instrument-agnostic (tested primarily on XAUUSD and US500/GER40), single-event-per-instance, fully parameter-driven, and manually scheduled (no live news feed in v1).

Core design principle: this is a risk-management machine first, an entry mechanism second. The straddle entry itself is trivial; the value of this build is in eliminating every way it can fail silently (double-fill whipsaw, stale orders, bad fills into abnormal spread, undersized/oversized stops, broker minimum-distance rejections).

## 2. Research Findings (Phase 2)

1. **Whipsaw risk is the dominant failure mode.** The most consistent warning across trader literature: once one side of the straddle fills, the opposite pending order must be cancelled instantly — leaving both live risks a double loss on a spike-then-reversal (very common on NFP, common on CPI, extreme on FOMC).
2. **Spreads widen materially during release**, commonly cited at several multiples of normal spread in the first 1–5 minutes. This affects both fill quality (favors stop-limit for slippage control) and the validity of the buffer distance itself (a buffer that's fine in normal conditions may be inside the spread during the release).
3. **Fixed, tight stops routinely get swept** by the initial noise spike before the "real" move develops — stops need to be sized with slippage and instrument volatility in mind, not a static default.
4. **Broker/instrument minimum stop distance ("freeze level")** can silently reject or reprice orders placed too close to spot. This must be read from the symbol at runtime, not assumed.
5. **Reversal (fade) risk is real and well-documented** — price can spike and fully round-trip within 15 minutes, especially on NFP. This is why a no-cap trailing stop (per the original spec) is the right call over a fixed static TP-only approach — it lets winners run but gives back gains mechanically as trend fails, rather than requiring a hard target.
6. **cTrader has no native OCO / bracket order type.** Confirmed via API docs — this must be built manually: place both pending orders, subscribe to the `PendingOrders.Filled` event, cancel the sibling order asynchronously the instant one fills.

### Refinements adopted into this spec (beyond the original list)

- **Stop-limit range parameter** (`StopLimitRangePips`) exposed when Stop-Limit mode is selected — controls max acceptable slippage past the trigger price before the order is abandoned rather than chasing a bad fill.
- **Minimum distance validation** — bot reads the symbol's minimum stop distance/spread at placement time and auto-widens or rejects placement per the Spread Guard parameter, rather than blindly submitting an order the broker will reject.
- **Pre-flight state check** — before placing anything, the bot confirms no existing position/pending order under its own label is already active on the chart, preventing duplicate straddles if `OnStart` re-fires or the bot is re-added.
- **Persistent kill-switch on error** — if either leg's placement fails (rejection, connectivity), the bot cancels the sibling order rather than leaving a naked single-sided straddle.
- **Full event-driven logging** — every state transition (armed → orders placed → filled → sibling cancelled → dynamic stop active → closed/timed out) is printed to the log and, optionally, shown as a chart status label, so the outcome of each news event can be audited afterward.

## 3. Parameter Specification

### 3.1 Risk & Sizing

| Parameter | Type | Default | Notes |
|---|---|---|---|
| `RiskMode` | enum: `PercentOfEquity`, `FixedAmount` | `PercentOfEquity` | |
| `RiskPercent` | double | 0.5 | Used if `RiskMode = PercentOfEquity` |
| `RiskFixedAmount` | double | 100 | Account currency, used if `RiskMode = FixedAmount` |
| `MaxLotCap` | double | 0 (off) | Optional hard cap on volume regardless of risk calc — safety rail against a mis-set SL producing an oversized position |
| `SlippageBufferPercent` | double | 30 | Inflates the assumed SL distance in the position-sizing formula only (not the actual SL) to account for news-event stop slippage. E.g. 30% means volume is sized as if the SL were 30% further away, so a slipped stop still lands near the intended risk amount rather than materially exceeding it |

### 3.2 News Timing

| Parameter | Type | Default | Notes |
|---|---|---|---|
| `NewsDateTime` | DateTime (cTrader native date/time picker) | — | The scheduled release time, entered in the timezone selected below |
| `NewsTimeZone` | enum: `NewYork`, `London/UK`, `Frankfurt`, `Tokyo`, `Singapore`, `HongKong` | `NewYork` | DST-aware conversion to server/UTC time (see 5.2) |
| `EntryLeadMinutes` | int | 2 | Minutes before news time that orders are placed. Adjustable 1–10 for testing |
| `OrderTimeoutMinutes` | int | 10 | Minutes after news time before any unfilled pending order(s) auto-cancel |

### 3.3 Entry Structure

| Parameter | Type | Default | Notes |
|---|---|---|---|
| `BufferDistance` | double | 10 | In pips (FX/metals) or points (indices) per auto-detected instrument type |
| `OrderExecutionType` | enum: `StopMarket`, `StopLimit` | `StopMarket` | Toggle for A/B testing |
| `StopLimitRangePips` | double | 5 | Max slippage tolerance past trigger before StopLimit order is abandoned (only used if `OrderExecutionType = StopLimit`) |
| `TriggerSide` | enum: `Standard`, `OppositeSide` | `OppositeSide` | Maps to cTrader `StopTriggerMethod`. `Standard` = buy stop triggers on Ask / sell stop on Bid (default cTrader behavior, vulnerable to spread-widening double-triggers at release). `OppositeSide` = buy stop triggers on Bid / sell stop on Ask — immune to spread blowout, fires only on real mid-price movement. See 5.7 |
| `ExpectedReleaseSpread` | double | 15 | User's estimate (pips/points) of typical spread blowout on this instrument during the release. Used only for the pre-flight sanity warning in 5.7 — if `BufferDistance < 2 × ExpectedReleaseSpread` and `TriggerSide = Standard`, the bot logs a loud warning that spread-triggered double fills are likely |
| `Volume` | derived | — | Calculated from risk parameters + SL distance + instrument tick value (not user-entered directly) |

### 3.4 Spread Guard

| Parameter | Type | Default | Notes |
|---|---|---|---|
| `SpreadGuardMode` | enum: `ProceedAnyway`, `AutoWidenBuffer`, `SkipTrade` | `ProceedAnyway` | Behavior when spread at T-minus-lead-time exceeds `SpreadGuardThreshold` |
| `SpreadGuardThreshold` | double | 3.0 | Multiple of the instrument's average spread (rolling sample) that counts as "abnormal" |
| `SpreadWidenFactor` | double | 1.5 | If `AutoWidenBuffer` selected: buffer is multiplied by this factor |

### 3.5 Stop Loss / Take Profit

| Parameter | Type | Default | Notes |
|---|---|---|---|
| `StopLossDistance` | double | 20 | Pips/points behind entry, auto-converted per instrument |
| `EnableTakeProfit` | bool | true | |
| `TakeProfitR` | double | 2.0 | Take profit expressed as multiple of risk (R), converted to price internally |

### 3.6 Dynamic (Trailing) Stop

| Parameter | Type | Default | Notes |
|---|---|---|---|
| `EnableDynamicStop` | bool | false | |
| `DynamicStopActivationR` | double | 0.25 | R-multiple at which trailing begins |
| `DynamicStopTrailR` | double | 0.25 | Step size (in R) the stop advances by, once active |
| `DynamicStopExtraPips` | double | 0.0 | Optional buffer added at the activation step (mirrors "break-even + extra pips" pattern) |

Design decision (revised after reviewing the prior ORB Breakout bot): implemented as a **quantized ratchet**, not a literal per-tick recompute. Every `OnTick()`, current profit-in-R is checked; each time it crosses a new `DynamicStopTrailR` increment past `DynamicStopActivationR`, the stop is advanced to lock in that step — and only ever forward, never loosened. This produces the same practical behavior as "the stop follows price by a constant R-distance" while avoiding tick-by-tick `ModifyPosition` calls, which risk broker rate-limiting or rejected/late modifications during the exact high-speed conditions a news spike creates. See 5.5 for the algorithm, adapted directly from the proven pattern in the ORB bot's `ProcessDynamicStop`.

**TP/Dynamic Stop precedence (confirmed):** when both `EnableTakeProfit` and `EnableDynamicStop` are on, TP remains a hard cap — the position closes at TP if reached, with the dynamic stop trailing underneath it the whole way up. Dynamic Stop only takes over the exit if price reverses before TP is hit.

### 3.6a Double-Fill Handling

| Parameter | Type | Default | Notes |
|---|---|---|---|
| `DoubleFillPolicy` | enum: `FlattenBoth`, `KeepBetterPriced`, `KeepFirstFilled` | `FlattenBoth` | Governs the rare case where both legs fill before the OCO cancel completes (see 6) |

### 3.7 Instrument Handling

| Parameter | Type | Default | Notes |
|---|---|---|---|
| `AutoDetectInstrument` | bool | true (not user-toggleable in v1, always on) | Reads `Symbol.PipSize`, `Symbol.TickSize`, and digit count at `OnStart` to determine whether the chart's instrument is pip-based (FX/metals) or point-based (indices), and scales `BufferDistance`/`StopLossDistance` inputs accordingly |

### 3.8 Diagnostics / Safety

| Parameter | Type | Default | Notes |
|---|---|---|---|
| `EnableChartLabels` | bool | true | Draws current bot state + key levels on chart |
| `EnableDetailedLogging` | bool | true | Full `Print()` trail of every decision |

## 4. State Machine

```
IDLE
  -> (Server time reaches NewsDateTime - EntryLeadMinutes, TZ-converted)
ARMING
  -> Pre-flight checks (no existing position/order under this label; spread check per SpreadGuardMode)
  -> PASS -> PLACING_ORDERS
  -> FAIL (SkipTrade selected & spread bad) -> SKIPPED (log + idle until next manual run)
PLACING_ORDERS
  -> Place Buy-side pending order (Stop or Stop-Limit) at Ask + BufferDistance
  -> Place Sell-side pending order (Stop or Stop-Limit) at Bid - BufferDistance
  -> Both placed successfully -> ARMED_WAITING
  -> Either fails -> cancel the other if placed -> ERROR_STATE (log reason)
ARMED_WAITING
  -> PendingOrders.Filled fires on Order A -> FILLED
       -> Immediately CancelPendingOrderAsync(Order B)
  -> OrderTimeoutMinutes elapses with neither filled -> cancel both -> TIMED_OUT
FILLED
  -> Apply SL (StopLossDistance) and TP (if EnableTakeProfit) to resulting position
  -> If EnableDynamicStop: begin monitoring R-multiple on every OnTick/OnBar
  -> Position closes (SL/TP/dynamic stop/manual) -> COMPLETE
TIMED_OUT / SKIPPED / ERROR_STATE / COMPLETE
  -> Bot remains attached to chart, logs final outcome, returns to IDLE
     (ready for the next NewsDateTime value the user manually re-enters)
```

## 5. Implementation Notes (cTrader Algo API)

### 5.1 Order placement & OCO emulation

cTrader has no native OCO order type — this must be hand-built:

- Use `PlaceStopOrder()` / `PlaceStopLimitOrder()` (the latter takes a `StopLimitRangePips` parameter natively, matching 3.3 directly) for both legs, each with a distinct `Label` (e.g. `NewsStraddle_Buy_<timestamp>`, `NewsStraddle_Sell_<timestamp>`) so they can be individually identified and managed.
- Subscribe to `PendingOrders.Filled` in `OnStart()`. When either leg's label matches this bot's active pair, immediately call `CancelPendingOrderAsync()` on the sibling order found via the `PendingOrders` collection lookup by label.
- Subscribe to `PendingOrders.Cancelled` to log cancellation reason (`Cancelled`, `Expired`, `Rejected`) for audit trail.
- Use the **Async** placement/cancellation methods throughout — critical during news volatility where synchronous round-trip latency could let both legs fill before cancellation completes.

### 5.2 Timezone / DST handling

Declare the robot as `[Robot(TimeZone = TimeZones.UTC)]` and perform all internal time comparison in UTC via `Server.TimeInUtc`. This eliminates broker-offset arithmetic entirely — exactly one conversion exists in the whole bot:

1. Take the user's `NewsDateTime` input as a "wall clock" time in the selected `NewsTimeZone`.
2. Convert to UTC via .NET `TimeZoneInfo.ConvertTimeToUtc()` with correct mappings for the 6 supported zones (`America/New_York`, `Europe/London`, `Europe/Berlin`, `Asia/Tokyo`, `Asia/Singapore`, `Asia/Hong_Kong`) — DST transitions resolve automatically.
3. Compare against `Server.TimeInUtc` in the timer loop. No broker-offset conversion step exists.

Recommend a `Timer` (cTrader `Timer.Start(1)` — 1 second interval) rather than relying purely on `OnTick()`, so timing precision doesn't depend on tick frequency (important on quiet instruments where ticks can be sparse right before a release).

### 5.3 Instrument auto-detection & pip/point conversion

On `OnStart()`, read `Symbol.PipSize` and `Symbol.TickSize`. Indices (US500, GER40) typically have `PipSize == TickSize` (i.e., "points"), while FX/metals have `PipSize = 10 * TickSize` in most conventions.

Build a single internal helper `ToPriceDistance(double userUnits)` that all buffer/SL/TP calculations route through, so the parameter UI always shows "pips/points" in the units natural to the instrument without the user manually recalculating.

Validate against the symbol's minimum stop level where exposed — if `BufferDistance` (or SL) is inside that minimum, apply `SpreadGuardMode` logic (widen/skip) rather than submitting and risking rejection.

### 5.4 Position sizing

Formula: `Volume = RiskAmount / (StopLossDistance_in_price × (1 + SlippageBufferPercent/100) × Symbol.PipValue per lot)`, normalized to `Symbol.VolumeInUnitsMin`/step via `Symbol.NormalizeVolumeInUnits()`. The slippage buffer is applied to the *sizing* denominator only — the actual SL is still placed at `StopLossDistance` — so a realistically slipped stop lands near the intended risk rather than overshooting it.

- `RiskAmount = Account.Equity * (RiskPercent/100)` or `RiskFixedAmount`, per `RiskMode`.
- Apply `MaxLotCap` as a final clamp if set.

### 5.5 Dynamic stop trailing (ratchet design, adapted from prior ORB bot)

Confirmed: monitored on `OnTick()`.

Maintain a `Dictionary<long, PositionState>` keyed by `Position.Id`, storing at minimum: `EntryPrice`, `InitialStopPrice`, `InitialRiskInPriceUnits`, `LastTrailSteps` (init `-1`).

On every `OnTick()`, for each bot-managed open position:

1. `profitR = CurrentProfitInPriceUnits / InitialRiskInPriceUnits` (direction-adjusted).
2. If `profitR < DynamicStopActivationR`, do nothing.
3. On first crossing of `DynamicStopActivationR`: move SL to `EntryPrice ± DynamicStopExtraPips` (activation-step move), mark this in state.
4. Compute `steps = Floor((profitR - DynamicStopActivationR) / DynamicStopTrailR)`. If `steps > state.LastTrailSteps`:
   - `lockedR = steps * DynamicStopTrailR`
   - `desiredSL = EntryPrice ± (DynamicStopExtraPips + lockedR * InitialRiskInPriceUnits)` (direction-adjusted)
   - Round `desiredSL` to `Symbol.TickSize`.
   - Guard: only apply if `desiredSL` is more favorable than the current `Position.StopLoss` (never loosen).
   - `Position.ModifyStopLossPrice(desiredSL)` (or `ModifyPosition` with `ProtectionType.Absolute`), then update `state.LastTrailSteps = steps`.
5. If `EnableTakeProfit = true`, TP remains untouched by this process — it is set once at fill time and acts as the hard cap regardless of dynamic stop progress (confirmed precedence, 3.6).

This mirrors the proven pattern in the ORB Breakout bot's `ProcessDynamicStop`/`PositionState` design rather than a naive per-tick SL recompute, which would risk excessive `ModifyPosition` calls and possible rate-limiting or rejected/stale modify requests during the highest-volatility seconds of the release.

### 5.6 Spread guard check

At `EntryLeadMinutes` before news, sample current spread (`Symbol.Spread`) against a rolling average spread computed over the preceding N minutes (e.g., last 30 mins, stored via a simple running buffer) to define "normal" for that instrument/session — a static pip threshold won't work equally for XAUUSD vs US500.

Apply `SpreadGuardMode` logic before proceeding to `PLACING_ORDERS`.

### 5.7 Trigger side — spread-blowout immunity (CRITICAL)

This is the single most important execution detail in the entire bot.

By cTrader default, a buy stop triggers when the Ask touches the level and a sell stop when the Bid touches it. At release time, spread can widen by 10–30+ points in one second on XAUUSD. With a symmetric buffer sized against *normal* spread, this means **both legs can trigger simultaneously from spread widening alone, with no real price movement** — Ask spikes up through the buy stop while Bid drops through the sell stop. This is not the rare gap-through-both-levels edge case; on a tight buffer during NFP/CPI it is the *expected* outcome, and it converts the straddle into an instant two-sided loss plus double spread cost.

Mitigation (default behavior):

- Place both legs with cTrader's `StopTriggerMethod.Opposite` — buy stop triggers on Bid reaching the level, sell stop triggers on Ask reaching it. Triggering is then driven by real directional movement, not spread expansion. Exposed via the `TriggerSide` parameter (3.3) so `Standard` can still be A/B tested deliberately.
- Trade-off documented here: with `OppositeSide`, the fill occurs roughly one spread-width later than with `Standard`, i.e. slightly worse entry on the winning side — a small, bounded cost versus the unbounded cost of a spread-triggered double fill.
- Pre-flight check: if `TriggerSide = Standard` AND `BufferDistance < 2 × ExpectedReleaseSpread`, log a prominent warning at ARMING and (optionally, per `SpreadGuardMode`) refuse to arm.
- Note: the same `StopTriggerMethod` consideration applies to the stop loss on the resulting position — use `StopTriggerMethod.Trade`/`Opposite` consistently so the SL is also not swept purely by spread blowout in the seconds after fill.

## 6. Edge Cases & Risk Controls Checklist

- Bot re-added to chart / restarted mid-cycle with a pending order already live under its label → detect and resume state rather than duplicating.
- Only one leg successfully places (partial failure) → cancel the other immediately, do not proceed half-armed.
- Both legs fill on the same tick (extreme gap through both levels, cancel race lost) → detect via `Positions.Opened` count check; resolve per `DoubleFillPolicy` (3.6a). Default: `FlattenBoth` — close both immediately at market and log as an anomaly, rather than trying to select a "better" side during an already-chaotic execution event. `KeepBetterPriced` and `KeepFirstFilled` are available as alternate settings to test.
- `OrderTimeoutMinutes` reached with no fill → cancel both, log as `TIMED_OUT`, no position taken.
- Weekend/market-closed news time entered by mistake → validate `NewsDateTime` falls within the symbol's trading sessions; warn in log if not.
- Dynamic stop enabled but `EnableTakeProfit` also enabled → confirm precedence: TP still fires as a hard cap even while dynamic stop trails underneath it (recommended default).
- Broker rejects order for min-distance/margin reasons → log full rejection reason, do not silently fail.

## 6a. Design Review: Prior ORB Breakout Bot (`ORB_Breakout_-_v2_cs`)

The existing ORB Breakout cBot was reviewed for reusable design patterns, specifically around dynamic stop management. Findings:

| Aspect | Verdict | Action Taken |
|---|---|---|
| Dynamic stop trailing mechanism | ORB bot's design is superior — quantized R-step ratchet vs. a naive continuous per-tick recompute | Adopted directly into 3.6/5.5 |
| Per-position state tracking (`PositionState` dictionary keyed by `Position.Id`) | Good pattern, directly applicable | Adopted for this bot's state management |
| Monotonic-only stop movement guard (never loosen) | Correct and necessary | Adopted |
| Price rounding to `Symbol.TickSize` before every `ModifyPosition` call | Correct, avoids broker rejection | Adopted |
| Multi-TP partial closes (TP1–TP4), early risk reduction | Present in ORB bot, not applicable here | Not carried over — News Straddle Bot uses a single TP per 3.5, keeping the mechanism intentionally simpler since the trade only exists for one release event, not a multi-stage trend-following exit |
| Session/timezone enum (`SessionTimeZoneEnum`) | Narrower than needed (4 zones, no DST handling shown) | Not reused directly — News Straddle Bot needs 6 zones with explicit DST handling per 5.2, built fresh using `TimeZoneInfo` |

Net effect: the trailing/ratchet engine in this spec is a direct adaptation of a pattern already used and trusted in production, rather than a new untested design.

## 7. Repository & File Structure

```
/News-Straddle-Bot
  |- NewsStraddleBot.cs   # Main cBot source
  |- README.md            # Usage guide, parameter reference, changelog
  |- SPEC.md              # This document (source of truth)
  \- /backtests
      \- notes.md         # Manual backtest/forward-test log
```

## 8. Build & Testing Plan

1. Scaffold the cBot skeleton with all parameters from section 3 exposed via `[Parameter()]` attributes, grouped logically (Risk, Timing, Entry, Spread Guard, SL/TP, Dynamic Stop).
2. Implement state machine (section 4) with full logging at each transition.
3. Implement timezone conversion (5.2) and unit-test manually against known DST transition dates (e.g., US DST start/end, UK/EU DST start/end) to confirm correct UTC conversion on both sides of the transition.
4. Implement instrument auto-detection (5.3) and validate on both XAUUSD and US500/GER40 charts side by side.
5. Implement OCO emulation (5.1) — test manually by forcing both orders close to spot on a demo account during a quiet period to confirm one fill reliably cancels the other within acceptable latency.
6. Implement sizing, SL/TP, dynamic stop (5.4–5.5).
7. Demo-account forward test across at least 3 real news events (recommend starting with a mid-tier release, not NFP/FOMC, to reduce first-run risk) before committing to live capital.
8. Log review loop: after each live event, review the full log against the state machine to confirm no unexpected transitions occurred.

## 8a. Validation Reality Check (READ BEFORE TRUSTING ANY BACKTEST)

**cTrader's backtester cannot validate this strategy.** It replays tick data with static or historically-averaged spreads and does not model release-time spread blowout, slippage on stop fills, requotes, or rejected orders — precisely the costs that determine whether a news straddle is profitable. A backtest of this bot will therefore look materially better than live performance, potentially turning a losing strategy into an apparently winning one. Demo forward-tests are only slightly better (demo fills are idealized).

Consequences for the project plan:

- Use backtesting **only** to verify mechanical correctness (state machine, OCO cancellation, timing, sizing math, ratchet behavior) — never to estimate profitability or optimize buffer/SL parameters.
- The only trustworthy performance data comes from **small-size live forward tests**. Recommend minimum position size for the first 10–20 events, with the per-event log (state transitions, spread at arming, spread at fill, slippage on entry and exit) treated as the primary output of v1.
- Strategy-level honesty: the retail straddle's edge is structurally thin because brokers widen spreads and permit slippage at release precisely because this trade exists. The bot eliminates every *execution* failure mode within its control (double fills, stale orders, sizing errors, timing errors) — whether the remaining spread/slippage toll is beatable is an empirical question that v1 is designed to answer cheaply, not assume.

## 9. Explicitly Out of Scope (v1)

- Live economic calendar API integration (manual entry only — flagged as a clean future phase).
- Cross-instrument/correlation-aware risk aggregation (explicitly declined).
- Multiple concurrent news events per bot instance (one event per instance/run, by design).

## 10. Confirmations — Resolved

1. **Double-fill / tie-break policy** — resolved: `DoubleFillPolicy` parameter, default `FlattenBoth` (3.6a, 6).
2. **TP vs Dynamic Stop precedence** — resolved: TP is always a hard cap; Dynamic Stop trails underneath it and only governs the exit if price reverses before TP is hit (3.6).
3. **OnTick vs OnBar** — resolved: OnTick, using the quantized ratchet from 5.5 (adapted from the ORB bot) rather than a raw per-tick recompute.

## 11. Revision Log

- **v1.0** — Initial spec (research, parameters, state machine, OCO emulation, DST handling).
- **v1.1** — Adopted quantized-ratchet dynamic stop from prior ORB Breakout bot; resolved double-fill policy (`FlattenBoth` default), TP-as-hard-cap precedence, OnTick monitoring.
- **v1.2 (critical review pass)** — Added `TriggerSide` (`StopTriggerMethod.Opposite` default) to prevent spread-blowout double-triggering — the highest-severity gap found (5.7). Added `SlippageBufferPercent` to the sizing formula so slipped stops land near intended risk. Added `ExpectedReleaseSpread` pre-flight sanity check. Simplified timezone design to pure-UTC internals (`TimeZones.UTC` + `Server.TimeInUtc`). Added 8a: backtests cannot validate profitability for this strategy — mechanical verification only; small-size live forward testing is the real validation phase.
