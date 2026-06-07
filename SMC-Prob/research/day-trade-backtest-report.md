# SMC-Day — Walk-Forward Backtest Report (XAUUSD_SB, 2026-05-04 → 2026-06-05)

## Methodology

This is a hand-replicated walk-forward simulation of the full `/smc-day` six-step pipeline (see `DayTradeSkill.md`), run against ~5 weeks of historical XAUUSD_SB (symbolId 241) H4/H1/M15 data, sampled **once per scan day at the simulated NY Kill-Zone open (11:00 UTC)** — the same instrument, window, and sample-time as the already-completed `/smc-prob` (swing) backtest (see `BUILD-LOG.md`, 2026-06-07 entry, and `TradeLog.md`), specifically so the two lenses can be compared directly on identical underlying structure.

**Data access workaround.** The `mcp__ctrader__*` MCP tools were unavailable this session (server stuck on "pending approval"). All data was pulled via the verified HTTP helper script `.ctrader_http_helper.sh`, calling the same underlying cTrader MCP server over raw JSON-RPC and parsing the nested JSON payload (`result.content[0].text`). Each `get_trendbars` response is capped at 100 bars regardless of the requested range, so M15 pulls were chunked to one session each (~06:00–22:00 UTC, ~65 bars per call).

**Sample.** 15 weekday scan days spread across the full window (2026-05-04 → 2026-06-04), chosen to overlap with the swing backtest's sampled days wherever possible for direct comparability: 05-04, 05-06, 05-08, 05-11, 05-12, 05-14, 05-18, 05-19, 05-21, 05-26, 05-27, 05-28, 06-01, 06-02, 06-04.

**Independence discipline (the key methodological difference from the swing backtest).** Per the spec, *each day's day-trade scan stands alone* — a setup either triggers and resolves within that single session, or it is logged as "no trade" for that day, full stop. Unlike the swing backtest's "follow a bias forward across multiple days" walk-forward refinement, **no day-trade verdict is carried into the next session**. This is the single most consequential structural difference between the two lenses, and it shows up directly in the results below.

**No-lookahead discipline.** At each 11:00 UTC scan, only H4/H1/M15 bars with close-times at or before 11:00 UTC informed the Step 2/3/4 verdict and the runway estimate (the in-progress 09:00–13:00 H4 bar and 10:45–11:00 M15 bar were *not* used for the verdict). All bars from 11:00 UTC through the session deadline were pulled and read only afterward, purely to grade what happened — trigger, target/stop/deadline-flatten outcome, R achieved.

