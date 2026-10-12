// Stock Swing Scanner cBot v1.0 (Vanessa Algo Bots)
// Long-only daily swing bot after Clement Ang / Oliver Kell's price cycle: wedge pop, tight base, breakout.
// Rules are pre-registered in research/STOCK_SWING_TEST_PLAN.md. Attach to ANY chart: the bot reads the daily bars of
// every symbol in "Symbols" itself. Each time a stock's new daily bar opens, it judges the bar that just closed,
// cancels that stock's unfilled order from the day before, manages open positions and, if the setup is there,
// places a buy-stop just above the base day's high with the stop just below its low.
// Log lines for analysis: O| (position opened), P| (partial close), X| (signal skipped), H| (history at the end).
using System;
using System.Collections.Generic;
using System.Linq;
using cAlgo.API;
using cAlgo.API.Indicators;
using cAlgo.API.Internals;

namespace cAlgo.Robots
{
    [Robot(AccessRights = AccessRights.None, TimeZone = TimeZones.UTC)]
    public class StockSwingScanner : Robot
    {
        [Parameter("Symbols", Group = "Universe",
            DefaultValue = "AAPL,AMZN,BA,BABA,BAC,CSCO,CVX,DIS,META,FDX,GE,GM,GOOG,IBM,INTC,JNJ,JPM,KO,MCD,MSFT,NFLX,NVDA,PFE,QCOM,RACE,T,TSLA,V,WMT,XOM,ZM,RTX,LMT,PLTR,AMD,AVGO,SBUX,MSTR,GME,NKE,ARM,SNOW,ASML,AZN,BRK.B,SPCX")]
        public string SymbolList { get; set; }

        [Parameter("Benchmark Symbol", Group = "Universe", DefaultValue = "US100.cash")]
        public string BenchmarkName { get; set; }

        [Parameter("Risk Per Trade ($)", Group = "Risk", DefaultValue = 300, MinValue = 1)]
        public double RiskAmount { get; set; }

        [Parameter("Max Open Positions", Group = "Risk", DefaultValue = 4, MinValue = 1)]
        public int MaxPositions { get; set; }

        [Parameter("Min ADR %", Group = "Setup", DefaultValue = 3.0)]
        public double MinAdrPct { get; set; }

        [Parameter("Wedge Pop Volume x 50d Avg", Group = "Setup", DefaultValue = 1.5)]
        public double PopVolMult { get; set; }

        [Parameter("Wedge Pop Lookback (days)", Group = "Setup", DefaultValue = 15)]
        public int PopLookback { get; set; }

        [Parameter("Base Length (days)", Group = "Setup", DefaultValue = 5)]
        public int BaseDays { get; set; }

        [Parameter("Base Max Range x ADR", Group = "Setup", DefaultValue = 1.5)]
        public double BaseRangeMult { get; set; }

        [Parameter("RS Within % Of 50d High", Group = "Setup", DefaultValue = 5.0)]
        public double RsTolerancePct { get; set; }

        [Parameter("Max Stop x ADR", Group = "Setup", DefaultValue = 1.0)]
        public double MaxStopAdr { get; set; }

        [Parameter("First Partial At x ADR", Group = "Exits", DefaultValue = 2.0)]
        public double Partial1Adr { get; set; }

        [Parameter("Extended: ATRs Above 50d", Group = "Exits", DefaultValue = 10.0)]
        public double ExtendedAtr { get; set; }

        [Parameter("Label", Group = "Other", DefaultValue = "SWG")]
        public string Label { get; set; }

        private class Book
        {
            public Symbol Sym;
            public Bars Daily;
            public ExponentialMovingAverage Ema10, Ema20;
            public SimpleMovingAverage Sma50, Sma200;
            public AverageTrueRange Atr14;
        }

        private class PosState
        {
            public double OrigVolume, Risk, AdrPrice, Entry;
            public bool Part1, Part2;
        }

        private readonly Dictionary<string, Book> _books = new Dictionary<string, Book>();
        private readonly Dictionary<int, PosState> _state = new Dictionary<int, PosState>();
        private readonly Dictionary<string, PosState> _pendingInfo = new Dictionary<string, PosState>();
        private Bars _bench;

