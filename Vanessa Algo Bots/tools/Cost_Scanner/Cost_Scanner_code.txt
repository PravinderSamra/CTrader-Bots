// Cost Scanner v1.0 (Vanessa Algo Bots). Never trades.
// Measures what each FTMO market really costs. Run as a BACKTEST on TICK DATA over about
// one month (attach to any chart). At the end the log prints one line per market:
// C|symbol|price|median spread|cheapest-hours spread|spread %|daily range %|
//   spread as % of the daily range|swap long %/yr|swap short %/yr|commission
// Spread is sampled at the first tick of each minute, Monday-Friday.
// "Cheapest hours" = median of the 6 cheapest UTC hours (the market's own busy session).
using System;
using System.Collections.Generic;
using System.Linq;
using cAlgo.API;
using cAlgo.API.Indicators;
using cAlgo.API.Internals;

namespace cAlgo.Robots
{
    [Robot(AccessRights = AccessRights.None, TimeZone = TimeZones.UTC)]
    public class CostScanner : Robot
    {
        private const string Default =
            "US500.cash,US100.cash,US30.cash,US2000.cash,GER40.cash,UK100.cash,"
            + "FRA40.cash,EU50.cash,JP225.cash,AUS200.cash,HK50.cash,XAUUSD,XAGUSD,"
            + "USOIL.cash,UKOIL.cash,NATGAS.cash,EURUSD,GBPUSD,USDJPY,AUDUSD,"
            + "USDCAD,USDCHF,NZDUSD,EURJPY,GBPJPY,BTCUSD,ETHUSD";

        [Parameter("Symbols", DefaultValue = Default)]
        public string List { get; set; }

        private class Book
        {
            public Symbol S;
            public Bars D;
            public DateTime LastMinute = DateTime.MinValue;
            public List<double>[] ByHour = new List<double>[24];
        }

        private readonly List<Book> _books = new List<Book>();

        protected override void OnStart()
        {
            foreach (var raw in List.Split(','))
            {
                var name = raw.Trim();
                if (name.Length == 0) continue;
                Symbol s;
                try { s = Symbols.GetSymbol(name); } catch { s = null; }
                if (s == null) { Print("not found: {0}", name); continue; }
                var b = new Book { S = s, D = MarketData.GetBars(TimeFrame.Daily, name) };
                for (int h = 0; h < 24; h++) b.ByHour[h] = new List<double>();
                _books.Add(b);
                s.Tick += args => Sample(b);
            }
            Print("Cost Scanner started: {0} markets", _books.Count);
        }

        private void Sample(Book b)
        {
            var t = Server.Time;
            var m = new DateTime(t.Year, t.Month, t.Day, t.Hour, t.Minute, 0);
            if (m == b.LastMinute) return;
            b.LastMinute = m;
            if (t.DayOfWeek == DayOfWeek.Saturday || t.DayOfWeek == DayOfWeek.Sunday) return;
            double sp = b.S.Ask - b.S.Bid;
            if (sp >= 0) b.ByHour[t.Hour].Add(sp);
        }

        private static double Median(List<double> v)
        {
            if (v.Count == 0) return double.NaN;
            var a = v.OrderBy(x => x).ToList();
            return a[a.Count / 2];
        }

        private double SwapPctYear(Symbol s, double swap, double price)
        {
            if (s.SwapCalculationType == SymbolSwapCalculationType.Percentage) return swap;
            return swap * s.PipSize * 365 / price * 100;
        }

        protected override void OnStop()
        {
            Print("C|symbol|price|median spread|cheapest-hours spread|spread %|daily range %|"
                + "spread % of range|swap long %/yr|swap short %/yr|commission");
            foreach (var b in _books)
            {
                var all = b.ByHour.SelectMany(x => x).ToList();
                if (all.Count == 0) { Print("C|{0}|no ticks", b.S.Name); continue; }
                double med = Median(all);
                var hours = Enumerable.Range(0, 24).Where(h => b.ByHour[h].Count > 30)
                    .Select(h => Median(b.ByHour[h])).OrderBy(x => x).Take(6).ToList();
                double cheap = hours.Count > 0 ? hours.Average() : med;
                double px = (b.S.Bid + b.S.Ask) / 2;
                int n = b.D.Count; double rng = 0; int k = 0;
                for (int i = Math.Max(0, n - 21); i < n - 1; i++)
                { rng += b.D.HighPrices[i] - b.D.LowPrices[i]; k++; }
                rng = k > 0 ? rng / k : double.NaN;
                Print("C|{0}|{1}|{2}|{3}|{4:F4}%|{5:F2}%|{6:F1}%|{7:F2}|{8:F2}|{9} {10}",
                    b.S.Name, px, med, cheap, cheap / px * 100, rng / px * 100,
                    cheap / rng * 100, SwapPctYear(b.S, b.S.SwapLong, px),
                    SwapPctYear(b.S, b.S.SwapShort, px), b.S.Commission, b.S.CommissionType);
            }
        }
    }
}
