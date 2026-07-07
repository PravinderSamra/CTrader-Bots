/* ═══════════════════════════════════════════
   UK time helpers — BST/GMT aware via Intl
   Single source of truth for UK-local time display across the dashboard.
   Uses the IANA "Europe/London" zone so DST transitions are automatic
   (no manual last-Sunday-of-March offset juggling).
   ═══════════════════════════════════════════ */

interface LondonParts {
  hour: number
  minute: number
  tz: string   // "BST" | "GMT" (or "GMT+1" in some locales)
}

function londonParts(d: Date): LondonParts {
  const parts = new Intl.DateTimeFormat('en-GB', {
    timeZone: 'Europe/London',
    hour: '2-digit',
    minute: '2-digit',
    hourCycle: 'h23',
    timeZoneName: 'short',
  }).formatToParts(d)

  const hour   = parseInt(parts.find(p => p.type === 'hour')?.value ?? '0', 10)
  const minute = parseInt(parts.find(p => p.type === 'minute')?.value ?? '0', 10)
  const tz     = parts.find(p => p.type === 'timeZoneName')?.value ?? 'GMT'
  return { hour, minute, tz }
}

/** True when the UK is observing British Summer Time (UTC+1). */
export function isBST(d: Date = new Date()): boolean {
  const { tz } = londonParts(d)
  return tz === 'BST' || tz.includes('+1')
}

/** "BST" or "GMT" for the given instant. */
export function ukTzLabel(d: Date = new Date()): string {
  return isBST(d) ? 'BST' : 'GMT'
}

/** "HH:MM BST" / "HH:MM GMT" — the canonical UK time display. */
export function ukTimeString(d: Date = new Date()): string {
  const { hour, minute } = londonParts(d)
  const hh = String(hour).padStart(2, '0')
  const mm = String(minute).padStart(2, '0')
  return `${hh}:${mm} ${ukTzLabel(d)}`
}

/** "HH:MM:SS BST" — with seconds, for the live header clock. */
export function ukClockString(d: Date = new Date()): string {
  const parts = new Intl.DateTimeFormat('en-GB', {
    timeZone: 'Europe/London',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hourCycle: 'h23',
  }).formatToParts(d)
  const hh = parts.find(p => p.type === 'hour')?.value ?? '00'
  const mm = parts.find(p => p.type === 'minute')?.value ?? '00'
  const ss = parts.find(p => p.type === 'second')?.value ?? '00'
  return `${hh}:${mm}:${ss} ${ukTzLabel(d)}`
}
