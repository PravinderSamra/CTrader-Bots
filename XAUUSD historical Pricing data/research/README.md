# XAUUSD Pricing Research

Quant analysis of the 5-year 1-minute dataset in `../data/`, from the perspective of an intraday (1m/5m) trader.

## Read these

1. **`REPORT.md`** — full findings: data quality, regime shift, intraday structure, session stats, level statistics, and all backtest results with year-by-year tables.
2. **`STRATEGY-PLAYBOOK.md`** — the actionable distillation: ranked strategies with exact rules, the stats behind them, and the list of ideas that tested *negative* (equally important).

## Folder layout

```
research/
├── REPORT.md               ← full research report
├── STRATEGY-PLAYBOOK.md    ← actionable strategy rules, ranked by edge
├── scripts/                ← reproducible analysis (python3, pandas/numpy/matplotlib)
│   ├── 00_prep.py          data load, cleaning, resampling, quality audit
│   ├── 01_intraday_structure.py  vol/volume by hour & DOW, high/low timing, sessions
│   ├── 02_tendencies.py    autocorrelation, Asian range, prior-day levels, round numbers
│   ├── 03_backtests.py     strategy backtests S1–S4 (first pass)
│   ├── 04_overnight_decomp.py    24h drift decomposition + corrected S1/S4 + weekend gaps
│   └── 05_practical.py     stops/filters/TP variants, gap fills, regime table, charts
├── output/                 ← archived console output of each script (the numbers cited)
└── charts/                 ← price/ATR overview, intraday profile, equity curves
```

## Reproducing

```bash
pip install pandas numpy matplotlib
cd research/scripts
python3 00_prep.py && python3 01_intraday_structure.py && python3 02_tendencies.py \
  && python3 03_backtests.py && python3 04_overnight_decomp.py && python3 05_practical.py
```

Runtime ≈ 10–15 min total; a resampled cache is written to the session scratchpad on first run.
Note: `03_backtests.py` S1a–c and S4a contain a dealing-day keying bug (documented in REPORT §6); the corrected versions are in `04_overnight_decomp.py` — kept for transparency since S2/S3 results from 03 are valid and cited.

## Headline findings (TL;DR)

- **The edge:** ~all of gold's 5-year drift accrued **22:00–02:00 UTC** (t=5.45, positive every year). Systematic overnight long = Sharpe ≈ 1.6–1.9 after costs.
- **The active trade:** NY opening-range breakout (13:30+30m, structural stop, no TP, exit 20:00) ≈ +0.08R/trade, Sharpe ≈ 1.0.
- **The map:** 62% of days break exactly one side of the Asian range and close beyond it 70% of the time; full "Judas" reversals are only 18–23%. PDH/PDL touched 85.6% of days.
- **The trap:** tight stops flip breakout systems from + to −; bar-level momentum/mean-reversion is zero; ATR grew 6× over the sample — size off ATR or die.
