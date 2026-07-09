#!/usr/bin/env tsx
/**
 * Save a /gold-session analysis to the dashboard's Gold-Session AI tab.
 *
 * Usage (from xauusd-dashboard/):
 *   npx tsx scripts/save-gold-session.ts /tmp/gold-session-meta.json /tmp/gold-session-analysis.txt
 *
 * Args:
 *   1. Path to a JSON file with: { session, bias, biasScore, probability, confidence }
 *   2. Path to a plain-text file containing the full analysis output
 *
 * Writes:
 *   public/data/sessions/<YYYY-MM-DD>/<HH-MM>.json
 *   public/data/sessions/index.json  (rolling 3-day window)
 *
 * Then commits and pushes to origin main so the dashboard deploys automatically.
 */

import * as fs from 'fs'
import * as path from 'path'
import { fileURLToPath } from 'url'
import { execSync } from 'child_process'

const __filename = fileURLToPath(import.meta.url)
const __dirname  = path.dirname(__filename)

const DATA_DIR   = path.join(__dirname, '../public/data/sessions')
const INDEX_FILE = path.join(DATA_DIR, 'index.json')
const REPO_ROOT  = path.join(__dirname, '../..')
const MAX_DAYS   = 3

type PriceZone = 'DISCOUNT' | 'PREMIUM' | 'EQUILIBRIUM' | 'OTE'

type KeyLevelKind =
  | 'BSL' | 'SSL' | 'PDH' | 'PDL' | 'PWH' | 'PWL'
  | 'ASIAN_HIGH' | 'ASIAN_LOW' | 'POC' | 'INVALIDATION' | 'DRAW' | 'OTHER'

interface KeyLevel {
  price: number
  kind:  KeyLevelKind
  note?: string
}

interface StructuredTradeIdea {
  direction: 'LONG' | 'SHORT'
  status:    'ACTIVE' | 'WAIT' | 'NO_TRADE'
  entryLow?:  number
  entryHigh?: number
  stop?:      number
  targets?:   number[]
  rr?:        number
  setupType?: string
}

interface SessionMeta {
  session:     string   // LONDON | NEW_YORK | OVERLAP | ASIAN
  bias:        string   // BULLISH | BEARISH | NEUTRAL
  biasScore:   number   // -5 to +5
  probability: number   // 0-100
  confidence:  number   // 1-10

  // ── Optional structured fields (Phase 2) — populated by the skill from the
  //    engine output. Absent on pre-Phase-2 records; the UI falls back to
  //    regex-parsing the analysis text when a field is missing. ──
  priceAtAnalysis?:     number
  drawOnLiquidity?:     number       // primary target level
  invalidation?:        number
  priceZone?:           PriceZone
  equilibrium?:         number
  keyLevels?:           KeyLevel[]
  tradeIdea?:           StructuredTradeIdea | null
  nextHighImpactEvent?: { event: string; timeIso: string } | null
  smtDivergence?:       'BULLISH' | 'BEARISH' | null
}

interface SessionRecord extends SessionMeta {
  timestamp: string
  date:      string
  time:      string
  analysis:  string
}

// Index stays lean — only what the sidebar needs. Heavy detail (keyLevels,
// full tradeIdea) lives in the per-session file, not the rolling index.
interface IndexEntry {
  date:        string
  time:        string
  filename:    string   // YYYY-MM-DD/HH-MM.json
  timestamp:   string
  session:     string
  bias:        string
  biasScore:   number
  probability: number
  confidence:  number
  priceZone?:  PriceZone
  tradeIdea?:  { direction: 'LONG' | 'SHORT'; status: 'ACTIVE' | 'WAIT' | 'NO_TRADE' } | null
}

interface SessionIndex {
  updatedAt: string
  sessions:  IndexEntry[]
}

function run(cmd: string) {
  return execSync(cmd, { stdio: 'pipe' }).toString().trim()
}

