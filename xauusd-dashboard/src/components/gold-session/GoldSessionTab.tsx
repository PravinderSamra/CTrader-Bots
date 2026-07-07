import { useState, useMemo } from 'react'
import { useGoldSessionIndex, useGoldSession, useSessionOutcomes } from '../../hooks/useGoldSessions'
import { BiasGauge } from '../briefing/BiasGauge'
import { EventCountdown } from '../common/EventCountdown'
import { LiquidityRuler } from './LiquidityRuler'
import type { GoldSessionEntry, GoldSessionRecord, StructuredTradeIdea, OutcomeRow, SessionResult } from '../../types/dashboard'
import {
  parsePriceInRange, parseSections, parseKVRows, parseLevelLines, valueColor, parseProbability,
  type PriceInRange, type KVRow,
} from './parsers'
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

// ── Outcome glyph + track-record stats ───────────────────────────────────────

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
  byBias: { bias: string; decided: number; winRate: number }[]
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

  const byBias = (['BULLISH', 'BEARISH'] as const).map(bias => {
    const rows = decidedRows.filter(o => o.bias === bias)
    const w = rows.filter(o => o.result === 'WIN').length
    return { bias, decided: rows.length, winRate: rows.length > 0 ? Math.round((w / rows.length) * 100) : 0 }
  }).filter(b => b.decided > 0)

  return { decided, wins, winRate, avgProbability, byBias }
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
      {stats.byBias.length > 0 && (
        <div className={styles.trackBias}>
          {stats.byBias.map(b => (
            <div key={b.bias} className={styles.trackBiasRow}>
              <span className={b.bias === 'BULLISH' ? styles.biasUp : styles.biasDown}>
                {b.bias === 'BULLISH' ? '▲' : '▼'}
              </span>
              <span className={styles.trackBiasLabel}>{b.bias === 'BULLISH' ? 'Long' : 'Short'}</span>
              <span className={styles.trackBiasVal}>{b.winRate}%</span>
              <span className={styles.trackBiasN}>({b.decided})</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function groupByDate(sessions: GoldSessionEntry[]): [string, GoldSessionEntry[]][] {
  const map = new Map<string, GoldSessionEntry[]>()
  for (const s of sessions) {
    if (!map.has(s.date)) map.set(s.date, [])
    map.get(s.date)!.push(s)
  }
  return [...map.entries()]
}

// ── Structured-or-regex resolvers (Phase 2: prefer meta fields, fall back to text) ──

function resolvePriceZone(session: GoldSessionRecord): PriceInRange | null {
  if (session.priceZone) {
    return {
      status: session.priceZone,
      level: session.equilibrium != null ? String(session.equilibrium) : '',
    }
  }
  return parsePriceInRange(session.analysis)
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

function RRBar({ idea }: { idea: StructuredTradeIdea }) {
  const entry = idea.entryLow != null && idea.entryHigh != null
    ? (idea.entryLow + idea.entryHigh) / 2
    : (idea.entryLow ?? idea.entryHigh ?? null)
  if (entry == null || idea.stop == null || !idea.targets || idea.targets.length === 0) return null

  const stop = idea.stop
  const risk = Math.abs(entry - stop)
  if (risk <= 0) return null

  const targets = [...idea.targets].sort((a, b) =>
    idea.direction === 'LONG' ? a - b : b - a)   // nearest first
  const rewards = targets.map(t => Math.abs(t - entry))
  const maxReward = Math.max(...rewards)
  const total = risk + maxReward

  const W = 320, padX = 2
  const usable = W - 2 * padX
  const redW = (risk / total) * usable
  const greenW = (maxReward / total) * usable
  const entryX = padX + redW

  const fmt = (p: number) => p.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

  return (
    <div className={styles.rrWrap}>
      <svg viewBox={`0 0 ${W} 50`} className={styles.rrSvg} role="img" aria-label="Risk-reward">
        {/* risk (red) + reward (green) spans */}
        <rect x={padX} y={22} width={redW} height={8} rx={2} className={styles.rrRisk} />
        <rect x={entryX} y={22} width={greenW} height={8} rx={2} className={styles.rrReward} />

        {/* stop marker — price + SL label sit BELOW the bar, left-anchored */}
        <line x1={padX} y1={18} x2={padX} y2={34} className={styles.rrStopMark} />
        <text x={padX} y={46} className={styles.rrTick} style={{ fill: 'var(--red)' }}>SL {fmt(stop)}</text>

        {/* entry marker — label ABOVE the bar, centred (clamped off the edges) */}
        <line x1={entryX} y1={14} x2={entryX} y2={38} className={styles.rrEntryMark} />
        <text x={Math.min(Math.max(entryX, 40), W - 40)} y={12} className={styles.rrTickMid} style={{ fill: 'var(--gold)' }}>
          Entry {fmt(entry)}
        </text>

        {/* target markers — R multiple ABOVE the bar at each target */}
        {targets.map((_t, i) => {
          const tx = entryX + (rewards[i] / maxReward) * greenW
          const r = rewards[i] / risk
          return (
            <g key={i}>
              <line x1={tx} y1={18} x2={tx} y2={34} className={styles.rrTargetMark} />
              <text x={Math.min(tx, W - 24)} y={46} className={styles.rrTickEnd} style={{ fill: 'var(--green)' }}>
                T{i + 1} · {r.toFixed(1)}R
              </text>
            </g>
          )
        })}
      </svg>
    </div>
  )
}

function TradeCard({ body, structured }: { body: string; structured?: StructuredTradeIdea | null }) {
  // Prefer the structured tradeIdea meta field; fall back to parsing the text.
  const isNoTrade = structured
    ? structured.status === 'NO_TRADE'
    : /NO TRADE/i.test(body.slice(0, 150))
  const dirMatch = body.match(/\*\*Direction:\*\*\s*(LONG|SHORT)/i)
  const direction = structured && structured.status !== 'NO_TRADE'
    ? structured.direction
    : dirMatch?.[1]?.toUpperCase()

  const variant = structured
    ? (structured.status === 'NO_TRADE' ? 'no-trade'
       : structured.status === 'WAIT'   ? 'watch'
       : structured.direction === 'LONG' ? 'long' : 'short')
    : (isNoTrade ? 'no-trade' : direction === 'LONG' ? 'long' : direction === 'SHORT' ? 'short' : 'watch')

  const badgeText = isNoTrade
    ? 'No Trade'
    : structured
      ? (structured.status === 'WAIT' ? 'Watch' : structured.direction)
      : (direction ?? 'Watch')

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
          {badgeText}
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
        <>
        {structured && <RRBar idea={structured} />}
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
        </>
      )}
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
        {levels.map((lvl, i) => {
          // Some KEY LEVELS lines are bold sub-headers ("- **Short zone:** …")
          // rather than "price — desc"; render those as prose so the ** becomes
          // bold instead of showing literally.
          const isProse = lvl.desc === '' && /\*\*/.test(lvl.price)
          if (isProse) {
            return <p key={i} className={styles.levelProse}><Inline text={lvl.price} /></p>
          }
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
      {body.split(/\n\n+/).map((para, i) => (
        <p key={i}><Inline text={para.trim()} /></p>
      ))}
    </div>
  )
}

function AnalysisRenderer({ session }: { session: GoldSessionRecord }) {
  const analysis = session.analysis
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

      {/* Liquidity Ruler (structured) — falls back to the text KV card otherwise */}
      {session.keyLevels && session.keyLevels.length > 0 && session.priceAtAnalysis != null ? (
        <LiquidityRuler levels={session.keyLevels} current={session.priceAtAnalysis} />
      ) : liquidity ? (
        <KVCard title="Liquidity Map" rows={parseKVRows(liquidity.body)} />
      ) : null}

      {/* Key PD Arrays */}
      {pdArrays && (
        <KVCard title="Key PD Arrays" rows={parseKVRows(pdArrays.body)} />
      )}

      {/* Trade Idea — render if the text section OR a structured tradeIdea exists */}
      {(tradeIdea || session.tradeIdea) && (
        <TradeCard body={tradeIdea?.body ?? ''} structured={session.tradeIdea} />
      )}

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
  const { byFilename: outcomeByFile, outcomes } = useSessionOutcomes()
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
                <OutcomeGlyph result={outcomeByFile.get(s.filename)?.result} />
              </button>
            ))}
          </div>
        ))}

        <TrackRecord outcomes={outcomes} />
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
              {session.nextHighImpactEvent && (
                <span style={{ marginLeft: 'auto' }}>
                  <EventCountdown next={{ event: session.nextHighImpactEvent.event, whenIso: session.nextHighImpactEvent.timeIso }} />
                </span>
              )}
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

            {/* Structured analysis */}
            <AnalysisRenderer session={session} />
          </div>
        )}
      </div>
    </div>
  )
}
