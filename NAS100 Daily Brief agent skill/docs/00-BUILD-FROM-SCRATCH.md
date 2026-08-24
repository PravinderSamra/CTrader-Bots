# NAS100 Daily Brief — Complete Build Documentation

**Purpose of this document:** hand it to a fresh Claude Code session with an
empty repo and it should be able to rebuild this system exactly, including the
mistakes worth not repeating.

Everything here was connection-tested. Every number quoted came from a real run.
Built 22–23 August 2026 across 11 commits.

---

# 1. What this is

A pre-session and intraday intelligence brief for day-trading the **NAS100**
(Nasdaq-100 CFD on Pepperstone via cTrader). One command produces:

- a **directional call** with a traceable score,
- **which of the trader's two entry models** suits today's dealer-gamma regime,
- the **exact levels to mark**, each with what to expect there,
- the **range/fuel budget** and the stop-management rule it implies,
- **event gates** and a filtered news read.

It is read-only. It never places orders.

## The two entry models it serves

These are the user's, and every design decision serves them:

**Strategy 1 — sweep → failed re-break → CISD reversal.** Price sweeps a key
liquidity level (PDH, PDL, PWH, PWL, Asia/London/NY H-L, unmitigated
highs/lows), drop to 1m, wait for a retrace, price *fails* to re-break the level
(lower high after a bullish sweep, higher low after a bearish one), wait for
CISD, enter the reversal. Stop beyond the sweep extreme or recent swing.

**Strategy 2 — CISD → HH/HL → fib OTE continuation.** After reversal signs on
1m: CISD, confirm a new higher high with a higher low behind it, wait for a
further HH, mark the leg with the fib tool, enter on the retrace into OTE
(0.62–0.79), stop below the fib, target above the previous swing high. Mirrored
for shorts.

**The core insight the whole product is built on:** which of these two works is
decided by **dealer gamma positioning**, not by the chart. Above the gamma flip
dealers fade extensions, so sweeps genuinely fail — Strategy 1. Below it they
amplify, so sweeps run — Strategy 2, and Strategy 1's hit rate drops materially.
A trader with the right direction and the wrong entry model still loses.

---

# 2. Where everything lives

```
.claude/skills/nas100-daily-brief/     <- the skill (canonical code)
├── SKILL.md                           always loaded, ~1.2k tokens
├── references/                        loaded on demand
│   ├── 01-reading-the-brief.md
│   ├── 02-gamma-levels-playbook.md
│   ├── 03-fuel-and-stop-management.md
│   ├── 04-strategy-selection.md
│   └── 05-news-and-events.md
└── scripts/                           3,496 lines of Python, no dependencies
    ├── ctrader_http.py     379  broker data over HTTPS keep-alive
    ├── session_context.py  176  day/session/DST/holiday awareness
    ├── cboe_gex.py         205  NDX chain -> GEX, BS-repriced gamma flip
    ├── gex_levels.py       227  NDX+QQQ combined board, expiry structure
    ├── levels_fuel.py      273  liquidity levels + ADR fuel gauge
    ├── macro_probe.py      272  vol, rates, FX, breadth, calendars, news
    ├── fred_probe.py       260  real yields, credit, liquidity
    ├── news_scorer.py      416  headline pre-filter -> NAS100 reaction
    ├── bias_engine.py      280  the deterministic bull/bear score
    ├── brief.py            436  orchestrator + markdown renderer
    ├── journal.py          173  writes every scan for later grading
    ├── review_day.py       189  grades a past day against real bars
    ├── source_health.py    123  probes all 32 sources
    └── test_news_scorer.py  87  22 regression cases

.claude/commands/nas100-brief.md       /nas100-brief slash command
.claude/agents/brief-reviewer.md       background retrospective sub-agent

NAS100 Daily Brief agent skill/        the project (data + docs)
├── research/01-10                     methodology and source research
├── docs/                              this document
├── formats/                           Phase-3 presentation options
├── journal/<trading-day>/             every scan, committed to git
├── examples_brief.md                  a real generated brief
├── PHASE1-FINDINGS.md
└── SETUP-SECRETS.md
```

**Why scripts live in the skill, not the project folder:** an earlier layout had
them in `prototypes/` with the intent of copying into the skill. Two copies
drift. The skill folder is canonical; `prototypes/README.md` is a pointer.

**Why the journal lives in the project folder, not the skill:** the skill is
code, the journal is data the user reads and Phase 4 learns from. `journal.py`
walks up to find it, overridable with `NAS100_JOURNAL_DIR`.

---

# 3. Data sources — every one connection-tested

