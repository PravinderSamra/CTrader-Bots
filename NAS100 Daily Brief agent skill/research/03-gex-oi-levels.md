# 03 — GEX, Open Interest & the Gamma Level Board

**Headline finding: we can build a genuine, professional-grade gamma map for
NAS100 for free, with no API key, from CBOE's own public delayed-quote feed.**
No vendor subscription, no scraping, no sign-up.

---

## 1. The data

Two endpoints, both keyless, both confirmed live (doc 02):

```
https://cdn.cboe.com/api/global/delayed_quotes/options/_NDX.json   # 7.2 MB
https://cdn.cboe.com/api/global/delayed_quotes/options/QQQ.json    # 5.3 MB
```

Every contract row carries `open_interest`, `volume`, `iv`, `delta`, `gamma`,
`vega`, `theta`, `rho`. That is the complete input set for a real GEX build —
it is the same upstream data the paid vendors resell.

**Both chains are required.** NDX index options are where institutional hedging
sits; QQQ is where the volume is. Using NDX alone under-counts dealer gamma
badly. `prototypes/gex_levels.py` loads both and scales QQQ strikes into NDX
points with the live NDX/QQQ ratio (**41.034** measured 2026-08-22), giving one
combined book: **3,608 NDX + 3,943 QQQ contracts** inside 45 DTE.

**Translating to your chart.** Everything above is in NDX index points. The
brief must convert to your Pepperstone NAS100 CFD price:

```
offset      = NAS100_CFD_mid − NDX_cash_spot
NAS100level = NDX_strike + offset
```

Measured on 2026-08-22: NDX 29,308.9 vs CFD 29,290.5 → **offset −18.4**. This
offset drifts with the futures basis and must be recomputed every run, never
hardcoded.

---

## 2. The maths

```
$GEX(strike) = gamma × OI × 100 × Spot² × 0.01      # $ of dealer delta per 1% move
Net GEX      = Σ call $GEX − Σ put $GEX
```

**Dealer sign convention.** We assume dealers are long calls / short puts —
the standard approximation, and the one the existing `GEX&OI` project uses. It
is an *approximation*: true dealer inventory is unobservable. It is reliable
enough for **ranking strikes and locating the flip**, which is what we need. It
is not reliable as an absolute dollar figure, so the brief should quote regime
and levels, never present "$X bn of gamma" as a precise fact.

**Gamma flip (zero-gamma level).** Not a simple cumulative sum — that is the
common shortcut and it is wrong, because gamma itself changes as spot moves.
`cboe_gex.py:gamma_flip()` re-prices the *entire book* with Black–Scholes gamma
across an 81-point spot grid spanning ±8%, holding each contract's own IV
fixed, and interpolates where total net GEX crosses zero. Risk-free rate comes
from `^IRX`.

**Expiry buckets.** Gamma is overwhelmingly concentrated in near-dated
contracts, and 0DTE now dominates intraday behaviour. The engine reports three
buckets separately — `0–2 DTE`, `this week (≤7)`, `full ≤45 DTE` — because they
often disagree, and *that disagreement is itself a signal* (see §5).

---

## 3. The level board — what each level IS and how to trade it

This is the list to mark on the chart each morning. Priced in NAS100 CFD terms.

### A. Gamma flip / zero-gamma level — **the most important line on the chart**
**What it is:** the price at which total dealer gamma crosses zero.

**Above it — positive gamma.** Dealers are long gamma and hedge *against* the
move: they sell rallies and buy dips. Realised volatility compresses, moves
mean-revert, ranges hold.
**Below it — negative gamma.** Dealers are short gamma and hedge *with* the
move: they sell into weakness and buy into strength. Volatility expands, trends
persist, dips do not get bought.

**Reaction to look for:** the flip acts as a **volatility switch, not a
support/resistance level**. Price crossing it is rarely rejected cleanly; what
changes is the *character* of everything afterwards. Expect a visible change in
candle size on the 1m within 15–30 minutes of the cross.

**Direct impact on your strategies:**
- **Above the flip → strategy 1 is the right tool.** Sweeps of PDH/Asia High
  genuinely fail here because dealers are actively fading them. Your LH-after-
  bullish-sweep forms cleanly.
- **Below the flip → strategy 1 is dangerous, strategy 2 is the right tool.**
  A sweep below the flip usually keeps going; the "failed break" you wait for
  doesn't form, and you get stopped at the sweep extreme. Switch to the CISD →
  HH/HL → OTE continuation model and trade *with* the expansion.
- Crossing the flip mid-trade is a **management trigger**: if you are in a
  strategy-1 mean-reversion trade and price breaks below the flip, tighten or
  exit — your edge just inverted.

*Worked example 2026-08-22: flip at NAS100 **29,327**, price 29,290 → **below the
flip, short-gamma regime**. Strategy 2 is favoured; strategy-1 fades need the
reclaim of 29,327 first.*

### B. Call wall — largest call gamma above spot
**What it is:** the strike where dealers hold the most long call gamma. To stay
hedged they must **sell the index as it rises into that strike**.

**Reaction to look for:** the strongest *magnetic ceiling* on the board. Price
grinds toward it and stalls. Rallies into the call wall lose momentum on the
1m — smaller candles, longer upper wicks. This is a **prime strategy-1 short
sweep level**: price pokes above, fails, prints a lower high, CISD → short.

**Above vs. below it:**
- Below the call wall: dealer selling caps upside; the wall is the realistic
  upper bound of the day's range. Target it, don't trade through it.
- **Through and holding above it:** the dealer hedge inverts. They are now
  short delta into a rising market and must **buy** — this is the classic
  *gamma squeeze*. A clean 1m close and hold above the call wall flips it from
  resistance to a launchpad. This is a strategy-2 setup, not a fade.

