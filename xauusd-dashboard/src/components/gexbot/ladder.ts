import type { GexSnapshot } from '../../types/gex'

export type LevelKind = 'call' | 'put' | 'zero' | 'spot'

export interface Level {
  price: number
  label: string
  kind: LevelKind
  /** Which reading it came from; spot and zero gamma belong to neither. */
  reading?: 'vol' | 'oi'
}

/**
 * The levels for one symbol, ordered high to low like a chart's price axis.
 *
 * Both readings are included deliberately. Which one price respects is the
 * open question this project exists to answer, so the ladder shows them side
 * by side rather than quietly picking one.
 */
export function buildLadder(s: GexSnapshot): Level[] {
  const levels: Level[] = [
    { price: s.major_pos_vol, label: 'Call wall', kind: 'call', reading: 'vol' },
    { price: s.major_neg_vol, label: 'Put wall', kind: 'put', reading: 'vol' },
    { price: s.major_pos_oi, label: 'Call wall', kind: 'call', reading: 'oi' },
    { price: s.major_neg_oi, label: 'Put wall', kind: 'put', reading: 'oi' },
    { price: s.spot, label: 'Spot', kind: 'spot' },
  ]
  // zero_gamma reads 0 until GexBot computes it during the session, and the
  // volume walls read 0 outside cash hours. Plotting those would put bogus
  // levels at the bottom of the ladder, which is worse than omitting them:
  // these numbers get drawn on a chart and traded against.
  if (s.zero_gamma > 0) {
    levels.push({ price: s.zero_gamma, label: 'Zero gamma', kind: 'zero' })
  }
  return levels.filter(l => l.price > 0).sort((a, b) => b.price - a.price)
}
