# ORB Scanner — Stocks-in-Play Opening Range Breakout Advisor

Agent skill that scans the US equity universe at 09:35 ET, identifies **Stocks in Play** (abnormal opening-range Relative Volume ≥ 100%), and reports the **top 3 picks** with complete trade plans (direction, entry stop, ATR-based stop loss, 1%-risk sizing, EoD exit). Advisory only for now — no order placement.

Based on: Zarattini, Barbon & Aziz (2024), *A Profitable Day Trading Strategy For The U.S. Equity Market* — 5-minute ORB on top-20 RVOL stocks: **+1,637% net (2016–2023), Sharpe 2.81, alpha 36%/yr, beta ≈ 0** vs S&P 500 +198%.

Data source: cTrader Open API via remote MCP over persistent HTTP (see `/ctrader-mcp-integration-guide.md`).

## Project map

| File | Purpose |
|---|---|
| `research/STRATEGY-ANALYSIS.md` | Canonical strategy reference — rules R1–R7, maths, nuances, cTrader adaptations |
| `research/paper/…ORB-Stocks-In-Play.pdf` | The source paper |
| `research/UNIVERSE-AUDIT.md` | (Phase 2) account symbol universe + data-quality audit |
| `skill-spec/SKILL-SPEC.md` | Build specification for Opus — architecture, algorithms, schemas, acceptance criteria |
| `DEVELOPMENT-PLAN.md` | Phases, ownership, status, open questions |
| `runs/` | Scan outputs (JSON + Markdown per run) |
| `.claude/skills/orb-scanner/` (repo root) | (Phase 3) the skill itself |

## Status

- ✅ Phase 0–1: research + spec complete (Fable 5, 2026-07-23)
- 🔒 Phase 2: universe audit — **blocked on `CTRADER_MCP_SLUG` secret**
- ⬜ Phase 3: implementation (Opus)
- ⬜ Phase 4: review (Fable 5)
- ⬜ Phase 5: live advisory validation
- ⬜ Phase 6 (future): execution

## Strategy TL;DR

1. Universe: price > $5, 14-day avg volume ≥ 1M shares, ATR14 > $0.50.
2. At 09:35 ET: RelVol = today's 5-min opening volume ÷ 14-day average of the same window. Keep ≥ 1.0, rank descending.
3. First 5-min candle bullish → long-only buy-stop at OR high; bearish → short-only sell-stop at OR low; doji → skip.
4. Stop loss 0.1 × ATR14 from fill; **no profit target**; exit 16:00 ET. One trade per stock per day; never flip direction.
5. Size for 1% equity risk, 4× leverage cap.

The edge is the RVOL selection, not the breakout: identical rules on all stocks ≈ +3%/yr; on top-RVOL stocks ≈ +42%/yr. Expect ~20–25% per-trade win rate carried by unbounded trend-day winners — never add profit targets, never widen stops.
