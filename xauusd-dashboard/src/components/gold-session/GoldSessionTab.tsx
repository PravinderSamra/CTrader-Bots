import { useState } from 'react'
import { useGoldSessionIndex, useGoldSession } from '../../hooks/useGoldSessions'
import { BiasGauge } from '../briefing/BiasGauge'
import type { GoldSessionEntry } from '../../types/dashboard'
import styles from './GoldSessionTab.module.css'

function dateLabel(dateStr: string): string {
  const today     = new Date().toISOString().slice(0, 10)
  const yesterday = new Date(Date.now() - 86_400_000).toISOString().slice(0, 10)
  if (dateStr === today)     return 'TODAY'
  if (dateStr === yesterday) return 'YESTERDAY'
  try {
    return new Date(`${dateStr}T00:00:00Z`)
      .toLocaleDateString('en-GB', { weekday: 'short', day: 'numeric', month: 'short', timeZone: 'UTC' })
      .toUpperCase()
  } catch { return dateStr }
}

function biasArrow(bias: string) {
  if (bias === 'BULLISH') return <span className={styles.biasUp}>▲</span>
  if (bias === 'BEARISH') return <span className={styles.biasDown}>▼</span>
  return <span className={styles.biasFlat}>–</span>
}

function sessionClass(session: string): string {
  if (session === 'LONDON')   return styles.badgeLondon
  if (session === 'NEW_YORK') return styles.badgeNewYork
  if (session === 'OVERLAP')  return styles.badgeOverlap
  return styles.badgeAsian
}

function groupByDate(sessions: GoldSessionEntry[]): [string, GoldSessionEntry[]][] {
  const map = new Map<string, GoldSessionEntry[]>()
  for (const s of sessions) {
    if (!map.has(s.date)) map.set(s.date, [])
    map.get(s.date)!.push(s)
  }
  return [...map.entries()]
}

export function GoldSessionTab() {
  const { index, loading: indexLoading } = useGoldSessionIndex()
  const [selectedFilename, setSelectedFilename] = useState<string | null>(null)

  const sessions      = index?.sessions ?? []
  const activeFile    = selectedFilename ?? sessions[0]?.filename ?? null
  const { session, loading: sessionLoading } = useGoldSession(activeFile)

  const grouped = groupByDate(sessions)

  return (
    <div className={styles.tab}>
      {/* ── Sidebar ── */}
      <aside className={styles.sidebar}>
        <div className={styles.sidebarTitle}>Session History</div>

        {indexLoading && (
          <div className={styles.sidebarEmpty}>Loading…</div>
        )}

        {!indexLoading && sessions.length === 0 && (
          <div className={styles.sidebarEmpty}>
            No sessions yet.<br />
            Run /gold-session to generate your first analysis.
          </div>
        )}

        {grouped.map(([date, entries]) => (
          <div key={date} className={styles.dateGroup}>
            <div className={styles.dateHeader}>{dateLabel(date)}</div>
            {entries.map(s => (
              <button
                key={s.filename}
                className={`${styles.entry} ${activeFile === s.filename ? styles.entryActive : ''}`}
                onClick={() => setSelectedFilename(s.filename)}
              >
                <span className={styles.entryTime}>{s.time} GMT</span>
                <span className={`${styles.entryBadge} ${sessionClass(s.session)}`}>
                  {s.session.replace('_', ' ')}
                </span>
                {biasArrow(s.bias)}
              </button>
            ))}
          </div>
        ))}
      </aside>

      {/* ── Main view ── */}
      <div className={styles.view}>
        {!activeFile && !indexLoading && (
          <div className={styles.emptyState}>
            <div className={styles.emptyTitle}>Gold-Session AI</div>
            <div className={styles.emptySub}>
              Run <code>/gold-session</code> in Claude Code to generate a full ICT/SMC
              intraday brief. Each analysis is saved here automatically with a
              rolling 3-day history.
            </div>
          </div>
        )}

        {sessionLoading && (
          <div className={styles.viewLoading}>Loading session…</div>
        )}

        {session && !sessionLoading && (
          <div className={styles.sessionView}>
            {/* Header row */}
            <div className={styles.viewHeader}>
              <span className={`${styles.viewBadge} ${sessionClass(session.session)}`}>
                {session.session.replace('_', ' ')}
              </span>
              <span className={styles.viewDate}>{dateLabel(session.date)}</span>
              <span className={styles.viewTime}>{session.time} GMT</span>
            </div>

            {/* Gauge + stats */}
            <div className={styles.gaugeRow}>
              <div className={styles.gaugeWrap}>
                <BiasGauge
                  score={session.biasScore}
                  label={session.bias as 'BULLISH' | 'NEUTRAL' | 'BEARISH'}
                  confidence={session.confidence}
                />
              </div>
              <div className={styles.statPills}>
                <div className={styles.statPill}>
                  <div className={styles.statLabel}>Probability</div>
                  <div className={styles.statValue}>{session.probability}%</div>
                </div>
                <div className={styles.statPill}>
                  <div className={styles.statLabel}>Confidence</div>
                  <div className={styles.statValue}>{session.confidence}/10</div>
                </div>
              </div>
            </div>

            <div className={styles.divider} />

            {/* Full analysis */}
            <pre className={styles.analysisText}>{session.analysis}</pre>
          </div>
        )}
      </div>
    </div>
  )
}
