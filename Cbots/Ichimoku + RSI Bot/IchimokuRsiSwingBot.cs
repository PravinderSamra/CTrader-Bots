using System;
using System.Collections.Generic;
using System.Linq;
using cAlgo.API;
using cAlgo.API.Indicators;
using cAlgo.API.Internals;

namespace cAlgo.Robots
{
    // ── Base enums (verbatim from base parameters reference) ──
    public enum RiskCurrency
    {
        AccountCurrency,
        GBP,
        USD
    }

    public enum SessionTimeZoneEnum
    {
        UTC,
        EuropeLondon,   // GMT/BST — auto DST-aware
        EuropeBerlin,   // CET/CEST — auto DST-aware
        AmericaNewYork  // EST/EDT — auto DST-aware
    }

    // ── Strategy-specific enums ──
    public enum InstrumentType
    {
        Stocks,   // Individual equities — gap-aware, exchange session hours
        Indices,  // Index CFDs — gap-aware, exchange session hours
        Forex,    // Currency pairs — near-24hr, tighter spreads
        Crypto    // Crypto CFDs — 24/7, high volatility
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
        ATR           = 3,  // Entry ± (AtrMultiplier × ATR14)
        SwingHighLow  = 4,  // Below recent swing low / above swing high
        TenkanSen     = 5   // Below/above Tenkan-sen (tightest)
    }

    // ── Base support classes (verbatim from base parameters reference) ──
    public class PositionState
    {
        public long   PositionId             { get; set; }
        public double EntryPrice             { get; set; }
        public double SLPriceInitial         { get; set; }
        public double InitialRiskPipsActual  { get; set; }
        public double InitialVolumeInUnits   { get; set; }
        public bool   EarlyRiskReductionDone { get; set; }
        public bool   BreakEvenDone          { get; set; }
        public bool   TP1Done                { get; set; }
        public bool   TP2Done                { get; set; }
        public bool   TP3Done                { get; set; }
        public bool   TP4Done                { get; set; }
        public double LastTrailSteps         { get; set; }
    }

    public class CloseBackoffState
    {
        public int      FailCount      { get; set; }
        public DateTime NextAttemptUtc { get; set; }
    }

    [Robot(TimeZone = TimeZones.UTC, AccessRights = AccessRights.None)]
    public class IchimokuRsiSwingBot : Robot
    {
        // ══════════════════════════════════════════════════════════════════
        // GROUP A — Instrument & Direction (Strategy-Specific)
        // ══════════════════════════════════════════════════════════════════

        [Parameter("Instrument Type", Group = "Instrument & Direction",
            DefaultValue = InstrumentType.Stocks)]
        public InstrumentType InstrumentTypeParam { get; set; }

        [Parameter("Trade Direction", Group = "Instrument & Direction",
            DefaultValue = TradeDirectionMode.Both)]
        public TradeDirectionMode TradeDirectionParam { get; set; }

        // ══════════════════════════════════════════════════════════════════
        // GROUP B — Ichimoku Settings
        // ══════════════════════════════════════════════════════════════════

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

        // ══════════════════════════════════════════════════════════════════
        // GROUP C — RSI Settings
        // ══════════════════════════════════════════════════════════════════

        [Parameter("RSI Period", Group = "RSI Settings",
            DefaultValue = 14, MinValue = 2)]
        public int RsiPeriod { get; set; }

        [Parameter("RSI Level", Group = "RSI Settings",
            DefaultValue = 50.0, MinValue = 1.0, MaxValue = 99.0)]
        public double RsiLevel { get; set; }

        // ══════════════════════════════════════════════════════════════════
        // GROUP D — Signal Filters
        // ══════════════════════════════════════════════════════════════════

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

        // ══════════════════════════════════════════════════════════════════
        // GROUP E — Stop Loss
        // ══════════════════════════════════════════════════════════════════

        [Parameter("Stop Loss Method", Group = "Stop Loss",
            DefaultValue = StopLossMethod.CloudBoundary)]
        public StopLossMethod StopLossMethodParam { get; set; }

        [Parameter("SL Cloud Buffer Pips", Group = "Stop Loss",
            DefaultValue = 5.0, MinValue = 0.0)]
        public double SlCloudBufferPips { get; set; }

        [Parameter("SL Kijun Buffer Pips", Group = "Stop Loss",
            DefaultValue = 5.0, MinValue = 0.0)]
        public double SlKijunBufferPips { get; set; }

        [Parameter("ATR Period", Group = "Stop Loss",
            DefaultValue = 14, MinValue = 2)]
        public int AtrPeriod { get; set; }

        [Parameter("ATR Multiplier", Group = "Stop Loss",
            DefaultValue = 2.0, MinValue = 0.1)]
        public double AtrMultiplier { get; set; }

        [Parameter("Swing Lookback Bars", Group = "Stop Loss",
            DefaultValue = 10, MinValue = 3, MaxValue = 50)]
        public int SwingLookbackBars { get; set; }

        [Parameter("SL Swing Buffer Pips", Group = "Stop Loss",
            DefaultValue = 5.0, MinValue = 0.0)]
        public double SlSwingBufferPips { get; set; }

        [Parameter("SL Tenkan Buffer Pips", Group = "Stop Loss",
            DefaultValue = 3.0, MinValue = 0.0)]
        public double SlTenkanBufferPips { get; set; }

        // ══════════════════════════════════════════════════════════════════
        // GROUP F — Session (UTC) — BASE PARAMETERS (verbatim)
        // ══════════════════════════════════════════════════════════════════

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

        // ══════════════════════════════════════════════════════════════════
        // GROUP G — Session Time Zone — BASE PARAMETERS (verbatim)
        // ══════════════════════════════════════════════════════════════════

        [Parameter("Use Fixed UTC Times", Group = "Session Time Zone", DefaultValue = true)]
        public bool UseFixedUtcTimes { get; set; }

        [Parameter("Session Time Zone", Group = "Session Time Zone",
            DefaultValue = SessionTimeZoneEnum.UTC)]
        public SessionTimeZoneEnum SessionTimeZoneParam { get; set; }

        // ══════════════════════════════════════════════════════════════════
        // GROUP H — Trades Per Day — BASE PARAMETERS (verbatim)
        // ══════════════════════════════════════════════════════════════════

