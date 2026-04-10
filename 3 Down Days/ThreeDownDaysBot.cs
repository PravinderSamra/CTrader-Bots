using System;
using System.Collections.Generic;
using System.Linq;
using cAlgo.API;
using cAlgo.API.Indicators;
using cAlgo.API.Internals;

namespace cAlgo.Robots
{
    public enum EntryMode { DailyBarOpen, LateSession }
    public enum SessionTimezone { NewYork, London, Frankfurt }
    public enum StopLossMode { FixedPips, CandleExtreme, CandlePercent, AtrBased, LowestLowNDays, SwingLow }
    public enum ExitMode { FirstUpCandle, SingleTP, DynamicOnly }
    public enum DynamicStopMode { StepLockR, TrailBehindPriceR }
    public enum RiskCurrency { AccountCurrency, USD, GBP }

    public class PositionState
    {
        public long PositionId { get; set; }
        public double EntryPrice { get; set; }
        public double InitialRiskPipsActual { get; set; }
        public double InitialVolumeInUnits { get; set; }
        public DateTime EntryTimeUtc { get; set; }
        public int EntryBarIndex { get; set; }
        public DateTime EntryDate { get; set; }
        public bool BreakEvenDone { get; set; }
        public double LastTrailSteps { get; set; }
    }

    [Robot(TimeZone = TimeZones.UTC, AccessRights = AccessRights.None)]
    public class ThreeDownDaysBot : Robot
    {
        // ── Entry Settings ──────────────────────────────────────────────
        [Parameter("Entry Mode", Group = "Entry Settings", DefaultValue = EntryMode.DailyBarOpen)]
        public EntryMode EntryMode { get; set; }

        [Parameter("Late Entry Time (HH:mm:ss)", Group = "Entry Settings", DefaultValue = "15:50:00")]
        public string LateEntryTime { get; set; }

        [Parameter("Late Entry Window (minutes)", Group = "Entry Settings", DefaultValue = 10, MinValue = 1, MaxValue = 30)]
        public int LateEntryWindowMinutes { get; set; }

        [Parameter("Number Of Down Days", Group = "Entry Settings", DefaultValue = 3, MinValue = 2, MaxValue = 10)]
        public int NumberOfDownDays { get; set; }

        [Parameter("Require Price Below SMA5", Group = "Entry Settings", DefaultValue = true)]
        public bool RequirePriceBelowSMA5 { get; set; }

        // ── Trend Filter ────────────────────────────────────────────────
        [Parameter("Require Trend Filter", Group = "Trend Filter", DefaultValue = true)]
        public bool RequireTrendFilter { get; set; }

        [Parameter("Trend SMA Period", Group = "Trend Filter", DefaultValue = 200, MinValue = 20, MaxValue = 500)]
        public int TrendSmaPeriod { get; set; }

        // ── Session & Timezone ──────────────────────────────────────────
        [Parameter("Selected Timezone", Group = "Session & Timezone", DefaultValue = SessionTimezone.NewYork)]
        public SessionTimezone SelectedTimezone { get; set; }

        // ── Stop Loss ───────────────────────────────────────────────────
        [Parameter("Stop Loss Mode", Group = "Stop Loss", DefaultValue = StopLossMode.AtrBased)]
        public StopLossMode StopLossMode { get; set; }

        [Parameter("Fixed Stop Pips", Group = "Stop Loss", DefaultValue = 20.0, MinValue = 1.0, MaxValue = 500.0)]
        public double FixedStopPips { get; set; }

        [Parameter("Candle Stop Percent", Group = "Stop Loss", DefaultValue = 100.0, MinValue = 0.0, MaxValue = 200.0)]
        public double CandleStopPercent { get; set; }

        [Parameter("ATR Stop Period", Group = "Stop Loss", DefaultValue = 10, MinValue = 2, MaxValue = 50)]
        public int AtrStopPeriod { get; set; }

        [Parameter("ATR Stop Multiplier", Group = "Stop Loss", DefaultValue = 1.5, MinValue = 0.5, MaxValue = 5.0)]
        public double AtrStopMultiplier { get; set; }

        [Parameter("Swing Low Lookback", Group = "Stop Loss", DefaultValue = 10, MinValue = 3, MaxValue = 50)]
        public int SwingLowLookback { get; set; }

        [Parameter("Min Stop Pips", Group = "Stop Loss", DefaultValue = 5.0, MinValue = 0.5, MaxValue = 50.0)]
        public double MinStopPips { get; set; }

        // ── Primary Exit ────────────────────────────────────────────────
        [Parameter("Exit Mode", Group = "Primary Exit", DefaultValue = ExitMode.FirstUpCandle)]
        public ExitMode ExitMode { get; set; }

        [Parameter("Take Profit R", Group = "Primary Exit", DefaultValue = 2.0, MinValue = 0.25, MaxValue = 20.0)]
        public double TakeProfitR { get; set; }

        [Parameter("Max Hold Bars", Group = "Primary Exit", DefaultValue = 5, MinValue = 1, MaxValue = 30)]
        public int MaxHoldBars { get; set; }

        // ── Dynamic Stop ─────────────────────────────────────────────────
        [Parameter("Enable Dynamic Stop", Group = "Dynamic Stop", DefaultValue = false)]
        public bool EnableDynamicStop { get; set; }

        [Parameter("Dynamic Stop Mode", Group = "Dynamic Stop", DefaultValue = DynamicStopMode.StepLockR)]
        public DynamicStopMode DynamicStopMode { get; set; }

        [Parameter("Break Even Trigger R", Group = "Dynamic Stop", DefaultValue = 1.0, MinValue = 0.0, MaxValue = 5.0)]
        public double BreakEvenTriggerR { get; set; }

        [Parameter("Break Even Extra Pips", Group = "Dynamic Stop", DefaultValue = 0.0, MinValue = 0.0, MaxValue = 50.0)]
        public double BreakEvenExtraPips { get; set; }

        [Parameter("Dynamic Step R", Group = "Dynamic Stop", DefaultValue = 0.5, MinValue = 0.1, MaxValue = 3.0)]
        public double DynamicStepR { get; set; }

        [Parameter("Trail Distance R", Group = "Dynamic Stop", DefaultValue = 1.0, MinValue = 0.1, MaxValue = 5.0)]
        public double TrailDistanceR { get; set; }

        // ── Risk Management ──────────────────────────────────────────────
        [Parameter("Risk Amount", Group = "Risk Management", DefaultValue = 100.0, MinValue = 1.0, MaxValue = 1000000.0)]
        public double RiskAmount { get; set; }

