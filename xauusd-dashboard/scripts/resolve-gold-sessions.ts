#!/usr/bin/env tsx
/**
 * Resolve past /gold-session predictions against what price actually did, so the
 * dashboard can show a calibration track-record ("Called 68% · Hit 61%").
 *
 * For each session record that (a) carries a directional call with the levels
 * needed to score it, (b) is at least MIN_AGE old, and (c) hasn't been resolved
 * yet, we fetch XAUUSD H1 bars over [analysis time, +WINDOW] and classify:
 *
 *   WIN    — price reached drawOnLiquidity (target) before invalidation (stop)
 *   LOSS   — price reached invalidation before the target (or both in one bar)
 *   EXPIRED_FAVOURABLE / _ADVERSE / _FLAT — neither hit within the window
 *   NO_CALL — no directional call / missing levels (terminal, excluded from stats)
 *
 * The outcome is written back into the session file AND appended to
 * public/data/sessions/outcomes.json — the permanent calibration archive
 * (never pruned, unlike the rolling index).
 *
 * Usage (from xauusd-dashboard/):
 *   npx tsx scripts/resolve-gold-sessions.ts          # resolve + write
 *   npx tsx scripts/resolve-gold-sessions.ts --dry    # classify + log, no writes
 *
 * Requires CTRADER_MCP_URL / CTRADER_MCP_TOKEN in the environment (the daily
 * workflow already provides them). Without a token it exits cleanly as a no-op.
 */

import * as fs from 'fs'
import * as path from 'path'
import { fileURLToPath } from 'url'
import { CTraderClient, KNOWN_SYMBOL_IDS, PIP_DIGITS } from './lib/ctrader'

const __filename = fileURLToPath(import.meta.url)
const __dirname  = path.dirname(__filename)

const DATA_DIR      = path.join(__dirname, '../public/data/sessions')
const OUTCOMES_FILE = path.join(DATA_DIR, 'outcomes.json')

const WINDOW_MS     = 8 * 3600 * 1000     // scoring window after analysis
const MIN_AGE_MS    = 4 * 3600 * 1000     // don't bother before the trade has had time to develop
const MAX_LOOKBACK_DAYS = 21              // ignore anything older (data + relevance)
const XAU_ID   = KNOWN_SYMBOL_IDS.XAUUSD
const XAU_SCALE = 10 ** (PIP_DIGITS.XAUUSD ?? 5)

const DRY = process.argv.includes('--dry')

type Result =
  | 'WIN' | 'LOSS'
  | 'EXPIRED_FAVOURABLE' | 'EXPIRED_ADVERSE' | 'EXPIRED_FLAT'
  | 'NO_CALL'

interface Outcome {
  result: Result
  resolvedAt: string
  maxFavourable: number | null
  maxAdverse: number | null
  barsSeen: number
}

interface SessionRecord {
  timestamp: string
  date: string
  time: string
  session: string
  bias: string
  probability: number
  confidence: number
  priceAtAnalysis?: number
  drawOnLiquidity?: number
  invalidation?: number
  priceZone?: string
  outcome?: Outcome
}

interface OutcomeRow {
  filename: string
  date: string
  time: string
  session: string
  bias: string
  probability: number
  confidence: number
  priceZone?: string
  result: Result
  resolvedAt: string
  maxFavourable: number | null
  maxAdverse: number | null
}

interface OutcomesFile {
  updatedAt: string
  outcomes: OutcomeRow[]
}

const round2 = (n: number) => Math.round(n * 100) / 100
const clamp0 = (n: number) => (n > 0 ? n : 0)

// Recursively list every session file (YYYY-MM-DD/HH-MM.json), newest first.
function listSessionFiles(): string[] {
  if (!fs.existsSync(DATA_DIR)) return []
  const out: string[] = []
  for (const day of fs.readdirSync(DATA_DIR)) {
    const dayDir = path.join(DATA_DIR, day)
    if (!/^\d{4}-\d{2}-\d{2}$/.test(day) || !fs.statSync(dayDir).isDirectory()) continue
    for (const f of fs.readdirSync(dayDir)) {
      if (f.endsWith('.json')) out.push(`${day}/${f}`)
    }
  }
  return out.sort().reverse()
}

/** Terminal outcome that needs no market data (bad/neutral call). */
function noCall(): Outcome {
  return { result: 'NO_CALL', resolvedAt: new Date().toISOString(), maxFavourable: null, maxAdverse: null, barsSeen: 0 }
}

/**
 * Classify a directional record against its H1 bars (display prices).
 * Returns null when the window isn't complete AND no level was hit — i.e. leave
 * it for a later run rather than finalising a premature EXPIRED.
 */
