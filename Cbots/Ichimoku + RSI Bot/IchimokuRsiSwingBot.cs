using System;
using System.Collections.Generic;
using cAlgo.API;
using cAlgo.API.Indicators;

namespace cAlgo.Robots
{
    // ════════════════════════════════════════════════════════════════════
    // ENUMS — placed outside Robot class, inside namespace (per spec §3)
    // ════════════════════════════════════════════════════════════════════

    // Base enums (verbatim from base parameters reference)
    public enum RiskCurrency
    {
        AccountCurrency,
        GBP,
        USD
    }

    public enum SessionTimeZoneEnum
    {
        UTC,
        EuropeLondon,    // GMT/BST — auto DST-aware
        EuropeBerlin,    // CET/CEST — auto DST-aware
        AmericaNewYork   // EST/EDT — auto DST-aware
    }

    // Strategy-specific enums
    public enum InstrumentType
    {
        Stocks,    // Individual equities — gap-aware, exchange session hours
        Indices,   // Index CFDs — gap-aware, exchange session hours
        Forex,     // Currency pairs — near-24hr, tighter spreads
        Crypto     // Crypto CFDs — 24/7, high volatility
    }

    public enum TradeDirectionMode
    {
        Both,
        LongOnly,
        ShortOnly
    }

    public enum StopLossMethod
    {
        CloudBoundary = 1,  // Below/above Senkou Span B — Ichimoku-native
        KijunSen      = 2,  // Below/above Kijun-sen line
        ATR           = 3,  // Entry ± (AtrMultiplier × ATR)
        SwingHighLow  = 4,  // Below recent swing low / above swing high
        TenkanSen     = 5   // Below/above Tenkan-sen (tightest)
    }

    // ════════════════════════════════════════════════════════════════════
    // SUPPORT CLASSES — outside Robot class, inside namespace (per spec §3)
    // ════════════════════════════════════════════════════════════════════

    /// <summary>
    /// Per-position state. Tracks entry, initial SL, initial volume, and
    /// management flags so each feature fires exactly once.
    /// </summary>
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

    /// <summary>
    /// Exponential back-off state for safe position closing.
    /// Prevents broker flooding on repeated close failures.
    /// </summary>
    public class CloseBackoffState
    {
        public int      FailCount       { get; set; }
        public DateTime NextAttemptUtc  { get; set; }
    }

    // ════════════════════════════════════════════════════════════════════
    // ROBOT CLASS
    // ════════════════════════════════════════════════════════════════════

    [Robot(TimeZone = TimeZones.UTC, AccessRights = AccessRights.None)]
    public class IchimokuRsiSwingBot : Robot
    {
        // ────────────────────────────────────────────────────────────────
        // GROUP A — Instrument & Direction  (strategy-specific)
        // ────────────────────────────────────────────────────────────────

        [Parameter("Instrument Type", Group = "Instrument & Direction",
            DefaultValue = InstrumentType.Stocks)]
        public InstrumentType InstrumentTypeParam { get; set; }

        [Parameter("Trade Direction", Group = "Instrument & Direction",
            DefaultValue = TradeDirectionMode.Both)]
        public TradeDirectionMode TradeDirectionParam { get; set; }

        // ────────────────────────────────────────────────────────────────
        // GROUP B — Ichimoku Settings
        // ────────────────────────────────────────────────────────────────

        [Parameter("Tenkan-sen Period", Group = "Ichimoku Settings",
            DefaultValue = 9, MinValue = 2)]
        public int TenkanPeriod { get; set; }

        [Parameter("Kijun-sen Period", Group = "Ichimoku Settings",
            DefaultValue = 26, MinValue = 2)]
        public int KijunPeriod { get; set; }

        [Parameter("Senkou Span B Period", Group = "Ichimoku Settings",
            DefaultValue = 52, MinValue = 2)]
        public int SenkouSpanBPeriod { get; set; }

