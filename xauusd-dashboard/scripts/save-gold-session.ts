#!/usr/bin/env tsx
/**
 * Save a /gold-session or /uk100-session analysis to the dashboard's
 * Gold-Session AI / UK100 AI tab.
 *
 * Usage (from xauusd-dashboard/):
 *   npx tsx scripts/save-gold-session.ts /tmp/gold-session-meta.json /tmp/gold-session-analysis.txt
 *   npx tsx scripts/save-gold-session.ts /tmp/uk100-session-meta.json /tmp/uk100-session-analysis.txt --instrument=uk100
 *
 * Args:
 *   1. Path to a JSON file with: { session, bias, biasScore, probability, confidence }
 *   2. Path to a plain-text file containing the full analysis output
 *   3. (optional) engine input path override — defaults to the instrument's
 *      canonical /tmp path (see ENGINE_INPUT below)
 *   --instrument=uk100  (optional flag, any position) — routes everything to
 *      the UK100 data dir/bot identity/commit prefix instead of gold's. Absent
 *      → behaves byte-identically to the original gold-only script.
 *
 * Writes (gold, default):
 *   public/data/sessions/<YYYY-MM-DD>/<HH-MM>.json
 *   public/data/sessions/index.json  (rolling 3-day window)
 * Writes (--instrument=uk100):
 *   public/data/uk100/sessions/<YYYY-MM-DD>/<HH-MM>.json
 *   public/data/uk100/sessions/index.json  (rolling 3-day window)
 *
 * Then commits and pushes to origin main so the dashboard deploys automatically.
 */

import * as fs from 'fs'
import * as os from 'os'
import * as path from 'path'
import { fileURLToPath } from 'url'
import { execSync } from 'child_process'

const __filename = fileURLToPath(import.meta.url)
const __dirname  = path.dirname(__filename)

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

// UK100-only (§6.2 of UK100-BUILD-PLAN.md) — the 15-min Opening Range
// Breakout decision-table output. Absent on gold records.
interface OrbPlaybook {
  direction:   'LONG_ONLY' | 'SHORT_ONLY' | 'BOTH_OK' | 'STAND_ASIDE'
  dayType:     'EVENT_DRIVEN' | 'TREND_EXPECTED' | 'RANGE_EXPECTED'
  reasoning:   string
  keyLevels:   { label: string; price: number }[]
  invalidation: string
  eventRisk?:  string
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
  orbPlaybook?:         OrbPlaybook | null
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
  // --instrument=uk100 can appear in any position; strip it out before
  // treating the rest of argv as the original positional args, so the gold
  // path (flag absent) parses byte-identically to before this flag existed.
  const rawArgs: string[] = []
  let instrument: 'gold' | 'uk100' = 'gold'
  for (const a of process.argv.slice(2)) {
    const m = a.match(/^--instrument=(gold|uk100)$/)
    if (m) { instrument = m[1] as 'gold' | 'uk100'; continue }
    rawArgs.push(a)
  }
  const isUk100 = instrument === 'uk100'

  const DATA_DIR   = isUk100
    ? path.join(__dirname, '../public/data/uk100/sessions')
    : path.join(__dirname, '../public/data/sessions')
  const INDEX_FILE = path.join(DATA_DIR, 'index.json')

  const metaPath     = rawArgs[0]
  const analysisPath = rawArgs[1]

