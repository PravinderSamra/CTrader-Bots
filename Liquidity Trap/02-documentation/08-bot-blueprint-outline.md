# 08 — Bot Blueprint Outline (Rules-Based Algo for the Liquidity Trap Strategy)

High-level design outline — **not code** — for turning the rules in files 01–04 into a cTrader (cAlgo/C#) bot. Every design element cites the transcript rule it implements. Items marked **[DECIDE]** need the user's judgment before implementation; they are collected in §J. Items marked **[PARAM]** are tunable numbers the sources never quantify (most are also open visuals — see file 07 §A).

Ground rule from the sources themselves: the author warns against template-matching the diagrams as a pattern (V1 [12:06]; V2 [29:29]; V3 [7:35]). A faithful bot therefore encodes the *liquidity bookkeeping* (which levels hold orders) rather than a candlestick-shape detector — the shape emerges from the bookkeeping.

---

## A. Scope and trading direction

- Implements the full long/short setup of file 03: preconditions (arming) → sweep trigger → structural stop → pool target → management. Bearish is the exact inversion (V2 [22:44]: "this exact model right here would literally just be inverted").
- v1 recommendation: single instrument, single timeframe-pair, no scale-ins, no discretionary overlays. Scale-ins (V1 [89:36]–[92:05]) and timeframe-close confluence (V1 [86:59]) are V1-only discretionary layers — defer to v2+ (file 05 §3 classifies them as non-load-bearing).

## B. Market data and timeframe requirements

1. **Two timeframe roles**, per the fractal deployment (V1 [11:32]; V2 [23:01]; V3 [15:11]):
   - **HTF ("direction")** — supplies the target pool and the bias. Candidates: 4H/1H (V3's entire walkthrough; CFD swing per V2 [24:05]) or 30m/15m (index intraday, V1 [41:28], [63:28]).
   - **LTF ("entry")** — supplies the sweep trigger and the refined LB/stop. Candidates: 5m ("do-it-all", V1 [42:40]) and 1m (V1 [66:37]; V2 [36:55]), or 1H/15m under a 4H HTF (V3 [8:41]).
2. **Bar data:** OHLC trendbars for both roles (cTrader `MarketData.GetBars`); the logic is swing/level-based and needs no volume or DOM. Level-2 data is explicitly *not* part of the system (V1 [55:08] is a host aside).
3. **Tick or 1m feed for trigger precision:** entries fire "as soon as" the level trades through (V2 [14:11]) — intra-bar, not on bar close. Either subscribe to ticks or accept 1m-close granularity **[DECIDE J6]**.
4. **Clock/session data:** exchange time normalized to New York (stock open 9:30 NY marked on every intraday chart, V1 [42:40]); Asia-session window boundaries if session liquidity is used (V1 [43:25]).
5. **News calendar feed** (high-impact/red-folder events) for the news blackout (V1 [67:13]) — cTrader has no built-in calendar API, so this needs an external source or manual schedule **[DECIDE J8]**.
6. **History depth:** enough HTF bars to hold multi-week pools ("maybe it's the next day or even the next week", V1 [25:49]; V3's weekly pool stood for months, V3 [2:27]).

## C. Core data model: the level registry

The heart of the bot. Every swing point becomes a `Level` object with a state machine — this implements file 01 §5, the load-bearing discrimination.

**Swing detection [PARAM]:** fractal high/low definition (e.g., N-bar pivot) per timeframe. The sources never define a swing numerically; they mark visually.

**Level states:**

| State | Meaning | Transition rule | Source |
|---|---|---|---|
| `Candidate` | Fresh swing point | on pivot confirmation | — |
| `Confirmed` (has liquidity) | Later swing approached it, respected it (did not trade through), and moved away | approach within tolerance → no violation → displacement away ≥ threshold | V1 [13:13]; V2 [5:24]; V3 [8:05] |
| `EqualsCluster` | ≥2 candidate/confirmed levels within tolerance band → treated as one pool at the extreme-most price | clustering pass | V1 [41:28]; V3 [0:43] |
| `Swept` | Price traded through it | trade-through detection (see §E) | all |
| `LiquidityBlock` | Swing that *itself* swept a level and has not since been respected → holds NO liquidity; valid stop anchor / entry zone | on sweep: mark the sweep's extreme as LB | V1 [28:44]; V2 [51:49], [67:41]; V3 [2:27] |
| `Reconfirmed` | An LB later respected + moved away → re-enters `Confirmed` | same respect test | V1 [45:24]–[46:01], [76:22] |

**Respect-test parameters [PARAM, file 07 §A1–A4]:** approach tolerance (touch vs proximity band), wick handling, move-away displacement threshold, equal-level tolerance, line-vs-zone height. These four numbers ARE the strategy's identification layer; get them from the Video3 screenshots and backtest sensitivity runs before trusting any of the rest.

**Bookkeeping invariants:**
- Multiple respects increment a strength counter (V2 [67:20]; V3 [13:29]) — usable as a quality score.
- Swept levels are removed from the target set but their sweep-extreme becomes an LB (V1 [43:25]–[44:44]).
- Unswept confirmed pools persist indefinitely as future targets (V1 [25:49]).
- Classify pools `Internal` (inside current range) vs `External` (range extremes): entries come off internal sweeps, targets are external (V1 [27:37]–[28:44]).

## D. `IdentifyLiquidityPool()` — what it must compute

Runs on each closed bar of both timeframes. Outputs feed §E–§G.

1. Update swing pivots; run the respect test against all left-hand levels within lookback (V1 [13:13]).
2. Update equal-highs/lows clusters (V1 [41:28]).
3. Detect sweeps since last bar → flip swept levels, mint/refresh LBs (V2 [51:49]).
4. Re-run respect test on LBs → promote to `Reconfirmed` where applicable (V1 [76:22]).
5. Maintain the **target set**: confirmed, unswept pools, each with side (above/below), strength, timeframe, and distance.
6. Compute **bias/draw**: nearest *logical* untaken pool (V3 [3:06]) with the priority heuristics of file 02 §C step 7 — pool with nothing beyond it ranks up (V1 [58:09]); direction of recent momentum ranks up (V1 [58:39]); side just cleared by a large move ranks down (V3 [3:06]).
7. Detect **liquidity void**: if no confirmed pool exists in either direction on the HTF → bot stands down entirely (V1 [14:32]: "I don't see any other liquidity. So why would I be trading?"; V2 [54:11]).

## E. Sweep definition (one precise event for many words)

The transcripts use sweep/spike/stab/run/grab/take interchangeably (glossary §2). The bot needs a single definition **[DECIDE J7]**, candidates:
- **(a) Touch-through:** any trade at price beyond the level (matches "as soon as the low gets stabbed", V2 [39:09]; V1's tick-level market execution [46:33]).
- **(b) Trade-through by X ticks:** adds noise filter; X is a new [PARAM].
- **(c) Wick-through with close-back:** closest to "false push" recognition (V1 [21:32]) but delays entry to bar close — the sources explicitly do NOT wait for closes on the base entry (candle-close confirmation is only for *adds*, V1 [86:15]).
Recommendation: (a) for parity with the stated rule, with (b) as a spread/noise guard on CFD.

## F. `DetectSweepAndReversalConfirmation()` — the arming + trigger state machine

Implements file 03 §1–2 as an explicit per-direction state machine (long case shown; shorts mirrored):

**State 0 → 1. Left-side taken (directional validation).** An old low (left-hand-side level) gets swept while a confirmed pool remains overhead (V2 [3:58], [27:48], [55:22]; V1 [24:29] lockout). This *activates* the bullish idea and simultaneously enforces the **bias lockout**: after any high is taken, longs are forbidden until the armed low-side pool is swept (V1 [24:29]–[25:49]; V3 [11:43]).

**State 1 → 2. Target pool check.** A `Confirmed` (or `EqualsCluster`) pool exists overhead = the trade's reason to exist. No pool → remain unarmed regardless of anything else (V1 [11:32]; V2 [29:29]; V3 [3:06]).

**State 2 → 3. Engineered liquidity prints.** As price approaches the target pool it respects it and retraces — i.e., the respect test fires *against the target pool itself* (or its zone), minting an engineered high (V2 [6:14], [28:11]; V3 [9:16]). Detection = a `Confirmed`-transition whose reference level is the target pool. "No engineered liquidity, no model" → without this transition, stay in state 2.

**State 3 → 4. Trap pool built below.** During the retrace: a minor high is taken (inducement, V2 [51:22]; V3 [7:05]) and a low prints that respects a prior low and moves away → a confirmed near-side pool now exists below (the pool to be swept; V2 [34:04]; V3 [8:05]: "high taken out, low respecting low... wait for price to come below this low"). Track the *extreme-most* such pool ("trail your eyes all the way to the extreme", V2 [38:46]).

**State 4 gate. LB / stop-anchor check.** An LB (or prior sweep-wick zone) exists at/below the armed pool (V3 [5:56] checklist; V1 [44:03]; V2 [51:49]). Then pre-compute stop and RR (§G); if RR < floor, either skip or delegate to the LTF instance of this same machine (fractal confirmation entry, V2 [35:05]–[39:32]; V3 [8:41]) **[DECIDE J5]**.

**State 4 → TRIGGER.** The armed pool's level trades through (§E definition) → submit entry immediately, no over-refinement (V2 [14:11]; V1 [30:34]; V3 [5:56], [10:38]). Alternative passive mode: resting limit at the pool level placed on reaching state 4 (V2 [58:10], [68:09]) — most automatable variant, equivalent per file 05 §2.5 **[DECIDE J6]**.

**Timing gates on the trigger (all configurable, V1-only):** inside session window (V1 [49:30]); ≥2–4 min after any news release and never before pending news (V1 [67:13]); optionally not into NY lunch (V1 [105:56]).

**Resets.** Stop-out → return to state 3 (must see fresh inducement + trap before re-entry; bias unchanged while the target pool survives — V2 [22:00]). Target pool swept without trigger → full reset, no chase (V1 [25:08]: "this is not a move I was supposed to be in"). Opposite-side sweep → lockout flips (V1 [24:29]). Max re-arms per pool is unspecified in the sources **[DECIDE J9]**.

## G. Entry / stop / target calculation

- **Entry price:** market at trigger (fill ≈ pool level minus slippage) or limit at pool level (V2 [58:10]). Depth tolerance: fills anywhere between pool level and the LB are valid (V3 [9:59]: "anywhere below this black line"); a non-extreme fill only reduces RR (V2 [42:48]; V1 [52:21]).
- **Stop:** beyond the LB / left-hand extreme — *structural, never a fixed pip count* (V1 [69:02]; V2 [16:17], [43:11]; V3 [14:41]). Buffer: 1–2 ticks futures-style on centralized feeds (V1 [68:28]); spread-aware "breathing room" on CFD (V2 [39:32]) — implement as `buffer = k × spread + fixed_offset` [PARAM].
- **Target(s):** the opposing confirmed pool — never a fixed R multiple (V1 [33:31]; V2 [59:17]). Two-tier: optional partial at the nearest internal/engineered-liquidity pool, full exit at the external/HTF pool (V1 [69:35]; V2 [58:35]; V3 [12:51]).
- **Trade filters:** minimum RR 1:3 computed entry→full-target vs entry→stop (V2 [36:18]); optional minimum absolute distance filter (V1 [94:38]: skips a 140-tick move) [PARAM].
- **Position size:** from fixed per-trade risk (stop distance × volume = risk budget); Marco uses a daily risk cap whose figure he never states (V2 [19:45]) **[DECIDE J10]**. Enforce a daily loss cutoff.

## H. In-trade management

Per file 04 §2–3, encoded mechanically:
1. **Break-even rule (recommended for the bot):** when the first opposing swing high (long case) is taken post-entry → stop to entry (V2 [63:34]; V3 [6:31], [10:38]). This is the V2/V3 mechanical formulation; V1's trail-below-higher-lows (V1 [32:17]) is the discretionary flavor (file 05 §2.1) — offer as an alternative mode **[DECIDE J11]**.
2. **Optional partial:** 20–25% at the internal pool (V2 [64:19]); or none (Marco's stated preference is holding to target, V2 [59:39]).
3. **No fear-based exits:** no mid-trade discretionary logic; stop/target/BE only (V1 [94:38], [103:48]).
4. **Expect re-stabs:** the extreme may be stabbed again after entry without invalidating anything until the structural stop is hit (V1 [84:30], [86:59]) — the BE rule must therefore not fire before an opposing high is actually taken.
5. **End-of-session flat rule** for intraday deployments (futures-style close-before-lunch/close, V1 [105:56]; V2 [23:42]) **[DECIDE J3]**.

## I. Suggested build phases

1. **Phase 1 — Marker/annotator (no orders):** implement §C–§D only; render levels, LBs, red/blue zones on the cTrader chart. Validate by eye against the V3 screenshots (`../03-images/Video3/`) and the worked examples in file 03 §7. This is also exactly how the sources say to train (V2 [69:58]: repetition/eye-training — here applied to validating the detector).
2. **Phase 2 — Signal-only:** add §F; log/alert armed setups and triggers with computed entry/stop/target/RR. Compare frequency against claims ("a couple times per day" on LTFs across assets, V2 [8:54]; extreme-RR ones "once or twice in a month", V2 [8:36]).
3. **Phase 3 — Backtest:** wire §G–§H into cTrader's backtester. The sources publish **no** statistics (file 04 §7) — the edge must be established empirically here, per file 05 §3's "fragile/unverified" caution. Sensitivity-sweep the [PARAM]s (respect tolerance, move-away threshold, swing N, sweep definition).
4. **Phase 4 — Demo/live:** small size, one instrument, with the daily risk cap and news blackout active.

## J. Open design questions — user's judgment required before coding

1. **Instrument.** Sources trade YM/NQ futures, gold, EURUSD, USDJPY and claim universality (V2 [0:22]). On cTrader this means CFDs: gold (XAUUSD — Marco's favorite, V2 [30:40]) vs an index CFD (NAS100/US30 as NQ/YM proxies — but the tick-tight futures stop logic, V1 [69:02], degrades on CFD feeds) vs a major FX pair. Pick one for v1.
2. **Timeframe pair.** 4H/1H swing (V3's fully-demonstrated variant; slower, HTF-robust, fewer trades) vs 15m/1m intraday (V2's gold example; more trades, more parameter risk — LTF entries are where "people are more prone to make mistakes", V2 [45:13]).
3. **Session filter.** Adopt V1's NY-window + lunch/EOD rules (only demonstrated for index futures) or run session-agnostic like the V2 CFD limit-order variant and V3 (file 05 §2.3 argues timing is an overlay, not core)?
4. **News blackout implementation.** Data source for the calendar; blackout width before/after; behavior for positions open into news.
5. **RR-too-low fallback.** Skip the trade (simplest) or implement the recursive LTF confirmation entry (faithful to V2 [36:39] but doubles the state machinery)? Recommend skip in v1.
6. **Execution style.** Market-on-stab (needs tick handling; slippage on spikes) vs resting limit at the pool (V2 [58:10]; clean fills but can be tagged by a wick that keeps running). 
7. **Sweep definition** (§E a/b/c) and all respect-test [PARAM]s — confirm against the Video3 screenshots first (file 07 §A).
8. **Equal-level tolerance and zone heights** — instrument-specific; needs the user's chosen instrument's tick/pip scale.
9. **Re-arm cap** after stop-outs on the same pool (sources give none; the daily risk cap is Marco's only stated brake, V2 [19:45]).
10. **Risk numbers.** Per-trade % and daily cap — deliberately absent from the sources (file 07 §E1); host's 0.5–0.75% (V2 [18:59]) is a starting suggestion only.
11. **Management mode.** Mechanical BE-on-first-high (V2/V3) vs trail-below-higher-lows (V1); partial size 0–25%.
12. **Success criteria before live.** Minimum backtest sample, walk-forward requirement, and the drawdown at which the bot is switched off — none of this comes from the videos; it must come from the user.

---

**Companion files:** rules source of truth — `03-the-liquidity-trap-setup.md`; parameter unknowns — `07-open-questions-pending-visuals.md` §A; edge assessment — `05-cross-video-synthesis.md` §3.
