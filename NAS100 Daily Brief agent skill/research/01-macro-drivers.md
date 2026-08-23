# 01 — What Actually Moves NAS100 Intraday

Scope: drivers that produce a **tradeable intraday move** on the NAS100 CFD
(minutes to hours), not long-horizon fundamentals. Ordered by how much they
matter to a 1-minute reversal trader.

---

## Tier 0 — the four things that decide the day

### 1. Rates expectations (the single biggest lever)
NAS100 is the longest-duration equity index in the world. Its constituents are
priced off cash flows years out, so the **discount rate dominates**. A 5bp move
in the US 10y (`^TNX`) during the NY session is routinely worth 80–150 NAS100
points, and it is *directional and immediate* — not a lagged effect.

- **Yields up → NAS100 down.** Inverse correlation is tightest during
  09:30–12:00 ET and around data prints.
- The **2y/5y** (`^FVX`) carries Fed-path expectations; the **10y** carries term
  premium and growth. A rise led by the 2y is a hawkish-repricing selloff (fast,
  sharp, mean-reverts less). A rise led by the 10y is a term-premium/supply
  selloff (grindier).
- **Decompose every nominal move — this is the part most traders skip.** A 10y
  move is either a *real-rate* move (`DFII10`) or a *breakeven/inflation-
  expectation* move (`T10YIE`), and they hit NAS100 differently:
  - **Real-rate-led rise → the most direct multiple compression there is.**
    The discount rate literally went up. Sell tech, immediately.
  - **Breakeven-led rise → an inflation scare.** It hits tech via the *Fed-path
    repricing that follows*, so the impulse is smaller and slower, and it is
    more likely to retrace if the next data print cools.
  - *Example 19→20 Aug 2026: 10y nominal +4bp, entirely breakeven (real +0bp).
    That is a much softer bearish signal than a +4bp real-rate move would be.*
- **Credit is the honest cross-check.** High-yield OAS (`BAMLH0A0HYM2`) widening
  while NAS100 rallies is the single most reliable bearish divergence available
  — credit is a better risk analyst than equity. Tight and stable HY spreads
  give a rally permission to continue.
- **Current regime (Aug 2026):** Fed funds 3.50–3.75%, June-2026 dot plot flipped
  from a projected cut to a **hike** — 9 of 18 members see tightening by
  year-end. 10y at ~4.74%. This is a *hawkish-risk* tape: upside inflation
  surprises are punished harder than downside surprises are rewarded.

### 2. The AI/semi complex (concentration risk)
The top ~8 names are roughly 50% of the index. NAS100 is, intraday, largely a
**leveraged bet on NVDA + the AI capex trade**.

- Watch `NVDA`, `AVGO`, `MSFT`, `AAPL`, `AMZN`, `META`, `GOOGL`, `TSLA`, plus
  `TSM` as the overnight tell.
- A single mega-cap gapping 3% moves the index 40–90 points before anything else
  happens.
- **Breadth divergence is a warning:** NAS100 up while NVDA/AVGO are down means
  the move is being carried by the tail — those rallies fail into the NY close
  far more often than they extend.
- **NVDA earnings is the highest-impact scheduled event in the calendar** — it
  outranks most CPI prints for NAS100 specifically. Next one: **26 Aug 2026,
  after-hours** (consensus $2.01 EPS). The day *before* is usually compressed
  (dealers pin), the day *after* is a gap-and-expand day where the fuel model
  and the gamma flip matter most.

### 3. Scheduled US macro data
Only a short list actually moves the index intraday. In descending order:

**All times below are US Eastern, because that is what they are actually
anchored to.** The UTC equivalent moves by an hour twice a year, and getting
this wrong is not cosmetic — it puts the stand-aside window in the wrong place.
`08:30 ET` = **12:30 UTC in EDT** (mid-Mar to early Nov) and **13:30 UTC in
EST**. The scripts resolve this from the feed's own timestamps and from
`zoneinfo`, so the brief always prints the correct UTC time for today.

| Event | Time (ET) | Why it matters | Reaction to a HOT print |
|---|---|---|---|
| **CPI** | 08:30 | Direct input to the Fed path | Bearish NAS100, yields up. Often a 150–350pt initial impulse then a full or partial retrace within 60–90 min |
| **FOMC decision + presser** | 14:00 / 14:30 | Rate path + dots + QT | Decision spike is noise; **the presser (14:30 ET) sets the real direction**. Frequent full reversal between the two |
| **NFP / jobs report** | 08:30 (1st Fri) | Growth vs. wage inflation | Ambiguous — strong jobs is bullish growth but hawkish rates. Reaction depends on regime; in a hawkish regime, strong jobs = bearish |
| **PCE (core)** | 08:30 | The Fed's preferred gauge | Same sign as CPI, usually smaller |
| **PPI** | 08:30 | Leads CPI | Smaller, but a big miss reprices the CPI expectation |
| **ISM Services / Manufacturing** | 10:00 | Growth pulse | Weak = growth scare (bearish) unless it flips the Fed dovish |
| **Jobless claims** | 08:30 Thu | Weekly labour tell | Small on its own; matters in clusters |
| **Retail sales** | 08:30 | Consumer | Moderate |
| **UoM sentiment + inflation expectations** | 10:00 | The 5–10y inflation-expectation subcomponent is the market mover, not the headline | Moderate–high on a surprise |
| **Treasury auctions (10y/30y)** | 13:00 | A tailing auction lifts yields fast | Bearish on a poor auction |
| **Fed speakers** | any | Reprices the path between meetings | Directional, size depends on the speaker's voting status |

**Rule for the brief:** a Tier-0 print inside the next 90 minutes overrides
every technical setup. Both NAS100 strategies require a clean sweep-and-reject;
a data print manufactures a *fake* sweep that then keeps going.

