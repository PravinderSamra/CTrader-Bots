import type { BriefingResult, NewsItem } from '../../types/dashboard'
import { BiasGauge } from './BiasGauge'
import styles from './BriefingPanel.module.css'

function fmtTime(iso: string): string {
  if (!iso) return ''
  try {
    const d = new Date(iso)
    return `${String(d.getUTCHours()).padStart(2,'0')}:${String(d.getUTCMinutes()).padStart(2,'0')} GMT`
  } catch { return iso }
}

function fmtHoursAgo(hoursAgo: number): string {
  if (hoursAgo >= 999) return ''
  if (hoursAgo < 1) return `${Math.round(hoursAgo * 60)}m ago`
  return `${hoursAgo.toFixed(1)}h ago`
}

interface Props {
  briefing: BriefingResult | null
  newsItems: NewsItem[]
}

export function BriefingPanel({ briefing, newsItems }: Props) {
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
              The briefing is regenerated hourly by the data-fetch workflow (06:00–20:00 GMT, Mon–Fri).
              Check back after the next scheduled run.
            </div>
          </div>
        )}

        {briefing && (
          <p className={styles.briefingText}>{briefing.briefing}</p>
        )}
      </div>

      {newsItems.length > 0 && (
        <div className={styles.headlines}>
          <div className={styles.headlinesLabel}>Recent Catalysts (last 24h)</div>
          {newsItems.map((n, i) => (
            <div key={i} className={styles.headline}>
              → {n.headline}
              {n.hoursAgo < 999 && (
                <span className={styles.headlineMeta}> · {fmtHoursAgo(n.hoursAgo)} · {n.source}</span>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
