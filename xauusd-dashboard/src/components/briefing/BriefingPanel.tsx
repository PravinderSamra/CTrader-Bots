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

function recencyClass(hoursAgo: number): string {
  if (hoursAgo < 2)  return styles.dotFresh
  if (hoursAgo < 8)  return styles.dotRecent
  return styles.dotOld
}

function sourceClass(source: string): string {
  const s = source.toLowerCase()
  if (s.includes('fed') || s.includes('fomc') || s.includes('reserve')) return styles.srcFed
  if (s.includes('treasury') || s.includes('ecb') || s.includes('boe') || s.includes('central')) return styles.srcCentral
  if (s.includes('geo') || s.includes('sanction') || s.includes('war') || s.includes('conflict')) return styles.srcGeo
  return styles.srcDefault
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
        <div className={styles.catalysts}>
          <div className={styles.catalystsLabel}>Recent Catalysts — last 24h</div>
          <div className={styles.timeline}>
            {newsItems.map((n, i) => (
              <div key={i} className={styles.tlItem}>
                <div className={styles.tlTrack}>
                  <div className={`${styles.tlDot} ${recencyClass(n.hoursAgo)}`} />
                  {i < newsItems.length - 1 && <div className={styles.tlLine} />}
                </div>
                <div className={styles.tlContent}>
                  <span className={styles.tlHeadline}>{n.headline}</span>
                  <div className={styles.tlMeta}>
                    {n.hoursAgo < 999 && <span className={styles.tlTime}>{fmtHoursAgo(n.hoursAgo)}</span>}
                    <span className={`${styles.tlSource} ${sourceClass(n.source)}`}>{n.source}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
