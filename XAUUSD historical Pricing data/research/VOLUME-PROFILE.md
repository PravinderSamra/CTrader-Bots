# Volume Profile Research — POC / VAH / VAL on XAUUSD

Scripts: `12_volume_profile.py` (profile construction + descriptive probabilities), `13_profile_strategies.py` (**invalidated first pass — kept as audit trail**), `14_profile_fixed.py` (corrected backtests). Costs $0.40/oz RT throughout.

**Method.** Per dealing day (22:00→21:59 UTC), each 1m bar's volume is spread across its high–low range into bins of ATR20/150 width. POC = highest-volume bin; Value Area = 70% of volume expanded around POC. Note: cTrader volume is **tick count**, so these are TPO-style (time-at-price) profiles — the structure most retail profile traders actually chart. Median VA width = $14.8 ≈ 43% of ATR.

---

## 1. Descriptive probabilities (the valid map facts)

| Fact | Number |
|---|---|
| Open location vs prior VA | inside 52% · above 25% · below 23% |
| P(touch prior POC) — open inside VA | **84.6%** |
| P(touch prior POC) — open above / below VA | 41.3% / 50.0% |
| Open outside VA → P(return to nearer VA edge) | **74.0%** |
| Open outside VA → P(reach prior POC) | 45.6% |
| Naked POC revisited next day / within 5 days / within 20 days | 65.9% / **82.7%** / 90.7% |
| **The classic "80% rule"** (accepted back into VA → rotates to far edge) | **33.8%** — the rule is FALSE on gold (failure case is more common: 40.3%) |

The magnetism is real — but it is *proximity geometry*, not directional information. Price visits nearby high-volume levels because they are nearby, not because they pull.

## 2. The audit (important — read once)

The first backtest run produced S1 (your POC-rotation idea) at **+1.55R avg, 77% win, −2.2R maxDD** — a result far too good to be true, and it wasn't. Two bugs: (1) "touch" was coded as `high ≥ level`, which is true whenever price is merely *above* a level, so the sim "bought" at levels many dollars below market and banked phantom profit; (2) the end-of-day flatten check misfired on evening bars. The tell was in the trade forensics: 1,182 of 1,269 trades were phantom evening fills. **Corrected, the raw success probability of the displacement geometry fell from a claimed 79.3% to 48.3% — almost exactly the 46% a pure random walk predicts for those barrier distances.** Every number in section 3 is from the corrected engine, with entries only at genuinely traded levels approached from the correct side.

## 3. Corrected strategy results — every eventuality tested

| Strategy | n | Win% | avgR | Verdict |
|---|---|---|---|---|
| S1 POC displacement → TP at VA edge *(your example)* | 768 | 47.8 | **−0.126** | ❌ |
| S1b same, no TP (stop + 20:55 exit) | 834 | 20.6 | −0.051 | ❌ |
| S2 Open outside VA → fade to nearer edge | 580 | 59.1 | −0.053 | ❌ (59% win, payoff poor) |
| S3 Inside open far from POC → trade to POC | 259 | 44.0 | −0.104 | ❌ |
| S4 "80% rule" acceptance rotation | 397 | 46.6 | +0.018 | ❌ ≈ zero, inconsistent years |
| S5 VA-edge rejection fade after 12:00 → TP POC | 283 | 41.3 | −0.038 | ❌ |

Six mechanical implementations covering rotation, magnetism, responsive fading, and acceptance — **none has positive expectancy after realistic costs**, and none shows year-over-year consistency. This is the same lesson the math/physics study predicted: prior-day levels are *locations*, and in a Hurst-0.5 market locations carry no directional information. The market visits them (the map facts above are true) but which way it leaves is a coin flip, and the fade/rotation payoffs after costs are slightly worse than the coin.

## 4. What profile IS good for here (the constructive findings)

1. **A filter for the ORB (real, modest):** ORB breakouts that fire *against* the side of an outside-value open earn **+0.004R** (n=304) vs **+0.123R** on inside-value days (n=650) and +0.078R aligned (n=297). Rule for the engine: **when the day opens outside the prior value area, skip (or halve) ORB signals in the opposite direction** — those are the gap-trap days.
2. **Target selection:** naked POCs (82.7% revisited within 5 days) and the prior POC on inside-open days (84.6% touch) join PDH/PDL (85.6%) as legitimate take-partial destinations for positions initiated by the validated systems.
3. **Day-type context:** open outside value (48% of days) marks imbalance; combined with the Asia-range map it sharpens the trend-day/range-day read. Context, not entries.
4. *(Tested and not useful: "initiative vs responsive" ORB split — responsive slightly better but inconsistent; ignore.)*

## 5. Verdict

Session volume profile on XAUUSD is a **map, not a signal**. Its levels are genuinely gravitational (touch rates 65–85%) but mechanically trading toward or away from them — in all six configurations including the POC→VA-edge rotation — nets zero or worse after costs. Keep profiles on the chart for targets and for the ORB gap-trap filter; allocate zero risk to standalone profile entries. The consistent pattern across this whole research project holds: **edges live in scheduled flows, expansion events, and stored structural energy — not in static levels.**

---

## 6. The recommended SVP strategy — "Profile-Filtered ORB" (added after §1–5)

Since no standalone SVP entry survived testing, the mechanically successful use of SVP is as **map + filter + targets around the validated NY ORB trigger**. Backtested (scripts output below, 2021–2026, $0.40/oz costs):

| Variant | n | Win% | avgR | maxDD |
|---|---|---|---|---|
| ORB baseline | 1,251 | 42.3 | +0.083 | −27.5R |
| **ORB + SVP gap-trap filter** | **947** | **43.0** | **+0.109** | **−23.4R** |
| + 50% partial at prior POC in path | 947 | 43.9 | +0.089 | −19.2R |

The filter version is +31% expectancy per trade with 24% fewer trades and fixes the weak 2026 (−0.01 → +0.04 avgR). The POC-partial variant trades ~0.02R expectancy for ~18% less drawdown — optional smoothing.

**Mechanical steps (UK summer clock; −1h in winter):**
1. **11pm** — dealing day starts. Build yesterday's session profile; mark **POC, VAH, VAL**; maintain the list of **naked POCs** from prior days.
2. **Reopen classification** — note the day's open vs prior value area: **inside / above / below**.
3. **8am** — add Asia High/Low and PDH/PDL to the map (targets only).
4. **2:00pm** — mark the 1:30–2:00pm opening range (OR). Sanity: skip the day if OR > 0.5×ATR20 or < 0.04×ATR20.
5. **Place OCO stop orders** at OR-high (buy) and OR-low (sell), **except**: day opened **above** value → no sell order; opened **below** value → no buy order (the gap-trap filter). Inside-value opens keep both.
6. On fill, cancel the other side. **Stop = far side of the OR.** No take-profit, no trailing.
7. *Optional:* if the prior POC (or nearest naked POC) lies beyond entry in the trade direction, exit 50% there; run the rest.
8. **Flat at 9pm** (8pm winter) or at the stop. One trade per day. Risk 0.5–1% of equity on the OR stop distance, sized daily off ATR20.

Everything else on the profile chart — VAH/VAL rotation trades, POC magnet trades, 80%-rule trades — remains untraded per §3.
