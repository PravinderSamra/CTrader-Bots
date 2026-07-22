# 05 — Cross-Video Synthesis

Comparison of the sources: where they agree, where they diverge, and an assessment (clearly labeled as **my analysis**, not sourced from the videos) of what carries the strategy's edge.

Video key: **V1** — Chart Fanatics ep. 1 with Marco Trades (Aug 2025, whiteboard + chart examples + live NQ trade). **V2** — Chart Fanatics ep. 2 with Marco ("Da Vinci model", Jul 2026). **V3** — Inter Equity Trading (Jan 2026, 16-minute NQ walkthrough). Added 2026-07: **PB** — the official first-party PDF playbook (`../04-official-playbook/marco-trades-liquidity-playbook.md`, "Marco Trade's Playbook" published via ChartFanatics); **IET** — twenty further Inter Equity Trading channel videos, 2026-01-31 → 2026-07-21 (`../01-transcripts/inter-equity-channel/`, documented in files 09–10; citations `(IET YYYY-MM-DD "title" [MM:SS])`).

**Relationship note (updated 2026-07-22, my analysis):** V1 and V2 are the same trader, so "agreement" between them is really internal consistency across a year. The original note here inferred the V3/Inter Equity creator was "a student of, or heavily derivative of, Marco's school". The 20 new IET transcripts now indicate something stronger: **the IET presenter appears to be Marco himself.** Evidence: his community addresses him by name on camera — "people will say, 'Oh, Marco, I understand your concepts, your system...'" (IET 2026-02-03 "Profitable 2026" [02:27]) and "everybody's sitting there like, 'Oh, Marco, well, now the highs are not taken...'" (IET 2026-04-07 "Why You Can't Trade" [06:06]–[06:26]); the official playbook is Marco's yet distributed content matches IET teaching one-for-one; vocabulary, entry model, session regime (NY futures + overnight forex limits), and even signature phrasings ("deem them to be false", "no man's land", "train the eyes") are identical; and the money-claims profile matches (IET claims $500K in Apex challenge passes, IET 2026-04-21 [11:24]; V1/V2 claim $500K+ payouts). Not conclusive — the channel brands itself "Inter Equity Trading" and never says "I am Marco Trades of Chart Fanatics" — but the working assumption should now be **one voice across all sources**: the Chart Fanatics interviews are guest appearances, IET is his own channel, and the playbook is his written summary. Consequence cuts both ways: corroboration is *even less independent* than previously assumed (nothing here is third-party validation), while authority is *higher* (files 09–10 document the strategy's author teaching his own system at length). Weight your confidence accordingly.

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

## 2.6 New-source reconciliation (playbook + IET channel, added 2026-07-22)

**Corroboration.** PB restates every core rule of files 01–04 in first-party writing (its own reconciliation table is in the playbook file); IET restates them across 6 months of fresh recordings (itemized table in file 09 §6). The model, entry trigger, structural stop, pool targets, trap-zone logic, fractality, and anti-pattern stance are corroborated *verbatim* — by what is now best understood as the same trader (relationship note above).

**Extensions** (new procedure, no conflict — full detail file 09 §7): the hard "no liquidity block, no entry" gate; the time apparatus (H4 6–10 a.m. candle model, "10:00 a.m. reversal", PDH/PDL day-frame, inside-day/bank-holiday no-trade calls, candle-closure entries only on perfect time confluence); the target-intact stacking rule; trail-to-new-LB; probability-graded lockout with a time exception; the 4-candle sniper entry anatomy (file 10 P7); "no man's land" range doctrine.

**Divergences among the new sources themselves:**

1. **Break-even policy (extends §2.1, and PB picks a side).** PB: "**No break-even stops unless partials have been taken**" (PB p.03) — V1's rule, in the authoritative document. But IET (same trader, contemporaneous) repeatedly goes BE *without* partialing when the first opposing pool is consumed and its RR doesn't justify a partial: "I'm going break even. I'm not paying myself. Why? 1-to-2.5... [at 1-to-6] I am paying myself" (IET 2026-07-14 [20:18]–[20:58]); "once we took out this internal high, I went risk-free" (IET 2026-06-30 [01:23]). *(My analysis: the practice is richer than the playbook's summary — the operative rule across V2/V3/IET is "risk-off when a liquidity level is consumed in your favor; partial only if the RR at that level makes sense"; PB's line reads as a simplification against fear-BE, which IET also warns about — "a lot of you will go break even out of fear... It has to make sense to break even your position", IET 2026-07-14 [16:56]–[17:16]. A bot should implement the IET form and treat PB's sentence as the guard against premature BE, not a ban.)*
2. **Refinement.** PB: "Don't refine entries too much; keep it simple" vs V2/IET's LTF drop-down when the stop is too wide. Resolved in the playbook file's closing note: over-refinement (hunting perfect ticks) is banned; the conditional LTF confirmation remains the RR-rescue tool (also IET 2026-06-30 [06:24]–[07:04]: no LB → seek LTF confirmation, same model).
3. **Lockout hardness.** V1/PB state the sequencing rule absolutely ("Buy below the low — never above", PB p.02); IET grades violations as "automatically lower probability" and licenses them only with session-time confluence (IET 2026-04-28 [01:02]–[01:22]) — which is how the ping-pong both-sides day exists at all (file 09 §4). *(My analysis: treat absolute lockout as the default; the time-qualified exception is an advanced overlay.)*
4. **Vocabulary.** IET equates the sweep's **imbalance** with the liquidity block ("this imbalance area, otherwise known as a liquidity block", IET 2026-03-03 [04:02]) — a repurposing of what files 01–06 catalogued purely as retail-POI vocabulary. Same geometry, new label use (glossary updated, file 06 §1).

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
