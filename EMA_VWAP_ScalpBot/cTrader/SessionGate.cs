using System;
using cAlgo.API;

namespace EmaVwapBot
{
    public enum InstrumentType { GER40, US500 }

    /// <summary>
    /// Enforces permitted trading windows. All times are UK (London) wall-clock time.
    /// GER40  — Window 1: 08:00–11:30  Window 2: 13:00–16:00  Hard close: 16:30
    /// US500  — Window 1: 14:00–17:30  Hard close: 18:00
    /// European lunch exclusion (11:30–13:00 GER40) is CRITICAL — see spec §7.
    /// </summary>
    public class SessionGate
    {
        private readonly InstrumentType _instrument;

        public SessionGate(InstrumentType instrument)
        {
            _instrument = instrument;
        }

        /// <summary>Returns true if the given UTC time falls within a permitted signal window.</summary>
        public bool IsInTradingWindow(DateTime utcTime)
        {
            DateTime ukTime = ConvertToUk(utcTime);
            TimeSpan t = ukTime.TimeOfDay;

            return _instrument == InstrumentType.GER40
                ? IsInGer40Window(t)
                : IsInUs500Window(t);
        }

        /// <summary>Returns true if the bot must close all positions at this time.</summary>
        public bool IsPastSessionClose(DateTime utcTime)
        {
            DateTime ukTime  = ConvertToUk(utcTime);
            TimeSpan t       = ukTime.TimeOfDay;
            TimeSpan cutoff  = _instrument == InstrumentType.GER40
                                 ? new TimeSpan(16, 30, 0)
                                 : new TimeSpan(18, 0, 0);
            return t >= cutoff;
        }

        /// <summary>Returns the session hard-close time (UK) as a TimeSpan.</summary>
        public TimeSpan SessionCloseTimeUk =>
            _instrument == InstrumentType.GER40
                ? new TimeSpan(16, 30, 0)
                : new TimeSpan(18, 0, 0);

        // ── private helpers ──────────────────────────────────────────────────

        private static bool IsInGer40Window(TimeSpan t)
        {
            // Window 1: 08:00–11:30 (exclusive upper bound at 11:30)
            bool w1 = t >= new TimeSpan(8, 0, 0) && t < new TimeSpan(11, 30, 0);
            // Window 2: 13:00–16:00 (no new signals after 16:00 to allow clean exits before 16:30)
            bool w2 = t >= new TimeSpan(13, 0, 0) && t < new TimeSpan(16, 0, 0);
            return w1 || w2;
        }

        private static bool IsInUs500Window(TimeSpan t)
        {
            // Window 1: 14:00–17:30
            return t >= new TimeSpan(14, 0, 0) && t < new TimeSpan(17, 30, 0);
        }

        private static DateTime ConvertToUk(DateTime utcTime)
        {
            // Use the OS timezone database for correct DST handling
            try
            {
                TimeZoneInfo ukZone = TimeZoneInfo.FindSystemTimeZoneById("Europe/London");
                return TimeZoneInfo.ConvertTimeFromUtc(utcTime, ukZone);
            }
            catch
            {
                // Fallback: approximate GMT+1 (BST, Apr–Oct) or GMT (Nov–Mar)
                int month = utcTime.Month;
                int offset = (month >= 4 && month <= 10) ? 1 : 0;
                return utcTime.AddHours(offset);
            }
        }
    }
}
