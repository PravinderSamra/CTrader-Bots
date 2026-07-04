// =============================================================================
// Gap Fade Bot — fades the daily opening gap back to the prior-day close.
// Single compilable .cs file for cTrader Automate. Runs on an M15 chart.
//
// Strategy (mirrors Gap-Retrace-Research Phase 1/2 backtest exactly):
//   * At the first M15 bar of a new session, gap = sessionOpen - priorDayClose.
//   * Qualify only if MinGapPct <= |gap%| <= MaxGapPct.
//   * Bias: gap UP -> fade SHORT ; gap DOWN -> fade LONG (target = prior-day close).
//   * Skip WarmupBars, then arm; ENTER on the first M15 bar that CLOSES back
//     through the session open in the fade direction (momentum rejection).
//   * Stop just beyond the session extreme so far (+ StopBufferPct of the gap).
//   * Take-profit = prior-day close (the fill). One trade per session.
//   * Optional flat-by time and a max-wait window to arm the trigger.
//
// This is the un-optimised, positive-expectancy rule from the research folder;
// see research/Phase2_* for stats. Test on DEMO before any live use.
// =============================================================================

using System;
using cAlgo.API;
using cAlgo.API.Internals;

namespace cAlgo.Robots
{
    public enum GapRiskMode
    {
        PercentOfEquity,
        FixedAmount
    }

    [Robot(TimeZone = TimeZones.UTC, AccessRights = AccessRights.None)]
    public class GapFadeBot : Robot
    {
        // ---- Gap qualification --------------------------------------------
        // Research default 0.25%: on 2y GER40 the weekday-only, gap>=0.25% fade was
        // +0.25R / 59% win, positive in 6/8 quarters; the >=0.15% all-gaps version
        // was only breakeven after costs. See research/Phase2_*.
        [Parameter("Min Gap %", Group = "Gap Filter", DefaultValue = 0.25, MinValue = 0.01)]
        public double MinGapPct { get; set; }

        [Parameter("Max Gap %", Group = "Gap Filter", DefaultValue = 1.0, MinValue = 0.05)]
        public double MaxGapPct { get; set; }

        // Weekend/holiday gaps (prior trading day >1 calendar day back) are bigger,
        // news-driven, fill less and overshoot -> the mechanical fade LOSES on them
        // (2y: -0.12R). Default: skip them.
        [Parameter("Skip Weekend/Holiday Gaps", Group = "Gap Filter", DefaultValue = true)]
        public bool SkipWeekendGaps { get; set; }

        // ---- Entry timing --------------------------------------------------
        [Parameter("Warmup Bars", Group = "Entry", DefaultValue = 2, MinValue = 0, MaxValue = 20)]
        public int WarmupBars { get; set; }

        [Parameter("Max Wait Bars", Group = "Entry", DefaultValue = 16, MinValue = 1)]
        public int MaxWaitBars { get; set; }

        [Parameter("Flatten Hour (UTC, -1=off)", Group = "Entry", DefaultValue = -1, MinValue = -1, MaxValue = 23)]
        public int FlattenHourUtc { get; set; }

        // ---- Risk & sizing -------------------------------------------------
        [Parameter("Risk Mode", Group = "Risk & Sizing", DefaultValue = GapRiskMode.PercentOfEquity)]
        public GapRiskMode RiskMode { get; set; }

        [Parameter("Risk Percent", Group = "Risk & Sizing", DefaultValue = 0.5, MinValue = 0.01)]
        public double RiskPercent { get; set; }

        [Parameter("Risk Fixed Amount", Group = "Risk & Sizing", DefaultValue = 100, MinValue = 0.01)]
        public double RiskFixedAmount { get; set; }

        [Parameter("Stop Buffer % of Gap", Group = "Risk & Sizing", DefaultValue = 10, MinValue = 0)]
        public double StopBufferPct { get; set; }

        [Parameter("Max Volume Cap (lots, 0=off)", Group = "Risk & Sizing", DefaultValue = 0, MinValue = 0)]
        public double MaxLotCap { get; set; }

        // ---- Take-profit ---------------------------------------------------
        [Parameter("TP2 into range (R, 0=off)", Group = "Take Profit", DefaultValue = 0, MinValue = 0)]
        public double Tp2RMultiple { get; set; }

