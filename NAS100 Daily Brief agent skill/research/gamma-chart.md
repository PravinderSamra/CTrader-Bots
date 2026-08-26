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