        [Parameter("Risk Currency Mode", Group = "Risk Management", DefaultValue = RiskCurrency.AccountCurrency)]
        public RiskCurrency RiskCurrencyMode { get; set; }

        [Parameter("Max Daily Losses", Group = "Risk Management", DefaultValue = 1, MinValue = 0, MaxValue = 10)]
        public int MaxDailyLosses { get; set; }

        [Parameter("Max Spread Pips", Group = "Risk Management", DefaultValue = 5.0, MinValue = 0.1, MaxValue = 50.0)]
        public double MaxSpreadPips { get; set; }

        // ── Day Filters ──────────────────────────────────────────────────
        [Parameter("Skip Mondays", Group = "Day Filters", DefaultValue = false)]
        public bool SkipMondays { get; set; }

        [Parameter("Skip Fridays", Group = "Day Filters", DefaultValue = false)]
        public bool SkipFridays { get; set; }

        // ── Logging ──────────────────────────────────────────────────────
        [Parameter("Bot Label", Group = "Logging", DefaultValue = "3DD")]
        public string BotLabel { get; set; }

        [Parameter("Enable Detailed Logging", Group = "Logging", DefaultValue = true)]
        public bool EnableDetailedLogging { get; set; }

        // ── Private Fields ───────────────────────────────────────────────
        private Bars _dailySeries;
        private SimpleMovingAverage _smaTrend;
        private SimpleMovingAverage _sma5;
        private AverageTrueRange _atr;
        private AverageTrueRange _dailyAtr;
        private Dictionary<long, PositionState> _positionStates;
        private bool _tradeAttemptedToday;
        private int _dailyLossCount;
        private DateTime _lastProcessedDate;
        private bool _hardCloseAttempted;
        private double _lastLoggedStop;
        private TimeZoneInfo _sessionTimeZone;
        private TimeSpan _lateEntryTimeCfg;
        private int _totalWins;
        private int _totalLosses;

        // ── OnStart ──────────────────────────────────────────────────────
        protected override void OnStart()
        {
            ResolveTimeZone();

            if (!TimeSpan.TryParse(LateEntryTime, out _lateEntryTimeCfg))
            {
                Print($"[ERROR] Invalid LateEntryTime format: '{LateEntryTime}'. Expected HH:mm:ss.");
                Stop();
                return;
            }

            if (EntryMode == EntryMode.LateSession)
            {
                _dailySeries = MarketData.GetBars(TimeFrame.Daily);
                if (TimeFrame == TimeFrame.Daily)
                    Print("[WARN] LateSession mode requires M5/M15 chart, not D1.");
            }

            if (EntryMode == EntryMode.DailyBarOpen)
            {
                if (TimeFrame != TimeFrame.Daily)
                    Print("[WARN] DailyBarOpen mode expects D1 chart.");
            }

            var closeSrc = EntryMode == EntryMode.LateSession
                ? _dailySeries.ClosePrices
                : Bars.ClosePrices;

            _smaTrend = Indicators.SimpleMovingAverage(closeSrc, TrendSmaPeriod);
            _sma5     = Indicators.SimpleMovingAverage(closeSrc, 5);

            if (StopLossMode == StopLossMode.AtrBased)
            {
                _atr = Indicators.AverageTrueRange(AtrStopPeriod, MovingAverageType.Simple);
                if (EntryMode == EntryMode.LateSession)
                    _dailyAtr = Indicators.AverageTrueRange(_dailySeries, AtrStopPeriod, MovingAverageType.Simple);
            }

            if (ExitMode == ExitMode.DynamicOnly && !EnableDynamicStop)
                Print("[WARN] ExitMode=DynamicOnly but EnableDynamicStop=False. Only MaxHoldBars time stop applies.");

            _positionStates    = new Dictionary<long, PositionState>();
            _tradeAttemptedToday = false;
            _dailyLossCount    = 0;
            _lastProcessedDate = DateTime.MinValue;
            _hardCloseAttempted = false;
            _lastLoggedStop    = 0;
            _totalWins         = 0;
            _totalLosses       = 0;

            Positions.Closed += OnPositionClosed;

            RecoverOpenPositions();
            PrintStartupConfig();

            Timer.Start(10);
            Print("[STARTUP] Bot ready.");
        }

        // ── OnStop ───────────────────────────────────────────────────────
        protected override void OnStop()
        {
            Timer.Stop();
            Positions.Closed -= OnPositionClosed;
            int openCount = Positions.Count(p => IsBotPosition(p));
            Print($"[SHUTDOWN] Balance: {Account.Balance:F2} {Account.Asset.Name} | Open positions: {openCount}");
        }

        // ── OnBar ────────────────────────────────────────────────────────
        protected override void OnBar()
        {
            UpdateDailyState();

            if (HasOpenBotPosition())
            {
                ManageOpenPosition();
                return;
            }

            if (!_tradeAttemptedToday)
                AttemptEntry();
        }

        // ── OnTick ───────────────────────────────────────────────────────
        protected override void OnTick()
        {
            if (!HasOpenBotPosition()) return;
            if (EnableDynamicStop)
                ProcessDynamicStop();
        }

        // ── OnTimer ──────────────────────────────────────────────────────
        protected override void OnTimer()
        {
            if (!HasOpenBotPosition()) return;

            if (EnableDynamicStop)
                ProcessDynamicStop();

            // Safety net: force-close if position open longer than (MaxHoldBars+1)*24h
            foreach (var pos in Positions.Where(p => IsBotPosition(p)).ToList())
            {
                var state = GetOrRegisterState(pos);
                var elapsed = Server.Time - state.EntryTimeUtc;
                if (elapsed.TotalHours > (MaxHoldBars + 1) * 24.0)
                {
                    Print($"[SAFETY_NET] Timer-triggered close: {pos.Label} open {elapsed.TotalHours:F1}h");
                    ClosePosition(pos);
                }
            }
        }

        // ── UpdateDailyState ─────────────────────────────────────────────
        private void UpdateDailyState()
        {
            DateTime localNow = GetLocalTime();
            if (localNow.Date <= _lastProcessedDate.Date) return;

            _tradeAttemptedToday = false;
            _dailyLossCount      = 0;
            _hardCloseAttempted  = false;
            _lastProcessedDate   = localNow;
            _lastLoggedStop      = 0;

            Print("───────────────────────────────────────────────────────────────");
            Print($"[NEW_DAY] {localNow:yyyy-MM-dd} ({localNow.DayOfWeek}) | UTC: {Server.Time:HH:mm:ss}");
            Print($"[NEW_DAY] Balance: {Account.Balance:F2} {Account.Asset.Name} | Equity: {Account.Equity:F2} {Account.Asset.Name}");

            LogCurrentDownDayCount();

            double smaVal = _smaTrend.Result.LastValue;
            Print($"[STATE] SMA{TrendSmaPeriod}: {smaVal:F5}");

            foreach (var pos in Positions.Where(p => IsBotPosition(p)))
            {
                var state = GetOrRegisterState(pos);
                int barsHeld = GetBarsHeld(pos, state);
                Print($"[STATE] Open: {pos.Label} | Pips: {pos.Pips:F1} | SL: {pos.StopLoss:F5} | Bars: {barsHeld}/{MaxHoldBars}");
            }
        }

