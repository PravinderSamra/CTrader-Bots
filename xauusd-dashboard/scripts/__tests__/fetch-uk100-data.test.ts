import { describe, it, expect } from 'vitest'
import { computeBias, firstCloseOutside, computeOrbIntel, isoWeekKey, tradingDayIsoWeekKey, type OrbIntelInput } from '../fetch-uk100-data'

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

// ── G1: ORB intelligence (UK100-ORB-INTEL-TLDR-DESIGN.md §2) ──
// Typed fixture builders via indexed access on the exported input type, since
// the block interfaces themselves are script-local (not exported).
const dOrb: OrbIntelInput['orbContext'] = {
  computedAt: '', mode: 'POST_ORB', cashOpenLondon: '08:00 BST',
  overnightHigh: null, overnightLow: null, priorDayHigh: null, priorDayLow: null, priorClose: null,
  prevWeekHigh: null, prevWeekLow: null, gapPts: null, gapPct: null, orbHigh: null, orbLow: null,
  orbBrokenDirection: null, eventWindows: [], adr14: null, adrUsedPct: null,
}
const dBias: OrbIntelInput['bias'] = { score: 0, label: 'NEUTRAL', conviction: 'LOW', drivers: [], eventSuppressed: false }
const dTape: OrbIntelInput['europeanTape'] = {
  eurostoxx50DayPct: null, dax40DayPct: null, eurUsdDayPct: null,
  ftseDaxCorr20d: null, ftseSx5eCorr20d: null, tapeAgreement: 'ALIGNED', preOpenLead: 'NONE',
}
const dUs: OrbIntelInput['usLinkage'] = { us500DayPct: null, nas100DayPct: null, vix: null, vixRegime: 'CALM', us10y: null, usdx: null }
const dFx: OrbIntelInput['fx'] = { gbpUsdDayPct: null, gbpUsd20dPercentile: null, sterlingEri: null, sterlingEriDayChange: null, ftseImpactFromGbp: 'NEUTRAL' }
const dRates: OrbIntelInput['ukRates'] = {
  bankRate: null, sonia: null, soniaMinusBankRate: null, gilt5y: null, gilt10y: null, gilt20y: null,
  gilt10yDayBp: null, gilt20yDayBp: null, slope5s20s: null, giltUst10ySpread: null, longEndStress: false, nextMpcDate: null, daysToMpc: null,
}
const dPos: OrbIntelInput['positioning'] = { gbpCotNetLong: null, gbpCotWoWChange: null, crowding: null, reportDate: null, ftseReadthrough: 'NEUTRAL' }

function mk(over: {
  orbContext?: Partial<OrbIntelInput['orbContext']>
  bias?: Partial<OrbIntelInput['bias']>
  europeanTape?: Partial<OrbIntelInput['europeanTape']>
  usLinkage?: Partial<OrbIntelInput['usLinkage']>
  fx?: Partial<OrbIntelInput['fx']>
  ukRates?: Partial<OrbIntelInput['ukRates']>
  positioning?: Partial<OrbIntelInput['positioning']>
  calendar?: OrbIntelInput['calendar']
  uk100Price?: number | null
  nowLondonHour?: number
  todaySession?: OrbIntelInput['todaySession']
} = {}): OrbIntelInput {
  return {
    orbContext: { ...dOrb, ...over.orbContext },
    bias: { ...dBias, ...over.bias },
    europeanTape: { ...dTape, ...over.europeanTape },
    usLinkage: { ...dUs, ...over.usLinkage },
    fx: { ...dFx, ...over.fx },
    ukRates: { ...dRates, ...over.ukRates },
    positioning: { ...dPos, ...over.positioning },
    calendar: over.calendar ?? [],
    uk100Price: over.uk100Price ?? null,
    nowLondonHour: over.nowLondonHour ?? 10,
    todaySession: over.todaySession ?? null,
  }
}

describe('computeOrbIntel — R1 fakeout/reclaim (2026-07-15 worked example)', () => {
  it('broke DOWN but price reclaimed above the ORB high → FADE_FAVOURED + STRONG FAVOURS_LONG', () => {
    const intel = computeOrbIntel(mk({
      orbContext: { mode: 'POST_ORB', orbBrokenDirection: 'DOWN', orbHigh: 10471.3, orbLow: 10449.0, adr14: 130.9, adrUsedPct: 68 },
      bias: { score: 1, label: 'NEUTRAL' },
      uk100Price: 10524.75,
    }))
    expect(intel.stance).toBe('FADE_FAVOURED')
    const r1 = intel.signals[0]
    expect(r1.severity).toBe('STRONG')
    expect(r1.direction).toBe('FAVOURS_LONG')
    expect(r1.source).toBe('STRUCTURE')
    expect(intel.stanceLine).toMatch(/Fade day/)
    expect(intel.aiStanceLine).toBeNull()
    expect(intel.baseRateNote).toBeNull()
  })

  it('mirrored: broke UP but price reclaimed below the ORB low → FADE_FAVOURED + STRONG FAVOURS_SHORT', () => {
    const intel = computeOrbIntel(mk({
      orbContext: { mode: 'POST_ORB', orbBrokenDirection: 'UP', orbHigh: 100, orbLow: 90 },
      uk100Price: 85,
    }))
    expect(intel.stance).toBe('FADE_FAVOURED')
    expect(intel.signals[0].direction).toBe('FAVOURS_SHORT')
  })
})