export function classify(
  rec: SessionRecord,
  bars: { open: number; high: number; low: number; close: number }[],
  now: number,
): Outcome | null {
  const bias  = rec.bias
  const entry = rec.priceAtAnalysis!
  const draw  = rec.drawOnLiquidity ?? null
  const inval = rec.invalidation ?? null
  const bullish = bias === 'BULLISH'

  let maxHigh = -Infinity
  let minLow  =  Infinity
  let result: Result | null = null

  for (const bar of bars) {
    if (bar.high > maxHigh) maxHigh = bar.high
    if (bar.low  < minLow)  minLow  = bar.low

    const drawHit  = draw  != null && (bullish ? bar.high >= draw  : bar.low  <= draw)
    const invalHit = inval != null && (bullish ? bar.low  <= inval : bar.high >= inval)

    // Both inside one bar → order unknowable → count the stop (conservative;
    // never inflate the win rate for a calibration archive).
    if (drawHit && invalHit) { result = 'LOSS'; break }
    if (invalHit)            { result = 'LOSS'; break }
    if (drawHit)             { result = 'WIN';  break }
  }

  const ts = Date.parse(rec.timestamp)
  const windowComplete = now >= ts + WINDOW_MS

  if (result === null) {
    if (!windowComplete) return null   // too early to finalise — retry next run
    const lastClose = bars[bars.length - 1].close
    const signed = bullish ? lastClose - entry : entry - lastClose
    result = Math.abs(signed) < entry * 0.001
      ? 'EXPIRED_FLAT'
      : signed > 0 ? 'EXPIRED_FAVOURABLE' : 'EXPIRED_ADVERSE'
  }

  const maxFavourable = round2(clamp0(bullish ? maxHigh - entry : entry - minLow))
  const maxAdverse    = round2(clamp0(bullish ? entry - minLow : maxHigh - entry))

  return { result, resolvedAt: new Date().toISOString(), maxFavourable, maxAdverse, barsSeen: bars.length }
}

function loadOutcomes(): OutcomesFile {
  try { return JSON.parse(fs.readFileSync(OUTCOMES_FILE, 'utf8')) as OutcomesFile }
  catch { return { updatedAt: '', outcomes: [] } }
}

async function main() {
  const now = Date.now()
  const client = new CTraderClient()

  const files = listSessionFiles()
  if (files.length === 0) { console.log('No session files found.'); return }

  const outcomesFile = loadOutcomes()
  const outcomesByFile = new Map(outcomesFile.outcomes.map(o => [o.filename, o]))

  let clientReady: boolean | null = null   // lazily init only if a record needs data
  let resolved = 0
  let skipped = 0

  for (const filename of files) {
    const full = path.join(DATA_DIR, filename)
    let rec: SessionRecord
    try { rec = JSON.parse(fs.readFileSync(full, 'utf8')) as SessionRecord }
    catch { continue }

    if (rec.outcome) { skipped++; continue }             // already terminal

    const ts = Date.parse(rec.timestamp)
    if (!Number.isFinite(ts)) { skipped++; continue }
    const age = now - ts
    if (age < MIN_AGE_MS) { skipped++; continue }        // too soon
    if (age > MAX_LOOKBACK_DAYS * 86_400_000) { skipped++; continue }

    // Only directional calls with the levels needed to score are resolvable.
    const directional = rec.bias === 'BULLISH' || rec.bias === 'BEARISH'
    const hasLevels = rec.priceAtAnalysis != null && (rec.drawOnLiquidity != null || rec.invalidation != null)
    let outcome: Outcome | null

    if (!directional || !hasLevels) {
      outcome = noCall()
    } else {
      if (clientReady === null) {
        clientReady = await client.init()
        if (!clientReady) {
          console.log('CTrader MCP unavailable (no token or init failed) — stopping; data-dependent records left unresolved.')
          break
        }
      }
      const toMs = Math.min(ts + WINDOW_MS, now)
      const rawBars = await client.getTrendbars(XAU_ID, 'H_1', ts, toMs)
      if (rawBars.length === 0) { console.log(`  ${filename}: no bars returned — retry next run`); skipped++; continue }
      const bars = rawBars.map(b => ({ open: b.open / XAU_SCALE, high: b.high / XAU_SCALE, low: b.low / XAU_SCALE, close: b.close / XAU_SCALE }))
      outcome = classify(rec, bars, now)
      if (outcome === null) { skipped++; continue }      // window not complete yet
    }

    console.log(`  ${filename}: ${rec.bias} → ${outcome.result}` +
      (outcome.maxFavourable != null ? ` (MFE $${outcome.maxFavourable} / MAE $${outcome.maxAdverse}, ${outcome.barsSeen} bars)` : ''))

    if (!DRY) {
      rec.outcome = outcome
      fs.writeFileSync(full, JSON.stringify(rec, null, 2))

      outcomesByFile.set(filename, {
        filename, date: rec.date, time: rec.time, session: rec.session,
        bias: rec.bias, probability: rec.probability, confidence: rec.confidence,
        ...(rec.priceZone ? { priceZone: rec.priceZone } : {}),
        result: outcome.result, resolvedAt: outcome.resolvedAt,
        maxFavourable: outcome.maxFavourable, maxAdverse: outcome.maxAdverse,
      })
    }
    resolved++
  }

  if (!DRY && resolved > 0) {
    const merged: OutcomesFile = {
      updatedAt: new Date().toISOString(),
      outcomes: [...outcomesByFile.values()].sort((a, b) => b.resolvedAt.localeCompare(a.resolvedAt)),
    }
    fs.writeFileSync(OUTCOMES_FILE, JSON.stringify(merged, null, 2))
  }

  console.log(`Resolved ${resolved} session${resolved !== 1 ? 's' : ''}, skipped ${skipped}.${DRY ? ' (dry run — no writes)' : ''}`)
}

// Only run when invoked directly (not when imported for unit tests).
if (process.argv[1] && fileURLToPath(import.meta.url) === path.resolve(process.argv[1])) {
  main().catch(err => { console.error('resolve-gold-sessions failed:', err); process.exit(1) })
}