        // ── LogCurrentDownDayCount ────────────────────────────────────────
        private void LogCurrentDownDayCount()
        {
            int streak = 0;
            var closeParts = new System.Text.StringBuilder();

            if (EntryMode == EntryMode.DailyBarOpen)
            {
                int maxCheck = Math.Min(NumberOfDownDays + 2, Bars.Count - 1);
                for (int i = 1; i <= maxCheck; i++)
                {
                    double c = Bars.Last(i).Close;
                    double prev = Bars.Last(i + 1).Close;
                    if (i <= 3) closeParts.Append($" Day -{i}: {c:F5} |");
                    if (c < prev) streak++;
                    else break;
                }
            }
            else
            {
                if (_dailySeries != null && _dailySeries.Count > 3)
                {
                    for (int i = 1; i <= Math.Min(NumberOfDownDays + 1, _dailySeries.Count - 2); i++)
                    {
                        double c = _dailySeries.Last(i).Close;
                        double prev = _dailySeries.Last(i + 1).Close;
                        if (i <= 3) closeParts.Append($" Day -{i}: {c:F5} |");
                        if (c < prev) streak++;
                        else break;
                    }
                }
            }

            Print($"[STATE] Current down day streak: {streak} (need {NumberOfDownDays})");
            if (closeParts.Length > 0)
                Print($"[STATE]{closeParts.ToString().TrimEnd('|')}");
        }

        // ── AttemptEntry ─────────────────────────────────────────────────
        private void AttemptEntry()
        {
            DateTime localNow = GetLocalTime();

            // LateSession: only attempt within window
            if (EntryMode == EntryMode.LateSession && !IsInLateEntryWindow())
                return;

            Print($"[ENTRY_EVAL] ═══ Evaluating entry at {localNow:HH:mm:ss} ({localNow.DayOfWeek}) ═══");

            // [FILTER:DAY_MON]
            if (SkipMondays && localNow.DayOfWeek == DayOfWeek.Monday)
            {
                if (EnableDetailedLogging) Print("[FILTER:DAY_MON] BLOCKED: Monday trading disabled");
                _tradeAttemptedToday = true;
                return;
            }
            if (EnableDetailedLogging) Print("[FILTER:DAY_MON] PASSED: Monday trading allowed");

            // [FILTER:DAY_FRI]
            if (SkipFridays && localNow.DayOfWeek == DayOfWeek.Friday)
            {
                if (EnableDetailedLogging) Print("[FILTER:DAY_FRI] BLOCKED: Friday trading disabled");
                _tradeAttemptedToday = true;
                return;
            }
            if (EnableDetailedLogging) Print($"[FILTER:DAY_FRI] PASSED: Friday trading allowed");

            // [FILTER:LOSS]
            if (MaxDailyLosses > 0 && _dailyLossCount >= MaxDailyLosses)
            {
                if (EnableDetailedLogging) Print($"[FILTER:LOSS] BLOCKED: Daily losses {_dailyLossCount}/{MaxDailyLosses}");
                _tradeAttemptedToday = true;
                return;
            }
            if (EnableDetailedLogging) Print($"[FILTER:LOSS] PASSED: Daily losses {_dailyLossCount}/{MaxDailyLosses}");

            // [FILTER:SPREAD]
            double spreadPips = Symbol.Spread / Symbol.PipSize;
            if (spreadPips > MaxSpreadPips)
            {
                if (EnableDetailedLogging) Print($"[FILTER:SPREAD] BLOCKED: {spreadPips:F1} pips > {MaxSpreadPips} pips max");
                return;
            }
            if (EnableDetailedLogging) Print($"[FILTER:SPREAD] PASSED: {spreadPips:F1} pips <= {MaxSpreadPips} pips max");

            // [FILTER:TREND]
            if (RequireTrendFilter)
            {
                double smaVal = _smaTrend.Result.LastValue;
                double refPrice = EntryMode == EntryMode.DailyBarOpen
                    ? Bars.Last(1).Close
                    : Symbol.Bid;
                if (refPrice <= smaVal)
                {
                    if (EnableDetailedLogging)
                        Print($"[FILTER:TREND] BLOCKED: Price {refPrice:F5} < SMA{TrendSmaPeriod} {smaVal:F5} — no trade in downtrend");
                    _tradeAttemptedToday = true;
                    return;
                }
                if (EnableDetailedLogging)
                    Print($"[FILTER:TREND] PASSED: Price {refPrice:F5} > SMA{TrendSmaPeriod} {smaVal:F5}");
            }

            // [FILTER:DOWNDAYS]
            bool downDaysOk = EntryMode == EntryMode.DailyBarOpen
                ? CountDownDays()
                : CountDownDaysLateSession();

            if (!downDaysOk)
            {
                _tradeAttemptedToday = true;
                return;
            }

            // [FILTER:SMA5]
            if (RequirePriceBelowSMA5)
            {
                double sma5Val = _sma5.Result.LastValue;
                double refClose = EntryMode == EntryMode.DailyBarOpen
                    ? Bars.Last(1).Close
                    : Symbol.Bid;
                if (refClose >= sma5Val)
                {
                    if (EnableDetailedLogging)
                        Print($"[FILTER:SMA5] BLOCKED: Close {refClose:F5} >= 5-SMA {sma5Val:F5}");
                    _tradeAttemptedToday = true;
                    return;
                }
                if (EnableDetailedLogging)
                    Print($"[FILTER:SMA5] PASSED: Close {refClose:F5} < 5-SMA {sma5Val:F5}");
            }

            // All filters passed
            Print("[ENTRY] ALL FILTERS PASSED. Executing trade.");
            _tradeAttemptedToday = true;
            ExecuteEntry();
        }

