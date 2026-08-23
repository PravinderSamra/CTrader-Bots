---
description: NAS100 daily brief — bias, gamma levels, fuel and stop management
argument-hint: "[full | quick | review | levels] (optional)"
allowed-tools: Bash, Read, Glob, Grep, Agent, Skill
---

Run the **nas100-daily-brief** skill.

Argument passed: `$ARGUMENTS`

- *(none)* or `full` — the complete brief, then spawn the background reviewer if
  a completed unreviewed trading day exists.
- `quick` — the brief only. Do **not** spawn the reviewer.
- `levels` — print only the level board and the fuel/stop-management line.
- `review` — skip the brief; run the retrospective review of the last completed
  day in the foreground and report it.

Invoke the skill and follow its SKILL.md. Deliver the brief before doing
anything else — the reviewer runs after, in the background, and must never
delay it.
