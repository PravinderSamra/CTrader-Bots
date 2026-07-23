# ORB Scanner — Development Plan

Roles: **Fable 5** = research, architecture, spec, review. **Opus** = implementation. **User** = decisions, secrets, live validation.

## Phase 0 — Research ingestion ✅ (2026-07-23)
Paper read in full, strategy formalised in `research/STRATEGY-ANALYSIS.md` (rules R1–R7, maths, execution nuances, cTrader adaptations).

## Phase 1 — Architecture & build spec ✅ (2026-07-23)
`skill-spec/SKILL-SPEC.md` written: file layout, engine/agent division, universe modes, algorithms, JSON schema, report template, tests, acceptance criteria.

## Phase 1b — FTMO universe research ✅ (2026-07-23)
Account confirmed as **FTMO prop-firm cTrader**. FTMO's full Equities CFD list pulled from their public symbols API: 59 equities → **45 scannable US stocks** (full list + specs in `research/FTMO-UNIVERSE.md`, snapshot in `research/data/ftmo-universe.json`). Critical finding: FTMO US stock CFDs trade 09:35–16:00 ET — the 09:30–09:35 opening-range bar is outside the CFD session, so OR measurement comes from an external equity feed while cTrader remains the pricing/execution venue (dual-source architecture, SKILL-SPEC §4.1). FTMO constraints folded into spec: 3.33× equity leverage, 5%/10% loss limits, news-trading restriction reminder.

## Phase 2 — Audit 🔶 partially unblocked
Owner: Opus (or Fable 5). Tasks in SKILL-SPEC §8. Output: `research/UNIVERSE-AUDIT.md` + `universe.json`.
- **(a) Measurement-feed evaluation — can start NOW, no token needed:** pick primary+fallback source for 5-min US equity bars (Alpha Vantage / TradingView OHLCV / aktools).
- **(b) cTrader account verification — 🔒 blocked on `CTRADER_MCP_SLUG`:** confirm the 45 symbols/symbolIds on the live FTMO account, divisors, and whether the 09:30 bar truly is absent.

## Phase 3 — Skill implementation (Opus)
Build per SKILL-SPEC: `ctrader_client.py`, `orb_scan.py` (+ pytest suite), `SKILL.md`, `universe.json`. Definition of done = acceptance criteria §9.

## Phase 4 — Fable 5 review
Line-by-line review against SKILL-SPEC §9 + strategy analysis. Run replay mode on ≥3 historical sessions incl. one high-news day. Findings fixed before sign-off.

## Phase 5 — Live advisory validation
Run `/orb-scanner` daily at 09:35 ET for ≥2 weeks (Routine can automate the trigger). Journal every scan in `runs/`. Compare picks vs what a manual read of the paper's rules would select; track hypothetical R outcomes. Tune only: watchlist cap, liquidity floor. **Do not tune strategy rules.**

## Phase 6 — Future: execution capability (explicitly out of scope now)
Consume the picks JSON to place bracket stop orders via `create_order` (trading profile). Requires: user green-light, sizing rework for spread-bet/CFD stake maths, spread-cost expectancy re-validation, kill-switch and max-daily-loss guard.

## Open questions for the user
1. ~~Which account?~~ **Answered: FTMO prop-firm cTrader account.** Remaining sub-question: Challenge/Verification or funded, and Standard or Swing? (Standard funded accounts carry the news-trading restriction; Swing is exempt.)
2. Scan automation: run as a scheduled Routine each trading day at 09:35 ET, or on-demand only?
3. Account equity figure for sizing lines (FTMO account size, e.g. $100k?), and risk per trade on the prop account — paper uses 1%, but 0.5% is common practice under FTMO's 5% daily-loss cap. Default until told otherwise: FTMO balance from `get_balance`, 1% risk.
4. Include the 13 EU stocks later as a separate 08:05 UTC scan (European open), or US-only permanently?
