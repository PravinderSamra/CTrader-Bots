# NAS100 — risk ladder vs risk from the room above $90k

Real cTrader logs, trigger 0.7, 2021-01-01 .. 2026-09-28. Every policy uses the 4-loss rule. room/N = (balance − $90k) ÷ N, between $100 and $1,500. 12-month figures: 5,000 simulated years from a fresh $100k, built from real 10-day blocks.

Risk per trade at different balances:

| Balance | ladder | ladder+ | room/25 | room/30 |
|---|---|---|---|---|
| $93,000 | $200 | $200 | $120 | $100 |
| $96,000 | $300 | $300 | $240 | $200 |
| $100,000 | $400 | $400 | $400 | $333 |
| $104,000 | $500 | $500 | $560 | $467 |
| $110,000 | $500 | $600 | $800 | $667 |
| $120,000 | $500 | $800 | $1,200 | $1,000 |
| $130,000 | $500 | $1,000 | $1,500 | $1,333 |

## Size 3 (total risk after add 1.6R)

| Policy | Replay 2021–26 final balance (no payouts) | Replay deepest drawdown | Replay worst day | 12 mo, no payouts: chance of $90k | typical profit | bad year (1 in 10) | 12 mo, monthly payouts: chance of $90k | typical payouts to you (80%) | bad year payouts |
|---|---|---|---|---|---|---|---|---|---|
| ladder | $173,983 | $10,404 | -$997 | 0.4% | $9,325 | $-2,885 | 0.6% | $7,591 | $1,055 |
| ladder+ | $229,180 | $21,698 | -$1,994 | 0.4% | $8,423 | $-2,907 | 0.6% | $7,591 | $1,055 |
| room/25 | $288,693 | $30,543 | -$2,992 | 0.0% | $7,368 | $-3,631 | 0.0% | $7,080 | $610 |
| room/30 | $278,845 | $30,543 | -$2,992 | 0.0% | $6,709 | $-2,839 | 0.0% | $6,142 | $665 |

## Size 5 (total risk after add 2.2R)

| Policy | Replay 2021–26 final balance (no payouts) | Replay deepest drawdown | Replay worst day | 12 mo, no payouts: chance of $90k | typical profit | bad year (1 in 10) | 12 mo, monthly payouts: chance of $90k | typical payouts to you (80%) | bad year payouts |
|---|---|---|---|---|---|---|---|---|---|
| ladder | $190,282 | $12,937 | -$1,340 | 1.5% | $11,352 | $-3,802 | 2.6% | $8,986 | $1,047 |
| ladder+ | $261,309 | $26,951 | -$2,680 | 1.5% | $9,964 | $-3,825 | 2.6% | $8,967 | $1,047 |
| room/25 | $334,643 | $38,002 | -$4,021 | 0.1% | $7,935 | $-4,627 | 0.1% | $8,151 | $429 |
| room/30 | $324,665 | $38,002 | -$4,021 | 0.0% | $7,496 | $-3,667 | 0.0% | $7,165 | $552 |

## Size 6.5 (total risk after add 2.65R)

| Policy | Replay 2021–26 final balance (no payouts) | Replay deepest drawdown | Replay worst day | 12 mo, no payouts: chance of $90k | typical profit | bad year (1 in 10) | 12 mo, monthly payouts: chance of $90k | typical payouts to you (80%) | bad year payouts |
|---|---|---|---|---|---|---|---|---|---|
| ladder | $202,801 | $14,835 | -$1,596 | 3.0% | $12,739 | $-4,650 | 5.6% | $9,934 | $1,016 |
| ladder+ | $286,183 | $30,943 | -$3,192 | 3.0% | $10,993 | $-4,698 | 5.6% | $9,925 | $1,016 |
| room/25 | $368,522 | $43,591 | -$4,789 | 0.3% | $7,938 | $-5,354 | 0.3% | $8,878 | $242 |
| room/30 | $359,657 | $43,591 | -$4,789 | 0.1% | $7,785 | $-4,294 | 0.1% | $7,885 | $482 |

## Size 10 (total risk after add 3.7R)

| Policy | Replay 2021–26 final balance (no payouts) | Replay deepest drawdown | Replay worst day | 12 mo, no payouts: chance of $90k | typical profit | bad year (1 in 10) | 12 mo, monthly payouts: chance of $90k | typical payouts to you (80%) | bad year payouts |
|---|---|---|---|---|---|---|---|---|---|
| ladder | $234,748 | $19,449 | -$2,195 | 8.1% | $16,023 | $-7,242 | 17.2% | $11,850 | $649 |
| ladder+ | $346,791 | $40,421 | -$4,390 | 8.2% | $12,485 | $-7,310 | 17.2% | $11,794 | $649 |
| room/25 | $444,912 | $57,225 | -$6,586 | 1.8% | $6,702 | $-6,809 | 2.8% | $10,026 | $0 |
| room/30 | $436,325 | $57,225 | -$6,586 | 1.0% | $7,403 | $-5,741 | 1.4% | $9,202 | $98 |