describe('computeOrbIntel — R2/R3 bias-vs-break', () => {
  it('R2: break UP against a BEARISH bias → CAUTION BREAKOUT_SUSPECT', () => {
    const intel = computeOrbIntel(mk({
      orbContext: { mode: 'POST_ORB', orbBrokenDirection: 'UP', orbHigh: 100, orbLow: 90 },
      bias: { score: -4, label: 'BEARISH' },
      uk100Price: 101, // above orbHigh but broke UP → R1 does NOT fire (needs DOWN+reclaim)
    }))
    const s = intel.signals.find(x => x.source === 'STRUCTURE')!
    expect(s.severity).toBe('CAUTION')
    expect(s.direction).toBe('BREAKOUT_SUSPECT')
  })

  it('R3: break DOWN aligned with a BEARISH bias → INFO FAVOURS_SHORT', () => {
    const intel = computeOrbIntel(mk({
      orbContext: { mode: 'POST_ORB', orbBrokenDirection: 'DOWN', orbHigh: 100, orbLow: 90 },
      bias: { score: -5, label: 'BEARISH' },
      uk100Price: 88,
    }))
    const s = intel.signals.find(x => x.source === 'STRUCTURE')!
    expect(s.severity).toBe('INFO')
    expect(s.direction).toBe('FAVOURS_SHORT')
  })
})

describe('computeOrbIntel — R4 range budget boundaries', () => {
  it('69% used → no RANGE budget signal', () => {
    const intel = computeOrbIntel(mk({ orbContext: { adrUsedPct: 69, adr14: 130 } }))
    expect(intel.signals.find(s => s.source === 'RANGE')).toBeUndefined()
  })
  it('70% used → CAUTION', () => {
    const intel = computeOrbIntel(mk({ orbContext: { adrUsedPct: 70, adr14: 130 } }))
    const s = intel.signals.find(x => x.source === 'RANGE')!
    expect(s.severity).toBe('CAUTION')
  })
  it('90% used → STRONG', () => {
    const intel = computeOrbIntel(mk({ orbContext: { adrUsedPct: 90, adr14: 130 } }))
    const s = intel.signals.find(x => x.source === 'RANGE')!
    expect(s.severity).toBe('STRONG')
  })
})

describe('computeOrbIntel — R5 gap against bias (opening window)', () => {
  it('gap +0.5% against a bearish bias, London hour 8 → CAUTION GAP BREAKOUT_SUSPECT', () => {
    const intel = computeOrbIntel(mk({
      orbContext: { mode: 'ORB_FORMING', gapPct: 0.5, priorClose: 10478 },
      bias: { score: -4, label: 'BEARISH' },
      nowLondonHour: 8,
    }))
    const s = intel.signals.find(x => x.source === 'GAP')!
    expect(s.severity).toBe('CAUTION')
    expect(s.direction).toBe('BREAKOUT_SUSPECT')
  })
  it('same gap but London hour 10 (past opening window) → no GAP signal', () => {
    const intel = computeOrbIntel(mk({
      orbContext: { gapPct: 0.5, priorClose: 10478 },
      bias: { score: -4 },
      nowLondonHour: 10,
    }))
    expect(intel.signals.find(s => s.source === 'GAP')).toBeUndefined()
  })
})

describe('computeOrbIntel — stance aggregation', () => {
  it('two CAUTION BREAKOUT_SUSPECT signals with no clean bias → BREAKOUTS_SUSPECT', () => {
    const intel = computeOrbIntel(mk({
      orbContext: { adrUsedPct: 75, adr14: 130 },   // R4 CAUTION suspect
      europeanTape: { tapeAgreement: 'DIVERGING' }, // R8 CAUTION suspect
      bias: { score: 0 },
    }))
    expect(intel.stance).toBe('BREAKOUTS_SUSPECT')
  })

  it('clean bias +4 with no opposing STRONG → LONG_FAVOURED', () => {
    const intel = computeOrbIntel(mk({ bias: { score: 4, label: 'BULLISH' } }))
    expect(intel.stance).toBe('LONG_FAVOURED')
  })

  it('bias +4 but a STRONG VIX-stress suspect opposes → not LONG_FAVOURED', () => {
    const intel = computeOrbIntel(mk({ bias: { score: 4, label: 'BULLISH' }, usLinkage: { vixRegime: 'STRESS' } }))
    expect(intel.stance).not.toBe('LONG_FAVOURED')
  })

  it('all-null snapshot → MIXED, never throws, signals is an array', () => {
    const intel = computeOrbIntel(mk())
    expect(intel.stance).toBe('MIXED')
    expect(Array.isArray(intel.signals)).toBe(true)
    expect(intel.stanceLine).toMatch(/mixed signals/i)
  })
})