Probed 2026-08-22/23 via `source_health.py`. **31 of 32 live. The core brief
needs no API keys at all.**

## 3.1 The headline find: free institutional-grade options data

```
https://cdn.cboe.com/api/global/delayed_quotes/options/_NDX.json   7.2 MB
https://cdn.cboe.com/api/global/delayed_quotes/options/QQQ.json    5.3 MB
https://cdn.cboe.com/api/global/delayed_quotes/quotes/_NDX.json    533 B
```

Every contract row carries `open_interest`, `volume`, `iv`, `delta`, **`gamma`**,
`vega`, `theta`, `rho`. No key, no quota, ~15-minute delay.

**This is the same upstream data every commercial GEX vendor resells.** We do
not need SpotGamma, MenthorQ or GEXBot. This single discovery removed the only
paid dependency the project would otherwise have had.

**Both chains are required.** NDX index options carry institutional hedging;
QQQ carries the volume. NDX alone under-counts dealer gamma badly. QQQ strikes
are scaled into NDX points by the live ratio (**41.034** measured 2026-08-22),
giving **3,608 NDX + 3,943 QQQ contracts** inside 45 DTE.

## 3.2 Broker price data — cTrader (direct HTTP only)

**Transport is a hard requirement, not a preference.** All broker data goes
through `ctrader_http.py`, a persistent HTTPS keep-alive client. The
`mcp__ctrader__*` injected tools must not be used anywhere in this skill.

Evidence, from building it: during one session the `mcp__ctrader__*` tools went
unavailable and reconnected **four separate times** while the HTTP client ran
throughout without interruption. The MCP transport also expires on phone and
browser sessions — which is exactly where this skill is used — and gives no
retry control, where the HTTP client handles session expiry with a bounded
backoff (see §8b).

Anything built on top of this skill inherits the same rule.



- **NAS100 = symbolId 116.** `US100`, `USTEC`, `NDX100` all resolve to `None`.
- Timeframes use the underscore form: `M_1 M_5 M_15 M_30 H_1 H_4 D_1 W_1`.
- `fetch_ohlcv(instrument, period, hours_back)` — the second arg is **hours,
  not bar count**. Asking for `6` gets six hours, which on a weekend is zero bars.
- Server caps responses at ~100 bars; `fetch_ohlcv_paged()` walks backwards.
- Daily bars roll at **21:00 UTC** (17:00 ET). Intraday bars must be bucketed
  the same way or "previous day" means two different things on the two feeds.
- Auth: `CTRADER_MCP_SLUG`, the base64url `eyJwb…` slug.

## 3.3 The rest of the live set

| Layer | Source | Notes |
|---|---|---|
| Index/futures | Yahoo v8 chart: `^NDX ^VXN ^TNX ^FVX ^IRX DX-Y.NYB NQ=F ES=F` + mega-caps | v8 `chart` is open; v7 `quote`/`options` are 401-gated |
| Volatility | CBOE quotes `_VIX _VIX9D _VVIX`, Yahoo `^VXN` | VXN is the *correct* gauge for NAS100, not VIX |
| Real rates/credit | FRED API — `DFII10 DFII5 T10YIE T5YIFR DGS10 DGS2 T10Y2Y NFCI BAMLH0A0HYM2 WALCL RRPONTSYD SOFR VIXCLS DTWEXBGS` | Free key, 120 req/min. 14/14 verified |
| Calendar | ForexFactory `ff_calendar_thisweek.json`; Nasdaq `api.nasdaq.com/api/calendar/economicevents` and `/earnings` | Only FF's `thisweek` variant still exists — `today`, `tomorrow`, `nextweek` all 404 |
| News | CNBC, MarketWatch, FT, Investing.com, Federal Reserve press, Yahoo per-ticker, Google News RSS with arbitrary `when:1d` queries | All keyless |

## 3.4 Tested and REJECTED — do not waste time re-testing

| Source | Result | Why rejected |
|---|---|---|
| **GDELT 2.0 DOC API** | Served 2 requests, then **HTTP 429 for 3+ minutes across 4 spaced retries** | Widely recommended as "the free unlimited news API". It rate-limits hard from shared/cloud IPs — exactly what a CI runner is. Disqualifying |
| CNN Fear & Greed | **418** "I'm a teapot. You're a bot." | Hard bot-block on both endpoints |
| Stooq CSV | 200 but returns a JS browser challenge | Unusable headless |
| Yahoo v7 quote / options | **401** | Crumb-gated. CBOE and v8 cover it |
| TradingEconomics guest | **410** | "guest account has been discontinued" |
| CBOE VIX term-structure JSON, history CSVs | **403** | VIX9D/VIX ratio replaces it |
| BLS RSS + schedule | **403** | FF + Nasdaq cover the same releases |
| Reuters business RSS | connection failure | CNBC/MW/FT cover it |
| FRED `fredgraph.csv` | unreachable | Use the proper JSON API |
| **NewsMCP** | **410 — service shut down** | Removed from `.mcp.json` |
| Marketaux / Finnhub / Alpaca / FMP / Polygon / EODHD / NewsAPI | all 401 (keys) | See §6.3 — an API was the wrong answer anyway |
| **Alpha Vantage** | placeholder key, no tools | Superseded on every axis. Removed |

