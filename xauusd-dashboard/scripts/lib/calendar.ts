/**
 * UK economic calendar merge/dedupe (UK100-V2-PLAN.md Phase A2). Pure
 * functions only — no I/O — extracted into scripts/lib/ so they can be unit
 * tested without triggering fetch-uk100-data.ts's unconditional `main()` call
 * (mirrors the ctrader.ts extraction for the same reason).
 */

export interface Uk100CalendarEvent {
  event: string; region: 'UK' | 'US' | 'EZ'; impact: 'HIGH' | 'MEDIUM' | 'LOW'
  timeIso: string; timeLondon: string
  daysFromToday: number; prior?: string; consensus?: string
}

function londonOffsetHours(d: Date): number {
  const m = d.getUTCMonth() + 1
  const day = d.getUTCDate()
  if (m > 3 && m < 10) return 1
  if (m === 3 && day >= 25) return 1
  if (m === 10 && day < 25) return 1
  return 0
}

function daysBetween(dateStr: string, fromStr: string): number {
  const a = new Date(`${dateStr}T00:00:00Z`).getTime()
  const b = new Date(`${fromStr}T00:00:00Z`).getTime()
  return Math.round((a - b) / 86_400_000)
}

// ── BoE MPC dates 2026 (from bankofengland.co.uk/monetary-policy, fetched
//    2026-07-10 per the plan's instruction to WebFetch rather than invent). ──

export const MPC_DATES_2026 = [
  '2026-02-05', '2026-03-19', '2026-04-30', '2026-06-18',
  '2026-07-30', '2026-09-17', '2026-11-05', '2026-12-17',
]

export function nextMpcDate(): { date: string | null; daysToMpc: number | null } {
  const todayStr = new Date().toISOString().slice(0, 10)
  const next = MPC_DATES_2026.find(d => d >= todayStr)
  if (!next) return { date: null, daysToMpc: null }
  return { date: next, daysToMpc: daysBetween(next, todayStr) }
}

// ── Static UK calendar fallback ──────────────────────────────────────────────
// Finnhub's /calendar/economic endpoint returns
// {"error":"You don't have access to this resource."} on this account's key
// (confirmed live via production workflow run 29166484720, job 86580355938,
// 2026-07-11) — a premium-gate, not a regionFromCountry mapping bug. Gold's
// identical Finnhub calendar call is affected the same way (out of scope to
// fix here per the plan). This static list is therefore the PRIMARY UK
// calendar source until/unless the Finnhub key is upgraded.
//
// Only the NEXT occurrence of each series was verified — via each series'
// ONS "latest" bulletin page on 2026-07-11 — because the ONS release cadence
// is irregular (the CPI sequence alone ran 18 Feb → 25 Mar → 22 Apr → 20 May
// → 17 Jun → 22 Jul, gaps of 4-5 weeks with no fixed day-of-month), so dates
// beyond the next confirmed one cannot be safely extrapolated. Wrong dates
// are worse than missing dates — do not add entries without checking the
// source bulletin first:
//   CPI            → ons.gov.uk/.../bulletins/consumerpriceinflation/latest
//   Labour Market  → ons.gov.uk/.../bulletins/uklabourmarket/latest
//   GDP            → ons.gov.uk/.../bulletins/gdpmonthlyestimateuk/latest
//   Retail Sales   → ons.gov.uk/.../bulletins/retailsales/latest
// TODO: re-verify and add the following occurrence once each date passes.
export const UK_STATIC_CALENDAR_2026: { date: string; event: string; timeLondon: string; impact: 'HIGH' }[] = [
  { date: '2026-07-16', event: 'UK GDP Monthly Estimate', timeLondon: '07:00', impact: 'HIGH' },
  { date: '2026-07-21', event: 'UK Labour Market Report', timeLondon: '07:00', impact: 'HIGH' },
  { date: '2026-07-22', event: 'UK CPI', timeLondon: '07:00', impact: 'HIGH' },
  { date: '2026-07-24', event: 'UK Retail Sales', timeLondon: '07:00', impact: 'HIGH' },
  ...MPC_DATES_2026.map(date => ({ date, event: 'BoE MPC Rate Decision', timeLondon: '12:00', impact: 'HIGH' as const })),
]

type CalendarKeywordClass = 'CPI' | 'LABOUR' | 'GDP' | 'RETAIL' | 'MPC' | 'OTHER'

function keywordClass(eventName: string): CalendarKeywordClass {
  const n = eventName.toUpperCase()
  if (n.includes('CPI') || n.includes('INFLATION')) return 'CPI'
  if (n.includes('LABOUR') || n.includes('LABOR') || n.includes('UNEMPLOYMENT') || n.includes('CLAIMANT') || n.includes('EARNINGS')) return 'LABOUR'
  if (n.includes('GDP')) return 'GDP'
  if (n.includes('RETAIL')) return 'RETAIL'
  if (n.includes('MPC') || n.includes('BANK RATE') || n.includes('INTEREST RATE')) return 'MPC'
  return 'OTHER'
}

function staticEntryToEvent(
  s: { date: string; event: string; timeLondon: string; impact: 'HIGH' },
  today: string,
): Uk100CalendarEvent {
  const [hh, mm] = s.timeLondon.split(':').map(Number)
  const dateOnly = new Date(`${s.date}T00:00:00Z`)
  const offsetH = londonOffsetHours(dateOnly)
  const timeIso = new Date(Date.UTC(
    dateOnly.getUTCFullYear(), dateOnly.getUTCMonth(), dateOnly.getUTCDate(), hh - offsetH, mm,
  )).toISOString()
  return {
    event: s.event, region: 'UK', impact: s.impact,
    timeIso, timeLondon: `${s.timeLondon} ${offsetH === 1 ? 'BST' : 'GMT'}`,
    daysFromToday: daysBetween(s.date, today),
  }
}

/**
 * Merge Finnhub's calendar with the static ONS-verified fallback, deduping by
 * (date, keyword-class) so the same release never appears twice if Finnhub
 * access is ever restored — the static entry wins since it's the one that
 * was hand-verified against the source bulletin. Entries outside the
 * dashboard's 0-4 day lookahead window are dropped here so every caller sees
 * an already-trimmed list.
 */
export function mergeCalendars(
  finnhub: Uk100CalendarEvent[],
  staticEntries: { date: string; event: string; timeLondon: string; impact: 'HIGH' }[],
  today: string,
): Uk100CalendarEvent[] {
  const staticEvents = staticEntries.map(s => staticEntryToEvent(s, today))
  const staticKeys = new Set(staticEvents.map(e => `${e.timeIso.slice(0, 10)}|${keywordClass(e.event)}`))
  const finnhubDeduped = finnhub.filter(e => !staticKeys.has(`${e.timeIso.slice(0, 10)}|${keywordClass(e.event)}`))
  return [...staticEvents, ...finnhubDeduped]
    .filter(e => e.daysFromToday >= 0 && e.daysFromToday <= 4)
    .sort((a, b) => a.timeIso.localeCompare(b.timeIso))
}
