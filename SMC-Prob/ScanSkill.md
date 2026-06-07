# Agent Skill: SMC-Scan — Combined Swing + Day-Trade Scanner

**Invoke with**: `/smc-scan [SYMBOL]`

**Install**:
```bash
cp "SMC-Prob/ScanSkill.md" ~/.claude/skills/smc-scan.md
```

*(Requires `smc-prob.md` and `smc-day.md` to also be installed — this skill orchestrates both rather than reimplementing either.)*

---

## Description

A single command that runs **both** SMC-Prob lenses — the Swing pipeline (`AgentSkill.md` / `/smc-prob`, validated by the 2026-06-07 backtest as a real source of edge over multi-day holds) and the Day-Trade pipeline (`DayTradeSkill.md` / `/smc-day`, designed for same-session, no-overnight-exposure setups) — against the same instrument(s), **as two independent parallel analyses**, and merges the results into a single combined report.

The point isn't to pick a winner between the two modes. They answer different questions about the same structure ("where will this go over days" vs. "is there a clean same-session round trip available right now") and their verdicts are not mutually exclusive — a clean swing bias and a clean day-trade entry can both exist on the same instrument from different structural levels at the same time. This skill's job is to surface *everything currently viable*, honestly and side by side, so the decision of what (if anything) to act on stays with the user.

---

## How It Works

### Step 1 — Resolve scope

Same instrument resolution as both base skills: a given `[SYMBOL]` restricts to one instrument; no symbol scans the full enabled watchlist (see `AgentSkill.md` "Default Watchlist" — shared across all three skills).

### Step 2 — Launch both analyses in parallel

Use the **Agent tool** to spawn two independent sub-agent analyses **in a single message** (they have no dependency on each other — both are fresh reads of the same live data, so there is no reason to run them sequentially):

- **Agent A — Swing analysis**: run the complete six-step pipeline exactly as specified in `AgentSkill.md` (Steps 1–6) against the target instrument(s). Produce its native trade-card or no-qualifying-setup output.
- **Agent B — Day-trade analysis**: run the complete six-step pipeline exactly as specified in `DayTradeSkill.md` (Steps 1–6, including the session-deadline determination and runway gate) against the same instrument(s). Produce its native trade-card or no-qualifying-day-trade output.

Brief each sub-agent with the full relevant pipeline spec (don't assume it has prior context — it hasn't seen this conversation) and the target instrument(s). Both should independently perform their own market-hours check against live data — if their readings of "is the market open / how stale is the data" disagree, that's worth surfacing, not silently reconciling.

### Step 3 — Merge into one combined report

Once both return, present a single combined report — do not just concatenate two raw trade cards; frame them so the user can compare at a glance:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SMC-SCAN — COMBINED SETUP REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Instrument(s) scanned : [list]
Data as of            : [timestamp / market-open status — flag if the two analyses disagreed on staleness]

── SWING TRADE LENS (multi-day hold, HTF liquidity targets) ──
[Agent A's full trade card — or its "no qualifying setup" card with what-to-watch level]

── DAY TRADE LENS (same-session only, flatten-by-deadline) ──
[Agent B's full trade card — or its "no qualifying day trade" card with the specific reason: no bias / no intraday entry / failed runway gate / below threshold]

── Summary — what's actually on the table right now ──
[One short paragraph: e.g. "Two independent setups available — a Grade-A swing short from the current premium retracement, and a Grade-B day-trade long off this morning's London sweep. They don't conflict (different structural levels, different timeframes) — both, either, or neither could be worth taking." OR "Nothing clears the bar on either lens right now — here's what to watch for on each: [swing watch level] / [day-trade watch level]."]

Tell me which (if any) you'd like to execute — one, the other, both, or neither — and at what size.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Step 4 — Flag follow-up candidates explicitly

If either lens (or both) produces a **"bias present, not yet at price"** verdict, call it out as a standing watch item — this is the manual seed of the laptop-resident scheduled-rescan workflow the user is building toward (see Behavioural Rules below and `BUILD-LOG.md`'s 2026-06-07 backtest entry, which found that *exactly this kind of followed-through setup produced the three largest wins in the test sample* — don't let one slip past unflagged).

---

## Behavioural Rules

1. **Each lens's verdict stands on its own merits.** A "no trade" from one mode is never softened, hedged, or talked up just because the other mode found something — and vice versa. Two honest, independent reads, presented side by side, full stop.
2. **Surface disagreement, don't paper over it.** If the two analyses read the HTF structure differently (e.g. one sees a confirmed CHoCH the other doesn't), or disagree on market-open/staleness status, say so plainly in the summary — that's a useful signal about read ambiguity, not a bug to hide.
3. **Always name follow-up candidates.** Any "bias present, no entry yet" verdict from either lens gets explicitly flagged with its watch level and a recommended re-scan trigger ("re-run `/smc-scan [SYMBOL]` once price approaches [level], or at the next [kill zone]"). This is the single most validated finding from the 2026-06-07 backtest — the setups that mattered most were the ones somebody followed forward.
4. **Log everything, tagged by mode.** Every distinct outcome from either lens — taken trade or stand-aside — gets logged to `TradeLog.md`, tagged `[Swing]` or `[Day]` in the Notes column, so the two modes' Step-4 weights can eventually be calibrated independently. The swing lens already has a small backtested calibration batch; the day-trade lens starts from zero and needs its own evidence base before its weights mean anything.
5. **Never auto-execute.** This skill analyses and reports — it places no orders on its own. Execution happens only on the user's explicit instruction, naming which setup(s) and at what size.

---

## Relationship to the Standalone Skills

`/smc-scan` doesn't replace `/smc-prob` or `/smc-day` — it's a convenience wrapper for when you want the full picture on an instrument in one pass. Run the standalone skills directly when you only care about one shape of trade (e.g. you're specifically swing-position-building, or specifically looking for something to close out before you step away from the screen).

---

## Looking Ahead — the Scheduled-Scan Vision

The user's stated end-state is an agent running on a laptop through the trading day on a strict schedule — periodic scans, and **automatic re-checks of "bias present, not yet at price" setups** (re-scanning when price approaches the flagged level, or abandoning the watch if the setup invalidates/reverses first) — exactly the walk-forward behaviour the 2026-06-07 backtest validated as the source of this skill's real edge.

This skill (and the manual re-scan habit it's meant to support) is the bridge to that: every "watch this level" flag it raises is a candidate for that future scheduler to track automatically. For now — running periodically from a phone, with the user manually triggering follow-up scans on flagged levels — `/smc-scan`'s job is to make those flags impossible to miss.
