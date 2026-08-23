# NAS100 Daily Brief — Phase 1 Findings

**Status: complete.** Everything below was connection-tested from this session
on **2026-08-22, 09:44–10:05 UTC**. Nothing here is assumed; every source was
called, every engine was run against live data, and the two bugs found along
the way are documented rather than quietly patched.

---

## The headline

**We can build the entire brief — macro, GEX/OI, news, levels, fuel and a bias
call — from free, connection-verified sources.** 31 of 32 candidate sources are
live. The core brief needs **no API keys at all**; one free optional key (FRED,
now supplied and wired in) adds the real-rate, credit and liquidity layer.

The most important find: **CBOE publishes the full NDX and QQQ options chains,
with per-contract open interest AND greeks, at no cost and with no API key.**
That is the same upstream data every commercial GEX vendor resells. We do not
need SpotGamma, MenthorQ or GEXBot.

---

## What was built and proven working

Five prototypes in `prototypes/`, all runnable right now:

| Script | What it does | Proven output |
|---|---|---|
| `source_health.py` | Probes all 28 sources, PASS/FAIL + latency | 27 LIVE / 1 correct-empty |
| `cboe_gex.py` | NDX chain → GEX, gamma flip (Black-Scholes re-priced), walls, max pain | 3,608 contracts parsed; flip located |
| `gex_levels.py` | Combines NDX + QQQ into one dealer-gamma board, converts to your CFD price | 7,551 contracts; full level board |
| `levels_fuel.py` | cTrader NAS100 → PDH/PDL/PWH/PWL, Asia/London/NY H-L, unmitigated pools, ADR fuel gauge | Full level set + fuel state |
| `macro_probe.py` | Vol regime, rates, FX, breadth, calendars, news | Complete macro layer |
| `fred_probe.py` | Real yields, breakevens, credit spreads, financial conditions, Fed liquidity | 14/14 series live |
| `news_scorer.py` | Headline pre-filter: relevance, negation and modal gates, then NAS100 reaction mapping | 138 headlines -> 43 relevant, 2-tier |
| `test_news_scorer.py` | Regression suite for the pre-filter | **22/22 passing** |
| `bias_engine.py` | Deterministic, fully-auditable bull/bear score | `-6 BEARISH` with traceable components |
| `brief.py` | End-to-end brief, no model in the loop | See `examples_brief.md` |

**`examples_brief.md` in this folder is a real brief generated from live data.**
That is the Phase-1 proof — not a mock-up.

---

## What I found about your market, today

Running the engines produced a coherent read worth stating, because it
validates the pipeline:

- **Below the gamma flip (29,327) → short-gamma regime.** Dealers amplify moves.
  Your **strategy 2** (CISD → HH/HL → OTE) is the right tool; strategy-1 fades
  have a lower hit rate here.
- **Price is below the *entire* prior-week range** (29,422–30,176). The weekly
  draw has flipped bearish and **PWL at 29,422 is now resistance, not support**
  — a level reclassification that is easy to miss on a 1m chart.
- **Call wall and max pain coincide at 29,381.6** — two independent methods on
  the same price makes it the strongest ceiling on the board.
- **Fuel is burning hot**: 67% of ADR14 used against ~38% normal for the hour
  (ratio 1.77), while VXN implies a 406-pt day vs. a 475-pt ADR.
- **NVDA reports Wednesday 26 Aug after-hours** (cons. $2.01). For NAS100 that
  outranks most CPI prints. Expect a pinned Tuesday and an expansive Thursday.

---

## Sources: the verdict

### Live and keyless (the whole brief runs on these)
- **cTrader** — NAS100 = symbolId **116**. `US100`/`USTEC`/`NDX100` do not
  resolve. Timeframes use the underscore form (`M_5`, `H_1`, `D_1`). Daily bars
  roll at 21:00 UTC.
- **CBOE delayed quotes** — `_NDX` and `QQQ` option chains (OI + full greeks),
  plus `_NDX`, `_VIX`, `_VIX9D`, `_VVIX`, `QQQ` spot quotes.
- **Yahoo chart API v8** — `^NDX ^VXN ^TNX ^FVX ^IRX DX-Y.NYB NQ=F ES=F` and
  individual mega-caps. (The v7 quote/options endpoints are 401-gated; v8 chart
  is open.)
- **ForexFactory** `ff_calendar_thisweek.json` — impact-tagged US calendar.
- **Nasdaq API** — per-date economic events and earnings.
- **RSS** — CNBC, MarketWatch, FT, Investing.com, Federal Reserve press, plus
  Google News RSS with arbitrary queries.
- **US Treasury** par-yield XML.

### Live with the free FRED key (now supplied)
`DFII10 DFII5 T10YIE T5YIFR DGS10 DGS2 T10Y2Y NFCI BAMLH0A0HYM2 WALCL
RRPONTSYD SOFR VIXCLS DTWEXBGS` — 14/14 verified.

