/**
 * Shared cTrader MCP client — the canonical low-level transport used by both
 * fetch-static-data.ts (hourly snapshot) and resolve-gold-sessions.ts (outcome
 * resolver). Extracted so the proven SSE-parsing logic lives in one place
 * rather than drifting between copies.
 *
 * Auth: reads CTRADER_MCP_URL / CTRADER_MCP_TOKEN from the environment (same as
 * the workflow already provides). No token → callers should detect the empty
 * token and skip.
 */

// .trim() both — a trailing newline in the GitHub secret would corrupt the URL
// or make the Authorization Bearer header invalid.
export const CTRADER_URL   = (process.env.CTRADER_MCP_URL   || 'https://mcp.ctrader.com/trading/mcp').trim()
export const CTRADER_TOKEN = (process.env.CTRADER_MCP_TOKEN || '').trim()

// All cTrader _SB spread-bet instruments use 10^5 pipettes (verified empirically).
export const PIP_DIGITS: Record<string, number> = {
  XAUUSD: 5, XAGUSD: 5,
  EURUSD: 5, USDJPY: 5, USDCHF: 5, USDCNH: 5,
  GBPUSD: 5, USDCAD: 5, USDSEK: 5,
  US500: 5, GER40: 5, UK100: 5,
}

// Broker-assigned symbolIds. This account trades the _SB (spread-bet) variants;
// XAUUSD_SB = 241 (confirmed 2026-07-07 — the old 41 does NOT resolve and returns
// no spot). Any entry that drifts is self-healed at runtime by fetchCTraderPrices,
// which re-resolves unpriced symbols via get_symbols (preferring enabled _SB IDs).
export const KNOWN_SYMBOL_IDS: Record<string, number> = {
  XAUUSD: 241, XAGUSD: 42,
  EURUSD: 1, USDJPY: 4, USDCHF: 6, USDCNH: 60,
  GBPUSD: 2, USDCAD: 8, USDSEK: 29,
  US500: 115, GER40: 110, UK100: 113,
}

/**
 * One MCP round-trip. Handles the SSE framing where a single event's payload
 * can span multiple physical "data:" lines for large results — rejoin all data
 * lines within an event before parsing (parsing only the first line silently
 * fails on any multi-line payload).
 */
export async function mcpFetch(body: object, sessionId?: string): Promise<{ data: unknown; sessionId: string | null }> {
  const headers: Record<string, string> = {
    Authorization: `Bearer ${CTRADER_TOKEN}`,
    'Content-Type': 'application/json',
    Accept: 'application/json, text/event-stream',
  }
  if (sessionId) headers['Mcp-Session-Id'] = sessionId

  const ctrl = new AbortController()
  const timer = setTimeout(() => ctrl.abort(), 20000)
  try {
    const res = await fetch(CTRADER_URL, { method: 'POST', headers, body: JSON.stringify(body), signal: ctrl.signal })
    const newSid = res.headers.get('Mcp-Session-Id') ?? res.headers.get('mcp-session-id') ?? sessionId ?? null
    const text = await res.text()

    if (!res.ok) {
      console.error(`CTrader MCP HTTP ${res.status}: ${text.slice(0, 200)}`)
      return { data: null, sessionId: newSid }
    }

    for (const event of text.split(/\r?\n\r?\n/)) {
      const dataLines = event.split(/\r?\n/).filter(l => l.startsWith('data:')).map(l => l.replace(/^data:\s?/, ''))
      if (dataLines.length === 0) continue
      try { return { data: JSON.parse(dataLines.join('\n')), sessionId: newSid } } catch { /* try next event */ }
    }
    try { return { data: JSON.parse(text), sessionId: newSid } } catch { /* ignore */ }
    if (text.length > 0) {
      console.error(`CTrader MCP: failed to parse response (${text.length} chars): ${text.slice(0, 200)}${text.length > 200 ? '…' : ''}`)
    }
    return { data: null, sessionId: newSid }
  } finally {
    clearTimeout(timer)
  }
}

export interface Trendbar {
  open: number
  high: number
  low: number
  close: number
  volume: number
}

/**
 * Stateful client: init() once, then callTool / getTrendbars. Wraps the
 * JSON-RPC handshake and the tool-result content unwrapping.
 */
export class CTraderClient {
  private sessionId: string | null = null

  hasToken(): boolean {
    return CTRADER_TOKEN.length > 0
  }

  async init(): Promise<boolean> {
    if (!this.hasToken()) return false
    const { data, sessionId } = await mcpFetch({
      jsonrpc: '2.0', id: 0, method: 'initialize',
      params: { protocolVersion: '2024-11-05', capabilities: {}, clientInfo: { name: 'xauusd-resolver', version: '1.0' } },
    })
    if (!(data as Record<string, unknown>)?.result) return false
    this.sessionId = sessionId
    await mcpFetch({ jsonrpc: '2.0', method: 'notifications/initialized', params: {} }, this.sessionId ?? undefined)
    return true
  }

  async callTool(name: string, args: object): Promise<unknown> {
    const { data } = await mcpFetch(
      { jsonrpc: '2.0', id: 1, method: 'tools/call', params: { name, arguments: args } },
      this.sessionId ?? undefined,
    )
    const parsed = data as Record<string, unknown> | undefined
    if (parsed?.error) {
      console.error(`CTrader MCP: ${name} returned JSON-RPC error: ${JSON.stringify(parsed.error).slice(0, 300)}`)
      return null
    }
    const result = parsed?.result as Record<string, unknown> | undefined
    const content = result?.content as Array<{ type: string; text: string }> | undefined
    if (content?.[0]?.type === 'text') {
      try { return JSON.parse(content[0].text) }
      catch (e) { console.error(`CTrader MCP: ${name} content JSON.parse failed: ${(e as Error).message}`); return null }
    }
    return null
  }

  /**
   * Fetch trendbars for a symbol over [fromMs, toMs]. Returns bars in the raw
   * pipette scale, ascending by time. Divide by 10^pipDigits for display prices.
   */
  async getTrendbars(symbolId: number, period: string, fromMs: number, toMs: number): Promise<Trendbar[]> {
    const raw = await this.callTool('get_trendbars', {
      symbolId, period,
      fromTimestamp: new Date(fromMs).toISOString(),
      toTimestamp: new Date(toMs).toISOString(),
    })
    const bars = ((raw as { trendbars?: unknown[] })?.trendbars
      ?? (raw as { bars?: unknown[] })?.bars ?? []) as Array<Record<string, number>>
    return bars
      .filter(b => b.high != null && b.low != null)
      .map(b => ({
        open:  b.open ?? b.close ?? 0,
        high:  b.high,
        low:   b.low,
        close: b.close ?? b.open ?? 0,
        volume: b.volume ?? 0,
      }))
  }
}