---

# 4. Methodology

## 4.1 GEX

```
$GEX(strike) = gamma × OI × 100 × Spot² × 0.01     # $ dealer delta per 1% move
Net GEX      = Σ call $GEX − Σ put $GEX
```

**Dealer convention:** long calls / short puts. This is an *approximation* —
true dealer inventory is unobservable by anyone, free or paid. It is reliable
for **ranking strikes and locating the flip**, which is what we need. It is not
reliable as an absolute dollar figure, so the brief quotes regime and levels and
never presents "$X bn of gamma" as fact.

**Gamma flip — done properly.** The common shortcut is a cumulative sum by
strike. That is wrong, because gamma itself changes as spot moves.
`cboe_gex.gamma_flip()` re-prices the **entire book** with Black-Scholes gamma
across an 81-point spot grid spanning ±8%, holding each contract's own IV fixed,
and interpolates the zero crossing. Risk-free rate from `^IRX`.

**Converting to the user's chart:**
```
offset       = NAS100_CFD_mid − NDX_cash_spot        # −18.4 measured
NAS100_level = NDX_strike + offset
```
Recomputed every run. It drifts with the futures basis and must never be
hardcoded.

## 4.2 Expiry structure — the "shape of the day"

The three buckets (0–2 DTE, ≤7d, ≤45d) are **near-dated vs longer-dated dealer
positioning**, and near-dated gamma **decays during the session**. So when they
disagree, the day has two regimes — one early, one late. That disagreement is
the signal:

| Shape | Meaning |
|---|---|
| `COHERENT_SHORT` | Whole book short gamma. Expansion, high conviction, ADR can be exceeded |
| `COHERENT_LONG` | Pinned range all day. Fade at the walls |
| `PIN_THEN_EXPAND` | 0DTE pins through the morning; as it decays the short-gamma book takes over. **Chop early, resolves late — save risk for after ~13:00 ET** |
| `SPIKE_THEN_REVERT` | Near-term instability inside a stabilising book. Fade extremes, back to the middle only |
| `FRONT_FLAT_BACK_*` | Front gamma-neutral; the back book sets the tone. Lower conviction |

A **0.05bn deadband** stops a rounding-level figure being read as directional —
a measured 0.002bn front book correctly reads flat, not positive.

## 4.3 Levels

Sources: PDH/PDL/PD-mid/PD-close, PWH/PWL (ISO calendar week), Asia/London/NY
session H-L, unmitigated swing clusters, plus the gamma set.

**Calibration, measured on 6 days of NAS100 M_5 (1,379 bars):**

| Cluster tolerance | Pools above | Confirmed (≥2 touches) |
|---|---|---|
| 5 pts | 21 | 1 |
| 10 pts | 17 | 4 |
| **15 pts** | 15 | **6** |
| 20 pts | 12 | 6 |

Chosen: `tol = max(12, ADR14 × 0.03)` ≈ 14pts. Below ~10pts every swing becomes
its own "pool" and the equal-highs signal vanishes. NAS100 needs a far wider
band than FX because ADR14 is ~475 points.

**Wall strength is measured in gamma force ($GEX), not open interest.** A first
version banded walls by contract count. Measured on real data that is
misleading in both directions:

| Wall | Contracts | Force | Distance | Force per 1k |
|---|---|---|---|---|
| Weekly call | 8,657 | 0.56bn | +91 | 0.0647 |
| Weekly put | 7,091 | 0.28bn | −109 | 0.0392 |
| 45-day put | 168,275 | 1.01bn | −609 | **0.0060** |

24× the contracts, 3.6× the force, and 11× weaker *per contract* than the
at-the-money wall — because gamma collapses with distance from spot. Contract
count says how many bets sit there; $GEX says how hard dealers must trade to
stay hedged, and only the second one moves price.

The scale is **relative to the strongest wall of the same type in that run**
rather than fixed thresholds, so it adapts to a quiet week versus an OPEX week.
Normalising across groups instead made a wall 609pts away render as the
strongest level on the board, so intraday and structural walls are ranked
separately and the absolute $bn is printed for cross-group comparison.

