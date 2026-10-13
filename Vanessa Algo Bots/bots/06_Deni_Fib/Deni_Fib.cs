// Deni Fib cBot v1.0 (Vanessa Algo Bots)
// Deni Dantev's Fibonacci 0.618 strategy (The Trading Cafe), coded exactly as screened and frozen on 13 Oct 2026
// (research/scripts/screens/fib_tune.py; in-sample gold 2021-23 / GBPUSD 2012-23, out-of-sample 2024-26 passed).
// One-hour bars, both directions, run on XAUUSD and GBPUSD. Short side (the long side is the mirror image):
//   1. Trend top: a swing high (3 bars each side) that is the highest high of the previous 50 bars.
//   2. Break: within 39 bars of the top, a bar CLOSES below the last swing low of the 50 bars before the top
//      (cancelled if price trades above the top first).
//   3. Leg low L = the lowest low since the top. Sell limit at L + 0.618 x (top - L); it follows L down while waiting.
//      Stop = top + 0.1 x ATR (14-bar average range at the top). Target = L - 0.272 x (top - L).
//      If price is already above the entry when the break is confirmed, sell at market instead.
//   4. The order lives 30 bars after the break; cancelled earlier if price trades above the top.
//   5. Close after 120 bars if neither stop nor target is hit. One trade per symbol per direction at a time; after a
//      trade only tops formed after it closed count.
// Size: "Risk Per Trade" dollars from entry to stop. Attach to any chart (e.g. XAUUSD, 1 hour).
// Log lines: S| (bars loaded), A| (setup armed), O| (order placed / position opened), X| (setup dropped),
// H| (history at the end: id|label|symbol|side|entry time|close time|volume|entry|close|gross|swap|commission|net).
using System;
using System.Collections.Generic;
using System.Linq;
using cAlgo.API;
using cAlgo.API.Internals;

namespace cAlgo.Robots
{
    [Robot(AccessRights = AccessRights.None, TimeZone = TimeZones.UTC)]
    public class DeniFib : Robot
    {
        [Parameter("Symbols", Group = "Universe", DefaultValue = "XAUUSD,GBPUSD")]
        public string SymbolList { get; set; }

        [Parameter("Risk Per Trade ($)", Group = "Risk", DefaultValue = 100, MinValue = 1)]
        public double RiskDollars { get; set; }

        [Parameter("Trend Lookback (bars)", Group = "Rules", DefaultValue = 50, MinValue = 10)]
        public int Look { get; set; }

        [Parameter("Entry Retracement", Group = "Rules", DefaultValue = 0.618, MinValue = 0.3, MaxValue = 0.95)]
        public double Fib { get; set; }

        [Parameter("Target Extension", Group = "Rules", DefaultValue = 0.272, MinValue = 0)]
        public double Ext { get; set; }

        [Parameter("Stop Buffer x ATR", Group = "Rules", DefaultValue = 0.1, MinValue = 0)]
        public double StopBuf { get; set; }

        [Parameter("Order Life (bars)", Group = "Rules", DefaultValue = 30, MinValue = 1)]
        public int Wait { get; set; }

        [Parameter("Max Hold (bars)", Group = "Rules", DefaultValue = 120, MinValue = 1)]
        public int MaxHold { get; set; }

        [Parameter("Label", Group = "Other", DefaultValue = "DFB")]
        public string Label { get; set; }

        private const int K = 3;          // swing strength (bars each side)
        private const int BreakWithin = 39;

        private class Setup
        {
            public int H, Next, Brk = -1;
            public double Top, Swing, L, Atr;
        }

        private class Side
        {
            public int Dir;                // -1 = short side (tops), +1 = long side (bottoms)
            public List<Setup> Setups = new List<Setup>();
            public Setup Active;           // the setup that owns the pending order
            public PendingOrder Order;
            public int FillIdx = -1, LastExit = -1;
        }

        private class Book
        {
            public Symbol Sym;
            public Bars B;
            public Side Short = new Side { Dir = -1 }, Long = new Side { Dir = 1 };
        }

        private readonly List<Book> _books = new List<Book>();

