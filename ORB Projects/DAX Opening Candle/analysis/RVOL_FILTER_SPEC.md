# Relative Volume (RVOL) filter — implementation spec

For Prav. Adds a time-of-day-normalised volume filter, for use on an opening-range
bot where the existing trailing-volume filter does not work.

## Why a second filter, when the NAS one works

The NAS bot's filter is `breakout bar volume / mean of preceding 20 minutes`, with a
1.2 threshold. Measured on 692 NAS trades, that filter is genuinely valuable:

| Keep top | Threshold | Expectancy | Total R |
|---|---|---|---|
| 100% (off) | — | +0.034R | 23.4 |
| 80% | 1.072 | +0.057R | 31.3 |
| **60%** | **1.207** | **+0.104R** | **43.4** |
| 50% | 1.275 | +0.165R | 57.1 |
| 20% | 1.492 | +0.024R | 3.3 |
| 10% | 1.606 | -0.067R | -4.7 |

It roughly triples expectancy at the 1.2 setting currently in use. **Leave it alone.**

It fails on an opening-range bot for a structural reason: the NAS bot breaks out well
after the open, so the preceding 20 minutes are normal-volume bars. A DAX 5-minute ORB
fires *at* the open, where the preceding bars are pre-auction and nearly empty. Measured
on GER40, the median opening bar is **3.77x** the preceding 20 minutes (NAS: 1.78x), so
a 1.2 threshold passes **100%** of days and filters nothing.

The research this is based on (Zarattini, Barbon & Aziz 2024) used the time-of-day
normalised version, and reported that filter accounted for almost all of the strategy's
return — unfiltered 29% vs filtered 1,637% over 2016-2023.

## Definition

    RVOL = Volume(today, bar at time T) / TypicalVolume(T)

    TypicalVolume(T) = median{ Volume(day d, bar at time T) : d in previous N trading days }

## Design decisions

**Median, not mean.** One news day at 5x normal volume drags a mean baseline up for a
fortnight and silently disables the filter. The median ignores it.

**N = 14 trading days** to start. Matches the ATR convention and the source paper.
Test 10 and 20 in-sample.

**Match on local exchange time, not UTC.** The 09:00 Frankfurt bar is 08:00 UTC in
winter and 07:00 UTC in summer. Look up historical bars by their Europe/Berlin
wall-clock time — do not subtract a fixed offset. This is the same DST trap that was
fixed in the session-time code; it applies again here.

**Exclude today** from its own baseline.

**Exclude half-days and holidays from the baseline.** They carry a fraction of normal
volume and drag the median down, causing the filter to fire on ordinary days afterwards.
Suggested rule: skip any day whose full-session volume is below 50% of the trailing
median session volume.

**Warm-up.** The filter cannot compute until N valid days are available. The bot must
either skip trading or bypass the filter during warm-up — and must log which, so the
behaviour is visible in the backtest afterwards.

**cTrader history.** cAlgo loads a limited number of bars by default. Fourteen days of
M5 bars is more than the default. Call `Bars.LoadMoreHistory()` in a loop at startup
until enough days are present, and handle the case where the broker returns nothing
more (stop looping; do not spin).

## Preferred variant: cumulative RVOL

Less noisy than a single bar, and it works for entries that fire later in the session —
so one implementation covers both the DAX ORB and the NAS bot:

    RVOL = SUM(volume, session open -> now)
           / median{ SUM(volume, session open -> same time of day), last 14 days }

## Starting thresholds for GER40

Measured on GER40 M5, 2023-07 to 2026-08, opening bar at 09:00 CET:

| Threshold | Days kept | Trades/year |
|---|---|---|
| 1.0 | 50.7% | 128 |
| 1.1 | 24.7% | 62 |
| 1.2 | 13.6% | 34 |
| 1.3 | 6.0% | 15 |

Test the **1.0-1.2** range. Below ~60 trades/year the strategy cannot be validated in
reasonable time and contributes too little to be worth running. Each threshold tried
counts as a variant for the multiple-testing correction.

## Logging requirement

**Log the RVOL value on every signal, pass or fail**, alongside the raw and typical
volumes:

    RVOL_DIAG time=<local> vol=<today> typical=<median> rvol=<ratio> n=<days used> passed=<bool>

Without this the filter's real selectivity can only be inferred from proxies. That
inference was made once in analysis and was wrong; the log line makes it a measurement.

## Caveat on the data

cTrader's CFD "volume" is tick count — the number of price updates — not contracts
traded. It is a reasonable proxy for activity but it is not real volume, and it is one
reason a volume filter can look sharper in backtest than it behaves live.
