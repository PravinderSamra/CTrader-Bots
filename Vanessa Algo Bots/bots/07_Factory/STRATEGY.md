# Factory Bot, candidate A: "Index Bollinger Dip" (plain words)

The first strategy found by our Strategy Factory (research/factory). One generic cBot (Factory_Bot.cs) runs it;
future factory strategies use the same bot with different settings.

## Why should it work?
When a stock index has an unusually sharp fall (a daily close far below its normal range), forced and emotional
selling tends to overshoot, and prices usually recover part of it within a week. Big funds can't easily trade
this across 10 small index CFDs at once; we can.

## The rules
- Markets: 10 indices: US500, US100, US30, US2000, GER40, UK100, FRA40, EU50, AUS200, HK50 (FTMO .cash names).
- **Buy** when an index closes **below its 20-day Bollinger band at 2.5 standard deviations**
  (20-day average minus 2.5 x the 20-day standard deviation). The order goes 60 minutes after the next daily open.
- **Sell 5 daily bars later.** No take profit. No normal stop: tests showed a normal stop sells right before the
  bounce and kills the edge.
- **Disaster stop** at 10 x the average daily range (ATR 20) below entry, for a true crash. It has almost never been hit.
- One position per index; several indices can be held at once (sharp falls often hit several together).

## Size
"Risk Per R" = $200, where R = 2 x the average daily range. That means a normal bad trade loses about $200-400,
the worst trade in 16 years lost about $1,000 (5R), and the worst single day was about -$1,100 (5.6R).

## Factory test results (daily bars, costs and swap included)
- Build period (to 2020) +0.13R, confirm 2021-23 +0.32R, unseen 2024-26 +0.30R per trade.
- 2010-2026: 328 trades, 59% win rate, average +0.20R, worst drawdown 11.5R (about $2,300 at $200/R).
- About 24 trades a year. Correlation with Daily Systems +0.05, with the NAS bot about 0.
- Account Monte Carlo (NAS $550 + Daily Systems + this at $200/R): fail odds 16.8% -> 16.2%, passes ~6 days sooner.

## Tick backtest to run (confirmation step)
- cBot: Factory_Bot.cs (build it in cTrader as a new cBot called "Factory Bot").
- Attach to **US500.cash, Daily (D1)** chart. Leave all settings at their defaults.
- **Tick data from server**, **1 Jan 2021 to today**, balance 100,000, commission 30.
- If any symbol prints "Symbol not found" at the start, tell me its FTMO name.
- Send me the log (it ends with H| lines) and a screenshot of the results.

Pass if: profitable in both 2021-23 and 2024-26, at least 6 of the 10 indices positive, and the worst drawdown
under about $3,500. Then it can go live at HALF size ($100 per R) for its first 30 trades (QUANT_PROCESS.md stage 6).

