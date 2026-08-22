#!/usr/bin/env tsx
/**
 * Resolve past /uk100-session predictions against what price actually did, so the
 * dashboard can show a calibration track-record — same purpose as
 * resolve-gold-sessions.ts (read that one first, this is a copy with UK100-
 * specific changes only: DATA_DIR, symbol, the intraday scoring window, the
 * directional-call gate, and the level-hit sequence enrichment below).
 *
 * For each session record that (a) carries a directional ACTIVE trade idea with
 * the levels needed to score it, (b) is at least MIN_AGE old, and (c) hasn't been
 * resolved yet, we fetch UK100 H1 bars over [analysis time, scoring cutoff] and
 * classify:
 *
 *   WIN    — price reached drawOnLiquidity (target) before invalidation (stop)
 *   LOSS   — price reached invalidation before the target (or both in one bar)
 *   EXPIRED_FAVOURABLE / _ADVERSE / _FLAT — neither hit within the window
 *   NO_CALL — no ACTIVE directional trade idea / missing levels (terminal, excluded from stats)
 *
 * UK100-specific: the record's own `bias` label can be NEUTRAL while the ORB
 * playbook still produces a genuine ACTIVE LONG/SHORT call (the ORB decision
 * table trades structure/session mechanics, not the macro bias score) — so the
 * directional gate here keys off `tradeIdea.status === 'ACTIVE'`, not `bias`,
 * unlike gold's resolver where bias IS the call.
 *
 * UK100-SESSION-REVIEW-2026-07-13.md §5 F7 enrichment: alongside the single
 * WIN/LOSS/EXPIRED result (computed from drawOnLiquidity/invalidation, same
 * conservative rule as gold — both hit in one bar counts the stop), each
 * outcome also carries `hits`: the chronological sequence of tradeIdea target
 * (T1/T2/...) and stop touches, e.g. `[{level:"T1",...},{level:"T2",...},
 * {level:"STOP",...}]` — a trade can run T1→T2 before eventually reversing
 * into the stop, which a single first-touch result can't express.
 *
 * Also UK100-specific: the scoring window is capped at the same-day 16:30
 * London cash close (in addition to gold's flat 8h window) — the ORB call is
 * strictly intraday, so bars after the close must not score it.
 *
 * The outcome is written back into the session file AND appended to
 * public/data/uk100/sessions/outcomes.json — the permanent calibration
 * archive (never pruned, unlike the rolling index).
 *
 * Usage (from xauusd-dashboard/):
 *   npx tsx scripts/resolve-uk100-sessions.ts          # resolve + write
 *   npx tsx scripts/resolve-uk100-sessions.ts --dry    # classify + log, no writes
 *
 * Requires CTRADER_MCP_URL / CTRADER_MCP_TOKEN in the environment (the daily
 * workflow already provides them). Without a token it exits cleanly as a no-op.
 */

import * as fs from 'fs'
import * as path from 'path'
import { fileURLToPath } from 'url'
import { CTraderClient, KNOWN_SYMBOL_IDS, PIP_DIGITS, type Trendbar } from './lib/ctrader'

const __filename = fileURLToPath(import.meta.url)
const __dirname  = path.dirname(__filename)

const DATA_DIR      = path.join(__dirname, '../public/data/uk100/sessions')
const OUTCOMES_FILE = path.join(DATA_DIR, 'outcomes.json')

const WINDOW_MS     = 8 * 3600 * 1000     // scoring window after analysis (same flat cap as gold)
const MIN_AGE_MS    = 4 * 3600 * 1000     // don't bother before the trade has had time to develop
const MAX_LOOKBACK_DAYS = 21              // ignore anything older (data + relevance)
const UK100_ID   = KNOWN_SYMBOL_IDS.UK100
const UK100_SCALE = 10 ** (PIP_DIGITS.UK100 ?? 5)

const DRY = process.argv.includes('--dry')

