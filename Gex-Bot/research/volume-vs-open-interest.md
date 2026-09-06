# Volume vs open interest — and the history mistake that delayed answering it

**Status:** open question. Method established; one session analysed (not
enough). The *composition* of both readings is now settled — see Part 3.
**Last updated:** 2026-09-05.

This file is written to be read cold, by someone with no context on this
project — including another Claude session investigating a similar question.
It has five parts:

1. **A research-methodology failure** and how it was corrected. Generalisable;
   read this even if you do not care about options data.
2. **The volume-vs-open-interest analysis** itself: question, method, results
   so far, and what would actually settle it.
3. **What the two readings actually are**, established by rebuilding the
   vendor's numbers from free public data. This is the most consequential
   section: it shows the two readings differ by *recency*, not by direction
   of flow, and that both rest on the same unverifiable assumption.
4. **How to get more history**, and what it costs.
5. **What the academic literature says**, and how far it can be trusted here.

> **On sourcing:** this repository is public and GexBot is a paid
> subscription, so this file describes findings in our own words and does not
> reproduce the vendor's documentation, data, or computed levels. Figures
> quoted are summary statistics from our own analysis.

---

# Part 1 — The history mistake

## The wrong conclusion

For most of this project I asserted, in writing and in several places:

> The API serves only a live snapshot. There is no history endpoint on our
> tier. Anything not recorded as it happens is gone. We can only start now.

This drove a real design decision: build a recorder polling every 5 minutes
during the session, and wait a week to accumulate enough data to answer
anything. That framing was presented as urgent — *every day without it is a
day of data you can never get back.*

**It was wrong.** History was available the whole time, at roughly 200×
the resolution the recorder produces.

## How the error was made

Endpoint discovery by guessing. Paths were probed that seemed plausible —
`/hist`, `/history`, `/historical`, `/download`, `/{ticker}/history`, and
several more — all returned 404. From that the conclusion drawn was "no
history on this tier."

The flaw is simple once named: **a 404 on a guessed path is evidence the
guess was wrong, not evidence the capability is absent.** The probe tested
the imagination of the person writing it, and that was mistaken for a test of
the API.

A second error compounded it. The vendor's documentation page had been
"checked" — a text fetch returned nothing useful, and it was treated as
absent. It was not absent. It was *unreadable by the method used*.

## What actually found it

The docs page is a client-side route in a React single-page app. Fetching it
returns the same ~2.8 KB shell as every other route, containing only
`You need to enable JavaScript to run this app.` Byte-identical for `/` and
`/docs`, which is the tell.

A headless browser would normally solve this, but the sandbox's browser could
not reach external hosts (its proxy tunnels closed mid-handshake, while `curl`
to the same host returned 200 — worth checking both before concluding a site
is blocking you).

What worked: **the documentation content is compiled into the app's JavaScript
bundle.** The bundle is linked from the HTML shell, fetches fine with `curl`,
and contains the field reference as structured data — field name, type, and
description — plus the full route table. Extracting it with a regex gave 87
documented fields and every API path, in about two minutes.

### The generalisable lesson

- **A 404 from a guessed path proves nothing about capability.** Find the
  route table; do not invent it.
- **"The docs page returned nothing" is a statement about your fetcher**, not
  about the docs. A single-page app serves the same shell for every route.
- **When a site is JS-rendered and you cannot run a browser, read the
  bundle.** Documentation, route tables, API schemas and field descriptions
  are routinely compiled into it as plain data.
- **Compare the byte size of two different routes.** Identical sizes mean
  client-side routing, and tell you immediately that fetching more URLs will
  not help.
- **Check more than one client.** `curl` succeeding where a browser fails
  (or the reverse) localises the problem to your tooling rather than the
  remote host.

### The lesson had to be learned twice

