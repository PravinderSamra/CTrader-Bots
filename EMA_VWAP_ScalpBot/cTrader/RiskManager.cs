using System;
using cAlgo.API;
using cAlgo.API.Internals;

namespace EmaVwapBot
{
    /// <summary>
    /// Calculates ATR-based stop losses and fixed-fractional position sizes.
    /// Spread-betting sizing: volume = round(riskGbp / stopPoints) × 100
    /// Each 100 units of volume = £1 per point movement (Pepperstone SB).
    /// </summary>
    public class RiskManager
    {
        private readonly double _riskPerTradePct;    // e.g. 1.0  = 1%
        private readonly double _atrMultiplier;      // e.g. 1.5
        private readonly double _minSlMultiplier;    // = 0.5 (skip if too narrow)
        private readonly double _maxSlMultiplier;    // = 2.5 (skip if news spike)

        public RiskManager(double riskPerTradePct, double atrMultiplier)
        {
            _riskPerTradePct = riskPerTradePct;
            _atrMultiplier   = atrMultiplier;
            _minSlMultiplier = 0.5;
            _maxSlMultiplier = 2.5;
        }

        /// <summary>
        /// Calculate the stop loss price for a long entry.
        /// Returns double.NaN if the calculated distance is outside valid bounds.
        /// </summary>
        public double CalculateLongStopLoss(double entryPrice, double atrValue)
        {
            double stopDistance = _atrMultiplier * atrValue;
            if (!IsValidStopDistance(stopDistance, atrValue))
                return double.NaN;
            return entryPrice - stopDistance;
        }

        /// <summary>
        /// Calculate the stop loss price for a short entry.
        /// Returns double.NaN if the calculated distance is outside valid bounds.
        /// </summary>
        public double CalculateShortStopLoss(double entryPrice, double atrValue)
        {
            double stopDistance = _atrMultiplier * atrValue;
            if (!IsValidStopDistance(stopDistance, atrValue))
                return double.NaN;
            return entryPrice + stopDistance;
        }

        /// <summary>
        /// Calculate volume in spread-betting units.
        /// volume = round(riskGbp / stopDistancePoints) × 100
        /// Minimum volume: 100 (= £1/pt stake). Step size: 100.
        /// </summary>
        public long CalculateVolume(double accountEquity, double entryPrice, double stopLossPrice)
        {
            double stopDistance = Math.Abs(entryPrice - stopLossPrice);
            if (stopDistance <= 0) return 0;

            double riskGbp = accountEquity * (_riskPerTradePct / 100.0);
            double stake   = riskGbp / stopDistance;
            long   volume  = Math.Max(100L, (long)Math.Round(stake) * 100L);
            return volume;
        }

        /// <summary>Stop distance must be within [0.5×ATR, 2.5×ATR].</summary>
        private bool IsValidStopDistance(double stopDistance, double atrValue)
        {
            return stopDistance >= _minSlMultiplier * atrValue
                && stopDistance <= _maxSlMultiplier * atrValue;
        }
    }
}
