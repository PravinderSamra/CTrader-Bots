# 03 — Daily Bias, Session Timing & Movement Between Levels

How to derive the day's bias (the draw on liquidity), the session/time apparatus
that qualifies entries, and how to judge whether price reaches the draw. HTF is
for level identification and bias; **execution is 1m/5m intraday** (doc 02 §A).
Provenance: doc 02 §Step 2, doc 04 §5, doc 09 §3–§4, Playbook §Directional
Bias / §Session.

---

## A. Deriving the day's bias / draw on liquidity

### A.1 Higher timeframe first, or nothing

Start Weekly/Daily/4H/1H (plus 30m/15m for intraday context). "If you don't see
anything on the higher, anything relevant, then you shouldn't be going to the
lower time frame" (doc 09 §3.1). Find the most recent **large displacement**
and ask: *what liquidity did it clear, and what did it leave behind?*
(doc 02 §C Step 1). If one big one-directional move left no confirmed pools:
**do not trade this chart** — wait days if needed while liquidity rebuilds.

### A.2 The two-lines doctrine (the actual bias algorithm)

Mark the nearest **confirmed** pool above and the nearest confirmed pool below.
Everything between them is **noise** (doc 09 §3.2):

> "Mark out the lows, mark out the highs, **wait for one of them to get taken,
> and react accordingly**."

The bias is *conditional* until one line breaks; the break simultaneously
defines the trap just completed and the draw toward the other line.

### A.3 Prioritizing the draw (which pool is price being pulled toward)

Rules-of-thumb, in rough priority order (doc 02 §C Step 2; doc 09 §3.3):

1. **Nearest logical untaken pool.** "Your eyes should be back to these highs.
   That is the only logical liquidity point I can see in front of us right now."
2. **The side just swept is exhausted.** Once a move has cleared one side, the
   opposite untaken pool becomes the draw; reversals typically occur once
   external liquidity is taken. After the target itself is consumed, that
   direction is "off the cards" until new liquidity builds.
3. **Momentum agreement.** Heavy directional momentum with no drastic pullback
   keeps the draw pointing with the trend.
4. **A pool with "nothing beyond it" ranks up.** If a pool sits directly
   above/below with a huge gap and no internal liquidity behind it, it is high
   priority — the market lacks fuel to go the other way (EURUSD example,
   doc 02 §C.7).
5. **Untaken pools persist** across days/weeks as future targets — leave them
   marked (doc 01 §4; doc 09 §3.6).

### A.4 State the bias as a conditional plan, never a prediction

"If I was looking to take buys, it would only be below here" (doc 02 §C.8).
Correct form: *"If X sweeps, the long arms toward Y."* Wrong form: *"Price will
go up."* And bias holds **only while the target pool survives**: "as long as
the highs stay intact… buys are valid. Cuz that's the target" (doc 09 §3.3).
Confidence is graded, not binary — an against-sequence idea is "automatically
lower probability" (doc 09 §3.3).

---

## B. The session & time apparatus

Time is a first-class arming input, not decoration (doc 09 §3.5 note). It is an
overlay on the model — the model itself is session-agnostic (doc 05 §2.3) —
but for index futures and gold intraday Marco applies it strictly.

### B.1 Session window — New York focus

- **Index futures & gold intraday: New York session only**, anchored on the
  9:30 a.m. NY stock open, "sometimes around 8:00 a.m… but mainly it's after
  stock open" (doc 09 §1.4; doc 04 §5). Mark the 9:30 open line on every chart.
- **If the setup doesn't form in the window, no trade. Ignore price action
  outside your session** (Playbook §Session).
- Pre-open chop "is building liquidity for New York to deal with" — mark those
  internal equal highs/lows; Asia high/low box on the execution chart
  (doc 02 §C.9).
- **FX = the session-agnostic exception:** resting limit orders in the
  LB/imbalance, stop and target pre-set, can run overnight/while asleep
  (doc 04 §5; doc 09 §1.4).
- **News:** never enter before scheduled news; wait ~2–4 minutes after the
  release. Liquidity is often built the day *before* news (doc 03 §2.4).
