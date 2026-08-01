# 01 — Reading the score

The score is a sum of components, each printed with the measurement behind it.
Present it as a table. A bare "72/100" is worse than useless because the user
cannot tell whether it came from 40 touches of hard history or from three
confluence bonuses stacked on nothing.

## The components

### Level history (base, 0–60)

The only component that is genuinely a measurement of *this level*. Derived from
the expectancy of touches matching the exact setup — same side (resistance for a
short, support for a long) and same day bias.

```
base = clamp((expectancy_r + 1) / 4 × 60, 0, 60) × sample_weight

sample_weight:  n≥15 → 1.00 | n 8–14 → 0.85 | n 4–7 → 0.65 | n<4 → 0.40
```

**Always say `n` out loud.** A 0.40 weight on `n=3` still produces a number, and
a number looks authoritative. It isn't.

If the level breaks more often than it holds in this setup, a −15 penalty fires
and the honest advice is break-and-retest rather than first-touch rejection.

### Edge robustness (+8 / 0 / −10)

Replays the same touches at seven stop widths from 0.6× to 3.0× the derived stop.
An edge that only exists at one stop width is a sampling artefact.

This matters more than it looks. On the worked XAUUSD example the derived stop
(p90 wick-through) happened to land on a locally unlucky value — expectancy
+1.49R — while neighbouring stops gave +2.04R and +1.61R. The level was fine; the
single stop estimate was noisy. Robustness catches that.

### Dealer gamma regime (+10 / −8 / 0)

Positive net GEX means dealers hedge *against* price — a pinning regime where
levels hold more and breakouts fail more, which favours fading. Negative means
they hedge *with* it — levels break more easily, so favour break-and-retest.

Zero means **unavailable**, which is always the case under `--as-of`. Say so.
A score with this component missing has a ceiling around 85 and is not
comparable to a live score.

### Volume node confluence (+8 HVN/POC, +3 LVN, 0 if far)

Distance from the level to the nearest node in the **real COMEX futures volume
profile** — actual traded contracts, converted to spot at each bar's own basis.
Within 8 points counts.

A level on an HVN has real business behind it and will grind. A level on an LVN
will run once it goes — useful for the target, less so for the hold.

### Options OI confluence (+7 / 0)

Nearest strike carrying top-quartile open interest, within a tolerance derived from
the measured mapping precision (2σ, ~15 points). Committed
size near the level means dealer hedging flow anchored there.

Remember this is GLD, translated by a measured ratio (~10.90, not 10). It is a
proxy, one step removed from gold itself — and the translation is **imprecise**.

The ratio has a measured stdev of ~0.02, which at GLD ~371 is **±7.6 spot points**,
against a strike spacing of only 10.9 points. So a single strike cannot be pinned
to a single spot price; adjacent strikes overlap within the error. The confluence
tolerance is set at 2σ from this measurement rather than a round number, and the
report prints the ± band. Say "there is committed size in this area", never "there
is a wall at exactly 4,055".

Contrast the futures side: the basis has stdev ~1.2 points, so volume-profile
levels are roughly 6× more precisely placed. When the two layers disagree about
where a level sits, trust the volume node.

### Gamma flip position (+5 / −3)

Which side of the flip price sits on. Below the flip favours shorts, above
favours longs. Only fires when gamma data exists.

### Session (+5 / 0 / −5)

How this level has performed in this session specifically, when there are ≥4
samples. Gold behaves very differently across Asia, London and US.

### Positioning, COT (+5 / −3 / 0)

Managed money long/short ratio above 6× is crowded. Crowded long is fuel for a
downside flush — helps a short, hurts a long. Weekly data; macro context only,
never entry timing.

## Talking about it

Lead with the verdict and the single strongest component, then the caveat that
most limits it. For example:

> **53/100 — CAUTION.** The level itself is the strongest evidence: 19 comparable
> touches, held 74%, expectancy +1.49R, and it's positive across all seven stop
> widths so the edge isn't a stop artefact. It sits 2.6 points off a real COMEX
> volume node. What's missing is the gamma layer — this is an as-of replay, so
> there's no options data, which caps the score. The US session has been the
> weak one at this level (−0.11R over 9 touches), which is what pulls it into
> CAUTION rather than TAKE.

What to avoid:

- Presenting the total without the breakdown.
- Describing the score as a probability. It is not calibrated to one.
- Treating a replayed score and a live score as comparable.
- Implying the tool can see order flow. It cannot.

## The trade block

Entry is at the level. Stop is the p90 wick-through on non-break visits **in the
matching setup bucket**, floored at the touch band and capped at 6× it. Targets
are mechanical 2R and 3R.

That stop is the answer to "just beyond the deepest wick", expressed as a
measurement. Quote the deepest-ever pierce alongside it so the user knows the
tail risk they are accepting.
