# 02 — Data Source Registry (every entry connection-tested)

All probes run **2026-08-22 09:44–09:52 UTC** from this session via
`prototypes/source_health.py`. Re-run that script any time; it prints
PASS/FAIL per source with latency and a content sanity-check.

**Result: 27 of 28 candidate sources LIVE. 0 API keys required for the core brief.**

---

## A. LIVE — verified working, no key, no scraping

### Price / structure
| ID | Endpoint | Latency | Payload | Use |
|---|---|---|---|---|
| `ctrader_nas100` | cTrader MCP `get_trendbars` / `get_spot_prices`, symbolId **116** | ~1–3s | JSON | **Primary.** Broker's own NAS100 CFD OHLCV — D_1/H_4/H_1/M_15/M_5/M_1. Every level printed is a price you can type straight onto your chart |
| `ndx_cash_cboe` | `cdn.cboe.com/api/global/delayed_quotes/quotes/_NDX.json` | 379ms | 533B | NDX cash spot — needed to compute the **CFD↔index offset** so GEX strikes translate to your chart |
| `ndx_cash_yahoo` | `query1.finance.yahoo.com/v8/finance/chart/^NDX` | 156ms | 1.6KB | NDX daily OHLC, cross-check |
| `nq_futures_1m` | Yahoo chart `NQ=F`, 1d/1m and 2d/5m | 208ms | 65KB | Globex overnight range → Asia/London H/L on the futures, and the gap vs. cash |
| `es_futures` | Yahoo chart `ES=F` | 175ms | 9.7KB | NQ-vs-ES relative strength (tech leadership tell) |

**Symbol resolution confirmed:** cTrader `NAS100` → symbolId **116**.
`US100`, `USTEC`, `NDX100` all resolve to `None` — do not use them.
Timeframe codes are `M_1 M_5 M_15 M_30 H_1 H_4 D_1 W_1` (underscore form).
Daily bars roll at **21:00 UTC**; bucket intraday bars the same way or
"previous day" means two different things on the two feeds.

### Options / GEX / OI  ← the important find
| ID | Endpoint | Latency | Payload | Use |
|---|---|---|---|---|
| `ndx_options` | `cdn.cboe.com/api/global/delayed_quotes/options/_NDX.json` | 330ms | **7.2 MB** | Full NDX index-option chain. **Every row carries `open_interest`, `volume`, `iv`, `delta`, `gamma`, `theta`, `vega`, `rho`.** 3,608 contracts inside 45 DTE with OI ≥ 1 |
| `qqq_options` | `.../options/QQQ.json` | 274ms | **5.3 MB** | QQQ chain, same fields. 3,943 contracts. QQQ carries a large share of Nasdaq dealer gamma — **the build must include it, not just NDX** |
| `qqq_quote` | `.../quotes/QQQ.json` | 181ms | 520B | QQQ spot → NDX/QQQ scaling ratio (measured **41.03** on 2026-08-22) |

This is the headline result of Phase 1. Free, keyless, ~15-minute delayed, and
it contains **exactly the fields a real GEX build needs**. Every commercial GEX
vendor (SpotGamma, MenthorQ, GEXBot) derives from this same CBOE data. We do
not need to pay for or scrape any of them.

Caveats, honestly stated:
- **~15-minute delay.** Irrelevant for pre-session level marking; it means the
  levels are a *map*, not a live tick feed. Refresh mid-session if you want the
  intraday drift in 0DTE gamma.
- **Payload is 7 MB.** It must be parsed by a script, never read into context.
  `prototypes/cboe_gex.py` reduces it to ~40 lines of JSON.
- Greeks are CBOE's own model values. Fine for ranking strikes; the flip point
  is re-priced independently with Black-Scholes (see doc 03).

### Volatility regime
| ID | Endpoint | Value on test | Use |
|---|---|---|---|
| `vxn` | Yahoo `^VXN` | **21.98** | NASDAQ-100 implied vol — the correct index for NAS100 |
| `vix` | CBOE `_VIX` | **15.13** | S&P 30d, for the VXN/VIX tech-stress ratio (1.45 on test) |
| `vix9d` | CBOE `_VIX9D` | **12.58** | 9-day. VIX9D/VIX = **0.831** → contango → mean-reversion regime |
| `vvix` | CBOE `_VVIX` | **86.27** | Vol-of-vol; > 100 = active tail hedging |

CBOE's VIX **futures term-structure** endpoint returns 403 — the VIX9D/VIX
ratio replaces it and needs no key.

