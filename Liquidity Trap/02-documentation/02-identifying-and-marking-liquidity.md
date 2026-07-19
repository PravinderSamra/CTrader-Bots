# 02 — Identifying and Marking Liquidity on a Chart

Concrete, procedural method for finding, marking, and prioritizing liquidity levels, assembled from all three videos. Read `01-liquidity-fundamentals.md` first — this file assumes you know the respect-and-move-away rule and the liquidity-block (LB) concept.

Citation format: `(Video N, [MM:SS])`. See file 01 header for the video key.

---

## A. Timeframe stack

| Role | Timeframes | Source |
|---|---|---|
| Bias / draw on liquidity (direction) | Weekly, Daily, 4H, 1H, 30m | Video 1, [11:32]–[12:06], [41:28] (starts YM analysis on 30m); Video 3, [0:43] (weekly/daily first) |
| Working / "do-it-all" execution chart (futures intraday) | 5-minute — "usually the timeframe I'm hanging out on... kind of a do-it-all timeframe for me" | Video 1, [42:40] |
| Refinement / high-RR confirmation entries | 1-minute (futures mostly; occasionally on gold CFD) | Video 1, [66:37]; Video 2, [36:55]–[37:13] |
| Futures entries generally | 1m / 5m entries targeting 15m / 1H levels | Video 2, [23:42]–[24:05] |
| CFD/forex swing deployment | Entries even off 1H / 4H, held days to a week to HTF targets | Video 2, [24:05]–[24:27], [64:40] (USDJPY); Video 3 (entire walkthrough on 4H/1H) |

The model itself is timeframe-agnostic/fractal (Video 1, [12:06]; Video 2, [2:34], [41:10]); the stack above is just how the speakers deploy it. Video 3 demonstrates the *entire* method on 4H/1H only, with one 15m refinement, producing 1:3.6–1:19 trades (Video 3, [15:54]).

## B. What qualifies as a liquidity level (the catalogue)

Mark a level ONLY when the market has confirmed it. Qualifying formations:

