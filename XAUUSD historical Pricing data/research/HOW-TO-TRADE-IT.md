# How To Trade It — Step By Step

Written for a Razor (raw-spread CFD) account and an FTMO swing account.

---

## Part 1 — What your accounts mean for the numbers

### Your Razor account: good news

Razor/raw-spread accounts on gold typically cost about **25 cents per ounce** round trip (roughly 18c spread + 7c commission), versus the 47 cents I originally assumed. That saving goes straight to profit:

| | Old assumption ($0.47) | **Your Razor account ($0.25)** |
|---|---|---|
| Day trades only | +$12,150/yr (+12.2%) | **+15.6%/yr** |
| Day + overnight | +$28,380/yr (+28.4%) | **+33.8%/yr** |

*(Holdout year, $100,000, risking 1% per trade.)* You already have the best lever in place — no action needed beyond placing orders in advance rather than clicking on the break.

### Your FTMO account: the 10% rule sets your size

FTMO has two limits. Only one of them matters here:

- **5% daily loss limit — never a problem.** The worst single day in five years of testing lost 3.15R. At 1% risk that's about −3.2% of that day's balance. You have plenty of headroom.
- **10% maximum total loss — this is the binding constraint.** It caps how big you can trade.

| Risk per trade | Day trades only | Day + overnight |
|---|---|---|
| **0.50%** | +7.9%/yr, worst dip −5.7% ✅ | **+16.5%/yr, worst dip −7.2% ✅** |
| 0.75% | +11.8%/yr, dip −8.5% ⚠️ close | +25.1%/yr, dip −10.8% ❌ fails |
| 1.00% | +15.6%/yr, dip −11.3% ❌ fails | +33.8%/yr, dip −14.2% ❌ fails |

**On FTMO, risk 0.5% per trade.** That's the largest size that survived the worst stretch in the test data with room to spare. At 0.75% you'd have breached in the holdout year.

**Leverage is not a constraint.** At 0.5% risk with gold near $4,000 you're trading about 0.15 lots — nowhere near the FTMO swing account's 1:30 limit.

**One thing to check:** FTMO charges swap (an overnight financing fee) on the 9pm–3am trade. It's not in my numbers. Ask them for the XAUUSD swap rate. If it's expensive, run day-trades only on FTMO and keep the overnight trade on your Razor account.

### Suggested split

- **Razor account** — run both trades at 1% risk. Expect roughly +30%/yr with dips around 14%.
- **FTMO account** — run both trades at 0.5% risk (or day-only if swap is costly). Expect roughly +16%/yr with dips around 7%, comfortably inside their rules.

---

## Part 2 — The strategy, step by step

The tested anchor for the afternoon trade is **13:30–14:00 UTC**. On a UK clock that is **2:30–3:00pm in summer (BST)** and **1:30–2:00pm in winter (GMT)**. UK times below are **summer** times; subtract one hour in winter. Setting your chart to UTC avoids the whole problem.

### Before you start each day, you need one number

**ATR20** = the average daily range of gold over the last 20 days. Add the "ATR" indicator to a **daily** gold chart, set the period to 20, and read the value. Example: if it says 100, gold has been moving about $100 a day. Check this once a week; it doesn't change fast.

---

### TRADE 1 — The afternoon trade (the main one)

**Step 1 — 3:00pm UK (14:00 UTC). Draw the box.**
Look at the 30 minutes between **2:30pm and 3:00pm UK (13:30–14:00 UTC)**. Find the highest price and the lowest price in that half hour. Draw a horizontal line at each. That's your box.

**Step 2 — Check the box is a sensible size.**
Measure the box height in dollars.
- If it's **smaller than 4% of ATR20** (e.g. under $4 when ATR is $100) — **skip today**, the market is asleep.
- If it's **bigger than 50% of ATR20** (e.g. over $50) — **skip today**, the move already happened.
- Anything in between is fine.

**Step 3 — Check where today opened.**
Look at where gold opened at 11pm last night, compared to yesterday's "value area" (the price zone where most of yesterday's trading happened — your platform's volume profile tool shows this).
- Opened **above** that zone → **only place a buy order today.**
- Opened **below** it → **only place a sell order today.**
- Opened **inside** it → **place both orders.**

*(This filter stops you taking the trade most likely to be a trap. If your platform doesn't do volume profile, using yesterday's high and low as a rough substitute is acceptable.)*

**Step 4 — Place your orders and walk away.**
Put a **buy stop** order just above the box, and a **sell stop** order just below it (subject to Step 3). Set them as OCO if your platform supports it, so whichever fills cancels the other. **Place them in advance and leave them.** Do not sit watching and click manually — that's how you pay extra in slippage.

