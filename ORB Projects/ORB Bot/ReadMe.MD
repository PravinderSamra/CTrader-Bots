# ORB Bot (non-volume Opening Range Breakout)

## Which file do I use?

**`ORB_Bot.cs`** — this is the fixed **v2.0** bot. Use this one.

Identify it by line 2 of the file:
`// ORB Breakout cBot — v2.0 (Consistency & Safety Overhaul)`

Paste **only this file** into a cBot in cTrader Automate. Do not add the archived
original to the same project — both declare the class `OrbBreakoutBot`, so having
both in one project causes duplicate-class compile errors.

For the premarket-range **+ volume** variant, see `../ORB Volume Breakout Bot/`.

## Contents

| Path | What it is |
|---|---|
| `ORB_Bot.cs` | ✅ The bot to run — v2.0, all fixes applied |
| `docs/Phase1_Review_and_Spec.md` | The code review (14 findings, A1–A14) + implementation spec |
| `IMPLEMENTATION_NOTES.md` | Item-by-item map of what changed, incl. Phase 1.5 fixes |
| `archive/ORB_Bot_Original.cs` | ⛔ Reference only — the pre-fix version. Do not run. |

## What v2.0 fixed

Four critical defects plus ten further improvements (full detail in
`docs/Phase1_Review_and_Spec.md`):

1. **ORB lock inconsistency** — the live and backfill paths built the range from
   different bars, so the same day could produce a different ORB after a restart, and
   some timeframe/window combinations never locked at all.
2. **Phantom entries at lock** — confirmation bars from *inside* the range window could
   trigger an entry the moment the ORB locked.
3. **Position sizing blow-up** — a fallback sizing formula multiplied by `LotSize`,
   which could request a volume orders of magnitude too large.
4. **Naked entry window** — market orders were sent with no stop attached; a stop is now
   attached at execution and refined to the exact ORB-anchored level afterwards.

Plus: full replay of missed post-range breakouts, chart-call guards so optimization runs
don't crash, errors that always print regardless of the debug-logging setting, a 1-second
timer so quiet markets don't stall time-based actions, corrected VWAP after a mid-session
restart, and two new safety parameters (`Entry Retrace Tolerance Pips`,
`Block Same-Bar Re-Entry`).

> **Not yet compiled.** No cTrader/.NET compiler was available in the environment where
> these changes were made — the file was verified structurally and against the cTrader API
> patterns already used in the original. Build it in cTrader Automate before use.
