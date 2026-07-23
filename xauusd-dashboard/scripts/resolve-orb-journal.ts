#!/usr/bin/env tsx
/**
 * Resolve the ORB intel journal (J2, UK100-ORB-JOURNAL-DESIGN.md §3) — score
 * each hourly orbIntel read written by fetch-uk100-data.ts (J1) against what
 * UK100 price actually did, so "flagged vs happened" becomes a computed field.
 * Same conventions as resolve-uk100-sessions.ts (read that first): CTraderClient,
 * no-token = clean no-op, --dry flag, direct-invocation guard, UK100 H1 bars,
 * a local cashCloseCutoffMs.
 *
 * For each journal entry (public/data/uk100/orb-journal/YYYY-MM-DD.json) with
 * outcome:null, within the last 21 days:
 *   - Scoring window: entry.at → min(entry.at + 8h, same-day 16:30 London).
 *   - Published within 30 min of the close (or after) → terminal UNSCORABLE.
 *   - now < window end → leave null, retry next run.
 *   - else fetch H1 bars over the window and compute forward returns,
 *     excursions, a deterministic per-stance verdict and per-signal verdicts.
 *
 * After resolving, regenerate scoreboard.json from ALL scored entries (full
 * history) — the per-stance / per-rule hit rates the skill (J3) and review
 * sessions read to retune the thresholds.
 *
 * Usage (from xauusd-dashboard/):
 *   npx tsx scripts/resolve-orb-journal.ts          # resolve + write
 *   npx tsx scripts/resolve-orb-journal.ts --dry    # classify + log, no writes
 *
 * Requires CTRADER_MCP_URL / CTRADER_MCP_TOKEN. Without a token it's a no-op.
 */

import * as fs from 'fs'
import * as path from 'path'
import { fileURLToPath } from 'url'
import { CTraderClient, KNOWN_SYMBOL_IDS, PIP_DIGITS, type Trendbar } from './lib/ctrader'

const __filename = fileURLToPath(import.meta.url)
const __dirname  = path.dirname(__filename)

const JOURNAL_DIR    = path.join(__dirname, '../public/data/uk100/orb-journal')
const SCOREBOARD_FILE = path.join(JOURNAL_DIR, 'scoreboard.json')

const WINDOW_MS         = 8 * 3600 * 1000   // forward scoring window (same flat cap as the session resolver)
const MIN_WINDOW_MS     = 30 * 60 * 1000    // below this the read has no meaningful window → UNSCORABLE
const MAX_LOOKBACK_DAYS = 21
const UK100_ID    = KNOWN_SYMBOL_IDS.UK100
const UK100_SCALE = 10 ** (PIP_DIGITS.UK100 ?? 5)

const DRY = process.argv.includes('--dry')
// --rescore: recompute outcomes that are already resolved (used after a verdict-
// logic change — e.g. the ADR-relative BREAKOUT_SUSPECT fix — to correct the
// frozen historical scoreboard rather than only affecting future entries).
const RESCORE = process.argv.includes('--rescore')
const round2 = (n: number) => Math.round(n * 100) / 100

// ── Local type copies (scripts keep their own, per repo convention) ──
type Verdict = 'RIGHT' | 'WRONG' | 'FLAT'
interface JournalSignal { direction: string; rule: string }
interface JournalOutcome {
  resolvedAt: string
  fwd1hPct: number | null
  fwd3hPct: number | null
  toClosePct: number
  maxUpPct: number
  maxDownPct: number
  verdict: Verdict | 'UNSCORABLE' | null
  signalVerdicts: { rule: string; verdict: Verdict }[]
}
interface JournalEntry {
  at: string
  stance: string
  price: number
  signals: JournalSignal[]
  outcome: JournalOutcome | null
}
interface JournalDay { date: string; entries: JournalEntry[] }

interface StanceStat { n: number; right: number; wrong: number; flat: number; avgToClosePct: number }
interface RuleStat { n: number; right: number; wrong: number; flat: number }
interface Scoreboard {
  updatedAt: string
  entriesScored: number
  byStance: Record<string, StanceStat>
  byRule: Record<string, RuleStat>
  breakoutsSuspect: { n: number; noExtensionRate: number; avgMaxUpPct: number; avgMaxDownPct: number }
}