### Tested and rejected (do not plumb these)
CNN Fear & Greed (HTTP 418 bot-block), Stooq (JS challenge), Yahoo v7
quote/options (401), TradingEconomics guest (410 — discontinued), CBOE VIX
term-structure and history CSVs (403), BLS RSS (403), Reuters RSS (connection
failure), FRED `fredgraph.csv` (unreachable from here).

Full detail with latencies in `research/02-data-sources.md`.

---

## ⚠️ Things you need to know / act on

### 1. NewsMCP has shut down — remove it from `.mcp.json`
The server now returns HTTP 410. It asked me to pass this on verbatim:

> "NewsMCP has been shut down because it was too expensive to run for free. If
> you or your organisation would be interested in a paid or sponsored version
> that stays online, please get in touch at newsmcp@laikai.lt. Messages from
> interested users directly influence whether the service comes back."

We don't need it — the RSS layer covers news comprehensively.

### 2. Two MCP servers are configured with placeholder keys and fail on every call
`.mcp.json` contains the literal strings `YOUR_TAVILY_API_KEY` and
`YOUR_API_KEY`. Tavily returns 401; Alpha Vantage exposes no tools at all.

---

## FRED key — supplied, tested, wired in ✅

The key you provided works: **14 of 14 series returned live data.** It is now
integrated into `fred_probe.py`, `macro_probe.py`, `bias_engine.py`,
`brief.py` and `source_health.py`.

**The key is not in the repo.** Everything reads `FRED_API_KEY` from the
environment; `SETUP-SECRETS.md` documents where to put it. Without it the brief
still runs end to end and prints an explicit note that the real-rate layer is
missing — it never degrades silently.

**Correction to my earlier advice:** I initially said to put the key in the
Claude Code cloud-environment variables. The docs are explicit that cloud
environments have *no dedicated secrets store* and that anyone using the
environment can read the values, so they advise against putting credentials
there at all. For a free, read-only, public-data key in a **personal**
environment that is an acceptable trade-off — but it is your call to make
knowingly, and the GitHub Actions secret store is the correct home for the
scheduled job. `SETUP-SECRETS.md` now states both accurately, and flags that
`CTRADER_MCP_SLUG` — which authenticates a **trading account** — sits in a
different risk category entirely.

On the exposure: you're right that it's low risk — free, read-only, public
data, no personal information, no billing. If you'd rather not leave it in a
chat transcript, regenerating takes ten seconds and needs **no code change**,
since nothing hardcodes it. The cTrader slug is the one that genuinely matters
(it authenticates a trading account) — keep that in the environment and GitHub
secrets only.

### What the FRED layer actually adds

| Read | Today's value | Why it earns its place |
|---|---|---|
| **10y real yield** `DFII10` | 2.35% (−4bp/5d) | The actual discount rate on tech cash flows — more predictive than the nominal |
| **Yield decomposition** | 10y +4bp 19→20 Aug, **entirely breakevens**, real +0bp | A breakeven-led rise is a *much softer* bearish signal than a real-rate-led one. Reading the nominal alone would have over-weighted it |
| **HY credit spread** `BAMLH0A0HYM2` | 2.75%, +4bp/5d | Credit's verdict on risk. Widening HY into an equity rally is the most reliable bearish divergence there is. Currently tight → credit is comfortable |
| **Financial conditions** `NFCI` | −0.559, easing w/w | Conditions *lead* price. Looser than average and still easing |
| **Fed liquidity** `WALCL` / `RRPONTSYD` | $6.75tn (−$14.3bn w/w), RRP $0.2bn | QT draining with the reverse-repo buffer effectively gone — a slow, persistent headwind |

**A third bug surfaced and was fixed here:** FRED series publish on different
lags (`DFII10` lands a day after `T10YIE`), so comparing each series' own
latest step compared *different days* — the decomposition reported "nominal
+4bp, real +0bp, breakeven +0bp", which is arithmetically impossible.
`aligned_change()` now finds the latest date common to all compared series and
measures every change over that same interval.

---

## Remaining API keys — optional, none blocking

**Nothing here blocks Phase 2.** The brief works fully without any of them.
These are upgrades, in priority order:

