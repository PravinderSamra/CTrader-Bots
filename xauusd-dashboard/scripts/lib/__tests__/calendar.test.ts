import { describe, it, expect } from 'vitest'
import { mergeCalendars } from '../calendar'

// mergeCalendars(finnhub, staticEntries, today) — UK100-V2-PLAN.md Phase A2.
// Finnhub's calendar endpoint is premium-gated on this account's key, so the
// static ONS-verified list is the primary UK source; these tests pin the
// merge/dedupe contract that lets both coexist safely if Finnhub access is
// ever restored.

describe('mergeCalendars', () => {
  const today = '2026-07-20'

  it('returns the static entries when Finnhub is empty', () => {
    const result = mergeCalendars(
      [],
      [{ date: '2026-07-22', event: 'UK CPI', timeLondon: '07:00', impact: 'HIGH' }],
      today,
    )
    expect(result).toHaveLength(1)
    expect(result[0].event).toBe('UK CPI')
    expect(result[0].region).toBe('UK')
    expect(result[0].daysFromToday).toBe(2)
  })

  it('drops the static entry from the merged output on a same-day same-class Finnhub duplicate, keeping the static values', () => {
    const result = mergeCalendars(
      [{
        event: 'UK CPI YoY', region: 'UK', impact: 'HIGH',
        timeIso: '2026-07-22T06:00:00Z', timeLondon: '07:00 BST', daysFromToday: 2,
        prior: '2.1%', consensus: '2.0%',
      }],
      [{ date: '2026-07-22', event: 'UK CPI', timeLondon: '07:00', impact: 'HIGH' }],
      today,
    )
    // static wins — exactly one CPI entry survives, not two
    expect(result).toHaveLength(1)
    expect(result[0].event).toBe('UK CPI')
  })

  it('keeps Finnhub events that do not collide with any static entry', () => {
    const result = mergeCalendars(
      [{
        event: 'US Nonfarm Payrolls', region: 'US', impact: 'HIGH',
        timeIso: '2026-07-21T12:30:00Z', timeLondon: '13:30 BST', daysFromToday: 1,
      }],
      [{ date: '2026-07-22', event: 'UK CPI', timeLondon: '07:00', impact: 'HIGH' }],
      today,
    )
    expect(result.map(e => e.event)).toEqual(['US Nonfarm Payrolls', 'UK CPI'])
  })

  it('drops entries outside the 0-4 day lookahead window', () => {
    const result = mergeCalendars(
      [],
      [
        { date: '2026-07-19', event: 'UK GDP Monthly Estimate', timeLondon: '07:00', impact: 'HIGH' }, // yesterday
        { date: '2026-07-21', event: 'UK Labour Market Report', timeLondon: '07:00', impact: 'HIGH' }, // +1
        { date: '2026-07-30', event: 'BoE MPC Rate Decision', timeLondon: '12:00', impact: 'HIGH' }, // +10, out of window
      ],
      today,
    )
    expect(result.map(e => e.event)).toEqual(['UK Labour Market Report'])
  })

  it('sorts the merged output chronologically', () => {
    const result = mergeCalendars(
      [],
      [
        { date: '2026-07-24', event: 'UK Retail Sales', timeLondon: '07:00', impact: 'HIGH' },
        { date: '2026-07-21', event: 'UK Labour Market Report', timeLondon: '07:00', impact: 'HIGH' },
      ],
      today,
    )
    expect(result.map(e => e.event)).toEqual(['UK Labour Market Report', 'UK Retail Sales'])
  })

  it('renders static timeLondon with the correct BST/GMT suffix', () => {
    const result = mergeCalendars(
      [],
      [{ date: '2026-07-22', event: 'UK CPI', timeLondon: '07:00', impact: 'HIGH' }],
      today,
    )
    expect(result[0].timeLondon).toBe('07:00 BST')
  })
})