The bundle was extracted, and then *not read again*. Later, asked whether
history existed for dates other than the last session, the same mistake
repeated in a smaller form: probing `?date=`, `?day=`, `?session=` and
reading the identical responses as evidence, instead of opening the contract
that had already been pulled out of the bundle and was sitting in the working
directory.

Two minutes in that file would have said, without any probing:

- the endpoint declares **no query parameters**, so no variant was ever going
  to work;
- today's report appears only after the evening export, and before then the
  endpoint returns the prior session **silently** — a failure mode probing
  would never have revealed, because every response is a valid 200;
- the endpoint requires headers we were not sending;
- the dated archive exists and is gated to a higher tier with a **rolling
  90-day window** — the single most useful fact for planning, and entirely
  invisible from the outside.

And then a third time. Part 3 reconstructs GexBot's per-strike numbers from
free public data to establish which dealer-inventory sign convention is in
use — a genuinely useful exercise, run without first checking that the FAQ
answers it in one sentence. It does: Classic is described there as *naive
GEX*, all calls positive and all puts negative, with a companion paragraph
conceding that volume cannot distinguish a buy from a sell. The measurement
confirmed the documentation to two decimal places. The same FAQ also carried
the licensing terms this project had been guessing at, a documented answer to
the volume-vs-OI reconciliation, and a whole *Historical Data* section — none
of which had been read, because the search had been for endpoints rather than
for answers.

The generalisable form: **the cost of reading documentation is bounded and
small; the cost of inferring behaviour from responses is unbounded and the
inferences are frequently wrong.** Probing tells you what happened once.
Documentation tells you what is guaranteed, what is silent, and what exists
but is not yours yet. When someone hands you a documentation link, that is
not context — it is an instruction.

And read *all* of it, not the part matching your current search term. Three
of the four things this project spent the most effort on — the sign
convention, the licensing position, and whether history could be bought —
were sitting in an FAQ the whole time, in categories nobody had opened.

## What is actually available (Classic package, verified)

| Endpoint | Result | Meaning |
|---|---|---|
| `/{ticker}/classic/{zero\|one\|full}` | 200 | Live snapshot, full strike ladder |
| `/{ticker}/classic/{period}/majors` | 200 | Wall levels only — never found by guessing |
| `/{ticker}/classic/{period}/maxchange` | 200 | Max-change panel — likewise |
| **`/hist/eod/{ticker}`** | **200** | **Completed session, full day** |
| `/v2/hist/{ticker}/{package}/{category}/{date}` | 403 | Dated archive — Quant tier |
| `/v2/negotiate` | 403 | WebSocket — Quant tier |
| `/tickers`, `/{package}/categories` | 200 | Public, no token |

The EOD report for one ticker is a ~20 MB zip holding one gzipped JSON per
expiry scope. For NQ_NDX on 2026-09-04:

```
15,131 samples   13:30:16 → 19:59:59 UTC   1–2 second intervals
143 strikes per sample, each with volume GEX, OI GEX and prior samples
```

Compare with the recorder: **78 samples a day at 5-minute spacing.** The EOD
report is roughly 200× denser and covers a session that had already happened.

### Two limits, verified rather than assumed

- **The endpoint takes no parameters at all.** This was first established
  empirically — every `?date=` variant returned a byte-identical file, with
  the `content-disposition` filename naming the most recent session
  regardless of what was asked, across dates a year apart. It was then
  *confirmed in the vendor's published contract*, which lists the endpoint's
  query parameters as an empty set and states that it returns the latest
  available report for the ticker. There was never a parameter to find.
- **Today's report only exists after the vendor's evening export.** Before
  that, the endpoint returns the **previous** session's report — with a 200
  and no error of any kind. A daily job that runs too early therefore
  silently archives yesterday twice and loses today permanently. This is why
  `archive_eod.py` takes `--expect-date` and `--fail-if-stale`, and why the
  workflow's cron sits after the export rather than at the close.
- **Backfill is impossible on this tier.** The dated archive that would allow
  it is 403. A session not downloaded on the day is lost — the same
  conclusion as before, but for the correct reason and one day at a time
  rather than for all history. See Part 4 for what would lift this.

