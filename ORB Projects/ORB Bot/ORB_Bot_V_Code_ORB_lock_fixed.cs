// =============================================================================
// ORB Breakout cBot - Opening Range Breakout Strategy (Missed Trade Fix + Diagnostics)
// Single compilable .cs file for cTrader Automate
// =============================================================================

using System;
using System.Collections.Generic;
using System.Linq;
using cAlgo.API;
using cAlgo.API.Indicators;
using cAlgo.API.Internals;

namespace cAlgo.Robots
{
 // =========================================================================
 // ENUMS
 // =========================================================================

 public enum PointUnitMode
 {
 UseTickSizeAsPoint,
 UsePipSizeAsPoint
 }
 public enum ReEntryMode
 {
 AfterStopLossOnly,
 AfterAnyExit
 }

 public enum CandleDirectionRequirement
 {
 NoPreference,
 RequireBullishForLong_RequireBearishForShort
 }

 public enum BreakoutCrossType
 {
 CloseBeyond,
 BodyCross,
 WickBeyond
 }

 public enum BreakoutEvaluationMoment
 {
 ClosedBarsOnly,
 AllowIntrabar
 }

 public enum RiskCurrency
 {
 AccountCurrency,
 GBP,
 USD
 }

 public enum TrendNeutralPolicy
 {
 BlockAll,
 AllowBoth,
 AllowIfPriceVsEma,
 AllowIfEmaSlope,
 AllowIfEmaVsVwap
 }

 public enum SessionTimeZoneEnum
 {
 UTC,
 EuropeLondon,
 EuropeBerlin,
 AmericaNewYork
 }

 // =========================================================================
 // PER-POSITION STATE TRACKER
 // =========================================================================

 public class PositionState
 {
 public long PositionId { get; set; }
 public double EntryPrice { get; set; }
 public double SLPriceInitial { get; set; }
 public double InitialRiskPipsActual { get; set; }
 public double InitialVolumeInUnits { get; set; }
 public bool EarlyRiskReductionDone { get; set; }
 public bool BreakEvenDone { get; set; }
 public bool TP1Done { get; set; }
 public bool TP2Done { get; set; }
 public bool TP3Done { get; set; }
 public bool TP4Done { get; set; }
 public double LastTrailSteps { get; set; }
 }

 public class CloseBackoffState
 {
 public int FailCount { get; set; }
 public DateTime NextAttemptUtc { get; set; }
 }


 // =========================================================================
 // MAIN CBOT CLASS
 // =========================================================================

 [Robot(TimeZone = TimeZones.UTC, AccessRights = AccessRights.None)]
 public class OrbBreakoutBot : Robot
 {
 // =====================================================================
 // PARAMETERS
 // =====================================================================

 // ----- Session (UTC) -----
 [Parameter("Range Start Time", Group = "Session (UTC)", DefaultValue = "08:00:00")]
 public string RangeStartTimeUtcStr { get; set; }

 [Parameter("Range End Time", Group = "Session (UTC)", DefaultValue = "08:15:00")]
 public string RangeEndTimeUtcStr { get; set; }

 [Parameter("Trading Start Time", Group = "Session (UTC)", DefaultValue = "00:00:00")]
 public string TradingStartTimeUtcStr { get; set; }

 [Parameter("Enable Kill Switch", Group = "Session (UTC)", DefaultValue = false)]
 public bool EnableKillSwitch { get; set; }

 [Parameter("Kill Switch Time", Group = "Session (UTC)", DefaultValue = "23:59:00")]
 public string KillSwitchTimeUtcStr { get; set; }

 // NOTE: This setting USED to close positions at the same Kill Switch Time.
 // It now enables a *separate* Close Positions Time (see parameter below).
 [Parameter("Enable Close Positions Time", Group = "Session (UTC)", DefaultValue = false)]
 public bool ClosePositionsAtKillSwitch { get; set; }

 [Parameter("Close Positions Time", Group = "Session (UTC)", DefaultValue = "23:59:00")]
 public string ClosePositionsTimeUtcStr { get; set; }

 // ----- Session Time Zone -----
 [Parameter("Use Fixed UTC Times", Group = "Session Time Zone", DefaultValue = true)]
 public bool UseFixedUtcTimes { get; set; }

 [Parameter("Session Time Zone", Group = "Session Time Zone", DefaultValue = SessionTimeZoneEnum.UTC)]
 public SessionTimeZoneEnum SessionTimeZoneParam { get; set; }

 // ----- ORB -----
 [Parameter("ORB Bars TimeFrame", Group = "ORB", DefaultValue = "Minute")]
 public TimeFrame OrbBarsTimeFrame { get; set; }

 [Parameter("Max ORB Range Pips", Group = "ORB", DefaultValue = 200)]
 public double MaxOrbRangePips { get; set; }

 [Parameter("Min ORB Range Pips", Group = "ORB", DefaultValue = 0.0)]
 public double MinOrbRangePips { get; set; }

 [Parameter("Point Unit Mode", Group = "ORB", DefaultValue = PointUnitMode.UsePipSizeAsPoint)]
 public PointUnitMode PointUnitModeParam { get; set; }

 // --- ORB Robustness (Backfill / Self-Heal) ---
 [Parameter("Enable ORB Backfill", Group = "ORB", DefaultValue = true)]
 public bool EnableOrbBackfill { get; set; }

 [Parameter("Enable ORB Self-Heal", Group = "ORB", DefaultValue = true)]
 public bool EnableOrbSelfHeal { get; set; }

 [Parameter("ORB Self-Heal Interval Seconds", Group = "ORB", DefaultValue = 30, MinValue = 5)]
 public int OrbSelfHealIntervalSeconds { get; set; }

 // --- ORB Robustness (Post-lock confirmation replay) ---
 // If ORB locks late (e.g., backfill/self-heal) we can miss the very first breakout candle.
 // This re-checks the most recent closed confirmation bar(s) immediately after the ORB locks.
 // It is intentionally time-limited to avoid "late" entries hours after the ORB window.
 [Parameter("Enable Post-Lock Confirm Replay", Group = "ORB", DefaultValue = true)]
 public bool EnablePostLockConfirmReplay { get; set; }

 [Parameter("Post-Lock Replay Confirm Bars", Group = "ORB", DefaultValue = 1, MinValue = 1, MaxValue = 5)]
 public int PostLockReplayConfirmBars { get; set; }

 [Parameter("Post-Lock Replay Max Delay Minutes", Group = "ORB", DefaultValue = 20, MinValue = 1, MaxValue = 240)]
 public int PostLockReplayMaxDelayMinutes { get; set; }



 // ----- Catch-Up Entry (optional) -----
 // Purpose: If you intentionally start trading LATER than the ORB build window (e.g., build ORB 09:00-09:15
 // but only allow entries from 10:20), this can optionally join a move that is already outside the ORB
 // thresholds at/after TradingStart.
 [Parameter("Enable Catch-Up Entry", Group = "Catch-Up Entry", DefaultValue = false)]
 public bool EnableCatchUpEntry { get; set; }

 [Parameter("Catch-Up Requires Confirmation Bars", Group = "Catch-Up Entry", DefaultValue = true)]
 public bool CatchUpRequiresConfirmationBars { get; set; }

 [Parameter("Catch-Up Max Distance Beyond Threshold Pips", Group = "Catch-Up Entry", DefaultValue = 0.0, MinValue = 0.0)]
 public double CatchUpMaxDistanceBeyondThresholdPips { get; set; }
 // ----- Entry Offset -----
 // Manual-only entry offset. Dynamic ATR offset has been removed so that entry thresholds are
 // always based on this fixed value for the day.
 // LongThreshold = ORB High + Entry Offset
 // ShortThreshold = ORB Low - Entry Offset
 [Parameter("Entry Offset Pips", Group = "Entry Offset", DefaultValue = 10)]
 public double EntryOffsetPipsManual { get; set; }


 // ----- Breakout -----
 [Parameter("Confirmation TimeFrame", Group = "Breakout", DefaultValue = "Minute5")]
 public TimeFrame ConfirmationTimeFrame { get; set; }

 [Parameter("Confirmation Bars Count", Group = "Breakout", DefaultValue = 1, MinValue = 1)]
 public int ConfirmationBarsCount { get; set; }

 [Parameter("Breakout Cross Type", Group = "Breakout", DefaultValue = BreakoutCrossType.CloseBeyond)]
 public BreakoutCrossType BreakoutCrossTypeParam { get; set; }

 [Parameter("Breakout Evaluation Moment", Group = "Breakout", DefaultValue = BreakoutEvaluationMoment.ClosedBarsOnly)]
 public BreakoutEvaluationMoment BreakoutEvaluationMomentParam { get; set; }

 [Parameter("Candle Direction Requirement", Group = "Breakout", DefaultValue = CandleDirectionRequirement.NoPreference)]
 public CandleDirectionRequirement CandleDirectionRequirementParam { get; set; }

 [Parameter("Allow Long", Group = "Breakout", DefaultValue = true)]
 public bool AllowLong { get; set; }

 [Parameter("Allow Short", Group = "Breakout", DefaultValue = true)]
 public bool AllowShort { get; set; }

 // ----- Trend Filter -----
 [Parameter("Enable Trend Filter", Group = "Trend Filter", DefaultValue = false)]
 public bool EnableTrendFilter { get; set; }

 [Parameter("Trend TimeFrame", Group = "Trend Filter", DefaultValue = "Minute15")]
 public TimeFrame TrendTimeFrame { get; set; }

 [Parameter("Trend EMA Period", Group = "Trend Filter", DefaultValue = 9, MinValue = 1)]
 public int TrendEmaPeriod { get; set; }

 [Parameter("Trend Slope Lookback Bars", Group = "Trend Filter", DefaultValue = 3, MinValue = 1)]
 public int TrendSlopeLookbackBars { get; set; }

 [Parameter("Trend Min Slope Pips", Group = "Trend Filter", DefaultValue = 0.0)]
 public double TrendMinSlopePips { get; set; }

 [Parameter("Neutral Min Slope Pips", Group = "Trend Filter", DefaultValue = 0.0)]
 public double NeutralMinSlopePips { get; set; }

 [Parameter("Trend Neutral Policy", Group = "Trend Filter", DefaultValue = TrendNeutralPolicy.BlockAll)]
 public TrendNeutralPolicy TrendNeutralPolicyParam { get; set; }

 [Parameter("Trend Filter Verbose Logs", Group = "Trend Filter", DefaultValue = false)]
 public bool TrendFilterVerboseLogs { get; set; }

 // ----- Trades Per Day -----
 [Parameter("Max Trades Per Day", Group = "Trades Per Day", DefaultValue = 1, MinValue = 1)]
 public int MaxTradesPerDay { get; set; }

 [Parameter("Re-Entry Mode", Group = "Trades Per Day", DefaultValue = ReEntryMode.AfterStopLossOnly)]
 public ReEntryMode ReEntryModeParam { get; set; }

 // ----- Trading Days -----
 [Parameter("Trade Monday", Group = "Trading Days", DefaultValue = true)]
 public bool TradeMonday { get; set; }

 [Parameter("Trade Tuesday", Group = "Trading Days", DefaultValue = true)]
 public bool TradeTuesday { get; set; }

 [Parameter("Trade Wednesday", Group = "Trading Days", DefaultValue = true)]
 public bool TradeWednesday { get; set; }

 [Parameter("Trade Thursday", Group = "Trading Days", DefaultValue = true)]
 public bool TradeThursday { get; set; }

 [Parameter("Trade Friday", Group = "Trading Days", DefaultValue = true)]
 public bool TradeFriday { get; set; }

 [Parameter("Trade Saturday", Group = "Trading Days", DefaultValue = false)]
 public bool TradeSaturday { get; set; }

 [Parameter("Trade Sunday", Group = "Trading Days", DefaultValue = false)]
 public bool TradeSunday { get; set; }

 // ----- Stops & Targets -----
 [Parameter("Stop Loss ORB Percent", Group = "Stops & Targets", DefaultValue = 50.0)]
 public double StopLossOrbPercent { get; set; }

 [Parameter("Take Profit R", Group = "Stops & Targets", DefaultValue = 2.0)]
 public double TakeProfitR { get; set; }

 // ----- Multi Take Profit -----
 [Parameter("Enable Multi TP", Group = "Multi Take Profit", DefaultValue = false)]
 public bool EnableMultiTp { get; set; }

 [Parameter("TP1 R", Group = "Multi Take Profit", DefaultValue = 1.0)]
 public double TP1_R { get; set; }

 [Parameter("TP1 Close Percent", Group = "Multi Take Profit", DefaultValue = 50)]
 public double TP1_ClosePercent { get; set; }

 [Parameter("TP2 R", Group = "Multi Take Profit", DefaultValue = 2.0)]
 public double TP2_R { get; set; }

 [Parameter("TP2 Close Percent", Group = "Multi Take Profit", DefaultValue = 50)]
 public double TP2_ClosePercent { get; set; }

 [Parameter("TP3 R", Group = "Multi Take Profit", DefaultValue = 0.0)]
 public double TP3_R { get; set; }

 [Parameter("TP3 Close Percent", Group = "Multi Take Profit", DefaultValue = 0)]
 public double TP3_ClosePercent { get; set; }

 [Parameter("TP4 R", Group = "Multi Take Profit", DefaultValue = 0.0)]
 public double TP4_R { get; set; }

 [Parameter("TP4 Close Percent", Group = "Multi Take Profit", DefaultValue = 0)]
 public double TP4_ClosePercent { get; set; }

 // ----- Dynamic Stop -----
 [Parameter("Enable Dynamic Stop", Group = "Dynamic Stop", DefaultValue = false)]
 public bool EnableDynamicStop { get; set; }

 [Parameter("Break Even Trigger R", Group = "Dynamic Stop", DefaultValue = 1.0)]
 public double BreakEvenTriggerR { get; set; }

 [Parameter("Dynamic Step R", Group = "Dynamic Stop", DefaultValue = 0.25)]
 public double DynamicStepR { get; set; }

 [Parameter("Break Even Extra Pips", Group = "Dynamic Stop", DefaultValue = 0.0)]
 public double BreakEvenExtraPips { get; set; }

 // ----- Early Risk Reduction -----
 [Parameter("Enable Early Risk Reduction", Group = "Early Risk Reduction", DefaultValue = false)]
 public bool EnableEarlyRiskReduction { get; set; }

 [Parameter("Early Risk Reduction Trigger R", Group = "Early Risk Reduction", DefaultValue = 0.5)]
 public double EarlyRiskReductionTriggerR { get; set; }

 [Parameter("Early Risk Reduction Remaining Risk %", Group = "Early Risk Reduction", DefaultValue = 50.0)]
 public double EarlyRiskReductionRemainingRiskPercent { get; set; }

 // ----- Risk -----
 [Parameter("Risk Amount", Group = "Risk", DefaultValue = 100)]
 public double RiskAmount { get; set; }

 [Parameter("Risk Currency", Group = "Risk", DefaultValue = RiskCurrency.AccountCurrency)]
 public RiskCurrency RiskCurrencyParam { get; set; }

 // ----- Execution Risk (Slippage / Gaps) -----
 [Parameter("Enable Execution Risk Cap", Group = "Execution Risk", DefaultValue = true)]
 public bool EnableExecutionRiskCap { get; set; }

 [Parameter("Assumed Stop Slippage Pips", Group = "Execution Risk", DefaultValue = 80.0, MinValue = 0.0)]
 public double AssumedStopSlippagePips { get; set; }

 [Parameter("Max Loss Per Trade (Account CCY)", Group = "Execution Risk", DefaultValue = 200.0, MinValue = 0.0)]
 public double MaxLossPerTradeAccountCcy { get; set; }

 // ----- Safety -----
 [Parameter("Min Risk Pips", Group = "Safety", DefaultValue = 2.0)]
 public double MinRiskPips { get; set; }

 [Parameter("Max Volume In Units", Group = "Safety", DefaultValue = 0)]
 public double MaxVolumeInUnits { get; set; }

 [Parameter("Max Spread Pips", Group = "Safety", DefaultValue = 0)]
 public double MaxSpreadPips { get; set; }

 [Parameter("Max Distance Beyond Threshold Pips", Group = "Safety", DefaultValue = 0)]
 public double MaxDistanceBeyondThresholdPips { get; set; }

 [Parameter("Require Entry Beyond Threshold", Group = "Safety", DefaultValue = true)]
 public bool RequireEntryBeyondThreshold { get; set; }

