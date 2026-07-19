# 07 — Open Questions Pending Visuals

The transcripts are audio-only captures of chart/whiteboard walkthroughs. The speakers constantly point ("here", "this level", "like this", "check this out") at things the captions cannot see. This file catalogues the moments where a visual reference would **materially change or clarify** understanding — i.e., where the docs in files 01–04 had to interpolate from context — so a future pass can resolve them against screenshots.

**Screenshot status:** stills are being collected from Google Drive into `../03-images/`. `Video3/` is complete (28 shots + `manifest.json`) and `Video2/` is complete (36 files); `Video1/` is pending. When resolving an item below, match its timestamp against the relevant video's manifest, update the affected doc file(s), and strike the item here.

Citations are `(Video N, [MM:SS])` into `../01-transcripts/`.

---

## A. Cross-cutting ambiguities (a visual would settle these once, for all files)

These are the highest-value unknowns because they are *parameters* every chart example depends on, and file 08's bot design needs numbers for them:

1. **What geometrically counts as "respect"?** — **RESOLVED** (see file 02 §B.1). Respect = wick terminating at/inside the prior level's zone without closing through; a touch is never required. Observed undershoot: ~60 pts (0.28%) against a line and ~200 pts inside a marked area on NQ (V3 `shot_016`, `shot_003`); ~4–6 pts (~0.1%) on gold against the left high (V2 `shot_023`). Working band: **0.1–0.3% of price**.
2. **How equal is "equal / relative equal"?** — **RESOLVED** (see file 02 §B.3). Observed spreads of the wick tips: ~30–40 pts (~0.15%) on NQ weekly (V3 `shot_004`/`shot_010`), ~5 pts (~0.1%) on gold (V2 `shot_018`). Working tolerance: **tips within ~0.1–0.3% of price**; V1's "relative equals" pending Section B.
3. **How far is "move away"?** — **STILL OPEN.** No shot shows a measured displacement threshold; the reconciled examples display displacements from ~10 pts (gold 1m) to ~100+ pts (gold 15m) after a respect, but nothing on-screen distinguishes minimum-valid displacement from chop. Only resolvable by backtest calibration (file 08).
4. **Level vs zone.** — **RESOLVED** (see file 02 §C step 9 note). Pattern across all reconciled shots: spread wick tips → **box spanning the tips** (V2 equal-highs box 5,095.2–5,109.8; V3 chain box); single/near-identical tips → **line snapped to the extreme tip** (V3 weekly line 23,364.25; V2 internal-lows lines). LBs always boxes spanning the sweep wick. Band height = tip spread, typically 0.15–0.3% of price.
5. **Color conventions conflict between videos.** — **PARTIALLY RESOLVED** (see file 02 §C step 9 legend-correction note). V2's live-chart legend is now fixed: **red boxes for every zone role** (target pool, engineered LQ, trap, buildup) + thin lines for levels + no blue at all — so role must be read from labels, not color. V3's legend (blue box = LB, red = trap/chain/buildup) was fixed by D2–D4. V1's legend remains pending Section B.
6. **Where exactly inside the swept zone do entries fill?** — **RESOLVED** (see file 03 §1.5 note). The valid band = [swept level → **far side** of the LB beneath], fractally at every scale: ~100–135 pts on NQ 1H/15m (D5/D8), ~10 pts on gold 1m (C7/C9: fills 5,057.17→5,051.19 bounded by the 5,047.3 wick-LB).
7. **Stop offset behind the LB.** — **PARTIALLY RESOLVED** (see file 03 §3.2 note). Gold CFD breathing room measured: ~$0.5–1 beyond a 1m wick (~0.01–0.02%), ~$3 beyond a 5m wick (~0.07%) (V2 `shot_008`, `shot_012`). No stated rule; V1's futures "tick or two" remains the only verbal quantity.

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

*Screenshots COLLECTED and RECONCILED (2026-07-19). All 36 shots carry the YouTube playbar timestamp (a few are fullscreen captures without a playbar; their moment is fixed by the iPhone-filename order). As with Video 3, `shot_NNN` numbering is scrambled — the original filenames (IMG_0951–0986 in `manifest.json`) give true chronological order. **Coverage note:** the captures stop at [50:51]; nothing after that point in the video (common-mistake overlay, NQ replay, USDJPY trade) was screenshotted, so C12–C15 stay open.*