        // ── CountDownDays (DailyBarOpen) ──────────────────────────────────
        private bool CountDownDays()
        {
            if (Bars.Count < NumberOfDownDays + 5)
            {
                Print($"[WARN] Insufficient bar history ({Bars.Count} bars). Need {NumberOfDownDays + 5}.");
                return false;
            }

            int downCount = 0;
            for (int i = 1; i <= NumberOfDownDays; i++)
            {
                double c    = Bars.Last(i).Close;
                double prev = Bars.Last(i + 1).Close;
                if (EnableDetailedLogging)
                {
                    if (c < prev)
                        Print($"[FILTER:DOWNDAYS] Day -{i}: {c:F5} < {prev:F5} (Day -{i+1}) ✓");
                    else
                        Print($"[FILTER:DOWNDAYS] Day -{i}: NOT a down day ({c:F5} NOT < {prev:F5}) ✗");
                }
                if (c < prev) downCount++;
                else break;
            }

            bool result = downCount == NumberOfDownDays;
            Print($"[FILTER:DOWNDAYS] {(result ? "SIGNAL" : "NO SIGNAL")}: {downCount}/{NumberOfDownDays} consecutive down closes found");
            return result;
        }

        // ── CountDownDaysLateSession ──────────────────────────────────────
        private bool CountDownDaysLateSession()
        {
            if (_dailySeries == null || _dailySeries.Count < NumberOfDownDays + 2)
            {
                Print("[WARN] Daily series not ready for down-day count.");
                return false;
            }

            double currentPrice    = Symbol.Bid;
            double yesterdayClose  = _dailySeries.Last(1).Close;
            bool todayIsDown       = currentPrice < yesterdayClose;

            if (EnableDetailedLogging)
                Print($"[FILTER:DOWNDAYS] Today live: {currentPrice:F5} vs yesterday close {yesterdayClose:F5} — {(todayIsDown ? "DOWN ✓" : "NOT DOWN ✗")}");

            if (!todayIsDown) { Print("[FILTER:DOWNDAYS] NO SIGNAL: Today not down"); return false; }

            int completedDownCount = 0;
            for (int i = 1; i < NumberOfDownDays; i++)
            {
                double c    = _dailySeries.Last(i).Close;
                double prev = _dailySeries.Last(i + 1).Close;
                if (c < prev)
                {
                    completedDownCount++;
                    if (EnableDetailedLogging)
                        Print($"[FILTER:DOWNDAYS] Day -{i}: {c:F5} < {prev:F5} (Day -{i+1}) ✓");
                }
                else
                {
                    if (EnableDetailedLogging)
                        Print($"[FILTER:DOWNDAYS] Day -{i}: NOT a down day ({c:F5} NOT < {prev:F5}) ✗");
                    Print($"[FILTER:DOWNDAYS] NO SIGNAL: {completedDownCount + 1}/{NumberOfDownDays} down days found");
                    return false;
                }
            }

            bool result = completedDownCount == (NumberOfDownDays - 1) && todayIsDown;
            Print($"[FILTER:DOWNDAYS] {(result ? "SIGNAL" : "NO SIGNAL")}: {NumberOfDownDays} down days confirmed");
            return result;
        }

        // ── ExecuteEntry ─────────────────────────────────────────────────
        private void ExecuteEntry()
        {
            double entryPrice = Symbol.Ask;

            var (stopPips, stopPrice) = CalculateStopLoss(entryPrice);

            // Volume calculation
            double riskAccountCcy  = ConvertRiskToAccountCurrency();
            double pipValuePerUnit  = Symbol.PipValue;
            double rawVolume        = riskAccountCcy / (stopPips * pipValuePerUnit);
            double normVolume       = Symbol.NormalizeVolumeInUnits(rawVolume);
            normVolume              = Math.Max(Symbol.VolumeInUnitsMin, Math.Min(Symbol.VolumeInUnitsMax, normVolume));

            if (normVolume < Symbol.VolumeInUnitsMin)
            {
                Print($"[ORDER_ABORT] Calculated volume {normVolume} below minimum {Symbol.VolumeInUnitsMin}. Skipping.");
                return;
            }

            Print($"[SIZING] Risk: {riskAccountCcy:F2} {Account.Asset.Name} | SL: {stopPips:F1} pips | PipValue: {pipValuePerUnit:F8}");
            Print($"[SIZING] Raw units: {rawVolume:F2} → Normalised: {normVolume} units");

            // TP calculation
            double? tpPips  = null;
            double  tpPrice = 0;
            if (ExitMode == ExitMode.SingleTP)
            {
                double tp = stopPips * TakeProfitR;
                tpPips    = tp;
                tpPrice   = entryPrice + tp * Symbol.PipSize;
                Print($"[TP_CALC] TP at {tpPrice:F5} ({TakeProfitR}R = {tp:F1} pips)");
                Print($"[EXIT:SINGLETP] TP set at {tpPrice:F5} ({TakeProfitR}R = {tp:F1} pips)");
            }

            string label   = $"{BotLabel}_Buy_{Server.Time:yyyyMMdd_HHmm}";
            string comment = $"3DD|Bars:{NumberOfDownDays}|SL:{StopLossMode}|Exit:{ExitMode}";

            var result = ExecuteMarketOrder(TradeType.Buy, SymbolName, normVolume, label, stopPips, tpPips, comment);

            if (result.IsSuccessful)
            {
                var pos   = result.Position;
                var state = new PositionState
                {
                    PositionId            = pos.Id,
                    EntryPrice            = pos.EntryPrice,
                    InitialRiskPipsActual = stopPips,
                    InitialVolumeInUnits  = pos.VolumeInUnits,
                    EntryTimeUtc          = Server.Time,
                    EntryBarIndex         = Bars.Count,
                    EntryDate             = GetLocalTime().Date,
                    BreakEvenDone         = false,
                    LastTrailSteps        = 0
                };
                _positionStates[pos.Id] = state;

                string tpStr = tpPips.HasValue ? $"{tpPrice:F5} ({tpPips.Value:F1} pips)" : "none";
                Print("╔══════════════════════════════════════════════════════════════╗");
                Print("║ TRADE ENTERED");
                Print("╠══════════════════════════════════════════════════════════════╣");
                Print($"║ Label:   {label}");
                Print($"║ Symbol:  {SymbolName}");
                Print($"║ Entry:   {pos.EntryPrice:F5}");
                Print($"║ Stop:    {stopPrice:F5} ({stopPips:F1} pips)");
                Print($"║ TP:      {tpStr}");
                Print($"║ Volume:  {normVolume} units");
                Print($"║ Risk:    {riskAccountCcy:F2} {Account.Asset.Name}");
                Print("╚══════════════════════════════════════════════════════════════╝");
            }
            else
            {
                Print($"[ORDER_FAILED] Error: {result.Error} | Vol: {normVolume} | SL: {stopPips:F1} pips");
            }
        }

