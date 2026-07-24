# 02 — Daily Bias & Trend (bull day or bear day)

Your explicit preference: **trade with the trend as primary.** So the first
decision every run is *"is today a bullish or bearish day, and how strongly?"*
The analyzer gives you a computed starting point; you refine it with context.

## Step 1 — Take the mechanical score

`daily_bias.score` (−100…+100) and `.label` combine four liquidity-consistent
drivers (see `.reasons`):
- **Daily structure** — higher highs/lows (bull) vs lower highs/lows (bear). The
  heaviest weight; this is the actual trend.
- **Price vs 20-day average** — which side of the mean price is on.
- **Position vs PDH/PDL / prior close** — above PDH = breakout strength; below
  PDL = breakdown; otherwise which side of yesterday's close.
- **Today's candle from the open** — green/red so far.

Read it as: **|score| ≥ 40 = strong trend day**, 25–39 = mild lean, < 25 =
NEUTRAL (no trend edge — with-trend and counter-trend collapse; treat both draws
as equal and let the *sweep* pick the side).

## Step 2 — Refine with liquidity logic (the model's own bias method)

The analyzer is deliberately simple; sharpen it with the research's daily-bias
doctrine (docs 09 §3, 10 P8) — these can upgrade/downgrade the label:

- **Two-lines frame.** The real draw is the *nearest logical untaken pool*. If
  one side was just swept (`recent_sweep`) and the opposite pool is intact, the
  intact pool is the magnet → bias leans that way regardless of a borderline
  score.
- **Swept side is exhausted.** After a big move clears one side, the opposite
  untaken pool becomes the draw. Don't fight a fresh reclaim.
- **PDH/PDL day-frame.** Unran PDL with an older low already swept below →
  anticipate: spike PDL → hold → run **up** toward PDH (intraday target = PDH).
  Mirror for shorts. Day-boundary pairs: today spikes yesterday's high →
  yesterday's low becomes a strong downside draw.
- **Momentum agreement.** Strong one-directional displacement with no deep
  pullback = trend intact; keep the draw with the trend.
- **Counter-moves that have NOT taken the opposite arming level are pullbacks** —
  pre-classified as noise, not reversals. A move is reversal-capable only after
  it *consumes* the opposing pool while a confirmed target survives the other
  side.

## Step 3 — Time/session context (index & gold intraday)

- The setup should form in the **New York session** (≈ stock open, with its
  run-in from London). The against-trend leg specifically often needs a **time
  excuse** — the ~10:00 a.m. NY reversal / the H4 06:00–10:00 candle roll. The
  with-trend leg does not.
- Avoid NY lunch (thin). Prefer being out of intraday risk before it.
- News just passed / bank holiday / inside-day-after-outside-day → downgrade or
  stand down.

## Step 4 — Set the trade plan direction

- **Primary = with the bias** (`label`). Your main idea trades this direction,
  targeting the in-reach draw on that side.
- **Secondary = counter-bias**, only if a clean counter-setup exists (opposite
  pool swept + reclaimed into an LB). Label it *counter-bias / short-term*,
  target the near pool only, expect less, be out fast (docs 03 §4.4, 09 §4).
- **NEUTRAL day** → no trend edge: wait for the first decisive sweep to define
  the trap and the draw, then trade that. Don't force a direction.

**State the bias as a conditional plan, not a prediction:** e.g. *"Bullish day
(score +45, higher highs/lows + above PDH); primary is a long on a sweep of the
session low back into its LB, targeting PDH."*
