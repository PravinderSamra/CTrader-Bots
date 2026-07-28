# ORB Bot — Phase 1 Deep Code Review & Implementation Spec

**Reviewer:** Fable 5 (deep analysis) · **Implementer:** Opus (per this spec) · **Date:** 2026-07-18
**Input:** `ORB_Bot_Original.cs` (3,493 lines, "ORB lock fixed" version from ChatGPT)
**Deliverable:** `ORB_Bot.cs` in this folder — the original with the changes below applied.

**Historical symptoms reported by the owner:** (a) ORB sometimes failed to lock; (b) bot
sometimes failed to enter when price broke out and met the configured criteria.

The current version already contains substantial mitigation machinery (backfill, self-heal,
post-lock replay, trade-count rehydration). The findings below are the defects that
**remain** — several directly produce the two historical symptoms, plus one latent sizing
bug that can massively oversize a position.

Line numbers refer to `ORB_Bot_Original.cs`.

---

## PART A — FINDINGS

### A1. CRITICAL — ORB range built inconsistently: live path includes bars that close AFTER the range end; backfill excludes them
- **Where:** live: `OnOrbBarClosed` (~1259–1281) includes any closed bar whose **open** is in
  `[start, end)` — with no check on its close time. Backfill: `TryBackfillAndMaybeLockOrb`
  (~1012–1029) additionally requires `barClose <= _orbEndUtcToday`.
- **Why it matters:** if the range window is not aligned to the ORB timeframe (e.g. window
  ends 08:12 on M5 bars, or a coarse TF like H1 is selected with a 15-min window), the live
  path **contaminates the range with post-window price action** (a bar opening 08:10 and
  closing 08:15 contributes ticks from 08:12–08:15), while the backfill path excludes that
  bar entirely. Consequences:
  - Live ORB ≠ restart/backfill ORB → **different high/low on the same day depending on
    whether the bot restarted** — exactly the kind of inconsistency the owner describes.
  - With a coarse TF (H1 + 15-min window): live locks a wildly wrong range from one H1
    bar; backfill can find **zero** qualifying bars → **never locks** + endless self-heal
    warnings — the historical "won't lock" symptom.
- **Fix (required):**
  1. Extract a single shared range-builder used by BOTH live and backfill paths with one
     inclusion rule: a bar contributes iff `openTime >= _orbStartUtcToday` **AND**
     `closeTime <= _orbEndUtcToday` (closed bars only).
  2. In the live path this means `OnOrbBarClosed` must check the bar's close time before
     merging its high/low.
  3. Lock condition unchanged: lock when any closed ORB bar's close time `>= _orbEndUtcToday`
     (both paths already do this).
  4. **Startup validation (new):** compute the ORB TF length (from the first two bars or
     `OrbBarsTimeFrame`); if the configured window is **shorter than one ORB bar**, print a
     hard ERROR and `Stop()` (a range that can never contain a full bar can never lock).
     If the window start/end are **not aligned** to the ORB TF grid, print a prominent
     WARNING explaining that bars overlapping the boundary are excluded.

### A2. CRITICAL — No "post-range" filter on confirmation bars: bars from inside the range window can trigger entries
- **Where:** `EvaluateEntryAtConfirmBar` (~1476+) — no check that the evaluated bar is after
  the range window. On the tick where the ORB locks, `ProcessNewConfirmBars` may evaluate
  the final in-range confirm bar (its close IS the range end).
- **Why it matters:** with `EntryOffsetPips = 0`, the range bar that *made* the ORB high
  closes at/near the high → `CloseBeyond` (close >= orbHigh + 0) fires → **phantom
  "breakout" entry at the moment of lock with no actual breakout**. `WickBeyond` is worse
  (high >= orbHigh always true for the high-maker bar). With the default offset 10 this was
  masked; at tighter offsets it produces inexplicable instant entries.
