# NAS100 — risk ladder vs risk from the room above $90k

Real cTrader logs, trigger 0.7, 2021-01-01 .. 2026-09-28. Every policy uses the 4-loss rule. room/N = (balance − $90k) ÷ N, between $100 and $1,500. 12-month figures: 5,000 simulated years from a fresh $100k, built from real 10-day blocks.

Risk per trade at different balances:

| Balance | ladder | steepA | steepB | ladder+ | room/25 | room/30 |
|---|---|---|---|---|---|---|
| $93,000 | $200 | $100 | $100 | $200 | $120 | $100 |
| $95,000 | $300 | $200 | $100 | $300 | $200 | $167 |
| $96,000 | $300 | $200 | $200 | $300 | $240 | $200 |
| $97,000 | $300 | $300 | $200 | $300 | $280 | $233 |
| $98,000 | $400 | $300 | $300 | $400 | $320 | $267 |
| $100,000 | $400 | $400 | $400 | $400 | $400 | $333 |
| $104,000 | $500 | $500 | $500 | $500 | $560 | $467 |
| $110,000 | $500 | $500 | $500 | $600 | $800 | $667 |
| $120,000 | $500 | $500 | $500 | $800 | $1,200 | $1,000 |
| $130,000 | $500 | $500 | $500 | $1,000 | $1,500 | $1,333 |

## Size 3 (total risk after add 1.6R)

| Policy | Replay 2021–26 final balance (no payouts) | Replay deepest drawdown | Replay worst day | 12 mo, no payouts: chance of $90k | typical profit | bad year (1 in 10) | 12 mo, monthly payouts: chance of $90k | typical payouts to you (80%) | bad year payouts | From $96,952, monthly payouts: chance of $90k | typical payouts |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ladder | $173,983 | $10,404 | -$997 | 0.4% | $9,325 | $-2,885 | 0.6% | $7,591 | $1,055 | 1.8% | $4,442 |
| steepA | $173,983 | $10,404 | -$997 | 0.0% | $8,102 | $-2,979 | 0.0% | $6,253 | $578 | 0.0% | $2,807 |
| steepB | $173,983 | $10,404 | -$997 | 0.0% | $7,503 | $-3,088 | 0.0% | $5,715 | $248 | 0.0% | $1,728 |
| ladder+ | $229,180 | $21,698 | -$1,994 | 0.4% | $8,423 | $-2,907 | 0.6% | $7,591 | $1,055 | 1.8% | $4,442 |
| room/25 | $288,693 | $30,543 | -$2,992 | 0.0% | $7,368 | $-3,631 | 0.0% | $7,080 | $610 | 0.0% | $3,492 |
| room/30 | $278,845 | $30,543 | -$2,992 | 0.0% | $6,709 | $-2,839 | 0.0% | $6,142 | $665 | 0.0% | $2,668 |

## Size 5 (total risk after add 2.2R)

| Policy | Replay 2021–26 final balance (no payouts) | Replay deepest drawdown | Replay worst day | 12 mo, no payouts: chance of $90k | typical profit | bad year (1 in 10) | 12 mo, monthly payouts: chance of $90k | typical payouts to you (80%) | bad year payouts | From $96,952, monthly payouts: chance of $90k | typical payouts |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ladder | $190,282 | $12,937 | -$1,340 | 1.5% | $11,352 | $-3,802 | 2.6% | $8,986 | $1,047 | 4.9% | $5,774 |
| steepA | $190,282 | $12,937 | -$1,340 | 0.0% | $9,678 | $-3,735 | 0.0% | $7,460 | $512 | 0.2% | $3,737 |
| steepB | $190,282 | $12,937 | -$1,340 | 0.0% | $8,837 | $-4,032 | 0.0% | $6,487 | $1 | 0.0% | $2,350 |
| ladder+ | $261,309 | $26,951 | -$2,680 | 1.5% | $9,964 | $-3,825 | 2.6% | $8,967 | $1,047 | 4.9% | $5,774 |
| room/25 | $334,643 | $38,002 | -$4,021 | 0.1% | $7,935 | $-4,627 | 0.1% | $8,151 | $429 | 0.3% | $4,380 |
| room/30 | $324,665 | $38,002 | -$4,021 | 0.0% | $7,496 | $-3,667 | 0.0% | $7,165 | $552 | 0.1% | $3,586 |

