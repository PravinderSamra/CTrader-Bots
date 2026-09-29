# NAS100 Add To Winner — how far can the add size go? (2026-09-29)

Method: add profits scale exactly with Add Size (real runs: $5,259 / $10,532 / $15,796 for sizes 1/2/3), so larger
sizes are simulated from the size-1.0 log as main + k × add. Validated against the real size-3 run: $15,778 vs $15,796,
every day within $4. Trigger 0.7, risk reduction 70% at 0.7R. NAS100 bot alone.

| Add size | Total risk after add | 2021–26 profit at $500 | Costliest losing run at $500 | Worst day at $500 | Ladder from $100k: chance of $90k in 12 mo | Typical 12-mo profit | Bad year (1 in 10) |
|---|---|---|---|---|---|---|---|
| 0 | 0.70R | $53,463 | $7,224 | −$692 | 0.0% | $6,511 | −$1,988 |
| 1 | 1.00R | $62,229 | $8,574 | −$692 | 0.0% | $7,612 | −$2,377 |
| 2 | 1.30R | $70,994 | $9,924 | −$826 | 0.1% | $8,713 | −$2,786 |
| 3 | 1.60R | $79,760 | $11,287 | −$997 | 0.3% | $9,861 | −$3,134 |
| 4 | 1.90R | $88,525 | $12,659 | −$1,168 | 0.7% | $10,943 | −$3,786 |
| 5 | 2.20R | $97,291 | $14,031 | −$1,339 | 1.6% | $11,839 | −$4,373 |
| 6 | 2.50R | $106,056 | $15,402 | −$1,509 | 2.4% | $12,878 | −$4,862 |
| 6.5 | 2.65R | $110,439 | $16,088 | −$1,595 | 3.1% | $13,239 | −$5,241 |
| 8 | 3.10R | $123,587 | $18,146 | −$1,851 | 5.2% | $14,659 | −$5,919 |
| 10 | 3.70R | $141,119 | $20,890 | −$2,192 | 9.2% | $16,683 | −$8,230 |

Ladder: ≥$104k → $500, ≥$98k → $400, ≥$95k → $300, below → $200. Monte Carlo: 4,000 futures, 10-day blocks.
Sizes above 4.33 need "Max Total Risk" raised to at least the "total risk after add" value.

Notes: yearly floor risk compounds (9.2% a year ≈ 25% over 3 years). Figures exclude the US500 bot; the combined
account needs its own risk budget (suggested: ≤ 2–3% a year chance of hitting $90k).
