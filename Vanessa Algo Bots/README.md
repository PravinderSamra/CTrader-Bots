# Vanessa Algo Bots — FTMO $100K 2-Step programme

Goal: intraday cBots that pass the FTMO $100,000 2-Step challenge (Phase 1 +10%, Phase 2 +5%)
and keep a funded account paying out, without ever touching the 5% daily or 10% total loss limits.

## FTMO limits and the bot's internal limits

| Rule | FTMO limit | Internal limit (default) |
|---|---|---|
| Max daily loss | $5,000 below the 00:00 CE(S)T balance/equity | Soft 3% (no new entries), hard 4% (close all positions, stop for the day) |
| Max total loss | $90,000 static floor | Hard 8.5% (close all positions, stop until reset manually) |
| Per-trade risk | — | 0.25–1.0% of equity, reduced automatically as drawdown grows |
| Trading window | — | Entries 08:00–21:00 UK, all positions closed before 21:00 UK |
| Profit target | 10% / 5% | Stop at target; keep going at minimum size only until 4 trading days are met |

## What we start from (evidence already in this repo)

| Strategy | Status | Key numbers |
|---|---|---|
| US500 15m ORB (`ORB Projects/ORB Bot` + `US500 ORB Bot/analysis`) | **Validated edge** | 1,099 trades 2022–26, out-of-sample +0.068R, permutation p=0.014; 1 trade/day: +0.079R, max DD 11.9R, worst day −1.29R |
| NAS100 London Range Breakout (`US30 London Range Breakout`) | **Promising, needs a clean test** | PF ~1.33–1.36, ~−12R DD; daily-R correlation with US500 +0.48 |
| US30 ORB Volume Breakout v2 (`ORB Projects/ORB Volume Breakout Bot`) | **No edge** | 432 trades, PF 1.03, 95% CI of expectancy spans zero; 2023/2024 negative |
| GER40 opening candle / RVOL breakout (`DAX Opening Candle Breakout`) | **Rejected** | Costs are larger than the gross edge. The Frankfurt morning session is uncorrelated with US500 (−0.04), so the session is still worth using. |

## Roadmap

0. **Risk core** — `core/FtmoRiskGuard`: resets the daily loss reference at 00:00 CE(S)T, uses the soft and hard breakers above, checks worst-case loss before every trade (open risk + new risk + slippage allowance), reduces risk as drawdown grows (risk ≤ remaining headroom ÷ 12), locks in the profit target, counts trading days, closes positions at the end of the session, and saves its state so a restart does not reset it. Every bot uses it.
1. **Bot 01 — US500 15m ORB**: port the validated configuration unchanged (NY 09:30–09:45 range, M5 close 10pt beyond it, stop at 50% of the range, 3R target, break-even at 1.2R with 1R steps, stop tightened to 37% of risk at 0.74R, entries until 13:30 ET, positions closed 15:50 ET, 1 trade/day) and add the risk core.
2. **Bot 02 — NAS100 London Range Breakout**: build it, then run a single pre-registered out-of-sample test with costs included before it gets any risk budget.
3. **Bot 03 — London-morning diversifier** (GER40 / XAUUSD / EURUSD / GBPUSD, 08:00–11:00 UK): new research aimed at low correlation with the US open. The GER40 2025–26 data has never been used and is reserved for this test.
4. **Portfolio layer**: Monte Carlo of the combined daily-R series under FTMO rules, used to set risk per bot for ≥85% pass rate and ≤10% bust rate.
5. **Mean-reversion research** (e.g. fading a failed breakout / liquidity trap) — only after 1–3 are running.

### What a strategy must show to go live
Transaction costs included in the test · out-of-sample t > 2 or permutation p < 0.05 · at least ~300 trades ·
no single month > 40% of profit · worst historical day at the chosen risk < 2% · FTMO Monte Carlo pass ≥ 85%.

## Folder structure

```
Vanessa Algo Bots/
├── README.md                 this file
├── docs/                     FTMO_RULES.md, TEST_PROTOCOL.md, RESEARCH_LOG.md (every run, including losers)
├── core/                     FtmoRiskGuard.cs — master copy, pasted verbatim into each bot
│                             (cTrader builds each cBot from a single file); sync_check.py checks the copies match
├── bots/
│   ├── 01_US500_ORB/         src/*.cs, presets/*.cbotset, backtests/ (logs + parsed CSV), README.md
│   ├── 02_NAS100_LRB/
│   └── 03_London_Diversifier/
├── research/                 scripts/, results/ — data is read from the existing repo folders, not copied
└── portfolio/                correlation + FTMO Monte Carlo across bots
```