        protected override void OnStart()
        {
            foreach (var raw in SymbolList.Split(','))
            {
                var name = raw.Trim();
                if (name.Length == 0) continue;
                Symbol sym;
                try { sym = Symbols.GetSymbol(name); } catch { sym = null; }
                if (sym == null) { Print("Symbol not found, skipped: {0}", name); continue; }
                var bars = MarketData.GetBars(TimeFrame.Hour, name);
                int guard = 0;
                while (bars.Count < Look + 60 && guard++ < 20)
                {
                    int before = bars.Count;
                    bars.LoadMoreHistory();
                    if (bars.Count == before) break;
                }
                Print("S|{0}|{1} hourly bars|first {2:yyyy-MM-dd}|$ per 1.0 price move per unit {3}|min units {4}", name, bars.Count,
                    bars.Count > 0 ? bars.OpenTimes[0] : DateTime.MinValue, sym.TickValue / sym.TickSize, sym.VolumeInUnitsMin);
                var b = new Book { Sym = sym, B = bars };
                _books.Add(b);
                bars.BarOpened += args => OnBar(b);
            }
            Positions.Opened += args =>
            {
                var p = args.Position;
                if (p.Label != Label) return;
                var b = _books.FirstOrDefault(x => x.Sym.Name == p.SymbolName);
                if (b == null) return;
                var s = p.TradeType == TradeType.Sell ? b.Short : b.Long;
                s.FillIdx = b.B.Count - 1;
                s.Setups.Clear(); s.Active = null; s.Order = null;
                Print("O|{0}|{1}|{2}|{3:yyyy-MM-dd HH:mm}|filled|{4}|{5}|{6}|{7}", p.Id, Label, p.SymbolName, p.EntryTime, p.TradeType,
                    p.VolumeInUnits, p.EntryPrice, p.StopLoss);
            };
            Positions.Closed += args =>
            {
                var p = args.Position;
                if (p.Label != Label) return;
                var b = _books.FirstOrDefault(x => x.Sym.Name == p.SymbolName);
                if (b == null) return;
                var s = p.TradeType == TradeType.Sell ? b.Short : b.Long;
                s.LastExit = b.B.Count - 1;
                s.FillIdx = -1;
            };
            Print("Deni Fib started: {0} symbols, risk ${1} per trade.", _books.Count, RiskDollars);
        }

        // Prices seen from the short side: the long side works on mirrored prices (high <-> -low).
        private static double Hi(Bars b, Side s, int i) => s.Dir < 0 ? b.HighPrices[i] : -b.LowPrices[i];
        private static double Lo(Bars b, Side s, int i) => s.Dir < 0 ? b.LowPrices[i] : -b.HighPrices[i];
        private static double Cl(Bars b, Side s, int i) => s.Dir < 0 ? b.ClosePrices[i] : -b.ClosePrices[i];
        private static double Real(Side s, double x) => s.Dir < 0 ? x : -x;

        private Position PosOf(Book b, Side s) =>
            Positions.FirstOrDefault(p => p.Label == Label && p.SymbolName == b.Sym.Name && p.TradeType == (s.Dir < 0 ? TradeType.Sell : TradeType.Buy));

        private void OnBar(Book b)
        {
            int t = b.B.Count - 2;          // the bar that has just closed
            if (t < Look + 2 * K + 1) return;
            foreach (var s in new[] { b.Short, b.Long }) Step(b, s, t);
        }

        private void Step(Book b, Side s, int t)
        {
            var bars = b.B;
            var pos = PosOf(b, s);
            if (pos != null)
            {
                if (s.FillIdx >= 0 && t >= s.FillIdx + MaxHold) ClosePosition(pos);
                return;
            }
            if (s.Order != null && !PendingOrders.Contains(s.Order)) { s.Order = null; s.Active = null; }

            // 1. new trend top, confirmed K bars after it
            int h = t - K;
            if (h > s.LastExit && h - Look >= 0)
            {
                double top = Hi(bars, s, h);
                bool fractal = true;
                for (int i = h - K; i <= h + K; i++) if (Hi(bars, s, i) > top) { fractal = false; break; }
                bool highest = true;
                for (int i = h - Look; i < h; i++) if (Hi(bars, s, i) > top) { highest = false; break; }
                if (fractal && highest)
                {
                    int j = -1;
                    for (int i = h - 1; i > h - Look; i--)
                    {
                        if (i - K < 0) break;
                        double lo = Lo(bars, s, i); bool f = true;
                        for (int q = i - K; q <= i + K; q++) if (Lo(bars, s, q) < lo) { f = false; break; }
                        if (f) { j = i; break; }
                    }
                    if (j >= 0)
                    {
                        double atr = 0;
                        for (int i = h - 13; i <= h; i++) atr += bars.HighPrices[i] - bars.LowPrices[i];
                        s.Setups.Add(new Setup { H = h, Next = h + 1, Top = top, Swing = Lo(bars, s, j), Atr = atr / 14 });
                    }
                }
            }

            // 2. walk every setup forward to the bar that has just closed
            foreach (var u in s.Setups.ToList())
            {
                bool drop = false; string why = "";
                for (int m = u.Next; m <= t && !drop; m++)
                {
                    if (u.Brk < 0)
                    {
                        if (m > u.H + BreakWithin) { drop = true; why = "no break"; break; }
                        if (Hi(bars, s, m) > u.Top) { drop = true; why = "new extreme before the break"; break; }
                        if (Cl(bars, s, m) < u.Swing)
                        {
                            u.Brk = m;
                            u.L = double.MaxValue;
                            for (int i = u.H; i <= m; i++) u.L = Math.Min(u.L, Lo(bars, s, i));
                            Print("A|{0}|{1}|{2:yyyy-MM-dd HH:mm}|top {3}|leg end {4}", b.Sym.Name, s.Dir < 0 ? "Sell" : "Buy",
                                bars.OpenTimes[m], Real(s, u.Top), Real(s, u.L));
                        }
                    }
                    else
                    {
                        if (m > u.Brk + Wait) { drop = true; why = "order expired"; break; }
                        if (Hi(bars, s, m) > u.Top) { drop = true; why = "price beyond the top"; break; }
                        u.L = Math.Min(u.L, Lo(bars, s, m));
                    }
                }
                u.Next = t + 1;
                if (drop)
                {
                    s.Setups.Remove(u);
                    if (u == s.Active)
                    {
                        if (s.Order != null && PendingOrders.Contains(s.Order)) CancelPendingOrder(s.Order);
                        s.Order = null; s.Active = null;
                        Print("X|{0}|{1}|{2:yyyy-MM-dd HH:mm}|{3}", b.Sym.Name, s.Dir < 0 ? "Sell" : "Buy", bars.OpenTimes[t], why);
                    }
                }
            }

            // 3. the earliest armed setup owns the (single) order for this side
            var a = s.Setups.Where(x => x.Brk >= 0).OrderBy(x => x.H).FirstOrDefault();
            if (a == null) return;
            if (s.Active != null && s.Active != a && s.Order != null && PendingOrders.Contains(s.Order)) { CancelPendingOrder(s.Order); s.Order = null; }
            s.Active = a;
            Place(b, s, a);
        }

