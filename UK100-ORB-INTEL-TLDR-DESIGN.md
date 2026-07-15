# UK100 — ORB Intelligence Tile + AI-Session TL;DR — Design Spec

**Date:** 2026-07-15 · **Author:** design session (Fable) · **Status:** APPROVED FOR BUILD — execute phases G1→G2→G3 in order.

This document is self-contained. The builder does not need to re-derive any of the analysis
below — but must re-verify each implementation against the acceptance criteria in each phase.
Work on branch `claude/xauusd-intelligence-dashboard-t5jnzh`. Each phase ends with the full
cycle: `npx tsc --noEmit` + `npx vitest run` + `npm run build` green (run from
`xauusd-dashboard/`), a live `npx tsx scripts/fetch-uk100-data.ts` run that completes without
error (discard the generated snapshot with `git checkout -- xauusd-dashboard/public/data/`
afterwards — do not commit a tokenless snapshot), then descriptive commit → push to the
feature branch → fast-forward push to `main` (`git push origin <branch>:main`). Stop after
any phase with nothing half-wired.

---

## 0. The two asks, in the user's words

1. **ORB tile**: "provide intel on the high-probability options based on pricing, market
   structure, historical levels, the macro data and AI's analysis of the other pieces the
   agents and dashboard pull. Something like *'due to XYZ the market is bearish and
   breakouts long may not be sustained'* — a set of bullet points."
2. **TL;DR at the top of the AI session**: "bullet points of the key points that get across
   the current market structure, regime and high-level plan for the day as well as key news
   stories. A top-level summary of the output the AI summary provided."

---

## 1. Findings from the investigation (read before building)

**F-A. The hourly snapshot already carries almost everything the ORB intel needs.**
`daily-snapshot.json` has: `orbContext` (mode, overnight H/L, PDH/PDL, prior close, gap,
ORB H/L, **sticky** `orbBrokenDirection` since F6/B3, event windows, ADR14 + `adrUsedPct`),
the 9-driver `bias` engine (incl. the F8 European-tape driver), `fx` (GBP sign-flip +
`gbpUsd20dPercentile`), `usLinkage` (US500/NAS100/VIX + regime), `europeanTape`
(SX5E/DAX day%, `tapeAgreement`, `preOpenLead`, `eurUsdDayPct`), `commodities`, `ukRates`
(`longEndStress`), `positioning` (GBP COT crowding), `sectorPanel`, `riskTone` (LLM),
`economicCalendar`, `newsItems`, and the LLM `briefing`. The intel layer is therefore a
**synthesis problem, not a data problem** — cross-referencing fields that already exist.

**F-B. The UK100 `briefing` paragraph is generated hourly but rendered NOWHERE.**
`generateUk100Briefing()` runs every fetch (its prompt already includes an "ORB relevance"
sentence, item 6) and the result is stored in the snapshot — but no UK100 component consumes
`snapshot.briefing` (only gold's `App.tsx` renders a BriefingPanel, for gold's own briefing).
The ORB-intel design below reuses this exact call (extended output schema) rather than adding
a new API call — which also finally puts that paid-for output on screen.

**F-C. What the hourly snapshot does NOT have: intraday ICT structure.**
BOS/CHoCH, FVGs, liquidity pools, premium/discount live in the Python engine, which only runs
when the user runs `/uk100-session`. Two mitigations (both in this design): (1) price-vs-level
geometry (price relative to ORB range, overnight range, PDH/PDL) is itself a structure proxy
and drives the fakeout/reclaim detection rule; (2) the fetch script can read the **same-day AI
session record** from `public/data/uk100/sessions/index.json` (present in the repo checkout the
workflow runs in) and surface its direction/status/probability as one "AI" bullet. Do **not**
try to port the Python structure engine to TS — out of scope.

**F-D. Historical *base rates* don't exist yet.** The Phase E ORB backtest
(`UK100-V2-PLAN.md` §7) hasn't been built, so "historical levels" today means reference
levels (PDH/PDL/PWH/PWL/ADR), not measured breakout win rates. The `OrbIntel` schema below
reserves an optional `baseRateNote` field so Phase E can plug in later without a schema break.
Do not fabricate base-rate numbers before Phase E exists.

**F-E. PWH/PWL are missing from the snapshot's `orbContext`** (the engine has them; the
hourly TS fetch doesn't compute them) — but `fetchCtraderData()` already holds 30 days of
UK100 D_1 bars (`uk100D1Bars`), so previous-ISO-week high/low is a cheap additive computation.
G1 adds them.

