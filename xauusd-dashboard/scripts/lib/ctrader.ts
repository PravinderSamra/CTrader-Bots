/**
 * Shared cTrader MCP client — the canonical low-level transport used by both
 * fetch-static-data.ts (hourly snapshot) and resolve-gold-sessions.ts (outcome
 * resolver). Extracted so the proven SSE-parsing logic lives in one place
 * rather than drifting between copies.
 *
 * Auth: reads CTRADER_MCP_URL / CTRADER_MCP_TOKEN from the environment (same as
 * the workflow already provides). No token → callers should detect the empty
 * token and skip.
 *
 * Session resilience (UK100-V2-PLAN.md Phase A1): the cTrader MCP sits behind a
 * load balancer, and the session created by `initialize` lives on one backend —
 * plain per-request `fetch()` calls round-robin across backends, so any request
 * landing on a different backend than the one holding the session 404s with
 * "Session not found; re-initialize" (observed live 2026-07-11, alternating
 * success/failure across sequential calls). Two independent mitigations:
 *   1. `dispatcher` pins every request through undici's keep-alive Agent with
 *      `connections: 1`, so all requests from one process serialise onto the
 *      SAME TCP connection (mirrors ctrader_http_fetch.py's Lesson-1 fix).
 *   2. `CTraderClient.callTool` detects the session-loss signature and
 *      transparently re-initializes + replays, bounded at 3 total attempts.
 */

import { Agent } from 'undici'

// .trim() both — a trailing newline in the GitHub secret would corrupt the URL
// or make the Authorization Bearer header invalid.
export const CTRADER_URL   = (process.env.CTRADER_MCP_URL   || 'https://mcp.ctrader.com/trading/mcp').trim()
export const CTRADER_TOKEN = (process.env.CTRADER_MCP_TOKEN || '').trim()

// Single pinned connection per process — see the module docstring. Shared across
// every mcpFetch call (both the CTraderClient class and fetch-static-data.ts's
// own inline closure), since it's keyed on nothing but the process lifetime.
const pinnedAgent = new Agent({ keepAliveTimeout: 30_000, connections: 1 })

// All cTrader _SB spread-bet instruments use 10^5 pipettes (verified empirically).
// The plain-CFD symbols added for UK100 (NAS100/BRENT/COPPER/VIX/USDX/EURGBP) were
// verified 2026-07-10 to divide by the same 10^5 (see UK100-BUILD-PLAN.md §1.1).
// EUSTX50 added 2026-07-13 (UK100-SESSION-REVIEW-2026-07-13.md F8) — same class
// as GER40/UK100, pipDigits 5 confirmed via the same ctrader_http_fetch.py
// symbol-resolution path used to verify the others.
export const PIP_DIGITS: Record<string, number> = {
  XAUUSD: 5, XAGUSD: 5,
  EURUSD: 5, USDJPY: 5, USDCHF: 5, USDCNH: 5,
  GBPUSD: 5, USDCAD: 5, USDSEK: 5,
  US500: 5, GER40: 5, UK100: 5, EUSTX50: 5,
  NAS100: 5, BRENT: 5, COPPER: 5, VIX: 5, USDX: 5, EURGBP: 5,
}

// Broker-assigned symbolIds. This account trades the _SB (spread-bet) variants;
// XAUUSD_SB = 241 (confirmed 2026-07-07 — the old 41 does NOT resolve and returns
// no spot). Any entry that drifts is self-healed at runtime by fetchCTraderPrices,
// which re-resolves unpriced symbols via get_symbols (preferring enabled _SB IDs).
//
// UK100 build additions (2026-07-10, see UK100-BUILD-PLAN.md §1.1): these are the
// plain-CFD symbolIds, not _SB — the user trades UK100 as a CFD, and live
// verification showed CFD and _SB prices identical to within spread noise (both
// wrappers price off the same underlying feed). Fallback _SB IDs if a CFD ID ever
// stops pricing: NAS100→205, BRENT→253 (Brent_SB), COPPER→2359, VIX→408, USDX→235,
// EURGBP→175.
// EUSTX50 = 124 (plain CFD, verified live 2026-07-13 via get_symbols — the
// European-tape driver's primary symbol, UK100-SESSION-REVIEW-2026-07-13.md F8).
export const KNOWN_SYMBOL_IDS: Record<string, number> = {
  XAUUSD: 241, XAGUSD: 42,
  EURUSD: 1, USDJPY: 4, USDCHF: 6, USDCNH: 60,
  GBPUSD: 2, USDCAD: 8, USDSEK: 29,
  US500: 115, GER40: 110, UK100: 113, EUSTX50: 124,
  NAS100: 116, BRENT: 249, COPPER: 109, VIX: 152, USDX: 101, EURGBP: 9,
}

