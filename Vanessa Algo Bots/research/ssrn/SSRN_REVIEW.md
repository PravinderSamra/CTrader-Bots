# SSRN / academic effects review (15 Oct 2026)

Rules taken from the papers, written down before testing, no tuning. FTMO costs: 0.025% spread+commission per round
trip, swap 5%/yr per night. Split 2014-20 / 2021-23 / 2024-26. Pass: positive net in all three, avg >= +0.05% a trade.

| Effect (paper) | Net per trade | 2014-20 | 2021-23 | 2024-26 | Verdict |
|---|---|---|---|---|---|
| Overnight drift (Cliff, Cooper & Gulen) | tested 12 Oct | | | | closed: FTMO swap eats most of it |
| FX 4pm fix reversal (Krohn et al.) | tested 29 Sep | | | | closed: gone after 2018 |
| Last-half-hour momentum (Gao et al.; Baltussen et al.) | tested 29 Sep | | | | closed: ran backwards |
| Turn of the month, 9 indices (Lakonishok & Smidt; McConnell & Xu) | -0.054% (1,317) | -0.137% | +0.019% | +0.058% | FAIL (gross only +0.07%) |
| Option-expiry week, US indices | -0.034% (427) | +0.093% | -0.567% | +0.227% | FAIL |
| European-open hour, US indices (Bondarenko & Muravyev) | -0.013% (9,449) | -0.006% | -0.027% | -0.014% | FAIL (gross +0.012%/day) |
| **Pre-FOMC drift (Lucca & Moench 2015)**, 9 indices | **+0.137% (814)** | +0.084% | +0.347% | +0.014% | **PASS (weakening)** |
| Pre-FOMC drift, NAS100 | **+0.218% (97)** | +0.131% | +0.476% | +0.138% | **PASS** |
| Pre-FOMC drift, US500 | +0.141% (97) | +0.119% | +0.299% | +0.021% | PASS (weak lately) |
| Pre-FOMC drift, US30 | +0.092% (97) | +0.115% | +0.144% | -0.017% | FAIL in 2024-26 |

Pre-FOMC rule: long from 14:00 New York on meeting day 1 to 14:00 New York on announcement day (just before the
statement), scheduled meetings only (fomc_drift.py, dates from federalreserve.gov).
Reading: the pre-FOMC drift is the one documented effect still alive on FTMO CFDs, but it is 8 events a year and
smaller in 2024-26. It is a small add-on, not an income engine. Everything else has faded after publication
(McLean & Pontiff 2016) or is eaten by CFD costs.
