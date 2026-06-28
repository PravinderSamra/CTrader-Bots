using System;

namespace EmaVwapBot
{
    /// <summary>
    /// Session VWAP with volume-weighted standard deviation bands.
    /// Resets on calendar date change (Server.Time.Date comparison — handles DST correctly).
    /// Uses the one-pass variance formula: Var = E[X²] - (E[X])²
    /// </summary>
    public class VwapCalculator
    {
        private double _cumTpv;       // SUM[ tp × volume ]
        private double _cumSqTpv;     // SUM[ tp² × volume ]
        private double _cumVol;       // SUM[ volume ]
        private DateTime _lastResetDate;
        private bool _initialized;

        public double Vwap      { get; private set; }
        public double Sd1Upper  { get; private set; }
        public double Sd1Lower  { get; private set; }
        public double Sd2Upper  { get; private set; }
        public double Sd2Lower  { get; private set; }
        public bool   IsValid   { get; private set; }

        public void Update(DateTime serverTime, double high, double low, double close, double volume)
        {
            if (!_initialized || serverTime.Date != _lastResetDate.Date)
            {
                _cumTpv       = 0;
                _cumSqTpv     = 0;
                _cumVol       = 0;
                _lastResetDate = serverTime;
                _initialized  = true;
                IsValid       = false;
                Vwap = Sd1Upper = Sd1Lower = Sd2Upper = Sd2Lower = 0;
            }

            if (volume <= 0) return;

            double tp   = (high + low + close) / 3.0;
            _cumTpv    += tp * volume;
            _cumSqTpv  += tp * tp * volume;
            _cumVol    += volume;

            double vwap    = _cumTpv / _cumVol;
            double variance = (_cumSqTpv / _cumVol) - (vwap * vwap);
            double stdDev  = Math.Sqrt(Math.Max(0.0, variance));

            Vwap     = vwap;
            Sd1Upper = vwap + stdDev;
            Sd1Lower = vwap - stdDev;
            Sd2Upper = vwap + 2.0 * stdDev;
            Sd2Lower = vwap - 2.0 * stdDev;
            IsValid  = true;
        }

        public void Reset()
        {
            _initialized = false;
            IsValid      = false;
        }
    }
}
