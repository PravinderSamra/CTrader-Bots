# UK100 — ORB Intel Journal (flagged vs happened) — Design Spec

**Date:** 2026-07-15 · **Author:** review session (Fable) · **Status:** APPROVED FOR BUILD — execute phases J0→J3 in order.

Same execution rules as `UK100-ORB-INTEL-TLDR-DESIGN.md`: work on
`claude/xauusd-intelligence-dashboard-t5jnzh`; each phase ends `npx tsc --noEmit` +
`npx vitest run` + `npm run build` green (from `xauusd-dashboard/`), a live tokenless
`npx tsx scripts/fetch-uk100-data.ts` run completing without error (discard the generated
snapshot afterwards), then commit → push → fast-forward push to `main`. Stop after any
phase with nothing half-wired. Gold untouched throughout.

---

## 0. The ask, and the design decision

The user asked for "a journal with all the ORB suggestions copied in on the repo in a
file dated to allow future reviews to compare what was flagged vs what actually happened,
to help the AI and agent learn from these findings and adjust" — with licence to pick a
better mechanism if one exists.

**Decision: keep the dated-file journal, but make it machine-readable and
self-scoring** rather than markdown copies of the tile text:

1. **Dated JSON journal** — every hourly fetch appends its full `orbIntel` output (plus
   the market context it was computed from) to `public/data/uk100/orb-journal/YYYY-MM-DD.json`.
   Dated, in-repo, reviewable — exactly the ask.
2. **Automatic resolution** — a resolver (same pattern as `resolve-uk100-sessions.ts`)
   later scores each entry against what price actually did: forward returns, excursions,
   and a deterministic RIGHT/WRONG/FLAT verdict per stance AND per individual signal.
   "Flagged vs happened" becomes a computed field, not a manual diff a future review has
   to reconstruct by hand.
3. **Scoreboard** — aggregated per-stance and per-rule hit rates in one small
   `scoreboard.json`, which is the actual learning artifact: it is what future review
   sessions (and eventually the skill itself) read to retune the R-rule thresholds, the
   provisional European-tape weight, and the bias weights — the recalibration the plan
   docs keep deferring "until there is data". This journal is what creates that data.

Why not markdown copies: the same prose already survives in git history (the snapshot is
committed hourly), but prose can't be aggregated — "R1 fired 14 times, the fade direction
closed favourably 11 times" is the thing that changes behaviour, and only structured
entries can produce it. A human-readable digest can always be generated FROM the JSON
(J3 includes one); the reverse is not true. The per-rule attribution requires one small
schema addition (J0) — signals currently don't say which rule produced them.

Relationship to existing machinery (do not duplicate it):
- `/uk100-session` records + `outcomes.json` (F7) already journal & resolve the **AI
  session's trade calls**. This journal covers the **hourly mechanical/AI ORB intel**,
  which today is overwritten every hour and lost.
- Phase E (`UK100-V2-PLAN.md` §7, unbuilt) is the **backward-looking** ORB backtest.
  This journal is the **forward-looking** live-collected complement — and once it has
  volume, its scoreboard is a legitimate live source for the tile's reserved
  `baseRateNote` field.

---

## 1. Phase J0 — attribute signals to rules (prerequisite, ~20 min)

Add `rule: string` (values `'R1'`…`'R13'`) to `OrbIntelSignal` in BOTH type homes
(`scripts/fetch-uk100-data.ts` script-local + `src/types/uk100.ts`), and set it at every
`signals.push(...)` site in `computeOrbIntel()` (each push corresponds to exactly one
rule; R8/R9/R11/R13 have multiple branches — they all share that rule's id, EXCEPT give
the `preOpenLead` branch of R8 the id `'R8b'` and the COT branch of R11 the id `'R11b'`
so the two genuinely independent sub-signals score separately). The tile UI ignores the
field. Update the G1 tests' fixtures only where TypeScript forces it (the field is on the
OUTPUT type, so existing assertions keep passing; add one assertion that the R1 signal
carries `rule: 'R1'`).

## 2. Phase J1 — write the journal (fetch script, ~1h)

**File layout:** `xauusd-dashboard/public/data/uk100/orb-journal/YYYY-MM-DD.json`
(London calendar date), shape:

```json
{ "date": "2026-07-16", "entries": [ { …entry… }, … ] }
```

**Entry schema** (define `OrbJournalEntry` in the script + mirror in `src/types/uk100.ts`):

