import { useState, useEffect, useRef, useCallback } from 'react'

const MCP_URL   = import.meta.env.VITE_CTRADER_MCP_URL   ?? 'https://mcp.ctrader.com/trading/mcp'
const MCP_TOKEN = import.meta.env.VITE_CTRADER_MCP_TOKEN ?? ''
const POLL_MS   = 20_000

export interface OpenPosition {
  direction:    'LONG' | 'SHORT'
  lots:         number
  entryPrice:   number
  currentPrice: number
  pnl:          number
  pnlPct:       number
}

async function mcpPost(body: object, sessionId?: string): Promise<{ data: unknown; sessionId: string | null }> {
  const headers: Record<string, string> = {
    Authorization: `Bearer ${MCP_TOKEN}`,
    'Content-Type': 'application/json',
    Accept: 'application/json, text/event-stream',
  }
  if (sessionId) headers['Mcp-Session-Id'] = sessionId
  const res = await fetch(MCP_URL, { method: 'POST', headers, body: JSON.stringify(body) })
  const newSid = res.headers.get('Mcp-Session-Id') ?? res.headers.get('mcp-session-id') ?? sessionId ?? null
  const text = await res.text()
  for (const line of text.split('\n')) {
    if (line.startsWith('data: ')) return { data: JSON.parse(line.slice(6)), sessionId: newSid }
  }
  try { return { data: JSON.parse(text), sessionId: newSid } } catch { /* ignore */ }
  return { data: null, sessionId: newSid }
}

async function callTool(tool: string, args: object, sid: string): Promise<unknown> {
  const { data } = await mcpPost({ jsonrpc: '2.0', id: 2, method: 'tools/call', params: { name: tool, arguments: args } }, sid)
  if (!data) return null
  const result  = (data as Record<string, unknown>).result as Record<string, unknown> | undefined
  const content = result?.content as Array<{ type: string; text: string }> | undefined
  if (content?.[0]?.type === 'text') { try { return JSON.parse(content[0].text) } catch { return null } }
  return null
}

export function useOpenPosition(): OpenPosition | null {
  const [pos, setPos] = useState<OpenPosition | null>(null)
  const sidRef = useRef<string | null>(null)

  const fetchPos = useCallback(async () => {
    if (!MCP_TOKEN) return

    try {
      // Initialise session if needed
      if (!sidRef.current) {
        const { data, sessionId } = await mcpPost({
          jsonrpc: '2.0', id: 0, method: 'initialize',
          params: { protocolVersion: '2024-11-05', capabilities: {}, clientInfo: { name: 'xauusd-position', version: '1.0' } },
        })
        if (!data || !(data as Record<string,unknown>).result || !sessionId) return
        await mcpPost({ jsonrpc: '2.0', method: 'notifications/initialized', params: {} }, sessionId)
        sidRef.current = sessionId
      }

      const raw = await callTool('get_positions', {}, sidRef.current!)
      const positions = (raw as { positions?: unknown[] })?.positions ?? []

      // Find the first open XAUUSD position
      interface RawPos {
        symbolName?: string; tradeSide?: string; volume?: number; lotSize?: number
        entryPrice?: number; currentPrice?: number; netProfit?: number
      }
      const xauPos = (positions as RawPos[]).find(p => {
        const name = (p.symbolName ?? '').toUpperCase()
        return name.includes('XAU') || name.includes('GOLD')
      })

      if (!xauPos) { setPos(null); return }

      const direction = (xauPos.tradeSide ?? '').toUpperCase() === 'SELL' ? 'SHORT' : 'LONG'
      const lotSize   = xauPos.lotSize ?? 10000
      const lots      = (xauPos.volume ?? 0) / (lotSize * 100)
      const pip       = 100000  // pipDigits=5 for XAUUSD
      const entry     = (xauPos.entryPrice  ?? 0) / pip
      const current   = (xauPos.currentPrice ?? 0) / pip
      const pnl       = xauPos.netProfit ?? 0
      const pnlPct    = entry > 0 ? ((current - entry) / entry) * 100 * (direction === 'SHORT' ? -1 : 1) : 0

      setPos({ direction, lots, entryPrice: entry, currentPrice: current, pnl, pnlPct })
    } catch {
      sidRef.current = null
    }
  }, [])

  useEffect(() => {
    fetchPos()
    const id = setInterval(fetchPos, POLL_MS)
    return () => clearInterval(id)
  }, [fetchPos])

  return pos
}
