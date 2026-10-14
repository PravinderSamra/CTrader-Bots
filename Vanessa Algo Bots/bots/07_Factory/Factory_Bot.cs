// Factory Bot v1.0 (Vanessa Algo Bots)
// Runs any daily Strategy Factory strategy from its settings.
// Same rules on every market in the Symbols list.
// Signals: the daily bar that has just closed.
// Orders: Order Delay minutes after the new daily bar
// opens, only while that market is trading.
// One position per market.
// Defaults = Factory candidate A (14 Oct 2026):
// buy an index that closes below the 20-day Bollinger
// band at 2.5 standard deviations, close 5 bars later,
// disaster stop 10 x ATR(20). Size: Risk Per R dollars
// per 2 x ATR(20) of price movement.
// Entries: BB, PB, SOUP, DOWN, BRK, MAX, NR, TOM.
// Filters: None, Trend, Calm.
// Exits: TIME, STOPTGT, CHAN, MR, MAEXIT.
// Details: research/factory/factory_d1.py and STRATEGY.md
// Log: S| bars, O| open, C| rule close, X| skipped,
// H| history at the end.
using System;
using System.Collections.Generic;
using System.Linq;
using cAlgo.API;
using cAlgo.API.Indicators;
using cAlgo.API.Internals;

namespace cAlgo.Robots
{
    public enum FacEntry { BB, PB, SOUP, DOWN, BRK, MAX, NR, TOM }
    public enum FacFilter { None, Trend, Calm }
    public enum FacExit { TIME, STOPTGT, CHAN, MR, MAEXIT }
    public enum FacSide { Long, Short }

    [Robot(AccessRights = AccessRights.None, TimeZone = TimeZones.UTC)]
    public class FactoryBot : Robot
    {
        private const string DefaultSymbols =
            "US500.cash,US100.cash,US30.cash,US2000.cash,"
            + "GER40.cash,UK100.cash,FRA40.cash,EU50.cash,"
            + "AUS200.cash,HK50.cash";

        [Parameter("Symbols", Group = "Universe",
            DefaultValue = DefaultSymbols)]
        public string SymbolList { get; set; }

        [Parameter("Entry", Group = "Strategy", DefaultValue = FacEntry.BB)]
        public FacEntry Entry { get; set; }

        [Parameter("Entry Param", Group = "Strategy", DefaultValue = 2.5)]
        public double EntryP { get; set; }

        [Parameter("Entry Param 2 (MAX slow)", Group = "Strategy", DefaultValue = 0)]
        public double EntryP2 { get; set; }

        [Parameter("Filter", Group = "Strategy", DefaultValue = FacFilter.None)]
        public FacFilter Filter { get; set; }

        [Parameter("Exit", Group = "Strategy", DefaultValue = FacExit.TIME)]
        public FacExit Exit { get; set; }

        [Parameter("Exit Param", Group = "Strategy", DefaultValue = 5)]
        public double ExitP { get; set; }

        [Parameter("Exit Param 2 (target x ATR)", Group = "Strategy", DefaultValue = 0)]
        public double ExitP2 { get; set; }

        [Parameter("Direction", Group = "Strategy", DefaultValue = FacSide.Long)]
        public FacSide Direction { get; set; }

        [Parameter("Risk Per R ($, R = 2 x ATR)", Group = "Risk", DefaultValue = 200,
            MinValue = 1)]
        public double RiskPerR { get; set; }

        [Parameter("Disaster Stop x ATR(20)", Group = "Risk", DefaultValue = 10,
            MinValue = 1)]
        public double DisasterAtr { get; set; }

        [Parameter("Order Delay (minutes)", Group = "Other", DefaultValue = 60,
            MinValue = 1)]
        public int DelayMinutes { get; set; }

        [Parameter("Label", Group = "Other", DefaultValue = "FAC-A")]
        public string Label { get; set; }

        private class Book
        {
            public Symbol Sym;
            public Bars D;
            public SimpleMovingAverage Sma5, Sma20, Sma200, SmaP, SmaFast, SmaSlow;
            public StandardDeviation Sd20;
            public RelativeStrengthIndex Rsi2;
            public AverageTrueRange Atr;
            public DateTime LastTick = DateTime.MinValue, OpenSince = DateTime.MinValue;
            public int EntryBar = -1;
        }