```ts
interface OrbJournalEntry {
  at: string                    // ISO timestamp of the fetch run
  londonTime: string            // "HH:MM BST|GMT" (reuse londonTimeLabel)
  mode: OrbContext['mode']
  price: number                 // UK100 mid at publish time
  stance: OrbIntelStance
  stanceLine: string
  signals: OrbIntelSignal[]     // incl. rule ids (J0)
  aiStanceLine: string | null
  aiBullets: string[]
  bias: { score: number; label: string }
  orb: {                        // the context the read was made from
    orbHigh: number | null; orbLow: number | null
    orbBrokenDirection: OrbContext['orbBrokenDirection']
    overnightHigh: number | null; overnightLow: number | null
    priorDayHigh: number | null; priorDayLow: number | null
    gapPct: number | null; adr14: number | null; adrUsedPct: number | null
  }
  outcome: OrbJournalOutcome | null   // written later by the resolver (J2)
}
```

**Writer rules** (new `appendOrbJournal()` in `fetch-uk100-data.ts`, called at the end of
`main()` AFTER the briefing merge so the entry carries the final `aiStanceLine`/`aiBullets`):
- **Skip entirely when `ctrader` is null OR `prices.UK100` is null** (tokenless/local
  runs must not pollute the journal with null-price entries) — log "ORB journal: skipped
  (no live price)".
- Read-modify-write the day file (create with `{date, entries: []}` if absent),
  `mkdirSync(recursive)` the dir, append one entry per run unconditionally (hourly cadence
  ≈ 14 entries/day; ~2–3 KB each — no dedup needed, the full hourly record is the point).
- Never prune (calibration archive, like `outcomes.json`). One file per day keeps each
  small and the dated-review workflow trivial (`git log -- …/2026-07-16.json`).
- No workflow change needed: the existing "Commit updated snapshot" step already stages
  all of `public/data/`.
- Tests: extract the append logic as a pure function
  `appendJournalEntry(existing: OrbJournalDay | null, entry: OrbJournalEntry): OrbJournalDay`
  and unit-test create-new-day / append-to-existing / preserves-prior-entries.

## 3. Phase J2 — resolve the journal (new script, ~2h)

New `xauusd-dashboard/scripts/resolve-orb-journal.ts`, copying
`resolve-uk100-sessions.ts`'s conventions exactly (CTraderClient, no-token = clean no-op,
`--dry` flag, direct-invocation guard, UK100 H1 bars, a local `cashCloseCutoffMs`).

For each journal file within the last 21 days, for each entry with `outcome: null`:
- **Scoring window:** `entry.at` → `min(entry.at + 8h, same-day 16:30 London)`.
- If the entry was published **within 30 min of the 16:30 close or after it** → terminal
  `{ verdict: 'UNSCORABLE' }` (no meaningful window; POST_CLOSE runs land here).
