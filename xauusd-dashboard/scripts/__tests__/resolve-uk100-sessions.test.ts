import { describe, it, expect } from 'vitest'
import { classify, classifyHits, cashCloseCutoffMs, firstFillIndex, recordLean, biasVerdictFor } from '../resolve-uk100-sessions'

describe('cashCloseCutoffMs', () => {
  it('resolves 16:30 BST (summer, UTC+1) for a July analysis time', () => {
    const ts = Date.UTC(2026, 6, 13, 8, 0, 0) // 2026-07-13 08:00 UTC
    const cutoff = cashCloseCutoffMs(ts)
    expect(new Date(cutoff).toISOString()).toBe('2026-07-13T15:30:00.000Z') // 16:30 BST = 15:30 UTC
  })

  it('resolves 16:30 GMT (winter, UTC+0) for a January analysis time', () => {
    const ts = Date.UTC(2026, 0, 13, 8, 0, 0) // 2026-01-13 08:00 UTC
    const cutoff = cashCloseCutoffMs(ts)
    expect(new Date(cutoff).toISOString()).toBe('2026-01-13T16:30:00.000Z')
  })
})

describe('classify — base WIN/LOSS/EXPIRED result (drawOnLiquidity/invalidation)', () => {
  const baseRec = {
    timestamp: '2026-07-13T08:00:00.000Z',
    date: '2026-07-13', time: '09:00 BST', session: 'LONDON',
    bias: 'NEUTRAL', probability: 60, confidence: 5,
    tradeIdea: { direction: 'LONG' as const, status: 'ACTIVE' },
    priceAtAnalysis: 100,
    drawOnLiquidity: 110,
    invalidation: 90,
  }
  const ts = Date.parse(baseRec.timestamp)
  const cutoffMs = ts + 8 * 3600 * 1000

  it('WIN when the target is reached before the stop', () => {
    const bars = [{ open: 100, high: 105, low: 99, close: 104 }, { open: 104, high: 111, low: 103, close: 110 }]
    const out = classify(baseRec, bars, ts + 3600_000, cutoffMs)
    expect(out?.result).toBe('WIN')
  })

  it('LOSS when the stop is reached before the target', () => {
    const bars = [{ open: 100, high: 102, low: 89, close: 90 }]
    const out = classify(baseRec, bars, ts + 3600_000, cutoffMs)
    expect(out?.result).toBe('LOSS')
  })

  it('LOSS (conservative) when both the target and stop are touched in the same bar', () => {
    const bars = [{ open: 100, high: 112, low: 88, close: 95 }]
    const out = classify(baseRec, bars, ts + 3600_000, cutoffMs)
    expect(out?.result).toBe('LOSS')
  })

  it('returns null (not yet resolvable) when neither level is hit and the window is not complete', () => {
    const bars = [{ open: 100, high: 101, low: 99, close: 100 }]
    const out = classify(baseRec, bars, ts + 3600_000, cutoffMs) // now < cutoffMs
    expect(out).toBeNull()
  })

  it('EXPIRED_FAVOURABLE when the window completes with price favourably placed but no level hit', () => {
    const bars = [{ open: 100, high: 103, low: 99, close: 103 }]
    const out = classify(baseRec, bars, cutoffMs + 1, cutoffMs)
    expect(out?.result).toBe('EXPIRED_FAVOURABLE')
  })

  it('EXPIRED_ADVERSE when the window completes with price adversely placed but no level hit', () => {
    const bars = [{ open: 100, high: 101, low: 96, close: 97 }]
    const out = classify(baseRec, bars, cutoffMs + 1, cutoffMs)
    expect(out?.result).toBe('EXPIRED_ADVERSE')
  })

  it('SHORT direction inverts the target/stop comparisons', () => {
    const shortRec = { ...baseRec, tradeIdea: { direction: 'SHORT' as const, status: 'ACTIVE' }, drawOnLiquidity: 90, invalidation: 110 }
    const bars = [{ open: 100, high: 101, low: 89, close: 90 }]
    const out = classify(shortRec, bars, ts + 3600_000, cutoffMs)
    expect(out?.result).toBe('WIN')
  })
})

