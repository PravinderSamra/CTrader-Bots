# XAUUSD Quant Research Report — 5 Years of 1-Minute Data

**Data:** 1,762,482 one-minute bars, 2021-07-18 → 2026-07-16 (cTrader feed, UTC, bar-open timestamps).
**Audience:** discretionary/systematic day trader on 1m & 5m timeframes.
**Reproduce:** every number here comes from `research/scripts/` (00→05), raw console output archived in `research/output/`.

---

## 1. Data quality

- Only ~1,300 gaps larger than 60 minutes across 5 years, and effectively all of them are weekends, Christmas/New Year, and US-holiday early closes. The feed is clean enough to trust minute-level statistics.
- The dealing day is **22:00 UTC → 21:00 UTC** with a 1-hour maintenance break (21:00–22:00). Volume in hour 21 is ~0.5% of the day — treat 21:00 as your hard flat-time if you don't want to hold the break.

## 2. The regime story (this changes everything)

| Year | First→last close | Avg daily range | Median daily range |
|------|------------------|-----------------|--------------------|
| 2021 | 1813 → 1829 | $21.7 | $19.3 |
| 2022 | 1801 → 1824 | $25.6 | $22.8 |
| 2023 | 1838 → 2063 | $23.7 | $20.9 |
| 2024 | 2059 → 2624 | $33.0 | $30.1 |
| 2025 | 2658 → 4311 | $60.5 | $51.0 |
| 2026 (H1) | 4333 → 3978 | **$134.9** | **$110.7** |

20-day ATR went from ~$17 (Dec 2021) to a peak of **~$205 (Feb 2026)**. Two consequences:

1. **Any fixed-dollar stop/target logic is broken.** Everything must be sized off ATR (I used prior 20-day ATR throughout). A 0.10-lot position in 2026 carries ~6× the daily P&L swing it did in 2022.
2. **Backtests weighted by dollars are dominated by 2025–26.** All expectancies below are reported as % of daily ATR ("ATR units") so years are comparable.

2025 is also notable for *daily-level chop*: the probability that today's direction matched yesterday's was only **41.9%** in 2025 (47–51% other years) — a strong up-drift delivered through alternating up/down days. Daily-close momentum was not the way to ride that move; intraday and overnight exposure was.

## 3. Intraday structure (all times UTC)

### 3.1 Where the volatility lives

Hourly range as a fraction of daily ATR (all years, normalised):

- **13:00–15:00 is the heart of the day** (0.35, 0.34 of ATR per hour) — COMEX open 13:30, US data 13:30, NYSE open 14:30, London PM fix 15:00.
- 12:00 (0.28) and 15:00–16:00 (0.28, 0.21) flank it.
- London open 07:00–08:00 is a secondary bump (0.19–0.20).
- The dead zone is **03:00–05:00** (0.11–0.16) and the pre-close 20:00–21:00.
- Volume shares match: hours 12–16 carry ~33% of the day's volume.

### 3.2 When the daily high/low forms

- **34% of daily extremes form in the 12:00–16:59 NY window** — the single most important fact for a day trader: the day's terminal high or low is most often *made* in the NY morning.
- 34% form in Asia (22:00–06:59) — largely because the day *starts* there (the open is often near one extreme on trend days).
- **Only 13% of daily extremes form during London 07:00–11:59.** London moves price but rarely terminates the move. Fading a London extension is statistically better than fading a NY extension.
- NY session (12:00–21:00) covers on average **77% of the full daily range** on its own; Asia covers 51%, London 43%.

### 3.3 Signed drift by hour — the one real calendar anomaly

Mean close−open per hour as % of ATR with t-stats (N≈1,270 per hour). Almost every hour is noise. The exceptions:

| Hour (UTC) | Mean (% ATR) | t-stat | Comment |
|-----------|--------------|--------|---------|
| **22:00** | +1.14 | **+3.8** | Asia reopen |
| **23:00** | +1.51 | **+4.9** | Asia reopen |
| 20:00 | +0.64 | +2.3 | pre-close |
| 01:00 | +0.87 | +2.0 | late Asia bid |
| 15:00 | −0.69 | −1.2 | PM-fix fade (weak, not tradeable alone) |

The full 24h decomposition (script 04) nails it down:

| Segment | Mean (% ATR/day) | t |
|---------|------------------|---|
| 20:00 → 21:00 close | +0.35 | +1.2 |
| close → 22:00 reopen (gap) | −0.04 | −0.2 |
| **22:00 → 02:00** | **+3.38** | **+5.45** |
| 02:00 → 07:00 | +0.23 | +0.4 |
| 07:00 → 12:00 (London) | +1.04 | +1.6 |
| 12:00 → 20:00 (NY) | −0.48 | −0.4 |