        [Parameter("Max Trades Per Day", Group = "Trades Per Day",
            DefaultValue = 1, MinValue = 1)]
        public int MaxTradesPerDay { get; set; }

        // ══════════════════════════════════════════════════════════════════
        // GROUP I — Trading Days — BASE PARAMETERS (verbatim)
        // ══════════════════════════════════════════════════════════════════

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

        // ══════════════════════════════════════════════════════════════════
        // GROUP J — Take Profit — BASE PARAMETERS (verbatim)
        // ══════════════════════════════════════════════════════════════════

        [Parameter("Take Profit R", Group = "Take Profit", DefaultValue = 2.0, MinValue = 0.1)]
        public double TakeProfitR { get; set; }

        // ══════════════════════════════════════════════════════════════════
        // GROUP K — Multi Take Profit — BASE PARAMETERS (verbatim)
        // ══════════════════════════════════════════════════════════════════

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

        // ══════════════════════════════════════════════════════════════════
        // GROUP L — Dynamic Stop — BASE PARAMETERS (verbatim)
        // ══════════════════════════════════════════════════════════════════

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

        // ══════════════════════════════════════════════════════════════════
        // GROUP M — Early Risk Reduction — BASE PARAMETERS (verbatim)
        // ══════════════════════════════════════════════════════════════════

        [Parameter("Enable Early Risk Reduction", Group = "Early Risk Reduction",
            DefaultValue = false)]
        public bool EnableEarlyRiskReduction { get; set; }

        [Parameter("Early Risk Reduction Trigger R", Group = "Early Risk Reduction",
            DefaultValue = 0.5, MinValue = 0.1)]
        public double EarlyRiskReductionTriggerR { get; set; }

        [Parameter("Early Risk Reduction Remaining Risk %", Group = "Early Risk Reduction",
            DefaultValue = 50.0, MinValue = 1.0, MaxValue = 100.0)]
        public double EarlyRiskReductionRemainingRiskPercent { get; set; }

        // ══════════════════════════════════════════════════════════════════
        // GROUP N — Risk — BASE PARAMETERS (verbatim)
        // ══════════════════════════════════════════════════════════════════

        [Parameter("Risk Amount", Group = "Risk", DefaultValue = 100, MinValue = 1)]
        public double RiskAmount { get; set; }

        [Parameter("Risk Currency", Group = "Risk",
            DefaultValue = RiskCurrency.AccountCurrency)]
        public RiskCurrency RiskCurrencyParam { get; set; }

        // ══════════════════════════════════════════════════════════════════
        // GROUP O — Execution Risk Cap — BASE PARAMETERS (verbatim)
        // ══════════════════════════════════════════════════════════════════

        [Parameter("Enable Execution Risk Cap", Group = "Execution Risk Cap",
            DefaultValue = true)]
        public bool EnableExecutionRiskCap { get; set; }

        [Parameter("Assumed Stop Slippage Pips", Group = "Execution Risk Cap",
            DefaultValue = 30.0, MinValue = 0.0)]
        public double AssumedStopSlippagePips { get; set; }

        [Parameter("Max Loss Per Trade (Account CCY)", Group = "Execution Risk Cap",
            DefaultValue = 200.0, MinValue = 0.0)]
        public double MaxLossPerTradeAccountCcy { get; set; }

        // ══════════════════════════════════════════════════════════════════
        // GROUP P — Safety — BASE PARAMETERS (verbatim)
        // ══════════════════════════════════════════════════════════════════

        [Parameter("Min Risk Pips", Group = "Safety", DefaultValue = 0.0, MinValue = 0.0)]
        public double MinRiskPips { get; set; }

        [Parameter("Max Volume In Units", Group = "Safety", DefaultValue = 0, MinValue = 0)]
        public double MaxVolumeInUnits { get; set; }

        [Parameter("Max Spread Pips", Group = "Safety", DefaultValue = 0, MinValue = 0)]
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

        // ══════════════════════════════════════════════════════════════════
        // GROUP Q — Diagnostics — BASE PARAMETERS (verbatim)
        // ══════════════════════════════════════════════════════════════════

        [Parameter("Bot Label Prefix", Group = "Diagnostics", DefaultValue = "ICHI")]
        public string BotLabelPrefix { get; set; }

        [Parameter("Enable Debug Logging", Group = "Diagnostics", DefaultValue = true)]
        public bool EnableDebugLogging { get; set; }

        [Parameter("Verbose Logging", Group = "Diagnostics", DefaultValue = false)]
        public bool VerboseLogging { get; set; }

        [Parameter("Explain Blocked Entries", Group = "Diagnostics", DefaultValue = true)]
        public bool ExplainBlockedEntries { get; set; }

        // ══════════════════════════════════════════════════════════════════
        // INTERNAL STATE — Base (verbatim from base parameters reference)
        // ══════════════════════════════════════════════════════════════════

        private TimeSpan _sessionStartTimeCfg;
        private TimeSpan _sessionEndTimeCfg;
        private TimeSpan _tradingStartTimeCfg;
        private TimeSpan _killSwitchTimeCfg;
        private TimeSpan _closePositionsTimeCfg;

        private TimeZoneInfo _sessionTz;

        private DateTime _sessionStartUtcToday;
        private DateTime _sessionEndUtcToday;
        private DateTime _tradingStartUtcToday;
        private DateTime _killSwitchUtcToday;
        private DateTime _closePositionsUtcToday;

        private DateTime _currentSessionDate;
        private bool     _noTradeToday;
        private int      _tradesToday;
        private bool     _killSwitchLoggedToday;
        private bool     _closePositionsLoggedToday;
        private bool     _sessionTimeLoggedToday;

        private Dictionary<long, PositionState>     _positionStates;
        private Dictionary<long, DateTime>          _lastCloseFailLogUtcByPosId;
        private Dictionary<long, CloseBackoffState> _closeBackoffByPosId;

        private double _tp1Pct, _tp2Pct, _tp3Pct, _tp4Pct;
        private double _maxTpR;

        // ── Strategy-specific state ──
        private IchimokuKinkoHyo       _ichimoku;
        private RelativeStrengthIndex  _rsi;
        private AverageTrueRange       _atr;
        private int                    _lastSignalBarIndex = -1;

