# 04 — Trade Management, Risk, Sessions, Instruments, and Claims

Everything the three videos state about position management, risk, filters, instruments, and performance claims. Performance claims are attributed to the speaker and are **not verified**.

Video key as in files 01–03 (V1/V2 = Marco via Chart Fanatics; V3 = Inter Equity Trading).

---

## 1. Risk per trade / position sizing

- Marco caps risk with **a fixed daily risk figure**: "from a risk perspective, I always have... a specific figure I'm willing to risk on a daily basis" (V2 [19:45]). The number itself is never stated.
- The host suggests the model's asymmetry lets you run small per-trade risk on prop accounts — "you could risk 0.5% to 0.75% and still make $10,000–$20,000 in payouts" (V2 [18:37]–[18:59]). This is the host's framing, not Marco's stated rule.
- Minimum reward filter: Marco takes setups only at **≥1:3 RR** ("I perform the best... when my RR is minimum 1-to-3 minimum", V2 [36:18]–[36:39]); if the structural stop makes RR worse, skip or refine to a lower timeframe (V2 [35:05]–[36:55]).
- He also skips small absolute moves regardless of RR ("only looking at a 140-tick move — I'm not interested in a small move like that", V1 [94:38]).
- V3 gives no explicit sizing rules.

## 2. Stop management (after entry)

Rules in execution order (all long-side; mirror for shorts):

