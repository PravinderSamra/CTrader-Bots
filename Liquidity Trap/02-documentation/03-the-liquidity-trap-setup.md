# 03 — The Liquidity Trap Setup (a.k.a. the "Da Vinci model")

The core pattern: how liquidity gets swept and price reverses, and the exact entry, stop, target, and invalidation rules. This is the most important file in the set. Per rule, agreement/divergence across the three sources is stated explicitly.

Video key: **V1** = Marco on Chart Fanatics #1; **V2** = Marco on Chart Fanatics #2 (where he names it the "Da Vinci model", V2 [2:09]–[2:34] — the name is cosmetic: "I kind of just threw a title on it"); **V3** = Inter Equity Trading (same school, same rules, same vocabulary).

All rules below are written for the **bullish (long) case**. Every source states the bearish case is the exact inversion (V1 [25:08]; V2 [6:14]: "you guys can literally just invert this"; V2 [22:20]–[22:44]; V2 [24:52]–[29:07] draws the full short version; V3 trades only longs in its example but uses the same mirrored language for sells). *Visually confirmed:* V2's bearish whiteboard is object-for-object the mirror of the bullish one — target-lows line at the bottom, old high taken from the left at the top, buyer-POI red lines drawn as an area from the left mid-lows, and "ENG LQ" labeling the **low** that respects previous lows before the rally that sweeps the high (`../03-images/Video2/shot_019.jpg` [27:36]). No object changes role in the inversion.

---

## 0. The trap in one paragraph

The market breaks a high (BOS) → retail buyers are induced and buy the pullback at their POIs → their stops build a pool below the pullback low → price gives false bullish reactions to induce more buyers → price then **sweeps below the pool (the trap / stop hunt)**, taking every early buyer out → with the buy-side of the book cleared and a confirmed pool still resting overhead, price reverses and runs to the overhead liquidity. You do not trade the trap move; you **enter long the moment the pool is swept**, stop hidden behind a no-liquidity extreme (liquidity block), target the overhead pool. (V1 [8:19]–[11:32]; V2 [13:20]–[16:42]; V3 [3:06]–[6:31].)

*Canonical geometry, from V2's master whiteboard diagram (`../03-images/Video2/shot_017.jpg` [10:59], `shot_031.jpg` [20:03]):* the target-highs line (marked `$`) runs across the top; the **seller POI is a red box whose top edge sits just below that line**, drawn starting from the left-hand internal high and extended right — the engineered high prints *into the box's right edge*, clearly below the target line (it never touches it). Below, the pool is a horizontal line under the two middle "respecting" lows, with green `$` signs beneath it; the **left-hand low is drawn deeper than the pool line**. The trap stab through the pool line at the right is where the blue entry mark goes, and small green `$` signs sit at the engineered high and above the target line (the refreshed buy stops). Relative depths on the drawing: pool lows shallow, left-hand low deepest, entry stab between the two.

## 1. Preconditions (setup arming) — ALL required

### Rule 1.1 — Something must have been taken from the left (directional validation)
Price must first run a level from the left-hand side in the *opposite* direction of your intended trade — e.g., for longs, an old low is swept ("grabbed something from the left-hand side, aka an old low", V2 [3:58]; "first step: taking out something from the left-hand side... that's what actually validates us looking for the sell" [inverted case], V2 [27:48]; "price trades below an old low from the left-hand side — now that bullish idea is activated", V2 [55:22]).
- **V1 agreement:** same requirement expressed as the strict rule — no buys until the low is taken (V1 [24:29]–[25:08]) — and in every chart example ("we spiked out these lows and never returned", V1 [75:45]–[76:22]).
- **V3 agreement:** the weekly sell-off clearing the chain of old lows into an LB is what arms the entire long campaign (V3 [1:52]–[3:06]).