## Size 6.5 (total risk after add 2.65R)

| Policy | Replay 2021–26 final balance (no payouts) | Replay deepest drawdown | Replay worst day | 12 mo, no payouts: chance of $90k | typical profit | bad year (1 in 10) | 12 mo, monthly payouts: chance of $90k | typical payouts to you (80%) | bad year payouts | From $96,952, monthly payouts: chance of $90k | typical payouts |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ladder | $202,801 | $14,835 | -$1,596 | 3.0% | $12,739 | $-4,650 | 5.6% | $9,934 | $1,016 | 8.8% | $6,638 |
| steepA | $202,801 | $14,835 | -$1,596 | 0.1% | $10,972 | $-4,320 | 0.2% | $8,192 | $445 | 0.7% | $4,444 |
| steepB | $202,801 | $14,835 | -$1,596 | 0.0% | $9,628 | $-4,300 | 0.0% | $6,989 | $0 | 0.2% | $2,864 |
| ladder+ | $286,183 | $30,943 | -$3,192 | 3.0% | $10,993 | $-4,698 | 5.6% | $9,925 | $1,016 | 8.8% | $6,607 |
| room/25 | $368,522 | $43,591 | -$4,789 | 0.3% | $7,938 | $-5,354 | 0.3% | $8,878 | $242 | 0.9% | $5,031 |
| room/30 | $359,657 | $43,591 | -$4,789 | 0.1% | $7,785 | $-4,294 | 0.1% | $7,885 | $482 | 0.4% | $4,218 |

## Size 10 (total risk after add 3.7R)

| Policy | Replay 2021–26 final balance (no payouts) | Replay deepest drawdown | Replay worst day | 12 mo, no payouts: chance of $90k | typical profit | bad year (1 in 10) | 12 mo, monthly payouts: chance of $90k | typical payouts to you (80%) | bad year payouts | From $96,952, monthly payouts: chance of $90k | typical payouts |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ladder | $234,748 | $19,449 | -$2,195 | 8.1% | $16,023 | $-7,242 | 17.2% | $11,850 | $649 | 21.8% | $8,440 |
| steepA | $234,748 | $19,449 | -$2,195 | 1.2% | $13,423 | $-5,963 | 2.1% | $9,585 | $90 | 3.5% | $5,835 |
| steepB | $234,748 | $19,449 | -$2,195 | 0.5% | $11,074 | $-4,987 | 0.7% | $8,139 | $0 | 1.2% | $3,695 |
| ladder+ | $346,791 | $40,421 | -$4,390 | 8.2% | $12,485 | $-7,310 | 17.2% | $11,794 | $649 | 21.8% | $8,359 |
| room/25 | $444,912 | $57,225 | -$6,586 | 1.8% | $6,702 | $-6,809 | 2.8% | $10,026 | $0 | 4.3% | $6,140 |
| room/30 | $436,325 | $57,225 | -$6,586 | 1.0% | $7,403 | $-5,741 | 1.4% | $9,202 | $98 | 2.3% | $5,347 |


## Current challenge: from $96,952, reaching $110,000 before $90,000 (NAS100 bot alone)

5,000 simulated futures from real 10-day blocks; about 9.2 trading days a month.

| Size | Rule | Pass | Fail | Median months to pass |
|---|---|---|---|---|
| 3 | ladder | 95.6% | 4.4% | 13.9 |
| 3 | steepA | 99.4% | 0.6% | 17.5 |
| 3 | steepB | 99.7% | 0.3% | 19.9 |
| 5 | ladder | 91.6% | 8.4% | 10.7 |
| 5 | steepA | 98.0% | 2.0% | 14.0 |
| 5 | steepB | 99.5% | 0.5% | 17.2 |
| 6.5 | ladder | 88.6% | 11.4% | 8.9 |
| 6.5 | steepA | 96.7% | 3.3% | 12.3 |
| 6.5 | steepB | 98.3% | 1.7% | 15.3 |
