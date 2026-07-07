/* ═══════════════════════════════════════════
   Session & Kill-Zone detection — ET-anchored
   Single source of truth for the dashboard, mirroring the Python engine's
   analysis/sessions.py (America/New_York anchors). ET anchoring means DST is
   handled automatically via Intl — the same instant classifies identically
   in Header, SessionTimeline and App, and never drifts an hour across a
   clock change.

   Kill-zone windows are copied verbatim from sessions.py. Session bands keep
   the dashboard's long-standing OVERLAP concept (London+NY prime window),
   which the engine folds into LONDON — the dashboard surfaces it as its own
   "PRIME SESSION" badge.
   ═══════════════════════════════════════════ */

export type SessionKey = 'ASIAN' | 'LONDON' | 'OVERLAP' | 'NEW_YORK' | 'OFF'

interface SessionDef {
  key: SessionKey
  label: string
  startET: [number, number]   // inclusive
  endET: [number, number]     // exclusive
  isPrime: boolean
}

// ET-anchored session bands (wall-clock America/New_York). Ordered; first match wins.
// London KZ (02:00–05:00 ET) and NY KZ (07:00–10:00 ET) overlay these independently.
const SESSIONS: SessionDef[] = [
  { key: 'ASIAN',    label: 'Asian',    startET: [19, 0], endET: [3, 0],  isPrime: false },
  { key: 'LONDON',   label: 'London',   startET: [3, 0],  endET: [8, 0],  isPrime: false },
  { key: 'OVERLAP',  label: 'Overlap',  startET: [8, 0],  endET: [11, 30], isPrime: true  },
  { key: 'NEW_YORK', label: 'New York', startET: [11, 30], endET: [17, 0], isPrime: false },
]

interface KillZoneDef {
  name: string
  startET: [number, number]
  endET: [number, number]
}

// Copied verbatim from analysis/sessions.py _KILL_ZONES.
const KILL_ZONES: KillZoneDef[] = [
  { name: 'Asia KZ',        startET: [20, 0],  endET: [0, 0]   },
  { name: 'London KZ',      startET: [2, 0],   endET: [5, 0]   },
  { name: 'NY KZ',          startET: [7, 0],   endET: [10, 0]  },
  { name: 'Silver Bullet',  startET: [9, 50],  endET: [10, 10] },
  { name: 'Silver Bullet',  startET: [13, 50], endET: [14, 10] },
  { name: 'London Close',   startET: [11, 0],  endET: [12, 0]  },
]

// ── ET clock helpers ─────────────────────────────────────────────────────────

function etParts(d: Date): { hour: number; minute: number } {
  const parts = new Intl.DateTimeFormat('en-US', {
    timeZone: 'America/New_York',
    hour: '2-digit',
    minute: '2-digit',
    hourCycle: 'h23',
  }).formatToParts(d)
  const hour   = parseInt(parts.find(p => p.type === 'hour')?.value ?? '0', 10)
  const minute = parseInt(parts.find(p => p.type === 'minute')?.value ?? '0', 10)
  return { hour, minute }
}

function etMinutes(d: Date): number {
  const { hour, minute } = etParts(d)
  return hour * 60 + minute
}

const hm = (t: [number, number]) => t[0] * 60 + t[1]

/** True if `mins` (minute-of-day) is within [start, end), handling midnight wrap. */
function inRange(mins: number, start: number, end: number): boolean {
  if (start <= end) return start <= mins && mins < end
  return mins >= start || mins < end   // crosses midnight (e.g. 19:00 → 03:00)
}

/**
 * Signed offset (minutes) to add to a UTC minute-of-day to reach the ET
 * minute-of-day for this instant. EDT ≈ -240, EST ≈ -300. Roughly constant
 * across a day (off only during the 1h DST-transition window) — precise enough
 * for positioning the timeline bar.
 */
export function etOffsetMinutes(d: Date = new Date()): number {
  const utcMin = d.getUTCHours() * 60 + d.getUTCMinutes()
  let diff = etMinutes(d) - utcMin
  if (diff > 720) diff -= 1440
  if (diff < -720) diff += 1440
  return diff
}

/** UTC minute-of-day corresponding to an ET wall-clock time on `now`'s date. */
export function etToUtcMinute(etHM: [number, number], now: Date = new Date()): number {
  const off = etOffsetMinutes(now)
  return ((hm(etHM) - off) % 1440 + 1440) % 1440
}

// ── Public API ───────────────────────────────────────────────────────────────

export interface SessionInfo {
  key: SessionKey
  label: string
  isPrime: boolean
  nextName: string
  nextLabel: string       // "1h 23m"
  minutesToNext: number
}

export function fmtDuration(mins: number): string {
  const h = Math.floor(mins / 60)
  const m = mins % 60
  return h > 0 ? `${h}h ${String(m).padStart(2, '0')}m` : `${m}m`
}
const fmtMins = fmtDuration

export function getSession(now: Date = new Date()): SessionInfo {
  const mins = etMinutes(now)
  const idx = SESSIONS.findIndex(s => inRange(mins, hm(s.startET), hm(s.endET)))

  if (idx === -1) {
    // OFF-HOURS (17:00–19:00 ET) → next up is ASIAN.
    const asia = SESSIONS[0]
    const toNext = ((hm(asia.startET) - mins) % 1440 + 1440) % 1440
    return { key: 'OFF', label: 'After Hours', isPrime: false, nextName: asia.label, nextLabel: fmtMins(toNext), minutesToNext: toNext }
  }

  const s = SESSIONS[idx]
  const next = SESSIONS[(idx + 1) % SESSIONS.length]
  const toNext = ((hm(s.endET) - mins) % 1440 + 1440) % 1440
  return { key: s.key, label: s.label, isPrime: s.isPrime, nextName: next.label, nextLabel: fmtMins(toNext), minutesToNext: toNext }
}

export interface KillZoneInfo {
  active: boolean
  name: string
  minutes: number   // remaining if active, else until next opens
}

export function getKillZone(now: Date = new Date()): KillZoneInfo {
  const mins = etMinutes(now)

  for (const kz of KILL_ZONES) {
    if (inRange(mins, hm(kz.startET), hm(kz.endET))) {
      const rem = ((hm(kz.endET) - mins) % 1440 + 1440) % 1440
      return { active: true, name: kz.name, minutes: rem }
    }
  }

  // Nearest upcoming kill zone (smallest forward distance to a start).
  let best: { name: string; until: number } | null = null
  for (const kz of KILL_ZONES) {
    const until = ((hm(kz.startET) - mins) % 1440 + 1440) % 1440
    if (best === null || until < best.until) best = { name: kz.name, until }
  }
  return { active: false, name: best!.name, minutes: best!.until }
}

// ── Timeline rendering helpers (UTC-day positioned) ──────────────────────────

export interface TimelineSegment {
  key: SessionKey
  label: string
  startUtcMin: number
  endUtcMin: number
}

export function sessionSegmentsUtc(now: Date = new Date()): TimelineSegment[] {
  return SESSIONS.map(s => ({
    key: s.key,
    label: s.label,
    startUtcMin: etToUtcMinute(s.startET, now),
    endUtcMin: etToUtcMinute(s.endET, now),
  }))
}

export interface TimelineBand {
  name: string
  startUtcMin: number
  endUtcMin: number
}

export function killZoneBandsUtc(now: Date = new Date()): TimelineBand[] {
  return KILL_ZONES.map(kz => ({
    name: kz.name,
    startUtcMin: etToUtcMinute(kz.startET, now),
    endUtcMin: etToUtcMinute(kz.endET, now),
  }))
}
