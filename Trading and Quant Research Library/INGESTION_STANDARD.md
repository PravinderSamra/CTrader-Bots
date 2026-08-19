# Ingestion Standard

The contract every entry in this library must satisfy. It exists so that entries produced in
different waves, by different agents, remain comparable and machine-readable.

## 1. Admission criteria

An entry is admitted only if **all** of the following hold:

1. **Primary source exists and is public.** A paper (arXiv, SSRN, journal, university repository),
   an open-source repository, or a documented public dataset. A paywalled journal version is
   acceptable only if a public preprint or working-paper version is linked.
2. **Stated sample.** The source names its data: instruments, date range, frequency, provider.
   "Backtested on years of data" is not a sample.
3. **Reproducible rule.** The entry/exit logic can be written down as deterministic pseudo-code.
   Discretionary judgement calls disqualify.
4. **Reported results.** Risk-adjusted performance, or a statistical test with a test statistic.
   A price chart with arrows is not a result.
5. **Mechanism.** A stated reason the edge should exist — risk premium, structural constraint,
   behavioural bias, or liquidity provision. "It works" is not a mechanism.

## 2. Rejection criteria (automatic)

- Get-rich-quick framing, signal-selling, or performance claims with no drawdown disclosure.
- Indicator mysticism: harmonic patterns, Gann/Elliott-style geometry, "market maker algorithms"
  presented without order-book data.
- Backtests with look-ahead bias, survivorship-biased universes, or in-sample parameter selection
  presented as out-of-sample results — unless ingested *specifically* as a documented failure case
  and tagged `evidence_grade: "rejected-case-study"`.
- Any result that cannot be traced to a named data source.

## 3. Citation discipline (the rule that makes this library worth having)

**Every numeric performance claim must be read out of the primary source.** Not recalled, not
taken from a secondary summary, not inferred from a chart. If a figure could not be verified
against the source document, it is either omitted or written as `NOT REPORTED IN SOURCE`.

Each `backtest_and_data_summary.md` carries a **Verification** block naming the exact document
consulted and which table or page the numbers came from. An entry whose numbers were not
confirmed against the source is marked `evidence_grade: "unverified"` and does not count as
ingested.

## 4. Required files

| File | Purpose | Hard requirements |
|---|---|---|
| `research_paper_or_source.md` | The edge and why it exists | Abstract/summary, source links, mathematical foundation, mechanism, known criticisms |
| `backtest_and_data_summary.md` | The evidence | Reported metrics with citations, data sample, cost treatment, thrives/fails regimes, decay status |
| `source_or_pseudo_code.txt` | The implementation | Runnable reference code or fully specified pseudo-code; explicit parameters; no hidden lookahead |
| `metadata.json` | Machine filtering | Must validate against `_schema/metadata.schema.json` |

## 5. `metadata.json` required fields

Mandated by the project brief:

- `strategy_type` — string, matches a category slug in `TAXONOMY.md`
- `asset_classes` — array of strings
- `complexity_score` — integer 1–10 (see rubric below)
- `execution_type` — one of `Manual`, `Mechanical`, `Quant`
- `requires_machine_learning` — boolean

Added by this library for downstream automation: `id`, `title`, `slug`, `sources`,
`evidence_grade`, `holding_period`, `data_requirements`, `capacity`, `decay_status`,
`related_strategies`, `tags`, `ingested_at`.

### Complexity rubric (1–10)

| Score | Meaning |
|---|---|
| 1–2 | Single-instrument rule computable by hand from daily bars |
| 3–4 | Multi-instrument, vectorised daily data, standard statistics |
| 5–6 | Cross-sectional or spread construction; rolling estimation; careful cost modelling |
| 7–8 | Stochastic control, continuous-time modelling, or intraday state management |
| 9–10 | Full low-latency infrastructure, order-book reconstruction, or co-located execution |

`complexity_score` scores **implementation difficulty of a faithful replication**, not the
sophistication of the mathematics.

## 6. Evidence grades

| Grade | Meaning |
|---|---|
| `verified-primary` | Every figure read from the primary source document in-session |
| `verified-secondary` | Figures from a credible replication, primary source unavailable |
| `unverified` | Not yet checked — never a completed ingestion |
| `rejected-case-study` | Ingested as a documented failure/cautionary example |