function main() {
  const metaPath     = process.argv[2]
  const analysisPath = process.argv[3]

  if (!metaPath || !analysisPath) {
    console.error('Usage: save-gold-session.ts <meta.json> <analysis.txt>')
    process.exit(1)
  }

  const meta     = JSON.parse(fs.readFileSync(metaPath, 'utf8')) as SessionMeta
  const analysis = fs.readFileSync(analysisPath, 'utf8').trim()

  // ── Freshness gate ─────────────────────────────────────────────────────────
  // This script is the single choke point through which every record reaches
  // the dashboard, so it verifies the analysis was actually built from a fresh
  // engine run. On 2026-07-09 a session whose cTrader fetch failed fabricated a
  // "fresh" brief from the previous day's saved records and published it —
  // wrong Asian range, phantom sweeps, day-old structure timestamps. The skill
  // docs already forbade that; a mechanical check is what actually stops it.
  // /tmp/gold_session_input.json is the canonical engine input the skill just
  // assembled (STEP 0 Phase C1); require it to exist and its newest M1/M5/H1
  // candle to be recent. No fresh engine input → no publish.
  const ENGINE_INPUT = process.argv[4] ?? '/tmp/gold_session_input.json'
  const MAX_INPUT_AGE_MIN = 60
  try {
    const inp = JSON.parse(fs.readFileSync(ENGINE_INPUT, 'utf8')) as Record<string, Array<{ timestamp: number }>>
    let newest = 0
    for (const key of ['m1', 'm5', 'h1']) {
      for (const bar of inp[key] ?? []) newest = Math.max(newest, bar.timestamp ?? 0)
    }
    const ageMin = (Date.now() - newest) / 60_000
    if (!newest || ageMin > MAX_INPUT_AGE_MIN) {
      console.error(`REFUSING TO SAVE: engine input at ${ENGINE_INPUT} has newest candle ${Math.round(ageMin)} min old (limit ${MAX_INPUT_AGE_MIN}).`)
      console.error('The analysis was not built from a fresh engine run. Re-run STEP 0 (fetch live trendbars, assemble input, run skill_adapter.py) and try again.')
      process.exit(1)
    }
  } catch {
    console.error(`REFUSING TO SAVE: cannot read engine input at ${ENGINE_INPUT}.`)
    console.error('Every dashboard record must come from a fresh skill_adapter.py run in this session — never from previously saved records or another run’s output.')
    process.exit(1)
  }

  const now  = new Date()
  const date = now.toISOString().slice(0, 10)

  // UK time: BST (UTC+1) runs from last Sunday of March to last Sunday of October.
  // Approximate with month boundaries — accurate to within a week at month edges.
  function ukOffsetHours(d: Date): number {
    const m = d.getUTCMonth() + 1 // 1-12
    const day = d.getUTCDate()
    if (m > 3 && m < 10) return 1
    if (m === 3 && day >= 25) return 1   // last Sun March ≈ 25–31
    if (m === 10 && day < 25) return 1   // last Sun Oct ≈ 25–31
    return 0
  }
  const offsetH      = ukOffsetHours(now)
  const ukMs         = now.getTime() + offsetH * 3_600_000
  const ukDate       = new Date(ukMs)
  const tzLabel      = offsetH === 1 ? 'BST' : 'GMT'
  const hhmm         = `${String(now.getUTCHours()).padStart(2,'0')}-${String(now.getUTCMinutes()).padStart(2,'0')}` // filename uses UTC
  const timeDisplay  = `${String(ukDate.getUTCHours()).padStart(2,'0')}:${String(ukDate.getUTCMinutes()).padStart(2,'0')} ${tzLabel}`

  const record: SessionRecord = { ...meta, timestamp: now.toISOString(), date, time: timeDisplay, analysis }

  // Write session file
  const sessionDir  = path.join(DATA_DIR, date)
  fs.mkdirSync(sessionDir, { recursive: true })
  const sessionFile = path.join(sessionDir, `${hhmm}.json`)
  fs.writeFileSync(sessionFile, JSON.stringify(record, null, 2))
  console.log(`Session saved: ${path.relative(REPO_ROOT, sessionFile)}`)

  // Load + update index (rolling MAX_DAYS window)
  let index: SessionIndex = { updatedAt: '', sessions: [] }
  try { index = JSON.parse(fs.readFileSync(INDEX_FILE, 'utf8')) as SessionIndex } catch { /* fresh index */ }

  const entry: IndexEntry = {
    date, time: timeDisplay, filename: `${date}/${hhmm}.json`,
    timestamp: now.toISOString(),
    session: meta.session, bias: meta.bias, biasScore: meta.biasScore,
    probability: meta.probability, confidence: meta.confidence,
    ...(meta.priceZone ? { priceZone: meta.priceZone } : {}),
    ...(meta.tradeIdea ? { tradeIdea: { direction: meta.tradeIdea.direction, status: meta.tradeIdea.status } } : {}),
  }

  const cutoff    = new Date()
  cutoff.setUTCDate(cutoff.getUTCDate() - MAX_DAYS)
  const cutoffStr = cutoff.toISOString().slice(0, 10)

  index.sessions = [
    ...index.sessions.filter(s => s.date >= cutoffStr && s.filename !== entry.filename),
    entry,
  ].sort((a, b) => b.timestamp.localeCompare(a.timestamp))
  index.updatedAt = now.toISOString()

  fs.writeFileSync(INDEX_FILE, JSON.stringify(index, null, 2))
  console.log(`Index updated (${index.sessions.length} session${index.sessions.length !== 1 ? 's' : ''}, last ${MAX_DAYS} days)`)

  // Git commit + push
  // Attribute the data commit to the bot identity PER-COMMAND (`git -c ...`),
  // NOT via `git config` — a persistent local config leaks the bot identity into
  // the repo and mislabels any subsequent human/Claude commits as gold-session-bot.
  const BOT_ID = `-c user.name="gold-session-bot" -c user.email="gold-session-bot@noreply.github.com"`
  try {
    run(`git -C "${REPO_ROOT}" add xauusd-dashboard/public/data/sessions/`)

    let hasStagedChanges = false
    try { run(`git -C "${REPO_ROOT}" diff --staged --quiet`); } catch { hasStagedChanges = true }

    if (hasStagedChanges) {
      run(`git -C "${REPO_ROOT}" ${BOT_ID} commit -m "chore: gold-session ${date} ${timeDisplay}"`)
      // Rebase the current branch onto the latest main so the push fast-forwards,
      // then push THIS commit (HEAD) to origin/main. Using `HEAD:main` (not
      // `push origin main`) is essential when the working tree is on a feature
      // branch — `git push origin main` would push the stale local `main` ref and
      // silently fail to deploy the session that was just committed on HEAD.
      //
      // BOT_ID must ALSO wrap this rebase: whenever origin/main has moved (common —
      // the hourly data-fetch workflow pushes independently), the rebase REPLAYS the
      // commit just made above, and `git rebase` sets the COMMITTER of the replayed
      // commit from the ambient ad-hoc `user.name`/`user.email` config — NOT from the
      // `-c` override scoped to the earlier `commit` invocation, which only applied to
      // that one command. Author is preserved from the original commit, so without
      // this the result is a split identity (author=gold-session-bot, committer=
      // whatever the local config happened to be) — observed 2026-07-08.
      run(`git -C "${REPO_ROOT}" ${BOT_ID} pull --rebase origin main`)
      run(`git -C "${REPO_ROOT}" push origin HEAD:main`)
      console.log('Committed and pushed to main — dashboard updates after GitHub Actions deploys (~1-2 min).')
    } else {
      console.log('No changes staged — session may already be committed.')
    }
  } catch (err) {
    console.error('Git operation failed:', (err as Error).message)
    console.error('Session file saved locally. Retry with: git push origin main')
    process.exit(1)
  }
}

main()
