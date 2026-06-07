# SMC-Prob

A Claude Agent Skill (`/smc-prob`) that combines **ICT/Smart Money Concepts (SMC) structural reading** with a **quantitative probability/confidence layer**, to answer the day-trader's three core questions for any instrument on demand:

1. Where is price likely to go from here?
2. Where is the high-probability entry?
3. How confident should I be in this setup (entry, target, invalidation)?

This project folder tracks the build, design decisions, and source material for that skill, and backs up the finished `AgentSkill.md` once built.

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

## Documents in This Folder

| File | Purpose |
|---|---|
| [README.md](./README.md) | This file — project overview, vision, and design direction |
| [BUILD-LOG.md](./BUILD-LOG.md) | Running log of build progress, decisions, and open questions |
| [research/skill-survey.md](./research/skill-survey.md) | Survey notes on the source skills this combines, and others considered |
| [AgentSkill.md](./AgentSkill.md) | The installable skill definition — `cp` to `~/.claude/skills/smc-prob.md` |
| [TradeLog.md](./TradeLog.md) | Live signal log and outcome tracking — logs every `/smc-prob` signal and its result, used to calibrate scoring weights over time |

---

## Status

✅ **v1 drafted** — `AgentSkill.md` defines the full two-stage pipeline (HTF/LTF structural read → confluence & probability scoring → trade card), the `/smc-prob` invocation spec, behavioural rules, and an ICT/SMC concepts glossary. Scoring weights are a first pass and will be calibrated against logged outcomes in `TradeLog.md`.

**Next**: install and test live against the cTrader MCP connection on a demo account; log signals to `TradeLog.md`; iterate scoring weights based on real outcomes.

See [BUILD-LOG.md](./BUILD-LOG.md) for the full decision history and open items.
