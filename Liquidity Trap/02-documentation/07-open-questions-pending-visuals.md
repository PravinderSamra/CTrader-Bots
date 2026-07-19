# 07 — Open Questions Pending Visuals

The transcripts are audio-only captures of chart/whiteboard walkthroughs. The speakers constantly point ("here", "this level", "like this", "check this out") at things the captions cannot see. This file catalogues the moments where a visual reference would **materially change or clarify** understanding — i.e., where the docs in files 01–04 had to interpolate from context — so a future pass can resolve them against screenshots.

**Screenshot status:** stills are being collected from Google Drive into `../03-images/`. `Video3/` is complete (28 shots + `manifest.json`) and `Video2/` is complete (36 files); `Video1/` is pending. When resolving an item below, match its timestamp against the relevant video's manifest, update the affected doc file(s), and strike the item here.

Citations are `(Video N, [MM:SS])` into `../01-transcripts/`.

---

## A. Cross-cutting ambiguities (a visual would settle these once, for all files)

These are the highest-value unknowns because they are *parameters* every chart example depends on, and file 08's bot design needs numbers for them:

1. **What geometrically counts as "respect"?** Must the approaching high/low *touch* the prior level, merely come near it, or is a wick-through-with-close-back-inside still a respect? Every marking decision hinges on this, yet it is only ever shown, never stated ("this high respecting this high to the left", V3 [1:16]; "high respected high", V1 [3:22]; "respecting this whole area here", V3 [4:11] — an *area*, not a line). Any clean screenshot of a marked respect would give the tolerance in ticks/points.
2. **How equal is "equal / relative equal"?** The tolerance band for equal lows/highs is never quantified (V1 [41:28] "equal lows, relative equal lows"; V3 [0:43] weekly "equal highs"; V1 [83:36] "relative equals"). A screenshot with the marked box would show the acceptable spread.
3. **How far is "move away"?** The displacement required to confirm a respect (distinguishing it from mere chop) is only demonstrated (V1 [13:13], [20:51]; V2 [9:36]). Needed as a distance/ratio.
4. **Level vs zone.** Levels are drawn sometimes as lines, sometimes as boxes ("blue line" V3 [5:24] vs "blue box" V3 [2:27]; "mark out this whole area" V2 [68:09]). When is a pool a price and when a band — and how tall are the bands?
5. **Color conventions conflict between videos.** V1's whiteboard "blue box" is the *trap zone above the lows* (V1 [9:33]), while V2/V3's blue box is a *liquidity block* (V2 [34:04] context; V3 [2:27]) and V1's live blue lines are *targets* (V1 [89:36]). Red boxes are trap/retail zones in all three, but V3 also uses a red box for a *tapped chain of lows* (V3 [2:27]) and for *buildup* zones (V3 [7:05], [13:29]). Screenshots would fix each video's actual legend. Until then, files 02/03 adopt V2/V3's convention (red = trap, blue = LB/level).
6. **Where exactly inside the swept zone do entries fill?** "Anywhere below this black line is a valid buy" (V3 [9:59]) defines the top of the entry zone but not its depth — is any price between the swept level and the LB valid, and does the LB's *near edge* or *far edge* bound it? (Also V1 [29:57] "entries in here somewhere"; V1 [75:45]–[76:22] entry "off" a prior-day wick area.)
7. **Stop offset behind the LB.** "A tick or two" for futures (V1 [69:02]) is concrete, but the CFD "breathing room" (V2 [39:09]; V1 [68:28]) is only shown on-screen. The gold 1m example's drawn stop distance would quantify it.

## B. Video 1 (Chart Fanatics ep. 1 — whiteboard, chart examples, live NQ)

*Screenshots pending (`../03-images/Video1/` empty).*