  if (!metaPath || !analysisPath) {
    console.error('Usage: save-gold-session.ts <meta.json> <analysis.txt> [engine-input.json] [--instrument=uk100]')
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
  // /tmp/{gold,uk100}_session_input.json is the canonical engine input the
  // skill just assembled (STEP 0 Phase C1); require it to exist and its
  // newest M1/M5/H1 candle to be recent. No fresh engine input → no publish.
  const DEFAULT_ENGINE_INPUT = isUk100 ? '/tmp/uk100_session_input.json' : '/tmp/gold_session_input.json'
  const ENGINE_INPUT = rawArgs[2] ?? DEFAULT_ENGINE_INPUT
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

  // Rebuild the rolling index by unioning `entry` onto a given base index JSON.
  // The base is always origin/main's CURRENT index.json (see the push loop
  // below) — never the local working copy, which can be arbitrarily stale.
  function buildIndex(baseIndexJson: string): SessionIndex {
    let idx: SessionIndex = { updatedAt: '', sessions: [] }
    try { idx = JSON.parse(baseIndexJson) as SessionIndex } catch { /* empty base */ }
    idx.sessions = [
      ...idx.sessions.filter(s => s.date >= cutoffStr && s.filename !== entry.filename),
      entry,
    ].sort((a, b) => b.timestamp.localeCompare(a.timestamp))
    idx.updatedAt = now.toISOString()
    return idx
  }

  // ── Conflict-proof commit + push to main ───────────────────────────────────
  // The old approach committed on the feature branch then `git pull --rebase
  // origin main`. index.json is a rolling window that BOTH this save and the
  // concurrent hourly data-fetch workflow rewrite, so the rebase routinely hit
  // a merge conflict on index.json and left the push half-done — the session
  // file landed but the index never updated, so the dashboard showed nothing
  // (observed 2026-07-09, Haiku run). Instructions can't fix that; the push has
  // to be conflict-proof by construction.
  //
  // Fix: never rebase. Build the commit directly on top of the true tip of
  // origin/main using plumbing, so index.json is rewritten FROM origin/main's
  // copy (not merged with it) and no conflict is possible:
  //   1. fetch origin/main
  //   2. index := buildIndex(origin/main's index.json) + our entry
  //   3. seed a temp git index from origin/main's tree, `git add` exactly our
  //      two files (session + index) → the tree = origin/main's tree with those
  //      two paths overlaid, nothing else from the working tree can leak in
  //   4. commit-tree with origin/main as the sole parent (BOT_ID on commit-tree
  //      sets BOTH author and committer, so no split-identity replay)
  //   5. push the new commit to main as a PLAIN (non-force) update — a true
  //      fast-forward when origin/main hasn't moved; cleanly REJECTED (not
  //      merged) if it raced, which sends us back to step 1 on the new tip.
  const botName = isUk100 ? 'uk100-session-bot' : 'gold-session-bot'
  const BOT_ID = `-c user.name="${botName}" -c user.email="${botName}@noreply.github.com"`
  const GIT      = `git -C "${REPO_ROOT}"`
  const sessionsSubdir = isUk100 ? 'uk100/sessions' : 'sessions'
  const REL_SESSION = `xauusd-dashboard/public/data/${sessionsSubdir}/${date}/${hhmm}.json`
  const REL_INDEX   = `xauusd-dashboard/public/data/${sessionsSubdir}/index.json`
  const commitPrefix = isUk100 ? 'uk100-session' : 'gold-session'
  const TMP_INDEX   = path.join(os.tmpdir(), `gs_git_index_${process.pid}`)

  function sleep(sec: number) { try { execSync(`sleep ${sec}`) } catch { /* best effort */ } }

  let pushed = false
  let sessionCount = 0
  let shortSha = ''
  let lastErr = ''
  for (let attempt = 0; attempt < 5 && !pushed; attempt++) {
    try {
      run(`${GIT} fetch origin main`)

      // Base the index on origin/main's current copy (empty on first-ever run).
      let baseIndex = ''
      try { baseIndex = run(`${GIT} show origin/main:${REL_INDEX}`) } catch { /* no index yet */ }
      const index = buildIndex(baseIndex)
      sessionCount = index.sessions.length
      fs.writeFileSync(INDEX_FILE, JSON.stringify(index, null, 2))

      // Stage exactly our two files into a temp index seeded from origin/main.
      try { fs.rmSync(TMP_INDEX) } catch { /* not present */ }
      const withIdx = `${GIT} -c "core.hooksPath=/dev/null"`
      const IDXENV  = { ...process.env, GIT_INDEX_FILE: TMP_INDEX }
      const runIdx  = (cmd: string) => execSync(cmd, { stdio: 'pipe', env: IDXENV }).toString().trim()
      runIdx(`${withIdx} read-tree origin/main`)
      runIdx(`${withIdx} add "${REL_SESSION}" "${REL_INDEX}"`)
      const tree   = runIdx(`${withIdx} write-tree`)
      const parent = run(`${GIT} rev-parse origin/main`)
      const commit = run(`${GIT} ${BOT_ID} commit-tree ${tree} -p ${parent} -m "chore: ${commitPrefix} ${date} ${timeDisplay}"`)

      // Plain (non-force) push: fast-forward if origin/main is still `parent`,
      // rejected if it raced — never a force, so a concurrent push is never
      // clobbered. Rejection throws → we loop and rebuild on the new tip.
      run(`${GIT} push origin ${commit}:main`)
      shortSha = commit.slice(0, 7)
      pushed = true
    } catch (err) {
      lastErr = (err as Error).message
      if (attempt < 4) sleep(1 + attempt)  // brief backoff before rebuilding on the new tip
    } finally {
      try { fs.rmSync(TMP_INDEX) } catch { /* */ }
    }
  }

  if (pushed) {
    console.log(`Index updated (${sessionCount} session${sessionCount !== 1 ? 's' : ''}, last ${MAX_DAYS} days)`)
    console.log(`Committed and pushed to main (${shortSha}) — dashboard updates after GitHub Actions deploys (~1-2 min).`)
  } else {
    console.error('Git push to main failed after 5 attempts:', lastErr)
    console.error(`Session file saved locally at ${path.relative(REPO_ROOT, sessionFile)}. Retry the save, or push manually.`)
    process.exit(1)
  }
}

main()