        [Parameter("Cloud Displacement", Group = "Ichimoku Settings",
            DefaultValue = 26, MinValue = 1)]
        public int CloudDisplacement { get; set; }
        // CRITICAL: also the lookback used to read current cloud values (spec §4.2)

        // ────────────────────────────────────────────────────────────────
        // GROUP C — RSI Settings
        // ────────────────────────────────────────────────────────────────

        [Parameter("RSI Period", Group = "RSI Settings",
            DefaultValue = 14, MinValue = 2)]
        public int RsiPeriod { get; set; }

        [Parameter("RSI Level", Group = "RSI Settings",
            DefaultValue = 50.0, MinValue = 1.0, MaxValue = 99.0)]
        public double RsiLevel { get; set; }
        // Long: RSI > RsiLevel. Short: RSI < RsiLevel.

        // ────────────────────────────────────────────────────────────────
        // GROUP D — Signal Filters
        // ────────────────────────────────────────────────────────────────

        [Parameter("Enable Chikou Confirmation", Group = "Signal Filters",
            DefaultValue = true)]
        public bool EnableChikouConfirmation { get; set; }

        [Parameter("Enable Cloud Twist Filter", Group = "Signal Filters",
            DefaultValue = true)]
        public bool EnableCloudTwistFilter { get; set; }

        [Parameter("Cloud Twist Look-Ahead Bars", Group = "Signal Filters",
            DefaultValue = 5, MinValue = 1, MaxValue = 26)]
        public int CloudTwistLookAheadBars { get; set; }

        [Parameter("Enable Min Cloud Thickness", Group = "Signal Filters",
            DefaultValue = false)]
        public bool EnableMinCloudThickness { get; set; }

        [Parameter("Min Cloud Thickness Pips", Group = "Signal Filters",
            DefaultValue = 20.0, MinValue = 0.0)]
        public double MinCloudThicknessPips { get; set; }

        // ────────────────────────────────────────────────────────────────
        // GROUP E — Stop Loss
        // ────────────────────────────────────────────────────────────────

        [Parameter("Stop Loss Method", Group = "Stop Loss",
            DefaultValue = StopLossMethod.CloudBoundary)]
        public StopLossMethod StopLossMethodParam { get; set; }

        [Parameter("SL Cloud Buffer Pips", Group = "Stop Loss",
            DefaultValue = 5.0, MinValue = 0.0)]
        public double SlCloudBufferPips { get; set; }
        // Method 1 only.

        [Parameter("SL Kijun Buffer Pips", Group = "Stop Loss",
            DefaultValue = 5.0, MinValue = 0.0)]
        public double SlKijunBufferPips { get; set; }
        // Method 2 only.

        [Parameter("ATR Period", Group = "Stop Loss",
            DefaultValue = 14, MinValue = 2)]
        public int AtrPeriod { get; set; }
        // Method 3 only.

        [Parameter("ATR Multiplier", Group = "Stop Loss",
            DefaultValue = 2.0, MinValue = 0.1)]
        public double AtrMultiplier { get; set; }
        // Method 3 only. SL distance = ATR × multiplier.

        [Parameter("Swing Lookback Bars", Group = "Stop Loss",
            DefaultValue = 10, MinValue = 3, MaxValue = 50)]
        public int SwingLookbackBars { get; set; }
        // Method 4 only.

        [Parameter("SL Swing Buffer Pips", Group = "Stop Loss",
            DefaultValue = 5.0, MinValue = 0.0)]
        public double SlSwingBufferPips { get; set; }
        // Method 4 only.

        [Parameter("SL Tenkan Buffer Pips", Group = "Stop Loss",
            DefaultValue = 3.0, MinValue = 0.0)]
        public double SlTenkanBufferPips { get; set; }
        // Method 5 only.

        // ────────────────────────────────────────────────────────────────
        // GROUP F — Session (UTC)  (base parameters — verbatim)
        // ────────────────────────────────────────────────────────────────

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

