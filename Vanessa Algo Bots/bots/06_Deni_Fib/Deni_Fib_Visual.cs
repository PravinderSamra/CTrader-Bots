// Deni Fib Visual v1.0 (Vanessa Algo Bots) - chart indicator, draws only, never trades.
// Shows on the chart what the Deni Fib cBot sees, using the same rules (see STRATEGY.md):
//   blue line   = the trend 'wave' line through the last rising swing lows (sell setups) / falling swing highs (buy setups),
//                 with the number of waves written on it;
//   grey dashed = the swing level that has to break; a small arrow marks the break candle;
//   Fibonacci   = cTrader's own Fibonacci tool from the trend top to the leg end (0, 61.8 and 100 levels shown);
//   orange      = the 0.618 entry, red = stop, green = the -0.272 target, for as long as the order lives;
//   a label     = what happened: WIN / LOSS / TIMED OUT / NOT FILLED.
// Add it to an XAUUSD or GBPUSD 1-hour chart (the bot's timeframe). It redraws once per new bar.
using System;
using System.Collections.Generic;
using System.Linq;
using cAlgo.API;

namespace cAlgo
{
    [Indicator(IsOverlay = true, AccessRights = AccessRights.None, TimeZone = TimeZones.UTC)]
    public class DeniFibVisual : Indicator
    {
        [Parameter("Bars To Draw", DefaultValue = 1500, MinValue = 100)]
        public int Span { get; set; }

        [Parameter("Trend Lookback (bars)", Group = "Rules (same as the bot)", DefaultValue = 50, MinValue = 10)]
        public int Look { get; set; }

        [Parameter("Entry Retracement", Group = "Rules (same as the bot)", DefaultValue = 0.618)]
        public double Fib { get; set; }

        [Parameter("Target Extension", Group = "Rules (same as the bot)", DefaultValue = 0.272)]
        public double Ext { get; set; }

        [Parameter("Stop Buffer x ATR", Group = "Rules (same as the bot)", DefaultValue = 0.1)]
        public double StopBuf { get; set; }

        [Parameter("Order Life (bars)", Group = "Rules (same as the bot)", DefaultValue = 30)]
        public int Wait { get; set; }

        [Parameter("Max Hold (bars)", Group = "Rules (same as the bot)", DefaultValue = 120)]
        public int MaxHold { get; set; }

        [Parameter("Show Unfilled Setups", DefaultValue = true)]
        public bool ShowUnfilled { get; set; }

        private const int K = 3, BreakWithin = 39;
        private const string Tag = "DFBV_";
        private readonly List<string> _names = new List<string>();
        private int _drawnAt = -1;

        protected override void Initialize() { }

        public override void Calculate(int index)
        {
            if (!IsLastBar || index == _drawnAt) return;
            _drawnAt = index;
            foreach (var n in _names) Chart.RemoveObject(n);
            _names.Clear();
            int last = index - 1;                     // last closed bar
            int from = Math.Max(Look + 20, last - Span);
            DrawSide(-1, from, last);
            DrawSide(1, from, last);
        }

        private double Hi(int dir, int i) => dir < 0 ? Bars.HighPrices[i] : -Bars.LowPrices[i];
        private double Lo(int dir, int i) => dir < 0 ? Bars.LowPrices[i] : -Bars.HighPrices[i];
        private double Cl(int dir, int i) => dir < 0 ? Bars.ClosePrices[i] : -Bars.ClosePrices[i];
        private double Op(int dir, int i) => dir < 0 ? Bars.OpenPrices[i] : -Bars.OpenPrices[i];
        private static double Real(int dir, double x) => dir < 0 ? x : -x;
        private DateTime T(int i) => Bars.OpenTimes[Math.Min(i, Bars.Count - 1)];

        private bool SwingHi(int dir, int i, int last)
        {
            if (i - K < 0 || i + K > last) return false;
            for (int q = i - K; q <= i + K; q++) if (Hi(dir, q) > Hi(dir, i)) return false;
            return true;
        }

        private bool SwingLo(int dir, int i, int last)
        {
            if (i - K < 0 || i + K > last) return false;
            for (int q = i - K; q <= i + K; q++) if (Lo(dir, q) < Lo(dir, i)) return false;
            return true;
        }

