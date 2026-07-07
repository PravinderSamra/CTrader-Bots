/* ═══════════════════════════════════════════
   Gold-Session analysis parsers
   Pure functions that extract structure from the markdown analysis text.
   Kept in their own module so they can be unit-tested without React
   (see __tests__/parsers.test.ts) — these are the parsers that regressed
   once already (the "Price Zone: H" bug).

   NOTE: with Phase 2 structured records, these are the FALLBACK path — the UI
   prefers explicit meta fields (priceZone, tradeIdea, …) when present and only
   parses free text for older records that lack them.
   ═══════════════════════════════════════════ */

export interface PriceInRange {
  status: string
  level: string
}

export function parsePriceInRange(analysis: string): PriceInRange | null {
  // Extract the full "Current Price vs Equilibrium" line first
  const lineMatch = analysis.match(/Current Price vs Equilibrium[^\n]*/i)
  if (!lineMatch) return null

  // Strip the label itself ("…vs Equilibrium:**") so the word "Equilibrium" in
  // the LABEL isn't matched as the zone status, and so an "H1"/"M5" timeframe
  // prefix doesn't get read as a bare "H"/"M".
  const afterLabel = lineMatch[0].replace(/^.*?Equilibrium[:*\s]*/i, '')

  const statusMatch = afterLabel.match(/\b(DISCOUNT|PREMIUM|EQUILIBRIUM|OTE)\b/i)
  if (!statusMatch) return null

  // Extract a price level if present on the same line
  const priceMatch = afterLabel.match(/([$]?[\d,]{4,}(?:\.\d+)?)/i)
  const level = priceMatch ? priceMatch[1].trim() : ''

  return { status: statusMatch[1].toUpperCase(), level }
}

export interface Section {
  title: string
  body: string
}

export function parseSections(text: string): Section[] {
  const sections: Section[] = []
  let title = ''
  let bodyLines: string[] = []

  for (const line of text.split('\n')) {
    if (line.startsWith('## ')) {
      if (title) sections.push({ title, body: bodyLines.join('\n').trim() })
      title = line.replace(/^##\s+/, '').trim()
      bodyLines = []
    } else if (!line.startsWith('# ')) {
      bodyLines.push(line)
    }
  }
  if (title) sections.push({ title, body: bodyLines.join('\n').trim() })
  return sections
}

export interface KVRow {
  label: string
  value: string
  subs: string[]
}

export function parseKVRows(body: string): KVRow[] {
  const rows: KVRow[] = []
  let current: KVRow | null = null

  for (const line of body.split('\n')) {
    const kvMatch = line.match(/^-\s+\*\*(.+?)\*\*[:\s]*(.*)?$/)
    if (kvMatch) {
      if (current) rows.push(current)
      current = {
        label: kvMatch[1].replace(/:$/, '').trim(),
        value: (kvMatch[2] ?? '').trim(),
        subs: [],
      }
    } else if (line.match(/^\s{2,}\S/) && current) {
      current.subs.push(line.trim())
    }
  }
  if (current) rows.push(current)
  return rows
}

export function parseLevelLines(body: string): { price: string; desc: string }[] {
  return body
    .split('\n')
    .filter(l => l.trim().startsWith('- '))
    .map(line => {
      const content = line.replace(/^-\s+/, '').trim()
      const dash = content.indexOf(' — ')
      return dash > -1
        ? { price: content.slice(0, dash).trim(), desc: content.slice(dash + 3).trim() }
        : { price: content, desc: '' }
    })
}

export function valueColor(value: string): string | undefined {
  const upper = value.toUpperCase()
  if (/\bBULLISH\b/.test(upper)) return 'var(--green)'
  if (/\bBEARISH\b/.test(upper)) return 'var(--red)'
  if (/\bNEUTRAL\b/.test(upper)) return 'var(--amber)'
  if (/\bTRANSITIONAL\b/.test(upper)) return 'var(--amber)'
  if (/\bACTIVE\b/.test(upper)) return 'var(--green)'
  if (/\bNot applicable\b/i.test(value)) return 'var(--text-dim)'
  if (/\bUNAVAILABLE\b/.test(upper)) return 'var(--text-dim)'
  return undefined
}

export interface ProbabilityInfo {
  primaryPct: number | null
  primaryBias: string | null
  secondaryPct: number | null
  secondaryBias: string | null
  confidence: string | null
  invalidation: string | null
}

export function parseProbability(body: string): ProbabilityInfo {
  // Format per skill output: "- **Primary Scenario:** 72% — BULLISH (...)".
  // The `**` closes after the label, so the percent sits OUTSIDE the bold —
  // `\*{0,2}` tolerates either placement. Dash may be em/en/hyphen.
  const primaryMatch      = body.match(/Primary Scenario:\*{0,2}\s*(\d+)%\s*[—–-]\s*(\w+)/i)
  const secondaryMatch    = body.match(/Secondary Scenario:\*{0,2}\s*(\d+)%\s*[—–-]\s*(\w+)/i)
  const confidenceMatch   = body.match(/Confidence Level:\*{0,2}\s*(\w+)/i)
  const invalidationMatch = body.match(/Key Invalidation Level:\*{0,2}\s*([$\d,.–\s]+)/i)

  return {
    primaryPct:    primaryMatch ? parseInt(primaryMatch[1], 10) : null,
    primaryBias:   primaryMatch ? primaryMatch[2] : null,
    secondaryPct:  secondaryMatch ? parseInt(secondaryMatch[1], 10) : null,
    secondaryBias: secondaryMatch ? secondaryMatch[2] : null,
    confidence:    confidenceMatch ? confidenceMatch[1].toUpperCase() : null,
    invalidation:  invalidationMatch ? invalidationMatch[1].trim() : null,
  }
}