// ── UK-time helper (copied locally, same as the session resolver) ──
function ukOffsetHours(d: Date): number {
  const m = d.getUTCMonth() + 1
  const day = d.getUTCDate()
  if (m > 3 && m < 10) return 1
  if (m === 3 && day >= 25) return 1
  if (m === 10 && day < 25) return 1
  return 0
}

/** 16:30 London cash close on the London calendar date the instant falls on. */
export function cashCloseCutoffMs(ts: number): number {
  const offsetH = ukOffsetHours(new Date(ts))
  const londonLocal = new Date(ts + offsetH * 3_600_000)
  const londonMidnightUtc = Date.UTC(londonLocal.getUTCFullYear(), londonLocal.getUTCMonth(), londonLocal.getUTCDate()) - offsetH * 3_600_000
  return londonMidnightUtc + 16.5 * 3_600_000
}

/** End of an entry's forward scoring window. */
export function windowEndMs(entryMs: number): number {
  return Math.min(entryMs + WINDOW_MS, cashCloseCutoffMs(entryMs))
}

// ── Deterministic verdict rules (pure, unit-tested) ──

/** The R1 signal's direction (for FADE_FAVOURED, which side the fade favours). */
function r1Direction(signals: JournalSignal[]): string | null {
  return signals.find(s => s.rule === 'R1')?.direction ?? null
}

export function stanceVerdict(stance: string, r1dir: string | null, toClosePct: number): Verdict | null {
  let longSide: boolean | null = null
  if (stance === 'LONG_FAVOURED') longSide = true
  else if (stance === 'SHORT_FAVOURED') longSide = false
  else if (stance === 'FADE_FAVOURED') longSide = r1dir === 'FAVOURS_LONG' ? true : r1dir === 'FAVOURS_SHORT' ? false : null
  else return null   // BREAKOUTS_SUSPECT / MIXED are not directional calls
  if (longSide === null) return null
  const signed = longSide ? toClosePct : -toClosePct
  if (signed >= 0.15) return 'RIGHT'
  if (signed <= -0.15) return 'WRONG'
  return 'FLAT'
}

// Default ADR (% of price) used only when a journal entry predates the `orb.adr14`
// field or it's null — roughly UK100's 14-day norm, so the fallback still scales
// the BREAKOUT_SUSPECT thresholds sanely rather than reverting to the old bug.
const DEFAULT_ADR_PCT = 1.2

export function signalVerdict(
  direction: string,
  toClosePct: number,
  maxUpPct: number,
  maxDownPct: number,
  adrPct: number | null = null,
): Verdict | null {
  if (direction === 'FAVOURS_LONG' || direction === 'FAVOURS_SHORT') {
    const signed = direction === 'FAVOURS_LONG' ? toClosePct : -toClosePct
    if (signed >= 0.15) return 'RIGHT'
    if (signed <= -0.15) return 'WRONG'
    return 'FLAT'
  }
  if (direction === 'BREAKOUT_SUSPECT') {
    // BREAKOUT_SUSPECT predicts "the break won't follow through — expect a
    // compressed/range day". Judge that on the day's REALISED RANGE relative to
    // its ADR, NOT absolute % — the old fixed 0.25%/0.40% thresholds were
    // calibrated for a low-vol instrument and mis-scored UK100 (ADR ≈1.28%),
    // where a normal range day still swings 0.6–0.9% intraday, so a genuine
    // flat-close range day (e.g. 2026-07-17, closed −0.06%) was force-marked
    // WRONG by an intraday wick. ADR-relative fixes that.
    const adr = adrPct && adrPct > 0 ? adrPct : DEFAULT_ADR_PCT
    const span = maxUpPct - maxDownPct   // maxDownPct is signed ≤ 0 → high-to-low realised range, %
    if (span <= 0.55 * adr) return 'RIGHT'   // compressed vs ADR — the break was indeed suspect
    if (span >= 1.0  * adr) return 'WRONG'   // a full-ADR (or more) expansion happened
    return 'FLAT'
  }
  return null   // NEUTRAL signals are not scored
}

