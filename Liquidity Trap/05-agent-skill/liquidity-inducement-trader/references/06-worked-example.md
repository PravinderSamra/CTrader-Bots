# 06 — Worked Example: One Full End-to-End Read

> **Illustrative example only.** The prices, timestamps and outcome below are a
> realistic *training scenario* adapted from the gold (XAUUSD) case documented
> in doc 03 §7 (rows 6–7) and doc 02 §E. It is not live advice, not a signal,
> and not a prediction — it exists to calibrate the flow of a run. Study it
> once; do not template-match its shapes (doc 01 §9).

Scenario: **XAUUSD (CFD), Tuesday, ~09:40 a.m. New York.** The user asks:
"mark up gold and give me a read."

---

## Step 1 — Frame the day (HTF → bias)

Pull 1D / 4H / 1H / 15m, then 5m/1m for execution.

- **Most recent large displacement:** two sessions ago a sharp sell-off swept
  an old daily low at **5,002.0** (something taken from the left — the
  directional validation for longs, doc 03 §1.1) and reversed hard. That
  sweep's extreme (wick to 4,995.4) has not been respected since → it is a
  **1D liquidity block**, not a pool.
- **What the move left behind:** overhead, a left-hand 4H high at **5,109.8**
  was respected twice afterwards (swing highs 5,104.6 and 5,106.1 — wicks
  terminating inside the zone, no close through; ~0.1% undershoot, within
  tolerance, doc 02 §B.1). That is a **confirmed equal-highs target pool**,
  boxed **5,095.2–5,109.8**.
- **Two-lines frame:** confirmed pool above = the equal-highs box; the ladder
  of intraday lows below is still forming. The swept daily-low side is
  exhausted → the draw points **up**.
- **Engineered liquidity:** yesterday afternoon price approached the box,
  printed a high at **5,082.4** that respected it and retraced — sellers are
  now positioned in front of the target, refreshing it (arming condition,
  doc 03 §1.3).
- **Day frame / time:** PDH 5,084.0 sits just above the engineered high; the
  06:00–10:00 H4 candle is running; 08:30 news passed >4 min ago; no bank
  holiday. Session window open.

**Bias (conditional):** long, medium-high confidence — draw is the equal highs
5,095.2–5,109.8; longs arm **only below** the intraday buildup low (gate 2/4),
ideally at/after the 10:00 H4 roll.

## Step 2 — Mark the liquidity map (the drawing payload)

Filled-in level spec per reference 02 §D:

