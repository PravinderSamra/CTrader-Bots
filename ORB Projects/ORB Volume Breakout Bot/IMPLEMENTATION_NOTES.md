# ORB Volume Breakout Bot — Phase 2 Implementation Notes

Spec: `docs/Phase2_Spec.md`
Base: `../ORB Bot/ORB_Bot.cs` (v2.0 + Phase 1.5 fixes) — **copied verbatim, then only the Phase 2
changes below were applied.** The base file was NOT modified.

Derived file: `ORB_Volume_Breakout_Bot.cs`.

## Spec item → change map

### §1 Identity
| Spec item | Change | Location |
|---|---|---|
| New file / class rename | `class OrbBreakoutBot` → `class OrbVolumeBreakoutBot` | class declaration (`[Robot(...)]`) |
| Header retitled + short changelog referencing this spec | Header block rewritten to "ORB Volume Breakout cBot — v1.0 (Premarket Range + Volume Breakout)" with a P2.1–P2.3 summary; the original Phase 1.5 A1–A14 changelog is preserved verbatim below it | top-of-file comment |
| Bot Label Prefix **default** `"ORB"` → `"ORBV"` (identifier unchanged) | `DefaultValue = "ORBV"` on `BotLabelPrefix` | Diagnostics group |

### §2 Volume filter — new "Volume Filter" parameter group
| Spec item | Change | Location |
|---|---|---|
| Group placed directly after "Breakout" | New group inserted after `AllowShort` | Parameters region |
| `EnableVolumeFilter` bool default true | `[Parameter("Enable Volume Filter", Group = "Volume Filter", DefaultValue = true)]` | Volume Filter group |
| `VolumeMultiplier` double default 1.2, MinValue 0.1 | `[Parameter("Volume Multiplier", ... DefaultValue = 1.2, MinValue = 0.1)]` | Volume Filter group |
| `VolumeLookbackBars` int default 20, MinValue 1, MaxValue 200 | `[Parameter("Volume Lookback Bars", ... DefaultValue = 20, MinValue = 1, MaxValue = 200)]` | Volume Filter group |
| Confirmation-TF `TickVolumes`; exclusive trailing window `[evalBar - Lookback, evalBar)`, clip at 0, require ≥1 bar else fail | New helper `EvaluateVolumeFilter(evalBarIndex, out evalVol, out trailingAvg, out required, out ratio)` | after `EvaluateEntryAtConfirmBar` |
| Pass condition `TickVolumes[evalBar] >= Multiplier x trailingAvg` | `return evalVol >= required;` in the helper | `EvaluateVolumeFilter` |
| **Signal qualification** (no-signal, not day-stand-down): fail ⇒ return as no-signal so later bars can still qualify; placed immediately after signal determined + direction-filtered; same for BodyCross multi-bar path (checks eval bar); works under post-lock replay | Volume filter block added right after `TradeType direction = ...`, before the entry gates; on fail it `return`s. Because both the closed-bar loop and post-lock replay call `EvaluateEntryAtConfirmBar`, and the direction/BodyCross logic already resolves to a single `evalBarIndex`, the check covers every path uniformly | `EvaluateEntryAtConfirmBar` |
| Intrabar comment (forming bar volume used as-is, conservative) | Comment added on the helper | `EvaluateVolumeFilter` header comment |
| Catch-up exempt (one explicit comment) | Comment added before the `CATCHUP SIGNAL` log; no volume check in `TryCatchUpEntry` | `TryCatchUpEntry` |
| Diagnostics: rejection log line | `Log("VOLUME FILTER: {side} breakout at {time} rejected. vol=... < required {mult}x avg({n})=...")` | volume block in `EvaluateEntryAtConfirmBar` |
| Diagnostics: enrich the `SIGNAL:` line with `vol=… avg=… ratio=…` | `SIGNAL:` `Log(...)` extended with a conditional ` | vol=... avg=... ratio=...` suffix (only when the filter is active) | `EvaluateEntryAtConfirmBar` |

### §3 Fixed-point stop — additions to "Stops & Targets"
| Spec item | Change | Location |
|---|---|---|
| `EnableFixedPointStop` bool default false | `[Parameter("Enable Fixed Point Stop", Group = "Stops & Targets", DefaultValue = false)]` | Stops & Targets group (after `TakeProfitR`) |
| `FixedStopPoints` double default 40, MinValue 0.1 | `[Parameter("Fixed Stop Points", ... DefaultValue = 40, MinValue = 0.1)]` | Stops & Targets group |
| ON: `slPrice = expectedEntry ∓ FixedStopPoints x _pointSize`, rounded to `Symbol.TickSize` | Two-mode SL computation; `expectedEntry` now computed **before** `slPrice` (reading `Symbol.Ask/Bid` is side-effect-free, so the ORB-percent branch is numerically unchanged); same `Math.Round(slPrice / TickSize) * TickSize` for both modes | `EnterTrade` |
| OFF: byte-for-byte the current ORB-percent logic | The `else` branch is the original two lines verbatim, followed by the original rounding line | `EnterTrade` |
| Unit: `FixedStopPoints` uses the Point-Unit unit (`_pointSize`); update the A14 unit block | Added "Group \"Stops & Targets\": Fixed Stop Points (only when Enable Fixed Point Stop = true)" to the A14 Point-Unit list, plus the 1 pip = 1 point note | A14 comment block |
| Downstream flows unchanged (risk pips, sizing, R-based TP, multi-TP, dynamic stop, early risk reduction, A4 attach-at-entry) — verified, no duplication | No downstream edits. All of them derive from `slPrice`/`estimatedRiskPips`/`initialRiskPipsActual`, which are computed the same way regardless of stop mode | verified, `EnterTrade` and management methods |
| Log active stop mode per trade in `TRADE ENTERED` | Appended `stopMode=FixedPoints({X}pt)` or `stopMode=OrbPercent({Y}%)` | `EnterTrade` `TRADE ENTERED` log |

### §4 / §5 Docs & delivery
- `README.md` — parameter guide + NAS100 and US30 research presets with disclaimers.
- `IMPLEMENTATION_NOTES.md` — this file.
- Committed to `claude/us30-london-range-breakout-lu3awm`; no PR.

## Downstream verification (both stop modes)
The initial stop price `slPrice` is the single source of risk. In both modes it is computed, then:
`estimatedRiskPips = |expectedEntry - slPrice| / Symbol.PipSize` drives volume sizing
(`VolumeForFixedRisk`), the execution-risk cap, and the A4 attach-time padded SL/TP. After the
fill, `initialRiskPipsActual = |entryPriceActual - slPrice| / PipSize` drives R-based TP, multi-TP,
dynamic stop (break-even + trailing), and early risk reduction — all via `state.InitialRiskPipsActual`.
None of these read the ORB range or the fixed-point parameters directly, so switching stop mode only
changes `slPrice` and everything else adapts automatically. No logic was duplicated.

## Deviations
None. All acceptance-criteria items were implemented exactly as specified.

## Structural verification
- Braces balanced (open == close) across the whole file.
- Paren/bracket counts carry the same literal-driven imbalance as the base file plus half-open
  interval notation `[a, b)` used in the new comments (comment text only — no code effect).
- No cTrader/.NET compiler is available in this environment; edits were kept conservative and match
  API patterns already present in the base file (`_confirmBars.TickVolumes[i]`, `Math.Round(.../TickSize)*TickSize`,
  `Log(...)` formatting). The file was re-read end-to-end after editing.
- Single definitions confirmed: one `class OrbVolumeBreakoutBot`, one `double expectedEntry`
  declaration in `EnterTrade`, one `EvaluateVolumeFilter` method.