**F-F. Today (2026-07-15) is a perfect worked example** for calibrating the rules: ORB broke
DOWN at the open, price then reclaimed the whole range, swept the overnight high and ran to
10533 — the mechanical `orbBrokenDirection: "DOWN"` alone is actively misleading without the
"break was a sweep; the reclaim is in control" synthesis. The fakeout rule (R1 below) exists
precisely for this shape, and the G1 unit tests pin it with these literal numbers.

---

## 2. PART 1 — ORB Intelligence (`orbIntel`)

### 2.1 Architecture: mechanical rules engine + AI overlay (hybrid)

- **Layer 1 — `computeOrbIntel()`** (pure function in `fetch-uk100-data.ts`, exported for
  tests): deterministic bullets from the rules table (§2.3). Zero API cost, never null,
  unit-testable, identical output for identical snapshots. This layer ALWAYS renders.
- **Layer 2 — AI overlay**: extend the **existing** `generateUk100Briefing()` Anthropic call's
  output JSON (no new API call) with an `orbIntel` object: a one-line stance sentence + 2–4
  synthesis bullets. Because the briefing runs LAST over the fully-assembled snapshot, the
  model sees the mechanical signals and adds cross-cutting synthesis on top instead of
  duplicating them. Merged into the snapshot post-call as `aiStanceLine`/`aiBullets`;
  `null`/`[]` when `ANTHROPIC_API_KEY` is absent — the tile degrades to Layer 1 only.
- **Layer 3 — same-day session echo**: one optional `AI`-source signal citing today's latest
  `/uk100-session` record (see §2.4 rule R12).

Rationale for hybrid over pure-LLM: the tile must never be empty on a key failure, must be
consistent run-to-run for the same inputs (this project's cross-session-consistency
discipline), and each mechanical bullet is unit-testable against the review-doc incidents.
Rationale for hybrid over pure-mechanical: the user explicitly asked for "AI's analysis of
the other pieces" — genuine synthesis ("GBP at its 20-day high AND crowded-short COT AND a
split European tape together mean...") is what the LLM adds cheaply on the existing call.

### 2.2 Schema (additive — no existing field changes)

Add to BOTH the script-local types in `scripts/fetch-uk100-data.ts` AND
`src/types/uk100.ts` (mirrored exactly, per existing convention):

```ts
export type OrbIntelDirection = 'FAVOURS_LONG' | 'FAVOURS_SHORT' | 'BREAKOUT_SUSPECT' | 'NEUTRAL'
export type OrbIntelSeverity  = 'INFO' | 'CAUTION' | 'STRONG'
export type OrbIntelSource    =
  'STRUCTURE' | 'RANGE' | 'GAP' | 'TAPE' | 'FX' | 'RATES' | 'POSITIONING' | 'EVENT' | 'AI'

export interface OrbIntelSignal {
  direction: OrbIntelDirection
  severity:  OrbIntelSeverity
  source:    OrbIntelSource
  text:      string            // one plain-English sentence, ≤ 200 chars
}

export type OrbIntelStance =
  'LONG_FAVOURED' | 'SHORT_FAVOURED' | 'FADE_FAVOURED' | 'BREAKOUTS_SUSPECT' | 'MIXED'

export interface OrbIntel {
  stance:       OrbIntelStance
  stanceLine:   string             // mechanical fallback stance sentence (always present)
  signals:      OrbIntelSignal[]   // 3–6, ranked (see §2.5), mechanical layer
  aiStanceLine: string | null      // LLM synthesis sentence; null when no API key
  aiBullets:    string[]           // LLM synthesis bullets (0–4); [] when no API key
  baseRateNote: string | null      // reserved for Phase E orb-stats; ALWAYS null for now
}
```

`Uk100Snapshot` gains `orbIntel: OrbIntel` (place directly after `orbContext`). Also add
`prevWeekHigh: number | null` and `prevWeekLow: number | null` to `OrbContext`
(script-local + `src/types/uk100.ts`) — computed in `fetchCtraderData()` from the existing
`uk100D1Bars` (high/low of bars whose London date falls in the previous ISO week; `null` if
fewer than 3 such bars). All existing consumers are unaffected (additive fields).

### 2.3 The signal rules table — THE core deliverable of the investigation