## The corrected design

`scripts/fetch_eod.py` downloads the report. `scripts/archive_eod.py` derives
what the research needs and stores only that, run daily by
`.github/workflows/gexbot-eod.yml`.

The raw report is **not** retained: it is paid vendor data and this repository
is public. What is stored per session (~330 KB) is the agreement statistics, a
touch-test parameter sweep, and a downsampled series of spot and the four wall
levels at 10-second steps.

Keeping the *series* rather than only summary statistics is the deliberate
part. Storing conclusions alone would freeze today's analysis parameters into
the archive permanently; keeping spot and the walls means the touch test can
be re-run at any tolerance or horizon, across every session ever archived,
without re-fetching anything.

The 5-minute recorder still runs. It is now the coarse live feed for the
dashboard, not the primary research instrument.

---

# Part 2 — Volume vs open interest

## The question

GexBot reports every gamma level twice: once weighted by **session volume**,
once by **open interest**. Both are available at every strike and for the
headline wall levels.

The two primary sources for this strategy disagree about which to use:

- A walkthrough by the strategy's author states plainly that the volume
  reading is the one they track, and describes the product as netting call
  and put **volume** at each strike.
- A later long-form interview by the same person describes reading **90-day
  open interest** before the session to see how the market is positioned.

They may be complementary — open interest for structural positioning before
the open, volume for what is happening now — but that is a hypothesis, not an
established fact.

> **Read Part 3 before acting on this section.** The reconstruction there
> shows the "volume" reading is *not* a measure of flow direction, which
> narrows what the question can even mean.

## Why it is not a cosmetic choice

The two readings frequently disagree, and the disagreement is large. From
15,131 samples across one full session (NQ_NDX 0DTE, 2026-09-04):

| | |
|---|---|
| Call wall at the **same strike** | **42.2%** of samples |
| Put wall at the **same strike** | **1.0%** of samples |
| Median gap, call wall | 20 points |
| Median gap, put wall | **150 points** |
| Same regime sign (net GEX) | **57.3%** of samples |

The put wall reading is essentially never the same strike, and the two
readings disagree about whether dealers are long or short gamma **43% of the
time**. A system built on the wrong one is not marginally worse — it is
inverted for nearly half the session.

This is the well-powered part of the analysis. It rests on 15,131
observations, not on a handful of events.

## Method — "touch and reaction"

Implemented in `scripts/analyse_vol_vs_oi.py`.

1. Walk the session sample by sample. A **touch** is spot coming within
   `tol` points of a wall. Consecutive samples near the same wall are one
   event; a `cooldown` gates re-arming, so a slow approach is not counted as
   hundreds of touches.
2. After each touch, look `horizon` minutes forward.
3. A wall is **respected** if price moved away from it in the direction the
   wall implies — down from a call wall, up from a put wall.
4. Compare respect rates between the volume walls and the OI walls.

**The control is as important as the test.** On a day that fell all
afternoon, "price was lower 15 minutes after touching resistance" is true of
almost any moment. The report therefore also gives the unconditional base
rate of down-moves over the same horizon. A wall that merely matches the
day's drift has demonstrated nothing.

## Results — one session

Baseline over 15 minutes, sampled across the session with no wall involved:
**46.8% lower, 53.2% higher.** So roughly a coin flip, very slightly upward.

Touch-test respect rates, swept across parameters:

| tol (pts) | cooldown | Volume call | Volume put | OI call | OI put |
|---|---|---|---|---|---|
| 5 | 15 min | 1 touch, 0% | 6, 50% | 8, 50% | 3, 67% |
| 10 | 15 min | 4, 50% | 9, 44% | 10, 50% | 3, 67% |
| 25 | 15 min | 7, 29% | 14, 57% | 12, 50% | 4, 50% |
| 50 | 5 min | 36, 31% | 58, 59% | 54, 44% | 16, 31% |

