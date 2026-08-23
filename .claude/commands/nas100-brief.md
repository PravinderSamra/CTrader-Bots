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
| `review` | `review_day.py` | Report it in the foreground; no brief |

Every mode is a flag on an existing script. **Never hand-assemble the output** —
the renderer is the agreed format and re-extracting it makes it drift.

Invoke the skill and follow its SKILL.md. Deliver the brief before doing
anything else — the reviewer runs after, in the background, and must never
delay it.
