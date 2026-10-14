# Strategy Factory

Our own SQX-style generator, run through research/QUANT_PROCESS.md.
- `factory_d1.py`: building blocks (8 entry types, 3 filters, 5 exit types, long/short), honest simulator
  (signal at the close, fill at the next open, stop before target, costs + swap), market groups.
- `run_factory.py`: generates every combination (2,208 per group, 8,832 in v1) and applies the pre-registered
  pipeline: build-period bar -> parameter neighbours + doubled costs -> confirm 2021-23 -> de-duplicate.
- `checks_v1.py`: edge over "always in the market" with the same exit + correlation with the live bots.
- `holdout_v1.py`: the one-time 2024-26 check of the shortlist.

## v1 results (14 Oct 2026, daily bars, 28 markets in 4 groups)
- 8,832 strategies -> 34 after confirm + de-duplication -> 29 positive on the 2024-26 holdout.
- Survivors are almost all LONG MEAN REVERSION ON INDICES (buy a close below the lower Bollinger band / RSI(2)
  dip / false 20-day breakdown, exit after N days). FX: weak, metals and energy: nothing survived confirm.
- Edge over always-in with the same exit: +0.10 to +0.37R per trade. Correlation with Daily Systems 0.03-0.24,
  with the NAS bot about 0.
- 20-day holds have large drawdowns (BB2.0 none TIME20: max DD 56R, worst trade -8R in Feb 2020).
  5-day holds are the prop-firm-friendly ones:
  BB2.5|none|TIME5|L: 328 trades 2010-26, +0.21R, max DD 11.5R, worst trade -3.4R; holdout +0.30R (95% low +0.09).
  BB2.0|trend|TIME5|L: 338 trades, +0.21R, max DD 11.0R, worst trade -3.1R; holdout +0.16R (95% low +0.02).
Next: portfolio Monte Carlo with the live bots, then one generic factory cBot for a cTrader tick test.

## v2 results (15 Oct 2026, 4-hour and 1-hour bars, 20 markets 2014-2026, 9,504 strategies)
- Pre-registered pipeline (run_factory_h.py). Survivors: H4 indices 0, H4 FX 0, H4 commodities 1, H1 all groups 0.
- The one survivor (H4 BRK100 London-hours short on gold/silver/oil, 3-bar hold: build +0.16R, confirm +0.13R,
  ~57 trades a year, NAS corr 0.00) FAILED the 2024-26 holdout: -0.09R on 146 trades.
- Across all 9,504: only ~75 were positive in both build and confirm, about what chance alone produces from that
  many tries. Best near-misses (H4 index Bollinger dip in London hours, H4 FX false breakouts) are not adopted:
  loosening the bar after seeing them would be data-mining.
- Reading: simple technical building blocks have no robust edge after costs on 1-hour / 4-hour CFD bars. Higher
  frequency needs structural ingredients (session/auction structure like the NAS opening range, documented
  calendar/flow effects, order flow), not more indicator combinations.