| # | Timestamp | Moment | Resolution |
|---|---|---|---|
| C1 | [3:58]–[6:34] | Whiteboard: engineered-liquidity definition | **RESOLVED** — see file 03 §1.3 note. Engineered high drawn ~80–90% of the way to the target line, never touching; on the gold chart the respecting highs print *inside the lower half* of the 5,095.2–5,109.8 target box. `shot_029.jpg` [5:21], `shot_030.jpg` [6:35], `shot_035.jpg` [7:50] (whiteboard); `shot_023.jpg`/`shot_018.jpg`/`shot_011.jpg` (chart). |
| C2 | [9:36]–[11:19] | Full bullish Da Vinci diagram | **RESOLVED** — see file 03 §0 geometry note. Seller POI = red box just under the target line, drawn from the left internal high; engineered high prints into its right edge; pool = line under the middle lows with the left-hand low drawn deeper. `shot_017.jpg` [10:59]. |
| C3 | [13:20]–[16:42] | Entry/stop/target drawing | **RESOLVED** — see file 03 §3.1 note. "SL" is written below the **deeper left-hand low**, not the swept pool low; entry blue-marked at the stab, blue target dash above the highs — the left-hand-low reading is confirmed. `shot_016.jpg` [15:21], `shot_031.jpg` [20:03]. |
| C4 | [25:24]–[28:38] | Bearish (inverted) whiteboard | **RESOLVED** — see file 03 header note. Exact object-for-object mirror; "ENG LQ" labels the low respecting previous lows; buyer POI red lines from the left mid-lows. `shot_019.jpg` [27:36]. |
| C5 | [31:26]–[33:38] | Gold 15m: target pool vs engineered zone | **RESOLVED** — see file 03 §1.2 note. Target pool = left high ~5,110 + two circled respecting highs, boxed 5,095.2–5,109.8; engineered zone = the *later* post-sweep high respecting that box ("Eng. LQ" label). `shot_010.jpg` [31:52], `shot_023.jpg` [32:10], `shot_018.jpg` [33:36], `shot_011.jpg` [34:44]. |
| C6 | [34:04]–[35:25] | The RR-shot condition | **RESOLVED** — see file 03 §2.3 note. On-screen tool: entry 5,049.5, stop 5,013.6 (35.9 pts / 0.711% below, beyond the LB), target 5,110.9 → **RR 1.72** — under the 1:3 floor, so the trade is skipped for the 1m. `shot_028.jpg` [35:38] (`shot_024.jpg` [35:59] shows the trailed-runner counterfactual, RR 3.44). |
| C7 | [36:55]–[39:32] | Gold 1m: last level + wick-LB | **RESOLVED** — see file 03 §2.3 note + file 02 §E. Last level ~5,050–5,051; 09:19 stab-wick (low ~5,047.3, hand-underlined) = the LB; entry 5,051.19 at the 10:00 restab, stop 5,046.2–5,046.9; target hit 5,111.66 ~15:00 → the "1:12". `shot_001.jpg`, `shot_033.jpg` [37:49], `shot_008.jpg` [39:25], `shot_002.jpg`, `shot_026.jpg` [39:45], `shot_025.jpg` [39:53], `shot_036.jpg` [40:03]. |
| C8 | [40:26]–[41:35] | Zoomed 1m grammar | **RESOLVED** — see file 02 §E note. The zoom frame circles each low-respecting-low pair and the red-box respect before the stab; teal entry column starts on the 10:00 bar. Best labelling reference in the corpus. `shot_027.jpg` [41:23]. |
| C9 | [42:48]–[43:33] | Conservative-entry overlay | **RESOLVED** — see file 03 §2.2 note. Conservative fill = the pool level itself, 5,057.17 (vs extreme 5,051.19), same stop 5,046.19 → **RR 4.96** capped at 5,111.66; runner target 5,179.5 showed RR 11.14 live. `shot_007.jpg` [43:35], `shot_009.jpg` [43:42], `shot_005.jpg`. |
| C10 | [46:03]–[49:38] | Gold 15m second example, entry #1 | **RESOLVED** — see file 03 §7 row 7. Tapped-twice red box 4,031–4,043 (Nov '25 chart); buildup entry trigger = the marked low ~4,033–4,035; entry 4,032.37, stop 4,022.07 below the underlined **left-hand** low ~4,025; target line 4,109.51 → **RR 7.49** (the "1:7.5"). `shot_013.jpg` [47:14], `shot_004.jpg`, `shot_032.jpg` [47:44], `shot_034.jpg` [47:54], `shot_003.jpg`, `shot_015.jpg` [49:06], `shot_012.jpg` [49:27], `shot_006.jpg`. |
| C11 | [49:38]–[52:41] | Entries #2–3; engineered pool grabbed | **PARTIALLY RESOLVED** — see file 03 §4.2 note. The grabbed engineered pool is the middle of three stacked "Eng LQ" callouts (~4,062 / **~4,088** / ~4,103); the rally off entry #1 runs the ~4,088 high (drawn arrow) before the next sell-off. Captures end at [50:51], so entry #2/#3's own position tools and the entry-#3 LB were not screenshotted. `shot_022.jpg` [50:20], `shot_014.jpg` [50:32], `shot_020.jpg` [50:51]. |
| C12 | [54:11]–[54:57] | Common-mistake overlay | **OPEN** — no screenshot; the Video 2 captures stop at [50:51]. |
| C13 | [55:22]–[58:35] | NQ replay: non-Da-Vinci extreme entry; passive limit variant | **OPEN** — no screenshot (captures stop at [50:51]). |
| C14 | [60:47]–[63:11] | Replay outcome + LB entry #2 | **OPEN** — no screenshot (captures stop at [50:51]). |
| C15 | [64:40]–[69:17] | USDJPY live trade | **OPEN** — no screenshot (captures stop at [50:51]). The only real-money V2 trade remains reconstructed from words alone (file 01 §5b, file 03 §7 row 9). |

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
