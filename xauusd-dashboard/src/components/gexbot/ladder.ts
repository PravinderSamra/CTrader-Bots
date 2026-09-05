import type { GexSnapshot, LadderRung } from '../../types/gex'

export type GexReading = 'vol' | 'oi'

/** Which way a strike's gamma has moved over the priors window. */
export type Trend = 'building' | 'unwinding' | 'flat'

export interface PlottedRung {
  strike: number
  /** Signed gamma for the active reading. Positive plots right, negative left. */
  value: number
  /** Earlier samples of `value`, most recent first. */
  priors: number[]
  /** 'C1'..'C5' for the largest positive, 'P1'..'P5' for the largest negative. */
  rank: string | null
  trend: Trend
}

export const PRIOR_LABELS = ['1m', '5m', '10m', '15m', '30m']

/** How many strikes either side of spot the ladder shows by default.
 *  GexBot narrows to the meaningful range rather than plotting the whole
 *  book; far strikes are mostly empty and squash the scale for everything
 *  near price, which is the part being traded. */
export const DEFAULT_WINDOW = 20

function readingOf(r: LadderRung, reading: GexReading): number {
  return reading === 'vol' ? r.gex_vol : r.gex_oi
}

/** Which prior the arrow compares against: index 1, the 5-minute sample.
 *
 *  It matches the recorder's poll interval, so the arrow answers the question
 *  actually being asked — "this wall was that size last time I looked, what is
 *  it now?" — and it is less jumpy than the 1-minute sample.
 *
 *  Comparing against the *oldest* sample instead reads the whole session, and
 *  gets the important case backwards: on a live pull the largest call wall had
 *  gone 19.6k (30m) -> 69.1k (5m) -> 44.8k, which is a wall being taken off
 *  right now but "building" against its 30-minute base. The dots still show
 *  the full arc; the arrow reports the latest leg. */
export const TREND_REFERENCE = 1

/**
 * Is this wall being built or taken off, since the reference sample?
 *
 * The threshold is relative, not absolute, because gamma spans several orders
 * of magnitude across the ladder — a fixed cutoff would call every large
 * strike "changed" and every small one "flat".
 */
export function trendOf(current: number, priors: number[], threshold = 0.1): Trend {
  if (!priors.length) return 'flat'
  const oldest = priors[Math.min(TREND_REFERENCE, priors.length - 1)]
  // Compare magnitudes: a put wall growing means its value gets more negative,
  // which is still the wall building.
  const from = Math.abs(oldest)
  const to = Math.abs(current)
  const base = Math.max(from, to)
  if (base === 0) return 'flat'
  const delta = (to - from) / base
  if (delta > threshold) return 'building'
  if (delta < -threshold) return 'unwinding'
  return 'flat'
}

/** Strikes nearest spot, ordered high to low like a chart's price axis. */
export function windowLadder(
  ladder: LadderRung[],
  spot: number,
  window = DEFAULT_WINDOW,
): LadderRung[] {
  return [...ladder]
    .sort((a, b) => Math.abs(a.strike - spot) - Math.abs(b.strike - spot))
    .slice(0, window * 2)
    .sort((a, b) => b.strike - a.strike)
}

/**
 * Rank the walls by size and attach each strike's trend.
 *
 * Ranking is over the rungs actually shown, so a rank always refers to
 * something visible. Positive and negative are ranked separately — they are
 * different walls doing different jobs, not two ends of one list.
 */
export function rankRungs(
  rows: LadderRung[],
  reading: GexReading,
  topN = 5,
): PlottedRung[] {
  const valued = rows.map(r => ({
    strike: r.strike,
    value: readingOf(r, reading),
    priors: reading === 'vol' ? r.priors : [],
    rank: null as string | null,
    trend: 'flat' as Trend,
  }))

  const rankFor = (
    subset: typeof valued,
    prefix: string,
    cmp: (a: number, b: number) => number,
  ) => {
    subset
      .sort((a, b) => cmp(a.value, b.value))
      .slice(0, topN)
      .forEach((row, i) => { row.rank = `${prefix}${i + 1}` })
  }

  rankFor(valued.filter(r => r.value > 0), 'C', (a, b) => b - a)
  rankFor(valued.filter(r => r.value < 0), 'P', (a, b) => a - b)

  for (const row of valued) row.trend = trendOf(row.value, row.priors)

  return valued.sort((a, b) => b.strike - a.strike)
}

/**
 * Largest absolute value in view — the scale every mark is drawn against.
 *
 * Priors count towards it when they are being plotted. A strike's gamma
 * 30 minutes ago is frequently larger than it is now (that is precisely what
 * an unwinding wall looks like), and scaling to the current value alone
 * pushes those dots outside the plot.
 */
export function scaleOf(rows: PlottedRung[], includePriors = true): number {
  return rows.reduce((m, r) => {
    const priorMax = includePriors
      ? r.priors.reduce((n, p) => Math.max(n, Math.abs(p)), 0)
      : 0
    return Math.max(m, Math.abs(r.value), priorMax)
  }, 0)
}

/**
 * Is this rung worth drawing prior dots on?
 *
 * Five dots on every rung is 200 marks, most of them stacked on the axis at
 * strikes carrying no gamma — it buries the handful of walls that are
 * actually moving. Dots are kept for rungs big enough to be part of the
 * story.
 */
export function showsPriors(rung: PlottedRung, scale: number, floor = 0.04): boolean {
  if (!rung.priors.length || scale === 0) return false
  if (rung.rank) return true
  const biggest = Math.max(
    Math.abs(rung.value),
    ...rung.priors.map(p => Math.abs(p)),
  )
  return biggest / scale >= floor
}

/**
 * Everything the ladder needs, derived from a snapshot.
 *
 * `priors` are only carried on the volume reading. They track the volume
 * series in the API payload, so pairing them with open-interest bars would
 * plot one quantity's history against another's level — the kind of quiet
 * mismatch that is very hard to spot once it is on screen.
 */
export function buildLadderView(
  snap: GexSnapshot,
  reading: GexReading,
  window = DEFAULT_WINDOW,
) {
  const rows = rankRungs(windowLadder(snap.ladder ?? [], snap.spot, window), reading)
  return { rows, scale: scaleOf(rows, reading === 'vol') }
}
