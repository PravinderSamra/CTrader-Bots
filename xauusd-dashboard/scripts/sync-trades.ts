#!/usr/bin/env tsx
/**
 * Pravzella trade sync — pulls closed positions from the cTrader MCP server and
 * upserts them into Supabase as reconstructed trades (cTrader's `get_deals` only
 * returns raw fills, not P&L, so each closed position is rebuilt from its fills).
 *
 * Runs on a schedule via .github/workflows/xauusd-trade-sync.yml. Always re-scans a
 * rolling lookback window (default 35 days, see LOOKBACK_DAYS) rather than tracking a
 * high-water mark — a position opened just before a previous sync's cutoff and closed
 * after it would otherwise have its opening fill permanently missed, making it
 * unreconstructable. Re-scanning is cheap (this account trades tens of positions a
 * month) and upserts are idempotent on (user_id, position_id), so this is simply more
 * correct with no real cost.
 *
 * Usage:
 *   npx tsx scripts/sync-trades.ts             # writes to Supabase
 *   npx tsx scripts/sync-trades.ts --dry-run    # reconstructs + prints, no Supabase calls,
 *                                                 no SUPABASE_* env vars required
 */

const DRY_RUN = process.argv.includes('--dry-run')

const CTRADER_URL   = process.env.CTRADER_MCP_URL   || 'https://mcp.ctrader.com/trading/mcp'
const CTRADER_TOKEN = process.env.CTRADER_MCP_TOKEN || ''

const SUPABASE_URL         = process.env.SUPABASE_URL || ''
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY || ''
const SUPABASE_USER_ID     = process.env.SUPABASE_USER_ID || ''

const LOOKBACK_DAYS = Number(process.env.TRADE_SYNC_LOOKBACK_DAYS || 35)
const WINDOW_HOURS  = 24 * 29 // stay under cTrader's 720h/30-day cap per call

// ── cTrader MCP protocol (mirrors fetch-static-data.ts's mcpFetch/callTool) ────────

async function mcpFetch(body: object, sessionId?: string): Promise<{ data: unknown; sessionId: string | null }> {
  const headers: Record<string, string> = {
    Authorization: `Bearer ${CTRADER_TOKEN}`,
    'Content-Type': 'application/json',
    Accept: 'application/json, text/event-stream',
  }
  if (sessionId) headers['Mcp-Session-Id'] = sessionId

  const ctrl = new AbortController()
  const timer = setTimeout(() => ctrl.abort(), 30000)
  try {
    const res = await fetch(CTRADER_URL, { method: 'POST', headers, body: JSON.stringify(body), signal: ctrl.signal })
    const newSid = res.headers.get('Mcp-Session-Id') ?? res.headers.get('mcp-session-id') ?? sessionId ?? null
    const text = await res.text()

    if (!res.ok) {
      console.error(`CTrader MCP HTTP ${res.status}: ${text.slice(0, 300)}`)
      return { data: null, sessionId: newSid }
    }

    for (const line of text.split('\n')) {
      if (line.startsWith('data: ')) {
        try { return { data: JSON.parse(line.slice(6)), sessionId: newSid } } catch { /* next line */ }
      }
    }
    try { return { data: JSON.parse(text), sessionId: newSid } } catch { /* ignore */ }
    return { data: null, sessionId: newSid }
  } finally {
    clearTimeout(timer)
  }
}

let sessionId: string | null = null

async function initSession(): Promise<void> {
  const { data, sessionId: sid } = await mcpFetch({
    jsonrpc: '2.0', id: 0, method: 'initialize',
    params: { protocolVersion: '2024-11-05', capabilities: {}, clientInfo: { name: 'pravzella-sync', version: '1.0' } },
  })
  if (!(data as Record<string, unknown>)?.result) throw new Error('CTrader MCP init failed — no result in response')
  sessionId = sid
  await mcpFetch({ jsonrpc: '2.0', method: 'notifications/initialized', params: {} }, sessionId ?? undefined)
}

