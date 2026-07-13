import { describe, it, expect } from 'vitest'
import { mergeCalendars, UK_STATIC_CALENDAR_2026, US_STATIC_CALENDAR_2026 } from '../calendar'

// mergeCalendars(finnhub, staticEntries, today) — UK100-V2-PLAN.md Phase A2 +
// UK100-SESSION-REVIEW-2026-07-13.md F4. Finnhub's calendar endpoint is
// premium-gated on this account's key, so the static ONS/Fed/BLS/BEA-verified
// lists are the primary UK+US source; these tests pin the merge/dedupe
// contract (now region-qualified) that lets both coexist safely if Finnhub
// access is ever restored.

describe('mergeCalendars', () => {
  const today = '2026-07-20'

  it('returns the static entries when Finnhub is empty', () => {
    const result = mergeCalendars(
      [],
      [{ date: '2026-07-22', event: 'UK CPI', timeLondon: '07:00', impact: 'HIGH', region: 'UK' }],
      today,
    )
    expect(result).toHaveLength(1)
    expect(result[0].event).toBe('UK CPI')
    expect(result[0].region).toBe('UK')
    expect(result[0].daysFromToday).toBe(2)
  })

  it('drops the static entry from the merged output on a same-day same-region same-class Finnhub duplicate, keeping the static values', () => {
    const result = mergeCalendars(
      [{
        event: 'UK CPI YoY', region: 'UK', impact: 'HIGH',
        timeIso: '2026-07-22T06:00:00Z', timeLondon: '07:00 BST', daysFromToday: 2,
        prior: '2.1%', consensus: '2.0%',
      }],
      [{ date: '2026-07-22', event: 'UK CPI', timeLondon: '07:00', impact: 'HIGH', region: 'UK' }],
      today,
    )
    // static wins — exactly one CPI entry survives, not two
    expect(result).toHaveLength(1)
    expect(result[0].event).toBe('UK CPI')
  })

  it('keeps Finnhub events that do not collide with any static entry', () => {
    const result = mergeCalendars(
      [{
        event: 'Some Other US Release', region: 'US', impact: 'HIGH',
        timeIso: '2026-07-21T12:30:00Z', timeLondon: '13:30 BST', daysFromToday: 1,
      }],
      [{ date: '2026-07-22', event: 'UK CPI', timeLondon: '07:00', impact: 'HIGH', region: 'UK' }],
      today,
    )
    expect(result.map(e => e.event)).toEqual(['Some Other US Release', 'UK CPI'])
  })

  it('drops entries outside the 0-4 day lookahead window', () => {
    const result = mergeCalendars(
      [],
      [
        { date: '2026-07-19', event: 'UK GDP Monthly Estimate', timeLondon: '07:00', impact: 'HIGH', region: 'UK' }, // yesterday
        { date: '2026-07-21', event: 'UK Labour Market Report', timeLondon: '07:00', impact: 'HIGH', region: 'UK' }, // +1
        { date: '2026-07-30', event: 'BoE MPC Rate Decision', timeLondon: '12:00', impact: 'HIGH', region: 'UK' }, // +10, out of window
      ],
      today,
    )
    expect(result.map(e => e.event)).toEqual(['UK Labour Market Report'])
  })

  it('sorts the merged output chronologically', () => {
    const result = mergeCalendars(
      [],
      [
        { date: '2026-07-24', event: 'UK Retail Sales', timeLondon: '07:00', impact: 'HIGH', region: 'UK' },
        { date: '2026-07-21', event: 'UK Labour Market Report', timeLondon: '07:00', impact: 'HIGH', region: 'UK' },
      ],
      today,
    )
    expect(result.map(e => e.event)).toEqual(['UK Labour Market Report', 'UK Retail Sales'])
  })

  it('renders static timeLondon with the correct BST/GMT suffix', () => {
    const result = mergeCalendars(
      [],
      [{ date: '2026-07-22', event: 'UK CPI', timeLondon: '07:00', impact: 'HIGH', region: 'UK' }],
      today,
    )
    expect(result[0].timeLondon).toBe('07:00 BST')
  })

  it('does NOT dedupe a UK and a US release of the same keyword class on the same day — region-qualified key', () => {
    const result = mergeCalendars(
      [],
      [
        { date: '2026-07-22', event: 'UK CPI', timeLondon: '07:00', impact: 'HIGH', region: 'UK' },
        { date: '2026-07-22', event: 'US CPI', timeLondon: '13:30', impact: 'HIGH', region: 'US' },
      ],
      today,
    )
    expect(result).toHaveLength(2)
    expect(result.map(e => e.event)).toEqual(['UK CPI', 'US CPI'])
    expect(result.map(e => e.region)).toEqual(['UK', 'US'])
  })

  it('dedupes a US static entry against a same-region same-day Finnhub duplicate, but leaves a UK entry on the same date untouched', () => {
    const result = mergeCalendars(
      [{
        event: 'US CPI YoY', region: 'US', impact: 'HIGH',
        timeIso: '2026-07-22T12:30:00Z', timeLondon: '13:30 BST', daysFromToday: 2,
      }],
      [
        { date: '2026-07-22', event: 'US CPI', timeLondon: '13:30', impact: 'HIGH', region: 'US' },
        { date: '2026-07-22', event: 'UK CPI', timeLondon: '07:00', impact: 'HIGH', region: 'UK' },
      ],
      today,
    )
    expect(result).toHaveLength(2)
    expect(result.find(e => e.region === 'US')?.event).toBe('US CPI') // static wins
    expect(result.find(e => e.region === 'UK')?.event).toBe('UK CPI') // untouched
  })

  it('merges the real UK_STATIC_CALENDAR_2026 and US_STATIC_CALENDAR_2026 exports together without collision', () => {
    // today = the UK GDP release date itself (daysFromToday 0, inside the
    // window); the other UK entries fall further out than the 0-4 day
    // lookahead from this particular today and are correctly absent — the
    // point of this test is that merging the two real exported arrays
    // together doesn't crash and produces no duplicate event names, not
    // that every UK entry is simultaneously in-window.
    const result = mergeCalendars([], [...UK_STATIC_CALENDAR_2026, ...US_STATIC_CALENDAR_2026], '2026-07-16')
    const events = result.map(e => e.event)
    expect(events).toContain('UK GDP Monthly Estimate')
    expect(new Set(events).size).toBe(events.length)
  })

  it('US_STATIC_CALENDAR_2026 entries are all region US, impact HIGH, and carry only known event types', () => {
    const allowedEvents = new Set(['FOMC Rate Decision', 'US CPI', 'US Nonfarm Payrolls', 'US PCE Price Index'])
    for (const e of US_STATIC_CALENDAR_2026) {
      expect(e.region).toBe('US')
      expect(e.impact).toBe('HIGH')
      expect(allowedEvents.has(e.event)).toBe(true)
      expect(e.date).toMatch(/^2026-\d{2}-\d{2}$/)
    }
  })
})