// Local type copies — same convention as resolve-gold-sessions.ts and
// fetch-uk100-data.ts (scripts keep their own copies rather than importing
// across the scripts/src boundary); src/types/dashboard.ts carries the
// canonical UI-facing versions (HitEvent, SessionOutcome.hits,
// OutcomeRow.orbDirection) that the frontend imports directly.
type Result =
  | 'WIN' | 'LOSS'
  | 'EXPIRED_FAVOURABLE' | 'EXPIRED_ADVERSE' | 'EXPIRED_FLAT'
  | 'NO_CALL'

interface HitEvent { level: string; timestamp: string }

interface TargetSpec { direction: 'LONG' | 'SHORT'; status: string; stop?: number; targets?: number[] }

interface BaseOutcome {
  result: Result
  resolvedAt: string
  maxFavourable: number | null
  maxAdverse: number | null
  barsSeen: number
}

interface Outcome extends BaseOutcome {
  hits: HitEvent[]
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
  tradeIdea?: TargetSpec | null
  orbPlaybook?: { direction: string } | null
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
  orbDirection?: string | null
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

// UK time: BST (UTC+1) runs from last Sunday of March to last Sunday of October.
// Approximate with month boundaries — accurate to within a week at month edges.
// Copied locally from save-gold-session.ts (existing convention: scripts keep
// their own copy of small date helpers rather than importing across scripts).
function ukOffsetHours(d: Date): number {
  const m = d.getUTCMonth() + 1 // 1-12
  const day = d.getUTCDate()
  if (m > 3 && m < 10) return 1
  if (m === 3 && day >= 25) return 1
  if (m === 10 && day < 25) return 1
  return 0
}

/** 16:30 London cash close, on the London calendar date the given UTC instant falls on. */
export function cashCloseCutoffMs(ts: number): number {
  const offsetH = ukOffsetHours(new Date(ts))
  const londonLocal = new Date(ts + offsetH * 3_600_000)
  const londonMidnightUtc = Date.UTC(londonLocal.getUTCFullYear(), londonLocal.getUTCMonth(), londonLocal.getUTCDate()) - offsetH * 3_600_000
  return londonMidnightUtc + 16.5 * 3_600_000
}

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
  return { result: 'NO_CALL', resolvedAt: new Date().toISOString(), maxFavourable: null, maxAdverse: null, barsSeen: 0, hits: [] }
}

/**
 * Classify a directional record against its H1 bars (display prices), using
 * drawOnLiquidity/invalidation exactly like gold's resolver — same
 * conservative both-in-one-bar=loss rule. `bullish` comes from the record's
 * ACTIVE tradeIdea.direction, not `bias` (which can be NEUTRAL on a genuine
 * ORB-playbook call — see file header).
 * Returns null when the window isn't complete AND no level was hit — i.e.
 * leave it for a later run rather than finalising a premature EXPIRED.
 */