### 4. Dealer positioning / gamma (see `03-gex-oi-levels.md`)
This is *the* reason NAS100 behaves differently on two days with identical
macro. Positive-gamma days pin and mean-revert (great for strategy 1 at the
walls). Negative-gamma days trend and extend (strategy 1 gets run over;
strategy 2's continuation model is the right tool).

---

## Tier 1 — regime and risk-appetite context

| Input | Source | How to read it |
|---|---|---|
| **VXN** (NASDAQ-100 implied vol) | `^VXN` | The correct vol index for NAS100 — **not VIX**. VXN/VIX ratio ≫ 1.3 = tech-specific stress. Currently 21.98 vs VIX 15.13 (ratio 1.45 — elevated tech-specific risk pricing) |
| **VIX9D / VIX** | CBOE | > 1.00 = backwardation, near-term event stress, **expect range expansion** (widen targets, expect ADR to be exceeded). < 0.92 = contango/calm, **mean-reversion favoured** |
| **VVIX** | CBOE | > 100 = active tail-hedging; big put buying feeds negative gamma |
| **DXY** | `DX-Y.NYB` | Sharp dollar strength = risk-off / liquidity tightening = bearish NAS100. Weak dollar is a mild tailwind |
| **ES vs NQ** | `ES=F` vs `NQ=F` | NQ outperforming ES = genuine tech-led risk appetite (trend day more likely). NQ underperforming on an up day = rotation out of tech, rallies fade |
| **10y real yield** | FRED `DFII10` | The actual discount rate on tech cash flows. Rising = multiple compression, and it is more predictive than the nominal |
| **HY credit spread** | FRED `BAMLH0A0HYM2` | Credit's risk verdict. Widening into an equity rally = fade the rally |
| **Financial conditions** | FRED `NFCI` | Negative = looser than average. Conditions *lead* price, so a tightening week is an early warning |
| **Fed liquidity** | FRED `WALCL`, `RRPONTSYD` | Balance sheet shrinking with reverse repo drained = QT biting reserves; a slow, persistent headwind |
| **Overnight Globex range** | `NQ=F` 5m | Asia and London windows on the futures set the levels the CFD opens into. A wide Globex range that has already used most of the ADR means the NY session has little fuel left |

---

## Tier 2 — episodic, but can dominate a specific day

- **Tariff / trade-policy headlines.** In the current tape these are live: the
  US–Canada talks collapsing (21 Aug 2026) is exactly the sort of unscheduled
  headline that produces a 200pt impulse with no warning. Semis are the most
  tariff-sensitive part of the index.
- **Government funding / debt-ceiling / Treasury-issuance headlines.**
- **Individual mega-cap news** — regulatory action, product launches, guidance
  cuts, an analyst downgrade of NVDA.
- **Month-end / quarter-end rebalancing** (last 2 sessions) and **OPEX**
  (3rd Friday, and the quarterly triple-witch) — OPEX days pin hard into the
  large strikes and then the gamma unwinds on the Monday after, which is one of
  the most reliable range-expansion days in the calendar.
- **Index reconstitution** (NASDAQ-100 annual reconstitution, December).

---

## Session map for a UK-based NAS100 trader (all UTC)

Anchored to exchange local time. Only the Asia window is genuinely fixed in
UTC (Tokyo has no DST); London and NY both shift.

| Window | Local | UTC in summer (EDT/BST) | UTC in winter (EST/GMT) | Character |
|---|---|---|---|---|
| Globex re-open | 18:00 ET | 22:00 | 23:00 | Thin, gappy — note the gap vs. the roll |
| **Asia** | — | 23:00–07:00 | 23:00–07:00 | Builds the Asia H/L that London sweeps |
| **London** | 08:00–13:30 UK | 07:00–12:30 | 08:00–13:30 | First real liquidity; often sweeps Asia and sets a false direction |
| **Pre-NY / data** | 08:30 ET print | 12:00–12:30 | 13:00–13:30 | **Stand aside** if a Tier-0 print is due |
| **NY open drive** | 09:30–11:00 ET | 13:30–15:00 | 14:30–16:00 | Highest volume; the day's high or low forms here ~65% of the time |
| **NY midday lull** | 11:30–13:30 ET | 15:30–17:30 | 16:30–18:30 | Volume dries, chop; positive gamma pins hardest |
| **NY afternoon** | 13:30–16:00 ET | 17:30–20:00 | 18:30–21:00 | 0DTE gamma unwind and MOC imbalance |
| **Close** | 16:00–17:00 ET | 20:00–21:00 | 21:00–22:00 | MOC, position squaring — no new entries |

---

## What this means for the two NAS100 strategies

**Strategy 1 (sweep → 1m reversal → LH/HL → CISD):**
- Works best when **positive gamma** + **contango vol** + **no Tier-0 event** +
  fuel already partly spent. That combination is what makes a sweep *fail*.
- It is most dangerous into a data print or in **negative gamma** below the
  flip, because dealers then chase the sweep instead of fading it — the "failed
  break" you're waiting for never forms.

**Strategy 2 (reversal → CISD → HH/HL → fib OTE entry):**
- Works best when **negative gamma / below the flip**, **backwardated vol**, and
  **ROOM_TO_EXPAND** fuel. That's the trending environment where a retrace to
  OTE actually holds and the leg extends past the prior swing.
- In heavy positive gamma near a call wall, the "new HH" is often the pin high —
  the OTE entry fills and then goes nowhere. Halve the target or skip.

The brief must therefore state the **gamma regime and vol term structure first**,
because those two decide *which of your two strategies is the right tool today*.
