import { describe, it, expect } from 'vitest'
import { synthesizeTldr } from '../tldr'
import type { Uk100SessionRecord, TldrBullet } from '../../../types/uk100'

// Minimal record scaffold — the fields synthesizeTldr does not read are set to
// placeholder values.
function rec(over: Partial<Uk100SessionRecord> = {}): Uk100SessionRecord {
  return {
    timestamp: '2026-07-15T14:26:31.542Z', date: '2026-07-15', time: '15:26 BST',
    session: 'LONDON', bias: 'NEUTRAL', biasScore: 1, probability: 61, confidence: 3,
    analysis: '',
    ...over,
  }
}

describe('synthesizeTldr', () => {
  it('returns record.tldr verbatim when present (skill-written is source of truth)', () => {
    const tldr: TldrBullet[] = [
      { tag: 'STRUCTURE', text: 'H1 NEUTRAL / M5 BULLISH — sweep-and-reclaim day.' },
      { tag: 'PLAN', text: 'BOTH_OK half size — prefer the fade toward 10502.' },
    ]
    expect(synthesizeTldr(rec({ tldr }))).toBe(tldr)
  })

  it('fallback synthesises REGIME/PLAN/LEVELS/RISK from the real 2026-07-15 record fields', () => {
    const out = synthesizeTldr(rec({
      bias: 'NEUTRAL', biasScore: 1, confidence: 3,
      orbPlaybook: { direction: 'BOTH_OK', dayType: 'RANGE_EXPECTED', reasoning: '', keyLevels: [], invalidation: '' },
      tradeIdea: { direction: 'SHORT', status: 'WAIT', targets: [10502.4, 10482.7], stop: 10535, rr: 1.61, setupType: 'FVG Entry' },
      probability: 61,
      invalidation: 10535,
      drawOnLiquidity: 10482.7,
      nextHighImpactEvent: { event: 'UK GDP Monthly Estimate', timeIso: '2026-07-16T06:00:00.000Z' },
    }))
    const tags = out.map(b => b.tag)
    expect(tags).toContain('REGIME')
    expect(tags).toContain('PLAN')
    expect(tags).toContain('LEVELS')
    expect(tags).toContain('RISK')
    expect(out.find(b => b.tag === 'PLAN')!.text).toMatch(/BOTH_OK/)
    expect(out.find(b => b.tag === 'PLAN')!.text).toMatch(/SHORT WAIT \(61%\)/)
    expect(out.find(b => b.tag === 'LEVELS')!.text).toMatch(/10535 invalidation/)
    // STRUCTURE/NEWS are not derivable from meta and must be omitted in fallback.
    expect(tags).not.toContain('STRUCTURE')
    expect(tags).not.toContain('NEWS')
  })

  it('skips bullets whose inputs are missing', () => {
    const out = synthesizeTldr(rec({
      bias: 'BEARISH', biasScore: -4, confidence: 6,
      // no orbPlaybook, no tradeIdea, no levels, no event
      orbPlaybook: undefined, tradeIdea: undefined,
      invalidation: undefined, drawOnLiquidity: undefined, nextHighImpactEvent: undefined,
    }))
    expect(out.map(b => b.tag)).toEqual(['REGIME'])
  })

  it('returns [] for a null record (card hidden)', () => {
    expect(synthesizeTldr(null)).toEqual([])
  })

  it('LEVELS does not repeat the draw when it equals T1', () => {
    const out = synthesizeTldr(rec({
      invalidation: 10535,
      drawOnLiquidity: 10502.4,
      tradeIdea: { direction: 'SHORT', status: 'WAIT', targets: [10502.4] },
    }))
    const levels = out.find(b => b.tag === 'LEVELS')!.text
    expect(levels).toMatch(/10502.4 T1/)
    expect(levels).not.toMatch(/10502.4 draw/)
  })
})
