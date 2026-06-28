import { useState, useCallback } from 'react'
import type { BriefingResult } from '../../types/dashboard'
import type { AggregatedData } from '../../services/dataAggregator'
import { generateBriefing } from '../../services/anthropicBriefing'
import { BiasGauge } from './BiasGauge'
import styles from './BriefingPanel.module.css'

function fmtTime(iso: string): string {
  if (!iso) return ''
  try {
    const d = new Date(iso)
    return `${String(d.getUTCHours()).padStart(2,'0')}:${String(d.getUTCMinutes()).padStart(2,'0')} GMT`
  } catch { return iso }
}

interface Props {
  data: AggregatedData
  headlines: string[]
}

export function BriefingPanel({ data, headlines }: Props) {
  const [briefing, setBriefing] = useState<BriefingResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const generate = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await generateBriefing(data)
      setBriefing(result)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unknown error generating briefing')
    } finally {
      setLoading(false)
    }
  }, [data])

  return (
    <div className={styles.panel}>
      <div className={styles.header}>
        <div>
          <div className={styles.eyebrow}>Daily Intelligence Briefing</div>
          <div className={styles.sub}>
            AI-synthesised market context for today's XAUUSD session
          </div>
        </div>
        <div className={styles.headerActions}>
          {briefing && (
            <span className={styles.genTime}>Generated: {fmtTime(briefing.generatedAt)}</span>
          )}
          <button
            className={styles.generateBtn}
            onClick={generate}
            disabled={loading}
          >
            {loading ? (
              <><span className="pulse">●</span> Generating...</>
            ) : briefing ? (
              '↺ Refresh Briefing'
            ) : (
              'Generate Briefing'
            )}
          </button>
        </div>
      </div>

      {briefing && (
        <div className={styles.gaugeWrap}>
          <BiasGauge
            score={briefing.biasScore}
            label={briefing.biasLabel}
            confidence={briefing.confidence}
          />
        </div>
      )}

      <div className={styles.body}>
        {error && (
          <div className={styles.error}>
            Error: {error}
          </div>
        )}

        {!briefing && !loading && !error && (
          <div className={styles.placeholder}>
            <div className={styles.placeholderTitle}>Ready to generate</div>
            <div className={styles.placeholderSub}>
              Click "Generate Briefing" to get today's AI-synthesised market analysis.
              The briefing reads all loaded data and produces a plain-English directional view with confidence scoring.
            </div>
          </div>
        )}

        {loading && (
          <div className={styles.loadingState}>
            <span className={`${styles.dot} pulse`}>●</span>
            <span className={styles.loadingText}>
              Analysing market data and composing briefing...
            </span>
          </div>
        )}

        {briefing && !loading && (
          <p className={styles.briefingText}>{briefing.briefing}</p>
        )}
      </div>

      {headlines.length > 0 && (
        <div className={styles.headlines}>
          <div className={styles.headlinesLabel}>Market Headlines</div>
          {headlines.map((h, i) => (
            <div key={i} className={styles.headline}>→ {h}</div>
          ))}
        </div>
      )}
    </div>
  )
}