        protected override void OnStart()
        {
            _bench = MarketData.GetBars(TimeFrame.Daily, BenchmarkName);
            LoadHistory(_bench, 260);
            foreach (var raw in SymbolList.Split(','))
            {
                var name = raw.Trim();
                if (name.Length == 0) continue;
                Symbol sym;
                try { sym = Symbols.GetSymbol(name); } catch { sym = null; }
                if (sym == null) { Print("Symbol not found, skipped: {0}", name); continue; }
                var bars = MarketData.GetBars(TimeFrame.Daily, name);
                LoadHistory(bars, 260);
                var b = new Book
                {
                    Sym = sym, Daily = bars,
                    Ema10 = Indicators.ExponentialMovingAverage(bars.ClosePrices, 10),
                    Ema20 = Indicators.ExponentialMovingAverage(bars.ClosePrices, 20),
                    Sma50 = Indicators.SimpleMovingAverage(bars.ClosePrices, 50),
                    Sma200 = Indicators.SimpleMovingAverage(bars.ClosePrices, 200),
                    Atr14 = Indicators.AverageTrueRange(bars, 14, MovingAverageType.Simple)
                };
                _books[name] = b;
                bars.BarOpened += args => OnDailyBar(b);
            }
            foreach (var p in MyPositions)
            {
                Book b;
                if (!_books.TryGetValue(p.SymbolName, out b)) continue;
                _state[p.Id] = new PosState { OrigVolume = p.VolumeInUnits, Entry = p.EntryPrice,
                    AdrPrice = AdrPct(b, b.Daily.Count - 2) * b.Daily.ClosePrices[b.Daily.Count - 2],
                    Risk = p.StopLoss.HasValue ? (p.EntryPrice - p.StopLoss.Value) * p.VolumeInUnits : RiskAmount };
                Print("Resumed managing {0} position {1}", p.SymbolName, p.Id);
            }
            Positions.Opened += OnOpened;
            Timer.Start(TimeSpan.FromMinutes(1));
            Print("Stock Swing Scanner started: {0} symbols, risk ${1} per trade, max {2} positions.", _books.Count, RiskAmount, MaxPositions);
        }

        private void LoadHistory(Bars bars, int need)
        {
            int guard = 0;
            while (bars.Count < need && guard++ < 20)
            {
                int before = bars.Count;
                bars.LoadMoreHistory();
                if (bars.Count == before) break;
            }
        }

        private IEnumerable<Position> MyPositions => Positions.Where(p => p.Label == Label);
        private IEnumerable<PendingOrder> MyOrders => PendingOrders.Where(o => o.Label == Label);

        // ---------- daily decision for one stock (the bar at Count-2 has just closed) ----------
        private void OnDailyBar(Book b)
        {
            var name = b.Sym.Name;
            foreach (var o in MyOrders.Where(o => o.SymbolName == name).ToList())
                CancelPendingOrder(o);

            int t = b.Daily.Count - 2;
            if (t < 210) return;
            ManageOnClose(b, t);

            if (MyPositions.Any(p => p.SymbolName == name)) return;
            if (MyPositions.Count() + MyOrders.Count() >= MaxPositions) return;
            double adr;
            string why = Setup(b, t, out adr);
            if (why != null) return;

            double high = b.Daily.HighPrices[t], low = b.Daily.LowPrices[t], close = b.Daily.ClosePrices[t];
            double entry = b.Sym.Ask > high * 1.001 ? 0 : Math.Round(high * 1.001, b.Sym.Digits);
            if (entry <= 0) { Print("X|{0}|{1:yyyy-MM-dd}|gapped above trigger", name, b.Daily.OpenTimes[t]); return; }
            double stop = Math.Round(low * 0.999, b.Sym.Digits);
            double dist = entry - stop;
            if (dist <= 0 || dist > MaxStopAdr * adr * close)
            {
                Print("X|{0}|{1:yyyy-MM-dd}|stop too wide {2:F2} vs ADR {3:F2}", name, b.Daily.OpenTimes[t], dist, adr * close);
                return;
            }
            double units = b.Sym.NormalizeVolumeInUnits(RiskAmount / dist, RoundingMode.Down);
            if (units < b.Sym.VolumeInUnitsMin) return;
            double slPips = dist / b.Sym.PipSize;
            var res = PlaceStopOrder(TradeType.Buy, name, units, entry, Label, slPips, null, Server.Time.Date.AddHours(23));
            if (res.IsSuccessful)
                _pendingInfo[name] = new PosState { OrigVolume = units, Risk = units * dist, AdrPrice = adr * close, Entry = entry };
        }

        // Returns null when the setup is valid; otherwise the reason it is not.
        private string Setup(Book b, int t, out double adr)
        {
            var d = b.Daily;
            adr = 0;
            double close = d.ClosePrices[t];
            if (!(close > b.Sma200.Result[t] && b.Sma200.Result[t] > b.Sma200.Result[t - 20])) return "trend";
            adr = AdrPct(b, t);
            if (adr * 100 < MinAdrPct) return "adr";

            bool pop = false;
            for (int j = t - PopLookback + 1; j <= t && !pop; j++)
            {
                if (!(d.ClosePrices[j] > b.Ema10.Result[j] && d.ClosePrices[j] > b.Ema20.Result[j])) continue;
                bool wasBelow = false;
                for (int k = j - 5; k < j; k++) if (d.ClosePrices[k] < b.Ema20.Result[k]) wasBelow = true;
                if (!wasBelow) continue;
                if (d.TickVolumes[j] >= PopVolMult * AvgVol(d, j - 1, 50)) pop = true;
            }
            if (!pop) return "no wedge pop";

            double hi = double.MinValue, lo = double.MaxValue, vb = 0;
            for (int i = t - BaseDays + 1; i <= t; i++)
            {
                hi = Math.Max(hi, d.HighPrices[i]); lo = Math.Min(lo, d.LowPrices[i]); vb += d.TickVolumes[i];
                if (d.ClosePrices[i] <= b.Ema20.Result[i]) return "base below 20 EMA";
            }
            if (hi - lo > BaseRangeMult * adr * close) return "base too wide";
            if (vb / BaseDays >= AvgVol(d, t, 50)) return "base volume not drying up";

            double rs = Ratio(d, t), rsMax = 0;
            for (int i = t - 49; i <= t; i++) rsMax = Math.Max(rsMax, Ratio(d, i));
            if (rs <= 0 || rs < rsMax * (1 - RsTolerancePct / 100)) return "relative strength";
            return null;
        }

