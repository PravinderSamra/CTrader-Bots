# Agent Skill: SMC-Prob — Day Trade Mode

**Invoke with**: `/smc-day [SYMBOL] [account=X] [risk=Y%]`

**Install**:
```bash
cp "SMC-Prob/DayTradeSkill.md" ~/.claude/skills/smc-day.md
```

---

## Description

Day-trade variant of SMC-Prob. It uses the **same ICT/SMC structural lens** as the swing skill (`AgentSkill.md` / `/smc-prob`) — HTF bias → LTF entry trigger → confluence scoring — but every parameter downstream of the entry is redefined around one hard constraint: **the position must be opened and closed within a single trading session. No overnight exposure, ever.**

This is *not* a smaller version of the swing skill — it is a structurally different trade. The swing skill hunts for entries that ride to higher-timeframe liquidity pools over days (validated by the 2026-06-07 backtest — see `BUILD-LOG.md`, average winning hold ≈ +5.4R over 1–5 days). This skill instead hunts for entries whose *target, stop, and exit are all realistically reachable before a defined session deadline* — and it has two things the swing skill doesn't:

1. A **session-runway gate** (Step 3) — a hard pass/fail check, not a scored signal — that rejects structurally-clean setups which simply can't complete in the time remaining.
2. A **flatten-by-deadline rule** (Step 5) — the position closes on the clock, not only on price. An open position at the deadline gets closed at market. That is the actual mechanical definition of "day trade," and it is non-negotiable.

If a setup is structurally excellent but fails the runway gate, **say so explicitly and point the user at `/smc-prob` instead** — don't force a day trade out of a swing-shaped setup, and don't silently drop a good read either.

---

## Required MCP Servers

Same as the swing skill — see `AgentSkill.md` "Required MCP Servers" for the full table (`ctrader` primary, `tradingview-mcp` and `newsmcp` optional cross-checks).

---

## cTrader data conventions (critical — do not skip)

Identical to the swing skill — see `AgentSkill.md` "cTrader data conventions" for the full detail (pipettes ÷ `10^5`, explicit `fromTimestamp`+`toTimestamp` on `get_trendbars`, account-type check first). Repeating the two that matter most for THIS mode:

- **Confirm the account's dealing model (spread-bet £/point vs. CFD lots) before sizing anything** — this account is spread-betting (`_SB` instruments, £-per-point staking). Re-verify if a different account connects.
- **Pull intraday data in tight windows** — this mode lives and dies on the current session's structure, so `get_trendbars` calls should be scoped to the last ~1–2 sessions for M15/M5, not the broad multi-week pulls the swing skill uses for HTF context.

---

## Default Watchlist

Reuse the verified `_SB` watchlist from `AgentSkill.md` ("Default Watchlist" table) — same symbols, IDs, and point sizes. No changes needed; the instrument universe is identical, only the trade *shape* differs.

---

## Execution Pipeline

### Step 1 — Setup

