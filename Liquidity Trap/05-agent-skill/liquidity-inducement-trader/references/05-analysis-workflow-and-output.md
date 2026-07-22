# 05 — Analysis Workflow & Advisory Output Format

The operational run-loop (SKILL.md §3 restated as a checklist) and the exact
format of what you return to the user each run. The level-spec JSON schema
lives in reference 02 §D — this file specifies how it is packaged, not the
schema itself.

---

## A. The run-loop checklist (execute in order, every run)

### Step 1 — Frame the day (HTF → bias) — reference 03 §A–B

- [ ] Pull HTF bars (Weekly/Daily/4H/1H + 30m/15m intraday context) through the
      TradingView connection.
- [ ] Find the most recent large displacement: what liquidity did it clear,
      what did it leave behind?
- [ ] Mark the two lines: nearest confirmed pool above and below.
- [ ] Note the day frame: PDH/PDL (and yesterday's shape — outside day →
      expect inside day), the H4 06:00–10:00 candle, session opens, scheduled
      news, bank holidays.
- [ ] Derive the **draw on liquidity** and state the bias as a conditional
      plan with a confidence grade. If nothing relevant on the HTF: stop —
      the verdict is no-trade for lack of liquidity.

### Step 2 — Mark the liquidity map — reference 02

- [ ] On the execution TF (1m/5m intraday; 1H/4H for FX swing), mark every
      qualifying object: target pools, LBs, trap zones, engineered liquidity,
      inducements, session/structure levels.
- [ ] Apply the taxonomy and non-level exclusions of reference 02 §A strictly
      (no swept level as a target; no lone retail POI).
- [ ] Build the `levels[]` array per the reference 02 §D schema — this is the
      drawing payload. Every level: correct `type`, `side`, `role`, `label`
      (label carries the meaning), `status`, `tf_origin`, `color_hint`.

### Step 3 — Read the movement between levels — reference 03 §C

- [ ] Which side was just swept? Momentum? Gaps/imbalances in the path?
      "Nothing beyond" pools?
- [ ] Probability the draw is reached first; with-sequence or against-sequence.
- [ ] **Intraday reachability (soft scope, reference 03 §C.4):** estimate
      today's reach budget (`daily_range`: ADR vs used); tag each target pool
      `reach: intraday | swing`; re-role out-of-reach pools as `swing_context`
      (drawn, muted, never the trade target). Actionable target = nearest
      in-reach pool. Only-draw-is-swing → partial-only or no-trade today.
- [ ] No-man's-land check: if price is stranded mid-range, the verdict is
      no-trade/watching — name both lines and the break you await.

### Step 4 — Find the setup (where + when) — reference 04

- [ ] Locate the induce → trap → enter sequence forming (or formed) inside the
      session window.
- [ ] Define the exact trigger, entry (kind + zone), stop (anchor + buffer),
      layered targets (internal partial / external full), RR to each,
      invalidation, alignment (with-bias / counter-bias).
- [ ] Run the six gates (SKILL.md §2) and the pre-trigger checklist
      (reference 04 §F). Any gate fails → the setup is `watching` at best,
      with the missing condition named.

### Step 5 — Decide and advise

- [ ] Verdict: `armed` (all gates pass), `watching` (setup forming; say what
      completes it), or `no_trade` (name the failed gate).
- [ ] Assemble the output per §B below. Never auto-execute anything.

---

## B. The advisory output format (return this every run)

Five parts, in this order:

### (i) One-line bias/draw

One sentence, conditional form, with confidence. Example:
`Bias: short (medium) — draw on liquidity is the equal lows at 4003.8; sells arm only above the 4042.4 PDH sweep.`

### (ii) The level-spec JSON (drawing payload)

The full JSON object per reference 02 §D — `symbol`, `as_of` (with timezone),
`timeframes`, `daily_bias`, `levels[]`, `setups[]`, `verdict`, `commentary` —
in a fenced `json` block. Field discipline per reference 02: every
`setups[].targets[].level_id` must exist in `levels[]`; a level is a line
(`price`) or a box (`zone`); off-screen pools are declared in `commentary`,
never fabricated.

### (iii) Human legend (3–6 lines)

Plain English, per reference 02 §E: the bias in one line, the 2–3 pools that
matter today, the LB/stop reference, and the one thing you are waiting for.
The JSON is for the chart; the legend is for the human.

### (iv) The setup(s) — or the explicit verdict

If `armed` (or `watching` with a defined trigger), for each setup:

```
S1 — SHORT (with-bias) — ARMED
Trigger: sweep of PDH 4042.4 then 5m rejection back below
Entry:   market on confirmation ~4040.5 (valid zone 4042.4 → 4046.0 LB far side)
Stop:    4047.0 (above LB 4046.0, + CFD spread buffer)
Targets: T1 4021.3 (internal partial, L5) · T2 4003.8 (external full, L7)
RR:      ~2.9 to T1 / ~5.6 to T2 (floor is ~1:3 to the analyzed target)
Invalidation: 5m close back above 4047
Session: NY open window; no entry before the 08:30 news +2–4 min
```

If no valid setup: state **no-trade** or **watching** with the reason in one
or two sentences — which gate failed, and what event would change the verdict.
A disciplined no-trade is a correct answer, not a failure.

### (v) The discipline block (always append)

Standing language, adapt wording but keep all three points:

> Nothing in this model is 100% — this is a probabilistic read, and the
> invalidation above is where it is wrong. This is analysis and a trade idea,
> **not financial advice**. I do not execute orders: marking the levels and
> proposing the setup is the deliverable; the decision and the click are yours.

---

## C. Compact fill-in template

```
BIAS: {long|short|neutral} ({confidence}) — draw {price/pool}; {conditional arming clause}.

```json
{ ...level-spec JSON per reference 02 §D... }
```

LEGEND:
- Bias: {one line}
- Pools that matter: {2–3, with prices and sides}
- Stop reference: {LB, zone}
- Waiting for: {the one arming/confirming event}

SETUP(S) / VERDICT:
{setup block(s) as in §B(iv), or}
NO TRADE — {failed gate + reason}. Watching for: {event}.

{discipline block}
```

## D. Run hygiene

- **Read the reference file for the step you are on** before acting on it
  (SKILL.md §3).
- If a timeframe or a pool the bias depends on is not visible, **say what you
  cannot see** and lower `confidence` — never guess (SKILL.md §6;
  reference 02 §D field discipline).
- Separate with-bias from counter-bias explicitly in every setup (SKILL.md §6).
- Keep prices at instrument tick precision; timestamps carry a timezone.
- On repeated runs for the same session, update `status` on existing levels
  (`intact → respected → swept`) rather than re-inventing the map — swept
  pools stay drawn, de-emphasised (reference 02 §B).
