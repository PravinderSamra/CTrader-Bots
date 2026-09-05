import { describe, it, expect } from 'vitest'
import {
  buildLadderView, rankRungs, scaleOf, showsPriors, trendOf, windowLadder,
} from '../ladder'
import { describeFreshness, isUsCashOpen } from '../../../hooks/useGexLevels'
import type { GexSnapshot, LadderRung } from '../../../types/gex'

/** Real rungs from a live NQ_NDX 0DTE pull, spot 29573.47. */
const RUNGS: LadderRung[] = [
  { strike: 29590.82, gex_vol: 1725.33, gex_oi: 128.15, priors: [8314.45, 11575.78, 3085.76, 1491.63, 979.1] },
  { strike: 29580.82, gex_vol: 25991.64, gex_oi: -115.18, priors: [35334.44, 38589.77, 10156.27, 4773.81, 3491.86] },
  { strike: 29570.82, gex_vol: 28340.21, gex_oi: 221.05, priors: [39994.46, 41551.03, 16253.71, 8584.63, 4201.91] },
  { strike: 29560.82, gex_vol: 44756.13, gex_oi: -213.96, priors: [58037.95, 69144.36, 61685.52, 34781.53, 19588.62] },
  { strike: 29550.82, gex_vol: 30306.32, gex_oi: 307.7, priors: [24965.42, 24228.45, 65438.73, 41616.3, 22114.43] },
  { strike: 29530.82, gex_vol: 900, gex_oi: 1684.54, priors: [900, 900, 900, 900, 900] },
  { strike: 29630.82, gex_vol: -500, gex_oi: -2915.4, priors: [-500, -500, -500, -500, -500] },
]

const SNAP: GexSnapshot = {
  fetched_at: '', source_ts: 1788551999, source_time: '',
  ticker: 'NQ_NDX', scope: 'zero',
  spot: 29573.47, zero_gamma: 29573.47,
  major_pos_vol: 29560.82, major_neg_vol: 29610.82, sum_gex_vol: 172733,
  major_pos_oi: 29530.82, major_neg_oi: 29630.82, sum_gex_oi: 2032,
  min_dte: 0, sec_min_dte: 4, delta_risk_reversal: 0, max_priors: null,
  regime_vol: 1, regime_oi: 1, regimes_agree: true, walls_agree: false,
  spot_vs_zero_gamma: 0,
  ladder: RUNGS,
}

describe('trendOf', () => {
  it('reports the latest leg, not the whole session', () => {
    // The real trap, caught by rendering it. Strike 29,560.82 went
    // 19.6k (30m) -> 34.8k -> 61.7k -> 69.1k (5m) -> 58.0k (1m) -> 44.8k now.
    // Against its 30-minute base that is "building"; against the last scan it
    // is a wall coming off, which is what a trader looking at the biggest call
    // wall needs to know. An arrow saying "building" here reads exactly
    // backwards.
    expect(trendOf(44756.13, RUNGS[3].priors)).toBe('unwinding')
  })

  it('reads a wall larger than the last scan as building', () => {
    expect(trendOf(20000, [12000, 9000, 8000, 7000, 6000])).toBe('building')
  })

  it('reads a wall smaller than the last scan as unwinding', () => {
    expect(trendOf(5000, [9000, 9500, 9800, 10000, 20000])).toBe('unwinding')
  })

  it('falls back to the last available sample on a short priors series', () => {
    expect(trendOf(100, [500])).toBe('unwinding')
  })

  it('treats small moves as flat rather than flapping', () => {
    expect(trendOf(1000, [1010, 1020, 1030, 1040, 1050])).toBe('flat')
  })

  it('judges a put wall by magnitude, so growing more negative is building', () => {
    // A put wall deepening from -1,000 to -5,000 is the wall being built,
    // even though the signed value fell.
    expect(trendOf(-5000, [-2000, -1500, -1200, -1100, -1000])).toBe('building')
  })

  it('is flat with no priors, and survives an all-zero series', () => {
    expect(trendOf(100, [])).toBe('flat')
    expect(trendOf(0, [0, 0, 0, 0, 0])).toBe('flat')
  })
})

describe('windowLadder', () => {
  it('keeps the strikes nearest spot and orders them high to low', () => {
    const out = windowLadder(RUNGS, 29573.47, 2)
    expect(out).toHaveLength(4)
    expect(out.map(r => r.strike)).toEqual([...out.map(r => r.strike)].sort((a, b) => b - a))
    // The far strikes must be the ones dropped.
    expect(out.some(r => r.strike === 29630.82)).toBe(false)
  })
})

