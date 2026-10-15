# Pre-registered test: Daily Systems bot, written 14 Oct 2026

One cBot that runs several simple daily-bar systems on several FTMO instruments. Each system has an on/off switch and is
judged on its own; the portfolio is judged after. Sources: Pavel Kycek (A-C), Naoufel T (D), Turnaround Tuesday (E,
classic rule, Naoufel's AI example), Marcy Silver (F). Screening results are in IDEAS_BACKLOG.md (item 3, Naoufel, Marcy).

## Instruments (fixed now, not picked by results)
US500.cash, US100.cash, US30.cash, GER40.cash, XAUUSD. FX and oil are left out of the first test: A-E are long-only
systems that rely on the upward drift of stock indices and gold.

## Bars and timing
FTMO daily bars (D1). All signals use the bar that has just closed. Orders are sent 60 minutes after the new daily bar
opens (avoids the wide spreads around the daily rollover). "Close" below means the D1 close.

## Systems (all long-only except F)
A. Pavel mean reversion: close < SMA(5), and |close - SMA(5)| > 2.5 x its average over the previous 20 days, and
   close > SMA(200). Exit: close > SMA(5), or after 4 bars.
B. Pavel short-term momentum: today's high-low range > 2 x the average range of the previous 5 days, and close > open.
   Exit after 5 bars.
C. Pavel trend following: close > highest close of the previous 100 bars. Exit: close < SMA(10).
D. Naoufel RSI(2): close > SMA(200) and RSI(2) < 20. Exit: RSI(2) > 70.
E. Turnaround Tuesday: Monday's close < Friday's close -> buy; exit at Tuesday's close.
F. Marcy measured move (both sides, as screened in rizzy.py, daily version): swing points with 2 bars each side; swing
   high H1, swing low L1, lower swing high H2; trend line H1-H2; D = line value at L1 - L1; short at the bar confirming H2
   when H1 >= the 20-bar Bollinger middle line; stop H2; target L1 - D; only if reward >= 1 x risk; exit after 20 bars
   at the latest. Long = mirror. Screening: NAS +0.15 to +0.21R but nearly all from 2024; the weakest system, kept in
   because Vanessa asked for it. Judged like the others.
One position per system per instrument at a time. Systems are independent (A and D can both be long US500).

## Risk
- Catastrophe stop on every position (A-E): 3 x ATR(20) below entry; F uses its own stop.
- Sizing is set AFTER the development run by a fixed rule: equal notional per position, chosen so that the worst
  single day of the whole bot in the development period would have lost no more than $2,000 on $100k (leaves room for
  the live NAS bot inside FTMO's $5k daily limit). Hard cap: total open notional <= 1.5 x balance.
- Bot-level daily guard: if the bot's closed + open P/L for the day reaches -$2,000, close everything and stop opening
  trades until the next day.

## Costs
Backtests on cTrader with m1 bars from server and commission 0 (FTMO index and gold CFDs have no commission);
cTrader applies spreads and swaps (long swap on indices ~8%/yr: it matters for C, the system with the longest holds).
One tick-data run of the final version to confirm.

## Test
Development period: from the first FTMO data the backtester has (expected ~2021) to 2023-12-31. The only choices allowed
there, written here before the test run: which systems stay on, and the sizing per the rule above. No parameter changes.
Test period 2024-01-01 .. latest date: run once.

## Pass rules (per system, test period)
- At least 20 trades across the instruments, net positive after spread and swap, and average trade > 0 on at least
  3 of the 5 instruments.
- Portfolio: positive, max drawdown under 6% at the chosen size, and correlation of daily P/L with the live NAS bot
  below +0.3.
A system that fails is switched off. If no system passes, the bot is parked.

## Logs
Same style as the Stock Swing Scanner: S| (bars loaded per instrument), O| (open), X| (skipped, with reason),
H| (history at the end, with swap), D| (signal counts per system and instrument).

## Development run 1 (v1.0, 14 Oct 2026): FTMO data starts Nov 2020, so 2020-11-08 .. 2023-12-31, $20k per position
863 trades, net -$1,288 overall; per system (net, trades, win rate, per-instrument):
- A Pavel mean reversion: +$8,068, 58, 66%, positive on all 5 instruments. KEEP.
- D Naoufel RSI(2): +$8,195, 206, 66%, positive on the 4 indices, gold -$3,284. KEEP (instruments are not picked
  per system; gold stays in).
- B momentum: +$211, 49, 49%. OFF (no edge).
- C trend following: -$6,279, 108, 37% (swap -$1,493). OFF.
- E Turnaround Tuesday: -$1,573, 277, 45%. OFF.
- F Marcy measured move: -$9,910, 165, 25%. OFF.
The daily guard fired on 16 days and the notional cap blocked 156 entries: too many correlated longs at $20k each.
Largest losses (~$1,000-1,200) were the 3 x ATR catastrophe stops on US100 (RSI(2) entries before a further fall):
working as designed; the size will shrink them.
Next (sizing step, per the rule above): v1.1 logs each day's P/L (P| lines). Run A + D only, daily guard off
(set to 1,000,000), $20k per position, same period. Choose the notional so the worst day (lowest intraday point) would
have been <= $2,000, round down to the nearest $1,000. Then the single test run 2024-01-01 .. latest with the guard on.

## Sizing run (v1.1, A + D only, guard off, $20k per position, 2020-11-08 .. 2023-12-31)
cTrader summary: net +$20,728, profit factor 1.71, 263 trades, 188 winners (71%), swap -$1,837, max equity drawdown
6.97%, largest loss -$1,288. A: 62 trades, 69% win, +$8,288, positive on all 5 instruments. D: 201 trades, 72% win,
+$12,441 (gold -$2,837). By year (A + D): 2020 +$3.5k, 2021 +$20.3k, 2022 -$5.8k, 2023 +$2.8k (2021 carries it).
Worst day (lowest intraday point): -$2,959 (29 Jan 2021); next -$2,683, -$2,061.
Sizing rule: $20,000 x 2,000 / 2,959 = $13,517 -> round down -> **$13,000 per position**.
Expected at that size (scaled): about +$13.5k over 3.1 years (~4%/yr), max drawdown ~4.5%.
FINAL TEST (run once): v1.1, A + D on (B, C, E, F off), Notional 13,000, Daily Guard 2,000, cap 1.5,
2024-01-01 .. latest date, m1 bars, commission 0, $100k. Pass rules as above.

## Win/loss shape and live monitoring rule (added 14 Oct 2026, before the final test)
Sizing run: average win $265, average loss $389 (median $227 / $275). Break-even win rate = 389 / (265 + 389) = 59%;
actual 71%, a 12-point cushion. Typical of mean reversion: many small wins, fewer larger losses (29 losses beyond -$500
make up most of the total loss). The risk is a regime where the win rate falls under ~60% (2022 was that year).
If the bot goes live: switch it off (back to demo) if, over its last 50 trades, the win rate is below 62%, or if its
drawdown exceeds 1.5 x the backtest maximum at the chosen size (~7%).

## FINAL TEST RESULT (v1.1, A + D, $13k per position, guard $2k, 2024-01-01 .. 2026-10-13): PASS
cTrader: net +$15,924, profit factor 1.63, 324 trades, 238 winners (73%), swap -$990, max equity drawdown 4.76%,
largest win +$1,323, largest loss -$887, daily guard fired twice (-$2,004, -$2,103).
- A: 72 trades, 65% win, +$3,525; positive on GER40, US500, US100, US30 (gold -$261): 4 of 5. PASS.
- D: 252 trades, 76% win, +$12,399; positive on all 5. PASS.
- Every calendar year positive (2024 +$5.0k, 2025 +$6.4k, 2026 to Oct +$4.5k).
- Correlation of daily P/L with the live NAS bot: -0.01 (285 overlapping days). PASS. Drawdown 4.76% < 6%. PASS.
Next: demo ('incubation') before real money; check FTMO weekend-holding rule for the account type; confirm combined
worst day with the NAS bot stays inside the $5k daily limit.

## Weekend check (decided 14 Oct 2026, before any run)
Vanessa's account is an FTMO Swing account, so holding over weekends is allowed; the question is weekend gap risk
(a Monday gap can't be stopped by the daily guard). v1.2 adds 'Flat Over Weekend': close all at Friday 15:30 New York,
reopen at the Monday order time with the same size and stop unless the system's exit rule fired on Friday's close.
Runs (A + D, $13k, guard $2,000, m1 bars, commission 0): development period 2020-11-08 .. 2023-12-31 with the switch
off and with it on. Adopt weekend-flat only if it keeps >= 85% of the net profit AND lowers the max equity drawdown or
the worst day. Then one confirmation run of the chosen setting on 2024-01-01 .. latest using TICK data (real spreads);
it must still meet the pass rules.

## Gold review rule (14 Oct 2026)
Gold flips between periods (A: +$927 dev / -$261 test; D: -$2,837 dev / +$1,548 test; both near break-even combined at
$13k). Kept on in both systems. Review after 12 months of demo + live: switch gold off only if it lost in BOTH systems
while the indices were net positive.

## Queued after the weekend decision: profit-lock test (agreed 14 Oct 2026, rules written now)
Two switches, tested separately on 2020-11-08 .. 2023-12-31 only, against the chosen weekend setting:
(a) breakeven: move the stop to entry once the trade is up 1 x ATR(20);
(b) trailing: stop 2 x ATR(20) below the highest close since entry (never lowered).
Keep a switch only if it raises net profit OR lowers the max equity drawdown, AND the win rate stays >= 65%.
Expectation (Connors' RSI(2) research): neither helps a 2-5 day mean-reversion exit.

## Implementation fix v1.3 (14 Oct 2026, no rule change)
The first tick-data run (2020-23) aborted on 3 Dec 2020: a GER40 market order sent at 23:00 UTC, when FTMO's GER40 is
still closed, hung the tick backtest. On m1 bars cTrader had filled such orders anyway, so GER40 entries in earlier m1
runs used prices from before the market reopened. v1.3 sends orders, exits, weekend closes and guard closes only when
that market is trading (a tick in the last 2 minutes and >= 15 minutes since it reopened); otherwise they retry every
minute. All further runs (weekend pair, tick confirmation) use v1.3. The 2024+ tick confirmation run in the plan above
now also checks that the GER40 timing change does not alter the pass verdict.

## Weekend check result (v1.3, A + D, $13k, guard $2k, m1, 2020-11-08 .. 2023-12-31)
| | Hold over weekend | Flat over weekend |
|---|---|---|
| Net | +$13,969 | +$13,934 (99.7%) |
| Trades / win rate | 265 / 71% | 426 / 62% (each weekend splits a trade in two) |
| Swap | -$1,191 | -$679 |
| Max drawdown (daily closes / intraday) | $5,334 / $5,856 | $5,499 / $5,899 |
| Worst day, lowest point | -$1,926 | -$1,926 |
| Worst day, close | -$1,756 | -$1,355 |
Rule: adopt only if >= 85% of net AND lower max equity drawdown or worst day (lowest point, as used for sizing).
Net passes, but the drawdown is slightly higher and the worst day identical -> NOT adopted. Setting: hold over weekends.
(No large weekend gap hit the positions in 2020-23, so the test can't show the insurance value; profit was the same.)
Next: the plan's tick-data confirmation on 2024-01-01 .. latest with v1.3, Flat Over Weekend = No.

## Weekend gap risk study (14 Oct 2026, screens/weekend_gaps.py) -> decision changed to FLAT OVER WEEKEND = YES
History, Friday close -> Monday open, 1990-2026 (Yahoo cash opens; US500/US100 opens are unreliable in old data, so
GER40/US30 are the better guides): gaps of -5% or worse happened 1-4 times per index in 35 years, -7% or worse 1-3 times
(Mar 2020, Aug 2015 US100, Apr 2025 GER40 -9.2%, Aug 1991). Gold never gapped more than -3.4%.
Bot exposure held over weekends: median ~$25k notional, 90th percentile $64-75k, max ~$90k (both periods). Actual worst
Monday-gap result in the backtests: -$561 (the 200-day filter keeps it out of most crashes).
Stress: $90k held x -7% = -$6.3k; x -10% = -$9.0k. Either breaches FTMO's $5k daily limit, and with ~$8k of room to the
$90k floor today a -10% weekend would end the account. Rough odds: ~1% a year (rare gap x high exposure), but the cost of
avoiding it was ~zero in the weekend test (+$13,934 vs +$13,969).
DECISION (overrides the 'drawdown or worst day' test above, which could not see this tail because 2020-23 had no such
gap while positions were held): Flat Over Weekend = YES. Live off-switch counts a Friday-closed + Monday-reopened trade as
one trade for the win-rate rule.
Tick confirmation run on 2024-01-01 .. latest uses v1.3 with Flat Over Weekend = YES.

## TICK CONFIRMATION RESULT (v1.3, A + D, $13k, guard $2k, Flat Over Weekend = YES, TICK data, 2024-01-01 .. 2026-10-13): PASS
cTrader: net +$15,003 closed (+$14,793 equity, one position open), profit factor 1.46, 516 trade pieces (each weekend
splits a trade; merged = 317 trades, 73.5% win), swap -$633, commission 0, max equity drawdown 5.25% (balance 4.25%),
largest win +$1,255, largest loss -$673, daily guard fired once (5 Aug 2024, -$2,009). Avg win +$161 / avg loss -$268
(merged trades).
- A: 72 trades, 68% win, +$3,566; positive on GER40 (+$1,704), US100 (+$959), US500 (+$897), US30 (+$16); gold -$10. PASS.
- D: 245 trades, 75% win, +$11,437; positive on all 5 (US100 +$3,748, US500 +$2,691, GER40 +$1,948, gold +$1,549,
  US30 +$1,502). PASS.
- Every year positive (2024 +$3.5k, 2025 +$5.5k, 2026 to Oct +$6.0k). Worst day -$2,009 (the guard).
- Correlation of daily P/L with the NAS bot: -0.01 (285 overlapping days). Drawdown 5.25% < 6%. PASS.
- Versus the m1 final test (hold over weekends): 94% of the profit (+$15,003 vs +$15,924); the difference is real
  spreads plus the weekend closes. Swap fell from -$990 to -$633. GER40 timing (v1.3) did not change the verdict.
VERDICT: ready to run on the FTMO account next to the NAS bot with these settings. Live off-switch unchanged: back off if
the last 50 trades (weekend splits counted as one) win under 62%, or the drawdown passes 7%.
Still open: the NAS bot's worst day, to confirm the two bots' combined worst day stays well inside the $5k daily limit.
Next tests (2020-23 only, as agreed): profit-lock switches, then the size ladder.

## v1.4 sanity re-run (15 Oct 2026, tick, 2024-01-01 .. 2026-10-13, Flat Over Weekend = YES, commission 30)
Net +$15,346 closed, PF 1.47, 516 pieces, max equity DD 5.18%, largest loss -$681. Trade-by-trade against the v1.3 run:
all 516 trades identical (same system, market, entry and exit days); 29 GER40 sizes differ by 0.01 lot (EUR rate).
Dollar differences come from the run settings and data, not the code: commission $30 (-$495; the v1.3 run had 0),
swap rates updated by FTMO since (-$452 vs -$633), and slightly different tick fills (US100/US30/GER40 entries 2-5
points better). Crash-safe code confirmed to leave backtest decisions unchanged.

## Combined risk with the NAS bot (13 Oct 2026; NAS Add to Winner with Ladder backtest 2021-01-01 .. 2026-10-13, tick)
NAS backtest: +$282k on $100k, PF 1.41, 972 trades, 43% win, max equity DD 18% (risk ladder $650 -> $1,350 per trade).
Daily P/L in R saved to data/nas_bot_daily_R_2021_2026.json. Live risk now ~$550 per trade (9.16 lots x 60-pt stop,
balance $97,421).
- NAS worst day: -2.6R (-$1.4k at $550). Worst combined day with Daily Systems: -$2.5k at the close, -$2.6k counting
  Daily Systems' lowest point. Well inside the $5k daily limit. Correlation of daily P/L: +0.02 (640 days).
- The binding limit is the $90k floor, not the daily limit: NAS drawdowns at $550 risk reached -27R (-$14.9k,
  Sep-Nov 2022) and -22R (-$12.3k, Dec 2024-Mar 2025); worst 10 trading days -15R (-$8.3k). Room today: $7.4k.
- Pass-first odds from $97,421 (+$12,579 to $110k before -$7,421 to $90k), every 5th historical start day, NAS
  backtest is in-sample so treat as optimistic:
  NAS $550 + DS: 85%, median 125 trading days | NAS $550 alone: 88%, 162 days
  NAS $450 + DS: 89%, 165 days | NAS $350 + DS: 95%, 228 days | NAS $250 + DS: 100%, 369 days

## Monte Carlo (13 Oct 2026, scripts/monte_carlo.py)
Block bootstrap of real daily P/L (random 20-day blocks of consecutive days, so losing streaks and same-day pairing of
the two bots are kept), 20,000 runs from $97,421: pass at $110k, fail at the $90k floor or a day worse than -$5k.
Daily Systems = tick backtest daily P/L 2020-11..2026-10 ($13k per position); NAS = daily R 2021-26 x risk.
- Daily Systems alone: pass 93%, fail 3%, but median 809 trading days to pass (too slow on its own).
- NAS $550 + DS: pass 83%, fail 17%, median 124 days | NAS $550 alone: 83% / 17%, 148 days
- NAS $450 + DS: pass 88%, fail 12%, median 157 days | NAS $450 alone: 88% / 12%, 196 days
- NAS $350 + DS: pass 92%, fail 8%, median 204 days | NAS $350 alone: 93% / 7%, 275 days
Reading: Daily Systems barely changes the fail odds (it is uncorrelated and small) but cuts the time to pass by ~15-25%.
The fail risk comes from NAS drawdowns against the $7.4k of room. Same answer as the historical-start test (85%).
NAS backtest is in-sample, so real fail odds are likely higher (20-30%).

## Profit-lock test (13 Oct 2026, 2020-23 only, scripts/ds_profit_lock_tick.py) - RESULT: NO CHANGE
Method: the bot's own 2020-23 tick-backtest trades (266 trades, weekend legs joined, exact baseline +$14,479) replayed
day by day on D1 bars (Pepperstone D1 2019-23 saved in data/d1_2019_2023); a switch can only close a trade earlier.
Rule agreed in advance: keep a switch only if profit rises or max drawdown falls, AND the win rate stays >= 65%.
- Baseline: 72% win, +$14,479, max DD $4,892.
- BE at 1 ATR: 45% win, +$4,598 (-68%), DD $3,699 -> FAIL (win rate collapses).
- TRAIL 2 ATR: 64% win, +$6,580 (-55%), DD $4,673 -> FAIL.
- Sensitivity: every BE level (0.5/1.5/2 ATR) and trail (1.5/3 ATR) earns less than the baseline; a 3 ATR trail is
  closest (+$13,020) because it almost never fires.
Why: these are mean-reversion trades. Price often dips back below the entry after being up, then completes the bounce;
a tight lock sells those trades at breakeven or a small win. The bot's own exits already do the job.
(A Python re-creation of the rules on Pepperstone D1 bars, scripts/ds_profit_lock.py, gave a different baseline
(+$1.7k) because of data/bar timing, so it was not used for the decision.)
Next: size ladder (20-30% steps as the balance grows, never in drawdown).

## Size ladder test (14 Oct 2026, scripts/ds_size_ladder.py) - RESULT: KEEP FLAT $13k
The bot's own tick trades re-sized by each rule (2020-23 first, 2024-26 once). Keep only if profit per $ of max
drawdown does not fall and the worst day stays inside the $2,000 guard.
- Flat $13k: 2020-23 +$14,479, DD $5,069 (ratio 2.86); 2024-26 +$15,003, DD $4,495 (3.34).
- Ladder A (Umar: +25% per +$3k, step down after a $2k drawdown): 2020-23 size ran to 9x in the 2021 rally, then
  2022 losses at that size: DD $26,218, worst day -$8,672. 2024-26 DD $7,871. REJECT (far too aggressive).
- Ladder B (size in proportion to balance): +$15,203 / DD $5,927 (2.56) and +$15,864 / DD $4,677 (3.39), worst day
  -$2,139 / -$2,058. About the same as flat. REJECT (no real gain, slightly more risk).
Reading: on a 10% challenge account the account never grows enough for a ladder to matter, and a fast ladder adds
size just before losing spells. Re-size by hand only after a big balance change (e.g. funded account or payout).
