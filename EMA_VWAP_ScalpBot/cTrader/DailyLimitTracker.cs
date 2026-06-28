using System;
using cAlgo.API;

namespace EmaVwapBot
{
    /// <summary>
    /// Tracks per-day trade count, daily P&L, and peak-equity kill switch.
    /// All thresholds are checked before any new position is opened.
    /// </summary>
    public class DailyLimitTracker
    {
        private readonly int    _maxTradesPerDay;
        private readonly double _maxDailyLossPct;      // e.g. 3.0  = 3%
        private readonly double _killSwitchDrawdownPct; // e.g. 8.0  = 8%

        private DateTime _trackingDate;
        private int      _tradesToday;
        private double   _dailyStartEquity;
        private double   _peakEquity;
        private bool     _killSwitchTripped;

        public bool  KillSwitchTripped => _killSwitchTripped;
        public int   TradesToday       => _tradesToday;

        public DailyLimitTracker(int maxTradesPerDay, double maxDailyLossPct, double killSwitchDrawdownPct)
        {
            _maxTradesPerDay       = maxTradesPerDay;
            _maxDailyLossPct       = maxDailyLossPct;
            _killSwitchDrawdownPct = killSwitchDrawdownPct;
            _trackingDate          = DateTime.MinValue;
        }

        /// <summary>Must be called on each bar to keep counters current.</summary>
        public void Update(DateTime serverDate, double currentEquity)
        {
            // Reset daily counters on new calendar day
            if (serverDate.Date != _trackingDate.Date)
            {
                _tradesToday      = 0;
                _dailyStartEquity = currentEquity;
                _trackingDate     = serverDate;
            }

            // Update peak equity (used for kill-switch calculation)
            if (currentEquity > _peakEquity)
                _peakEquity = currentEquity;
        }

        /// <summary>
        /// Returns true if a new trade can be opened.
        /// False if any of: kill switch tripped, daily trade limit reached, daily loss limit reached.
        /// </summary>
        public bool CanOpenNewTrade(double currentEquity)
        {
            if (_killSwitchTripped)
                return false;

            if (_tradesToday >= _maxTradesPerDay)
                return false;

            // Daily loss check
            if (_dailyStartEquity > 0)
            {
                double dailyLossPct = (_dailyStartEquity - currentEquity) / _dailyStartEquity * 100.0;
                if (dailyLossPct >= _maxDailyLossPct)
                    return false;
            }

            // Kill switch check (peak-to-trough)
            if (_peakEquity > 0)
            {
                double drawdownPct = (_peakEquity - currentEquity) / _peakEquity * 100.0;
                if (drawdownPct >= _killSwitchDrawdownPct)
                {
                    _killSwitchTripped = true;
                    return false;
                }
            }

            return true;
        }

        /// <summary>Call after each confirmed trade entry.</summary>
        public void RegisterTrade()
        {
            _tradesToday++;
        }

        /// <summary>Initialise peak equity on bot start.</summary>
        public void InitialisePeak(double equity)
        {
            if (_peakEquity <= 0)
                _peakEquity = equity;
        }
    }
}
