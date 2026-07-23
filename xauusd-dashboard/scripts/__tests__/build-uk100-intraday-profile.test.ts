import { describe, it, expect } from 'vitest'
import { computeProfile, computeExpansionState, type IntradayProfile } from '../build-uk100-intraday-profile'

const PROFILE: IntradayProfile = {
  generatedAt: '2026-07-23T00:00:00Z', instrument: 'UK100', daysSampled: 40, avgSessionRangePts: 110,
  byHourLondon: { '8': { cumRangePct: 48, cumVolPct: 14 }, '11': { cumRangePct: 74, cumVolPct: 46 },
    '15': { cumRangePct: 95, cumVolPct: 91 }, '16': { cumRangePct: 100, cumVolPct: 100 } },
}

// 08:00 BST = 07:00 UTC, 16:00 BST = 15:00 UTC (July → BST, UTC+1).
const t = (h: number, day = 20) => Date.UTC(2026, 6, day, h - 1, 0)

describe('computeProfile', () => {
  it('normalises each day to its own range/volume and forward-fills empty hours', () => {
    // One day, two bars. Day range = 120-80 = 40; day vol = 30+70 = 100.
    // 08:00 bar: cumRange 100-90=10 → 25%; cumVol 30 → 30%.
    // 16:00 bar: full range → 100%; full vol → 100%.
    const day = { date: '2026-07-20', bars: [
      { timestamp: t(8), high: 100, low: 90, volume: 30 },
      { timestamp: t(16), high: 120, low: 80, volume: 70 },
    ] }
    const p = computeProfile([day])
    expect(p.daysSampled).toBe(1)
    expect(p.byHourLondon['8']).toEqual({ cumRangePct: 25, cumVolPct: 30 })
    // 09:00–15:00 carry the 08:00 cumulative forward (no bar in those hours).
    expect(p.byHourLondon['12']).toEqual({ cumRangePct: 25, cumVolPct: 30 })
    expect(p.byHourLondon['16']).toEqual({ cumRangePct: 100, cumVolPct: 100 })
  })

  it('averages across days (a big day does not dominate — each is normalised)', () => {
    const day1 = { date: '2026-07-20', bars: [
      { timestamp: t(8, 20), high: 100, low: 90, volume: 30 },   // → 25% / 30%
      { timestamp: t(16, 20), high: 120, low: 80, volume: 70 },
    ] }
    const day2 = { date: '2026-07-21', bars: [
      { timestamp: t(8, 21), high: 145, low: 100, volume: 10 },  // range 45/100=45%, vol 10%
      { timestamp: t(16, 21), high: 200, low: 100, volume: 90 },
    ] }
    const p = computeProfile([day1, day2])
    expect(p.daysSampled).toBe(2)
    // hour 8 average: range (25+45)/2 = 35; vol (30+10)/2 = 20
    expect(p.byHourLondon['8']).toEqual({ cumRangePct: 35, cumVolPct: 20 })
    expect(p.byHourLondon['16']).toEqual({ cumRangePct: 100, cumVolPct: 100 })
  })

  it('skips degenerate days (zero range or zero volume)', () => {
    const flat = { date: '2026-07-20', bars: [
      { timestamp: t(8), high: 100, low: 100, volume: 0 },
      { timestamp: t(16), high: 100, low: 100, volume: 0 },
    ] }
    const p = computeProfile([flat])
    expect(p.daysSampled).toBe(0)
    expect(Object.keys(p.byHourLondon)).toHaveLength(0)
  })
})

describe('computeExpansionState', () => {
  it('EXPANSION when range is well ahead of the time-of-day pace', () => {
    const e = computeExpansionState(PROFILE, 11, 100) // 100/74 = 1.35
    expect(e.label).toBe('EXPANSION')
    expect(e.rangeVsTypical).toBe(1.35)
    expect(e.moveMostlyDone).toBe(false) // only 46% of volume typically done at 11:00
  })
  it('COMPRESSED when range lags the pace', () => {
    expect(computeExpansionState(PROFILE, 11, 40).label).toBe('COMPRESSED') // 0.54
  })
  it('NORMAL in between', () => {
    expect(computeExpansionState(PROFILE, 11, 60).label).toBe('NORMAL') // 0.81
  })
  it('moveMostlyDone once most of the day\'s volume has typically traded', () => {
    expect(computeExpansionState(PROFILE, 15, 50).moveMostlyDone).toBe(true) // 91% vol done
  })
  it('UNKNOWN pre-open and when no profile', () => {
    expect(computeExpansionState(PROFILE, 7, 20).label).toBe('UNKNOWN')
    expect(computeExpansionState(null, 11, 50).label).toBe('UNKNOWN')
  })
})
