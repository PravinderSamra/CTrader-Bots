# 05 — Cross-Video Synthesis

Comparison of the three sources: where they agree, where they diverge, and an assessment (clearly labeled as **my analysis**, not sourced from the videos) of what carries the strategy's edge.

Video key: **V1** — Chart Fanatics ep. 1 with Marco Trades (Aug 2025, whiteboard + chart examples + live NQ trade). **V2** — Chart Fanatics ep. 2 with Marco ("Da Vinci model", Jul 2026). **V3** — Inter Equity Trading (Jan 2026, 16-minute NQ walkthrough).

**Relationship note (my analysis):** V1 and V2 are the same trader, so "agreement" between them is really internal consistency across a year; divergences between them are evolution or context differences. V3 uses Marco's exact proprietary vocabulary — "liquidity block", "engineered liquidity", "the market communicating", "deem them to be false", "we are not predicting", "trap" — and identical rules, strongly suggesting the V3 creator is a student of, or heavily derivative of, Marco's school. So the doc set effectively has **one independent source plus one corroborating retelling**, not three independent confirmations. Weight your confidence accordingly.

## 1. Agreement matrix

| Rule / concept | V1 | V2 | V3 | Notes |
|---|---|---|---|---|
| Liquidity = resting orders / stop losses | ✅ [3:59] | ✅ implied throughout | ✅ implied throughout | Only V1 defines it explicitly |
| Not every high/low has liquidity; respect-and-move-away confirms it | ✅ [3:22], [13:13] | ✅ [5:24], [26:14] | ✅ [1:16], [5:24] | Unanimous, core |
| Never predict pools; let market communicate | ✅ [13:56] | ✅ [5:24] | ✅ [14:06] | Unanimous |
| Liquidity block (sweep-wick = no liquidity; stop anchor / entry zone) | ✅ concept [28:44], [76:22], no name | ✅ named "liquidity block" [35:05], [51:49] | ✅ named, heaviest user [2:27], [12:15] | Same object; naming appears between V1 and V2 |
| Buy only below swept lows / sell only above swept highs | ✅ [10:12], [24:29] | ✅ [13:46] | ✅ [11:43] | Unanimous, core |
| Bias lockout (high taken → no buys until low taken) | ✅ [24:29] strict rule | ✅ implied by model sequence | ✅ [11:43] | V1 states it most explicitly |
| Enter immediately on sweep; no imbalance/over-refinement | ✅ [30:34], [46:33] | ✅ [14:11], [48:50] | ✅ [5:56], [9:59] | Unanimous, core |
| Stop behind left-hand low/LB, structural, always | ✅ [69:02] | ✅ [16:17], [43:11] | ✅ [14:41] | Unanimous, core |
| Target = opposing confirmed pool, never fixed R | ✅ [33:31] | ✅ [49:13], [59:17] | ✅ [5:56] | Unanimous, core |
| False/short-lived reactions inside trap zone | ✅ [9:33] | ✅ [37:58], [50:03] | ✅ [3:43], [7:35] | Unanimous |
| Fractal: HTF direction, LTF entry | ✅ [11:32], [31:14] | ✅ [23:01], [39:32] | ✅ [15:11] | Unanimous |
| Engineered liquidity as *named arming condition* | ⚠️ structure present [8:19], [21:32], term absent | ✅ core requirement [6:34], [28:11] | ✅ term used [9:16] | V2 formalizes what V1 drew |
| "Take out something from the left" as step 1 | ✅ in all examples | ✅ explicit [27:48] | ✅ [1:52] | Unanimous |
| Roll stop to BE when first opposing high taken | ⚠️ prefers trailing below higher low; BE only after partials [32:17], [32:55] | ✅ explicit BE rule [63:34] | ✅ BE or tuck below low [6:31] | Genuine (minor) divergence — see §2.1 |
| Partial sizing | 50–70% at first target when confident [47:05] | 20–25% max, prefer full hold [64:19] | Silent (shows intraday partial points only) | Divergence — see §2.2 |
| Session/time window, news filter | ✅ detailed NY-session regime [42:40], [49:30], [67:13] | ⚠️ mentions limit entries overnight instead [58:10], [68:09] | ❌ none | V1-only material — see §2.3 |
| Min RR 1:3 / skip when stop too big | ⚠️ skips small tick moves [94:38] | ✅ explicit [35:25], [36:18] | ⚠️ prefers LTF refinement to shrink SL [8:41] | Compatible variants |
| Scaling in below fresh local sweeps | ✅ live session [89:36]–[92:05] | ❌ not covered | ❌ not covered | V1-only |
| Re-arm after failed sweep (wait for new induce+trap) | ⚠️ implied by "rinse and repeat" | ✅ explicit [22:00] | ⚠️ implied | V2 clearest |
| Instruments universal (indices, gold, FX) | ✅ | ✅ | ✅ (NQ only shown) | |

