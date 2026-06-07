# SMC-Prob — Build Log

Running record of progress, decisions, and open questions. Newest entries at the top.

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