        // ────────────────────────────────────────────────────────────────
        // GROUP G — Session Time Zone  (base parameters — verbatim)
        // ────────────────────────────────────────────────────────────────

        [Parameter("Use Fixed UTC Times", Group = "Session Time Zone", DefaultValue = true)]
        public bool UseFixedUtcTimes { get; set; }

        [Parameter("Session Time Zone", Group = "Session Time Zone",
            DefaultValue = SessionTimeZoneEnum.UTC)]
        public SessionTimeZoneEnum SessionTimeZoneParam { get; set; }

        // ────────────────────────────────────────────────────────────────
        // GROUP H — Trades Per Day  (base parameters — verbatim)
        // ────────────────────────────────────────────────────────────────

        [Parameter("Max Trades Per Day", Group = "Trades Per Day",
            DefaultValue = 1, MinValue = 1)]
        public int MaxTradesPerDay { get; set; }

        // ────────────────────────────────────────────────────────────────
        // GROUP I — Trading Days  (base parameters — verbatim)
        // ────────────────────────────────────────────────────────────────

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

        // ────────────────────────────────────────────────────────────────
        // GROUP J — Take Profit  (base parameters — verbatim)
        // ────────────────────────────────────────────────────────────────

        [Parameter("Take Profit R", Group = "Take Profit",
            DefaultValue = 2.0, MinValue = 0.1)]
        public double TakeProfitR { get; set; }
        // Single TP as multiple of risk. Final runner TP when Multi TP active.

        // ────────────────────────────────────────────────────────────────
        // GROUP K — Multi Take Profit  (base parameters — verbatim)
        // ────────────────────────────────────────────────────────────────

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
        // Set TP R = 0 or Close% = 0 to disable a level.
        // Percentages auto-scaled if total > 100%.
        // Hard TP order placed at highest active TP R.

        // ────────────────────────────────────────────────────────────────
        // GROUP L — Dynamic Stop  (base parameters — verbatim)
        // ────────────────────────────────────────────────────────────────

        [Parameter("Enable Dynamic Stop", Group = "Dynamic Stop", DefaultValue = false)]
        public bool EnableDynamicStop { get; set; }

        [Parameter("Break Even Trigger R", Group = "Dynamic Stop",
            DefaultValue = 1.0, MinValue = 0.1)]
        public double BreakEvenTriggerR { get; set; }

        [Parameter("Break Even Extra Pips", Group = "Dynamic Stop",
            DefaultValue = 0.0, MinValue = 0.0)]
        public double BreakEvenExtraPips { get; set; }

        [Parameter("Dynamic Step R", Group = "Dynamic Stop",
            DefaultValue = 0.25, MinValue = 0.0)]
        public double DynamicStepR { get; set; }
        // When profitR >= BreakEvenTriggerR: SL -> entry + BreakEvenExtraPips.
        // Then trail by DynamicStepR per additional R. SL never moves backwards.

        // ────────────────────────────────────────────────────────────────
        // GROUP M — Early Risk Reduction  (base parameters — verbatim)
        // ────────────────────────────────────────────────────────────────

        [Parameter("Enable Early Risk Reduction", Group = "Early Risk Reduction",
            DefaultValue = false)]
        public bool EnableEarlyRiskReduction { get; set; }

        [Parameter("Early Risk Reduction Trigger R", Group = "Early Risk Reduction",
            DefaultValue = 0.5, MinValue = 0.1)]
        public double EarlyRiskReductionTriggerR { get; set; }

        [Parameter("Early Risk Reduction Remaining Risk %", Group = "Early Risk Reduction",
            DefaultValue = 50.0, MinValue = 1.0, MaxValue = 100.0)]
        public double EarlyRiskReductionRemainingRiskPercent { get; set; }
        // Fires once when profitR >= trigger and BreakEven not yet fired.
        // Moves SL to entry - (InitialRiskPips * RemainingRisk%).

        // ────────────────────────────────────────────────────────────────
        // GROUP N — Risk  (base parameters — verbatim)
        // ────────────────────────────────────────────────────────────────