- **Avoid NY lunch** (dead volume); ideally out of intraday positions before it
  (doc 04 §5). **Bank holidays: do not trade** (doc 09 §3.4).

### B.2 The H4 06:00–10:00 candle frame and the "10:00 a.m. reversal"

The flagship timing-plus-bias rule (doc 09 §3.5, from IET 2026-02-10):

1. Reference candle = the **06:00–10:00 a.m. (NY) H4 candle**.
2. At **10:00 a.m.** the next H4 candle opens — "a very, very powerful time,
   especially in the futures market."
3. Bullish case: **longs only below the previous H4 low, only around/after
   10:00.** "We are not longing until that low is taken out. Once the low is
   taken out, longs are active. It's a very strict rule." (Mirror for shorts.)
4. The sell-off into the sweep is pre-classified false — the **"10:00 a.m.
   reversal"** tendency.
5. Standard plumbing still required: LB present, stop covering the left-hand
   low.
6. Mechanical target option: **the previous H4 high** — or liquidity targets
   beyond it.

Related: **moves at stock open are presumed traps** — "if price action delivers
an entry in and around stock open, that move is typically going to be a trap
move; once the trap move is complete… then you can look for that reversal"
(doc 09 §4.2). The only sanctioned candle-closure entry is on a **perfect
time confluence** (multiple candle opens aligning to the minute, spike and
close back through the level) (doc 09 §3.5).

### B.3 PDH/PDL framing (the daily bias in candle form)

From doc 09 §3.4:

