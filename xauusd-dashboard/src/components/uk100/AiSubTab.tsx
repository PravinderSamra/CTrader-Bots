import { useState, useMemo } from 'react'
import { useUk100SessionIndex, useUk100Session, useUk100SessionOutcomes } from '../../hooks/useUk100Sessions'
import { BiasGauge } from '../briefing/BiasGauge'
import { OrbPlaybookCard } from './OrbPlaybookCard'
import { TldrCard } from './TldrCard'
import { synthesizeTldr } from './tldr'
import type { Uk100SessionEntry, Uk100SessionRecord } from '../../types/uk100'
import type { OutcomeRow, SessionResult } from '../../types/dashboard'
import {
  parsePriceInRange, parseSections, parseKVRows, parseLevelLines, valueColor, parseProbability,
  type PriceInRange, type KVRow,
} from '../gold-session/parsers'
// Reuse the gold-session tab's visual system (cards/KV rows/sidebar/prose) —
// it's a generic markdown-brief renderer, not gold-specific. A dedicated
// stylesheet would duplicate ~150 classes for no visual difference.
import styles from '../gold-session/GoldSessionTab.module.css'

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

function biasArrow(bias: string) {
  if (bias === 'BULLISH') return <span className={styles.biasUp}>▲</span>
  if (bias === 'BEARISH') return <span className={styles.biasDown}>▼</span>
  return <span className={styles.biasFlat}>–</span>
}

// ── Outcome glyph + track-record stats (C3, UK100-V2-PLAN.md §5 Phase C3) ──
// Mirrors GoldSessionTab.tsx's OutcomeGlyph/TrackRecord exactly (copied, not
// exported/shared, per the plan — consolidation is a later phase), with one
// UK100-specific change: the breakdown groups by `orbDirection`
// (LONG_ONLY/SHORT_ONLY/BOTH_OK) instead of `bias` — UK100's bias label is
// frequently NEUTRAL even on a genuine ORB-playbook call (see
// resolve-uk100-sessions.ts's file header), so a bias-only breakdown would
// silently drop most rows; orbDirection is always populated on a scored call.

function OutcomeGlyph({ result }: { result?: SessionResult }) {
  if (!result || result === 'NO_CALL') return null
  if (result === 'WIN')  return <span className={styles.outWin} title="Target hit before invalidation">✓</span>
  if (result === 'LOSS') return <span className={styles.outLoss} title="Invalidation hit first">✗</span>
  return <span className={styles.outExpired} title={`Expired: ${result.replace('EXPIRED_', '').toLowerCase()}`}>○</span>
}

interface TrackStats {
  decided: number
  wins: number
  winRate: number | null
  avgProbability: number | null
  byOrbDirection: { direction: string; decided: number; winRate: number }[]
}

function computeTrackStats(outcomes: OutcomeRow[]): TrackStats {
  // Most recent 30 scored (exclude NO_CALL); win rate over WIN/LOSS only.
  const scored = outcomes
    .filter(o => o.result !== 'NO_CALL')
    .sort((a, b) => b.resolvedAt.localeCompare(a.resolvedAt))
    .slice(0, 30)

  const decidedRows = scored.filter(o => o.result === 'WIN' || o.result === 'LOSS')
  const wins = decidedRows.filter(o => o.result === 'WIN').length
  const decided = decidedRows.length
  const winRate = decided > 0 ? Math.round((wins / decided) * 100) : null
  const avgProbability = decided > 0
    ? Math.round(decidedRows.reduce((s, o) => s + o.probability, 0) / decided)
    : null

  const byOrbDirection = (['LONG_ONLY', 'SHORT_ONLY', 'BOTH_OK'] as const).map(direction => {
    const rows = decidedRows.filter(o => o.orbDirection === direction)
    const w = rows.filter(o => o.result === 'WIN').length
    return { direction, decided: rows.length, winRate: rows.length > 0 ? Math.round((w / rows.length) * 100) : 0 }
  }).filter(b => b.decided > 0)

  return { decided, wins, winRate, avgProbability, byOrbDirection }
}

function orbDirectionLabel(d: string): string {
  if (d === 'LONG_ONLY') return 'Long-only'
  if (d === 'SHORT_ONLY') return 'Short-only'
  if (d === 'BOTH_OK') return 'Both-OK'
  return d
}

