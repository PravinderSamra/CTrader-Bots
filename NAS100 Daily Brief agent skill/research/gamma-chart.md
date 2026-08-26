# The per-strike gamma chart

**Status: shipped.** `scripts/gex_chart.py`, run with `/nas100-brief chart`.

## What it draws

One horizontal bar per strike bin, net gamma (calls minus puts), positive one
way and negative the other, with call resistance, put support, the gamma flip
and spot marked across it. Contract counts sit beside every value.

Built for one specific purpose the trader named: **enter at the max call or put
wall, target the next one.** That is why the chart carries something the
commercial dashboards do not — **rank badges**. C1/C2/C3 mark the three heaviest
POSITIVE strikes (brakes), P1/P2/P3 the three heaviest NEGATIVE (accelerants).
"The next wall" should be readable off the image without arithmetic.

## Why SVG and not matplotlib

The container is ephemeral and matplotlib is not installed in a fresh one. A
chart built on it is a chart that silently stops working on some future
morning — the same silent-failure shape as D1 and D3 in `HYPOTHESES.md`. SVG is
pure standard library, and being vector it is the honest answer to "make sure
every level and label is legible": it stays sharp at any zoom on a phone.

## Layout: fixed lanes

The first version let the legend, the marker labels and the bar values each find
their own x. They collided in three places at once — the legend overlapped
itself, `CALL RESISTANCE` sat on top of `+1.05bn`, and the footer ran off the
canvas.

Everything now has a reserved lane: marker label, rank badge, strike, plot,
value. Nothing is positioned relative to anything it could run into, and the
legend is a fixed 3×2 grid rather than a measured flow.

## A bug worth recording: ranks that contradicted their own bars

The first ranking took the top strikes by |net GEX| on each side of spot. On a
call-dominated chain like NDX that stamped **P1 on a strongly POSITIVE bar** —
the badge said accelerant, the bar said brake, on the same row.

Ranks are now assigned **within sign**: C from positives, P from negatives.
Same failure mode as the secondary-walls put labels (D2) — a label derived from
*position relative to spot* when the meaning comes from *the sign of dealer
gamma*.

## Read it correctly

- Bars are **net** gamma per strike — a tall green bar is a strike where dealers
  are long gamma and will damp movement. That is a brake, and a magnet.
- Red bars are strikes where dealers are short gamma and **amplify**. Price
  tends to accelerate through, not stall.
- **On NDX the put side is frequently thin or absent.** The index carries far
  less protective put open interest than SPX, so the book below spot can be net
  positive all the way down. When there is no negative strike below spot the
  chart says so rather than promoting the least-positive one and calling it
  support — which is what a naive `min()` would have done.
- Open interest is the previous close. See the OI staleness section in
  `references/02-gamma-levels-playbook.md`, and `live-walls/` for the attempt to
  do better.

## Not included, deliberately

The reference dashboard overlays a DEX profile and a cumulative GEX curve. Both
are computable from data already fetched. Neither is on the chart because
neither is a **level**, and the chart exists to be marked up — the same test
that rejected vanna and charm (R2).

---

# The retrospective chart

`scripts/gex_retro.py` — takes the levels a **past** scan published and draws
what price actually did to each one.

```
python3 gex_retro.py                             # yesterday's last scan vs today
python3 gex_retro.py --from 2026-08-26 --scan 2211 --to 2026-08-26
python3 gex_retro.py --gamma-only                # options levels only
```

## Why it is not just the written review

The review already grades levels and prints a verdict per line. What it cannot
show is **when** in the session a level was touched, and what the path looked
like around it. A level that "held" at 14:00 on the first approach is a
different object from one that "held" at 19:00 after price had already sliced
through it twice, and the text grades both identically.

Grading is `review_day.grade_level`, unchanged and imported rather than
reimplemented — so the picture and the written review can never drift apart.
That was deliberate: two graders would eventually disagree and there would be no
way to tell which was right.

## Reading it

- **HELD** (solid green) — price stalled there with no clean break either way.
- **BROKE** (dashed red) — it went through.
- **CHOP** (dashed amber) — traded both sides. In a pinning regime this is the
  correct behaviour at a level, not a failure, and the counts should be read
  with that in mind.
- **not reached** (faint grey) — never tested. Not evidence either way.
- Dots mark **first touch**, which is the touch that matters for an entry.

## The source scan matters, and choosing it is a judgement

`--from` defaults to the last scan of the previous trading day. That is the
honest forward test — those levels were published before the session existed.

But the trading day rolls at 21:00 UTC, so an evening scan is filed under the
*next* day's folder. The richest forward test is usually
`--from <target day> --scan <evening time>`: levels published before the session
opened, graded across the whole session. The chart titles itself by the scan's
own date rather than the folder it sits in, because the first version said
"2026-08-26 levels vs 2026-08-26 price" for a scan taken on the 25th.

## First run, 2026-08-26

Levels published 25 Aug 22:11Z, graded across the whole of 26 Aug:

| | |
|---|---|
| Reached | 12 of 17 |
| Held | 2 |
| Broke | 4 |
| Chopped | **6** |
| Never reached | 5 |
| Held rate (of reached) | 16.7% |

**The single best level was the call wall at 29,343** — it HELD, and the day's
high was 29,353.8. Ten points. Published fifteen hours earlier.

**Six of the twelve reached levels chopped**, and they were all in one band:
29,093–29,144 (put wall, gamma flip, PWL, PD mid, London low, equal lows). That
is not six independent failures, it is one pinning zone that happens to contain
six named levels — which flatters the "chopped" count and is worth remembering
before reading anything into it. It is also the clearest visual argument yet for
H6's eventual breakdown by level *type*, and for splitting it by gamma regime.
