# Two additions I think matter more than compression

Shortening the brief is the obvious fix. These two are the ones I'd actually
fight for — they change what the brief *is*, not just how long it is.

---

## 1. Pre-staged triggers, not just a bias

Right now the brief says "bearish, strategy 2, here are 16 levels." It stops
one step short of what you actually do at 09:15, which is **wait for a specific
thing to happen at a specific price.**

Both your strategies are trigger-based. So pre-stage them:

```
▶ PRIMARY — short (with bias)
  WAIT FOR  sweep of 29452 PDH  →  1m CISD  →  lower high
  ENTER     on the LH break
  STOP      above the sweep wick (~29470)
  TARGET 1  29327 flip        (+125, 2.5R)
  TARGET 2  29182 put wall    (+270 — needs 270 of a 156pt budget:
                               PARTIALS ONLY, don't plan on it)
  KILL      1m close back above 29470

▶ SECONDARY — short continuation (S2, no sweep needed)
  WAIT FOR  1m CISD down  →  LH  →  new LL  →  fib the leg
  ENTER     OTE 0.62–0.79 of that leg
  STOP      beyond 0.79
  TARGET    29182

▶ FLIP — what kills the bearish case
  1m close and HOLD above 29327 (gamma flip)
  → regime turns long-gamma, S1 fades become valid again
  → then longs at 29275 / 29201, target 29382
```

**Why this matters:** it converts "here is data" into "here is the plan," and
it pre-computes the R:R so you're not doing arithmetic while price is moving.
It also makes the fuel budget bite — notice Target 2 above is flagged as
unreachable inside today's remaining 156pt budget. That's exactly the
stop-management problem you asked for, caught *before* you enter rather than
halfway through the trade.

---

## 2. What changed since the last run

We run 4× a day. Runs 2, 3 and 4 shouldn't make you re-read everything — they
should lead with the diff:

```
Δ SINCE 09:15 ET (4h ago)
  ✔ 29452 PDH SWEPT at 10:42 — failed, LH printed. S1 short triggered.
  ↓ gamma flip 29327 → 29290 (dealers repositioned lower)
  ⛽ fuel 67% → 84% LOW_FUEL — tighten, BE at 0.7R now
  ✚ new level: 29418 post-sweep high, now the nearest pool above
  ○ bias unchanged −6
```

Five lines instead of eight screens. On the mid-NY and EOD runs this is
probably *all* you need — the full brief only matters at the pre-open run when
you have no prior context.

This needs the archive we're already building for Phase 4, so it costs almost
nothing extra.
