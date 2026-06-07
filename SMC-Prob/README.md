# SMC-Prob

A family of three Claude Agent Skills (`/smc-prob`, `/smc-day`, `/smc-scan`) that combine **ICT/Smart Money Concepts (SMC) structural reading** with a **quantitative probability/confidence layer**, to answer the trader's three core questions for any instrument on demand:

1. Where is price likely to go from here?
2. Where is the high-probability entry?
3. How confident should I be in this setup (entry, target, invalidation)?

What started as a single skill split into two complementary lenses on the same structural read — a **swing-trade mode** (multi-day holds riding to higher-timeframe liquidity targets) and a **day-trade mode** (same-session only, hard flatten-by-deadline rule) — plus a **combined scanner** that runs both in parallel and surfaces everything viable at once. See "Architecture" below for why.

This project folder tracks the build, design decisions, and source material for these skills, and backs up the finished `.md` definitions once built.

---

## Origin

This skill was scoped from a research session comparing public Claude agent-skill repositories for day trading (see [`research/skill-survey.md`](./research/skill-survey.md)). Two repos stood out as complementary halves of the same problem:

| Source | What it contributes | Gap it has alone |
|---|---|---|
| [MobiusQuant/OpenMobius-skill](https://github.com/MobiusQuant/OpenMobius-skill) | ICT/SMC structural framework — Break of Structure, Change of Character, Order Blocks, Fair Value Gaps, premium/discount zones. Answers *"where is price likely to go and where to enter."* | No probability/confidence scoring (acknowledged roadmap-only item in their README) |
| [agiprolabs/claude-trading-skills](https://github.com/agiprolabs/claude-trading-skills) | Quantitative confidence layer — ML signal classification (XGBoost + walk-forward validation), statistical regime detection, market microstructure/orderflow timing, Kelly-criterion sizing, Sharpe/Sortino risk metrics. Answers *"how likely is this to work, and how big should it be."* | No structural/SMC market-reading framework of its own |

SMC-Prob is **not a copy or fork** of either — it's a fresh, standalone Agent Skill (prompt-driven `.md`, in the style of `Trade Picker/AgentSkill.md`) that borrows the *concepts* from both and re-implements them as an MCP-tool-driven analysis pipeline against live cTrader data.

---

## Design Direction (agreed)

- **Standalone skill**, not an extension of `ICT-SMC-Local-Agent` / `ICT-SMC-Remote-Agent`. Those are Python-based scanning agents; SMC-Prob is a `.md` Agent Skill invoked with `/smc-prob`, reasoning live through MCP tool calls — same pattern as `Trade Picker`.
- **Two-stage pipeline**:
  1. **Structural read (SMC lens)** — identify market structure (BOS/CHoCH), Order Blocks, Fair Value Gaps, premium/discount zones, liquidity targets (BSL/SSL), and kill-zone timing, to determine direction and entry zone.
  2. **Probability layer (quant lens)** — score the structural setup against statistical/quantitative confirmation (trend regime, volatility context, momentum confirmation, confluence scoring) to produce a confidence score and risk-calculated trade parameters (entry, stop, targets, R:R, position size).
- **Data source**: live prices/trendbars/symbols pulled through the existing `ctrader` MCP connection (plus `tradingview-mcp` / other connected MCPs for supplementary confirmation, where useful).
- **Output**: a single structured "trade card" — direction, entry zone, stop, targets, R:R, confidence score, and the structural + statistical reasoning behind it (transparent, not a black box).

---

## Architecture — why three skills, not one

The original `/smc-prob` was built and backtested first (see the 2026-06-07 backtest entry in `BUILD-LOG.md`). That backtest produced a real, useful finding: every winning trade in the sample was a **multi-day hold riding to a higher-timeframe liquidity pool** (avg ≈ +5.4R, 1–5 day holds) — i.e., the skill's natural shape is a *swing* trade, not an intraday one, even though its entries are timed with day-trading precision (kill zones, LTF triggers).

When asked whether the skill suited day trading specifically — open and closed within a session, no overnight exposure — the honest answer was "not as built": its targets are HTF liquidity pools that routinely take days to fill, and it has no mechanism to force an exit on a clock. Building genuine day-trade behaviour into the same pipeline would mean adding a hard session-runway gate and a flatten-by-deadline rule that *fundamentally conflict* with the swing skill's "ride it to the HTF target" design — they're not compatible settings on one dial, they're two different trades built on the same structural read.

So rather than compromise the validated swing design, or bolt on an awkward "mode" flag, the skill split into three:

| Skill | Invocation | What it answers | Hold shape |
|---|---|---|---|
| **`AgentSkill.md`** | `/smc-prob` | "Where will this go over the coming days, and where's the best place to ride that?" | Multi-day, rides to HTF liquidity targets — **the original, backtest-validated design, unchanged** |
| **`DayTradeSkill.md`** | `/smc-day` | "Is there a clean, completable round trip available before this session ends?" | Same-session only — hard session-runway gate + flatten-by-deadline rule (new) |
| **`ScanSkill.md`** | `/smc-scan` | "What's viable on this instrument *right now*, across both lenses?" | Runs both pipelines as parallel sub-agents, merges into one combined report — the user picks what (if anything) to act on |

They share the same structural foundation (HTF bias is law in both — Step 2 is identical), the same watchlist, the same data conventions, and the same £/point sizing model. They diverge only where the trade *shape* genuinely diverges: target selection, the runway gate, and the exit rule.

---

## Documents in This Folder

| File | Purpose |
|---|---|
| [README.md](./README.md) | This file — project overview, vision, and design direction |
| [BUILD-LOG.md](./BUILD-LOG.md) | Running log of build progress, decisions, and open questions |
| [research/skill-survey.md](./research/skill-survey.md) | Survey notes on the source skills this combines, and others considered |
| [AgentSkill.md](./AgentSkill.md) | **Swing-trade skill** — multi-day holds riding to HTF liquidity targets. `cp` to `~/.claude/skills/smc-prob.md`, invoke with `/smc-prob` |
| [DayTradeSkill.md](./DayTradeSkill.md) | **Day-trade skill** — same-session only, session-runway gate, hard flatten-by-deadline rule. `cp` to `~/.claude/skills/smc-day.md`, invoke with `/smc-day` |
| [ScanSkill.md](./ScanSkill.md) | **Combined scanner** — runs both lenses in parallel as sub-agents, merges into one report. `cp` to `~/.claude/skills/smc-scan.md`, invoke with `/smc-scan` |
| [TradeLog.md](./TradeLog.md) | Live signal log and outcome tracking — every signal from any of the three skills, tagged by mode, used to calibrate each mode's scoring weights independently over time |

---

## Status

✅ **All three skills installed** (`~/.claude/skills/smc-prob.md`, `smc-day.md`, `smc-scan.md`).

- **`/smc-prob` (swing)** — v1.2, live-tested end-to-end, and the only one of the three with real calibration data behind it: a 2026-06-07 walk-forward backtest over ~5 weeks of XAUUSD_SB produced 4/4 winning trade calls (avg ≈ +5.4R) and ~83–92% correct stand-asides. See the backtest entry in `BUILD-LOG.md` for full methodology and findings — including the validated "follow a bias-only setup forward rather than scoring it fresh each day" refinement, which produced the three largest wins in the sample.
- **`/smc-day` (day-trade)** — v1, freshly built, **not yet live-tested or backtested**. Its session-runway gate and flatten-by-deadline rule are designed but unvalidated against real data — that's the natural next step once the user starts running it.
- **`/smc-scan` (combined)** — v1, freshly built, orchestrates the other two as parallel sub-agent analyses and merges their output. Also not yet live-tested.

**Next**: run `/smc-day` and `/smc-scan` live to validate the new pipelines (the day-trade lens especially needs its own backtest batch — it currently has zero logged outcomes, vs. the swing lens's small-but-real sample); keep logging every signal from all three to `TradeLog.md`, tagged by mode, so each can be calibrated on its own evidence rather than borrowing the other's.

See [BUILD-LOG.md](./BUILD-LOG.md) for the full decision history and open items.