| # | Timestamp | Moment | What's unresolved / why it matters |
|---|---|---|---|
| B1 | [2:39]–[3:59] | First whiteboard drawing: "we have high, low, high... This high respected previous highs... there's now liquidity above this high" | The canonical downtrend diagram. Exact geometry (how many swings, where the respected high sits relative to the prior high) is the template for every later example. |
| B2 | [4:36]–[6:27] | Uptrend inducement diagram: "once price returns back to this area at the extreme... they're going to want to buy down here" | Where "the extreme" retracement area sits relative to the broken high — how deep the retail pullback zone is drawn. |
| B3 | [8:19]–[10:49] | Full trap diagram with OB/POI, blue box, and the [10:49] "internal lows" sequence | V1's blue box = trap zone (see A5). Also: where the post-trap buy entry arrow is drawn relative to the lows ("buys below these lows" — how far below?). |
| B4 | [15:06]–[16:51] | EURUSD Feb 2025 story told on the whiteboard: "this move happened, this right here... below that point, there's no liquidity" | Which EU level/date is meant; verifiable against a real EURUSD chart (Feb–Apr 2025) once the drawn shape is visible. |
| B5 | [20:51]–[22:46] | Two-panel HTF/LTF fractal diagram: "so it's just basically like this, boom and boom" | The relationship drawn between the HTF low and the LTF trap ("boom and boom" = two arrows the captions can't see). Clarifies file 03 §2.3's HTF→LTF handoff. |
| B6 | [24:29]–[25:49] | The strict-rule diagram in red marker: "until this low is taken out right here... boom, boom, boom. Now, I can look to sell" | Which low/high in the drawn sequence anchors the lockout — the *last* internal low or the *origin* low. Affects file 02 §D's mechanical restatement. |
| B7 | [28:44]–[30:34] | No-liquidity-high execution diagram: "I'm looking to take entries in here somewhere. Okay, sell entries up here" | The extent of the "in here" sell zone below the swept high (see A6). |
| B8 | [41:28]–[43:25] | YM 30m→5m: "we can mark on right away... a level of equal lows, relative equal lows"; 9:30 line; "we stabbed out previous lows here" | Actual prices/dates of the equal-lows pool and which prior lows were stabbed; the tolerance question A2 in the wild. |
| B9 | [43:25]–[45:24] | YM: BOS red box, Asia purple box, "we leave these equal highs" pre-open | Placement/height of the red trap box relative to the BOS; which internal highs count as the pre-open equals. |
| B10 | [45:24]–[47:43] | YM entry: "this bullish move... came up to sweep these internal highs... I'm looking to take my sell entry there. Right there." | The exact bar and level of the entry, and the drawn sell-tool showing stop above which high (the [50:32] RR readout of 1:3.6 depends on it). |
| B11 | [50:32]–[51:45] | Next-day YM continuation: "both these red boxes I'm viewing as a trap" | Which two zones (pullback level vs extreme imbalance) the boxes cover — the clearest dual-trap example in the set. |
| B12 | [53:56]–[59:45] | EURUSD 4H/daily: "if I was looking to take buys, it would only be below here"; "the next internal low is all the way down here and there's a huge gap in between" | The identity of *the* low (file 02 §C step 7's priority rule is generalized from this one example) and the structural-liquidity circle at [59:45]. |
| B13 | [59:45]–[60:55] | FOMC wick: "this wick actually went lower... we came up, swept out some more liquidity to the left, brought in buyers, took those buyers out and then the move occurred" | Which left-hand liquidity the wick swept — a live case of internal-vs-external sequencing worth verifying on a real chart. |
| B14 | [63:28]–[66:37] | NQ 15m→5m→1m mid-April: internal lows chain, "massive inefficiency right below", the high "swapped" pre-NY | Which high became the no-liquidity high, and where the inefficiency sits — needed to reproduce the example. |
| B15 | [67:13]–[69:35] | NQ news-spike short: "this high, right, swept this level of liquidity, leaving this whole area... I'm essentially looking to take an entry off of" | The extent of the entry zone at the swept high; partial level "down at these lows" — which lows. |
| B16 | [72:24]–[77:31] | NQ Apr 1 long: lows "respected once, twice, three, four times"; prior-day wick zone: "we spiked out these lows... never returned... this whole area here is definitely an area I can look to see a buy from" | Boundaries of the prior-day no-liquidity zone (entry + stop anchor); which internal highs were the first target ("small partial above the high"). |
| B17 | [83:36]–[85:11] | Live NQ: "spiked it right into my area I want to take a buy from below these lows"; targets marked ("imbalance above... highs we left in London... relative equals also 4-hour high... a high to the left"); "stop below PDL" | The live trade's actual entry zone, the four marked targets, and PDL's price. This is the most completely-managed example in the corpus; every number is on-screen only. |
| B18 | [89:36]–[92:05] | Scale-ins: "add below this low here at 10:19... need to trade below this low"; "price stay above 23142 or else this scale-in is invalid" | Which 1m lows gated each add; 23142's relation to the add price (the only absolute price spoken in V1). |
| B19 | [92:05]–[96:30] | Anticipated stall: "once we trade back up into this high... won't be surprised if we struggle in here"; "approaching this trap area" red box | Which left-hand structure defined the stall zone — the worked example of anticipating mid-trade resistance (file 04 §8). |
| B20 | [102:13]–[105:56] | "This high tapped into what? Absolutely nothing" + final target "23 237.5" | The distinction being drawn between a high that tapped nothing (fuel for continuation) vs structure; and the target's derivation from the marked highs. |

## C. Video 2 (Chart Fanatics ep. 2 — Da Vinci model)

*Screenshots COLLECTED — `../03-images/Video2/` (36 files). Ready to resolve against the shots.*

| # | Timestamp | Moment | What's unresolved / why it matters |
|---|---|---|---|
| C1 | [3:58]–[6:34] | Whiteboard: engineered-liquidity definition — "look how we are respecting it, printing this high and then the market starts to retrace" | How close the engineered high is drawn to the target pool (touching? just below?). This is *the* arming condition (file 03 §1.3); its geometric tolerance is unstated everywhere. |
| C2 | [9:36]–[11:19] | Full bullish Da Vinci diagram: "high is taken, this low respecting this low and boom we have built liquidity... sellers are entering from an area on the left hand side" | Canonical relative positions of: left-side low, pool, engineered high, seller POI. The master template file 03 §0 verbalizes. |
| C3 | [13:20]–[16:42] | Entry/stop/target drawing: "entry here and stop loss is going to be below this low... your stop loss is going to cover this low from the left-hand side" | Whether the drawn stop anchors to the *swept pool low* or a *deeper left-hand low* — the captions support both readings; file 03 §3.1 chose the left-hand/LB reading from corroborating quotes. A frame would confirm. |
| C4 | [25:24]–[28:38] | Bearish (inverted) whiteboard sequence | Mirror-case check that all objects invert cleanly (file 03 assumes exact inversion per V2 [22:44]). |
| C5 | [31:26]–[33:38] | Gold 15m: "these two swing points, these two highs respecting this high from the left"; equal highs marked as future target | Which highs constitute the target pool vs the engineered zone — the example's whole logic chain hangs on which is which. |
| C6 | [34:04]–[35:25] | Gold: internal lows marked; "we had a big... liquidity block, a low that doesn't hold any liquidity. So the stop loss is too big" | How far the LB sat below the pool (the RR-shot condition, ~1:1.7 per host [35:56]) — quantifies file 03 §2.3's trigger for dropping to the LTF. |
| C7 | [36:55]–[39:32] | Gold 1m: "we run that last level of liquidity... not just this low, not just this low... all the way to the extreme, it's going to be this low down here. And... this last wick here... not to hold liquidity" | Identifying the "last level" among ~5 candidate lows, and the wick-LB below it. The purest trail-to-the-extreme demonstration (file 02 §E); currently reconstructed from words alone. |
| C8 | [40:26]–[41:35] | Zoomed entry: red box respect, "high taken, low respecting low" ×3 | The 1m grammar frame-by-frame — would make the best training/labelling reference for a detector (file 08). |
| C9 | [42:48]–[43:33] | Conservative-entry overlay: "even if you grab this low... you are still catching almost a one to five" | Which alternate low the conservative entry uses — defines how much fill-tolerance the model forgives. |
| C10 | [46:03]–[49:38] | Gold 15m second example: red boxes tapped "once, twice", buildup ("lows taken... highs taken"), entry at the low, stop below left-hand low | Which of the stacked lows was entry #1's trigger vs its stop anchor; the drawn 1:7.5. |
| C11 | [49:38]–[52:41] | Entries #2–3: "price rallies... and grabs what? The engineered liquidity"; "you have another low. I call it a liquidity block" | Which high was the engineered pool that got grabbed (it flipped from arming condition to *target* here — unique in the corpus, noted in file 03 §4.2), and the LB for entry #3. |
| C12 | [54:11]–[54:57] | Common-mistake overlay: "price temporarily respects this and goes long for two, three hours... then boom you get the sell-off and we trap" | The retail long zone vs the eventual entry level — the clearest side-by-side of trap vs trade. |
| C13 | [55:22]–[58:35] | NQ replay: "little possible extreme entry. Not a Da Vinci" at a no-liquidity low; then the limit-order setup ("set a limit at this liquidity point... stop loss goes below") | (a) What made the extreme entry a non-Da-Vinci (missing engineered liquidity? no pool?) — a boundary case for file 03 §1; (b) exact limit/stop placement of the passive variant. |
| C14 | [60:47]–[63:11] | Replay outcome + second entry "all the way down into... a liquidity block... look at the precision here" | The LB tap that filled entry #2 and the drawn 1:3.5/1:4–5 readouts. |
| C15 | [64:40]–[69:17] | USDJPY live trade: target pool ("low high taken, highs taken, lows respected, lows respected"), the multi-respected high ("respects it. Respects it... taps into it a bunch"), the entry LB ("a high that has taken out a previous high... I mark out this whole area") | The only real-money V2 trade: its marked pool, engineered low, LB zone, limit price, stop, and the 1:5 partial level. Also the *bearish* LB definition frame (file 01 §5b cites the words; the picture is missing). |

## D. Video 3 (Inter Equity Trading — NQ weekly→4H/1H)

*Screenshots COLLECTED and RECONCILED (2026-07-19). All 28 shots carry the YouTube playbar timestamp, so matches are exact. Note: the shot_NNN numbering follows Drive upload time, which is scrambled relative to capture order — the original iPhone filenames (IMG_1035–1062 in `manifest.json`) give the true chronological order.*

| # | Timestamp | Moment | Resolution |
|---|---|---|---|
| D1 | [0:43]–[1:52] | Weekly equal highs = macro draw | **RESOLVED** — see file 02 §B.3. Two weekly wick highs (Dec '24 / Feb '25, NQH2026 chart) marked as a single line, drawn at 23,397 then finalized at 23,364.25; tips within ~30–40 pts (~0.15%). `shot_004.jpg` [1:18], `shot_010.jpg` [1:55]. |
| D2 | [1:52]–[2:27] | Chain of tapped lows + red box | **RESOLVED** — see file 02 §C step 3. The chain is the cluster of 2024 lows ~18,400–19,300; one wide red box covers the whole cluster — confirming V3's atypical red-box use (feeds A5). `shot_011.jpg` [2:30], `shot_027.jpg` [3:04]. |
| D3 | [2:27]–[3:06] | HTF LB boundaries and tap depth | **RESOLVED** — see file 02 §C step 4. Blue box with top edge at 17,894.75; April '25 wick tapped ~1,400 pts into it (low ~16,4xx) before reversing. `shot_027.jpg` [3:04], `shot_020.jpg` [3:34]. |
| D4 | [4:11]–[4:47] | Respect against an *area* | **RESOLVED** — see file 02 §B.1. Red box top 20,751.75; the respecting high printed 20,545.75, ~200 pts *inside* the box — zone-based respect confirmed, no touch required (feeds A1/A4). `shot_003.jpg` [4:42], `shot_005.jpg` [4:46], `shot_014.jpg`. |
| D5 | [5:24]–[6:31] | Entry #1 geometry | **RESOLVED** — see file 03 §1.5 note + §7 table. Liquidity line 19,923.75; LB 19,828–19,924 (~96 pts); entry at LB top 19,829–19,830; stop 19,295.25 (below left-hand low, 533.75 pts); target 23,364.25; RR 6.62. `shot_012.jpg` [5:51], `shot_014.jpg` [6:09], `shot_017.jpg` [6:59]. |
| D6 | [7:05]–[8:05] | Which high acquired liquidity; sell forbidden | **RESOLVED** — see file 02 §D note. High marked 20,899.00 after respect at 20,839.75 (~59 pts); selling forbidden because the low side had just been taken. `shot_016.jpg` [8:01], `shot_023.jpg` [8:32]. |
| D7 | [8:05]–[9:16] | 4H LB vs refined 1H LB sizes | **PARTIALLY RESOLVED** — see file 03 §2.3 note. Refined stop = 404.75 pts (entry 20,446.75, stop 20,042.00, RR 7.2). The rejected 4H LB is never shown with on-screen numbers, so the RR *gain* from refinement can't be quantified. `shot_028.jpg` [9:00], `shot_024.jpg` [9:11]. |
| D8 | [9:16]–[10:38] | Black line / valid-buy depth | **RESOLVED** — see file 03 §1.5 note + §7 table. Engineered-liquidity red boxes at ~20,870–20,960 (15m); black line ~20,767.50; stop beyond 15m LB at 20,632.25 → valid-buy band ≈135 pts, bounded below by the LB's far side (feeds A6). `shot_015.jpg` [9:59], `shot_021.jpg` [10:37]. |
| D9 | [11:09]–[12:51] | Left-hand LB tap | **RESOLVED** — see file 03 §7 table. Blue-box LB 21,396.00–21,522.75 (~127 pts); wick tapped it precisely; entry at box top, stop at box bottom; intraday target lines ~21,980 and ~22,270. `shot_002.jpg` (fullscreen), `shot_018.jpg` [13:29]. |
| D10 | [13:29]–[15:11] | 20-hour buildup box + last stop anchor | **RESOLVED** — see file 03 §3.1 note + §7 table. Red buildup box from the 21,849.00 line up to ~22,000 (May 27–29); entry 21,850.25; stop 21,432.25 sits *inside the lower half* of the HTF LB (21,396–21,523) — "covering" the LB, not strictly beyond it. `shot_019.jpg` [14:28], `shot_026.jpg` [15:13]. |
| D11 | [15:54] | RR-to-entry pairing | **RESOLVED** — see file 03 §7 (new sub-table). The five figures map chronologically: E1 = 6.62 ("1:6"), E2 = 7.2 ("1:7"), E3 ≈ 19.2 ("1:19"), E4 ≈ 14.5 ("1:14"), E5 = 3.63 ("1:3.6"). On-screen position-tool readouts in `shot_017.jpg`, `shot_024.jpg`, `shot_021.jpg`, `shot_002.jpg`, `shot_026.jpg`. |

## E. Non-visual open questions (no screenshot will answer these)

Kept here so the "open questions" list is complete in one place:

1. **Numeric risk figures.** Marco's daily risk cap is "a specific figure" never stated (V2 [19:45]); per-trade % never stated (host's 0.5–0.75% at V2 [18:59] is the host's framing). Needs user's own decision (file 08 §J).
2. **Win rate.** Claimed "incredible" (V2 [20:05]) but never quantified; only resolvable by backtest.
3. **Session rules for non-index instruments.** V1's NY-window regime is demonstrated on index futures only; whether Marco applies any session filter to gold/FX day entries (vs the sleep-through limit orders, V2 [68:09]) is unstated.
4. **Maximum re-arms.** After a stop-out, the model re-arms (V2 [22:00]) — but no cap on attempts per pool/day is ever given (the host asks about "max tries" at V2 [19:26]; Marco answers with the daily risk figure instead).
5. **The V1↔V3 relationship.** V3 uses Marco's proprietary vocabulary verbatim but the connection (student? licensee? imitator?) is never stated — relevant to how independent its corroboration is (file 05, relationship note).
6. **Marco's exact futures timeframe pairs.** "1 minute, 5 minute [entries]... targeting 15 minute, 1 hour levels" (V2 [24:05]) vs the 5m "do-it-all" (V1 [42:40]) — which combination is default is a judgment call the docs left as a range.

---

**Next file:** `08-bot-blueprint-outline.md`.