## Conclusion so far: inconclusive, and the reason matters

**No wall type shows a respect rate distinguishable from the 47/53 baseline.**
Every cell sits near a coin flip.

More tellingly, the rates move *erratically* as parameters widen — the volume
call wall reads 0%, then 50%, then 29%, then 31%. A real effect would degrade
smoothly as the tolerance admits more marginal touches. Jumping around like
that is the signature of small-sample noise, and the touch counts explain why:
at a usable tolerance there are **single-digit events per wall per day**.

Loosening tolerance to 50 points buys more events, but a "touch" 50 points
from a wall on an instrument with a 230-point daily range is not a touch in
any meaningful sense. The sample cannot be inflated into significance.

**One session cannot answer this question.** That is a statement about
statistical power, not about the method — which runs, is parameterised, and
is now pointed at an archive that grows daily.

### What would settle it

- **20–30 sessions**, giving low-hundreds of touch events per wall type.
  At roughly 10 usable touches per session, that is 4–6 weeks of the daily
  archive.
- **Condition on regime.** The theory predicts walls behave differently when
  net GEX is positive (suppression, mean reversion) versus negative
  (amplification, trend). Pooling both may be cancelling a real effect. The
  archived series carries both net GEX readings per sample, so this is
  testable retrospectively.
- **Test the first two hours separately.** The strategy's author trades only
  that window and is explicit that later hours are dominated by different
  greeks. A whole-session test may be diluting the period the claim is
  actually about.
- **Test the pre-open OI levels specifically**, rather than intraday OI. The
  interview's claim is about positioning read at the open — a different
  proposition from the intraday OI walls tested here.

Until then: **neither reading is established as correct, and the dashboard
shows both without picking one.**

## Reproducing this

```bash
export GEX_BOT_API_TOKEN=...

# The most recent completed session (~20 MB)
python3 scripts/fetch_eod.py --ticker nq_ndx --out-dir ./eod

# Analyse it
python3 scripts/analyse_vol_vs_oi.py --zip ./eod/eod_report_NQ_NDX_*.zip

# Sweep the parameters
for tol in 5 10 25 50; do
  python3 scripts/analyse_vol_vs_oi.py --zip ./eod/*.zip --tol $tol
done
```

## Caveats a reader should carry forward

- **One session, one instrument, one expiry scope.** 2026-09-04 NQ_NDX 0DTE,
  a −11 point day on a 230 point range. Nothing here generalises yet.
- **Not a strategy backtest.** No entries, stops, costs or slippage. It tests
  one narrow claim: does price turn at these levels more often than chance.
- **Walls move intraday.** Each touch is tested against the wall as it stood
  at that moment, which is correct but means "the wall" is not one fixed
  price across the day.
- **Some large volume walls are probably phantoms, and the test cannot tell.**
  The vendor describes nodes where "all those orders are matched — even though
  there's a lot of volume, that level isn't necessarily super important,
  because there's no disagreement about that level." A matched node leaves
  nobody holding an imbalance to hedge. Naive volume GEX cannot distinguish
  that from a real wall, so the touch sample is diluted with levels that were
  never going to do anything. This is a plausible reason for a near-coin-flip
  result that does not require the approach to be wrong — and it is the
  specific thing the State package's classification is built to filter.
- **The performance claims that motivated this project are unverified.** The
  75% win rate, 1:10 reward-to-risk and "a stop every two or three weeks"
  quoted by the strategy's author come from promotional videos with no
  statistics shown. They are the hypothesis, not the baseline.

---

# Part 3 — What the two readings actually are

Part 2 treats "volume GEX" and "OI GEX" as two competing measurements and asks
which one price respects. That framing quietly assumes something about what
they measure. This part tests that assumption instead of inheriting it, and
the answer changes the question.

## The assumption at the bottom of every gamma level

