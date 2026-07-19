# 00 — Index: Liquidity Trap Strategy Documentation

Complete documentation of the "Liquidity Trap" / "Da Vinci model" trading strategy, extracted from three YouTube source videos and organized for a future reader (human or AI) to become expert in the strategy — and ultimately to implement it as a cTrader bot.

## Source material

All claims in these docs cite transcripts in `../01-transcripts/` as `(Video N, [MM:SS])`:

- **Video 1 (V1)** — `video1_transcript.md` — Chart Fanatics ep. 1 with **Marco Trades** (the strategy's author): whiteboard theory, four chart examples, and a full live NQ trading session (Aug 2025).
- **Video 2 (V2)** — `video2_transcript.md` — Chart Fanatics ep. 2 with Marco, 11 chapters: names and formalizes the setup as the **"Da Vinci model"**, adds the engineered-liquidity arming condition, gold/NQ/USDJPY examples (Jul 2026).
- **Video 3 (V3)** — `video3_transcript.md` — Inter Equity Trading: an independent-in-name 16-minute NQ walkthrough using Marco's exact vocabulary and rules on 4H/1H only (Jan 2026).

Chart screenshots for resolving visual ambiguities live in `../03-images/` (Video3 complete: 28 shots + manifest; Video2 complete: 36 files; Video1 pending).

## The nine files

| File | One-line summary |
|---|---|
| `00-index.md` | This file — map of the doc set and how to use it. |
| `01-liquidity-fundamentals.md` | What liquidity is (resting stop orders), why pools form (inducement), the core respect-and-move-away rule that separates real liquidity from empty highs/lows, liquidity blocks, internal vs external, fractality. |
| `02-identifying-and-marking-liquidity.md` | The procedural chart-marking method: timeframe stack, the catalogue of qualifying levels (and explicit non-levels), the step-by-step marking procedure, the bias-lockout rule, and a pre-trade checklist. |
| `03-the-liquidity-trap-setup.md` | **The most important file.** The full entry model: five arming preconditions, the sweep trigger, structural stop rules, pool-based targets, invalidation/re-arm logic, and a table of all ten worked examples with RRs. |
| `04-trade-management-and-risk.md` | Position sizing, stop rolling/break-even, partials, scale-ins, session/news filters, instruments, and the (unverified) frequency/win-rate/money claims. |
| `05-cross-video-synthesis.md` | Agreement matrix across the three sources, the genuine divergences (BE trigger, partial size, timing), and a clearly-labeled analysis of which rules carry the edge vs which are cosmetic. |
| `06-glossary.md` | Every strategy-specific term defined with sources: core concepts, the many sweep synonyms, chart color conventions, execution terms, an ICT-vocabulary translation map, and auto-caption artifacts. |
| `07-open-questions-pending-visuals.md` | Catalogue of "here / this level / like this" moments the audio alone can't resolve, per video with timestamps, plus the cross-cutting parameter unknowns (respect tolerance, zone heights, stop buffers) and non-visual open questions. |
| `08-bot-blueprint-outline.md` | High-level algo design: data/timeframe requirements, the level-registry state machine, `IdentifyLiquidityPool()` and `DetectSweepAndReversalConfirmation()` specs, entry/stop/target math, build phases, and the 12 design decisions the user must make before coding. |

## How to use this documentation (cold start)

**If you are picking this up with zero context**, read in this order:

1. **01 → 02 → 03** — this is the strategy itself, in dependency order (concepts → identification → trade rules). File 03 is the executable core; files 01–02 define every term it uses.
2. **04** — management/risk layer and which claims are marketing.
3. **05** — before trusting anything, read the relationship note (V3 is *not* an independent confirmation) and §3's load-bearing-vs-cosmetic assessment.
4. **06** — keep open as a reference; the transcripts use ~8 synonyms for "sweep" and inconsistent box colors, and the glossary normalizes all of it. §8 lists caption artifacts so you don't chase phantom terms ("Molly", "VOS", "frapple").
5. **07 + 08** — only when moving toward implementation.

**Rules for working with this doc set:**

- **Citations are the contract.** Every concrete rule carries a `(Video N, [MM:SS])` pointer into `../01-transcripts/`. If you extend these docs, keep that convention; if a claim has no citation, treat it as analysis, not source material.
- **Don't hallucinate beyond the sources.** The transcripts are the ground truth. Where they are ambiguous, file 07 records the ambiguity instead of papering over it — preserve that discipline. Unquantified parameters (respect tolerance, equal-lows band, stop buffers, risk %) are *genuinely unspecified*, not accidentally omitted.
- **The one-paragraph version of the strategy** (from file 03 §0): the market induces retail entries whose stops build a liquidity pool; price sweeps the pool (the trap), then reverses toward the opposite confirmed pool. You enter the moment the pool is swept — long below swept lows, short above swept highs — with a structural stop behind a no-liquidity extreme (liquidity block) and the opposing pool as target. The two gates that make it a system rather than a pattern: only *market-confirmed* levels count (respect-and-move-away, file 01 §5), and the bias lockout (no longs after a high is taken until the low-side pool is swept, file 02 §D).
- **Pending work:** collect Video1 screenshots into `../03-images/`, resolve file 07's items (Video2's and Video3's are ready now), pin down file 08 §J's twelve decisions with the user, then build the bot in the four phases of file 08 §I — validating the level detector against the screenshots before any order is ever placed.
- **Verification caveat:** all performance figures ($500K+ payouts, "incredible" win rate, the 1:19s) are self-reported on sponsor-funded shows (file 04 §7). Nothing here has been backtested; file 08 Phase 3 exists for that reason.
