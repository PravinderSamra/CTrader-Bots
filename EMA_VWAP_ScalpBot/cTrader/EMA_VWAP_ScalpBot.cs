using System;
using cAlgo.API;
using cAlgo.API.Indicators;
using cAlgo.API.Internals;

namespace EmaVwapBot
{
    /// <summary>
    /// EMA + VWAP Scalping Bot — cTrader cBot implementation.
    /// Build Specification v1.0 (June 2025).
    ///
    /// Architecture: runs on 1M primary timeframe to enable precision 1M entry.
    /// Accesses 5M and 1H secondary series for signal and bias evaluation.
    /// All signal evaluation uses completed bars only (Last(1) for secondary series,
    /// Last(0) for primary since OnBar fires on bar close in cTrader).
    ///
    /// Stop loss is placed as a server-side StopOrder at entry time.
    /// </summary>
    [Robot(TimeZone = TimeZones.UTC, AccessRights = AccessRights.None)]
    public class EmaVwapScalpBot : Robot
    {
        // ── Parameters — Section 11 (externalised for MCP/UI access) ─────────

        [Parameter("Instrument Type", DefaultValue = "GER40")]
        public string InstrumentName { get; set; }

        [Parameter("EMA Fast Period (5M)", DefaultValue = 9, MinValue = 7, MaxValue = 13, Step = 1)]
        public int EmaFastPeriod { get; set; }

        [Parameter("EMA Slow Period (5M)", DefaultValue = 21, MinValue = 18, MaxValue = 26, Step = 1)]
        public int EmaSlowPeriod { get; set; }

        // Fixed — not subject to optimisation (spec §11)
        [Parameter("EMA Bias Period (1H) [FIXED=21]", DefaultValue = 21)]
        public int EmaBiasPeriod { get; set; }

        [Parameter("ATR Period (5M)", DefaultValue = 14, MinValue = 10, MaxValue = 18, Step = 2)]
        public int AtrPeriod { get; set; }

        [Parameter("ATR Multiplier (SL)", DefaultValue = 1.5, MinValue = 1.0, MaxValue = 2.5, Step = 0.25)]
        public double AtrMultiplier { get; set; }

        [Parameter("Min Body Filter (%)", DefaultValue = 40, MinValue = 30, MaxValue = 60, Step = 10)]
        public int MinBodyFilterPct { get; set; }

        [Parameter("Max Entry Distance (x ATR)", DefaultValue = 1.0, MinValue = 0.5, MaxValue = 1.5, Step = 0.25)]
        public double MaxEntryDistanceAtr { get; set; }

        [Parameter("Max Trades Per Day", DefaultValue = 3, MinValue = 2, MaxValue = 4, Step = 1)]
        public int MaxTradesPerDay { get; set; }

        [Parameter("Risk Per Trade (%)", DefaultValue = 1.0)]
        public double RiskPerTradePct { get; set; }

        [Parameter("Max Daily Loss (%)", DefaultValue = 3.0)]
        public double MaxDailyLossPct { get; set; }

        [Parameter("Kill Switch Drawdown (%)", DefaultValue = 8.0)]
        public double KillSwitchDrawdownPct { get; set; }

        [Parameter("Breakeven Buffer (pts)", DefaultValue = 1.0)]
        public double BreakevenBuffer { get; set; }

        [Parameter("Enable News Filter", DefaultValue = false)]
        public bool EnableNewsFilter { get; set; }

        // ── Secondary data series ─────────────────────────────────────────────

        private Bars _bars5m;
        private Bars _bars1h;
        private int  _prev5mCount;
        private int  _prev1hCount;

        // ── Indicators ────────────────────────────────────────────────────────

        private ExponentialMovingAverage _ema5mFast;
        private ExponentialMovingAverage _ema5mSlow;
        private ExponentialMovingAverage _ema1hBias;
        private AverageTrueRange         _atr5m;

        // ── Strategy components ───────────────────────────────────────────────

        private VwapCalculator    _vwap;
        private SignalEngine      _signal;
        private RiskManager       _risk;
        private SessionGate       _session;
        private DailyLimitTracker _dailyTracker;

        // ── Trade state ───────────────────────────────────────────────────────

        private bool   _tp1Hit;
        private double _tp1Price;
        private double _tp2Price;
        private string _tradeLabel;
        private int    _dailyTradeSeq;

        // ── Lifecycle ─────────────────────────────────────────────────────────