        private class Order
        {
            public DateTime Due;
            public Book B;
            public int T;
            public bool Close;
        }

        private readonly List<Book> _books = new List<Book>();
        private readonly List<Order> _queue = new List<Order>();
        private int Side => Direction == FacSide.Long ? 1 : -1;

        protected override void OnStart()
        {
            foreach (var raw in SymbolList.Split(','))
            {
                var name = raw.Trim();
                if (name.Length == 0) continue;
                Symbol sym;
                try { sym = Symbols.GetSymbol(name); } catch { sym = null; }
                if (sym == null) { Print("Symbol not found, skipped: {0}",
                    name); continue; }
                var bars = MarketData.GetBars(TimeFrame.Daily, name);
                int guard = 0;
                while (bars.Count < 320 && guard++ < 20)
                {
                    int before = bars.Count;
                    bars.LoadMoreHistory();
                    if (bars.Count == before) break;
                }
                Print("S|{0}|{1} daily bars|first {2:yyyy-MM-dd}", name, bars.Count,
                    bars.Count > 0 ? bars.OpenTimes[0] : DateTime.MinValue);
                var b = new Book
                {
                    Sym = sym, D = bars,
                    Sma5 = Indicators.SimpleMovingAverage(bars.ClosePrices, 5),
                    Sma20 = Indicators.SimpleMovingAverage(bars.ClosePrices, 20),
                    Sma200 = Indicators.SimpleMovingAverage(bars.ClosePrices, 200),
                    SmaP = Indicators.SimpleMovingAverage(bars.ClosePrices,
                        Math.Max(2, (int)ExitP)),
                    SmaFast = Indicators.SimpleMovingAverage(bars.ClosePrices,
                        Math.Max(2, (int)EntryP)),
                    SmaSlow = Indicators.SimpleMovingAverage(bars.ClosePrices,
                        Math.Max(3, (int)EntryP2)),
                    Sd20 = Indicators.StandardDeviation(bars.ClosePrices, 20,
                        MovingAverageType.Simple),
                    Rsi2 = Indicators.RelativeStrengthIndex(bars.ClosePrices, 2),
                    Atr = Indicators.AverageTrueRange(bars, 20,
                        MovingAverageType.Simple)
                };
                _books.Add(b);
                sym.Tick += args =>
                {
                    var now = Server.Time;
                    if (now - b.LastTick > TimeSpan.FromMinutes(30)) b.OpenSince = now;
                    b.LastTick = now;
                };
                bars.BarOpened += args => OnDailyBar(b);
            }
            Timer.Start(TimeSpan.FromMinutes(1));
            Print("Factory Bot started: {0} {1} {2} {3} {4} {5} {6}",
                Label, Entry, EntryP, Filter, Exit, ExitP, _books.Count);
        }

        private Position PosOf(Book b) => Positions.FirstOrDefault(
            p => p.Label == Label && p.SymbolName == b.Sym.Name);

        private double MaxClose(Book b, int t, int k)
        {
            double m = double.MinValue;
            for (int i = t - k; i < t; i++) m = Math.Max(m, b.D.ClosePrices[i]);
            return m;
        }

        private double MinClose(Book b, int t, int k)
        {
            double m = double.MaxValue;
            for (int i = t - k; i < t; i++) m = Math.Min(m, b.D.ClosePrices[i]);
            return m;
        }

