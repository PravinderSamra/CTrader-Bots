# cTrader cBot Base Parameters — Reference Document

> **Purpose:** This document defines the standard reusable parameter sections, internal state, and implementation methods that should be included in every cBot. When building a new cBot, copy all sections from this document and add your strategy-specific parameters and logic on top.

---

## Table of Contents
1. [Required Enums & Support Classes](#1-required-enums--support-classes)
2. [Parameter Declarations](#2-parameter-declarations)
   - 2.1 Session (UTC)
   - 2.2 Session Time Zone
   - 2.3 Trades Per Day
   - 2.4 Trading Days
   - 2.5 Take Profit
   - 2.6 Multi Take Profit
   - 2.7 Dynamic Stop
   - 2.8 Early Risk Reduction
   - 2.9 Risk
   - 2.10 Execution Risk Cap
   - 2.11 Safety
   - 2.12 Diagnostics
3. [Internal State Variables](#3-internal-state-variables)
4. [OnStart() Initialisation](#4-onstart-initialisation)
5. [OnTick() Base Logic](#5-ontick-base-logic)
6. [OnStop()](#6-onstop)
7. [Complete Method Implementations](#7-complete-method-implementations)
   - 7.1 Session Timezone
   - 7.2 Session Time Computation
   - 7.3 Daily Reset
   - 7.4 Trading Day Check
   - 7.5 Risk Currency Conversion
   - 7.6 Volume Sizing & Execution Risk Cap
   - 7.7 Position Management (Multi TP, Dynamic Stop, Early Risk Reduction)
   - 7.8 Safe Position Close
   - 7.9 Position Closed Handler
   - 7.10 Restart Safety — Trade Count Rehydration
   - 7.11 Diagnostics / Logging
   - 7.12 Volume Normalisation Helpers
   - 7.13 Position Identification Helpers
8. [Integration Notes for Strategy-Specific Code](#8-integration-notes-for-strategy-specific-code)
9. [Common Misconfiguration Warnings](#9-common-misconfiguration-warnings)

---

## 1. Required Enums & Support Classes

Place these **outside** the Robot class, inside the namespace block.

```csharp
public enum RiskCurrency
{
    AccountCurrency,
    GBP,
    USD
}

public enum SessionTimeZoneEnum
{
    UTC,
    EuropeLondon,   // UK — GMT/BST, auto DST-aware
    EuropeBerlin,   // Frankfurt/Germany — CET/CEST, auto DST-aware
    AmericaNewYork  // New York — EST/EDT, auto DST-aware
}

// Per-position state. Tracks entry price, initial SL, initial volume,
// and flags for each management feature so they fire exactly once.
public class PositionState
{
    public long   PositionId              { get; set; }
    public double EntryPrice              { get; set; }
    public double SLPriceInitial          { get; set; }
    public double InitialRiskPipsActual   { get; set; }
    public double InitialVolumeInUnits    { get; set; }
    public bool   EarlyRiskReductionDone  { get; set; }
    public bool   BreakEvenDone           { get; set; }
    public bool   TP1Done                 { get; set; }
    public bool   TP2Done                 { get; set; }
    public bool   TP3Done                 { get; set; }
    public bool   TP4Done                 { get; set; }
    public double LastTrailSteps          { get; set; }
}

// Exponential backoff state for safe position closing (prevents broker flooding).
public class CloseBackoffState
{
    public int      FailCount       { get; set; }
    public DateTime NextAttemptUtc  { get; set; }
}
```

---

## 2. Parameter Declarations

### 2.1 Session (UTC)

All times are entered in **HH:mm:ss** format. Times are interpreted as either fixed UTC or local session-timezone times depending on the Session Time Zone settings (section 2.2).

| Parameter | Default | Description |
|---|---|---|
| Session Start Time | `09:30:00` | When the session/range window begins |
| Session End Time | `09:35:00` | When the session/range window closes |
| Trading Start Time | `09:35:00` | Earliest time new entries are allowed. Can equal Session End or be later for delayed strategies. Setting earlier than Session End is valid — entries will still wait for the session to complete |
| Enable Kill Switch | `false` | Block all new entries after Kill Switch Time |
| Kill Switch Time | `23:59:00` | No new entries at or after this time |
| Enable Close Positions Time | `false` | Force-close all open bot positions at a separate time |
| Close Positions Time | `23:59:00` | Force-flat time (independent of Kill Switch) |

```csharp
[Parameter("Session Start Time", Group = "Session", DefaultValue = "09:30:00")]
public string SessionStartTimeStr { get; set; }

[Parameter("Session End Time", Group = "Session", DefaultValue = "09:35:00")]
public string SessionEndTimeStr { get; set; }

[Parameter("Trading Start Time", Group = "Session", DefaultValue = "09:35:00")]
public string TradingStartTimeStr { get; set; }

[Parameter("Enable Kill Switch", Group = "Session", DefaultValue = false)]
public bool EnableKillSwitch { get; set; }

[Parameter("Kill Switch Time", Group = "Session", DefaultValue = "23:59:00")]
public string KillSwitchTimeStr { get; set; }

[Parameter("Enable Close Positions Time", Group = "Session", DefaultValue = false)]
public bool EnableClosePositionsTime { get; set; }

[Parameter("Close Positions Time", Group = "Session", DefaultValue = "23:59:00")]
public string ClosePositionsTimeStr { get; set; }
```

**Behaviour notes:**
- Kill Switch blocks **new entries** only. Open positions are unaffected unless Close Positions Time is also active.
- Close Positions Time force-closes **all open bot positions** AND blocks new entries. It is independent of Kill Switch.
- If Kill Switch Time < Session End Time, no trades will ever occur. The bot logs a warning at startup.
- If Close Positions Time < Session End Time, same result. The bot logs a warning at startup.
- Times configured earlier than Session Start are assumed to be **next-day** (cross-midnight sessions).

---

### 2.2 Session Time Zone

Controls whether entered times are treated as fixed UTC or automatically converted from a local timezone (with full DST support).

| Parameter | Default | Description |
|---|---|---|
| Use Fixed UTC Times | `true` | When `true`, all session times are literal UTC. When `false`, times are in the selected local timezone and automatically converted to UTC each day, including DST transitions |
| Session Time Zone | `UTC` | Active when Use Fixed UTC Times = false. Options: UTC, EuropeLondon, EuropeBerlin, AmericaNewYork |

```csharp
[Parameter("Use Fixed UTC Times", Group = "Session Time Zone", DefaultValue = true)]
public bool UseFixedUtcTimes { get; set; }

[Parameter("Session Time Zone", Group = "Session Time Zone", DefaultValue = SessionTimeZoneEnum.UTC)]
public SessionTimeZoneEnum SessionTimeZoneParam { get; set; }
```

**DST handling:**
- `EuropeLondon` — GMT (UTC+0) in winter, BST (UTC+1) in summer.
- `EuropeBerlin` — CET (UTC+1) in winter, CEST (UTC+2) in summer. Covers Frankfurt.
- `AmericaNewYork` — EST (UTC-5) in winter, EDT (UTC-4) in summer.
- DST spring-forward gaps are automatically resolved by shifting +1 hour.
- DST fall-back ambiguous times log a warning and use the standard-time interpretation.
- The resolver tries both Windows TZ IDs (e.g. `"Eastern Standard Time"`) and IANA IDs (e.g. `"America/New_York"`) so the bot works on Windows VPS and Linux/Mac cTrader hosts.

---

### 2.3 Trades Per Day

```csharp
[Parameter("Max Trades Per Day", Group = "Trades Per Day", DefaultValue = 1, MinValue = 1)]
public int MaxTradesPerDay { get; set; }
```

**Behaviour notes:**
- Counter resets at the start of each session day (based on Session Time Zone).
- **Restart-safe**: if the bot restarts mid-session, trade count is rehydrated from open positions and account History so `MaxTradesPerDay = 1` is always honoured.
- Partial TP closes on the same position do NOT count as additional trades.

---

### 2.4 Trading Days

```csharp
[Parameter("Trade Monday",    Group = "Trading Days", DefaultValue = true)]
public bool TradeMonday { get; set; }

[Parameter("Trade Tuesday",   Group = "Trading Days", DefaultValue = true)]
public bool TradeTuesday { get; set; }

[Parameter("Trade Wednesday", Group = "Trading Days", DefaultValue = true)]
public bool TradeWednesday { get; set; }

[Parameter("Trade Thursday",  Group = "Trading Days", DefaultValue = true)]
public bool TradeThursday { get; set; }

[Parameter("Trade Friday",    Group = "Trading Days", DefaultValue = true)]
public bool TradeFriday { get; set; }

[Parameter("Trade Saturday",  Group = "Trading Days", DefaultValue = false)]
public bool TradeSaturday { get; set; }

[Parameter("Trade Sunday",    Group = "Trading Days", DefaultValue = false)]
public bool TradeSunday { get; set; }
```

**Behaviour notes:**
- Day-of-week is evaluated against the **session date** (already timezone-adjusted), not raw UTC date. This ensures Friday in New York is not treated as Saturday in UTC when trading after 19:00 UTC.

---

### 2.5 Take Profit

Single TP expressed as a multiple of initial risk (R). Used when Multi TP is disabled, or as the fallback TP for the final runner when Multi TP is active.

```csharp
[Parameter("Take Profit R", Group = "Take Profit", DefaultValue = 2.0, MinValue = 0.1)]
public double TakeProfitR { get; set; }
```

---

### 2.6 Multi Take Profit

Up to 4 partial close levels. Each level is defined by an R-multiple target and a percentage of the **initial** position volume to close at that level.

- Set `TP R = 0` or `Close % = 0` to disable a level.
- Percentages are scaled automatically if the total exceeds 100%.
- The bot sets the hard TP order on the full position at the **highest active TP R**. Partial closes execute via market order as each level is reached.

```csharp
[Parameter("Enable Multi TP", Group = "Multi Take Profit", DefaultValue = false)]
public bool EnableMultiTp { get; set; }

[Parameter("TP1 R",             Group = "Multi Take Profit", DefaultValue = 1.0)]
public double TP1_R { get; set; }

[Parameter("TP1 Close Percent", Group = "Multi Take Profit", DefaultValue = 40)]
public double TP1_ClosePercent { get; set; }

[Parameter("TP2 R",             Group = "Multi Take Profit", DefaultValue = 2.0)]
public double TP2_R { get; set; }

[Parameter("TP2 Close Percent", Group = "Multi Take Profit", DefaultValue = 0)]
public double TP2_ClosePercent { get; set; }

[Parameter("TP3 R",             Group = "Multi Take Profit", DefaultValue = 3.0)]
public double TP3_R { get; set; }

[Parameter("TP3 Close Percent", Group = "Multi Take Profit", DefaultValue = 40)]
public double TP3_ClosePercent { get; set; }

[Parameter("TP4 R",             Group = "Multi Take Profit", DefaultValue = 4.0)]
public double TP4_R { get; set; }

[Parameter("TP4 Close Percent", Group = "Multi Take Profit", DefaultValue = 0)]
public double TP4_ClosePercent { get; set; }
```

**Example config (screenshot defaults):**
- TP1 @ 2R → close 40%
- TP2 @ 2.5R → close 0% (disabled)
- TP3 @ 3R → close 40%
- TP4 @ 4R → close 0% (disabled — remainder runs to the hard TP at 4R)

---

### 2.7 Dynamic Stop (Break Even + Trailing)

Moves the stop loss to break even once a profit threshold is reached, then optionally trails it in R steps.

```csharp
[Parameter("Enable Dynamic Stop", Group = "Dynamic Stop", DefaultValue = false)]
public bool EnableDynamicStop { get; set; }

[Parameter("Break Even Trigger R", Group = "Dynamic Stop", DefaultValue = 1.0, MinValue = 0.1)]
public double BreakEvenTriggerR { get; set; }

[Parameter("Break Even Extra Pips", Group = "Dynamic Stop", DefaultValue = 0.0, MinValue = 0.0)]
public double BreakEvenExtraPips { get; set; }

[Parameter("Dynamic Step R", Group = "Dynamic Stop", DefaultValue = 0.25, MinValue = 0.0)]
public double DynamicStepR { get; set; }
```

**Behaviour notes:**
- When `profitR >= BreakEvenTriggerR`, SL moves to `entry + BreakEvenExtraPips` (locking a small profit buffer).
- With `DynamicStepR > 0`, for every additional R step of profit beyond the trigger, SL advances by one step. E.g., trigger=1R, step=0.25R → at 1.25R profit, SL locks 0.25R; at 1.5R profit, SL locks 0.5R, etc.
- SL only ever moves in the profitable direction (never backwards).
- Early Risk Reduction (section 2.8) deactivates automatically once Break Even fires.

---

### 2.8 Early Risk Reduction

Reduces the stop loss distance before break even is reached, to cut potential loss if the trade goes wrong after an initial move in your favour.

```csharp
[Parameter("Enable Early Risk Reduction", Group = "Early Risk Reduction", DefaultValue = false)]
public bool EnableEarlyRiskReduction { get; set; }

[Parameter("Early Risk Reduction Trigger R", Group = "Early Risk Reduction", DefaultValue = 0.5, MinValue = 0.1)]
public double EarlyRiskReductionTriggerR { get; set; }

[Parameter("Early Risk Reduction Remaining Risk %", Group = "Early Risk Reduction", DefaultValue = 50.0, MinValue = 1.0, MaxValue = 100.0)]
public double EarlyRiskReductionRemainingRiskPercent { get; set; }
```

**Behaviour notes:**
- Fires once when `profitR >= EarlyRiskReductionTriggerR` and Break Even has not yet fired.
- Moves SL to `entry - (InitialRiskPips * RemainingRisk%)`. E.g., with 50% remaining: if initial SL was 20 pips below entry, new SL is 10 pips below entry.
- Fires only once. Does not repeat.
- If Dynamic Stop is also enabled, Early Risk Reduction is automatically suppressed once `profitR >= BreakEvenTriggerR` to avoid conflicting SL movements.

---

### 2.9 Risk

Risk is always defined as a **fixed currency amount** per trade. Volume is calculated automatically from the SL distance so that the specified currency amount is risked.

```csharp
[Parameter("Risk Amount", Group = "Risk", DefaultValue = 100, MinValue = 1)]
public double RiskAmount { get; set; }

[Parameter("Risk Currency", Group = "Risk", DefaultValue = RiskCurrency.AccountCurrency)]
public RiskCurrency RiskCurrencyParam { get; set; }
```

**Options:**
- `AccountCurrency` — risk exactly `RiskAmount` in whatever currency your account is denominated in. No conversion needed.
- `GBP` — risk `RiskAmount` GBP, converted to account currency at current rates.
- `USD` — risk `RiskAmount` USD, converted to account currency at current rates.

**Behaviour notes:**
- Currency conversion uses cTrader's `AssetConverter.Convert()`. If conversion fails, falls back to treating the amount as account currency and logs a warning.
- Volume is calculated using `Symbol.VolumeForFixedRisk()` and rounded **down** to avoid over-risking.

---

### 2.10 Execution Risk Cap

An additional safety layer on volume sizing. Even if your intended risk is correctly sized to your SL, a gap or slippage at the stop can cause a much larger loss. This cap sizes volume so that even with an **assumed worst-case slippage**, the loss stays within a hard limit.

```csharp
[Parameter("Enable Execution Risk Cap", Group = "Execution Risk Cap", DefaultValue = true)]
public bool EnableExecutionRiskCap { get; set; }

[Parameter("Assumed Stop Slippage Pips", Group = "Execution Risk Cap", DefaultValue = 30.0, MinValue = 0.0)]
public double AssumedStopSlippagePips { get; set; }

[Parameter("Max Loss Per Trade (Account CCY)", Group = "Execution Risk Cap", DefaultValue = 200.0, MinValue = 0.0)]
public double MaxLossPerTradeAccountCcy { get; set; }
```

**Behaviour notes:**
- `WorstCasePips = SLDistance + AssumedStopSlippagePips`
- Volume is capped so that `WorstCasePips × volume ≤ MaxLossPerTradeAccountCcy`
- If the risk-sized volume is already within the cap, no clamping occurs and the trade is unaffected.
- This does **not** guarantee the maximum loss in all market conditions (e.g., extreme gaps), but materially reduces the risk of a runaway loss.
- If the cap would reduce volume below broker minimum, the trade is skipped and logged.

---

### 2.11 Safety

Guards against account-damaging edge cases. When limits are set to `0`, that check is disabled (except margin safety which has its own enable flag).

```csharp
[Parameter("Min Risk Pips", Group = "Safety", DefaultValue = 0.0, MinValue = 0.0)]
public double MinRiskPips { get; set; }

[Parameter("Max Volume In Units", Group = "Safety", DefaultValue = 0, MinValue = 0)]
public double MaxVolumeInUnits { get; set; }

[Parameter("Max Spread Pips", Group = "Safety", DefaultValue = 0, MinValue = 0)]
public double MaxSpreadPips { get; set; }

[Parameter("Enable Margin Safety", Group = "Safety", DefaultValue = true)]
public bool EnableMarginSafety { get; set; }

[Parameter("Max Margin Usage %", Group = "Safety", DefaultValue = 60.0, MinValue = 1.0, MaxValue = 100.0)]
public double MaxMarginUsagePercent { get; set; }

[Parameter("Clamp Volume To Margin", Group = "Safety", DefaultValue = true)]
public bool ClampVolumeToMargin { get; set; }

[Parameter("Enable Protection Fallback", Group = "Safety", DefaultValue = true)]
public bool EnableProtectionFallback { get; set; }

[Parameter("Fallback SL Pips", Group = "Safety", DefaultValue = 20.0, MinValue = 0.0)]
public double FallbackStopLossPips { get; set; }
```

| Parameter | Effect |
|---|---|
| Min Risk Pips | Skip trade if SL distance < this value. Prevents nonsensically tight stops. Set to 0 to disable |
| Max Volume In Units | Hard cap on position size. Overrides risk-sizing if breached. Set to 0 to disable |
| Max Spread Pips | Skip trade if current spread > this value. Protects against news spikes. Set to 0 to disable |
| Enable Margin Safety | Checks estimated margin before entering |
| Max Margin Usage % | Maximum % of free margin the new trade may consume |
| Clamp Volume To Margin | If `true`, reduce volume proportionally to fit within margin limit instead of skipping. If `false`, skip the trade entirely |
| Enable Protection Fallback | If the strategy-computed SL/TP fails to apply (broker rejection), attempt a fixed-pip fallback SL before closing the position |
| Fallback SL Pips | Fixed pip distance for the fallback SL, anchored to actual entry price. Never tighter than the original intended SL |

**Important:** Margin safety and spread checks protect the account without shortening winning trades — they only gate entry. Once in a trade, they have no effect.

---

### 2.12 Diagnostics

```csharp
[Parameter("Bot Label Prefix", Group = "Diagnostics", DefaultValue = "BOT")]
public string BotLabelPrefix { get; set; }

[Parameter("Enable Debug Logging", Group = "Diagnostics", DefaultValue = true)]
public bool EnableDebugLogging { get; set; }

[Parameter("Verbose Logging", Group = "Diagnostics", DefaultValue = false)]
public bool VerboseLogging { get; set; }

[Parameter("Explain Blocked Entries", Group = "Diagnostics", DefaultValue = true)]
public bool ExplainBlockedEntries { get; set; }
```

| Parameter | Effect |
|---|---|
| Bot Label Prefix | Prepended to all position labels: `{Prefix}_{Symbol}_{yyyyMMdd}`. Used to identify this bot's positions |
| Enable Debug Logging | Master switch. When `false`, no log output is produced (useful for backtests to improve speed) |
| Verbose Logging | When `true`, logs full account state on every trade entry and close: equity, margin, balance, commission, swap, spread |
| Explain Blocked Entries | When `true`, logs the reason every time a valid signal is blocked by a gate (kill switch, max trades, no-trade day, etc.) |

---

## 3. Internal State Variables

Declare these as private fields inside your Robot class.

```csharp
// --- Parsed time spans ---
private TimeSpan _sessionStartTimeCfg;
private TimeSpan _sessionEndTimeCfg;
private TimeSpan _tradingStartTimeCfg;
private TimeSpan _killSwitchTimeCfg;
private TimeSpan _closePositionsTimeCfg;

// --- Resolved session timezone ---
private TimeZoneInfo _sessionTz;

// --- Daily UTC session boundaries (recomputed each day) ---
private DateTime _sessionStartUtcToday;
private DateTime _sessionEndUtcToday;
private DateTime _tradingStartUtcToday;
private DateTime _killSwitchUtcToday;
private DateTime _closePositionsUtcToday;

// --- Daily state ---
private DateTime _currentSessionDate;
private bool     _noTradeToday;
private int      _tradesToday;
private bool     _killSwitchLoggedToday;
private bool     _closePositionsLoggedToday;
private bool     _sessionTimeLoggedToday;

// --- Per-position tracking ---
private Dictionary<long, PositionState>   _positionStates;

// --- Safe-close retry throttling ---
private Dictionary<long, DateTime>        _lastCloseFailLogUtcByPosId;
private Dictionary<long, CloseBackoffState> _closeBackoffByPosId;

// --- Multi TP internal (normalised percents & max R) ---
private double _tp1Pct, _tp2Pct, _tp3Pct, _tp4Pct;
private double _maxTpR;
```

---

## 4. OnStart() Initialisation

```csharp
protected override void OnStart()
{
    // 1. Parse all time parameters
    if (!TimeSpan.TryParse(SessionStartTimeStr, out _sessionStartTimeCfg))
    { Print("ERROR: Cannot parse SessionStartTime '{0}'", SessionStartTimeStr); Stop(); return; }

    if (!TimeSpan.TryParse(SessionEndTimeStr, out _sessionEndTimeCfg))
    { Print("ERROR: Cannot parse SessionEndTime '{0}'", SessionEndTimeStr); Stop(); return; }

    if (!TimeSpan.TryParse(TradingStartTimeStr, out _tradingStartTimeCfg))
    { Print("ERROR: Cannot parse TradingStartTime '{0}'", TradingStartTimeStr); Stop(); return; }

    if (!TimeSpan.TryParse(KillSwitchTimeStr, out _killSwitchTimeCfg))
    { Print("ERROR: Cannot parse KillSwitchTime '{0}'", KillSwitchTimeStr); Stop(); return; }

    if (!TimeSpan.TryParse(ClosePositionsTimeStr, out _closePositionsTimeCfg))
    { Print("ERROR: Cannot parse ClosePositionsTime '{0}'", ClosePositionsTimeStr); Stop(); return; }

    // 2. Resolve session timezone
    _sessionTz = ResolveTimeZone();
    if (_sessionTz == null) { Print("ERROR: Failed to resolve session timezone."); Stop(); return; }

    // 3. Initialise dictionaries
    _positionStates             = new Dictionary<long, PositionState>();
    _lastCloseFailLogUtcByPosId = new Dictionary<long, DateTime>();
    _closeBackoffByPosId        = new Dictionary<long, CloseBackoffState>();

    // 4. Normalise Multi TP percents and compute max TP R
    NormalizeMultiTpPercents();
    ComputeMaxTpR();

    // 5. Subscribe to position closed event
    Positions.Closed += OnPositionsClosed;

    // 6. Initialise daily state
    _currentSessionDate = DateTime.MinValue;
    ResetForDate(GetSessionDate(Server.Time));

    // 7. Register any existing bot positions (restart recovery)
    foreach (var pos in Positions)
        if (IsBotPosition(pos) && !IsIgnorableDustPosition(pos))
            RegisterExistingPosition(pos);

    // 8. Strategy-specific initialisation goes here
    // e.g., load bars, indicators, etc.

    Log("Bot started. Symbol={0} TZ={1}", Symbol.Name,
        UseFixedUtcTimes ? "UTC(fixed)" : SessionTimeZoneParam.ToString());
    Log("VOLUME_DIAG symbol={0} min={1} step={2} max={3}",
        Symbol.Name, Symbol.VolumeInUnitsMin, Symbol.VolumeInUnitsStep, Symbol.VolumeInUnitsMax);

    // 9. Startup sanity warnings
    if (EnableKillSwitch && _tradingStartUtcToday >= _killSwitchUtcToday)
        Print("WARNING: TradingStartTime >= KillSwitchTime. No entries possible today.");
    if (EnableClosePositionsTime && _closePositionsUtcToday <= _sessionEndUtcToday)
        Print("WARNING: ClosePositionsTime <= SessionEndTime. Entries will be blocked all day.");
}
```

---

## 5. OnTick() Base Logic

```csharp
protected override void OnTick()
{
    var nowUtc = Server.Time;

    // Check for new session day
    DateTime sessionDate = GetSessionDate(nowUtc);
    if (sessionDate != _currentSessionDate)
        ResetForDate(sessionDate);

    // Force-close and block entries after Close Positions Time
    if (EnableClosePositionsTime && nowUtc >= _closePositionsUtcToday)
    {
        if (!_closePositionsLoggedToday)
        {
            Log("CLOSE POSITIONS TIME reached ({0:HH:mm}). Closing all bot positions.", _closePositionsUtcToday);
            _closePositionsLoggedToday = true;
        }
        if (HasOpenBotPosition())
            CloseAllBotPositions("CLOSE TIME");
    }

    // ── STRATEGY-SPECIFIC LOGIC GOES HERE ──
    // e.g., process new bars, evaluate signals, call EnterTrade()

    // Manage open positions on every tick (Multi TP, Dynamic Stop, Early Risk Reduction)
    ManageOpenPositions();
}
```

---

## 6. OnStop()

```csharp
protected override void OnStop()
{
    Positions.Closed -= OnPositionsClosed;
    Log("Bot stopped.");
}
```

---

## 7. Complete Method Implementations

### 7.1 Session Timezone

```csharp
private TimeZoneInfo ResolveTimeZone()
{
    if (UseFixedUtcTimes)
        return TimeZoneInfo.Utc;

    // Try both Windows TZ IDs and IANA IDs so the bot works on
    // Windows VPS and Linux/macOS cTrader hosts.
    string[] candidates;
    switch (SessionTimeZoneParam)
    {
        case SessionTimeZoneEnum.EuropeLondon:
            candidates = new[] { "GMT Standard Time", "Europe/London" };
            break;
        case SessionTimeZoneEnum.EuropeBerlin:
            candidates = new[] { "W. Europe Standard Time", "Europe/Berlin" };
            break;
        case SessionTimeZoneEnum.AmericaNewYork:
            candidates = new[] { "Eastern Standard Time", "America/New_York" };
            break;
        default:
            return TimeZoneInfo.Utc;
    }

    foreach (var id in candidates)
    {
        try
        {
            var tz = TimeZoneInfo.FindSystemTimeZoneById(id);
            Print("SESSION_TIMEZONE resolved='{0}' id='{1}'", tz.DisplayName, id);
            return tz;
        }
        catch { /* try next */ }
    }

    Print("WARNING: Could not resolve timezone for {0}. Falling back to UTC.", SessionTimeZoneParam);
    return TimeZoneInfo.Utc;
}

private DateTime GetSessionDate(DateTime utcNow)
{
    if (UseFixedUtcTimes) return utcNow.Date;
    return TimeZoneInfo.ConvertTimeFromUtc(utcNow, _sessionTz).Date;
}
```

---

### 7.2 Session Time Computation

```csharp
private DateTime ConvertConfiguredTimeToUtc(DateTime sessionDate, TimeSpan configuredTime)
{
    if (UseFixedUtcTimes)
        return sessionDate + configuredTime;

    DateTime localDt = sessionDate + configuredTime;
    try
    {
        if (_sessionTz.IsInvalidTime(localDt))
            localDt = localDt.AddHours(1); // DST spring-forward gap

        if (_sessionTz.IsAmbiguousTime(localDt))
            Print("WARNING: Ambiguous time {0} in {1} (DST fall-back). Using standard-time offset.", localDt, SessionTimeZoneParam);

        return TimeZoneInfo.ConvertTimeToUtc(localDt, _sessionTz);
    }
    catch
    {
        return sessionDate + configuredTime; // safe fallback
    }
}

private void ComputeSessionTimesForDay(DateTime sessionDate)
{
    _sessionStartUtcToday    = ConvertConfiguredTimeToUtc(sessionDate, _sessionStartTimeCfg);
    _sessionEndUtcToday      = ConvertConfiguredTimeToUtc(sessionDate, _sessionEndTimeCfg);
    _tradingStartUtcToday    = ConvertConfiguredTimeToUtc(sessionDate, _tradingStartTimeCfg);
    _killSwitchUtcToday      = ConvertConfiguredTimeToUtc(sessionDate, _killSwitchTimeCfg);
    _closePositionsUtcToday  = ConvertConfiguredTimeToUtc(sessionDate, _closePositionsTimeCfg);

    // Cross-midnight: ensure end > start
    if (_sessionEndUtcToday <= _sessionStartUtcToday)
        _sessionEndUtcToday = _sessionEndUtcToday.AddDays(1);

    // Kill switch / close positions intended to be after session —
    // if configured earlier than session start, treat as next-day.
    if (_killSwitchUtcToday     < _sessionStartUtcToday) _killSwitchUtcToday     = _killSwitchUtcToday.AddDays(1);
    if (_closePositionsUtcToday < _sessionStartUtcToday) _closePositionsUtcToday = _closePositionsUtcToday.AddDays(1);
}
```

---

### 7.3 Daily Reset

```csharp
private void ResetForDate(DateTime sessionDate)
{
    _currentSessionDate          = sessionDate;
    _noTradeToday                = false;
    _tradesToday                 = 0;
    _killSwitchLoggedToday       = false;
    _closePositionsLoggedToday   = false;
    _sessionTimeLoggedToday      = false;

    ComputeSessionTimesForDay(sessionDate);

    // Check if today is an enabled trading day
    if (!IsTradingDayEnabled(sessionDate.DayOfWeek))
    {
        _noTradeToday = true;
        Log("NO TRADE TODAY: Trading disabled for {0}.", sessionDate.DayOfWeek);
    }

    Log("=== New day reset: {0:yyyy-MM-dd} ===", sessionDate);
    LogSessionTimezone();

    // Restart safety: rehydrate trade count from history
    RehydrateTradesTodayFromHistory("RESET");

    // Strategy-specific daily reset hook (call your own reset logic here)
    // e.g., ResetStrategyState();
}

private void LogSessionTimezone()
{
    if (_sessionTimeLoggedToday) return;
    _sessionTimeLoggedToday = true;

    if (UseFixedUtcTimes)
    {
        Log("SESSION_TIMEZONE mode=UTC");
    }
    else
    {
        Log("SESSION_TIMEZONE mode=Local tz={0} sessionUtc={1:HH:mm}-{2:HH:mm} tradingStartUtc={3:HH:mm} killUtc={4:HH:mm} closeUtc={5:HH:mm}",
            SessionTimeZoneParam,
            _sessionStartUtcToday, _sessionEndUtcToday,
            _tradingStartUtcToday, _killSwitchUtcToday, _closePositionsUtcToday);
    }
}
```

---

### 7.4 Trading Day Check

```csharp
private bool IsTradingDayEnabled(DayOfWeek dow)
{
    switch (dow)
    {
        case DayOfWeek.Monday:    return TradeMonday;
        case DayOfWeek.Tuesday:   return TradeTuesday;
        case DayOfWeek.Wednesday: return TradeWednesday;
        case DayOfWeek.Thursday:  return TradeThursday;
        case DayOfWeek.Friday:    return TradeFriday;
        case DayOfWeek.Saturday:  return TradeSaturday;
        case DayOfWeek.Sunday:    return TradeSunday;
        default: return true;
    }
}
```

---

### 7.5 Risk Currency Conversion

```csharp
private double GetRiskInAccountCurrency()
{
    string accountCcy = Account.Asset.Name;

    if (RiskCurrencyParam == RiskCurrency.AccountCurrency)
        return RiskAmount;

    string fromCcy = (RiskCurrencyParam == RiskCurrency.GBP) ? "GBP" : "USD";

    if (fromCcy == accountCcy)
        return RiskAmount;

    try
    {
        double converted = AssetConverter.Convert(RiskAmount, fromCcy, accountCcy);
        if (converted <= 0)
        {
            Log("WARNING: Currency conversion returned {0}. Falling back to RiskAmount={1}.", converted, RiskAmount);
            return RiskAmount;
        }
        return converted;
    }
    catch (Exception ex)
    {
        Log("WARNING: Currency conversion failed: {0}. Falling back to RiskAmount={1}.", ex.Message, RiskAmount);
        return RiskAmount;
    }
}
```

---

### 7.6 Volume Sizing & Execution Risk Cap

Call this inside your `EnterTrade()` method after computing the SL distance (`estimatedRiskPips`) and the strategy-specific SL price.

```csharp
// Returns the volume to trade, or -1 if the trade should be skipped.
private double ComputeVolume(TradeType tradeType, double estimatedRiskPips, double effectiveTpR)
{
    double riskInAccountCcy = GetRiskInAccountCurrency();
    if (riskInAccountCcy <= 0)
    {
        Log("ERROR: Risk amount in account currency <= 0. Cannot trade.");
        return -1;
    }

    // Safety: min risk pips
    if (MinRiskPips > 0 && estimatedRiskPips < MinRiskPips)
    {
        Log("SAFETY: Risk {0:F1} pips < MinRiskPips {1}. Skipping.", estimatedRiskPips, MinRiskPips);
        return -1;
    }

    // Base volume from risk amount
    double volumeRisk;
    try
    {
        volumeRisk = Symbol.VolumeForFixedRisk(riskInAccountCcy, estimatedRiskPips, RoundingMode.Down);
    }
    catch (Exception ex)
    {
        Log("ERROR: VolumeForFixedRisk failed: {0}. Manual fallback.", ex.Message);
        if (Symbol.PipValue <= 0) { Log("ERROR: PipValue=0. Cannot compute volume."); return -1; }
        volumeRisk = riskInAccountCcy * Symbol.LotSize / (estimatedRiskPips * Symbol.PipValue);
    }
    volumeRisk = Symbol.NormalizeVolumeInUnits(volumeRisk, RoundingMode.Down);

    // Execution risk cap
    double volumeCap = volumeRisk;
    if (EnableExecutionRiskCap && MaxLossPerTradeAccountCcy > 0 && AssumedStopSlippagePips > 0)
    {
        double worstCasePips = estimatedRiskPips + AssumedStopSlippagePips;
        try
        {
            volumeCap = Symbol.VolumeForFixedRisk(MaxLossPerTradeAccountCcy, worstCasePips, RoundingMode.Down);
        }
        catch
        {
            if (Symbol.PipValue > 0)
                volumeCap = MaxLossPerTradeAccountCcy * Symbol.LotSize / (worstCasePips * Symbol.PipValue);
        }
        volumeCap = Symbol.NormalizeVolumeInUnits(volumeCap, RoundingMode.Down);

        if (volumeCap < Symbol.VolumeInUnitsMin)
        {
            Log("EXECUTION_RISK: Cap {0} < broker min {1}. Skipping trade.", volumeCap, Symbol.VolumeInUnitsMin);
            return -1;
        }

        if (volumeCap < volumeRisk)
            Log("EXECUTION_RISK: Clamping vol {0} -> {1} (slipAssumed={2:F1} maxLoss={3:F2}).",
                volumeRisk, volumeCap, AssumedStopSlippagePips, MaxLossPerTradeAccountCcy);
    }

    double volumeInUnits = Math.Min(volumeRisk, volumeCap);
    volumeInUnits = Symbol.NormalizeVolumeInUnits(volumeInUnits, RoundingMode.Down);

    if (volumeInUnits < Symbol.VolumeInUnitsMin)
    {
        Log("ERROR: Volume {0} < broker min {1}. Cannot trade.", volumeInUnits, Symbol.VolumeInUnitsMin);
        return -1;
    }

    // Safety: max volume cap
    if (MaxVolumeInUnits > 0 && volumeInUnits > MaxVolumeInUnits)
    {
        Log("SAFETY: Volume {0} > MaxVolumeInUnits {1}. Clamping.", volumeInUnits, MaxVolumeInUnits);
        volumeInUnits = Symbol.NormalizeVolumeInUnits(MaxVolumeInUnits, RoundingMode.Down);
        if (volumeInUnits < Symbol.VolumeInUnitsMin)
        {
            Log("ERROR: Clamped volume {0} < min {1}. Cannot trade.", volumeInUnits, Symbol.VolumeInUnitsMin);
            return -1;
        }
    }

    // Safety: margin check
    if (EnableMarginSafety && MaxMarginUsagePercent > 0)
    {
        double freeMargin = System.Convert.ToDouble(Account.FreeMargin);
        if (freeMargin <= 0)
        {
            Log("SAFETY: Free margin <= 0. Skipping trade.");
            return -1;
        }

        double allowedMargin  = freeMargin * (MaxMarginUsagePercent / 100.0);
        double estimatedMargin = Symbol.GetEstimatedMargin(tradeType, volumeInUnits);

        if (estimatedMargin > 0 && estimatedMargin > allowedMargin)
        {
            if (!ClampVolumeToMargin)
            {
                Log("SAFETY: Margin {0:F2} > allowed {1:F2}. Skipping.", estimatedMargin, allowedMargin);
                return -1;
            }

            double clampedVol = Symbol.NormalizeVolumeInUnits(
                volumeInUnits * (allowedMargin / estimatedMargin), RoundingMode.Down);

            if (clampedVol < Symbol.VolumeInUnitsMin)
            {
                Log("SAFETY: Margin clamp would go below min. Skipping.");
                return -1;
            }

            Log("SAFETY: Clamping vol for margin. {0} -> {1}.", volumeInUnits, clampedVol);
            volumeInUnits = clampedVol;
        }
    }

    return volumeInUnits;
}
```

---

### 7.7 Position Management (Multi TP, Dynamic Stop, Early Risk Reduction)

Call `ManageOpenPositions()` on every tick.

```csharp
private void ManageOpenPositions()
{
    foreach (var pos in Positions)
    {
        if (!IsBotPosition(pos) || IsIgnorableDustPosition(pos)) continue;

        PositionState state;
        if (!_positionStates.TryGetValue(pos.Id, out state)) continue;

        double profitPips = pos.Pips;
        double profitR    = profitPips / state.InitialRiskPipsActual;

        if (EnableMultiTp)            ProcessPartialTp(pos, state, profitPips);
        if (EnableEarlyRiskReduction) ProcessEarlyRiskReduction(pos, state, profitR);
        if (EnableDynamicStop)        ProcessDynamicStop(pos, state, profitR);
    }
}

// ── Multi TP ──

private void ProcessPartialTp(Position pos, PositionState state, double profitPips)
{
    if (!state.TP1Done && TP1_R > 0 && _tp1Pct > 0 && profitPips >= TP1_R * state.InitialRiskPipsActual)
        state.TP1Done = ExecutePartialClose(pos, state.InitialVolumeInUnits, _tp1Pct, "TP1", TP1_R);
    if (!state.TP2Done && TP2_R > 0 && _tp2Pct > 0 && profitPips >= TP2_R * state.InitialRiskPipsActual)
        state.TP2Done = ExecutePartialClose(pos, state.InitialVolumeInUnits, _tp2Pct, "TP2", TP2_R);
    if (!state.TP3Done && TP3_R > 0 && _tp3Pct > 0 && profitPips >= TP3_R * state.InitialRiskPipsActual)
        state.TP3Done = ExecutePartialClose(pos, state.InitialVolumeInUnits, _tp3Pct, "TP3", TP3_R);
    if (!state.TP4Done && TP4_R > 0 && _tp4Pct > 0 && profitPips >= TP4_R * state.InitialRiskPipsActual)
        state.TP4Done = ExecutePartialClose(pos, state.InitialVolumeInUnits, _tp4Pct, "TP4", TP4_R);
}

private bool ExecutePartialClose(Position pos, double initialVolume, double closePercent, string label, double tpR)
{
    double desiredClose   = initialVolume * (closePercent / 100.0);
    double minVol         = Symbol.VolumeInUnitsMin;
    double step           = GetVolumeStepSafe();
    double tol            = Math.Max(1e-12, step * 1e-6);
    double requestedClose = NormalizeVolumeDownRequested(desiredClose);

    if (requestedClose < minVol)
    {
        Log("{0} skipped: volume {1} < min {2}. Marking done.", label, requestedClose, minVol);
        return true;
    }

    double maxCloseable = NormalizeVolumeDownSafe(pos.VolumeInUnits);
    double closeVolume  = Math.Min(requestedClose, maxCloseable);

    if (closeVolume < minVol)
        return TryClosePositionSafely(pos, string.Format("{0} (cap<min) at {1:F2}R", label, tpR));

    if (closeVolume >= pos.VolumeInUnits - tol)
        return TryClosePositionSafely(pos, string.Format("{0} FULL CLOSE at {1:F2}R", label, tpR));

    double remainingAfter = pos.VolumeInUnits - closeVolume;
    if (remainingAfter > 0 && remainingAfter < minVol)
    {
        Log("{0} would leave dust {1} < min {2}. Full close instead.", label, remainingAfter, minVol);
        return TryClosePositionSafely(pos, string.Format("{0} DUST FULL CLOSE at {1:F2}R", label, tpR));
    }

    var result = ClosePosition(pos, closeVolume);
    if (result.IsSuccessful)
    {
        Log("{0} partial close: {1:F1}% at {2:F2}R ({3} units)", label, closePercent, tpR, closeVolume);
        return true;
    }

    // BadVolume: step down and retry once
    if (result.Error == ErrorCode.BadVolume && step > 0)
    {
        double v = NormalizeVolumeDownSafe(closeVolume - step);
        if (v >= minVol && v <= pos.VolumeInUnits + tol)
        {
            var r2 = ClosePosition(pos, v);
            if (r2.IsSuccessful)
            {
                Log("{0} partial close (stepped): {1:F1}% at {2:F2}R ({3} units)", label, closePercent, tpR, v);
                return true;
            }
        }
    }

    Log("{0} partial close FAILED: {1}", label, result.Error);
    return false;
}

// ── Early Risk Reduction ──

private void ProcessEarlyRiskReduction(Position pos, PositionState state, double profitR)
{
    if (state.EarlyRiskReductionDone || state.BreakEvenDone) return;
    if (profitR < EarlyRiskReductionTriggerR) return;
    if (EnableDynamicStop && profitR >= BreakEvenTriggerR) return;

    double remainingRiskPips = state.InitialRiskPipsActual * (EarlyRiskReductionRemainingRiskPercent / 100.0);
    double desiredSL = (pos.TradeType == TradeType.Buy)
        ? state.EntryPrice - remainingRiskPips * Symbol.PipSize
        : state.EntryPrice + remainingRiskPips * Symbol.PipSize;
    desiredSL = Math.Round(desiredSL / Symbol.TickSize) * Symbol.TickSize;

    if (pos.StopLoss.HasValue)
    {
        if (pos.TradeType == TradeType.Buy  && desiredSL <= pos.StopLoss.Value) return;
        if (pos.TradeType == TradeType.Sell && desiredSL >= pos.StopLoss.Value) return;
    }

    ModifyPosition(pos, desiredSL, pos.TakeProfit, ProtectionType.Absolute, false, StopTriggerMethod.Trade);
    state.EarlyRiskReductionDone = true;
    Log("EARLY RISK REDUCTION: SL -> {0} (remaining {1:F1}% at {2:F2}R)", desiredSL, EarlyRiskReductionRemainingRiskPercent, profitR);
}

// ── Dynamic Stop (Break Even + Trail) ──

private void ProcessDynamicStop(Position pos, PositionState state, double profitR)
{
    if (profitR < BreakEvenTriggerR) return;

    double desiredSL;

    if (!state.BreakEvenDone)
    {
        desiredSL = (pos.TradeType == TradeType.Buy)
            ? state.EntryPrice + BreakEvenExtraPips * Symbol.PipSize
            : state.EntryPrice - BreakEvenExtraPips * Symbol.PipSize;
        desiredSL = Math.Round(desiredSL / Symbol.TickSize) * Symbol.TickSize;

        bool shouldMove = true;
        if (pos.StopLoss.HasValue)
        {
            if (pos.TradeType == TradeType.Buy  && desiredSL <= pos.StopLoss.Value) shouldMove = false;
            if (pos.TradeType == TradeType.Sell && desiredSL >= pos.StopLoss.Value) shouldMove = false;
        }

        if (shouldMove)
        {
            ModifyPosition(pos, desiredSL, pos.TakeProfit, ProtectionType.Absolute, false, StopTriggerMethod.Trade);
            Log("BREAK EVEN: SL -> {0} (entry + {1} pips)", desiredSL, BreakEvenExtraPips);
        }
        state.BreakEvenDone = true;
    }

    if (DynamicStepR > 0)
    {
        double steps = Math.Floor((profitR - BreakEvenTriggerR) / DynamicStepR);
        if (steps < 0) steps = 0;

        if (steps > state.LastTrailSteps)
        {
            double lockedR    = steps * DynamicStepR;
            double lockInPips = BreakEvenExtraPips + lockedR * state.InitialRiskPipsActual;

            desiredSL = (pos.TradeType == TradeType.Buy)
                ? state.EntryPrice + lockInPips * Symbol.PipSize
                : state.EntryPrice - lockInPips * Symbol.PipSize;
            desiredSL = Math.Round(desiredSL / Symbol.TickSize) * Symbol.TickSize;

            bool shouldMove = true;
            if (pos.StopLoss.HasValue)
            {
                if (pos.TradeType == TradeType.Buy  && desiredSL <= pos.StopLoss.Value) shouldMove = false;
                if (pos.TradeType == TradeType.Sell && desiredSL >= pos.StopLoss.Value) shouldMove = false;
            }

            if (shouldMove)
            {
                ModifyPosition(pos, desiredSL, pos.TakeProfit, ProtectionType.Absolute, false, StopTriggerMethod.Trade);
                Log("TRAIL: SL -> {0} (locked {1:F2}R steps={2} profitR={3:F2})", desiredSL, lockedR, steps, profitR);
            }
            state.LastTrailSteps = steps;
        }
    }
}
```

---

### 7.8 Safe Position Close

Handles broker floating-point residue, `BadVolume` errors, and exponential backoff to prevent log/broker flooding.

```csharp
private bool TryClosePositionSafely(Position pos, string context)
{
    DateTime nowUtc = Server.Time;

    CloseBackoffState st;
    if (_closeBackoffByPosId != null && _closeBackoffByPosId.TryGetValue(pos.Id, out st))
        if (nowUtc < st.NextAttemptUtc) return false;

    double minVol  = Symbol.VolumeInUnitsMin;
    double step    = GetVolumeStepSafe();
    double posVol  = pos.VolumeInUnits;
    double tol     = Math.Max(1e-12, step * 1e-6);

    if (IsIgnorableDustVolume(posVol))
    {
        if (_closeBackoffByPosId != null) _closeBackoffByPosId.Remove(pos.Id);
        LogCloseFailThrottled(pos.Id, "{0}: Dust position {1} vol={2}. Ignoring.", context, pos.Label, posVol);
        return true;
    }

    double closeVol = NormalizeVolumeDownSafe(posVol);
    if (closeVol < minVol && posVol >= minVol - tol)
        closeVol = NormalizeVolumeNearestStrict(minVol);

    if (closeVol < minVol)
    {
        LogCloseFailThrottled(pos.Id, "{0}: STUCK {1} vol={2} < min={3}.", context, pos.Label, posVol, minVol);
        ScheduleCloseBackoff(pos.Id, nowUtc, hardFail: true);
        return false;
    }

    if (closeVol > posVol + tol)
        closeVol = NormalizeVolumeDownSafe(posVol);

    var res = ClosePosition(pos, closeVol);
    if (res.IsSuccessful)
    {
        bool fullyClosed = closeVol >= posVol - tol;
        Log("{0}: CLOSE {1} {2} closeVol={3} P/L={4:F2}", context, fullyClosed ? "OK" : "PARTIAL",
            pos.Label, closeVol, pos.NetProfit);
        if (fullyClosed && _closeBackoffByPosId != null) _closeBackoffByPosId.Remove(pos.Id);
        else if (_closeBackoffByPosId != null)
            _closeBackoffByPosId[pos.Id] = new CloseBackoffState { FailCount = 0, NextAttemptUtc = nowUtc.AddSeconds(1) };
        return fullyClosed;
    }

    if (res.Error == ErrorCode.BadVolume && step > 0)
    {
        double v = closeVol;
        for (int i = 0; i < 2; i++)
        {
            v = NormalizeVolumeDownSafe(v - step);
            if (v < minVol || v > posVol + tol) break;
            var r2 = ClosePosition(pos, v);
            if (r2.IsSuccessful)
            {
                Log("{0}: CLOSE OK (stepped) {1} closeVol={2} P/L={3:F2}", context, pos.Label, v, pos.NetProfit);
                if (_closeBackoffByPosId != null) _closeBackoffByPosId.Remove(pos.Id);
                return true;
            }
            if (r2.Error != ErrorCode.BadVolume) break;
        }
    }

    LogCloseFailThrottled(pos.Id, "{0}: FAILED {1} posVol={2} closeVol={3} err={4}",
        context, pos.Label, posVol, closeVol, res.Error);
    ScheduleCloseBackoff(pos.Id, nowUtc, hardFail: false);
    return false;
}

private void ScheduleCloseBackoff(long posId, DateTime nowUtc, bool hardFail)
{
    if (_closeBackoffByPosId == null) return;
    CloseBackoffState st;
    if (!_closeBackoffByPosId.TryGetValue(posId, out st))
        st = new CloseBackoffState { FailCount = 0, NextAttemptUtc = nowUtc };
    st.FailCount = Math.Max(0, st.FailCount + 1);
    int fc = st.FailCount;
    int delay = hardFail ? 30 : (fc >= 10 ? 300 : fc >= 6 ? 60 : fc >= 4 ? 30 : fc >= 3 ? 10 : fc >= 2 ? 5 : 2);
    st.NextAttemptUtc = nowUtc.AddSeconds(delay);
    _closeBackoffByPosId[posId] = st;
}

private void CloseAllBotPositions(string reason)
{
    foreach (var pos in Positions.ToArray())
        if (IsBotPosition(pos) && !IsIgnorableDustPosition(pos))
            TryClosePositionSafely(pos, reason + " FORCE CLOSE");
}

private void LogCloseFailThrottled(long posId, string format, params object[] args)
{
    DateTime nowUtc = Server.Time;
    DateTime lastLog;
    if (_lastCloseFailLogUtcByPosId != null && _lastCloseFailLogUtcByPosId.TryGetValue(posId, out lastLog))
        if ((nowUtc - lastLog).TotalSeconds < 10) return;
    if (_lastCloseFailLogUtcByPosId != null) _lastCloseFailLogUtcByPosId[posId] = nowUtc;
    Log(format, args);
}
```

---

### 7.9 Position Closed Handler

Wire this up in `OnStart()` with `Positions.Closed += OnPositionsClosed` and unsubscribe in `OnStop()`.

```csharp
private void OnPositionsClosed(PositionClosedEventArgs args)
{
    var pos = args.Position;
    if (!IsBotPosition(pos)) return;

    _positionStates.Remove(pos.Id);
    if (_lastCloseFailLogUtcByPosId != null) _lastCloseFailLogUtcByPosId.Remove(pos.Id);
    if (_closeBackoffByPosId        != null) _closeBackoffByPosId.Remove(pos.Id);

    Log("POSITION CLOSED: {0} reason={1} P/L={2:F2} pips={3:F1}",
        pos.Label, args.Reason, pos.NetProfit, pos.Pips);

    if (VerboseLogging)
    {
        string commStr; string swapStr;
        try { commStr = pos.Commissions.ToString("F2"); } catch { commStr = "N/A"; }
        try { swapStr = pos.Swap.ToString("F2"); }        catch { swapStr = "N/A"; }

        Print("[{0}] CLOSE_DIAG label={1} reason={2} net={3:F2} gross={4:F2} commission={5} swap={6} pips={7:F1} entry={8} balance={9:F2} equity={10:F2} margin={11:F2} freeMargin={12:F2} marginLevel={13}",
            BotLabelPrefix, pos.Label, args.Reason,
            pos.NetProfit, pos.GrossProfit, commStr, swapStr,
            pos.Pips, pos.EntryPrice,
            Account.Balance, Account.Equity, Account.Margin, Account.FreeMargin,
            (!Account.MarginLevel.HasValue || double.IsNaN(Account.MarginLevel.Value) || double.IsInfinity(Account.MarginLevel.Value))
                ? "N/A" : Account.MarginLevel.Value.ToString("F2"));
    }
}
```

---

### 7.10 Restart Safety — Trade Count Rehydration

Ensures `_tradesToday` is correct even if the bot restarts mid-session.

```csharp
private string GetBotLabelForDate(DateTime sessionDate)
{
    return string.Format("{0}_{1}_{2}", BotLabelPrefix, SymbolName, sessionDate.ToString("yyyyMMdd"));
}

private int GetTradesExecutedForSessionDate(DateTime sessionDate)
{
    string label = GetBotLabelForDate(sessionDate);
    var ids = new HashSet<long>();

    foreach (var pos in Positions)
    {
        if (pos == null || pos.SymbolName != SymbolName || pos.Label != label) continue;
        if (IsIgnorableDustPosition(pos)) continue;
        ids.Add(pos.Id);
    }

    try
    {
        var hist = History.FindAll(label, SymbolName);
        if (hist != null)
            foreach (var ht in hist)
                try { ids.Add(ht.PositionId); } catch { }
    }
    catch { }

    return ids.Count;
}

private void RehydrateTradesTodayFromHistory(string context)
{
    try
    {
        int found = GetTradesExecutedForSessionDate(_currentSessionDate);
        if (found != _tradesToday)
            Log("RESTART SAFETY [{0}]: tradesToday was {1}, rehydrated to {2} (max={3}).",
                context, _tradesToday, found, MaxTradesPerDay);
        _tradesToday = found;
    }
    catch (Exception ex)
    {
        Log("RESTART SAFETY: Failed to rehydrate tradesToday. {0}", ex.Message);
    }
}
```

---

### 7.11 Diagnostics / Logging

```csharp
private void Log(string message, params object[] args)
{
    if (!EnableDebugLogging) return;
    string formatted;
    if (args != null && args.Length > 0)
        try { formatted = string.Format(message, args); } catch { formatted = message; }
    else
        formatted = message;
    Print("[{0}] {1} {2}", BotLabelPrefix, Server.Time.ToString("yyyy-MM-dd HH:mm:ss"), formatted);
}
```

**Entry diagnostic (call after a successful order fill, inside your `EnterTrade()`):**

```csharp
if (VerboseLogging)
{
    Print("[{0}] ENTRY_DIAG symbol={1} side={2} volume={3} entry={4} sl={5} tp={6} riskPips={7:F2} spread={8:F4} balance={9:F2} equity={10:F2} margin={11:F2} freeMargin={12:F2} marginLevel={13}",
        BotLabelPrefix, SymbolName, tradeType, position.VolumeInUnits,
        position.EntryPrice, slPriceApplied, tpPriceApplied, riskPipsApplied,
        Symbol.Ask - Symbol.Bid,
        Account.Balance, Account.Equity, Account.Margin, Account.FreeMargin,
        (!Account.MarginLevel.HasValue || double.IsNaN(Account.MarginLevel.Value))
            ? "N/A" : Account.MarginLevel.Value.ToString("F2"));
}
```

---

### 7.12 Volume Normalisation Helpers

These prevent `BadVolume` errors from double floating-point representation issues.

```csharp
private double GetVolumeStepSafe()
{
    double step = Symbol.VolumeInUnitsStep;
    return step > 0 ? step : Symbol.VolumeInUnitsMin;
}

private int GetStepDecimals(double step)
{
    if (step <= 0) return 2;
    int decimals = 0;
    double s = step;
    while (decimals < 8 && Math.Abs(s - Math.Round(s)) > 1e-12) { s *= 10.0; decimals++; }
    return decimals;
}

// For close volumes of remaining positions — guarantees result <= input.
private double NormalizeVolumeDownSafe(double volume)
{
    double step = Symbol.VolumeInUnitsStep;
    if (step <= 0) return Symbol.NormalizeVolumeInUnits(volume, RoundingMode.Down);
    double eps   = Math.Max(1e-12, step * 1e-9);
    double steps = Math.Floor((volume + eps) / step);
    int    dec   = GetStepDecimals(step);
    double v     = Math.Round(steps * step, dec, MidpointRounding.AwayFromZero);
    while (v > volume && v - step >= 0)
        v = Math.Round(v - step, dec, MidpointRounding.AwayFromZero);
    return Math.Max(0, v);
}

// For requested/target volumes (e.g. partial TP sizes) — avoids off-by-one from float noise.
private double NormalizeVolumeDownRequested(double volume)
{
    double step = Symbol.VolumeInUnitsStep;
    if (step <= 0) return Symbol.NormalizeVolumeInUnits(volume, RoundingMode.Down);
    double eps   = Math.Max(1e-12, step * 1e-9);
    double steps = Math.Floor((volume + eps) / step);
    int    dec   = GetStepDecimals(step);
    return Math.Max(0, Math.Round(steps * step, dec, MidpointRounding.AwayFromZero));
}

// For snapping to nearest step (used when volume is just fractionally below min).
private double NormalizeVolumeNearestStrict(double volume)
{
    double step = Symbol.VolumeInUnitsStep;
    if (step <= 0) return Symbol.NormalizeVolumeInUnits(volume, RoundingMode.ToNearest);
    double steps = Math.Round(volume / step, MidpointRounding.AwayFromZero);
    int    dec   = GetStepDecimals(step);
    return Math.Max(0, Math.Round(steps * step, dec, MidpointRounding.AwayFromZero));
}

private bool IsIgnorableDustVolume(double volume)
{
    double step = GetVolumeStepSafe();
    double dust = Math.Max(1e-12, Math.Min(Symbol.VolumeInUnitsMin, step) * 1e-3);
    return volume <= dust;
}

private bool IsIgnorableDustPosition(Position pos) => IsIgnorableDustVolume(pos.VolumeInUnits);
```

---

### 7.13 Position Identification Helpers

```csharp
private bool IsBotPosition(Position pos)
{
    if (pos.SymbolName != SymbolName) return false;
    if (string.IsNullOrEmpty(pos.Label)) return false;
    return pos.Label.StartsWith(string.Format("{0}_{1}_", BotLabelPrefix, SymbolName));
}

private bool HasOpenBotPosition()
{
    foreach (var pos in Positions)
        if (IsBotPosition(pos) && !IsIgnorableDustPosition(pos)) return true;
    return false;
}

private Position GetFirstOpenBotPosition()
{
    foreach (var pos in Positions)
        if (IsBotPosition(pos) && !IsIgnorableDustPosition(pos)) return pos;
    return null;
}

private void RegisterExistingPosition(Position pos)
{
    if (_positionStates.ContainsKey(pos.Id)) return;
    if (!pos.StopLoss.HasValue)
    {
        Log("WARNING: Existing position {0} has no SL. Cannot register.", pos.Label);
        return;
    }
    double riskPips = Math.Abs(pos.EntryPrice - pos.StopLoss.Value) / Symbol.PipSize;
    if (riskPips <= 0) riskPips = 1;
    _positionStates[pos.Id] = new PositionState
    {
        PositionId             = pos.Id,
        EntryPrice             = pos.EntryPrice,
        SLPriceInitial         = pos.StopLoss.Value,
        InitialRiskPipsActual  = riskPips,
        InitialVolumeInUnits   = pos.VolumeInUnits,
        EarlyRiskReductionDone = false,
        BreakEvenDone          = false,
        TP1Done = false, TP2Done = false, TP3Done = false, TP4Done = false,
        LastTrailSteps         = -1
    };
    Log("Registered existing position {0} riskPips={1:F1}", pos.Label, riskPips);
}

// ── Multi TP helpers (call in OnStart) ──

private void NormalizeMultiTpPercents()
{
    _tp1Pct = (TP1_R > 0 && TP1_ClosePercent > 0) ? TP1_ClosePercent : 0;
    _tp2Pct = (TP2_R > 0 && TP2_ClosePercent > 0) ? TP2_ClosePercent : 0;
    _tp3Pct = (TP3_R > 0 && TP3_ClosePercent > 0) ? TP3_ClosePercent : 0;
    _tp4Pct = (TP4_R > 0 && TP4_ClosePercent > 0) ? TP4_ClosePercent : 0;
    double total = _tp1Pct + _tp2Pct + _tp3Pct + _tp4Pct;
    if (total > 100 && total > 0)
    {
        double scale = 100.0 / total;
        _tp1Pct *= scale; _tp2Pct *= scale; _tp3Pct *= scale; _tp4Pct *= scale;
        Log("Multi TP normalised: TP1={0:F1}% TP2={1:F1}% TP3={2:F1}% TP4={3:F1}%",
            _tp1Pct, _tp2Pct, _tp3Pct, _tp4Pct);
    }
}

private void ComputeMaxTpR()
{
    _maxTpR = TakeProfitR;
    if (!EnableMultiTp) return;
    if (TP1_R > 0 && _tp1Pct > 0 && TP1_R > _maxTpR) _maxTpR = TP1_R;
    if (TP2_R > 0 && _tp2Pct > 0 && TP2_R > _maxTpR) _maxTpR = TP2_R;
    if (TP3_R > 0 && _tp3Pct > 0 && TP3_R > _maxTpR) _maxTpR = TP3_R;
    if (TP4_R > 0 && _tp4Pct > 0 && TP4_R > _maxTpR) _maxTpR = TP4_R;
}
```

---

## 8. Integration Notes for Strategy-Specific Code

When building a new cBot using this reference:

1. **Copy all enums and support classes** from section 1 into the namespace.
2. **Copy all base parameters** from section 2. Add your strategy-specific parameters below them.
3. **Copy all internal state variables** from section 3. Add your own strategy state below them.
4. **In `OnStart()`**, copy the base initialisation block first, then add your strategy initialisation (bars, indicators, etc.) after the comment `// 8. Strategy-specific initialisation goes here`.
5. **In `OnTick()`**, copy the base block. Insert your signal detection and `EnterTrade()` call where indicated by `// ── STRATEGY-SPECIFIC LOGIC GOES HERE ──`.
6. **`EnterTrade()` is strategy-specific** and is NOT part of this base. However, every `EnterTrade()` implementation must:
   - Compute `estimatedRiskPips` from SL distance
   - Call `ComputeVolume(tradeType, estimatedRiskPips, effectiveTpR)` — returns -1 to abort
   - Call `ExecuteMarketOrder(...)` with the label `GetBotLabelForDate(_currentSessionDate)`
   - Apply SL and TP with `ModifyPosition(...)` — use `TryApplyInitialProtectionWithFallback(...)` pattern
   - Verify `position.StopLoss.HasValue` after — close and return if not
   - Increment `_tradesToday++`
   - Create and store a `PositionState` in `_positionStates[position.Id]`
   - Call verbose entry diagnostic if `VerboseLogging`
7. **Entry gate checklist** — every signal evaluation must check these gates in order before calling `EnterTrade()`:
   - `if (_noTradeToday) return;`
   - `if (nowUtc < _tradingStartUtcToday) return;`
   - `if (EnableClosePositionsTime && nowUtc >= _closePositionsUtcToday) return;`
   - `if (EnableKillSwitch && nowUtc >= _killSwitchUtcToday) return;`
   - `if (HasOpenBotPosition()) return;`
   - `if (_tradesToday >= MaxTradesPerDay) return;`
   - `if (MaxSpreadPips > 0 && spread > MaxSpreadPips) return;`

---

## 9. Common Misconfiguration Warnings

The bot should log these at startup (add to end of `OnStart()`):

```csharp
// Warn if kill switch would prevent any entries
DateTime earliestEntry = _sessionEndUtcToday > _tradingStartUtcToday
    ? _sessionEndUtcToday : _tradingStartUtcToday;

if (EnableKillSwitch && _killSwitchUtcToday <= earliestEntry)
    Print("WARNING: KillSwitchTime ({0:HH:mm}) <= earliest possible entry ({1:HH:mm}). Zero trades will occur.",
        _killSwitchUtcToday, earliestEntry);

if (EnableClosePositionsTime && _closePositionsUtcToday <= earliestEntry)
    Print("WARNING: ClosePositionsTime ({0:HH:mm}) <= earliest possible entry ({1:HH:mm}). Zero trades will occur.",
        _closePositionsUtcToday, earliestEntry);

if (EnableKillSwitch && _tradingStartUtcToday >= _killSwitchUtcToday)
    Print("WARNING: TradingStartTime >= KillSwitchTime. No entries possible.");

if (_tradingStartUtcToday < _sessionEndUtcToday)
    Print("INFO: TradingStartTime ({0:HH:mm}) is before SessionEnd ({1:HH:mm}). Bot will wait for session to end before entering.",
        _tradingStartUtcToday, _sessionEndUtcToday);
```

---

*End of reference document. Version: 2026-04-15*
