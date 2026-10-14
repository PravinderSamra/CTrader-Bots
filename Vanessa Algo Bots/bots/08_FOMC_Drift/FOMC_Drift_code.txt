// Pre-FOMC Drift v1.0 (Vanessa Algo Bots)
// Lucca & Moench (2015): US stock indices tend to rise in
// the 24 hours before a scheduled Fed (FOMC) announcement.
// Tested 15 Oct 2026 on FTMO costs, 2014-2026
// (research/ssrn/SSRN_REVIEW.md): NAS100 +0.22% a trade,
// US500 +0.14%, positive in every period.
// Rule: buy each index at 14:00 New York on meeting day 1
// (the day before the statement), sell at 13:58 New York on
// announcement day, just before the 14:00 statement.
// Meeting day-1 dates are a setting (one list per year,
// from federalreserve.gov). Scheduled meetings only.
// Size: Notional Per Position dollars per index.
// Safety stop: Stop Loss % below the entry.
// Log: O| open, C| close, X| skipped, H| history at the end.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using cAlgo.API;
using cAlgo.API.Internals;

namespace cAlgo.Robots
{
    [Robot(AccessRights = AccessRights.None, TimeZone = TimeZones.UTC)]
    public class FomcDrift : Robot
    {
        private const string Dates2021to2023 =
            "2021-01-26,2021-03-16,2021-04-27,2021-06-15,"
            + "2021-07-27,2021-09-21,2021-11-02,2021-12-14,"
            + "2022-01-25,2022-03-15,2022-05-03,2022-06-14,"
            + "2022-07-26,2022-09-20,2022-11-01,2022-12-13,"
            + "2023-01-31,2023-03-21,2023-05-02,2023-06-13,"
            + "2023-07-25,2023-09-19,2023-10-31,2023-12-12";

        private const string Dates2024to2027 =
            "2024-01-30,2024-03-19,2024-04-30,2024-06-11,"
            + "2024-07-30,2024-09-17,2024-11-06,2024-12-17,"
            + "2025-01-28,2025-03-18,2025-05-06,2025-06-17,"
            + "2025-07-29,2025-09-16,2025-10-28,2025-12-09,"
            + "2026-01-27,2026-03-17,2026-04-28,2026-06-16,"
            + "2026-07-28,2026-09-15,2026-10-27,2026-12-08,"
            + "2027-01-26,2027-03-16,2027-04-27,2027-06-08,"
            + "2027-07-27,2027-09-14,2027-10-26,2027-12-07";

        [Parameter("Symbols", Group = "Universe",
            DefaultValue = "US100.cash,US500.cash")]
        public string SymbolList { get; set; }

        [Parameter("Meeting Day-1 Dates 2021-2023", Group = "Calendar",
            DefaultValue = Dates2021to2023)]
        public string DatesA { get; set; }

        [Parameter("Meeting Day-1 Dates 2024-2027", Group = "Calendar",
            DefaultValue = Dates2024to2027)]
        public string DatesB { get; set; }

        [Parameter("Extra Dates (yyyy-mm-dd,...)", Group = "Calendar",
            DefaultValue = "")]
        public string DatesC { get; set; }

        [Parameter("Notional Per Position ($)", Group = "Risk",
            DefaultValue = 20000, MinValue = 100)]
        public double Notional { get; set; }

        [Parameter("Stop Loss %", Group = "Risk",
            DefaultValue = 3.0, MinValue = 0.5)]
        public double StopPct { get; set; }

        [Parameter("Label", Group = "Other", DefaultValue = "FOMC")]
        public string Label { get; set; }

        private readonly HashSet<DateTime> _day1 = new HashSet<DateTime>();
        private readonly List<Symbol> _syms = new List<Symbol>();
        private DateTime _openedFor = DateTime.MinValue;