Gamma is a property of a contract. **Gamma exposure is a property of a
position**, and a position has a side. To turn one into the other you must
assert who is holding what — and no public data feed knows that. Exchanges
publish volume and open interest; they do not publish who was long.

The near-universal convention resolves this by assumption: dealers are **long
calls and short puts**, so call gamma enters positive and put gamma negative.
That is the formula in every retail GEX tool. It is an inventory guess. If it
is wrong, every wall in the ladder has the wrong sign, support and resistance
swap, and the regime read inverts.

So: does GexBot use that convention, and is that all it is doing?

## The test

`scripts/sign_convention_test.py`. The method is reconstruction:

1. Take the final sample of a GexBot EOD report for the **next expiry** scope
   (`gex_one`) — one expiry, unambiguous.
2. Download Cboe's **free, public, unauthenticated** delayed NDX chain, which
   carries per-contract gamma, open interest and session volume.
3. Recover the strike basis. GexBot quotes NQ-futures-adjusted strikes; the
   chain quotes NDX strikes. They differ by one constant, recovered by voting
   across strike pairs and tie-broken by the observed spot difference — the
   regular NDX strike grid means an offset fifty points wrong still aligns
   every strike, so alignment count alone is not enough.
4. Aggregate `Γ × OI` and `Γ × volume` per strike, per side.
5. Fit all four sign conventions against GexBot's published per-strike values.

Only `gex_one` can be tested, and that limit is worth stating precisely: the
session's own 0DTE contracts have already expired and dropped out of the free
chain by the time the EOD report exists, so `gex_zero` cannot be reconstructed
at all and `gex_full` — which contains them — reconstructs only weakly
(r ≈ 0.38 at any expiry window). This is a property of the free data, not a
defect in the method.

## Result

NQ_NDX, 2026-09-04 final sample, next expiry 2026-09-08, ~110 strikes:

| Convention | Open interest | Volume |
|---|---|---|
| **A  +calls −puts** (dealers long calls, short puts) | **r = +0.974, r² = 0.95** | **r = +0.978, r² = 0.96** |
| B  −calls +puts (inverted) | r = −0.974 | r = −0.978 |
| C  +calls +puts (no directional assumption) | r = +0.423 | r = +0.716 |
| D  −calls −puts | r = −0.423 | r = −0.716 |

B is not a rival hypothesis — it is A with the sign flipped, and only A
reproduces the levels rather than their mirror image. C and D are decisively
rejected.

The fitted scale settles the units as well. Under convention A the regression
slope is **98% of** `Γ × OI × 100 × S² × 0.01` expressed in millions — the
textbook "notional gamma per 1% move, in $m". The remaining 2% is comfortably
explained by the chain being a delayed end-of-day snapshot against a 15:59
sample.

**GexBot Classic is computing the standard formula with the standard sign
convention, in the standard units.** Nothing proprietary is happening at this
layer. That is a useful thing to know: it means the *levels* are reproducible
and the value of the subscription is latency, coverage and packaging, not a
secret model.

> **This was documented before it was measured.** The vendor's FAQ describes
> Classic as *naive GEX* — all calls treated as positive gamma, all puts
> negative, from the OCC's daily open-interest tally — and contrasts it with
> the State package's classified order flow. The metrics page goes further
> and says outright that opening/closing data is not available intraday and
> that wide spreads and mid-price prints make it hard to tell from Time &
> Sales whether an option was bought or sold, describing volume as an
> *"intermediary solution"* giving a *"rough idea"* of hedging.
>
> The founders say the same thing on camera, in their own walkthrough
> (2023-10-14): *"so far our classic gexbot, we're making the assumption
> where **all puts are bought and all calls are sold**, and therefore the
> naive gex still works generally well"*, and elsewhere *"assuming that puts
> are negative gamma and calls are positive gamma"*. Customers buying puts
> and selling calls means dealers short puts and long calls — convention A,
> stated outright.
>
> So the reconstruction below confirmed the documentation rather than
> discovering anything the vendor had hidden. It still earns its place — it
> pins the *scale* to 98% of textbook, proves the levels are reproducible
> from free data, and turns "they say it is naive" into "we have verified it
> is naive at r ≈ 0.97". But the reading order should have been documentation
> first. See Part 1: this was the third time in this project that behaviour
> was inferred from probing when it was written down.