        protected override void OnStart()
        {
            // Validate EMA constraint: Slow must be >= Fast + 5
            if (EmaSlowPeriod < EmaFastPeriod + 5)
            {
                Print($"EVWAP: Invalid — EMA Slow ({EmaSlowPeriod}) must be >= EMA Fast ({EmaFastPeriod}) + 5. Bot stopping.");
                Stop();
                return;
            }

            // Load secondary timeframe data
            _bars5m = MarketData.GetBars(TimeFrame.Minute5);
            _bars1h = MarketData.GetBars(TimeFrame.Hour);
            _prev5mCount = _bars5m.Count;
            _prev1hCount = _bars1h.Count;

            // Build indicators on 5M series
            _ema5mFast = Indicators.ExponentialMovingAverage(_bars5m.ClosePrices, EmaFastPeriod);
            _ema5mSlow = Indicators.ExponentialMovingAverage(_bars5m.ClosePrices, EmaSlowPeriod);
            _ema1hBias = Indicators.ExponentialMovingAverage(_bars1h.ClosePrices, EmaBiasPeriod);
            _atr5m     = Indicators.AverageTrueRange(AtrPeriod, MovingAverageType.Exponential, _bars5m);

            // Initialise strategy components
            _vwap  = new VwapCalculator();
            _signal = new SignalEngine(MinBodyFilterPct, MaxEntryDistanceAtr);
            _risk   = new RiskManager(RiskPerTradePct, AtrMultiplier);
            _session = new SessionGate(ParseInstrument(InstrumentName));
            _dailyTracker = new DailyLimitTracker(MaxTradesPerDay, MaxDailyLossPct, KillSwitchDrawdownPct);
            _dailyTracker.InitialisePeak(Account.Equity);

            Print($"EVWAP: Started on {Symbol.Name} | EMA {EmaFastPeriod}/{EmaSlowPeriod} | ATR {AtrPeriod}×{AtrMultiplier} | Risk {RiskPerTradePct}%");
        }

        protected override void OnBar()
        {
            // ── Detect bar completions on secondary timeframes ─────────────────
            bool new5mBar = _bars5m.Count > _prev5mCount;
            bool new1hBar = _bars1h.Count > _prev1hCount;
            _prev5mCount = _bars5m.Count;
            _prev1hCount = _bars1h.Count;

            // ── Update daily tracker ──────────────────────────────────────────
            _dailyTracker.Update(Server.Time, Account.Equity);

            // ── Update VWAP with current 1M bar (completed bar = Bars.Last(0)) ─
            var bar1m = Bars.Last(0);
            _vwap.Update(Server.Time, bar1m.High, bar1m.Low, bar1m.Close, bar1m.TickVolume);

            // ── Kill switch check ─────────────────────────────────────────────
            if (_dailyTracker.KillSwitchTripped)
            {
                if (Positions.Count > 0)
                    CloseAllPositions("KILL_SWITCH");
                return;
            }

            // ── Session end: close all positions ─────────────────────────────
            if (_session.IsPastSessionClose(Server.Time))
            {
                if (Positions.Count > 0)
                    CloseAllPositions("SESSION_END");
                return;
            }

            // ── In-trade exit management (on every 5M bar) ────────────────────
            if (new5mBar && Positions.Count > 0)
                ManageOpenPosition();

            // ── 1M precision entry (when awaiting signal confirmation) ─────────
            if (_signal.State == EntryState.AwaitingEntry)
            {
                bool entered = _signal.Check1mEntry(bar1m.Close, bar1m.Open);
                if (entered)
                    ExecuteEntry(bar1m.Open);
            }

            // ── 5M signal evaluation ──────────────────────────────────────────
            if (new5mBar && _signal.State == EntryState.Idle && Positions.Count == 0)
            {
                if (!_vwap.IsValid) return;

                // Use Last(1) for secondary series (last COMPLETED bar)
                int idx5m = _bars5m.Count - 2;
                int idx1h = _bars1h.Count - 2;

                if (idx5m < EmaSlowPeriod + 5 || idx1h < EmaBiasPeriod + 2) return;

                double close5m = _bars5m.ClosePrices[idx5m];
                double open5m  = _bars5m.OpenPrices[idx5m];
                double high5m  = _bars5m.HighPrices[idx5m];
                double low5m   = _bars5m.LowPrices[idx5m];
                double ema9    = _ema5mFast.Result[idx5m];
                double ema21   = _ema5mSlow.Result[idx5m];
                double close1h = _bars1h.ClosePrices[idx1h];
                double ema1h   = _ema1hBias.Result[idx1h];
                double atr     = _atr5m.Result[idx5m];

                bool inSession   = _session.IsInTradingWindow(Server.Time);
                bool canOpen     = _dailyTracker.CanOpenNewTrade(Account.Equity);

                var dir = _signal.Evaluate5mSignal(
                    close5m, open5m, high5m, low5m,
                    ema9, ema21, _vwap.Vwap,
                    close1h, ema1h,
                    inSession, canOpen);

                if (dir != SignalDirection.None)
                {
                    Print($"EVWAP: 5M {dir} signal | Close={close5m:F1} VWAP={_vwap.Vwap:F1} EMA9={ema9:F1} EMA21={ema21:F1} ATR={atr:F1}");
                    _signal.ActivatePendingEntry(dir, _vwap.Vwap, atr);

                    // Record TP levels from VWAP SD bands (set at signal time)
                    if (dir == SignalDirection.Long)
                    {
                        _tp1Price = _vwap.Sd1Upper;
                        _tp2Price = _vwap.Sd2Upper;
                    }
                    else
                    {
                        _tp1Price = _vwap.Sd1Lower;
                        _tp2Price = _vwap.Sd2Lower;
                    }
                }
            }
        }