```json
{
  "symbol": "XAUUSD",
  "as_of": "2026-01-27T09:40:00-05:00",
  "timeframes": { "bias": ["1D", "4H", "1H"], "execution": "1m" },

  "daily_bias": {
    "direction": "long",
    "draw": "5109.8",
    "rationale": "Old daily low 5002.0 swept and left behind (side exhausted); confirmed equal highs 5095.2-5109.8 respected twice overhead; engineered liquidity printed at 5082.4.",
    "confidence": "medium"
  },

  "levels": [
    {
      "id": "L1",
      "type": "pool_target",
      "side": "buy_side",
      "role": "draw",
      "zone": [5109.8, 5095.2],
      "label": "Equal highs 5095.2-5109.8 (buy-side target, 4H, respected)",
      "tf_origin": "4H",
      "status": "respected",
      "color_hint": "green",
      "note": "Left-hand high 5109.8 respected twice (5104.6, 5106.1). Full target."
    },
    {
      "id": "L2",
      "type": "liquidity_block",
      "side": "n/a",
      "role": "context",
      "zone": [5002.0, 4995.4],
      "label": "LB 5002.0-4995.4 (1D sweep extreme - no liquidity below)",
      "tf_origin": "1D",
      "status": "intact",
      "color_hint": "blue",
      "note": "The left-side sweep that validates longs. Too far to anchor an intraday stop."
    },
    {
      "id": "L3",
      "type": "engineered_liquidity",
      "side": "buy_side",
      "role": "arming",
      "price": 5082.4,
      "label": "Eng.LQ 5082.4 (arming, 15m)",
      "tf_origin": "15m",
      "status": "respected",
      "color_hint": "purple",
      "note": "Respected the target box and retraced. Becomes the internal partial on the way up."
    },
    {
      "id": "L4",
      "type": "inducement",
      "side": "n/a",
      "role": "expected_reaction",
      "price": 5068.3,
      "label": "Inducement 5068.3 (internal - do not trade, 5m)",
      "tf_origin": "5m",
      "status": "swept",
      "color_hint": "red",
      "note": "Minor high broken during the retrace; buyers induced (retail BOS). Their stops feed the pool below."
    },
    {
      "id": "L5",
      "type": "trap_zone",
      "side": "n/a",
      "role": "expected_reaction",
      "zone": [5071.0, 5066.2],
      "label": "Trap 5071.0-5066.2 (5m FVG - expected false reaction)",
      "tf_origin": "5m",
      "status": "intact",
      "color_hint": "red",
      "note": "Retail buy POI above the lows. Any bounce from here is pre-classified false."
    },
    {
      "id": "L6",
      "type": "pool_target",
      "side": "sell_side",
      "role": "arming",
      "price": 5057.2,
      "label": "Buildup low 5057.2 (sell-side pool - sweep arms the long, 1m)",
      "tf_origin": "1m",
      "status": "intact",
      "color_hint": "orange",
      "note": "Last unswept rung of the low-respecting-low ladder. Its sweep is the entry trigger."
    },
    {
      "id": "L7",
      "type": "liquidity_block",
      "side": "n/a",
      "role": "stop_anchor",
      "zone": [5051.2, 5047.3],
      "label": "LB 5051.2-5047.3 (stop anchor / entry zone, 1m)",
      "tf_origin": "1m",
      "status": "intact",
      "color_hint": "blue",
      "note": "09:19 stab-wick below the ladder; no liquidity beneath. Valid fill band runs L6 down through this box."
    },
    {
      "id": "L8",
      "type": "structure",
      "side": "n/a",
      "role": "context",
      "price": 5084.0,
      "label": "PDH 5084.0 (context, 1D)",
      "tf_origin": "1D",
      "status": "intact",
      "color_hint": "gray",
      "note": "Sits just above L3; secondary internal reference on the way to L1."
    }
  ],

  "setups": [
    {
      "id": "S1",
      "direction": "long",
      "alignment": "with_bias",
      "state": "armed",
      "trigger": "Stab of L6 (5057.2) into LB L7 at/after the 10:00 H4 roll - the 10:00 a.m. reversal script",
      "entry": { "kind": "market_on_confirmation", "zone": [5057.2, 5051.2] },
      "stop": { "price": 5046.2, "anchor": "below LB L7 wick (5047.3)", "buffer": "~$1 CFD spread room" },
      "targets": [
        { "price": 5082.4, "kind": "internal_partial", "level_id": "L3" },
        { "price": 5109.8, "kind": "external_full", "level_id": "L1" }
      ],
      "rr_estimate": 11.7,
      "invalidation": "1m close below 5046.2 (price accepting under the no-liquidity extreme)",
      "session_window": "NY, at/after 10:00 H4 roll",
      "note": "RR 11.7 at the 5051.2 stab fill; worst valid fill 5057.2 still ~4.8 to full target - floor intact. Partial at L3 pays ~6R at the stab fill, so paying yourself there is justified (>=~1:5)."
    }
  ],

  "verdict": "armed",
  "commentary": "The sell-off cleared the old daily low and left the equal highs intact overhead - that pool is the draw. Sellers engineered at 5082.4 give price its reason to go up. Buyers have been induced above 5068.3 and their stops now pool under the 5057.2 buildup low; the 09:19 stab left a clean 1m LB beneath it. Waiting for the 10:00 re-stab of 5057.2 into the LB: that trap completes the model. Direct 5m entry was rejected - stop under the 4H structure gives ~1:1.7, under the 1:3 floor - so this is the LTF confirmation entry (doc 03 s2.3)."
}
```

