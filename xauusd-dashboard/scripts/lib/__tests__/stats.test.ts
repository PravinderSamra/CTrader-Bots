import { describe, it, expect } from 'vitest'
import { pearson, dailyReturnsByDate, pairByDate } from '../stats'

describe('pearson', () => {
  it('returns null with fewer than 15 pairs', () => {
    const xs = Array.from({ length: 14 }, (_, i) => i)
    const ys = Array.from({ length: 14 }, (_, i) => i * 2)
    expect(pearson(xs, ys)).toBeNull()
  })

  it('returns 1 for a perfectly correlated series (known fixture)', () => {
    const xs = Array.from({ length: 20 }, (_, i) => i)
    const ys = Array.from({ length: 20 }, (_, i) => i * 3 + 5)
    expect(pearson(xs, ys)).toBe(1)
  })

  it('returns -1 for a perfectly inverse series (known fixture, D1-plan example)', () => {
    const xs = Array.from({ length: 20 }, (_, i) => i)
    const ys = Array.from({ length: 20 }, (_, i) => -i * 2 + 10)
    expect(pearson(xs, ys)).toBe(-1)
  })

  it('returns null when one series has zero variance', () => {
    const xs = Array.from({ length: 20 }, () => 5)
    const ys = Array.from({ length: 20 }, (_, i) => i)
    expect(pearson(xs, ys)).toBeNull()
  })

  it('truncates to the shorter series length from the tail', () => {
    const xs = Array.from({ length: 25 }, (_, i) => i)
    const ys = Array.from({ length: 20 }, (_, i) => i)
    // both truncated to the last 20 of xs vs all 20 of ys — still a clean +1
    expect(pearson(xs, ys)).toBe(1)
  })
})

describe('dailyReturnsByDate', () => {
  it('computes log returns keyed by the newer date', () => {
    const bars = [
      { timestamp: Date.parse('2026-07-01T16:00:00Z'), close: 100 },
      { timestamp: Date.parse('2026-07-02T16:00:00Z'), close: 110 },
      { timestamp: Date.parse('2026-07-03T16:00:00Z'), close: 99 },
    ]
    const rets = dailyReturnsByDate(bars)
    expect(rets.size).toBe(2)
    expect(rets.get('2026-07-02')).toBeCloseTo(Math.log(110 / 100), 6)
    expect(rets.get('2026-07-03')).toBeCloseTo(Math.log(99 / 110), 6)
    expect(rets.has('2026-07-01')).toBe(false) // first date has no prior to diff against
  })

  it('keeps only the last close when a date has multiple bars', () => {
    const bars = [
      { timestamp: Date.parse('2026-07-01T10:00:00Z'), close: 100 },
      { timestamp: Date.parse('2026-07-01T16:00:00Z'), close: 105 }, // same UTC date, later bar wins
      { timestamp: Date.parse('2026-07-02T16:00:00Z'), close: 110 },
    ]
    const rets = dailyReturnsByDate(bars)
    expect(rets.get('2026-07-02')).toBeCloseTo(Math.log(110 / 105), 6)
  })

  it('ignores bars with a missing/zero timestamp or non-positive close', () => {
    const bars = [
      { timestamp: 0, close: 100 },
      { timestamp: Date.parse('2026-07-01T16:00:00Z'), close: 0 },
      { timestamp: Date.parse('2026-07-02T16:00:00Z'), close: 110 },
    ]
    expect(dailyReturnsByDate(bars).size).toBe(0)
  })
})

describe('pairByDate', () => {
  it('pairs only shared dates, sorted ascending, most recent N', () => {
    const a = new Map([['2026-07-01', 0.01], ['2026-07-02', 0.02], ['2026-07-03', 0.03]])
    const b = new Map([['2026-07-02', 0.05], ['2026-07-03', 0.06], ['2026-07-04', 0.07]])
    const { xs, ys } = pairByDate(a, b, 20)
    expect(xs).toEqual([0.02, 0.03])
    expect(ys).toEqual([0.05, 0.06])
  })

  it('caps to the most recent maxPairs entries', () => {
    const a = new Map(Array.from({ length: 30 }, (_, i) => [`2026-01-${String(i + 1).padStart(2, '0')}`, i]))
    const b = new Map(a)
    const { xs } = pairByDate(a, b, 20)
    expect(xs).toHaveLength(20)
    expect(xs[xs.length - 1]).toBe(29) // most recent, not earliest
  })

  it('returns empty arrays when there is no date overlap', () => {
    const a = new Map([['2026-07-01', 0.01]])
    const b = new Map([['2026-08-01', 0.02]])
    const { xs, ys } = pairByDate(a, b, 20)
    expect(xs).toEqual([])
    expect(ys).toEqual([])
  })
})