/** Score a scorable entry (window complete) against its H1 bars. */
export function computeOutcome(
  entry: { at: string; price: number; stance: string; signals: JournalSignal[]; orb?: { adr14?: number | null } },
  bars: { timestamp: number; high: number; low: number; close: number }[],
  cutoffMs: number,
): JournalOutcome {
  // ADR as a % of entry price, for ADR-relative BREAKOUT_SUSPECT scoring.
  const adrPct = entry.orb?.adr14 && entry.price ? (entry.orb.adr14 / entry.price) * 100 : null
  const entryMs = Date.parse(entry.at)
  const entryPrice = entry.price
  const pct = (v: number) => round2((v - entryPrice) / entryPrice * 100)
  const usable = bars.filter(b => b.timestamp >= entryMs && b.timestamp <= cutoffMs)
  const scan = usable.length > 0 ? usable : bars
  const maxUpPct = pct(Math.max(...scan.map(b => b.high)))
  const maxDownPct = pct(Math.min(...scan.map(b => b.low)))
  const toClosePct = pct(scan[scan.length - 1].close)

  const windowH = (cutoffMs - entryMs) / 3_600_000
  const fwdAt = (h: number): number | null => {
    if (windowH < h - 0.5) return null   // window doesn't reach h hours out
    const target = entryMs + h * 3_600_000
    const upto = scan.filter(b => b.timestamp <= target + 30 * 60_000)
    if (upto.length === 0) return null
    return pct(upto[upto.length - 1].close)
  }

  const verdict = stanceVerdict(entry.stance, r1Direction(entry.signals), toClosePct)
  const signalVerdicts = entry.signals
    .map(s => ({ rule: s.rule, verdict: signalVerdict(s.direction, toClosePct, maxUpPct, maxDownPct, adrPct) }))
    .filter((x): x is { rule: string; verdict: Verdict } => x.verdict !== null)

  return {
    resolvedAt: new Date().toISOString(),
    fwd1hPct: fwdAt(1), fwd3hPct: fwdAt(3),
    toClosePct, maxUpPct, maxDownPct,
    verdict, signalVerdicts,
  }
}

// ── Scoreboard aggregation (pure, unit-tested) ──
function bump(s: { right: number; wrong: number; flat: number }, v: Verdict): void {
  if (v === 'RIGHT') s.right++
  else if (v === 'WRONG') s.wrong++
  else s.flat++
}

export function buildScoreboard(entries: { stance: string; outcome: JournalOutcome }[]): Scoreboard {
  const byStance: Record<string, StanceStat> = {}
  const byRule: Record<string, RuleStat> = {}
  let bsN = 0, bsNoExt = 0, bsSumUp = 0, bsSumDown = 0

  for (const e of entries) {
    const o = e.outcome
    if (o.verdict === 'RIGHT' || o.verdict === 'WRONG' || o.verdict === 'FLAT') {
      const s = (byStance[e.stance] ??= { n: 0, right: 0, wrong: 0, flat: 0, avgToClosePct: 0 })
      s.n++; bump(s, o.verdict); s.avgToClosePct += o.toClosePct
    }
    for (const sv of o.signalVerdicts) {
      const r = (byRule[sv.rule] ??= { n: 0, right: 0, wrong: 0, flat: 0 })
      r.n++; bump(r, sv.verdict)
    }
    if (e.stance === 'BREAKOUTS_SUSPECT') {
      bsN++
      if (o.maxUpPct < 0.25 && Math.abs(o.maxDownPct) < 0.25) bsNoExt++
      bsSumUp += o.maxUpPct; bsSumDown += o.maxDownPct
    }
  }
  for (const k of Object.keys(byStance)) byStance[k].avgToClosePct = round2(byStance[k].avgToClosePct / byStance[k].n)

  return {
    updatedAt: new Date().toISOString(),
    entriesScored: entries.length,
    byStance, byRule,
    breakoutsSuspect: {
      n: bsN,
      noExtensionRate: bsN ? round2(bsNoExt / bsN) : 0,
      avgMaxUpPct: bsN ? round2(bsSumUp / bsN) : 0,
      avgMaxDownPct: bsN ? round2(bsSumDown / bsN) : 0,
    },
  }
}

// ── File listing ──
function listJournalFiles(): string[] {
  if (!fs.existsSync(JOURNAL_DIR)) return []
  return fs.readdirSync(JOURNAL_DIR)
    .filter(f => /^\d{4}-\d{2}-\d{2}\.json$/.test(f))
    .sort()
}