 [Parameter("Enable Margin Safety", Group = "Safety", DefaultValue = true)]
 public bool EnableMarginSafety { get; set; }

 [Parameter("Max Margin Usage %", Group = "Safety", DefaultValue = 50.0, MinValue = 1, MaxValue = 100)]
 public double MaxMarginUsagePercent { get; set; }

 [Parameter("Clamp Volume To Margin", Group = "Safety", DefaultValue = true)]
 public bool ClampVolumeToMargin { get; set; }

 // ----- Protection Fallback (Safety) -----
 [Parameter("Enable Protection Fallback", Group = "Safety", DefaultValue = true)]
 public bool EnableProtectionFallback { get; set; }

 [Parameter("Fallback SL Pips", Group = "Safety", DefaultValue = 20.0, MinValue = 0.0)]
 public double FallbackStopLossPips { get; set; }


 // ----- Diagnostics -----
 [Parameter("Bot Label Prefix", Group = "Diagnostics", DefaultValue = "ORB")]
 public string BotLabelPrefix { get; set; }

 [Parameter("Enable Debug Logging", Group = "Diagnostics", DefaultValue = true)]
 public bool EnableDebugLogging { get; set; }

 [Parameter("Verbose Logging", Group = "Diagnostics", DefaultValue = false)]
 public bool VerboseLogging { get; set; }

 [Parameter("Explain Blocked Entries", Group = "Diagnostics", DefaultValue = true)]
 public bool ExplainBlockedEntries { get; set; }

 [Parameter("Explain Near-Miss Breakouts", Group = "Diagnostics", DefaultValue = false)]
 public bool ExplainNearMissBreakouts { get; set; }

 [Parameter("Draw ORB Lines", Group = "Diagnostics", DefaultValue = true)]
 public bool DrawOrbLines { get; set; }

 [Parameter("Draw Threshold Lines", Group = "Diagnostics", DefaultValue = true)]
 public bool DrawThresholdLines { get; set; }

 // =====================================================================
 // INTERNAL STATE
 // =====================================================================

 // Parsed time spans (configured values, may be local or UTC)
 private TimeSpan _rangeStartTimeCfg;
 private TimeSpan _rangeEndTimeCfg;
 private TimeSpan _tradingStartTimeCfg;
 private TimeSpan _killSwitchTimeCfg;
 private TimeSpan _closePositionsTimeCfg;

 // Session timezone
 private TimeZoneInfo _sessionTz;

 // Daily UTC-converted session boundaries
 private DateTime _orbStartUtcToday;
 private DateTime _orbEndUtcToday;
 private DateTime _tradingStartUtcToday;
 private DateTime _killSwitchUtcToday;
 private DateTime _closePositionsUtcToday;

 // Bar series
 private Bars _orbBars;
 private Bars _confirmBars;
 private Bars _trendBars;

 // Indicators
 private ExponentialMovingAverage _trendEma;

 // Point size (pip or tick depending on PointUnitMode)
 private double _pointSize;

 // Daily state
 private DateTime _currentSessionDate;
 private double _orbHigh;
 private double _orbLow;
 private bool _orbLocked;
 private bool _noTradeToday;
 private int _tradesToday;
 private PositionCloseReason _lastCloseReason;
 private bool _hasLastCloseReason;
 private double _entryOffsetPipsForDay;
 private double _orbRangePrice;
 private bool _killSwitchLoggedToday;
 private bool _closePositionsLoggedToday;
 private bool _sessionTimeLoggedToday;

 // ORB robustness state
 private bool _orbBackfillDoneToday;
 private DateTime _lastOrbSelfHealUtc;
 private int _orbSelfHealAttemptsToday;
 private bool _orbNotLockedWarnedToday;

 // Post-lock replay state (to avoid missing the first breakout candle when ORB locks late)
 private bool _needsPostLockConfirmReplay;
 private DateTime _orbLockedUtc;

 // Catch-up state
 private bool _catchUpAttemptedToday;

 // Per-position state
 private Dictionary<long, PositionState> _positionStates;


 // Close/force-close retry throttling (prevents log spam & broker flooding)
 private Dictionary<long, DateTime> _lastCloseAttemptUtcByPosId;
 private Dictionary<long, DateTime> _lastCloseFailLogUtcByPosId;
 private Dictionary<long, CloseBackoffState> _closeBackoffByPosId;
 // Tracking processed bar indices
 private int _lastOrbBarIndex;
 private int _lastConfirmBarIndex;
 private int _lastTrendBarIndex;

 // VWAP state
 private double _vwapCumTPV;
 private double _vwapCumV;
 private Dictionary<int, double> _vwapValues;
 private DateTime _vwapCurrentDate;

 // Multi TP normalized percents
 private double _tp1Pct, _tp2Pct, _tp3Pct, _tp4Pct;

 // Max R for final TP
 private double _maxTpR;

 // =====================================================================
 // LIFECYCLE
 // =====================================================================

 protected override void OnStart()
 {
 // Parse time parameters
 if (!TimeSpan.TryParse(RangeStartTimeUtcStr, out _rangeStartTimeCfg))
 {
 Print("ERROR: Cannot parse RangeStartTime '{0}'. Use HH:mm:ss format.", RangeStartTimeUtcStr);
 Stop();
 return;
 }
 if (!TimeSpan.TryParse(RangeEndTimeUtcStr, out _rangeEndTimeCfg))
 {
 Print("ERROR: Cannot parse RangeEndTime '{0}'. Use HH:mm:ss format.", RangeEndTimeUtcStr);
 Stop();
 return;
 }
 if (!TimeSpan.TryParse(TradingStartTimeUtcStr, out _tradingStartTimeCfg))
 {
 Print("ERROR: Cannot parse TradingStartTime '{0}'. Use HH:mm:ss format.", TradingStartTimeUtcStr);
 Stop();
 return;
 }
 if (!TimeSpan.TryParse(KillSwitchTimeUtcStr, out _killSwitchTimeCfg))
 {
 Print("ERROR: Cannot parse KillSwitchTime '{0}'. Use HH:mm:ss format.", KillSwitchTimeUtcStr);
 Stop();
 return;
 }

 if (!TimeSpan.TryParse(ClosePositionsTimeUtcStr, out _closePositionsTimeCfg))
 {
 Print("ERROR: Cannot parse ClosePositionsTime '{0}'. Use HH:mm:ss format.", ClosePositionsTimeUtcStr);
 Stop();
 return;
 }

 // Resolve session timezone
 _sessionTz = ResolveTimeZone();
 if (_sessionTz == null)
 {
 Print("ERROR: Failed to resolve session timezone.");
 Stop();
 return;
 }

 // Determine point size
 _pointSize = (PointUnitModeParam == PointUnitMode.UseTickSizeAsPoint) ? Symbol.TickSize : Symbol.PipSize;
 if (_pointSize <= 0)
 {
 Print("ERROR: pointSize is <= 0. TickSize={0} PipSize={1}", Symbol.TickSize, Symbol.PipSize);
 Stop();
 return;
 }

 // Create bar series
 _orbBars = MarketData.GetBars(OrbBarsTimeFrame);
 _confirmBars = MarketData.GetBars(ConfirmationTimeFrame);
 if (_orbBars == null || _confirmBars == null)
 {
 Print("ERROR: Failed to acquire bar series.");
 Stop();
 return;
 }
 // Trend filter setup
 if (EnableTrendFilter)
 {
 _trendBars = MarketData.GetBars(TrendTimeFrame);
 if (_trendBars != null)
 {
 _trendEma = Indicators.ExponentialMovingAverage(_trendBars.ClosePrices, TrendEmaPeriod);
 }
 else
 {
 Print("WARNING: Failed to load TrendTimeFrame bars. Trend filter disabled.");
 EnableTrendFilter = false;
 }
 }

 // Initialize VWAP state
 _vwapValues = new Dictionary<int, double>();
 _vwapCumTPV = 0;
 _vwapCumV = 0;
 _vwapCurrentDate = DateTime.MinValue;

 // Initialize position states
 _positionStates = new Dictionary<long, PositionState>();


 _lastCloseAttemptUtcByPosId = new Dictionary<long, DateTime>();
 _lastCloseFailLogUtcByPosId = new Dictionary<long, DateTime>();
 _closeBackoffByPosId = new Dictionary<long, CloseBackoffState>();
 // Normalize multi TP percentages
 NormalizeMultiTpPercents();

 // Compute max TP R
 ComputeMaxTpR();

 // Initialize bar tracking indices
 _lastOrbBarIndex = _orbBars.Count - 1;
 _lastConfirmBarIndex = _confirmBars.Count - 1;
 _lastTrendBarIndex = (_trendBars != null) ? _trendBars.Count - 1 : -1;

 // Subscribe to position closed event
 Positions.Closed += OnPositionsClosed;

 // Initialize daily state
 _currentSessionDate = DateTime.MinValue;
 ResetForDate(GetSessionDate(Server.Time));

 // Register existing bot positions
 foreach (var pos in Positions)
 {
 if (IsBotPosition(pos) && !IsIgnorableDustPosition(pos))
 {
 RegisterExistingPosition(pos);
 }
 }

 Log("ORB Bot started. Symbol={0} PointSize={1} OrbTF={2} ConfirmTF={3} TZ={4}",
 Symbol.Name, _pointSize, OrbBarsTimeFrame, ConfirmationTimeFrame,
 UseFixedUtcTimes ? "UTC(fixed)" : SessionTimeZoneParam.ToString());

 Log("VOLUME_DIAG symbol={0} min={1} step={2} max={3}", Symbol.Name, Symbol.VolumeInUnitsMin, Symbol.VolumeInUnitsStep, Symbol.VolumeInUnitsMax);


 // Startup sanity warnings
 if (MinOrbRangePips > 0 && MaxOrbRangePips > 0 && MinOrbRangePips > MaxOrbRangePips)
 Print("WARNING: MinOrbRangePips ({0}) > MaxOrbRangePips ({1}). No trades will ever be taken.", MinOrbRangePips, MaxOrbRangePips);
 if (EnableKillSwitch && _tradingStartUtcToday >= _killSwitchUtcToday)
 Print("WARNING: TradingStartTime ({0}) is at or after KillSwitchTime ({1}). No entries possible.", _tradingStartTimeCfg, _killSwitchTimeCfg);

 if (ClosePositionsAtKillSwitch && EnableKillSwitch && _closePositionsUtcToday < _killSwitchUtcToday)
 Print("WARNING: ClosePositionsTime ({0}) is earlier than KillSwitchTime ({1}). Entries will also be blocked at ClosePositionsTime.", _closePositionsTimeCfg, _killSwitchTimeCfg);

 // Schedule sanity (very common misconfiguration that results in ZERO trades):
 // The bot can only open trades once BOTH:
 // - ORB is locked (which happens at/after ORB end time)
 // - TradingStartTime has been reached
 // Therefore, if your kill switch / close positions time is <= that earliest-possible entry time,
 // entries will be blocked all day and you will see repeated self-heal attempts.
 DateTime earliestPossibleEntryUtc = _orbEndUtcToday;
 if (_tradingStartUtcToday > earliestPossibleEntryUtc)
 earliestPossibleEntryUtc = _tradingStartUtcToday;

 if (_tradingStartUtcToday < _orbEndUtcToday)
 {
 Print("INFO: TradingStartTime ({0:HH:mm}) is BEFORE ORB End ({1:HH:mm}). This bot will NOT enter until the ORB locks at the end of the ORB window.",
 _tradingStartUtcToday, _orbEndUtcToday);
 }

 if (EnableKillSwitch && _killSwitchUtcToday <= earliestPossibleEntryUtc)
 {
 Print("WARNING: KillSwitchTime ({0:HH:mm}) is at/before the earliest possible entry time ({1:HH:mm}). Result: ZERO trades. Fix by moving KillSwitch later or shortening the ORB window.",
 _killSwitchUtcToday, earliestPossibleEntryUtc);
 }

 if (ClosePositionsAtKillSwitch && _closePositionsUtcToday <= earliestPossibleEntryUtc)
 {
 Print("WARNING: ClosePositionsTime ({0:HH:mm}) is at/before the earliest possible entry time ({1:HH:mm}). Result: ZERO trades. Fix by moving ClosePositions later, or shortening the ORB window, or disabling ClosePositionsAtKillSwitch.",
 _closePositionsUtcToday, earliestPossibleEntryUtc);
 }
 }

 protected override void OnTick()
 {
 var nowUtc = Server.Time;

 // Check for new session day
 DateTime sessionDate = GetSessionDate(nowUtc);
 if (sessionDate != _currentSessionDate)
 ResetForDate(sessionDate);

 // Close positions time: force flat after this time (independent from the entry kill switch)
 if (ClosePositionsAtKillSwitch && nowUtc >= _closePositionsUtcToday)
 {
 if (!_closePositionsLoggedToday)
 {
 Log("CLOSE TIME reached ({0:HH:mm}). Closing any open positions and blocking new entries.", _closePositionsUtcToday);
 _closePositionsLoggedToday = true;
 }

 if (HasOpenBotPosition())
 CloseAllBotPositions("CLOSE TIME");
 }

 // Process any new ORB bars
 ProcessNewOrbBars();

 // ORB self-heal: if we are past the ORB window and it still isn't locked (restart / missed bars),
 // force a backfill + lock attempt so trading can proceed safely.
 EnsureOrbBuiltAndLocked(nowUtc);

 // If ORB just locked (especially via backfill/self-heal) replay the most recent confirmation
 // candle(s) so we don't miss the first breakout.
 TryPostLockConfirmReplay(nowUtc);
 // Process trend bars (for VWAP accumulation)
 if (EnableTrendFilter && _trendBars != null)
 ProcessNewTrendBars();

 // Process any new closed confirmation bars
 ProcessNewConfirmBars();

 // Catch-up entry: if TradingStart has begun and price is already outside the ORB,
 // optionally enter once (subject to filters).
 TryCatchUpEntry(nowUtc);

 // AllowIntrabar: evaluate the forming bar on every tick
 if (BreakoutEvaluationMomentParam == BreakoutEvaluationMoment.AllowIntrabar)
 {
 int currentBarIndex = _confirmBars.Count - 1;
 if (currentBarIndex >= 0)
 EvaluateEntryAtConfirmBar(currentBarIndex, true);
 }

 // Manage open positions (partials, early reduction, dynamic stop)
 ManageOpenPositions();
 }

 protected override void OnStop()
 {
 Positions.Closed -= OnPositionsClosed;
 Log("ORB Bot stopped.");
 }

 // =====================================================================
 // SESSION TIMEZONE
 // =====================================================================

 private TimeZoneInfo ResolveTimeZone()
 {
 if (UseFixedUtcTimes)
 return TimeZoneInfo.Utc;

 // cTrader runs on multiple platforms. Windows typically uses Windows TZ IDs (e.g., "Eastern Standard Time"),
 // while macOS/Linux typically use IANA IDs (e.g., "America/New_York").
 // We try both to avoid silently falling back to UTC.
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
 // Log once at startup for visibility.
 Print("SESSION_TIMEZONE resolved='{0}' id='{1}'", tz.DisplayName, id);
 return tz;
 }
 catch
 {
 // try next
 }
 }