## The consequence, and it is the important one

Run the same fit against **volume** and the winner is the same convention,
with the same call-positive/put-negative sign, at essentially the same scale.

That means the volume reading is:

```
Σ Γ × (calls traded today)  −  Σ Γ × (puts traded today)
```

using **raw, unsigned contract volume**. Not buyer-initiated minus
seller-initiated. Not opening minus closing. Just how many contracts changed
hands, with the side *assumed* exactly as it is assumed for open interest.

This is not a criticism of the vendor — raw volume carries no side, and no
free or Classic-tier feed anywhere publishes signed options flow. It is a
correction to how the two readings should be interpreted:

> **The volume and OI readings do not differ in what they know about
> direction. They differ only in recency.** Open interest is every contract
> still outstanding, sign assumed. Volume is the contracts that traded today,
> sign assumed identically. One is a stock, the other a flow, and both inherit
> the same unverifiable dealer-inventory assumption.

Three things follow:

1. **"Volume shows what dealers are doing now" is wrong as stated.** It shows
   what *traded* today. A strike where customers aggressively sold calls and
   one where they aggressively bought them are indistinguishable in this
   number, and are assigned the same sign.
2. **The two readings cannot disagree about direction, only about horizon.**
   The 43%-of-the-session regime disagreement documented in Part 2 is
   therefore a disagreement between *today's turnover* and *the standing
   book* — which is a meaningful and tradeable distinction, but a different
   one from the one the source videos imply.
3. **The touch test in Part 2 remains the right test**, but what it is
   choosing between is now precisely defined: a recency-weighted level versus
   a stock-weighted level, not "flow" versus "positioning".

## The convention is scoped to SPX — and we do not trade SPX

The same walkthrough carries a limit that neither of the trader videos
mentions and that this project had not identified:

> "this is really something that's **only true for SPX**, due to the nature of
> the agents who are actually trading SPX. Now **for individual equities,
> generally that assumption does not hold**, and so making an assumption like
> that can really distort what the actual landscape looks like."

The naive sign assumption is not offered as a universal truth. It is offered
as an empirical claim about **who trades SPX**, verified by the vendor against
their own classified data for SPX, and explicitly denied for single stocks.

**We trade `NQ_NDX`.** An index sits on the SPX side of that line rather than
the single-stock side, but NDX is not SPX, its participant mix is not SPX's,
and the vendor makes no claim about it — at the time of that video NDX was not
even a covered ticker.

This matters more than anything else in Part 2, because it is not a question
our archive can answer. Every level we record already has the assumption baked
in. Touch-testing volume walls against OI walls compares two readings that
share the assumption; if the assumption is wrong for NDX, both are distorted
and the test cannot see it. **This is now the single best question to put to
the vendor**, and the reason the trader in the source videos may take his
levels from SPX and merely *execute* on NQ.

## What would falsify the sign convention itself

Nothing above validates convention A as *true* — only that GexBot uses it,
says so, and claims to have verified it for SPX specifically. Establishing whether dealers really are net long calls and short
puts requires data that says which side initiated each trade, and which of
those trades opened versus closed a position.

The vendor sells exactly that as the **State** package: classified
order-flow imbalance derived from OPRA quote reactions, with matched trades
filtered out to leave excess customer demand. So the escalation path for this
question is an upgrade, not an exchange data purchase — see Part 4, which an
earlier draft got wrong.

## Reproducing Part 3

```bash
# free, no key, no account
curl -o ndx.json \
  https://cdn.cboe.com/api/global/delayed_quotes/options/_NDX.json

python3 scripts/sign_convention_test.py \
  --zip ./eod/eod_report_NQ_NDX_2026-09-04.zip --chain ndx.json
```

