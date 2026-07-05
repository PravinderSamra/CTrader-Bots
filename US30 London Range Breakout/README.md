# US30 / NAS100 — London Range Breakout research

Research study into a post-London-range, US-open breakout day-trading strategy on the
US30 and NAS100, using 3 years of 5-minute cTrader data.

## TL;DR
- The strategy *as originally specified* (50pt stop / 100pt target, break from 09:30 ET)
  is **not viable** over 3 years.
- **Waiting until 10:00 ET**, requiring **high volume**, and using **wider stops with
  2.5–3.5R targets** makes it a **robust, every-year-profitable** edge.
- **NAS100 is the better instrument** (PF ~1.33–1.36, ~−12R drawdown, cleaner volume edge);
  US30 works too but with deeper drawdowns.
- **Read `docs/Final_Study_London_Range_Breakout.md` for the full study.**

## Layout
```
data/US30/      us30_m5.csv   (212,296 M5 bars, 2023-07 → 2026-07) + manifest.json
data/NAS100/    nas100_m5.csv (212,383 M5 bars) + manifest.json
scripts/        ctrader_client.py  download_data.py  sessions.py  backtest.py
                run_sweeps.py  volume_study.py  robustness.py  make_charts.py  rerun_45d.py
analysis/       all result CSVs + sweep/volume/candidate outputs + 45-day comparison
charts/         equity curves, risk heatmaps, volume win-rate charts
docs/           Phase1_Plan_and_Requirements.md   Final_Study_London_Range_Breakout.md
```

## Reproduce
```bash
pip install pandas numpy matplotlib
export CTRADER_MCP_SLUG=...            # already set in this environment
python scripts/download_data.py US30 NAS100   # (data already stored; only to refresh)
python scripts/run_sweeps.py US30 NAS100      # session + risk sweeps -> analysis/
python scripts/volume_study.py US30 NAS100    # volume investigation -> analysis/
python scripts/robustness.py                  # yearly walk-forward -> analysis/
python scripts/make_charts.py                 # -> charts/
```

Data is stored so any strategy pivot / re-analysis needs no re-download.
Notes: cTrader `get_trendbars` caps at 100 bars/call (range-mode only); volume is
**tick volume**, not contracts. See `../ctrader-mcp-integration-guide.md`.
