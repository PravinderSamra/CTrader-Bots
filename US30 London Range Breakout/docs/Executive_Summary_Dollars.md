# Executive Summary — P&L in Dollars

**$100,000 account · flat $100 risk per trade (1R = $100) · 3-year backtest (Jul 2023 – Jul 2026).**

Dollars = R × $100 (independent of stop size). Wins = trades closed in profit, losses = trades closed in loss. Streaks = consecutive wins/losses in date order. First qualifying high-volume breakout per day. **Dealing costs are modelled** as one bid/ask spread per trade (US30 2.0pt, NAS100 1.5pt; spread-bet indices carry no separate commission). Slippage on stops not modelled. Interactive version with a Gross/After-costs toggle: `exec_summary.html`; one-page PDF: `London_Range_Breakout_Exec_Summary.pdf`. Month & week detail: `analysis/dollar/*_monthly*.csv`, `*_weekly*.csv`.

## 3-year net profit — the decision (after costs)

| Instrument | 2.0R | 2.5R | 3.0R | 3.5R | Best |
|---|--:|--:|--:|--:|:--:|
| **US30** | +$6,561 | +$8,694 | +$10,033 ✅ | +$8,498 | 3.0R |
| **NAS100** | +$2,626 | +$5,263 | +$7,031 | +$7,807 ✅ | 3.5R |

### Gross → net (cost impact)

| Instrument | RR | Gross | Net | Cost drag |
|---|--:|--:|--:|--:|
| US30 | 2.0R | +$8,198 | +$6,561 | −$1,637 |
| US30 | 2.5R | +$10,330 | +$8,694 | −$1,637 |
| US30 | 3.0R | +$11,670 | +$10,033 | −$1,637 |
| US30 | 3.5R | +$10,135 | +$8,498 | −$1,637 |
| NAS100 | 2.0R | +$4,118 | +$2,626 | −$1,492 |
| NAS100 | 2.5R | +$6,756 | +$5,263 | −$1,492 |
| NAS100 | 3.0R | +$8,523 | +$7,031 | −$1,492 |
| NAS100 | 3.5R | +$9,299 | +$7,807 | −$1,492 |

> **US30 at 3.0R nets +$10,033** (highest total). **NAS100 (best +$7,807 at 3.5R)** earns comparable dollars in ~35% fewer trades with roughly half the drawdown, and is profitable every year (US30 was near-flat in 2024). Costs trim ~$1,500–1,650 per configuration but do not overturn the edge.

## US30 — yearly detail (net of costs)

*Configuration: range 08:00→09:30 ET · execute 10:00–13:00 ET · **75pt** stop · vol ≥1.2× · spread 2.0pt ($2.67/trade)*

### US30 — 2.0R target

| Year | Trades | Won | Lost | Win % | Longest win streak | Longest loss streak | Net P&L | Balance |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| 2023 *(part-yr)* | 95 | 43 | 52 | 45.3% | 6 | 7 | +$1,202 | $101,202 |
| 2024 | 218 | 77 | 141 | 35.3% | 5 | 8 | −$936 | $100,267 |
| 2025 | 217 | 94 | 123 | 43.3% | 4 | 7 | +$4,739 | $105,006 |
| 2026 *(part-yr)* | 83 | 34 | 49 | 41.0% | 3 | 6 | +$1,556 | $106,561 |
| **3-yr total** | **613** | **248** | **365** | **40.5%** | — | — | **+$6,561** | **$106,561** |

### US30 — 2.5R target

| Year | Trades | Won | Lost | Win % | Longest win streak | Longest loss streak | Net P&L | Balance |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| 2023 *(part-yr)* | 95 | 41 | 54 | 43.2% | 6 | 7 | +$1,065 | $101,065 |
| 2024 | 218 | 73 | 145 | 33.5% | 5 | 8 | +$90 | $101,155 |
| 2025 | 217 | 87 | 130 | 40.1% | 4 | 7 | +$5,150 | $106,305 |
| 2026 *(part-yr)* | 83 | 32 | 51 | 38.6% | 3 | 9 | +$2,389 | $108,694 |
| **3-yr total** | **613** | **233** | **380** | **38.0%** | — | — | **+$8,694** | **$108,694** |

### US30 — 3.0R target

