# Phase 3 — Output format options  ⚠️ HISTORICAL

> **These are the options considered, not the format shipped.** The brief was
> refined in place instead: scoring table collapsed, regime written in plain
> English with the technical read above it, level board cut from 30 rows to 13
> and merged by price, wall strength by gamma force, plus the corridor read.
>
> **For the shipped format see `../examples_brief.md`** (a real generated brief)
> and `docs/00-BUILD-FROM-SCRATCH.md` §6.7.
>
> Kept as a record of what was weighed and why — the price-ladder idea in
> option A was not adopted, and the trigger/diff ideas in option C are still
> open.

The problem, measured: the current brief is **127 lines ≈ 8 phone screens**.
You read it 15 minutes before the NY open, on a phone. That's the wrong shape.

But "make it shorter" is the wrong goal on its own — the risk is cutting the
thing that stops you taking a bad trade. So the principle here is **layering,
not deletion**: nothing is removed, it's ordered so the decision is on screen 1
and everything else is reference you can ignore.

## The three layers

| Layer | What it answers | Where |
|---|---|---|
| **Decide** | Long or short? Which strategy? Am I gated? How do I manage the stop? | Screen 1 — must never scroll |
| **Mark** | What goes on the chart, and what do I expect at each level? | Screen 2 — the ladder |
| **Why** | Do I believe the call? | Screen 3+ — skipped on a normal day |

## Files

| File | What it is |
|---|---|
| `A-decision-card.md` | ⭐ Recommended. Decision card + price ladder + why |
| `B-terse.md` | Maximum compression, ~15 lines, loses the reasoning |
| `C-additions.md` | Two structural changes I'd argue for regardless of format |

## The compression techniques used

1. **Symbol legend over prose.** Five symbols learned once (🎯 🧲 🚧 ⚡ ⚠️)
   replace a sentence per level. 16 levels × ~20 words = 320 words → 16 lines.
2. **The price ladder.** Levels sorted by price with current price in the
   middle, distance on the right. Spatially matches how you read a chart, and
   makes "what's inside my remaining budget" instantly visible.
3. **Numbers before prose.** `67% ADR · 156pt left · 1.5× hot` beats a
   paragraph saying the same thing.
4. **Three levels, not sixteen, on screen 1.** Ceiling, flip, floor. The other
   thirteen are chart-marking, not decision-making.
5. **Fixed shape every run.** Same layout, same order, every time — so you
   learn where to look instead of reading.

## What must never be cut

- The **event gate**. A stand-aside line is the single highest-value output;
  both your strategies break on a data-print sweep.
- The **fuel → stop-management rule**. It's the thing you specifically asked
  for and it's what stops a winner being given back.
- **Which strategy**. Right direction with the wrong entry model still loses.
- **Staleness / fallback warnings**. A silently stale gamma level is worse than
  no gamma level.
