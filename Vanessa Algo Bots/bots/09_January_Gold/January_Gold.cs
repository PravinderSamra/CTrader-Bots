// January Gold v1.0 (Vanessa Algo Bots)
// Gold has been strong in January: FTMO XAUUSD 2012-2026,
// +3.7% a January after costs and swap, 11 of 15 years up
// (research/screens/gold_seasonal.py). Rule: buy at the first
// tradable moment of January, sell at the first tradable
// moment of February. Safety stop Stop Loss % below entry.
// Never re-enters in the same January (checks History).
// Log: O| open, C| close, X| skipped, R|gap laptop asleep,
// H| history at the end.
using System;
using System.Linq;
using cAlgo.API;
using cAlgo.API.Internals;

namespace cAlgo.Robots
{
    [Robot(AccessRights = AccessRights.None, TimeZone = TimeZones.UTC)]
    public class JanuaryGold : Robot
    {
        [Parameter("Symbol", Group = "Market", DefaultValue = "XAUUSD")]
        public string SymbolName0 { get; set; }

        [Parameter("Entry Month (1 = January)", Group = "Calendar",
            DefaultValue = 1, MinValue = 1, MaxValue = 12)]
        public int EntryMonth { get; set; }

        [Parameter("Notional ($)", Group = "Risk", DefaultValue = 20000,
            MinValue = 100)]
        public double Notional { get; set; }

        [Parameter("Stop Loss %", Group = "Risk", DefaultValue = 7.0,
            MinValue = 0.5)]
        public double StopPct { get; set; }

        [Parameter("Label", Group = "Other", DefaultValue = "JANGOLD")]
        public string Label { get; set; }

        private Symbol _s;
        private DateTime _lastTick = DateTime.MinValue;
        private DateTime _openSince = DateTime.MinValue;
        private DateTime _lastBeat = DateTime.MinValue;

        protected override void OnStart()
        {
            _s = Symbols.GetSymbol(SymbolName0);
            if (_s == null)
            {
                Print("Symbol not found: {0}", SymbolName0);
                Stop();
                return;
            }
            _s.Tick += args =>
            {
                var now = Server.Time;
                if (now - _lastTick > TimeSpan.FromMinutes(30)) _openSince = now;
                _lastTick = now;
            };
            Timer.Start(TimeSpan.FromMinutes(1));
            Print("January Gold v1.0 started: {0}, month {1}, ${2}, stop {3}%",
                _s.Name, EntryMonth, Notional, StopPct);
        }

        private bool Tradable() =>
            Server.Time - _lastTick <= TimeSpan.FromMinutes(2)
                && Server.Time - _openSince >= TimeSpan.FromMinutes(15);

        private Position Mine => Positions.FirstOrDefault(
            p => p.Label == Label && p.SymbolName == _s.Name);

        private void Heartbeat()
        {
            if (RunningMode != RunningMode.RealTime) return;
            var now = Server.Time;
            var gap = now - _lastBeat;
            if (_lastBeat != DateTime.MinValue && gap > TimeSpan.FromMinutes(5))
                Print("R|gap: no activity from {0:yyyy-MM-dd HH:mm} to "
                    + "{1:yyyy-MM-dd HH:mm} UTC ({2:F1} h) - laptop asleep or offline?",
                    _lastBeat, now, gap.TotalHours);
            _lastBeat = now;
        }

        protected override void OnTimer()
        {
            Heartbeat();
            if (!Tradable()) return;
            var now = Server.Time;
            var pos = Mine;
            if (pos != null)
            {
                if (now.Month != EntryMonth)
                {
                    Print("C|{0}|{1}|{2:yyyy-MM-dd HH:mm}|end of the month",
                        Label, _s.Name, now);
                    ClosePosition(pos);
                }
                return;
            }
            if (now.Month != EntryMonth) return;
            bool traded = History.Any(h => h.Label == Label
                && h.SymbolName == _s.Name && h.EntryTime.Year == now.Year
                && h.EntryTime.Month == EntryMonth);
            if (traded) return;
            double price = _s.Ask;
            double perUnit = price * _s.TickValue / _s.TickSize;
            double units = _s.NormalizeVolumeInUnits(Notional / perUnit,
                RoundingMode.Down);
            if (units < _s.VolumeInUnitsMin)
            {
                Print("X|{0}|{1}|size_below_minimum", Label, _s.Name);
                return;
            }
            var r = ExecuteMarketOrder(TradeType.Buy, _s.Name, units, Label);
            if (!r.IsSuccessful)
            {
                Print("X|{0}|{1}|order rejected: {2}", Label, _s.Name, r.Error);
                return;
            }
            var m = r.Position.ModifyStopLossPrice(price * (1 - StopPct / 100));
            if (m == null || !m.IsSuccessful)
            {
                Print("X|{0}|{1}|could not set stop, closed", Label, _s.Name);
                ClosePosition(r.Position);
                return;
            }
            Print("O|{0}|{1}|{2:yyyy-MM-dd HH:mm}|{3}|{4}|SL {5}", Label, _s.Name,
                now, r.Position.VolumeInUnits, r.Position.EntryPrice,
                r.Position.StopLoss);
        }

        protected override void OnStop()
        {
            foreach (var h in History.Where(h => h.Label == Label)
                .OrderBy(h => h.ClosingTime))
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