 Print("WARNING: Could not resolve session timezone for {0}. Falling back to UTC.", SessionTimeZoneParam);
 return TimeZoneInfo.Utc;
 }


 private DateTime GetSessionDate(DateTime utcNow)
 {
 if (UseFixedUtcTimes)
 return utcNow.Date;

 DateTime localNow = TimeZoneInfo.ConvertTimeFromUtc(utcNow, _sessionTz);
 return localNow.Date;
 }

 private DateTime ConvertConfiguredTimeToUtc(DateTime sessionDate, TimeSpan configuredTime)
 {
 if (UseFixedUtcTimes)
 return sessionDate + configuredTime;

 DateTime localDt = sessionDate + configuredTime;
 try
 {
 if (_sessionTz.IsInvalidTime(localDt))
 {
 // DST spring-forward gap: shift forward by 1 hour
 localDt = localDt.AddHours(1);
 }
 if (_sessionTz.IsAmbiguousTime(localDt))
 {
 Print("WARNING: Ambiguous time {0} in {1} (DST fall-back). Using standard-time interpretation.", localDt, SessionTimeZoneParam);
 }
 return TimeZoneInfo.ConvertTimeToUtc(localDt, _sessionTz);
 }
 catch (Exception)
 {
 return sessionDate + configuredTime;
 }
 }

 private void ComputeSessionTimesForDay(DateTime sessionDate)
 {
 _orbStartUtcToday = ConvertConfiguredTimeToUtc(sessionDate, _rangeStartTimeCfg);
 _orbEndUtcToday = ConvertConfiguredTimeToUtc(sessionDate, _rangeEndTimeCfg);
 _tradingStartUtcToday = ConvertConfiguredTimeToUtc(sessionDate, _tradingStartTimeCfg);
 _killSwitchUtcToday = ConvertConfiguredTimeToUtc(sessionDate, _killSwitchTimeCfg);
 _closePositionsUtcToday = ConvertConfiguredTimeToUtc(sessionDate, _closePositionsTimeCfg);

 // Cross-midnight normalization
 //
 // We always ensure the ORB window end is AFTER the ORB start.
 //
 // IMPORTANT: TradingStartTime is allowed to be earlier than ORBStartTime
 // (e.g., TradingStart = 00:00, ORBStart = 08:00). The previous implementation
 // incorrectly pushed TradingStartTime to the *next* day whenever it was earlier
 // than ORBStartTime, which could effectively disable trading for the entire
 // session (TradingStart becomes after the KillSwitch or after the backtest day).
 //
 // We only shift TradingStartTime forward when the ORB window itself crosses
 // midnight (ORBEnd <= ORBStart) and the configured TradingStartTime is also
 // earlier than ORBStartTime (i.e., it is intended to be after midnight).
 bool orbCrossesMidnight = _orbEndUtcToday <= _orbStartUtcToday;
 if (orbCrossesMidnight)
 _orbEndUtcToday = _orbEndUtcToday.AddDays(1);

 // For standard daytime sessions (ORB does not cross midnight), DO NOT shift trading start.
 if (orbCrossesMidnight && _tradingStartUtcToday < _orbStartUtcToday)
 _tradingStartUtcToday = _tradingStartUtcToday.AddDays(1);

 // Kill switch is commonly intended to be after the ORB session; if it is configured
 // earlier than ORBStartTime, interpret it as occurring after midnight (next day).
 if (_killSwitchUtcToday < _orbStartUtcToday)
 _killSwitchUtcToday = _killSwitchUtcToday.AddDays(1);

 // Close-positions time is commonly intended to be after the trading session; if it is configured
 // earlier than ORBStartTime, interpret it as occurring after midnight (next day).
 if (_closePositionsUtcToday < _orbStartUtcToday)
 _closePositionsUtcToday = _closePositionsUtcToday.AddDays(1);
 }

 // =====================================================================
 // DAILY STATE RESET
 // =====================================================================

 private void ResetForDate(DateTime sessionDate)
 {
 _currentSessionDate = sessionDate;
 _orbHigh = double.MinValue;
 _orbLow = double.MaxValue;
 _orbLocked = false;
 _noTradeToday = false;
 _tradesToday = 0;
 _lastCloseReason = PositionCloseReason.StopLoss;
 _hasLastCloseReason = false;
 _orbRangePrice = 0;
 _killSwitchLoggedToday = false;
 _closePositionsLoggedToday = false;
 _sessionTimeLoggedToday = false;

 _orbBackfillDoneToday = false;
 _lastOrbSelfHealUtc = DateTime.MinValue;
 _orbSelfHealAttemptsToday = 0;
 _orbNotLockedWarnedToday = false;

 _needsPostLockConfirmReplay = false;
 _orbLockedUtc = DateTime.MinValue;


 _catchUpAttemptedToday = false;

 // Manual entry offset for the day (always ready)
 _entryOffsetPipsForDay = EntryOffsetPipsManual;
 // Compute UTC session times for this day
 ComputeSessionTimesForDay(sessionDate);

 // Check trading day (use the sessionDate day-of-week; sessionDate already accounts for timezone mode)
 DayOfWeek dow = sessionDate.DayOfWeek;

 if (!IsTradingDayEnabled(dow))
 {
 _noTradeToday = true;
 Log("NO TRADE TODAY: Trading disabled for {0}.", dow);
 }

 // Remove old chart objects for previous day
 RemoveOldDrawings();

 Log("=== New day reset: {0:yyyy-MM-dd} ===", sessionDate);

 // Log session timezone info once per day
 LogSessionTimezone(sessionDate);

 // If the bot started late or restarted, reconstruct ORB from already-closed bars
 // and lock/draw immediately when possible.
 TryBackfillAndMaybeLockOrb("RESET");

 // STARTUP/RESTART SAFETY: if the cBot restarts mid-session it will otherwise forget
 // how many trades it already took today, which can allow multiple trades despite
 // MaxTradesPerDay = 1. Rehydrate from open positions + History using today's label.
 RehydrateTradesTodayFromHistory("RESET");
 }

 private bool IsTradingDayEnabled(DayOfWeek dow)
 {
 switch (dow)
 {
 case DayOfWeek.Monday: return TradeMonday;
 case DayOfWeek.Tuesday: return TradeTuesday;
 case DayOfWeek.Wednesday: return TradeWednesday;
 case DayOfWeek.Thursday: return TradeThursday;
 case DayOfWeek.Friday: return TradeFriday;
 case DayOfWeek.Saturday: return TradeSaturday;
 case DayOfWeek.Sunday: return TradeSunday;
 default: return true;
 }
 }

 private void LogSessionTimezone(DateTime sessionDate)
 {
 if (_sessionTimeLoggedToday) return;
 _sessionTimeLoggedToday = true;

 if (UseFixedUtcTimes)
 {
 Log("SESSION_TIMEZONE mode=UTC tz=UTC");
 }
 else
 {
 Log("SESSION_TIMEZONE mode=Local tz={0} rangeUtc={1:HH:mm}-{2:HH:mm} tradingStartUtc={3:HH:mm} killUtc={4:HH:mm} closeUtc={5:HH:mm}",
 SessionTimeZoneParam,
 _orbStartUtcToday, _orbEndUtcToday,
 _tradingStartUtcToday, _killSwitchUtcToday, _closePositionsUtcToday);
 }
 }

 // =====================================================================
 // ORB BAR PROCESSING
 // =====================================================================

 // ---------------------------------------------------------------------
 // ORB ROBUSTNESS: Backfill + Self-Heal
 //
 // Problem this solves:
 // - If the bot starts/restarts AFTER the ORB window has partially/fully completed,
 // the live bar-closed loop may never see those ORB bars, so ORB never locks and
 // no lines are drawn / no trades occur.
 //
 // This logic reconstructs the ORB from already-closed history bars and can
 // lock/draw immediately once a post-ORB bar has closed (same condition as live logic).
 // ---------------------------------------------------------------------

 private void EnsureOrbBuiltAndLocked(DateTime nowUtc)
 {
 if (_orbLocked) return;
 if (!EnableOrbSelfHeal) return;

 // Do not run ORB self-heal on disabled trading days. This avoids misleading
 // "ORB should be locked" warnings on days where the bot has intentionally stood down.
 if (_noTradeToday) return;

 // Nothing to do before the ORB window has ended. Locking is only valid once
 // the final ORB bar has closed, which is detectable as soon as the first
 // post-ORB bar exists. Example: 09:30-09:45 on M5 locks at 09:45, not 09:50.
 if (nowUtc < _orbEndUtcToday) return;

 int interval = Math.Max(5, OrbSelfHealIntervalSeconds);
 if (_lastOrbSelfHealUtc != DateTime.MinValue && (nowUtc - _lastOrbSelfHealUtc).TotalSeconds < interval)
 return;

 _lastOrbSelfHealUtc = nowUtc;
 _orbSelfHealAttemptsToday++;

 TryBackfillAndMaybeLockOrb("SELF_HEAL");

 // Only warn once we're at/after the time we actually EXPECT to be able to trade.
 // Earliest possible entries occur after BOTH ORB end and TradingStart.
 DateTime warnAt = _orbEndUtcToday;
 if (_tradingStartUtcToday > warnAt) warnAt = _tradingStartUtcToday;

 if (!_orbLocked && nowUtc >= warnAt && !_orbNotLockedWarnedToday)
 {
 _orbNotLockedWarnedToday = true;
 Log("WARNING: ORB should be locked by now but it is not. No entries possible until ORB locks. Self-heal will keep retrying.");
 }
 }

 private void TryBackfillAndMaybeLockOrb(string source)
 {
 if (_orbBars == null) return;
 if (_orbLocked) return;
 if (!EnableOrbBackfill) return;

 EnsureOrbHistoryCoverageForToday(source);

 int lastClosed = _orbBars.Count - 2;
 if (lastClosed < 0) return;

 // The ORB can lock as soon as the final ORB bar is closed. For time-based
 // bars, that is when the first bar at/after _orbEndUtcToday exists.
 // This preserves the required behaviour: an M5 09:30-09:45 ORB locks at
 // 09:45 as soon as the 09:40-09:45 bar is closed, not at 09:50.
 bool finalOrbBarClosed = GetBarCloseTimeUtc(_orbBars, lastClosed) >= _orbEndUtcToday;

 double hi = double.MinValue;
 double lo = double.MaxValue;
 int included = 0;

 int startIdx = FindFirstOrbBarIndexAtOrAfter(_orbStartUtcToday);
 if (startIdx < 0) startIdx = 0;
 if (startIdx > lastClosed) startIdx = lastClosed;

 for (int i = startIdx; i <= lastClosed; i++)
 {
 DateTime barOpen = _orbBars.OpenTimes[i];
 if (barOpen < _orbStartUtcToday) continue;
 if (barOpen >= _orbEndUtcToday) break;

 // Only use closed bars. This avoids including the forming post-ORB bar.
 DateTime barClose = GetBarCloseTimeUtc(_orbBars, i);
 if (barClose == DateTime.MinValue || barClose > _orbEndUtcToday)
 continue;

 double bh = _orbBars.HighPrices[i];
 double bl = _orbBars.LowPrices[i];

 if (bh > hi) hi = bh;
 if (bl < lo) lo = bl;
 included++;
 }

 if (included <= 0)
 return;

 // Authoritative rebuild: replace the ORB range with the value derived from
 // closed bars in the ORB window. Do not merge with any partial live state.
 _orbHigh = hi;
 _orbLow = lo;

 if (!_orbBackfillDoneToday)
 Log("ORB BACKFILL: Rebuilt from {0} closed bar(s). High={1} Low={2} finalClosed={3} [source={4}]", included, _orbHigh, _orbLow, finalOrbBarClosed, source);

 _orbBackfillDoneToday = true;

 if (finalOrbBarClosed)
 LockOrb("BACKFILL/" + source);
 }

 private void EnsureOrbHistoryCoverageForToday(string source)
 {
 if (_orbBars == null || _orbBars.Count <= 0) return;

 // If the loaded series already starts before the ORB window, no action is needed.
 if (_orbBars.OpenTimes[0] <= _orbStartUtcToday)
 return;

 // Load a small amount of additional history if cTrader has not yet provided
 // the ORB window. This is intentionally bounded so a bad feed cannot loop forever.
 int totalLoaded = 0;
 for (int attempt = 0; attempt < 5 && _orbBars.Count > 0 && _orbBars.OpenTimes[0] > _orbStartUtcToday; attempt++)
 {
 int loaded = 0;
 try
 {
 loaded = _orbBars.LoadMoreHistory();
 }
 catch (Exception ex)
 {
 if (EnableDebugLogging)
 Log("ORB HISTORY: LoadMoreHistory failed [source={0}] {1}", source, ex.Message);
 break;
 }

 if (loaded <= 0)
 break;

 totalLoaded += loaded;
 }

 if (totalLoaded > 0 && EnableDebugLogging)
 Log("ORB HISTORY: Loaded {0} older bar(s) for ORB rebuild [source={1}]", totalLoaded, source);
 }

 // Helper: determine the close time of a closed bar.
 // For time-based bars, the next bar's OpenTime is the current bar's CloseTime.
 // If the next bar doesn't exist (rare for our usage), we return OpenTime as a safe fallback.
 private DateTime GetBarCloseTimeUtc(Bars bars, int barIndex)
 {
 if (bars == null) return DateTime.MinValue;
 if (barIndex < 0 || barIndex >= bars.Count) return DateTime.MinValue;

 int next = barIndex + 1;
 if (next >= 0 && next < bars.Count)
 return bars.OpenTimes[next];

 return bars.OpenTimes[barIndex];
 }

 private int FindFirstOrbBarIndexAtOrAfter(DateTime utcTime)
 {
 if (_orbBars == null || _orbBars.Count <= 0) return -1;

 int lo = 0;
 int hi = _orbBars.Count - 1;
 int ans = _orbBars.Count;

 while (lo <= hi)
 {
 int mid = lo + ((hi - lo) / 2);
 DateTime t = _orbBars.OpenTimes[mid];

 if (t >= utcTime)
 {
 ans = mid;
 hi = mid - 1;
 }
 else
 {
 lo = mid + 1;
 }
 }

 if (ans == _orbBars.Count)
 return _orbBars.Count - 1;

 return ans;
 }

 private void LockOrb(string source)
 {
 if (_orbLocked) return;
 if (!(_orbHigh > double.MinValue && _orbLow < double.MaxValue)) return;

 _orbLocked = true;
 _orbRangePrice = _orbHigh - _orbLow;

 double orbRangePips = _orbRangePrice / _pointSize;

 Log("ORB LOCKED: High={0} Low={1} Range={2:F1} pips (price={3}) [source={4}]",
 _orbHigh, _orbLow, orbRangePips, _orbRangePrice, source);

 // Check max ORB range filter
 if (MaxOrbRangePips > 0 && orbRangePips >= MaxOrbRangePips)
 {
 _noTradeToday = true;
 Log("NO TRADE TODAY: ORB range {0:F1} pips >= max {1}. Standing down.", orbRangePips, MaxOrbRangePips);
 }

 // Check min ORB range filter
 if (MinOrbRangePips > 0 && orbRangePips < MinOrbRangePips)
 {
 _noTradeToday = true;
 Log("NO TRADE TODAY: ORB range {0:F1} pips < min {1}. Standing down.", orbRangePips, MinOrbRangePips);
 }

 // Draw ORB + threshold lines
 DrawOrbLinesOnChart();
 DrawThresholdLinesOnChart();

 // Arm a one-time replay of the latest closed confirmation bar(s) so we don't miss
 // the first breakout when ORB locks late (e.g., self-heal/backfill timing).
 _needsPostLockConfirmReplay = EnablePostLockConfirmReplay && !EnableCatchUpEntry;
 _orbLockedUtc = Server.Time;
 }

 private void TryPostLockConfirmReplay(DateTime nowUtc)
 {
 if (!_needsPostLockConfirmReplay) return;
 if (!EnablePostLockConfirmReplay) { _needsPostLockConfirmReplay = false; return; }

 // If Catch-Up Entry is enabled, we deliberately do NOT run post-lock replay.
 // Catch-Up is the dedicated mechanism for delayed-start strategies and avoids conflicts.
 if (EnableCatchUpEntry) { _needsPostLockConfirmReplay = false; return; }

 // Only meaningful once ORB is locked.
 if (!_orbLocked) return;

 // Don't do anything on a "no trade" day.
 if (_noTradeToday) { _needsPostLockConfirmReplay = false; return; }

 // Wait until trading is allowed.
 if (nowUtc < _tradingStartUtcToday) return;

 // Safety: avoid late entries long after the time we actually *allow* entries.
 // Use the later of ORB end and TradingStart as the "replay anchor" so delayed-start strategies
 // (e.g., start trading at 10:20 ET) are not incorrectly treated as "too late".
 var replayAnchorUtc = (_tradingStartUtcToday > _orbEndUtcToday) ? _tradingStartUtcToday : _orbEndUtcToday;
 double minsAfterAnchor = (nowUtc - replayAnchorUtc).TotalMinutes;
 if (minsAfterAnchor > PostLockReplayMaxDelayMinutes)
 {
 if (EnableDebugLogging)
 {
 string anchorLabel = (_tradingStartUtcToday > _orbEndUtcToday) ? "TradingStart" : "ORB end";
 Log("POST-LOCK REPLAY skipped: now is {0:F1} min after {1} (limit={2}m).", minsAfterAnchor, anchorLabel, PostLockReplayMaxDelayMinutes);
 }

 _needsPostLockConfirmReplay = false;
 return;
 }

 if (_confirmBars == null || _confirmBars.Count < 2)
 {
 _needsPostLockConfirmReplay = false;
 return;
 }

 int lastClosed = _confirmBars.Count - 2;
 if (lastClosed < 0)
 {
 _needsPostLockConfirmReplay = false;
 return;
 }

 int barsToReplay = Math.Max(1, PostLockReplayConfirmBars);
 int start = Math.Max(0, lastClosed - (barsToReplay - 1));

 if (EnableDebugLogging)
 Log("POST-LOCK REPLAY: Evaluating last {0} closed confirmation bar(s) (idx {1}->{2}).", barsToReplay, start, lastClosed);

 for (int i = start; i <= lastClosed; i++)
 {
 EvaluateEntryAtConfirmBar(i, false);

 // If a trade was opened, no need to continue.
 if (HasOpenBotPosition() || _tradesToday >= MaxTradesPerDay)
 break;
 }

 _needsPostLockConfirmReplay = false;
 }


 private void ProcessNewOrbBars()
 {
 int currentCount = _orbBars.Count;
 if (currentCount <= _lastOrbBarIndex)
 return;

 int lastClosed = currentCount - 2;

 for (int i = _lastOrbBarIndex; i <= lastClosed; i++)
 {
 if (i < 0) continue;
 OnOrbBarClosed(i);
 }

 _lastOrbBarIndex = currentCount - 1;
 }

 private void OnOrbBarClosed(int barIndex)
 {
 if (barIndex < 0 || barIndex >= _orbBars.Count) return;

 DateTime sessionDate = GetSessionDate(Server.Time);
 if (sessionDate != _currentSessionDate)
 ResetForDate(sessionDate);

 if (_orbLocked) return;

 DateTime barOpenTime = _orbBars.OpenTimes[barIndex];

 // Is this bar within the ORB window?
 if (barOpenTime >= _orbStartUtcToday && barOpenTime < _orbEndUtcToday)
 {
 double barHigh = _orbBars.HighPrices[barIndex];
 double barLow = _orbBars.LowPrices[barIndex];

 if (barHigh > _orbHigh)
 _orbHigh = barHigh;
 if (barLow < _orbLow)
 _orbLow = barLow;
 }

 // Check if ORB should lock.
 // We lock as soon as we see a bar CLOSE that reaches/passes the ORB end time.
 // This avoids a "1 bar late" lock (e.g., ORB ends 08:15 on M5 bars -> lock at 08:15, not 08:20).
 DateTime barCloseTime = GetBarCloseTimeUtc(_orbBars, barIndex);
 if (barCloseTime >= _orbEndUtcToday && !_orbLocked && _orbHigh > double.MinValue && _orbLow < double.MaxValue)
 {
 LockOrb("LIVE");
 }
 }

 // =====================================================================
 // TREND BAR PROCESSING (VWAP accumulation)
 // =====================================================================

 private void ProcessNewTrendBars()
 {
 if (_trendBars == null) return;

 int currentCount = _trendBars.Count;
 if (currentCount <= _lastTrendBarIndex)
 return;

 int lastClosed = currentCount - 2;

 for (int i = _lastTrendBarIndex; i <= lastClosed; i++)
 {
 if (i < 0) continue;
 OnTrendBarClosed(i);
 }

 _lastTrendBarIndex = currentCount - 1;
 }

 private void OnTrendBarClosed(int barIndex)
 {
 if (barIndex < 0 || barIndex >= _trendBars.Count) return;

 DateTime barDate = _trendBars.OpenTimes[barIndex].Date;

 // Reset VWAP on new day
 if (barDate != _vwapCurrentDate)
 {
 _vwapCumTPV = 0;
 _vwapCumV = 0;
 _vwapValues.Clear();
 _vwapCurrentDate = barDate;
 }

 // Accumulate VWAP
 double h = _trendBars.HighPrices[barIndex];
 double l = _trendBars.LowPrices[barIndex];
 double c = _trendBars.ClosePrices[barIndex];
 double tp = (h + l + c) / 3.0;
 double vol = _trendBars.TickVolumes[barIndex];

 if (vol > 0)
 {
 _vwapCumTPV += tp * vol;
 _vwapCumV += vol;
 }

 double vwap = (_vwapCumV > 0) ? _vwapCumTPV / _vwapCumV : c;
 _vwapValues[barIndex] = vwap;
 }

 // =====================================================================
 // TREND FILTER
 // =====================================================================

 private enum TrendBias { Bullish, Bearish, Neutral }

 private struct TrendInfo
 {
 public bool Valid;
 public TrendBias Bias;
 public double Price;
 public double Ema;
 public double Vwap;
 public double EmaSlopePips;
 public double VwapSlopePips;
 public string Reason;
 }

 private TrendInfo GetTrendInfo()
 {
 var ti = new TrendInfo
 {
 Valid = false,
 Bias = TrendBias.Neutral,
 Price = double.NaN,
 Ema = double.NaN,
 Vwap = double.NaN,
 EmaSlopePips = double.NaN,
 VwapSlopePips = double.NaN,
 Reason = ""
 };

 if (_trendBars == null || _trendEma == null)
 {
 ti.Reason = "no trend data";
 return ti;
 }

 int idx = _trendBars.Count - 2; // last closed bar
 if (idx < TrendSlopeLookbackBars || idx < 0)
 {
 ti.Reason = "not enough bars";
 return ti;
 }

 double ema = _trendEma.Result[idx];
 double price = _trendBars.ClosePrices[idx];

 // Get VWAP
 double vwap;
 if (!_vwapValues.TryGetValue(idx, out vwap))
 {
 ti.Reason = "VWAP not available";
 return ti;
 }

 // Slopes
 double emaPrev = _trendEma.Result[idx - TrendSlopeLookbackBars];
 double emaSlopePips = (ema - emaPrev) / Symbol.PipSize;

 double vwapPrev;
 double vwapSlopePips = 0;
 if (_vwapValues.TryGetValue(idx - TrendSlopeLookbackBars, out vwapPrev))
 {
 vwapSlopePips = (vwap - vwapPrev) / Symbol.PipSize;
 }
 else
 {
 ti.Reason = "VWAP slope not available";
 return ti;
 }

 // Bullish: EMA9 > VWAP, Price > EMA9 AND Price > VWAP,
 // EMA slope >= +min, VWAP slope >= +min
 bool bullish = ema > vwap
 && price > ema && price > vwap
 && emaSlopePips >= TrendMinSlopePips
 && vwapSlopePips >= TrendMinSlopePips;

 // Bearish: EMA9 < VWAP, Price < EMA9 AND Price < VWAP,
 // EMA slope <= -min, VWAP slope <= -min
 bool bearish = ema < vwap
 && price < ema && price < vwap
 && emaSlopePips <= -TrendMinSlopePips
 && vwapSlopePips <= -TrendMinSlopePips;

 string biasStr;
 TrendBias bias;
 if (bullish)
 {
 bias = TrendBias.Bullish;
 biasStr = "Bullish";
 }
 else if (bearish)
 {
 bias = TrendBias.Bearish;
 biasStr = "Bearish";
 }
 else
 {
 bias = TrendBias.Neutral;
 biasStr = "Neutral";
 }

 ti.Valid = true;
 ti.Bias = bias;
 ti.Price = price;
 ti.Ema = ema;
 ti.Vwap = vwap;
 ti.EmaSlopePips = emaSlopePips;
 ti.VwapSlopePips = vwapSlopePips;
 ti.Reason = string.Format("price={0:F5} ema9={1:F5} vwap={2:F5} emaSlope={3:F2} vwapSlope={4:F2} bias={5}",
 price, ema, vwap, emaSlopePips, vwapSlopePips, biasStr);

 return ti;
 }

 // =====================================================================
 // CONFIRMATION BAR PROCESSING
 // =====================================================================

 private void ProcessNewConfirmBars()
 {
 int currentCount = _confirmBars.Count;
 if (currentCount <= _lastConfirmBarIndex)
 return;

 int lastClosed = currentCount - 2;

 for (int i = _lastConfirmBarIndex; i <= lastClosed; i++)
 {
 if (i < 0) continue;
 EvaluateEntryAtConfirmBar(i, false);
 }

 _lastConfirmBarIndex = currentCount - 1;
 }

 private void EvaluateEntryAtConfirmBar(int evalBarIndex, bool isIntrabar)
 {
 var nowUtc = Server.Time;
 DateTime sessionDate = GetSessionDate(nowUtc);
 if (sessionDate != _currentSessionDate)
 ResetForDate(sessionDate);

 // Gate: ORB must be locked
 if (!_orbLocked) return;

 // Compute thresholds early so we can explain misses (even if later gates block).
 double longThreshold = _orbHigh + _entryOffsetPipsForDay * _pointSize;
 double shortThreshold = _orbLow - _entryOffsetPipsForDay * _pointSize;
 // Evaluate signals with N confirmation bars
 int N = ConfirmationBarsCount;
 if (evalBarIndex < N - 1) return;

 bool longSignal;
 bool shortSignal;

 // IMPORTANT: BodyCross + N>1 is extremely restrictive if we require EVERY bar to "body cross".
 // After the first breakout bar, subsequent bars usually OPEN beyond the threshold,
 // so strict BodyCross (open <= threshold && close >= threshold) fails.
 //
 // For BodyCross with multi-bar confirmation, we treat it as:
 // - At least ONE bar within the last N bars must represent the actual cross (BodyCross, including gap-cross)
 // - AND ALL last N bars must CLOSE beyond the threshold (stay outside)
 if (BreakoutCrossTypeParam == BreakoutCrossType.BodyCross && N > 1)
 {
 longSignal = EvaluateBodyCrossWithCloseConfirmationLong(evalBarIndex, N, longThreshold);
 shortSignal = EvaluateBodyCrossWithCloseConfirmationShort(evalBarIndex, N, shortThreshold);
 }
 else
 {
 longSignal = true;
 shortSignal = true;

 if (isIntrabar && N > 1)
 {
 for (int k = 0; k < N - 1; k++)
 {
 int idx = evalBarIndex - (N - 1) + k;
 if (idx < 0) { longSignal = false; shortSignal = false; break; }
 if (!CheckBarBreakoutLong(idx, longThreshold)) longSignal = false;
 if (!CheckBarBreakoutShort(idx, shortThreshold)) shortSignal = false;
 }
 if (longSignal && !CheckBarBreakoutLong(evalBarIndex, longThreshold)) longSignal = false;
 if (shortSignal && !CheckBarBreakoutShort(evalBarIndex, shortThreshold)) shortSignal = false;
 }
 else
 {
 for (int k = 0; k < N; k++)
 {
 int idx = evalBarIndex - (N - 1) + k;
 if (idx < 0) { longSignal = false; shortSignal = false; break; }
 if (!CheckBarBreakoutLong(idx, longThreshold)) longSignal = false;
 if (!CheckBarBreakoutShort(idx, shortThreshold)) shortSignal = false;
 }
 }
 }

 // Direction filters
 if (!AllowLong) longSignal = false;
 if (!AllowShort) shortSignal = false;

 // Ambiguous check
 if (longSignal && shortSignal)
 {
 Log("AMBIGUOUS: Both long and short signals active. No trade.");
 return;
 }

 // No signal: optionally explain near-miss (price touched threshold but rules didn't qualify)
 if (!longSignal && !shortSignal)
 {
 if (!isIntrabar)
 LogNearMissBreakout(evalBarIndex, N, longThreshold, shortThreshold);
 return;
 }

 TradeType direction = longSignal ? TradeType.Buy : TradeType.Sell;

 // From here on: we have a VALID signal. Any return below is a "blocked entry".
 bool canExplain = ExplainBlockedEntries && !isIntrabar;
 DateTime barTime = _confirmBars.OpenTimes[evalBarIndex];

 // Gate: no-trade day (ORB range or disabled day)
 if (_noTradeToday)
 {
 if (canExplain)
 Log("ENTRY BLOCKED: {0} signal at {1:HH:mm} but _noTradeToday=true (range/day filter).", direction, barTime);
 return;
 }

 // Gate: trading start time
 if (nowUtc < _tradingStartUtcToday)
 {
 if (canExplain)
 Log("ENTRY BLOCKED: {0} signal at {1:HH:mm} but TradingStart not reached yet (now={2:HH:mm}, start={3:HH:mm}).", direction, barTime, nowUtc, _tradingStartUtcToday);
 return;
 }

 // Gate: close-positions time (force flat). After this time we do not allow new entries.
 if (ClosePositionsAtKillSwitch && nowUtc >= _closePositionsUtcToday)
 {
 if (!_closePositionsLoggedToday)
 {
 Log("Close positions time active. Blocking new entries.");
 _closePositionsLoggedToday = true;
 }
 if (canExplain)
 Log("ENTRY BLOCKED: {0} signal at {1:HH:mm} but ClosePositionsTime already reached (now={2:HH:mm}, close={3:HH:mm}).", direction, barTime, nowUtc, _closePositionsUtcToday);
 return;
 }

 // Gate: kill switch
 if (EnableKillSwitch && nowUtc >= _killSwitchUtcToday)
 {
 if (!_killSwitchLoggedToday)
 {
 Log("Kill switch active. Blocking new entries.");
 _killSwitchLoggedToday = true;
 }
 if (canExplain)
 Log("ENTRY BLOCKED: {0} signal at {1:HH:mm} but KillSwitch already active (now={2:HH:mm}, kill={3:HH:mm}).", direction, barTime, nowUtc, _killSwitchUtcToday);
 return;
 }

 // Gate: no existing open bot position
 var openPos = GetFirstOpenBotPosition();
 if (openPos != null)
 {
 if (canExplain)
 Log("ENTRY BLOCKED: {0} signal at {1:HH:mm} but existing open bot position found: {2} vol={3}.", direction, barTime, openPos.Label, openPos.VolumeInUnits);
 return;
 }

 // Gate: max trades per day
 if (_tradesToday >= MaxTradesPerDay)
 {
 if (canExplain)
 Log("ENTRY BLOCKED: {0} signal at {1:HH:mm} but MaxTradesPerDay reached ({2}/{3}).", direction, barTime, _tradesToday, MaxTradesPerDay);
 return;
 }

 // Gate: re-entry mode
 if (_tradesToday > 0)
 {
 if (!_hasLastCloseReason)
 {
 if (canExplain)
 Log("ENTRY BLOCKED: {0} signal at {1:HH:mm} but last close reason unknown (_hasLastCloseReason=false).", direction, barTime);
 return;
 }

 if (ReEntryModeParam == ReEntryMode.AfterStopLossOnly)
 {
 if (_lastCloseReason != PositionCloseReason.StopLoss && _lastCloseReason != PositionCloseReason.StopOut)
 {
 if (canExplain)
 Log("ENTRY BLOCKED: {0} signal at {1:HH:mm} but ReEntryMode=AfterStopLossOnly and last close was {2}.", direction, barTime, _lastCloseReason);
 return;
 }
 }
 }

 // Trend filter gate
 if (EnableTrendFilter)
 {
 TrendInfo ti = GetTrendInfo();
 string trendReason = ti.Reason;
 TrendBias bias = ti.Bias;

 bool pass = true;
 string blockReason = "";

 if (bias == TrendBias.Bullish && direction == TradeType.Sell)
 {
 pass = false;
 blockReason = "Bullish trend blocks SHORT";
 }
 else if (bias == TrendBias.Bearish && direction == TradeType.Buy)
 {
 pass = false;
 blockReason = "Bearish trend blocks LONG";
 }
 else if (bias == TrendBias.Neutral)
 {
 switch (TrendNeutralPolicyParam)
 {
 case TrendNeutralPolicy.BlockAll:
 pass = false;
 blockReason = "Neutral trend, policy=BlockAll";
 break;

 case TrendNeutralPolicy.AllowBoth:
 pass = true;
 break;

 case TrendNeutralPolicy.AllowIfPriceVsEma:
 if (!ti.Valid)
 {
 pass = false;
 blockReason = "Neutral trend but trend data not ready";
 }
 else
 {
 pass = (direction == TradeType.Buy) ? (ti.Price > ti.Ema) : (ti.Price < ti.Ema);
 if (!pass) blockReason = "Neutral trend, price vs EMA disagrees";
 }
 break;

 case TrendNeutralPolicy.AllowIfEmaSlope:
 if (!ti.Valid)
 {
 pass = false;
 blockReason = "Neutral trend but trend data not ready";
 }
 else
 {
 double minSlope = NeutralMinSlopePips;
 pass = (direction == TradeType.Buy)
 ? (ti.EmaSlopePips >= minSlope)
 : (ti.EmaSlopePips <= -minSlope);
 if (!pass) blockReason = "Neutral trend, EMA slope not supportive";
 }
 break;

 case TrendNeutralPolicy.AllowIfEmaVsVwap:
 if (!ti.Valid)
 {
 pass = false;
 blockReason = "Neutral trend but trend data not ready";
 }
 else
 {
 pass = (direction == TradeType.Buy) ? (ti.Ema > ti.Vwap) : (ti.Ema < ti.Vwap);
 if (!pass) blockReason = "Neutral trend, EMA vs VWAP disagrees";
 }
 break;

 default:
 pass = false;
 blockReason = "Neutral trend, unknown policy";
 break;
 }
 }

 if (TrendFilterVerboseLogs)
 {
 Log("TREND_FILTER side={0} {1} pass={2} reason={3}",
 direction, trendReason, pass, pass ? "aligned" : blockReason);
 }

 if (!pass)
 {
 Log("Trend filter blocked {0}: {1}", direction, blockReason);
 return;
 }
 }

 // Safety: max spread
 if (MaxSpreadPips > 0)
 {
 double spreadPips = (Symbol.Ask - Symbol.Bid) / Symbol.PipSize;
 if (spreadPips > MaxSpreadPips)
 {
 Log("SAFETY: Spread {0:F1} pips > max {1}. Skipping.", spreadPips, MaxSpreadPips);
 return;
 }
 }

 // Safety: max distance beyond threshold
 if (MaxDistanceBeyondThresholdPips > 0)
 {
 double entryEst = (direction == TradeType.Buy) ? Symbol.Ask : Symbol.Bid;
 double threshold = (direction == TradeType.Buy) ? longThreshold : shortThreshold;
 double distPips;
 if (direction == TradeType.Buy)
 distPips = (entryEst - threshold) / Symbol.PipSize;
 else
 distPips = (threshold - entryEst) / Symbol.PipSize;

 if (distPips > MaxDistanceBeyondThresholdPips)
 {
 Log("SAFETY: Distance beyond threshold {0:F1} pips > max {1}. Skipping.", distPips, MaxDistanceBeyondThresholdPips);
 return;
 }
 }

 Log("SIGNAL: {0} | Bars evaluated: {1} | LongThreshold={2} ShortThreshold={3}",
 direction, N, longThreshold, shortThreshold);

 EnterTrade(direction);
 }



 // =====================================================================


 // =====================================================================
 // CATCH-UP ENTRY (OPTIONAL)
 // =====================================================================

 private void TryCatchUpEntry(DateTime nowUtc)
 {
 if (!EnableCatchUpEntry)
 return;

 // Only attempt once per day (prevents spam / multiple late entries).
 if (_catchUpAttemptedToday)
 return;

 // We only care once TradingStart has begun.
 if (nowUtc < _tradingStartUtcToday)
 return;

 // We need a locked ORB to know thresholds.
 if (!_orbLocked)
 return;

 // Do not attempt catch-up if today is a no-trade day.
 if (_noTradeToday)
 {
 _catchUpAttemptedToday = true;
 return;
 }

 // After ClosePositionsTime or KillSwitchTime we never enter new trades.
 if (ClosePositionsAtKillSwitch && nowUtc >= _closePositionsUtcToday)
 {
 _catchUpAttemptedToday = true;
 return;
 }

 if (EnableKillSwitch && nowUtc >= _killSwitchUtcToday)
 {
 _catchUpAttemptedToday = true;
 return;
 }

 // No entry if a bot position is already open.
 if (HasOpenBotPosition())
 {
 _catchUpAttemptedToday = true;
 return;
 }

 // Max trades per day gate.
 if (_tradesToday >= MaxTradesPerDay)
 {
 _catchUpAttemptedToday = true;
 return;
 }

 // Re-entry mode gate (mirrors normal logic).
 if (_tradesToday > 0)
 {
 if (!_hasLastCloseReason)
 {
 _catchUpAttemptedToday = true;
 return;
 }

 if (ReEntryModeParam == ReEntryMode.AfterStopLossOnly)
 {
 if (_lastCloseReason != PositionCloseReason.StopLoss && _lastCloseReason != PositionCloseReason.StopOut)
 {
 _catchUpAttemptedToday = true;
 return;
 }
 }
 }

 // Compute thresholds.
 double longThreshold = _orbHigh + _entryOffsetPipsForDay * _pointSize;
 double shortThreshold = _orbLow - _entryOffsetPipsForDay * _pointSize;

 // Determine whether price is already outside ORB thresholds.
 // Use Ask for long (buy fills at Ask) and Bid for short (sell fills at Bid).
 double ask = Symbol.Ask;
 double bid = Symbol.Bid;

 bool longCandidate = AllowLong && ask >= longThreshold;
 bool shortCandidate = AllowShort && bid <= shortThreshold;

 if (longCandidate && shortCandidate)
 {
 Log("CATCHUP: Ambiguous (price beyond both thresholds). No trade.");
 _catchUpAttemptedToday = true;
 return;
 }

 if (!longCandidate && !shortCandidate)
 {
 Log("CATCHUP: No catch-up entry. Price is inside ORB thresholds at/after TradingStart.");
 _catchUpAttemptedToday = true;
 return;
 }

 TradeType direction = longCandidate ? TradeType.Buy : TradeType.Sell;

 // Optional: require last N closed confirmation bars to show "breakout evidence" beyond the threshold.
 // This treats breakout as a STATE (still beyond) rather than an EVENT (crossed this bar).
 if (CatchUpRequiresConfirmationBars)
 {
 int N = Math.Max(1, ConfirmationBarsCount);
 int lastClosed = _confirmBars.Count - 2;
 if (lastClosed < N - 1)
 {
 // Not enough bars yet (rare if TradingStart is late). Try later.
 return;
 }

 for (int k = 0; k < N; k++)
 {
 int idx = lastClosed - (N - 1) + k;
 if (idx < 0)
 return;

 bool ok = (direction == TradeType.Buy)
 ? CheckBarBeyondThresholdLongForCatchUp(idx, longThreshold)
 : CheckBarBeyondThresholdShortForCatchUp(idx, shortThreshold);

 if (!ok)
 {
 Log("CATCHUP: Confirmation bars do not support {0}. No catch-up entry.", direction);
 _catchUpAttemptedToday = true;
 return;
 }
 }
 }

 // Trend filter gate
 if (EnableTrendFilter)
 {
 TrendInfo ti = GetTrendInfo();
 string trendReason = ti.Reason;
 TrendBias bias = ti.Bias;

 bool pass = true;
 string blockReason = "";

 if (bias == TrendBias.Bullish && direction == TradeType.Sell)
 {
 pass = false;
 blockReason = "Bullish trend blocks SHORT";
 }
 else if (bias == TrendBias.Bearish && direction == TradeType.Buy)
 {
 pass = false;
 blockReason = "Bearish trend blocks LONG";
 }
 else if (bias == TrendBias.Neutral)
 {
 switch (TrendNeutralPolicyParam)
 {
 case TrendNeutralPolicy.BlockAll:
 pass = false;
 blockReason = "Neutral trend, policy=BlockAll";
 break;

 case TrendNeutralPolicy.AllowBoth:
 pass = true;
 break;

 case TrendNeutralPolicy.AllowIfPriceVsEma:
 if (!ti.Valid)
 {
 pass = false;
 blockReason = "Neutral trend but trend data not ready";
 }
 else
 {
 pass = (direction == TradeType.Buy) ? (ti.Price > ti.Ema) : (ti.Price < ti.Ema);
 if (!pass) blockReason = "Neutral trend, price vs EMA disagrees";
 }
 break;

 case TrendNeutralPolicy.AllowIfEmaSlope:
 if (!ti.Valid)
 {
 pass = false;
 blockReason = "Neutral trend but trend data not ready";
 }
 else
 {
 double minSlope = NeutralMinSlopePips;
 pass = (direction == TradeType.Buy)
 ? (ti.EmaSlopePips >= minSlope)
 : (ti.EmaSlopePips <= -minSlope);
 if (!pass) blockReason = "Neutral trend, EMA slope not supportive";
 }
 break;

 case TrendNeutralPolicy.AllowIfEmaVsVwap:
 if (!ti.Valid)
 {
 pass = false;
 blockReason = "Neutral trend but trend data not ready";
 }
 else
 {
 pass = (direction == TradeType.Buy) ? (ti.Ema > ti.Vwap) : (ti.Ema < ti.Vwap);
 if (!pass) blockReason = "Neutral trend, EMA vs VWAP disagrees";
 }
 break;

 default:
 pass = false;
 blockReason = "Neutral trend, unknown policy";
 break;
 }
 }

 if (TrendFilterVerboseLogs)
 {
 Log("TREND_FILTER ctx=CATCHUP side={0} {1} pass={2} reason={3}",
 direction, trendReason, pass, pass ? "aligned" : blockReason);
 }

 if (!pass)
 {
 Log("CATCHUP: Trend filter blocked {0}: {1}", direction, blockReason);
 _catchUpAttemptedToday = true;
 return;
 }
 }

 // Safety: max spread
 if (MaxSpreadPips > 0)
 {
 double spreadPips = (Symbol.Ask - Symbol.Bid) / Symbol.PipSize;
 if (spreadPips > MaxSpreadPips)
 {
 Log("CATCHUP SAFETY: Spread {0:F1} pips > max {1}. Skipping.", spreadPips, MaxSpreadPips);
 _catchUpAttemptedToday = true;
 return;
 }
 }

 // Safety: max distance beyond threshold (catch-up can optionally have its own limit)
 double maxDist = (CatchUpMaxDistanceBeyondThresholdPips > 0)
 ? CatchUpMaxDistanceBeyondThresholdPips
 : MaxDistanceBeyondThresholdPips;

 if (maxDist > 0)
 {
 double entryEst = (direction == TradeType.Buy) ? ask : bid;
 double threshold = (direction == TradeType.Buy) ? longThreshold : shortThreshold;
 double distPips = (direction == TradeType.Buy)
 ? (entryEst - threshold) / Symbol.PipSize
 : (threshold - entryEst) / Symbol.PipSize;

 if (distPips > maxDist)
 {
 Log("CATCHUP SAFETY: Distance beyond threshold {0:F1} pips > max {1}. Skipping.", distPips, maxDist);
 _catchUpAttemptedToday = true;
 return;
 }
 }

 Log("CATCHUP SIGNAL: {0} | LongThreshold={1} ShortThreshold={2}", direction, longThreshold, shortThreshold);

 // Mark attempted BEFORE entry to avoid repeated order attempts on rapid ticks.
 _catchUpAttemptedToday = true;
 EnterTrade(direction);
 }

 // Catch-up confirmation checks: treat the breakout as a STATE (still beyond), not an EVENT (crossed this bar).
 private bool CheckBarBeyondThresholdLongForCatchUp(int barIndex, double threshold)
 {
 double open = _confirmBars.OpenPrices[barIndex];
 double close = _confirmBars.ClosePrices[barIndex];

 // Catch-Up requires CLOSED evidence beyond the threshold (safer, avoids wick-spike entries).
 if (close < threshold)
 return false;

 if (CandleDirectionRequirementParam == CandleDirectionRequirement.RequireBullishForLong_RequireBearishForShort)
 {
 if (close <= open)
 return false;
 }

 return true;
 }

 private bool CheckBarBeyondThresholdShortForCatchUp(int barIndex, double threshold)
 {
 double open = _confirmBars.OpenPrices[barIndex];
 double close = _confirmBars.ClosePrices[barIndex];

 // Catch-Up requires CLOSED evidence beyond the threshold (safer, avoids wick-spike entries).
 if (close > threshold)
 return false;

 if (CandleDirectionRequirementParam == CandleDirectionRequirement.RequireBullishForLong_RequireBearishForShort)
 {
 if (close >= open)
 return false;
 }

 return true;
 }

 // BODYCROSS + MULTI-BAR CONFIRMATION HELPERS
 // =====================================================================

 // Long: at least one BodyCross (including gap-cross) within window, AND all bars in window close >= threshold
 private bool EvaluateBodyCrossWithCloseConfirmationLong(int evalBarIndex, int N, double threshold)
 {
 int startIdx = evalBarIndex - (N - 1);
 if (startIdx < 0) return false;

 bool anyBodyCross = false;

 for (int i = startIdx; i <= evalBarIndex; i++)
 {
 double open = _confirmBars.OpenPrices[i];
 double close = _confirmBars.ClosePrices[i];

 // Must STAY beyond threshold for ALL N bars
 if (close < threshold)
 return false;

 // At least one bar must represent the actual cross
 bool bodyCross = (open <= threshold && close >= threshold);
 if (!bodyCross && i > 0)
 {
 double prevClose = _confirmBars.ClosePrices[i - 1];
 bodyCross = (prevClose <= threshold && close >= threshold);
 }

 if (bodyCross)
 {
 if (CandleDirectionRequirementParam == CandleDirectionRequirement.RequireBullishForLong_RequireBearishForShort)
 {
 if (close <= open) bodyCross = false;
 }
 if (bodyCross) anyBodyCross = true;
 }
 }

 return anyBodyCross;
 }

 // Short: at least one BodyCross (including gap-cross) within window, AND all bars in window close <= threshold
 private bool EvaluateBodyCrossWithCloseConfirmationShort(int evalBarIndex, int N, double threshold)
 {
 int startIdx = evalBarIndex - (N - 1);
 if (startIdx < 0) return false;

 bool anyBodyCross = false;

 for (int i = startIdx; i <= evalBarIndex; i++)
 {
 double open = _confirmBars.OpenPrices[i];
 double close = _confirmBars.ClosePrices[i];

 // Must STAY beyond threshold for ALL N bars
 if (close > threshold)
 return false;

 // At least one bar must represent the actual cross
 bool bodyCross = (open >= threshold && close <= threshold);
 if (!bodyCross && i > 0)
 {
 double prevClose = _confirmBars.ClosePrices[i - 1];
 bodyCross = (prevClose >= threshold && close <= threshold);
 }

 if (bodyCross)
 {
 if (CandleDirectionRequirementParam == CandleDirectionRequirement.RequireBullishForLong_RequireBearishForShort)
 {
 if (close >= open) bodyCross = false;
 }
 if (bodyCross) anyBodyCross = true;
 }
 }

 return anyBodyCross;
 }

