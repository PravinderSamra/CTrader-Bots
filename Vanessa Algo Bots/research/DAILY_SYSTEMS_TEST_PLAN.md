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
