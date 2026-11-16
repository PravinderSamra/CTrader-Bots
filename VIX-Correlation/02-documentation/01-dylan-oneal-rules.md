# VIX / ES / NQ correlation — rules extracted from source

**Source:** Chart Fanatics, guest Dylan O'Neal (Wall Street prop trader).
Recorded early June 2025; examples dated Feb 20, May 7 and May 28, 2025.
Transcript supplied by Vanessa 2026-11-16. Raw transcript not yet archived
(see "Provenance" at the end).

**Status: NOT TESTED.** Nothing here has been backtested. This document is a
faithful extraction of what the source claims, written before any testing so
that the rules are pre-registered and cannot be quietly reshaped to fit a
result later. Same discipline as the wall studies.

---

## 1. The underlying thesis

- VIX measures expected S&P volatility over the next 30 days, priced off SPX
  options positioning.
- SPX put demand up → VIX up. Put demand down → VIX down.
- VIX up = "pressure put onto ES". VIX down = "pressure taken off ES".
- Claim: ~90% of US S&P futures volume is algorithmic, and those buy/sell
  programs are tied to VIX pricing. VIX up triggers sell programs; VIX down
  triggers buy programs. Presented as partly self-reinforcing.
- VIX is described as a **leading** indicator: it can move before ES/NQ.
- VIX is correlated to **S&P options only**, NOT Nasdaq options. NQ is usable
  as confluence only because NQ and ES share heavy constituents.

Directional consequence used throughout:

| VIX state | Implication for ES |
|---|---|
| Weak / downtrending | Support levels more likely to hold; dips get bought |
| Strong / uptrending | Resistance more likely to hold; rallies get sold |

---

## 2. Setup A — "triple confirmation" long (the bear trap)

The headline setup, and the one described in most detail.

**Conditions, all on the same session:**

1. **ES breaches below its previous day low (PDL)**, "with momentum".
2. **VIX shows relative weakness** — VIX has NOT reached its previous day
   high (PDH); it is making a *lower high* relative to PDH.
3. **NQ shows relative strength** — NQ makes a *higher low*, i.e. does NOT
   break its own PDL.

Reading: ES is breaking down, but the options market is not pricing the
turbulence that a real breakdown needs, and NQ refuses to confirm. Therefore
the downside continuation is expected to be short-lived → squeeze back up.

**Entry trigger:** wait for **BOTH ES and NQ to recapture back above the
previous day low**, then enter long.

**Entry is on price, not on a candle close.** Stated explicitly and with a
reason: waiting for a close means the close may print far from the level,
widening the stop unpredictably. Entry is "as soon as price is above, with
some cushion".

**Which instrument to buy:** whichever is showing **relative strength** —
the one that went less deep below its PDL. Explicitly: do not buy the weak
one.

**Stop loss:** below the low made during the breach.

**Target:** "ideally more than 2:1". Take-profits mapped in advance at
technical levels, taking profit *ahead* of the level, not at it.

**Worked example (May 7, 2025, from a community member):**
- ES and NQ both breached their PDL — NQ also made a lower low, so condition
  3 FAILED. Source still considered the thesis valid but lower probability,
  because VIX weakness is "the main factor".
- Bought ES (shallower breach = relative strength).
- Entry ~5608, stop ~5594. Risk ~12–14 handles, "to make 24, 30, and then
  some".

---

## 3. Setup B — all three in sync, short continuation

The mirror, and the highest-probability *continuation* case:

1. ES breaches below PDL
2. NQ breaches below PDL
3. **VIX at or above its PDH**, with momentum

→ "largest probability of sustained downside pressure".

Stated as a gate on shorting: if you are going to short below PDL, you
**need** VIX at or above its PDH. Without it, the move is expected to be
short-lived and to squeeze.

---

## 4. Setup C — the front-run

VIX breaks above its PDH **before** ES and NQ reach their PDLs. Treated as an
earlier, better-priced short entry, on the basis that put demand is already
rising. Flagged by the source as the discretionary version of Setup B.

---

## 5. The 1% rule

Uses net % change versus yesterday's close.

| Condition | Implication | Action |
|---|---|---|
| ES up ≥1% **and** VIX up ≥1% | Too much pressure; ES unlikely to sustain the highs | Find resistance; expect roll-over |
| ES down ≥1% **and** VIX down ≥1% | Downside not confirmed | Find support; expect a bounce |

