# ORB Bot v2.0 — Implementation Notes (Phase 1.5)

Maps each spec item (A1–A14) from `docs/Phase1_Review_and_Spec.md` to the concrete
changes made in `ORB_Bot.cs` (derived from `ORB_Bot_Original.cs`, which is untouched).
Same namespace/class (`cAlgo.Robots.OrbBreakoutBot`), same `[Robot]` attribute, single file.

> **Reviewer note — three INTENTIONAL behavior corrections:** A1, A2 and A5 deliberately
> change what the bot does (not just how). They are called out explicitly in their sections
> below and summarised at the end.

---

## A1 — Consistent ORB range builder (INTENTIONAL behavior change)
- **New `IsBarInOrbWindow(int barIndex)`** — the single shared inclusion rule used by BOTH paths:
  a bar contributes iff it is a closed bar with `openTime >= _orbStartUtcToday` **AND**
  `closeTime <= _orbEndUtcToday` (close time derived via existing `GetBarCloseTimeUtc`).
- **`OnOrbBarClosed`** (live path) now calls `IsBarInOrbWindow` instead of the old
  "open in `[start,end)`, no close check" test. This is the behavior correction: the live path
  previously contaminated the range with post-window ticks and could diverge from backfill.
- **`TryBackfillAndMaybeLockOrb`** inner loop now also calls `IsBarInOrbWindow` (it already had the
  equivalent open/close checks) so both paths are provably identical.