## 2. Divergences in detail

### 2.1 Break-even trigger
V2/V3: mechanical — first opposing high taken → BE (V2 [63:34]; V3 [6:31]). V1: Marco trails below the new higher low instead and dislikes BE unless partials are banked (V1 [32:17]–[33:31]). *(My analysis: these produce nearly identical realized risk in practice — the higher low and BE are usually close — but a bot must pick one. V2 is the later, cleaner formulation and V3 corroborates it; treat V1's trailing variant as the discretionary flavor.)*

### 2.2 Partial size
V1: 50–70% at the LTF pool, rest to HTF target (V1 [47:05]). V2: hold ~all, partial max 20–25%, and he explicitly says he *changed* toward holding more over the prior 1–1.5 years (V2 [59:39]–[60:24]). *(My analysis: this is a documented evolution of the same trader, not a contradiction; the V2 rule supersedes V1 for "Marco's current system". The invariant across both: partials only ever occur at liquidity levels.)*

### 2.3 Timing filters
Only V1 supplies the session apparatus (NY window, 9:30 open marker, post-news 2–4 min wait, lunch avoidance, TF-close confluence). V2's CFD/limit-order material shows the model working with *no* session constraint. V3 is session-silent. *(My analysis: timing is an overlay belonging to Marco's futures day-trading deployment, not to the model itself. For a bot: session filters are a configurable regime, not core logic — but the news blackout is cheap insurance and V1 states it as an absolute rule.)*

### 2.4 Vocabulary drift
Same objects, different labels across videos: V1 "no liquidity above/below this high/low" = V2/V3 "liquidity block"; V1 "false move / trap move" = V2 "engineered liquidity + trap"; V1 "internal/external" = V2 "internal points / external highs". The glossary (file 06) normalizes these.

### 2.5 Entry mechanics
V1: market execution at the sweep tick (futures) (V1 [46:33]). V2: adds the resting-limit-at-the-level variant for HTF/CFD ([58:10], [68:09]). V3: "anywhere below the line is a valid buy" — a zone, not a tick ([9:59]). *(My analysis: three fill styles for the same trigger; economically equivalent apart from slippage/fill risk. A bot can implement any; the limit-at-level version is the most automatable.)*

## 3. Assessment: load-bearing edge vs cosmetics — **my analysis, not the sources**

**Load-bearing (the edge lives here):**
1. **The liquidity-existence filter** (respect-and-move-away vs liquidity block). This is the discriminator that separates the system from generic "sweep trading" — it dictates *which* sweep is tradeable, where the stop is safe, and which levels are targets. Every other rule consumes its output. It is also the rule all three sources repeat most often.
2. **The sequencing/lockout rule** (only buy below taken lows, and only after the opposite side armed the setup). This is the trade-permission gate that removes the losing trades retail takes inside the trap zone; both videos frame it as *the* fix for the most common mistake (V1 [24:29]; V2 [26:14]).
3. **Target = opposing confirmed pool.** Ensures each trade has a mechanical reason to exist and an asymmetric RR; without a pool overhead there is no trade even after a perfect sweep.
4. **Stop behind the no-liquidity extreme.** The structural justification ("no orders beyond it, so no reason for price to go there") is what makes the tight stop — and therefore the RR — defensible.
5. **Engineered liquidity as arming condition** (V2's step). It filters premature entries at pools the market hasn't yet "advertised", i.e., it is the difference between fading any low and fading a *prepared* low.

**Cosmetic / presentational (edge-neutral):**
- The "Da Vinci" branding, red/blue box color conventions, whiteboard layouts.
- Market execution vs limit at the level; exact partial percentages; BE-vs-trail flavor (§2.1–2.2) — these tune expectancy but don't create it.
- Instrument choice and the futures/CFD split (execution plumbing).
- Session window specifics (regime overlay; see §2.3) — with the caveat that Marco clearly believes NY-timing confluence materially improves *his* futures results.

**Fragile / unverified (my analysis):** the win-rate and payout claims (file 04 §7) are self-reported on a sponsor-funded show; V3's corroboration is not independent (§ relationship note); and the causal story ("orders resting there draw price") is a narrative — the rules could work for order-flow reasons or merely as a disciplined trend-pullback-extreme framework. None of the sources present backtest statistics. Any bot build should validate the edge empirically before trusting the discretionary claims.

---

**Next file:** `06-glossary.md`.