        // ══════════════════════════════════════════════════════════════════
        // ON START
        // ══════════════════════════════════════════════════════════════════

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

            // 8. Strategy-specific initialisation
            _ichimoku = Indicators.IchimokuKinkoHyo(TenkanPeriod, KijunPeriod, SenkouSpanBPeriod);
            _rsi      = Indicators.RelativeStrengthIndex(Bars.ClosePrices, RsiPeriod);
            if (StopLossMethodParam == StopLossMethod.ATR)
                _atr = Indicators.AverageTrueRange(AtrPeriod, MovingAverageType.Exponential);

            _lastSignalBarIndex = -1;

            Log("Bot started. Symbol={0} TZ={1}", Symbol.Name,
                UseFixedUtcTimes ? "UTC(fixed)" : SessionTimeZoneParam.ToString());
            Log("VOLUME_DIAG symbol={0} min={1} step={2} max={3}",
                Symbol.Name, Symbol.VolumeInUnitsMin, Symbol.VolumeInUnitsStep, Symbol.VolumeInUnitsMax);

            // 9. Startup sanity warnings (base reference verbatim)
            if (EnableKillSwitch && _tradingStartUtcToday >= _killSwitchUtcToday)
                Print("WARNING: TradingStartTime >= KillSwitchTime. No entries possible today.");
            if (EnableClosePositionsTime && _closePositionsUtcToday <= _sessionEndUtcToday)
                Print("WARNING: ClosePositionsTime <= SessionEndTime. Entries will be blocked all day.");

            DateTime earliestEntry = _sessionEndUtcToday > _tradingStartUtcToday
                ? _sessionEndUtcToday : _tradingStartUtcToday;

            if (EnableKillSwitch && _killSwitchUtcToday <= earliestEntry)
                Print("WARNING: KillSwitchTime ({0:HH:mm}) <= earliest possible entry ({1:HH:mm}). Zero trades will occur.",
                    _killSwitchUtcToday, earliestEntry);
            if (EnableClosePositionsTime && _closePositionsUtcToday <= earliestEntry)
                Print("WARNING: ClosePositionsTime ({0:HH:mm}) <= earliest possible entry ({1:HH:mm}). Zero trades will occur.",
                    _closePositionsUtcToday, earliestEntry);
            if (_tradingStartUtcToday < _sessionEndUtcToday)
                Print("INFO: TradingStartTime ({0:HH:mm}) is before SessionEnd ({1:HH:mm}). Bot will wait for session to end before entering.",
                    _tradingStartUtcToday, _sessionEndUtcToday);

            // 10. Ichimoku-specific startup validation (Section 13 of spec)
            Log("ICHIMOKU BOT: Symbol={0} InstrumentType={1} Direction={2}",
                SymbolName, InstrumentTypeParam, TradeDirectionParam);
            Log("FILTERS: Chikou={0} CloudTwist={1} (lookAhead={2}) MinCloudThickness={3} ({4} pips)",
                EnableChikouConfirmation, EnableCloudTwistFilter, CloudTwistLookAheadBars,
                EnableMinCloudThickness, MinCloudThicknessPips);
            Log("STOP LOSS METHOD: {0}", StopLossMethodParam);

            if (!EnableChikouConfirmation)
                Print("WARNING: Chikou Span confirmation is DISABLED. Signal quality will be lower.");
            if (TradeDirectionParam != TradeDirectionMode.Both)
                Log("WARNING: Trade direction restricted to {0} only.", TradeDirectionParam);
            if ((InstrumentTypeParam == InstrumentType.Stocks || InstrumentTypeParam == InstrumentType.Indices)
                && (TradeSaturday || TradeSunday))
                Print("WARNING: Saturday/Sunday trading is enabled for {0}. Stocks/Indices markets are closed on weekends.",
                    InstrumentTypeParam);
        }

        // ══════════════════════════════════════════════════════════════════
        // ON STOP
        // ══════════════════════════════════════════════════════════════════

        protected override void OnStop()
        {
            Positions.Closed -= OnPositionsClosed;
            Log("Bot stopped.");
        }

        // ══════════════════════════════════════════════════════════════════
        // ON BAR — signal evaluation only (spec Section 9.1)
        // ══════════════════════════════════════════════════════════════════

        protected override void OnBar()
        {
            // One position at a time — checked first (spec Section 9.1)
            if (HasOpenBotPosition()) return;

            var nowUtc = Server.Time;

            // Pre-signal gate checks (spec Section 5.2 / 10)
            if (_noTradeToday)                                              { ExplainBlock("NoTradeToday");       return; }
            if (nowUtc < _tradingStartUtcToday)                            { ExplainBlock("BeforeTradingStart"); return; }
            if (EnableClosePositionsTime && nowUtc >= _closePositionsUtcToday) { ExplainBlock("AfterCloseTime");    return; }
            if (EnableKillSwitch && nowUtc >= _killSwitchUtcToday)         { ExplainBlock("KillSwitch");         return; }
            if (_tradesToday >= MaxTradesPerDay)                           { ExplainBlock("MaxTradesReached");   return; }

            double spreadPips = Symbol.Spread / Symbol.PipSize;
            if (MaxSpreadPips > 0 && spreadPips > MaxSpreadPips)          { ExplainBlock("SpreadTooWide");      return; }

            // Gap warning for Stocks/Indices (spec Section 8)
            if ((InstrumentTypeParam == InstrumentType.Stocks || InstrumentTypeParam == InstrumentType.Indices)
                && _atr != null && Bars.Count > 2)
            {
                double atrVal    = _atr.Result[1];
                double gapSize   = Math.Abs(Bars.OpenPrices[1] - Bars.ClosePrices[2]);
                if (atrVal > 0 && gapSize > 2.0 * atrVal)
                    Log("GAP WARNING: Bar open gapped {0:F1} pips (> 2×ATR {1:F1} pips). Proceeding with signal evaluation.",
                        gapSize / Symbol.PipSize, atrVal / Symbol.PipSize);
            }

            // Evaluate signals
            if (EvaluateLongSignal())       EnterTrade(TradeType.Buy);
            else if (EvaluateShortSignal()) EnterTrade(TradeType.Sell);
        }