        // ── CalculateStopLoss ────────────────────────────────────────────
        private (double stopPips, double stopPrice) CalculateStopLoss(double entryPrice)
        {
            double pipSize = Symbol.PipSize;
            double rawPips, stopPrice;

            // Reference candle
            double refHigh, refLow, refClose;
            if (EntryMode == EntryMode.DailyBarOpen)
            {
                var c  = Bars.Last(1);
                refHigh  = c.High; refLow = c.Low; refClose = c.Close;
            }
            else
            {
                refHigh  = GetTodaySessionHigh();
                refLow   = GetTodaySessionLow();
                refClose = _dailySeries != null && _dailySeries.Count > 1 ? _dailySeries.Last(1).Close : Symbol.Bid;
                if (refLow  == 0) refLow  = _dailySeries?.Last(1).Low  ?? Symbol.Bid;
                if (refHigh == 0) refHigh = _dailySeries?.Last(1).High ?? Symbol.Bid;
            }

            double atrVal = 0;
            if (StopLossMode == StopLossMode.AtrBased)
                atrVal = EntryMode == EntryMode.LateSession && _dailyAtr != null
                    ? _dailyAtr.Result.LastValue
                    : (_atr?.Result.LastValue ?? 0);

            Print($"[SL_CALC] Mode: {StopLossMode}");
            Print($"[SL_CALC] Reference candle: High={refHigh:F5} Low={refLow:F5} Close={refClose:F5} ATR={atrVal:F5}");

            switch (StopLossMode)
            {
                case StopLossMode.FixedPips:
                    rawPips   = FixedStopPips;
                    stopPrice = entryPrice - rawPips * pipSize;
                    break;

                case StopLossMode.CandleExtreme:
                    stopPrice = refLow;
                    rawPips   = (entryPrice - stopPrice) / pipSize;
                    break;

                case StopLossMode.CandlePercent:
                {
                    double range = refHigh - refLow;
                    double dist  = range * (CandleStopPercent / 100.0);
                    stopPrice    = refClose - dist;
                    rawPips      = (entryPrice - stopPrice) / pipSize;
                    if (stopPrice >= entryPrice)
                    {
                        Print($"[WARN] CandlePercent stopPrice {stopPrice:F5} >= entry {entryPrice:F5}. Using MinStopPips.");
                        rawPips   = MinStopPips;
                        stopPrice = entryPrice - rawPips * pipSize;
                    }
                    break;
                }

                case StopLossMode.AtrBased:
                    rawPips   = (atrVal * AtrStopMultiplier) / pipSize;
                    stopPrice = entryPrice - rawPips * pipSize;
                    break;

                case StopLossMode.LowestLowNDays:
                {
                    double lowestLow;
                    if (EntryMode == EntryMode.DailyBarOpen)
                    {
                        lowestLow = double.MaxValue;
                        for (int i = 1; i <= NumberOfDownDays; i++)
                            lowestLow = Math.Min(lowestLow, Bars.Last(i).Low);
                    }
                    else
                    {
                        lowestLow = GetTodaySessionLow();
                        if (lowestLow == 0 && _dailySeries != null) lowestLow = _dailySeries.Last(1).Low;
                        if (_dailySeries != null)
                            for (int i = 1; i < NumberOfDownDays; i++)
                                lowestLow = Math.Min(lowestLow, _dailySeries.Last(i).Low);
                    }
                    stopPrice = lowestLow;
                    rawPips   = (entryPrice - stopPrice) / pipSize;
                    break;
                }

                case StopLossMode.SwingLow:
                {
                    double swingLow = FindSwingLow();
                    if (swingLow <= 0)
                    {
                        // Fallback to LowestLowNDays
                        double lowestLow;
                        if (EntryMode == EntryMode.DailyBarOpen)
                        {
                            lowestLow = double.MaxValue;
                            for (int i = 1; i <= NumberOfDownDays; i++)
                                lowestLow = Math.Min(lowestLow, Bars.Last(i).Low);
                        }
                        else
                        {
                            lowestLow = GetTodaySessionLow();
                            if (lowestLow == 0 && _dailySeries != null) lowestLow = _dailySeries.Last(1).Low;
                            if (_dailySeries != null)
                                for (int i = 1; i < NumberOfDownDays; i++)
                                    lowestLow = Math.Min(lowestLow, _dailySeries.Last(i).Low);
                        }
                        swingLow = lowestLow;
                        Print($"[SL:SWINGLOW] No swing low found in {SwingLowLookback} bars, using LowestLow fallback: {swingLow:F5}");
                    }
                    stopPrice = swingLow;
                    rawPips   = (entryPrice - stopPrice) / pipSize;
                    break;
                }

                default:
                    rawPips   = FixedStopPips;
                    stopPrice = entryPrice - rawPips * pipSize;
                    break;
            }

            // Enforce minimum
            if (rawPips < MinStopPips)
            {
                rawPips   = MinStopPips;
                stopPrice = entryPrice - rawPips * pipSize;
            }

            // Guard: stop above entry
            if (stopPrice >= entryPrice)
            {
                Print($"[WARN] stopPrice {stopPrice:F5} >= entryPrice {entryPrice:F5}. Forcing MinStopPips.");
                rawPips   = MinStopPips;
                stopPrice = entryPrice - rawPips * pipSize;
            }

            Print($"[SL_CALC] Raw stop pips: {rawPips:F1} | After MinStop floor: {rawPips:F1}");
            Print($"[SL_CALC] Stop price: {stopPrice:F5}");
            return (rawPips, stopPrice);
        }

        // ── FindSwingLow ─────────────────────────────────────────────────
        private double FindSwingLow()
        {
            int limit = SwingLowLookback;
            for (int i = 2; i <= limit; i++)
            {
                double curLow, prevLow, nextLow;
                if (EntryMode == EntryMode.DailyBarOpen)
                {
                    if (i + 1 >= Bars.Count) break;
                    curLow  = Bars.Last(i).Low;
                    prevLow = Bars.Last(i - 1).Low;
                    nextLow = Bars.Last(i + 1).Low;
                }
                else
                {
                    if (_dailySeries == null || i + 1 >= _dailySeries.Count) break;
                    curLow  = _dailySeries.Last(i).Low;
                    prevLow = _dailySeries.Last(i - 1).Low;
                    nextLow = _dailySeries.Last(i + 1).Low;
                }

                if (curLow < prevLow && curLow < nextLow)
                {
                    Print($"[SL:SWINGLOW] Found swing low at {curLow:F5} ({i} bars back)");
                    return curLow;
                }
            }
            return 0;
        }