/**
 * One MCP round-trip. Handles the SSE framing where a single event's payload
 * can span multiple physical "data:" lines for large results — rejoin all data
 * lines within an event before parsing (parsing only the first line silently
 * fails on any multi-line payload).
 */
export async function mcpFetch(body: object, sessionId?: string): Promise<{ data: unknown; sessionId: string | null; httpStatus: number | null }> {
  const headers: Record<string, string> = {
    Authorization: `Bearer ${CTRADER_TOKEN}`,
    'Content-Type': 'application/json',
    Accept: 'application/json, text/event-stream',
  }
  if (sessionId) headers['Mcp-Session-Id'] = sessionId

  const ctrl = new AbortController()
  const timer = setTimeout(() => ctrl.abort(), 20000)
  try {
    const res = await fetch(CTRADER_URL, {
      method: 'POST', headers, body: JSON.stringify(body), signal: ctrl.signal,
      // @ts-expect-error — Node's global fetch is undici under the hood and
      // accepts `dispatcher`, but the DOM lib types (used for the ambient
      // fetch signature) don't declare it. Pinning every request onto one
      // keep-alive connection is the fix for the load-balancer session-loss
      // bug documented in this file's module docstring.
      dispatcher: pinnedAgent,
    })
    const newSid = res.headers.get('Mcp-Session-Id') ?? res.headers.get('mcp-session-id') ?? sessionId ?? null
    const text = await res.text()

    if (!res.ok) {
      console.error(`CTrader MCP HTTP ${res.status}: ${text.slice(0, 200)}`)
      // Still attempt to parse the body — on this deployment a non-2xx response
      // IS the JSON-RPC error object (e.g. "Session not found; re-initialize"),
      // and callers need to see it to detect and recover from session loss.
      try { return { data: JSON.parse(text), sessionId: newSid, httpStatus: res.status } } catch { /* not JSON */ }
      return { data: null, sessionId: newSid, httpStatus: res.status }
    }

    for (const event of text.split(/\r?\n\r?\n/)) {
      const dataLines = event.split(/\r?\n/).filter(l => l.startsWith('data:')).map(l => l.replace(/^data:\s?/, ''))
      if (dataLines.length === 0) continue
      try { return { data: JSON.parse(dataLines.join('\n')), sessionId: newSid, httpStatus: res.status } } catch { /* try next event */ }
    }
    try { return { data: JSON.parse(text), sessionId: newSid, httpStatus: res.status } } catch { /* ignore */ }
    if (text.length > 0) {
      console.error(`CTrader MCP: failed to parse response (${text.length} chars): ${text.slice(0, 200)}${text.length > 200 ? '…' : ''}`)
    }
    return { data: null, sessionId: newSid, httpStatus: res.status }
  } finally {
    clearTimeout(timer)
  }
}

export interface Trendbar {
  timestamp: number // ms epoch — added for F8's date-keyed correlation pairing (scripts/lib/stats.ts); additive, existing positional consumers are unaffected
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

  /** True when a JSON-RPC error is the load-balancer session-loss signature
   * (see this file's module docstring) — recoverable by re-initializing. */
  private isSessionLoss(err: unknown): boolean {
    const e = err as { code?: number; message?: string } | undefined
    return e?.code === -32000 || /session not found/i.test(e?.message ?? '')
  }

  async callTool(name: string, args: object): Promise<unknown> {
    const MAX_ATTEMPTS = 3 // initial + 2 re-init retries — bounded so a dead
                            // backend can never hang the hourly workflow.
    let parsed: Record<string, unknown> | undefined
    for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt++) {
      const { data } = await mcpFetch(
        { jsonrpc: '2.0', id: 1, method: 'tools/call', params: { name, arguments: args } },
        this.sessionId ?? undefined,
      )
      parsed = data as Record<string, unknown> | undefined
      const err = parsed?.error as { code?: number; message?: string } | undefined
      if (err && this.isSessionLoss(err) && attempt < MAX_ATTEMPTS) {
        console.error(`CTrader MCP: ${name} lost its session (attempt ${attempt}/${MAX_ATTEMPTS}) — re-initializing and retrying`)
        await this.init()
        continue
      }
      break
    }
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
        timestamp: b.timestamp ?? 0,
        open:  b.open ?? b.close ?? 0,
        high:  b.high,
        low:   b.low,
        close: b.close ?? b.open ?? 0,
        volume: b.volume ?? 0,
      }))
  }
}