### Rule 1.2 — A confirmed target pool must exist (the draw)
There must be identified, *market-confirmed* liquidity in your trade direction: equal highs / respected highs overhead for a long (V2 [16:42]: "Think about it — where is the liquidity?... You want to be targeting that liquidity"; V1 [11:32]: "a lot of people make the mistake of... but what liquidity are you targeting? There needs to be that logic"; V3 [3:06]: "the only logical liquidity point"). **No target pool → no trade**, even if a sweep occurs (V1 [14:32]; V2 [29:29]: "You need to make sure you always have a reason, a logic for price to move to the upside. Is there highs intact?").
- All three sources agree; V1 and V2 state it most forcefully as the anti-pattern-trading rule.
- *Visual: how the target pool and the engineered zone are told apart (V2 gold 15m/5m, Jan '26):* the **target pool** is the equal-highs zone — the left-hand high ~5,110 plus the two circled swing highs (~5,104–5,106) that respected it — marked as one red box **5,095.2–5,109.8** (`../03-images/Video2/shot_010.jpg` [31:52] raw levels, `shot_023.jpg` [32:10] circles, `shot_018.jpg` [33:36] box values). The **engineered liquidity** is the *separate, later* high that printed after the old-low sweep (~4,998) and respected that whole box from below — labeled "Eng. LQ" on the box's rightward extension (`shot_011.jpg` [34:44]). Same red box, two roles: the highs that *built* it are the target; the high that *respects* it afterwards is the arming condition.

### Rule 1.3 — Engineered liquidity must print (V2's "no engineered liquidity, no model")
As price first approaches the target pool, it must **respect it and retrace** — printing a high under the target that "respects highs to the left" — evidencing sellers entering in front of your target. "The most important part to this model: if you don't see engineered liquidity, it's not a Da Vinci model" (V2 [6:14]–[6:34]); "no engineered liquidity, no model. If we have engineered liquidity, then the model is active" (V2 [28:11]). The engineered high both (a) confirms/refreshes the liquidity above (more buy stops now rest there) and (b) supplies the *reason* for price to go up after the trap (V2 [6:58]–[7:18], [66:59]).
- **V1:** does not use the term, but the identical structure is present: the respected high left on the left-hand side that sellers trade from, whose respect confirms liquidity above, is drawn in every diagram (V1 [8:19]–[8:59], [21:32]–[22:46]: "we trapped sellers... high respected high, moved away — there's liquidity above that high"). Treat V1's "respected high before the false move" as the same object.
- **V3:** uses the exact V2 term ("look at the engineered liquidity we have at the highs", V3 [9:16]) and the exact mechanic ("sellers are selling these areas... it reacts off it to build liquidity — so there's liquidity above this high", V3 [7:35]).
- *Visual confirmation of the geometry (V2 shots):* on the whiteboard the engineered high is drawn clearly **below** the target-highs line — reaching roughly 80–90% of the way up, not touching it (`../03-images/Video2/shot_029.jpg` [5:21], circled and labeled "ENG LQ"). On the gold 15m/5m chart the same object is concrete: the left-hand high sits at ~5,110, the equal-highs target zone is drawn as a red box 5,095.2–5,109.8, and the two later "respecting" swing highs print at ~5,104–5,106 — i.e. *inside the lower half of the target zone* without trading through its top (`shot_023.jpg` [32:10] circles, `shot_018.jpg` [33:36] box values, `shot_011.jpg` [34:44] "Eng. LQ" label). So the arming condition tolerates an undershoot of roughly 0.1–0.3% of price; a touch is not required, and a wick *into* the marked zone still counts as respect.

### Rule 1.4 — Early buyers must be induced, then a pool built below
After the engineered-liquidity retrace begins, the market typically breaks a minor high (inducing buyers who read it as a BOS) and/or respects a low, building the pool that will be trapped: "we have just induced buyers — it's a common retail concept of high taken out, pullback, and they want to buy this thing... I view that to be early buyers. I want to see price below the low" (V2 [51:22]–[51:49]; also V2 [48:00]–[48:27]: "lows taken, highs taken... people want to be buying above this low — I view this low to have liquidity, so I want to buy below it"). V1: the whole blue-box discussion — reactions above the lows are false and only build the pool (V1 [9:33]–[10:12]). V3: "buyers induced after taking out this high... buyers trapped" (V3 [7:05]–[7:35], [11:09]–[11:43]: "at the least, you want to see price below this low... since we have induced buyers, people want to be buying above this low").
- The pool to be swept must itself be *confirmed* by the low-respecting-low grammar (V2 [34:04]–[34:34]; V3 [8:05]: "high taken out, low respecting low — price has literally confirmed to us that we have liquidity below this low. Wait for price to come below this low").

### Rule 1.5 — A liquidity block (or equivalent no-liquidity extreme) should sit beyond the entry
The sweep should deliver price into (or at least toward) a level that holds **no** liquidity — a prior sweep-wick low ("LB") — because that is why the reversal is possible there: "this reaction is possible — why? We have spiked liquidity; there shouldn't be any liquidity below this low right now" (V1 [44:03]–[44:44]); "there's no liquidity below this low, therefore why would we run this low? We tap into these areas, take entries off them" (V3 [12:15]); "we have another low that has spiked out previous lows... I always buy once the lows are taken out — stop goes below this low from the left-hand side" (V2 [51:49]–[52:12]).
- **Divergence in emphasis:** V3 makes the LB an explicit checklist item ("liquidity block below — everything checks the boxes", V3 [5:56]) and reuses it as the entry zone itself ("anywhere below this black line is a valid buy — why? LB below", V3 [9:59]). V2 treats it primarily as the stop anchor and skips trades when the LB is too far (see Rule 4.3). V1 expresses it as "no liquidity below this low → safe place to take the entry / put the stop" (V1 [76:22]–[76:54]) without the LB name.
- *Visual confirmation of the entry-zone depth (V3 shots):* in entry #1 the swept liquidity line is 19,923.75 and the LB directly below it spans 19,828.00–19,923.75 (~96 NQ points, ~0.5%); the entry limit fills at the LB's **top edge** (19,829–19,830) (`../03-images/Video3/shot_012.jpg` [5:51], `shot_014.jpg` [6:09], `shot_017.jpg` [6:59]). In entry #3 the "anywhere below this black line" zone runs from the line at ~20,767.50 down ~135 points to the stop just beyond the 15m LB at 20,632.25 (`shot_021.jpg` [10:37]). So "valid buy anywhere below the line" in practice means: the band between the swept level and the far side of the LB beneath it — roughly 100–135 points on NQ in these 1H/15m cases.

## 2. The trigger — entry rules

### Rule 2.1 — Enter when the identified pool is swept. Immediately. No over-refinement.
> "As soon as, and this is very important, ... once this low right here is taken, where the liquidity is, you enter your buy position." (V2 [14:11]–[14:35])
> "A lot of people like to overrefine and look for an imbalance in this low. In my opinion, unnecessary... typically when people overrefine you're going to start missing entries." (V2 [13:46]–[14:35]; repeated [48:50]: "I always buy once the liquidity is taken. I don't need to over refine and find an imbalance in here.")

- **V1 agreement:** "Would you just execute once the high is taken? — Exactly. Once this high is taken... I'll take it as soon as the high is spiked out" (V1 [30:34]–[31:14], [46:33]–[47:05], sell-side). Market execution, not limits, is his personal preference from forex-spread days (V1 [46:33]–[47:05]).
- **V3 agreement:** "We need to be taking an entry once the liquidity is taken. Boom. Entry" (V3 [5:56]); "as soon as price stabs out this low, anywhere below this black line is a valid buy" (V3 [9:59]); "every entry: once liquidity is taken, once liquidity is taken — the same thing over and over" (V3 [10:38]–[11:09]).
- **Nuance (V2, HTF/passive variant):** on higher-timeframe setups or when asleep, a **limit order resting at the liquidity level** with stop below the LB is equivalent — "you set a limit at this liquidity point, stop loss goes below, you don't even need to look at the chart" (V2 [58:10]–[58:35]); his USDJPY trade was exactly this (V2 [68:09]–[68:30]).
- **Nuance (V1, live session):** in live trading Marco distinguishes the *initial* entry (at/into the no-liquidity area below the lows, after the sweep) from *scale-ins*, which each require their own fresh mini-sweep ("we'll add another three contracts below this low if we can trade below it", V1 [91:08]–[92:05]) — see file 04.

### Rule 2.2 — The entry price is at/through the swept level, toward the extreme
Best case, entry fills right at the stab of the level with the LB just beyond (V2 [39:09]: "your entry as soon as the low gets stabbed... stop loss goes below the low"). You do not need the absolute extreme: "you don't need the very top... you don't need the very bottom... direction and bias is what pays the profits" (V1 [52:21]–[52:59]); a non-extreme fill still yielded ~1:5 vs 1:12 in the gold example (V2 [42:48]–[43:33]).

*Visual quantification of the fill tolerance (V2 gold 1m):* extreme entry **5,051.19** vs conservative entry **5,057.17** — i.e., the forgiving fill is at the *pool level itself* (~6 pts / 0.12% above the extreme), with the **same stop 5,046.19** and same capped target 5,111.66; on-screen RR degrades from ~1:12 to **4.96** ("almost a one to five", `../03-images/Video2/shot_007.jpg` [43:35]). The uncapped runner to 5,179.5 showed **RR 11.14** live on the same conservative entry (`shot_009.jpg` [43:42], `shot_005.jpg`). So the valid fill band in this example spans the pool line down to the LB — anywhere inside it keeps the model's minimum-RR floor (Rule 4.3) intact.

### Rule 2.3 — Lower-timeframe confirmation variant (when the direct stop is too wide)
When the swept structure's LB is far away ("the stop loss is too big, the RR is shot... I just don't take those trades", V2 [35:05]–[35:25]), drop to the lower timeframe and wait for the **same model to print fractally there**: the LTF builds its own buildup → sweeps its own last level of internal liquidity into a LTF liquidity block → enter on that LTF stab with a tight LTF stop (gold 1m example, V2 [36:55]–[39:32]).

*Both sides of the trade-off are on-screen in the gold example (V2 shots):* the **rejected direct 15m/5m entry** measures entry 5,049.5, stop 5,013.6 (35.9 pts / 0.711%, below the LB low), target 5,110.9 (+61.9 pts) → **RR 1.72** — the "one to 1.7" the host quotes, under Marco's 1:3 floor (`../03-images/Video2/shot_028.jpg` [35:38]). The **1m replacement entry** it converts into: the 1m buildup's last level sits at ~5,050–5,051; the 09:19 stab-wick below it (low ~5,047.3) is the 1m LB; the 10:00 restab fills the entry at **5,051.19** with stop **5,046.2–5,046.9** (~4.3–5.0 pts, CFD breathing room beyond the wick); same HTF target, hit at **5,111.66** ~5 hours later → the on-screen "1 to 12" (`shot_021.jpg` [36:47] TF drop, `shot_001.jpg` 1m levels, `shot_008.jpg` [39:25] entry/stop tool, `shot_002.jpg` wick-LB underlined, `shot_026.jpg` [39:45] + `shot_025.jpg` [39:53] playout, `shot_036.jpg` [40:03] 10:00→~15:00 duration). Net effect of the drop: stop shrinks ~8×, RR multiplies ~7×, entry price barely moves. "Higher time frame for direction and then it happens again on the lower time frame for entry" (V2 [39:32]–[40:00]; same idea V1 [31:14]: "your execution would come off a more fractal confirmation using the same mindset, same model"; V3 [15:11]–[15:54]: LTF refinement is how "the RRs drastically increase"). V3's milder version of the same fix: refine the LB on a lower timeframe (4H LB too big → 1H LB shrinks the SL, V3 [8:05]–[8:41]). *Visual: the refined 1H-LB stop for V3's entry #2 is 404.75 points (1.98%) — entry 20,446.75, stop 20,042.00, giving RR 7.2 to the 23,363 target (`../03-images/Video3/shot_028.jpg` [9:00], `shot_024.jpg` [9:11]); the rejected unrefined 4H-LB stop is never shown numerically on screen.*

### Rule 2.4 — Timing filters on the trigger (V1 only; V2/V3 silent)
- Trade a fixed session window; Marco trades New York, marks 9:30 stock open, looks for entries **after** the open (V1 [42:02]–[43:25], [49:30]–[50:00]: "I have a specific time window... what happens outside of the time window is completely irrelevant to me").
- **Never enter before scheduled news; wait ~2–4 minutes after the release** (V1 [67:13]–[67:52]).
- Timeframe-close confluence strengthens the trigger: the live NQ entry came as "the 4-hour closed, spiked it right into my area... at 10:00 a.m." (V1 [83:36]); he watches 5m/15m/30m/1H closes throughout (V1 [86:15]–[87:54], [97:15]). "You need like a heavy timing confluence in order to take these kind of entries" (V1 [86:59]).
- Avoid entering into NY lunch (dead volume) (V1 [105:56]).

## 3. Stop-loss rules

### Rule 3.1 — Stop goes beyond the swept structure, behind the left-hand-side low/LB. Always.
> "Stop loss is going to be below this low... your stop loss is going to cover this low from the left-hand side." (V2 [16:17]–[16:42])
> "Stop covers this high always. I don't want to get greedy and get too low. Always above the high." (V1 [69:02]–[69:35], sell-side)
> "Remember, the stop loss is the most important part. You need to make sure your stop loss covers here. Don't get greedy." (V2 [43:11])
> "When liquidity is taken, stop covering liquidity block. Liquidity taken, stop below liquidity block — all the way up into this last entry." (V3 [14:41])

All three sources are in full agreement: the stop is *structural* — behind the LB / the left-hand low that the sweep tapped — never a fixed pip/tick count, never inside the swept range.

*Visual confirmation of the whiteboard ambiguity (V2 shot):* the drawn stop in the master diagram anchors to the **deeper left-hand low, not the swept pool low** — in the finished drawing "SL" is written in red *below the leftmost deep low*, which the marker drew visibly deeper than the pool lows the entry stab runs (`../03-images/Video2/shot_031.jpg` [20:03]; entry is the blue mark at the stab, target the blue dash above the highs line). This settles the two possible readings of V2 [16:17]–[16:42] in favor of the left-hand-low anchor.

*Visual nuance (V3 shots):* "stop covering the liquidity block" does not always mean strictly beyond its far edge. V3's entry #5 stop sits at 21,432.25 — **inside the lower half** of the HTF LB (21,396.00–21,522.75), covering most but not all of it (`../03-images/Video3/shot_026.jpg` [15:13], `shot_019.jpg` [14:28]). Entry #1's stop (19,295.25) is placed below the deeper *left-hand low*, ~530 points beyond the LB used for entry (`shot_014.jpg`, `shot_017.jpg`). So the anchor is chosen case-by-case: sometimes the LB's interior, sometimes a deeper left-hand low — but always behind structure that swept liquidity.

### Rule 3.2 — Instrument-specific buffer
- **Futures:** stop can sit "literally a tick or two above the high" because everyone trades one centralized feed (V1 [68:28]–[69:02]).
- **Forex/CFD:** give "breathing room" / keep it "well above or below" due to spread and differing feeds (V1 [68:28]; V2 [39:32]: "this is going to be on a CFD chart — let's give it a little bit of breathing room").

## 4. Target rules

### Rule 4.1 — Target = the opposing confirmed liquidity pool. Never a fixed RR number.
> "Simple things: I'm targeting opposing liquidity." (V1 [69:02]–[69:35])
> "Target back at the highs. Remember, we're not guessing where to target — the market communicated that to us: high respecting high." (V2 [49:13])
> "Don't forget about our targets, guys: these equal highs left for us, done on purpose... all the way back at the extreme." (V3 [5:56])
> Anti-fixed-R rule: "A lot of people like to say I'll take a partial at 1:3 or 1:5... it's literally just a random point in the chart... if I'm analyzing the chart, I'm going to be targeting these areas" (V1 [33:31]–[34:07]; V2 [59:17]–[59:39] same).

### Rule 4.2 — Layered targets: LTF/internal partial, HTF/external full
Nearest opposing internal pools (engineered-liquidity highs, structural highs, prior-day levels) serve as partial points; the HTF external pool is the full target: "there's usually a more lower-timeframe target I'm using to partial, and then you'll have your higher-timeframe target you can finish the whole trade at" (V1 [69:35]–[70:08]; V2 [58:35]–[58:55]: engineered-liquidity highs "could be used as a partial point... and then the external point"; V3 [12:51]: "great intraday targets on the way back up... but don't forget that higher time frame narrative — we are targeting the highs").

*Visual: engineered highs flipping from arming condition to target (V2 gold 15m/5m, Nov '25):* after entry #1 the chart carries **three successive "Eng LQ" callouts stacked toward the external target** — ~4,062, ~4,088 and ~4,103, under the 4,109.5 target line. The rally off entry #1 "grabs" the ~4,088 engineered high (drawn arrow into it) before selling off to build the next setup (`../03-images/Video2/shot_022.jpg` [50:20], `shot_014.jpg` [50:32], `shot_020.jpg` [50:51]). Each bearish reaction that armed one leg becomes the liquidity the next leg runs — the mechanism behind "every bearish reaction is engineered liquidity" (V2 [52:12]–[52:41]).

### Rule 4.3 — Minimum reward filter
Marco: "I perform the best... when my RR is minimum 1-to-3 minimum" (V2 [36:18]–[36:39]); if the structural stop makes RR poor ("shot"), skip or seek the LTF confirmation entry (V2 [35:05]–[36:55]). He also skips *small* absolute moves: "I won't be paying myself yet because we're only looking at a 140-tick move. I'm not interested in a small move like that" (V1 [94:38]–[95:34]). V1/V3 don't state a numeric floor (V3 shows a 1:3.6 as its smallest example, V3 [15:54]).

### Rule 4.4 — Beyond the target
Once the target pool is taken, that sweep may itself arm the *next* setup in the other direction — but only with fresh reason/logic, never automatically (V2 [29:07]–[29:48]: counter-bias sell whose target sweep can set up the with-bias buy; V1 [28:09]: reversals typically occur once external is taken).

## 5. Invalidation and failure handling

### Rule 5.1 — Hard invalidation = stop hit (price keeps running beyond the LB)
Nothing in the model is 100% (V1 [29:25], [57:31]; V2 [19:45]). If the swept extreme keeps going, you're out at the structural stop; V2's re-arm rule: "let's just say price comes down and sweeps out this low [again] — then I need to wait for something like this to occur *again*: I need to see early buyers induced, I need to see those early buyers taken out, and then I will look for my entry again... it does not mean the direction, the bias, the idea is incorrect" — because the overhead target pool still exists (V2 [22:00]–[22:20]). A failed attempt resets to Rule 1.4, not to a flip of bias.

### Rule 5.2 — Setup never armed / trade missed
If price respects the pool and runs *without* sweeping it: "it doesn't matter — this is not a move I was supposed to be in" (V1 [25:08]–[25:49]). The unswept pool remains a future target (V1 [25:49]–[26:28]). No chasing; the bias-lockout rule (file 02 §D) stays in force.

### Rule 5.3 — Scale-in invalidation is independent
Each add has its own local invalidation: "now that we've traded below this low, I do want to see price stay above 23142 or else this scale-in is invalid, which is completely fine" (V1 [92:05]). Adds that don't independently satisfy the model are rule-breaks (V1 [79:44]–[80:55]).

### Rule 5.4 — Behavioral invalidations (rule-breaks that void the system)
- Buying above the lows / selling below the highs (inside the trap zone) because a reaction "looks strong" (V1 [10:12], [78:39]–[79:13]: SMC-background students' classic error — "based off my system, I'm not taking entries in this area. It needs to be below this low").
- Entering on pattern-match without a target pool (V1 [11:32]; V2 [29:29]; V3 [7:35]).
- Trading a liquidity-void chart (V1 [14:32]–[15:06]).
- Trading outside your session window / before news (V1 [49:30], [67:13]).

## 6. What the sweep looks like (recognition cues)

- The trap move is a **false push**: a spike through the level that fails to hold — often a wick — followed by the reversal ("this false move to the upside... we take out that seller liquidity and then the move occurs — boom and boom", V1 [21:32]–[22:46]).
- Reactions *at* the level before the sweep are choppy/false; expect the extreme possibly to be stabbed more than once ("just because we've ran the 4H low does not mean this lower-timeframe low isn't off the cards yet — this can definitely still get spiked out before the move starts going up", V1 [84:30]–[85:11]; "lows have been spiked once more — it's completely fine, we can hang around down here for a bit", V1 [86:59]–[87:54]).
- Candle-close confirmation is used for *adding*, not for the base entry: "if we can get a nice five-minute close above, I will add a little more volume... not a strong close for me → I won't take anything now" (V1 [86:15]–[86:59]).
- Post-entry, expect a possible deeper stab to the true extreme before the run ("sometimes what occurs is we'll induce lower once more and then the move will start occurring — that's why I got my stop below PDL", V1 [84:30]–[85:11]).

## 7. Canonical worked examples (for study/backtest reference)

| # | Source | Instrument / date | What it demonstrates | RR |
|---|---|---|---|---|
| 1 | V1 [41:28]–[52:21] | YM (Dow futures), 30m→5m, NY session | Textbook short: 30m equal lows target, Asia sweep, internal-highs sweep entry, stop above left-hand high | 1:3.6 to first pool, ~1:10 HTF (V1 [50:00]) |
| 2 | V1 [53:56]–[61:32] | EURUSD 4H/daily (Feb–Apr 2025) | Bias lockout + draw prioritization: only buys below the identified low; nothing below it but a huge gap | n/a (analysis) |
| 3 | V1 [63:28]–[70:08] | NQ 15m→5m→1m, mid-April | Short after news spike sweeps the high; stop a tick above; partial at trapped-buyer lows | n/a |
| 4 | V1 [72:24]–[77:31] | NQ 5m→1m, April 1 | Long: multi-respected lows swept, entry off prior-day no-liquidity wick zone, partial above first high | small first target |
| 5 | V1 [83:36]–[107:47] | NQ live, NY session | Full live management: 4H-close timing, scale-ins below fresh sweeps, stop trailing, partials at pools, lunch-hour deadline | ~$6,400 across 4 accounts (V1 [107:47]) |
| 6 | V2 [30:40]–[43:33] | Gold 15m + 1m (Tue 27 Jan '26) | HTF Da Vinci for direction + 1m Da Vinci for entry; last-level-of-liquidity stab. **Reconstructed from shots:** target box 5,095.2–5,109.8; rejected direct entry 5,049.5/stop 5,013.6 = RR 1.72; 1m entry 5,051.19 (10:00), stop 5,046.2, target hit 5,111.66 (~15:00) | 1:12 extreme / 1:4.96 conservative (entry 5,057.17); runner RR 11.14 |
| 7 | V2 [46:03]–[54:57] | Gold 15m/5m (Nov 20–24 '25) | Three stacked entries; every bearish reaction = engineered liquidity. **Entry #1 from shots:** tapped-twice red box 4,031–4,043; entry 4,032.37, stop 4,022.07 (below left-hand low ~4,025), target line 4,109.51 → RR 7.49 | 1:7.5, 1:7 |
| 8 | V2 [55:02]–[63:11] | NQ 5m (replay) | HTF passive limit entry at pool, stop under LB, "don't need to look at the chart"; second entry into LB | ~1:4–1:5; 1:3.5 |
| 9 | V2 [64:40]–[69:17] | USDJPY HTF (live trade that week) | Bearish Da Vinci, limit entry while asleep at engineered-liquidity high/LB, $6,600 realized + partials running | ~1:5 shown |
| 10 | V3 [0:43]–[16:33] | NQ weekly→4H→1H | Entire long campaign off weekly equal-highs draw; five entries, each "liquidity taken → stop below LB" | 1:6, 1:7, 1:19, 1:14, 1:3.6 (V3 [15:54]) — pairing resolved below |

**V3's five entries, fully reconstructed from the screenshots** (all prices are NQH2026 chart values; target for all = weekly equal highs 23,359–23,364):

| Entry | Swept level | Entry price | Stop | Stop distance | RR (on-screen) | Evidence |
|---|---|---|---|---|---|---|
| 1 | 19,923.75 (1H low) | 19,829–19,830 (top of LB 19,828–19,924) | 19,295.25 (below left-hand low) | 533.75 pts | 6.62 → the "1:6" | `../03-images/Video3/shot_012.jpg`, `shot_014.jpg`, `shot_017.jpg` |
| 2 | 20,446.50 (1H low) | 20,446.75 | 20,042.00 (below refined 1H LB) | 404.75 pts | 7.2 → the "1:7" | `shot_028.jpg`, `shot_024.jpg` |
| 3 | ~20,767.50 (black line, 15m) | 20,767.50 | 20,632.25 (below 15m LB) | 135.25 pts | ≈19.2 → the "1:19" | `shot_015.jpg`, `shot_021.jpg` |
| 4 | tap into left-hand LB | 21,522.75 (top of blue-box LB 21,396–21,523) | 21,396.00 (LB bottom) | 126.75 pts | ≈14.5 → the "1:14" | `shot_002.jpg`, `shot_018.jpg` |
| 5 | 21,849.00 (1H low under 20-hour red-box buildup) | 21,850.25 | 21,432.25 (inside/covering HTF LB) | 418.00 pts | 3.63 → the "1:3.6" | `shot_019.jpg`, `shot_026.jpg`, `shot_025.jpg` (overview) |

The five RR figures at V3 [15:54] map to the five entries **in chronological order**.

---

**Next file:** `04-trade-management-and-risk.md`.