**Essentially all of gold's 5-year drift accrued between 22:00 and 02:00 UTC.** It was positive in every single year (weakest 2022 at +0.9% ATR/day, strongest 2021/2023/2025 at +5–7% ATR/day). The NY session — where all the volatility and volume is — contributed *nothing* net. This matches the long-documented "gold overnight/Asia-demand drift" in the literature; it has persisted here through both the ranging 2021–23 regime and the parabolic 2024–26 regime.

The maintenance-break gap itself is **not** an independent edge — it flips sign with the macro trend (gapped down 81% of days in 2021, up 74% in 2026). It's a trend proxy, nothing more.

### 3.4 Day-of-week

Thursday is the strongest day (+9.1% ATR mean, 56% up-days), Friday the weakest (+0.2% ATR). Monday 55% up. Directionally consistent with the bull regime rather than an independent edge — use as a mild tailwind/headwind filter, not a signal.

## 4. Micro behaviour (1m/5m)

- **Lag-1 autocorrelation is ~zero at every timeframe** (1m: −0.008, 5m: −0.001, 15m: −0.003, 1h: −0.017) and stable across years. There is no naive momentum or mean-reversion edge at bar level. Whatever edge you trade must come from *conditioning* (levels, sessions, ranges), not from bar-to-bar signal.
- **After a 3-sigma 5m bar, continuation over the next 30m is 46.9%** (N=5,112) — a *slight* fade tendency, but the aligned mean move is +0.05bp ≈ zero after costs. Do not chase 1m/5m spikes; do not systematically fade them either.
- **$100 round numbers are neither magnets nor barriers**: price spends *less* time near them than uniform (4.8% vs 6%), and post-cross follow-through is ≈ +0.9bp — noise. (Psychological levels matter for order placement, not for prediction.)

## 5. Range/level statistics that actually condition the day

### 5.1 Asian range (22:00–06:59) is the day's skeleton

Across 1,290 days:

- P(London/NY breaks Asian high) = 68.8%, low = 62.6%, **at least one side = 96.7%**, both sides = 34.7%.
- **62% of days break only ONE side** — and on those days price **closes beyond the broken side 69–70% of the time**. One-side-break days are trend days, and the break direction is the day direction.
- The ICT-style "Judas swing" (London sweeps one side then fully reverses through the other side) happens only **18% (after high sweep) / 23% (after low sweep)** of the time. When London breaks a side first, the day **closes through that side ~50%** of the time and closes back past the range mid only ~32–33%. **Continuation is the base case; the full sweep-reversal is the minority pattern.** Trade reversals only with explicit confirmation (displacement back through the range), never by default.

### 5.2 Prior-day levels

- P(touch prior-day high) = 52.1%, P(touch prior-day low) = 44.4%, **P(touch either) = 85.6%**, inside days only 14.4%. PDH/PDL are legitimate first targets for any intraday position.
- Once touched, close-through vs rejection is a coin flip (52.6% close above PDH; 48.8% close below PDL) — the *touch* is predictable, the *resolution* is not. Take partials into the level.

### 5.3 Weekend gaps

Mean |gap| = 10% of ATR. No directional bias (45% up). **89% of all gaps fill within 24h — but only 60% of large gaps (>15% ATR) do.** The gap-fill trade only "works" on gaps too small to pay for after costs; the big tempting ones fail 40% of the time. Skip it as a system; use unfilled Friday-close levels as Monday magnets instead.

## 6. Strategy backtests (all net of $0.40/oz round-trip cost)

Cost model: $0.30 spread + $0.10 slippage per round trip. Expectancy in % of daily ATR; "R-on-risk" = P&L / entry-to-stop distance. Full year-by-year tables in `output/03_backtests.txt` and `output/05_practical.txt`.