## Step 3 — Movement read

Draw above, just-swept side below, no intact internal pools between the LB and
the engineered high except the trap zone L5 (whose reactions are pre-classified
false). With-sequence long; time qualifier (10:00 H4 roll) available. If the
10:00 move instead runs *up* through 5,082.4 without sweeping 5,057.2 first —
that is a move "I was not supposed to be in": lockout holds, no chase.

## Step 4–5 — The advisory (what the user sees)

**Bias:** long (medium) — draw is the equal highs 5,095.2–5,109.8; the long
arms only on a stab of 5,057.2 into the 1m LB, ideally at/after 10:00.

**Legend:**
- Bias: long toward the 4H equal highs — the only logical untaken pool.
- Pools that matter: equal highs 5,095.2–5,109.8 (target), buildup low 5,057.2
  (sweep = trigger), engineered high 5,082.4 (partial).
- Stop reference: 1m LB 5,051.2–5,047.3; stop 5,046.2 with CFD spread room.
- Waiting for: the 10:00 stab below 5,057.2 with rejection back up.

**Setup:** as `S1` above — entry band 5,057.2 → 5,051.2, stop 5,046.2, partial
5,082.4 (~1:6 at the stab fill), full 5,109.8 (~1:11.7), invalidation 1m close
below 5,046.2. Management: risk-off at BE once 5,068.3 (first opposing
internal high) is consumed; partial at 5,082.4 since it pays ≥ ~1:5; runner to
the box (reference 04 §D; playbook's stricter "no BE unless partialed" noted).

**Discipline:** nothing is 100% — invalidation above is where this is wrong.
Analysis, not financial advice; no orders are executed by this skill.

*(In the source case the re-stab filled 5,051.19 at 10:00 and the target zone
printed 5,111.66 ~5 hours later — doc 03 §7 row 6. Outcomes vary; the process
is the deliverable.)*

---

## Counter-example — the no-trade / no-man's-land read

Same skill, different chart: **UK100, 12:10 p.m. NY.** Two lines are marked —
PDH **9,412.0** (buy-side, respected yesterday) above, equal lows **9,344.5**
(sell-side, 5m) below. Price is chopping at ~9,378: overlapping 5m highs/lows,
no displacement, both pools intact, no fresh sweep, no LB near price. It is
also NY lunch.

```json
{
  "symbol": "UK100",
  "as_of": "2026-01-27T12:10:00-05:00",
  "timeframes": { "bias": ["1D", "4H", "1H"], "execution": "5m" },
  "daily_bias": {
    "direction": "neutral",
    "draw": "n/a - two-sided",
    "rationale": "Price mid-range between two intact pools; neither side taken since the last displacement.",
    "confidence": "low"
  },
  "levels": [
    { "id": "L1", "type": "pool_target", "side": "buy_side", "role": "target",
      "price": 9412.0, "label": "PDH 9412.0 (buy-side target, 1D, respected)",
      "tf_origin": "1D", "status": "respected", "color_hint": "green" },
    { "id": "L2", "type": "pool_target", "side": "sell_side", "role": "target",
      "price": 9344.5, "label": "Equal lows 9344.5 (sell-side target, 5m)",
      "tf_origin": "5m", "status": "intact", "color_hint": "orange" }
  ],
  "setups": [],
  "verdict": "no_trade",
  "commentary": "No-man's-land: price is stranded mid-range at ~9378 between two intact pools, building liquidity both ways - everything in between is noise. No sweep, no LB near price, and it is NY lunch (dead volume). Standing down until one line is taken; the break defines the trap and the draw toward the other line."
}
```

**Verdict to the user:** NO TRADE — gates 2, 3, 5 and 6 all fail (no trap, no
LB, outside the preferred window, mid-range). Watching for a sweep of 9,412.0
or 9,344.5; react accordingly, per reference 03 §C.2. "When you don't see
liquidity, you are the liquidity — wait." Declining here is the system working,
not a missed trade.
