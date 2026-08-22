import { describe, it, expect } from 'vitest'
import { stanceVerdict, signalVerdict, computeOutcome, buildScoreboard, cashCloseCutoffMs, windowEndMs } from '../resolve-orb-journal'

describe('cashCloseCutoffMs / windowEndMs', () => {
  it('16:30 BST (summer) = 15:30 UTC', () => {
    expect(new Date(cashCloseCutoffMs(Date.UTC(2026, 6, 16, 9, 0))).toISOString()).toBe('2026-07-16T15:30:00.000Z')
  })
  it('window caps at the cash close for a late entry', () => {
    // 14:00 UTC (15:00 BST) + 8h would be 22:00, but the close caps it at 15:30 UTC.
    const entry = Date.UTC(2026, 6, 16, 14, 0)
    expect(windowEndMs(entry)).toBe(cashCloseCutoffMs(entry))
  })
  it('window is the flat 8h for an early entry', () => {
    const entry = Date.UTC(2026, 6, 16, 6, 0) // 07:00 BST
    expect(windowEndMs(entry)).toBe(entry + 8 * 3600 * 1000)
  })
})

describe('stanceVerdict', () => {
  it('LONG_FAVOURED: +0.15% close → RIGHT, −0.15% → WRONG, between → FLAT', () => {
    expect(stanceVerdict('LONG_FAVOURED', null, 0.15)).toBe('RIGHT')
    expect(stanceVerdict('LONG_FAVOURED', null, -0.15)).toBe('WRONG')
    expect(stanceVerdict('LONG_FAVOURED', null, 0.1)).toBe('FLAT')
  })
  it('SHORT_FAVOURED inverts', () => {
    expect(stanceVerdict('SHORT_FAVOURED', null, -0.3)).toBe('RIGHT')
    expect(stanceVerdict('SHORT_FAVOURED', null, 0.3)).toBe('WRONG')
  })
  it('FADE_FAVOURED takes its direction from the R1 signal', () => {
    expect(stanceVerdict('FADE_FAVOURED', 'FAVOURS_LONG', 0.5)).toBe('RIGHT')
    expect(stanceVerdict('FADE_FAVOURED', 'FAVOURS_SHORT', 0.5)).toBe('WRONG')
  })
  it('BREAKOUTS_SUSPECT and MIXED are not directional → null', () => {
    expect(stanceVerdict('BREAKOUTS_SUSPECT', null, 0.9)).toBeNull()
    expect(stanceVerdict('MIXED', null, -0.9)).toBeNull()
  })
})

describe('signalVerdict', () => {
  it('directional signals use the ±0.15% toClose test', () => {
    expect(signalVerdict('FAVOURS_LONG', 0.2, 0, 0)).toBe('RIGHT')
    expect(signalVerdict('FAVOURS_SHORT', 0.2, 0, 0)).toBe('WRONG')
    expect(signalVerdict('FAVOURS_LONG', 0.05, 0, 0)).toBe('FLAT')
  })
  it('BREAKOUT_SUSPECT: both excursions < 0.25 → RIGHT (went nowhere)', () => {
    expect(signalVerdict('BREAKOUT_SUSPECT', 0, 0.2, -0.2)).toBe('RIGHT')
  })
  it('BREAKOUT_SUSPECT: an excursion ≥ 0.40 → WRONG (a real extension)', () => {
    expect(signalVerdict('BREAKOUT_SUSPECT', 0, 0.45, -0.1)).toBe('WRONG')
    expect(signalVerdict('BREAKOUT_SUSPECT', 0, 0.1, -0.5)).toBe('WRONG')
  })
  it('BREAKOUT_SUSPECT: in-between excursion → FLAT', () => {
    expect(signalVerdict('BREAKOUT_SUSPECT', 0, 0.3, -0.1)).toBe('FLAT')
  })
  it('NEUTRAL signals are not scored → null', () => {
    expect(signalVerdict('NEUTRAL', 0.9, 0.9, -0.9)).toBeNull()
  })
})