        // ── ManageOpenPosition ────────────────────────────────────────────
        private void ManageOpenPosition()
        {
            foreach (var pos in Positions.Where(p => IsBotPosition(p)).ToList())
            {
                var state    = GetOrRegisterState(pos);
                int barsHeld = GetBarsHeld(pos, state);
                double profitR = state.InitialRiskPipsActual > 0
                    ? pos.Pips / state.InitialRiskPipsActual : 0;

                if (EnableDetailedLogging)
                {
                    Print($"[MANAGE] {pos.Label} | Pips: {pos.Pips:F1} | R: {profitR:F2}R | BE done: {state.BreakEvenDone}");
                    string slStr = pos.StopLoss.HasValue ? pos.StopLoss.Value.ToString("F5") : "none";
                    string tpStr = pos.TakeProfit.HasValue ? pos.TakeProfit.Value.ToString("F5") : "none";
                    Print($"[MANAGE] Current SL: {slStr} | TP: {tpStr} | Bars held: {barsHeld}");
                }

                // EXIT: FirstUpCandle
                if (ExitMode == ExitMode.FirstUpCandle)
                {
                    bool exitSignal = false;
                    if (EntryMode == EntryMode.DailyBarOpen)
                    {
                        if (Bars.Count >= 3 && Bars.Last(1).Close > Bars.Last(2).Close)
                            exitSignal = true;
                    }
                    else
                    {
                        if (_dailySeries != null && _dailySeries.Count >= 3
                            && _dailySeries.Last(1).Close > _dailySeries.Last(2).Close)
                            exitSignal = true;
                    }

                    if (exitSignal)
                    {
                        double c  = EntryMode == EntryMode.DailyBarOpen ? Bars.Last(1).Close : _dailySeries.Last(1).Close;
                        double pc = EntryMode == EntryMode.DailyBarOpen ? Bars.Last(2).Close : _dailySeries.Last(2).Close;
                        Print($"[EXIT:FIRSTUPCANDLE] TRIGGERED — Close {c:F5} > PriorClose {pc:F5}");
                        ClosePosition(pos);
                        return;
                    }
                }

                // EXIT: TimeStop (all modes)
                if (barsHeld >= MaxHoldBars)
                {
                    Print($"[EXIT:TIMESTOP] TRIGGERED — {barsHeld} bars held (max {MaxHoldBars})");
                    ClosePosition(pos);
                    return;
                }

                if (EnableDetailedLogging)
                    Print($"[MANAGE] No exit trigger. Position continuing. ({barsHeld}/{MaxHoldBars} bars)");
            }
        }

        // ── GetBarsHeld ───────────────────────────────────────────────────
        private int GetBarsHeld(Position pos, PositionState state)
        {
            if (EntryMode == EntryMode.DailyBarOpen)
                return Bars.Count - state.EntryBarIndex;

            // LateSession: count daily bars since entry date
            if (_dailySeries == null) return 0;
            int count = 0;
            for (int i = 1; i < _dailySeries.Count; i++)
            {
                if (_dailySeries.Last(i).OpenTime.Date <= state.EntryDate) break;
                count++;
            }
            return count;
        }

        // ── ProcessDynamicStop ────────────────────────────────────────────
        private void ProcessDynamicStop()
        {
            foreach (var pos in Positions.Where(p => IsBotPosition(p)).ToList())
            {
                if (!_positionStates.TryGetValue(pos.Id, out var state)) continue;

                double profitR = state.InitialRiskPipsActual > 0
                    ? pos.Pips / state.InitialRiskPipsActual : 0;

                // Breakeven move
                if (!state.BreakEvenDone && profitR >= BreakEvenTriggerR)
                {
                    double beSL = state.EntryPrice + BreakEvenExtraPips * Symbol.PipSize;
                    if (!pos.StopLoss.HasValue || beSL > pos.StopLoss.Value)
                    {
                        ModifyPosition(pos, beSL, pos.TakeProfit, ProtectionType.Absolute);
                        state.BreakEvenDone = true;
                        Print($"[DYNAMIC:BREAKEVEN] SL moved to {beSL:F5} (entry + {BreakEvenExtraPips} extra pips) at {profitR:F2}R");
                    }
                    else
                    {
                        state.BreakEvenDone = true;
                    }
                }

                if (!state.BreakEvenDone) continue;

                if (DynamicStopMode == DynamicStopMode.StepLockR)
                {
                    double steps = Math.Floor((profitR - BreakEvenTriggerR) / DynamicStepR);
                    if (steps > state.LastTrailSteps && steps > 0)
                    {
                        double lockInR    = steps * DynamicStepR;
                        double lockInPips = lockInR * state.InitialRiskPipsActual + BreakEvenExtraPips;
                        double newSL      = state.EntryPrice + lockInPips * Symbol.PipSize;

                        if (!pos.StopLoss.HasValue || newSL > pos.StopLoss.Value)
                        {
                            ModifyPosition(pos, newSL, pos.TakeProfit, ProtectionType.Absolute);
                            state.LastTrailSteps = steps;
                            Print($"[DYNAMIC:STEPLOCK] SL -> {newSL:F5} (locked {lockInR:F2}R, step {steps}, profitR={profitR:F2}R)");
                        }
                    }
                }
                else if (DynamicStopMode == DynamicStopMode.TrailBehindPriceR)
                {
                    double trailPips  = TrailDistanceR * state.InitialRiskPipsActual;
                    double desiredSL  = Symbol.Bid - trailPips * Symbol.PipSize;

                    if (!pos.StopLoss.HasValue || desiredSL > pos.StopLoss.Value)
                    {
                        ModifyPosition(pos, desiredSL, pos.TakeProfit, ProtectionType.Absolute);

                        // Throttle logging — only log if SL moved > 1 pip
                        if (Math.Abs(desiredSL - _lastLoggedStop) > Symbol.PipSize)
                        {
                            Print($"[DYNAMIC:TRAIL] SL -> {desiredSL:F5} (trail {TrailDistanceR:F2}R = {trailPips:F1} pips)");
                            _lastLoggedStop = desiredSL;
                        }
                    }
                }
            }
        }