        // ══════════════════════════════════════════════════════════════════
        // ON TICK — position management only (spec Section 9.2)
        // ══════════════════════════════════════════════════════════════════

        protected override void OnTick()
        {
            var nowUtc = Server.Time;

            // Daily reset check
            DateTime sessionDate = GetSessionDate(nowUtc);
            if (sessionDate != _currentSessionDate)
                ResetForDate(sessionDate);

            // Force-close at Close Positions Time
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

            // Kill switch one-time log
            if (EnableKillSwitch && nowUtc >= _killSwitchUtcToday && !_killSwitchLoggedToday)
            {
                Log("KILL SWITCH TIME reached ({0:HH:mm}). No new entries.", _killSwitchUtcToday);
                _killSwitchLoggedToday = true;
            }

            // Position management (Multi TP, Dynamic Stop, Early Risk Reduction)
            ManageOpenPositions();
        }

        // ══════════════════════════════════════════════════════════════════
        // 7.1 SESSION TIMEZONE
        // ══════════════════════════════════════════════════════════════════

        private TimeZoneInfo ResolveTimeZone()
        {
            if (UseFixedUtcTimes)
                return TimeZoneInfo.Utc;

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
                catch { }
            }

            Print("WARNING: Could not resolve timezone for {0}. Falling back to UTC.", SessionTimeZoneParam);
            return TimeZoneInfo.Utc;
        }

        private DateTime GetSessionDate(DateTime utcNow)
        {
            if (UseFixedUtcTimes) return utcNow.Date;
            return TimeZoneInfo.ConvertTimeFromUtc(utcNow, _sessionTz).Date;
        }

        // ══════════════════════════════════════════════════════════════════
        // 7.2 SESSION TIME COMPUTATION
        // ══════════════════════════════════════════════════════════════════

        private DateTime ConvertConfiguredTimeToUtc(DateTime sessionDate, TimeSpan configuredTime)
        {
            if (UseFixedUtcTimes)
                return sessionDate + configuredTime;

            DateTime localDt = sessionDate + configuredTime;
            try
            {
                if (_sessionTz.IsInvalidTime(localDt))
                    localDt = localDt.AddHours(1);
                if (_sessionTz.IsAmbiguousTime(localDt))
                    Print("WARNING: Ambiguous time {0} in {1} (DST fall-back). Using standard-time offset.", localDt, SessionTimeZoneParam);
                return TimeZoneInfo.ConvertTimeToUtc(localDt, _sessionTz);
            }
            catch
            {
                return sessionDate + configuredTime;
            }
        }

        private void ComputeSessionTimesForDay(DateTime sessionDate)
        {
            _sessionStartUtcToday   = ConvertConfiguredTimeToUtc(sessionDate, _sessionStartTimeCfg);
            _sessionEndUtcToday     = ConvertConfiguredTimeToUtc(sessionDate, _sessionEndTimeCfg);
            _tradingStartUtcToday   = ConvertConfiguredTimeToUtc(sessionDate, _tradingStartTimeCfg);
            _killSwitchUtcToday     = ConvertConfiguredTimeToUtc(sessionDate, _killSwitchTimeCfg);
            _closePositionsUtcToday = ConvertConfiguredTimeToUtc(sessionDate, _closePositionsTimeCfg);

            if (_sessionEndUtcToday <= _sessionStartUtcToday)
                _sessionEndUtcToday = _sessionEndUtcToday.AddDays(1);

            if (_killSwitchUtcToday     < _sessionStartUtcToday) _killSwitchUtcToday     = _killSwitchUtcToday.AddDays(1);
            if (_closePositionsUtcToday < _sessionStartUtcToday) _closePositionsUtcToday = _closePositionsUtcToday.AddDays(1);
        }

        // ══════════════════════════════════════════════════════════════════
        // 7.3 DAILY RESET
        // ══════════════════════════════════════════════════════════════════

        private void ResetForDate(DateTime sessionDate)
        {
            _currentSessionDate        = sessionDate;
            _noTradeToday              = false;
            _tradesToday               = 0;
            _killSwitchLoggedToday     = false;
            _closePositionsLoggedToday = false;
            _sessionTimeLoggedToday    = false;

            ComputeSessionTimesForDay(sessionDate);

            if (!IsTradingDayEnabled(sessionDate.DayOfWeek))
            {
                _noTradeToday = true;
                Log("NO TRADE TODAY: Trading disabled for {0}.", sessionDate.DayOfWeek);
            }

            Log("=== New day reset: {0:yyyy-MM-dd} ===", sessionDate);
            LogSessionTimezone();
            RehydrateTradesTodayFromHistory("RESET");
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

        // ══════════════════════════════════════════════════════════════════
        // 7.4 TRADING DAY CHECK
        // ══════════════════════════════════════════════════════════════════

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

        // ══════════════════════════════════════════════════════════════════
        // 7.5 RISK CURRENCY CONVERSION
        // ══════════════════════════════════════════════════════════════════

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

        // ══════════════════════════════════════════════════════════════════
        // 7.6 VOLUME SIZING & EXECUTION RISK CAP
        // ══════════════════════════════════════════════════════════════════

        private double ComputeVolume(TradeType tradeType, double estimatedRiskPips, double effectiveTpR)
        {
            double riskInAccountCcy = GetRiskInAccountCurrency();
            if (riskInAccountCcy <= 0)
            {
                Log("ERROR: Risk amount in account currency <= 0. Cannot trade.");
                return -1;
            }

            if (MinRiskPips > 0 && estimatedRiskPips < MinRiskPips)
            {
                Log("SAFETY: Risk {0:F1} pips < MinRiskPips {1}. Skipping.", estimatedRiskPips, MinRiskPips);
                return -1;
            }

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

            if (EnableMarginSafety && MaxMarginUsagePercent > 0)
            {
                double freeMargin = System.Convert.ToDouble(Account.FreeMargin);
                if (freeMargin <= 0)
                {
                    Log("SAFETY: Free margin <= 0. Skipping trade.");
                    return -1;
                }

                double allowedMargin   = freeMargin * (MaxMarginUsagePercent / 100.0);
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

        // ══════════════════════════════════════════════════════════════════
        // 7.10 RESTART SAFETY — TRADE COUNT REHYDRATION
        // ══════════════════════════════════════════════════════════════════

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

        // ══════════════════════════════════════════════════════════════════
        // 7.11 DIAGNOSTICS / LOGGING
        // ══════════════════════════════════════════════════════════════════

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

        private void ExplainBlock(string reason)
        {
            if (ExplainBlockedEntries)
                Log("BLOCKED: {0}", reason);
        }

        // ══════════════════════════════════════════════════════════════════
        // 7.12 VOLUME NORMALISATION HELPERS
        // ══════════════════════════════════════════════════════════════════

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

        private double NormalizeVolumeDownRequested(double volume)
        {
            double step = Symbol.VolumeInUnitsStep;
            if (step <= 0) return Symbol.NormalizeVolumeInUnits(volume, RoundingMode.Down);
            double eps   = Math.Max(1e-12, step * 1e-9);
            double steps = Math.Floor((volume + eps) / step);
            int    dec   = GetStepDecimals(step);
            return Math.Max(0, Math.Round(steps * step, dec, MidpointRounding.AwayFromZero));
        }

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

        // ══════════════════════════════════════════════════════════════════
        // 7.13 POSITION IDENTIFICATION HELPERS
        // ══════════════════════════════════════════════════════════════════

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
                PositionId            = pos.Id,
                EntryPrice            = pos.EntryPrice,
                SLPriceInitial        = pos.StopLoss.Value,
                InitialRiskPipsActual = riskPips,
                InitialVolumeInUnits  = pos.VolumeInUnits,
                EarlyRiskReductionDone = false,
                BreakEvenDone          = false,
                TP1Done = false, TP2Done = false, TP3Done = false, TP4Done = false,
                LastTrailSteps        = -1
            };
            Log("Registered existing position {0} riskPips={1:F1}", pos.Label, riskPips);
        }

        // ── Multi TP helpers ──

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

        // ══════════════════════════════════════════════════════════════════
        // SIGNAL EVALUATION — LONG (spec Section 5.3)
        // ══════════════════════════════════════════════════════════════════

        private bool EvaluateLongSignal()
        {
            // Duplicate signal guard (spec Section 11.7)
            if (Bars.Count - 1 == _lastSignalBarIndex) return false;

            // CONDITION 1 — Direction gate
            if (TradeDirectionParam == TradeDirectionMode.ShortOnly)
            {
                ExplainBlock("Long blocked: direction=ShortOnly");
                return false;
            }

            // Read confirmed bar[1] Ichimoku values (spec Section 11.3)
            // Senkou Spans at index [CloudDisplacement + 1] for bar[1]
            int spanIdx = CloudDisplacement + 1;
            double spanA = _ichimoku.SenkouSpanA[spanIdx];
            double spanB = _ichimoku.SenkouSpanB[spanIdx];

            if (double.IsNaN(spanA) || double.IsNaN(spanB))
            {
                ExplainBlock("Long blocked: Ichimoku not warmed up");
                return false;
            }

            double cloudTop    = Math.Max(spanA, spanB);
            double cloudBottom = Math.Min(spanA, spanB);
            double closePrice  = Bars.ClosePrices[1];

            // CONDITION 2 — Price above both Span A and Span B
            if (closePrice <= spanA || closePrice <= spanB)
            {
                ExplainBlock(string.Format("Long blocked: close {0:F5} not above cloud (SpanA={1:F5} SpanB={2:F5})", closePrice, spanA, spanB));
                return false;
            }

            // CONDITION 3 — Price NOT inside cloud (explicit enforcement)
            if (closePrice >= cloudBottom && closePrice <= cloudTop)
            {
                ExplainBlock("Long blocked: price inside cloud (no-trade zone)");
                return false;
            }

            // CONDITION 4 — Tenkan-sen above Kijun-sen
            double tenkan = _ichimoku.TenkanSen[1];
            double kijun  = _ichimoku.KijunSen[1];
            if (double.IsNaN(tenkan) || double.IsNaN(kijun))
            {
                ExplainBlock("Long blocked: Tenkan/Kijun not ready");
                return false;
            }
            if (tenkan <= kijun)
            {
                ExplainBlock(string.Format("Long blocked: Tenkan ({0:F5}) not above Kijun ({1:F5})", tenkan, kijun));
                return false;
            }

            // CONDITION 5 — Chikou Span confirmation (if enabled)
            if (EnableChikouConfirmation)
            {
                double chikouClose     = closePrice;                              // current close IS Chikou value
                double historicalClose = Bars.ClosePrices[1 + CloudDisplacement]; // price CloudDisplacement bars before bar[1]
                if (chikouClose <= historicalClose)
                {
                    ExplainBlock(string.Format("Long blocked: Chikou ({0:F5}) not above historical close ({1:F5})", chikouClose, historicalClose));
                    return false;
                }
            }

            // CONDITION 6 — RSI above level
            double rsiVal = _rsi.Result[1];
            if (double.IsNaN(rsiVal) || rsiVal <= RsiLevel)
            {
                ExplainBlock(string.Format("Long blocked: RSI ({0:F2}) not above RsiLevel ({1:F2})", rsiVal, RsiLevel));
                return false;
            }

            // CONDITION 7 — No imminent cloud twist (if enabled)
            if (IsCloudTwistImminent())
            {
                ExplainBlock("Long blocked: imminent cloud twist detected");
                return false;
            }

            // CONDITION 8 — Minimum cloud thickness (if enabled)
            if (!IsCloudThickEnough(spanA, spanB))
            {
                ExplainBlock(string.Format("Long blocked: cloud too thin ({0:F1} pips < {1:F1} pips)",
                    Math.Abs(spanA - spanB) / Symbol.PipSize, MinCloudThicknessPips));
                return false;
            }

            return true;
        }

        // ══════════════════════════════════════════════════════════════════
        // SIGNAL EVALUATION — SHORT (spec Section 5.4)
        // ══════════════════════════════════════════════════════════════════

        private bool EvaluateShortSignal()
        {
            // Duplicate signal guard (spec Section 11.7)
            if (Bars.Count - 1 == _lastSignalBarIndex) return false;

            // CONDITION 1 — Direction gate
            if (TradeDirectionParam == TradeDirectionMode.LongOnly)
            {
                ExplainBlock("Short blocked: direction=LongOnly");
                return false;
            }

            // Read confirmed bar[1] Ichimoku values
            int spanIdx = CloudDisplacement + 1;
            double spanA = _ichimoku.SenkouSpanA[spanIdx];
            double spanB = _ichimoku.SenkouSpanB[spanIdx];

            if (double.IsNaN(spanA) || double.IsNaN(spanB))
            {
                ExplainBlock("Short blocked: Ichimoku not warmed up");
                return false;
            }

            double cloudTop    = Math.Max(spanA, spanB);
            double cloudBottom = Math.Min(spanA, spanB);
            double closePrice  = Bars.ClosePrices[1];

            // CONDITION 2 — Price below both Span A and Span B
            if (closePrice >= spanA || closePrice >= spanB)
            {
                ExplainBlock(string.Format("Short blocked: close {0:F5} not below cloud (SpanA={1:F5} SpanB={2:F5})", closePrice, spanA, spanB));
                return false;
            }

            // CONDITION 3 — Price NOT inside cloud (explicit enforcement)
            if (closePrice >= cloudBottom && closePrice <= cloudTop)
            {
                ExplainBlock("Short blocked: price inside cloud (no-trade zone)");
                return false;
            }

            // CONDITION 4 — Tenkan-sen below Kijun-sen
            double tenkan = _ichimoku.TenkanSen[1];
            double kijun  = _ichimoku.KijunSen[1];
            if (double.IsNaN(tenkan) || double.IsNaN(kijun))
            {
                ExplainBlock("Short blocked: Tenkan/Kijun not ready");
                return false;
            }
            if (tenkan >= kijun)
            {
                ExplainBlock(string.Format("Short blocked: Tenkan ({0:F5}) not below Kijun ({1:F5})", tenkan, kijun));
                return false;
            }

            // CONDITION 5 — Chikou Span confirmation (if enabled)
            if (EnableChikouConfirmation)
            {
                double chikouClose     = closePrice;
                double historicalClose = Bars.ClosePrices[1 + CloudDisplacement];
                if (chikouClose >= historicalClose)
                {
                    ExplainBlock(string.Format("Short blocked: Chikou ({0:F5}) not below historical close ({1:F5})", chikouClose, historicalClose));
                    return false;
                }
            }

            // CONDITION 6 — RSI below level
            double rsiVal = _rsi.Result[1];
            if (double.IsNaN(rsiVal) || rsiVal >= RsiLevel)
            {
                ExplainBlock(string.Format("Short blocked: RSI ({0:F2}) not below RsiLevel ({1:F2})", rsiVal, RsiLevel));
                return false;
            }

            // CONDITION 7 — No imminent cloud twist (if enabled)
            if (IsCloudTwistImminent())
            {
                ExplainBlock("Short blocked: imminent cloud twist detected");
                return false;
            }

            // CONDITION 8 — Minimum cloud thickness (if enabled)
            if (!IsCloudThickEnough(spanA, spanB))
            {
                ExplainBlock(string.Format("Short blocked: cloud too thin ({0:F1} pips < {1:F1} pips)",
                    Math.Abs(spanA - spanB) / Symbol.PipSize, MinCloudThicknessPips));
                return false;
            }

            return true;
        }

        // ══════════════════════════════════════════════════════════════════
        // CLOUD TWIST DETECTION (spec Section 11.4)
        // ══════════════════════════════════════════════════════════════════

        private bool IsCloudTwistImminent()
        {
            if (!EnableCloudTwistFilter) return false;

            // Future cloud: index 0 = CloudDisplacement bars ahead of current price.
            // A twist = sign of (SpanA - SpanB) changes across the look-ahead window.
            double sign0 = Math.Sign(_ichimoku.SenkouSpanA[0] - _ichimoku.SenkouSpanB[0]);
            for (int i = 1; i < CloudTwistLookAheadBars; i++)
            {
                double signI = Math.Sign(_ichimoku.SenkouSpanA[i] - _ichimoku.SenkouSpanB[i]);
                if (signI != sign0 && signI != 0 && sign0 != 0)
                    return true;
            }
            return false;
        }

        // ══════════════════════════════════════════════════════════════════
        // CLOUD THICKNESS CHECK (spec Section 11.5)
        // ══════════════════════════════════════════════════════════════════

        private bool IsCloudThickEnough(double spanA, double spanB)
        {
            if (!EnableMinCloudThickness) return true;
            double thicknessPips = Math.Abs(spanA - spanB) / Symbol.PipSize;
            return thicknessPips >= MinCloudThicknessPips;
        }

        // ══════════════════════════════════════════════════════════════════
        // STOP LOSS CALCULATION — all 5 methods (spec Section 6)
        // ══════════════════════════════════════════════════════════════════

        private double CalculateStopLoss(TradeType tradeType, double entryEstimate)
        {
            int spanIdx     = CloudDisplacement + 1;
            double spanA    = _ichimoku.SenkouSpanA[spanIdx];
            double spanB    = _ichimoku.SenkouSpanB[spanIdx];
            double cloudTop    = Math.Max(spanA, spanB);
            double cloudBottom = Math.Min(spanA, spanB);

            double slPrice = double.NaN;

            switch (StopLossMethodParam)
            {
                // ── Method 1: Cloud Boundary (default) ──
                case StopLossMethod.CloudBoundary:
                    if (tradeType == TradeType.Buy)
                        slPrice = cloudBottom - SlCloudBufferPips * Symbol.PipSize;
                    else
                        slPrice = cloudTop + SlCloudBufferPips * Symbol.PipSize;
                    break;

                // ── Method 2: Kijun-sen ──
                case StopLossMethod.KijunSen:
                    double kijun = _ichimoku.KijunSen[1];
                    if (tradeType == TradeType.Buy)
                        slPrice = kijun - SlKijunBufferPips * Symbol.PipSize;
                    else
                        slPrice = kijun + SlKijunBufferPips * Symbol.PipSize;
                    break;

                // ── Method 3: ATR ──
                case StopLossMethod.ATR:
                    if (_atr == null)
                    {
                        Log("ERROR: ATR indicator not initialised. Falling back to CloudBoundary SL.");
                        slPrice = tradeType == TradeType.Buy
                            ? cloudBottom - SlCloudBufferPips * Symbol.PipSize
                            : cloudTop    + SlCloudBufferPips * Symbol.PipSize;
                        break;
                    }
                    double atrVal = _atr.Result[1];
                    if (tradeType == TradeType.Buy)
                        slPrice = entryEstimate - AtrMultiplier * atrVal;
                    else
                        slPrice = entryEstimate + AtrMultiplier * atrVal;

                    // ATR validation: SL must clear the cloud boundary (spec Section 6, Method 3)
                    if (tradeType == TradeType.Buy && slPrice > cloudBottom)
                    {
                        Log("ATR SL ({0:F5}) > cloudBottom ({1:F5}). Using cloudBottom instead.", slPrice, cloudBottom);
                        slPrice = cloudBottom - SlCloudBufferPips * Symbol.PipSize;
                    }
                    else if (tradeType == TradeType.Sell && slPrice < cloudTop)
                    {
                        Log("ATR SL ({0:F5}) < cloudTop ({1:F5}). Using cloudTop instead.", slPrice, cloudTop);
                        slPrice = cloudTop + SlCloudBufferPips * Symbol.PipSize;
                    }
                    break;

                // ── Method 4: Swing High/Low ──
                case StopLossMethod.SwingHighLow:
                    if (tradeType == TradeType.Buy)
                    {
                        double swingLow = Bars.LowPrices[1];
                        for (int i = 1; i <= SwingLookbackBars && i < Bars.Count; i++)
                            if (Bars.LowPrices[i] < swingLow) swingLow = Bars.LowPrices[i];
                        slPrice = swingLow - SlSwingBufferPips * Symbol.PipSize;
                    }
                    else
                    {
                        double swingHigh = Bars.HighPrices[1];
                        for (int i = 1; i <= SwingLookbackBars && i < Bars.Count; i++)
                            if (Bars.HighPrices[i] > swingHigh) swingHigh = Bars.HighPrices[i];
                        slPrice = swingHigh + SlSwingBufferPips * Symbol.PipSize;
                    }
                    break;

                // ── Method 5: Tenkan-sen (tightest) ──
                case StopLossMethod.TenkanSen:
                    double tenkan = _ichimoku.TenkanSen[1];
                    if (tradeType == TradeType.Buy)
                        slPrice = tenkan - SlTenkanBufferPips * Symbol.PipSize;
                    else
                        slPrice = tenkan + SlTenkanBufferPips * Symbol.PipSize;
                    break;
            }

            // Round to nearest tick
            if (!double.IsNaN(slPrice) && Symbol.TickSize > 0)
                slPrice = Math.Round(slPrice / Symbol.TickSize) * Symbol.TickSize;

            return slPrice;
        }

        // ══════════════════════════════════════════════════════════════════
        // ENTER TRADE — spec Section 9.3 (10-step sequence)
        // ══════════════════════════════════════════════════════════════════

        private void EnterTrade(TradeType tradeType)
        {
            // STEP 1 — Snapshot bar[1] values for logging
            int    spanIdx      = CloudDisplacement + 1;
            double spanA        = _ichimoku.SenkouSpanA[spanIdx];
            double spanB        = _ichimoku.SenkouSpanB[spanIdx];
            double tenkan       = _ichimoku.TenkanSen[1];
            double kijun        = _ichimoku.KijunSen[1];
            double rsiVal       = _rsi.Result[1];
            double cloudThkPips = Math.Abs(spanA - spanB) / Symbol.PipSize;
            double entryEstimate = tradeType == TradeType.Buy ? Symbol.Ask : Symbol.Bid;

            // STEP 2 — Calculate SL price
            double slPrice = CalculateStopLoss(tradeType, entryEstimate);
            if (double.IsNaN(slPrice))
            {
                Log("ERROR: SL calculation returned NaN for {0}. Skipping.", tradeType);
                return;
            }

            // STEP 3 — Validate SL distance
            double slDistance = Math.Abs(entryEstimate - slPrice) / Symbol.PipSize;
            if (slDistance <= 0)
            {
                Log("ERROR: SL distance <= 0 ({0:F5}). Skipping {1} entry.", slDistance, tradeType);
                return;
            }
            if (MinRiskPips > 0 && slDistance < MinRiskPips)
            {
                Log("GATE 9: SL distance {0:F1} pips < MinRiskPips {1}. Skipping.", slDistance, MinRiskPips);
                return;
            }

            // STEP 4 — Calculate TP price
            double effectiveTpR = EnableMultiTp ? _maxTpR : TakeProfitR;
            double tpDistance   = slDistance * effectiveTpR;
            double tpPrice      = tradeType == TradeType.Buy
                ? entryEstimate + tpDistance * Symbol.PipSize
                : entryEstimate - tpDistance * Symbol.PipSize;
            if (Symbol.TickSize > 0)
                tpPrice = Math.Round(tpPrice / Symbol.TickSize) * Symbol.TickSize;

            // STEP 5 — Compute volume (GATE 10)
            double volumeInUnits = ComputeVolume(tradeType, slDistance, effectiveTpR);
            if (volumeInUnits < 0)
                return; // already logged inside ComputeVolume

            // STEP 6 — Execute market order
            string label  = GetBotLabelForDate(_currentSessionDate);
            var    result = ExecuteMarketOrder(tradeType, SymbolName, volumeInUnits, label, null, null);
            if (!result.IsSuccessful)
            {
                Log("ERROR: ExecuteMarketOrder failed: {0}. Skipping.", result.Error);
                return;
            }

            var position = result.Position;
            if (position == null)
            {
                Log("ERROR: Order filled but position is null. Cannot apply SL/TP.");
                return;
            }

            // STEP 7 — Apply SL and TP with protection fallback pattern
            double slPriceApplied = slPrice;
            double tpPriceApplied = tpPrice;

            var modResult = ModifyPosition(position, slPrice, tpPrice, ProtectionType.Absolute, false, StopTriggerMethod.Trade);
            if (!modResult.IsSuccessful)
            {
                Log("WARNING: ModifyPosition SL/TP failed ({0}). Attempting fallback.", modResult.Error);
                modResult = ModifyPosition(position, slPrice, null, ProtectionType.Absolute, false, StopTriggerMethod.Trade);
            }

            // Verify SL was applied
            if (!position.StopLoss.HasValue)
            {
                if (EnableProtectionFallback && FallbackStopLossPips > 0)
                {
                    double fallbackSl = tradeType == TradeType.Buy
                        ? position.EntryPrice - FallbackStopLossPips * Symbol.PipSize
                        : position.EntryPrice + FallbackStopLossPips * Symbol.PipSize;
                    if (Symbol.TickSize > 0)
                        fallbackSl = Math.Round(fallbackSl / Symbol.TickSize) * Symbol.TickSize;
                    ModifyPosition(position, fallbackSl, null, ProtectionType.Absolute, false, StopTriggerMethod.Trade);
                    Log("PROTECTION FALLBACK: Applied fallback SL at {0:F5} ({1:F1} pips).", fallbackSl, FallbackStopLossPips);
                    slPriceApplied = fallbackSl;
                }

                if (!position.StopLoss.HasValue)
                {
                    Log("CRITICAL: Could not apply any SL to position {0}. Closing immediately.", position.Id);
                    TryClosePositionSafely(position, "NO SL EMERGENCY");
                    return;
                }
            }

            slPriceApplied = position.StopLoss.Value;
            if (position.TakeProfit.HasValue)
                tpPriceApplied = position.TakeProfit.Value;

            double riskPipsApplied = Math.Abs(position.EntryPrice - slPriceApplied) / Symbol.PipSize;

            // STEP 8 — Increment trade counter
            _tradesToday++;

            // STEP 9 — Create and store PositionState
            _positionStates[position.Id] = new PositionState
            {
                PositionId            = position.Id,
                EntryPrice            = position.EntryPrice,
                SLPriceInitial        = slPriceApplied,
                InitialRiskPipsActual = riskPipsApplied > 0 ? riskPipsApplied : slDistance,
                InitialVolumeInUnits  = position.VolumeInUnits,
                EarlyRiskReductionDone = false,
                BreakEvenDone          = false,
                TP1Done = false, TP2Done = false, TP3Done = false, TP4Done = false,
                LastTrailSteps        = -1
            };

            // Mark this bar so we don't fire again on the same bar (spec Section 11.7)
            _lastSignalBarIndex = Bars.Count - 1;

            // STEP 10 — Log entry diagnostic
            double spreadPips      = Symbol.Spread / Symbol.PipSize;
            double kijunDistPips   = Math.Abs(position.EntryPrice - kijun) / Symbol.PipSize;

            Log("ENTRY: {0} symbol={1} entry={2:F5} sl={3:F5} tp={4:F5} vol={5} slPips={6:F1} R={7:F2} spread={8:F4} method={9}",
                tradeType, SymbolName,
                position.EntryPrice, slPriceApplied, tpPriceApplied,
                position.VolumeInUnits, riskPipsApplied, effectiveTpR,
                spreadPips, StopLossMethodParam);

            if (VerboseLogging)
            {
                Print("[{0}] ENTRY_DIAG symbol={1} side={2} volume={3} entry={4} sl={5} tp={6} riskPips={7:F2} spread={8:F4} balance={9:F2} equity={10:F2} margin={11:F2} freeMargin={12:F2} marginLevel={13} cloudSpanA={14:F5} cloudSpanB={15:F5} cloudThickPips={16:F1} kijunDistPips={17:F1} rsi={18:F2} tenkan={19:F5} kijun={20:F5}",
                    BotLabelPrefix, SymbolName, tradeType,
                    position.VolumeInUnits, position.EntryPrice,
                    slPriceApplied, tpPriceApplied, riskPipsApplied,
                    Symbol.Ask - Symbol.Bid,
                    Account.Balance, Account.Equity, Account.Margin, Account.FreeMargin,
                    (!Account.MarginLevel.HasValue || double.IsNaN(Account.MarginLevel.Value))
                        ? "N/A" : Account.MarginLevel.Value.ToString("F2"),
                    spanA, spanB, cloudThkPips, kijunDistPips, rsiVal, tenkan, kijun);
            }
        }

        // ══════════════════════════════════════════════════════════════════
        // 7.7 POSITION MANAGEMENT — ManageOpenPositions
        // ══════════════════════════════════════════════════════════════════

        private void ManageOpenPositions()
        {
            foreach (var pos in Positions)
            {
                if (!IsBotPosition(pos) || IsIgnorableDustPosition(pos)) continue;

                PositionState state;
                if (!_positionStates.TryGetValue(pos.Id, out state)) continue;

                double profitPips = pos.Pips;
                double profitR    = state.InitialRiskPipsActual > 0
                    ? profitPips / state.InitialRiskPipsActual
                    : 0;

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
            Log("EARLY RISK REDUCTION: SL -> {0:F5} (remaining {1:F1}% at {2:F2}R)", desiredSL, EarlyRiskReductionRemainingRiskPercent, profitR);
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
                    Log("BREAK EVEN: SL -> {0:F5} (entry + {1} pips)", desiredSL, BreakEvenExtraPips);
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
                        Log("TRAIL: SL -> {0:F5} (locked {1:F2}R steps={2} profitR={3:F2})", desiredSL, lockedR, steps, profitR);
                    }
                    state.LastTrailSteps = steps;
                }
            }
        }

        // ══════════════════════════════════════════════════════════════════
        // 7.8 SAFE POSITION CLOSE
        // ══════════════════════════════════════════════════════════════════

        private bool TryClosePositionSafely(Position pos, string context)
        {
            DateTime nowUtc = Server.Time;

            CloseBackoffState st;
            if (_closeBackoffByPosId != null && _closeBackoffByPosId.TryGetValue(pos.Id, out st))
                if (nowUtc < st.NextAttemptUtc) return false;

            double minVol = Symbol.VolumeInUnitsMin;
            double step   = GetVolumeStepSafe();
            double posVol = pos.VolumeInUnits;
            double tol    = Math.Max(1e-12, step * 1e-6);

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
            int fc    = st.FailCount;
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

        // ══════════════════════════════════════════════════════════════════
        // 7.9 POSITION CLOSED HANDLER
        // ══════════════════════════════════════════════════════════════════

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
    }
}



