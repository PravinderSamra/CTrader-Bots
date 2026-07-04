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

👉 Full write-up (theory, wick-vs-body, stats, instrument choice, 5m/15m entry/exit playbook,
backtest, caveats): **[`research/Phase1_Gap_Retrace_Research.md`](research/Phase1_Gap_Retrace_Research.md)**

## Layout
```
Gap-Retrace-Research/
├── README.md
├── research/Phase1_Gap_Retrace_Research.md   # the deliverable — read this
├── data/                                      # saved cTrader bars (reusable)
│   ├── {GER40,US500,US30,NAS100,UK100,XAUUSD}_D1.csv   # 3y daily
│   ├── GER40_M15.csv    # 5.4 months, 15-min
│   └── GER40_M5.csv     # 6 weeks, 5-min
├── scripts/
│   ├── ctrader_client.py     # persistent-connection cTrader MCP client
│   ├── fetch_daily.py        # download 3y D1 for 6 instruments
│   ├── fetch_intraday.py     # download GER40 M15 + M5
│   ├── analyze_gaps.py       # daily gap/fill/retrace statistics
│   ├── intraday_analysis.py  # GER40 intraday mechanics
│   ├── backtest_fade.py      # mechanical fade backtest
│   └── make_charts.py        # research figures
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
- ✅ **Phase 1 — research & statistics** (this folder)
- ⏳ Phase 2 — longer history + costs, US RTH cash-open gaps, coded confirmation rule, cBot skeleton
  (see §9 of the write-up).