        protected override void OnStart()
        {
            foreach (var list in new[] { DatesA, DatesB, DatesC })
                foreach (var raw in (list ?? "").Split(','))
                {
                    DateTime d;
                    if (DateTime.TryParseExact(raw.Trim(), "yyyy-MM-dd",
                        CultureInfo.InvariantCulture, DateTimeStyles.None, out d))
                        _day1.Add(d.Date);
                }
            foreach (var raw in SymbolList.Split(','))
            {
                var name = raw.Trim();
                if (name.Length == 0) continue;
                Symbol s;
                try { s = Symbols.GetSymbol(name); } catch { s = null; }
                if (s == null)
                {
                    Print("Symbol not found, skipped: {0}", name);
                    continue;
                }
                _syms.Add(s);
            }
            Timer.Start(TimeSpan.FromSeconds(30));
            Print("Pre-FOMC Drift started: {0} meetings, {1} symbols, ${2} each.",
                _day1.Count, _syms.Count, Notional);
        }

        // UTC -> New York time (2nd Sunday of March to 1st Sunday of November).
        private static DateTime NewYork(DateTime utc)
        {
            var mar = new DateTime(utc.Year, 3, 1);
            var dstStart = mar.AddDays((7 - (int)mar.DayOfWeek) % 7 + 7).AddHours(7);
            var nov = new DateTime(utc.Year, 11, 1);
            var dstEnd = nov.AddDays((7 - (int)nov.DayOfWeek) % 7).AddHours(6);
            return utc.AddHours(utc >= dstStart && utc < dstEnd ? -4 : -5);
        }

        private IEnumerable<Position> Mine =>
            Positions.Where(p => p.Label == Label);

        protected override void OnTimer()
        {
            var ny = NewYork(Server.Time);
            int mins = ny.Hour * 60 + ny.Minute;

            // exit: announcement day (day 1 + 1) from 13:58 New York,
            // or any later time if a position is somehow still open
            foreach (var p in Mine.ToList())
            {
                var entryNy = NewYork(p.EntryTime);
                var exitDay = entryNy.Date.AddDays(1);
                if (ny.Date > exitDay || (ny.Date == exitDay && mins >= 13 * 60 + 58))
                {
                    Print("C|{0}|{1}|{2:yyyy-MM-dd HH:mm}|before the statement",
                        Label, p.SymbolName, ny);
                    ClosePosition(p);
                }
            }

            // entry: meeting day 1, 14:00-14:30 New York, once per meeting
            if (!_day1.Contains(ny.Date) || _openedFor == ny.Date) return;
            if (mins < 14 * 60 || mins > 14 * 60 + 30) return;
            _openedFor = ny.Date;
            foreach (var s in _syms)
            {
                if (Mine.Any(p => p.SymbolName == s.Name)) continue;
                double price = s.Ask;
                double perUnit = price * s.TickValue / s.TickSize;
                double units = s.NormalizeVolumeInUnits(Notional / perUnit,
                    RoundingMode.Down);
                if (units < s.VolumeInUnitsMin)
                {
                    Print("X|{0}|{1}|size_below_minimum", Label, s.Name);
                    continue;
                }
                var r = ExecuteMarketOrder(TradeType.Buy, s.Name, units, Label);
                if (!r.IsSuccessful)
                {
                    Print("X|{0}|{1}|order rejected: {2}", Label, s.Name, r.Error);
                    continue;
                }
                var m = r.Position.ModifyStopLossPrice(price * (1 - StopPct / 100));
                if (m == null || !m.IsSuccessful)
                {
                    Print("X|{0}|{1}|could not set stop, closed", Label, s.Name);
                    ClosePosition(r.Position);
                    continue;
                }
                Print("O|{0}|{1}|{2:yyyy-MM-dd HH:mm}|{3}|{4}", Label, s.Name,
                    ny, r.Position.VolumeInUnits, r.Position.EntryPrice);
            }
        }

        protected override void OnStop()
        {
            var hist = History.Where(h => h.Label == Label)
                .OrderBy(h => h.ClosingTime);
            foreach (var h in hist)
                Print("H|{0}|{1}|{2}|{3:yyyy-MM-dd HH:mm}|"
                    + "{4:yyyy-MM-dd HH:mm}|{5}|{6}|{7}|"
                    + "{8:F2}|{9:F2}|{10:F2}|{11:F2}",
                    h.PositionId, h.Label, h.SymbolName, h.EntryTime,
                    h.ClosingTime, h.VolumeInUnits, h.EntryPrice,
                    h.ClosingPrice, h.GrossProfit, h.Swap, h.Commissions,
                    h.NetProfit);
        }
    }
}
