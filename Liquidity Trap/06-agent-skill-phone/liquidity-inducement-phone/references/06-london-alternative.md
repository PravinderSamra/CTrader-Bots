# 06 — The London Alternative Idea

The model is written for New York. Gate 5 exists because that is the session
the doctrine was built and tested on. **This does not mean a London setup is
untradeable — it means the skill must not present one as if it carried the same
evidence.** You are London-based; you want to see the setup and judge it
yourself. So produce it, label it honestly, and let the decision be yours.

## When to produce it

On **every** scan, alongside the primary. Not only when the session is London —
because the London levels are worth marking before the session, and worth
reviewing after.

The London window is `session.label == "LONDON_AM"` (08:00–11:00 London,
DST-correct from the analyzer — never hand-convert). The pools and sweeps are
computed the same way; only the framing and the confidence differ.

## What the evidence actually says

Be straight about this every time, briefly:

- Replaying 22 sessions under the live rules, London morning produced a filled
  setup on **7 of 22 days**, against NY's 6 of 22. Comparable frequency, **no
  demonstrated edge either way.**
- Resolved-trade counts were single-digit per window. That is not an edge test,
  and an earlier looser version of the same study produced a *positive* London
  result that did not survive proper entry rules.
- So: **the London idea is a marked-up setup, not a validated one.** Treat its
  confidence as lower than the NY primary even when the structure looks better.

Do not restate all of that every scan — one clause is enough, e.g. *"London alt
(unvalidated window — comparable frequency to NY, no proven edge)."*

## How to build it

Identically to the primary (references 01–05), with no relaxation of the gates:

1. Confirmed, unswept pool in the target direction.
2. A real trap — `recent_sweep` with `still_valid: true`, ideally naming a
   `pool_taken`.
3. A liquidity block behind the entry; quote `entry_zone` and `stop_beyond`.
4. Target = the opposing confirmed unswept pool, scoped against
   `remaining_budget` — and if it is far, taken as direction with the
   management plan from reference 05.
5. The same RR floor.

**Gate 5 is the only rule relaxed, and it is relaxed explicitly, not silently.**
If any *other* gate fails, the London idea is "no setup" exactly as the primary
would be. Never lower the bar to manufacture something to show.

## How to present it

A third block after PRIMARY and SECONDARY:

```
LONDON ALT (unvalidated window — no proven edge vs NY):
  Trigger : sweep of <low>–<high>  (pool: <name>, <n> touches)
  Entry   : <entry_zone low>–<high>
  Stop    : <stop_beyond>
  Target  : <zone low>–<high>  (<n> pts = <x>% of remaining budget)
  Manage  : <trail/partial plan per reference 05>
  State   : ARMED / WATCHING / NO-SETUP — <reason>
```

If there is no London setup, say so in one line — `LONDON ALT: no setup (no
sweep in the London window)` — rather than omitting the block. Its absence
should be visible, so the journal records the day as "looked, found nothing"
rather than "never checked."

## It gets journalled like everything else

Every London alternative is logged with `kind: "london_alt"` (reference 07), so
that after enough sessions the question "does London actually work for me"
becomes answerable from your own recorded ideas rather than from a replay whose
assumptions I chose.
