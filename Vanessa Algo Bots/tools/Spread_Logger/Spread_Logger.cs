// Spread Logger cBot (Vanessa Algo Bots)
// Measures the real bid/ask spread by hour of the day. Run it as a BACKTEST on tick data over a long period
// (e.g. 1 Jan 2024 to today). It never trades. When the backtest ends, the Log tab shows a table with, for each hour
// (UK time by default): how many minutes were sampled, the average spread, the median and the 90th percentile.
// Spread is in price units, so on US100.cash it is in index points.
// Sampling: the spread at the first tick of each minute (Mon-Fri), so busy minutes do not count more than quiet ones.
using System;
using System.Text;
using cAlgo.API;

namespace cAlgo.Robots
{
    [Robot(AccessRights = AccessRights.None, TimeZone = TimeZones.UTC)]
    public class SpreadLogger : Robot
    {
        [Parameter("Report In UK Time", DefaultValue = true)]
        public bool UkTime { get; set; }

        private const int Bins = 1000;          // histogram bins
        private double _binSize;                 // price units per bin
        private readonly long[] _count = new long[24];
        private readonly double[] _sum = new double[24];
        private readonly long[,] _hist = new long[24, Bins];
        private DateTime _lastMinute = DateTime.MinValue;
        private TimeZoneInfo _uk;

        protected override void OnStart()
        {
            _binSize = Symbol.TickSize > 0 ? Symbol.TickSize * 10 : 0.01;
            try { _uk = TimeZoneInfo.FindSystemTimeZoneById("GMT Standard Time"); }
            catch { try { _uk = TimeZoneInfo.FindSystemTimeZoneById("Europe/London"); } catch { _uk = null; } }
            if (UkTime && _uk == null)
                Print("UK time zone not found; reporting in UTC instead.");
        }

        protected override void OnTick()
        {
            DateTime utc = Server.Time;
            var minute = new DateTime(utc.Year, utc.Month, utc.Day, utc.Hour, utc.Minute, 0, DateTimeKind.Utc);
            if (minute == _lastMinute) return;
            _lastMinute = minute;

            DateTime local = (UkTime && _uk != null) ? TimeZoneInfo.ConvertTimeFromUtc(minute, _uk) : minute;
            if (local.DayOfWeek == DayOfWeek.Saturday || local.DayOfWeek == DayOfWeek.Sunday) return;

            double spread = Symbol.Ask - Symbol.Bid;
            if (spread < 0) return;
            int h = local.Hour;
            _count[h]++;
            _sum[h] += spread;
            int bin = (int)(spread / _binSize);
            if (bin >= Bins) bin = Bins - 1;
            _hist[h, bin]++;
        }

        private double Percentile(int h, double p)
        {
            long target = (long)Math.Ceiling(_count[h] * p), seen = 0;
            for (int b = 0; b < Bins; b++)
            {
                seen += _hist[h, b];
                if (seen >= target) return (b + 0.5) * _binSize;
            }
            return (Bins - 0.5) * _binSize;
        }

        protected override void OnStop()
        {
            string zone = (UkTime && _uk != null) ? "UK time" : "UTC";
            Print("SPREAD REPORT {0} ({1}), spread in price units", SymbolName, zone);
            Print("SPREAD hour | minutes | average | median | 90th percentile");
            for (int h = 0; h < 24; h++)
            {
                if (_count[h] == 0) continue;
                Print("SPREAD {0:00}:00 | {1} | {2:F2} | {3:F2} | {4:F2}",
                    h, _count[h], _sum[h] / _count[h], Percentile(h, 0.5), Percentile(h, 0.9));
            }
        }
    }
}
