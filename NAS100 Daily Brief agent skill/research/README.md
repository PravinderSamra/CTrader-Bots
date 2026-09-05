# Research

Two kinds of material live here.

## Phase 1 — how the brief was built (`01`–`10`)

The source-by-source research behind the shipped product: which feeds were
tested, which were rejected and why, and how each layer was designed. These are
a record of decisions already made.

| Doc | |
|---|---|
| [01-macro-drivers.md](01-macro-drivers.md) | What actually moves the NDX |
| [02-data-sources.md](02-data-sources.md) | Every feed, connection-tested |
| [03-gex-oi-levels.md](03-gex-oi-levels.md) | The CBOE gamma pipeline |
| [04-news-layer.md](04-news-layer.md) | Feeds and filtering |
| [05-levels-and-strategy-map.md](05-levels-and-strategy-map.md) | Levels → the two entry models |
| [06-range-and-fuel.md](06-range-and-fuel.md) | ADR, budget, expansion state |
| [07-bias-engine.md](07-bias-engine.md) | Scoring design |
| [08-phase2-architecture.md](08-phase2-architecture.md) | Skill layout |
| [09-news-sentiment-replacement.md](09-news-sentiment-replacement.md) | Why the paid API went |
| [10-journal-and-review-loop.md](10-journal-and-review-loop.md) | The review discipline |

## Open threads — work that is NOT in the brief

Each gets a method document, a prediction record, and a grading loop that runs
against reality. Same discipline as `journal/HYPOTHESES.md`, applied *before* a
thing ships rather than after.

| Thread | Status | |
|---|---|---|
| **Live wall estimation** — inferring today's open interest from today's volume | Collecting · **0 graded days** | [live-walls/METHOD.md](live-walls/METHOD.md) |
| **Per-strike gamma chart** | **Shipped** | [gamma-chart.md](gamma-chart.md) |
| **tick-stream.xyz** — vendor evaluation | Evaluated, nothing bought | [tickstream/EVALUATION.md](tickstream/EVALUATION.md) |
| **GEXBot** — account held, client built | Additive only; H12/H13 open | [gexbot/EVALUATION.md](gexbot/EVALUATION.md) |

**Nothing in an open thread is promoted into the scan until its accuracy log
earns it.** The estimator writes only to `research/`; the brief does not read it.