`computeOrbIntel(input)` takes a single input object (spec the exact shape from the fields
referenced below, all nullable) and evaluates every rule; each rule either emits one signal
or nothing. **Every threshold below is deliberate — do not re-tune during the build.** Where
a rule needs "now", use London hour (reuse the `londonNow()` helper already in the file).

`mode` = `orbContext.mode`. "Remaining range budget" = `adr14 × (1 − adrUsedPct/100)`
(null-safe: skip budget rules when either input is null).

| # | Rule (fires when…) | Emits | Example text |
|---|---|---|---|
| **R1 — Fakeout / reclaim** (mode POST_ORB or CLOSED) | `orbBrokenDirection` = DOWN AND current price > `orbHigh` (or mirrored: UP AND price < `orbLow`) | STRONG · FAVOURS_LONG (resp. SHORT) · STRUCTURE | "ORB broke DOWN but price has fully reclaimed the range — the break was a liquidity sweep; the reclaim direction is in control, don't trade the original break." |
| **R2 — Counter-bias break** (POST_ORB) | `orbBrokenDirection` = UP AND `bias.score` ≤ −3 (or DOWN AND ≥ +3), and R1 did not fire | CAUTION · BREAKOUT_SUSPECT · STRUCTURE | "ORB broke UP against a BEARISH macro bias (−4) — counter-bias breaks fail more often; treat continuation as suspect until the overnight high is taken." |
| **R3 — With-bias break** (POST_ORB) | `orbBrokenDirection` matches sign of `bias.score`, \|score\| ≥ 3, R1 not fired | INFO · FAVOURS_LONG/SHORT · STRUCTURE | "ORB break DOWN is aligned with the BEARISH macro bias (−5) — continuation has the backdrop behind it." |
| **R4 — Range budget** | `adrUsedPct` ≥ 70 (CAUTION) or ≥ 90 (STRONG) | BREAKOUT_SUSPECT · RANGE | "78% of a typical day's range is already spent — fresh breakouts have little fuel; favour fades back into the range over chasing." |
| **R5 — Gap against bias** (PRE_OPEN/ORB_FORMING/OPENING hour, i.e. London hour < 9) | \|`gapPct`\| ≥ 0.4 AND gap sign opposes `bias.score` sign with \|score\| ≥ 3 | CAUTION · BREAKOUT_SUSPECT · GAP | "Gapped UP +0.5% against a bearish bias — a gap-fill toward prior close (10478) is the statistically favoured first move, not continuation." |
| **R6 — Gap with bias, room to run** (same window) | \|`gapPct`\| ≥ 0.25 AND gap sign matches bias sign (\|score\| ≥ 3) AND overnight range < 0.5 × `adr14` | INFO · FAVOURS_LONG/SHORT · GAP | "Gap up in the bias direction with a tight overnight range — trend-day conditions; the first ORB break long carries the setup." |
| **R7 — Draw beyond fuel** | nearest unswept PDH (if bias ≥ 0) / PDL (if < 0) is further from current price than the remaining range budget | CAUTION · NEUTRAL · RANGE | "The obvious draw (PDH 10545) sits beyond what's left of a typical day's range — targets past it are stretch-only today." |
| **R8 — European tape** | `tapeAgreement` = DIVERGING → CAUTION·BREAKOUT_SUSPECT; SPLIT → INFO·NEUTRAL; ALIGNED AND \|`eurostoxx50DayPct`\| > 0.15 → INFO·FAVOURS_(sign) — all source TAPE. In PRE_OPEN/ORB_FORMING additionally: `preOpenLead` ≠ NONE → INFO·FAVOURS_(lead) | | "FTSE is diverging from a united European tape — it's trading its own story today; tape-based confirmation is unreliable." / "European futures already broke UP through their overnight range pre-open — an early lean for an upside resolution." |
| **R9 — US tape / VIX** | `vixRegime` = STRESS → STRONG·BREAKOUT_SUSPECT·TAPE ("violent reversals both ways — cut size"). Else if London hour ≥ 13.5 AND \|`us500DayPct`\| ≥ 0.3 → INFO·FAVOURS_(sign)·TAPE citing the 14:30 US-open handoff | | "Past 13:30 with US futures −0.6% — the US handoff argues against holding longs into 14:30." |
| **R10 — GBP extreme** | `gbpUsd20dPercentile` ≥ 85 AND `gbpUsdDayPct` > 0 → CAUTION·BREAKOUT_SUSPECT (long side)·FX; mirrored ≤ 15 AND < 0 → INFO·FAVOURS_LONG·FX | | "Sterling is at the 89th percentile of its 20-day range and still rising — a persistent FX headwind capping upside breaks." |
| **R11 — Fiscal stress / COT** | `longEndStress` = true → STRONG·FAVOURS_SHORT·RATES (overrides all bank-rotation logic). Separately: `positioning.crowding` = CROWDED_SHORT → INFO·BREAKOUT_SUSPECT·POSITIONING ("a GBP short-squeeze is a latent slap for upside breaks") | | "20Y gilt +9bp — fiscal-stress selloff; this historically drags the whole index regardless of the banks rotation." |
| **R12 — Same-day AI session echo** | latest entry in `public/data/uk100/sessions/index.json` has `date` = today (London) | INFO · FAVOURS_(tradeIdea.direction, or NEUTRAL if NO_TRADE) · AI | "Today's 15:26 BST AI session read: SHORT fade toward 10502 (WAIT, 61%) — playbook BOTH_OK." |
| **R13 — Event windows** | `orbContext.eventWindows` non-empty → CAUTION·BREAKOUT_SUSPECT·EVENT (pre-release breaks are positioning). Else if a HIGH-impact calendar event has `daysFromToday` = 1 AND London hour ≥ 14 → INFO·NEUTRAL·EVENT ("late-session moves may be de-risking ahead of tomorrow's print, not conviction") | | "UK GDP prints tomorrow 07:00 BST — late-session breakouts today are as likely pre-event positioning as conviction." |

