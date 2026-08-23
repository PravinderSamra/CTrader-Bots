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

> **Built as planned, with one change.** The scripts are NOT duplicated between
> a project folder and the skill — they live only in
> `.claude/skills/nas100-daily-brief/scripts/`, because two copies drift. The
> project folder keeps research, docs, formats and the journal.
> The layout below is the original proposal; see `docs/00-BUILD-FROM-SCRATCH.md`
> §2 for what actually exists.

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

### The schedule (agreed) — anchored to exchange time, not UTC

Each slot is anchored to the session it serves, so it tracks DST automatically.
The UTC columns are what the cron entries actually use.

| Slot | Local anchor | UTC (summer) | UTC (winter) | Job |
|---|---|---|---|---|
| **Pre-London** | 06:00 UK | 05:00 | 06:00 | Overnight Globex range, Asia H/L, the day's calendar and gamma map before London opens |
| **Pre-NY open** | **09:15 ET** | **13:15** | **14:15** | **The one you trade from.** After the 08:30 ET data print, pre-market fully developed, 15 min before the cash open. Catches anything that cropped up overnight or in pre-market |
| **Mid-NY** | 13:00 ET | 17:00 | 18:00 | 0DTE gamma drift, fuel consumed — the stop-management update |
| **EOD archive** | 16:15 ET | 20:15 | 21:15 | Silent. Feeds the Phase-4 archive only |

**This replaces the originally-proposed 12:00 UTC slot.** That one sat *before*
the 08:30 ET print, so its levels were invalidated by the print minutes later.
The 09:15 ET slot is strictly better: it includes the print reaction, and the
06:00 UK brief already carries the day's calendar warning.

### Implementing DST-aware cron on GitHub Actions

GitHub cron is UTC-only and has no DST awareness, so each ET-anchored slot needs
both UTC times registered, with the job deciding whether it is the live one:

```yaml
on:
  schedule:
    - cron: "0 5,6 * * 1-5"      # pre-London   06:00 UK
    - cron: "15 13,14 * * 1-5"   # pre-NY open  09:15 ET
    - cron: "0 17,18 * * 1-5"    # mid-NY       13:00 ET
    - cron: "15 20,21 * * 1-5"   # EOD archive  16:15 ET
  workflow_dispatch:
```

The job exits early when the current run is the wrong side of the DST switch:

```python
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
et = datetime.now(timezone.utc).astimezone(ZoneInfo("America/New_York"))
uk = datetime.now(timezone.utc).astimezone(ZoneInfo("Europe/London"))
SLOTS = {(6, 0): "pre_london_uk", (9, 15): "pre_ny_et",
         (13, 0): "mid_ny_et", (16, 15): "eod_et"}
```
Match on the *local* hour/minute, not the UTC one, and each slot then fires
exactly once per day in both seasons.

GitHub's cron is best-effort and can fire several minutes late; nothing in the
design depends on exact firing times.

### Alternative: Claude Code Routines
Routines are Claude Code's own scheduler and can run a session on a cron without
a workflow file at all. Same UTC-only caveat applies. Worth comparing against
Actions when we build Phase 2 — Actions wins on committing the archive back to
the repo, Routines wins on not needing a workflow or secrets plumbing.

---|---|
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
