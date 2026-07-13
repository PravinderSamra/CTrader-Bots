import { describe, it, expect } from 'vitest'
import {
  explainBias, explainFx, explainRates, explainUsLinkage,
  explainCommodities, explainEuropeanTape, explainPositioning, explainOrb, explainSectors, explainCalendar,
} from '../explainers'
import type { FxBlock, UkRatesBlock, OrbContext, BiasBlock, EuropeanTapeBlock } from '../../../types/uk100'

// The GBP sign-flip is the one rule the whole UK100 section is built on and
// the easiest to state backwards in prose — these tests pin the direction.
describe('explainFx — GBP sign-flip', () => {
  const base: FxBlock = {
    gbpUsdDayPct: 0, gbpUsd20dPercentile: null,
    sterlingEri: null, sterlingEriDayChange: null, ftseImpactFromGbp: 'NEUTRAL',
  }

  it('weak pound is described as HELPING the index', () => {
    const text = explainFx({ ...base, gbpUsdDayPct: -0.6, ftseImpactFromGbp: 'BULLISH' })
    expect(text).toMatch(/pound is down/i)
    expect(text).toMatch(/tailwind/i)
    expect(text).not.toMatch(/headwind for upward/i)
  })

  it('strong pound is described as a HEADWIND', () => {
    const text = explainFx({ ...base, gbpUsdDayPct: 0.7, ftseImpactFromGbp: 'BEARISH' })
    expect(text).toMatch(/pound is up/i)
    expect(text).toMatch(/headwind/i)
  })

  it('always states the counter-intuitive rule itself', () => {
    for (const impact of ['BULLISH', 'BEARISH', 'NEUTRAL'] as const) {
      expect(explainFx({ ...base, ftseImpactFromGbp: impact })).toMatch(/WEAKER pound usually HELPS/i)
    }
    expect(explainFx(null)).toMatch(/WEAKER pound usually HELPS/i)
  })
})

describe('explainRates', () => {
  const base: UkRatesBlock = {
    bankRate: 3.75, sonia: 3.73, soniaMinusBankRate: -0.02,
    gilt5y: 4.4, gilt10y: 5.0, gilt20y: 5.7, gilt10yDayBp: 0, gilt20yDayBp: 0,
    slope5s20s: 1.3, giltUst10ySpread: 0.5, longEndStress: false,
    nextMpcDate: '2026-07-30', daysToMpc: 20,
  }

  it('long-end stress reads as a caution flag, not a banks positive', () => {
    const text = explainRates({ ...base, gilt20yDayBp: 12, longEndStress: true })
    expect(text).toMatch(/caution/i)
    expect(text).not.toMatch(/mildly GOOD for bank/i)
  })

  it('moderate 10Y rise reads as mildly good for banks', () => {
    const text = explainRates({ ...base, gilt10yDayBp: 6 })
    expect(text).toMatch(/mildly GOOD for bank/i)
  })

  it('flags an imminent MPC decision', () => {
    const text = explainRates({ ...base, daysToMpc: 3 })
    expect(text).toMatch(/rate decision in 3 days/i)
  })
})

describe('explainOrb — mode awareness', () => {
  const base: OrbContext = {
    computedAt: '', mode: 'POST_ORB', cashOpenLondon: '08:00 BST',
    overnightHigh: 10498.5, overnightLow: 10438.8,
    priorDayHigh: 10514.2, priorDayLow: 10380.4, priorClose: 10457,
    gapPts: 34.6, gapPct: 0.33, orbHigh: 10494.7, orbLow: 10471.7,
    orbBrokenDirection: 'UP', eventWindows: [], adr14: 133.4, adrUsedPct: 49,
  }

  it('an upward break names the range LOW as the failure line', () => {
    const text = explainOrb(base)
    expect(text).toMatch(/broken ABOVE/i)
    expect(text).toMatch(/10471\.7/)
  })

  it('a downward break names the range HIGH as the failure line', () => {
    const text = explainOrb({ ...base, orbBrokenDirection: 'DOWN' })
    expect(text).toMatch(/broken BELOW/i)
    expect(text).toMatch(/10494\.7/)
  })

  it('high ADR usage warns the easy move may be gone', () => {
    const text = explainOrb({ ...base, adrUsedPct: 85 })
    expect(text).toMatch(/85% of a typical day/i)
  })

  it('pre-open says nothing to do until 08:00', () => {
    const text = explainOrb({ ...base, mode: 'PRE_OPEN', orbBrokenDirection: null })
    expect(text).toMatch(/until 08:00/i)
  })
})

describe('null-safety — every explainer returns usable text with no data', () => {
  it('never throws and always explains the concept', () => {
    expect(explainBias(null)).toBeTruthy()
    expect(explainFx(null)).toBeTruthy()
    expect(explainRates(null)).toBeTruthy()
    expect(explainUsLinkage(null)).toBeTruthy()
    expect(explainCommodities(null)).toBeTruthy()
    expect(explainEuropeanTape(null)).toBeTruthy()
    expect(explainPositioning(null)).toBeTruthy()
    expect(explainOrb(null)).toBeTruthy()
    expect(explainSectors([])).toBeTruthy()
    expect(explainCalendar([])).toBeTruthy()
  })

  it('empty calendar still warns about the usual release slots', () => {
    expect(explainCalendar([])).toMatch(/07:00 and 13:30/i)
  })
})

describe('explainEuropeanTape', () => {
  const base: EuropeanTapeBlock = {
    eurostoxx50DayPct: 0.4, dax40DayPct: 0.5,
    ftseDaxCorr20d: 0.6, ftseSx5eCorr20d: 0.65,
    tapeAgreement: 'ALIGNED', preOpenLead: 'NONE',
  }
  it('ALIGNED reads as confidence-adding, not a naive "tape up = buy"', () => {
    const text = explainEuropeanTape(base)
    expect(text).toMatch(/tracking the rest of Europe/i)
    expect(text).toMatch(/adds confidence/i)
  })
  it('DIVERGING warns the FTSE is trading its own story, not the tape', () => {
    const text = explainEuropeanTape({ ...base, tapeAgreement: 'DIVERGING' })
    expect(text).toMatch(/trading its own story/i)
    expect(text).toMatch(/unreliable/i)
  })
  it('SPLIT flags the European tape itself as internally conflicted', () => {
    const text = explainEuropeanTape({ ...base, tapeAgreement: 'SPLIT' })
    expect(text).toMatch(/disagree with each other/i)
  })
  it('a pre-open lead is surfaced explicitly', () => {
    expect(explainEuropeanTape({ ...base, preOpenLead: 'UP' })).toMatch(/broken UP/i)
    expect(explainEuropeanTape({ ...base, preOpenLead: 'DOWN' })).toMatch(/broken DOWN/i)
  })
})

describe('explainBias', () => {
  const base: BiasBlock = {
    score: 5, label: 'BULLISH', conviction: 'MEDIUM', drivers: [], eventSuppressed: false,
  }
  it('bullish reads as wind at the back of upward moves', () => {
    expect(explainBias(base)).toMatch(/RISING/i)
  })
  it('event suppression is surfaced', () => {
    expect(explainBias({ ...base, eventSuppressed: true })).toMatch(/announcement today/i)
  })
})
