# SMC-Prob — Build Log

Running record of progress, decisions, and open questions. Newest entries at the top.

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