function TrackRecord({ outcomes }: { outcomes: OutcomeRow[] }) {
  const stats = computeTrackStats(outcomes)
  if (stats.decided === 0) return null

  const edge = stats.winRate != null && stats.avgProbability != null
    ? stats.winRate - stats.avgProbability
    : null

  return (
    <div className={styles.trackCard}>
      <div className={styles.trackTitle}>Track Record · last {stats.decided}</div>
      <div className={styles.trackHeadline}>
        <span className={styles.trackCalled}>Called {stats.avgProbability}%</span>
        <span className={styles.trackDot}>·</span>
        <span className={stats.winRate! >= 50 ? styles.trackHitGood : styles.trackHitBad}>
          Hit {stats.winRate}%
        </span>
      </div>
      {edge != null && (
        <div className={styles.trackEdge}>
          {edge >= 0 ? 'Calibrated / beating' : 'Below'} its own probability by {Math.abs(edge)}pts
        </div>
      )}
      {stats.byOrbDirection.length > 0 && (
        <div className={styles.trackBias}>
          {stats.byOrbDirection.map(b => (
            <div key={b.direction} className={styles.trackBiasRow}>
              <span className={styles.trackBiasLabel}>{orbDirectionLabel(b.direction)}</span>
              <span className={styles.trackBiasVal}>{b.winRate}%</span>
              <span className={styles.trackBiasN}>({b.decided})</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function groupByDate(sessions: Uk100SessionEntry[]): [string, Uk100SessionEntry[]][] {
  const map = new Map<string, Uk100SessionEntry[]>()
  for (const s of sessions) {
    if (!map.has(s.date)) map.set(s.date, [])
    map.get(s.date)!.push(s)
  }
  return [...map.entries()]
}

function resolvePriceZone(session: Uk100SessionRecord): PriceInRange | null {
  if (session.priceZone) {
    return {
      status: session.priceZone,
      level: session.equilibrium != null ? String(session.equilibrium) : '',
    }
  }
  return parsePriceInRange(session.analysis)
}

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
    </div>
  )
}

function ProbCard({ body }: { body: string }) {
  const { primaryPct, primaryBias, secondaryPct, secondaryBias, confidence, invalidation } = parseProbability(body)

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
              <span className={styles.probBias} style={{ color: biasColor(primaryBias) }}>{primaryBias}</span>
            </div>
            <div className={styles.probTrack}>
              <div className={styles.probFill} style={{ width: `${primaryPct}%`, background: biasColor(primaryBias) }} />
            </div>
            <div className={styles.probPct} style={{ color: biasColor(primaryBias) }}>{primaryPct}%</div>
          </div>
        )}
        {secondaryPct !== null && (
          <div className={styles.probRow}>
            <div className={styles.probLabel}>
              Secondary
              <span className={styles.probBias} style={{ color: biasColor(secondaryBias) }}>{secondaryBias}</span>
            </div>
            <div className={styles.probTrack}>
              <div className={styles.probFill} style={{ width: `${secondaryPct}%`, background: biasColor(secondaryBias), opacity: 0.7 }} />
            </div>
            <div className={styles.probPct} style={{ color: 'var(--text-muted)' }}>{secondaryPct}%</div>
          </div>
        )}
        {(confidence || invalidation) && (
          <div className={styles.probMeta}>
            {confidence && <span className={`${styles.confBadge} ${confClass}`}>{confidence} CONFIDENCE</span>}
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
        {levels.map((lvl, i) => {
          const isProse = lvl.desc === '' && /\*\*/.test(lvl.price)
          if (isProse) return <p key={i} className={styles.levelProse}><Inline text={lvl.price} /></p>
          return (
            <div key={i} className={styles.levelRow}>
              <code className={styles.levelPrice}><Inline text={lvl.price} /></code>
              {lvl.desc && <span className={styles.levelDesc}><Inline text={lvl.desc} /></span>}
            </div>
          )
        })}
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
      {body.split(/\n\n+/).map((para, i) => <p key={i}><Inline text={para.trim()} /></p>)}
    </div>
  )
}

function TradeCard({ body, structured }: { body: string; structured?: Uk100SessionRecord['tradeIdea'] }) {
  const isNoTrade = structured ? structured.status === 'NO_TRADE' : /NO TRADE/i.test(body.slice(0, 150))
  const dirMatch = body.match(/\*\*Direction:\*\*\s*(LONG|SHORT)/i)
  const direction = structured && structured.status !== 'NO_TRADE' ? structured.direction : dirMatch?.[1]?.toUpperCase()

  const variant = structured
    ? (structured.status === 'NO_TRADE' ? 'no-trade' : structured.status === 'WAIT' ? 'watch' : structured.direction === 'LONG' ? 'long' : 'short')
    : (isNoTrade ? 'no-trade' : direction === 'LONG' ? 'long' : direction === 'SHORT' ? 'short' : 'watch')

  const badgeText = isNoTrade ? 'No Trade' : structured ? (structured.status === 'WAIT' ? 'Watch' : structured.direction) : (direction ?? 'Watch')

  const rows = parseKVRows(body)
  const reasonPara = body
    .split(/\n\n+/)
    .map(p => p.trim())
    .find(p => p.length > 0 && !/\*\*NO TRADE/.test(p))
    ?? ''

  return (
    <div className={styles.tradeCard} data-variant={variant}>
      <div className={styles.tradeHeader}>
        <CardTitle>Trade Idea</CardTitle>
        <span className={styles.tradeBadge} data-variant={variant}>{badgeText}</span>
      </div>
      {isNoTrade ? (
        reasonPara && <p className={styles.noTradeReason}><Inline text={reasonPara.replace(/\*\*/g, '')} /></p>
      ) : (
        <div className={styles.kvList}>
          {rows.map((row, i) => {
            const color = valueColor(row.value)
            return (
              <div key={i} className={styles.kvRow}>
                <div className={styles.kvLabel}>{row.label}</div>
                <div className={styles.kvValue} style={color ? { color } : undefined}><Inline text={row.value} /></div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

function AnalysisRenderer({ session }: { session: Uk100SessionRecord }) {
  const analysis = session.analysis
  const sections = useMemo(() => parseSections(analysis), [analysis])

  if (sections.length < 2) {
    return <pre className={styles.analysisText}>{analysis}</pre>
  }

  const find = (keyword: string) => sections.find(s => s.title.toUpperCase().includes(keyword.toUpperCase()))

  const accountCtx  = find('ACCOUNT CONTEXT')
  const regime      = find('REGIME ASSESSMENT')
  const structure   = find('STRUCTURE')
  const liquidity   = find('LIQUIDITY MAP')
  const pdArrays    = find('KEY PD ARRAYS')
  const tradeIdea   = find('TRADE IDEA')
  const probability = find('PROBABILITY')
  const keyLevels   = find('KEY LEVELS')
  const narrative   = find('MARKET NARRATIVE')
  // ORB PLAYBOOK is rendered structurally via OrbPlaybookCard above, from
  // session.orbPlaybook — skip its raw text section here to avoid duplication.

  const collapsibleSections = sections.filter(s => {
    const t = s.title.toUpperCase()
    return t.includes('MACRO REGIME') || t.includes('SESSION CONTEXT') || t.includes('CROSS-CHECK')
  })

  return (
    <div className={styles.analysisGrid}>
      {(accountCtx || regime) && (
        <div className={styles.primaryGrid}>
          {accountCtx && <KVCard title="Account Context" rows={parseKVRows(accountCtx.body)} />}
          {regime && <KVCard title="Regime Assessment" rows={parseKVRows(regime.body)} />}
        </div>
      )}

      {structure && <KVCard title="Structure" rows={parseKVRows(structure.body)} />}
      {liquidity && <KVCard title="Liquidity Map" rows={parseKVRows(liquidity.body)} />}
      {pdArrays && <KVCard title="Key PD Arrays" rows={parseKVRows(pdArrays.body)} />}

      {(tradeIdea || session.tradeIdea) && (
        <TradeCard body={tradeIdea?.body ?? ''} structured={session.tradeIdea} />
      )}

      {probability && <ProbCard body={probability.body} />}
      {keyLevels && <LevelsCard body={keyLevels.body} />}

      {collapsibleSections.map(sec => (
        <Collapsible key={sec.title} title={sec.title}>
          <ProseBody body={sec.body} />
        </Collapsible>
      ))}

      {narrative && (
        <Collapsible title="Market Narrative">
          <p className={styles.narrativeText}><Inline text={narrative.body.trim()} /></p>
          <p className={styles.disclaimer}>For informational and educational purposes only. Not financial advice.</p>
        </Collapsible>
      )}

      {sections
        .filter(s => {
          const t = s.title.toUpperCase()
          return (
            !t.includes('ACCOUNT CONTEXT') && !t.includes('REGIME ASSESSMENT') && !t.includes('STRUCTURE') &&
            !t.includes('LIQUIDITY MAP') && !t.includes('KEY PD ARRAYS') && !t.includes('TRADE IDEA') &&
            !t.includes('PROBABILITY') && !t.includes('KEY LEVELS') && !t.includes('MACRO REGIME') &&
            !t.includes('SESSION CONTEXT') && !t.includes('CROSS-CHECK') && !t.includes('MARKET NARRATIVE') &&
            !t.includes('ORB PLAYBOOK')
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

export function AiSubTab() {
  const { index, loading: indexLoading } = useUk100SessionIndex()
  const { byFilename: outcomeByFile, outcomes } = useUk100SessionOutcomes()
  const [selectedFilename, setSelectedFilename] = useState<string | null>(null)

  const sessions   = index?.sessions ?? []
  const activeFile = selectedFilename ?? sessions[0]?.filename ?? null
  const { session, loading: sessionLoading } = useUk100Session(activeFile)

  const grouped = groupByDate(sessions)

  return (
    <div className={styles.tab}>
      <aside className={styles.sidebar}>
        <div className={styles.sidebarTitle}>UK100 Session History</div>

        {indexLoading && <div className={styles.sidebarEmpty}>Loading…</div>}

        {!indexLoading && sessions.length === 0 && (
          <div className={styles.sidebarEmpty}>
            No sessions yet.<br />
            Run /uk100-session to generate your first analysis.
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
                <span className={`${styles.entryBadge} ${styles.badgeLondon}`}>{s.session}</span>
                {biasArrow(s.bias)}
                <OutcomeGlyph result={outcomeByFile.get(s.filename)?.result} />
              </button>
            ))}
          </div>
        ))}

        <TrackRecord outcomes={outcomes} />
      </aside>

      <div className={styles.view}>
        {!activeFile && !indexLoading && (
          <div className={styles.emptyState}>
            <div className={styles.emptyIcon}>◈</div>
            <div className={styles.emptyTitle}>UK100 AI Session</div>
            <div className={styles.emptySub}>
              Run <code>/uk100-session</code> in Claude Code to generate a full ICT/SMC
              ORB-playbook brief. Each analysis is saved here automatically with a
              rolling 3-day history.
            </div>
          </div>
        )}

        {sessionLoading && (
          <div className={styles.viewLoading}><span className="pulse">Loading session…</span></div>
        )}

        {session && !sessionLoading && (
          <div className={styles.sessionView}>
            <div className={styles.viewHeader}>
              <span className={`${styles.viewBadge} ${styles.badgeLondon}`}>{session.session}</span>
              <span className={styles.viewDate}>{dateLabel(session.date)}</span>
              <span className={styles.viewTime}>{session.time}</span>
            </div>

            {(() => {
              const bullets = synthesizeTldr(session)
              return bullets.length > 0 ? <TldrCard bullets={bullets} /> : null
            })()}

            <div className={styles.gaugeRow} data-bias={session.bias}>
              <div className={styles.gaugeWrap}>
                <BiasGauge
                  score={session.biasScore}
                  label={session.bias as 'BULLISH' | 'NEUTRAL' | 'BEARISH'}
                  confidence={session.confidence}
                  max={10}
                />
              </div>
              <div className={styles.statPills}>
                <div className={styles.statPill}>
                  <div className={styles.statLabel}>Probability</div>
                  <div
                    className={styles.statValue}
                    style={{ color: session.probability >= 65 ? 'var(--green)' : session.probability <= 40 ? 'var(--red)' : 'var(--text)' }}
                  >
                    {session.probability}%
                  </div>
                </div>
                <div className={styles.statPill}>
                  <div className={styles.statLabel}>Confidence</div>
                  <div className={styles.statValue}>{session.confidence}<span className={styles.statDenom}>/10</span></div>
                </div>
                {(() => {
                  const pir = resolvePriceZone(session)
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

            {session.orbPlaybook && <OrbPlaybookCard playbook={session.orbPlaybook} />}

            <AnalysisRenderer session={session} />
          </div>
        )}
      </div>
    </div>
  )
}