        private static double AdrPct(Book b, int t)
        {
            double a = 0;
            for (int i = t - 19; i <= t; i++) a += b.Daily.HighPrices[i] / b.Daily.LowPrices[i] - 1;
            return a / 20;
        }

        private static double AvgVol(Bars d, int end, int n)
        {
            double s = 0;
            for (int i = end - n + 1; i <= end; i++) s += d.TickVolumes[i];
            return s / n;
        }

        private double Ratio(Bars d, int i)
        {
            int bi = _bench.OpenTimes.GetIndexByTime(d.OpenTimes[i].Date.AddHours(19));
            if (bi < 0) return 0;
            double bc = _bench.ClosePrices[bi];
            return bc > 0 ? d.ClosePrices[i] / bc : 0;
        }

        // ---------- exits judged on the daily close ----------
        private void ManageOnClose(Book b, int t)
        {
            foreach (var p in MyPositions.Where(p => p.SymbolName == b.Sym.Name).ToList())
            {
                PosState s;
                if (!_state.TryGetValue(p.Id, out s)) continue;
                double close = b.Daily.ClosePrices[t];
                if (close < b.Ema10.Result[t])
                {
                    ClosePosition(p);
                    continue;
                }
                if (!s.Part2 && close > b.Sma50.Result[t] + ExtendedAtr * b.Atr14.Result[t])
                {
                    PartialClose(p, s, "extended");
                    s.Part2 = true;
                }
            }
        }

        // ---------- first partial at +2x ADR, checked every minute ----------
        protected override void OnTimer()
        {
            foreach (var p in MyPositions.ToList())
            {
                PosState s;
                if (!_state.TryGetValue(p.Id, out s) || s.Part1 || s.AdrPrice <= 0) continue;
                var sym = Symbols.GetSymbol(p.SymbolName);
                if (sym.Bid >= p.EntryPrice + Partial1Adr * s.AdrPrice)
                {
                    PartialClose(p, s, "2xADR");
                    s.Part1 = true;
                    if (Positions.FirstOrDefault(x => x.Id == p.Id) != null)
                        p.ModifyStopLossPrice(p.EntryPrice);
                }
            }
        }

        private void PartialClose(Position p, PosState s, string why)
        {
            var sym = Symbols.GetSymbol(p.SymbolName);
            double part = sym.NormalizeVolumeInUnits(s.OrigVolume / 3, RoundingMode.Down);
            if (part < sym.VolumeInUnitsMin) return;
            if (part >= p.VolumeInUnits) { ClosePosition(p); return; }
            Print("P|{0}|{1}|{2:yyyy-MM-dd}|{3}|{4}|{5:F2}", p.Id, p.SymbolName, Server.Time, why, part, sym.Bid);
            ClosePosition(p, part);
        }

        private void OnOpened(PositionOpenedEventArgs args)
        {
            var p = args.Position;
            if (p.Label != Label) return;
            PosState s;
            if (!_pendingInfo.TryGetValue(p.SymbolName, out s))
                s = new PosState { OrigVolume = p.VolumeInUnits, Risk = RiskAmount, AdrPrice = 0 };
            _pendingInfo.Remove(p.SymbolName);
            s.OrigVolume = p.VolumeInUnits;
            double sl = p.StopLoss ?? 0;
            if (sl > 0) s.Risk = (p.EntryPrice - sl) * p.VolumeInUnits;
            _state[p.Id] = s;
            Print("O|{0}|{1}|{2:yyyy-MM-dd}|{3}|{4:F2}|{5:F2}|{6:F2}", p.Id, p.SymbolName, p.EntryTime, p.VolumeInUnits, p.EntryPrice, sl, s.Risk);
        }

        protected override void OnStop()
        {
            // H|positionId|symbol|entry time|close time|volume|entry|close|gross|swap|commission|net
            foreach (var h in History.Where(h => h.Label == Label).OrderBy(h => h.ClosingTime))
                Print("H|{0}|{1}|{2:yyyy-MM-dd}|{3:yyyy-MM-dd}|{4}|{5:F2}|{6:F2}|{7:F2}|{8:F2}|{9:F2}|{10:F2}",
                    h.PositionId, h.SymbolName, h.EntryTime, h.ClosingTime, h.VolumeInUnits, h.EntryPrice, h.ClosingPrice,
                    h.GrossProfit, h.Swap, h.Commissions, h.NetProfit);
        }
    }
}