describe('rankRungs', () => {
  it('ranks positive and negative separately, largest first', () => {
    const rows = rankRungs(RUNGS, 'vol')
    const byRank = Object.fromEntries(
      rows.filter(r => r.rank).map(r => [r.rank, r.strike]),
    )
    expect(byRank.C1).toBe(29560.82)   // 44,756 — the largest positive
    expect(byRank.P1).toBe(29630.82)   // the only negative
    expect(rows.find(r => r.strike === 29630.82)?.rank).toBe('P1')
  })

  it('ranks the open-interest reading on its own values, not volume', () => {
    // On OI the biggest positive is 29,530.82 (1,684) — a different strike
    // from the volume answer. Ranking must follow the active reading.
    const rows = rankRungs(RUNGS, 'oi')
    expect(rows.find(r => r.rank === 'C1')?.strike).toBe(29530.82)
    expect(rows.find(r => r.rank === 'P1')?.strike).toBe(29630.82)
  })

  it('carries priors on volume but not on open interest', () => {
    // The priors series tracks volume in the API payload. Pairing it with OI
    // bars would plot one quantity's history against another's level.
    expect(rankRungs(RUNGS, 'vol').some(r => r.priors.length > 0)).toBe(true)
    expect(rankRungs(RUNGS, 'oi').every(r => r.priors.length === 0)).toBe(true)
  })

  it('leaves unranked rungs without a rank rather than inventing one', () => {
    const rows = rankRungs(RUNGS, 'vol', 2)
    expect(rows.filter(r => r.rank?.startsWith('C'))).toHaveLength(2)
  })
})

describe('buildLadderView', () => {
  it('returns rows high-to-low, scaled so no prior dot escapes the plot', () => {
    const { rows, scale } = buildLadderView(SNAP, 'vol', 20)
    expect(rows.length).toBe(RUNGS.length)
    expect(rows[0].strike).toBeGreaterThan(rows[rows.length - 1].strike)

    // The largest *current* bar is 44,756 at 29,560.82, but that strike sat at
    // 69,144 five minutes earlier. Scaling to the current value alone pushed
    // those dots outside the track and over the labels — caught by rendering
    // it. A wall being smaller now than it was is the normal case for an
    // unwinding wall, so the scale has to cover the priors too.
    expect(scale).toBe(69144.36)
    for (const r of rows) {
      expect(Math.abs(r.value)).toBeLessThanOrEqual(scale)
      for (const p of r.priors) expect(Math.abs(p)).toBeLessThanOrEqual(scale)
    }
  })

  it('ignores priors in the scale when they are not being plotted', () => {
    // The open-interest reading carries no priors, so letting the volume
    // series inflate its scale would flatten every OI bar for no reason.
    const { rows, scale } = buildLadderView(SNAP, 'oi', 20)
    expect(scale).toBe(2915.4)
    expect(scale).toBe(Math.max(...rows.map(r => Math.abs(r.value))))
  })

  it('copes with a snapshot recorded before ladders were stored', () => {
    // gex_latest documents written by the earlier recorder have no ladder.
    const { rows, scale } = buildLadderView({ ...SNAP, ladder: undefined }, 'vol')
    expect(rows).toEqual([])
    expect(scale).toBe(0)
  })

  it('scaleOf is 0 for an empty ladder, so no bar divides by zero', () => {
    expect(scaleOf([])).toBe(0)
  })
})

describe('describeFreshness', () => {
  const at = (iso: string) => new Date(iso)

  it('treats a recent reading as fresh', () => {
    expect(describeFreshness(SNAP.source_ts, at('2026-09-04T20:02:59Z')).stale).toBe(false)
  })

  it('flags anything past the polling interval as stale', () => {
    expect(describeFreshness(SNAP.source_ts, at('2026-09-04T20:20:00Z')).stale).toBe(true)
  })

  it('describes a weekend-long gap readably', () => {
    expect(describeFreshness(SNAP.source_ts, at('2026-09-07T12:00:00Z')).label).toBe('2d ago')
  })

  it('never reports a negative age from clock skew', () => {
    expect(describeFreshness(SNAP.source_ts, at('2026-09-04T19:00:00Z')).ageSeconds).toBe(0)
  })
})

describe('isUsCashOpen', () => {
  it('is closed at the weekend', () => {
    // 2026-09-05 is a Saturday; the recorder's cron is Mon-Fri for this reason.
    expect(isUsCashOpen(new Date('2026-09-05T15:00:00Z'))).toBe(false)
  })

  it('is open mid-session on a weekday, closed outside it', () => {
    expect(isUsCashOpen(new Date('2026-09-04T15:00:00Z'))).toBe(true)
    expect(isUsCashOpen(new Date('2026-09-04T09:00:00Z'))).toBe(false)
  })
})


describe('showsPriors', () => {
  const rung = (value: number, priors: number[], rank: string | null = null) =>
    ({ strike: 1, value, priors, rank, trend: 'flat' as const })

  it('always keeps dots on a ranked wall', () => {
    // Ranked walls are the ones being traded; their history is the point.
    expect(showsPriors(rung(50, [40, 30, 20, 10, 5], 'C3'), 100000)).toBe(true)
  })

  it('drops dots on rungs too small to be part of the story', () => {
    // 200 dots, most stacked on the axis at empty strikes, buries the walls
    // that are actually moving.
    expect(showsPriors(rung(10, [12, 9, 8, 7, 6]), 100000)).toBe(false)
  })

  it('keeps a rung whose priors were large even if it is small now', () => {
    // A wall that has been taken off is exactly what we want to see.
    expect(showsPriors(rung(100, [50000, 40000, 30000, 20000, 10000]), 100000)).toBe(true)
  })

  it('is false with no priors or no scale', () => {
    expect(showsPriors(rung(500, []), 1000)).toBe(false)
    expect(showsPriors(rung(500, [400]), 0)).toBe(false)
  })
})
