# News Straddle Bot — Backtest / Forward-Test Log

Per `SPEC.md` section 8a: cTrader's backtester cannot validate this strategy's profitability (it doesn't model release-time spread blowout, slippage, or rejected orders). Use it only to verify mechanical correctness. The entries below should be dominated by **live/demo forward tests at minimum size**, which are the actual v1 validation output.

Copy the block below for each run.

---

## Run template

- **Date/Event**: e.g. 2026-08-01 — US NFP
- **Instrument**: e.g. XAUUSD
- **Mode**: Backtest (mechanical only) / Demo forward test / Live (min size)
- **Key parameters**: RiskMode, RiskPercent/RiskFixedAmount, BufferDistance, StopLossDistance, TriggerSide, OrderExecutionType, SpreadGuardMode, EnableDynamicStop
- **Spread at arming**: 
- **Spread at fill**: 
- **Which leg filled**: Buy / Sell / Both (double fill) / Neither (timed out)
- **Entry slippage vs target price**: 
- **Exit reason**: SL / TP / Dynamic stop / Timed out / Double-fill flatten
- **Exit slippage**: 
- **State transitions observed** (paste from log): 
- **Anomalies / unexpected behavior**: 
- **Net result**: 

---

(Add entries above this line, most recent first.)
