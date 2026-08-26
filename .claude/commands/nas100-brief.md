---
description: NAS100 daily brief — bias, gamma levels, fuel and stop management
argument-hint: "[full | quick | review | levels] (optional)"
allowed-tools: Bash, Read, Glob, Grep, Agent, Skill
---

Run the **nas100-daily-brief** skill.

Argument passed: `$ARGUMENTS`

| Mode | Runs | Then |
|---|---|---|
| *(none)* / `full` | `brief.py` | Spawn `brief-reviewer` in the background if a completed unreviewed day exists |
| `quick` | `brief.py` | Nothing — no reviewer |
| `levels` | `brief.py --levels` | Nothing |
| `chart` | The gamma chart on its own (every other mode already includes it) |
| `retro` | A past scan's levels drawn against what price actually did — how well the published levels held |
| `review` | `review_day.py` | Report it in the foreground; no brief |

Every mode is a flag on an existing script. **Never hand-assemble the output** —
the renderer is the agreed format and re-extracting it makes it drift.

Invoke the skill and follow its SKILL.md. **Always deliver the brief as a file via SendUserFile** — bash output is not reliably visible to the user, so a scan that only prints to the tool result has delivered nothing. Deliver the brief before doing
anything else — the reviewer runs after, in the background, and must never
delay it.


## Every scan returns two files

1. **`NAS100-brief-<stamp>.md`** — the written brief
2. **`NAS100-gamma-<stamp>.svg`** — the per-strike call/put wall chart

Both, every time, in one `SendUserFile` call with `display: "render"`. A scan
that returns only the markdown is incomplete. If the chart fails, send the brief
and say so.
