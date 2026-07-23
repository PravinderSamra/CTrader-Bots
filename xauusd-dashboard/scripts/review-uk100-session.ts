#!/usr/bin/env tsx
/**
 * Post-session review — grade a saved UK100 brief against what price actually
 * did, and print a human-readable scorecard. This automates the manual "pull
 * the tape, compare to the brief" review done by hand in the 2026-07-23
 * assessment (#4): bias-direction accuracy, the trade result (incl. whether a
 * WAIT entry zone actually filled), the price path (MFE/MAE, session close),
 * and level sanity (did the draw / invalidation get hit; is T1 == the trigger).
 *
 * READ-ONLY — it never writes; the resolver (resolve-uk100-sessions.ts) owns the
 * persisted outcome. Use this for an on-demand look, including before the
 * resolver's window has closed.
 *
 * Usage (from xauusd-dashboard/):
 *   npx tsx scripts/review-uk100-session.ts               # newest brief
 *   npx tsx scripts/review-uk100-session.ts 2026-07-23/08-56.json
 *
 * Requires CTRADER_MCP_URL / CTRADER_MCP_TOKEN.
 */

import * as fs from 'fs'
import * as path from 'path'
import { fileURLToPath } from 'url'
import { CTraderClient, KNOWN_SYMBOL_IDS, PIP_DIGITS, type Trendbar } from './lib/ctrader'
import { cashCloseCutoffMs, recordLean, biasVerdictFor, firstFillIndex, classify, classifyHits } from './resolve-uk100-sessions'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const DATA_DIR = path.join(__dirname, '../public/data/uk100/sessions')
const UK100_ID = KNOWN_SYMBOL_IDS.UK100
const SCALE = 10 ** (PIP_DIGITS.UK100 ?? 5)
const r1 = (n: number) => Math.round(n * 10) / 10

function newestRecord(): string | null {
  if (!fs.existsSync(DATA_DIR)) return null
  const days = fs.readdirSync(DATA_DIR).filter(d => /^\d{4}-\d{2}-\d{2}$/.test(d)).sort()
  for (const day of days.reverse()) {
    const files = fs.readdirSync(path.join(DATA_DIR, day)).filter(f => f.endsWith('.json')).sort()
    if (files.length) return `${day}/${files[files.length - 1]}`
  }
  return null
}

async function main() {
  const arg = process.argv.find(a => a.endsWith('.json'))
  const rel = arg ?? newestRecord()
  if (!rel) { console.error('No UK100 session records found.'); process.exit(1) }
  const rec = JSON.parse(fs.readFileSync(path.join(DATA_DIR, rel), 'utf8'))

  const ts = Date.parse(rec.timestamp)
  const cutoffMs = Math.min(ts + 8 * 3600_000, cashCloseCutoffMs(ts))
  const now = Date.now()
  const toMs = Math.min(cutoffMs, now)
  const windowComplete = now >= cutoffMs

  const client = new CTraderClient()
  if (!(await client.init())) { console.error('CTrader MCP unavailable — cannot review.'); process.exit(1) }
  const raw = await client.getTrendbars(UK100_ID, 'H_1', ts, toMs)
  if (raw.length === 0) { console.error('No bars returned for the review window.'); process.exit(1) }
  const bars = raw.map((b: Trendbar) => ({ open: b.open / SCALE, high: b.high / SCALE, low: b.low / SCALE, close: b.close / SCALE }))

  const entry = rec.priceAtAnalysis as number
  const hi = Math.max(...bars.map(b => b.high))
  const lo = Math.min(...bars.map(b => b.low))
  const close = bars[bars.length - 1].close
  const ti = rec.tradeIdea ?? {}
  const lean = recordLean(rec.bias, ti.direction)

  const L: string[] = []
  L.push(`\n══ UK100 SESSION REVIEW ══ ${rec.date} ${rec.time} — ${rel}`)
  L.push(`Brief: bias ${rec.bias} (${rec.biasScore ?? '?'}) · prob ${rec.probability}% · ${ti.direction ?? '—'} ${ti.status ?? ''} · playbook ${rec.orbPlaybook?.direction ?? '—'}`)
  L.push(`Window: ${new Date(ts).toISOString()} → ${new Date(toMs).toISOString()} (${windowComplete ? 'session closed' : 'STILL OPEN — provisional'})`)
  L.push('')

  // 1) Bias direction
  if (lean && entry != null) {
    const chgPct = Math.round((close - entry) / entry * 10000) / 100
    const verdict = biasVerdictFor(lean, entry, close)
    L.push(`DIRECTION  lean ${lean} · price @ analysis ${r1(entry)} → close ${r1(close)} (${chgPct >= 0 ? '+' : ''}${chgPct}%) → ${verdict}`)
  } else {
    L.push(`DIRECTION  no directional lean to grade`)
  }

  // 2) Price path
  L.push(`PATH       session H ${r1(hi)} / L ${r1(lo)} · MFE ${r1(lean === 'BEARISH' ? entry - lo : hi - entry)}pt / MAE ${r1(lean === 'BEARISH' ? hi - entry : entry - lo)}pt (in lean direction)`)

  // 3) Trade result
  const dirOk = ti.direction === 'LONG' || ti.direction === 'SHORT'
  if (dirOk && ti.status === 'ACTIVE') {
    const base = classify(rec, bars, now, cutoffMs, entry)
    L.push(`TRADE      ACTIVE ${ti.direction} → ${base?.result ?? 'pending'}`)
  } else if (dirOk && ti.status === 'WAIT' && ti.entryLow != null && ti.entryHigh != null) {
    const fill = firstFillIndex(ti.direction, ti.entryLow, ti.entryHigh, bars)
    if (fill === -1) {
      L.push(`TRADE      WAIT ${ti.direction} [${ti.entryLow}–${ti.entryHigh}] → entry zone NEVER filled`)
    } else {
      const fillEntry = ti.direction === 'LONG' ? ti.entryHigh : ti.entryLow
      const base = classify(rec, bars.slice(fill), now, cutoffMs, fillEntry)
      const hits = ti.targets?.length && ti.stop != null ? classifyHits(ti.direction, ti.targets, ti.stop, raw.slice(fill)) : []
      L.push(`TRADE      WAIT ${ti.direction} FILLED @ bar ${fill} (${fillEntry}) → ${base?.result ?? 'pending'}${hits.length ? ` [${hits.map(h => h.level).join('→')}]` : ''}`)
    }
  } else {
    L.push(`TRADE      ${ti.status ?? 'NO_TRADE'} — nothing to score as a trade (bias grade above still applies)`)
  }

  // 4) Level sanity
  const draw = rec.drawOnLiquidity, inval = rec.invalidation
  if (draw != null) {
    const hit = lean === 'BEARISH' ? lo <= draw : hi >= draw
    L.push(`DRAW       ${r1(draw)} → ${hit ? 'reached' : 'not reached'}`)
    if (ti.direction && (ti.entryLow === draw || ti.entryHigh === draw)) L.push(`  ⚠ draw equals the entry/trigger level — T1 should sit BEYOND the trigger (skill rule)`)
  }
  if (inval != null) {
    const tripped = lean === 'BEARISH' ? hi >= inval : lo <= inval
    L.push(`INVAL      ${r1(inval)} → ${tripped ? 'TAGGED (check for a false-break wick)' : 'held'}`)
  }
  L.push('')
  console.log(L.join('\n'))
}

main().catch(err => { console.error('review-uk100-session failed:', err); process.exit(1) })