        private bool EntrySignal(Book b, int t)
        {
            var d = b.D; var C = d.ClosePrices;
            var H = d.HighPrices; var L = d.LowPrices;
            int s = Side; int p = (int)EntryP;
            switch (Entry)
            {
                case FacEntry.BB:
                    return s > 0
                        ? C[t] < b.Sma20.Result[t] - EntryP * b.Sd20.Result[t]
                            : C[t] > b.Sma20.Result[t] + EntryP * b.Sd20.Result[t];
                case FacEntry.PB:
                    return s > 0 ? C[t] > b.Sma200.Result[t]
                        && b.Rsi2.Result[t] < EntryP : C[t] < b.Sma200.Result[t]
                            && b.Rsi2.Result[t] > 100 - EntryP;
                case FacEntry.SOUP:
                {
                    double lo = double.MaxValue, hi = double.MinValue;
                    for (int i = t - p; i < t; i++) { lo = Math.Min(lo,
                        L[i]); hi = Math.Max(hi, H[i]); }
                    return s > 0 ? L[t] < lo && C[t] > lo : H[t] > hi && C[t] < hi;
                }
                case FacEntry.DOWN:
                    for (int i = t - p + 1; i <= t; i++) if (s > 0
                        ? !(C[i] < C[i - 1]) : !(C[i] > C[i - 1])) return false;
                    return true;
                case FacEntry.BRK:
                    return s > 0 ? C[t] > MaxClose(b, t, p) : C[t] < MinClose(b, t, p);
                case FacEntry.MAX:
                {
                    bool up = b.SmaFast.Result[t] > b.SmaSlow.Result[t],
                        prev = b.SmaFast.Result[t - 1] > b.SmaSlow.Result[t - 1];
                    return s > 0 ? up && !prev : !up && prev;
                }
                case FacEntry.NR:
                {
                    double r = H[t - 1] - L[t - 1];
                    for (int i = t - p; i < t; i++) if (H[i] - L[i] < r) return false;
                    return s > 0 ? C[t] > H[t - 1] : C[t] < L[t - 1];
                }
                case FacEntry.TOM:
                {
                    var day = Session(d, t); int left = 0;
                    for (var x = day.AddDays(1); x.Month == day.Month; x = x.AddDays(1))
                        if (x.DayOfWeek != DayOfWeek.Saturday
                            && x.DayOfWeek != DayOfWeek.Sunday) left++;
                    return left == p;
                }
            }
            return false;
        }

        private bool FilterOk(Book b, int t)
        {
            var C = b.D.ClosePrices;
            switch (Filter)
            {
                case FacFilter.Trend: return Side > 0 ? C[t] > b.Sma200.Result[t]
                    : C[t] < b.Sma200.Result[t];
                case FacFilter.Calm:
                {
                    var w = new List<double>();
                    for (int i = t - 99; i <= t; i++) w.Add(b.Atr.Result[i]);
                    w.Sort();
                    return b.Atr.Result[t] < (w[49] + w[50]) / 2;
                }
            }
            return true;
        }

        private bool ExitSignal(Book b, int t)
        {
            var C = b.D.ClosePrices; int s = Side; int held = t - b.EntryBar;
            switch (Exit)
            {
                case FacExit.TIME: return held >= (int)ExitP;
                case FacExit.STOPTGT: return held >= 20;
                case FacExit.CHAN: return held >= 120 || (s > 0 ? C[t] < MinClose(b,
                    t, (int)ExitP) : C[t] > MaxClose(b, t, (int)ExitP));
                case FacExit.MR: return held >= 10 || (s > 0
                    ? C[t] > b.Sma5.Result[t] : C[t] < b.Sma5.Result[t]);
                case FacExit.MAEXIT: return held >= 120 || (s > 0
                    ? C[t] < b.SmaP.Result[t] : C[t] > b.SmaP.Result[t]);
            }
            return false;
        }

        private static DateTime Session(Bars d,
            int i) => d.OpenTimes[i].AddHours(5).Date;

        private void OnDailyBar(Book b)
        {
            int t = b.D.Count - 2;
            if (t < 210) return;
            var due = b.D.OpenTimes[t + 1].AddMinutes(DelayMinutes);
            var pos = PosOf(b);
            if (pos != null)
            {
                if (b.EntryBar < 0) b.EntryBar = Math.Max(0,
                    b.D.OpenTimes.GetIndexByTime(pos.EntryTime) - 1);
                if (ExitSignal(b, t)) _queue.Add(new Order { Due = due, B = b, T = t,
                    Close = true });
                return;
            }
            if (_queue.Any(q => q.B == b && !q.Close)) return;
            if (EntrySignal(b, t) && FilterOk(b, t)) _queue.Add(new Order { Due = due,
                B = b, T = t });
        }