*(Note: `round()` is banker's rounding, so a wall at exactly half strength
rendered 2 dots instead of 3 until half-up rounding was used explicitly.)*

**Tenor confluence** — the weekly and 45-day wall at the same strike — is called
out explicitly, because a wall defended across expiries is materially stronger
than a one-week wall.

**Structural walls are exempt from the range-budget filter.** An earlier version
dropped the 45-day put wall at 28,681.6 — **168,275 contracts, the single
biggest concentration on the entire chain** — purely because it sat 609pts away,
beyond today's budget. That is the level a multi-day sell-off is defended at and
it belongs on the chart permanently. Being out of today's range is the *point*
of a structural level, not a reason to hide it. They also carry no `(stretch)`
tag, since "partials only" is the wrong framing for a boundary you are not
trading toward today.

**The corridor read translates distant structure into a daily decision.** A
structural wall hundreds of points away is not a level a day trader reaches, so
publishing it alone was only half an answer. `path_read()` reports what sits
*between* price and the next real barrier each way, because **only a positive
gamma shelf actually brakes a move** — a run of negative shelves is a
low-friction corridor. Measured on one run: every shelf from 29,181 down to
28,681 was negative, i.e. no structural friction for a full ADR, which is
directly actionable ("a breakdown has room, do not fade it") in a way the
distant wall alone was not.

**What is deliberately NOT published:**
- **Single-touch swing extremes.** They were 9 of 30 rows, every one labelled
  "context only" — the board was telling the user not to trade them while
  spending a row each. A lone swing high is where price turned, not a pile of stops.
- **Negative gamma shelves.** By definition price *accelerates through* them, so
  as a chart marking they say nothing actionable. Retained in the data for the
  bias engine; not drawn.
- **Anything beyond the range budget**, except core day-frame levels which stay
  flagged `(stretch)` — see §6.5.

Rows are **merged by price** (tolerance scaled to the instrument). Confluence
makes one level stronger, it does not deserve three rows.

## 4.4 The bias engine

Deterministic, and **every component prints its own contribution and reasoning**
so a wrong call is traceable to the rule that caused it. That transparency is a
design requirement — it is how all three bugs in §6.1 were caught.

| Component | Max ± | Rationale |
|---|---|---|
| Gamma regime | ±8 | Highest weight: decides *how* price moves, hence which model works |
| Macro (FRED) | ±9 | Real yields ±3, credit ±2, others ±1. Weighted below intraday levers because FRED lags 1–2 days: regime, not trigger |
| Volatility | ±6 | VXN change, VIX9D/VIX term, VXN/VIX tech stress, VVIX |
| Rates/FX | ±6 | 10y daily change ±3 — the single biggest macro lever on NAS100 |
| Breadth | ±5 | Mega-cap average, narrow-rally divergence, NDX vs ES |
| Structure | ±5 | Prior-week displacement ±3, PD mid, pool imbalance |
| News | ±4 | Only HIGH-confidence headlines vote |
| Fuel | **0** | **Reports, never votes.** Changes management and target scope, not direction |
| Events | **0 + gate** | Can raise a hard STAND-ASIDE |

Direction and conviction are separate. Events are a gate, not a vote.

**Highest-value single rule discovered:** *prior-week displacement*. Price
trading entirely outside the previous calendar week's range is worth ±3 and is
easy to miss on a 1m chart. On 2026-08-22 it flipped the call from MILDLY
BEARISH to BEARISH — and it **reclassifies a level**: PWL at 29,422 stopped
being support and became resistance, so it should be traded as a short-sweep
level, not a long-sweep one.

## 4.5 Fuel and stop management

```
ADR14, adr_used_pct, remaining_budget → ROOM_TO_EXPAND / MODERATE / LOW_FUEL / EXHAUSTED
```

**The budget forecasts RANGE EXTENSION, not price travel — and the output used
to imply the latter.** `EXHAUSTED` printed "do not initiate", which reads as
"nothing will happen". Measured 2026-08-24: a 0.0pt budget was followed by
5.3pts of extension (the forecast was right) while price traversed 284.4pts
inside the range. The metric was sound; the description was wrong.

This also inverts the setup preference: if the range will not extend, price must
turn at the extremes, so `LOW_FUEL`/`EXHAUSTED` favours **fading the extremes**
even when the gamma regime favours continuation. On 24 Aug the brief called
continuation at 28,903 with a 0pt budget — price bottomed 30pts later and
rallied 178 into the close.