Read the file's `orbContext`/`bias`/`europeanTape` etc. from the assembled snapshot pieces
already in scope in `main()` — call `computeOrbIntel()` after `computeOrbContext()` and
before the briefing call, so the briefing prompt sees it.

### 2.4 Stance aggregation (deterministic)

1. If R1 fired → `FADE_FAVOURED` (its direction), stanceLine built from R1's text.
2. Else if \|`bias.score`\| ≥ 3 AND no STRONG signal opposes that direction →
   `LONG_FAVOURED`/`SHORT_FAVOURED`.
3. Else if ≥ 2 signals with direction BREAKOUT_SUSPECT at severity ≥ CAUTION →
   `BREAKOUTS_SUSPECT`.
4. Else → `MIXED`.

`stanceLine` template: `"<stance phrase> — <top-ranked signal text>"` where stance phrases
are exactly: LONG_FAVOURED → "Backdrop favours upside breaks"; SHORT_FAVOURED → "Backdrop
favours downside breaks"; FADE_FAVOURED → "Fade day — the ORB break was a trap";
BREAKOUTS_SUSPECT → "Breakouts suspect in both directions today"; MIXED → "No clean edge —
mixed signals". This is the mechanical fallback for the user's "due to XYZ…" sentence; the
AI's `aiStanceLine` (when present) renders INSTEAD of it, with the mechanical one as fallback.

### 2.5 Ranking & cap

Sort signals STRONG > CAUTION > INFO; ties by source priority
STRUCTURE > RANGE > GAP > TAPE > RATES > FX > EVENT > POSITIONING > AI. Keep at most **6**;
always keep R1 and R12 if they fired (R12 may displace the lowest-ranked INFO).

### 2.6 AI overlay — briefing prompt change (G2)

In `BRIEFING_SYSTEM_PROMPT`: (a) mention that the snapshot now contains `orbIntel.signals`
(the mechanical read) and instruct the model to ADD synthesis, not repeat them; (b) change
the output JSON contract to:

```json
{ "biasScore": ..., "biasLabel": ..., "confidence": ..., "briefing": "...",
  "orbIntel": { "stanceLine": "one sentence in the form 'Due to X, Y and Z, <read>'",
                 "bullets": ["...", "..."] } }
```

Rules for the model (state them in the prompt): 2–4 bullets, each ≤ 30 words, each must cite
at least one concrete snapshot number, no invented data, bullets must cover something the
mechanical signals do NOT already say (cross-field synthesis). After the call, merge:
`orbIntel.aiStanceLine = parsed.orbIntel?.stanceLine ?? null`,
`orbIntel.aiBullets = parsed.orbIntel?.bullets ?? []`. Tolerate the field being absent in the
response (older cached prompts, model noncompliance) — never fail the snapshot on it.
`max_tokens`: raise 1200 → 1500.