- Resolve target instrument(s): single symbol if specified, else the full watchlist.
- **Market-hours check** — identical to the swing skill's Step 1 (compare `get_spot_prices` timestamp to current time; if stale, label "last session" and proceed with reduced/no live conviction — a day trade fundamentally cannot be opened in a closed market, so a stale read here usually means "no trade, market closed" rather than "last session, here's what to watch").
- **NEW — determine and state the session deadline up front.** This single number governs every downstream step. Default deadlines (adjust for the actual current session and instrument's typical liquidity windows; see `AgentSkill.md` "Time Zone Convention" and Kill Zones table for the BST/GMT figures):
  - A setup forming in the **London Kill Zone** (07:00–10:00 BST / 06:00–09:00 GMT) → flatten by **NY open** (~13:00 BST / 12:00 GMT) — don't carry a London-session trade into the regime change of the NY open.
  - A setup forming in the **NY Kill Zone** (12:00–15:00 BST / 11:00–14:00 GMT) or **Silver Bullet** (14:50–15:10 BST / 13:50–14:10 GMT) → flatten by **NY close** (~22:00 BST / 21:00 GMT).
  - A setup forming **outside any kill zone** → score this honestly in Step 4 (it already scores lower for timing) and set the deadline to the end of whichever session is currently active.
  - State the deadline explicitly at the top of the analysis, **in UK local time**: *"Session deadline: flatten by [HH:MM BST/GMT] — N hours/minutes of runway remain."* Every subsequent step is judged against this number.
- Pull each candidate's `description` from `get_symbols` (point size, dealing model) and cache it for the session — same as the swing skill.

---

### Step 2 — HTF Structural Read (Directional Bias)

**Identical to the swing skill's Step 2** — pull 4H and 1H candles, determine market structure (BOS/CHoCH), premium/discount zone, and nearest BSL/SSL.

A day trade taken against the higher-timeframe grain is exactly as undisciplined as a swing trade against it — **HTF bias is still law.** No shortcuts here just because the hold will be shorter.

> Same stop condition as the swing skill: no clear HTF bias → stop here, output "no trade — no HTF bias."

---

### Step 3 — LTF Structural Read + Session-Runway Gate (Entry Trigger)

Only runs if Step 2 produced a directional bias. Pull **15M and 5M** candles (~150 bars each) — and where useful, the current/prior session's range explicitly (Asian/London/NY high-low).

1. **Liquidity sweep check** — same as swing mode (has a recent session swept the prior session's high/low — AMD "Manipulation" phase complete?).
2. **Entry zone scan — INTRADAY SCOPE ONLY.** This is the first real divergence from the swing skill: scan for FVGs/OBs/minor swing points *within the current or immediately-prior session's structure* — not the broader multi-day HTF OB/FVG pool the swing skill draws from. A level that requires a multi-day round trip to fill is a swing setup wearing a day-trade costume; reject it here, don't carry it forward.
3. **NEW — Session-Runway Gate (hard pass/fail, not a scored signal).** Using the instrument's recent intraday velocity (e.g., average true range per hour across the last few comparable sessions), estimate: *is there realistically enough time between now and the session deadline to (a) reach Target 1 and (b) exit cleanly?* 
   - **If no — stop here.** Output "no trade — insufficient session runway" and say so plainly, even if the structural read scores well. Do not let a clean Step 2 read pressure you into presenting a setup that the clock will kill. If the underlying structure genuinely looks strong, say explicitly: *"this read is valid but better suited to swing mode — see `/smc-prob [SYMBOL]`."*
   - **If yes — proceed to grading**, same A/B/C rubric as the swing skill (FVG+OB overlap + correct zone + sweep = A; one of FVG/OB present, correctly zoned = B; counter-zone or no sweep = C).

**Output of this step:** entry zone, grade, sweep status, distance from current price, **and the runway verdict (pass/fail with the reasoning shown)**.

> If no FVG/OB confluence exists in the bias direction within intraday-reachable distance, **stop here** — "no trade — HTF bias present, no LTF entry yet" (same as swing skill; a day trade can't "wait three days" for one to form, so if it doesn't show up THIS session, the call for today is simply "no trade," not a multi-day watch item — see Behavioural Rules on the boundary between modes).

---

### Step 4 — Confluence & Probability Scoring

Same two-axis, max-14 system as the swing skill (`AgentSkill.md` Step 4 — reuse the exact scoring table), with **two re-interpretations specific to this mode**:

- **Kill-zone timing (+1 in the swing skill's table) is functionally closer to mandatory here.** A setup forming outside an active kill zone has even less session runway behind it — weight this mentally as a strong signal toward "fail the runway gate," not just a missed point.
- **Volatility context (ATR, +1) is now load-bearing, not cosmetic.** In the swing skill it answers "is the move not already exhausted." Here it directly answers "does current intraday velocity support completing this round-trip before the deadline" — i.e., it's the same number the Step 3 runway gate just used. Show that working once and reference it here rather than recomputing.

Same thresholds apply: 11–14 = high-probability, 8–10 = moderate (flagged, reduced size), <8 = no trade.

---

### Step 5 — Trade Parameters & Position Sizing

- **Target 1/2 — redefined as INTRADAY liquidity pools.** Nearest reachable-before-deadline pool (current/prior session high or low, LTF FVG/OB, minor swing point) — *not* the HTF BSL/SSL the swing skill targets. These will sit much closer to current price; expect smaller R multiples than the swing skill's backtested 1.5R–9R range as a direct consequence of this constraint. That's not a flaw — it's the trade-off for zero overnight exposure.
- **Stop — same structural principle** (beyond the invalidation point of the OB/FVG/protecting swing), anchored to *intraday* (LTF) structure — naturally tighter than the swing skill's HTF-anchored stops.
- **R:R gate** — same non-negotiable ≥2:1 to Target 1. With both target and stop now intraday-scale, this should still hold; if it doesn't, that's the runway gate's logic confirming itself — the setup isn't a clean day trade.
- **NEW — the flatten rule (this is the mechanical core of "day trade"):** *Flatten by [session deadline] regardless of target progress.* State it in exactly those words in the trade card. An open position at the deadline is closed at market — full stop, no exceptions, no "let it run a bit longer, it's close." This is what actually makes it a day trade rather than a swing trade with a tight stop and good intentions.
- **Position sizing** — identical £/point spread-bet model as the swing skill (see `AgentSkill.md` Step 5 for the full worked example and formula). Show the working.

---

### Step 6 — Trade Card Output

Same format as the swing skill's trade card (`AgentSkill.md` Step 6), with **one mandatory addition** — a session-deadline line immediately under "Trade Parameters":

```
— Trade Parameters —
Entry Zone        : [price range]
Stop Loss         : [price]   (structural — beyond [OB/FVG/swing])
Target 1          : [price]   (+X pips/points) — close 50%
Target 2          : [price]   (+X pips/points) — close remainder
R:R               : ~XR to Target 1
Session deadline  : flatten by [HH:MM UK time (BST/GMT)] — exit regardless of target progress (N hrs runway remaining at entry)
```

If the runway gate fails, use a variant of the swing skill's "no qualifying setup" card that names the specific reason:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SMC-DAY — NO QUALIFYING DAY TRADE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Instrument(s) reviewed : [list]
Reason                 : [No HTF bias / No intraday LTF entry / Insufficient session runway / Score below threshold (X/14)]
Session deadline       : [HH:MM UK time (BST/GMT)] — [N mins/hrs runway remaining]
Recommended re-scan    : [HH:MM UK time (BST/GMT) — ~N min from now] — [trigger], OR "today's runway exhausted — next session: [HH:MM BST/GMT, kill zone]"
Better fit elsewhere?  : [if the structural read is genuinely clean but too slow to resolve intraday — say so and point at /smc-prob]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Computing "Recommended re-scan"** — use the same level-ETA / structure-ETA / session-ETA logic as the swing skill (`AgentSkill.md`, Step 6), stated in UK local time (BST/GMT), but with one extra cap: **the recommendation can never fall after today's session deadline.** If the soonest sensible re-check (by that logic) would land after the flatten-by-deadline time, today's runway can't support a fresh day trade regardless — say so explicitly and recommend the next session's kill-zone open instead (e.g. *"today's runway is exhausted for this setup — recommend re-scanning at tomorrow's London KZ open, ~07:00 BST"*). Don't recommend a same-day re-scan that would itself fail the runway gate on arrival.

---

## ICT/SMC Concepts Glossary

Reuse the swing skill's glossary in full (`AgentSkill.md` — BOS, CHoCH, OB, FVG, Premium/Discount, BSL/SSL, AMD cycle, Liquidity sweep, Kill Zones table) — every concept applies identically here. The only addition this mode needs:

| Term | Meaning |
|---|---|
| **Session deadline / flatten rule** | The defined cutoff time by which an open day-trade position must be closed regardless of price action — the mechanical feature that distinguishes a day trade from a swing trade with a tight stop. Treated as a hard exit trigger, equal in force to the stop loss or target. |
| **Session-runway gate** | A pass/fail check (Step 3) asking whether there is realistically enough time, given the instrument's current intraday velocity, to complete the full round trip (entry → Target 1 → exit) before the session deadline. Failing this gate is a "no trade," independent of how clean the structural read looks. |

---

## Behavioural Rules

All eight behavioural rules from the swing skill apply unchanged (`AgentSkill.md` — HTF bias is law, never force a trade, structure defines the stop, R:R ≥ 2:1, show your work, report what's missing, sanity-check sizing, log outcomes). This mode adds:

9. **The clock is a hard constraint, exactly like the stop loss.** A failed session-runway gate is a "no trade" — full stop, the same as a failed structural read. Never present a structurally-clean setup as a day trade if it can't complete in time.
10. **Flatten on the clock, not only on price.** Once a position is open, the session deadline is as real an exit trigger as the stop or target. "It's so close to target, let's give it another hour past the deadline" is exactly the kind of discipline failure this mode exists to prevent — it is what turns a day trade into an accidental, unplanned overnight swing position.
11. **Know the seam between modes, and say so out loud.** If Step 2/3 produces a structurally excellent read that simply can't complete within the session (fails the runway gate, or — per Step 3 — would require a level outside intraday scope to fill), don't drop it silently. Say plainly: *"this read is valid, but it's a swing setup, not a day trade — worth running `/smc-prob [SYMBOL]` to evaluate it on those terms."* The two modes are complementary lenses on the same structure, not competing verdicts.

---

## Invocation Modifiers

| Command | Behaviour |
|---|---|
| `/smc-day` | Scan the full enabled watchlist for day-trade setups; surface the single highest-confidence one that clears the session-runway gate (or "no qualifying day trade") |
| `/smc-day XAUUSD_SB` | Restrict analysis to a single instrument |
| `/smc-day XAUUSD_SB risk=1%` | Include live spread-bet position sizing — same model and defaults as the swing skill |

---

## Relationship to `/smc-prob` (the swing skill)

These are **two independent lenses on the same structural read, not a "lite" and "full" version of one thing.** Run them separately when you want one specific shape of trade; run them together via `/smc-scan` (see `ScanSkill.md`) when you want to see everything available on an instrument at once and decide for yourself which — one, the other, both, or neither — is worth acting on.

A useful mental model: the swing skill answers *"where will price go over the coming days, and where's the best place to ride that"*; this skill answers *"is there a clean, completable round trip available before the session ends — and is it worth taking on its own terms, separate from the bigger picture."* Both can be true on the same instrument at once, from different structural levels — that's not a contradiction, it's two different trades.
