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
| **1** | Research: find, test and prove data sources; design the models | ✅ **Complete** — `PHASE1-FINDINGS.md` |
| **2** | Build the agent skill | ✅ **Complete** — skill, slash command and sub-agent all live |
| **3** | Refine information selection and output presentation | ✅ **Complete** — level board 30→12 rows, plain-English regime, collapsed scoring |
| 4 | Continuous improvement against the logged archive | 🔄 **Running.** 1 trading day logged. Open questions tracked in `journal/HYPOTHESES.md`; `scripts/track.py` prints the evidence table. Nothing changes below 3 sessions |

## Where it lives

| What | Path |
|---|---|
| The skill | `.claude/skills/nas100-daily-brief/` |
| Slash command | `/nas100-brief` (`.claude/commands/nas100-brief.md`) |
| Background reviewer | `.claude/agents/brief-reviewer.md` |
| Scripts (canonical) | `.claude/skills/nas100-daily-brief/scripts/` |
| Journal (committed) | `journal/<trading-day>/` |
| **Full build documentation** | **`docs/00-BUILD-FROM-SCRATCH.md`** |

## Using it

```
/nas100-brief              full brief + background review of the last session
/nas100-brief quick        brief only, no reviewer
/nas100-brief levels       just the level board and stop-management line
/nas100-brief review       skip the brief, run the retrospective now
```
Or just ask: *"what's the bias on NAS100"*, *"nas100 scan"*, *"mark the levels"*.

---

## Quick start (Phase 1 prototypes)

Everything runs today. `CTRADER_MCP_SLUG` must be in the environment for the
cTrader level engine (it already is in this repo's sessions). `FRED_API_KEY`
is optional — it adds the real-rate/credit/liquidity layer, and the brief says
so out loud if it's missing. See `SETUP-SECRETS.md`.

```bash
cd .claude/skills/nas100-daily-brief/scripts

python3 source_health.py        # probe all 28 sources, PASS/FAIL + latency
python3 brief.py                # the full brief, markdown
python3 brief.py --json         # the full structured payload

python3 levels_fuel.py          # levels + ADR fuel gauge only
python3 gex_levels.py 29290.5   # gamma board only (pass your CFD price)
python3 macro_probe.py          # macro / vol / calendar / news only
python3 bias_engine.py          # the bull/bear score with full reasoning
python3 fred_probe.py           # real yields, credit, financial conditions, Fed liquidity
python3 news_scorer.py          # headline pre-filter -> NAS100 reaction mapping
python3 test_news_scorer.py     # 22 regression cases for the pre-filter
python3 review_day.py           # grade a past day against real bars
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
- **31 of 32 candidate sources are live**, and the core brief needs **no keys
  at all**. The one optional free key (FRED) adds real yields, credit spreads,
  financial conditions and Fed liquidity. Full registry with latencies and the
  rejected list in `research/02-data-sources.md`.
- **Real yields beat nominal yields for predicting tech.** A 10y move is either
  a real-rate move (direct multiple compression) or a breakeven move (softer,
  slower, more likely to retrace). The brief decomposes every move.
- **Raw data is ~13 MB (~3.4M tokens); the reduced payload is ~8 KB (~2.5k
  tokens)** — a ~1,400:1 reduction that has to happen in a script, never in
  context.

---

## Reading order

1. `PHASE1-FINDINGS.md` — the summary, the action items, and the API keys worth
   signing up for
2. `examples_brief.md` — what the output actually looks like
2b. `SETUP-SECRETS.md` — where the two environment variables go
3. `research/05-levels-and-strategy-map.md` — the level board mapped to your
   two setups
4. `research/03-gex-oi-levels.md` — what each gamma level means and how to
   trade it
5. `research/06-range-and-fuel.md` — fuel, and the stop-management rules it
   drives
6. `research/08-phase2-architecture.md` — how Phase 2 should be built
7. `research/09-news-sentiment-replacement.md` — why we replaced Alpha Vantage
   with a pre-filter rather than another sentiment API
8. `research/10-journal-and-review-loop.md` — journal, grading, session awareness
9. **`docs/00-BUILD-FROM-SCRATCH.md`** — the complete build record: every source,
   decision, rejected option and bug. Enough to rebuild this from an empty repo

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