        [Parameter("TP1 close fraction %", Group = "Take Profit", DefaultValue = 100, MinValue = 1, MaxValue = 100)]
        public double Tp1FractionPct { get; set; }

        // ---- Diagnostics ---------------------------------------------------
        [Parameter("Enable Chart Labels", Group = "Diagnostics", DefaultValue = true)]
        public bool EnableChartLabels { get; set; }

        [Parameter("Enable Logging", Group = "Diagnostics", DefaultValue = true)]
        public bool EnableLogging { get; set; }

        // ---- State ---------------------------------------------------------
        private const string Label = "GAP-FADE";
        private Bars _daily;
        private int _sessionDay = int.MinValue;   // Server-time day index of current session
        private double _priorClose, _priorHigh, _priorLow, _sessionOpen, _gap;
        private bool _up, _qualified, _tradedThisSession;
        private int _barsIntoSession;
        private double _sessionExtreme;

        protected override void OnStart()
        {
            _daily = MarketData.GetBars(TimeFrame.Daily);
            if (TimeFrame != TimeFrame.Minute15)
                Print("WARNING: GapFadeBot is designed for an M15 chart; current TF = {0}.", TimeFrame);
            Print("GapFadeBot started on {0}. MinGap={1}% MaxGap={2}% Warmup={3} MaxWait={4}.",
                  SymbolName, MinGapPct, MaxGapPct, WarmupBars, MaxWaitBars);
        }

        protected override void OnBar()
        {
            // Work on the just-closed bar.
            int idx = Bars.Count - 2;
            if (idx < 1) return;
            var closed = Bars[idx];
            int day = DayKey(closed.OpenTime);

            if (day != _sessionDay)
                StartNewSession(day, closed);
            else
                ProcessSessionBar(closed);

            if (FlattenHourUtc >= 0 && Server.Time.Hour == FlattenHourUtc)
                FlattenAll("flatten-hour");
        }

        private int DayKey(DateTime t)
        {
            return t.Year * 400 + t.DayOfYear;
        }

        private void StartNewSession(int day, Bar firstBar)
        {
            _sessionDay = day;
            _qualified = _tradedThisSession = false;
            _barsIntoSession = 0;

            // Prior *completed* daily bar (index Count-2 is the current forming day on Daily,
            // so we walk back to the last fully-closed daily bar strictly before this session).
            int di = PriorDailyIndex(firstBar.OpenTime);
            if (di < 0) return;
            _priorClose = _daily.ClosePrices[di];
            _priorHigh = _daily.HighPrices[di];
            _priorLow = _daily.LowPrices[di];

            // Weekend/holiday filter: >1 calendar day between prior daily bar and this session.
            bool weekendGap = (firstBar.OpenTime.Date - _daily.OpenTimes[di].Date).TotalDays > 1.5;
            if (SkipWeekendGaps && weekendGap)
            {
                if (EnableLogging)
                    Print("Skip weekend/holiday gap on {0:yyyy-MM-dd}.", firstBar.OpenTime);
                return;
            }
            _sessionOpen = firstBar.Open;
            _gap = _sessionOpen - _priorClose;
            if (_priorClose <= 0 || _gap == 0) return;

            double gpct = _gap / _priorClose * 100.0;
            _up = _gap > 0;
            _sessionExtreme = _up ? firstBar.High : firstBar.Low;

            if (Math.Abs(gpct) >= MinGapPct && Math.Abs(gpct) <= MaxGapPct)
            {
                _qualified = true;
                if (EnableLogging)
                    Print("New session {0:yyyy-MM-dd}: gap {1:+0.00;-0.00}% ({2:0.0} pts) -> fade {3}. priorClose={4}",
                          firstBar.OpenTime, gpct, _gap, _up ? "SHORT" : "LONG", _priorClose);
                if (EnableChartLabels)
                {
                    Chart.DrawHorizontalLine("gapFill", _priorClose, Color.DodgerBlue, 2, LineStyle.LinesDots);
                    Chart.DrawHorizontalLine("pdh", _priorHigh, Color.Gray, 1, LineStyle.Dots);
                    Chart.DrawHorizontalLine("pdl", _priorLow, Color.Gray, 1, LineStyle.Dots);
                }
            }
        }