        // ── Entry execution ───────────────────────────────────────────────────

        private void ExecuteEntry(double entryPrice)
        {
            var dir = _signal.PendingDirection;
            int idx5m = _bars5m.Count - 2;  // last completed 5M bar
            double atr = _atr5m.Result[idx5m];

            double slPrice = dir == SignalDirection.Long
                ? _risk.CalculateLongStopLoss(entryPrice, atr)
                : _risk.CalculateShortStopLoss(entryPrice, atr);

            if (double.IsNaN(slPrice))
            {
                Print($"EVWAP: Entry skipped — stop distance outside valid range (ATR={atr:F1})");
                _signal.Reset();
                return;
            }

            long volume = _risk.CalculateVolume(Account.Equity, entryPrice, slPrice);
            if (volume <= 0)
            {
                _signal.Reset();
                return;
            }

            _dailyTradeSeq++;
            _tradeLabel = $"EVWAP_{Symbol.Name}_{Server.Time:yyyyMMdd}_{_dailyTradeSeq:D3}";

            var tradeType = dir == SignalDirection.Long ? TradeType.Buy : TradeType.Sell;
            var result    = ExecuteMarketOrder(tradeType, Symbol.Name, volume, _tradeLabel,
                                               Math.Abs(entryPrice - slPrice), null);

            if (!result.IsSuccessful)
            {
                Print($"EVWAP: Order failed — {result.Error}");
                _signal.Reset();
                return;
            }

            _tp1Hit = false;
            _dailyTracker.RegisterTrade();

            Print($"EVWAP: ENTERED {dir} | Entry={entryPrice:F1} SL={slPrice:F1} TP1={_tp1Price:F1} TP2={_tp2Price:F1} Vol={volume} Label={_tradeLabel}");
        }

        // ── Position management ───────────────────────────────────────────────

        private void ManageOpenPosition()
        {
            var pos = GetManagedPosition();
            if (pos == null) return;

            bool isLong   = pos.TradeType == TradeType.Buy;
            double curBid = Symbol.Bid;
            double curAsk = Symbol.Ask;
            double price  = isLong ? curBid : curAsk;

            int idx5m = _bars5m.Count - 2;
            double ema9  = _ema5mFast.Result[idx5m];
            double vwap  = _vwap.Vwap;

            // Priority 1: Hard SL — handled server-side by cTrader (no code action needed)

            // Priority 2: TP1 — VWAP ±1SD
            if (!_tp1Hit)
            {
                bool tp1Hit = isLong ? price >= _tp1Price : price <= _tp1Price;
                if (tp1Hit)
                {
                    // Close 50% of position
                    long halfVol = pos.VolumeInUnits / 2;
                    if (halfVol >= 100)
                    {
                        ClosePosition(pos, halfVol);
                        // Move stop to breakeven on remaining
                        double beStop = isLong
                            ? pos.EntryPrice + BreakevenBuffer
                            : pos.EntryPrice - BreakevenBuffer;
                        ModifyPosition(pos, beStop, null);
                        _tp1Hit = true;
                        Print($"EVWAP: TP1 hit | Closed 50% at {price:F1} | Stop moved to BE {beStop:F1}");
                    }
                }
                return; // Only process one exit level per bar
            }

            // Priority 3: TP2 — VWAP ±2SD
            bool tp2Hit = isLong ? price >= _tp2Price : price <= _tp2Price;
            if (tp2Hit)
            {
                ClosePosition(pos);
                _signal.Reset();
                Print($"EVWAP: TP2 hit | Closed 100% at {price:F1}");
                return;
            }

            // Priority 4: EMA/VWAP Reversion (5M candle close triggers this)
            var bar5m = _bars5m.Last(1); // last completed 5M bar
            bool reverted = isLong
                ? bar5m.Close < ema9 || bar5m.Close < vwap
                : bar5m.Close > ema9 || bar5m.Close > vwap;

            if (reverted)
            {
                ClosePosition(pos);
                _signal.Reset();
                Print($"EVWAP: Reversion exit | 5M Close={bar5m.Close:F1} EMA9={ema9:F1} VWAP={vwap:F1}");
            }
        }

        // ── Utilities ─────────────────────────────────────────────────────────

        private Position GetManagedPosition()
        {
            foreach (var pos in Positions)
            {
                if (pos.Label != null && pos.Label.StartsWith("EVWAP_") && pos.SymbolName == Symbol.Name)
                    return pos;
            }
            return null;
        }

        private void CloseAllPositions(string reason)
        {
            foreach (var pos in Positions)
            {
                if (pos.SymbolName == Symbol.Name)
                    ClosePosition(pos);
            }
            _signal.Reset();
            Print($"EVWAP: All positions closed — {reason}");
        }

        private static InstrumentType ParseInstrument(string name)
        {
            return name.ToUpper().Contains("US500") || name.ToUpper().Contains("SPX")
                ? InstrumentType.US500
                : InstrumentType.GER40;
        }

        protected override void OnStop()
        {
            Print("EVWAP: Bot stopped.");
        }
    }
}
