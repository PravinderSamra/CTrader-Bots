# 09 — Replacing Alpha Vantage: the news-sentiment decision

**Question:** Alpha Vantage's free tier is 25 API calls **per day** (not 25
days — worth correcting, because it makes the free tier *tighter* than assumed,
not looser). What replaces it long-term, for free?

**Answer:** nothing needs to. Alpha Vantage's only remaining role in our design
was `NEWS_SENTIMENT` — CBOE beat its options data and FRED beat its treasury
data. And on testing, a generic sentiment score turns out to be the **wrong
tool** for this job, not merely an expensive one.

---

## 1. What we actually need (and why a tone score can't give it)

`research/04-news-layer.md` specifies the requirement: for each headline,
**direction, magnitude, and half-life** *for NAS100*. That is a domain mapping,
not a tone measurement. The two come apart constantly:

| Headline | Tone | Actual NAS100 reaction |
|---|---|---|
| "Fed holds rates steady" | Neutral | Strongly bullish or bearish depending on what was priced |
| "Nvidia beats, guides light" | Positive | Reliably bearish |
| "Nasdaq futures climb after sharp selloff" | Negative words dominate | Bullish |
| "Strong jobs report" | Positive | **Bearish** in the current hawkish regime |

A sentiment API scores the first column. We need the third. No amount of
sentiment accuracy bridges that gap, so switching sentiment vendors would have
been solving the wrong problem.

---

## 2. Candidates tested (2026-08-22)

### Keyless
| Source | Result | Verdict |
|---|---|---|
| **GDELT 2.0 DOC API** | Worked twice, then **HTTP 429 for 3+ minutes across 4 spaced retries** | ❌ **Rejected.** Widely recommended as "the free unlimited news API", but it rate-limits hard from shared/cloud IPs — which is exactly where the Phase-2 scheduled job runs. Also returns heavy non-English noise without a `sourcelang` filter |
| **Stocktwits** `api.stocktwits.com/api/2/streams/symbol/NVDA.json` | ✅ 200, 30 messages, poster-tagged Bullish/Bearish (7/3, 20 untagged) | ⚠️ Works, but it's retail chatter — a *contrarian gauge at extremes*, not a news feed. Optional Phase-4 addition |
| **Yahoo per-ticker RSS** `feeds.finance.yahoo.com/rss/2.0/headline?s=NVDA` | ✅ 200, 20 items with timestamps | ✅ **Adopted** — added to the feed set |
| SEC EDGAR full-text | ✅ 200 | Useful for 8-K filings; out of scope for an intraday brief |

### Key-required (all returned 401 as expected)
| Service | Free tier | Verdict |
|---|---|---|
| **Marketaux** | **100 requests/day, 3 articles per request** (confirmed from their pricing page) | ✅ **Best like-for-like swap if you want an API** — 4× Alpha Vantage's 25/day, includes sentiment, permanently free. But 300 articles/day max |
| Finnhub | 60 calls/min; company news free, the *news-sentiment* endpoint is premium | ⚠️ Good news access, but the sentiment part is paid — i.e. it doesn't solve the stated problem |
| Alpaca | News API (Benzinga-sourced) with a free paper account | ⚠️ Promising; could not verify free-tier availability without an account. Worth a look only if you want raw Benzinga |
| FMP / Polygon / EODHD / NewsAPI | 250/day · 5/min · 20/day · 100/day dev-only with 24h delay | ❌ All either quota-bound, delayed, or sentiment-paywalled |

---

## 3. What we built instead — and what it taught us

`prototypes/news_scorer.py`: ten keyless RSS feeds, a rules engine mapping
headlines to **NAS100 reaction** (not tone), with `research/04-news-layer.md`'s
magnitudes and half-lives attached.

**The first version was bad, and the measurement is the point.** Scored against
124 live headlines, **8 of its top 14 were wrong**:

```
"Nasdaq Futures CLIMB After Sharp Selloff"          -> bearish   WRONG
"Nasdaq 100 SNAPS five-day slump"                   -> bearish   WRONG
"IF a Stock Market Crash Is Coming..."              -> bearish   WRONG (hypothetical)
"Analyst calls BITCOIN 'global bubble', could SOAR" -> bullish   WRONG (irrelevant)
"QATAR cuts state spending as war shrinks economy"  -> bearish   WRONG (irrelevant)
"KLARNA's stock crash..."                           -> bearish   WRONG (irrelevant)
```

Bag-of-keywords cannot handle **negation, subordinate clauses, hypotheticals,
or relevance**. Five rounds of patching produced five new failure modes:

