import { describe, it, expect } from 'vitest'
import {
  parsePriceInRange,
  parseSections,
  parseKVRows,
  parseProbability,
} from '../parsers'
import fixture from '../../../test-fixtures/session-2026-07-06.json'

const analysis = (fixture as { analysis: string }).analysis

describe('parsePriceInRange', () => {
  it('skips an H1/M5 prefix and returns the first real zone keyword (regression: the "H" bug)', () => {
    // The real line begins "Current Price vs Equilibrium:** H1 PREMIUM (...)".
    // The old /[A-Z]+/ regex matched "H" from "H1"; the fixed parser must return PREMIUM.
    const line = '- **Current Price vs Equilibrium:** H1 PREMIUM (4161.77 above H1 eq 4151.42)'
    const r = parsePriceInRange(line)
    expect(r).not.toBeNull()
    expect(r!.status).toBe('PREMIUM')
    expect(r!.level).toBe('4161.77')
  })

  it('parses the real 2026-07-06 fixture without returning a bare "H"', () => {
    const r = parsePriceInRange(analysis)
    expect(r).not.toBeNull()
    expect(['DISCOUNT', 'PREMIUM', 'EQUILIBRIUM', 'OTE']).toContain(r!.status)
    expect(r!.status).toBe('PREMIUM')
  })

  it('returns null when there is no equilibrium line', () => {
    expect(parsePriceInRange('nothing relevant here')).toBeNull()
  })

  it('returns null when the line has no known zone keyword', () => {
    expect(parsePriceInRange('- **Current Price vs Equilibrium:** unknown state')).toBeNull()
  })
})

describe('parseSections', () => {
  it('splits the real fixture into its 11 top-level sections', () => {
    const sections = parseSections(analysis)
    expect(sections.length).toBe(11)
    const titles = sections.map(s => s.title)
    expect(titles).toContain('ACCOUNT CONTEXT')
    expect(titles).toContain('PROBABILITY ASSESSMENT')
    expect(titles).toContain('MARKET NARRATIVE')
  })

  it('does not include the top-level # title as a section', () => {
    const sections = parseSections(analysis)
    expect(sections.every(s => !s.title.startsWith('GOLD INTRADAY'))).toBe(true)
  })
})

describe('parseKVRows', () => {
  it('extracts bold key/value pairs from the Account Context section', () => {
    const account = parseSections(analysis).find(s => s.title === 'ACCOUNT CONTEXT')
    expect(account).toBeDefined()
    const rows = parseKVRows(account!.body)
    expect(rows.length).toBeGreaterThan(0)
    expect(rows.some(r => /open position/i.test(r.label))).toBe(true)
  })
})

describe('parseProbability', () => {
  it('extracts primary/secondary/confidence/invalidation from the real fixture', () => {
    const prob = parseSections(analysis).find(s => s.title.includes('PROBABILITY'))
    expect(prob).toBeDefined()
    const p = parseProbability(prob!.body)
    expect(p.primaryPct).toBe(72)
    expect(p.primaryBias).toBe('BULLISH')
    expect(p.secondaryPct).toBe(30)
    expect(p.secondaryBias).toBe('BEARISH')
    expect(p.confidence).toBe('MEDIUM')
    expect(p.invalidation).toMatch(/^4150\.00/)
  })

  it('returns all-null on empty input rather than throwing', () => {
    const p = parseProbability('')
    expect(p.primaryPct).toBeNull()
    expect(p.confidence).toBeNull()
  })
})
