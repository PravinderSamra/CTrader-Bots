# Pre-registered test: the NAS100 range breakout on gold and bitcoin

Written 30 Sep 2026, before any run. The rules below are fixed now so the result can't be tuned after the fact.

## Question
Does the NAS100 London Range breakout (range 02:00–09:30 New York, entry 10:00–11:00 NY, close 15:50 NY)
work on other markets, so that a second bot can spread the risk?

## Candidates
| Market | Why | Concern |
|---|---|---|
| **XAUUSD (gold)** | Active in the NY morning; moves largely independently of US stocks | The earlier London-open (Asian range) gold test failed, but it used a different design |
| **BTCUSD (bitcoin)** | Since the 2024 US ETFs, the US open drives much of its flow | Larger costs; partly follows the Nasdaq |
| US30, US500 | – | Excluded: same US open as NAS100, so bad days coincide (US500 lost on 41% of NAS losing days) |
| GER40 / UK100 | – | Excluded: rejected in Vanessa's earlier work |

## Settings
Same bot (v3.0 Add To Winner), **Add To Winner OFF**, Vanessa's live NAS100 settings. Only these may differ:
- **Fixed stop (points)**, scaled to each market. On NAS100 the 60-point stop is about 0.25 × the median NY-session
  range (median 240 points, Jul 2023 – Sep 2026), and about 0.46 × the median 02:00–09:30 range (130 points).
  - Gold, same period: median NY-session range $23.3 and median 02:00–09:30 range $22.4, so the equivalent stop is about $6–10.
    **Grid: $6, $8, $10.**
  - Bitcoin (recent sample, price about $84k): equivalent stop about $300–600. **Grid: $300, $450, $600.**
- Commission and spread: FTMO's costs for each market. Weekdays only (Trade Saturday and Trade Sunday = No).
- Risk Amount $300, tick data, Trades-Only Log = Yes.

## Procedure
1. **Tuning, 1 Jan 2021 – 31 Dec 2023:** run the 3 stop sizes. Pick the one with the highest net profit
   (the smallest stop if two are within 5%). If none is profitable, **stop: FAIL**, and skip step 2.
2. **Test, 1 Jan 2024 – 28 Sep 2026, run ONCE** with the chosen stop. No further changes after this run.

## Pass (all must hold in the test period)
- Profit factor ≥ 1.2 and net profit > 0
- Profitable in at least 2 of the 3 test years (2026 counts as a year)
- Max equity drawdown ≤ 8% at $300 risk
- On days when both it and NAS100 traded, both lost on no more than 35% of those days (so it genuinely spreads the risk)

A market that passes goes to the combined test with NAS100 and the growth ladder (as in `COMBINED_NAS100_US500.md`).
Add To Winner would only be tried after a pass.

## Results

### Gold (XAUUSD), tuning 2021-01-01 .. 2023-12-31, Add To Winner off, $300 risk (run 30 Sep 2026)
On this account gold's pip is $1, so Fixed Stop Points = the stop in dollars.

| Stop | Net profit |
|---|---|
| $6 | −$6,676.12 |
| $8 | −$5,877.15 |
| $10 | −$4,997.81 |

**PROVISIONAL, TO BE RE-RUN:** these runs used bar data, not tick data (Vanessa, 30 Sep). With stops this tight, bar data
can get the order of stop and target wrong, so they don't count yet. All three lost; the re-run on tick data decides.

### Bitcoin (BTCUSD), tuning 2021-01-01 .. 2023-12-31, tick data, Add To Winner off, $300 risk (run 30 Sep 2026)
On this account bitcoin's pip is $1, so Fixed Stop Points = the stop in dollars.

| Stop | Net profit | Max equity DD | Wins / trades |
|---|---|---|---|
| $300 | +$3,487.53 | 9.64% | 120 / 360 |
| **$450** | **+$8,397.81** | **7.70%** | **140 / 360** |
| $600 | +$5,895.55 | 6.43% | 151 / 360 |

**Chosen by the rule (highest net profit): $450.** The test (2024-01-01 .. 2026-09-28) is run once with a $450 stop.