The chain must be fetched **before the next expiry expires**, or the contracts
being reconstructed will have dropped out of it. In practice: run it the same
weekend as the report.

---

# Part 4 — Getting more history, and what it costs

Part 2 concluded that 20–30 sessions are needed and the daily archive supplies
one per day — 4 to 6 weeks of waiting. The obvious question is whether that
can be bought instead.

## From GexBot itself

**Read from the vendor's published contract and FAQ, not inferred:**

| | |
|---|---|
| `/hist/eod/{ticker}` (ours) | latest completed session only, no parameters |
| Dated archive endpoint | **403 on Classic** — gated to the Quant package |
| Quant API access | a rolling 90-calendar-day window |
| **Earliest date available at all** | **365 calendar days**, "for purchase or lookup" |
| Historical granularity | **1-second snapshots, ~23,400 per session** |
| What is fixed vs live in those files | Greeks, spot and IV move through the day; **OI and all OI-based levels are computed once near the open and stay fixed** |

Two things here matter more than the 90-day figure.

**First: a year of history exists and is purchasable.** The FAQ states the
earliest available date is 365 calendar days back, for *purchase or lookup*.
That is a backfill path, not just a rolling window — so the "20–30 sessions"
Part 2 asks for is a purchase decision, not a six-week wait. Ask what a
backfill of ~30 sessions of NQ_NDX costs; that is a much smaller ask than a
tier upgrade and may not need one.

**Second, and this one changes how Part 2's results should be read: the OI
levels cannot move intraday, by construction.** OI is tallied overnight by
the OCC and GexBot recomputes the OI levels once daily near the open — the
FAQ says the API's OI data updates once per day at 08:00 ET. So an "OI wall"
is a fixed line for the whole session. The volume levels are the only
Classic reading that responds to what is happening now.

That is a *documented* answer to the reconciliation this project has been
guessing at: open interest is a pre-open structural read because it is
physically incapable of being anything else, and volume is the intraday one.
The two source videos were not contradicting each other.

**Pricing could not be established from any public source, and this should be
treated as an open action rather than an answer.** The vendor's site renders
its price table from an authenticated billing integration; the prices are not
present in the JavaScript bundle (only the Research add-on's are — quoted
there as a $50/month add-on or $100/month standalone). Third-party resale
listings quote figures for other tiers, but reselling sites are not a
citable source for a vendor's own prices and one search result conflated
GexBot with a similarly-named competitor. **The reliable move is to open the
pricing page while logged in** — thirty seconds with an account beats any
amount of inference from outside, which is the same lesson as Part 1.

## From free public data

Part 3 is the proof of concept: **the OI walls are fully reconstructable for
free.** Cboe's delayed chain endpoint needs no key and no account, carries
gamma, open interest and volume per contract, and reproduces GexBot's
per-strike numbers at r² ≈ 0.95.

What that does and does not buy:

- **It does buy** an independent check on any level, and the ability to build
  OI-based walls for instruments GexBot does not cover.
- **It does not buy history.** The endpoint serves the current chain only. It
  has the same shape of limitation as the EOD report: snapshot it daily or
  lose it. Archiving it is cheap and worth starting.
- **It does not buy signed flow.** Raw volume carries no side (Part 3).

## Signed flow: the State package, not Cboe

An earlier draft of this section recommended **Cboe Open-Close Volume
Summary** as the dataset that would settle the sign question, since it
classifies every trade by participant type, buy/sell and open/close. That is
still true of the dataset. It was the wrong recommendation, because the
vendor's own FAQ addresses it directly and takes the opposite view:

> gexbot classifies transactions from OPRA's consolidated feed using
> proprietary algorithms, based on how trades move the volatility surface —
> **rather than purchasing static Cboe Open-Close inventory reports** —
> on the grounds that it measures how market makers behave rather than what
> they report.

