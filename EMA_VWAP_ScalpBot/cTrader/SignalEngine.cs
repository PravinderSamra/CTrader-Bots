using System;

namespace EmaVwapBot
{
    public enum SignalDirection { None, Long, Short }

    public enum EntryState { Idle, AwaitingEntry, InTrade }

    /// <summary>
    /// Evaluates all 8 entry conditions (L1-L8 / S1-S8) on each 5M bar close.
    /// Tracks entry state for the 1M precision tier.
    /// All conditions must pass simultaneously — no weighting, no exceptions.
    /// </summary>
    public class SignalEngine
    {
        private readonly double _minBodyPct;          // e.g. 40.0 = 40%
        private readonly double _maxEntryDistanceAtr; // e.g. 1.0 = 1× ATR

        private EntryState     _state            = EntryState.Idle;
        private SignalDirection _pendingDirection = SignalDirection.None;
        private int            _barsWaited       = 0;
        private double         _vwapAtSignal;
        private double         _atrAtSignal;

        public EntryState     State            => _state;
        public SignalDirection PendingDirection => _pendingDirection;

        public SignalEngine(double minBodyPct, double maxEntryDistanceAtr)
        {
            _minBodyPct            = minBodyPct;
            _maxEntryDistanceAtr   = maxEntryDistanceAtr;
        }

        // ── 5M signal evaluation ─────────────────────────────────────────────

        /// <summary>
        /// Evaluate 5M bar for entry signal. Call on each completed 5M bar.
        /// Returns the signal direction, or None if no signal.
        /// </summary>
        public SignalDirection Evaluate5mSignal(
            double close5m, double open5m, double high5m, double low5m,
            double ema9_5m, double ema21_5m, double vwap,
            double close1h, double ema21_1h,
            bool inSession, bool canOpenTrade)
        {
            if (!inSession || !canOpenTrade) return SignalDirection.None;

            // L1/S1 — 1H bias gate
            bool longBias  = IsLongBias(close1h, ema21_1h);
            bool shortBias = IsShortBias(close1h, ema21_1h);
            if (!longBias && !shortBias) return SignalDirection.None;

            // Body filter (L6/S6)
            double range = high5m - low5m;
            if (range <= 0) return SignalDirection.None;
            double bodyPct = Math.Abs(close5m - open5m) / range * 100.0;
            if (bodyPct < _minBodyPct) return SignalDirection.None;

            if (longBias)
            {
                // L2: close above EMA9
                // L3: close above EMA21
                // L4: close above VWAP
                // L5: EMA9 above EMA21
                if (close5m > ema9_5m && close5m > ema21_5m && close5m > vwap && ema9_5m > ema21_5m)
                    return SignalDirection.Long;
            }

            if (shortBias)
            {
                // S2: close below EMA9
                // S3: close below EMA21
                // S4: close below VWAP
                // S5: EMA9 below EMA21
                if (close5m < ema9_5m && close5m < ema21_5m && close5m < vwap && ema9_5m < ema21_5m)
                    return SignalDirection.Short;
            }

            return SignalDirection.None;
        }

        // ── 1H bias ──────────────────────────────────────────────────────────

        private static bool IsLongBias(double close1h, double ema21_1h)
        {
            // Flat zone: within 0.05% of EMA = no bias
            double flatZone = ema21_1h * 0.0005;
            return close1h > ema21_1h + flatZone;
        }

        private static bool IsShortBias(double close1h, double ema21_1h)
        {
            double flatZone = ema21_1h * 0.0005;
            return close1h < ema21_1h - flatZone;
        }

        // ── 1M entry state machine ────────────────────────────────────────────

        /// <summary>Activate the 1M waiting state after a valid 5M signal.</summary>
        public void ActivatePendingEntry(SignalDirection direction, double vwapNow, double atrNow)
        {
            _state            = EntryState.AwaitingEntry;
            _pendingDirection = direction;
            _barsWaited       = 0;
            _vwapAtSignal     = vwapNow;
            _atrAtSignal      = atrNow;
        }

        /// <summary>
        /// Check whether the current 1M bar qualifies for entry.
        /// Returns true if we should execute a market order on this bar's open.
        /// Automatically abandons setup after 3 bars.
        /// </summary>
        public bool Check1mEntry(double close1m, double open1m)
        {
            if (_state != EntryState.AwaitingEntry) return false;

            _barsWaited++;

            // Maximum 3 bars wait
            if (_barsWaited > 3)
            {
                Reset();
                return false;
            }

            // Max entry distance: must be within 1.0× ATR of VWAP
            double distFromVwap = Math.Abs(open1m - _vwapAtSignal);
            if (distFromVwap > _maxEntryDistanceAtr * _atrAtSignal)
                return false;

            // 1M bar must close in signal direction
            bool qualifies = _pendingDirection == SignalDirection.Long
                ? close1m > open1m   // bullish 1M bar
                : close1m < open1m;  // bearish 1M bar

            if (qualifies)
            {
                _state = EntryState.InTrade;
                return true;
            }

            return false;
        }

        /// <summary>Reset to idle (setup abandoned or trade exited).</summary>
        public void Reset()
        {
            _state            = EntryState.Idle;
            _pendingDirection = SignalDirection.None;
            _barsWaited       = 0;
        }
    }
}
