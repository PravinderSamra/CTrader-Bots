# Darren Winters weekly watch lists (tested 16 Oct 2026)
watchlists.json: 7 weekly emails, 1 Jul - 16 Oct 2026 (pasted by Vanessa). test_lists.py: start at the close of the first
trading day after the email; equal-weight UP minus DOWN after 0.2% costs; each side vs SPY / FTSE 100. Yahoo daily data.

## Result (6 lists with a month of data; results_2026_jul_oct.txt)
| | 1 week: UP - DOWN | 1 month: UP - DOWN |
|---|---|---|
| S&P 100 | -0.52% (positive 2/6) | -4.20% (positive 1/6) |
| FTSE 100 | -0.51% (2/6) | -6.10% (0/6) |
| FX | +0.16% (4/6) | +0.34% (4/6) |
US UP names lagged SPY after every list; UK DOWN names beat the FTSE after 4 of 6. FAIL so far. Caveat: only ~2 months of
independent data (the lists overlap), one market phase (Jul-Sep 2026), so "the opposite works" is NOT established either.
Next (pre-registered now): older lists as unseen data, testing both the original direction and the reverse (2 trials).

## Unseen test, Jan - Jun 2026 (19 lists; unseen_test.py, results_unseen_jan_jun.txt): FAIL both ways
| 1 month after each list | As intended (UP - DOWN) | Reversed |
|---|---|---|
| S&P 100 | +2.54% (12/19 positive), 95% range -2.0% to +8.1% | -2.94% |
| FTSE 100 | -1.30% (10/19) | +0.90% |
| FX | +0.07% (12/19) | -0.17% |
1-week results are similar noise (S&P +0.32%, FTSE +0.78%, FX -0.12%). Every one of 12 trials fails (none clears both
halves and a bootstrap range above zero). The Jul-Aug "reverse" pattern did not repeat. VERDICT: the lists carry no
measurable information; roughly a coin flip. Closed; older emails not needed. Data notes: stale tickers (MRW delisted
2021, RMG/IDS, DLG), S&P 400 names on an "S&P 100" list, BLND on both UK lists on 26 Mar 2026.
