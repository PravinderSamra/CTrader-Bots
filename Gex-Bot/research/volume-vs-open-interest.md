# Volume vs open interest — and the history mistake that delayed answering it

**Status:** open question, method established, one session analysed (not enough).
**Last updated:** 2026-09-05.

This file is written to be read cold, by someone with no context on this
project — including another Claude session investigating a similar question.
It has two halves:

1. **A research-methodology failure** and how it was corrected. Generalisable;
   read this even if you do not care about options data.
2. **The volume-vs-open-interest analysis** itself: question, method, results
   so far, and what would actually settle it.

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

- **The `date` parameter is accepted but ignored.** Requests for any date
  return a byte-identical file; the `content-disposition` filename names the
  most recent session regardless of what was asked. Confirmed across dates a
  year apart.
- **Backfill is therefore impossible on this tier.** The dated archive that
  would allow it is 403. A session not downloaded on the day is lost — the
  same conclusion as before, but for the correct reason and one day at a
  time rather than for all history.

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
- **The performance claims that motivated this project are unverified.** The
  75% win rate, 1:10 reward-to-risk and "a stop every two or three weeks"
  quoted by the strategy's author come from promotional videos with no
  statistics shown. They are the hypothesis, not the baseline.