| Year | Trades | Won | Lost | Win % | Longest win streak | Longest loss streak | Net P&L | Balance |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| 2023 *(part-yr)* | 95 | 41 | 54 | 43.2% | 6 | 7 | +$1,230 | $101,230 |
| 2024 | 218 | 70 | 148 | 32.1% | 5 | 8 | +$480 | $101,710 |
| 2025 | 217 | 83 | 134 | 38.2% | 4 | 7 | +$5,267 | $106,976 |
| 2026 *(part-yr)* | 83 | 31 | 52 | 37.3% | 3 | 9 | +$3,057 | $110,033 |
| **3-yr total** | **613** | **225** | **388** | **36.7%** | — | — | **+$10,033** | **$110,033** |

### US30 — 3.5R target

| Year | Trades | Won | Lost | Win % | Longest win streak | Longest loss streak | Net P&L | Balance |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| 2023 *(part-yr)* | 95 | 41 | 54 | 43.2% | 6 | 7 | +$1,058 | $101,058 |
| 2024 | 218 | 68 | 150 | 31.2% | 5 | 9 | −$64 | $100,995 |
| 2025 | 217 | 80 | 137 | 36.9% | 4 | 8 | +$5,012 | $106,006 |
| 2026 *(part-yr)* | 83 | 30 | 53 | 36.1% | 3 | 9 | +$2,492 | $108,498 |
| **3-yr total** | **613** | **219** | **394** | **35.7%** | — | — | **+$8,498** | **$108,498** |

## NAS100 — yearly detail (net of costs)

*Configuration: range 02:00→09:30 ET · execute 10:00–11:00 ET · **40pt** stop · vol ≥1.2× · spread 1.5pt ($3.75/trade)*

### NAS100 — 2.0R target

| Year | Trades | Won | Lost | Win % | Longest win streak | Longest loss streak | Net P&L | Balance |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| 2023 *(part-yr)* | 81 | 29 | 52 | 35.8% | 2 | 6 | −$369 | $99,631 |
| 2024 | 152 | 57 | 95 | 37.5% | 4 | 9 | +$1,125 | $100,756 |
| 2025 | 147 | 56 | 91 | 38.1% | 5 | 8 | +$584 | $101,340 |
| 2026 *(part-yr)* | 18 | 11 | 7 | 61.1% | 6 | 2 | +$1,286 | $102,626 |
| **3-yr total** | **398** | **153** | **245** | **38.4%** | — | — | **+$2,626** | **$102,626** |

### NAS100 — 2.5R target

| Year | Trades | Won | Lost | Win % | Longest win streak | Longest loss streak | Net P&L | Balance |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| 2023 *(part-yr)* | 81 | 29 | 52 | 35.8% | 2 | 6 | +$561 | $100,561 |
| 2024 | 152 | 51 | 101 | 33.6% | 4 | 10 | +$1,507 | $102,069 |
| 2025 | 147 | 53 | 94 | 36.1% | 5 | 8 | +$1,653 | $103,722 |
| 2026 *(part-yr)* | 18 | 11 | 7 | 61.1% | 6 | 2 | +$1,542 | $105,263 |
| **3-yr total** | **398** | **144** | **254** | **36.2%** | — | — | **+$5,263** | **$105,263** |

### NAS100 — 3.0R target

| Year | Trades | Won | Lost | Win % | Longest win streak | Longest loss streak | Net P&L | Balance |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| 2023 *(part-yr)* | 81 | 29 | 52 | 35.8% | 2 | 6 | +$715 | $100,715 |
| 2024 | 152 | 46 | 106 | 30.3% | 4 | 12 | +$1,406 | $102,121 |
| 2025 | 147 | 52 | 95 | 35.4% | 5 | 8 | +$2,918 | $105,039 |
| 2026 *(part-yr)* | 18 | 11 | 7 | 61.1% | 6 | 2 | +$1,992 | $107,031 |
| **3-yr total** | **398** | **138** | **260** | **34.7%** | — | — | **+$7,031** | **$107,031** |

### NAS100 — 3.5R target

| Year | Trades | Won | Lost | Win % | Longest win streak | Longest loss streak | Net P&L | Balance |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| 2023 *(part-yr)* | 81 | 28 | 53 | 34.6% | 2 | 7 | +$591 | $100,591 |
| 2024 | 152 | 44 | 108 | 28.9% | 4 | 12 | +$2,097 | $102,688 |
| 2025 | 147 | 49 | 98 | 33.3% | 3 | 12 | +$3,367 | $106,055 |
| 2026 *(part-yr)* | 18 | 10 | 8 | 55.6% | 6 | 3 | +$1,752 | $107,807 |
| **3-yr total** | **398** | **131** | **267** | **32.9%** | — | — | **+$7,807** | **$107,807** |
