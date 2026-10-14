# Our quant process: from idea to live bot (agreed 14 Oct 2026)

Goal: a portfolio of bots that pays an income through prop firms, built the way a professional quant desk works,
sized for one person's time. Every new strategy (playbooks, Market Wizards, SSRN papers, strategy factory output)
goes through these stages. Nothing touches a live bot except through stage 7.

## 1. Idea card (before any testing)
- **Why should it work?** One line: a risk premium, a behavioural bias, or a structural flow. No reason, no bot.
- Exact rules written down **before** looking at results (pre-registration), plus the pass bar.
- Markets, timeframe, costs, swap.

## 2. Screen (Python, research/scripts/screens)
- Honest fills: market orders at bar closes, or for resting orders a bar that touches the entry AND the stop
  counts as filled-and-stopped. Stop checked before target inside a bar. Costs + swap in every number.
- Data split: build/tune on older data only; the most recent 2-3 years stay unseen until the final check, run once.
- Report: trades, win rate, average R **with a 95% confidence range (bootstrap)**, total R, max drawdown, every year.

## 3. Pass bar (stricter the more we try)
- Minimum: average >= +0.10R after costs, positive in both halves, >= 100 trades (>= 50 for daily systems).
- **Trial counter**: log how many variants were tried for the idea. Up to 4 variants: the bar above. 5-20 variants:
  the lower end of the 95% range must be above 0. More than 20: treat as data-mined, needs a second unseen dataset.
- Must survive: +/-20% changes to every parameter, doubled costs, and at least one related market.

## 4. Fit with the portfolio
- Correlation of daily P/L with every live bot (want under 0.3).
- Monte Carlo of the whole account with the new bot added (scripts/monte_carlo.py): pass/fail odds against the
  prop firm's daily loss and drawdown limits, worst day, worst losing run.
- Risk budget: each bot gets a fixed share of the drawdown room, sized by its own volatility.

## 5. cTrader confirmation
- cBot built from the frozen rules (one generic cBot where possible), compiled here first.
- Vanessa runs a tick backtest on the firm's data; I match it trade by trade against the screen. Any gap is
  explained before going live (this is what caught Deni Fib).

## 6. Live start at half risk (instead of a paper incubation period)
- First 30 trades at 50% of the planned risk. If they are inside the backtest's expected range, step up to 100%.

## 7. Monthly review (Vanessa + Claude, every bot)
- Live vs backtest: trades, win rate, average R, slippage per trade, drawdown, worst day.
- **Kill rules, written per bot in its STRATEGY.md:** pause if the last 50 trades fall below the backtest's 95%
  range, or the drawdown passes 1.5x the backtest's worst. Paused bots are re-tested before restarting.
- Live code is never edited; changes are a new version that goes back through stages 2-5.

## 8. Scaling (once income allows)
- VPS so bots never depend on a laptop (about GBP 15-30 a month).
- More prop accounts running the same proven bots (check each firm's rules on copy trading and maximum total
  allocation first).

## Reviewer checklist (Claude runs this before reporting any result)
- [ ] Could the result come from a fill or bar-order assumption? (same-bar fills, limit orders, gaps)
- [ ] Were costs, swap and the firm's real spreads used?
- [ ] Is the unseen period really unseen (no parameter chosen after looking at it)?
- [ ] How many variants were tried, and does the pass bar reflect that?
- [ ] Is the profit spread across years and markets, or carried by one year / one trend?
- [ ] Does it overlap a live bot (same market, same hours)?

## Longer-term plan (Vanessa's goals)
1. Portfolio of prop-firm bots giving an income (now).
2. Futures scalping, about 2 hours a day around the 14:30 UK US open (research/futures_lane).
3. Property: rental / holiday income.
4. More swing-trading strategies.