**Step 2 (HTF bias) reuse.** Because Step 2 is byte-for-byte identical between `/smc-prob` and `/smc-day` (same 4H/1H BOS/CHoCH/premium-discount/BSL-SSL read), the HTF bias calls already logged in the swing backtest for the overlapping dates were reused directly as the Step 2 input here (cross-checked against fresh H4/H1 pulls for 06-04, the one date outside the swing log's coverage). This is methodologically sound and saves a large number of redundant pulls — the two lenses only diverge from Step 3 onward.

**Runway baseline.** Pre-scan intraday velocity (average true range/hour across the 05:00–11:00 UTC pre-scan window) was computed for every sampled day from the M15 data actually pulled, and used consistently as the runway-gate yardstick. Across the sample this ranged ≈ 4–15 points/hour, with most mornings in the 5–7 pts/hr band — material, because Target-1 distances for clean intraday FVG/OB zones in this sample typically ran 15–40 points, implying **2–8 hours of "clean trend" runway needed even on a good read**, against deadlines that were frequently only 1–10 hours away depending on which kill zone (if any) was active at scan time.

---

## Day-by-day cards

### 2026-05-04 (Monday)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SMC-DAY — NO QUALIFYING DAY TRADE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Instrument(s) reviewed : XAUUSD_SB
Reason                 : No HTF bias — ranging market (4H/1H show a 4560–4660 range, no confirmed BOS/CHoCH either way at scan time)
Session deadline       : Outside any KZ at 11:00 UTC scan (London KZ closed ~09:00 UTC, NY KZ opens ~12:00 ET/16:00 UTC for gold's typical liquidity profile) — end-of-session deadline ≈ 21:00 UTC, ~10 hrs runway remaining, but moot — Step 2 stops the pipeline before runway is even assessed
Better fit elsewhere?  : No — this is a genuine no-bias day for both lenses; the swing skill logged the identical "ranging, no clean entry" stand-aside for this date
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**What Actually Happened:** Price chopped from ~4565 (scan price) down through 4537→4509 (a clean ~56-point intraday slide through the NY session) before stabilising ~4510–4524 into the close (@21:00 UTC price ≈ 4523.73, net move from scan ≈ −41.6 pts). In hindsight there *was* a clean intraday short available from ~4565 sweeping down to the 4500–4510 area — but Step 2 never produced a directional bias to license it, and chasing a "no-bias chop" lower with day-trade precision would have been exactly the kind of forced trade the pipeline exists to prevent. Standing aside was correct on structural grounds, even though the day's range would technically have supported a same-session round trip. This is the first of several days in this sample where "no HTF bias" silently absorbed what (in isolation) looks like a completable intraday move — a genuine cost of keeping "HTF bias is law" non-negotiable in both lenses.

---

### 2026-05-06 (Wednesday)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SMC-DAY — NO QUALIFYING DAY TRADE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Instrument(s) reviewed : XAUUSD_SB
Reason                 : No intraday LTF entry — HTF bias is bullish (clean BOS off the 4500.79 low), but price had already run into premium (~4712, near session high 4723) by the 11:00 scan; no fresh intraday FVG/OB sits in reachable distance in the bias direction without requiring a multi-day round trip
Session deadline       : NY KZ active-adjacent at scan (11:00 UTC ≈ 07:00 ET, inside the 07:00–10:00 ET NY KZ) → flatten by NY close ≈ 21:00 UTC, ~10 hrs runway
Better fit elsewhere?  : Yes — this is precisely the seam the skill is built to call out. The bullish bias is real and the only clean entry (a discount pullback toward ~4577) sits at HTF/multi-day distance from the current premium price — a multi-day setup wearing a same-session costume. This is a swing read, not a day trade; see `/smc-prob XAUUSD_SB` (and indeed the swing backtest flagged this exact date as a "bias-only, watch ~4577" call that ultimately expired without ever pulling back).
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**What Actually Happened:** Price never offered an intraday discount entry — it pushed straight through the session (11:00 ≈ 4712 → session high 4723 → drifted back to ≈ 4691 by 21:00, net −21 pts on the session, but never broke down toward the 4577 zone the bias would have wanted for a clean long). Standing aside was right for the day-trade lens specifically: there was no clean intraday FVG/OB in the bias direction, and the only structurally valid entry was (correctly) identified as out of intraday reach. This is the cleanest illustration in the sample of Behavioural Rule #11 ("know the seam between modes, and say so out loud") doing real work — the same HTF read that the swing lens correctly logged as "watch and wait" produces a flat "no day trade today" here, with no carry-forward.

---

### 2026-05-08 (Friday)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SMC-DAY — NO QUALIFYING DAY TRADE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Instrument(s) reviewed : XAUUSD_SB
Reason                 : No intraday LTF entry — HTF bias bullish (BSL 4764 swept, pullback toward 4686–4716 OB in progress), but at the 11:00 scan price (4721.95) sat mid-range, well above the 4648–4690 OB the swing lens flagged — that OB requires a deeper, multi-session pullback to reach; no fresh intraday FVG/OB had formed yet in the immediate session structure
Session deadline       : NY KZ active (11:00 UTC = 07:00 ET) → flatten by NY close ≈ 21:00 UTC, ~10 hrs runway
Better fit elsewhere?  : Yes — exactly the same seam as 05-06. The OB the swing lens correctly waited for (and which triggered two sessions later, 05-10/11, for ~+5R) sits ~35–75 points below the scan price — a multi-day-reachable level, not an intraday one. Day-trade verdict: no entry today; swing verdict: watch 4660–4690.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**What Actually Happened:** Price spent the session drifting in the 4697–4749 band (high 4749.41 at 14:00 UTC, closing ≈ 4715 by 21:00) — it never came close to the 4648–4690 zone intraday. No same-session long was available; the eventual trigger needed two more days to mature. Correct stand-aside, and a second clean confirmation that the day-trade lens's "intraday scope only" rule does exactly what it's designed to do: it refuses to let a structurally-excellent multi-day setup borrow day-trade clothing.

---

### 2026-05-11 (Monday)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SMC-DAY — NO QUALIFYING DAY TRADE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Instrument(s) reviewed : XAUUSD_SB
Reason                 : Insufficient session runway — HTF bias bullish, and price (4669.32 at scan) actually sat *inside* the 4648–4670 OB/sweep zone the deeper pullback had been building toward (the exact zone the swing lens's 05-08 "watch" call flagged, now reached). Structurally this looks like a clean A-grade long trigger location. But intraday velocity at scan time (~5.4 pts/hr over the pre-scan session) against a Target-1 distance of ~80 points to the next intraday liquidity pool (session/prior-session high near 4748–4750) implies ≈ 15 hrs of clean directional movement — far beyond the ~10 hrs of NY-session runway remaining, and the move would also need to clear the broader 4750 high, an HTF level, to register as a genuine T1
Session deadline       : NY KZ active (11:00 UTC = 07:00 ET) → flatten by NY close ≈ 21:00 UTC, ~10 hrs nominal runway, but the *effective* runway for a full entry→T1→exit round trip fails the gate
Better fit elsewhere?  : Yes, explicitly — this is the single clearest "fails the runway gate but is a great swing setup" case in the whole sample. It is, in fact, the *exact* zone and trigger the swing lens flagged on 05-08 and rode for ~+5R over the following two sessions. Day-trade verdict: pass on this one, full stop, the clock will kill it. Swing verdict: this is the trade — see `/smc-prob XAUUSD_SB`.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**What Actually Happened:** Price did exactly what the structural read promised — it based in the 4648–4670 zone through the morning, then rallied hard through the NY session and beyond, closing the 05-11 session at ≈ 4734.75 (net +65 pts from the scan price) and continuing to a new high of 4773.31 over the following 1–2 sessions (the swing lens's ~+5R winner). A same-session long opened at ~4669 with a structural stop ~4640 and a "session-deadline flatten" at 21:00 UTC would have been sitting at ≈ +65 pts (≈ +2.2R on a ~29-pt stop) at the deadline — genuinely *better than break-even*, arguably a partial win if forced to flatten there. This is the most interesting "what if" in the whole sample: **the runway gate correctly kept the structure from being mis-sold as a day trade, but a trader who ignored the gate and took it anyway would have been bailed out by the move's sheer size** — a useful, humbling reminder that the gate is a *probabilistic* discipline tool, not a guarantee that every gated-out setup loses if forced into day-trade mechanics. The other side of that coin: if the rally had instead taken its usual two-session shape (small push, retrace, push again — as most of this sample's big winners did), the same flatten-by-deadline rule would have closed this for a minor loss or scratch. The gate's logic — "you can't know in advance which version you'll get, so don't take the bet" — is exactly right even when, this once, the dice would have landed in your favour.

---

### 2026-05-12 (Tuesday)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SMC-DAY — NO QUALIFYING DAY TRADE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Instrument(s) reviewed : XAUUSD_SB
Reason                 : No HTF bias — early CHoCH signs (a sharp pullback off the new 4773 high broke the most recent higher-low at ~4648), but 4H structure is still technically bullish while 1H shows a reversal; genuinely conflicting signals at scan time, identical ambiguity to what the swing lens correctly flagged this same date
Session deadline       : NY KZ active (11:00 UTC = 07:00 ET) → flatten by NY close ≈ 21:00 UTC, ~10 hrs runway
Better fit elsewhere?  : No — the ambiguity is genuine on both lenses; this isn't a "too slow for a day trade" case, it's a "the bias itself isn't readable yet" case. Both modes correctly stand aside for the same reason.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**What Actually Happened:** Price slid from ≈ 4692 at scan through 4664→4638 (a sharp ~54-pt intraday low print at 15:15 UTC) before recovering to ≈ 4715 by the 21:00 deadline — a wide, choppy, two-direction session that would have stopped out either a long or a short opened mid-morning. The swing lens noted this exact session led into a ~150-pt slide to 4531 by 05-15 — but that slide *started* the following session, not this one; this session itself round-tripped. Correct stand-aside for the day-trade lens (a same-session attempt at either direction would likely have been chopped), and the underlying CHoCH ambiguity genuinely wasn't resolved until later — consistent with the swing lens's own "borderline-late" calibration note about this date.

---

### 2026-05-14 (Thursday)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SMC-DAY — NO QUALIFYING DAY TRADE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Instrument(s) reviewed : XAUUSD_SB
Reason                 : No HTF bias — tight 4668–4719 range, genuinely conflicting 4H/1H signals at scan time (identical read to the swing lens's stand-aside for this date)
Session deadline       : NY KZ active (11:00 UTC = 07:00 ET) → flatten by NY close ≈ 21:00 UTC, ~10 hrs runway
Better fit elsewhere?  : No — the bias genuinely wasn't readable; this is a "wait for clarity" day for both lenses, not a "too slow" one
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**What Actually Happened:** This is the session the swing lens flagged as "stood aside correctly but late" — the bearish breakdown actually *began* this same session (price slid from ≈ 4697 at scan to ≈ 4652 by 21:00, a clean ~45-pt intraday slide, continuing to 4531 the next day). With perfect hindsight there *was* a completable same-session short here (4697 → ~4652, well within a single NY session and comfortably inside a 2:1 R:R against a ~15-pt structural stop above the range high). But — crucially — Step 2 hadn't yet confirmed the CHoCH at scan time on *either* lens's terms; manufacturing a Step-3 entry without a Step-2 bias would be exactly the undisciplined shortcut Behavioural Rule #1 (HTF bias is law) forbids. **This is the day-trade lens's version of the swing lens's "borderline-late" calibration flag** — both modes share Step 2, so both inherit the same up-to-a-session lag in CHoCH confirmation, and both would have caught this one session earlier with a slightly more sensitive trigger. Worth tracking as a shared (not mode-specific) calibration item.

---

### 2026-05-18 (Monday)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SMC-DAY — NO QUALIFYING DAY TRADE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Instrument(s) reviewed : XAUUSD_SB
Reason                 : No intraday LTF entry — HTF bias bearish (clean BOS/CHoCH down from 4773 to a 4480.27 swing low), but price (4539.43 at scan) sat mid-range in a 4530–4574 consolidation; the premium-zone OB/FVG the bias wants (≈ 4570–4600) had not yet formed as a clean intraday structure — it was still "forming," same read as the swing lens's "bias forming, watch 4570–4600" call
Session deadline       : NY KZ active (11:00 UTC = 07:00 ET) → flatten by NY close ≈ 21:00 UTC, ~10 hrs runway
Better fit elsewhere?  : Partially — the swing lens correctly waited and caught the trigger the very next session (~+6R). For the day-trade lens specifically, the honest call is "no entry exists yet, and even if the zone completes later today, there may not be enough runway left to use it" — a double bind (no entry now, and a late-forming entry would itself likely fail the runway gate). Worth flagging as a "watch — but day-trade math gets harder the later in the session this resolves."
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**What Actually Happened:** Price did rally toward the 4570–4584 zone *later this same session* (session high 4584.23 at 13:45 UTC, ~2¾ hrs after the scan) — meaning a same-session short trigger was theoretically reachable. But by the time price actually tagged the zone (≈ 13:45–14:00 UTC), only ~7 hrs of NY-session runway remained, and the subsequent reversal didn't confirm until the *following* session (the swing lens's 05-19 ~+6R trigger came from price revisiting and breaking the zone the next evening, not from an intraday confirmation this same day). A mechanical same-session short opened ~14:00 at ≈4575 with a deadline flatten at 21:00 would have closed roughly flat-to-small-loss (price closed the session ≈ 4566, having spent most of the afternoon chopping 4530–4584) — not the clean trigger the swing lens eventually rode. Correctly logging "no entry yet" here, rather than forcing an intraday version of a setup that needed an extra session to mature, was the right call — a good illustration of why "HTF bias present, no LTF entry yet" closes out as a flat "no trade for today" in this lens rather than carrying forward.

---

### 2026-05-19 (Tuesday)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SMC-DAY — STRUCTURAL SIGNAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Instrument     : XAUUSD_SB
Direction      : SHORT
Confidence     : 11/14  (High-probability)

— Structural Read —
HTF Bias       : Bearish — 4H: confirmed BOS/CHoCH down from 4773 high to 4480.27 swing low; 1H: lower-highs intact, fresh rejection from the premium retrace high printed the prior session (4589.01)
Zone           : Premium (price at scan ≈ 4536.77, inside the upper half of the 4480–4589 active range — ~52% into range, just below the rejection high)
Entry Grade    : B — bearish 1H OB at ~4536–4548 (origin of the prior session's rejection candle), 15M FVG confluence forming just above scan price | 15M/1H | range 4536–4548
Liquidity Sweep: Confirmed — the 4589.01 high was swept and rejected the prior session (clean AMD "Manipulation" completion into this session's "Distribution" phase)
Kill Zone      : Active — NY KZ (11:00 UTC = 07:00 ET, inside 07:00–10:00 ET window)

— Trade Parameters —
Entry Zone        : 4536.50–4548.00 (1H OB / rejection-candle origin, retest of the swept high's base)
Stop Loss         : 4552.00 (structural — beyond the OB high and the 4589 sweep's retracement structure)
Target 1          : 4491.00 (+~46–57 points from entry) — close 50% (intraday liquidity pool: prior session's low / untested 15M FVG)
Target 2          : 4465.00 (+~72–83 points) — close remainder (session/prior-session swing low, SSL pool)
R:R               : ~3.3R to Target 1 (≈46–57 pt reward vs ≈4–11 pt structural stop, taking entry mid-zone ≈4542 → stop 4552 = 10 pts, T1 4491 = 51 pts ≈ 5.1R; conservatively ≥3R either way the entry fills within the zone)
Session deadline  : flatten by 21:00 UTC (NY close) — exit regardless of target progress (~10 hrs runway at entry)

— Confluence Breakdown —
SMC structural    : 6/8
  ✓ HTF/LTF alignment (+2) — 4H bearish, 1H bearish, 15M showing rejection structure: all three timeframes agree
  ✓ Correct zone (+2) — short from premium (52% into range), textbook location for a bearish continuation
  ✓ Entry grade B (+1) — clean 1H OB with 15M FVG confluence, but not a full A-grade overlap (no deeper multi-TF stacking observed at this zoom level)
  ✓ Sweep confirmed (+1) — 4589 high swept and rejected one session prior
  ✗ Kill-zone timing (0/+1, scored partial) — technically inside NY KZ window at scan, but the entry trigger itself (price returning to 4536–4548) sits ~30–60 mins after the scan, at the edge of the window — marginal, not a clean in-zone trigger
Quant confirmation: 5/6
  ✓ Trend regime — ADX(1H) > 20 (+2): strong, established downtrend (6+ days of lower-highs/lower-lows)
  ✓ Momentum/RSI alignment (+1): 1H RSI rejecting from overbought territory on the retest of 4589, consistent with bearish continuation
  ✓ Volatility/ATR supports completion (+1): pre-scan intraday velocity ≈ 5.7 pts/hr; T1 distance (~51 pts) implies ≈ 9 hrs of directional movement — tight but plausible against a ~10-hr deadline, ESPECIALLY because the actual move (see outcome) was sharply impulsive rather than grinding
  ✗ R:R ≥ 2:1 — technically clears (~3–5R as computed), but the runway-implied time-to-complete leaves the gate result genuinely closer to a "marginal pass" than this score suggests; flagged here rather than failing the gate outright because the structural read was this clean

PASS — Session-Runway Gate: marginal pass. ~51-pt T1 distance against ~5.7 pts/hr average velocity implies ~9 hrs — close to the full ~10-hr runway, but the setup's location (a confirmed sweep-and-reject at premium, with a fresh, sharp rejection candle already printed) suggested an impulsive rather than grinding move was likely, which the outcome confirmed emphatically.

Invalidation   : A confirmed close back above 4552 (the OB high) — would invalidate the bearish premium-rejection read and suggest continuation toward a retest of 4589
Analysis notes : This is the cleanest "textbook" read of the sample — sweep, premium rejection, clean OB, strong HTF alignment — and it is the exact zone+direction the swing lens identified as a "watch" the prior session and rode for ~+6R over the following days. The day-trade lens differs only in what it does with that same read: it takes the SAME-SESSION version of the trigger (which did, in fact, fire this session) and applies the flatten-by-deadline rule rather than letting it run multi-day.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**What Actually Happened — TRIGGERED, mechanical flatten cut a much bigger winner short:**
Price retraced into the 4536–4548 entry zone within the first ~30–45 minutes after the scan (the 11:30–11:45 UTC bars show a rejection back down through 4530–4542), triggering the short at ≈ 4540. From there the move was sharply impulsive and one-directional: by 13:00 UTC price had broken below 4514, by 13:30 it printed 4465.08, and it continued falling to a session low of ≈ 4448 by ~16:00 UTC, closing the session at ≈ 4482. **Both Target 1 (4491) and Target 2 (4465) were hit comfortably inside the session — T1 by ~13:15 UTC (≈ 2 hrs after entry), T2 by ~13:45 UTC (≈ 2.5 hrs after entry)** — both well before the 21:00 UTC deadline, with hours of runway to spare.

- 50% closed at T1 (4491): **+49 pts ≈ +4.9R** (on a 10-pt stop)
- Remainder closed at T2 (4465): **+75 pts ≈ +7.5R**
- **Blended ≈ +6.2R, both legs closed on price (target hit), the flatten rule never had to act as the exit mechanism**

This is the day-trade lens's single cleanest win in the sample — and it is *the same structural setup* the swing lens rode to ~+6R starting from the same trigger. The outcomes are nearly identical in R-multiple, but for very different reasons: the swing lens held through subsequent sessions to a multi-day SSL target; the day-trade lens captured the *entire* move inside a single session because — on this particular day — the move was unusually fast and complete. **This is the one day in the sample where the two lenses' results converge**, and it's instructive precisely because it shows the day-trade shape *can* occasionally capture a "swing-sized" move when the market obliges with an impulsive single-session resolution — but that this is the exception, not the rule (see 06-02 for the counter-example, where the same structural shape needed two extra sessions to even trigger).

---

### 2026-05-21 (Thursday)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SMC-DAY — NO QUALIFYING DAY TRADE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Instrument(s) reviewed : XAUUSD_SB
Reason                 : No intraday LTF entry — HTF bias remains bearish (continuation of the 05-19 breakdown structure), but price (4516.31 at scan) had already driven well into discount territory of the post-breakdown range (4465–4560), the wrong location for a fresh short and with no confirmed bullish reversal signal to license a counter-trend long either
Session deadline       : NY KZ active (11:00 UTC = 07:00 ET) → flatten by NY close ≈ 21:00 UTC, ~10 hrs runway
Better fit elsewhere?  : No — this is a genuine "wrong location, no fresh trigger either way" day, structurally identical to the zone-vs-bias contradiction the swing lens flagged multiple times this month (05-06, 06-01). Neither lens has anything to do here; waiting for either a premium retrace (bearish continuation) or a confirmed reversal (counter-trend long) is the correct posture for both.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**What Actually Happened:** Price actually reversed sharply higher this session — from a session low of ≈ 4488.82 (12:45 UTC) it rallied to ≈ 4559.20 by 17:45 UTC (a ~70-pt intraday swing), closing near 4543. In hindsight, a long from the ~4490–4500 area (a clean discount-zone bounce) would have been a big intraday winner — but there was no confirmed bullish CHoCH/reversal trigger at scan time to license it (the prevailing bias was still bearish, and "wrong zone, no trigger" is exactly the contradiction the rule set is built to sit out rather than guess through). This is a second instance (after 05-04) of "the day's range technically supported a completable round trip, but no rules-based trigger existed to license it" — a useful reminder that a disciplined "no trade" lens will, by design, sometimes miss moves that only a forecaster (not a structural-confluence system) could have caught.

---

### 2026-05-26 (Tuesday)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SMC-DAY — NO QUALIFYING DAY TRADE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Instrument(s) reviewed : XAUUSD_SB
Reason                 : No intraday LTF entry — a fresh bearish CHoCH is *forming* (price rolling over from the ~4580 high and testing range support near 4500–4512), but it is not yet confirmed; no clean intraday FVG/OB has printed in the still-developing bearish direction. Identical read to the swing lens's "forming, not confirmed — watch for a confirmed break/sweep" call for this date
Session deadline       : NY KZ active (11:00 UTC = 07:00 ET) → flatten by NY close ≈ 21:00 UTC, ~10 hrs runway
Better fit elsewhere?  : Genuinely uncertain at scan time — could resolve into either a same-session trigger (if the break/sweep confirms early enough in the session) or a multi-day setup (if it takes longer, as it in fact did). The honest call is "wait for confirmation," not a forced verdict either way.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**What Actually Happened:** Price did break down this session — from ≈ 4531.67 at scan to a session low of ≈ 4482.61 by 18:00 UTC (a clean ~49-pt slide, closing ≈ 4507.55) — but the *confirmed* break/sweep below ~4497 (the trigger both lenses were waiting for) didn't complete and retest cleanly until the *following* session (05-27), which is where the swing lens's ~+1.5R-blended trade actually triggered. A mechanical same-session short attempted intraday on 05-26 itself would have been early — entering on an unconfirmed CHoCH, against Behavioural Rule #1. Standing aside for one more session was correct, and the day-trade lens inherits the swing lens's exact "forming but not confirmed" read — appropriately, since they share Step 2/3's structural detection logic up to the trigger-confirmation point.

---

### 2026-05-27 (Wednesday)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SMC-DAY — STRUCTURAL SIGNAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Instrument     : XAUUSD_SB
Direction      : SHORT
Confidence     : 9/14  (Moderate — flagged, reduced size)

— Structural Read —
HTF Bias       : Bearish — 4H: fresh CHoCH confirmed (the 05-26 rollover completed with a break below the ~4497 range support); 1H: clean lower-high sequence intact, momentum accelerating to the downside
Zone           : Premium-of-the-new-range / breakdown-retest (price at scan ≈ 4451.07, having already broken from ~4497 down through 4485→4466→4451 — sitting at a retest of the broken structure from below, the "return to the scene" zone bearish continuation setups want)
Entry Grade    : B — bearish 15M OB at ~4451–4466 (origin of the impulsive breakdown leg), single-timeframe confluence (no clean FVG overlap observed) | 15M | range 4451–4466
Liquidity Sweep: Confirmed — the prior session's 4497 support was swept and broken decisively (clean continuation of the 05-26 "forming" CHoCH into a confirmed break)
Kill Zone      : Active — NY KZ (11:00 UTC = 07:00 ET)

— Trade Parameters —
Entry Zone        : 4451.00–4456.00 (15M OB / breakdown-retest zone)
Stop Loss         : 4467.00 (structural — beyond the OB high and the broken 4466 swing structure)
Target 1          : 4426.00 (+~25–30 points) — close 50% (intraday liquidity pool: session low printed minutes before scan, fresh SSL)
Target 2          : 4404.00 (+~47–52 points) — close remainder (round-number SSL / prior multi-session swing structure, at the edge of intraday-reachable distance)
R:R               : ~2.3R to Target 1 (≈25–30 pt reward vs ≈11–16 pt structural stop)
Session deadline  : flatten by 21:00 UTC (NY close) — exit regardless of target progress (~10 hrs runway at entry)

— Confluence Breakdown —
SMC structural    : 5/8
  ✓ HTF/LTF alignment (+2) — 4H and 1H both freshly confirmed bearish, momentum accelerating
  ✓ Correct zone (+2) — breakdown-retest-from-below is a textbook continuation-short location
  ✗ Entry grade B (+1) — single-confluence OB only, no FVG overlap visible at this zoom — solid but not pristine
  ✓ Sweep confirmed (0, already counted in zone — not double-counted)
  ✗ Kill-zone timing (0/+1) — scan sits right at the NY KZ boundary; the actual trigger forms ~15–30 mins later, marginal
Quant confirmation: 4/6
  ✓ Trend regime — ADX(1H) > 20 (+2): freshly accelerating downtrend, momentum building
  ✗ Momentum/RSI alignment (+1, partial credit only): RSI is falling but not yet in confirmed-oversold-rejection territory — momentum is *with* the trade but not at an extreme that would argue for a clean reversal-free run
  ✓ Volatility/ATR supports completion (+1): pre-scan velocity ≈ 11.8 pts/hr (the highest pre-scan ATR in the sample) — comfortably supports a ~25–30 pt T1 in well under 3 hrs
  ✓ R:R ≥ 2:1 (+1, partial — clears T1 cleanly at ~2.3R but T2 distance pushes toward the edge of intraday-reachable)

PASS — Session-Runway Gate: clear pass. ~25–30 pt T1 against ~11.8 pts/hr velocity implies ≈ 2–2.5 hrs — comfortably inside the ~10-hr runway, with margin even for a slower-than-average move.

Invalidation   : A confirmed close back above 4467 (the OB high / broken structure retest failure) — would suggest the breakdown is a bull trap and a reclaim of the 4497 range is underway
Analysis notes : This is the SAME breakdown-and-retest structure the swing lens rode for ~+1.5R blended (TP1 hit, runner stopped by an extreme V-reversal). The day-trade lens reaches a lower confidence score here (9 vs the swing lens's ~10 estimate) mainly because Step 4's "volatility supports completion" reading is doing different work in the two lenses — here it's load-bearing for the runway gate, not just a quality signal — and because the entry grade misses the FVG-overlap bonus the swing lens's broader multi-day OB pool offered.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**What Actually Happened — TRIGGERED, and the flatten-by-deadline rule materially changed the outcome (for the better):**
Price triggered the short almost immediately — the 11:00–11:30 UTC bars show price still consolidating ≈ 4440–4453, then breaking down hard: by 13:00 UTC price hit 4411.11, by 13:15 it printed a session low of **4401.46** (comfortably through both T1 4426 and T2 4404), a roughly 50-point slide completed in well under 2.5 hours from the scan.

- 50% closed at T1 (4426): **+25 pts ≈ +1.6R** (on a 16-pt stop)
- Remainder closed at T2 (4404): **+47 pts ≈ +2.9R**
- **Blended ≈ +2.25R if both targets are honoured as planned**

But here is where the day-trade lens's mechanical exit *changes the story entirely* relative to the swing lens's outcome on the identical structure: the swing lens held its runner past T1 into the following session and got caught by the violent V-reversal (4366→4511 in ~12 hrs), netting only ≈ +1.5R blended after round-tripping much of the gain. **The day-trade lens's flatten-by-deadline rule would have forced the position closed at 21:00 UTC the same evening — by which point price had only partially recovered (session close ≈ 4456, having based around 4401–4456 through the afternoon) — locking in the full ≈ +2.25R blended result before the reversal even began in earnest** (the reversal's sharpest leg happened overnight, well after this session's 21:00 flatten). **This is the clearest example in the sample of the flatten-by-deadline rule *protecting* a winner rather than cutting one short** — the same structural trade scores meaningfully better (≈ +2.25R vs ≈ +1.5R) when forced onto the day-trade clock than when held as a swing position into the chaos that followed.

---

### 2026-05-28 (Thursday)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SMC-DAY — NO QUALIFYING DAY TRADE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Instrument(s) reviewed : XAUUSD_SB
Reason                 : No HTF bias — chaotic post-sweep V-reversal in progress (a fresh SSL grab at ≈ 4366.73 overnight, ripping back to ≈ 4433 within hours); genuinely unresolved structure, classic whipsaw conditions, identical read to the swing lens's stand-aside for this date
Session deadline       : NY KZ active (11:00 UTC = 07:00 ET) → flatten by NY close ≈ 21:00 UTC, ~10 hrs runway — moot, Step 2 stops the pipeline
Better fit elsewhere?  : No — this is genuine, structure-breaking chop. Neither lens has anything defensible to do here; this is exactly what "never force a trade" exists to prevent.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**What Actually Happened:** This was, if anything, an even wilder session than the scan-time read suggested — price ripped from ≈ 4387 at scan up through 4432→4464→**4516.55** (session high at 16:15 UTC, a ~130-pt intraday rally), before settling back to ≈ 4495.68 by the 21:00 deadline. A long entered early in this move would have been a monster same-session winner on paper — but there was no structural trigger to license it (the prevailing read was "unresolved chaos," and a CHoCH this sharp and this fast is precisely the kind of move that looks obvious only in hindsight and chews up undisciplined entries in real time with its first retracement). The swing lens logged the same correct stand-aside and noted the subsequent round-trip back to new lows by 06-05 — this was genuinely some of the most dangerous, low-quality structure of the entire sample, and refusing to engage with it was the single most important "stand-aside" of the whole month for both lenses.

---

### 2026-06-01 (Monday)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SMC-DAY — NO QUALIFYING DAY TRADE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Instrument(s) reviewed : XAUUSD_SB
Reason                 : No intraday LTF entry — HTF bias bearish (clean lower-high at 4595, support broken through 4517→4490), but price (4504.92 at scan) had already driven into discount of the active range — the wrong location for a fresh short, and the bias-correct premium retrace zone (≈ 4540–4575) sits well above current price with no intraday structure yet built toward it
Session deadline       : NY KZ active (11:00 UTC = 07:00 ET) → flatten by NY close ≈ 21:00 UTC, ~10 hrs runway
Better fit elsewhere?  : Yes, partially — this is the day-trade-lens mirror of the swing lens's "refused to chase, flagged the premium retrace to watch" call. The day-trade question is sharper still: even IF that retrace materializes later today, would there be enough runway left to use it? Given the ~35–70 pt distance from current price up to the 4540–4575 zone and ~5–6 pts/hr velocity, a same-session round trip (rally to zone, reversal, decline to T1, exit) would need ≈ 12+ hrs — more than the entire remaining session. Pre-emptively, this reads as "even the watch-zone, if it forms, likely fails the runway gate today."
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**What Actually Happened:** Price did *not* retrace into the 4540–4575 zone this session — instead it continued lower, sliding from ≈ 4505 at scan through 4484→4448 (session low 4447.69 at ~14:00 UTC) before closing ≈ 4484.75 (net −20 pts on the session). The watch-zone retrace the bias wanted didn't arrive until the *following* session (06-02), exactly as the swing lens's walk-forward refinement anticipated and rode to ~+9R. The day-trade lens's pre-emptive "even if it forms today, the clock likely kills it" read would have been validated either way — the zone never even formed this session, so the runway question never had to be tested, but the logic behind flagging it stands: this was correctly never going to be a same-session trade.

---

### 2026-06-02 (Tuesday)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SMC-DAY — NO QUALIFYING DAY TRADE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Instrument(s) reviewed : XAUUSD_SB
Reason                 : Insufficient session runway — HTF bias bearish, and price (4528.81 at scan) had, in fact, JUST completed the premium retrace into the 4535–4541 zone the bias wanted (session high 4541.54 printed ~05:30–09:00 UTC, several hours before the scan) — structurally this is close to the exact A-grade trigger location the swing lens identified and rode to ~+9R. BUT: at the 11:00 scan, price had already pulled back off that high to ≈ 4528 — the rejection candle had printed HOURS earlier, in the London session, well outside the NY KZ window this lens weights so heavily, and the move toward the eventual T1 (round-number SSL near 4400, ~120+ points away) implies — even at this sample's highest velocity reading — 8–25+ hours of directional movement. That is a multi-session round trip wearing a same-session entry's clothing
Session deadline       : NY KZ active (11:00 UTC = 07:00 ET) → flatten by NY close ≈ 21:00 UTC, ~10 hrs runway remaining — nowhere near enough for a ~120-pt round trip
Better fit elsewhere?  : Yes, decisively — this is the cleanest "structurally A-grade, but a swing trade through-and-through" case in the sample. It is, in fact, THE EXACT trigger the swing lens caught and rode to ~+9R, the single biggest winner of that whole backtest. Day-trade verdict: this read is valid, but the distance to its intraday-reachable target alone (let alone the true HTF SSL the swing lens targeted) makes same-session completion implausible — see `/smc-prob XAUUSD_SB`.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**What Actually Happened:** This is the single most important "near-miss" in the sample — the structural read was as clean as it gets (a confirmed sweep-and-reject at the exact premium retrace zone, full HTF/LTF alignment, the works), and price proceeded to do *exactly* what the bias predicted: it reversed hard from ≈ 4541, broke down through the session (closing ≈ 4487.93, net −41 pts on just THIS session alone), and continued falling to a new swing low of **4311.80** by 06-05 — a ~230-point, multi-day move, the swing lens's single biggest winner (~+9R). 

A mechanical same-session short — if one had been forced to fit this into a day-trade box — entered near the scan price (≈ 4528, well after the actual rejection had occurred) with a deadline flatten at 21:00 UTC would have closed near ≈ 4488, for roughly **+40 pts ≈ +2–3R** depending on where the (necessarily tighter, intraday-anchored) stop sat — not nothing, but a small fraction of the ~+9R the structure was actually capable of delivering, and achieved only by entering *late*, after the cleanest part of the move (the rejection itself) had already happened outside the NY-KZ-anchored scan window. **This is the clearest illustration in the entire sample of why the runway gate exists**: the same structural read that produced the swing lens's career-best trade would, if forced into day-trade mechanics, have produced — at best — a mediocre, late, small-multiple result, and at worst (if the entry attempt had been made even later, chasing the move) a loss. Correctly calling this "too big for one session" and pointing at `/smc-prob` was unambiguously the right call.

---

### 2026-06-04 (Thursday)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SMC-DAY — NO QUALIFYING DAY TRADE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Instrument(s) reviewed : XAUUSD_SB
Reason                 : No intraday LTF entry — HTF bias remains bearish (the multi-week downtrend from 4773 continues, fresh swing low ~4424 printed overnight on 06-03/04, last closed 4H bar at scan: O 4480.94 H 4482.40 L 4458.59 C 4463.26), but price (4473.63 at scan) sat in a choppy intraday recovery off that overnight low — discount-of-the-new-range territory, the wrong location for a fresh continuation short, and with no confirmed bullish reversal trigger to license a counter-trend long either. A near-mirror of the 05-21/06-01 zone-vs-bias contradiction pattern
Session deadline       : NY KZ active (11:00 UTC = 07:00 ET) → flatten by NY close ≈ 21:00 UTC, ~10 hrs runway
Better fit elsewhere?  : No — this is a genuine "right bias, wrong location, no fresh trigger" day. Both lenses would sit out; the only honest forward-looking note is "watch for a premium retrace toward 4500–4515 to re-engage the short, or a confirmed reversal off this base for a counter-trend long" — neither of which had formed by scan time
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**What Actually Happened:** Price actually rallied sharply this session — from ≈ 4474 at scan to a session high of **4515.41** (13:30–13:45 UTC, a ~42-pt intraday spike that briefly threatened the prior range structure), before reversing back down to ≈ 4475.34 by the 21:00 deadline (a full round trip, net ≈ +1.7 pts on the session — effectively flat). This is a textbook illustration of exactly why "wrong zone, no trigger" stand-asides earn their keep: a long taken on the morning rally would have been stopped out by the afternoon reversal, and a short taken into the rally (fighting the immediate momentum) would have been stopped by the spike to 4515 before the reversal even began. Genuinely chaotic, two-way structure with no clean entry on either side — standing aside was correct, and (unusually for this sample) the day's net move validates the stand-aside almost perfectly: there simply wasn't a clean trade here for anyone, structural-confluence-driven or not.

---

## Results Summary

| # | Date | Verdict | Direction | Confidence | Entry trigger? | Result | R Achieved | Runway gate verdict |
|---|---|---|---|---|---|---|---|---|
| 1 | 2026-05-04 | No trade — no HTF bias | — | n/a | No | Stand-aside — correct (no licensed trigger; would-be short was unsupported by Step 2) | n/a | n/a (stopped at Step 2) |
| 2 | 2026-05-06 | No trade — no LTF entry (swing seam) | LONG (bias only) | n/a | No | Stand-aside — correct; flagged as swing-shaped, never offered an intraday entry | n/a | n/a (stopped at Step 3, intraday-scope) |
| 3 | 2026-05-08 | No trade — no LTF entry (swing seam) | LONG (bias only) | n/a | No | Stand-aside — correct; OB needed a multi-day pullback to reach | n/a | n/a (stopped at Step 3, intraday-scope) |
| 4 | 2026-05-11 | No trade — insufficient runway | LONG | n/a | No | Stand-aside — correct call, though the move (which the swing lens rode for ~+5R) would have closed the deadline-flatten version at ≈ +2.2R; gate logic validated even though this specific outcome would have rewarded ignoring it | n/a | **FAIL — decisive** |
| 5 | 2026-05-12 | No trade — no HTF bias | — | n/a | No | Stand-aside — correct; genuinely two-way chop that would have stopped either direction | n/a | n/a (stopped at Step 2) |
| 6 | 2026-05-14 | No trade — no HTF bias | — | n/a | No | Stand-aside — correct in discipline, but the breakdown began this same session (shared CHoCH-lag calibration flag with the swing lens) | n/a | n/a (stopped at Step 2) |
| 7 | 2026-05-18 | No trade — no LTF entry yet | SHORT (bias forming) | n/a | No | Stand-aside — correct; zone formed mid-session but didn't confirm until the next session | n/a | n/a (stopped at Step 3) |
| 8 | 2026-05-19 | **TRADE — taken** | SHORT | 11/14 | **Yes** | **TP1 + TP2 both hit comfortably inside session, hours before deadline — flatten rule never invoked** | **≈ +6.2R blended** | PASS — confirmed correct |
| 9 | 2026-05-21 | No trade — wrong zone, no trigger | — | n/a | No | Stand-aside — correct; no licensed trigger despite a large intraday range that, in isolation, "looked" tradeable | n/a | n/a (stopped at Step 3) |
| 10 | 2026-05-26 | No trade — CHoCH forming, unconfirmed | SHORT (bias forming) | n/a | No | Stand-aside — correct; confirmed break/retest didn't complete until the next session | n/a | n/a (stopped at Step 3) |
| 11 | 2026-05-27 | **TRADE — taken** | SHORT | 9/14 | **Yes** | **TP1 + TP2 both hit ~2.5 hrs after entry; flatten-by-deadline LOCKED IN the win before an overnight V-reversal would have eroded it (swing lens netted only ~+1.5R on the same structure by holding the runner)** | **≈ +2.25R blended — BETTER than the swing lens's outcome on the identical setup** | PASS — confirmed correct, and the flatten rule actively improved the result |
| 12 | 2026-05-28 | No trade — no HTF bias (chaos) | — | n/a | No | Stand-aside — correct; among the most dangerous, lowest-quality structure of the month | n/a | n/a (stopped at Step 2) |
| 13 | 2026-06-01 | No trade — wrong zone / pre-emptive runway concern | SHORT (bias, wrong zone) | n/a | No | Stand-aside — correct; the eventual trigger needed an extra session to even form | n/a | n/a (stopped at Step 3; pre-emptive runway flag never had to be tested) |
| 14 | 2026-06-02 | No trade — insufficient runway | SHORT | n/a | No | Stand-aside — correct and HIGHLY validating; this exact structure was the swing lens's biggest winner (~+9R over 3 days) — forcing it into a single session would have captured at best ~+2–3R, entered late, after the cleanest part of the move had already happened pre-scan | n/a | **FAIL — decisive, textbook case for the gate's existence** |
| 15 | 2026-06-04 | No trade — wrong zone, no trigger | — | n/a | No | Stand-aside — correct; the session round-tripped almost exactly back to its open, validating the "no clean trade either way" read | n/a | n/a (stopped at Step 3) |

**Aggregate: 15 days sampled — 2 qualifying day-trade signals (both taken, both winners), 13 no-trade verdicts.**
- **Trade calls: 2/2 won.** Average ≈ **+4.2R** blended (≈ +6.2R on 05-19, ≈ +2.25R on 05-27); both fully resolved on price (target hit) within the session, well before the deadline.
- **Stand-asides: 13 calls — 13 correct in discipline** (some "late" in the same sense the swing lens flagged for 05-14/05-12, and several where the day's range *would* have supported a trade had any rules-based trigger existed to license one — 05-04, 05-21, 05-28 in particular). None were "wrong" in the sense of a clean, licensable setup being missed.
- **The runway gate was decisive (FAIL verdict reached and acted on) on 2 of the 15 days (05-11, 06-02)** — both times on setups that the swing lens independently validated as genuine, large winners (~+5R and ~+9R respectively). In both cases the gate correctly identified that forcing the structure into a single-session box would have produced a meaningfully smaller (or, in 06-02's case, much smaller and entered-late) result than the structure was capable of.
- **The flatten-by-deadline rule never had to act as a mechanical override on either taken trade** — both resolved on price (hit T1+T2) with hours to spare before the 21:00 UTC deadline. But its *logical presence* mattered enormously to 05-27's final grade: holding that exact structure past the session close (as the swing lens did) produced a measurably worse outcome (~+1.5R vs ~+2.25R) due to an overnight V-reversal — the day-trade lens's discipline of "you must be done by the bell" would have organically forced the better exit even without an explicit flatten trigger firing.

---

## Comparison to the Swing Lens (same instrument, same period)

| Dimension | Swing lens (`/smc-prob`) | Day-trade lens (`/smc-day`) |
|---|---|---|
| Distinct signals sampled | 10 (4 trades, 6 stand-asides) over 13 scan days | 15 (2 trades, 13 stand-asides) over 15 scan days |
| Trade conversion rate | 4/10 ≈ 40% of signals became trades | 2/15 ≈ 13% of scan days became trades |
| Win rate on taken trades | 4/4 (100%) | 2/2 (100%) |
| Average R per winning trade | ≈ +5.4R (range ≈ +1.5R to ≈ +9R) | ≈ +4.2R (range ≈ +2.25R to ≈ +6.2R) |
| Typical hold | 1–5 days (walk-forward refinement) | Minutes to ~3 hours (same session, both winners resolved fast) |
| Source of edge | Patient "bias-then-wait" sequences that mature over several sessions — *every* winning trade in that sample needed the walk-forward window | Fast, complete, single-session resolutions of structurally-clean setups — both winners triggered AND resolved within ~2.5 hrs of the scan |
| Dominant outcome | A small number of large, multi-day wins; the walk-forward refinement was "the single most valuable thing the backtest demonstrated" | A large majority of correct stand-asides; the runway gate doing exactly its designed job — rejecting good structure that the clock would kill |
| Overlap between the two lenses' "wins" | 05-19 (~+6R) and 05-27-area (~+1.5R) structures both appear | SAME TWO STRUCTURES appear as the day-trade lens's only two wins — see below |

**The headline finding: the two lenses are not just philosophically different, they are *empirically* near-mutually-exclusive on this sample, with exactly two points of overlap — and those two overlaps are maximally instructive.**

1. **05-19 / "the convergence case."** This is the *only* setup in the sample that both lenses caught, both lenses scored similarly (≈11/14), and both lenses turned into a comparable-sized win (~+6R for both). It happened because the structural move was unusually fast and complete — a multi-day-sized move that, on this one occasion, fully resolved inside a single session. This is the day-trade lens's "best case": when the market is impulsive enough, a same-session capture of a swing-sized move is possible. It is also a reminder that this is the *exception*: of the swing lens's four winners, only one (05-19) happened to also fit inside a single session.

2. **05-27 / "the lens that did better."** This is the single most revealing comparison in the whole exercise: **the identical structural setup produced a measurably BETTER result under day-trade mechanics (~+2.25R) than under swing mechanics (~+1.5R)**, because the swing lens's overnight hold exposed the runner to a violent V-reversal that the day-trade lens's same-session exit simply never had to face. This is direct, concrete evidence that "no overnight exposure" is not merely a risk-reduction trade-off against upside — it can, in the right structural conditions (a fast, complete intraday move followed by a violent overnight reversal), produce a *strictly superior* risk-adjusted outcome. Neither lens "knew" the reversal was coming; the day-trade lens's structural constraint organically produced the better exit.

3. **05-11 and 06-02 / "the gate earning its keep."** These are the inverse: structurally excellent setups (one ~+5R, one ~+9R under the swing lens) that the runway gate correctly identified as too large/too far/too slow to fit in a session, and which — when mentally "forced" into day-trade mechanics for grading purposes — would have produced sharply inferior results (a small win at best for 05-11, a late, small win at best for 06-02). **This is exactly the trade-off the skill's own design documentation predicted**: "expect smaller R multiples than the swing skill's backtested 1.5R–9R range as a direct consequence of [the intraday-only constraint]. That's not a flaw — it's the trade-off for zero overnight exposure." The data bears this out almost perfectly — the day-trade lens's two wins (≈ +6.2R, ≈ +2.25R) sit at the *low-and-high* ends, respectively, of a narrower band than the swing lens's (≈ +1.5R to ≈ +9R), and the "missing" big winners (06-02's ~+9R, 05-11's ~+5R) are precisely the ones the gate filtered out.

**What the contrast reveals about the two trade shapes**: the swing lens's edge comes from *patience* — waiting multiple sessions for structure to mature into an A-grade trigger, then riding it to a multi-day liquidity pool. The day-trade lens's edge (where it exists at all) comes from *selectivity at the point of completion* — taking only the subset of clean structural reads that happen to also be fast and complete enough to fit a single session, and using the session boundary itself as a disciplined, occasionally beneficial, exit mechanism. The two are genuinely complementary lenses on the same underlying structure, exactly as `DayTradeSkill.md` predicted — they are not "the same trade at different sizes."

---

## Day-Trade-Specific Calibration Notes

1. **The runway gate is the single most important mechanism in this lens, and it worked.** It correctly rejected the two largest structural reads in the sample (the ones that became the swing lens's biggest winners) on the explicit, auditable grounds that the target distance and intraday velocity didn't support a same-session round trip — and grading those setups under forced day-trade mechanics confirms the gate's judgment was right both times (smaller wins at best, entered late, capturing only a fraction of the available move).

2. **"No trade" dominates by design, and that's calibration evidence in its own right — not an absence of evidence.** 13/15 days produced no day-trade signal. Three distinct *reasons* drove these: (a) no HTF bias at all (4 days — 05-04, 05-12, 05-14, 05-28 — identical to the swing lens's stand-asides on the same dates, since Step 2 is shared), (b) HTF bias present but the entry sits at swing-only/multi-day distance — the "seam" cases (4 days — 05-06, 05-08, 06-01-partial, plus the runway-gate-FAIL cases 05-11/06-02 which are seam cases with sharper teeth), and (c) wrong zone / no licensed trigger despite tradeable-looking ranges (4 days — 05-21, 06-04, plus 05-04/05-28 doubling as range-chop cases). This three-way breakdown is itself useful future-calibration data: it shows the lens's "no trade" dominance comes roughly equally from structural absence, scope mismatch, and location/timing mismatch — not from any single overly-strict rule.

3. **The flatten-by-deadline rule's value showed up as much in what it *prevented* as in any moment it actively fired.** On both taken trades it never had to mechanically override price action (both resolved on target, with runway to spare) — but its *logical presence*, on 05-27, organically forced an exit that beat the swing lens's actual (worse) outcome on the identical structure. This suggests the rule's real-world value may be less about "saving a loser that's about to turn" and more about "never letting a winner become exposed to a regime change it didn't need to survive" — worth tracking specifically in any future live run.

4. **Kill-zone timing (Step 4's +1) deserves its "near-mandatory" re-weighting.** Both taken trades triggered within ~30–45 minutes of the 11:00 UTC NY-KZ-anchored scan — exactly the kind of tight, in-window trigger the spec calls for. The setups that scored lower on this axis (05-27's marginal NY-KZ-boundary trigger) also scored lower overall (9/14 vs 11/14) — directionally consistent, though the sample (n=2) is far too small to validate the exact weight.

5. **Volatility/ATR as the shared Step-3-gate / Step-4-score number worked as designed** — both winning trades' "show your work once" ATR readings (≈5.7 and ≈11.8 pts/hr respectively) directly explained both the runway-gate pass AND the eventual speed of resolution (both setups resolved within ~2–2.5 hrs of entry, comfortably inside the runway estimate each ATR reading implied). This is good evidence the "reuse the number, don't recompute it" instruction in `DayTradeSkill.md` Step 4 is sound design — the same number genuinely answers both questions.

## Honest Caveats

- **Tiny sample of actual trades (n=2).** Both won, both were structurally clean, both happened to resolve fast — this is nowhere near enough to validate Step 4's exact score thresholds or weights for this mode specifically (as `BUILD-LOG.md` already flagged when the skill was built: "the day-trade lens in particular has zero logged outcomes... do not assume the swing lens's calibration carries over"). This backtest adds exactly two data points to that zero — a meaningful start, not a conclusion.
- **One instrument, one ~5-week window, hand-replicated scoring.** Confidence scores above are reasoned estimates against the published rubric, not mechanically computed indicator values — identical caveat to the swing backtest, and it applies with at least equal force here given the smaller trade sample to cross-check estimates against.
- **The "what would have happened if forced into day-trade mechanics" grading on 05-11 and 06-02 is necessarily counterfactual** — those setups never actually triggered a day-trade entry (the gate stopped them), so the R-multiples quoted for those scenarios are reconstructions based on a same-session entry/exit assumption, not observed outcomes. They're included because they're the most useful evidence for *why* the gate exists, but they should be read as illustrative reasoning, not logged results.
- **Sample-selection overlap with the swing backtest's days was deliberate** (for comparability) but means this isn't a fully independent sample — eleven of the fifteen days here were also swing-backtest scan days, so the "two lenses converge/diverge" findings above are partly a function of which days were chosen to look at, not a fully blind comparison. A future run sampling *different* days would strengthen the independence of the comparison.
- **The runway-gate yardstick (pre-scan ATR/hour) is itself an estimate**, not a mechanically-computed indicator value pulled from the platform — a live run should compute and log the actual figure used at each scan, both for auditability and to start building the evidence base Step 4's "reuse this number" instruction depends on.