describe('computeOutcome', () => {
  const entryMs = Date.UTC(2026, 6, 16, 9, 0)   // 10:00 BST
  const cutoffMs = entryMs + 6 * 3600 * 1000
  // H1 bars, entry price 10000. Rising to a +0.4% close.
  const bars = [
    { timestamp: entryMs,               high: 10010, low: 9990,  close: 10005 },
    { timestamp: entryMs + 3600_000,    high: 10030, low: 10000, close: 10025 },
    { timestamp: entryMs + 2 * 3600_000, high: 10045, low: 10020, close: 10040 },
    { timestamp: entryMs + 3 * 3600_000, high: 10050, low: 10030, close: 10040 },
  ]
  const entry = { at: new Date(entryMs).toISOString(), price: 10000, stance: 'LONG_FAVOURED',
    signals: [{ direction: 'FAVOURS_LONG', rule: 'R3' }, { direction: 'BREAKOUT_SUSPECT', rule: 'R4' }] }

  it('computes toClose / excursions / forward returns and a RIGHT long verdict', () => {
    const o = computeOutcome(entry, bars, cutoffMs)
    expect(o.toClosePct).toBe(0.4)          // (10040-10000)/10000
    expect(o.maxUpPct).toBe(0.5)            // high 10050
    expect(o.maxDownPct).toBe(-0.1)         // low 9990
    expect(o.fwd1hPct).toBe(0.25)           // close of the +1h bar (10025)
    expect(o.verdict).toBe('RIGHT')
    // R3 FAVOURS_LONG → RIGHT; R4 BREAKOUT_SUSPECT with a 0.5% up excursion → WRONG.
    expect(o.signalVerdicts).toEqual([
      { rule: 'R3', verdict: 'RIGHT' },
      { rule: 'R4', verdict: 'WRONG' },
    ])
  })

  it('fwd3hPct is null when the window is shorter than ~3h', () => {
    const shortCutoff = entryMs + 2 * 3600 * 1000
    const o = computeOutcome(entry, bars.slice(0, 3), shortCutoff)
    expect(o.fwd3hPct).toBeNull()
  })
})

describe('buildScoreboard', () => {
  const mk = (stance: string, verdict: 'RIGHT' | 'WRONG' | 'FLAT' | null, toClosePct: number, signalVerdicts: { rule: string; verdict: 'RIGHT' | 'WRONG' | 'FLAT' }[], maxUpPct = 0, maxDownPct = 0) => ({
    stance,
    outcome: { resolvedAt: '', fwd1hPct: null, fwd3hPct: null, toClosePct, maxUpPct, maxDownPct, verdict, signalVerdicts },
  })

  it('aggregates per-stance, per-rule, and the breakouts-suspect no-extension rate', () => {
    const sb = buildScoreboard([
      mk('FADE_FAVOURED', 'RIGHT', 0.3, [{ rule: 'R1', verdict: 'RIGHT' }]),
      mk('FADE_FAVOURED', 'WRONG', -0.2, [{ rule: 'R1', verdict: 'WRONG' }]),
      mk('LONG_FAVOURED', 'RIGHT', 0.4, [{ rule: 'R3', verdict: 'RIGHT' }, { rule: 'R1', verdict: 'RIGHT' }]),
      mk('BREAKOUTS_SUSPECT', null, 0, [{ rule: 'R4', verdict: 'RIGHT' }], 0.1, -0.1),   // no extension
      mk('BREAKOUTS_SUSPECT', null, 0, [{ rule: 'R4', verdict: 'WRONG' }], 0.5, -0.1),   // extended
    ])
    expect(sb.entriesScored).toBe(5)
    expect(sb.byStance.FADE_FAVOURED).toEqual({ n: 2, right: 1, wrong: 1, flat: 0, avgToClosePct: 0.05 })
    expect(sb.byStance.LONG_FAVOURED.right).toBe(1)
    expect(sb.byStance.BREAKOUTS_SUSPECT).toBeUndefined()   // not a directional stance
    expect(sb.byRule.R1).toEqual({ n: 3, right: 2, wrong: 1, flat: 0 })
    expect(sb.byRule.R4).toEqual({ n: 2, right: 1, wrong: 1, flat: 0 })
    expect(sb.breakoutsSuspect.n).toBe(2)
    expect(sb.breakoutsSuspect.noExtensionRate).toBe(0.5)
  })
})
