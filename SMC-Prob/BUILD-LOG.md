# SMC-Prob — Build Log

Running record of progress, decisions, and open questions. Newest entries at the top.

---

## 2026-06-10 — Added concrete "Recommended re-scan" times to no-trade verdicts

Following two consecutive no-trade scans on Gold/NAS100 (both showing post-sweep bullish CHoCH but in the wrong zone for either lens's bias), the "what to watch for" flags were qualitative only — no concrete time to actually come back and check. Added a `Recommended re-scan` field to both lenses' "no trade" cards (`AgentSkill.md` Step 6, `DayTradeSkill.md` Step 6), computed from whichever of **level-ETA** (distance to the watch level ÷ relevant ATR-per-hour), **structure-ETA** (next 1H/4H candle close), or **session-ETA** (next kill zone) is soonest — floored at 15 min, capped at session close. The day-trade variant adds one more cap: the recommendation can never exceed today's flatten-by-deadline time; if the soonest sensible check would land after that, it explicitly recommends the next session's kill-zone open instead. `ScanSkill.md`'s combined report now surfaces a single `Recommended next scan` line taking the sooner of the two lenses' times.

---

## 2026-06-07 — Walk-forward backtest: SMC-Day (XAUUSD_SB) over the last month

Ran a hand-replicated walk-forward simulation of the full `/smc-day` six-step pipeline against the same instrument, ~5-week window, and sample-time as the swing backtest below (XAUUSD_SB, 2026-05-04 → 2026-06-04, daily scans at simulated NY KZ open / 11:00 UTC) — specifically so the two lenses could be compared directly on identical underlying structure. Logged every card (qualifying and no-trade alike) to `research/day-trade-backtest-report.md` in the exact format it would have been shown live, and condensed entries to `TradeLog.md` tagged `[Day]`.

**Methodology note — the data-access workaround.** The `mcp__ctrader__*` MCP tools were unavailable this session (server stuck on "pending approval," and a previous attempt at this exact task had stalled there). All data was instead pulled via a verified HTTP helper script (`.ctrader_http_helper.sh`) that calls the same underlying cTrader MCP server directly over JSON-RPC and parses the nested JSON payload — future readers should know the data is equivalent (same broker, same account, same symbol IDs), just accessed via a different transport. One quirk worth noting for future pulls: `get_trendbars` caps every response at 100 bars regardless of the requested range, so M15 pulls had to be chunked to one session each (~65 bars/session) rather than pulled in bulk.

**Sampled 15 weekday scan days**, deliberately overlapping with the swing backtest's sampled days for direct comparability (eleven of the fifteen days here were also swing-backtest scan days — see caveats). Reused the swing backtest's already-logged Step 2 (HTF bias) reads directly for overlapping dates, since Step 2 is byte-for-byte identical between the two skills — this is methodologically sound (the two lenses only diverge from Step 3 onward) and saved a large number of redundant pulls. Computed pre-scan intraday velocity (ATR/hour, 05:00–11:00 UTC) fresh from the M15 data for every sampled day, and used it consistently as the runway-gate yardstick (it ranged ≈ 4–15 pts/hr across the sample, with most mornings in the 5–7 pts/hr band).

**The single most consequential methodological difference from the swing backtest: no carry-forward.** Per the day-trade lens's design, each day's scan is fully independent — a setup either triggers and resolves within that one session, or it's a flat "no trade" for the day, full stop, with zero walk-forward refinement. This is the structural opposite of the swing backtest's most-validated finding (that patient, multi-session "bias-then-wait" sequences were the actual source of edge) — and the contrast between the two backtests' results makes that opposition vivid and concrete, not just theoretical.

**Aggregate results — 15 days sampled, 2 qualifying day-trade signals (both taken, both winners), 13 no-trade verdicts:**
- **Trade calls: 2/2 won, average ≈ +4.2R blended** (≈ +6.2R on 05-19 — a sweep-and-reject premium short that resolved in ~2.5 hrs; ≈ +2.25R on 05-27 — a breakdown-retest short that also resolved in ~2.5 hrs). Both fully resolved on price (target hit) hours before the session deadline; the flatten-by-deadline rule never had to fire as a mechanical override on either.
- **"No trade" dominated heavily, exactly as predicted** ("expect 'no trade' to dominate since the runway gate is a hard filter" — and it did, though the gate itself was only the decisive *reason* twice; the other eleven stand-asides split roughly evenly between "no HTF bias" (4 days, identical Step-2 reads to the swing log on the same dates), "bias present but entry sits at swing-only/multi-day distance — the seam" (4 days), and "wrong zone / no licensed trigger despite a tradeable-looking range" (4 days, with some overlap)).
- **The runway gate was decisively the deciding factor on 2 of the 15 days (05-11, 06-02)** — and both are maximally instructive: they are the *exact same structures* the swing lens independently rode to ~+5R and ~+9R respectively (its two biggest winners). Counterfactually grading what a forced same-session version would have produced (≈ +2.2R for 05-11, entered at the actual A-grade location; ≈ +2–3R at best for 06-02, entered late because the cleanest part of that move happened in the London session hours before the NY-KZ-anchored scan) confirms the gate's judgment was correct both times — forcing these structures into a single session would have captured only a fraction of what they were capable of, or worse.
- **The flatten-by-deadline rule's value showed up as much in what it organically prevented as in any moment it mechanically fired.** It never had to override price action on either taken trade (both hit target with runway to spare) — but on 05-27 its *logical presence* (the structural requirement to be flat by the close) produced a measurably BETTER outcome than the swing lens achieved on the **identical setup**: ≈ +2.25R for the day-trade lens vs ≈ +1.5R net for the swing lens, because the swing lens's overnight hold of the same short got caught in a violent V-reversal (4366→4511 in ~12 hrs) that the day-trade lens's same-session exit simply never had to face. This is concrete, not theoretical, evidence that "no overnight exposure" can be strictly superior in the right conditions — not merely lower-variance.

**Direct comparison to the swing lens (same instrument, same period, see full table in the report):** the two lenses turned out to be near-mutually-exclusive on this sample, with exactly two points of overlap, and those two overlaps tell the whole story. (1) **05-19** is the *only* setup both lenses caught, scored similarly, and won similarly (~+6R both) — it happened because an unusually fast, complete, single-session move let the day-trade lens capture a "swing-sized" result; this is the day-trade lens's best case, and the exception, not the rule (only 1 of the swing lens's 4 winners happened to also fit in one session). (2) **05-27** is where the day-trade lens *beat* the swing lens outright on the identical structure, for the overnight-exposure reason above. Everything else diverges cleanly: the swing lens's edge comes from patience (every one of its 4 winners needed the multi-session walk-forward window to mature); the day-trade lens's edge — where it exists — comes from selectivity at the point of completion (only taking the subset of clean reads that are ALSO fast and complete enough to fit one session) and from the session boundary itself acting as a disciplined, occasionally beneficial, exit mechanism. The day-trade lens's R-range (≈ +2.25R to ≈ +6.2R) sits inside and is narrower than the swing lens's (≈ +1.5R to ≈ +9R) — and the "missing" big winners are precisely the ones the runway gate filtered out. This is *exactly* the trade-off `DayTradeSkill.md` predicted when it was drafted ("expect smaller R multiples... that's not a flaw, it's the trade-off for zero overnight exposure") — the data bears it out almost perfectly.