async function callTool(name: string, args: object): Promise<unknown> {
  const { data } = await mcpFetch({ jsonrpc: '2.0', id: 1, method: 'tools/call', params: { name, arguments: args } }, sessionId ?? undefined)
  const result = (data as Record<string, unknown>)?.result as Record<string, unknown> | undefined
  const content = result?.content as Array<{ type: string; text: string }> | undefined
  if (content?.[0]?.type === 'text') {
    try { return JSON.parse(content[0].text) } catch { return null }
  }
  return null
}

// ── Symbol resolution ───────────────────────────────────────────────────────

const SUFFIX_RE = /(_SBE|_SB|-F_SBE|-F_SB|-PERP_SBE|-PERP_SB|-PERP|-F)$/

async function buildSymbolMap(): Promise<Map<number, string>> {
  const raw = await callTool('get_symbols', {})
  const symbols = (raw as { symbols?: Array<{ symbolName: string; symbolId: number }> })?.symbols ?? []
  const map = new Map<number, string>()
  for (const s of symbols) {
    if (!s.symbolName || s.symbolId == null) continue
    map.set(s.symbolId, s.symbolName.replace(SUFFIX_RE, '').toUpperCase())
  }
  return map
}

// ── Deal fetching ───────────────────────────────────────────────────────────

interface Deal {
  dealId: number
  positionId: number
  symbolId: number
  tradeSide: 'BUY' | 'SELL'
  volume: number
  filledVolume: number
  executionPrice: number
  executionTimestamp: number
  dealStatus: string
  commission: number
}

async function fetchAllDeals(fromMs: number, toMs: number): Promise<Deal[]> {
  const all: Deal[] = []
  let windowStart = fromMs
  while (windowStart < toMs) {
    const windowEnd = Math.min(windowStart + WINDOW_HOURS * 3_600_000, toMs)
    const raw = await callTool('get_deals', {
      fromTimestamp: new Date(windowStart).toISOString(),
      toTimestamp: new Date(windowEnd).toISOString(),
      maxRows: 1000,
    })
    const deals = (raw as { deals?: Deal[] })?.deals ?? []
    all.push(...deals.filter(d => d.dealStatus === 'FILLED'))
    windowStart = windowEnd
  }
  // De-dupe (window edges can overlap by construction)
  const byId = new Map(all.map(d => [d.dealId, d]))
  return [...byId.values()]
}

// ── Trade reconstruction ────────────────────────────────────────────────────

interface ReconstructedTrade {
  position_id: number
  symbol: string
  direction: 'LONG' | 'SHORT'
  volume: number
  entry_price: number
  exit_price: number
  entry_time: string
  exit_time: string
  gross_pnl: number
  commission: number
  net_pnl: number
}

function round2(n: number): number {
  return Math.round(n * 100) / 100
}

