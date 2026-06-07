# SMC-Prob — Build Log

Running record of progress, decisions, and open questions. Newest entries at the top.

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