Normal behaviour would be the two moving inversely, so both moving the same
way by ≥1% is the anomaly being traded.

Noted as not happening often.

---

## 6. Rule of 16

VIX ÷ 16 = implied average **daily % move** in the S&P over the next 30 days.
VIX 32 → 2% daily. VIX 64 → 4% daily. Offered as a volatility-expectation
tool, not an entry rule. (Source does not know the derivation; it is the
annualisation constant, √252 ≈ 15.87.)

---

## 7. Known failure mode (stated by the source)

**ES at all-time or multi-year highs.** VIX hits a "natural floor" — puts
become cheap, fund managers buy hedges because they are cheap, and VIX
drifts UP while ES stays strong. This produces a false pressure signal.

Source's response: stand aside. Explicitly called a low-probability trade.
Also noted that ES is in uncharted territory there, so there is little
resistance to lean on anyway.

Asymmetric: described as a problem at highs, not at lows.

---

## 8. What is mechanical vs what is discretionary

**Mechanical — directly computable:**

- Previous day high/low for ES, NQ, VIX
- Today's running high and low for each
- Breach of PDL (price < PDL)
- Recapture of PDL (price > PDL)
- VIX today's high vs VIX PDH
- Net % change vs previous close (the 1% rule)
- Distance from multi-year high (the failure-mode filter)

**Discretionary — needs a parameter before a bot can exist:**

| Phrase used | What a bot needs |
|---|---|
| "with momentum" / "with aggression" / "velocity in the tape" | A measurable definition, or drop it and test without |
| VIX "not quite at" PDH | A threshold. Is 99% of PDH weakness? 95%? |
| recapture "with some cushion" | A fixed distance. Example implies ~8 handles on ES ≈ 0.14% |
| target "more than 2:1" | A fixed R, or a rule for picking the level |
| "whichever is stronger" | Formalise as: smaller breach depth below PDL |

**Not stated at all:**

- No win rate is claimed for this setup anywhere in the source.
- No frequency is given — only "depends on the market; higher VIX, more often".
- No session window. Source trades it at any hour (the May 28 example
  triggered at ~03:00 and was missed because they were asleep).
- No maximum time in trade. Source explicitly refuses to put a timeline on
  trades.

---

## 9. Feasibility on this account (checked 2026-11-16)

| Leg | Symbol | Status |
|---|---|---|
| VIX | `VIX` (id 152, "US Volatility Index") | enabled, daily OHLCV + volume confirmed |
| ES | `US500.cash` | already traded by Daily Systems and Factory Bot |
| NQ | `US100.cash` | already traded by both bots |

Multi-symbol loading, previous-day levels and a once-a-minute timer are all
already built and in production in `Cbots/Daily Systems/DailySystems.cs`.

**Two structural mismatches to decide deliberately, not inherit:**

1. **Broker VIX is not CBOE VIX.** A VIX CFD is priced off VIX futures. Levels
   will not match the source's charts. Self-consistent for a bot, but it means
   results cannot be checked against the source's screenshots.
2. **Daily bars roll at 21:00/22:00 UTC**, not the New York cash close.
   "Previous day high/low" therefore means something different from what the
   source is pointing at. Candidate fix: compute PDH/PDL from the NY cash
   session (09:30–16:00 ET) instead of the broker day.

---

## 10. Open questions for testing

- **Q1.** Does the VIX-weakness filter actually improve on a naive PDL
  reclaim? The honest null is that PDL-reclaim mean reversion works on its
  own and VIX adds nothing. Must be tested against that control, not against
  no-trade.
- **Q2.** Does NQ confluence add anything beyond ES alone? The May 7 example
  worked with condition 3 failing.
- **Q3.** What threshold defines VIX "relative weakness"?
- **Q4.** NY-session PDH/PDL vs broker-day PDH/PDL — which performs better?
- **Q5.** Does the all-time-high failure mode show up in the data, and is the
  stand-aside filter worth its cost in missed trades?
- **Q6.** How often does Setup A actually fire? If it is a handful of times a
  year, it is not a bot, it is an alert.

---

## Provenance

Transcript pasted into chat 2026-11-16 by Vanessa. The raw transcript has
NOT been committed — it was supplied as chat text, and transcribing it by
hand risks a corrupted source of truth. If the original file is placed in
Drive it should be committed verbatim to `VIX-Correlation/01-transcripts/`
and this document linked to it.