| Round | Misfire found | Structural fix |
|---|---|---|
| 1 | "climb **after** selloff", "**snaps** slump" | `REVERSAL_UP` / `REVERSAL_DOWN` detection |
| 2 | Bitcoin/Qatar/Klarna scoring at all | relevance gate + off-topic-subject gate |
| 3 | "Nvidia Warns **Top** Customers" matched `tops?` | require `tops estimates`, not bare "top" |
| 4 | "Cooling on paper, **but** pressures have gone beyond" | `CONTRAST` clause detection |
| 5 | "**May** Plunge After Earnings, **Even If** It Beats" | `MODAL` gate — one rule retiring a whole class |

**That long tail is the finding.** It is also precisely the failure mode a
generic sentiment API has — so this was never a vendor problem.

### The resulting design: pre-filter, not scorer

The script is now a **high-precision pre-filter** with two tiers:

- **`HIGH`** — declarative, past-tense, unambiguous events only (a CPI print, a
  guidance cut, an export-control announcement). These are the *only* items
  that move the bias number. Deliberately rare: **0–3 per day.**
- **`NEEDS_JUDGEMENT`** — everything else topically relevant, surfaced with its
  flags for the model to read against `04-news-layer.md`. This is where
  negation, context and relevance actually get handled correctly.

**Design principle:** for a pre-filter, **over-filtering is the dangerous
failure** — signal that never reaches the model is lost, while an extra
headline the model discards costs almost nothing. An audit found the first
version silently dropping *"Big week coming up with PCE, Nvidia earnings and
then Jackson Hole"*, *"Federal Reserve issues FOMC statement"*, and *"S&P 500
positioning at record highs, Citi warns"*. The gates were rebalanced so only
promotional/listicle noise and 13F filing spam are dropped outright.

Jackson Hole is a good example of the payoff: it had **no rule and no calendar
entry** in the first build. It now surfaces — including *"All eyes on Warsh's
Jackson Hole debut as markets seek clarity on inflation"*, which is a
materially important headline the brief would otherwise have missed entirely.

### Regression tests
`prototypes/test_news_scorer.py` — **22 cases, 22 passing.** Every `FALSE` case
is a real misfire observed on live RSS; every `TRUE` case is hard news the
`HIGH` tier must still catch, so that tightening the gates can never quietly
reduce the scorer to "never fires". Two genuine bugs were caught by these tests
*after* I believed the code was finished:

1. `HYPOTHETICAL` contained a bare `forecast`, which matched "US CPI rises 0.4%,
   **hotter than forecast**" — a comparison *to* consensus is a hard fact, the
   opposite of speculative.
2. `export control` had no plural, so *"White House imposes new export
   **controls** on chip sales to China"* — the single highest-impact tariff
   variant for this index — was dropped entirely.

---

## 4. Recommendation

**Primary: no API. Keep the pre-filter + model judgement.**
Ten keyless feeds, no quota, no key, nothing that expires or needs renewing.
It handles the negation and relevance problems that *no* sentiment vendor
solves, and it costs only tokens we already spend.

**If you want an API anyway: Marketaux free tier** (100 req/day, 3 articles per
request, sentiment included, permanently free). It is a straight 4× upgrade on
Alpha Vantage's 25/day. I would treat it as an *additional* feed into the same
pre-filter, never as the source of truth — its sentiment score has the same
blind spots demonstrated above.

**Do not use GDELT** for the scheduled job, despite its reputation. It locked
out this IP after two requests and stayed locked for over three minutes.

**Alpha Vantage can be removed from `.mcp.json` entirely.** Nothing in the
brief depends on it.

---

## 5. Honest limitations

1. **`HIGH` fires rarely.** On the Saturday test run: 0 of 138 headlines, which
   is *correct* — weekend content is all preview and speculation. On a CPI or
   earnings day expect 1–3. If you ever see it scoring 8 headlines, something
   has regressed; run the test suite.
2. **The rules are hand-written and English-only.** They encode my reading of
   how NAS100 responds. Phase 4 should validate them against the logged archive
   and re-weight.
3. **Headlines only, not article bodies.** Deliberate — bodies would multiply
   both the token cost and the ambiguity. The model can fetch a specific
   article if one matters.
4. **Freshness weighting is crude** (1.0 / 0.6 / 0.3 / 0.1 by age bucket) and
   several feeds omit `pubDate`, which defaults them to "fresh". Worth
   tightening once the archive shows how much it matters.
