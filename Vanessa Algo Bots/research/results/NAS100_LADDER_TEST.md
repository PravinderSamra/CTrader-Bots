# Risk-ladder test — NAS100

Ladder: ≥$104,000 → $500, ≥$98,000 → $400, ≥$95,000 → $300, ≥$0 → $200. Streak rule: one level lower after 4 losing days in a row, until the next winning day.

## CONTROL_rebuilt

### Replay of 2021–2026 from $100,000

| Policy | Final balance | Lowest balance | Room left above $90k at the low | Deepest drawdown | Average risk |
|---|---|---|---|---|---|
| fixed300 | $132,078 | $99,943 | $9,943 | $4,334 (4.3%) | $300 |
| fixed500 | $153,463 | $99,905 | $9,905 | $7,224 (7.2%) | $500 |
| ladder | $152,281 | $99,924 | $9,924 | $7,224 (7.2%) | $482 |
| ladder+streak | $150,020 | $99,924 | $9,924 | $6,870 (6.9%) | $467 |

### Next 12 months from today's $96,952.19 (5,000 simulated futures, 10-day blocks)

| Policy | Chance of hitting $90k | Median 12-month profit |
|---|---|---|
| fixed300 | 0.6% | $5,092 |
| fixed500 | 5.9% | $8,487 |
| ladder | 0.1% | $5,343 |
| ladder+streak | 0.1% | $5,010 |

## NB_0.7_x1

### Replay of 2021–2026 from $100,000

| Policy | Final balance | Lowest balance | Room left above $90k at the low | Deepest drawdown | Average risk |
|---|---|---|---|---|---|
| fixed300 | $137,337 | $100,000 | $10,000 | $5,145 (5.1%) | $300 |
| fixed500 | $162,229 | $100,000 | $10,000 | $8,574 (8.6%) | $500 |
| ladder | $160,666 | $100,000 | $10,000 | $8,574 (8.6%) | $482 |
| ladder+streak | $158,270 | $100,000 | $10,000 | $7,870 (7.9%) | $467 |

### Next 12 months from today's $96,952.19 (5,000 simulated futures, 10-day blocks)

| Policy | Chance of hitting $90k | Median 12-month profit |
|---|---|---|
| fixed300 | 1.2% | $5,925 |
| fixed500 | 8.8% | $9,875 |
| ladder | 0.2% | $6,061 |
| ladder+streak | 0.2% | $5,744 |

## NC_0.7_x2

### Replay of 2021–2026 from $100,000

| Policy | Final balance | Lowest balance | Room left above $90k at the low | Deepest drawdown | Average risk |
|---|---|---|---|---|---|
| fixed300 | $142,609 | $100,000 | $10,000 | $5,960 (6.0%) | $300 |
| fixed500 | $171,016 | $100,000 | $10,000 | $9,934 (9.9%) | $500 |
| ladder | $168,585 | $100,000 | $10,000 | $9,934 (9.9%) | $484 |
| ladder+streak | $166,284 | $100,000 | $10,000 | $9,136 (9.1%) | $468 |

### Next 12 months from today's $96,952.19 (5,000 simulated futures, 10-day blocks)

| Policy | Chance of hitting $90k | Median 12-month profit |
|---|---|---|
| fixed300 | 2.4% | $6,767 |
| fixed500 | 11.3% | $11,278 |
| ladder | 0.7% | $6,733 |
| ladder+streak | 0.5% | $6,386 |