1. **Respected high (sell-side of the pattern / buy stops above).** A high that approached a previous high, respected it (didn't trade through), and moved away → liquidity above (Video 1, [3:22], [13:13]; Video 2, [25:49]–[26:39]). Multiple respects strengthen it (Video 2, [67:20]; Video 3, [13:29]: "taps into it once, twice, three times — this is inducing buyers").
   - *Visual confirmation (Video 3 shots):* "respect" does **not** require a touch of the exact prior price. In V3's 4H example the respect target is an **area** (red box, top edge 20,751.75 extending several hundred points down), and the "respecting" high printed at 20,545.75 — ~200 points *below* the box top, i.e. the wick terminated inside the previously-tapped zone (`../03-images/Video3/shot_003.jpg` [4:42], `shot_005.jpg` [4:46], `shot_014.jpg` label 20,545.75). In the 1H example at V3 [8:01] the respecting high printed 20,839.75 against a marked high of 20,899.00 — a ~59-point (~0.28%) undershoot, no touch (`shot_016.jpg`). So respect = wick terminating at/inside the prior level's zone without closing through it; tolerance observed on NQ ranged from ~60 pts against a line to ~200 pts inside a marked area.
2. **Respected low (sell stops below).** Mirror: low respecting a previous low, then moves away → liquidity below (Video 1, [13:56]; Video 2, [66:15]; Video 3, [5:24]).
3. **Equal / relative-equal highs or lows.** "We can mark on right away that we have a level of equal lows, relative equal lows... very simple stuff. It's an area of liquidity" (Video 1, [41:28]–[42:02]); weekly equal highs as the macro draw (Video 3, [0:43]–[1:16]); "we left the equals up here" (Video 2, [46:24]).
   - *Visual confirmation (Video 3 shots):* the weekly "equal highs" are two wick highs ~2 months apart (Dec '24 and Feb '25 on the NQH2026 chart) marked as a **single horizontal line**, not a box — snapped at 23,397.00 while drawing ([1:18], `../03-images/Video3/shot_004.jpg`) and finalized at 23,364.25 ([1:55], `shot_010.jpg`). The two wick tips sit within roughly 30–40 points of each other on a ~23,300 index — i.e. "equal" tolerated ~0.15% of price here.
4. **Old / previous highs and lows** ("something from the left-hand side", "an old low"): untaken prior swing points that price later runs (Video 2, [3:58], [27:48], [31:26]; Video 1, [25:49] — untaken pools become future targets).
5. **Trendline / channel liquidity.** Explicitly collapsed into the same rule: "people can say channel, people can say trendline liquidity. At the end of the day... it's literally just liquidity, period" — a sequence of respected highs/lows along a slope is just repeated high-taken/low-respected (Video 1, [12:37]–[13:13], [73:42]: "create all this internal liquidity, trendline, however you want to call it, it's just liquidity in my eyes"; Video 2, [38:23]: "you can call it a channel, you can call it structure, whatever it is, it's building liquidity").
6. **Session highs/lows.** Asia session high/low marked as a box on the execution chart; the pre-New-York spike-out of Asia liquidity is part of the YM example ("we've spiked out all of Asia liquidity... this is Asia high and Asia low", Video 1, [43:25]–[44:03]). Previous-day low (PDL) used as a stop reference in the live trade (Video 1, [84:30]–[85:11]). Chop just before NY open "is kind of building liquidity for New York to deal with" — mark those internal equal highs/lows too (Video 1, [44:44]–[45:24]).
7. **Structural liquidity chains.** Stacks of internal lows/highs left behind by a trend: "these are all internal lows left... it is just structural liquidity left" (Video 1, [64:36]–[65:14], [59:45]: "low high low to the downside — that's structural liquidity").
8. **Engineered liquidity** (Video 2's key term): the specific respected-high (or low) that forms *against* your target level as price first approaches it — sellers entering in front of a buy-side pool. This is a liquidity level AND the arming condition of the Da Vinci setup (Video 2, [4:20]–[6:34], [27:22]; Video 3, [9:16]: "look at the engineered liquidity we have at the highs"). Full treatment in file 03.

### Explicit NON-levels (do not mark as liquidity)

- **Liquidity blocks (LBs):** any swing point that *itself* swept liquidity and has not since been respected — no orders rest beyond it (Video 1, [28:44]–[29:25]; Video 2, [32:52], [51:49]; Video 3, [2:27]). Mark these separately (blue box in Videos 2/3) as stop-anchor/entry zones, not as targets.
- **Retail POIs on their own:** order blocks, FVGs/imbalances, Fibonacci levels, support/resistance, breaker structures. These are marked only as **trap zones** (red boxes) where false reactions are expected, because retail entries there build the pools (Video 1, [5:10]–[5:52], [51:06]–[51:45], [73:42]–[74:20]; Video 2, [10:57], [56:38]).
- A high/low broken *through* immediately with no respect: no evidence of orders.

## C. Step-by-step chart-marking procedure

The following numbered procedure is a faithful proceduralization of what the speakers do on every chart example (YM: Video 1, [41:28]–[47:43]; NQ: Video 1, [63:28]–[77:31]; gold: Video 2, [30:40]–[54:57]; NQ: Video 2, [55:02]–[63:11]; UJ: Video 2, [64:40]–[69:17]; NQ: Video 3, entire video).

### Step 1 — Establish the higher-timeframe picture
1. Open weekly/daily (swing context) or 30m/15m (intraday context) and zoom out (Video 1, [41:28]; Video 3, [0:43]).
2. Find the most recent *large displacement move* and ask: **what liquidity did it clear, and what did it leave behind?** ("What was the purpose of it?... To clear all of this liquidity", Video 3, [2:27]).
3. Mark the surviving confirmed pools: equal highs/lows, respected old highs/lows, chains of tapped lows to the left (Video 3, [1:52]–[2:27]). *Visual: V3's weekly "chain" is the cluster of 2024 lows around ~18,400–19,300 (chart values), covered by a single wide red box (`../03-images/Video3/shot_011.jpg` [2:30], `shot_027.jpg` [3:04]) — so in V3 a red box can mean "tapped chain of lows", not only "retail trap zone".*
4. Mark HTF liquidity blocks (extreme sweeps that never got respected) as blue boxes (Video 3, [2:27]–[3:06]). *Visual: the weekly LB is a blue box whose top edge is marked by a line at 17,894.75; the April '25 crash wick drove ~1,400 points deep into the box (wick low ~16,4xx) before the weekly reversal — a tap can travel far inside the box and still be "the reaction at the extreme" (`shot_027.jpg` [3:04], `shot_020.jpg` [3:34] with the tap circled).*
5. If the chart shows one big one-directional move and *no* confirmed pools remain: **do not trade this chart**; wait days if needed for liquidity to rebuild (Video 1, [14:32]–[15:06], [55:44]–[57:31]).

### Step 2 — Determine the draw on liquidity (bias)
6. The bias = the direction of the nearest *logical* untaken pool. "Your eyes should be back to these highs. That is the only logical liquidity point I can see in front of us right now" (Video 3, [3:06]).
7. Prioritization rules-of-thumb extracted from the examples:
   - **A pool sitting directly above/below with nothing beyond it** ("the next internal low is all the way down here and there's a huge gap in between") is high priority — the market lacks fuel to go the other way (Video 1, [58:09]–[59:11], EU example).
   - **Momentum agreement:** heavy directional momentum with no drastic pullback keeps the draw pointing with the trend (Video 1, [58:39]–[59:11]).
   - **Recently swept side is exhausted:** once a big move has cleared one side, the opposite untaken pool becomes the draw (Video 3, [3:06]; Video 1, [28:09]: reversals typically occur once external is taken).
   - **Untaken pools persist** as future targets across days/weeks (Video 1, [25:49]–[26:28]).
8. State the bias as a conditional plan, not a prediction: "if I was looking to take buys, it would only be below here" (Video 1, [56:55]–[57:31]).

### Step 3 — Mark the trap architecture on the execution timeframe
9. Drop to the execution TF (5m futures intraday; 1H/4H for swing). Mark:
   - The **stock-open / session-open time line** (9:30 a.m. NY for index futures) — "an important level of time" (Video 1, [42:40]–[43:25], [65:14]).
   - Asia high/low box, pre-open equal highs/lows (Video 1, [43:25]–[45:24]).
   - **Red boxes** = retail entry zones (POI/OB/imbalance areas) where false reactions are expected — "both these red boxes I'm viewing as a trap" (Video 1, [51:06]–[51:45], [73:42]–[74:20]; Video 2, [37:58], [46:48]).
   - **Blue boxes/lines** = liquidity blocks and the identified liquidity level to be swept (Video 2, [34:04]; Video 3, [5:24], [12:15]).
10. Track which highs/lows currently have **no** liquidity (recent sweep wicks). These are candidate entry-off zones and stop anchors, and — key bookkeeping rule — they *acquire* liquidity the moment price later respects them and moves away ("since we've respected it, there's going to be liquidity up here now", Video 1, [45:24]–[46:01], [76:22]).

### Step 4 — Wait
11. The explicitly-stated hardest part: "you have to allow the market to build liquidity" (Video 1, [5:52]); "if you don't see liquidity, you are the liquidity. When big moves happen, you wait. You wait for liquidity to get engineered, things clear up, and you take entries" (Video 2, [53:48]–[54:11]). No confirmed pool + no engineered liquidity = no marking, no trade.

## D. The one-strict-rule filter (bias lockout)

Marco's non-negotiable sequencing rule, stated as the fix for the most common mistake (Video 1, [24:29]–[25:49]):

> **"If we are moving to the downside and I'm looking for a whole buy scenario to play out: if we get a move to the upside and we take out highs, I will not buy this asset... until this low is taken out. It doesn't matter what happens anywhere in between."**
>
> **"When going to the downside: if we are moving to the upside and the market comes down, I will not look to take a sell until this high is taken out."**

I.e., once the market takes out a high, longs are locked out until the corresponding low-side pool is swept (and vice versa). Sometimes the market respects the low and runs without you — "this is not a move I was supposed to be in" (Video 1, [25:08]–[25:49]). Restated during examples: "high taken, which tells me I do not want to be buying unless this low's taken" (Video 1, [65:58]–[66:37]); "I will not sell unless this high is taken out" (Video 1, [67:52]–[68:28]); "we're not going to be buying once highs are taken out" (Video 3, [11:43]). This is the rule that converts liquidity marking into trade permission.

*Visual example of the lockout (Video 3, [7:35]–[8:32]):* the high that acquired liquidity is marked with a blue line at 20,899.00 after a lower high respected it at 20,839.75 (`../03-images/Video3/shot_016.jpg` [8:01], circle drawn on the respecting high). Selling that reaction is explicitly forbidden because the low side had just been taken out; instead the next long is armed at the 20,446.50 low line (`shot_023.jpg` [8:32] shows both lines marked simultaneously — liquidity above 20,899, pending sweep below 20,446.50).

## E. Worked micro-example of the marking grammar

From the gold 1m entry (Video 2, [40:49]–[41:35]) — the whole vocabulary reduces to one repeated grammar:

> "High taken, low respecting low → liquidity. Move bullish, take out a high, low respecting low → liquidity. High taken, low respecting low, high taken, low respecting low... all of this is a buildup."

Each cycle of *sweep one side, respect the other, move away* prints one more confirmed pool. You mark the confirmed side, note the swept side as an LB, and trail your attention to the **last unswept level at the extreme**: "we run that last level of liquidity... not just this low, not this one, not this one — if you trail your eyes all the way to the extreme, it's going to be this low down here" (Video 2, [38:46]–[39:09]). The extreme-most confirmed pool is the one whose sweep arms the entry (file 03).

## F. Marking checklist (condensed)

Before considering any trade, the chart should show, in your own markings:

- [ ] HTF draw on liquidity identified (the target pool) and stated as a conditional bias (Video 3, [3:06]; Video 1, [56:55]).
- [ ] The pool is *confirmed* (respected + moved away, or equal highs/lows), not guessed (Video 2, [5:24]; Video 3, [14:06]).
- [ ] Trap/red-box zones marked where retail will enter against the draw (Video 1, [51:06]; Video 2, [37:58]).
- [ ] Liquidity blocks (no-liquidity extremes) marked as blue boxes for stops/entries (Video 2, [51:49]; Video 3, [5:56]).
- [ ] The near-side pool that must be swept before entry is identified (the "entry-arming" level) (Video 2, [14:11]; Video 1, [24:29]).
- [ ] Bias lockout checked: has the opposite side been taken since your last valid sweep? If yes, stand down until re-armed (Video 1, [24:29]–[25:49]).
- [ ] Video 3's tri-condition sanity check: "We have liquidity to the upside [reason/target]. We have a buildup of buyers [pool to sweep]. And we have a liquidity block below [stop anchor]. Everything checks the boxes." (Video 3, [5:56]).

---

**Next file:** `03-the-liquidity-trap-setup.md` — the trap/Da Vinci entry model itself.