- Lock condition unchanged (lock when a closed ORB bar's close time `>= _orbEndUtcToday`).
- **New `ValidateOrbWindowAlignment()`** (called at end of `OnStart`): derives the ORB bar length
  from the two most recent bars; if the configured window is shorter than one ORB bar it prints a
  hard `LogError` and calls `Stop()`; if window start/length are not aligned to the ORB TF grid it
  prints a prominent `LogWarn`.

## A2 — Post-range filter on confirmation bars (INTENTIONAL behavior change)
- **`EvaluateEntryAtConfirmBar`**: immediately after the `_orbLocked` gate, rejects any evaluation
  bar whose `OpenTimes[evalBarIndex] < _orbEndUtcToday` (applies to intrabar forming bar too).
  Additionally rejects if the earliest bar of the N-bar window
  (`evalBarIndex-(N-1)`) opens before the ORB end (open times are monotonic, so the first bar
  suffices). This kills the phantom lock-time entry from the range's high/low-making bar.
- **`LogNearMissBreakout`**: window start is advanced past any in-range bars, and it returns if the
  whole window is inside the range, so diagnostics match the new signal rule.

## A3 — Fallback sizing no longer oversizes
- **`EnterTrade`**: both manual fallback formulas had `* Symbol.LotSize` **removed**
  (`riskInAccountCcy / (estimatedRiskPips * Symbol.PipValue)` and the `volumeCap` equivalent).
- **New implied-risk sanity guard** right after `volumeRisk` normalization: recomputes
  `volumeRisk * estimatedRiskPips * Symbol.PipValue`; if it exceeds `2 × riskInAccountCcy` it logs
  `LogError` and skips the trade.

## A4 — SL attached at execution (INTENTIONAL, safety)
- **`EnterTrade`**: `effectiveTpR` is now computed **before** order submission. The market order is
  sent with a **padded pip SL/TP attached** via
  `ExecuteMarketOrder(..., attachSlPips, attachTpPips)` where
  `attachSlPips = max(estimatedRiskPips + 2, MinRiskPips)` and
  `attachTpPips = effectiveTpR * estimatedRiskPips + 2`.
- The exact ORB-anchored absolute SL/TP is then **refined** via the existing `ModifyPosition`
  ladder (`TryApplyInitialProtectionWithFallback` retained).
- **Behavior fix:** a failed *refinement* no longer closes the position — if refinement + fallback
  fail but `position.StopLoss.HasValue` (the attach-time SL), it logs a `LogWarn` and keeps the
  position. Closing now only happens if `!position.StopLoss.HasValue`.

## A5 — Post-lock replay covers all post-ORB bars (INTENTIONAL behavior change)
- **`TryPostLockConfirmReplay`** rewritten: instead of replaying the last
  `PostLockReplayConfirmBars` bars, it now scans back (bounded by `MaxBarScanBack`) to the first
  closed confirm bar with `OpenTime >= _orbEndUtcToday` and replays **all** post-ORB closed bars in
  chronological order. Anchor/delay-window semantics unchanged.
- **Default `PostLockReplayMaxDelayMinutes` raised 20 → 30.**
- `PostLockReplayConfirmBars` is now unused as a limiter (kept for settings compatibility; marked
  obsolete in a code comment). A non-default value logs a one-time `LogWarn` in `OnStart`.
- `_orbLockedUtc` (previously dead — see A13.3) is now read to log lock→replay latency.

## A6 — Chart access guarded
- **New `ChartAvailable`** property: `Chart != null && RunningMode != RunningMode.Optimization`
  (wrapped in try/catch). `DrawOrbLinesOnChart`, `DrawThresholdLinesOnChart` and `RemoveOldDrawings`
  early-return when `!ChartAvailable`.

## A7 — Errors/warnings always print
- **New `LogError(...)` / `LogWarn(...)`** (via shared `PrintWithPrefix`) that **always** `Print`
  (prefixing `ERROR:` / `WARNING:`) regardless of `EnableDebugLogging`. `Log(...)` (info) keeps the
  existing gate. Routed through them: `ORDER FAILED`, all `ERROR:` conditions, all `SAFETY:` skips,
  `ENTRY BLOCKED` explanations, trend-filter blocks, protection warnings, currency-conversion
  warnings, close failures (`LogCloseFailThrottled` now uses `LogWarn`), the ORB-not-locked warning,
  and the register-existing-position warning. No new parameters.

## A8 — Time-based (prepend-immune) bar trackers
- `_lastOrbBarIndex/_lastConfirmBarIndex/_lastTrendBarIndex` (int) replaced by
  `_lastOrbBarOpenTime/_lastConfirmBarOpenTime/_lastTrendBarOpenTime` (`DateTime`).
- **New `FindFirstUnprocessedIndex(bars, lastProcessedOpenTime, lastClosed)`** scans back from the
  last closed bar (bounded by `MaxBarScanBack = 500`) to the first bar newer than the last processed
  OpenTime. `ProcessNewOrbBars`, `ProcessNewConfirmBars`, `ProcessNewTrendBars` all rewritten to use
  it and to advance the tracker to the last closed bar's OpenTime. Immune to `LoadMoreHistory()`
  prepends. The old off-by-one guard (A13.5) is gone as a result.

## A9 — VWAP session backfill + session-date reset
- **New `EnsureVwapSessionBackfill()`** (called from the OnTick trend branch): once per session it
  resets and rebuilds the VWAP accumulators from the first trend bar of the current session date
  (bounded scan), then seeds `_lastTrendBarOpenTime` so incremental processing does not double count.
  Tracked by new `_vwapBackfilledDate`.
- **New `AccumulateVwap(int)`** extracted from `OnTrendBarClosed`.
- `OnTrendBarClosed` daily reset now keys off `GetSessionDate(openTime)` instead of raw UTC `.Date`.

## A10 — 1-second Timer drives time-based tasks
- `Timer.Start(TimeSpan.FromSeconds(1))` in `OnStart`; `Timer.Stop()` in `OnStop`.
- **New `OnTimer()`** and **new `RunTimeDrivenTasks(nowUtc)`** containing day-reset, close-time
  force-close, kill-switch logging, `EnsureOrbBuiltAndLocked`, `TryPostLockConfirmReplay`,
  `TryCatchUpEntry`. Called from both `OnTick` and `OnTimer`, dedup-guarded via
  `_lastTimeDrivenRunUtc` so the subset runs at most once per wall-clock second (no double
  execution). Tick-only work (ORB/confirm/trend bar processing, intrabar eval, position management)
  stays in `OnTick`.

## A11 — Entry Retrace Tolerance Pips
- **New parameter** `EntryRetraceTolerancePips` ("Entry Retrace Tolerance Pips", Group "Safety",
  default 0, MinValue 0). In `EnterTrade`'s `RequireEntryBeyondThreshold` check, entry passes if
  `expectedEntry >= threshold - tol` (long) / `<= threshold + tol` (short), `tol =
  EntryRetraceTolerancePips * Symbol.PipSize`. Skips logged via `LogWarn` with both prices.

## A12 — Block Same-Bar Re-Entry
- **New parameter** `BlockSameBarReEntry` ("Block Same-Bar Re-Entry", Group "Trades Per Day",
  default true). New state `_lastEntryConfirmBarOpenTime` / `_pendingEntryConfirmBarOpenTime`
  (reset in `ResetForDate`). `EvaluateEntryAtConfirmBar` skips (intrabar + closed) when the current
  eval bar's open time equals the last entry's bar time. The pending bar time is set before each
  `EnterTrade` call (in both the normal and catch-up paths) and committed to
  `_lastEntryConfirmBarOpenTime` only on a successful entry.

## A13 — Housekeeping
1. `_lastCloseAttemptUtcByPosId` field, its init and its removal call deleted.
2. `AlmostEqual` deleted.
3. `_orbLockedUtc` now read in the post-lock replay log line (lock→replay latency).
4. **New `PassesTrendFilter(TradeType direction, string context)`** extracted; both
   `EvaluateEntryAtConfirmBar` and `TryCatchUpEntry` now call it instead of the duplicated block.
5. Off-by-one ORB guard removed (superseded by A8 time-based tracking).
6. Partial-close failure log in `ExecutePartialClose` now routed through `LogCloseFailThrottled`
   (which itself now prints via `LogWarn`).
7. No `[Parameter]` identifiers renamed; the misleading `ClosePositionsAtKillSwitch` identifier is
   retained (comment only).

## A14 — Unit-semantics documentation
- A comment block at the top of the PARAMETERS region documents which parameters use the Point Unit
  Mode unit (`_pointSize`: ORB range + Entry Offset) vs `Symbol.PipSize` always (Safety pips,
  Execution-Risk pips, and all R/risk math). No behavior change.

---

## Parameter changes summary
- Changed default: `PostLockReplayMaxDelayMinutes` 20 → 30 (A5). No identifier/display/group changes.
- New: `Entry Retrace Tolerance Pips` (Safety, default 0, MinValue 0) — A11.
- New: `Block Same-Bar Re-Entry` (Trades Per Day, default true) — A12.
- All other existing `[Parameter]` identifiers, display names, groups and defaults preserved.

## Acceptance checklist (self-verified in the output file)
- [x] One shared ORB range-builder; live == backfill (`IsBarInOrbWindow`); startup hard-stop if
      window < 1 ORB bar; alignment warning (`ValidateOrbWindowAlignment`).
- [x] Confirmation bars opening before ORB end cannot produce/contribute to a signal (A2 gates in
      `EvaluateEntryAtConfirmBar` + `LogNearMissBreakout`).
- [x] Both fallback sizing formulas corrected; implied-risk sanity guard present.
- [x] Market orders carry attached padded SL at execution; refinement to absolute levels retained;
      position not closed when only refinement fails.
- [x] Post-lock replay covers all post-ORB closed bars within the delay window.
- [x] All `Chart.` access guarded (`ChartAvailable`, incl. Optimization).
- [x] Errors/warnings always print (`LogError`/`LogWarn`).
- [x] Bar trackers are time-based, bounded scans (`MaxBarScanBack`).
- [x] VWAP backfilled from session start; session-date keyed reset.
- [x] 1-second Timer drives time-based tasks; dedup guard prevents double execution.
- [x] New params present with correct groups/defaults; no renamed identifiers.
- [x] Dead code removed (A13.1–3); trend gate deduplicated (A13.4).
- [x] Unit-semantics comment block present (A14).

## Environment caveat
There is no cTrader/.NET compiler in this environment. The file was verified structurally
(balanced braces 829/829, balanced code parentheses, every new symbol defined, no duplicate members,
no dangling references to removed fields) and every new API call matches a pattern already present in
the original file (`ExecuteMarketOrder` pip overload, `ModifyPosition`, `Timer.Start/Stop`, `OnTimer`,
`RunningMode`, `Chart.*`). It has NOT been compiled.

---

## Phase 1.5 review fixes (2026-07-18)

Reviewer (Fable 5) verified all 14 A-items against the full diff; 13 passed as
implemented. Two adjustments were applied (implemented by Opus; finalized/committed by
the reviewer after the implementer session hit a usage limit mid-task):

1. **ValidateOrbWindowAlignment gap robustness (defect fix).** The ORB bar length was
   derived from the last two bars' open-time delta, which spans the market closure if the
   bot starts right after a weekend/session gap (~49h) and falsely triggered the
   "window shorter than one ORB bar" hard-stop on valid configurations. Now derived as
   the MINIMUM positive delta over the last up-to-10 consecutive bar pairs (gap-immune).
2. **SL-only attach when no TP target (edge-case hardening).** With `effectiveTpR <= 0`,
   the attach-at-entry logic previously fell back to a ~2-pip TP, which would close the
   trade in profit noise almost immediately. Now: `takeProfitPips = null` at
   `ExecuteMarketOrder`, and the initial refinement also passes a null TP
   (`refineTpPrice`), leaving the position SL-protected with no degenerate target.

Post-fix structural verification: braces 831/831, code-only parens 1132/1132.