function reconstructTrades(deals: Deal[], symbolMap: Map<number, string>): ReconstructedTrade[] {
  const byPosition = new Map<number, Deal[]>()
  for (const d of deals) {
    if (!byPosition.has(d.positionId)) byPosition.set(d.positionId, [])
    byPosition.get(d.positionId)!.push(d)
  }

  const trades: ReconstructedTrade[] = []

  for (const [positionId, group] of byPosition) {
    const sorted = [...group].sort((a, b) => a.executionTimestamp - b.executionTimestamp)
    const direction: 'LONG' | 'SHORT' = sorted[0].tradeSide === 'BUY' ? 'LONG' : 'SHORT'
    const openSide = sorted[0].tradeSide

    let runningSize = 0
    let entrySum = 0, entryVol = 0
    let exitSum = 0, exitVol = 0
    let commission = 0
    let closed = false

    for (const fill of sorted) {
      const signedSize = fill.tradeSide === 'BUY' ? fill.filledVolume : -fill.filledVolume
      commission += fill.commission
      if (fill.tradeSide === openSide) {
        entrySum += fill.executionPrice * fill.filledVolume
        entryVol += fill.filledVolume
      } else {
        exitSum += fill.executionPrice * fill.filledVolume
        exitVol += fill.filledVolume
      }
      runningSize += signedSize
      if (runningSize === 0 && entryVol > 0 && exitVol > 0) {
        closed = true
        break
      }
    }

    if (!closed) continue // still open — skip this pass, will be picked up once fully closed

    const avgEntry = entrySum / entryVol
    const avgExit = exitSum / exitVol
    const stake = entryVol / 100 // GBP per point
    const grossPnl = (direction === 'LONG' ? avgExit - avgEntry : avgEntry - avgExit) * stake
    const netPnl = grossPnl - commission

    const symbol = symbolMap.get(sorted[0].symbolId) ?? `SYM_${sorted[0].symbolId}`
    const entryTime = sorted.find(f => f.tradeSide === openSide)!.executionTimestamp
    const lastCloseFill = [...sorted].reverse().find(f => f.tradeSide !== openSide)!

    trades.push({
      position_id: positionId,
      symbol,
      direction,
      volume: round2(stake),
      entry_price: avgEntry,
      exit_price: avgExit,
      entry_time: new Date(entryTime).toISOString(),
      exit_time: new Date(lastCloseFill.executionTimestamp).toISOString(),
      gross_pnl: round2(grossPnl),
      commission: round2(commission),
      net_pnl: round2(netPnl),
    })
  }

  return trades.sort((a, b) => a.exit_time.localeCompare(b.exit_time))
}

// ── Supabase upsert ─────────────────────────────────────────────────────────

async function upsertTrades(trades: ReconstructedTrade[]): Promise<void> {
  if (trades.length === 0) return
  const rows = trades.map(t => ({ ...t, user_id: SUPABASE_USER_ID, source: 'ctrader_sync' }))
  const url = `${SUPABASE_URL}/rest/v1/trades?on_conflict=user_id,position_id`
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      apikey: SUPABASE_SERVICE_KEY,
      Authorization: `Bearer ${SUPABASE_SERVICE_KEY}`,
      'Content-Type': 'application/json',
      Prefer: 'resolution=merge-duplicates,return=minimal',
    },
    body: JSON.stringify(rows),
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`Supabase upsert failed: ${res.status} ${text.slice(0, 500)}`)
  }
}

// ── Main ─────────────────────────────────────────────────────────────────────

async function main() {
  console.log(`=== Pravzella trade sync ${DRY_RUN ? '(dry run)' : ''} ===`)

  if (!CTRADER_TOKEN) {
    console.error('CTRADER_MCP_TOKEN not set — nothing to sync.')
    process.exit(1)
  }
  if (!DRY_RUN && (!SUPABASE_URL || !SUPABASE_SERVICE_KEY || !SUPABASE_USER_ID)) {
    console.error('SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY / SUPABASE_USER_ID must be set (or pass --dry-run).')
    process.exit(1)
  }

  await initSession()
  const symbolMap = await buildSymbolMap()
  console.log(`Loaded ${symbolMap.size} symbols`)

  const toMs = Date.now()
  const fromMs = toMs - LOOKBACK_DAYS * 24 * 3_600_000
  const deals = await fetchAllDeals(fromMs, toMs)
  console.log(`Fetched ${deals.length} filled deals over the last ${LOOKBACK_DAYS} days`)

  const trades = reconstructTrades(deals, symbolMap)
  console.log(`Reconstructed ${trades.length} closed trades`)

  if (DRY_RUN) {
    console.log(JSON.stringify(trades, null, 2))
    return
  }

  await upsertTrades(trades)
  console.log(`Upserted ${trades.length} trades to Supabase`)
}

main().catch(err => {
  console.error('Sync failed:', err)
  process.exit(1)
})
