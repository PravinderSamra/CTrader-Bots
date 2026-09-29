# Live review — FTMO challenge, bots switched on mid-August 2026 (data to 2026-09-28)

Source: TradeZella export `data/tradezella_2026-09-29.csv` (Aug 5 – Sep 28, bot and manual trades).

## Totals by playbook
| Playbook | Trades | Net |
|---|---|---|
| BOT - US500 ORB | 20 | −$1,884.08 |
| BOT - London Range Volume Breakout (US100) | 9 | −$68.75 (includes the 09-11 trade below) |
| Manual: NEWS Trading | 2 | −$1,359.37 |
| Manual: ORB JP225 | 6 | −$508.31 |
| Manual: INVERSE ORB US500 | 5 | −$160.65 |
| Manual: ORB US500 | 3 | +$235.75 |
| **All** | 45 | **−$3,745.41** |

## Data issues to resolve
1. **2026-09-11 08:30:06 US100 short, 15 lots, 1-second trade, +$257.10** is tagged as the range bot, but it was opened
   at the 08:30 ET CPI release. The bot only enters 10:00–11:00 ET, so it is almost certainly a manual news trade. Excluded below.
2. **US500 bot, 2026-08-25:** two trades in one day; the first opened at 09:44 ET (inside the 09:30–09:45 opening range)
   with 70 lots on a ~4.7-point stop. From 08-27 onwards the bot trades once a day at 09:55–12:05 ET, as in the backtest,
   so the settings on 08-25 appear to have been different.
3. **US500 bot, 2026-08-28:** loss of −$494 (≈1.65R at $300 risk), 20.1 points on 24.59 lots: about 8 points past the stop.
4. **US100 bot stop distances were 38–67 points.** The five-year backtest used a fixed 60-point stop. Losses of 38, 41, 45
   and 56 points cannot be a 60-point stop, so the live settings differ from the tested ones. Needs the `.cbotset` to confirm.
5. Risk per trade: US500 bot ≈ $300 (full losses cluster at −$296 to −$311); US100 bot 8.33 lots (≈$500 on a 60-pt stop)
   in August, 5 lots (≈$300) from September.

## Is the losing run normal?
**US500 bot:** 20 trades, −6.28R (1R = $300), 6 winners (30%) vs 50% in the backtest.
- Bootstrap from the 937 backtest first-trade-of-day results: a 20-trade stretch this bad happens about **5%** of the time
  (20 of 918 rolling 20-trade windows in the backtest were as bad or worse; worst was −9.06R).
- Without the two 08-25 trades (different settings): −4.54R over 18 trades, about **10%** of the time.
- Verdict: an unlucky patch at the edge of normal, not yet evidence the edge has gone. Watch the next 20–30 trades.

**US100 bot:** 8 genuine trades, **+0.09R** in total (−$326 in dollars because the two biggest losses were at the
August size). Backtest expectation ≈ +1.6R over 8 trades with a spread of roughly ±4R: fully normal.

**Gamma:** trade days were mostly mid/high gamma (SqueezeMetrics, prior-day tercile); far too few trades to read anything.

## FTMO exposure
Worst combined bot day so far ≈ −$594 (2026-09-16). At $300 per bot the bots' worst realistic day is ~0.6% of the
account, far inside the 5% daily limit. The largest single loss in the period was manual (NEWS Trading, 2026-08-12, −$1,531.75).