- **Fix (required):** in `EvaluateEntryAtConfirmBar`, immediately after the `_orbLocked`
  gate, reject any evaluation bar whose **open time < `_orbEndUtcToday`** (for intrabar
  evaluation, the forming bar's open time must also satisfy this). Apply the same rule
  inside the multi-bar windows: bars inside the range window must not count toward the
  N-bar confirmation window; if the window would include them, there is no signal.
  Also apply to `LogNearMissBreakout` windows for accurate diagnostics.

### A3. CRITICAL (latent) — Fallback volume formula oversizes by `LotSize`×
- **Where:** `EnterTrade` fallback when `Symbol.VolumeForFixedRisk` throws (~2329):
  `volumeRisk = riskInAccountCcy * Symbol.LotSize / (estimatedRiskPips * Symbol.PipValue);`
- **Why it matters:** `Symbol.PipValue` is the pip value **per one unit of volume**. The
  correct manual formula is `risk / (riskPips * PipValue)`. Multiplying by `LotSize`
  (100,000 on FX) requests a volume up to 100,000× too large. `NormalizeVolumeInUnits`
  clamps into `[min,max]` → result: **max-volume position** (margin clamp may then reduce
  it to "50% of free margin" — still enormously oversized vs the intended fixed risk).
  Same bug in the `volumeCap` fallback (~2349).
- **Fix (required):** remove `* Symbol.LotSize` from both fallback formulas. Additionally,
  after computing `volumeRisk` by any path, add a sanity guard: recompute the implied risk
  (`volume * riskPips * PipValue`) and if it exceeds `2 × riskInAccountCcy`, log ERROR and
  skip the trade (belt-and-braces against future API surprises).

### A4. CRITICAL — Entry is placed with **no stop loss attached** (naked window)
- **Where:** `ExecuteMarketOrder(tradeType, SymbolName, volumeInUnits, label, null, null)`
  (~2434), protection applied afterwards via `ModifyPosition`.
- **Why it matters:** between fill and successful modify, the position is unprotected. If
  the bot disconnects/crashes in that window, or all protection attempts fail *and* the
  close also fails, a naked position rides. The existing "close on protection failure" path
  itself churns spread on every failed attempt.
- **Fix (required):** attach a **conservative pip-distance SL/TP directly in
  `ExecuteMarketOrder`** using the estimated entry: SL pips = `estimatedRiskPips` padded by
  a small buffer (e.g. +2 pips, and never less than `MinRiskPips`); TP pips =
  `effectiveTpR × estimatedRiskPips` padded likewise. Then immediately refine to the exact
  ORB-anchored **absolute** prices via the existing `ModifyPosition` logic (keep the
  existing fallback ladder). If refinement fails, the position still has the conservative
  protective stop — do **not** close it in that case; log WARNING and keep the padded SL.
  The "close position" escape remains only for the case where even the attached-at-entry
  SL is missing (`!position.StopLoss.HasValue`).

### A5. HIGH — Missed entries when the ORB locks late: replay window too narrow and closed bars are consumed unevaluated
- **Where:** `ProcessNewConfirmBars` advances `_lastConfirmBarIndex` even when
  `EvaluateEntryAtConfirmBar` returns instantly because `!_orbLocked` (~1459–1474).
  The compensating `TryPostLockConfirmReplay` (~1165) replays only
  `PostLockReplayConfirmBars` (default **1**) bars and only within
  `PostLockReplayMaxDelayMinutes` (default 20) of the anchor.
- **Why it matters (historical symptom b):** restart at 08:50 after a valid 08:20 breakout
  → replay skipped (35 min > 20) → breakout never evaluated → **no trade despite valid
  signal**. Or: breakout bar closed 2 bars before lock; replay of the single most recent
  bar fails `CloseBeyond` (price pulled back) → missed, even though an N=1 evaluation of
  the actual breakout bar would have entered (and `RequireEntryBeyondThreshold` would
  govern safety).
- **Fix (required):** rewrite the replay to evaluate **all closed confirmation bars whose
  open time ≥ `_orbEndUtcToday`**, in chronological order, capped by the existing
  `PostLockReplayMaxDelayMinutes` anchor logic (unchanged semantics: if now is beyond the
  window, skip and log). Remove the `PostLockReplayConfirmBars` count as the limiter of
  *which* bars get replayed (keep the parameter for backwards compatibility of saved
  settings, but it becomes unused — mark `[Obsolete-style comment]` in code and log once
  if a non-default value is set). Raise the default `PostLockReplayMaxDelayMinutes` from
  20 → 30.

### A6. HIGH — Chart API calls crash during optimization
- **Where:** `RemoveOldDrawings` called unconditionally from `ResetForDate` (~886);
  `DrawOrbLinesOnChart` / `DrawThresholdLinesOnChart` (~3431–3470).
- **Why it matters:** in cTrader **optimization** runs, `Chart` is null → NRE → the run
  aborts mid-optimization; results look random/flaky.
- **Fix (required):** add a single guard helper `bool ChartAvailable => Chart != null;`
  and early-return from all three drawing methods (and any other `Chart.` access) when
  false or when `RunningMode == RunningMode.Optimization`.

### A7. HIGH — Errors are silenced when `EnableDebugLogging = false`
- **Where:** `Log()` (~3476) gates ALL messages, including `ORDER FAILED`, protection
  failures, and safety skips.
- **Why it matters:** with debug logging off, the bot fails silently — the owner sees
  "it just didn't take the trade" with no trace. This directly feeds the "flaky" perception.
- **Fix (required):** introduce `LogError(...)` and `LogWarn(...)` that **always** `Print`
  (prefixing `ERROR:`/`WARNING:`), and route every failure/blocked-entry/safety-skip
  message through them. `Log(...)` (info) keeps the existing gate. No new parameters.

### A8. MEDIUM — Bar-index trackers break if `LoadMoreHistory()` prepends bars
- **Where:** `_lastOrbBarIndex/_lastConfirmBarIndex/_lastTrendBarIndex` are raw indices
  (~476–478, init ~593); `EnsureOrbHistoryCoverageForToday` calls `_orbBars.LoadMoreHistory()`
  (~1064) which **prepends** bars and shifts every index.
- **Why it matters:** after a prepend, `ProcessNewOrbBars` re-iterates a large historical
  index range (wasted work; benign for ORB because of time filtering, but fragile), and the
  pattern is a trap if ever applied to confirm bars (it would re-evaluate historical bars
  as fresh entries).
- **Fix (required):** convert all three trackers from raw index to **last-processed bar
  OpenTime** (`DateTime`). Each `ProcessNew*` scans from the end back to the first bar with
  `OpenTime > lastProcessedOpenTime` and processes forward from there. This is immune to
  prepends. (Keep the loops bounded: never scan more than e.g. 500 bars back.)

### A9. MEDIUM — VWAP is wrong after a mid-session start/restart (trend filter)
- **Where:** VWAP accumulates only from bars processed after start (~1306–1336); daily reset
  keyed to **UTC** bar date, not the session date; `GetTrendInfo` then treats the partial
  VWAP as valid as soon as one new bar closes.
- **Why it matters:** with the trend filter enabled, a restart mid-session silently produces
  a wrong VWAP → wrong trend bias → blocked or mis-allowed entries with no indication.
- **Fix (required):** on first use each session (and on start), **backfill** the VWAP
  accumulators from the first trend bar of the current session date (loop closed trend bars
  whose open time ≥ session start-of-day in the session timezone). Key the daily VWAP reset
  to the same session-date logic used elsewhere (`GetSessionDate` of the bar open time),
  not raw UTC date.

### A10. MEDIUM — Tick-only state machine stalls in quiet markets
- **Where:** everything runs from `OnTick` only.
- **Why it matters:** force-close at Close-Positions time, self-heal, and catch-up all wait
  for the next tick; on a quiet/holiday session these can fire minutes late (or not at all
  until the next tick).
- **Fix (required):** `Timer.Start(TimeSpan.FromSeconds(1))` in `OnStart`; in `OnTimer`,
  run the time-driven subset: day-reset check, close-time force close, kill-switch logging,
  `EnsureOrbBuiltAndLocked`, `TryPostLockConfirmReplay`, `TryCatchUpEntry`. (This repo's
  News-Straddle bot uses the same pattern.) Guard so the same work isn't done twice in the
  same second by tick and timer (e.g. shared `RunTimeDrivenTasks(nowUtc)` with a
  last-run timestamp).

### A11. LOW — `RequireEntryBeyondThreshold` silently eats valid signals on small retraces
- **Where:** ~2247–2268.
- **Why it matters:** the breakout bar closes beyond, but by evaluation time price retraced
  1–2 pips inside → skip. This is *by design* (and a good safety), but it is a common cause
  of "it met my criteria and didn't enter". 
- **Fix (required):** add parameter **"Entry Retrace Tolerance Pips"** (Group "Safety",
  default **0** = exactly current behaviour). Entry passes if
  `expectedEntry >= threshold − tolerance` (long) / `<= threshold + tolerance` (short).
  Always log the skip through `LogWarn` including both prices (already mostly done).

### A12. LOW — Same-forming-bar instant re-entry (intrabar mode)
- **Where:** intrabar evaluation runs every tick (~702–707); after an SL exit with
  `MaxTradesPerDay > 1` + `AfterStopLossOnly`, the same forming bar can re-trigger
  immediately in the same second.
- **Fix (required):** record the confirm-bar open time of the last entry; add parameter
  **"Block Same-Bar Re-Entry"** (Group "Trades Per Day", default **true**): if the current
  evaluation bar's open time equals the last entry's bar time, skip (both intrabar and
  closed-bar paths).

### A13. LOW — Housekeeping
1. `_lastCloseAttemptUtcByPosId` is written nowhere (only removed) — delete the field.
2. `AlmostEqual` unused — delete.
3. `_orbLockedUtc` set but never read — use it in the replay log line (lock→replay latency)
   or delete.
4. The trend-filter gate is duplicated verbatim in `EvaluateEntryAtConfirmBar` and
   `TryCatchUpEntry` (~1642–1735 and ~1910–2004) — extract
   `bool PassesTrendFilter(TradeType direction, string context)` and call from both.
5. `ProcessNewOrbBars` guard `if (currentCount <= _lastOrbBarIndex)` is off-by-one
   (harmless) — goes away with A8's time-based tracking.
6. Partial-close failure log (~2792) is unthrottled → wrap with the existing throttled
   logger.
7. Do **NOT** rename any `[Parameter]` property identifiers (saved user settings bind to
   them). The misleading `ClosePositionsAtKillSwitch` identifier stays; improve its code
   comment only.

### A14. Documentation of unit semantics (no behavior change)
`Max/Min ORB Range`, `Entry Offset` use the **Point Unit Mode** (`_pointSize` = pip or
tick), while `MinRiskPips`, `MaxSpreadPips`, `Fallback SL`, risk math and R-multiples use
`Symbol.PipSize` always. Add a comment block at the top of the parameters region making
this explicit, per group. (On index CFDs where pip=1 point this is invisible; on FX with
tick mode it bites.)

---

## PART B — IMPLEMENTATION INSTRUCTIONS (for Opus)

**Deliverable:** `ORB Projects/ORB Bot/ORB_Bot.cs` — full file based on
`ORB_Bot_Original.cs` with items **A1–A14** applied. Also write
`ORB Projects/ORB Bot/IMPLEMENTATION_NOTES.md` mapping each spec item → what changed
(method names + brief description), including the three intentional behavior corrections
(A1, A2, A5) called out for the Phase 1.5 reviewer.

**Rules:**
1. Preserve every existing `[Parameter]` property identifier, display name, group and
   default (except `PostLockReplayMaxDelayMinutes` default 20 → 30 per A5). New parameters
   only as specified (A11, A12).
2. Class stays a single compilable file, same namespace/class name (`OrbBreakoutBot`),
   same `[Robot]` attribute. Keep the existing logging style and comment tone.
3. No cTrader compiler exists in this environment: keep edits conservative and
   syntactically airtight; match existing API call patterns already present in the file.
   After writing, re-read the full output file end-to-end checking brace balance and that
   every new symbol is defined.
4. Version header: bump the top comment block to
   `ORB Breakout cBot — v2.0 (Consistency & Safety Overhaul)` with a short changelog list
   referencing A-item numbers.
5. Commit to branch `claude/us30-london-range-breakout-lu3awm` and push
   (`git push -u origin <branch>`, retry up to 4 times with 2s/4s/8s/16s backoff on network
   failure). Do NOT open a PR. Commit message summarises the A-items.

**Acceptance criteria (Phase 1.5 review will verify):**
- [ ] One shared ORB range-builder; live == backfill inclusion rule (open ≥ start AND
      close ≤ end); startup hard-stop if window < 1 ORB bar; alignment warning.
- [ ] Confirmation bars opening before ORB end can never produce or contribute to a signal.
- [ ] Both fallback sizing formulas corrected; implied-risk sanity guard present.
- [ ] Market orders always carry an attached SL (padded) at execution; refinement to
      absolute levels retained; position no longer closed when only the refinement fails.
- [ ] Post-lock replay covers all post-ORB closed bars within the delay window.
- [ ] All `Chart.` access guarded for null/optimization.
- [ ] Errors/warnings always print regardless of `EnableDebugLogging`.
- [ ] Bar trackers are time-based (prepend-immune), bounded scans.
- [ ] VWAP backfilled from session start; session-date keyed reset.
- [ ] 1-second Timer drives time-based tasks; no double-execution with OnTick.
- [ ] New params: `Entry Retrace Tolerance Pips` (default 0), `Block Same-Bar Re-Entry`
      (default true). No renamed identifiers.
- [ ] Dead code removed (A13.1–3), trend gate deduplicated (A13.4).
- [ ] Unit-semantics comment block present (A14).

---

## PART C — Phase 2 preview (design confirmed, full spec after Phase 1.5)

The owner's premarket-range + volume strategy (from the `US30 London Range Breakout`
research) maps onto this bot almost entirely via existing parameters:
- Range marking: `Range Start/End` + `SessionTimeZone = AmericaNewYork` (e.g. 02:00→09:30 ET
  US30: 08:00→09:30 ET), `UseFixedUtcTimes = false`.
- Skip first 30 min: `Trading Start Time = 10:00` ET.
- One trade/day, first qualifying breakout: `MaxTradesPerDay = 1`, `CloseBeyond`, offset 0.
- R-target exits: `TakeProfitR` (research: NAS100 3.5R @ 40pt, US30 3.0R @ 75pt).

**Confirmed missing pieces for Phase 2** (to be built as a second bot variant):
1. **Volume filter** — the core addition: breakout candle tick volume ≥ X× trailing-N
   average of confirm-TF bars (research default ≥1.2×, trailing-20, excluding current bar),
   with optional z-score mode. `Bars.TickVolumes` provides the data.
2. **Fixed-point stop mode** — research used fixed point stops (40/75 pt), but this bot
   only supports `StopLossOrbPercent`. Add `StopMode = OrbPercent | FixedPoints`.
3. Instrument preset documentation (US30/NAS100 configs from the research, incl. "no
   trailing / static stop" default per the stop-loss management study).
