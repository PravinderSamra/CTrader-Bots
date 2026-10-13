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
