/**
 * Small statistics helpers extracted as pure functions for unit testing
 * (mirrors the calendar.ts/ctrader.ts extraction pattern). Built for the
 * European-tape correlation fields (UK100-SESSION-REVIEW-2026-07-13.md F8);
 * UK100-V2-PLAN.md's Phase D1 GBP↔FTSE correlation is specced to reuse the
 * same `pearson()` when that phase is built — do not duplicate it there.
 */

export interface DatedClose {
  timestamp: number // ms epoch
  close: number
}

/**
 * Buckets bars to their UTC calendar date (last close wins if a date has
 * more than one bar) and returns day-over-day log returns keyed by the
 * NEWER date of each consecutive pair. Date-keyed rather than positional so
 * two series with slightly different trading calendars (UK/DE/EU holidays
 * rarely align) can still be paired correctly by `pairByDate`.
 */
export function dailyReturnsByDate(bars: DatedClose[]): Map<string, number> {
  const byDate = new Map<string, number>()
  for (const b of bars) {
    if (!b.timestamp || !(b.close > 0)) continue
    const d = new Date(b.timestamp).toISOString().slice(0, 10)
    byDate.set(d, b.close)
  }
  const dates = [...byDate.keys()].sort()
  const out = new Map<string, number>()
  for (let i = 1; i < dates.length; i++) {
    const prev = byDate.get(dates[i - 1])!
    const cur = byDate.get(dates[i])!
    out.set(dates[i], Math.log(cur / prev))
  }
  return out
}

/**
 * Intersects two date→return maps on shared dates, sorts ascending, and
 * keeps the most recent `maxPairs` — ready to feed straight into pearson().
 */
export function pairByDate(a: Map<string, number>, b: Map<string, number>, maxPairs: number): { xs: number[]; ys: number[] } {
  const common = [...a.keys()].filter(d => b.has(d)).sort()
  const recent = common.slice(-maxPairs)
  return { xs: recent.map(d => a.get(d)!), ys: recent.map(d => b.get(d)!) }
}

/**
 * Pearson correlation coefficient of two equal-length (or truncated-to-equal,
 * from the tail) numeric series. Returns null when fewer than 15 pairs are
 * available (UK100-V2-PLAN.md D1's threshold — too few points for a
 * meaningful read) or when either series has zero variance.
 */
export function pearson(xs: number[], ys: number[]): number | null {
  const n = Math.min(xs.length, ys.length)
  if (n < 15) return null
  const x = xs.slice(-n)
  const y = ys.slice(-n)
  const mx = x.reduce((a, b) => a + b, 0) / n
  const my = y.reduce((a, b) => a + b, 0) / n
  let cov = 0, vx = 0, vy = 0
  for (let i = 0; i < n; i++) {
    const dx = x[i] - mx
    const dy = y[i] - my
    cov += dx * dy
    vx += dx * dx
    vy += dy * dy
  }
  if (vx === 0 || vy === 0) return null
  return Math.round((cov / Math.sqrt(vx * vy)) * 100) / 100
}
