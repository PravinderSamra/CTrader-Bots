# 08 — Phase 2 Architecture: is GitHub actually the token-efficient choice?

You asked me to confirm the GitHub approach rather than assume it. Here is the
honest answer, with numbers.

---

## The measured token problem

| Stage | Size | Approx. tokens |
|---|---|---|
| CBOE NDX chain (raw) | 7.2 MB | ~1,900,000 |
| CBOE QQQ chain (raw) | 5.3 MB | ~1,400,000 |
| Yahoo / calendar / RSS raw | ~0.5 MB | ~130,000 |
| **Raw total** | **~13 MB** | **~3,400,000** |
| Script-reduced JSON payload | ~8 KB | **~2,500** |
| Rendered markdown brief | ~7 KB | **~2,000** |

**The reduction ratio is roughly 1,400:1, and it comes entirely from running a
script over the data — not from where that script runs.** This is the single
most important architectural fact: the model must never see a raw options
chain. It must see the *output* of `gex_levels.py`.

## So: does GitHub save tokens?

**No — not by itself.** Comparing the two execution paths for the same brief:

| | Run scripts in-session | Dispatch a GitHub Action |
|---|---|---|
| Script output into context | ~2,500 tok | ~2,500 tok |
| Orchestration overhead | 1 Bash call (~150 tok) | dispatch + poll + fetch logs (~1,500–3,000 tok, 3–6 tool calls) |
| Latency | 25–60 s | 90–180 s |
| Needs `CTRADER_MCP_SLUG` on device | **yes** | no (uses repo secrets) |

Running in-session is **cheaper and faster**. The reason your Liquidity Trap
phone skill uses the Actions path is **credential portability on a phone**, not
token efficiency — and its own SKILL.md says as much ("zero token on the
phone"). It is the right call there for the right reason; it just isn't a token
argument.

## Where GitHub genuinely wins — and it wins big

1. **Scheduled pre-computation is the cheapest read path of all.**
   A cron workflow that runs the engines at fixed times and commits a small
   `data/NAS100_latest.json` means an on-demand brief is *one file read* —
   ~2,500 tokens, ~2 seconds, and it still works if CBOE is slow or cTrader is
   down. This beats both paths above.
2. **The historical archive builds itself.** Every scheduled run appends
   `data/history/YYYY-MM-DD-HHMM.json`. That archive is the entire foundation
   of Phase 4 — you cannot ask "which bias components actually predicted the
   day" without it, and you cannot retro-fit it later.
3. **Versioned, reviewable analysis logic.** The scoring rules live in code, in
   git, with the reasoning in the commit history. When Phase 4 changes a
   weight, the change is diffable.
4. **The model stops re-deriving.** With the logic in scripts, the model's job
   each run is judgement and presentation — not recomputing gamma. That is
   both cheaper and more reliable.

---

## Recommended architecture

```
.claude/skills/nas100-daily-brief/          <- Claude Code auto-loads this
├── SKILL.md                                <- ~1,200 tokens, always loaded
├── references/                             <- progressive disclosure, on demand
│   ├── 01-reading-the-output.md
│   ├── 02-gamma-levels-playbook.md
│   ├── 03-fuel-and-management.md
│   ├── 04-strategy-selection.md
│   ├── 05-news-interpretation.md
│   └── 06-journal.md
└── scripts/
    ├── ctrader_http.py                     <- shared with the Liquidity Trap skill
    ├── cboe_gex.py
    ├── gex_levels.py
    ├── levels_fuel.py
    ├── macro_probe.py
    ├── bias_engine.py
    ├── brief.py                            <- the one entry point
    └── source_health.py                    <- pre-flight

NAS100 Daily Brief agent skill/             <- this folder: research + archive
├── research/                               <- docs 01-08 (not loaded at runtime)
├── prototypes/                             <- Phase-1 working code
└── data/
    ├── NAS100_latest.json
    └── history/YYYY-MM-DD-HHMM.json

.github/workflows/nas100-brief.yml          <- cron + workflow_dispatch
```

### Three execution paths, in preference order

1. **Cached (cheapest).** Read `data/NAS100_latest.json`. Use when it is
   < 45 minutes old. ~2,500 tokens, ~2 s.
2. **Local live (freshest).** `cd scripts && python3 brief.py --json`. Use when
   the cache is stale and `CTRADER_MCP_SLUG` is in the environment (it is, in
   this repo's sessions). ~2,650 tokens, ~40 s.
3. **Workflow dispatch (phone / no credentials).** Dispatch
   `nas100-brief.yml`, read the JSON between `===BRIEF_START===` and
   `===BRIEF_END===` in the job log. Mirrors the proven Liquidity Trap phone
   path. ~4,000 tokens, ~150 s.

The SKILL.md should encode exactly this fallback ladder, and **say out loud in
the brief which path it used and how old the data is**.

### Suggested cron schedule (UTC)

| Time | Purpose |
|---|---|
| 06:00 | Pre-London brief — overnight Globex range, Asia levels, calendar |
| 12:00 | Pre-NY brief — London range complete, refreshed gamma before the 13:30 data window |
| 17:00 | Mid-NY refresh — 0DTE gamma drift, fuel consumed, management update |
| 20:15 | End-of-day snapshot — for the Phase-4 archive only, no notification |

Note GitHub's cron is best-effort and can run several minutes late; nothing in
the design should depend on exact firing times.

---

## Progressive disclosure — the other real token lever

SKILL.md is loaded on **every** invocation, so it must stay small (~1,200
tokens): the run ladder, the non-negotiable gates, and pointers. The detailed
playbooks in `references/` are loaded only when the model actually needs them —
exactly the pattern your Liquidity Trap skill already uses with its
`references/01`–`07`. Doc 03's gamma playbook, for instance, is ~2,000 tokens
and is only needed when the brief is annotating gamma levels.

**Steady-state cost of a full brief: roughly 5,000–6,000 tokens**
(SKILL.md + one or two references + the reduced data payload) against
~3,400,000 tokens of underlying raw data.

---

## Two housekeeping items for `.mcp.json`

Neither blocks Phase 2, both should be cleaned up:

1. **`newsmcp` is dead** — the server returns HTTP 410. Remove the entry.
2. **`tavily` and `alpha-vantage` hold literal placeholder keys**
   (`YOUR_TAVILY_API_KEY`, `YOUR_API_KEY`) and fail on every call. Either
   supply real keys or remove them so they stop failing silently at startup.

The brief has **no dependency on any of the three** — every source it uses is
keyless.