So the classified, non-naive read already exists as a product: it is the
**State** package. `Classic` is documented as *naive* GEX (Part 3); `State`
is documented as classified order-flow imbalance that filters out matched
trades to leave excess customer demand. Buying an institutional exchange
feed to reproduce, at end-of-day granularity, something the vendor sells as
a real-time upgrade would be an expensive way to arrive somewhere worse.

Cboe Open-Close remains the right answer to a *different* question — an
independent audit of the vendor's classification, rather than obtaining a
classification at all. For reference: C1 end-of-day history goes back to
2005, intraday to 2019, and pricing is not on the product page (it points at
SEC-filed fee schedules; a search result attributes **$500/month** to an
exchange fee schedule, **not verified against the filing** and to be treated
as an order of magnitude, not a quote).

**The proportionate purchases, in order: a history backfill, then State.**
Not Open-Close.

## Recommended order

1. **Keep the daily archive running.** It is free, already built, and every
   day of delay is a session that cannot be recovered.
2. **Start archiving the free Cboe chain daily too.** Also free, and it is the
   only independent check on the vendor's numbers.
3. **Ask what a backfill costs.** A year is available for purchase or lookup;
   ~30 sessions of one ticker is the ask, and it may not require a tier
   upgrade at all. This is now the fastest route to a powered result.
4. **Then consider State**, if the question becomes "is the naive sign
   assumption right" rather than "which naive reading works better".
5. **Leave Open-Close alone** unless the goal becomes auditing the vendor.

## Licensing — no longer an inference

The terms were previously unreadable (client-rendered site), so this project
made a conservative guess and kept vendor data out of the public repository.
The FAQ now states the rule explicitly: downloaded files may be stored
locally, but the data is for **personal, non-commercial use only** — no
redistribution, resale, sharing, or use in managing assets for anyone else,
and the subscriber represents they are a non-professional user.

The guess was correct, and the design that followed from it — Firestore
rather than the public repo, `Gex-Bot/data/` gitignored, only derived
statistics committed — is what the terms actually require. It is now a quoted
rule rather than a cautious assumption.

---

# Part 5 — What the literature says

Searched for peer-reviewed work on whether open interest or volume better
explains dealer hedging pressure and price behaviour.

**A caveat that must travel with this section: only abstracts were readable.**
Every full PDF attempt failed — timeouts, 405s and 403s from the hosts. What
follows is therefore a map of where to look, not a synthesis of findings, and
nothing here should be cited onward without opening the papers.

- **Ni, Pearson & Poteshman**, on stock price clustering at option expiration,
  is the closest thing to a foundational result: it argues that option market
  makers' hedging demonstrably moves the underlying toward strikes. It is the
  strongest published support for the *mechanism* the whole strategy assumes.
  Notably, it is built on **open interest at expiry**, not on volume.
- **Barbon & Buraschi, "Gamma Fragility"**, models dealer gamma imbalance as a
  driver of price fragility and amplification — the positive/negative gamma
  regime distinction, formalised.
- A **2024 paper on options market quality** appeared in results relating
  dealer gamma positioning to liquidity and volatility.
- An **SSRN paper by Chilingarian** makes precisely the argument Part 3
  measured: that the call-positive/put-negative sign is an *inventory
  assumption*, not a property of the greek, and that results are sensitive to
  it. This is the one to read first, because Part 3 confirms empirically that
  the assumption is in force in the data we are trading from.

**What the literature does not settle.** The academic work concerns dealer
gamma *positioning* — which is an open-interest concept. There appears to be
no established literature endorsing "session volume gamma" as a positioning
measure at all. Given Part 3's finding that the volume reading is unsigned
turnover with an assumed side, that absence is unsurprising and is itself
weak evidence for the open-interest reading.

The honest summary: **theory supports the mechanism and leans open-interest;
it does not adjudicate the specific intraday question this project is asking.**
Our own archive still has to.
