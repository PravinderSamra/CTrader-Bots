# Plain English Summary — What We Found and What To Do

No jargon. Everything explained.

---

## 1. The story in one paragraph

Your CRT strategy lost money badly — it would have wiped out a $100,000 account in 9 months. The reason wasn't bad luck; the stop-loss was so tight (about $1.88 of gold) that broker costs ate a quarter of everything you risked on every single trade. I rebuilt it: wider stops, a different entry signal, and taking profit in two stages. The rebuilt version makes money. Tested on a year of data I deliberately hid from myself while building it, it returned **+12% (day-trades only)** or **+28% (if you also allow one overnight trade)** on a $100,000 account.

---

## 2. What "fix the cost base" means

**"Cost base" = what your broker charges you every time you trade.** Three parts:

1. **Spread** — the gap between the buy price and the sell price. If gold shows 4000.00 / 4000.30, that 30-cent gap is the spread. You pay it the moment you enter.
2. **Commission** — a flat fee some brokers charge, typically around $7 per lot round trip (7 cents per ounce).
3. **Slippage** — when you get filled at a slightly worse price than you asked for, because the market moved while your order travelled.

I assumed all three together cost **47 cents per ounce** for a round trip (in and out).

**Why that matters so much here.** The strategy risks roughly **$6–15 per ounce** on each trade. So 47 cents is about **7% of everything you risk**. Every trade starts 7% in the hole before the market has done anything.

Now here's the important bit. If you cut that cost, the saving goes **straight into your profit**, because nothing else changes:

| What your broker charges you | Your profit per trade | Compared to now |
|---|---|---|
| 94 cents (typical UK spread-betting account) | very small | **−68%** |
| 47 cents (what I assumed) | baseline | — |
| 25 cents (a "raw spread" / ECN account) | much bigger | **+32%** |
| 15 cents (institutional) | bigger still | **+46%** |

**In practice this means two things:**

- **Trade on a raw-spread (ECN) account, not a spread-betting account.** Spread-betting brokers bake a wide spread into the price — often 50–90 cents on gold. Raw-spread brokers show you a tiny spread (10–20 cents) and charge a separate visible commission. Total cost is roughly half. That alone is worth about a third more profit.
- **Use resting orders.** Place your buy and sell orders in the market *in advance*, sitting there waiting. Don't watch the chart and click when it breaks — that's when you pay slippage. Getting your order in the queue early saves about 10 cents a trade, worth roughly 14% more profit.

**This is the single biggest improvement available, and it has nothing to do with the strategy.** No tweak I tested came close. It's just about which account you trade on and how you place orders.

---

## 3. Your question: what if we allow the overnight trade?

First, a clarification worth making. The overnight trade is **not really a swing trade**. You buy at **9pm** and sell at **3am** — six hours, and you're flat before breakfast. You never hold across days. It's an overnight *hold*, not a multi-day swing.

Here are the real numbers, all from the hidden test year, $100,000 account, risking 1% per trade:

| Version | Profit for the year | Worst drop along the way | Trades per week |
|---|---|---|---|
| **Day-trades only** | **+$12,150 (+12.2%)** | −12.0% | 5.2 |
| **Overnight trade only** | **+$14,472 (+14.5%)** | −13.3% | 3.8 |
| **Both together** | **+$28,380 (+28.4%)** | −14.9% | 9.0 |

**Adding the overnight trade more than doubles the profit — and barely increases the risk.**

That looks too good until you see why: the two trades happen at completely different times of day (afternoon vs late evening) and their results are almost perfectly unrelated to each other. When one has a bad week the other often doesn't. So you get double the profit while the bumps partly cancel out. That's genuine diversification, not a trick.

Month by month, both together, over the hidden test year:

Jul +$1,537 · Aug +$4,232 · **Sep +$20,999** · Oct +$5,134 · Nov −$2,383 · Dec −$55 · Jan +$10,262 · Feb −$5,697 · Mar +$8,968 · Apr −$7,019 · May −$7,297 · Jun +$489 · Jul −$791

Two things to notice honestly:
- **September alone made $21,000** — most of the year's profit. Take that month away and the year is roughly break-even. That's normal for this kind of strategy, but it means you cannot expect steady monthly income.
- **Four of the last five months lost money.** Either normal ups and downs, or the edge is fading. Thirteen months isn't enough data to tell.

**The one thing to check before using the overnight trade:** brokers charge a small fee for holding a position overnight (called "swap" or "financing"). On gold this is often 30–80 cents per ounce per night, and it's charged three times over on Wednesdays. That fee is *not* included in my numbers. If your broker's overnight fee is at the high end, it could eat a large part of this trade's profit. **Ask your broker for their XAUUSD swap rate before trading it.** If it's expensive, this trade isn't worth doing.

---

## 4. The strategy, in plain words

**Day trade (afternoon):**
1. At 2pm UK, look at where gold traded between 1:30pm and 2pm. Note the high and the low. That's your box.
2. Skip today if the box is unusually huge or unusually tiny compared to how much gold has been moving lately.
3. Place a buy order just above the box and a sell order just below it. Whichever triggers first, cancel the other.
4. Put your stop-loss a fixed distance away — a quarter of gold's average daily range. **Not** at the other side of the box. This is the change that fixed everything.
5. When you're up by the same amount you risked, take a third of the position off and move your stop to break-even so the rest is risk-free.
6. Close whatever's left at 9:55pm.
7. If that trade finishes and price then breaks the *other* side of the box, take that trade too. Maximum two trades a day.

**Overnight trade (optional):**
1. Monday to Thursday at 9pm, buy gold.
2. Stop-loss half of gold's average daily range below.
3. Sell at 3am. No profit target.

**Position size:** risk 1% of your account on each trade. Work out your size from the stop distance.

---

## 5. What I'd actually recommend

1. **Sort your broker account out first.** Raw-spread/ECN, and place orders in advance. Worth more than any strategy change.
2. **Ask about the overnight fee.** If it's cheap, use both trades — that's the +28% version. If it's expensive, day-trades only at +12%.
3. **Start small.** Risk 0.25–0.5% per trade for your first 100 trades and check the results match what I've predicted. Then scale up.
4. **Expect lumpy results.** Roughly half of weeks and half of months lose money. The profit comes from a few big months. If you can't sit through three losing months without changing the rules, this strategy will not work for you.
5. **Don't add more trades to fill the day.** I tested opening-range trades at 7am, 8am, midday, 2:30pm and 3pm — *every one lost money*. The 1:30pm slot is the only one that works. More activity would make you poorer, not richer.

**Realistic expectation:** something like **10–15% a year day-trading only, or 20–28% including the overnight trade**, with drops of 12–15% along the way and long boring stretches where nothing works. That is a genuinely good result for one instrument — but it is not a fast or smooth income.
