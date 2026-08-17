# Trade Review — Monday 17 August 2026

Live data pulled from cTrader (symbol 241, XAUUSD_SB) after the session closed at 21:00 UTC.
Run through Strategy 1 exactly as written.

## ⚠️ Correction to the playbook

The tested opening range is **13:30–14:00 UTC**. In UK summer time (BST) that is **2:30–3:00pm**,
not 1:30–2:00pm as the playbook previously said. The playbook has been corrected. Best practice:
**set your chart to UTC** so DST never trips you up.

## Today's numbers

| Item | Value |
|---|---|
| ATR20 (20 days before today) | **$89.89** |
| Day open (22:00 UTC Sun) | 4379.84 |
| Friday's value area | VAL 4337.58 · POC 4377.18 · VAH 4396.38 |
| Open location | **INSIDE** value → both orders allowed |
| Asia range (22:00–07:00) | 4367.15 – 4416.50 = $49.35 (55% of ATR20 — wide, a good sign) |
| Friday high / low | 4397.08 / 4310.88 |

## What you would have marked

**The box (13:30–14:00 UTC / 2:30–3:00pm UK):**
- **Box HIGH = 4416.25**
- **Box LOW = 4384.61**
- Height **$31.64 = 35.2% of ATR20** → inside the 4%–50% gate → **valid trade day**

**Orders placed at 14:00 UTC** (both allowed, open was inside value):
- Buy stop just above **4416.25**
- Sell stop just below **4384.61**, OCO

## The trade

| | |
|---|---|
| Break | **UPSIDE at 14:16 UTC** (3:16pm UK) — long filled ≈ **4416.25** |
| Stop | 4416.25 − (0.25 × 89.89) = **4393.78** |
| Risk | **$22.47/oz** |
| Size — Razor 1% | $1,000 ÷ 22.47 = **44.5 oz (0.44 lots)** |
| Size — FTMO 0.5% | $500 ÷ 22.47 = **22.2 oz (0.22 lots)** |
| T1 (+1R) | **4438.72** |
| Downside side broken? | No — box low never traded → **no second trade** |

## Outcome

- Day high reached **4428.84** — that is +$12.59, or **0.56R**. T1 at 4438.72 was **$9.88 short**.
- The stop at 4393.78 was never threatened either (day low after entry stayed above it).
- Position ran to the **20:55 UTC flat** and closed at **4415.77** — essentially at entry.

**Result: −$0.73/oz = −0.03R.** Razor 1%: **−$32**. FTMO 0.5%: **−$16**.

A scratch. No partial was taken (never reached +1R), so no break-even move happened.

## What today teaches

1. **This is the most common outcome, not a failure.** Roughly half of days finish near flat. The
   strategy makes its money from the minority of days that trend all afternoon.
2. **The filters all passed and the trade still went nowhere.** Correct process, neutral result —
   that is the job. Nothing was done wrong today.
3. **One detail worth noticing:** Friday's high (4397.08) was already well below the entry, so the
   break happened into open space with no prior-day level ahead as a magnet. The Asia research
   found that is the *weakest* magnet condition (21–22% sustain vs 33% when a level sits just
   ahead). It is not a rule in Strategy 1 — one day proves nothing — but it is consistent.
4. **The box high (4416.25) was almost exactly the Asia high (4416.50).** When those coincide the
   level is more significant, and price closing the day at 4416.52 — right on it — shows it was
   the day's pivot.
