# 04 — News & Event Layer: sources, and what each headline type means

The job of this layer is **not** to summarise the news. It is to answer one
question per item: *does this make NAS100 more likely to go up or down in the
next few hours, and by how much?*

---

## 1. Sources (all live, all keyless — see doc 02 for probe results)

### Scheduled events
| Source | Endpoint | Gives |
|---|---|---|
| ForexFactory week feed | `nfs.faireconomy.media/ff_calendar_thisweek.json` | Every event, **High/Medium/Low impact tag**, forecast, previous, exact timestamp. Filter `country == "USD"` and `impact in (High, Medium)` |
| Nasdaq econ events | `api.nasdaq.com/api/calendar/economicevents?date=YYYY-MM-DD` | Per-date detail with consensus + previous. Covers the weekend gap the FF `thisweek` feed leaves |
| Nasdaq earnings | `api.nasdaq.com/api/calendar/earnings?date=YYYY-MM-DD` | Per-date earnings, EPS consensus, market cap, before/after-hours flag. **Filter to the NDX heavyweights** |
| Fed calendar | `federalreserve.gov/newsevents/calendar.htm` | FOMC dates + speaker schedule |

**Heavyweight watchlist** (top NDX weights + the AI complex):
`NVDA AAPL MSFT AMZN META GOOGL GOOG TSLA AVGO AMD NFLX COST TSM`

### Unscheduled headlines
| Source | Endpoint |
|---|---|
| Google News — NASDAQ 24h | `news.google.com/rss/search?q=nasdaq+100+when:1d&hl=en-US&gl=US&ceid=US:en` |
| Google News — mega-cap 24h | same, `q=(Nvidia+OR+Apple+OR+Microsoft+OR+Amazon+OR+Meta+OR+Alphabet+OR+Tesla)+stock+when:1d` |
| CNBC top news | `search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114` |
| MarketWatch top stories | `feeds.content.dowjones.io/public/rss/mw_topstories` |
| FT Markets | `ft.com/markets?format=rss` |
| Investing.com economic news | `investing.com/rss/news_285.rss` |
| **Fed press releases** | `federalreserve.gov/feeds/press_all.xml` — policy straight from the source, no journalist in between |

Google News RSS is the workhorse: arbitrary query, `when:1d` window, no key,
cross-outlet de-duplication. Add ad-hoc queries when a theme is live (e.g.
`q=tariff+semiconductor+when:1d`).

---

## 2. Headline → market-reaction mapping

The brief must tag every surfaced item with a **direction**, a **magnitude**,
and a **half-life**. Half-life matters most for your trading: a 20-minute
headline is noise to fade; a multi-day theme changes the daily bias.

### Macro data
| Print | Surprise direction | NAS100 reaction | Magnitude | Half-life |
|---|---|---|---|---|
| CPI / core CPI | Hot | **Bearish** — yields up, multiple compression | 150–350 pts initial | 60–90 min, often substantially retraced |
| CPI / core CPI | Cool | **Bullish** | 150–300 pts | Tends to hold better than the hot-print move in the current hawkish regime |
| Core PCE | Hot / cool | Same sign as CPI | 80–180 pts | 45 min |
| NFP | Strong | **Regime-dependent.** In the current hawkish tape (dots flipped to a hike), strong jobs = hawkish = **bearish** | 150–300 pts | 90 min |
| NFP | Weak | Bullish *unless* weak enough to read as a growth scare, then bearish | 150–300 pts | 90 min |
| Average hourly earnings | Hot | Bearish, often the real mover inside NFP | 80–150 pts | 45 min |
| ISM Services | Weak | Bearish (growth) | 80–150 pts | 45 min |
| Jobless claims | Rising trend | Mildly bullish (dovish) unless recessionary | 30–70 pts | 20 min |
| Retail sales | Strong | Mixed — good growth, hawkish rates | 60–120 pts | 30 min |
| UoM 5–10y inflation expectations | Higher | Bearish; **the subcomponent moves more than the headline** | 80–150 pts | 45 min |
| Poor 10y/30y Treasury auction | Tail | Bearish, yields jump | 60–140 pts | 30 min |

### Fed communication
| Item | Reaction |
|---|---|
| FOMC statement (19:00) | Initial spike is usually noise. Do not trade the first 5 minutes |
| **Powell presser (19:30)** | This sets the real direction. Frequent full reversal of the 19:00 move. Both strategies work well *after* 19:50 once direction is set |
| Dot-plot shift | Largest single repricing event. A hawkish shift is bearish NAS100 and the effect persists for days |
| Voting-member speaker turning hawkish | Bearish, 40–100 pts, half-life ~1h |
| Non-voter / regional president | Usually ignorable |

### Earnings
| Item | Reaction |
|---|---|
| **NVDA** | The single largest scheduled NAS100 event, ranking with CPI. Reports after-hours. The session *before* is compressed and pinned; the session *after* gaps and expands. Next: **26 Aug 2026 AH, cons. $2.01** |
| MSFT / AAPL / AMZN / GOOGL / META | 60–200 pts on the index depending on weight and surprise |
| AVGO / AMD / TSM / MU | Move the whole semi complex, so their index impact exceeds their own weight |
| A hyperscaler cutting capex guidance | Bearish for the entire AI complex — a multi-day theme, not an intraday blip |

### Unscheduled themes
| Theme | Reaction | Half-life |
|---|---|---|
| Tariff / export-control headlines on semis | **Bearish**, sharp, often 150–250 pts with no warning | Hours to days. Currently live (US–Canada talks collapsed 21 Aug 2026) |
| Geopolitical escalation | Bearish, dollar up, yields down | Hours |
| Mega-cap regulatory action | Stock-specific; index impact scales with weight | Days |
| "AI capex is slowing" narrative pieces | Bearish for the complex | Days |
| "AI capex supercycle" / strong hyperscaler capex | Bullish | Days |
| Debt-ceiling / funding brinkmanship | Bearish, dollar mixed | Days |

---

## 3. Turning headlines into a score

Each item gets `direction ∈ {+1, 0, −1}` × `weight` (High=3, Medium=2, Low=1)
× `freshness` (≤4h = 1.0, 4–12h = 0.6, 12–24h = 0.3). Sum → the **news
component** of the bias engine (doc 07).

Two hard rules that override the score:
1. **A High-impact US event inside the next 90 minutes puts the brief into
   STAND-ASIDE.** Both your strategies need a genuine liquidity sweep that
   *fails*; a data print manufactures a sweep that keeps going. The brief
   should say "no entries before HH:MM" and give the levels to watch after.
2. **A headline less than 15 minutes old that has already moved price > 0.4×
   ADR is not tradeable on either model** until a new structure forms. Mark it
   and wait.

---

## 4. What the brief should output

For each pertinent item, three lines maximum:

```
[HIGH] 13:30 US Core CPI m/m  (cons 0.3%, prev 0.2%)
   → Hot print = bearish: yields up, NAS100 down 150-350pts, half-life ~75min.
     Cool print = bullish, similar size. STAND ASIDE 13:20-14:00.
     After 14:00 the 13:30-14:00 range high/low become the day's primary
     sweep levels for strategy 1.
```

That last line matters and is easy to miss: **a data print does not just create
risk, it creates the day's best liquidity levels.** The high and low of the
first 30 minutes after a Tier-0 print are among the most reliably swept levels
on the chart, and they belong on the level list.
