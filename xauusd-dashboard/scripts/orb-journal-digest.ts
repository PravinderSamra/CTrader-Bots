#!/usr/bin/env tsx
/**
 * ORB journal digest (J3, UK100-ORB-JOURNAL-DESIGN.md §4.3) — print a human
 * markdown table of a day's ORB intel reads (time, stance, top signal, verdict,
 * to-close return) from public/data/uk100/orb-journal/YYYY-MM-DD.json.
 * On-demand only; no workflow wiring.
 *
 * Usage (from xauusd-dashboard/):
 *   npx tsx scripts/orb-journal-digest.ts              # today (London)
 *   npx tsx scripts/orb-journal-digest.ts 2026-07-16   # a specific day
 */

import * as fs from 'fs'
import * as path from 'path'
import { fileURLToPath } from 'url'
import type { OrbJournalDay } from '../src/types/uk100'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const JOURNAL_DIR = path.join(__dirname, '../public/data/uk100/orb-journal')

function ukOffsetHours(d: Date): number {
  const m = d.getUTCMonth() + 1
  const day = d.getUTCDate()
  if (m > 3 && m < 10) return 1
  if (m === 3 && day >= 25) return 1
  if (m === 10 && day < 25) return 1
  return 0
}
function todayLondon(): string {
  const now = new Date()
  return new Date(now.getTime() + ukOffsetHours(now) * 3_600_000).toISOString().slice(0, 10)
}

function main() {
  const date = process.argv[2] ?? todayLondon()
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) { console.error(`Bad date "${date}" — expected YYYY-MM-DD.`); process.exit(1) }
  const file = path.join(JOURNAL_DIR, `${date}.json`)
  let day: OrbJournalDay
  try { day = JSON.parse(fs.readFileSync(file, 'utf8')) as OrbJournalDay }
  catch { console.error(`No ORB journal for ${date} (${path.relative(process.cwd(), file)}).`); process.exit(1) }

  console.log(`# ORB intel journal — ${date}  (${day.entries.length} entries)\n`)
  console.log('| Time | Mode | Stance | Top signal | Verdict | toClose% |')
  console.log('|---|---|---|---|---|---|')
  for (const e of day.entries) {
    const top = e.signals[0] ? `${e.signals[0].rule} ${e.signals[0].source}` : '—'
    const verdict = e.outcome?.verdict ?? '·'   // '·' = not yet resolved
    const toClose = e.outcome && e.outcome.verdict !== 'UNSCORABLE' ? `${e.outcome.toClosePct >= 0 ? '+' : ''}${e.outcome.toClosePct}` : '—'
    console.log(`| ${e.londonTime} | ${e.mode} | ${e.stance} | ${top} | ${verdict} | ${toClose} |`)
  }

  const resolved = day.entries.filter(e => e.outcome && e.outcome.verdict !== 'UNSCORABLE' && e.outcome.verdict != null)
  const right = resolved.filter(e => e.outcome!.verdict === 'RIGHT').length
  const wrong = resolved.filter(e => e.outcome!.verdict === 'WRONG').length
  const flat = resolved.filter(e => e.outcome!.verdict === 'FLAT').length
  console.log(`\nResolved directional calls: ${resolved.length}  ·  RIGHT ${right} / WRONG ${wrong} / FLAT ${flat}`)
}

main()