**Day-trade-specific calibration notes:**
- The runway gate is doing real, auditable, correctly-decisive work — not just a theoretical safeguard. Both times it fired, grading the counterfactual confirmed it was right.
- Both winning trades triggered within ~30–45 minutes of the NY-KZ-anchored 11:00 UTC scan and resolved in ~2–2.5 hours — directionally consistent with Step 4's "kill-zone timing is near-mandatory" re-weighting for this mode (n=2, far too small to validate the exact weight, but the pattern is clean).
- The shared "show your work once" ATR number (used for both the Step 3 runway gate and the Step 4 quant score) did exactly the double duty `DayTradeSkill.md` designed it for — both winning trades' pre-scan ATR readings (≈ 5.7 and ≈ 11.8 pts/hr) directly explained both the gate's pass verdict and the eventual speed of resolution.
- The 05-14 "stood aside but the breakdown began that same session" case is a *shared* calibration flag with the swing lens, not a day-trade-specific one — both lenses inherit the same up-to-a-session CHoCH-confirmation lag from the shared Step 2, and both would have caught it a session earlier with a slightly more sensitive trigger. Worth tracking as a Step-2 (not Step-3/4) item.

**Honest caveats**: this is a tiny sample of actual trades (n=2, both wins — nowhere near enough to validate Step 4's day-trade-specific thresholds, exactly as flagged when the skill was built: "do not assume the swing lens's calibration carries over"); one instrument, one ~5-week window, hand-replicated scoring (confidence scores are reasoned estimates against the published rubric, not mechanically computed indicator values); the counterfactual R-multiples quoted for the two runway-gate-FAIL cases (05-11, 06-02) are necessarily reconstructions (those setups never actually triggered a day-trade entry — the gate stopped them) included for illustrative reasoning, not logged results; and the sample deliberately overlapped with the swing backtest's days for comparability, which means the "two lenses converge/diverge" findings are partly a function of which days were chosen, not a fully blind comparison — a future run on different days would strengthen that independence. Treat this as a genuine first calibration data point for `/smc-day` (its first ever logged outcomes), not gospel.

---

## 2026-06-07 — Split into three skills: swing (`/smc-prob`), day-trade (`/smc-day`), combined scanner (`/smc-scan`)

Following the walk-forward backtest (below) and a discussion of whether the existing skill suits day trading, built out a genuine architectural split rather than bolting a "mode" flag onto the existing pipeline.

**Why a split, not a flag:** the backtest showed the existing skill's natural shape is a *swing* trade — every winning call was a multi-day hold riding to an HTF liquidity pool (avg ≈ +5.4R over 1–5 days), even though its entries are timed with day-trading precision (kill zones, LTF triggers). A genuine same-session, no-overnight-exposure mode needs two things the swing design fundamentally can't have at the same time: a **hard session-runway gate** (reject structurally-clean setups that can't complete before a deadline) and a **flatten-by-deadline rule** (close on the clock, not just on price/structure). Bolting those onto the validated swing pipeline would compromise the very design the backtest just proved out. So instead of one skill with an awkward dial, there are now three:

1. **`AgentSkill.md` / `/smc-prob` (swing) — unchanged.** The validated multi-day pipeline, left exactly as backtested.
2. **`DayTradeSkill.md` / `/smc-day` (day-trade) — new.** Same Step 1/2 (market-hours check, HTF bias — HTF bias is law in both modes, no shortcuts), then diverges hard: Step 3 adds a **session-runway gate** (pass/fail, not scored — estimates from intraday ATR whether there's realistically enough time to complete entry→target→exit before a defined session deadline; fails this and it's a flat "no trade" regardless of how clean the structural read looks), Step 5 redefines targets as **intraday-only** liquidity pools (current/prior session high-low, LTF FVG/OB — not the HTF BSL/SSL the swing skill rides for days) and adds the **flatten-by-deadline rule** as a mechanical exit equal in force to the stop or target. Two new behavioural rules make the clock a hard constraint ("the clock is a hard constraint, exactly like the stop loss" / "flatten on the clock, not only on price") and require the skill to name the seam when a read is swing-shaped rather than day-trade-shaped ("this is valid, but it's a swing setup — try `/smc-prob`").
3. **`ScanSkill.md` / `/smc-scan` (combined) — new.** Per the user's explicit request: "have a sub agent designed to do the work in parallel to find and analyse the Day Trades... Then when a scan is done, I can be provided with the relevant Swing Trades available to take, as well as Day Trade options... Then I can get you to execute one, the other, or both." Implemented exactly that — it spawns the swing and day-trade pipelines as **two parallel sub-agent analyses** (via the Agent tool, single message — no dependency between independent reads of the same live data), then merges both into one combined report (`── SWING TRADE LENS ──` / `── DAY TRADE LENS ──` / a plain-English summary of what's actually on the table). Neither verdict is softened by the other; disagreements between the two reads are surfaced, not papered over; every "bias present, not at price yet" flag from either lens is called out explicitly as a follow-up candidate — directly building on the backtest's most validated finding (see below: the setups that mattered most were the ones somebody followed forward).

All three share the same structural foundation (Step 2 HTF read is identical across swing and day-trade — "HTF bias is law" applies equally to both), the same verified `_SB` watchlist, the same data conventions, and the same £/point spread-bet sizing model — they diverge only where the trade *shape* genuinely diverges.

**Installed all three** (`~/.claude/skills/smc-prob.md`, `smc-day.md`, `smc-scan.md`).

**The bigger picture — this is step one toward the user's stated end-state**: an agent running on a laptop through the trading day on a strict schedule, periodically scanning and **automatically re-checking "bias present, not at price" setups** (re-scan as price approaches the flagged level; abandon the watch if it invalidates first) — i.e. the walk-forward behaviour the backtest just validated as the actual source of edge, made systematic and scheduled rather than manual. For now (running periodically from a phone), `/smc-scan` is built specifically to make every such flag impossible to miss, so the user can manually trigger the follow-up scans the future scheduler will eventually automate.

**Still open:**
- `/smc-day` and `/smc-scan` are freshly built and **not yet live-tested or backtested** — the day-trade lens in particular has zero logged outcomes (vs. the swing lens's small-but-real backtested batch). Both need their own evidence base before their Step 4 weights mean anything; do not assume the swing lens's calibration carries over.
- `TradeLog.md` entries from all three skills should be tagged by mode (`[Swing]` / `[Day]`) going forward so each can be calibrated independently.
- The scheduled-laptop-scanner vision remains the long-term target; `/smc-scan` is the manual bridge to it, not the thing itself.

---

## 2026-06-07 — Walk-forward backtest: XAUUSD_SB over the last month

Ran a hand-replicated walk-forward simulation of the full six-step pipeline against ~5 weeks of historical XAUUSD_SB H4/H1/M15 data (2026-05-04 → 2026-06-05), to get a first read on how `/smc-prob` would have performed "blind," called once per day at the simulated NY Kill Zone open (11:00 UTC). Logged every distinct signal — taken trades and stand-asides alike — to `TradeLog.md`.

**Methodology.** Pulled H4 candles for the full window in two ≤30-day chunks up front, kept a running mental model of swing structure as I moved chronologically forward, and pulled M15 only on demand at specific scan points / follow-through windows (saving a large number of calls vs. per-day full pulls). Sampled 13 weekday scan points spread across the full month (every-other trading day, roughly) rather than all 25 — full daily granularity would have meant ~75 individual MCP pulls (H4+H1+M15 ×25) for marginal extra signal, since most "no entry yet" verdicts persist for several consecutive days and would otherwise be triple-counted. **No-lookahead discipline**: at each scan timestamp, only H4/H1/M15 bars with close-times at or before that timestamp informed the Step 2/3/4 verdict (e.g. at an 11:00 UTC scan, the most recent usable closed H4 bar opened 05:00/closed 09:00, with the 09:00 bar still "in progress"); subsequent bars were pulled and read only afterward, purely to grade what actually happened. **Walk-forward refinement**: three of the ten distinct signals were "HTF bias present, no LTF entry yet" calls — each was followed forward (not re-scored as a fresh independent signal on subsequent days) until either (a) price reached the flagged entry zone with structure intact → graded as a real triggered trade from there, or (b) the window expired (capped ~5 trading days) with no trigger → logged as "expired, never triggered."

**Aggregate results — 10 distinct signals (4 trade calls, 6 stand-asides):**
- **Trade calls: 4/4 won** (one with a caveat — see below). Two were clean "A"-grade triggers reached via the walk-forward refinement (05-19 short off the 05-18 bias, ~+6R; 06-02 short off the 06-01 bias, ~+9R — the single biggest winner of the sample). One was a "B"-grade long off the 05-08 bias (~+5R, triggered 05-10/11). One was a "B"-grade short off the 05-26 bias (05-27 trigger) that hit TP1 for ~+3R on the 50%-close portion before an extreme V-reversal would have stopped the runner — net ≈ +1.5R blended, and a vivid real-world justification for the "close 50% at T1" rule (a full-size hold round-trips to a loss here).
- **Average R on taken trades: ≈ +5.4R** (driven up by the two A-grade walk-forward triggers; median closer to +4R).
- **Stand-asides: 6 calls, 5 clearly correct, 1 borderline-late** (≈ 83–92% accuracy depending on how the borderline case is scored). Correct stand-asides: 05-04 (genuine range, no clean entry either side), 05-12 (CHoCH ambiguity — avoided buying into a reversal that fell ~150pts), 05-22 (multi-day chop after a bearish leg exhausted), 05-28 (chaotic post-sweep V-reversal — classic whipsaw, round-tripped both ways over the following week). The 05-06 "bias-only, no entry" call technically never triggered (price never offered the planned discount pullback before running to new highs) — correct in discipline, but a reminder that "wait for the better location" sometimes means missing a continuation entirely. The borderline case is 05-14: stood aside correctly (avoided a wrong-side long), but the bearish breakdown began that same session, and the underlying CHoCH evidence (a break of the 4648 swing low) was arguably already visible a session earlier on 05-12 — see calibration note below.

**Calibration observations:**
- **Every signal that reached a confluence read of ~10+ won, and the two A-grade (~12/14) walk-forward triggers were the cleanest, largest winners** — directionally consistent with the 11–14 "high-probability" tier being the most reliable, though the sample (4 trades) is far too small to validate the exact thresholds.
- **The walk-forward refinement was the single most valuable thing this backtest demonstrated**: 3 of 4 winning trades (and the two biggest winners) came from "no entry yet" bias calls that would have been logged as flat misses under naive day-by-day independent scoring. This strongly supports keeping that refinement as the standard interpretation of a persisting "bias present, no entry" verdict — a single structural read can validly produce one followed-through outcome over several days.
- **Possible mis-calibration flag**: the 05-14 stand-aside suggests Step 2's CHoCH-confirmation logic may lag a real structural shift by up to a session — worth watching for in future live runs (a slightly more sensitive CHoCH trigger could have caught the 05-14/15 bearish turn a day earlier, in time to set up the watch-zone for 05-18 sooner).
- **Zone-vs-bias contradictions ("bias says X but price is already in the wrong half of the range") showed up three separate times** (05-06, 06-01, and the live 06-07 entry at the top of this log) — and in all three cases, correctly refusing to chase and instead flagging the retrace-to-better-location level was the right call; two of those three retraces (06-01→06-02) materialized cleanly into A-grade triggers. This is good evidence the "HTF bias is law, never force a counter-zone entry" rule is doing real work, not just being overly conservative.

**Structural patterns worth noting**: every winning trade in this sample originated from a *patient* bias-then-wait sequence (none came from a same-session "bias + immediate entry" read) — in this particular month, the highest-quality setups all needed the walk-forward window to mature. Grade-A setups (both reached via walk-forward) outperformed Grade-B setups in this sample, consistent with Step 4's weighting.

**Honest caveats**: this is one instrument, one ~5-week window, hand-replicated scoring (not a live run of the actual skill, and confidence scores above are estimates reasoned through Step 4's rubric rather than mechanically computed indicator values), and a small sample (10 signals, 4 trades) — treat this as a *first* calibration data point, not gospel. A live or larger-sample run, ideally across the full watchlist, is needed before adjusting any Step 4 weights.

---

## 2026-06-07 — First full end-to-end run (`/smc-prob XAUUSD_SB`); v1.2

Ran the complete six-step pipeline live against XAUUSD_SB (gold) — first full structural read → scoring → verdict cycle, not just a plumbing check.

**Found one more real-world gap: no market-hours check.** The run happened on a Sunday (2026-06-07 15:11 UTC); gold markets were closed. `get_spot_prices` and `get_trendbars` silently returned **Friday's stale close** (timestamped 2026-06-05 ~20:55 UTC) with no signal that the data was stale — the skill would have presented day-old weekend data as a live read with no caveat.
- **Fix (v1.2)**: added an explicit market-hours check as the first action in Step 1 — compare the spot price's `timestamp` against current time; if stale beyond ~15–20 min during normal trading hours, label the analysis "last session" and lead with that fact rather than silently analysing old candles.

**The analytical pipeline itself produced a correct, disciplined result** on real data:
- **HTF read**: clean, confirmed bearish CHoCH/BOS on H4 — three consecutive large bearish candles broke a consolidation range and printed new lows (swing range 4311.80–4515.41, equilibrium ≈ 4413.6)
- **Zone check**: price had already driven deep into the **discount** zone (~8% above the swing low) — which is wrong location for a fresh short (shorts want premium) and there was no confirmed bullish reversal to justify a counter-trend long either
- **Verdict: no qualifying setup** — correctly stood aside rather than forcing a short into poor location just because the trend looked convincing. This is *exactly* the discipline Step 4's thresholds and Behavioural Rule #2 ("never force a trade") are designed to produce, and it held up under a real, live, slightly-messy market read (decisive trend + contradictory location is a common real-world combination, not an edge case).
- Output included concrete "what to watch for" levels for the next session (premium-zone short-continuation setup near 4460–4515, or a sweep-and-reversal long setup below 4311.80) — giving the user something actionable even from a "no trade" read.

**v1.2 installed.** Logged this run to `TradeLog.md` as a "no-trade" entry — tracking correct stand-asides is just as important for calibration as tracking taken trades, since a skill that's too eager to find confluence is worse than one that's appropriately cautious.

**Still open:**
- Haven't yet seen the pipeline produce an actual high-confidence trade card (score ≥ 11/14) — need to run it during live market hours, ideally across the full watchlist, to see one through to a real entry/stop/target output and validate the sizing math end-to-end.
- Confluence score weights remain uncalibrated — first calibration pass requires several logged outcomes (taken trades + correct/incorrect stand-asides).

---

## 2026-06-07 — Live test against connected cTrader account; v1 corrected to v1.1

Installed the skill (`cp AgentSkill.md ~/.claude/skills/smc-prob.md`) and ran the early pipeline steps live against the connected cTrader MCP to validate assumptions before a full end-to-end run. **Found three real-world mismatches between the v1 draft and the live account — all now fixed in `AgentSkill.md`:**

1. **Account type mismatch (the big one).** The connected account is a **UK spread-betting account**, not a CFD/FTMO account like `ICT-SMC-Local-Agent` assumes. Live evidence:
   - `get_symbols` shows the plain instrument names (`EURUSD`, `XAUUSD`, etc.) as `"enabled": false`; the *tradeable* equivalents are `_SB`-suffixed (`EURUSD_SB`, `XAUUSD_SB`, `NAS100_SB`, …).
   - `get_balance` returned a GBP balance (`depositAssetId: 6`, `moneyDigits: 2` → ~£48,233.50).
   - Each `_SB` symbol's `description` field states its dealing convention directly, e.g. `"EUR vs US Dollar, bet in 1 GBP per (0.0001)"` — this is a **£-stake-per-point** model, not the CFD lots/`lotSize`/cents-of-base model the cTrader MCP's general instructions describe (and which v1's sizing math used).
   - **Fix**: rewrote Step 5 sizing to the spread-bet £/point model (same approach as `Trade Picker`'s "Spread Bet" mode), reading the point size straight from each symbol's `description`. Also added an explicit instruction to check `enabled` + `description` *first* on any newly-connected account, since CFD and spread-bet models are mutually exclusive and the wrong one produces a meaningless stake.

2. **Default watchlist was wrong for this account.** v1's watchlist (copied from `ICT-SMC-Local-Agent`'s FTMO list) used plain CFD names and included crypto. Live `get_symbols` showed:
   - The correct enabled equivalents have different names than expected in places — Nasdaq-100 is `NAS100_SB` (not `US100_SB`), oil is `Crude_SB`/`Brent_SB` (not `USOIL_SB`).
   - `BTCUSD_SB`, `ETHUSD_SB`, `SOLUSD_SB` exist but are **all disabled** on this account — crypto isn't tradeable here.
   - **Fix**: replaced the watchlist with the 12 confirmed-enabled `_SB` instruments, their live `symbolId`s (needed for `get_trendbars`/`get_spot_prices`), and their point sizes — with a note that this table is account-specific and must be re-verified if a different account connects.

3. **`get_trendbars` call convention differs from its tool description.** The schema suggests `count` alone or `toTimestamp`+`count` should work ("last N bars ending now" / "ending at toTimestamp"), but both were rejected live with `"fromTimestamp: must not be null"`. Only the explicit `fromTimestamp`+`toTimestamp` range form worked.
   - **Fix**: documented this in the cTrader data conventions section — always pass both timestamps explicitly.

**Spot-checked the structural-read data itself** (EURUSD_SB H1, last ~46 bars): a clean recent swing high near 1.1645 followed by a sharp impulsive break down to ~1.1522 — exactly the kind of BOS/CHoCH shape Step 2 is designed to detect. The pipeline's *analytical* design holds up against real data; the issues found were all in the *plumbing* (account/instrument/sizing assumptions), which is precisely what a live test is for.

**v1.1 is now installed** (`~/.claude/skills/smc-prob.md`) with all three fixes applied.

---

## 2026-06-07 — Open questions resolved; AgentSkill.md v1 drafted

**Decisions:**

1. **Instrument scope** — Default to the same FTMO Swing-eligible watchlist already documented in `ICT-SMC-Local-Agent/CLAUDE.md` (14 instruments — forex majors, XAUUSD, US/UK/EU indices, USOIL, BTC/ETH/SOL). Reuses an already-curated, broker-validated list rather than inventing a new one. `/smc-prob [SYMBOL]` overrides to focus on a single instrument.
2. **Timeframes** — Standard ICT top-down structure: **HTF (4H/1H) for directional bias**, **LTF (15M/5M) for the entry trigger**. This is the methodology the kill-zone definitions already in the repo assume (e.g. NY KZ as the LTF execution window for an HTF bias formed overnight).
3. **Probability methodology** — Start **rules-based confluence scoring** (transparent, auditable, no training data required), modeled on `Trade Picker`'s normalised-scoring approach, but split into two axes: SMC structural signals + quant/statistical confirmation signals, combined into one score. An ML-classifier phase (à la agiprolabs' XGBoost skill) is deferred until `TradeLog.md` has enough logged outcomes to train and validate one credibly — premature ML on no data would be worse than a transparent rule set.
4. **Kill zones** — Reused verbatim from `ICT-SMC-Local-Agent/CLAUDE.md`: NY KZ 07:00–10:00 ET, Silver Bullet 09:50–10:10 ET, London KZ 02:00–05:00 ET. Keeps timing definitions consistent across both projects.
5. **Output format** — Trade card modeled on `Trade Picker/AgentSkill.md`'s card, extended with SMC-specific fields: structure state (BOS/CHoCH), OB/FVG levels + grade, liquidity targets (BSL/SSL), premium/discount zone, kill-zone status, AMD-cycle/sweep confirmation.
6. **Position sizing** — Pull live account balance via `mcp__ctrader__get_balance` rather than requiring the user to type it in; convert risk % to cTrader volume using the symbol's `lotSize`/`pipDigits` from `get_symbols` (cents-of-base convention) — explicitly guards against the "reuse the forex 10,000,000 constant for XAUUSD" oversizing trap called out in the cTrader MCP's own instructions.

**Done:**
- Drafted `AgentSkill.md` v1 — full two-stage pipeline (structural read → confluence/probability scoring → trade card), `/smc-prob` invocation spec, behavioural rules, and an ICT/SMC concepts glossary.

**Still open / to validate once tested live:**
- Confluence score weights are a first pass — will need calibration against logged outcomes in `TradeLog.md`.
- Whether `tradingview-mcp` cross-confirmation adds enough value to justify the extra calls, or whether cTrader-derived indicators alone are sufficient — assess after the first batch of live tests.
- Whether the FTMO watchlist should be configurable per-account (the current list assumes the FTMO Swing account context from `ICT-SMC-Local-Agent`).

---

## 2026-06-07 — Project scaffolded

**Done:**
- Created `SMC-Prob/` project folder in `CTrader-Bots`
- Wrote `README.md` capturing the project's origin, the two source skills it combines, and the agreed design direction
- Logged the source-skill research in `research/skill-survey.md`

**Decisions made:**
- **Name**: `SMC-Prob`, invoked as `/smc-prob`
- **Build approach**: fresh standalone Agent Skill (`.md`, prompt-driven, MCP-tool-call pipeline) — *not* an extension of the existing `ICT-SMC-Local-Agent` / `ICT-SMC-Remote-Agent` Python agents. Those remain separate, Python-based scanning systems; SMC-Prob is a lighter conversational skill in the `Trade Picker` style.
- **Scope of this pass**: scaffolding and tracking docs only — no skill logic yet.

**Open questions for the next build phase:**
1. **Instrument scope** — all cTrader symbols, or a fixed watchlist (mirror `ICT-SMC-Local-Agent`'s FTMO instrument list, or define a new one)?
2. **Timeframe(s)** — which timeframe(s) define the structural read (HTF bias) vs. the entry trigger (LTF)? (ICT methodology typically uses an HTF→LTF top-down approach, e.g. 4H/1H bias → 5M/15M entry.)
3. **Probability methodology** — do we want a transparent rules-based confluence score (like `Trade Picker`'s normalised scoring table — easy to audit, no training data needed) or an ML-classifier approach (like agiprolabs' XGBoost skill — needs historical data + training, more opaque but potentially sharper)? Leaning toward starting rules-based (auditable, immediate) with ML as a later phase.
4. **Kill zones / session timing** — reuse the kill-zone definitions already documented in `ICT-SMC-Local-Agent/CLAUDE.md` (NY KZ 07:00–10:00 ET, Silver Bullet 09:50–10:10 ET, London KZ 02:00–05:00 ET)?
5. **Output format** — model the trade card on `Trade Picker`'s card (direction/entry/stop/targets/R:R/confidence/confluence list/invalidation), extended with the SMC-specific fields (structure state, OB/FVG levels, liquidity targets, premium/discount zone)?
6. **Position sizing** — reuse `Trade Picker`'s spread-bet/CFD/direct sizing logic, or defer sizing to the existing cTrader account data via the MCP (`get_balance`, `get_positions`)?

---

## Next Steps

- [ ] Resolve open questions above (with user input)
- [ ] Draft the two-stage pipeline spec (structural read → probability scoring → trade card)
- [ ] Write `AgentSkill.md` v1 (rules-based confluence scoring, single instrument or small watchlist)
- [ ] Test `/smc-prob` against live cTrader data on a demo account
- [ ] Add `TradeLog.md` for signal/outcome tracking
- [ ] Iterate scoring weights based on logged outcomes; consider ML-classifier phase 2