| # | Strategy | Trades | Win% | Expectancy | Sharpe | MaxDD | Verdict |
|---|----------|--------|------|------------|--------|-------|---------|
| S1 | **Overnight long 20:00→02:00**, Mon–Thu | 1,017 | 54.1 | +2.78% ATR | **1.95** | −5.3R | ✅ best edge in the data |
| S1s | S1 with 0.5-ATR stop | 1,017 | 53.6 | +2.30% ATR | 1.59 | −5.9R | ✅ edge survives a stop |
| S1t | S1 + close>SMA20 filter, 0.5-ATR stop | 596 | 52.9 | +2.67% ATR | 1.74 | −5.4R | ✅ better per-trade, fewer trades |
| S3a | **NY ORB**: 13:30+30m range, breakout→20:00, stop far side | 1,252 | 42.3 | +2.05% ATR (+0.083 R-on-risk) | 0.97 | −4.9R | ✅ genuine, modest |
| S3a2 | NY ORB + 2R take-profit | 1,252 | 44.1 | +1.32% ATR | 0.73 | −6.5R | ⚠️ TP hurts — edge is in the tails |
| S2a | Asian-range breakout 07:00–14:30, stop far side | 1,180 | 44.0 | +1.31% ATR | 0.42 | −16.9R | ⚠️ marginal, 2 losing years |
| S2b | Same + buffer, tight 0.33-ATR stop | 1,114 | 40.9 | −0.55% ATR | −0.20 | −22.7R | ❌ tight stops kill it |
| S3b | NYSE-open ORB (14:30) | 1,251 | 43.0 | +0.11% ATR | 0.06 | −6.8R | ❌ dead |
| S4 | Midday continuation (12:00 beyond Asian range → hold) | 550 | 40.9 | +0.05% ATR | 0.01 | −12.0R | ❌ dead (longs −0.04R: buying extension late is toxic) |

Reading the table like a 30-year desk veteran:

1. **The overnight drift (S1) is the only statistical edge in this data I'd call *strong*** — t≈5.5 on the underlying segment, positive every year, survives costs, survives a stop, survives regime change. Its one bad year (2022, −0.02R/trade) was the Fed-hiking chop. Caveat that matters: a 20:00→02:00 hold crosses the swap cut — on most CFD brokers long-XAUUSD swap is *negative* (typically $0.3–0.8/oz/night, 3× Wednesday). At avg +$1.81/oz/trade gross-of-swap, **check your broker's swap before trading this**; on a high-swap account, take the 22:00→02:00 version only (avg +$1.22, no full-night financing on some brokers) or trade it via futures/micro-futures.
2. **NY ORB is real but humble** — +0.08R per trade at 42% win rate means long losing streaks; its money comes from the ~15% of days that trend hard out of the NY open. Never cap it with a take-profit (2R TP cut expectancy by a third). Let it run to 20:00.
3. **Breakouts pay with *wide* stops (structural), die with tight stops.** S2a (far-side stop) vs S2b (0.33-ATR stop) is the cleanest demonstration in the data: identical entries, +1.31% vs −0.55% ATR. In a 1m/5m book this is the #1 behavioural error to avoid.
4. **Late continuation entries are dead** (S4). If you missed the break at the level, wait for the next day. Chasing at 12:00 after London has extended is the worst trade in this study, especially longs.

## 7. What I'd actually do (the desk view)

If I had to make money from this instrument with this data, my book would be, in order of allocation:

1. **Carry the overnight drift systematically** (S1 family) — small, always-on, ATR-sized, Mon–Thu, with a 0.5-ATR disaster stop. This is the "collect the anomaly" leg. It is boring and it is the best risk-adjusted return here.
2. **Trade the NY open aggressively but structurally** (S3a) — the 13:30–15:00 window is where daily extremes are made. ORB with the far-side stop, no TP, flat by 20:00. Accept 42% win rate; the tail days pay the month.
3. **Use the Asian range as the day's map, not as a signal.** One-side break = trend day (70% close-through) → trade *with* it on 5m pullbacks; both-sides-broken by noon = range day → fade extremes back to the mid. Reversal trades only on confirmed displacement back inside the range.
4. **Target PDH/PDL** (85.6% touch rate) for take-profits; take partials at the level because resolution is a coin flip.
5. **Size everything off ATR20 and re-size weekly.** The instrument's unit of movement changed 6× over the sample; the trader who kept fixed lots through Feb 2026 ($205 ATR) either blew up or was flat.

What I would *not* trade: bar-level momentum or mean-reversion (autocorr ≈ 0), round-number strategies, weekend-gap fades, the NYSE-open ORB, midday continuation chases, and default "Judas swing" reversals without confirmation.

## 8. Honest limitations

- Single broker feed (cTrader CFD); volume is tick-volume, not COMEX volume.
- Cost model is flat $0.40/oz; spreads widen 3–10× around 13:30 data releases and the 22:00 reopen — the ORB entries near 14:00 are conservative, but any strategy *entering exactly at 22:00* needs a limit-order implementation. Swap/financing not modelled (flagged on S1).
- No news filter: NFP/CPI/FOMC days are in every backtest. The ORB numbers include them (that mostly *helps* it); the overnight numbers are hardly news-sensitive.
- Session boundaries are fixed UTC; US/UK DST shifts smear event times ±1h across ~30% of the year. Sharper edges are likely obtainable with exchange-clock alignment.
- 2026 is a live, violent regime ($100+ daily ranges, correction off 4,500). Every ATR-normalised edge above held in 2026, but position sizes that felt "normal" in 2024 are 4× too big now.