### 2.7 Tile UI (`Uk100OrbTile.tsx` restructure)

Top-to-bottom: (1) existing mode badge row; (2) **stance banner** — stance as a badge
(FADE_FAVOURED/BREAKOUTS_SUSPECT → `badge-amber`, LONG_FAVOURED → `badge-green`,
SHORT_FAVOURED → `badge-red`, MIXED → `badge-muted`) + `aiStanceLine ?? stanceLine` as one
emphasised sentence; (3) **signal bullets** — each signal as a compact row: small source chip
(STRUCTURE/TAPE/FX/…) + text, text coloured by direction (up/down/flat classes already global);
`aiBullets` appended after mechanical ones with an `AI` chip; (4) a `<details>` collapsible
"Range numbers" containing the CURRENT tile's number grid unchanged (ORB H/L, broken,
overnight, PDH/PDL + new PWH/PWL row, prior close, gap, ADR) — the numbers demote to
secondary, intel is primary; (5) existing event-window caution banner + `TileExplainer`
(update `explainOrb` only if its tests break — not otherwise in scope). The tile will get
taller than its grid siblings; that is accepted — do NOT truncate signals to avoid it.

### 2.8 Tests (extend `scripts/__tests__/fetch-uk100-data.test.ts`)

Pin at minimum: R1 with 2026-07-15's literal numbers (broke DOWN, orbHigh 10471.3, price
10524.75 → FADE_FAVOURED + STRONG FAVOURS_LONG signal); R2 counter-bias; R4 at 69/70/90
boundaries; R5 gap-against; stance rule 3 (two CAUTION suspects → BREAKOUTS_SUSPECT); the
all-null snapshot (→ MIXED, ≥0 signals, never throws); ranking cap at 6 with R1 retained.

---

## 3. PART 2 — AI-Session TL;DR

### 3.1 Placement & source of truth

A `TldrCard` rendered at the very top of the session view in `AiSubTab.tsx` — above the
`gaugeRow` (it's the first thing read). Source of truth: a new **structured meta field
written by the skill** (deterministic, like every other meta field), NOT client-side parsing
of the analysis text. Fallback for records without it: synthesize from existing structured
fields (§3.4); hide the card only when even that fails.

### 3.2 Schema

```ts
export type TldrTag = 'STRUCTURE' | 'REGIME' | 'PLAN' | 'LEVELS' | 'NEWS' | 'RISK'
export interface TldrBullet { tag: TldrTag; text: string }   // text ≤ 220 chars
```

Add `tldr?: TldrBullet[]` (4–7 entries) to: `SessionMeta` in
`scripts/save-gold-session.ts` (passes through the spread untouched — verify it lands in the
saved file), `Uk100SessionRecord` in `src/types/uk100.ts`. Keep the rolling `index.json`
lean — do NOT add tldr to `IndexEntry`.

### 3.3 Skill-doc changes (`.claude/commands/uk100-session.md`)

1. **Output format**: insert a `## TL;DR` section immediately after the H1 title line (before
   `## ACCOUNT CONTEXT`) — exactly one bullet per tag in this fixed order, with derivation
   rules stated in the doc so two sessions on the same data produce the same bullets:
   - `STRUCTURE` — H1 + M5 regime and the most recent structural event with its timestamp,
     from the engine's `structure_breaks` (e.g. "H1 NEUTRAL / M5 BULLISH — sweep-and-reclaim
     day; first bearish M1 crack at 15:05 BST").
   - `REGIME` — mechanical `bias.score`/`label`/`conviction` verbatim + the STEP 5 macro
     verdict clause (e.g. "Bias NEUTRAL +1, LOW conviction — macro genuinely mixed").
   - `PLAN` — ORB playbook direction + day type + the single actionable sentence of the day,
     consistent with STEP 8's output (e.g. "BOTH_OK half size — prefer the fade toward 10502
     over chasing PDH; WAIT status, US_OVERLAP gate active").
   - `LEVELS` — the 2–3 most decision-relevant prices only, with one-word roles
     ("10533 invalidation · 10502 T1 · 10545 PDH draw").
   - `NEWS` — top same-session catalyst with `hoursAgo` + source, or the literal phrase
     "No market-moving news identified" (from `newsItems`).
   - `RISK` — next HIGH-impact event with UK-local time, or "No high-impact events this week".
   Optionally ONE extra bullet (any tag) when something material doesn't fit — hard cap 7.
2. **Meta JSON**: add the `tldr` array to the STEP 9 example + the deterministic-derivation
   table ("`tldr` — mirror the printed TL;DR section verbatim, same order, same texts").
3. Add to WHAT-TO-NEVER-DO: "Never print a brief without the TL;DR section; never let the
   TL;DR contradict the sections it summarises."

### 3.4 Fallback for old records — `synthesizeTldr()`

Pure function in a NEW file `src/components/uk100/tldr.ts` (exported, unit-tested):
`synthesizeTldr(record: Uk100SessionRecord): TldrBullet[]`. If `record.tldr?.length` → return
it unchanged. Else build from structured fields, skipping any bullet whose inputs are missing:
REGIME from `bias`/`biasScore`/`confidence`; PLAN from `orbPlaybook.direction`+`dayType` and
`tradeIdea` (direction/status/probability); LEVELS from `invalidation` + `drawOnLiquidity` +
first `tradeIdea.targets`; RISK from `nextHighImpactEvent`. STRUCTURE/NEWS are omitted in
fallback (not reliably derivable from meta). Return `[]` only if nothing derivable → card hidden.

### 3.5 UI — `TldrCard`

New component in `src/components/uk100/TldrCard.tsx`, rendered by `AiSubTab` as
`{(() => { const bullets = synthesizeTldr(session); return bullets.length > 0 && <TldrCard bullets={bullets} /> })()}`
above the gauge row. Visual: a `styles.card`-class card titled "TL;DR", each bullet a row with
a small tag chip (reuse the badge classes: PLAN → `badge-gold`, RISK/NEWS → `badge-amber`,
others `badge-muted`) and the text in normal body type. No collapsing — the whole point is
zero clicks. Mobile: chips wrap above text (flex-wrap) — verify at 390px width.

### 3.6 Tests

`src/components/uk100/__tests__/tldr.test.ts`: passthrough when `record.tldr` present;
fallback synthesis from the real 2026-07-15 record's fields (fixture: bias NEUTRAL/+1,
orbPlaybook BOTH_OK/RANGE_EXPECTED, tradeIdea SHORT/WAIT/61%, invalidation 10535,
nextHighImpactEvent UK GDP) → asserts REGIME/PLAN/LEVELS/RISK bullets exist and PLAN mentions
"BOTH_OK"; empty record → `[]`.