// F7 (UK100-SESSION-REVIEW-2026-07-13.md §5): the "today's T1->T2->STOP
// sequence" the review doc calls out as the canonical test case — a real
// 2026-07-13 UK100 session (bias NEUTRAL, ORB-playbook ACTIVE LONG,
// targets [10495.9, 10506.9, 10526.3], stop 10477) that ran to two targets
// before eventually reversing into the stop.
describe('classifyHits — F7 chronological level-hit sequence', () => {
  it('records a T1 -> T2 -> STOP sequence in order', () => {
    const bars = [
      { high: 10496, low: 10490, timestamp: Date.UTC(2026, 6, 13, 13, 0) },   // T1 (10495.9)
      { high: 10508, low: 10500, timestamp: Date.UTC(2026, 6, 13, 14, 0) },   // T2 (10506.9)
      { high: 10505, low: 10470, timestamp: Date.UTC(2026, 6, 13, 15, 0) },   // STOP (10477)
    ]
    const hits = classifyHits('LONG', [10495.9, 10506.9, 10526.3], 10477, bars)
    expect(hits.map(h => h.level)).toEqual(['T1', 'T2', 'STOP'])
    expect(hits[0].timestamp).toBe(new Date(Date.UTC(2026, 6, 13, 13, 0)).toISOString())
  })

  it('stops the scan at STOP — no further targets are recorded after it', () => {
    const bars = [
      { high: 10496, low: 10490, timestamp: 1 },   // T1
      { high: 10490, low: 10470, timestamp: 2 },   // STOP
      { high: 10530, low: 10520, timestamp: 3 },   // would be T2/T3 if scanned — must not appear
    ]
    const hits = classifyHits('LONG', [10495.9, 10506.9, 10526.3], 10477, bars)
    expect(hits.map(h => h.level)).toEqual(['T1', 'STOP'])
  })

  it('a bar touching an unhit target AND the stop counts only the stop (conservative rule)', () => {
    const bars = [{ high: 10530, low: 10470, timestamp: 1 }] // touches T1/T2/T3 and stop all in one bar
    const hits = classifyHits('LONG', [10495.9, 10506.9, 10526.3], 10477, bars)
    expect(hits).toEqual([{ level: 'STOP', timestamp: new Date(1).toISOString() }])
  })

  it('returns an empty sequence when nothing is touched', () => {
    const bars = [{ high: 10493, low: 10480, timestamp: 1 }]
    const hits = classifyHits('LONG', [10495.9, 10506.9], 10477, bars)
    expect(hits).toEqual([])
  })

  it('stops scanning once all targets are hit (no stop ever touched)', () => {
    const bars = [{ high: 10510, low: 10490, timestamp: 1 }, { high: 10490, low: 10470, timestamp: 2 }]
    // T1 and T2 both hit in bar 1; bar 2 would hit STOP but scanning should
    // already have ended once all targets were hit... actually it should
    // still scan for the stop since the position could still be open past
    // partial targets — this fixture intentionally shows both targets hit
    // then the loop naturally ends without a stop entry once all targets
    // are exhausted and the loop's hitIdx.size === targets.length break fires.
    const hits = classifyHits('LONG', [10495.9, 10506.9], 10477, bars)
    expect(hits.map(h => h.level)).toEqual(['T1', 'T2'])
  })

  it('SHORT direction inverts the target/stop comparisons', () => {
    const bars = [{ high: 10480, low: 10470, timestamp: 1 }]
    const hits = classifyHits('SHORT', [10475, 10465], 10490, bars)
    expect(hits.map(h => h.level)).toEqual(['T1'])
  })
})

