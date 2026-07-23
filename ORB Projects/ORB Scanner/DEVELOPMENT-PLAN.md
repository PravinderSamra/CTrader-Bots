# ORB Scanner — Development Plan

Roles: **Fable 5** = research, architecture, spec, review. **Opus** = implementation. **User** = decisions, secrets, live validation.

## Phase 0 — Research ingestion ✅ (2026-07-23)
Paper read in full, strategy formalised in `research/STRATEGY-ANALYSIS.md` (rules R1–R7, maths, execution nuances, cTrader adaptations).

## Phase 1 — Architecture & build spec ✅ (2026-07-23)
`skill-spec/SKILL-SPEC.md` written: file layout, engine/agent division, universe modes, algorithms, JSON schema, report template, tests, acceptance criteria.

## Phase 2 — Connectivity & universe audit 🔒 blocked on `CTRADER_MCP_SLUG` secret
Owner: Opus (or Fable 5). Tasks in SKILL-SPEC §8. Output: `research/UNIVERSE-AUDIT.md` + `universe.json`.
**Key risk resolved here:** does the account expose US shares with usable 5-minute volume? Decides universe Mode A (ctrader-native) vs Mode B (hybrid).
Decision point for user at the end of this phase.

## Phase 3 — Skill implementation (Opus)
Build per SKILL-SPEC: `ctrader_client.py`, `orb_scan.py` (+ pytest suite), `SKILL.md`, `universe.json`. Definition of done = acceptance criteria §9.

## Phase 4 — Fable 5 review
Line-by-line review against SKILL-SPEC §9 + strategy analysis. Run replay mode on ≥3 historical sessions incl. one high-news day. Findings fixed before sign-off.

## Phase 5 — Live advisory validation
Run `/orb-scanner` daily at 09:35 ET for ≥2 weeks (Routine can automate the trigger). Journal every scan in `runs/`. Compare picks vs what a manual read of the paper's rules would select; track hypothetical R outcomes. Tune only: watchlist cap, liquidity floor. **Do not tune strategy rules.**

## Phase 6 — Future: execution capability (explicitly out of scope now)
Consume the picks JSON to place bracket stop orders via `create_order` (trading profile). Requires: user green-light, sizing rework for spread-bet/CFD stake maths, spread-cost expectancy re-validation, kill-switch and max-daily-loss guard.

## Open questions for the user
1. cTrader account for this project: the existing Pepperstone UK **spread-betting demo** may not carry US shares. If the audit finds none, do you have/want a share-CFD account (Pepperstone Razor CFD carries US share CFDs), or run hybrid/advisory mode?
2. Scan automation: run as a scheduled Routine each trading day at 09:35 ET, or on-demand only?
3. Account equity figure to use for sizing lines in reports (default $25,000 like the paper)?