async function main() {
  const now = Date.now()
  const files = listJournalFiles()
  if (files.length === 0) { console.log('No ORB journal files found.'); return }

  const client = new CTraderClient()
  let clientReady: boolean | null = null
  let resolved = 0, unscorable = 0, pending = 0
  const dayCache = new Map<string, JournalDay>()

  const readDay = (file: string): JournalDay | null => {
    if (dayCache.has(file)) return dayCache.get(file)!
    try { const d = JSON.parse(fs.readFileSync(path.join(JOURNAL_DIR, file), 'utf8')) as JournalDay; dayCache.set(file, d); return d }
    catch { return null }
  }

  for (const file of files) {
    const dateMs = Date.parse(`${file.slice(0, 10)}T12:00:00Z`)
    if (now - dateMs > MAX_LOOKBACK_DAYS * 86_400_000) continue   // too old to resolve (kept for the scoreboard pass)
    const day = readDay(file)
    if (!day) continue
    let changed = false

    for (const entry of day.entries) {
      if (entry.outcome && !RESCORE) continue
      if (entry.outcome && entry.outcome.verdict === 'UNSCORABLE') continue   // window was too short — nothing to recompute
      const entryMs = Date.parse(entry.at)
      if (!Number.isFinite(entryMs)) continue
      const cutoffMs = windowEndMs(entryMs)

      if (cutoffMs - entryMs < MIN_WINDOW_MS) {
        entry.outcome = { resolvedAt: new Date().toISOString(), fwd1hPct: null, fwd3hPct: null, toClosePct: 0, maxUpPct: 0, maxDownPct: 0, verdict: 'UNSCORABLE', signalVerdicts: [] }
        changed = true; unscorable++
        continue
      }
      if (now < cutoffMs) { pending++; continue }   // window not complete — retry next run

      if (clientReady === null) {
        clientReady = await client.init()
        if (!clientReady) { console.log('CTrader MCP unavailable (no token or init failed) — stopping; unresolved entries left for next run.'); break }
      }
      const rawBars = await client.getTrendbars(UK100_ID, 'H_1', entryMs, cutoffMs)
      if (rawBars.length === 0) { console.log(`  ${file} @ ${entry.at}: no bars — retry next run`); pending++; continue }
      const bars = rawBars.map((b: Trendbar) => ({ timestamp: b.timestamp, high: b.high / UK100_SCALE, low: b.low / UK100_SCALE, close: b.close / UK100_SCALE }))
      entry.outcome = computeOutcome(entry, bars, cutoffMs)
      changed = true; resolved++
      console.log(`  ${file} @ ${entry.at}: ${entry.stance} → ${entry.outcome.verdict ?? '—'} (toClose ${entry.outcome.toClosePct}%, up ${entry.outcome.maxUpPct}% / down ${entry.outcome.maxDownPct}%)`)
    }

    if (clientReady === false) break
    if (changed && !DRY) fs.writeFileSync(path.join(JOURNAL_DIR, file), JSON.stringify(day, null, 2))
  }

  // Scoreboard — regenerate from ALL scored entries across the FULL history.
  const scored: { stance: string; outcome: JournalOutcome }[] = []
  for (const file of files) {
    const day = readDay(file)
    if (!day) continue
    for (const e of day.entries) {
      if (e.outcome && e.outcome.verdict !== 'UNSCORABLE') scored.push({ stance: e.stance, outcome: e.outcome })
    }
  }
  if (!DRY && (resolved > 0 || !fs.existsSync(SCOREBOARD_FILE)) && scored.length > 0) {
    fs.writeFileSync(SCOREBOARD_FILE, JSON.stringify(buildScoreboard(scored), null, 2))
  }

  console.log(`ORB journal: resolved ${resolved}, unscorable ${unscorable}, pending ${pending}; scoreboard entries ${scored.length}.${DRY ? ' (dry run — no writes)' : ''}`)
}

// Only run when invoked directly (not when imported for unit tests).
if (process.argv[1] && fileURLToPath(import.meta.url) === path.resolve(process.argv[1])) {
  main().catch(err => { console.error('resolve-orb-journal failed:', err); process.exit(1) })
}