**Step 5 — Set the stop-loss: 0.25 × ATR20.**
If ATR20 is $100, your stop goes **$25** away from your entry price.

⚠️ **This is the most important rule in the whole strategy.** Do NOT put the stop at the other side of the box. The old version did that, the stop was tiny, and broker costs ate the account alive. A fixed, wider stop is what makes this work.

**Step 6 — Work out your position size.**
`Ounces = (Account × Risk%) ÷ Stop distance in dollars`

Example — $100,000 account, 1% risk, ATR $100 so stop is $25:
$100,000 × 1% = $1,000 ÷ $25 = **40 ounces = 0.40 lots.**
On FTMO at 0.5%: $500 ÷ $25 = 20 ounces = 0.20 lots.

**Step 7 — Take some profit at 1R.**
When you're up by the same amount you risked ($25 in the example), **close a third of the position** and **move your stop to your entry price**. From that moment the trade cannot lose you money.

**Step 8 — Close the rest at 9:55pm.** No profit target on the runner. Let it run all afternoon.

**Step 9 — If it finishes, you get one more shot.**
If that trade closes (either stopped out or at a profit) and price then breaks the **opposite** side of the box, take that trade too — same stop rule, same 1R partial, same 9:55pm close.
**Maximum two trades a day, one per side.** This second trade is a real part of the edge, not an optional extra.

---

### TRADE 2 — The overnight trade (optional but doubles the return)

**Step 1 — Monday to Thursday only, at 9:00pm: buy gold.** No conditions, no chart reading. Every Monday, Tuesday, Wednesday and Thursday.

**Step 2 — Stop-loss 0.5 × ATR20 below entry.** ATR $100 → stop $50 away.

**Step 3 — Position size:** $1,000 ÷ $50 = 20 ounces (0.20 lots) at 1% risk on $100k.

**Step 4 — Close at 3:00am.** No profit target. Set a timed close or a pending order.

**Never Friday.** You'd be holding into the weekend, which is a different risk entirely.

---

## Part 3 — Rules that keep you out of trouble

1. **Never move the stop further away.** Ever. Moving to break-even at 1R is the only adjustment allowed.
2. **Never add trades to fill the day.** I tested opening-range trades at 07:00, 08:00, 12:00, 14:30 and 15:00 UTC — **every single one lost money**. Only the 13:30 UTC slot works.
3. **Recheck ATR20 weekly** and resize. Gold's daily range went from $22 to $135 over five years; fixed lot sizes would have destroyed you.
4. **Expect roughly half of weeks and half of months to lose.** The profit comes from a few strong months. In the test year, September alone made most of the annual gain.
5. **Start at a quarter size** for your first 100 trades. Compare your real results with what's predicted here before going full size.
6. **Stop if it stops working:** if your last 50 trades show no profit, cut your size in half and re-test before continuing.

---

## Part 4 — A full worked example

Gold at $4,000. ATR20 = $100. Razor account, $100,000, 1% risk.

- **3:00pm UK (14:00 UTC)** — the 13:30–14:00 UTC range was 3,996 to 4,004. Box height $8. That's 8% of ATR — inside the 4%–50% window ✓
- Gold opened last night inside yesterday's value area → **both orders allowed** ✓
- Place buy stop at **4,004.50**, sell stop at **3,995.50** (just outside the box), OCO.
- **2:40pm** — the buy fills at 4,004.50.
- Stop goes at 4,004.50 − $25 = **3,979.50**.
- Size: $1,000 ÷ $25 = 40 oz = **0.40 lots**.
- **3:20pm** — gold reaches 4,029.50 (up $25 = 1R). **Close 13 oz**, banking about $325. Move stop to 4,004.50. Trade is now risk-free.
- **9:55pm** — close the remaining 27 oz at 4,041. That's $36.50 × 27 = about $985.
- **Day's result: roughly +$1,310** on a $1,000 risk.
- **9:00pm that evening** (if it's Mon–Thu) the overnight trade is placed separately: buy 20 oz, stop $50 below, close at 3:00am.

---

## The honest bottom line

On your Razor account at 1% risk, running both trades, the tested expectation is around **+30% a year with dips of about 14%** along the way. On FTMO at 0.5% risk, around **+16% a year with dips of about 7%** — safely inside their rules.

Roughly half your weeks will be red. A handful of months will make most of the money. The strategy works because of strict sizing and a wide stop, not because it wins often — it wins about 52% of the time.
