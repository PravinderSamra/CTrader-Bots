# News Straddle Bot

A cTrader cBot that automates the pre-news volatility straddle: two pending stop orders placed symmetrically around spot shortly before a scheduled release, with the untriggered side cancelled the instant the other fills. Built from `SPEC.md` (the original design document, transcribed verbatim from the supplied PDF).

**This is a risk-management machine first, an entry mechanism second.** Read `SPEC.md` section 8a before trusting any backtest — cTrader's backtester does not model release-time spread blowout or slippage, so it will make this strategy look better than it will trade live. The only trustworthy validation is small-size live/demo forward testing across real news events.

## Files

- `NewsStraddleBot.cs` — the cBot source. Paste the whole file into a new cBot in cTrader Automate.
- `SPEC.md` — the original design spec (source of truth for *intent*).
- `backtests/notes.md` — template for logging manual backtest/forward-test runs.

## Quick start

1. Add `NewsStraddleBot.cs` to cTrader Automate (`Automate` tab → `Add` → `New cBot` → paste source → `Build`).
2. Drag it onto the chart of the instrument you want to trade (tested against XAUUSD and US500/GER40).
3. Set `News Date/Time` and `News Time Zone` to the release you're targeting (e.g. `2026-08-01 08:30:00` in `NewYork` for a US NFP release).
4. Review every parameter group below before your first live/demo run — the defaults are deliberately conservative but `TriggerSide` and `SpreadGuardMode` in particular change the bot's behavior materially.
5. Start the bot. It sits in `IDLE` doing nothing until `EntryLeadMinutes` before your configured news time, then arms, places both legs, and manages the outcome per the state machine in `SPEC.md` section 4.
6. After the event, read the log (`[NewsStraddle] ...` lines) top to bottom — it prints every state transition, every guard decision, and every order/position event. This log is the actual v1 deliverable per the spec's validation philosophy, not the P&L of any one event.
7. To arm the next event, just change `News Date/Time` (and `News Time Zone` if needed) on the running bot — no restart required. The bot re-arms automatically once the new time is in the future and detects it hasn't already processed it.

## Parameter reference

Parameters are grouped in the cTrader UI exactly as in `SPEC.md` section 3: **Risk & Sizing**, **News Timing**, **Entry Structure**, **Spread Guard**, **Stop Loss / Take Profit**, **Dynamic Stop**, **Double-Fill Handling**, **Diagnostics / Safety**. Names, defaults and semantics match the spec 1:1 — see SPEC.md for the full table. A few worth calling out:

- **`TriggerSide` (default `OppositeSide`)** — the single most important setting in the bot (SPEC.md 5.7). Leave it on `OppositeSide` unless you are deliberately A/B testing; `Standard` is vulnerable to both legs triggering from spread widening alone during the release, with no real price movement.
- **`SpreadGuardMode` (default `ProceedAnyway`)** — controls what happens if spread is abnormal or inside the broker's minimum distance at arming time. `ProceedAnyway` just warns; `AutoWidenBuffer` scales the buffer up; `SkipTrade` aborts the cycle entirely rather than risk a broker rejection or a spread-triggered double fill.
- **`DoubleFillPolicy` (default `FlattenBoth`)** — governs the rare case where the OCO cancel race is lost and both legs fill. `FlattenBoth` treats it as an anomaly and closes both at market; `KeepBetterPriced`/`KeepFirstFilled` are available if you want to test keeping a side.
- **`MaxLotCap` (default 0/off)** — a hard ceiling on computed volume, independent of the risk calc, as a safety rail against a mis-set stop producing an oversized position.

## Implementation notes / deviations from the literal spec text

These are deliberate engineering choices made while translating the spec into working code, verified against the live cTrader Automate API reference (not just training-data recall) before implementation:

- **SL/TP/expiry are attached natively at order placement**, not applied after fill. `PlaceStopOrderAsync`/`PlaceStopLimitOrderAsync` both accept `stopLoss`, `takeProfit` (absolute prices via `ProtectionType.Absolute`) and `expiration` directly, so the resulting position is protected atomically the instant it opens — there is no window where a filled leg is naked. The order's native `expiration` (set to `NewsDateTime + OrderTimeoutMinutes`) is what drives the `TIMED_OUT` transition, via the `PendingOrders.Cancelled` event with `Reason = Expired`, rather than a separately-polled timeout.
- **Minimum broker stop distance** is read from `Symbol.MinStopLossDistance` / `Symbol.MinDistanceType` (the real cAlgo API surface) rather than the `Symbol.MinPipDistance` name mentioned in the spec prose, which doesn't exist in the current API. Folded into the same pre-flight guard as the spread check, both gated by `SpreadGuardMode`.
- **Session/weekend validation** uses `Symbol.MarketHours.IsOpened(utcTime)` — a non-blocking warning only, per the spec's "warn in log if not."
- **Spread baseline window** is a fixed 30 minutes (matching the spec's own "e.g., last 30 mins" wording) rather than an exposed parameter, since the spec doesn't list it as one.
- **A rare async race is explicitly handled**: because the two legs are placed via independent async calls, a fill confirmation for one leg can theoretically arrive before the *other* leg's own placement confirmation. The bot flags this case and cancels the sibling the instant its placement confirms, instead of assuming the sibling reference is always populated by the time a fill arrives.
- **Re-arming for the next event does not require a bot restart.** The armed news time is tracked separately from the raw `NewsDateTime` parameter, so editing `NewsDateTime`/`NewsTimeZone` on a running bot (cTrader supports live parameter edits) is picked up on the next 1-second timer tick once the bot is back in `IDLE`.

## Testing plan (per SPEC.md section 8)

1. **Mechanical verification only** in the cTrader backtester: confirm the state machine transitions correctly, the OCO cancel fires and lands, sizing math produces sane volumes, and the dynamic-stop ratchet only ever tightens. Do **not** use backtest P&L to judge the strategy.
2. **DST sanity check**: run with `NewsDateTime` values that straddle a US/UK/EU DST transition and confirm the logged UTC arm/news times shift by exactly one hour across the boundary.
3. **Instrument auto-detection**: verify on both XAUUSD (pip-based) and US500/GER40 (point-based) that `BufferDistance`/`StopLossDistance` produce sensible price distances (check the log's `ORDERS SUBMITTED` line).
4. **OCO race test**: on a demo account during a quiet period, manually move price toward one of the pending legs and confirm the sibling is cancelled promptly, with the fill/cancel sequence visible in the log.
5. **Live forward test**: start with a mid-tier release (not NFP/FOMC) at minimum position size, per the spec's explicit recommendation. Treat the per-event log — not the trade P&L — as the primary v1 output for the first 10–20 events.

## Known limitations (v1, matching SPEC.md section 9)

- No live economic calendar integration — `NewsDateTime` is entered manually per run.
- One event per bot instance/run; run multiple chart instances for multiple simultaneous events.
- No cross-instrument or correlation-aware risk aggregation.