        private void DrawSide(int dir, int from, int last)
        {
            int busy = -1, n = 0;
            for (int h = from; h <= last - K; h++)
            {
                if (h <= busy || !SwingHi(dir, h, last)) continue;
                double top = Hi(dir, h);
                bool highest = true;
                for (int i = h - Look; i < h; i++) if (Hi(dir, i) > top) { highest = false; break; }
                if (!highest) continue;
                var lows = new List<int>();
                for (int i = h - Look + 1; i < h; i++) if (SwingLo(dir, i, last)) lows.Add(i);
                if (lows.Count == 0) continue;
                double swing = Lo(dir, lows[lows.Count - 1]);

                int brk = -1;
                for (int m = h + 1; m <= Math.Min(h + BreakWithin, last); m++)
                {
                    if (Hi(dir, m) > top) break;
                    if (Cl(dir, m) < swing) { brk = m; break; }
                }
                if (brk < 0) continue;

                double L = double.MaxValue; int lIdx = h;
                for (int i = h; i <= brk; i++) if (Lo(dir, i) < L) { L = Lo(dir, i); lIdx = i; }
                int fill = -1; double entry = 0; int endWait = Math.Min(brk + Wait, last);
                for (int m = brk + 1; m <= endWait; m++)
                {
                    if (Hi(dir, m) > top) { endWait = m; break; }
                    if (Hi(dir, m) >= L + Fib * (top - L)) { fill = m; break; }
                    if (Lo(dir, m) < L) { L = Lo(dir, m); lIdx = m; }
                }
                if (fill < 0 && !ShowUnfilled) continue;

                double atr = 0;
                for (int i = h - 13; i <= h; i++) atr += Bars.HighPrices[i] - Bars.LowPrices[i];
                atr /= 14;
                double rng = top - L;
                entry = Math.Max(L + Fib * rng, fill >= 0 ? Op(dir, fill) : 0);
                if (fill < 0) entry = L + Fib * rng;
                double stop = top + StopBuf * atr, target = L - Ext * rng;

                // outcome (same as the screen: stop checked first on each bar)
                string result = "NOT FILLED"; int end = endWait;
                if (fill >= 0)
                {
                    result = "OPEN"; end = Math.Min(fill + MaxHold, last);
                    if (Hi(dir, fill) >= stop) { result = "LOSS"; end = fill; }
                    else
                        for (int m = fill + 1; m <= Math.Min(fill + MaxHold, last); m++)
                        {
                            if (Hi(dir, m) >= stop) { result = "LOSS"; end = m; break; }
                            if (Lo(dir, m) <= target) { result = "WIN"; end = m; break; }
                            if (m == fill + MaxHold) { result = "TIMED OUT"; end = m; }
                        }
                    busy = end;
                }

                string id = Tag + (dir < 0 ? "S" : "B") + (n++) + "_";
                var side = dir < 0 ? "Sell" : "Buy";
                var main = dir < 0 ? Color.FromHex("#E0605A") : Color.FromHex("#3BAA6E");

                // wave line: the consecutive rising swing lows (in mirrored terms) leading into the top
                var wave = new List<int>();
                for (int k = lows.Count - 1; k >= 0; k--)
                {
                    if (wave.Count == 0 || Lo(dir, lows[k]) < Lo(dir, wave[0])) wave.Insert(0, lows[k]);
                    else break;
                }
                if (wave.Count >= 2)
                {
                    int a = wave[Math.Max(0, wave.Count - 3)], b = wave[wave.Count - 1];
                    double ya = Real(dir, Lo(dir, a)), yb = Real(dir, Lo(dir, b));
                    double slope = (yb - ya) / (b - a);
                    Add(Chart.DrawTrendLine(id + "wave", T(a), ya, T(brk), ya + slope * (brk - a), Color.FromHex("#4A90D9"), 2, LineStyle.Solid));
                    Add(Chart.DrawText(id + "wavetxt", wave.Count + " waves", T(a), ya, Color.FromHex("#4A90D9")));
                }
                // the swing level that broke
                Add(Chart.DrawTrendLine(id + "swing", T(lows[lows.Count - 1]), Real(dir, swing), T(brk), Real(dir, swing), Color.Gray, 1, LineStyle.LinesDots));
                Add(Chart.DrawIcon(id + "brk", dir < 0 ? ChartIconType.DownArrow : ChartIconType.UpArrow, T(brk), Real(dir, Cl(dir, brk)), main));
                // Fibonacci from the top to the leg end
                var fib = Chart.DrawFibonacciRetracement(id + "fib", T(h), Real(dir, top), T(lIdx), Real(dir, L), Color.FromHex("#9B8AC4"), 1, LineStyle.Dots);
                foreach (var lv in fib.FibonacciLevels)
                {
                    double p = lv.Percent;
                    lv.IsVisible = Near(p, 0) || Near(p, 61.8) || Near(p, 0.618) || Near(p, 100) || Near(p, 1);
                }
                Add(fib);
                // entry, stop, target for as long as the order / trade lives
                int x0 = brk, x1 = Math.Max(end, brk + 1);
                Add(Chart.DrawTrendLine(id + "entry", T(x0), Real(dir, entry), T(x1), Real(dir, entry), Color.Orange, 2, LineStyle.Solid));
                Add(Chart.DrawTrendLine(id + "stop", T(x0), Real(dir, stop), T(x1), Real(dir, stop), Color.Red, 1, LineStyle.Solid));
                Add(Chart.DrawTrendLine(id + "tgt", T(x0), Real(dir, target), T(x1), Real(dir, target), Color.LimeGreen, 1, LineStyle.Solid));
                Add(Chart.DrawText(id + "lbl", side + " 0.618: " + result, T(x0), Real(dir, stop), main));
            }
        }

        private static bool Near(double a, double b) => Math.Abs(a - b) < 1e-6;

        private void Add(ChartObject o)
        {
            if (o == null) return;
            o.IsInteractive = false;
            _names.Add(o.Name);
        }
    }
}
