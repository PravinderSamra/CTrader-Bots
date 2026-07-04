# Gap-and-Retrace Research

Research into the **gap-up / gap-down → retrace-to-fill** trading idea: when an instrument opens
away from the prior day's range, how often price retraces to *fill* that gap, how deep it retraces
before its directional move, and how to trade it mechanically on the 5m/15m.

**Data source:** cTrader / Pepperstone UK spread-betting CFDs, pulled live via the cTrader MCP.

## Headline findings (Phase 1)
- On 24h CFDs the classic intra-week "opening gap" barely exists — **real gaps only form over the
  weekend and (for European indices) the nightly session void.** US index CFDs gap ≥0.15% on only
  ~3–4% of weekday rolls; **GER40 (DAX) gaps on ~22%** → it is the chosen instrument.
- **GER40 tradeable gaps fill same-session ~66% (daily) / ~85% (intraday M15)**, and the day more
  often **fades** (closes against the gap) than continues → a mean-reversion edge.
- **Small gaps fill (88% for <0.25%), big gaps run (38% for >1%).** Trade the ~0.15–0.6% band.
- Median **time-to-fill ~90 min**; the retrace typically **overshoots** the fill (median ≥200% of gap).
- A mechanical fade back to the fill is **positive-expectancy**; a confirmation entry wins **~70%**.

👉 Phase 1 write-up (theory, wick-vs-body, stats, instrument choice, 5m/15m entry/exit playbook):
**[`research/Phase1_Gap_Retrace_Research.md`](research/Phase1_Gap_Retrace_Research.md)**

## Phase 2 findings (2-year validation, costs, coded rule, cBot)
- On the **full 2 years** the naive "fade every gap" is only **breakeven after costs** — the
  Phase-1 5.4-month edge was a favourable regime.
- The edge is real once filtered by mechanism: **weekday-only + gap ≥0.25% → +0.25R, 59% win,
  positive in 6/8 quarters.** **Weekend gaps LOSE the fade** (−0.12R) — skip them.
- **US cash-open (RTH) gaps** *do* exist and fill fast — reconstructed from the CFD by windowing to
  09:30-ET: US500 fills ~62% (median ~15 min), US30 ~65% (0–30 min); same "small fills / big runs".
- Ships a compilable **`cbot/GapFadeBot.cs`** implementing the exact rule with research defaults.
- ⚠️ Even the recommended config is **lumpy / regime-dependent** — a small edge, not a steady curve.

👉 Phase 2 write-up: **[`research/Phase2_Strategy_And_Validation.md`](research/Phase2_Strategy_And_Validation.md)**

## Layout
```
Gap-Retrace-Research/
├── README.md
├── research/Phase1_Gap_Retrace_Research.md   # the deliverable — read this
├── cbot/GapFadeBot.cs                         # compilable cTrader Automate bot (Phase 2)
├── data/                                      # saved cTrader bars (reusable)
│   ├── {GER40,US500,US30,NAS100,UK100,XAUUSD}_D1.csv   # 3y daily
│   ├── GER40_M15.csv / GER40_M5.csv                    # Phase 1 intraday
│   └── {GER40,US500,US30}_M15_2y.csv                   # Phase 2, 2y 15-min
├── scripts/
│   ├── ctrader_client.py     # persistent-connection cTrader MCP client
│   ├── fetch_daily.py / fetch_intraday.py / fetch_phase2.py   # downloaders
│   ├── analyze_gaps.py       # daily gap/fill/retrace statistics
│   ├── intraday_analysis.py  # GER40 intraday mechanics
│   ├── backtest_fade.py      # mechanical fade backtest (Phase 1)
│   ├── gapfade_strategy.py   # coded rule + walk-forward + sensitivity (Phase 2)
│   ├── rth_gap_study.py      # US cash-open (RTH) gap reconstruction (Phase 2)
│   └── make_charts.py / make_charts_phase2.py   # research figures
└── analysis/                 # generated outputs (txt stats + PNG figures)
```

## Reproduce
```bash
cd scripts
python3 fetch_daily.py && python3 fetch_intraday.py    # pull data (needs CTRADER_MCP_SLUG env)
python3 analyze_gaps.py && python3 intraday_analysis.py && python3 backtest_fade.py
python3 make_charts.py
```
Data CSV columns: `timestamp(ms), time(ISO), open, high, low, close, volume` — display prices.

## Status
- ✅ **Phase 1 — research & statistics**
- ✅ **Phase 2 — 2y validation, costs, US RTH gaps, coded rule, cBot** (`Phase2_Strategy_And_Validation.md`)
- ⏳ Phase 3 — compile/optimise the cBot on-platform, economic-calendar filter, US500 RTH bot variant,
  demo forward-test (see Phase 2 §7).
