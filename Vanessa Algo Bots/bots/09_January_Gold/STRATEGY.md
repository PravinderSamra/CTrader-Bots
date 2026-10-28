# January Gold (plain words)

## Why it should work
Gold has been unusually strong in January: buying for Chinese New Year (jewellery and savings) and investors
rebalancing at the start of the year. FTMO XAUUSD 2012-2026 (research/screens/gold_seasonal.py, gold_january_robust.py):
January +3.7% on average after spread and swap, 11 of 15 years up (t = 3.4); every sub-window works (first half +2.2%,
second half +1.4%, 15 Dec - 31 Jan +4.4%); December, as a comparison, +0.2%. Other months averaged +0.4%.
The published 'autumn effect' (Sep + Nov) failed, and copper has no January effect; silver has a weaker one.

## The rules
- Buy XAUUSD at the first tradable moment of January (15 minutes after the market reopens after the holiday).
- Sell at the first tradable moment of February.
- Safety stop 7% below the entry (the deepest dip inside a January since 2012 was -5.4%).
- One trade a year; if the stop is hit it does not buy again that January.

## Size
"Notional ($)" = $20,000: a typical January +$750, the worst January since 2012 about -$580, the deepest dip during a
January about -$1,080, the stop about -$1,400. Swap for the month is included in the figures (~0.4%).

## Backtest to run in cTrader
- Attach January_Gold.cs to an XAUUSD, Daily chart. Defaults.
- M1 bars, as far back as cTrader allows (e.g. 1 Jan 2016) to today, balance 100,000, commission 30.
- Pass if: about +3% on average per January, most Januaries positive, and each trade opens in early January and closes
  on 1-2 February. Send the log (O|, C| and H| lines) and a screenshot.

## Switch-off rule
Pause if three Januaries in a row lose, or a single January loses more than 7% (the stop).
