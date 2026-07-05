# Executive Summary — P&L in Dollars

**$100,000 account · flat $100 risk per trade (1R = $100) · 3-year backtest (Jul 2023 – Jul 2026).**

Dollars = R × $100 (independent of stop size). Wins = trades closed in profit, losses = trades closed in loss. Streaks = consecutive wins/losses in date order. First qualifying high-volume breakout per day. **Costs (spread/commission) not yet modelled** (~ −$1,200 to −$1,600 drag over the sample). Interactive version: `exec_summary.html`. Month & week detail: `analysis/dollar/*_monthly.csv`, `*_weekly.csv`.

## 3-year net profit — the decision

| Instrument | 2.0R | 2.5R | 3.0R | 3.5R | Best |
|---|--:|--:|--:|--:|:--:|
| **US30** | $8,198 | $10,330 | $11,670 ✅ | $10,135 | 3.0R |
| **NAS100** | $4,118 | $6,756 | $8,523 | $9,299 ✅ | 3.5R |

> **US30 at 3.0R = +$11,670** is the highest single total. **NAS100 (best +$9,299 at 3.5R)** earns comparable dollars in ~35% fewer trades with roughly half the drawdown, and is profitable every year (US30 lost −$354 in 2024). Higher R targets raise totals up to ~3R, then plateau.

## US30

*Configuration: range 08:00→09:30 ET · execute 10:00–13:00 ET · **75pt** stop · vol ≥1.2×*

### US30 — 2.0R target

| Year | Trades | Won | Lost | Win % | Longest win streak | Longest loss streak | P&L | Balance |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| 2023 *(part-yr)* | 95 | 43 | 52 | 45.3% | 6 | 7 | +$1,456 | $101,456 |
| 2024 | 218 | 77 | 141 | 35.3% | 5 | 8 | −$354 | $101,102 |
| 2025 | 217 | 94 | 123 | 43.3% | 4 | 7 | +$5,318 | $106,421 |
| 2026 *(part-yr)* | 83 | 34 | 49 | 41.0% | 3 | 6 | +$1,777 | $108,198 |
| **3-yr total** | **613** | **248** | **365** | **40.5%** | — | — | **+$8,198** | **$108,198** |

### US30 — 2.5R target

| Year | Trades | Won | Lost | Win % | Longest win streak | Longest loss streak | P&L | Balance |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| 2023 *(part-yr)* | 95 | 41 | 54 | 43.2% | 6 | 7 | +$1,318 | $101,318 |
| 2024 | 218 | 73 | 145 | 33.5% | 5 | 8 | +$672 | $101,991 |
| 2025 | 217 | 87 | 130 | 40.1% | 4 | 7 | +$5,729 | $107,720 |
| 2026 *(part-yr)* | 83 | 32 | 51 | 38.6% | 3 | 9 | +$2,611 | $110,330 |
| **3-yr total** | **613** | **233** | **380** | **38.0%** | — | — | **+$10,330** | **$110,330** |

### US30 — 3.0R target

| Year | Trades | Won | Lost | Win % | Longest win streak | Longest loss streak | P&L | Balance |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| 2023 *(part-yr)* | 95 | 41 | 54 | 43.2% | 6 | 7 | +$1,484 | $101,484 |
| 2024 | 218 | 70 | 148 | 32.1% | 5 | 8 | +$1,062 | $102,545 |
| 2025 | 217 | 83 | 134 | 38.2% | 4 | 7 | +$5,846 | $108,391 |
| 2026 *(part-yr)* | 83 | 31 | 52 | 37.3% | 3 | 9 | +$3,279 | $111,670 |
| **3-yr total** | **613** | **225** | **388** | **36.7%** | — | — | **+$11,670** | **$111,670** |

### US30 — 3.5R target

| Year | Trades | Won | Lost | Win % | Longest win streak | Longest loss streak | P&L | Balance |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| 2023 *(part-yr)* | 95 | 41 | 54 | 43.2% | 6 | 7 | +$1,312 | $101,312 |
| 2024 | 218 | 68 | 150 | 31.2% | 5 | 9 | +$518 | $101,830 |
| 2025 | 217 | 80 | 137 | 36.9% | 4 | 8 | +$5,591 | $107,422 |
| 2026 *(part-yr)* | 83 | 30 | 53 | 36.1% | 3 | 9 | +$2,713 | $110,135 |
| **3-yr total** | **613** | **219** | **394** | **35.7%** | — | — | **+$10,135** | **$110,135** |

## NAS100

*Configuration: range 02:00→09:30 ET · execute 10:00–11:00 ET · **40pt** stop · vol ≥1.2×*

### NAS100 — 2.0R target

| Year | Trades | Won | Lost | Win % | Longest win streak | Longest loss streak | P&L | Balance |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| 2023 *(part-yr)* | 81 | 29 | 52 | 35.8% | 2 | 6 | −$66 | $99,934 |
| 2024 | 152 | 58 | 94 | 38.2% | 7 | 9 | +$1,695 | $101,630 |
| 2025 | 147 | 56 | 91 | 38.1% | 5 | 8 | +$1,135 | $102,765 |
| 2026 *(part-yr)* | 18 | 11 | 7 | 61.1% | 6 | 2 | +$1,353 | $104,118 |
| **3-yr total** | **398** | **154** | **244** | **38.7%** | — | — | **+$4,118** | **$104,118** |

### NAS100 — 2.5R target

| Year | Trades | Won | Lost | Win % | Longest win streak | Longest loss streak | P&L | Balance |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| 2023 *(part-yr)* | 81 | 29 | 52 | 35.8% | 2 | 6 | +$865 | $100,865 |
| 2024 | 152 | 52 | 100 | 34.2% | 7 | 10 | +$2,077 | $102,943 |
| 2025 | 147 | 53 | 94 | 36.1% | 5 | 8 | +$2,204 | $105,147 |
| 2026 *(part-yr)* | 18 | 11 | 7 | 61.1% | 6 | 2 | +$1,609 | $106,756 |
| **3-yr total** | **398** | **145** | **253** | **36.4%** | — | — | **+$6,756** | **$106,756** |

### NAS100 — 3.0R target

| Year | Trades | Won | Lost | Win % | Longest win streak | Longest loss streak | P&L | Balance |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| 2023 *(part-yr)* | 81 | 29 | 52 | 35.8% | 2 | 6 | +$1,018 | $101,018 |
| 2024 | 152 | 47 | 105 | 30.9% | 7 | 12 | +$1,976 | $102,995 |
| 2025 | 147 | 52 | 95 | 35.4% | 5 | 8 | +$3,469 | $106,464 |
| 2026 *(part-yr)* | 18 | 11 | 7 | 61.1% | 6 | 2 | +$2,059 | $108,523 |
| **3-yr total** | **398** | **139** | **259** | **34.9%** | — | — | **+$8,523** | **$108,523** |

### NAS100 — 3.5R target

| Year | Trades | Won | Lost | Win % | Longest win streak | Longest loss streak | P&L | Balance |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| 2023 *(part-yr)* | 81 | 28 | 53 | 34.6% | 2 | 7 | +$895 | $100,895 |
| 2024 | 152 | 45 | 107 | 29.6% | 7 | 12 | +$2,667 | $103,562 |
| 2025 | 147 | 49 | 98 | 33.3% | 3 | 12 | +$3,918 | $107,480 |
| 2026 *(part-yr)* | 18 | 10 | 8 | 55.6% | 6 | 3 | +$1,819 | $109,299 |
| **3-yr total** | **398** | **132** | **266** | **33.2%** | — | — | **+$9,299** | **$109,299** |
