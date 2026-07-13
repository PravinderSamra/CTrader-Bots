import { describe, it, expect } from 'vitest'
import { computeBias, firstCloseOutside } from '../fetch-uk100-data'

// B1 (UK100-V2-PLAN.md §4): label thresholds for the four continuous
// drivers (GBP, US futures, Brent, Copper) moved from |comp| > 0.3 to
// |comp| >= 0.8. Score arithmetic (weightedSum) must be unchanged — only
// the human-facing `impact` label on the driver entry.
const baseInput = {
  gbpUsdDayPct: null, sterlingEriDayChange: null,
  us500DayPct: null, nas100DayPct: null,
  vix: null,
  brentDayPct: null, copperDayPct: null,
  gilt10yDayBp: null, gilt20yDayBp: null,
  cotCrowding: null,
  riskToneLabel: null,
  eventSuppressed: false,
  ger40DayPct: null, eustx50DayPct: null,
  nowLondonHour: 10,
}

describe('computeBias — B1 label thresholds', () => {
  it('all-null inputs still produce a NEUTRAL label (VIX defaults to CALM when vix is null, a pre-existing quirk unrelated to B1)', () => {
    const bias = computeBias(baseInput)
    expect(bias.score).toBe(1)
    expect(bias.label).toBe('NEUTRAL')
  })

  it('-0.09% GBP day% now labels NEUTRAL (regression pin, was BULLISH pre-B1)', () => {
    const bias = computeBias({ ...baseInput, gbpUsdDayPct: -0.09 })
    const gbp = bias.drivers.find(d => d.name === 'GBP')!
    expect(gbp.impact).toBe('NEUTRAL')
  })

  it('-0.6% GBP day% labels BULLISH (comfortably past the 0.8 floor)', () => {
    const bias = computeBias({ ...baseInput, gbpUsdDayPct: -0.6 })
    const gbp = bias.drivers.find(d => d.name === 'GBP')!
    expect(gbp.impact).toBe('BULLISH')
  })

  it('+0.29% US500 stays NEUTRAL (just under the ~0.3% floor)', () => {
    const bias = computeBias({ ...baseInput, us500DayPct: 0.29 })
    const us = bias.drivers.find(d => d.name === 'US futures')!
    expect(us.impact).toBe('NEUTRAL')
  })

  it('+0.31% US500 labels BULLISH (comp comfortably clears the ~0.3% floor)', () => {
    const bias = computeBias({ ...baseInput, us500DayPct: 0.31 })
    const us = bias.drivers.find(d => d.name === 'US futures')!
    expect(us.impact).toBe('BULLISH')
  })

  it('+0.59% Brent stays NEUTRAL (just under the ~0.6% floor)', () => {
    const bias = computeBias({ ...baseInput, brentDayPct: 0.59 })
    const brent = bias.drivers.find(d => d.name === 'Brent')!
    expect(brent.impact).toBe('NEUTRAL')
  })

  it('-0.62% Copper labels BEARISH (comp comfortably clears the -0.6% floor)', () => {
    const bias = computeBias({ ...baseInput, copperDayPct: -0.62 })
    const copper = bias.drivers.find(d => d.name === 'Copper (China proxy)')!
    expect(copper.impact).toBe('BEARISH')
  })

  it('score arithmetic is untouched by B1 — a mid-range GBP move produces the expected weighted score', () => {
    // GBP -0.6% -> comp = clampScore(0.6/0.5*2) = 2 (clamped), weight 3.0 ->
    // GBP contributes 6; VIX defaults to CALM (comp=1, weight 1.5) -> +1.5.
    // weightedSum = 7.5. totalWeight = 13 + europeanTapeWeight(10) = 15.5
    // (pre-14:30 London -> 2.5). divisor = 1.35 * 15.5/13 = 1.6096...
    // score = round(7.5 / 1.6096) = 5.
    const bias = computeBias({ ...baseInput, gbpUsdDayPct: -0.6 })
    expect(bias.score).toBe(5)
  })
})

// B3 (UK100-V2-PLAN.md §4): sticky orbBrokenDirection — first M5 close
// outside the ORB range, chronological, sticky.
describe('firstCloseOutside — B3 sticky ORB break', () => {
  it('no bars scanned yet returns NONE', () => {
    expect(firstCloseOutside([], 100, 90)).toBe('NONE')
  })

  it('no close ever leaves the range returns NONE', () => {
    expect(firstCloseOutside([92, 95, 98, 91], 100, 90)).toBe('NONE')
  })

  it('a break above reports UP', () => {
    expect(firstCloseOutside([95, 101, 103], 100, 90)).toBe('UP')
  })

  it('a break below reports DOWN', () => {
    expect(firstCloseOutside([95, 88, 85], 100, 90)).toBe('DOWN')
  })

  it('a break up that later closes back inside the range still reports UP (sticky, first match wins)', () => {
    expect(firstCloseOutside([95, 101, 97, 93], 100, 90)).toBe('UP')
  })

  it('a break down that later reclaims back inside still reports DOWN (sticky)', () => {
    expect(firstCloseOutside([95, 88, 93, 96], 100, 90)).toBe('DOWN')
  })

  it('scans chronologically — the FIRST breach wins even if a later opposite breach also occurs', () => {
    expect(firstCloseOutside([95, 101, 88], 100, 90)).toBe('UP')
  })
})
