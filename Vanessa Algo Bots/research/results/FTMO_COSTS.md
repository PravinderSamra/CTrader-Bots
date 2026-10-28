# FTMO real costs by market (Cost Scanner, tick backtest 27 Sep - 27 Oct 2026; results/FTMO_COST_SCAN_2026-10.log)
Round-trip spread as % of a normal day's range (20-day average high-low), cheapest UTC hours. Commission from FTMO's
published schedule (scanner's figure is the backtest setting, not reliable): indices $0, FX ~$5/lot round turn
(~0.43 bp), metals small. Non-USD indices also pay a 0.70% currency-conversion fee on profit/loss.
Swap is a fixed amount per unit, so as %/yr it changes with price (gold: 6.5%/yr at $4,060, 14%/yr at $1,830).

| Market | Spread | % of price | Day range | Cost % of range | Swap long / short %/yr | Note |
|---|---|---|---|---|---|---|
| US100 | 1.45 | 0.005% | 1.77% | 0.3% | -9.0 / +0.3 | NAS bot, Daily Systems, FOMC |
| US30 | 2.1 | 0.004% | 1.15% | 0.3% | -9.0 / +0.3 | cheap, little used |
| GER40 | 1.2 | 0.005% | 1.31% | 0.4% (+0.7% fee) | -7.2 / -0.7 | EUR conversion fee |
| UK100 | 0.8 | 0.007% | 1.16% | 0.6% (+0.7% fee) | -7.6 / -1.1 | GBP conversion fee |
| JP225 | 10 | 0.016% | 2.58% | 0.6% (+0.7% fee) | -5.6 / -2.3 | JPY conversion fee |
| XAUUSD | 0.40 | 0.010% | 1.67% | 0.6% | -6.5 / -0.4 | cheap intraday |
| US500 | 0.6 | 0.008% | 1.02% | 0.8% | -8.9 / +0.2 | |
| EURUSD | 0.1 pip | 0.001% | 0.61% | ~0.9% incl. commission | -3.3 / +0.2 | cheapest to HOLD |
| USDJPY | 0.3 pip | 0.002% | 0.55% | ~1.1% incl. commission | +1.0 / -4.7 | |
| GBPUSD | 0.3 pip | 0.002% | 0.55% | ~1.2% incl. commission | -1.7 / -1.0 | |
| AUS200 | 1 | 0.011% | 1.13% | 1.0% (+0.7% fee) | -10.1 / +0.5 | |
| EU50 / HK50 / FRA40 | | 0.019-0.026% | 1.2-1.7% | 1.5-1.7% | | expensive |
| USOIL / UKOIL | 0.07 | 0.06-0.07% | 3.5-3.7% | 1.6-1.9% | +3.2 / -19.1 ; +16.0 / -74.7 | longs EARN swap |
| US2000 / XAGUSD | | 0.03-0.08% | 1.5-3.5% | 2.2% | -9.0 ; -10.6 | expensive |
| BTC / ETH | | | 2.5-3.9% | (FTMO commission ~0.0325%) | -30 / -30 | very expensive to hold |
| NATGAS | 0.06 | 2.1% | 4.8% | 43% | -256 / +58 | untradeable |

Takeaways: cheapest to trade intraday = US100, US30, GER40, XAUUSD (then US500, UK100). Cheapest to HOLD for days/weeks =
major FX pairs (swap within +/-5%/yr, often near zero) and index SHORTS; index/gold LONGS cost 6.5-10%/yr. Avoid NATGAS,
silver, US2000, HK50, FRA40, EU50 and crypto. January Gold correction: at today's gold price its swap is ~6.5%/yr (~$110 a
January at $20k), not 14%; recomputed 2021-26 net ~ +$1,850 (3 up / 3 down) - still fails "most Januaries up".
