/**
 * GexBot gamma levels, as written to Firestore by
 * .github/workflows/gexbot-record.yml (Gex-Bot/scripts/record_snapshot.py).
 *
 * Field names mirror GexBot's API exactly rather than being renamed, so a
 * value on screen can be traced straight back to the source payload.
 *
 * Every level comes in two readings, and the project has not yet established
 * which one price actually respects — see
 * Gex-Bot/youtube-research/analysis/strategy-synthesis.md §5. The UI shows
 * both and takes no side.
 */

/** One entry in the max-change panel: 1/5/10/15/30-minute lookbacks. */
export interface MaxPrior {
  strike: number
  change: number
}

/** One strike in the gamma ladder.
 *
 *  `priors` holds five earlier samples of this strike's gamma (1, 5, 10, 15
 *  and 30 minutes ago, most recent first). They are what makes a wall
 *  readable as building or being taken off, and are plotted as dots against
 *  the same axis as the bar -- the feature GexBot's own ladder is built
 *  around. The ordering is inferred from the GexFuture walkthrough rather
 *  than stated by the API; see Gex-Bot/docs/recorder.md. */
export interface LadderRung {
  strike: number
  gex_vol: number
  gex_oi: number
  priors: number[]
}

export interface GexSnapshot {
  /** When our recorder fetched it (ISO). */
  fetched_at: string
  /** GexBot's own timestamp for the data (unix seconds). */
  source_ts: number
  source_time: string

  ticker: string
  /** zero = 0DTE, one = next expiry, full = 90-day view. */
  scope: string

  spot: number
  /** Regime divider. 0 when GexBot has not computed it (outside RTH). */
  zero_gamma: number

  // Volume-weighted reading — today's traded flow.
  major_pos_vol: number
  major_neg_vol: number
  sum_gex_vol: number

  // Open-interest reading — standing positioning.
  major_pos_oi: number
  major_neg_oi: number
  sum_gex_oi: number

  min_dte: number | null
  sec_min_dte: number | null
  delta_risk_reversal: number
  max_priors: MaxPrior[] | null

  // Derived by the recorder so disagreement is queryable, not recomputed.
  regime_vol: number
  regime_oi: number
  regimes_agree: boolean
  walls_agree: boolean
  spot_vs_zero_gamma: number | null

  /** Full per-strike ladder. Present on gex_latest only -- the history
   *  collection stays compact deliberately. */
  ladder?: LadderRung[]
}

/** Which of the two readings the UI is currently showing. */
export type GexReading = 'vol' | 'oi'
