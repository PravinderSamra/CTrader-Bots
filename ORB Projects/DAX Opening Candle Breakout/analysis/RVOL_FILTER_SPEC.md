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

## Use the cumulative variant — it is the only one that fits this codebase

**Revised after reviewing `ORB_Volume_Breakout_Bot_v2.cs`.**

The single-bar definition above assumes the filter runs on a known bar (the opening bar).
It does not. `EvaluateVolumeFilter(evalBarIndex, ...)` runs on the *evaluation bar*, which
can be any confirmation bar in the session — the filter is signal qualification, not an
entry gate, so a bar that fails does not stand the day down and a later bar can qualify.
A fixed "bar at time T" baseline cannot serve that.

The cumulative form generalises to any evaluation bar and must be the primary definition:

    RVOL = SUM(volume, session open -> evaluation bar)
           / median{ SUM(volume, session open -> same local time), last N days }

This also handles the intrabar case for free: a partially formed bar contributes partial
volume to both sides of the ratio.

## Implementation notes specific to v2

**Mirror the existing method signature.** `EvaluateVolumeFilter` returns bool with
`out evalVol, out trailingAvg, out required, out ratio`. Add `EvaluateRvolFilter` with the
same shape and select between them with a mode enum, so the call site and all logging stay
unchanged:

    [Parameter("Volume Filter Mode", Group = "Volume Filter", DefaultValue = VolumeFilterMode.TrailingBars)]
    public VolumeFilterMode VolumeMode { get; set; }   // TrailingBars | RelativeToTypical

**Preserve signal-qualification semantics.** A failed RVOL check must `return` as no-signal,
not stand the day down. Same as the existing filter.

**Do not build the baseline from the m1 confirmation series.** All live configs run
`ConfirmationTimeFrame: m1`. Fourteen days of the DAX cash session at m1 is roughly 7,000
bars, and cAlgo will not have that loaded by default. Build the RVOL baseline from a
separate, coarser series — `MarketData.GetBars(TimeFrame.Minute5)` or m15 — which needs
~1,400 bars for the same 14 days. Volume ratios are scale-free, so the coarser series gives
the same answer at a fraction of the history.

**Backtest warm-up.** The first N days of any backtest cannot compute a baseline. Either
start the backtest 14 trading days before the evaluation window, or accept that the first
fortnight produces no trades — and log which, so it is visible afterwards rather than being
mistaken for a filter that is too tight.

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

v2 already logs `vol=... avg=... ratio=...` on the SIGNAL line, so passes are covered.
Rejections currently log `required` but not `ratio`. Add the ratio to the rejection line so
both sides are measurable from one grep:

    RVOL_DIAG time=<local> vol=<today> typical=<median> rvol=<ratio> n=<days used> passed=<bool>

Without the ratio on both sides, the filter's real selectivity can only be inferred from
proxies. That inference was made once during analysis and was wrong; the log line makes it
a measurement.

## Caveat on the data

cTrader's CFD "volume" is tick count — the number of price updates — not contracts
traded. It is a reasonable proxy for activity but it is not real volume, and it is one
reason a volume filter can look sharper in backtest than it behaves live.