        // ── OnPositionClosed ──────────────────────────────────────────────
        private void OnPositionClosed(PositionClosedEventArgs args)
        {
            var pos = args.Position;
            if (!IsBotPosition(pos)) return;

            _positionStates.TryGetValue(pos.Id, out var state);

            double rMultiple = 0;
            int barsHeld = 0;
            if (state != null && state.InitialRiskPipsActual > 0)
            {
                rMultiple = pos.Pips / state.InitialRiskPipsActual;
                barsHeld  = GetBarsHeld(pos, state);
            }

            var duration = Server.Time - (state?.EntryTimeUtc ?? Server.Time);
            bool isWin   = pos.NetProfit >= 0;
            if (isWin) _totalWins++; else { _totalLosses++; _dailyLossCount++; }

            string slStr = pos.StopLoss.HasValue   ? pos.StopLoss.Value.ToString("F5")   : "none";
            string tpStr = pos.TakeProfit.HasValue  ? pos.TakeProfit.Value.ToString("F5") : "none";
            int tradeNum  = _totalWins + _totalLosses;

            Print("╔══════════════════════════════════════════════════════════════╗");
            Print("║ POSITION CLOSED");
            Print("╠══════════════════════════════════════════════════════════════╣");
            Print($"║ Label:        {pos.Label}");
            Print($"║ Direction:    {pos.TradeType}");
            Print($"║ Entry:        {pos.EntryPrice:F5}");
            Print($"║ Close Reason: {args.Reason}");
            Print($"║ Gross P/L:    {pos.GrossProfit:F2} {Account.Asset.Name}");
            Print($"║ Net P/L:      {pos.NetProfit:F2} {Account.Asset.Name} (after commission/swap)");
            Print($"║ Pips:         {pos.Pips:F1}");
            Print($"║ R-Multiple:   {rMultiple:F2}R");
            Print($"║ Volume:       {pos.VolumeInUnits} units");
            Print($"║ Duration:     {duration.Days}d {duration.Hours}h {duration.Minutes}m");
            Print($"║ Bars Held:    {barsHeld}");
            Print($"║ Final SL:     {slStr}");
            Print($"║ Final TP:     {tpStr}");
            Print("╠══════════════════════════════════════════════════════════════╣");
            Print($"║ {(isWin ? "WIN" : "LOSS")} #{tradeNum} | Balance: {Account.Balance:F2} | Equity: {Account.Equity:F2}");
            Print("╚══════════════════════════════════════════════════════════════╝");

            _positionStates.Remove(pos.Id);
            _lastLoggedStop = 0;
        }

        // ── Position Utilities ────────────────────────────────────────────
        private bool HasOpenBotPosition()
            => Positions.Any(p => IsBotPosition(p));

        private bool IsBotPosition(Position pos)
            => pos.SymbolName == SymbolName
            && pos.Label != null
            && pos.Label.StartsWith(BotLabel);

        private PositionState GetOrRegisterState(Position pos)
        {
            if (!_positionStates.TryGetValue(pos.Id, out var state))
            {
                RegisterExistingPosition(pos);
                _positionStates.TryGetValue(pos.Id, out state);
            }
            return state;
        }

        private void RecoverOpenPositions()
        {
            foreach (var pos in Positions.Where(p => IsBotPosition(p)))
                RegisterExistingPosition(pos);
        }

        private void RegisterExistingPosition(Position pos)
        {
            if (_positionStates.ContainsKey(pos.Id)) return;

            double riskPips = pos.StopLoss.HasValue
                ? Math.Abs(pos.EntryPrice - pos.StopLoss.Value) / Symbol.PipSize
                : FixedStopPips;

            // Estimate entry bar index
            int entryBarIndex = Bars.Count;
            for (int i = 1; i < Bars.Count; i++)
            {
                if (Bars.Last(i).OpenTime <= pos.EntryTime)
                {
                    entryBarIndex = Bars.Count - i;
                    break;
                }
            }

            var state = new PositionState
            {
                PositionId            = pos.Id,
                EntryPrice            = pos.EntryPrice,
                InitialRiskPipsActual = riskPips,
                InitialVolumeInUnits  = pos.VolumeInUnits,
                EntryTimeUtc          = pos.EntryTime,
                EntryBarIndex         = entryBarIndex,
                EntryDate             = TimeZoneInfo.ConvertTimeFromUtc(pos.EntryTime.ToUniversalTime(), _sessionTimeZone).Date,
                BreakEvenDone         = false,
                LastTrailSteps        = 0
            };
            _positionStates[pos.Id] = state;

            Print($"[RECOVER] Position: {pos.Label} | Entry: {pos.EntryPrice:F5} | SL: {(pos.StopLoss.HasValue ? pos.StopLoss.Value.ToString("F5") : "none")} | Risk: {riskPips:F1} pips | Pips P/L: {pos.Pips:F1}");
        }

        // ── Session Helpers ───────────────────────────────────────────────
        private DateTime GetLocalTime()
            => TimeZoneInfo.ConvertTimeFromUtc(Server.Time.ToUniversalTime(), _sessionTimeZone);

        private bool IsInLateEntryWindow()
        {
            var localNow    = GetLocalTime();
            var windowStart = localNow.Date + _lateEntryTimeCfg;
            var windowEnd   = windowStart.AddMinutes(LateEntryWindowMinutes);
            return localNow >= windowStart && localNow < windowEnd;
        }

        private bool IsBarInTradingSession(DateTime barLocal)
        {
            var t = barLocal.TimeOfDay;
            switch (SelectedTimezone)
            {
                case SessionTimezone.NewYork:
                    return t >= TimeSpan.FromHours(9.5) && t < TimeSpan.FromHours(16);
                case SessionTimezone.London:
                    return t >= TimeSpan.FromHours(8) && t < TimeSpan.FromHours(16.5);
                case SessionTimezone.Frankfurt:
                    return t >= TimeSpan.FromHours(9) && t < TimeSpan.FromHours(17.5);
                default:
                    return true;
            }
        }

        private double GetTodaySessionLow()
        {
            var localNow = GetLocalTime();
            double low   = double.MaxValue;
            for (int i = 0; i < Math.Min(Bars.Count, 200); i++)
            {
                var barLocal = TimeZoneInfo.ConvertTimeFromUtc(
                    Bars.Last(i).OpenTime.ToUniversalTime(), _sessionTimeZone);
                if (barLocal.Date < localNow.Date) break;
                if (!IsBarInTradingSession(barLocal)) continue;
                low = Math.Min(low, Bars.Last(i).Low);
            }
            return low == double.MaxValue ? 0 : low;
        }

        private double GetTodaySessionHigh()
        {
            var localNow = GetLocalTime();
            double high  = double.MinValue;
            for (int i = 0; i < Math.Min(Bars.Count, 200); i++)
            {
                var barLocal = TimeZoneInfo.ConvertTimeFromUtc(
                    Bars.Last(i).OpenTime.ToUniversalTime(), _sessionTimeZone);
                if (barLocal.Date < localNow.Date) break;
                if (!IsBarInTradingSession(barLocal)) continue;
                high = Math.Max(high, Bars.Last(i).High);
            }
            return high == double.MinValue ? 0 : high;
        }

