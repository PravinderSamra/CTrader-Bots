import { useState, useEffect } from 'react'
import type { CalendarEvent } from '../types/dashboard'

const FINNHUB_KEY = import.meta.env.VITE_FINNHUB_KEY ?? ''
const HIGH_IMPACT_EVENTS = ['CPI', 'PCE', 'NFP', 'FOMC', 'ISM', 'GDP', 'PPI', 'Claims', 'JOLTS', 'Nonfarm', 'Federal Funds', 'Interest Rate']

type FinnhubEvent = {
  event: string
  time?: string
  impact?: string
  unit?: string
  estimate?: number | null
  prev?: number | null
  actual?: number | null
  country?: string
  currency?: string
}

function normaliseImpact(raw: string | undefined, eventName: string): CalendarEvent['impact'] {
  if (!raw) {
    const name = eventName.toUpperCase()
    if (HIGH_IMPACT_EVENTS.some(k => name.includes(k.toUpperCase()))) return 'HIGH'
    return 'LOW'
  }
  const r = raw.toLowerCase()
  if (r === 'high' || r === '3') return 'HIGH'
  if (r === 'medium' || r === '2') return 'MEDIUM'
  return 'LOW'
}

export function useEconomicCalendar(): CalendarEvent[] {
  const [events, setEvents] = useState<CalendarEvent[]>([])

  useEffect(() => {
    if (!FINNHUB_KEY) return

    const today = new Date()
    const dateStr = today.toISOString().slice(0, 10)
    const url = `https://finnhub.io/api/v1/calendar/economic?from=${dateStr}&to=${dateStr}&token=${FINNHUB_KEY}`

    fetch(url)
      .then(r => r.ok ? r.json() : null)
      .then((data: { economicCalendar?: FinnhubEvent[] } | null) => {
        if (!data?.economicCalendar) return
        const filtered = data.economicCalendar
          .filter(e => ['US', 'EU', 'GB', 'JP', 'EUR', 'USD', 'GBP', 'JPY'].some(c =>
            (e.country ?? e.currency ?? '').toUpperCase().includes(c)
          ))
          .map(e => ({
            time: e.time?.slice(11, 16) ?? '',
            event: e.event,
            impact: normaliseImpact(e.impact, e.event),
            currency: e.currency ?? e.country ?? 'US',
            forecast: e.estimate ?? null,
            previous: e.prev ?? null,
            actual: e.actual ?? null,
          } satisfies CalendarEvent))
          .sort((a, b) => a.time.localeCompare(b.time))
        setEvents(filtered)
      })
      .catch(() => {/* api unavailable */})
  }, [])

  return events
}

export function useNewsHeadlines(): string[] {
  const [headlines, setHeadlines] = useState<string[]>([])

  useEffect(() => {
    if (!FINNHUB_KEY) return

    const url = `https://finnhub.io/api/v1/news?category=general&token=${FINNHUB_KEY}`
    fetch(url)
      .then(r => r.ok ? r.json() : [])
      .then((data: Array<{ headline: string; category?: string }>) => {
        const keywords = ['gold', 'fed', 'inflation', 'yield', 'dollar', 'rate', 'powell', 'treasury']
        const relevant = data
          .filter(a => keywords.some(k => a.headline.toLowerCase().includes(k)))
          .slice(0, 5)
          .map(a => a.headline)
        setHeadlines(relevant)
      })
      .catch(() => {/* ignore */})
  }, [])

  return headlines
}

export function useVIX(): number | null {
  const [vix, setVix] = useState<number | null>(null)

  useEffect(() => {
    if (!FINNHUB_KEY) return
    // VIX via Finnhub quote
    fetch(`https://finnhub.io/api/v1/quote?symbol=VIX&token=${FINNHUB_KEY}`)
      .then(r => r.ok ? r.json() : null)
      .then((data: { c?: number } | null) => { if (data?.c) setVix(data.c) })
      .catch(() => {/* ignore */})
  }, [])

  return vix
}