- **Unran PDL/PDH script:** if yesterday closed up leaving its low unran, and
  an older daily low was recently swept (→ acts as an LB), anticipate: open →
  spike below PDL → hold the LB → trade higher, **intraday target = PDH**
  (swing extension: the prior day's high beyond it). Mirror for shorts.
- **Day-boundary sweep pairs:** Monday spikes Friday's high → Friday's low
  becomes a "great, great" downside target.
- **After a wild outside day** (both extremes spiked): expect an **inside day**
  — small scalpy conditions, "usually on the brakes", often no trading.
- **Fractal:** the same spike-prior-candle-extreme script applies at any bar
  size (e.g., the previous-30m-low entry).

### B.4 4H-candle nature veto

A bullish 4H close followed by a candle that *respects* rather than runs the
prior low is "a bit of a red flag… I personally just like to sit out"
(doc 09 §7 item 8). A candle-behavior quality filter — use it to downgrade,
not to invent trades.

---

## C. Probability & movement between levels

### C.1 Will the draw be reached first?

Judge with these inputs (SKILL.md §3 step 3; doc 02 §C.7; doc 09 §3):

- **Which side was just swept** — the swept side is exhausted; the surviving
  pool is the magnet.
- **Momentum** — displacement with no drastic pullback favors continuation to
  the draw.
- **"Nothing beyond" pools** — a draw with no internal liquidity in its path
  travels faster; a path littered with intact internal pools means expect
  reactions at each (see C.3).
- **Counter-moves that have NOT taken the opposing arming level are pullbacks,
  pre-classified false** — "we did not take out the highs, so this bearish
  movement should just be a pullback" (doc 10 P8). A move is reversal-capable
  only after it *consumes* the arming level while a confirmed target survives
  opposite.
- **Time asymmetry:** liquidity builds slowly and is consumed fast (5 days of
  build swallowed in 18 hours; 4.5 days in 19 hours — doc 09 §3.6). A setup
  can take days to arm; marked levels stay valid meanwhile. Do not read slow
  build as failure of the bias.

### C.2 The no-man's-land stand-down doctrine

When price sits mid-range between the two marked pools with nothing confirmed
to react from (doc 09 §3.2; doc 10 P10; IET 2026-05-13 "Advanced Gold"):

> "I call this like **no man's land**… very choppy price action. This is where
> build-up of liquidity happens. I'm typically not trading in here. I want to
> see price either above or below. **I will wait days if I have to, or weeks.**"

- Everything between the two lines is noise; reactions in there are false and
  build fuel for both edges.
- The correct output is **no-trade / watching**, stating which line's break
  you are waiting for. "When you don't see liquidity, you are the liquidity."
- Exit condition: either edge breaks — then classify the break (inducing sweep
  vs trapping sweep, reference 01 §5) and re-run the read.

### C.3 Ping-pong: how price travels between pools

Price moves pool-to-pool, and one leg's target consumption can be the next
leg's arming sweep (doc 09 §4):

- **Each leg must independently satisfy the full model** — pool, trap, LB,
  target, time. The reversal is *not* taken merely because the prior leg's
  target was hit; the internal levels left behind on the way are its
  precondition ("if we didn't leave these highs, most likely I probably
  wouldn't be looking for this buy back up").
- **The against-sequence leg needs a time excuse** (stock open / 10:00 H4
  roll); the with-sequence leg doesn't (doc 09 §4.2).
- On the way to the external draw, expect **reactions at each intact internal
  pool and at old LBs dragged forward** — anticipate them so they neither
  shake you out nor lure you in (doc 09 §2.4; doc 10 P9). These internal pools
  are also the partial points (reference 04).
- **Both-sides days are rare** — "these days do not come often." The default
  is one-directional (doc 09 §4.2).
- Mid-trade, monitor the flip side "just in case I'm incorrect" — the lows
  being built under you are someone's next buy opportunity (doc 09 §4.2).

### C.4 Intraday reachability — soft scope (targets must be day-sized)

This is an **intraday** desk. The strategy is fractal, so the same structure
produces both intraday *and* multi-day swing targets — but a trade idea whose
target price cannot realistically print **today** is not an intraday setup. Soft
scope keeps the full map visible while making sure the *actionable target is
always day-sized.* It never deletes a valid pool; it only re-roles the ones out
of reach.

**Step 1 — estimate today's reach budget.** From the bars you already pulled:
- `adr` = the instrument's recent typical daily range (a rough average of the
  last ~10–20 daily candles' high–low; use round working figures — e.g. gold
  often ~$30–60, UK100 often ~60–110 pts, NAS100 futures several hundred).
- `used_today` = current session high − session low so far.
- `remaining_est` = `max(adr − used_today, small floor)` — rough headroom left.
  Widen it on a strong trend/high-momentum day, tighten it late in the session
  or on an inside day (doc 09 §3.4 "inside day → on the brakes").

**Step 2 — classify every `pool_target` by reach** from the *current price*:
- Distance to the pool `≲ remaining_est` (with a little tolerance) → `reach:
  "intraday"`. Eligible to be a trade target.
- Distance clearly `> remaining_est`, or it needs multiple sessions given
  momentum → `reach: "swing"`, `role: "swing_context"`. Still drawn (muted), so
  you see where the bigger draw is — but it is **not** today's target.

**Step 3 — pick the actionable target = the nearest `intraday` pool in the bias
direction.** Internal in-reach pools are partials; the nearest in-reach external
pool is the full target (reference 04 §C). Any `swing_context` pool beyond it is
context only.

**Step 4 — if the only draw in the bias direction is `swing`:** the honest read
is *right idea, wrong day.* Either (a) take the trade for a **partial-only**,
in-reach internal pool and be flat by session end, noting it in the setup
`note`; or (b) if there is no in-reach pool at all, `verdict: no_trade` — "the
setup is a swing, not an intraday trade; standing down for today." Do **not**
dangle a target price won't reach in the session.

This is a *soft* scope, not a gate: it never blocks a genuinely in-reach setup,
it just prevents swing-distance targets from being presented as intraday trades.
Reachability is a *probability filter on the target*, always stated with the
usual "nothing is 100%" caveat — a fast trend day can exceed ADR, and that's
fine to note as upside, never as the planned target.

### C.5 What to tell the user

For each run, the movement read should state, in one or two sentences: the
draw, the path (which internal pools/LBs lie between here and there), the
probability grade (with-sequence vs against-sequence, time qualifier present or
not), whether the target is **in today's reach** (soft scope, §C.4), and the
single event you are waiting for. If price is in no-man's-land, say exactly that
and name both lines.