1. **Initial stop:** structural, behind the swept low / liquidity block, always (V1 [69:02]; V2 [16:17]; V3 [14:41]) — details in file 03 §3.
2. **First trail:** once the trade starts moving and price leaves a higher low that "should not be revisited", roll the stop below that low — "once I start getting this move up, I'll look to trail my stop below this low... so now essentially I've cut my risk almost in half" (V1 [32:17]–[33:31]). Live: "I'm confident enough in the setup to roll my stop below this low we've created here. I'll take some risk off the table" (V1 [90:23]).
3. **Break-even trigger (V2's crisp rule):** "as soon as I take this entry and price takes out highs — some sort of highs — I understand buyers are induced... this high gets taken out, I roll my stop to break even. And I'm very extremely confident in my target getting hit" (V2 [63:34]–[64:19]). V3 identical: "as soon as we take out this high, we can all agree that liquidity has been taken. So manage your risk — maybe roll it to break even or just tuck it below this low... when these highs are taken out, you need to be managing your position" (V3 [6:31]–[7:05], [10:38]: "as soon as price takes out these highs, roll your stop loss").
   - **V1 nuance/divergence:** Marco in V1 says he is "not the biggest fan of setting my trade to break even **unless** I've partialed or closed majority out" (V1 [32:55]–[33:31]) — i.e., in V1 break-even is tied to having banked partials; in V2 it is tied to the first opposing-high sweep. Both appear in his live trade: he rolls the stop progressively as highs are taken and refuses to let a ~200-tick winner return to entry ("there is no reason why I would want to see price back down to my entry. That'd be foolish", V1 [98:46]).
4. **Never move the stop out of fear:** "stop is going to stay where it is... I'm not going to roll it out of fear or anything like that. When the chart tells me to, I will" (V1 [94:38]).
5. **Don't let mid-trade candles shake you out:** "sometimes all it takes is taking the entry, setting your stop and a target. What happens in between is irrelevant... don't let these candle closures influence you and make you get emotional" (V1 [103:48]–[104:29]).

## 3. Partials and targets

- **Philosophy: hold to analyzed targets, not fixed R multiples.** "I'm not looking to close at a specific R... it's literally just a random point in the chart" (V1 [33:31]–[34:07]; V2 [59:17]: "I'm analyzing the chart for a reason... why not take advantage of that analysis"). Targets are liquidity pools only.
- **Partial sizing:** Marco holds majority volume to target; when he partials it is "very very small... 20–25% of my position" (V2 [64:19]). He recommends students practice removing the 1:3 partial habit entirely: "just hold to those targets — that's when the profits drastically increase. That's something that I did a year, a year and a half ago... once I started holding more volume the profits did increase" (V2 [59:39]–[60:24]).
  - **V1 divergence (confidence-scaled partials):** at the first (LTF) target he may take "usually 50%, maybe 70% if I'm very confident in the higher time frame, and then I'd hold the rest to the further target" (V1 [47:05]–[47:43]). So stated partial size ranges 20–70% across the two videos; the invariant is that partials happen **only at liquidity levels** and the runner always aims at the HTF pool.
- **Where partials go:** above/below the first opposing pool (e.g., "small partial above the high cuz that was my first target", V1 [76:54]–[77:31]; engineered-liquidity highs as partial points, V2 [58:35]–[58:55]; "great intraday targets on the way back up", V3 [12:51]).
- **Runner math argument (host):** a 20% runner at 1:10–1:20 can equal or exceed the 1:3 majority partial (V2 [43:33]–[44:22]).

## 4. Scaling in (adding volume) — V1 live session only

- Adds are made only where the model independently re-triggers: below a fresh local sweep — "if we can get some sort of rally, a little sell-off, I will add below this low... but we need to trade below this low" (V1 [89:36]–[90:23]); "we'll add another three contracts below this low if we can trade below it" (V1 [91:08]).
- Candle-close gate for adds: "if we can get a nice five-minute close above, I will add a little more volume... not a strong close for me → nothing convincing, I won't take anything now" (V1 [86:15]–[86:59]).
- Each add has an independent invalidation level (V1 [92:05]) and is easier to justify once initial-entry risk has been rolled off (V1 [91:08]–[92:05]).
- Anti-rule: scale-ins that don't fit the rules but are forced "to their original trade idea" are the classic way traders leak profits (V1 [79:44]–[80:55]).

## 5. Session / time-of-day / news filters (V1; Marco's personal regime)

- **Fixed daily time window; ignore everything outside it.** "I have a specific time window, a specific time of the day I like to trade... what happens outside of the time window is completely irrelevant to me" (V1 [49:30]–[50:00]).
- His window: **New York session**, anchored on 9:30 a.m. NY stock open, which he marks on every chart ("an important level of time... it has a direct correlation with the indexes. Typically I'm looking for entries after the open", V1 [42:40]–[43:25], [65:14]). Example trades occur ~1.5h after the open (V1 [42:02]) and at the 10:00 a.m. 4H close (V1 [83:36]).
- **News:** "I'll never enter before news. I want to wait for the news to get released and I'm entering after — usually 2, 3, 4 minutes, somewhere in that range" (V1 [67:13]–[67:52]). Liquidity often builds the day before scheduled news (V1 [26:28]).
- **NY lunch:** avoid holding into it — "typically the hour tends to be dead in volume... in an ideal situation, I'm out of this position before lunch" (V1 [105:56]). Late-morning entries get time-pressured management (V1 [99:35]: "timing wise it's getting a little late — I usually don't stay on the chart at this time").
- Session behavior notes: pre-NY-open chop "is building liquidity for New York to deal with" (V1 [45:24]); Asia range sweeps feature in index setups (V1 [43:25]); the host notes optimum windows have less chop/ranging (V1 [71:54]–[72:24]).
- V2 adds the *counter-example*: CFD limit-order setups let you take London moves while asleep (Marco is in Toronto) — the model does not require screen time outside your window (V2 [68:09]–[68:51], [58:10]).
- V3 states no session rules (its walkthrough is HTF).

## 6. Instruments and market-specific notes

- **Discussed/traded:** YM (Dow futures), NQ (Nasdaq futures), EURUSD, USDJPY, Gold (XAUUSD — "my favorite asset to trade", V2 [30:40]–[31:01]); claimed universal: "no matter if you trade gold or NASDAQ, S&P or EURUSD, this strategy works" (V2 [0:22]); V3 uses NQ.
- **Futures vs CFD/forex:**
  - Futures: centralized feed → tight stops (a tick or two beyond the level), limit fills reliable, no spread games (V1 [68:28]–[69:02], [46:33]); must close before market close → intraday only, 1m/5m entries targeting 15m/1H pools (V2 [23:42]–[24:05]).
  - CFD/forex: spread + broker-feed variance → stop needs breathing room (V1 [68:28]; V2 [39:32]); can hold days/weeks → used for HTF targets and swing Da Vincis (V2 [24:05]–[24:27], [64:40]).
- **Watchlist size:** for learners, "I would cap myself out at about two, three pairs on my watch list... you're still going to find plenty of opportunity on a weekly basis" (V1 [35:46]–[36:22]). Multiple assets = backup when one is far from any liquidity (V1 [36:22], host).
- **No cross-market correlation / SMT:** "I purely focus on... whatever chart is in front of me is the chart I'm trading. [SMT divergence] is nothing I've really come across that I enjoy" (V1 [63:28]–[64:04]).

## 7. Frequency and expectancy claims (attributed, unverified)

- Setup frequency: extreme-RR versions "sometimes a couple times in a week, sometimes once or twice a month" (V2 [8:36]–[8:54]); day-to-day the model appears "a couple times per day if you have a couple different assets on the list" on lower TFs (V2 [8:54]–[9:11]).
- Win-rate claims (Marco): "if you end up applying this model correctly and waiting for the higher probable ones, the win rate is incredible to say the least" (V2 [0:02], [20:05]); "the strike rate of it hitting these areas is very high" (V2 [59:39]); host claims the usual high-RR/low-win-rate tradeoff "doesn't need to be there" with this model (V2 [44:22]–[44:49]). Marco's explanation for why high RR usually degrades win rate: LTF entries breed mistakes, not the model itself (V2 [44:49]–[45:33]). **No numeric win rate is ever stated.**
- RR observed in examples: 1:3.6, ~1:5, 1:7, 1:7.5, 1:10, 1:12, 1:14, 1:19 (V1 [50:00]; V2 [39:32], [52:12], [62:50]; V3 [15:54]); "1 to 10 plus... doesn't happen all the time" (V2 [8:36]).
- Money claims: Marco — "$500K+" payouts (V1 title; V2 [0:12] "over $500,000 in payouts"), "$6,400 across four accounts" in the live session (V1 [107:47]), USDJPY trade $6,600 realized, potentially >$11k (V2 [64:40]–[65:26]). Host (RZ) — "last year I did over $100,000 in payouts whilst doing this... this year, January, I've already done 20,000" using a hybrid of this foundation plus his own additions (V2 [0:02], [61:13]–[61:57]).
- All figures are self-reported on a sponsored YouTube show; treat as marketing-grade until independently verified.

## 8. Psychological/discipline rules stated as part of the system

- Patience is the named hardest part: waiting for liquidity to build and for the trap move (V1 [5:52], [13:56]–[14:32], [17:54]–[18:27]; V2 [15:54]–[16:17], [53:48]).
- "Unlearn to relearn": retail concepts are kept only as a map of where others get trapped (V1 [34:38]–[35:11], [37:58]–[38:33]).
- Don't chase missed moves; the lockout rule covers this (V1 [16:51]–[17:54], [24:29]).
- Anticipate stall zones in advance so they don't shake you out ("I like anticipating these things... I was already mentally ready for it", V1 [92:05]–[93:01], [95:34]–[96:30]).
- If it doesn't reach target, "there's no profits and it is what it is" — no forcing (V1 [99:35]–[100:21]).
- Train the eyes via repetition on historical charts before live use (V2 [69:36]–[70:42]; V1 [34:38], [70:08]–[70:40]).

---

**Next file:** `05-cross-video-synthesis.md`.