        // ---------------- execution ----------------
        private bool Tradable(Book b) =>
            Server.Time - b.LastTick <= TimeSpan.FromMinutes(2)
                && Server.Time - b.OpenSince >= TimeSpan.FromMinutes(15);

        private double MoneyPerUnit(Symbol s) => s.TickValue / s.TickSize;

        private void Open(Order o)
        {
            var b = o.B; var s = b.Sym;
            if (PosOf(b) != null) return;
            double atr = b.Atr.Result[o.T];
            if (!(atr > 0)) return;
            var tt = Side > 0 ? TradeType.Buy : TradeType.Sell;
            double price = Side > 0 ? s.Ask : s.Bid;
            double raw = RiskPerR / (2 * atr * MoneyPerUnit(s));
            double units = s.NormalizeVolumeInUnits(raw, RoundingMode.Down);
            if (units < s.VolumeInUnitsMin)
            {
                Print("X|{0}|{1}|size_below_minimum", Label, s.Name);
                return;
            }
            double stopDist = DisasterAtr * atr; double? tgt = null;
            if (Exit == FacExit.STOPTGT) { stopDist = Math.Min(stopDist,
                ExitP * atr); if (ExitP2 > 0) tgt = price + Side * ExitP2 * atr; }
            else if (Exit == FacExit.CHAN
                || Exit == FacExit.MAEXIT) stopDist = Math.Min(stopDist, 2 * atr);
            else if (Exit == FacExit.MR) stopDist = Math.Min(stopDist, 3 * atr);
            double sl = price - Side * stopDist;
            var r = ExecuteMarketOrder(tt, s.Name, units, Label);
            if (!r.IsSuccessful) { Print("X|{0}|{1}|order rejected: {2}", Label,
                s.Name, r.Error); return; }
            var p = r.Position;
            var m1 = p.ModifyStopLossPrice(sl);
            var m2 = tgt.HasValue ? p.ModifyTakeProfitPrice(tgt) : m1;
            if (m1 == null || !m1.IsSuccessful || m2 == null || !m2.IsSuccessful)
            {
                Print("X|{0}|{1}|could not set stop/target, closed", Label, s.Name);
                ClosePosition(p);
                return;
            }
            b.EntryBar = o.T;
            Print("O|{0}|{1}|{2}|{3:yyyy-MM-dd HH:mm}|{4}|{5}|{6}|SL {7}|TP {8}",
                p.Id, Label, s.Name, p.EntryTime, p.TradeType,
                p.VolumeInUnits, p.EntryPrice, p.StopLoss, p.TakeProfit);
        }

        protected override void OnTimer()
        {
            foreach (var o in _queue.Where(x => x.Due <= Server.Time
                && Tradable(x.B)).ToList())
            {
                _queue.Remove(o);
                if (o.Close)
                {
                    var p = PosOf(o.B);
                    if (p != null) { Print("C|{0}|{1}|{2:yyyy-MM-dd HH:mm}|exit rule",
                        Label, o.B.Sym.Name, Server.Time); ClosePosition(p); }
                    o.B.EntryBar = -1;
                    continue;
                }
                Open(o);
            }
        }

        protected override void OnStop()
        {
            var hist = History.Where(h => h.Label == Label)
                .OrderBy(h => h.ClosingTime);
            foreach (var h in hist)
                Print("H|{0}|{1}|{2}|{3}|{4:yyyy-MM-dd HH:mm}|"
                    + "{5:yyyy-MM-dd HH:mm}|{6}|{7}|{8}|"
                    + "{9:F2}|{10:F2}|{11:F2}|{12:F2}",
                    h.PositionId, h.Label, h.SymbolName, h.TradeType, h.EntryTime,
                        h.ClosingTime, h.VolumeInUnits, h.EntryPrice,
                    h.ClosingPrice, h.GrossProfit, h.Swap, h.Commissions, h.NetProfit);
        }
    }
}