        private int PriorDailyIndex(DateTime sessionOpenTime)
        {
            for (int i = _daily.Count - 1; i >= 0; i--)
            {
                if (_daily.OpenTimes[i] < sessionOpenTime.Date)
                    return i;
            }
            return -1;
        }

        private void ProcessSessionBar(Bar b)
        {
            if (!_qualified || _tradedThisSession) return;
            _barsIntoSession++;
            _sessionExtreme = _up ? Math.Max(_sessionExtreme, b.High) : Math.Min(_sessionExtreme, b.Low);

            if (_barsIntoSession < WarmupBars) return;
            if (_barsIntoSession > WarmupBars + MaxWaitBars) { _qualified = false; return; }

            // Trigger: close back through the session open in the fade direction.
            bool trigger = _up ? (b.Close < _sessionOpen) : (b.Close > _sessionOpen);
            if (!trigger) return;

            if (Positions.Find(Label, SymbolName) != null) return;
            EnterTrade(b.Close);
            _tradedThisSession = true;
        }

        private void EnterTrade(double entry)
        {
            double buf = Math.Abs(_gap) * (StopBufferPct / 100.0);
            double sl = _up ? _sessionExtreme + buf : _sessionExtreme - buf;
            double tp = _priorClose;
            double riskDist = Math.Abs(entry - sl);
            if (riskDist <= 0) { if (EnableLogging) Print("Skip: non-positive risk distance."); return; }

            // Reward sanity: skip if the fill is on the wrong side / already passed.
            bool tpValid = _up ? (tp < entry) : (tp > entry);
            if (!tpValid) { if (EnableLogging) Print("Skip: prior-close already filled at trigger."); return; }

            long volume = ComputeVolume(riskDist);
            if (volume <= 0) { if (EnableLogging) Print("Skip: volume rounds to zero."); return; }

            var side = _up ? TradeType.Sell : TradeType.Buy;
            double slPips = riskDist / Symbol.PipSize;
            double tpPips = Math.Abs(entry - tp) / Symbol.PipSize;

            var r = ExecuteMarketOrder(side, SymbolName, volume, Label, slPips, tpPips);
            if (r.IsSuccessful)
            {
                if (EnableLogging)
                    Print("ENTER {0} {1} vol={2} entry~{3} SL={4} TP={5} (risk {6:0.0} pips)",
                          side, SymbolName, volume, entry, sl, tp, slPips);
                if (EnableChartLabels)
                    Chart.DrawIcon("entry" + Server.Time.Ticks,
                        _up ? ChartIconType.DownArrow : ChartIconType.UpArrow,
                        Server.Time, entry, _up ? Color.OrangeRed : Color.LimeGreen);
            }
            else if (EnableLogging)
            {
                Print("Order failed: {0}", r.Error);
            }
        }

        private long ComputeVolume(double riskDistancePrice)
        {
            double riskCash = RiskMode == GapRiskMode.PercentOfEquity
                ? Account.Equity * (RiskPercent / 100.0)
                : RiskFixedAmount;

            // value per 1 unit over the stop distance = riskDistancePrice * (pipValue / pipSize)
            double perUnitRisk = (riskDistancePrice / Symbol.PipSize) * Symbol.PipValue;
            if (perUnitRisk <= 0) return 0;
            double units = riskCash / perUnitRisk;
            double volume = Symbol.NormalizeVolumeInUnits(units, RoundingMode.Down);

            if (MaxLotCap > 0)
            {
                double capUnits = Symbol.QuantityToVolumeInUnits(MaxLotCap);
                if (volume > capUnits)
                    volume = Symbol.NormalizeVolumeInUnits(capUnits, RoundingMode.Down);
            }
            if (volume < Symbol.VolumeInUnitsMin) return 0;
            return (long)volume;
        }

        private void FlattenAll(string reason)
        {
            foreach (var p in Positions)
            {
                if (p.Label == Label && p.SymbolName == SymbolName)
                {
                    if (EnableLogging) Print("Flatten {0} ({1})", p.Id, reason);
                    ClosePosition(p);
                }
            }
        }

        protected override void OnStop()
        {
            Print("GapFadeBot stopped.");
        }
    }
}
