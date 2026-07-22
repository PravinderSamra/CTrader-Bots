# 02 — Level Marking, Labelling & Output Schema

How to identify, label, and **emit** the liquidity map so your TradingView
connection can draw it. This is the contract between the strategy brain and the
chart. (Rule provenance: research files 02, 03, 09, 10 and the official playbook.)

---

## A. The object taxonomy (what you are allowed to mark)

Mark an object **only when the market has confirmed it.** Six object types:

| `type` | What qualifies it | Drawn as | Primary `role` |
|---|---|---|---|
| `pool_target` | A high/low that was **respected and moved away**, or **equal highs/lows**, PDH/PDL, session high/low, an old *untaken* swing. Holds resting stops. | line (single tip) or box (spread tips) | `draw` / `target` |
| `liquidity_block` | The **swept, no-liquidity extreme** left by a sweep — no orders rest beyond it. | box spanning the sweep wick | `stop_anchor` / `entry_zone` |
| `engineered_liquidity` | The respected high/low that forms **against your target** as price first approaches it — the arming condition. | box or line | `arming` |
| `inducement` | An **internal** level whose sweep pulls in early participants; its far side becomes the next pool. **Mark, never trade.** | line or small box | `expected_reaction` |
| `trap_zone` | Retail POI / order block / FVG / imbalance where a **false reaction is expected**. Fuel map, not an entry. | box | `expected_reaction` |
| `structure` | Reference frame only: session boxes (Asia/London/APAC), the H4 06:00–10:00 candle range, VWAP, day open. | line/box | `context` |

**Explicit non-levels — never mark as a target:** a level already swept (it is
now an LB, not a pool); a high/low broken straight through with no respect; a
lone retail POI with no liquidity logic. (A swept pool *re-acquires* target
status only if price later respects it again and moves away — update its
`status` then.)

## B. Labelling convention

Every drawn object gets a label of the form:

```
<ROLE> <PRICE-or-RANGE> (<side>, <tf_origin>[, <status>])
```

Examples:
- `PDH 4042.40 (buy-side target, 1D, respected)`
- `Equal lows 10527.8 (sell-side target, 5m)`
- `LB 4002–3995 (stop anchor, 1H)`
- `Eng.LQ 4067.9 (arming, 15m)`
- `Inducement 4014.6 (internal — do not trade, 5m)`
- `Trap 4016–4021 (15m FVG — expected false reaction)`

Rules:
- **The label carries the meaning; colour does not.** Marco's live charts often
  use red for every role. Never infer intent from colour — always write the role
  in the label.
- Keep prices to the instrument's tick precision. For a zone, show `top–bottom`.
- Mark `status` on pools: `intact | respected | swept`. Swept pools stay on the
  chart (they explain the move) but are visually de-emphasised.

## C. Colour hints (secondary, configurable)

Provide a `color_hint` so the drawing is readable, but treat it as cosmetic. The
cleanest convention in the source material (Video 3 legend) — use as default:

| Role | `color_hint` |
|---|---|
| `pool_target` / `draw` | `green` (buy-side) / `orange` (sell-side) — or a single neutral if the connection prefers |
| `liquidity_block` | `blue` |
| `trap_zone` / `inducement` | `red` |
| `engineered_liquidity` | `purple` |
| `structure` (session/frame) | `gray` |

If the host draws with a fixed palette, keep the **labels** authoritative and
let colour fall where it may.

## D. The level-spec output schema (hand this to the drawing connection)

Emit one JSON object per analysis run. Your TradingView connection draws each
`levels[]` entry (a horizontal line at `price`, or a box across `zone`) with its
`label`, and renders each `setups[]` entry as the trade idea.

```jsonc
{
  "symbol": "XAUUSD",
  "as_of": "2026-07-20T14:22:00+01:00",   // include timezone
  "timeframes": { "bias": ["1D","4H","1H"], "execution": "5m" },

  "daily_bias": {
    "direction": "long" | "short" | "neutral",
    "draw": "4042.40",                     // the primary pool price is being pulled toward
    "rationale": "one sentence: which pool, why (nearest untaken / swept side exhausted / momentum)",
    "confidence": "high" | "medium" | "low"
  },

  "levels": [
    {
      "id": "L1",
      "type": "pool_target" | "liquidity_block" | "engineered_liquidity" | "inducement" | "trap_zone" | "structure",
      "side": "buy_side" | "sell_side" | "n/a",
      "role": "draw" | "target" | "stop_anchor" | "entry_zone" | "arming" | "expected_reaction" | "context",
      "price": 4042.40,                    // for a single-line level; omit if zone-only
      "zone": [4021.34, 4016.81],          // [top, bottom] for a box; omit if line-only
      "label": "PDH 4042.40 (buy-side target, 1D, respected)",
      "tf_origin": "1D",
      "status": "intact" | "respected" | "swept",
      "color_hint": "green",
      "note": "optional short context"
    }
    // ... one per marked object
  ],

  "setups": [
    {
      "id": "S1",
      "direction": "long" | "short",
      "alignment": "with_bias" | "counter_bias",
      "state": "armed" | "watching" | "invalidated" | "triggered",
      "trigger": "sweep of L3 (equal highs 10567.9) then 5m rejection back below",
      "entry": { "kind": "market_on_confirmation" | "limit", "zone": [4017.0, 4015.0] },
      "stop":   { "price": 4021.0, "anchor": "above LB / swept high", "buffer": "CFD spread" },
      "targets": [
        { "price": 4003.81, "kind": "internal_partial", "level_id": "L5" },
        { "price": 3982.74, "kind": "external_full",    "level_id": "L7" }
      ],
      "rr_estimate": 3.1,
      "invalidation": "5m close back above 4021",
      "session_window": "NY open",
      "note": "counter-bias/short-term vs the HTF long draw"
    }
  ],

  "verdict": "armed" | "watching" | "no_trade",
  "commentary": "2–4 sentence desk read: the story, the movement between levels, and what you're waiting for."
}
```

### Field discipline
- `levels[]` is the **drawing payload** — complete and self-consistent (every
  `setups[]` reference by `level_id` must exist in `levels[]`).
- A level is either a **line** (`price`) or a **box** (`zone`), not both, unless
  the box also has a key line (then set `price` to that line and `zone` to the
  band).
- `verdict` must honour the §2 gates in SKILL.md: only `armed` if all gates pass;
  otherwise `watching` (setup forming) or `no_trade` (no valid setup / no-man's-
  land / outside session).
- If a pool the bias depends on is **off-screen** (e.g. HTF draw below the
  visible range), say so in `commentary` and set `confidence` accordingly — do
  not fabricate a level you cannot see.

## E. Minimal human legend (always accompany the JSON)

After the JSON, give the user a 3–6 line plain-English legend: the bias in one
line, the 2–3 pools that matter today, the LB/stop reference, and the one thing
you're waiting for. The JSON is for the chart; the legend is for the human.
