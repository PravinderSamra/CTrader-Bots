# The Gold Playbook — Two Strategies, Explained Simply

Everything in this file survived testing on 5 years of 1-minute gold data **and** a final year of data that was hidden away during development. Everything that failed has been left out.

Two strategies. Both traded by hand. Both take a few minutes a day.

---

# BEFORE YOU START

### 1. The right account

Use your **Razor (raw spread) account**, not a spread-betting account. This matters more than any rule below — a wide-spread account cuts the profit by about two thirds. You already have the right one.

### 2. One number you need: **ATR20**

**What it is:** the average amount gold has moved per day over the last 20 days. If ATR20 = 100, gold typically travels about $100 from its low to its high each day.

**How to get it:** open a gold chart, switch it to the **Daily** timeframe, add the indicator called **ATR** (Average True Range), set the period to **20**. Read the number.

**How often:** check it once a week and write it down. Every stop-loss and position size below is built from this one number.

### 3. How to work out your position size

This is the most important skill in trading. The formula:

> **Ounces to trade = (Account size × Risk %) ÷ Stop-loss distance in dollars**

**Worked example.** You have a $100,000 account. You risk 1%. Gold's ATR20 is $100, and this strategy puts the stop $25 away.

- $100,000 × 1% = **$1,000** — the most you can lose on this trade
- $1,000 ÷ $25 = **40 ounces**
- 40 ounces = **0.40 lots** (100 ounces = 1 lot)

If the trade hits your stop you lose $1,000, exactly as planned. Nothing else matters as much as getting this right.

**What risk % to use:**

| Account | Risk per trade |
|---|---|
| Your Razor account | **1%** |
| Your FTMO account | **0.5%** (their 10% max-loss rule makes 1% too big) |
| First 100 trades, any account | **0.25%** while you learn |

### 4. Terms you'll see below

- **Stop order** — an instruction to buy *above* the current price, or sell *below* it. It sits waiting and fires automatically if price gets there. You place it in advance and walk away.
- **OCO** — "one cancels the other". You place two stop orders; when one fires, the other is deleted automatically.
- **1R** — the amount you risked. If you risked $1,000, then "up 1R" means you're $1,000 in profit.
- **Break-even stop** — moving your stop-loss to the exact price you entered at, so the trade can no longer lose money.

---

# STRATEGY 1 — THE 1:30PM TRADE

**Why it works:** at 1:30pm UK time, the US gold futures market opens and US economic data is released. It is the single most active moment in gold's day — about a third of all daily movement happens in the following three hours. This trade simply positions you for whichever way that burst goes. It doesn't predict direction; it catches whichever direction shows up.

*(All times UK. In winter, subtract one hour from every time below.)*

### Step 1 — 2:00pm: draw the box

Look at your 5-minute gold chart. Find the **highest price and the lowest price between 1:30pm and 2:00pm**. Draw a horizontal line at each. That's your box.

### Step 2 — check the box is a sensible size

Measure the box height in dollars. Compare it to ATR20:

- **Smaller than 4% of ATR20** (under $4 if ATR is 100) → **no trade today.** The market is asleep and costs will eat you.
- **Bigger than 50% of ATR20** (over $50) → **no trade today.** The move already happened.
- Anything in between → **good, carry on.**

### Step 3 — check where today opened

Look at where gold opened at 11pm last night compared to **yesterday's main trading zone** (the price area where most of yesterday's business happened — your platform's Volume Profile tool shows this as the "value area"). If you don't have that tool, use yesterday's high and low as a rough substitute.

- Opened **above** that zone → **only place a BUY order today.**
- Opened **below** it → **only place a SELL order today.**
- Opened **inside** it → **place both orders.**

*Why: when gold opens outside yesterday's zone and then breaks the opposite way, it's usually a trap. This single filter improved results by about a third in testing.*

### Step 4 — place your orders and walk away

- **Buy stop** order a little above the top of the box
- **Sell stop** order a little below the bottom of the box
- Set them as **OCO** so the loser cancels automatically

**Place them in advance and leave the screen.** Do not sit watching and click manually when it breaks — that costs you real money in slippage.

### Step 5 — the stop-loss: **0.25 × ATR20**

If ATR20 is $100, your stop goes **$25** from your entry price.

⚠️ **This is the single most important rule in this document.** Do NOT put the stop at the other side of the box. An earlier version of this strategy did exactly that, the stop was tiny, and broker costs destroyed a $100,000 account in 9 months. A wider, fixed stop is what makes this work.

### Step 6 — size the position

Use the formula from earlier: (Account × Risk%) ÷ $25.

### Step 7 — take money off at 1R

When you're up by the amount you risked ($25 per ounce in our example):

1. **Close one third of the position** — bank it
2. **Move your stop to your entry price**

From this moment the trade cannot lose you money. This is the step that lifted the win rate from 43% to 54%.

### Step 8 — close the rest at 9:55pm

No profit target on the remainder. Let it run all afternoon. Most days it's small; occasionally it's a very big day, and those days pay for the month.

