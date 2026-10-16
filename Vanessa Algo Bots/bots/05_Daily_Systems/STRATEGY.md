# Daily Systems bot: what it does, in plain words

Two "buy the dip in an uptrend" strategies, run separately on five markets:
US500, US100, US30, GER40 and gold. Long (buy) trades only.

## The two strategies

**A. Pavel's mean reversion**
- Buy when all three are true at the daily close:
  1. The close is below its 5-day average.
  2. The drop below the 5-day average is unusually large: more than 2.5 times the average gap of the last 20 days.
  3. The close is above its 200-day average (the market is in a long-term uptrend).
- Sell at the first daily close back above the 5-day average, or after 4 days, whichever comes first.

**D. Naoufel's RSI(2)**
- RSI(2) measures the last two days' moves on a 0-100 scale. Below 20 means a sharp two-day drop.
- Buy when RSI(2) is below 20 and the close is above its 200-day average.
- Sell when RSI(2) rises above 70 (the bounce has happened). Usually 2-5 days later.

Both can hold the same market at the same time; they are separate trades.

## Stop loss and take profit
- No fixed take profit. The exits above do that job: the trade is closed once the bounce has happened.
- Every trade has an emergency stop loss at 3 x ATR(20) below the entry (ATR = the average daily range of the last
  20 days). That is usually 4-6% below the entry price. It is a safety net, not the normal way out.

## Size: "Notional per position" = $13,000
Notional is the value of the position, not the amount at risk. $13,000 notional means the position moves about $130
for every 1% the market moves. For example US500 at 6,500 = 2 units (US500 moves $1 per point per unit).
At that size: average winning trade about +$160 to +$220, average losing trade about -$270 to -$300,
emergency stop about -$500 to -$800.

## Timing
Decisions use the daily close. Orders are sent about 11 pm UK time (one hour after FTMO's new daily bar opens, to
avoid the wide spreads around the daily rollover).

## Safety rules
- Daily guard: if the bot is down $2,000 on the day, it closes everything and stops until the next day.
- Total size cap: all open positions together at most 1.5 x the account balance.
- Flat over the weekend (setting "Flat Over Weekend" = Yes): close everything Friday 15:30 New York time, reopen
  Monday at the normal order time with the same size and stop, unless the exit rule fired on Friday's close.
  This removes the risk of a big Monday gap (e.g. -7% to -10%) that the daily guard can't stop.

## Results (backtests, $100k account, $13k per position)
- Jan 2024 - Oct 2026, final settings on real tick data (real spreads, flat over weekends): +$15,003 closed,
  73% of trades won (counting a weekend split as one trade), worst drawdown 5.25%, worst day -$2,009 (daily guard),
  every year positive (2024 +$3.5k, 2025 +$5.5k, 2026 to Oct +$6.0k).
- Same period on m1 bars, holding over weekends: +$15,924, 73% won, worst drawdown 4.76%.

## Settings to use on the FTMO account
Systems A and D on (B, C, E, F off), Notional 13000, Max Notional Mult 1.5, Cat ATR 3.0, Daily Guard 2000,
Flat Over Weekend = Yes, Delay Minutes 60. Attach to any chart (e.g. US500.cash D1); it trades all five markets itself.
- Live off-switch: back to demo if the win rate over the last 50 trades drops below 62%, or drawdown passes ~7%.

Full rules and every test: research/DAILY_SYSTEMS_TEST_PLAN.md.

## v1.4 crash-safe (15 Oct 2026)
Live only: saves waiting orders, weekend positions, each trade's signal day and the daily guard total every minute
(cTrader LocalStorage, this computer), reloads them after a restart, makes a missed day's decisions straight away, and
never trades the same signal twice (checks History). Switched off in backtests, so backtest results are identical to v1.3.
Restart with v1.4 any time except the order window (about 23:00-00:30 UK).

## v1.4.1 (16 Oct 2026)
Live log showed "R|save failed: keys can only contain Latin letters, numbers and spaces": the v1.4 save key used
underscores, so nothing was saved (trading itself unaffected). Key is now letters and digits only; a failure prints once.
Also found: after the 15 Oct rebuild the live instance stayed stopped (cTrader stops instances on Build), so the
Friday 16 Oct weekend close did not run; Vanessa closed the US500 DSY-D trade by hand at 20:50 UK.