- Else if `now` < window end → leave `null`, retry next run (same "don't finalise a
  premature outcome" rule as the session resolver).
- Else fetch H1 bars over the window and compute:

```ts
interface OrbJournalOutcome {
  resolvedAt: string
  fwd1hPct: number | null       // close of the bar ~1h after entry vs entry price
  fwd3hPct: number | null       // ~3h after (null when the window is shorter)
  toClosePct: number            // last in-window close vs entry price
  maxUpPct: number              // max high excursion above entry price in-window
  maxDownPct: number            // max low excursion below entry price (negative)
  verdict: 'RIGHT' | 'WRONG' | 'FLAT' | 'UNSCORABLE' | null
  signalVerdicts: { rule: string; verdict: 'RIGHT' | 'WRONG' | 'FLAT' }[]
}
```

**Deterministic verdict rules** (pure exported function, unit-tested):
- Directional stances — `LONG_FAVOURED` (and `FADE_FAVOURED` whose R1 signal is
  `FAVOURS_LONG`): `toClosePct ≥ +0.15` → RIGHT, `≤ −0.15` → WRONG, else FLAT. Mirrored
  for the short side.
- `BREAKOUTS_SUSPECT` and `MIXED`: `verdict: null` — not a directional call. The
  excursion fields carry the analysable content (see scoreboard's no-extension rate).
- **Per-signal verdicts** (`signalVerdicts`, one per signal in the entry):
  `FAVOURS_LONG`/`FAVOURS_SHORT` signals get the same ±0.15% toClose test;
  `BREAKOUT_SUSPECT` signals get RIGHT when `maxUpPct < 0.25 AND |maxDownPct| < 0.25`
  (breakouts indeed went nowhere), WRONG when either excursion ≥ 0.40, else FLAT;
  `NEUTRAL` signals are skipped. This per-rule ledger is the core learning input.

**Scoreboard** — after resolving, regenerate
`public/data/uk100/orb-journal/scoreboard.json` from ALL resolved entries (full history,
never windowed):

```json
{ "updatedAt": "...", "entriesScored": 123,
  "byStance": { "FADE_FAVOURED": { "n": 14, "right": 9, "wrong": 3, "flat": 2, "avgToClosePct": 0.21 }, ... },
  "byRule":   { "R1": { "n": 14, "right": 11, "wrong": 2, "flat": 1 }, "R4": { ... }, ... },
  "breakoutsSuspect": { "n": 22, "noExtensionRate": 0.64, "avgMaxUpPct": 0.19, "avgMaxDownPct": -0.22 } }
```

**Workflow:** one new step in `xauusd-daily-fetch.yml` directly after "Resolve
uk100-session outcomes", `continue-on-error: true`, same two cTrader secrets, running
`npx tsx scripts/resolve-orb-journal.ts`. The commit step already stages the outputs.

**Tests:** verdict rules (both directions, FLAT band edges, UNSCORABLE timing,
BREAKOUT_SUSPECT signal thresholds 0.25/0.40), scoreboard aggregation from a fixture set,
and window-not-complete → stays null.

## 4. Phase J3 — close the learning loop (~45 min)

1. **Skill doc** (`.claude/commands/uk100-session.md` STEP 8): add one instruction —
   fetch `https://pravindersamra.github.io/CTrader-Bots/xauusd-dashboard/data/uk100/orb-journal/scoreboard.json`
   alongside the macro snapshot (best-effort; skip silently if 404/empty) and, **only for
   rules/stances with `n ≥ 20`**, cite the measured rate in the ORB PLAYBOOK reasoning
   (e.g. "journal: FADE_FAVOURED has closed favourably 9/14 since 2026-07-16 — small n,
   weight accordingly"). Below n=20, say nothing — never quote small-n rates as edge.
2. **Review-session handshake:** add a line to the journal section of the README (below)
   noting that periodic review sessions (the `UK100-SESSION-REVIEW-*` pattern) should
   read `orb-journal/` + `scoreboard.json` as primary evidence when retuning the R-rule
   thresholds, the PROVISIONAL `europeanTapeWeight`, and the bias weights — replacing
   priors with measured rates, the discipline every plan doc defers to "once there is data".
3. **Digest CLI (small):** `npx tsx scripts/orb-journal-digest.ts [YYYY-MM-DD]` — prints
   a markdown table of that day's entries (time, stance, top signal, verdict, toClose%)
   for humans; no workflow wiring, on-demand only.
4. **README:** an "ORB intel journal" subsection under the ORB intelligence section:
   file layout, entry/outcome schemas condensed, verdict thresholds, the n≥20 rule, and
   the statement that `baseRateNote` may be populated from the scoreboard once
   `entriesScored ≥ 100` (a later change, not part of J3).

## 5. Non-goals

- No UI in this pass (a scoreboard card can come later once there's data worth showing).
- No auto-tuning: the journal informs *reviewed* threshold changes, it never mutates
  weights programmatically.
- No gold journal.
- `baseRateNote` population deferred until `entriesScored ≥ 100` (see J3.4).

## 6. Related outstanding items (from the G-phase review — for a future session)

- **F-B (briefing paragraph still rendered nowhere in full):** G2 put the briefing call's
  ORB synthesis on the tile, but the 200–300-word paragraph itself remains unrendered.
  Correction: new `Uk100BriefingCard` consuming `snapshot.briefing` (paragraph +
  `confidence`/10 + `generatedAt` freshness label), rendered as a full-width row directly
  under the `biasRow` in `Uk100Tab.tsx`'s macro sub-tab; null-safe ("briefing unavailable"
  when the key was absent). Reuse gold's `BriefingPanel` only if its prop type already
  matches `Uk100Briefing` — otherwise a small dedicated card, do not fork gold's component.
- **F-D (no measured base rates):** unchanged; corrected properly by Phase E
  (`UK100-V2-PLAN.md` §7) — and incrementally by this journal's scoreboard (J3.4).
