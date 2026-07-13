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

export interface StaticCalendarEntry {
  date: string; event: string; timeLondon: string; impact: 'HIGH'; region: 'UK' | 'US'
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
export const UK_STATIC_CALENDAR_2026: StaticCalendarEntry[] = [
  { date: '2026-07-16', event: 'UK GDP Monthly Estimate', timeLondon: '07:00', impact: 'HIGH', region: 'UK' },
  { date: '2026-07-21', event: 'UK Labour Market Report', timeLondon: '07:00', impact: 'HIGH', region: 'UK' },
  { date: '2026-07-22', event: 'UK CPI', timeLondon: '07:00', impact: 'HIGH', region: 'UK' },
  { date: '2026-07-24', event: 'UK Retail Sales', timeLondon: '07:00', impact: 'HIGH', region: 'UK' },
  ...MPC_DATES_2026.map(date => ({ date, event: 'BoE MPC Rate Decision', timeLondon: '12:00', impact: 'HIGH' as const, region: 'UK' as const })),
]

// ── Static US calendar (UK100-SESSION-REVIEW-2026-07-13.md F4) ──────────────
// The static UK calendar above covers only UK releases by design, so US
// CPI/NFP/FOMC/PCE — the biggest single intraday movers of UK100 at
// 13:30/19:00 London — were invisible to eventSuppressed/eventWindows and the
// ORB Playbook's stand-aside rows. Unlike the ONS bulletins above, the FOMC/
// BLS/BEA schedules are published a full year ahead on fixed dates, so (like
// MPC_DATES_2026) the FULL 2026 schedule is included, not just the next
// occurrence — each date WebFetch-verified 2026-07-13 against the primary
// source, not invented:
//   FOMC (decision day = day 2 of each 2-day meeting) → federalreserve.gov/monetarypolicy/fomccalendars.htm
//   CPI                                               → bls.gov/schedule/news_release/cpi.htm
//   Employment Situation (NFP)                        → bls.gov/schedule/news_release/empsit.htm
//   PCE Price Index ("Personal Income and Outlays")   → bea.gov/news/schedule
// PCE's page only lists releases from 30 Jul 2026 onward (a rolling forward
// window, not a full-year archive) — earlier-2026 PCE dates were NOT
// re-verified and are deliberately omitted rather than guessed; they're also
// operationally moot since they're already past. Release times are the
// well-established market convention (14:00 ET for FOMC statements, 08:30 ET
// for BLS/BEA releases) converted via the same fixed 5-hour ET→London offset
// used throughout the year (the brief DST-mismatch windows in Mar/Nov are not
// worth modelling for a calendar-caution feature).
export const US_STATIC_CALENDAR_2026: StaticCalendarEntry[] = [
  // FOMC Rate Decision — federalreserve.gov, 2026 two-day meetings, day 2:
  ...['2026-01-28', '2026-03-18', '2026-04-29', '2026-06-17', '2026-07-29', '2026-09-16', '2026-10-28', '2026-12-09']
    .map(date => ({ date, event: 'FOMC Rate Decision', timeLondon: '19:00', impact: 'HIGH' as const, region: 'US' as const })),
  // US CPI — bls.gov/schedule/news_release/cpi.htm:
  ...['2026-01-13', '2026-02-13', '2026-03-11', '2026-04-10', '2026-05-12', '2026-06-10', '2026-07-14',
      '2026-08-12', '2026-09-11', '2026-10-14', '2026-11-10', '2026-12-10']
    .map(date => ({ date, event: 'US CPI', timeLondon: '13:30', impact: 'HIGH' as const, region: 'US' as const })),
  // US Nonfarm Payrolls (Employment Situation) — bls.gov/schedule/news_release/empsit.htm:
  ...['2026-01-09', '2026-02-11', '2026-03-06', '2026-04-03', '2026-05-08', '2026-06-05', '2026-07-02',
      '2026-08-07', '2026-09-04', '2026-10-02', '2026-11-06', '2026-12-04']
    .map(date => ({ date, event: 'US Nonfarm Payrolls', timeLondon: '13:30', impact: 'HIGH' as const, region: 'US' as const })),
  // US PCE Price Index — bea.gov/news/schedule (forward-listed from 30 Jul 2026 only, see note above):
  ...['2026-07-30', '2026-08-26', '2026-09-30', '2026-10-29', '2026-11-25', '2026-12-23']
    .map(date => ({ date, event: 'US PCE Price Index', timeLondon: '13:30', impact: 'HIGH' as const, region: 'US' as const })),
]

type CalendarKeywordClass = 'FOMC' | 'NFP' | 'PCE' | 'CPI' | 'LABOUR' | 'GDP' | 'RETAIL' | 'MPC' | 'OTHER'

function keywordClass(eventName: string): CalendarKeywordClass {
  const n = eventName.toUpperCase()
  if (n.includes('FOMC') || n.includes('FEDERAL RESERVE') || n.includes('FED RATE') || n.includes('FED INTEREST RATE')) return 'FOMC'
  if (n.includes('NFP') || n.includes('NONFARM') || n.includes('EMPLOYMENT SITUATION') || n.includes('JOBS REPORT')) return 'NFP'
  if (n.includes('PCE')) return 'PCE'
  if (n.includes('CPI') || n.includes('INFLATION')) return 'CPI'
  if (n.includes('LABOUR') || n.includes('LABOR') || n.includes('UNEMPLOYMENT') || n.includes('CLAIMANT') || n.includes('EARNINGS')) return 'LABOUR'
  if (n.includes('GDP')) return 'GDP'
  if (n.includes('RETAIL')) return 'RETAIL'
  if (n.includes('MPC') || n.includes('BANK RATE') || n.includes('INTEREST RATE')) return 'MPC'
  return 'OTHER'
}

function staticEntryToEvent(s: StaticCalendarEntry, today: string): Uk100CalendarEvent {
  const [hh, mm] = s.timeLondon.split(':').map(Number)
  const dateOnly = new Date(`${s.date}T00:00:00Z`)
  const offsetH = londonOffsetHours(dateOnly)
  const timeIso = new Date(Date.UTC(
    dateOnly.getUTCFullYear(), dateOnly.getUTCMonth(), dateOnly.getUTCDate(), hh - offsetH, mm,
  )).toISOString()
  return {
    event: s.event, region: s.region, impact: s.impact,
    timeIso, timeLondon: `${s.timeLondon} ${offsetH === 1 ? 'BST' : 'GMT'}`,
    daysFromToday: daysBetween(s.date, today),
  }
}

/**
 * Merge Finnhub's calendar with the static ONS/Fed/BLS/BEA-verified
 * fallbacks, deduping by (date, region, keyword-class) — region-qualified so
 * a UK CPI print and a US CPI print landing on the same calendar day are
 * correctly treated as two distinct events, never merged into one — so the
 * same release never appears twice if Finnhub access is ever restored. The
 * static entry wins on a collision since it's the one that was hand-verified
 * against the primary source. Entries outside the dashboard's 0-4 day
 * lookahead window are dropped here so every caller sees an already-trimmed
 * list.
 */
export function mergeCalendars(
  finnhub: Uk100CalendarEvent[],
  staticEntries: StaticCalendarEntry[],
  today: string,
): Uk100CalendarEvent[] {
  const staticEvents = staticEntries.map(s => staticEntryToEvent(s, today))
  const key = (e: Uk100CalendarEvent) => `${e.timeIso.slice(0, 10)}|${e.region}|${keywordClass(e.event)}`
  const staticKeys = new Set(staticEvents.map(key))
  const finnhubDeduped = finnhub.filter(e => !staticKeys.has(key(e)))
  return [...staticEvents, ...finnhubDeduped]
    .filter(e => e.daysFromToday >= 0 && e.daysFromToday <= 4)
    .sort((a, b) => a.timeIso.localeCompare(b.timeIso))
}
