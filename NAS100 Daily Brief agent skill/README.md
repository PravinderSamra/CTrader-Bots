# NAS100 Daily Brief — Agent Skill

A daily intelligence brief for intraday NAS100 day trading: macro, dealer
gamma (GEX/OI), news, the level board to mark on the chart, a directional
opinion, and the range/fuel budget that tells you how actively to manage a
stop.

Built for two specific setups:
1. **Sweep → failed re-break → CISD reversal** (1m)
2. **CISD → HH/HL → fib OTE continuation** (1m)

The brief's job is not just to hand you levels — it is to tell you **which of
those two strategies is the right tool today**, because that is decided by the
dealer-gamma regime, not by the chart.

---

## Status

| Phase | Scope | State |
|---|---|---|
| **1** | Research: find, test and prove data sources; design the models | ✅ **Complete** — see `PHASE1-FINDINGS.md` |
| 2 | Build the agent skill (repo-hosted, scheduled pre-compute) | Not started — plan in `research/08-phase2-architecture.md` |
| 3 | Refine information selection and output presentation | Not started |
| 4 | Continuous improvement against the logged archive | Not started |

---

## Quick start (Phase 1 prototypes)

Everything runs today, no API keys. `CTRADER_MCP_SLUG` must be in the
environment for the cTrader-based level engine (it already is in this repo's
sessions).

```bash
cd "NAS100 Daily Brief agent skill/prototypes"

python3 source_health.py        # probe all 28 sources, PASS/FAIL + latency
python3 brief.py                # the full brief, markdown
python3 brief.py --json         # the full structured payload

python3 levels_fuel.py          # levels + ADR fuel gauge only
python3 gex_levels.py 29290.5   # gamma board only (pass your CFD price)
python3 macro_probe.py          # macro / vol / calendar / news only
python3 bias_engine.py          # the bull/bear score with full reasoning
```

`examples_brief.md` is a real brief generated from live data on 2026-08-22 —
not a mock-up.

---

## Key facts established in Phase 1

- **CBOE publishes the full NDX and QQQ option chains — open interest *and*
  greeks — free, keyless.** This is the same upstream data the paid GEX vendors
  resell. No subscription needed.
- **cTrader NAS100 = symbolId 116** (`US100`/`USTEC`/`NDX100` do not resolve).
  Timeframes use the underscore form; daily bars roll at 21:00 UTC.
- **27 of 28 candidate sources are live and keyless.** The full registry, with
  latencies and the rejected list, is in `research/02-data-sources.md`.
- **Raw data is ~13 MB (~3.4M tokens); the reduced payload is ~8 KB (~2.5k
  tokens)** — a ~1,400:1 reduction that has to happen in a script, never in
  context.

---

## Reading order

1. `PHASE1-FINDINGS.md` — the summary, the action items, and the API keys worth
   signing up for
2. `examples_brief.md` — what the output actually looks like
3. `research/05-levels-and-strategy-map.md` — the level board mapped to your
   two setups
4. `research/03-gex-oi-levels.md` — what each gamma level means and how to
   trade it
5. `research/06-range-and-fuel.md` — fuel, and the stop-management rules it
   drives
6. `research/08-phase2-architecture.md` — how Phase 2 should be built

---

## Design commitments

- **No silent staleness.** Every source is stamped with its own `as_of`, and
  the brief says out loud when it is running on a fallback or on cached data.
- **Every opinion is traceable.** The bias score prints each component's
  contribution and reasoning, so a wrong call can be traced to the rule that
  caused it — and fixed.
- **Honest confidence.** "NEUTRAL / TWO-WAY — no edge today" is a valid and
  expected output. The brief does not manufacture setups.
- **Deterministic where possible.** Numbers come from scripts; the model adds
  judgement and presentation on top, and never re-derives what code can
  compute exactly.
