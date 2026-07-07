import type { CalendarEvent } from '../types/dashboard'

export interface ResolvedEvent {
  event: string
  currency?: string
  whenIso: string
  msUntil: number
}

/**
 * Nearest upcoming HIGH-impact event from the week-ahead calendar. Calendar
 * `time` is a UTC "HH:MM" slice (see fetch-static-data.ts), so the event instant
 * is `${date}T${time}:00Z`. Returns null when nothing HIGH is still ahead.
 */
export function nextHighImpactEvent(calendar: CalendarEvent[], now: number = Date.now()): ResolvedEvent | null {
  let best: ResolvedEvent | null = null
  for (const e of calendar) {
    if (e.impact !== 'HIGH' || !e.date) continue
    const iso = e.time ? `${e.date}T${e.time}:00Z` : `${e.date}T00:00:00Z`
    const t = Date.parse(iso)
    if (!Number.isFinite(t)) continue
    const msUntil = t - now
    if (msUntil <= 0) continue
    if (best === null || msUntil < best.msUntil) {
      best = { event: e.event, currency: e.currency, whenIso: iso, msUntil }
    }
  }
  return best
}

/** "3d 4h" / "3h 20m" / "45m" */
export function fmtCountdown(ms: number): string {
  const totalMin = Math.floor(ms / 60_000)
  const d = Math.floor(totalMin / 1440)
  const h = Math.floor((totalMin % 1440) / 60)
  const m = totalMin % 60
  if (d > 0) return `${d}d ${h}h`
  if (h > 0) return `${h}h ${String(m).padStart(2, '0')}m`
  return `${m}m`
}
