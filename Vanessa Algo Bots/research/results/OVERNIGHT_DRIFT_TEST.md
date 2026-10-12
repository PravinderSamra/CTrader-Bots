# Overnight drift ("buy the close, sell the open") on FTMO: closed

Checked 12 Oct 2026. Idea: index gains come mostly overnight (Cliff, Cooper & Gulen; Boyarchenko, Larsen & Whelan).
Data: cTrader m5 (NAS100, US30, GER40, UK100) and H1 (JP225), July 2023 to July/Oct 2026, a rising market throughout.
Overnight = from the cash close to the next cash open of each index.

## Where the gain was made
| Index | Overnight | Daytime | Share overnight | Overnight per year (= break-even swap) |
|---|---|---|---|---|
| NAS100 | +78.8% | +10.1% | 86% | 19.4% |
| GER40 | +43.2% | +13.1% | 74% | 11.5% |
| US30 | +23.6% | +24.5% | 49% | 7.1% |
| UK100 | +14.3% | +24.7% | 38% | 4.3% |
| JP225 | +107.7% | -1.7% | 102% | 22.4% |

## FTMO costs (swing account, from cTrader Symbol info)
| | Swap long (pts/contract/night) | As a yearly rate | Spread | Note |
|---|---|---|---|---|
| US100.cash | -6.99 | 8.2% | 0.65 | USD, no conversion fee |
| GER40.cash | -4.50 | 6.4% | ~1-2 | EUR: 0.70% P&L conversion fee |
| JP225.cash | -9.33 | 4.9% | ~10 | JPY: 0.70% P&L conversion fee |
Swap is charged at 20:59 UK on every position open at that time, triple on Friday. Weekend swaps disabled.

## Net of FTMO costs (1x the account in size)
- NAS100: +38% over 3 years (about 11% a year).
- GER40: +9 to +13% (about 3-4% a year); lost in 2 of 4 part-years.
- JP225: +45 to +60% (about 11-14% a year), but max drawdown 22.7% and a worst night of -8.4% (4-7 Apr 2025).
- US30, UK100: overnight return below the swap.

## Verdict: closed
On FTMO the overnight hold is a long-only index bet with gap risk. The $5k daily limit and the $90k floor cap the size
at well under 0.5x the account (JP225's worst night alone would breach both at 1x), which leaves a few % a year at best,
and the sample is a bull market only. Not pursued. Lesson kept: the NAS bot's 15:50 NY close (20:50 UK) avoids the
20:59 swap entirely; non-USD indices carry a 0.70% P&L conversion fee that every future backtest must include.