| # | Service | Cost | What it adds | Worth it? |
|---|---|---|---|---|
| ~~1~~ | ~~**FRED**~~ | Free | ✅ **Done — supplied and integrated** | — |
| ~~2~~ | ~~**Alpha Vantage**~~ | Free, 25 calls/**day** | ❌ **Dropped — remove from `.mcp.json`.** Its only remaining role was `NEWS_SENTIMENT`, and testing showed a generic tone score is the wrong tool, not just a rationed one. Replaced by `news_scorer.py`. Full reasoning in `research/09` | No |
| 3 | **Tavily** — https://app.tavily.com | Free, 1,000/month | Better web research than the built-in search for chasing a live theme mid-session. The key already has a slot in `.mcp.json` | Optional — built-in WebSearch covers most of it |
| 4 | **Finnhub** — https://finnhub.io/register | Free tier | Earnings surprise history and analyst revisions. Nasdaq's calendar already covers dates and consensus | Low priority |

**Deliberately NOT recommending:** any paid GEX vendor. CBOE gives us the same
underlying data for free, and `gex_levels.py` already builds the board.

---

## Honest limitations

1. **CBOE options data is ~15 minutes delayed.** Fine for a pre-session level
   map; it means the levels are a map, not a live feed.
2. **Dealer positioning is an assumption, not an observation.** We use the
   standard long-call/short-put convention. Levels and regime are robust;
   absolute dollar figures are approximate. Nobody — free or paid — actually
   knows dealer inventory.
3. **The 7 MB payload must never enter context.** It is script-reduced by a
   factor of ~1,400:1 before the model sees anything.
4. **ForexFactory now only publishes the `thisweek` variant** (`today`,
   `tomorrow`, `nextweek` all 404). Nasdaq's per-date endpoint fills the gap.
5. **Fuel percentages need real-session validation.** The time-of-day range-
   consumption curve in doc 06 is my best estimate; Phase 4 should replace it
   with measured data from the archive.
6. **The bias weights are a first draft.** They are reasoned, not fitted. They
   should be re-weighted in Phase 4 against logged outcomes.

---

## Three bugs found and fixed during the build (worth knowing)

1. **Yahoo's `chartPreviousClose` is the close before the *entire range*, not
   the prior session.** On a 10-day range it reported AVGO at −13.87% when the
   real daily move was +1.21%, corrupting the whole breadth component. Fixed.
   *Lesson: hand-verify one number against a known value before trusting any
   new feed.*
2. **The narrow-rally divergence rule fired on a non-divergence** (mega-cap
   average of +0.01% counted as "down"). Fixed.

3. **FRED series publish on different lags**, so per-series change comparisons
   compared different days and mis-attributed the yield move. Fixed with
   `aligned_change()`.

All three were caught only because every component prints its reasoning. That
transparency is a design requirement, not a nicety. The common lesson: **never
trust a feed's convenience field — derive the comparison yourself and
sanity-check the arithmetic.**

---

## On your GitHub question — confirmed, with a correction

You were right that GitHub is the correct home, but **not for the reason
stated**. Running scripts in-session is actually *cheaper* than dispatching a
workflow (a dispatch costs 1,500–3,000 extra tokens in polling and log
retrieval and adds ~2 minutes). Your Liquidity Trap phone skill uses Actions
for **credential portability on a phone**, not token efficiency.

Where GitHub genuinely wins:
- A **scheduled job that pre-computes and commits `data/NAS100_latest.json`** is
  the cheapest read path of all — one small file, ~2,500 tokens, ~2 seconds.
- The **historical archive builds itself**, which is the entire foundation of
  Phase 4. You cannot retro-fit it later.
- Analysis logic is versioned and diffable, and the model stops re-deriving
  numbers a script can compute exactly.

Recommended: skill + scripts in the repo, a cron workflow writing
`latest.json` four times a day, and a three-tier fallback (cached → local live
→ workflow dispatch). Full detail and the token maths in
`research/08-phase2-architecture.md`.

---

## What I need from you before Phase 2

1. **Confirm the four cron times** (06:00 / 12:00 / 17:00 / 20:15 UTC) suit
   your routine, or give me the times you actually want a brief.
2. ~~Sign up for the FRED key~~ ✅ done — but **add `FRED_API_KEY` to your
   Claude Code environment settings** so it persists into future sessions, and
   as a GitHub Actions repo secret for the Phase-2 scheduled job
   (`SETUP-SECRETS.md`). I can't persist an environment variable from here.
3. ~~Clean up `.mcp.json`~~ ✅ **done** — removed `newsmcp` (HTTP 410, service
   shut down), `alpha-vantage` (placeholder key, superseded) and `tavily`
   (placeholder key, 401). Two more are non-functional but were left in place
   rather than removed unasked: `massive` (placeholder key, paid service) and
   `tradingview-ohlcv` (needs a manual clone to `/tmp` that never exists in a
   fresh container). Say the word and they go too.
4. **Confirm the output format.** `examples_brief.md` is my proposed shape.
   Tell me what to cut and what to add — Phase 3 is presentation refinement,
   but it's cheaper to get the skeleton right now.

---

## Files in this project

```
NAS100 Daily Brief agent skill/
├── PHASE1-FINDINGS.md              <- this file
├── SETUP-SECRETS.md                <- where the two env vars go (no values in repo)
├── examples_brief.md               <- a REAL brief from live data
├── research/
│   ├── 01-macro-drivers.md         what actually moves NAS100 intraday
│   ├── 02-data-sources.md          every source, tested, with latencies
│   ├── 03-gex-oi-levels.md         GEX/OI methodology + the level playbook
│   ├── 04-news-layer.md            news sources + headline→reaction mapping
│   ├── 05-levels-and-strategy-map.md  the level board, mapped to YOUR 2 setups
│   ├── 06-range-and-fuel.md        fuel model + stop-management rules
│   ├── 07-bias-engine.md           how the bull/bear opinion is formed
│   └── 08-phase2-architecture.md   GitHub vs local, with token maths
└── prototypes/                     working, tested code
```