*Worked example: call wall NAS100 **29,381.6** (this week, $0.56bn, 8,657 OI) —
which is also exactly where **max pain** sits (29,381.6). Two independent
methods landing on the same price makes it the single strongest magnet/ceiling
on the board.*

### C. Put wall — largest put gamma / OI below spot
**What it is:** the strike with the heaviest put open interest below spot,
where downside hedging is concentrated.

**Reaction to look for:** a **defended floor while the market is in positive
gamma**. Price approaches, decelerates, wicks, and reverses as put holders take
profit and dealers unwind short hedges. A strong strategy-1 long sweep level:
price pokes below, fails, prints a higher low, CISD → long.

**Above vs. below it — and this is the part that costs people money:**
- Above the put wall in **positive** gamma: genuine support, fade the sweep.
- **Below the put wall, or in negative gamma:** it inverts. Dealers short
  gamma must sell into the decline, and a break of the put wall is where the
  **acceleration** happens, not where it stops. In a negative-gamma tape, treat
  a put-wall break as a *continuation short trigger*, never a bounce.

*Worked example: put wall NAS100 **29,181.6** this week (7,091 OI), with a far
larger structural wall at **28,681.6** on the full 45-DTE book (168,275 OI —
the biggest single concentration anywhere on the chain). 29,181.6 is today's
floor; 28,681.6 is the week's floor.*

### D. Max pain
**What it is:** the strike minimising total option-holder payout at expiry —
the price the aggregate book "wants" at the bell.

**Reaction to look for:** a weak magnet that strengthens sharply as expiry
approaches. Irrelevant on a Monday, meaningful on Thursday, strong on a Friday
OPEX. When max pain and the call wall coincide, treat it as a hard pin.

*Worked example: **29,381.6**, coincident with the call wall.*

### E. High-|GEX| strike bins (the pin/reaction shelf)
**What it is:** the individual 50-point bins carrying the largest absolute net
gamma, regardless of sign.

**Reaction to look for:** these are where intraday price gets *sticky*. Large
**positive** bins pin price (chop, poor R:R for continuation, good for fades).
Large **negative** bins are acceleration zones (price moves *through* them
faster, good for continuation, bad for fades).

The brief should print these as a ranked shelf with the sign attached, because
the sign tells you whether to expect a stall or a slide at each shelf.

*Worked example, this-week bucket:*
| NAS100 level | Net GEX | Expect |
|---|---|---|
| 29,381.6 | **+0.290 $bn** | Pin / stall — the call wall, fade longs into it |
| 30,131.6 | +0.112 $bn | Pin, far above — upside cap if the day trends |
| 29,081.6 | −0.131 $bn | Acceleration — price slices through, don't fade |
| 28,981.6 | −0.122 $bn | Acceleration |
| 28,931.6 | −0.179 $bn | Acceleration |
| 28,681.6 | **−0.201 $bn** | Structural put wall; break = downside expansion |

### F. Max OI strikes (distinct from max GEX)
**What it is:** raw contract concentration, ignoring gamma weighting.

**Reaction to look for:** these are **psychological / expiry-magnet** levels
rather than hedging-flow levels. Far-OTM max-OI strikes (e.g. 31,381.6 call OI
64,290; 23,581.6 put OI 4,923) are *not* intraday levels — they are the market's
tail-risk boundaries and belong in the "context, not target" section of the
brief. Do not mark far-OTM OI as a chart level; it will only clutter.

---

## 4. Reading the whole regime in one line

| Net GEX | VIX9D/VIX | Regime | Which strategy |
|---|---|---|---|
| Positive, spot above flip | < 0.95 (contango) | **Pinned range** | Strategy 1 at the walls. Small targets, high hit-rate |
| Positive, spot near flip | ~1.0 | **Unstable pin** | Reduce size; the flip is in play |
| Negative, spot below flip | < 0.95 | **Grinding trend** | Strategy 2 with-trend; strategy 1 only at the far walls |
| Negative, spot below flip | > 1.0 (backwardation) | **Expansion / air pocket** | Strategy 2 only. Widen stops, expect ADR to be exceeded, trail aggressively |

---

## 5. When the expiry buckets disagree — a real signal

*Worked example 2026-08-22:*
- `0–2 DTE`: net **−0.291** $bn — near-dated book is short gamma
- `this week`: net **−0.331** $bn
- `full 45 DTE`: net **−0.943** $bn

All three negative and deepening with tenor. That is a **coherent short-gamma
structure** — the market is genuinely positioned for movement, not just noise
in the front expiry. Conviction in the "expect expansion" read is high.

Where they *disagree* — e.g. 0DTE strongly positive while the full book is
negative — you get a **pin now, expansion later** day: chop through the morning
that resolves violently in the last two hours as 0DTE gamma decays away. That
pattern is worth calling out explicitly, because it tells you to be patient
early and aggressive late.

---

## 6. Honest limitations

1. **15-minute delay.** Fine for a pre-session level map. It means intraday
   0DTE gamma drift is not live. Re-run mid-session if you want it current.
2. **Dealer convention is an assumption** (see §2). Levels and regime are
   robust; absolute dollar figures are not.
3. **QQQ↔NDX scaling** uses a spot ratio. It ignores the small tracking
   difference and dividend timing. Immaterial at 50-point bin resolution.
4. **No dealer-inventory data exists publicly.** Anyone claiming exact dealer
   positioning — free or paid — is running the same assumption we are.
5. **Weekend staleness varies by chain.** On the test run the NDX chain
   timestamped 09:42 and QQQ 03:44. The brief must print both `as_of` stamps
   and warn when they diverge by more than an hour.