**The review engine was grading fuel on the wrong quantity**, comparing the
budget against traversal rather than extension, which reported a 3.8x
under-estimate where the model had been accurate. Fixed to grade extension and
report traversal separately.

**NAS100-specific correction that matters most:** the index does not spend its
range evenly — roughly 15% Asia, 25% London, **45% NY open**, 15% afternoon. So
"67% of ADR used" at 08:00 ET is an exhausted day (the biggest window hasn't
opened); the same 67% at 13:00 ET is normal. Hence `fuel_ratio` = used ÷ normal
for this **Eastern** hour.

Cross-checks: VXN-implied range (forward-looking, where ADR is backward-looking)
and a gamma multiplier (positive ×0.8, negative ×1.3, backwardation ×1.2).

## 4.6 News

**The key realisation: a sentiment score is the wrong tool.** Tone and NAS100
reaction come apart constantly — "Fed holds rates steady" is tonally neutral but
directionally decisive; "strong jobs report" is tonally positive and bearish in a
hawkish regime. What is needed is a **headline → reaction mapping** (direction,
magnitude, half-life), which is domain knowledge, not sentiment.

Design: a **two-tier pre-filter**, not a scorer.
- `HIGH` — declarative, past-tense, unambiguous events only. The *only* tier that
  moves the bias number. Deliberately rare: **0–3 per day.**
- `NEEDS_JUDGEMENT` — everything else relevant, surfaced with flags for the model
  to read in context, where negation and relevance are handled correctly.

**For a pre-filter, over-filtering is the dangerous failure.** Signal that never
reaches the model is lost; an extra headline the model discards costs nothing.
Only promotional noise and 13F spam are dropped outright.

---

# 5. The journal and review loop

Every scan writes `journal/<trading-day>/HHMM-<session>.json` + `.md`, plus a
flat `index.json`.

The JSON records the **prediction before the outcome is known** — bias score,
expected direction, gamma flip, expiry shape, fuel state, and every published
level. **That data cannot be reconstructed afterwards.** Writes are best-effort
and never raise; a disk problem must not break a brief. It is committed to git
deliberately — cloud containers are wiped, so an ignored journal leaves Phase 4
with nothing to learn from.

`review_day.py` grades a past day against real cTrader bars: direction call from
the scan time forward, every level graded as *stalled / broke up / broke down /
chopped*, and realised range vs published budget. It is a **script, not a
prompt**, because the arithmetic is deterministic and must not be re-derived.

**First real run (2026-08-20):**
```
REVIEW 2026-08-20  O 29487.1 H 29600.9 L 29115.9 C 29219.2  range 485.0  net -267.9
  direction: 1 right / 0 wrong    levels touched: 0.75
  fuel: budget 156.1 vs realised 266.6 -> UNDER-estimated
    29381.6  CALL WALL + MAX PAIN   broke DOWN through it
```
It independently surfaced a concern already flagged by eye — **the range budget
is too conservative.** That is the loop earning its keep on day one.

