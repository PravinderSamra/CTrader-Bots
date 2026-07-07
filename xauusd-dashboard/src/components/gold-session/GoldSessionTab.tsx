import { useState, useMemo } from 'react'
import { useGoldSessionIndex, useGoldSession } from '../../hooks/useGoldSessions'
import { BiasGauge } from '../briefing/BiasGauge'
import type { GoldSessionEntry } from '../../types/dashboard'
import styles from './GoldSessionTab.module.css'

// ── Sidebar utilities ────────────────────────────────────────────────────────

function dateLabel(dateStr: string): string {
  const today     = new Date().toISOString().slice(0, 10)
  const yesterday = new Date(Date.now() - 86_400_000).toISOString().slice(0, 10)
  if (dateStr === today)     return 'Today'
  if (dateStr === yesterday) return 'Yesterday'
  try {
    return new Date(`${dateStr}T00:00:00Z`)
      .toLocaleDateString('en-GB', { weekday: 'short', day: 'numeric', month: 'short', timeZone: 'UTC' })
  } catch { return dateStr }
}

function sessionClass(session: string): string {
  if (session === 'LONDON')   return styles.badgeLondon
  if (session === 'NEW_YORK') return styles.badgeNewYork
  if (session === 'OVERLAP')  return styles.badgeOverlap
  return styles.badgeAsian
}

function biasArrow(bias: string) {
  if (bias === 'BULLISH') return <span className={styles.biasUp}>▲</span>
  if (bias === 'BEARISH') return <span className={styles.biasDown}>▼</span>
  return <span className={styles.biasFlat}>–</span>
}

function groupByDate(sessions: GoldSessionEntry[]): [string, GoldSessionEntry[]][] {
  const map = new Map<string, GoldSessionEntry[]>()
  for (const s of sessions) {
    if (!map.has(s.date)) map.set(s.date, [])
    map.get(s.date)!.push(s)
  }
  return [...map.entries()]
}

// ── Price-in-range parser ────────────────────────────────────────────────────

interface PriceInRange { status: string; level: string }

function parsePriceInRange(analysis: string): PriceInRange | null {
  // Extract the full "Current Price vs Equilibrium" line first
  const lineMatch = analysis.match(/Current Price vs Equilibrium[^\n]*/i)
  if (!lineMatch) return null
  const line = lineMatch[0]

  // Match only the known status keywords (stops H1/M5 prefixes returning "H"/"M")
  const statusMatch = line.match(/\b(DISCOUNT|PREMIUM|EQUILIBRIUM|OTE)\b/i)
  if (!statusMatch) return null

  // Extract a price level if present on the same line
  const priceMatch = line.match(/([\$]?[\d,]{4,}(?:\.\d+)?)/i)
  const level = priceMatch ? priceMatch[1].trim() : ''

  return { status: statusMatch[1].toUpperCase(), level }
}

// ── Analysis parser ──────────────────────────────────────────────────────────

interface Section {
  title: string
  body: string
}

interface KVRow {
  label: string
  value: string
  subs: string[]
}

