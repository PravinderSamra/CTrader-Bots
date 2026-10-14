# Market Wizards traders: what can be tested (first sort, 14 Oct 2026)

Vanessa's list of 80 traders from the Market Wizards books (Jack Schwager). Sorted by whether their method is
rule-based enough to code and test on FTMO markets. To be used as building blocks for the strategy factory.

## A. Testable: published or well-known mechanical rules (start here)
| Trader | Book | Method to code |
|---|---|---|
| Richard Dennis + William Eckhardt | MW / New MW | Turtle system: 20/55-day breakouts, 2 x ATR stop, volatility sizing, pyramiding |
| Ed Seykota | MW | Moving-average trend following (EMA crossovers), "let profits run" |
| Tom Basso | New MW | Multi-market trend following with volatility-based position sizing |
| Larry Hite | MW | Trend following with strict per-trade risk (1%) |
| Linda Raschke | New MW | Holy Grail (ADX + 20 EMA pullback), Turtle Soup (false 20-day breakout), 80-20, Anti |
| Victor Sperandeo | New MW | 1-2-3 trend change, 2B top/bottom (failed new high) |
| Gil Blake | New MW | Short-term timing from statistical persistence (day-of-week, consecutive days) |
| Kristjan Qullamaggie | Next Gen | Momentum breakouts after tight bases, episodic pivots (EP already screened via Pradeep) |
| Mark Minervini | Stock MW | Trend template (price vs 50/150/200 MA) + volatility contraction breakout (stocks) |
| Jason Shapiro | Unknown MW | Contrarian to COT large-speculator extremes (free CFTC data, weekly) |
| Marsten Parker | Unknown MW | Systematic stock mean reversion / momentum systems |
| Tom Hougaard | Next Gen | DAX (GER40) intraday trend days, adding to winners |
| Pavel Krejci | Unknown MW | ALREADY LIVE: Daily Systems strategy A (mean reversion) |

## B. Partly testable: idea codeable, but key parts are judgement or need data we lack
William O'Neil / David Ryan (CAN SLIM: needs earnings data; base breakouts already failed on FTMO stocks),
Peter Brandt (classical chart patterns), Richard Bargh, Brent Penfold, Steve Lescarbeau (secret momentum system),
Monroe Trout (short-term statistical futures), Mark Weinstein, Al Weiss (long-term cycles), Robert Krausz
(Fibonacci: similar ideas already failed), Amrit Kaur, Daljit Dhaliwal, Michael Marcus, Randy McKay,
Jaffray Woodriff (machine learning: his "many models, test hard" approach is the strategy factory itself).

## C. Not testable for us: discretionary macro, fundamental equity, options, pit trading, psychology
Bruce Kovner, Paul Tudor Jones, Stanley Druckenmiller, Jim Rogers, Colm O'Shea, Ray Dalio, Michael Platt,
Steve Clark, Scott Ramsey, Bill Lipschutz, John Netto, Samantha LaDuc (macro); Michael Steinhardt, Stuart Walton,
Michael Lauer, Steve Cohen, Michael Masters, Steve Watson, Dana Galante, Ahmet Okumus, Larry Robbins,
Joel Greenblatt, Martin Taylor, Tom Claugus, Joe Vidich, Steve Mandel, Kevin Daly, Jeffrey Neumann,
Chris Camillo, Nate Michaud, Claudio Guazzoni (fundamental / small-cap / event-driven equity);
Tony Saliba, Mark Ritchie, Joe Ritchie, Blair Hull, Jeff Yass, John Bender, Mark D. Cook, Alphonse Fletcher,
Kris Abdelmessih, David Sun, Edward Thorp, David Shaw (options, market making, arbitrage);
Gary Bielfeldt, Tom Baldwin, Marty Schwartz, Amritpal Singh, Morad Askar (pit / order-flow scalping:
Askar's volume profile belongs in research/futures_lane); Jimmy Balodimas (discretionary counter-trend);
Van Tharp, Ari Kiev (psychology; Tharp's position-sizing ideas feed the size-ladder work).

Note: the C list is still worth reading for risk management and psychology, just not for bot rules.