`.claude/agents/brief-reviewer.md` runs this in the **background, after** the
brief is delivered. Its hard rules: propose no change without evidence from
**3+ sessions** (tuning on one day's noise is how a model gets worse), never edit
scoring logic, never touch a `prediction` block.

---

# 6. Key decisions, and what we chose not to do

## 6.1 Three bugs found, and the rule they produced

1. **Yahoo's `chartPreviousClose` is the close before the *entire range*, not
   the prior session.** On a 10-day range it reported AVGO at **−13.87%** when
   the real daily move was **+1.21%**, corrupting the whole breadth component.
2. **FRED series publish on different lags** (`DFII10` lands a day after
   `T10YIE`), so comparing each series' own latest step compared *different
   days*. The yield decomposition output "nominal +4bp, real +0bp, breakeven
   +0bp" — arithmetically impossible, and it silently mis-attributed the driver.
   Fixed with `aligned_change()`, which finds the latest date common to all
   compared series.
3. **A narrow-rally rule fired on a non-divergence** — a mega-cap average of
   +0.01% counted as "down".

**The rule: never trust a feed's convenience field. Derive the comparison
yourself and sanity-check the arithmetic.** All three were caught only because
every bias component prints its reasoning.

## 6.2 The DST error — the most dangerous one

Phase-1 research tables listed US data prints at **13:30 UTC year-round**. That
is the *EST* figure. Verified against the live ForexFactory feed, which carries
its own offset: Core PCE on 2026-08-26 is stamped `08:30:00-04:00` = **12:30
UTC**.

This sat in the **stand-aside window** — the most safety-critical number in the
brief. Following the docs, a trader would have stood aside 13:20–14:00 UTC and
traded **straight through** the actual print at 12:30.

Two code paths carried it: hardcoded session windows (NY 13:30–20:00 UTC) and a
fuel curve keyed by UTC hour. Both now resolve through `zoneinfo`. Only Asia is
genuinely fixed in UTC — Tokyo has no DST; London and NY both shift.

**Lesson: anything time-anchored must be derived from exchange local time.** A
hardcoded UTC hour is correct for at most half the year.

## 6.3 Not buying a GEX vendor, and not buying a news API

CBOE gives the same upstream data free. `gex_levels.py` builds the board.

For news, five rounds of regex patching produced five new failure modes:

| Round | Misfire | Structural fix |
|---|---|---|
| 1 | "climb **after** selloff", "**snaps** slump" | reversal detection |
| 2 | Bitcoin/Qatar/Klarna scoring at all | relevance + off-topic gates |
| 3 | "Warns **Top** Customers" matched `tops?` | require "tops estimates" |
| 4 | "cooling on paper, **but** pressures…" | contrast-clause detection |
| 5 | "**May** plunge, **even if** it beats" | modal gate — one whole class |

**That long tail is the finding**, and it is the same failure mode a generic
sentiment API has. So the answer was a pre-filter plus model judgement, not a
different vendor. Marketaux (100 req/day free) is documented as the best
like-for-like swap **if** an API is ever wanted, but it was not needed.

## 6.4 Regex tuning has a long tail — stop patching, change the design

Rounds 1–4 each fixed one phrasing. Round 5's modal gate retired a whole class
at once. When the fifth patch produced a sixth misfire, the correct response was
not a sixth regex but to **shrink what the deterministic tier claims** and route
the rest to the model. `test_news_scorer.py` (22 cases, all passing) then locks
it: every FALSE case is a real observed misfire, every TRUE case is hard news the
HIGH tier must still catch — so tightening the gates can never quietly reduce
the scorer to "never fires". Those tests caught two further bugs *after* the code
looked finished (a bare `forecast` matching "hotter than forecast"; `export
control` lacking a plural, which dropped the single highest-impact tariff
headline for this index).

## 6.5 Filters that were too aggressive

The first budget filter banished **PDH to a footnote** for being 162pts away
against a 156pt budget. Technically out of reach — and the level most likely to
be swept all day. Core day-frame levels now stay on the board flagged
`(stretch)`. Similarly, the first relevance gate silently dropped *"Big week
coming up with PCE, Nvidia earnings and then Jackson Hole"*, *"Federal Reserve
issues FOMC statement"* and a Citi positioning warning.

**Lesson: when a filter's failure mode is losing signal, bias it toward passing
through.**

## 6.6 GitHub is the right home — but not for the stated reason

Running scripts in-session is **cheaper** than dispatching a workflow (a
dispatch costs 1,500–3,000 extra tokens in polling and log retrieval, plus ~2
minutes). GitHub wins on three other things: a **scheduled job pre-computing a
small `latest.json`** is the cheapest read path of all; the **historical archive
builds itself**, which Phase 4 depends on and cannot be retro-fitted; and
analysis logic becomes versioned and diffable.

**Token maths:** raw sources ~13 MB (~3.4M tokens) → reduced payload ~8 KB
(~2.5k tokens). A ~1,400:1 reduction that must happen **in a script** — the
model must never see a raw options chain.

## 6.7 Presentation: layering, not deletion

The brief hit 127 lines ≈ 8 phone screens, read 15 minutes before the open. But
"make it shorter" risks cutting the thing that prevents a bad trade. Decisions:
- Level board 30 rows → 12, carrying more signal.
- Scoring table collapsed behind `<details>`, with a one-line `Driven by:` summary.
- Regime section: **technical read first, plain-English explanation underneath.**
  An earlier pass replaced the jargon outright and *lost* the terminology — the
  user wants to learn it, and pairing the two teaches it.
- **Never cut:** the event gate, the fuel→stop rule, the strategy call, and
  staleness/fallback warnings.

## 6.8 The schedule

Anchored to the session it serves, so it tracks DST. GitHub cron is UTC-only, so
each slot registers both UTC times and the job matches on **local** hour/minute.
Simulated both seasons: exactly four fires per day, no duplicates, no gaps.

| Slot | Anchor | Summer | Winter |
|---|---|---|---|
| Pre-London | 06:00 UK | 05:00 | 06:00 |
| **Pre-NY open** | **09:15 ET** | **13:15** | **14:15** |
| Mid-NY | 13:00 ET | 17:00 | 18:00 |
| EOD archive | 16:15 ET | 20:15 | 21:15 |

The pre-NY slot replaced an originally-proposed 12:00 UTC one, which sat *before*
the 08:30 ET print and so had its levels invalidated minutes later.

---

# 7. Rebuilding from zero

Order matters — each step is verifiable before the next.

1. **Prove cTrader.** Resolve `NAS100` → expect **116**. Pull `D_1`/`H_1`/`M_5`.
   Remember `hours_back`, not bar count.
2. **Prove CBOE.** Fetch `_NDX.json`, confirm rows carry `gamma` and
   `open_interest`. Parse the OSI symbol (`NDX260821C04000000`).
3. **Build GEX** (`cboe_gex.py`): per-strike $GEX, BS-repriced flip, walls, max
   pain. Then **combine NDX+QQQ** (`gex_levels.py`) and add the CFD offset.
4. **Build levels + fuel** (`levels_fuel.py`). Calibrate the cluster tolerance
   empirically — do not guess it.
5. **Build the macro layer** (`macro_probe.py`), then FRED (`fred_probe.py`).
   Hand-verify one number against a known value before trusting any feed.
6. **Build the news pre-filter** (`news_scorer.py`) **and its tests together.**
   Write the regression cases from real misfires as you find them.
7. **Build the bias engine** (`bias_engine.py`). Every rule must print its
   reasoning.
8. **Build session context** (`session_context.py`) with `zoneinfo` from the
   start. Do not hardcode UTC hours.
9. **Build the orchestrator** (`brief.py`), then **journal** and **review**.
10. **Write SKILL.md, references, the slash command, and the sub-agent.**

### The output format is code, not instruction

The agreed presentation lives in `brief.py`'s renderer, and SKILL.md tells the
model to print it **as-is** with an explicit do-not list: don't recompute
numbers, don't reword a level's "what to expect" note, don't expand the
collapsed blocks, don't reorder sections, don't add levels.

This matters because a format settled over several review rounds is worthless if
the model paraphrases it each run. **Every slash-command mode is therefore a
flag on an existing script, never something the model assembles.** `levels` mode
exists as `brief.py --levels` for exactly this reason — verified emitting the
same 12 board rows, byte-identical to the full brief.

**Verification at each stage:**
```bash
cd .claude/skills/nas100-daily-brief/scripts
python3 source_health.py       # expect 31 live (32 with FRED_API_KEY set)
python3 test_news_scorer.py    # expect 22/22
python3 brief.py               # expect a full brief, exit 0
python3 brief.py --levels      # expect the board only, rows identical to above
python3 review_day.py          # expect a graded day, or "nothing to review"
```

**Environment:** `CTRADER_MCP_SLUG` required; `FRED_API_KEY` optional (the brief
degrades gracefully and says so). Neither belongs in the repo — see
`SETUP-SECRETS.md`. Note the Claude Code docs advise against putting credentials
in cloud-environment variables at all; GitHub Actions secrets are the correct
store for scheduled runs.

---

# 8. Open questions and what's next

**Known and unresolved:**
1. **The range budget looks too conservative.** One review (156 vs 266) plus the
   fact that PDH *and* PDL both flag `(stretch)` on a typical day. Needs 3+
   sessions before changing.
2. **The time-of-day range-consumption curve is an estimate**, not measured.
   Replace it from the archive.
3. **Bias weights are reasoned, not fitted.** Re-weight against logged outcomes.
4. **The reviewer has never run on real accumulated history** — it has only been
   verified against a deliberately backdated entry, which was deleted.

**How improvement is actually governed.** Open questions live in
`journal/HYPOTHESES.md` as a register: each carries its claim, the evidence so
far, and the number of sessions needed before it can be acted on.
`scripts/track.py` regenerates the evidence table across every completed trading
day and prints `actionable: YES/NO`. The reviewer consults both, appends today's
observation, and proposes nothing while the answer is NO.

This exists because the first review got it wrong in both available directions:
it proposed a recalibration built on the wrong metric, and cited a synthetic
backdated entry as one of three "independent sessions". The register carries a
withdrawn section so neither can be quietly resurrected. `track.py` also
collapses scans taken within 15 minutes of each other and refuses to grade a
session that is still in progress — both caught inflating the numbers on the
first run.

**Phase 4 questions the archive can answer:** which components actually predict
direction; whether sweeps of the call wall fail more often than sweeps of PDH;
whether strategy selection by gamma regime measurably beats picking one; whether
the fuel model is calibrated.

**A standing rule:** a fabricated or backfilled journal entry silently corrupts
every statistic drawn from the archive. One was created during development to
test the review loop and deleted immediately. The reviewer is instructed to flag
and exclude any it finds.

---

# 8b. Reliability notes

**The NDX cash index does not print outside US cash hours, and says so nowhere.**
Ask CBOE for `_NDX` at 08:26 UTC on a Monday and you get Friday's close — HTTP
200, a plausible number, no error. Only `last_trade_time` reveals it.

Caught on the first live weekday run: the CFD had gapped ~200pts overnight while
cash sat at Friday's print, so `offset = cfd − cash` computed **−200.7** instead
of the true ~−4. Every options level on the board was shifted by 200 points,
during exactly the pre-market window the brief is designed to be read in.

Worse than wrong numbers, it **inverted the trade**. The stale reference put
price *above* the gamma flip → "long gamma, dealers fade extensions, this is
your fade day, use Strategy 1". Corrected, price was *below* the flip → "short
gamma, dealers amplify, Strategy-1 fades have a materially lower hit rate".
Opposite instructions from the same data.

`gex_levels._cash_is_stale()` now checks `last_trade_time`, and when cash is
more than 30 minutes old `_nq_implied_cash()` rolls it forward by the NQ futures
move since NQ's own prior close — futures trade nearly 24h, cash does not. The
brief prints which basis was used and never hides the substitution. If the
futures fallback also fails the board is published with a loud warning rather
than a silent guess.

**CBOE's published greeks carry the same staleness, and it flips the sign.**
Asked "does below-flip mean negative gamma", the brief was found printing
"BELOW flip — short gamma" beside a net GEX of **+0.067bn** and a shape of
`FRONT_FLAT_BACK_LONG` — three mutually contradictory readings. Two causes:

1. The gamma flip was computed from **NDX options only** (3,980 contracts),
   ignoring QQQ's 4,117 — despite this document already stating that NDX alone
   under-counts dealer gamma badly. Including QQQ moved the flip 162 points.
   The naive fix is wrong: QQQ strikes are rescaled into NDX space while their
   gamma and OI belong to QQQ space, so valuing them at NDX spot² over-weights
   QQQ by the ~41× ratio. Each row now carries `scale` and `strike_native` and
   is priced where it actually lives, with only the dollar results combined.
2. The bucket figures used CBOE's **published** greeks, stamped Friday 16:14 at
   a spot of 29,309, while the market sat at 29,136. Published greeks gave
   **+0.46bn** (pinning); repriced at the real spot they gave **−5.48bn**
   (amplifying). Opposite sign, opposite instruction — printed next to a flip
   that *was* repriced. Buckets now reprice with Black-Scholes at the current
   spot whenever the chain is stale, so flip, buckets, walls and shape all
   derive from one basis. All three buckets then read NEGATIVE and the shape
   resolved to `COHERENT_SHORT`, matching the flip.

The general lesson, and the third instance of it in this build: **a feed
returning 200 with a plausible number is not the same as a feed returning
current data.** Yahoo's `chartPreviousClose`, FRED's per-series publication
lags, and now CBOE's out-of-hours cash quote all failed this way.



**cTrader sessions expire under load.** The client retried expiry once, which is
enough for an idle session but not for `fetch_ohlcv_paged`, which issues dozens
of sequential calls — a re-initialised session can expire again immediately.
Observed as `get_trendbars: no result ({'_session_expired': True})` killing an
entire brief on the third consecutive run. A scheduled job that dies here
produces no brief at all, so the retry is now bounded with backoff (3 attempts,
0.4s/0.8s/1.2s) and reports a clear message if it still fails.

**Journal entries are never edited, even when superseded.** Entries written
before the wall-strength change still contain the old `[MAJOR]`/`[MODERATE]`
labels. That is correct: a journal records what was said at the time, and
rewriting history would corrupt every statistic Phase 4 draws from it.

# 9. Honest limitations

1. CBOE options data is **~15 minutes delayed**. A map, not a live feed.
2. **Dealer positioning is assumed, not observed.** Levels and regime are
   robust; absolute dollar figures are approximate. Nobody knows dealer
   inventory — anyone claiming otherwise is running the same assumption.
3. The **7 MB payload must never enter context.** Script-reduced ~1,400:1.
4. **ForexFactory now only publishes `thisweek`.** Nasdaq's per-date endpoint
   fills the gap.
5. **News rules are hand-written and English-only.** They encode one reading of
   how NAS100 responds. Validate against the archive.
6. **`HIGH`-confidence news fires rarely by design** — 0 of 138 headlines on a
   weekend test, which is correct. If it ever scores 8, something regressed.
7. **US holidays are a hardcoded list.** A wrong entry silently turns a closed
   day into a trading day. Extend yearly.