        [Parameter("Risk Amount", Group = "Risk", DefaultValue = 100, MinValue = 1)]
        public double RiskAmount { get; set; }

        [Parameter("Risk Currency", Group = "Risk",
            DefaultValue = RiskCurrency.AccountCurrency)]
        public RiskCurrency RiskCurrencyParam { get; set; }
        // Volume auto-calculated from SL distance so exactly RiskAmount is risked.

        // ────────────────────────────────────────────────────────────────
        // GROUP O — Execution Risk Cap  (base parameters — verbatim)
        // ────────────────────────────────────────────────────────────────

        [Parameter("Enable Execution Risk Cap", Group = "Execution Risk Cap",
            DefaultValue = true)]
        public bool EnableExecutionRiskCap { get; set; }

        [Parameter("Assumed Stop Slippage Pips", Group = "Execution Risk Cap",
            DefaultValue = 30.0, MinValue = 0.0)]
        public double AssumedStopSlippagePips { get; set; }

        [Parameter("Max Loss Per Trade (Account CCY)", Group = "Execution Risk Cap",
            DefaultValue = 200.0, MinValue = 0.0)]
        public double MaxLossPerTradeAccountCcy { get; set; }
        // WorstCasePips = SLDistance + AssumedStopSlippagePips
        // Volume capped so WorstCasePips × volume <= MaxLossPerTradeAccountCcy

        // ────────────────────────────────────────────────────────────────
        // GROUP P — Safety  (base parameters — verbatim)
        // ────────────────────────────────────────────────────────────────

        [Parameter("Min Risk Pips", Group = "Safety",
            DefaultValue = 0.0, MinValue = 0.0)]
        public double MinRiskPips { get; set; }

        [Parameter("Max Volume In Units", Group = "Safety",
            DefaultValue = 0, MinValue = 0)]
        public double MaxVolumeInUnits { get; set; }

        [Parameter("Max Spread Pips", Group = "Safety",
            DefaultValue = 0, MinValue = 0)]
        public double MaxSpreadPips { get; set; }

        [Parameter("Enable Margin Safety", Group = "Safety", DefaultValue = true)]
        public bool EnableMarginSafety { get; set; }

        [Parameter("Max Margin Usage %", Group = "Safety",
            DefaultValue = 60.0, MinValue = 1.0, MaxValue = 100.0)]
        public double MaxMarginUsagePercent { get; set; }

        [Parameter("Clamp Volume To Margin", Group = "Safety", DefaultValue = true)]
        public bool ClampVolumeToMargin { get; set; }

        [Parameter("Enable Protection Fallback", Group = "Safety", DefaultValue = true)]
        public bool EnableProtectionFallback { get; set; }

        [Parameter("Fallback SL Pips", Group = "Safety",
            DefaultValue = 20.0, MinValue = 0.0)]
        public double FallbackStopLossPips { get; set; }

        // ────────────────────────────────────────────────────────────────
        // GROUP Q — Diagnostics  (base parameters — verbatim)
        // ────────────────────────────────────────────────────────────────

        [Parameter("Bot Label Prefix", Group = "Diagnostics", DefaultValue = "ICHI")]
        public string BotLabelPrefix { get; set; }

        [Parameter("Enable Debug Logging", Group = "Diagnostics", DefaultValue = true)]
        public bool EnableDebugLogging { get; set; }

        [Parameter("Verbose Logging", Group = "Diagnostics", DefaultValue = false)]
        public bool VerboseLogging { get; set; }

        [Parameter("Explain Blocked Entries", Group = "Diagnostics", DefaultValue = true)]
        public bool ExplainBlockedEntries { get; set; }

        // ════════════════════════════════════════════════════════════════
        // Stage 2 onward: state variables, OnStart, signal evaluation,
        // EnterTrade, position management, and all helper methods.
        // ════════════════════════════════════════════════════════════════

    } // end class IchimokuRsiSwingBot
} // end namespace