function parseSections(text: string): Section[] {
  const sections: Section[] = []
  let title = ''
  let bodyLines: string[] = []

  for (const line of text.split('\n')) {
    if (line.startsWith('## ')) {
      if (title) sections.push({ title, body: bodyLines.join('\n').trim() })
      title = line.replace(/^##\s+/, '').trim()
      bodyLines = []
    } else if (!line.startsWith('# ')) {
      bodyLines.push(line)
    }
  }
  if (title) sections.push({ title, body: bodyLines.join('\n').trim() })
  return sections
}

function parseKVRows(body: string): KVRow[] {
  const rows: KVRow[] = []
  let current: KVRow | null = null

  for (const line of body.split('\n')) {
    const kvMatch = line.match(/^-\s+\*\*(.+?)\*\*[:\s]*(.*)?$/)
    if (kvMatch) {
      if (current) rows.push(current)
      current = {
        label: kvMatch[1].replace(/:$/, '').trim(),
        value: (kvMatch[2] ?? '').trim(),
        subs: [],
      }
    } else if (line.match(/^\s{2,}\S/) && current) {
      current.subs.push(line.trim())
    }
  }
  if (current) rows.push(current)
  return rows
}

function parseLevelLines(body: string): { price: string; desc: string }[] {
  return body
    .split('\n')
    .filter(l => l.trim().startsWith('- '))
    .map(line => {
      const content = line.replace(/^-\s+/, '').trim()
      const dash = content.indexOf(' — ')
      return dash > -1
        ? { price: content.slice(0, dash).trim(), desc: content.slice(dash + 3).trim() }
        : { price: content, desc: '' }
    })
}

function valueColor(value: string): string | undefined {
  const upper = value.toUpperCase()
  if (/\bBULLISH\b/.test(upper)) return 'var(--green)'
  if (/\bBEARISH\b/.test(upper)) return 'var(--red)'
  if (/\bNEUTRAL\b/.test(upper)) return 'var(--amber)'
  if (/\bTRANSITIONAL\b/.test(upper)) return 'var(--amber)'
  if (/\bACTIVE\b/.test(upper)) return 'var(--green)'
  if (/\bNot applicable\b/i.test(value)) return 'var(--text-dim)'
  if (/\bUNAVAILABLE\b/.test(upper)) return 'var(--text-dim)'
  return undefined
}

// ── Inline bold renderer ─────────────────────────────────────────────────────

function Inline({ text }: { text: string }) {
  const parts = text.split(/(\*\*[^*]+\*\*)/)
  return (
    <>
      {parts.map((part, i) =>
        part.startsWith('**') && part.endsWith('**')
          ? <strong key={i}>{part.slice(2, -2)}</strong>
          : <span key={i}>{part}</span>
      )}
    </>
  )
}

// ── Analysis sub-components ──────────────────────────────────────────────────

function CardTitle({ children }: { children: React.ReactNode }) {
  return <h3 className={styles.cardTitle}>{children}</h3>
}

function KVCard({ title, rows }: { title: string; rows: KVRow[] }) {
  if (rows.length === 0) return null
  return (
    <div className={styles.card}>
      <CardTitle>{title}</CardTitle>
      <div className={styles.kvList}>
        {rows.map((row, i) => {
          if (!row.value && row.subs.length > 0) {
            return (
              <div key={i} className={styles.kvGroupRow}>
                <div className={styles.kvGroupLabel}>{row.label}</div>
                <div className={styles.kvGroupItems}>
                  {row.subs.map((sub, j) => (
                    <div key={j} className={styles.kvGroupItem}>
                      <Inline text={sub} />
                    </div>
                  ))}
                </div>
              </div>
            )
          }
          const color = valueColor(row.value)
          return (
            <div key={i} className={styles.kvRow}>
              <div className={styles.kvLabel}>{row.label}</div>
              <div className={styles.kvValue} style={color ? { color } : undefined}>
                <Inline text={row.value} />
                {row.subs.length > 0 && (
                  <div className={styles.kvSubs}>
                    {row.subs.map((sub, j) => (
                      <div key={j} className={styles.kvSubItem}>
                        <Inline text={sub} />
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

function TradeCard({ body }: { body: string }) {
  const isNoTrade = /NO TRADE/i.test(body.slice(0, 150))
  const dirMatch = body.match(/\*\*Direction:\*\*\s*(LONG|SHORT)/i)
  const direction = dirMatch?.[1]?.toUpperCase()

  const variant = isNoTrade ? 'no-trade' : direction === 'LONG' ? 'long' : direction === 'SHORT' ? 'short' : 'watch'

  const rows = parseKVRows(body)

  const watchIdx = body.indexOf('Watch Level')
  const watchBody = watchIdx > -1 ? body.slice(watchIdx) : ''

  const reasonPara = body
    .split(/\n\n+/)
    .map(p => p.trim())
    .find(p => p.length > 0 && !/\*\*NO TRADE/.test(p) && !/Watch Level/.test(p) && !/PRIMARY WATCH/.test(p) && !/SECONDARY WATCH/.test(p))
    ?? ''

  return (
    <div className={styles.tradeCard} data-variant={variant}>
      <div className={styles.tradeHeader}>
        <CardTitle>Trade Idea</CardTitle>
        <span className={styles.tradeBadge} data-variant={variant}>
          {isNoTrade ? 'No Trade' : direction ?? 'Watch'}
        </span>
      </div>

      {isNoTrade ? (
        <div className={styles.noTradeContent}>
          {reasonPara && (
            <p className={styles.noTradeReason}><Inline text={reasonPara.replace(/\*\*/g, '')} /></p>
          )}
          {watchBody && (
            <details className={styles.watchLevels}>
              <summary className={styles.watchSummary}>Watch Levels</summary>
              <div className={styles.watchBody}>
                {watchBody.split('\n').filter(l => l.trim()).map((line, i) => (
                  <p key={i} className={styles.watchLine}><Inline text={line} /></p>
                ))}
              </div>
            </details>
          )}
        </div>
      ) : (
        <div className={styles.kvList}>
          {rows.map((row, i) => {
            const color = valueColor(row.value)
            return (
              <div key={i} className={styles.kvRow}>
                <div className={styles.kvLabel}>{row.label}</div>
                <div className={styles.kvValue} style={color ? { color } : undefined}>
                  <Inline text={row.value} />
                  {row.subs.length > 0 && (
                    <div className={styles.kvSubs}>
                      {row.subs.map((sub, j) => (
                        <div key={j} className={styles.kvSubItem}><Inline text={sub} /></div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

function ProbCard({ body }: { body: string }) {
  const primaryMatch = body.match(/\*\*Primary Scenario:\s*(\d+)%\*\*\s*[—–]\s*(\w+)/)
  const secondaryMatch = body.match(/\*\*Secondary Scenario:\s*(\d+)%\*\*\s*[—–]\s*(\w+)/)
  const confidenceMatch = body.match(/\*\*Confidence Level:\*\*\s*(\w+)/)
  const invalidationMatch = body.match(/\*\*Key Invalidation Level:\*\*\s*([\$\d,\.–\s]+)/)

  const primaryPct = primaryMatch ? parseInt(primaryMatch[1]) : null
  const primaryBias = primaryMatch ? primaryMatch[2] : null
  const secondaryPct = secondaryMatch ? parseInt(secondaryMatch[1]) : null
  const secondaryBias = secondaryMatch ? secondaryMatch[2] : null
  const confidence = confidenceMatch ? confidenceMatch[1].toUpperCase() : null
  const invalidation = invalidationMatch ? invalidationMatch[1].trim() : null

  const biasColor = (bias: string | null) => {
    if (bias === 'BULLISH') return 'var(--green)'
    if (bias === 'BEARISH') return 'var(--red)'
    return 'var(--amber)'
  }

  const confClass =
    confidence === 'HIGH'   ? styles.confHigh :
    confidence === 'MEDIUM' ? styles.confMed  :
    confidence === 'LOW'    ? styles.confLow  : ''

  return (
    <div className={styles.card}>
      <CardTitle>Probability Assessment</CardTitle>
      <div className={styles.probSection}>
        {primaryPct !== null && (
          <div className={styles.probRow}>
            <div className={styles.probLabel}>
              Primary
              <span className={styles.probBias} style={{ color: biasColor(primaryBias) }}>
                {primaryBias}
              </span>
            </div>
            <div className={styles.probTrack}>
              <div
                className={styles.probFill}
                style={{ width: `${primaryPct}%`, background: biasColor(primaryBias) }}
              />
            </div>
            <div className={styles.probPct} style={{ color: biasColor(primaryBias) }}>
              {primaryPct}%
            </div>
          </div>
        )}
        {secondaryPct !== null && (
          <div className={styles.probRow}>
            <div className={styles.probLabel}>
              Secondary
              <span className={styles.probBias} style={{ color: biasColor(secondaryBias) }}>
                {secondaryBias}
              </span>
            </div>
            <div className={styles.probTrack}>
              <div
                className={styles.probFill}
                style={{ width: `${secondaryPct}%`, background: biasColor(secondaryBias), opacity: 0.7 }}
              />
            </div>
            <div className={styles.probPct} style={{ color: 'var(--text-muted)' }}>
              {secondaryPct}%
            </div>
          </div>
        )}
        {(confidence || invalidation) && (
          <div className={styles.probMeta}>
            {confidence && (
              <span className={`${styles.confBadge} ${confClass}`}>{confidence} CONFIDENCE</span>
            )}
            {invalidation && (
              <span className={styles.invalidation}>
                Invalidation: <code className={styles.invalidationPrice}>{invalidation}</code>
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

function LevelsCard({ body }: { body: string }) {
  const levels = parseLevelLines(body)
  if (levels.length === 0) return null
  return (
    <div className={styles.card}>
      <CardTitle>Key Levels to Watch</CardTitle>
      <div className={styles.levelsGrid}>
        {levels.map((lvl, i) => (
          <div key={i} className={styles.levelRow}>
            <code className={styles.levelPrice}>{lvl.price}</code>
            {lvl.desc && <span className={styles.levelDesc}>{lvl.desc}</span>}
          </div>
        ))}
      </div>
    </div>
  )
}

function Collapsible({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <details className={styles.collapsible}>
      <summary className={styles.collapsibleSummary}>
        <span>{title}</span>
        <span className={styles.collapsibleChevron} aria-hidden />
      </summary>
      <div className={styles.collapsibleBody}>{children}</div>
    </details>
  )
}

function ProseBody({ body }: { body: string }) {
  const rows = parseKVRows(body)
  if (rows.length > 0) {
    return (
      <div className={styles.kvList}>
        {rows.map((row, i) => {
          if (!row.value && row.subs.length > 0) {
            return (
              <div key={i} className={styles.kvGroupRow}>
                <div className={styles.kvGroupLabel}>{row.label}</div>
                <div className={styles.kvGroupItems}>
                  {row.subs.map((sub, j) => (
                    <div key={j} className={styles.kvGroupItem}><Inline text={sub} /></div>
                  ))}
                </div>
              </div>
            )
          }
          const color = valueColor(row.value)
          return (
            <div key={i} className={styles.kvRow}>
              <div className={styles.kvLabel}>{row.label}</div>
              <div className={styles.kvValue} style={color ? { color } : undefined}>
                <Inline text={row.value} />
                {row.subs.length > 0 && (
                  <div className={styles.kvSubs}>
                    {row.subs.map((sub, j) => (
                      <div key={j} className={styles.kvSubItem}><Inline text={sub} /></div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>
    )
  }
  return (
    <div className={styles.prose}>
      {body.split(/\n\n+/).map((para, i) => (
        <p key={i}><Inline text={para.trim()} /></p>
      ))}
    </div>
  )
}

function AnalysisRenderer({ analysis }: { analysis: string }) {
  const sections = useMemo(() => parseSections(analysis), [analysis])

  if (sections.length < 2) {
    return <pre className={styles.analysisText}>{analysis}</pre>
  }

  const find = (keyword: string) =>
    sections.find(s => s.title.toUpperCase().includes(keyword.toUpperCase()))

  const accountCtx  = find('ACCOUNT CONTEXT')
  const regime      = find('REGIME ASSESSMENT')
  const structure   = find('STRUCTURE')
  const liquidity   = find('LIQUIDITY MAP')
  const pdArrays    = find('KEY PD ARRAYS')
  const tradeIdea   = find('TRADE IDEA')
  const probability = find('PROBABILITY')
  const keyLevels   = find('KEY LEVELS')
  // macroRegime, sessionCtx, crossCheck handled via collapsibleSections filter below
  const narrative   = find('MARKET NARRATIVE')

  const collapsibleSections = sections.filter(s => {
    const t = s.title.toUpperCase()
    return (
      t.includes('MACRO REGIME') ||
      t.includes('SESSION CONTEXT') ||
      t.includes('CROSS-CHECK')
    )
  })

  return (
    <div className={styles.analysisGrid}>
      {/* Primary 2-col: Account + Regime */}
      {(accountCtx || regime) && (
        <div className={styles.primaryGrid}>
          {accountCtx && (
            <KVCard title="Account Context" rows={parseKVRows(accountCtx.body)} />
          )}
          {regime && (
            <KVCard title="Regime Assessment" rows={parseKVRows(regime.body)} />
          )}
        </div>
      )}

      {/* Structure */}
      {structure && (
        <KVCard title="Structure" rows={parseKVRows(structure.body)} />
      )}

      {/* Liquidity Map */}
      {liquidity && (
        <KVCard title="Liquidity Map" rows={parseKVRows(liquidity.body)} />
      )}

      {/* Key PD Arrays */}
      {pdArrays && (
        <KVCard title="Key PD Arrays" rows={parseKVRows(pdArrays.body)} />
      )}

      {/* Trade Idea */}
      {tradeIdea && <TradeCard body={tradeIdea.body} />}

      {/* Probability */}
      {probability && <ProbCard body={probability.body} />}

      {/* Key Levels */}
      {keyLevels && <LevelsCard body={keyLevels.body} />}

      {/* Collapsible secondaries */}
      {collapsibleSections.map(sec => (
        <Collapsible key={sec.title} title={sec.title}>
          <ProseBody body={sec.body} />
        </Collapsible>
      ))}

      {/* Market Narrative */}
      {narrative && (
        <Collapsible title="Market Narrative">
          <p className={styles.narrativeText}>
            <Inline text={narrative.body.replace(/\[DISCLAIMER[^\]]*\]/g, '').trim()} />
          </p>
          <p className={styles.disclaimer}>
            For informational and educational purposes only. Not financial advice.
          </p>
        </Collapsible>
      )}

      {/* Any remaining sections not handled above */}
      {sections
        .filter(s => {
          const t = s.title.toUpperCase()
          return (
            !t.includes('ACCOUNT CONTEXT') &&
            !t.includes('REGIME ASSESSMENT') &&
            !t.includes('STRUCTURE') &&
            !t.includes('LIQUIDITY MAP') &&
            !t.includes('KEY PD ARRAYS') &&
            !t.includes('TRADE IDEA') &&
            !t.includes('PROBABILITY') &&
            !t.includes('KEY LEVELS') &&
            !t.includes('MACRO REGIME') &&
            !t.includes('SESSION CONTEXT') &&
            !t.includes('CROSS-CHECK') &&
            !t.includes('MARKET NARRATIVE')
          )
        })
        .map(sec => (
          <Collapsible key={sec.title} title={sec.title}>
            <ProseBody body={sec.body} />
          </Collapsible>
        ))}
    </div>
  )
}

// ── Main tab ─────────────────────────────────────────────────────────────────

export function GoldSessionTab() {
  const { index, loading: indexLoading } = useGoldSessionIndex()
  const [selectedFilename, setSelectedFilename] = useState<string | null>(null)

  const sessions   = index?.sessions ?? []
  const activeFile = selectedFilename ?? sessions[0]?.filename ?? null
  const { session, loading: sessionLoading } = useGoldSession(activeFile)

  const grouped = groupByDate(sessions)

  return (
    <div className={styles.tab}>
      {/* ── Sidebar ── */}
      <aside className={styles.sidebar}>
        <div className={styles.sidebarTitle}>Session History</div>

        {indexLoading && <div className={styles.sidebarEmpty}>Loading…</div>}

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
                <span className={styles.entryTime}>{s.time}</span>
                <span className={`${styles.entryBadge} ${sessionClass(s.session)}`}>
                  {s.session.replace('_', ' ')}
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
            <div className={styles.emptyIcon}>◈</div>
            <div className={styles.emptyTitle}>Gold-Session AI</div>
            <div className={styles.emptySub}>
              Run <code>/gold-session</code> in Claude Code to generate a full ICT/SMC
              intraday brief. Each analysis is saved here automatically with a
              rolling 3-day history.
            </div>
          </div>
        )}

        {sessionLoading && (
          <div className={styles.viewLoading}>
            <span className="pulse">Loading session…</span>
          </div>
        )}

        {session && !sessionLoading && (
          <div className={styles.sessionView}>
            {/* Header row */}
            <div className={styles.viewHeader}>
              <span className={`${styles.viewBadge} ${sessionClass(session.session)}`}>
                {session.session.replace('_', ' ')}
              </span>
              <span className={styles.viewDate}>{dateLabel(session.date)}</span>
              <span className={styles.viewTime}>{session.time}</span>
            </div>

            {/* Gauge + stats */}
            <div
              className={styles.gaugeRow}
              data-bias={session.bias}
            >
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
                  <div
                    className={styles.statValue}
                    style={{
                      color: session.probability >= 65 ? 'var(--green)'
                           : session.probability <= 40 ? 'var(--red)'
                           : 'var(--text)'
                    }}
                  >
                    {session.probability}%
                  </div>
                </div>
                <div className={styles.statPill}>
                  <div className={styles.statLabel}>Confidence</div>
                  <div className={styles.statValue}>{session.confidence}<span className={styles.statDenom}>/10</span></div>
                </div>
                {(() => {
                  const pir = parsePriceInRange(session.analysis)
                  if (!pir) return null
                  const cls = pir.status === 'DISCOUNT' ? styles.pirDiscount
                    : pir.status === 'PREMIUM' ? styles.pirPremium
                    : pir.status === 'OTE' ? styles.pirOte
                    : styles.pirEquilibrium
                  return (
                    <div className={styles.statPill}>
                      <div className={styles.statLabel}>Price Zone</div>
                      <div className={`${styles.pirBadge} ${cls}`}>
                        {pir.status}
                        {pir.level && <span className={styles.pirLevel}>{pir.level}</span>}
                      </div>
                    </div>
                  )
                })()}
              </div>
            </div>

            {/* Structured analysis */}
            <AnalysisRenderer analysis={session.analysis} />
          </div>
        )}
      </div>
    </div>
  )
}