export function classify(
  rec: SessionRecord,
  bars: { open: number; high: number; low: number; close: number }[],
  now: number,
  cutoffMs: number,
): BaseOutcome | null {
  const bullish = rec.tradeIdea!.direction === 'LONG'
  const entry = rec.priceAtAnalysis!
  const draw  = rec.drawOnLiquidity ?? null
  const inval = rec.invalidation ?? null

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

  const windowComplete = now >= cutoffMs

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

/**
 * F7 enrichment: the chronological sequence of tradeIdea target (T1/T2/...)
 * and stop touches, scanned against timestamped bars. Independent of
 * classify()'s WIN/LOSS result (which stays anchored to drawOnLiquidity/
 * invalidation for gold-compatible semantics) — this is a richer trace for
 * display, e.g. a T1→T2→STOP sequence where price ran to two targets before
 * eventually reversing into the stop.
 *
 * Same conservative rule as classify(): a bar that touches both an unhit
 * target and the stop counts only the stop, and the scan ends there (a
 * closed position can't go on to hit later targets).
 */
export function classifyHits(
  direction: 'LONG' | 'SHORT',
  targets: number[],
  stop: number,
  bars: { high: number; low: number; timestamp: number }[],
): HitEvent[] {
  const bullish = direction === 'LONG'
  const hits: HitEvent[] = []
  const hitIdx = new Set<number>()

  for (const bar of bars) {
    const stopTouched = bullish ? bar.low <= stop : bar.high >= stop
    if (stopTouched) {
      hits.push({ level: 'STOP', timestamp: new Date(bar.timestamp).toISOString() })
      break
    }
    targets.forEach((t, i) => {
      if (hitIdx.has(i)) return
      const touched = bullish ? bar.high >= t : bar.low <= t
      if (touched) {
        hitIdx.add(i)
        hits.push({ level: `T${i + 1}`, timestamp: new Date(bar.timestamp).toISOString() })
      }
    })
    if (hitIdx.size === targets.length) break
  }

  return hits
}

function loadOutcomes(): OutcomesFile {
  try { return JSON.parse(fs.readFileSync(OUTCOMES_FILE, 'utf8')) as OutcomesFile }
  catch { return { updatedAt: '', outcomes: [] } }
}

async function main() {
  const now = Date.now()
  const client = new CTraderClient()

  const files = listSessionFiles()
  if (files.length === 0) { console.log('No UK100 session files found.'); return }

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

    // Only an ACTIVE directional trade idea, with the levels needed to
    // score it, is a resolvable "call" — bias alone (which can be NEUTRAL
    // on a genuine ORB-playbook call, see file header) is not enough.
    const directional = rec.tradeIdea?.status === 'ACTIVE' &&
      (rec.tradeIdea.direction === 'LONG' || rec.tradeIdea.direction === 'SHORT')
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
      const cutoffMs = Math.min(ts + WINDOW_MS, cashCloseCutoffMs(ts))
      const toMs = Math.min(cutoffMs, now)
      const rawBars = await client.getTrendbars(UK100_ID, 'H_1', ts, toMs)
      if (rawBars.length === 0) { console.log(`  ${filename}: no bars returned — retry next run`); skipped++; continue }
      const bars = rawBars.map((b: Trendbar) => ({ open: b.open / UK100_SCALE, high: b.high / UK100_SCALE, low: b.low / UK100_SCALE, close: b.close / UK100_SCALE }))
      const base = classify(rec, bars, now, cutoffMs)
      if (base === null) { skipped++; continue }         // window not complete yet

      const tradeIdea = rec.tradeIdea!
      const hits = tradeIdea.targets && tradeIdea.targets.length > 0 && tradeIdea.stop != null
        ? classifyHits(tradeIdea.direction, tradeIdea.targets, tradeIdea.stop, rawBars)
        : []
      outcome = { ...base, hits }
    }

    console.log(`  ${filename}: ${rec.tradeIdea?.direction ?? rec.bias} → ${outcome.result}` +
      (outcome.maxFavourable != null ? ` (MFE ${outcome.maxFavourable}pt / MAE ${outcome.maxAdverse}pt, ${outcome.barsSeen} bars)` : '') +
      (outcome.hits.length > 0 ? ` [${outcome.hits.map(h => h.level).join('→')}]` : ''))

    if (!DRY) {
      rec.outcome = outcome
      fs.writeFileSync(full, JSON.stringify(rec, null, 2))

      outcomesByFile.set(filename, {
        filename, date: rec.date, time: rec.time, session: rec.session,
        bias: rec.bias, probability: rec.probability, confidence: rec.confidence,
        ...(rec.priceZone ? { priceZone: rec.priceZone } : {}),
        orbDirection: rec.orbPlaybook?.direction ?? null,
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

  console.log(`Resolved ${resolved} UK100 session${resolved !== 1 ? 's' : ''}, skipped ${skipped}.${DRY ? ' (dry run — no writes)' : ''}`)
}

// Only run when invoked directly (not when imported for unit tests).
if (process.argv[1] && fileURLToPath(import.meta.url) === path.resolve(process.argv[1])) {
  main().catch(err => { console.error('resolve-uk100-sessions failed:', err); process.exit(1) })
}