### Rates / FX / macro
| ID | Endpoint | Value on test | Use |
|---|---|---|---|
| `us10y` | Yahoo `^TNX` | 4.738 (+0.83%) | Discount rate on long-duration tech |
| `us5y` | Yahoo `^FVX` | — | Fed-path proxy (Yahoo's `^UST2YR` is unreliable; `^FVX` is the stable short-end series) |
| `us13w` | Yahoo `^IRX` | — | Risk-free rate input for the Black-Scholes gamma re-pricing |
| `dxy` | Yahoo `DX-Y.NYB` | 98.839 (−0.98%) | Risk appetite / liquidity |
| `ust_curve_xml` | `home.treasury.gov/.../xml?data=daily_treasury_yield_curve` | 249KB | Official par curve — authoritative daily settle, use to sanity-check Yahoo |

### Calendars
| ID | Endpoint | Notes |
|---|---|---|
| `ff_calendar` | `nfs.faireconomy.media/ff_calendar_thisweek.json` | ForexFactory week feed with **High/Medium/Low impact tags**, forecast and previous. **Only the `thisweek` variant still exists** — `today`, `tomorrow` and `nextweek` all now return 404 |
| `nasdaq_econ_cal` | `api.nasdaq.com/api/calendar/economicevents?date=YYYY-MM-DD` | Per-date, any date (so it covers the Friday/weekend gap that `thisweek` leaves). Consensus + previous |
| `nasdaq_earn_cal` | `api.nasdaq.com/api/calendar/earnings?date=YYYY-MM-DD` | Per-date earnings with EPS consensus and market cap. Verified on three weekdays: 25 Aug → 47 rows, **26 Aug → 49 rows incl. NVDA (`time-after-hours`, cons. $2.01)**, 27 Aug → 60 rows. Returns a 146-byte empty payload on weekends — that is correct behaviour, not a failure |
| `fed_calendar` | `federalreserve.gov/newsevents/calendar.htm` | 82KB HTML — FOMC dates and speaker schedule |

### News
| ID | Endpoint | Items |
|---|---|---|
| `cnbc_rss` | `search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114` | Top news |
| `marketwatch_rss` | `feeds.content.dowjones.io/public/rss/mw_topstories` | Top stories |
| `yahoo_fin_rss` | `finance.yahoo.com/news/rssindex` | Broad market |
| `ft_markets_rss` | `ft.com/markets?format=rss` | Markets |
| `investing_rss` | `investing.com/rss/news_285.rss` | Economic news |
| `fed_press_rss` | `federalreserve.gov/feeds/press_all.xml` | **Policy headlines direct from the source** |
| `gnews_nasdaq` | `news.google.com/rss/search?q=nasdaq+100+when:1d` | NASDAQ, last 24h |
| `gnews_mag7` | `news.google.com/rss/search?q=(Nvidia+OR+Apple+OR+...)+stock+when:1d` | Mega-cap, last 24h |

Google News RSS `when:1d` is the workhorse — any query, any window, no key, and
it de-duplicates across outlets reasonably well.

---

## B. TESTED AND REJECTED — do not plumb these in

| Source | Result | Verdict |
|---|---|---|
| CNN Fear & Greed API | **HTTP 418** "I'm a teapot. You're a bot." on both `/graphdata` and `/current` | Hard bot-block. Dropped — VXN + VIX9D/VIX + VVIX cover the same ground with better resolution |
| Stooq CSV | 200 but returns a JS browser-challenge page | Unusable headless |
| Yahoo options v7 (`/v7/finance/options/QQQ`) | **401** | Crumb-gated. CBOE covers it better anyway |
| Yahoo quote v7 batch | **401** | Use the v8 `chart` endpoint per symbol instead — that one is open |
| TradingEconomics guest API | **410** — "guest account has been discontinued" | Dead |
| CBOE VIX term-structure JSON | **403** AccessDenied | Replaced by VIX9D/VIX |
| CBOE history CSVs (`_VIX_History.csv`) | **403** | Not needed |
| BLS RSS + release schedule | **403** | ForexFactory + Nasdaq cover the same releases |
| Reuters business RSS | connection failure | CNBC/MarketWatch/FT cover it |
| FRED `fredgraph.csv` | connection failure from this environment | FRED's proper API is reachable (returns a clean 400 on a bad key) — **needs a free key** |
| **NewsMCP** (`@newsmcp/server` in `.mcp.json`) | **410 — service shut down** | See the note in `PHASE1-FINDINGS.md`; must be removed from `.mcp.json` |
| **Tavily MCP** | **401** — `.mcp.json` holds the literal placeholder `YOUR_TAVILY_API_KEY` | Needs a free key (or just use built-in WebSearch) |
| **Alpha Vantage MCP** | Not exposed — `.mcp.json` holds the literal placeholder `YOUR_API_KEY` | Needs a free key. **Not required** — CBOE beats its options data and Yahoo covers the rest |
| `massive` MCP | Placeholder key | Paid; not needed |

---

## C. Deliberate architectural choice: why not Alpha Vantage

The existing `GEX&OI` project was designed around Alpha Vantage
`REALTIME_OPTIONS` on a **25-calls-per-day** free tier, which forced a call
budget spreadsheet. CBOE's endpoint has **no key, no quota, and better
coverage** (full chain in one request vs. per-symbol calls), and it is the
upstream source Alpha Vantage itself resells. For NAS100 specifically, CBOE is
strictly better. Alpha Vantage stays on the optional list only for
`NEWS_SENTIMENT` scoring, which is a nice-to-have, not a dependency.

---

## D. Redundancy plan (what happens when something breaks)

| Layer | Primary | Fallback 1 | Fallback 2 |
|---|---|---|---|
| NAS100 price/structure | cTrader (broker prices) | Yahoo `NQ=F` + offset | Yahoo `^NDX` + offset |
| Index spot for GEX mapping | CBOE `_NDX` quote | Yahoo `^NDX` | last CBOE chain `close` field |
| GEX / OI | CBOE `_NDX` + `QQQ` chains | QQQ alone (scaled ×41.03) | previous run's cached levels, clearly labelled stale |
| Vol regime | VXN + VIX9D/VIX + VVIX | VIX alone | ATR-implied from cTrader |
| Rates | Yahoo `^TNX`/`^FVX`/`^IRX` | Treasury par-curve XML | — |
| Calendar | ForexFactory `thisweek` | Nasdaq econ-events per-date | Fed calendar HTML |
| News | Google News RSS ×2 | CNBC + MarketWatch + FT | built-in WebSearch |

Every source in the brief must be stamped with its own `as_of` timestamp, and
the brief must **say out loud** when it is running on a fallback. A silently
stale GEX level is worse than no GEX level.
