import { describe, it, expect } from 'vitest'
import { buildLadder } from '../ladder'
import { describeFreshness, isUsCashOpen } from '../../../hooks/useGexLevels'
import type { GexSnapshot } from '../../../types/gex'

/** A live mid-session SPX reading, recorded 2026-09-04 20:00 UTC. */
const SPX: GexSnapshot = {
  fetched_at: '2026-09-04T21:47:25.797291+00:00',
  source_ts: 1788552000,
  source_time: '2026-09-04T20:00:00+00:00',
  ticker: 'SPX',
  scope: 'zero',
  spot: 7717.85,
  zero_gamma: 7712.5,
  major_pos_vol: 7720,
  major_neg_vol: 7710,
  sum_gex_vol: 311384.75,
  major_pos_oi: 7715,
  major_neg_oi: 7720,
  sum_gex_oi: -5668.521,
  min_dte: 0,
  sec_min_dte: 4,
  delta_risk_reversal: 0,
  max_priors: [{ strike: 7715, change: 823541.587 }],
  regime_vol: 1,
  regime_oi: -1,
  regimes_agree: false,
  walls_agree: false,
  spot_vs_zero_gamma: 1,
}

/** Pre-open, where volume-derived fields and zero gamma all read 0. */
const PRE_OPEN: GexSnapshot = {
  ...SPX,
  zero_gamma: 0,
  major_pos_vol: 0,
  major_neg_vol: 0,
  sum_gex_vol: 0,
  regime_vol: 0,
  regimes_agree: false,
}

describe('buildLadder', () => {
  it('orders levels high to low, like a chart price axis', () => {
    const prices = buildLadder(SPX).map(l => l.price)
    expect(prices).toEqual([...prices].sort((a, b) => b - a))
  })

  it('includes both readings of both walls, plus spot and zero gamma', () => {
    const ladder = buildLadder(SPX)
    expect(ladder).toHaveLength(6)

    const kinds = ladder.map(l => `${l.kind}:${l.reading ?? '-'}`)
    expect(kinds).toContain('call:vol')
    expect(kinds).toContain('call:oi')
    expect(kinds).toContain('put:vol')
    expect(kinds).toContain('put:oi')
    expect(kinds).toContain('spot:-')
    expect(kinds).toContain('zero:-')
  })

  it('never drops a reading, even when the two disagree on wall placement', () => {
    // On this snapshot the volume call wall (7720) sits above the OI one
    // (7715), and 7720 is also the OI *put* wall. Showing one reading only,
    // or de-duplicating by price, would hide exactly the conflict the project
    // is trying to measure.
    const ladder = buildLadder(SPX)
    const at7720 = ladder.filter(l => l.price === 7720)
    expect(at7720).toHaveLength(2)
    expect(at7720.map(l => l.kind).sort()).toEqual(['call', 'put'])
  })

  it('omits zero gamma when GexBot has not computed it', () => {
    // It reads 0 outside the session; a level at price 0 would be nonsense
    // sitting at the bottom of a ladder people trade off.
    const ladder = buildLadder(PRE_OPEN)
    expect(ladder.some(l => l.kind === 'zero')).toBe(false)
    expect(ladder.every(l => l.price > 0)).toBe(true)
  })

  it('omits volume walls pre-open but keeps the open-interest ones', () => {
    const ladder = buildLadder(PRE_OPEN)
    expect(ladder.some(l => l.reading === 'vol')).toBe(false)
    expect(ladder.filter(l => l.reading === 'oi')).toHaveLength(2)
    // Spot must survive -- it is what distances are measured from.
    expect(ladder.some(l => l.kind === 'spot')).toBe(true)
  })
})

describe('describeFreshness', () => {
  const at = (iso: string) => new Date(iso)

  it('treats a recent reading as fresh', () => {
    const now = at('2026-09-04T20:03:00Z')          // 3 min after source_ts
    const f = describeFreshness(SPX.source_ts, now)
    expect(f.stale).toBe(false)
    expect(f.label).toBe('3m ago')
  })

  it('flags anything past the polling interval as stale', () => {
    // The recorder polls every 5 minutes, so 20 minutes means the market is
    // shut or the workflow has stopped -- either way, not live.
    const now = at('2026-09-04T20:20:00Z')
    expect(describeFreshness(SPX.source_ts, now).stale).toBe(true)
  })

  it('describes multi-hour and multi-day gaps readably', () => {
    expect(describeFreshness(SPX.source_ts, at('2026-09-04T22:30:00Z')).label)
      .toBe('2h 30m ago')
    // A Monday morning read of Friday's close -- the weekend case.
    expect(describeFreshness(SPX.source_ts, at('2026-09-07T12:00:00Z')).label)
      .toBe('2d ago')
  })

  it('never reports a negative age from clock skew', () => {
    const now = at('2026-09-04T19:59:00Z')          // before source_ts
    expect(describeFreshness(SPX.source_ts, now).ageSeconds).toBe(0)
  })
})

describe('isUsCashOpen', () => {
  it('is closed at the weekend', () => {
    // 2026-09-05 is a Saturday; the recorder's cron is Mon-Fri for this reason.
    expect(isUsCashOpen(new Date('2026-09-05T15:00:00Z'))).toBe(false)
    expect(isUsCashOpen(new Date('2026-09-06T15:00:00Z'))).toBe(false)
  })

  it('is open mid-session on a weekday', () => {
    expect(isUsCashOpen(new Date('2026-09-04T15:00:00Z'))).toBe(true)
  })

  it('is closed outside cash hours on a weekday', () => {
    expect(isUsCashOpen(new Date('2026-09-04T09:00:00Z'))).toBe(false)
    expect(isUsCashOpen(new Date('2026-09-04T22:00:00Z'))).toBe(false)
  })
})
