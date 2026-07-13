# CPI Market Impact Analysis — Methodology

Analysis of how US CPI (headline, "All Items") MoM and YoY releases move
**US500** and **NAS100** in the minutes following the 13:30 UK-local release
(8:30am US Eastern, every release day, regardless of DST — see "Release Timing" below).

## Data sources

- **CPI actual values**: FRED `CPIAUCSL` (seasonally adjusted, for MoM %) and
  `CPIAUCNS` (not seasonally adjusted, for YoY %), cross-checked against
  contemporaneous BLS release text where possible to match the *originally
  reported* figure rather than a later revision.
- **CPI forecast/consensus values**: investing.com / tradingeconomics economic
  calendar history, cross-checked across sources where available.
- **Release dates/times**: BLS official release schedule
  (bls.gov/schedule/news_release/cpi.htm), always 8:30am US Eastern.
- **Price data**: cTrader MCP `get_trendbars`, M_1 (1-minute) OHLC, symbols
  `US500` (id 115) and `NAS100` (id 116). Raw prices are in 1/100000 units;
  divide by 100,000 to get the display index price.

## Release timing / DST handling

US CPI is released at **8:30am America/New_York** on every release date. UK
local time is **not always 13:30** — it depends on whether the UK and US are
both in / both out of daylight saving on that specific date:

- Both on DST (BST + EDT) or both off (GMT + EST): 8:30am ET = **13:30 UK**.
- The ~1-3 week windows each year where the UK and US DST transitions don't
  align (UK DST starts *after* US DST in spring; UK DST ends *before* US DST
  in autumn), the release lands at **12:30 UK** instead.

Each release's exact UK local time is computed per-date from the US Eastern
time rule, not assumed to be constant.

## Expected-reaction classification (pre-trade logic)

For each of MoM and YoY independently, compare actual vs forecast:

- `actual > forecast` → **Bearish** contribution (hotter inflation → hawkish → risk-off for equities)
- `actual < forecast` → **Bullish** contribution (cooler inflation → dovish → risk-on for equities)
- `actual == forecast` → **Neutral** contribution (in line, no fresh catalyst)

Combine the two contributions into one expected label:

- Both non-neutral and agree → **Bullish** / **Bearish** (high-confidence)
- One non-neutral, other neutral → same direction as the non-neutral one (lower confidence)
- Both neutral, OR the two contributions disagree (one hot, one cool) → **Whipsaw expected** (no clean directional edge, elevated two-way risk)

## Actual-reaction classification (price-based)

Let `P0` = close of the 1-minute candle ending exactly at release time (last
print before the number hits). Let `P1, P5, P15, P30` = close price 1 / 5 /
15 / 30 minutes after release.

- `net_move = P30 - P0` (the headline number used for points-moved)
- `initial_move = P5 - P0` (immediate impulse)
- `threshold` = 0.05% of `P0`, computed per event/instrument (keeps the bar fair across different index price levels)

Classification:

1. `|net_move| < threshold` → **Whipsaw / Flat** (no sustained direction survived 30 minutes)
2. `sign(initial_move) != sign(net_move)` and the reversal from the post-impulse extreme back through `P0` exceeds `threshold` → **Whipsaw** (sharp initial move that reversed)
3. Otherwise → **Bullish** if `net_move > 0`, **Bearish** if `net_move < 0`

**Points moved** (reported only for Bullish/Bearish outcomes) = `|net_move|`
in raw index points. Whipsaw events instead report the initial spike range
(`high - low` in the first 5 minutes) to characterize the chop.

## Hit / Miss

A release "hits" if the actual-reaction label matches the expected-reaction
label (Whipsaw counted as matching Whipsaw). This is the headline accuracy
metric for "does the textbook CPI-surprise trade logic actually work on
US500/NAS100."

## Known limitations

- Headline CPI only (not core CPI ex food & energy), per the request scope.
- Forecast/consensus figures are sourced from public calendar sites, which
  themselves aggregate a survey — treat as indicative consensus, not a
  single authoritative number.
- The Oct/Nov 2025 US government shutdown disrupted the BLS release
  schedule; see `data/cpi_calendar.csv` notes column for how each affected
  month was handled.
- cTrader price history reflects this broker's own feed/spread, not a
  composite/NBBO index price — absolute point moves are broker-specific.