### Step 9 — you get one second chance

If that trade finishes — stopped out or closed — **and price then breaks the opposite side of the box**, take that trade too. Same stop, same 1R partial, same 9:55pm close.

**Maximum two trades per day, one per side.** This second trade is a genuine part of the edge, not an optional extra. Testing showed it improved every measure at once: more trades, higher win rate, more profit, *less* drawdown.

### A confidence note

If the overnight session (11pm–8am) was **wide and volatile**, that's a **good** sign for this trade, not a bad one. Wide overnight ranges were the best days for this strategy in testing. Never skip the trade because "gold already moved overnight".

---

# STRATEGY 2 — THE EVENING TRADE

**Why it works:** gold has drifted upward between roughly 11pm and 3am in every single year of the past five, on strong statistical evidence. This is thought to be Asian physical buying. You aren't predicting anything — you're just present for a period that has consistently drifted up.

**This is the simplest trade you will ever place. There is no chart reading at all.**

### Step 1 — Monday to Thursday at 9:00pm: buy gold

No conditions. No analysis. Every Monday, Tuesday, Wednesday and Thursday.

**Never on Friday** — you'd be holding into the weekend, which is a completely different risk.

### Step 2 — stop-loss: **0.5 × ATR20**

If ATR20 is $100, the stop goes **$50** below your entry.

### Step 3 — size it

$100,000 × 1% = $1,000 ÷ $50 = **20 ounces (0.20 lots)**.

### Step 4 — close at 3:00am

Set a pending order or a timed close. No profit target. You're flat before you wake up.

### ⚠️ One thing to check first

Brokers charge a small fee for holding a position overnight (called **swap**). On gold this can be 30–80 cents per ounce per night, and triple on Wednesdays. That fee is **not** in my results. **Ask your broker what their XAUUSD swap rate is before running this trade.** If it's at the expensive end, skip this strategy and trade Strategy 1 only.

---

# RISK MANAGEMENT — THE RULES THAT KEEP YOU ALIVE

1. **Never move a stop further away.** Ever. Moving to break-even at 1R is the only adjustment allowed in this playbook.
2. **Never risk more than 1%** (0.5% on FTMO) per trade, no matter how confident you feel.
3. **Recheck ATR20 every week** and resize. Gold's daily range went from $22 to $135 over the tested five years. Traders using fixed lot sizes through that were wiped out.
4. **Maximum three positions a day** — two from Strategy 1, one from Strategy 2.
5. **If you lose 3 trades in one day, stop trading for the day.** You've hit roughly 3% down; there's nothing left worth chasing.
6. **Never add extra trades to fill the day.** I tested this exact setup at 7am, 8am, midday, 2:30pm and 3pm — **every single one lost money**. Only the 1:30pm slot works. More activity makes you poorer, not richer.
7. **Never trade the Asia range breakout**, in either direction. I studied it extensively — continuation and reversal both lose after costs.
8. **Start at 0.25% risk for your first 100 trades.** Compare your real results against the expectations below before increasing size.
9. **Review every 50 trades, not every day.** A single day tells you nothing.

---

# WHAT TO REALISTICALLY EXPECT

Tested on the hidden year, $100,000 account, Razor costs:

| | Strategy 1 only | Both strategies |
|---|---|---|
| Profit for the year | **+15.6%** | **+33.8%** |
| Worst drop along the way | −11.3% | −14.2% |
| Trades per week | ~5 | ~9 |
| Winning weeks | about half | about 6 in 10 |

**On FTMO at 0.5% risk:** roughly +16% a year with a worst drop around 7%, safely inside their rules.

### Be honest with yourself about these three things

1. **You will win about 52% of the time.** This is not a strategy that feels good. It works because losses are controlled and a few large winners carry everything.
2. **About half of your weeks will lose money.** In the tested year, one month made most of the annual profit. Most months feel like nothing is happening.
3. **You will have losing months in a row.** In the test year there was a three-month losing stretch. If that would make you abandon the rules, do not trade this — the rule-breaking is what turns a winning system into a losing account.

---

# YOUR DAILY CHECKLIST

**Once a week:** update ATR20 from the daily chart.

**Every trading day:**

- [ ] **2:00pm** — mark the 1:30–2:00pm box high and low
- [ ] Box between 4% and 50% of ATR20? If no → done for the day
- [ ] Check where today opened vs yesterday's value zone → decide buy only / sell only / both
- [ ] Work out size: (Account × 1%) ÷ (0.25 × ATR20)
- [ ] Place OCO stop orders just outside the box, with stops attached
- [ ] Walk away
- [ ] **At +1R** — close a third, move stop to entry
- [ ] **9:55pm** — close whatever is left
- [ ] If the first trade finished and the other side breaks → take it, same rules
- [ ] **9:00pm Mon–Thu** — buy gold, stop 0.5 × ATR20 below, close 3:00am

That's the whole job. Under ten minutes a day.