        private void ResolveTimeZone()
        {
            string tzId;
            switch (SelectedTimezone)
            {
                case SessionTimezone.NewYork:   tzId = "Eastern Standard Time"; break;
                case SessionTimezone.London:    tzId = "GMT Standard Time";     break;
                case SessionTimezone.Frankfurt: tzId = "Central European Standard Time"; break;
                default:                        tzId = "UTC"; break;
            }

            try
            {
                _sessionTimeZone = TimeZoneInfo.FindSystemTimeZoneById(tzId);
            }
            catch
            {
                // Try alternate Linux ID
                try
                {
                    string linuxId = SelectedTimezone == SessionTimezone.NewYork  ? "America/New_York"
                                   : SelectedTimezone == SessionTimezone.London   ? "Europe/London"
                                   : "Europe/Berlin";
                    _sessionTimeZone = TimeZoneInfo.FindSystemTimeZoneById(linuxId);
                }
                catch
                {
                    Print($"[ERROR] Could not resolve timezone for {SelectedTimezone}. Falling back to UTC.");
                    _sessionTimeZone = TimeZoneInfo.Utc;
                }
            }
        }

        // ── Risk Conversion ───────────────────────────────────────────────
        private double ConvertRiskToAccountCurrency()
        {
            string accountCcy = Account.Asset.Name;

            if (RiskCurrencyMode == RiskCurrency.AccountCurrency)
            {
                Print($"[RISK_CONV] No conversion needed. Risk: {RiskAmount:F2} {accountCcy}");
                return RiskAmount;
            }

            string targetCcy = RiskCurrencyMode == RiskCurrency.USD ? "USD" : "GBP";

            if (targetCcy == accountCcy)
            {
                Print($"[RISK_CONV] No conversion needed. Risk: {RiskAmount:F2} {accountCcy}");
                return RiskAmount;
            }

            // Try inverse pair first: accountCcy + targetCcy
            string pairInverse = accountCcy + targetCcy;
            string pairDirect  = targetCcy + accountCcy;

            var symInverse = Symbols.GetSymbol(pairInverse);
            if (symInverse != null)
            {
                double rate      = symInverse.Bid;
                double converted = RiskAmount * rate;
                Print($"[RISK_CONV] Converting {RiskAmount:F2} {targetCcy} → {accountCcy} using {pairInverse} rate {rate:F5} = {converted:F2} {accountCcy}");
                return converted;
            }

            var symDirect = Symbols.GetSymbol(pairDirect);
            if (symDirect != null)
            {
                double rate      = 1.0 / symDirect.Ask;
                double converted = RiskAmount * rate;
                Print($"[RISK_CONV] Converting {RiskAmount:F2} {targetCcy} → {accountCcy} using {pairDirect} (inverse) rate {rate:F5} = {converted:F2} {accountCcy}");
                return converted;
            }

            Print($"[WARN] Could not find conversion pair for {targetCcy}/{accountCcy}. Using RiskAmount as-is.");
            return RiskAmount;
        }

        // ── Startup Config Dump ───────────────────────────────────────────
        private void PrintStartupConfig()
        {
            var offset = _sessionTimeZone.GetUtcOffset(Server.Time);
            string tzDisplay = $"{_sessionTimeZone.Id} (UTC{(offset >= TimeSpan.Zero ? "+" : "")}{offset.Hours:D2}:{offset.Minutes:D2})";
            string maxLossStr = MaxDailyLosses == 0 ? "unlimited" : MaxDailyLosses.ToString();

            Print("╔══════════════════════════════════════════════════════════════╗");
            Print("║          3 DOWN DAYS BOT — STARTUP CONFIGURATION            ║");
            Print("╚══════════════════════════════════════════════════════════════╝");
            Print($"[CONFIG] Symbol: {SymbolName} | TF: {TimeFrame} | Account: {Account.Asset.Name}");
            Print($"[CONFIG] PipSize: {Symbol.PipSize} | PipValue: {Symbol.PipValue:F6} | TickSize: {Symbol.TickSize}");
            Print($"[CONFIG] VolumeMin: {Symbol.VolumeInUnitsMin} | VolumeMax: {Symbol.VolumeInUnitsMax} | Step: {Symbol.VolumeInUnitsStep}");
            Print("── Entry ──");
            Print($"[CONFIG] EntryMode: {EntryMode}");
            Print($"[CONFIG] NumberOfDownDays: {NumberOfDownDays}");
            Print($"[CONFIG] Timezone: {SelectedTimezone} → {tzDisplay}");
            Print($"[CONFIG] LateEntryTime: {LateEntryTime} | Window: {LateEntryWindowMinutes} min (LateSession mode only)");
            Print("── Filters ──");
            Print($"[CONFIG] TrendFilter: {(RequireTrendFilter ? "SMA" + TrendSmaPeriod : "DISABLED")}");
            Print($"[CONFIG] Require5SMA: {RequirePriceBelowSMA5}");
            Print($"[CONFIG] SkipMondays: {SkipMondays} | SkipFridays: {SkipFridays}");
            Print($"[CONFIG] MaxDailyLosses: {maxLossStr}");
            Print($"[CONFIG] MaxSpreadPips: {MaxSpreadPips}");
            Print("── Stop Loss ──");
            Print($"[CONFIG] StopLossMode: {StopLossMode}");
            Print($"[CONFIG] FixedPips: {FixedStopPips} | AtrPeriod: {AtrStopPeriod} | AtrMult: {AtrStopMultiplier}");
            Print($"[CONFIG] CandlePercent: {CandleStopPercent}% | SwingLookback: {SwingLowLookback}");
            Print($"[CONFIG] MinStopPips: {MinStopPips}");
            Print("── Exit ──");
            Print($"[CONFIG] ExitMode: {ExitMode} | TakeProfitR: {TakeProfitR} | MaxHoldBars: {MaxHoldBars}");
            Print("── Dynamic Stop ──");
            Print($"[CONFIG] EnableDynamicStop: {EnableDynamicStop} | Mode: {DynamicStopMode}");
            Print($"[CONFIG] BreakEvenTrigger: {BreakEvenTriggerR}R | BreakEvenExtra: {BreakEvenExtraPips} pips");
            Print($"[CONFIG] DynamicStepR: {DynamicStepR} | TrailDistanceR: {TrailDistanceR}");
            Print("── Risk ──");
            Print($"[CONFIG] RiskAmount: {RiskAmount} {RiskCurrencyMode}");
            Print("── Logging ──");
            Print($"[CONFIG] DetailedLogging: {EnableDetailedLogging} | BotLabel: {BotLabel}");
            Print("════════════════════════════════════════════════════════════════");
        }
    } // end class ThreeDownDaysBot
} // end namespace
