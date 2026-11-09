# NQ/ES "SMT sweep into FVG" (Threads, mkx6itrade): pre-registered 9 Nov 2026, before any run
Claim: 1-2 trades a day, 55-65% win rate, 2.5-3R average winner (= roughly +0.9 to +1.6R a trade).
Data: FTMO US100.cash (NQ) and US500.cash (ES) 5-minute bars, Jul 2023 - Jul 2026 (the study data). Trade US100 only.
Times New York. Costs: 1.5 pts a round trip on US100.

Mechanical version (shorts shown; longs mirror):
1. Levels: previous day high (18:00-17:00 session) and overnight high (18:00 - 09:30).
2. Sweep: between 09:30 and 10:30 a US100 bar trades above one of those levels.
3. SMT: at that moment US500 has NOT traded above its own matching level (the "crack in correlation").
4. Displacement: within the next 6 bars a bearish 5-minute fair value gap forms (bar 1 low > bar 3 high).
5. Premium: the gap's midpoint sits in the upper half of the previous 4-hour candle (4h candles from 18:00).
6. Entry: sell limit at the gap's bottom edge, valid until 10:30. Stop 2 pts above the sweep high.
   Target 2.5R (the claimed average winner). Flat at 12:00. One trade a day. If the entry bar also reaches the
   stop, it counts as a loss (honest fills).
Trials (three in total):
 T1 rules 1-6.  T2 = T1 plus the 06:00 bias: if London (02-05) swept one side of Asia (20-00) and closed back
 inside, trade only in London's reversal direction; otherwise trade only against the overnight move (18:00 -> 09:30).
 T3 = T1 without the SMT check (shows whether SMT adds anything).
Pass (T1 or T2): avg >= +0.15R after costs, profit factor >= 1.3, >= 60 trades, positive in each of 2023H2-24,
2025, 2026H1, and better than T3. Win rate checked against the 55% claim.
