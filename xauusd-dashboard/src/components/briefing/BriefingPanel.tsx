import type { BriefingResult } from '../../types/dashboard'
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
  briefing: BriefingResult | null
  headlines: string[]
}

export function BriefingPanel({ briefing, headlines }: Props) {
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
        {!briefing && (
          <div className={styles.placeholder}>
            <div className={styles.placeholderTitle}>Briefing not yet available</div>
            <div className={styles.placeholderSub}>
              The daily briefing is generated once per day by the data-fetch workflow (06:45 GMT, Mon–Fri).
              Check back after the next scheduled run.
            </div>
          </div>
        )}

        {briefing && (
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