describe('firstFillIndex — WAIT entry-zone fill detection', () => {
  it('LONG fills when a bar dips into the zone from above (low <= entryHigh)', () => {
    const bars = [
      { high: 10620, low: 10610 },  // above the zone — no fill
      { high: 10615, low: 10596 },  // low 10596 <= entryHigh 10600 → fills here (idx 1)
      { high: 10630, low: 10605 },
    ]
    expect(firstFillIndex('LONG', 10590, 10600, bars)).toBe(1)
  })

  it('SHORT fills when a bar bounces into the zone from below (high >= entryLow)', () => {
    const bars = [
      { high: 10470, low: 10460 },  // below the zone — no fill
      { high: 10489, low: 10475 },  // high 10489 >= entryLow 10488 → fills here (idx 1)
    ]
    expect(firstFillIndex('SHORT', 10488, 10496, bars)).toBe(1)
  })

  it('returns -1 when price never reaches the zone within the window', () => {
    const bars = [{ high: 10470, low: 10460 }, { high: 10475, low: 10465 }]
    expect(firstFillIndex('SHORT', 10488, 10496, bars)).toBe(-1) // never bounced to 10488
  })
})

describe('classify — WAIT-fill scoring (the 2026-07-16 miss the resolver used to drop)', () => {
  // SHORT WAIT: entry zone 10488–10496, stop/invalidation 10505.2, target 10429.6.
  // The market rose INTO the zone, then kept rising through the stop — a real
  // LOSS that the old ACTIVE-only gate scored as NO_CALL. Here we feed only the
  // post-fill bars (as main() slices them) with entry = entryLow (10488, the
  // short's least-favourable fill) and expect a LOSS.
  const shortRec = {
    timestamp: '2026-07-16T07:39:00.000Z',
    date: '2026-07-16', time: '08:39 BST', session: 'LONDON',
    bias: 'BEARISH', probability: 80, confidence: 5,
    tradeIdea: { direction: 'SHORT' as const, status: 'WAIT', entryLow: 10488, entryHigh: 10496, stop: 10508, targets: [10429.6] },
    priceAtAnalysis: 10460.65,
    drawOnLiquidity: 10429.6,   // target (down)
    invalidation: 10505.2,      // stop (up)
  }
  const ts = Date.parse(shortRec.timestamp)
  const cutoffMs = ts + 8 * 3600 * 1000

  it('scores LOSS when a filled SHORT WAIT then runs through its invalidation', () => {
    // post-fill bars: price pushes up past 10505.2 → stop hit
    const postFill = [{ open: 10490, high: 10515, low: 10488, close: 10512 }]
    const out = classify(shortRec, postFill, ts + 4 * 3600_000, cutoffMs, 10488)
    expect(out?.result).toBe('LOSS')
  })

  it('scores WIN when a filled SHORT WAIT reaches its target before the stop', () => {
    const postFill = [{ open: 10490, high: 10497, low: 10425, close: 10430 }]
    const out = classify(shortRec, postFill, ts + 4 * 3600_000, cutoffMs, 10488)
    expect(out?.result).toBe('WIN')
  })
})

describe('recordLean / biasVerdictFor — bias-direction accuracy', () => {
  it('lean is the bias label, else the trade direction, else null', () => {
    expect(recordLean('BULLISH')).toBe('BULLISH')
    expect(recordLean('BEARISH', 'LONG')).toBe('BEARISH')    // explicit bias wins
    expect(recordLean('NEUTRAL', 'SHORT')).toBe('BEARISH')   // NEUTRAL → fall back to trade dir
    expect(recordLean('NEUTRAL', 'LONG')).toBe('BULLISH')
    expect(recordLean('NEUTRAL')).toBeNull()
  })
  it('grades the lean against the session close with a ±0.15% dead-band', () => {
    // 2026-07-23: BEARISH, price 10675.35 → close ~10580 → RIGHT
    expect(biasVerdictFor('BEARISH', 10675.35, 10580)).toBe('RIGHT')
    expect(biasVerdictFor('BEARISH', 10675.35, 10720)).toBe('WRONG')   // rose → bearish wrong
    expect(biasVerdictFor('BULLISH', 10000, 10005)).toBe('FLAT')       // +0.05% < 0.15%
    expect(biasVerdictFor('BULLISH', 10000, 10200)).toBe('RIGHT')
  })
})