---

## 4. Execution phases

| Phase | Scope | Files | Est. |
|---|---|---|---|
| **G1** | `computeOrbIntel()` + rules R1–R13 (R12 file-read helper) + stance aggregation + PWH/PWL in orbContext + schema in both type homes + tile restructure (§2.7) + tests (§2.8) + README (bias-engine section gains an "ORB intel" subsection listing the rules table condensed) | `scripts/fetch-uk100-data.ts`, `src/types/uk100.ts`, `src/components/uk100-tiles/Uk100OrbTile.tsx`, `scripts/__tests__/fetch-uk100-data.test.ts`, `xauusd-dashboard/README.md` | 3–4h |
| **G2** | Briefing prompt + output-schema extension, merge of `aiStanceLine`/`aiBullets`, tolerant parsing, max_tokens 1500. Live-verify: with no key locally the fetch must still produce `orbIntel` with `aiStanceLine: null` | `scripts/fetch-uk100-data.ts`, README (one paragraph) | 45m–1h |
| **G3** | TL;DR: skill-doc section + meta field + `save-gold-session.ts` SessionMeta + types + `tldr.ts` + `TldrCard` + AiSubTab wiring + tests (§3.6) | `.claude/commands/uk100-session.md`, `scripts/save-gold-session.ts`, `src/types/uk100.ts`, `src/components/uk100/tldr.ts`, `src/components/uk100/TldrCard.tsx`, `src/components/uk100/AiSubTab.tsx`, new test file | 1.5–2h |

Gold is untouched in all three phases. `orbIntel` is UK100-only.

## 5. Non-goals / deferred

- No new Anthropic API call (reuse the briefing call).
- No porting of the Python ICT structure engine to TS (F-C).
- No base-rate numbers until Phase E's backtest exists (`baseRateNote` stays null; F-D).
- No TL;DR on the gold tab (do it there later only if this lands well).
- Rendering the full `briefing` paragraph on the UK100 Macro tab remains an open, separate
  item (F-B) — G2 partially addresses it via the tile; a dedicated briefing panel is NOT in
  scope here.
