# UK100 First Live Session Review — 2026-07-13 (post-mortem + fix plan)

**Status:** ready for implementation · **Written:** 2026-07-13 evening by the review model (Fable) · **Builder:** Sonnet
**Scope:** review of the first real `/uk100-session` run (14:45 BST brief, record `public/data/uk100/sessions/2026-07-13/13-46.json`), the skill doc, the shared engine, and the dashboard data feeding it — scored against actual market data through the 16:30 BST cash close.
**Prerequisite reading:** `UK100-V2-PLAN.md` (phases B–F remain valid; §6 below says how this doc's fixes interleave with them). The v1/v2 execution rules apply unchanged (verify → commit → push → fast-forward `main` per fix; never force-push main; never hand-edit `index.json`/`outcomes.json`).

Everything in §1–§4 was observed directly (live trendbars, engine output, deployed record, source code) — do not re-litigate the diagnoses, but re-verify each fix against the cited evidence.

---

## 1. HOW THE CALL ACTUALLY PLAYED OUT (ground truth)

Brief published 13:46 UTC (14:46 BST): **LONG 10484–10491 (live at 10490.6), stop 10477, T1 10495.9, T2 10506.9, T3 10526.3**, invalidation "M5 close back below 10482/10478.3", primary 62% bullish into the 10495–10507 zone, secondary 33% "rejection from that same zone back toward the M5 SSL pools (10466.9/10455.3)".

M5 bars after publication (UTC, display prices):

| Bar | High | Low | Close | Note |
|---|---|---|---|---|
| 13:45 | 10496.9 | 10490.7 | 10490.9 | **T1 (10495.9) hit in the publication bar** |
| 13:50 | 10506.4 | 10487.3 | 10506.3 | tags the FVG zone |
| 13:55 | **10513.5** | 10505.9 | 10508.6 | **T2 (10506.9) hit +10 min**; session high 10513.5, ~6.6pt above the flagged FVG top |
| 14:00–14:10 | — | — | ~10492 | rejection begins from inside the grade-A bear FVG (10497.8–10506.9) |
| 14:15 | 10498.3 | **10460.1** | 10479.9 | **53-pt slam in one bar; STOP (10477) hit**; low lands between the M5 SSL pools 10466.9/10455.3, vol 856 = session peak |
| 14:20→15:30 | ≤10498 | ≥10467 | 10484.6 | chop into the 16:30 BST cash close |

**Verdict:** chronologically T1 → T2 → stop. Under first-touch scoring (the gold resolver convention) this records as a **win**; a trader following the brief's own prose ("book into strength into the FVG, do not fight it, don't hold late-session") banked +0.4R and +1.2R partials; a mechanical hold-for-T3 gave the runner back at the stop ~30 min later. T3 was never realistic (see §3.5).

**The striking part:** *both* scenarios materialised in sequence exactly as written — bullish continuation into 10495–10507, then rejection from that zone to the M5 SSL pools. The structural read (reclaim into an overhead grade-A bearish FVG as the day's ceiling, bearish SMT as the caution) was genuinely good. The failures below are calibration, labeling, and timing-policy failures — not read failures.

---

## 2. WHAT WORKED (keep, don't touch)

1. **One-command fetch** (`ctrader_http_fetch.py --instrument uk100`): flawless — all trendbar windows including the dedicated `orb_h1`/`orb_m5`, candles <7 min old, live balance/positions, zero session-loss errors (Phase A1 fix held across three separate runs today).
2. **Engine freshness gates** passed silently; no stale-data risk.
3. **Deterministic meta rules** were followed: `bias`/`biasScore`/`smtDivergence`/`priceZone` copied verbatim from engine/snapshot; `confidence` mapped correctly (MEDIUM→5); `session`/`tradeIdea.status` rules applied correctly.
4. **Static calendar (Phase A2, shipped hours earlier) already paid off live:** `nextHighImpactEvent` = UK GDP 16 Jul 07:00 BST populated from the merged static source, and the build-up-caution line cited it. First production proof of the new merge path.
5. **Save pipeline:** clean save, index update, direct push to main, Pages deploy verified live ~2 min later. Record fields all present and well-formed.
6. **Skill degradation paths:** TradingView MCP was down → skill correctly used the engine's `pattern_check` as primary and said so; no stall, no fabrication.
7. **Sticky ORB in the engine:** `orb_broken_direction: DOWN` was correct at 14:41 BST even though price had re-entered the range (first-close-outside semantics).

---

## 3. WHAT WAS WRONG OR MISLEADING (each with root cause)

### 3.1 ⚠️ ENGINE BUG (shared, affects gold too): OTE zone mislabeled — P0
`ICT-SMC-Local-Agent/analysis/structure.py:449-457` (`calculate_premium_discount`):
```python
ote_low  = low + (high - low) * 0.618
ote_high = low + (high - low) * 0.786
...
status = "OTE ZONE ... Highest-probability LONG zone."
```
That zone is 61.8–78.6% of the way **up** the dealing range — the deep **premium** side. In ICT terms, a retrace UP into 62–79% after a bearish leg is the OTE for **SHORTS**; the OTE for LONGS is the mirror zone in discount (21.4–38.2% above the low, i.e. `high − 0.618..0.786 × range`). The code is direction-blind and always labels its (premium-side) zone "highest-probability LONG zone" — backwards or meaningless depending on the leg direction.

**Live impact today:** H1 range 10380.4–10537.3, eq 10458.85. Price 10490.6 was in **premium**, yet the engine said "OTE — highest-probability LONG zone"; the brief cited it in three sections, and the meta shipped `priceZone: "OTE"`. Axiom 4 ("never buy at premium") should have counted *against* the long; instead the mislabel supported it. Same code path feeds every **gold** brief.

**Fix (F1):** make the function direction-aware. Determine the impulse leg from the recent range (e.g. sign of `candles[-1].close − candles[0].close` over the lookback, or take an optional `trend` argument from the caller — the adapter already computes per-TF trend): for a bullish leg, OTE-for-longs = `high − 0.786..0.618×range` (discount side); for a bearish leg, OTE-for-shorts = `low + 0.618..0.786×range` (premium side); label accordingly ("OTE for LONGS (discount retracement)" / "OTE for SHORTS (premium retracement)"). When trend is NEUTRAL, report both zones without a directional recommendation. Update `skill_adapter.py`/`uk100_adapter.py` consumers if the dict shape changes (prefer keeping `ote_low`/`ote_high` + new `ote_direction` field for backward compat). **Mirror to `ICT-SMC-Remote-Agent/analysis/structure.py` byte-identically** (established procedure, cf. tasks #59–61). Regression: run both adapters on the saved fixture `/tmp` inputs (copies preserved at the scratchpad `review/` dir this session — if gone, refetch live) and on a gold input; eyeball that OTE zones land in discount for bullish legs. Meta `priceZone` derivation in both skill docs: "OTE wins if price is inside it" must become "OTE wins only if price is inside the OTE zone *for the trade direction under consideration*; otherwise report PREMIUM/DISCOUNT".

### 3.2 No time-of-day gate in the ORB playbook — P0 (policy)
The brief proposed a **fresh ACTIVE long at 14:45 BST** — 15 min after the US cash open, 62% of ADR14 already used, 1h45m to the cash close — while its own London Session Map says "US cash open 14:30 can reverse the day — book partials before it" and "don't chase pre-US chop". The decision table (STEP 8) has no row expressing this, so the mechanics couldn't say no. The 14:15Z (15:15 BST) reversal bar was precisely the US-session risk the map warns about.

**Fix (F2a, skill doc):** add a first-match row to the decision table between rows 2 and 3: *"Time is past 14:30 London (US_OVERLAP) → any new setup is `WAIT`-status maximum (never `ACTIVE`), targets capped at the nearest liquidity pool (no T3-class stretch targets), and the brief must state the remaining-session context explicitly."* And a matching PROBABILITY SCORING subtraction: **−10% US_OVERLAP window** (currently only PRE_US/POST_CLOSE subtract).

### 3.3 Probability number not auditable — P1
The skill requires "Compute additively from the PROBABILITY SCORING RULES table (base 50, list each +/− applied). Do not freehand a number." The brief printed 62% with no arithmetic. 62 is plausible but unfalsifiable — and at least one credit it likely claimed (+10 "correct premium/discount zone") rested on the §3.1 mislabel.

**Fix (F2b, skill doc):** make it structurally impossible to skip — add a mandatory line to the OUTPUT FORMAT's PROBABILITY ASSESSMENT block: `- **Arithmetic:** 50 [base] +15 [...] −10 [...] = NN%`, and state that a brief without this line is non-compliant and must not be saved.

### 3.4 `rr` field ambiguity — P2
Meta shipped `rr: 1.2`, which is the R:R to **T2** (16.3pt reward / 13.6pt risk). To T1 it was 0.39. Nothing defines which target `rr` refers to, so the Track-Record UI and the future resolver can't interpret it consistently (gold has the same latent ambiguity).

**Fix (F2c, skill doc, both instruments):** define `rr` = (T1 − entry-mid) / (entry-mid − stop), i.e. always the *first* target, and add the definition to both skill docs' meta field guides. (Richer alternatives — an array of per-target R:R — are not worth a schema change now.)

### 3.5 T3 was structurally unreachable — P2
T3 10526.3 was 36pt above entry with ~50pt of typical daily range left (ADR14 133 × 38% remaining) *and* required clearing the grade-A bear FVG the brief itself called "the realistic ceiling for today". Cosmetic here (T1/T2 did the work), but a resolver scoring "all targets" would count it as noise.

**Fix (F2d, skill doc):** targets must be consistent with remaining range: state that T-levels beyond `adr14 × (1 − adrUsedPct/100)` points from entry may only be listed as "stretch, requires displacement" and never counted in `rr`/sizing. (The engine can help — see F3.)

### 3.6 Setup-type taxonomy — P2
`setupType: "ORB Break"` — but the ORB break was DOWN and the trade was LONG; this was a failed-breakdown *reclaim*. Miscategorised setups will pollute the per-setup stats the resolver/backtest phases are meant to produce.

**Fix (F2e, skill doc):** add `Failed-Break Reclaim` to the setup-type vocabulary and one sentence defining it (price breaks the ORB one way, fails to reach the overnight extreme, and closes back inside — trade in the reclaim direction).

### 3.7 Stale US-linkage read during the US session — P1 (data gap)
The brief's US read (US500 −0.37%, NAS100 −0.96%, VIX 17.13) came from the 11:53Z macro snapshot — **~2h stale**, quoted 15 minutes after the US cash open. The UK100 fetch script only pulls UK100 + GBPUSD live. During US_OVERLAP the single most important cross-asset input is the *live* US tape.

**Fix (F3, `ctrader_http_fetch.py`):** in `--instrument uk100` mode, also fetch spot for US500 (symbolId 115), NAS100 (116), VIX (152) — one extra `get_spot_prices` call, zero new auth — and print them in the summary JSON. Skill STEP 5 gains a line: "During US_OVERLAP, quote the live US tape from the fetch output; use the snapshot only for day-% context." Also have `uk100_adapter.py` pass through a `remaining_adr_pts` field (`adr14 × (1 − used%)` needs `adrUsedPct`, which lives in the snapshot — simplest: compute remaining range in the skill from snapshot `adr14`/`adrUsedPct` and the fetch's day high/low; do not over-engineer).

### 3.8 The calendar knows UK events only — P1 (data gap)
The static calendar (Phase A2) is UK-only by design; Finnhub (which would have carried US events) is premium-gated. Consequence: **US CPI/NFP/FOMC — the biggest single intraday movers of UK100 at 13:30/19:00 London — are invisible** to `eventSuppressed`, `eventWindows`, ORB rows 1–2, and the brief's `eventRisk` field. Today had no US print, but the first NFP Friday will sail through as "no events today".

**Fix (F4, `xauusd-dashboard/scripts/lib/calendar.ts`):** add `US_STATIC_CALENDAR_2026` in the same shape (`region: 'US'`), populated the same way A2 was: **WebFetch-verify each date, never invent**. Sources: federalreserve.gov FOMC calendar (all 2026 meeting dates are published); bls.gov release schedules for CPI and Employment Situation (published ~a year ahead); BEA for PCE. Times in London terms (13:30 for CPI/NFP, 19:00 for FOMC statement — mind BST/GMT). Merge via the existing `mergeCalendars` (it already dedupes by (date, keyword-class); add US keyword classes: NFP/CPI-US/FOMC/PCE — note the existing `keywordClass` maps "CPI" for UK; disambiguate by region in the dedupe key: `(date, region, class)`). Unit tests extend `calendar.test.ts`. Gold's calendar benefits automatically once gold's fetch adopts the same lib (optional follow-up, keep out of scope unless trivial).

### 3.9 COT week-over-week reads 0 — P2 (bug, both instruments)
`fetch-uk100-data.ts:449-483`: `wow = net − prevData.cotNetLong` where `prevData` is the **previous hourly snapshot**, not the previous CFTC report. After the first run following a new report, every later run within the freshness window compares the report to itself → `gbpCotWoWChange: 0` (today's snapshot shows exactly this: report 2026-07-07, WoW 0). The PositioningTile is silently underinformative.

**Fix (F5):** persist the *prior report's* net alongside the current one (e.g. `cotPrevReport: { reportDate, netLong }` in the snapshot); recompute `wow` only when `reportDate` changes, else carry the stored value. Check whether gold's `fetch-static-data.ts` COT block has the same pattern and fix it identically if so.

### 3.10 Dashboard ORB tile contradicted the engine — P1 (already planned as V2 Phase B3)
The 11:53Z snapshot said `orbBrokenDirection: "DOWN"` (price was below the ORB low at that moment). After the reclaim, the ~13:53Z hourly snapshot would have flipped to `"NONE"` (current-price comparison), while the engine correctly held `DOWN` (sticky first-close-outside). Live proof of `UK100-V2-PLAN.md` §1.5 — no new work, but **Phase B3 is now evidence-backed and should not be deprioritised.**

### 3.11 Two-leg day shapes can't be expressed — P3 (accepted limitation, doc-only)
The brief's own analysis implied "long to the FVG, then flatten/flip" — the day's best move was the short off that zone, which the brief predicted as its secondary but had no way to encode (one `tradeIdea` per record). Do **not** change the schema now. **Fix (F2f, skill doc):** when the primary target is an opposing A/B-grade FVG and the session is late, the skill should prefer `WAIT` status or explicitly instruct "flatten at T2, no runner" in the trade idea — one sentence in STEP 8's reasoning rules.

### 3.12 Cold-start nits in the skill doc — P2
The run was near-flawless procedurally, but three things relied on the builder already knowing them:
- **moneyDigits:** `get_balance` returns cents (`4646598` = £46,465.98, `moneyDigits: 2`). Sonnet divided correctly; a cold model may print £4.6M. Add one line to STEP 0/ACCOUNT CONTEXT.
- **Post-save git state:** the save script pushes to `origin/main` via plumbing without moving the local branch — a session on a feature branch is left with untracked session files + a behind branch (this tripped the stop-hook today). Add to STEP 9c: "afterwards, if this session has a repo checkout: `git fetch origin main`, remove the now-committed local session files if git blocks the merge (verify byte-identical first via `git diff origin/main -- <paths>`), then `git merge --ff-only origin/main`."
- **newsItems watch:** `newsItems` was `[]` in production today. Plausible (quiet Monday + strict keyword filter), but if it stays empty for ~a week, diagnose exactly like the A2 calendar (log the raw response length once) — add this as a maintenance note in the skill's macro-snapshot bullet or the README, not code.

---

## 4. ACCURACY SCORECARD (for the record / future calibration)

| Claim in the brief | Outcome | Grade |
|---|---|---|
| Primary 62%: continuation into 10495–10507 | T1 hit in the publication bar, T2 +10 min, high 10513.5 | ✅ |
| "10497.8–10506.9 FVG is the realistic ceiling today" | Session high 10513.5, then −53pt rejection | ✅ (zone top exceeded by 6.6pt then slammed) |
| Secondary 33%: rejection from zone → M5 SSL pools 10466.9/10455.3 | 14:15Z low 10460.1, between the two pools | ✅ |
| Invalidation "M5 close back below 10482/10478.3" | 14:15Z bar closed 10479.9 → thesis correctly dead | ✅ |
| SMT BEARISH = "don't chase, treat as bounce into resistance" | The reversal came | ✅ |
| `priceZone: OTE` ("highest-probability LONG zone") | Actually H1 premium — engine mislabel (§3.1) | ❌ |
| Fresh ACTIVE long at 14:45 BST | Stopped on the runner 30 min later; late-session entry against own map | ⚠️ policy gap (§3.2) |
| T3 10526.3 | Never approached (session high 10513.5) | ❌ unreachable (§3.5) |
| US linkage numbers | 2h stale during live US session | ⚠️ (§3.7) |
| 62% arithmetic | Not shown | ⚠️ (§3.3) |

Net: **directionally strong, mechanically sloppy at the edges.** First-touch scoring = win; the sloppiness is exactly what F1–F5 remove.

---

## 4A. EUROPEAN CORRELATION STUDY (measured live 2026-07-13 — motivates F8/F9)

Prompted by the user's observation that UK100 rises and falls with GER40 and the Euro Stoxx 50 daily. **Measured, not assumed** — UK100 log-return Pearson correlation against each reference, pulled live from cTrader (`get_trendbars`, this account):

| Reference (broker symbolId) | H_1, ~15d (n≈99) | M_5, today (n=99) |
|---|---|---|
| **Euro Stoxx 50** — `EUSTX50` (124) | **+0.68** | +0.73 |
| CAC 40 — `FRA40` (125) | +0.68 | — |
| DAX — `GER40` (110) | +0.64 | **+0.75** |
| S&P 500 — `US500` (115) | +0.55 | +0.48 |
| GBP/USD (2) | +0.06 | — |
| EUR/USD (1) | +0.14 | — |

*(D_1 correlation not tabled: `get_trendbars D_1` silently returns empty on windows wider than the production 22-day pull, a known cap quirk — the intraday timeframe is the relevant one for an ORB/intraday tool anyway, and daily FTSE/DAX/SX5E correlation is textbook ~0.7–0.85 in normal regimes. Re-measure over a 22-day D_1 window if a daily figure is wanted.)*

**Findings:**
1. **The European complex out-correlates the US tape intraday.** Euro Stoxx 50 ≈ CAC ≈ DAX all cluster at r≈0.64–0.68 (H1) / 0.73–0.75 (M5) — materially tighter than S&P 500 (0.48–0.55) and an order of magnitude tighter than GBP/EUR FX. The user's intuition is correct and then some: at the 08:00 London open the FTSE trades the **European cash-session risk pulse**, not the (thin Globex) US tape.
2. **Euro Stoxx 50 is the single best / tied-best correlate** and is the pan-Eurozone benchmark — the cleanest read of "European risk on/off." It is available here as a plain CFD (`EUSTX50`, symbolId **124**, pipDigits 5 — same class as US500/GER40/UK100). CAC 40 (`FRA40`, **125**) is near-collinear with it (adds little marginal signal).
3. **GBP intraday r≈0.06 confirms the sign-flip design is right.** GBP's effect on FTSE is *conditional/regime* (big on GBP-driven days, ~zero otherwise), NOT linear co-movement — which is exactly why the weight-3 GBP driver is a sign-flipped conditional, not a correlation term. It also means the bias engine currently weights its *least* intraday-informative macro input (GBP, w3.0) highest while having **no European-tape input at all** — the biggest single gap this study exposes.

**Why this is more than "add another correlated number to the bias sum" (it would be partly circular — the European tape *is* European beta).** The value is in three non-circular uses:
- **(a) Pre-open lead.** DAX/SX5E open the same 08:00 London / 09:00 CET, but STOXX (FESX) and DAX (FDAX) **futures trade the pre-market and lead** the FTSE open. "European tape already broke UP through its overnight range while the FTSE ORB is still forming" is a genuine, non-circular directional lead for the 08:00 ORB.
- **(b) Divergence / decoupling detector.** When FTSE is *not* tracking the complex — a commodity-driven outperformance day (today: Brent +3.36%, FTSE firmer than the read-through), or a UK-specific gilt/political shock — that decoupling is itself the signal: it says the FTSE is trading its own idiosyncratic story and the European-beta assumption is off. A rolling DAX↔FTSE / SX5E↔FTSE correlation (same `pearson()` the V2 plan already specs for GBP↔FTSE) quantifies "is the link live right now."
- **(c) Multi-tape conviction gate.** DAX + SX5E + US futures all agreeing on direction ⇒ higher-probability ORB break in that direction; split ⇒ lower. Time-of-day-weighted: **European tape dominates pre-14:30 London; US tape dominates post-14:30** (dovetails with F2a/F3's US_OVERLAP handling).

**Implication for V2 Phase D.** The plan currently specs only a GER40 driver at weight 2.0. This study says: make **Euro Stoxx 50 the primary European-tape driver** (co-equal with or ahead of DAX), keep DAX as the second tape for the agree/diverge signal, and enter the European-tape driver at a weight reflecting its measured explanatory power (≥2.0, i.e. at least the US-futures 2.5 tier for the pre-14:30 window) — with the final weight **validated against the Phase C resolver data**, not hard-coded on faith (same empirical discipline as the rest of the project). Do **not** cut the GBP weight: its conditional value is real; it's just orthogonal to this.

Additional EUR-side data points worth adding while touching this area (lower priority, listed in F9):
- **EUR/USD day%** — the EUR analog of the GBP sign-flip: a strong EUR is a headwind for DAX/SX5E exporters, so it modulates how bullish a European-tape rally really is for the read-through.
- **EUR/GBP** (already carried as `GBPEUR`) as the decoupling tell: when it's flat and FTSE+complex move together = shared risk beta; when it moves = expect FTSE and the European complex to diverge.
- **Bund yield / BTP–Bund spread** — European sovereign-rates analog to the gilt strip already pulled; SX5E is bank-heavy so it matters. Nice-to-have, not blocking.

---

## 5. FIX LIST (execute in this order)

| # | What | Files | Effort | Priority |
|---|---|---|---|---|
| F1 | Direction-aware OTE + labels; `ote_direction` field; adapters + both skill docs' `priceZone` rule; **mirror to Remote agent**; regress gold + UK100 on fixtures | `ICT-SMC-{Local,Remote}-Agent/analysis/structure.py`, `skill_adapter.py`, `uk100_adapter.py`, both skill docs | 1–1.5h | P0 |
| F2 | Skill-doc hardening: (a) US_OVERLAP row + −10% scoring; (b) mandatory probability-arithmetic line; (c) `rr`=T1 definition (both docs); (d) remaining-range target cap; (e) `Failed-Break Reclaim` setup type; (f) flatten-at-opposing-FVG rule; plus §3.12 nits (moneyDigits, post-save git, newsItems watch) | `.claude/commands/uk100-session.md` (+ `gold-session.md` for c only) | 45m | P0 |
| F3 | Live US tape: US500/NAS100/VIX spots in `--instrument uk100` fetch + STEP 5 live-tape line + remaining-ADR arithmetic guidance | `ICT-SMC-Local-Agent/ctrader_http_fetch.py`, skill doc | 45m | P1 |
| F4 | `US_STATIC_CALENDAR_2026` (FOMC/CPI/NFP/PCE, WebFetch-verified only), region-aware dedupe key, tests | `xauusd-dashboard/scripts/lib/calendar.ts`, `calendar.test.ts` | 1h | P1 |
| F5 | COT WoW report-over-report (UK100 + check gold) | `fetch-uk100-data.ts`, possibly `fetch-static-data.ts` | 30m | P2 |
| F6 | = **V2 Phase B unchanged** (label thresholds, VIX vocab, sticky `orbBrokenDirection`, 08:20 cron) — §3.10 upgraded B3 from "planned" to "evidence-backed" | per V2 plan | per V2 plan | P1 |
| F7 | = **V2 Phase C** (resolver) with one enrichment: record the *chronological sequence* of level hits (e.g. `hits: ["T1","T2","STOP"]` + timestamps) rather than a single first-touch outcome — today's T1→T2→STOP sequence is the canonical test case; keep the conservative both-in-one-bar=loss rule from the V2 plan | per V2 plan + this note | +30m over V2 est. | P2 |
| F8 | **European-tape driver (§4A, supersedes V2 Phase D's GER40-only spec).** Add **Euro Stoxx 50** (`EUSTX50`, symbolId **124**, pipDigits 5) to `KNOWN_SYMBOL_IDS`/`PIP_DIGITS` and to the UK100 fetch (spot + day% + a short intraday series for correlation); keep **GER40** (110) as the second tape. New snapshot block `europeanTape`: `{ eurostoxx50DayPct, dax40DayPct, ftseDaxCorr20d, ftseSx5eCorr20d, tapeAgreement: 'ALIGNED'|'SPLIT'|'DIVERGING', preOpenLead: 'UP'|'DOWN'|'NONE' }` (reuse the V2 `pearson()`; `preOpenLead` from the European tape's own overnight-range break at UK100 fetch time when mode=PRE_OPEN/OPENING_HOUR). Bias engine: add a **European-tape driver**, weight ≥2.0, *time-of-day weighted* (full weight pre-14:30 London, reduced post-14:30 as the US tape takes over — pairs with F2a/F3); final weight a TODO to be recalibrated from F7 resolver data, not faith-fixed. Skill STEP 5 gains a European-tape paragraph (cite `europeanTape`, use the divergence/lead reads per §4A(a)–(c), never as a naive "tape up ⇒ buy"). New macro tile `Uk100EuropeanTapeTile`. Unit-test the correlation + agreement/divergence classification (pure fns). Gold untouched. | `xauusd-dashboard/scripts/lib/ctrader.ts`, `fetch-uk100-data.ts`, `src/types/uk100.ts`, a new tile + explainer + test, README | 2.5–3.5h | P1 |
| F9 | **EUR-side context (optional, while F8 is open).** `eurUsdDayPct` (EUR/USD id 1 — the EUR sign-flip analog: strong EUR = DAX/SX5E exporter headwind, modulates read-through) surfaced in the European-tape read; use existing `GBPEUR` as the decoupling tell (flat EUR/GBP + complex moving together = shared beta; moving = expect divergence). **Bund yield / BTP–Bund spread** (European sovereign-rates analog to the gilt strip) is a further nice-to-have — only if a clean free source is found, else defer. | `fetch-uk100-data.ts`, skill STEP 5 | 45m–1h | P2/P3 |

Then V2 Phases D/E/F continue as written (**F8 replaces Phase D's GER40 sub-item; the rest of Phase D — GBP↔FTSE correlation, volume confirmation, riskFraction — stands**). Screenshot verification of the AI sub-tab (old task #84) remains blocked by the sandbox's TLS-intercepting proxy (Chromium won't trust the CA; `libnss3-tools` uninstallable) — verify via the deployed JSON endpoints instead, as done today, or screenshot from a local machine.

### Execution rules (unchanged from V2, restated)
- Each fix ends: `npx tsc --noEmit` + `npm run build` + `npx vitest run` green (where TS touched), workflow YAML parses, **gold regression** where shared code is touched (`fetch-static-data.ts` shape-check; for F1 also run `skill_adapter.py` on a gold fixture) → descriptive commit → push to `claude/xauusd-intelligence-dashboard-t5jnzh` → fast-forward push to `main`. Never force-push main.
- F1 touches the shared engine: `analysis/` must remain byte-identical between Local and Remote agents.
- Never invent calendar dates (F4): every date WebFetch-verified against the official source, cite the source URL in a comment, only the dates you verified.
- Locally-generated snapshots are discarded (`git checkout -- xauusd-dashboard/public/data/`), never committed.

---

## 6. HANDOFF PROMPT (give this to the builder model)

> Execute `UK100-SESSION-REVIEW-2026-07-13.md` §5, fixes F1–F5 in order, then F8 and F9 (F6/F7 = existing UK100-V2-PLAN.md Phases B and C — do those in sequence too; F8 supersedes V2 Phase D's GER40-only European driver, the rest of Phase D still stands). Read the review doc fully first — it is self-contained; do not re-derive the diagnoses, but re-verify each fix against the evidence cited in §3 and the measured correlations in §4A. Work on branch `claude/xauusd-intelligence-dashboard-t5jnzh`. Each fix ends with the full verify → commit → push → fast-forward-main cycle from §5's execution rules, so you can stop after any fix with nothing half-wired. F1 modifies the shared engine: mirror `analysis/structure.py` byte-identically to `ICT-SMC-Remote-Agent`, and regression-test BOTH `skill_adapter.py` (gold) and `uk100_adapter.py` (UK100) on live-fetched fixtures before committing. F4's calendar dates must each be WebFetch-verified against federalreserve.gov / bls.gov / bea.gov — wrong dates are worse than missing dates. F8 adds Euro Stoxx 50 (`EUSTX50`, symbolId 124) as the primary European-tape driver — its bias-engine weight is a TODO to be recalibrated from F7 resolver data, not a faith-fixed constant; wire the plumbing/tile/tests now and mark the weight provisional.

---

## 7. OPEN QUESTIONS FOR THE USER (non-blocking)

1. **Management style for the resolver (F7):** should the Track Record score first-touch (T1 before stop = win, gold's convention) or sequence-aware partial credit (T1+T2 banked, runner stopped = larger win)? Today's trade is a win under both, but the conventions diverge on other shapes. Default if unanswered: first-touch, matching gold.
2. **Late-session policy strictness (F2a):** the proposed rule still allows WAIT-status ideas after 14:30 London. If you'd rather have a hard NO-NEW-TRADES cutoff (e.g. 15:30 London), say so — one-line change.
3. **US calendar scope (F4):** FOMC/CPI/NFP/PCE proposed. Add ISM/JOLTS/Retail Sales? Each adds noise to `eventSuppressed`; the four proposed are the ones that reliably move UK100.
4. **European-tape weighting (F8):** the measured intraday correlation (§4A) says the European tape deserves a bias-engine weight at least on par with the US-futures 2.5 driver for the pre-14:30 window — but I've left the exact number as a resolver-validated TODO rather than hard-coding it. If you'd prefer a concrete starting weight to run with now (e.g. 2.5 pre-14:30 decaying to ~1.0 post-14:30), say so and it goes in as the provisional constant. Also: keep CAC 40 (`FRA40`, 125) out (near-collinear with Euro Stoxx 50) unless you specifically want a third confirmation tape.