## Switch-off rule (monthly review)
Pause if the last 50 trades average below -0.05R, or the drawdown passes $3,500 (1.5 x the backtest's worst).

## cTrader backtest result (14 Oct 2026, M1 bars, 1 Jan 2021 - 14 Oct 2026, $200/R, commission 30): PASS
- Net +$7,465, profit factor 1.92, 176 trades, 58% win, average +$42 a trade (about +0.21R).
- 2021-23: +$2,505 (104 trades); 2024-26: +$4,960 (72 trades). By year: 2021 +4,750, 2022 -1,444, 2023 -801,
  2024 +1,827, 2025 +1,182, 2026 +1,951.
- 8 of the 9 indices traded were positive (AUS200 -$230). US2000.cash does not exist at FTMO (skipped).
- Max balance drawdown 2.69% (~$2.8k), max equity drawdown 3.97% (~$4.2k, floating loss in the April 2025 sell-off);
  worst trade -$472, worst exit day -$508. Swap -$273, commission -$105.
- Versus the factory screen (2021-26: +0.31R): weaker (+0.21R), mainly 2022-23 (FTMO daily bars differ from the
  research feed). Still clearly positive in both halves.
- Decision: go live at HALF size, Risk Per R = $100, for the first 30 trades (QUANT_PROCESS stage 6).

## Disaster stop width and add-to-winner (14 Oct 2026, research/factory/stop_and_add.py, 2010-2026, 9 indices)
- 10 x ATR: +67.9R, max DD 9.8R, worst day -5.1R, hit once (Feb 2020). 8 x: +65.6R, DD 11.3R, worst day -4.7R.
  7 x: +59.5R, DD 15.9R, worst day -10.6R (5 hits). 6 x: DD 17.2R, worst day -12.1R. 5 x: DD 21.5R, worst day -17.7R.
  7 and 10 look the same in 2021-26 only because there was no crash; in a 2020-style crash a tighter stop sells
  several indices at the low on the same day. KEEP 10 x ATR (8 x is an acceptable alternative).
- Add to winner (add the same size after day 1 or 2 if up 0.5R): day 1 +65.1R, DD 17.3R, worst day -11.4R;
  day 2 +67.0R, DD 10.0R. Neither improves anything. REJECTED.

## v1.1 risk budget (14 Oct 2026)
Up to 9 indices can be open at once (12 days in 16 years). If every disaster stop hit on one day that would be
9 x 5R = 45R ($4,500 at $100/R, $9,000 at $200/R). v1.1 caps the total at "Max Full Positions" = 6: once open
positions add up to 6 full-size risks, new ones get the leftover share (or are skipped). 2010-2026: +58.3R (vs +67.9R),
max DD 9.1R (vs 9.8R), worst real day unchanged (-5.1R), absolute worst case 30R = $3,000 at $100/R.
Caps of 4 or 3 cost too much profit (+39.7R / +26.8R): the days many indices dip together are the best days.

## v1.1 cTrader backtest (14 Oct 2026, M1, 1 Jan 2021 - 14 Oct 2026, $200/R, commission 30): PASS
Net +$5,954 (v1.0: +$7,465), PF 1.74, 168 trades, 57% win, average +$35, largest loss -$472, max balance DD 2.90%,
max equity DD 4.09%. The cap cost ~20% of profit in a period with no crash (about $130 a year at the live $100/R);
it only pays off on a crash day. Accepted as insurance. GO LIVE at Risk Per R = $100 for the first 30 trades.
Log check: 2021-23 +$1,926 (99 trades), 2024-26 +$4,027 (69). By index: UK100 +1,527, GER40 +1,444, US500 +1,396,
HK50 +686, EU50 +666, US100 +536, FRA40 +324, US30 -31, AUS200 -596 (7 of 9 positive). 12 signals skipped because
the risk budget was full. AUS200 stays in (removing the one weak market after seeing results would be curve-fitting).

## Market list (14 Oct 2026)
FTMO also has US2000.cash and JP225.cash. Same rule, risk budget 6, 2010-2026: 9 indices +58.3R / DD 9.1R;
+US2000 +53.5R / DD 10.1R (US2000 alone -0.05R, 29 trades); +JP225 +55.3R / DD 12.0R (JP225 alone 28 trades,
negative to 2020). Both left out. Default Symbols = the 9 indices that passed the cTrader test.

## Weekend gap check and v1.2 (15 Oct 2026)
research/factory/weekend_gaps_fac.py, 9 indices 2014-2026: 99% of trades hold over a weekend (300 weekends).
Monday gaps averaged -0.033R each (-9.8R in total, t = -2.5); closing Friday and reopening Monday would have cost
about 2.5R in extra spread. Worst real weekends: Mar 2020 -4.3R (all positions), Apr 2025 -1.8R. Positions are
small when markets are wild, so a -7% to -9% gap cost only about 1R per position. Stress: -10% gap in a calm market
with 6 full positions is about -25R ($2,500 at $100/R, $5,000 at $200/R).
v1.2 adds "Flat Over Weekend" (default OFF, so live behaviour is unchanged): close at Friday 15:30 New York (a
market that shuts earlier closes in its last 45 minutes), reopen at the Monday order time with the same size and
stop, unless the exit rule fired on Friday's close.
PRE-REGISTERED TEST (written before any cTrader run; the Python result above was seen first, so cTrader decides):
v1.2 or later, US500.cash D1, defaults ($200/R), M1 bars, 1 Jan 2021 - 14 Oct 2026, balance 100,000, commission 30; once with Flat Over
Weekend = No and once with Yes. Adopt Yes only if net profit is at least 95% of the No run AND the max equity
drawdown is no higher. Otherwise keep No. The No run must match the v1.1 result, +$5,954 (sanity check).

## v1.3 crash-safe (15 Oct 2026)
Live only: saves waiting orders, weekend positions and each trade's signal day every minute (cTrader LocalStorage,
this computer), reloads them after a restart, makes a missed day's decisions straight away, and never trades the same
signal twice (checks History). Switched off in backtests, so backtest results are identical to v1.2.
Label default changed to BOLL (15 Oct 2026) so the trades are easy to recognise; older trades carry FAC-A.

## Weekend test RESULT (15 Oct 2026, v1.3, M1, 1 Jan 2021 - 14 Oct 2026, $200/R, commission 30): ADOPT FLAT OVER WEEKEND
| | Weekend = No | Weekend = Yes |
|---|---|---|
| Net profit | +$5,954 (matches v1.1 exactly) | +$7,291 (+22%) |
| Profit factor | 1.74 | 1.61 (more, smaller trade pieces) |
| Max balance / equity DD | 2.90% / 4.09% | 2.95% / 3.79% |
| Largest loss | -$472 | -$400 |
| 2021-23 / 2024-26 | +$1,926 / +$4,027 | +$2,010 / +$5,282 |
| Indices positive | 7 of 9 | 7 of 9 |
Pre-registered rule (>= 95% of profit and equity DD no higher): PASSED. Gains mostly in the European indices.
Log check: 167 weekend closes, 121 reopened, 46 not reopened (5-day exit fell on Friday's close), 289 pieces =
168 trades + 121 reopens; 12 risk-budget skips as before. HK50 closes Friday ~07:45 UTC, GER40/UK100 ~19:05,
AUS200 ~19:10, others 15:30 New York. 3 trades stayed open over a holiday weekend (market shut on the Friday:
Christmas 2022 UK100, 26 May 2023 HK50, Good Friday 2026 US100) - can't be avoided by a Friday rule; accepted.
Live setting: Flat Over Weekend = Yes (code default changed to true).
v1.3.1 (16 Oct 2026): save key fixed (letters/digits only; v1.3 keys with underscores were rejected by cTrader).
v-next (21 Oct 2026): logs R|gap when the timer stops for more than 5 minutes (laptop asleep/offline). Found after Daily Systems/Bollinger orders due 19 Oct ~23:00 UK went in at 16:24 UK on 20 Oct.
