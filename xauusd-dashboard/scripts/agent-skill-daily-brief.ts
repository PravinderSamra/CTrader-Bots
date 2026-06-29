#!/usr/bin/env tsx
/**
 * XAUUSD Daily Brief — Standalone Agent Skill
 *
 * Usage:
 *   npx tsx scripts/agent-skill-daily-brief.ts
 *   npx tsx scripts/agent-skill-daily-brief.ts --save
 *
 * Reads env vars: ANTHROPIC_API_KEY, VITE_FINNHUB_KEY (optional)
 * Outputs briefing JSON to stdout; --save writes to briefings/YYYY-MM-DD.json
 */

import * as fs from 'fs'
import * as path from 'path'
import * as https from 'https'

const ANTHROPIC_KEY = process.env.ANTHROPIC_API_KEY ?? process.env.VITE_ANTHROPIC_KEY ?? ''
const FINNHUB_KEY   = process.env.VITE_FINNHUB_KEY ?? ''
const SAVE_FLAG     = process.argv.includes('--save')

// ── HTTP helpers ───────────────────────────────────────────────────────────

function httpGet(url: string, headers: Record<string,string> = {}): Promise<string> {
  return new Promise((resolve, reject) => {
    const opts = new URL(url)
    const req = https.get({
      hostname: opts.hostname,
      path: opts.pathname + opts.search,
      headers: { 'User-Agent': 'xauusd-brief-agent/1.0', ...headers },
    }, res => {
      let data = ''
      res.on('data', c => { data += c })
      res.on('end', () => resolve(data))
    })
    req.on('error', reject)
    req.setTimeout(15000, () => { req.destroy(); reject(new Error('Timeout')) })
  })
}

function httpsPost(url: string, body: string, headers: Record<string,string>): Promise<string> {
  return new Promise((resolve, reject) => {
    const opts = new URL(url)
    const req = https.request({
      hostname: opts.hostname,
      path: opts.pathname,
      method: 'POST',
      headers: { 'Content-Length': Buffer.byteLength(body), ...headers },
    }, res => {
      let data = ''
      res.on('data', c => { data += c })
      res.on('end', () => resolve(data))
    })
    req.on('error', reject)
    req.setTimeout(60000, () => { req.destroy(); reject(new Error('Timeout')) })
    req.write(body)
    req.end()
  })
}

// ── Load snapshot (if available) ───────────────────────────────────────────

const SNAPSHOT_PATH = path.join(__dirname, '../public/data/daily-snapshot.json')

// ── Fetch calendar from Finnhub ────────────────────────────────────────────

async function fetchCalendar(): Promise<Array<{ time: string; event: string; impact: string; forecast: unknown; previous: unknown }>> {
  if (!FINNHUB_KEY) return []
  try {
    const today = new Date().toISOString().slice(0, 10)
    const raw = await httpGet(`https://finnhub.io/api/v1/calendar/economic?from=${today}&to=${today}&token=${FINNHUB_KEY}`)
    const data = JSON.parse(raw) as { economicCalendar?: Array<{ event: string; time?: string; impact?: string; estimate?: unknown; prev?: unknown }> }
    return (data.economicCalendar ?? [])
      .slice(0, 8)
      .map(e => ({ time: e.time?.slice(11, 16) ?? '', event: e.event, impact: e.impact ?? 'LOW', forecast: e.estimate ?? null, previous: e.prev ?? null }))
  } catch {
    return []
  }
}

async function fetchHeadlines(): Promise<string[]> {
  if (!FINNHUB_KEY) return []
  try {
    const raw = await httpGet(`https://finnhub.io/api/v1/news?category=general&token=${FINNHUB_KEY}`)
    const data = JSON.parse(raw) as Array<{ headline: string }>
    const kw = ['gold', 'fed', 'inflation', 'yield', 'dollar', 'rate']
    return data.filter(a => kw.some(k => a.headline.toLowerCase().includes(k))).slice(0, 5).map(a => a.headline)
  } catch {
    return []
  }
}

// ── System prompt ──────────────────────────────────────────────────────────

const SYSTEM_PROMPT = `You are a senior gold trading analyst and market intelligence advisor.
Your job is to write a daily intelligence briefing for a beginner day trader who uses ICT / Smart Money Concepts methodology to trade XAUUSD.

Write a SINGLE flowing briefing paragraph (200–300 words) using PLAIN, BEGINNER-FRIENDLY language.

Your briefing MUST cover: regime/dominant driver, overnight context, directional bias with reasoning, confidence score (X/10), event risk, key levels, trade integration guidance.

End with one sentence a beginner can screenshot and remember.

Return your response as JSON:
{ "biasScore": number from -5 to +5, "biasLabel": "BEARISH" | "NEUTRAL" | "BULLISH", "confidence": number 1-10, "briefing": "your paragraph" }`

// ── Main ───────────────────────────────────────────────────────────────────

async function main() {
  if (!ANTHROPIC_KEY) {
    console.error('Error: ANTHROPIC_API_KEY not set')
    process.exit(1)
  }

  let snapshot: Record<string, unknown> = {}
  try {
    snapshot = JSON.parse(fs.readFileSync(SNAPSHOT_PATH, 'utf8'))
  } catch {
    process.stderr.write('Warning: daily-snapshot.json not found — macro data unavailable\n')
  }

  const [calendar, headlines] = await Promise.all([fetchCalendar(), fetchHeadlines()])

  const dataPayload = {
    timestamp: new Date().toISOString(),
    session: (() => {
      const h = new Date().getUTCHours()
      if (h >= 13 && h < 16) return 'OVERLAP'
      if (h >= 8  && h < 16) return 'LONDON'
      if (h >= 16 && h < 21) return 'NEW_YORK'
      return 'ASIAN'
    })(),
    macro: snapshot,
    calendar,
    headlines,
    note: 'Real-time prices unavailable in agent skill mode — macro context from daily snapshot',
  }

  const reqBody = JSON.stringify({
    model: 'claude-sonnet-4-6',
    max_tokens: 1200,
    system: SYSTEM_PROMPT,
    messages: [{ role: 'user', content: `Today's data:\n\n${JSON.stringify(dataPayload, null, 2)}` }],
  })

  process.stderr.write('Calling Anthropic API...\n')
  const raw = await httpsPost('https://api.anthropic.com/v1/messages', reqBody, {
    'x-api-key': ANTHROPIC_KEY,
    'anthropic-version': '2023-06-01',
    'content-type': 'application/json',
  })

  const res = JSON.parse(raw) as { content?: Array<{ type: string; text: string }>; error?: { message: string } }
  if (res.error) { console.error('Anthropic error:', res.error.message); process.exit(1) }

  const text = res.content?.find(c => c.type === 'text')?.text ?? ''
  const cleaned = text.replace(/^```json?\s*/i, '').replace(/\s*```$/, '').trim()
  const briefing = JSON.parse(cleaned) as { biasScore: number; biasLabel: string; confidence: number; briefing: string }
  const result = { ...briefing, generatedAt: new Date().toISOString() }

  const output = JSON.stringify(result, null, 2)
  console.log(output)

  if (SAVE_FLAG) {
    const dir = path.join(__dirname, '../briefings')
    fs.mkdirSync(dir, { recursive: true })
    const file = path.join(dir, `${new Date().toISOString().slice(0, 10)}.json`)
    fs.writeFileSync(file, output)
    process.stderr.write(`Briefing saved to ${file}\n`)
  }
}

main().catch(err => { console.error(err); process.exit(1) })