// =====================================================================
 // BREAKOUT CHECK HELPERS
 // =====================================================================

 private bool CheckBarBreakoutLong(int barIndex, double threshold)
 {
 double open = _confirmBars.OpenPrices[barIndex];
 double high = _confirmBars.HighPrices[barIndex];
 double close = _confirmBars.ClosePrices[barIndex];

 bool crossOk = false;
 switch (BreakoutCrossTypeParam)
 {
 case BreakoutCrossType.CloseBeyond: crossOk = close >= threshold; break;
 case BreakoutCrossType.BodyCross:
 crossOk = open <= threshold && close >= threshold;
 // Gap-cross support: if the bar OPENS already beyond the threshold,
 // treat it as a valid breakout if the PREVIOUS bar closed on the other side.
 if (!crossOk && barIndex > 0)
 {
 double prevClose = _confirmBars.ClosePrices[barIndex - 1];
 crossOk = prevClose <= threshold && close >= threshold;
 }
 break;
 case BreakoutCrossType.WickBeyond: crossOk = high >= threshold; break;
 }
 if (!crossOk) return false;

 if (CandleDirectionRequirementParam == CandleDirectionRequirement.RequireBullishForLong_RequireBearishForShort)
 {
 if (close <= open) return false;
 }
 return true;
 }

 private bool CheckBarBreakoutShort(int barIndex, double threshold)
 {
 double open = _confirmBars.OpenPrices[barIndex];
 double low = _confirmBars.LowPrices[barIndex];
 double close = _confirmBars.ClosePrices[barIndex];

 bool crossOk = false;
 switch (BreakoutCrossTypeParam)
 {
 case BreakoutCrossType.CloseBeyond: crossOk = close <= threshold; break;
 case BreakoutCrossType.BodyCross:
 crossOk = open >= threshold && close <= threshold;
 // Gap-cross support: if the bar OPENS already beyond the threshold,
 // treat it as a valid breakout if the PREVIOUS bar closed on the other side.
 if (!crossOk && barIndex > 0)
 {
 double prevClose = _confirmBars.ClosePrices[barIndex - 1];
 crossOk = prevClose >= threshold && close <= threshold;
 }
 break;
 case BreakoutCrossType.WickBeyond: crossOk = low <= threshold; break;
 }
 if (!crossOk) return false;

 if (CandleDirectionRequirementParam == CandleDirectionRequirement.RequireBullishForLong_RequireBearishForShort)
 {
 if (close >= open) return false;
 }
 return true;
 }

 // =====================================================================
 // TRADE ENTRY
 // =====================================================================

 private void EnterTrade(TradeType tradeType)
 {
 // Compute SL price anchored to ORB
 double slPrice;
 if (tradeType == TradeType.Buy)
 slPrice = _orbHigh - (StopLossOrbPercent / 100.0) * _orbRangePrice;
 else
 slPrice = _orbLow + (StopLossOrbPercent / 100.0) * _orbRangePrice;

 slPrice = Math.Round(slPrice / Symbol.TickSize) * Symbol.TickSize;

 double expectedEntry = (tradeType == TradeType.Buy) ? Symbol.Ask : Symbol.Bid;

 // Safety: Ensure we only enter if price is still on the correct side of the breakout threshold.
 // This prevents "wick beyond" signals from entering after price has already retraced back inside the ORB.
 if (RequireEntryBeyondThreshold)
 {
 double entryBufferPrice = _entryOffsetPipsForDay * _pointSize;
 double longThresholdNow = _orbHigh + entryBufferPrice;
 double shortThresholdNow = _orbLow - entryBufferPrice;

 if (tradeType == TradeType.Buy && expectedEntry < longThresholdNow)
 {
 Log("SAFETY: Entry not beyond LONG threshold at entry time. Entry={0}, Threshold={1}. Skipping.",
 expectedEntry.ToString("F" + Symbol.Digits),
 longThresholdNow.ToString("F" + Symbol.Digits));
 return;
 }

 if (tradeType == TradeType.Sell && expectedEntry > shortThresholdNow)
 {
 Log("SAFETY: Entry not beyond SHORT threshold at entry time. Entry={0}, Threshold={1}. Skipping.",
 expectedEntry.ToString("F" + Symbol.Digits),
 shortThresholdNow.ToString("F" + Symbol.Digits));
 return;
 }
 }


 double estimatedRiskPips = Math.Abs(expectedEntry - slPrice) / Symbol.PipSize;
 if (estimatedRiskPips <= 0)
 {
 Log("ERROR: initialRiskPips <= 0. SL={0} Entry={1}. Cannot trade.", slPrice, expectedEntry);
 return;
 }

 // Safety: min risk pips
 if (MinRiskPips > 0 && estimatedRiskPips < MinRiskPips)
 {
 Log("SAFETY: Risk {0:F1} pips < min {1}. Skipping.", estimatedRiskPips, MinRiskPips);
 return;
 }

 // Check SL is on correct side
 if (tradeType == TradeType.Buy && slPrice >= expectedEntry)
 {
 Log("ERROR: SL ({0}) >= entry ({1}) for LONG. Cannot trade.", slPrice, expectedEntry);
 return;
 }
 if (tradeType == TradeType.Sell && slPrice <= expectedEntry)
 {
 Log("ERROR: SL ({0}) <= entry ({1}) for SHORT. Cannot trade.", slPrice, expectedEntry);
 return;
 }

 // Volume sizing with fixed risk
 double riskInAccountCcy = GetRiskInAccountCurrency();
 if (riskInAccountCcy <= 0)
 {
 Log("ERROR: Risk amount in account currency is <= 0. Cannot trade.");
 return;
 }


double volumeInUnits;

// --- Execution Risk sizing ---
// We size for the NORMAL intended risk (riskInAccountCcy) based on the SL distance (estimatedRiskPips),
// but we ALSO apply an optional cap so that even if the stop fills worse by AssumedStopSlippagePips,
// the loss should not exceed MaxLossPerTradeAccountCcy (in account currency).
//
// This cannot guarantee exact maximum loss in real markets (gaps can exceed any assumption),
// but it materially reduces the chance of losing far more than intended.

double volumeRisk;
try
{
 volumeRisk = Symbol.VolumeForFixedRisk(riskInAccountCcy, estimatedRiskPips, RoundingMode.Down);
}
catch (Exception ex)
{
 Log("ERROR: VolumeForFixedRisk failed: {0}. Falling back to manual calc.", ex.Message);
 if (Symbol.PipValue <= 0 || estimatedRiskPips <= 0)
 {
 Log("ERROR: Cannot compute volume. PipValue={0} riskPips={1}", Symbol.PipValue, estimatedRiskPips);
 return;
 }
 volumeRisk = riskInAccountCcy * Symbol.LotSize / (estimatedRiskPips * Symbol.PipValue);
}

volumeRisk = Symbol.NormalizeVolumeInUnits(volumeRisk, RoundingMode.Down);

// Optional cap volume for worst-case stop slippage
double volumeCap = volumeRisk;
if (EnableExecutionRiskCap && MaxLossPerTradeAccountCcy > 0 && AssumedStopSlippagePips > 0)
{
 double worstCasePips = estimatedRiskPips + AssumedStopSlippagePips;
 if (worstCasePips > 0)
 {
 try
 {
 volumeCap = Symbol.VolumeForFixedRisk(MaxLossPerTradeAccountCcy, worstCasePips, RoundingMode.Down);
 }
 catch
 {
 // Fallback: derive volumeCap manually
 if (Symbol.PipValue > 0)
 volumeCap = MaxLossPerTradeAccountCcy * Symbol.LotSize / (worstCasePips * Symbol.PipValue);
 }

 volumeCap = Symbol.NormalizeVolumeInUnits(volumeCap, RoundingMode.Down);

 if (volumeCap < Symbol.VolumeInUnitsMin)
 {
 Log("EXECUTION_RISK: VolumeCap {0} < minimum {1} (riskPips={2:F1}, slipAssumed={3:F1}). Skipping trade.",
 volumeCap, Symbol.VolumeInUnitsMin, estimatedRiskPips, AssumedStopSlippagePips);
 return;
 }

 // Use the smaller of the two volumes
 if (volumeCap < volumeRisk)
 {
 Log("EXECUTION_RISK: Clamping volume for gap/slippage. VolRisk={0} -> VolCap={1} (riskPips={2:F1}, slipAssumed={3:F1}, maxLoss={4:F2}).",
 volumeRisk, volumeCap, estimatedRiskPips, AssumedStopSlippagePips, MaxLossPerTradeAccountCcy);
 }
 }
}

volumeInUnits = Math.Min(volumeRisk, volumeCap);
volumeInUnits = Symbol.NormalizeVolumeInUnits(volumeInUnits, RoundingMode.Down);

 if (volumeInUnits < Symbol.VolumeInUnitsMin)
 {
 Log("ERROR: Volume {0} < minimum {1}. Cannot trade.", volumeInUnits, Symbol.VolumeInUnitsMin);
 return;
 }

 // Safety: max volume cap
 if (MaxVolumeInUnits > 0 && volumeInUnits > MaxVolumeInUnits)
 {
 Log("SAFETY: Volume {0} > max {1}. Clamping.", volumeInUnits, MaxVolumeInUnits);
 volumeInUnits = Symbol.NormalizeVolumeInUnits(MaxVolumeInUnits, RoundingMode.Down);
 if (volumeInUnits < Symbol.VolumeInUnitsMin)
 {
 Log("ERROR: Clamped volume {0} < minimum {1}. Cannot trade.", volumeInUnits, Symbol.VolumeInUnitsMin);
 return;
 }
 }

 // Safety: Avoid opening positions that would consume too much margin (can trigger stop-out / liquidation).
 if (EnableMarginSafety && MaxMarginUsagePercent > 0)
 {
 double freeMargin = System.Convert.ToDouble(Account.FreeMargin);

 if (freeMargin <= 0)
 {
 Log("SAFETY: Free margin is <= 0 ({0}). Skipping trade.", freeMargin);
 return;
 }

 double allowedMargin = freeMargin * (MaxMarginUsagePercent / 100.0);
 double estimatedMargin = Symbol.GetEstimatedMargin(tradeType, volumeInUnits);

 if (estimatedMargin > 0 && estimatedMargin > allowedMargin)
 {
 if (!ClampVolumeToMargin)
 {
 Log("SAFETY: Estimated margin {0} exceeds allowed {1} (FreeMargin {2} * {3}%). Skipping.",
 estimatedMargin, allowedMargin, freeMargin, MaxMarginUsagePercent);
 return;
 }

 // Margin scales approximately linearly with volume, so clamp proportionally.
 double clampedVol = volumeInUnits * (allowedMargin / estimatedMargin);
 clampedVol = Symbol.NormalizeVolumeInUnits(clampedVol, RoundingMode.Down);

 if (clampedVol < Symbol.VolumeInUnitsMin)
 {
 Log("SAFETY: Margin cap would reduce volume below minimum. EstMargin={0}, AllowedMargin={1}. Skipping.",
 estimatedMargin, allowedMargin);
 return;
 }

 Log("SAFETY: Clamping volume due to margin. RequestedVol={0}, ClampedVol={1}, EstMargin={2}, AllowedMargin={3}.",
 volumeInUnits, clampedVol, estimatedMargin, allowedMargin);

 volumeInUnits = clampedVol;
 }
 }

 string label = string.Format("{0}_{1}_{2}", BotLabelPrefix, SymbolName, _currentSessionDate.ToString("yyyyMMdd"));

 var result = ExecuteMarketOrder(tradeType, SymbolName, volumeInUnits, label, null, null);

 if (!result.IsSuccessful)
 {
 Log("ORDER FAILED: {0}", result.Error);
 return;
 }

 var position = result.Position;
 double entryPriceActual = position.EntryPrice;
 double initialRiskPipsActual = Math.Abs(entryPriceActual - slPrice) / Symbol.PipSize;

 if (initialRiskPipsActual <= 0)
 {
 Log("ERROR: Actual risk pips <= 0 after fill. Entry={0} SL={1}. Closing position.", entryPriceActual, slPrice);
 ClosePosition(position);
 return;
 }

 double effectiveTpR = TakeProfitR;
 if (EnableMultiTp) effectiveTpR = _maxTpR;

 double tpDistancePips = effectiveTpR * initialRiskPipsActual;
 double tpPrice;
 if (tradeType == TradeType.Buy)
 tpPrice = entryPriceActual + tpDistancePips * Symbol.PipSize;
 else
 tpPrice = entryPriceActual - tpDistancePips * Symbol.PipSize;

 tpPrice = Math.Round(tpPrice / Symbol.TickSize) * Symbol.TickSize;

 // Apply protection. If the exact ORB-anchored protection fails, try a safer fallback SL.
 double slPriceApplied = slPrice;
 double tpPriceApplied = tpPrice;
 double riskPipsApplied = initialRiskPipsActual;

 var protectResult = ModifyPosition(position, slPrice, tpPrice, ProtectionType.Absolute, false, StopTriggerMethod.Trade);

 if (!protectResult.IsSuccessful)
 {
 Log("ERROR: Failed to set SL/TP on position {0}. Error={1}. Attempting fallback protection...",
 position.Id, protectResult.Error);

 bool fallbackOk = TryApplyInitialProtectionWithFallback(
 position,
 tradeType,
 slPrice,
 tpPrice,
 entryPriceActual,
 effectiveTpR,
 initialRiskPipsActual,
 out slPriceApplied,
 out tpPriceApplied,
 out riskPipsApplied);

 if (!fallbackOk || !position.StopLoss.HasValue)
 {
 Log("ERROR: Failed to apply SL protection (including fallback) on position {0}. Closing to enforce risk.", position.Id);
 ClosePosition(position);
 return;
 }
 }

 // Final protection verification: SL must exist.
 if (!position.StopLoss.HasValue)
 {
 Log("ERROR: Position {0} has no StopLoss after protection attempts. Closing to enforce risk.", position.Id);
 ClosePosition(position);
 return;
 }

 // Use actual applied levels (safer than assuming desired levels were accepted).
 slPriceApplied = position.StopLoss.Value;
 tpPriceApplied = position.TakeProfit.HasValue ? position.TakeProfit.Value : tpPriceApplied;
 riskPipsApplied = Math.Abs(entryPriceActual - slPriceApplied) / Symbol.PipSize;

 if (riskPipsApplied <= 0)
 {
 Log("ERROR: Applied risk pips <= 0 after protection. Entry={0} SL={1}. Closing position.", entryPriceActual, slPriceApplied);
 ClosePosition(position);
 return;
 }

 _tradesToday++;

 var state = new PositionState
 {
 PositionId = position.Id,
 EntryPrice = entryPriceActual,
 SLPriceInitial = slPriceApplied,
 InitialRiskPipsActual = riskPipsApplied,
 InitialVolumeInUnits = position.VolumeInUnits,
 EarlyRiskReductionDone = false,
 BreakEvenDone = false,
 TP1Done = false, TP2Done = false, TP3Done = false, TP4Done = false,
 LastTrailSteps = -1
 };
 _positionStates[position.Id] = state;

 Log("TRADE ENTERED: {0} {1} vol={2} entry={3} SL={4} TP={5} riskPips={6:F1} label={7}",
 tradeType, SymbolName, position.VolumeInUnits, entryPriceActual, slPriceApplied, tpPriceApplied,
 riskPipsApplied, label);

 // Verbose logging
 if (VerboseLogging)
 {
 double spreadPts = (Symbol.Ask - Symbol.Bid) / _pointSize;
 Print("[{0}] ENTRY_DIAG symbol={1} side={2} volume={3} entry={4} sl={5} tp={6} riskPips={7:F2} spreadPts={8:F2} Account.Balance={9:F2} Account.Equity={10:F2} Account.Margin={11:F2} Account.FreeMargin={12:F2} Account.MarginLevel={13}",
 BotLabelPrefix, SymbolName, tradeType, position.VolumeInUnits,
 entryPriceActual, slPriceApplied, tpPriceApplied, riskPipsApplied, spreadPts,
 Account.Balance, Account.Equity, Account.Margin, Account.FreeMargin,
 (!Account.MarginLevel.HasValue || double.IsNaN(Account.MarginLevel.Value) || double.IsInfinity(Account.MarginLevel.Value)) ? "N/A" : Account.MarginLevel.Value.ToString("F2"));
 if (EnableDebugLogging)
 {
 Print("[{0}] EXECUTION_RISK_DIAG enabled={1} slipAssumedPips={2:F1} maxLoss={3:F2}",
 label, EnableExecutionRiskCap, AssumedStopSlippagePips, MaxLossPerTradeAccountCcy);
 }
 }
 }

 private bool TryApplyInitialProtectionWithFallback(
 Position position,
 TradeType tradeType,
 double desiredSlPrice,
 double desiredTpPrice,
 double entryPrice,
 double effectiveTpR,
 double initialRiskPipsActual,
 out double slPriceApplied,
 out double tpPriceApplied,
 out double riskPipsApplied)
 {
 slPriceApplied = desiredSlPrice;
 tpPriceApplied = desiredTpPrice;
 riskPipsApplied = initialRiskPipsActual;

 // 1) Sometimes TP is the culprit. Try applying SL only first.
 var slOnlyRes = ModifyPosition(position, desiredSlPrice, null, ProtectionType.Absolute, false, StopTriggerMethod.Trade);
 if (slOnlyRes.IsSuccessful && position.StopLoss.HasValue)
 {
 slPriceApplied = position.StopLoss.Value;
 riskPipsApplied = Math.Abs(entryPrice - slPriceApplied) / Symbol.PipSize;

 var tpRes = ModifyPosition(position, slPriceApplied, desiredTpPrice, ProtectionType.Absolute, false, StopTriggerMethod.Trade);
 if (tpRes.IsSuccessful && position.TakeProfit.HasValue)
 {
 tpPriceApplied = position.TakeProfit.Value;
 }
 else
 {
 tpPriceApplied = position.TakeProfit.HasValue ? position.TakeProfit.Value : double.NaN;
 Log("WARNING: SL applied but TP failed. PositionId={0} Error={1}.", position.Id, tpRes.Error);
 }

 Log("PROTECTION: SL applied via SL-only fallback. PositionId={0} SL={1} TP={2}", position.Id, slPriceApplied, tpPriceApplied);
 return true;
 }

 if (!EnableProtectionFallback)
 return false;

 // 2) Fixed-pip fallback SL anchored to actual entry (TP uses the same effective R).
 double fallbackStopPips = Math.Max(FallbackStopLossPips, MinRiskPips);
 if (fallbackStopPips < initialRiskPipsActual)
 fallbackStopPips = initialRiskPipsActual; // do not tighten on fallback; only widen or match

 if (fallbackStopPips <= 0)
 return false;

 double fallbackSlPrice = (tradeType == TradeType.Buy)
 ? entryPrice - fallbackStopPips * Symbol.PipSize
 : entryPrice + fallbackStopPips * Symbol.PipSize;
 fallbackSlPrice = Math.Round(fallbackSlPrice / Symbol.TickSize) * Symbol.TickSize;

 double fallbackTpPips = effectiveTpR * fallbackStopPips;
 double fallbackTpPrice = (tradeType == TradeType.Buy)
 ? entryPrice + fallbackTpPips * Symbol.PipSize
 : entryPrice - fallbackTpPips * Symbol.PipSize;
 fallbackTpPrice = Math.Round(fallbackTpPrice / Symbol.TickSize) * Symbol.TickSize;

 var fbRes = ModifyPosition(position, fallbackSlPrice, fallbackTpPrice, ProtectionType.Absolute, false, StopTriggerMethod.Trade);
 if (fbRes.IsSuccessful && position.StopLoss.HasValue)
 {
 slPriceApplied = position.StopLoss.Value;
 tpPriceApplied = position.TakeProfit.HasValue ? position.TakeProfit.Value : fallbackTpPrice;
 riskPipsApplied = Math.Abs(entryPrice - slPriceApplied) / Symbol.PipSize;

 Log("FALLBACK PROTECTION: Applied fallback SL/TP. PositionId={0} SL={1} TP={2} riskPips={3:F1}",
 position.Id, slPriceApplied, tpPriceApplied, riskPipsApplied);
 return true;
 }

 // 3) Last attempt: fallback SL only.
 var fbSlRes = ModifyPosition(position, fallbackSlPrice, null, ProtectionType.Absolute, false, StopTriggerMethod.Trade);
 if (fbSlRes.IsSuccessful && position.StopLoss.HasValue)
 {
 slPriceApplied = position.StopLoss.Value;
 riskPipsApplied = Math.Abs(entryPrice - slPriceApplied) / Symbol.PipSize;

 var fbTpRes = ModifyPosition(position, slPriceApplied, fallbackTpPrice, ProtectionType.Absolute, false, StopTriggerMethod.Trade);
 if (fbTpRes.IsSuccessful && position.TakeProfit.HasValue)
 {
 tpPriceApplied = position.TakeProfit.Value;
 }
 else
 {
 tpPriceApplied = position.TakeProfit.HasValue ? position.TakeProfit.Value : double.NaN;
 Log("WARNING: Fallback SL applied but TP failed. PositionId={0} Error={1}.", position.Id, fbTpRes.Error);
 }

 Log("FALLBACK PROTECTION: Applied fallback SL only. PositionId={0} SL={1} TP={2} riskPips={3:F1}",
 position.Id, slPriceApplied, tpPriceApplied, riskPipsApplied);
 return true;
 }

 return false;
 }

 // =====================================================================
 // RISK CURRENCY CONVERSION
 // =====================================================================

 private double GetRiskInAccountCurrency()
 {
 string accountCcy = Account.Asset.Name;

 if (RiskCurrencyParam == RiskCurrency.AccountCurrency)
 return RiskAmount;

 string fromCcy = RiskCurrencyParam == RiskCurrency.GBP ? "GBP" : "USD";

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

 // =====================================================================
 // POSITION MANAGEMENT (OnTick)
 // =====================================================================

 private void ManageOpenPositions()
 {
 foreach (var pos in Positions)
 {
 if (!IsBotPosition(pos) || IsIgnorableDustPosition(pos)) continue;

 PositionState state;
 if (!_positionStates.TryGetValue(pos.Id, out state))
 continue;

 double profitPips = pos.Pips;
 double profitR = profitPips / state.InitialRiskPipsActual;

 if (EnableMultiTp) ProcessPartialTp(pos, state, profitPips);
 if (EnableEarlyRiskReduction && !state.EarlyRiskReductionDone) ProcessEarlyRiskReduction(pos, state, profitR);
 if (EnableDynamicStop) ProcessDynamicStop(pos, state, profitR);
 }
 }

 // =====================================================================
 // MULTI TP PARTIAL CLOSES
 // =====================================================================

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

 private bool ExecutePartialClose(Position pos, double initialVolume, double closePercent, string tpLabel, double tpR)
 {
 // Percent-based scaling uses the INITIAL volume so the TP ladder is stable
 double desiredClose = initialVolume * (closePercent / 100.0);

 double minVol = Symbol.VolumeInUnitsMin;
 double step = GetVolumeStepSafe();
 double tol = Math.Max(1e-12, step * 1e-6);

 // Quantize the requested close DOWN to the broker step (prevents BadVolume)
 double requestedClose = NormalizeVolumeDownRequested(desiredClose);

 if (requestedClose < minVol)
 {
 Log("{0} skipped: computed volume {1} < min {2}. Marking done.", tpLabel, requestedClose, minVol);
 return true;
 }

 // Cap to what is actually closeable *right now* (never exceed remaining)
 double maxCloseable = NormalizeVolumeDownSafe(pos.VolumeInUnits);
 double closeVolume = Math.Min(requestedClose, maxCloseable);

 if (closeVolume < minVol)
 {
 // Remaining is likely very small or just under min due to floating residue.
 // Let the full-close logic handle it.
 return TryClosePositionSafely(pos, string.Format("{0} (cap<min) at {1:F2}R", tpLabel, tpR));
 }

 // If the computed close is >= remaining volume (within tolerance), treat as a full close request
 if (closeVolume >= pos.VolumeInUnits - tol)
 {
 return TryClosePositionSafely(pos, string.Format("{0} FULL CLOSE at {1:F2}R", tpLabel, tpR));
 }

 // If this partial close would leave an un-closeable remainder (< min), close the whole position now.
 double remainingAfter = pos.VolumeInUnits - closeVolume;
 if (remainingAfter > 0 && remainingAfter < minVol)
 {
 Log("{0} partial would leave remainder {1} < min {2}. Closing FULL position instead.", tpLabel, remainingAfter, minVol);
 return TryClosePositionSafely(pos, string.Format("{0} DUST FULL CLOSE at {1:F2}R", tpLabel, tpR));
 }

 // Submit the partial close.
 var result = ClosePosition(pos, closeVolume);
 if (result.IsSuccessful)
 {
 Log("{0} partial close: {1:F1}% at {2:F2}R ({3} units)", tpLabel, closePercent, tpR, closeVolume);
 return true;
 }

 // If BadVolume, step down one step and retry once (avoids spam)
 if (result.Error == ErrorCode.BadVolume && step > 0)
 {
 double v = NormalizeVolumeDownSafe(closeVolume - step);
 if (v >= minVol && v <= pos.VolumeInUnits + tol)
 {
 var r2 = ClosePosition(pos, v);
 if (r2.IsSuccessful)
 {
 Log("{0} partial close (stepped down): {1:F1}% at {2:F2}R ({3} units)", tpLabel, closePercent, tpR, v);
 return true;
 }

 result = r2;
 }
 }

 Log("{0} partial close FAILED: {1}", tpLabel, result.Error);
 return false;
 }

 // =====================================================================
 // EARLY RISK REDUCTION
 // =====================================================================

 private void ProcessEarlyRiskReduction(Position pos, PositionState state, double profitR)
 {
 if (state.EarlyRiskReductionDone || state.BreakEvenDone) return;
 if (profitR < EarlyRiskReductionTriggerR) return;
 if (EnableDynamicStop && profitR >= BreakEvenTriggerR) return;

 double remainingRiskPips = state.InitialRiskPipsActual * (EarlyRiskReductionRemainingRiskPercent / 100.0);

 double desiredSL;
 if (pos.TradeType == TradeType.Buy)
 desiredSL = state.EntryPrice - remainingRiskPips * Symbol.PipSize;
 else
 desiredSL = state.EntryPrice + remainingRiskPips * Symbol.PipSize;

 desiredSL = Math.Round(desiredSL / Symbol.TickSize) * Symbol.TickSize;

 if (pos.StopLoss.HasValue)
 {
 if (pos.TradeType == TradeType.Buy && desiredSL <= pos.StopLoss.Value) return;
 if (pos.TradeType == TradeType.Sell && desiredSL >= pos.StopLoss.Value) return;
 }

 ModifyPosition(pos, desiredSL, pos.TakeProfit, ProtectionType.Absolute, false, StopTriggerMethod.Trade);
 state.EarlyRiskReductionDone = true;

 Log("EARLY RISK REDUCTION: SL moved to {0} (remaining risk {1:F1}% at {2:F2}R)",
 desiredSL, EarlyRiskReductionRemainingRiskPercent, profitR);
 }

 // =====================================================================
 // DYNAMIC STOP (BREAK EVEN + TRAILING)
 // =====================================================================

 private void ProcessDynamicStop(Position pos, PositionState state, double profitR)
 {
 if (profitR < BreakEvenTriggerR) return;

 double desiredSL;

 if (!state.BreakEvenDone)
 {
 if (pos.TradeType == TradeType.Buy)
 desiredSL = state.EntryPrice + BreakEvenExtraPips * Symbol.PipSize;
 else
 desiredSL = state.EntryPrice - BreakEvenExtraPips * Symbol.PipSize;

 desiredSL = Math.Round(desiredSL / Symbol.TickSize) * Symbol.TickSize;

 bool shouldMove = true;
 if (pos.StopLoss.HasValue)
 {
 if (pos.TradeType == TradeType.Buy && desiredSL <= pos.StopLoss.Value) shouldMove = false;
 if (pos.TradeType == TradeType.Sell && desiredSL >= pos.StopLoss.Value) shouldMove = false;
 }

 if (shouldMove)
 {
 ModifyPosition(pos, desiredSL, pos.TakeProfit, ProtectionType.Absolute, false, StopTriggerMethod.Trade);
 Log("BREAK EVEN: SL moved to {0} (entry + {1} extra pips)", desiredSL, BreakEvenExtraPips);
 }
 state.BreakEvenDone = true;
 }

 if (DynamicStepR > 0)
 {
 double steps = Math.Floor((profitR - BreakEvenTriggerR) / DynamicStepR);
 if (steps < 0) steps = 0;

 if (steps > state.LastTrailSteps)
 {
 double lockedR = steps * DynamicStepR;
 double lockInPips = BreakEvenExtraPips + lockedR * state.InitialRiskPipsActual;

 if (pos.TradeType == TradeType.Buy)
 desiredSL = state.EntryPrice + lockInPips * Symbol.PipSize;
 else
 desiredSL = state.EntryPrice - lockInPips * Symbol.PipSize;

 desiredSL = Math.Round(desiredSL / Symbol.TickSize) * Symbol.TickSize;

 bool shouldMove = true;
 if (pos.StopLoss.HasValue)
 {
 if (pos.TradeType == TradeType.Buy && desiredSL <= pos.StopLoss.Value) shouldMove = false;
 if (pos.TradeType == TradeType.Sell && desiredSL >= pos.StopLoss.Value) shouldMove = false;
 }

 if (shouldMove)
 {
 ModifyPosition(pos, desiredSL, pos.TakeProfit, ProtectionType.Absolute, false, StopTriggerMethod.Trade);
 Log("TRAIL: SL -> {0} (locked {1:F2}R, steps={2}, profitR={3:F2})",
 desiredSL, lockedR, steps, profitR);
 }
 state.LastTrailSteps = steps;
 }
 }
 }

 // =====================================================================
 // FORCE CLOSE
 // =====================================================================

 private void LogCloseFailThrottled(long posId, string format, params object[] args)
 {
 // Avoid flooding the log if we get stuck in a BadVolume loop
 DateTime nowUtc = Server.Time;

 DateTime lastLog;
 if (_lastCloseFailLogUtcByPosId != null && _lastCloseFailLogUtcByPosId.TryGetValue(posId, out lastLog))
 {
 if ((nowUtc - lastLog).TotalSeconds < 10)
 return;
 }

 if (_lastCloseFailLogUtcByPosId != null)
 _lastCloseFailLogUtcByPosId[posId] = nowUtc;

 Log(format, args);
 }

 private bool TryClosePositionSafely(Position pos, string context)
 {
 DateTime nowUtc = Server.Time;

 // Exponential backoff per position (prevents hammering the broker / flooding Trade logs)
 if (_closeBackoffByPosId != null)
 {
 CloseBackoffState st;
 if (_closeBackoffByPosId.TryGetValue(pos.Id, out st))
 {
 if (nowUtc < st.NextAttemptUtc)
 return false;
 }
 }

 double minVol = Symbol.VolumeInUnitsMin;
 double step = GetVolumeStepSafe();
 double posVol = pos.VolumeInUnits;
 double tol = Math.Max(1e-12, step * 1e-6);

 // If the position is effectively flat (floating dust / ghost remainder), stop trying to close it
 // and (critically) do NOT count it as an open position.
 if (IsIgnorableDustVolume(posVol))
 {
 if (_closeBackoffByPosId != null) _closeBackoffByPosId.Remove(pos.Id);

 LogCloseFailThrottled(pos.Id,
 "{0}: Ignoring dust/ghost position {1} vol={2} (min={3}).",
 context, pos.Label, posVol, minVol);

 return true;
 }

 // Compute a close volume that is guaranteed NOT to exceed the remaining position volume.
 // This fixes the classic cTrader floating residue case:
 // remaining=0.29999999999999993, Normalize(...)=0.3 -> BadVolume.
 double closeVol = NormalizeVolumeDownSafe(posVol);

 // If we're just under minVol due to floating residue (e.g., 0.09999999999999998), try closing minVol.
 if (closeVol < minVol && posVol >= (minVol - tol))
 closeVol = NormalizeVolumeNearestStrict(minVol);

 if (closeVol < minVol)
 {
 // We cannot send a valid market close (broker min size).
 LogCloseFailThrottled(pos.Id,
 "{0}: STUCK position {1} vol={2} < min={3}. Unable to close via market order.",
 context, pos.Label, posVol, minVol);

 ScheduleCloseBackoff(pos.Id, nowUtc, hardFail: true);
 return false;
 }

 // Final clamp: never try to close more than we have (even with float noise)
 if (closeVol > posVol + tol)
 closeVol = NormalizeVolumeDownSafe(posVol);

 var res = ClosePosition(pos, closeVol);
 if (res.IsSuccessful)
 {
 bool fullyClosed = closeVol >= posVol - tol;

 if (fullyClosed)
 {
 Log("{0}: CLOSE OK {1} closeVol={2} (posVol{3}) P/L={4:F2}", context, pos.Label, closeVol, posVol, pos.NetProfit);
 if (_closeBackoffByPosId != null) _closeBackoffByPosId.Remove(pos.Id);
 return true;
 }

 Log("{0}: PARTIAL close OK {1} closeVol={2} (posVol{3})", context, pos.Label, closeVol, posVol);

 // quick retry after partial progress
 if (_closeBackoffByPosId != null)
 _closeBackoffByPosId[pos.Id] = new CloseBackoffState { FailCount = 0, NextAttemptUtc = nowUtc.AddSeconds(1) };

 return false;
 }

 // If BadVolume, step down one (or two) steps and retry quickly.
 if (res.Error == ErrorCode.BadVolume && step > 0)
 {
 double v = closeVol;
 for (int i = 0; i < 2; i++)
 {
 v = NormalizeVolumeDownSafe(v - step);
 if (v < minVol) break;
 if (v > posVol + tol) continue;

 var r2 = ClosePosition(pos, v);
 if (r2.IsSuccessful)
 {
 bool fullyClosed = v >= posVol - tol;

 if (fullyClosed)
 {
 Log("{0}: CLOSE OK {1} closeVol={2} (posVol{3}) P/L={4:F2}", context, pos.Label, v, posVol, pos.NetProfit);
 if (_closeBackoffByPosId != null) _closeBackoffByPosId.Remove(pos.Id);
 return true;
 }

 Log("{0}: PARTIAL close OK {1} closeVol={2} (posVol{3})", context, pos.Label, v, posVol);

 if (_closeBackoffByPosId != null)
 _closeBackoffByPosId[pos.Id] = new CloseBackoffState { FailCount = 0, NextAttemptUtc = nowUtc.AddSeconds(1) };

 return false;
 }

 res = r2;
 if (res.Error != ErrorCode.BadVolume)
 break;
 }
 }

 LogCloseFailThrottled(pos.Id,
 "{0}: Close FAILED for {1} posVol={2} closeVol={3} step={4} min={5} error={6}",
 context, pos.Label, posVol, closeVol, step, minVol, res.Error);

 ScheduleCloseBackoff(pos.Id, nowUtc, hardFail: false);
 return false;
 }

 private void ScheduleCloseBackoff(long posId, DateTime nowUtc, bool hardFail)
 {
 if (_closeBackoffByPosId == null)
 return;

 CloseBackoffState st;
 if (!_closeBackoffByPosId.TryGetValue(posId, out st))
 st = new CloseBackoffState { FailCount = 0, NextAttemptUtc = nowUtc };

 // Escalate quickly on hard fails (e.g., < minVol), otherwise exponential-ish backoff.
 st.FailCount = Math.Max(0, st.FailCount + 1);
 int fc = st.FailCount;

 int delay = 2;
 if (hardFail) delay = 30;
 else
 {
 if (fc >= 2) delay = 5;
 if (fc >= 3) delay = 10;
 if (fc >= 4) delay = 30;
 if (fc >= 6) delay = 60;
 if (fc >= 10) delay = 300;
 }

 st.NextAttemptUtc = nowUtc.AddSeconds(delay);
 _closeBackoffByPosId[posId] = st;
 }

 private void CloseAllBotPositions(string reason)
 {
 foreach (var pos in Positions.ToArray())
 {
 if (IsBotPosition(pos) && !IsIgnorableDustPosition(pos))
 {
 TryClosePositionSafely(pos, reason + " FORCE CLOSE");
 }
 }
 }

 // =====================================================================
 // POSITION CLOSED HANDLER
 // =====================================================================

 private void OnPositionsClosed(PositionClosedEventArgs args)
 {
 var pos = args.Position;
 if (!IsBotPosition(pos)) return;

 _lastCloseReason = args.Reason;
 _hasLastCloseReason = true;
 _positionStates.Remove(pos.Id);


 if (_lastCloseAttemptUtcByPosId != null) _lastCloseAttemptUtcByPosId.Remove(pos.Id);
 if (_lastCloseFailLogUtcByPosId != null) _lastCloseFailLogUtcByPosId.Remove(pos.Id);
 if (_closeBackoffByPosId != null) _closeBackoffByPosId.Remove(pos.Id);
 Log("POSITION CLOSED: {0} reason={1} P/L={2:F2} pips={3:F1}",
 pos.Label, args.Reason, pos.NetProfit, pos.Pips);

 // Verbose close logging
 if (VerboseLogging)
 {
 string commStr;
 string swapStr;
 try { commStr = pos.Commissions.ToString("F2"); } catch { commStr = "N/A"; }
 try { swapStr = pos.Swap.ToString("F2"); } catch { swapStr = "N/A"; }

 Print("[{0}] CLOSE_DIAG label={1} reason={2} net={3:F2} gross={4:F2} commission={5} swap={6} pips={7:F1} entry={8} balance={9:F2} equity={10:F2} margin={11:F2} freeMargin={12:F2} marginLevel={13}",
 BotLabelPrefix, pos.Label, args.Reason,
 pos.NetProfit, pos.GrossProfit, commStr, swapStr,
 pos.Pips, pos.EntryPrice,
 Account.Balance, Account.Equity, Account.Margin, Account.FreeMargin,
 (!Account.MarginLevel.HasValue || double.IsNaN(Account.MarginLevel.Value) || double.IsInfinity(Account.MarginLevel.Value)) ? "N/A" : Account.MarginLevel.Value.ToString("F2"));
 }
 }

 // =====================================================================
 // HELPERS
 // =====================================================================


 // =====================================================================
 // VOLUME NORMALIZATION HELPERS (ROBUST)
 // =====================================================================

 private int GetStepDecimals(double step)
 {
 if (step <= 0) return 2;
 int decimals = 0;
 double s = step;
 // Try to find a reasonable decimal precision for typical steps (0.1, 0.01, 0.25, etc.)
 while (decimals < 8 && Math.Abs(s - Math.Round(s)) > 1e-12)
 {
 s *= 10.0;
 decimals++;
 }
 return decimals;
 }

 private double GetVolumeStepSafe()
 {
 double step = Symbol.VolumeInUnitsStep;
 if (step <= 0)
 step = Symbol.VolumeInUnitsMin;
 return step;
 }

 private double NormalizeVolumeNearestStrict(double volume)
 {
 double step = Symbol.VolumeInUnitsStep;
 if (step <= 0)
 return Symbol.NormalizeVolumeInUnits(volume, RoundingMode.ToNearest);

 double steps = Math.Round(volume / step, MidpointRounding.AwayFromZero);
 double v = steps * step;
 int dec = GetStepDecimals(step);
 v = Math.Round(v, dec, MidpointRounding.AwayFromZero);
 if (v < 0) v = 0;
 return v;
 }

 // For target/requested volumes (e.g., TP partial sizes). Slight +eps avoids off-by-one-step
 // when volume is represented as 0.5999999999999 instead of 0.6.
 private double NormalizeVolumeDownRequested(double volume)
 {
 double step = Symbol.VolumeInUnitsStep;
 if (step <= 0)
 return Symbol.NormalizeVolumeInUnits(volume, RoundingMode.Down);

 double eps = Math.Max(1e-12, step * 1e-9);
 double steps = Math.Floor((volume + eps) / step);
 double v = steps * step;
 int dec = GetStepDecimals(step);
 v = Math.Round(v, dec, MidpointRounding.AwayFromZero);
 if (v < 0) v = 0;
 return v;
 }

 // For remaining position volume. Guarantees the result is <= the input (prevents BadVolume).
 private double NormalizeVolumeDownSafe(double volume)
 {
 double step = Symbol.VolumeInUnitsStep;
 if (step <= 0)
 return Symbol.NormalizeVolumeInUnits(volume, RoundingMode.Down);

 // Use a tiny +eps to avoid the classic double issue where:
 // 2.0 / 0.1 = 19.999999999... -> Floor -> 19 (=> 1.9)
 // Then clamp back down to guarantee the result never exceeds the input volume.
 double eps = Math.Max(1e-12, step * 1e-9);
 double steps = Math.Floor((volume + eps) / step);
 double v = steps * step;
 int dec = GetStepDecimals(step);
 v = Math.Round(v, dec, MidpointRounding.AwayFromZero);

 // Hard guarantee: v must be <= volume (no tolerance; if we undershoot we can close in multiple steps)
 while (v > volume && v - step >= 0)
 v = Math.Round(v - step, dec, MidpointRounding.AwayFromZero);

 if (v < 0) v = 0;
 return v;
 }

 private bool IsIgnorableDustVolume(double volume)
 {
 double minVol = Symbol.VolumeInUnitsMin;
 double step = GetVolumeStepSafe();
 double dust = Math.Max(1e-12, Math.Min(minVol, step) * 1e-3);
 return volume <= dust;
 }

 private bool IsIgnorableDustPosition(Position pos)
 {
 return IsIgnorableDustVolume(pos.VolumeInUnits);
 }

 private bool AlmostEqual(double a, double b, double tol)
 {
 return Math.Abs(a - b) <= tol;
 }




 // =====================================================================
 // DAILY TRADE COUNT REHYDRATION (RESTART SAFETY)
 // =====================================================================
 //
 // Problem this solves:
 // - If the cBot restarts mid-session (code rebuild, VPS hiccup, reconnect, etc.)
 // _tradesToday resets to 0 because we always run ResetForDate(...) on startup.
 // - That can allow a SECOND trade on the same day even when MaxTradesPerDay = 1.
 //
 // Fix:
 // - Rebuild tradesToday from:
 // (1) any currently-open positions for today's label
 // (2) account History for today's label
 // - We de-duplicate by PositionId to avoid counting partial-TP closes as extra trades.

 private string GetBotLabelForDate(DateTime sessionDate)
 {
 return string.Format("{0}_{1}_{2}", BotLabelPrefix, SymbolName, sessionDate.ToString("yyyyMMdd"));
 }

 private int GetTradesExecutedForSessionDate(DateTime sessionDate)
 {
 string label = GetBotLabelForDate(sessionDate);
 var ids = new HashSet<long>();

 // Count any currently-open bot positions for this specific session date label
 foreach (var pos in Positions)
 {
 if (pos == null) continue;
 if (pos.SymbolName != SymbolName) continue;
 if (pos.Label != label) continue;
 if (IsIgnorableDustPosition(pos)) continue;
 ids.Add(pos.Id);
 }

 // Count any historical trades for this label (closed positions).
 // NOTE: In some cases (partial closes), History can contain multiple records for the same PositionId.
 // We only care about *entries*, so we de-duplicate by PositionId.
 try
 {
 var hist = History.FindAll(label, SymbolName);
 if (hist != null)
 {
 foreach (var ht in hist)
 {
 try { ids.Add(ht.PositionId); } catch { }
 }
 }
 }
 catch
 {
 // If History is unavailable for some reason, fall back to open positions only.
 }

 return ids.Count;
 }

 private void RehydrateTradesTodayFromHistory(string context)
 {
 try
 {
 int found = GetTradesExecutedForSessionDate(_currentSessionDate);

 if (found != _tradesToday)
 {
 Log("RESTART SAFETY: {0} | SessionDate={1:yyyy-MM-dd} | tradesToday was {2}, rehydrated to {3} (MaxTradesPerDay={4}).",
 context, _currentSessionDate, _tradesToday, found, MaxTradesPerDay);
 }

 // Set directly to the authoritative count
 _tradesToday = found;
 }
 catch (Exception ex)
 {
 Log("RESTART SAFETY: Failed to rehydrate tradesToday. {0}", ex.Message);
 }
 }
 private Position GetFirstOpenBotPosition()
 {
 foreach (var pos in Positions)
 {
 if (IsBotPosition(pos) && !IsIgnorableDustPosition(pos))
 return pos;
 }
 return null;
 }

 private void LogNearMissBreakout(int evalBarIndex, int N, double longThreshold, double shortThreshold)
 {
 if (!ExplainNearMissBreakouts) return;

 int start = evalBarIndex - (N - 1);
 if (start < 0) start = 0;

 int longWick = 0, shortWick = 0, longOk = 0, shortOk = 0;
 for (int idx = start; idx <= evalBarIndex; idx++)
 {
 if (_confirmBars.HighPrices[idx] >= longThreshold) longWick++;
 if (_confirmBars.LowPrices[idx] <= shortThreshold) shortWick++;
 if (CheckBarBreakoutLong(idx, longThreshold)) longOk++;
 if (CheckBarBreakoutShort(idx, shortThreshold)) shortOk++;
 }

 DateTime barTime = _confirmBars.OpenTimes[evalBarIndex];
 double o = _confirmBars.OpenPrices[evalBarIndex];
 double h = _confirmBars.HighPrices[evalBarIndex];
 double l = _confirmBars.LowPrices[evalBarIndex];
 double c = _confirmBars.ClosePrices[evalBarIndex];

 // Only log if price actually touched/exceeded a threshold by wick at least once in the confirmation window.
 if (longWick > 0 && longOk < N)
 {
 Log("NEAR MISS LONG: {0:HH:mm} window {1} bars touched LONG threshold by wick ({2}/{1}) but only {3}/{1} met breakout rules. CrossType={4} DirReq={5}. LastBar O={6} H={7} C={8} Thresh={9}",
 barTime, N, longWick, longOk, BreakoutCrossTypeParam, CandleDirectionRequirementParam,
 o, h, c, longThreshold);
 }

 if (shortWick > 0 && shortOk < N)
 {
 Log("NEAR MISS SHORT: {0:HH:mm} window {1} bars touched SHORT threshold by wick ({2}/{1}) but only {3}/{1} met breakout rules. CrossType={4} DirReq={5}. LastBar O={6} L={7} C={8} Thresh={9}",
 barTime, N, shortWick, shortOk, BreakoutCrossTypeParam, CandleDirectionRequirementParam,
 o, l, c, shortThreshold);
 }
 }

 private bool IsBotPosition(Position pos)
 {
 if (pos.SymbolName != SymbolName) return false;
 if (string.IsNullOrEmpty(pos.Label)) return false;
 string prefix = string.Format("{0}_{1}_", BotLabelPrefix, SymbolName);
 return pos.Label.StartsWith(prefix);
 }

 private bool HasOpenBotPosition()
 {
 foreach (var pos in Positions)
 {
 if (IsBotPosition(pos) && !IsIgnorableDustPosition(pos)) return true;
 }
 return false;
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
 PositionId = pos.Id,
 EntryPrice = pos.EntryPrice,
 SLPriceInitial = pos.StopLoss.Value,
 InitialRiskPipsActual = riskPips,
 InitialVolumeInUnits = pos.VolumeInUnits,
 EarlyRiskReductionDone = false,
 BreakEvenDone = false,
 TP1Done = false, TP2Done = false, TP3Done = false, TP4Done = false,
 LastTrailSteps = -1
 };
 Log("Registered existing position {0} riskPips={1:F1}", pos.Label, riskPips);
 }

 // =====================================================================
 // MULTI TP NORMALIZATION
 // =====================================================================

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
 Log("Multi TP percents normalized: TP1={0:F1}% TP2={1:F1}% TP3={2:F1}% TP4={3:F1}%",
 _tp1Pct, _tp2Pct, _tp3Pct, _tp4Pct);
 }
 }

 private void ComputeMaxTpR()
 {
 _maxTpR = TakeProfitR;
 if (EnableMultiTp)
 {
 if (TP1_R > 0 && _tp1Pct > 0 && TP1_R > _maxTpR) _maxTpR = TP1_R;
 if (TP2_R > 0 && _tp2Pct > 0 && TP2_R > _maxTpR) _maxTpR = TP2_R;
 if (TP3_R > 0 && _tp3Pct > 0 && TP3_R > _maxTpR) _maxTpR = TP3_R;
 if (TP4_R > 0 && _tp4Pct > 0 && TP4_R > _maxTpR) _maxTpR = TP4_R;
 }
 }

 // =====================================================================
 // DRAWING
 // =====================================================================

 private void DrawOrbLinesOnChart()
 {
 if (!DrawOrbLines || !_orbLocked) return;

 string dateStr = _currentSessionDate.ToString("yyyyMMdd");
 Chart.RemoveObject("ORB_HIGH_" + dateStr);
 Chart.RemoveObject("ORB_LOW_" + dateStr);

 DateTime lineEnd = _orbStartUtcToday.AddDays(1);
 Chart.DrawTrendLine("ORB_HIGH_" + dateStr, _orbStartUtcToday, _orbHigh, lineEnd, _orbHigh, Color.DodgerBlue, 2, LineStyle.Solid);
 Chart.DrawTrendLine("ORB_LOW_" + dateStr, _orbStartUtcToday, _orbLow, lineEnd, _orbLow, Color.DodgerBlue, 2, LineStyle.Solid);
 }

 private void DrawThresholdLinesOnChart()
 {
 if (!DrawThresholdLines || !_orbLocked || _entryOffsetPipsForDay <= 0) return;

 string dateStr = _currentSessionDate.ToString("yyyyMMdd");
 string longName = "ORB_LONG_THRESH_" + dateStr;
 string shortName = "ORB_SHORT_THRESH_" + dateStr;
 Chart.RemoveObject(longName);
 Chart.RemoveObject(shortName);

 double longThreshold = _orbHigh + _entryOffsetPipsForDay * _pointSize;
 double shortThreshold = _orbLow - _entryOffsetPipsForDay * _pointSize;

 DateTime lineEnd = _orbStartUtcToday.AddDays(1);
 Chart.DrawTrendLine(longName, _orbStartUtcToday, longThreshold, lineEnd, longThreshold, Color.LimeGreen, 1, LineStyle.Dots);
 Chart.DrawTrendLine(shortName, _orbStartUtcToday, shortThreshold, lineEnd, shortThreshold, Color.OrangeRed, 1, LineStyle.Dots);
 }

 private void RemoveOldDrawings()
 {
 DateTime prevDate = _currentSessionDate.AddDays(-1);
 string prevDateStr = prevDate.ToString("yyyyMMdd");
 Chart.RemoveObject("ORB_HIGH_" + prevDateStr);
 Chart.RemoveObject("ORB_LOW_" + prevDateStr);
 Chart.RemoveObject("ORB_LONG_THRESH_" + prevDateStr);
 Chart.RemoveObject("ORB_SHORT_THRESH_" + prevDateStr);
 }

 // =====================================================================
 // LOGGING
 // =====================================================================

 private void Log(string message, params object[] args)
 {
 if (!EnableDebugLogging) return;

 string formatted;
 if (args != null && args.Length > 0)
 {
 try { formatted = string.Format(message, args); }
 catch { formatted = message; }
 }
 else
 {
 formatted = message;
 }

 Print("[{0}] {1} {2}", BotLabelPrefix, Server.Time.ToString("yyyy-MM-dd HH:mm:ss"), formatted);
 }
 }
}