describe('computeOrbIntel — ranking cap keeps R1 and R12', () => {
  it('caps signals at 6 while retaining the R1 fakeout and the R12 AI echo', () => {
    const intel = computeOrbIntel(mk({
      // R1 fires (fade)
      orbContext: { mode: 'POST_ORB', orbBrokenDirection: 'DOWN', orbHigh: 100, orbLow: 90, adrUsedPct: 95, adr14: 130, priorDayHigh: 200, eventWindows: [{ event: 'X', timeLondon: '13:30 BST', impact: 'HIGH' }] },
      uk100Price: 150,                                        // reclaimed → R1; also R7 (draw beyond) fires
      europeanTape: { tapeAgreement: 'DIVERGING' },           // R8
      usLinkage: { vixRegime: 'STRESS' },                     // R9 strong
      fx: { gbpUsd20dPercentile: 90, gbpUsdDayPct: 0.6 },     // R10
      ukRates: { longEndStress: true, gilt20yDayBp: 12 },     // R11 strong
      positioning: { crowding: 'CROWDED_SHORT' },             // R11 pos
      todaySession: { time: '15:26 BST', direction: 'SHORT', status: 'WAIT', probability: 61, orbDirection: 'BOTH_OK', draw: 10502 },
    }))
    expect(intel.signals.length).toBeLessThanOrEqual(6)
    expect(intel.signals.some(s => s.source === 'STRUCTURE' && s.severity === 'STRONG')).toBe(true) // R1 kept
    expect(intel.signals.some(s => s.source === 'AI')).toBe(true) // R12 kept
  })
})

describe('isoWeekKey', () => {
  it('assigns consecutive Mondays to consecutive weeks', () => {
    // 2026-07-06 and 2026-07-13 are Mondays in adjacent ISO weeks.
    const w1 = isoWeekKey(new Date(Date.UTC(2026, 6, 6)))
    const w2 = isoWeekKey(new Date(Date.UTC(2026, 6, 13)))
    expect(w1).not.toBe(w2)
    expect(w1).toMatch(/^\d{4}-W\d{2}$/)
  })
  it('groups a Mon–Fri span into one week key', () => {
    const mon = isoWeekKey(new Date(Date.UTC(2026, 6, 6)))
    const fri = isoWeekKey(new Date(Date.UTC(2026, 6, 10)))
    expect(mon).toBe(fri)
  })
})

// Post-G1 review fix: cTrader stamps UK100 D_1 bars at the session open —
// 21:00 UTC of the PRIOR calendar day (live-verified 2026-07-15). The raw
// stamp therefore ISO-buckets every Monday bar into the previous week;
// tradingDayIsoWeekKey compensates. Timestamps below are LITERAL live bars.
describe('tradingDayIsoWeekKey — session-open stamp compensation', () => {
  const wk28 = isoWeekKey(new Date(Date.UTC(2026, 6, 8))) // Wed 08 Jul, plain W28 reference

  it('Monday 06 Jul trading day (stamped Sun 05 Jul 21:00Z) buckets into ITS OWN week (W28)', () => {
    expect(tradingDayIsoWeekKey(1783285200000)).toBe(wk28)
    // …whereas the raw stamp would have mis-bucketed it into W27 — the bug this fixes.
    expect(isoWeekKey(new Date(1783285200000))).not.toBe(wk28)
  })

  it('mid-week bars keep their week (Tue 07 Jul trading day, stamped Mon 06 Jul 21:00Z)', () => {
    expect(tradingDayIsoWeekKey(1783371600000)).toBe(wk28)
  })

  it('the NEXT Monday (13 Jul, stamped Sun 12 Jul 21:00Z) does NOT leak into W28', () => {
    expect(tradingDayIsoWeekKey(1783890000000)).not.toBe(wk28)
  })

  it('is a no-op for a midnight-same-day stamping convention', () => {
    expect(tradingDayIsoWeekKey(Date.UTC(2026, 6, 6, 0, 0))).toBe(wk28)
  })
})