        private void Place(Book b, Side s, Setup a)
        {
            var sym = b.Sym;
            double rng = a.Top - a.L;
            double entry = Real(s, a.L + Fib * rng), stop = Real(s, a.Top + StopBuf * a.Atr), target = Real(s, a.L - Ext * rng);
            double dist = Math.Abs(stop - entry);
            if (dist <= 0) return;
            double units = sym.NormalizeVolumeInUnits(RiskDollars / (dist * sym.TickValue / sym.TickSize), RoundingMode.Down);
            if (units < sym.VolumeInUnitsMin) { Print("X|{0}|size below minimum", sym.Name); return; }
            var tt = s.Dir < 0 ? TradeType.Sell : TradeType.Buy;

            // already beyond the entry: take it at market now (the screen fills at the next bar's open)
            double px = s.Dir < 0 ? sym.Bid : sym.Ask;
            bool beyond = s.Dir < 0 ? px >= entry : px <= entry;
            if (beyond && s.Order == null)
            {
                bool badPx = s.Dir < 0 ? (px >= stop || px <= target) : (px <= stop || px >= target);
                if (badPx) return;
                var r = ExecuteMarketOrder(tt, sym.Name, units, Label);
                if (!r.IsSuccessful) { Print("X|{0}|market order rejected: {1}", sym.Name, r.Error); return; }
                var m1 = r.Position.ModifyStopLossPrice(stop);
                var m2 = r.Position.ModifyTakeProfitPrice(target);
                if (m1 == null || !m1.IsSuccessful || m2 == null || !m2.IsSuccessful)
                {
                    Print("X|{0}|could not set stop/target, closed", sym.Name);
                    ClosePosition(r.Position);
                }
                return;
            }
            if (beyond) return;   // an existing order will fill on its own

            if (s.Order == null)
            {
                var r = PlaceLimitOrder(tt, sym.Name, units, entry, Label, stop, target, ProtectionType.Absolute);
                if (!r.IsSuccessful) { Print("X|{0}|limit order rejected: {1}", sym.Name, r.Error); return; }
                s.Order = r.PendingOrder;
                Print("O|{0}|{1}|{2:yyyy-MM-dd HH:mm}|limit placed|{3}|{4}|entry {5}|stop {6}|target {7}", sym.Name, Label,
                    Server.Time, tt, units, entry, stop, target);
            }
            else if (Math.Abs(s.Order.TargetPrice - entry) > sym.TickSize / 2 || Math.Abs(s.Order.VolumeInUnits - units) > 0)
            {
                ModifyPendingOrder(s.Order, entry, stop, target, ProtectionType.Absolute);
                if (Math.Abs(s.Order.VolumeInUnits - units) > 0) s.Order.ModifyVolume(units);
            }
        }

        protected override void OnStop()
        {
            foreach (var h in History.Where(h => h.Label == Label).OrderBy(h => h.ClosingTime))
                Print("H|{0}|{1}|{2}|{3}|{4:yyyy-MM-dd HH:mm}|{5:yyyy-MM-dd HH:mm}|{6}|{7}|{8}|{9:F2}|{10:F2}|{11:F2}|{12:F2}",
                    h.PositionId, h.Label, h.SymbolName, h.TradeType, h.EntryTime, h.ClosingTime, h.VolumeInUnits, h.EntryPrice,
                    h.ClosingPrice, h.GrossProfit, h.Swap, h.Commissions, h.NetProfit);
        }
    }
}
