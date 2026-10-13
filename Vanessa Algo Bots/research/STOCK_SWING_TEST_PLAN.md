# Pre-registered test: daily stock swing bot (Clement Ang / Oliver Kell price cycle), written 12 Oct 2026

Source: Clement Ang, Chart Fanatics (US Investing Championship). Long setup first; the short mirror is a later test.

## Universe (fixed by rule, not by picking winners)
All US stocks FTMO offers (46, Oct 2026): AAPL, AMZN, BA, BABA, BAC, CSCO, CVX, DIS, META, FDX, GE, GM, GOOG, IBM, INTC,
JNJ, JPM, KO, MCD, MSFT, NFLX, NVDA, PFE, QCOM, RACE, T, TSLA, V, WMT, XOM, ZM, RTX, LMT, PLTR, AMD, AVGO, SBUX, MSTR, GME,
NKE, ARM, SNOW, ASML, AZN, BRK.B, SPCX. European stocks excluded (EUR, 0.70% conversion fee, different session).
Known bias: this is today's list, so recent winners are over-represented. Treat a pass with extra caution.

## Rules (daily bars, evaluated after the US close; benchmark US100.cash)
Eligible stock on day t:
1. Close > 200-day SMA, and the 200-day SMA is higher than 20 days ago.
2. ADR (average of daily high/low - 1, last 20 days) >= 3%.
3. Wedge pop in the last 15 days: a close above both the 10 and 20 EMA, after closing below the 20 EMA within the 5 days
   before it, on volume >= 1.5x the 50-day average.
4. Base: last 5 days' high-low range <= 1.5x ADR in price terms; closes stay above the 20 EMA; 5-day average volume below
   the 50-day average.
5. Relative strength: stock/US100 ratio within 5% of its 50-day high.
6. No position already open in the stock.
Entry: buy-stop at day t's high + 0.1% (valid for day t+1 only; cancelled if not filled). Stop: day t's low - 0.1%.
Skip if the stop distance is more than 1x ADR.
Size: fixed risk per trade (same $ amount). Max 4 open positions; max total open risk 4x one trade.
Exits: sell 1/3 when profit >= 2x ADR (then stop to break-even); sell 1/3 when the close is > 10 ATR(14) above the 50-day
SMA; sell the rest on a daily close below the 10 EMA. Initial stop always active.
Costs (FTMO Symbol info, NVDA, 12 Oct 2026): commission 0.00%; spread ~$0.11 at $225 (0.05%); lot = 1 share, min 1 share;
swap long -$0.0528/share/night (~8.4%/yr), short -$0.0418, triple on Friday, charged 20:59 UTC; CFD hours 13:35-20:00 UTC.
Backtests use cTrader tick data, so spread and swap are applied by cTrader. Note: volume rules use CFD tick volume.
Earnings: not filtered in the first test (no calendar); measured afterwards from gap days.

## Test
Tune nothing on 2024-26. Development period 2021-01-01 .. 2023-12-31: only these may change there, once each, and
the choice is written here before the test run: wedge-pop volume multiple (1.5 / 2.0), base length (5 / 10 days).
Test period 2024-01-01 .. 2026-09-30: run once.

## Pass (test period)
Expectancy >= +0.25R per trade after costs; profit factor >= 1.3 with the best 5 trades removed still > 1.0;
at least 60 trades; profitable in at least 2 of 2024, 2025, 2026; correlation of daily P/L with the NAS bot < 0.3.

## Data check (agreed 13 Oct 2026)
First run 2020-23 on tick data (commission 0). Then the same run on m1 bars from server with a fixed 5-pip ($0.05) spread.
If net P/L, trade count and win rate agree within a few percent, later runs of this bot (and other daily stock bots) use m1.
Intraday-entry bots (NAS bot, capitulation bot VWAP entries) stay on tick data.

## Amendment (14 Oct 2026, before any trade results were seen)
First runs (tick and m1, 2020-23 requested) showed:
- FTMO stock data in the backtester starts 3 Jan 2022 (about 300 daily bars of history load before that, so the
  210-bar warm-up is fine). META, RTX, LMT, ARM, SPCX had no data at the start; the chart symbol (NVDA) got no history.
- Zero trades. Funnel over 2022-23 (stock-days): trend filter 13,020 (2022 bear market), ADR < 3% 6,062,
  no wedge pop 929, base checks 266, valid setups 1 (gapped above the trigger).
Changes:
1. Min ADR 3% -> 2%. The 3% figure comes from small/mid-cap traders (Kell, Ang). FTMO's list is mega caps: median ADR
   2022-23 is 2.4% and only 34% of stock-days reach 3% (Yahoo data). 2% keeps two thirds of stock-days. This is a
   universe correction, not a fit to results (there are no results yet).
2. Bug fix: relative strength compared each stock's close with the benchmark's previous-day close (FTMO daily bars
   open the evening before). Fixed in v1.2.
3. Attach the bot to a chart that is not in the symbol list (US100.cash, Daily).
4. Test periods: in-sample 2022-23 (FTMO data starts 2022), out-of-sample 2024-26 run once. m1 bars with commission 0;
   one tick-data run of the final version to confirm.
All other rules unchanged.

## Amendment 2 (14 Oct 2026, implementation fix, no rule change)
Run 3 (v1.2, 2022-23, m1): 9 valid setups, but 7 were skipped as 'gapped above trigger' and none traded. Checked against
Yahoo daily data: 4 of those 7 did NOT gap (real open below the trigger, 3 of them traded through it). Cause: the bot judged
the setup on the first tick of the new daily bar, which in winter is pre-market (13:35 UTC = 08:35 New York) with a wide
spread. v1.3: entries and daily-close exits are executed at 09:31 New York time; if price is already above the trigger the
bot buys at market (the plan's buy-stop would have filled at the open), still subject to the max-stop (1 x ADR) rule.
Expect few trades: about 4-5 setups a year on FTMO's mega-cap list.

## Amendment 3 (14 Oct 2026) - rules frozen
Run 4 (v1.3, 2022-23): 8 valid setups; 2 trades (AVGO, both stopped, -1R each); 6 skipped by the max-stop rule, 4 of them
marked 'gapped'. INTC was marked gapped on days its real open was below the trigger, so the 09:31 Ask was still inflated by
the opening spread. v1.4: decision at 09:35 New York, 'gapped' judged on Bid, X| lines log bid/ask/trigger.
With ~4 setups a year a 2022-23 in-sample run cannot guide any choice, so the rules are now frozen and the single
evaluation is one run over all FTMO data, 2022-01-01 to the latest date (m1 bars, commission 0). Verdict rule: keep the bot
only if it is net positive after swaps with at least 15 trades; otherwise park it.

## Verdict (14 Oct 2026): PARKED
Final run, v1.4, 2022-01-01 .. 2026-10-13 (m1, commission 0): 43 valid setups, 16 trades, 2 winners (MSTR, JPM),
net -$3,706 on $300 risk per trade (about -12R). Fails the pass rule (>= 15 trades AND net positive).
Two defects seen in passing, not fixed because the bot is parked: one position (GM, 3 Nov 2025) opened with no stop,
and BRK.B lost 3x its planned risk (gap through the stop). Rules were frozen before the run; nothing to tune.
Takeaway: Kell/Ang's price-cycle breakouts need fast small/mid caps; FTMO's mega caps rarely set up and fail when they do.
