/* ═══════════════════════════════════════════
   Plain-English tile explainers — UK100 macro tab.

   Each function takes the same data block its tile renders and returns 1–3
   sentences a complete beginner can act on: not "what is a gilt" in the
   abstract, but "what does TODAY'S number mean for trading the index today".
   Pure functions (no React) so they can be unit-tested — the GBP sign-flip
   explainer especially, since the inverse pound/FTSE relationship is the one
   rule the whole UK100 section is built on and the easiest to state backwards.

   Copy style: plain words, no tickers/jargon unless immediately explained,
   always end on the trading takeaway.
   ═══════════════════════════════════════════ */

import type {
  BiasBlock, FxBlock, UkRatesBlock, UsLinkageBlock, CommoditiesBlock,
  PositioningBlock, SectorRead, OrbContext, Uk100CalendarEvent,
} from '../../types/uk100'

export function explainBias(bias: BiasBlock | null): string {
  if (!bias) return 'This dial adds up all the forces below into one overall lean for the index today. No data yet — check back after the next hourly refresh.'
  const convictionNote =
    bias.conviction === 'HIGH' ? 'and the signals mostly agree, so it carries real weight'
    : bias.conviction === 'MEDIUM' ? 'with moderate agreement between the signals'
    : 'but the signals are weak or mixed, so treat it lightly'
  const suppressed = bias.eventSuppressed
    ? ' A major scheduled announcement today is muting confidence — big news can override everything else.'
    : ''
  if (bias.label === 'BULLISH') {
    return `Adding up everything below, today's forces lean in favour of the index RISING (score ${bias.score > 0 ? '+' : ''}${bias.score} out of 10), ${convictionNote}. For today: upward moves have the wind at their back; be more sceptical of downward ones.${suppressed}`
  }
  if (bias.label === 'BEARISH') {
    return `Adding up everything below, today's forces lean in favour of the index FALLING (score ${bias.score} out of 10), ${convictionNote}. For today: downward moves have the wind at their back; be more sceptical of upward ones.${suppressed}`
  }
  return `Adding up everything below, there is no clear push in either direction today (score ${bias.score >= 0 ? '+' : ''}${bias.score} out of 10). For today: expect choppier, less committed price movement — be pickier about trades and quicker to take profit.${suppressed}`
}

export function explainFx(fx: FxBlock | null): string {
  const flip = 'Counter-intuitively, a WEAKER pound usually HELPS the FTSE 100: most of its giant companies earn in dollars and euros, and those earnings are worth more when converted back into a weaker pound.'
  if (!fx || fx.gbpUsdDayPct == null) return `${flip} No pound data yet today.`
  const move = fx.gbpUsdDayPct
  if (fx.ftseImpactFromGbp === 'BULLISH') {
    return `The pound is down ${Math.abs(move).toFixed(2)}% today. ${flip} So today the currency is a genuine tailwind — it supports the index moving up.`
  }
  if (fx.ftseImpactFromGbp === 'BEARISH') {
    return `The pound is up ${move.toFixed(2)}% today. ${flip} So a STRONGER pound, like today, works against the index — a headwind for upward moves.`
  }
  return `The pound has barely moved today (${move >= 0 ? '+' : ''}${move.toFixed(2)}%). ${flip} Today's move is too small to matter either way — the currency is not driving the index right now.`
}

export function explainRates(rates: UkRatesBlock | null): string {
  if (!rates) return 'Gilts are UK government IOUs; their interest rates are what the UK government pays to borrow. Sharp rises spook the whole market. No data yet today.'
  const mpcNote = rates.daysToMpc != null && rates.daysToMpc <= 7
    ? ` Note: the Bank of England announces its interest-rate decision in ${rates.daysToMpc} day${rates.daysToMpc === 1 ? '' : 's'} — markets often go quiet and hesitant just before it.`
    : ''
  if (rates.longEndStress) {
    return `UK government borrowing costs jumped sharply today (long-term gilt rates up ${rates.gilt20yDayBp != null ? `+${rates.gilt20yDayBp} basis points — hundredths of a percent` : 'sharply'}). Moves this size signal worry about UK public finances and usually drag the WHOLE index down, bank shares especially. Today: a genuine caution flag against buying dips.${mpcNote}`
  }
  if (rates.gilt10yDayBp != null && rates.gilt10yDayBp >= 4) {
    return `UK borrowing costs edged up today (+${rates.gilt10yDayBp} basis points on 10-year government debt) — a modest rise like this is mildly GOOD for bank shares (they earn more on lending) and roughly neutral for everyone else.${mpcNote}`
  }
  if (rates.gilt10yDayBp != null && rates.gilt10yDayBp <= -4) {
    return `UK borrowing costs fell today (${rates.gilt10yDayBp} basis points on 10-year government debt) — mildly negative for bank shares, mildly helpful for the rest. Not a big driver on its own.${mpcNote}`
  }
  return `UK interest rates and government borrowing costs are calm today — this tile is NOT driving the index right now. That's one less thing to worry about.${mpcNote}`
}

export function explainUsLinkage(us: UsLinkageBlock | null): string {
  if (!us) return 'The UK index rarely fights the giant US market for long — when America rallies or sells off, London usually follows. No US data yet today.'
  const vixNote =
    us.vixRegime === 'STRESS' ? ' The "fear index" (VIX) is in genuinely stressed territory — rallies are less trustworthy and moves get violent; trade smaller.'
    : us.vixRegime === 'ELEVATED' ? ` The "fear index" (VIX, ${us.vix?.toFixed(1) ?? '—'}) is a touch above calm — normal caution applies.`
    : ' The "fear index" (VIX) is calm — a supportive backdrop for steady moves.'
  if (us.us500DayPct == null) return `The UK index tends to follow the big US market.${vixNote}`
  if (us.us500DayPct >= 0.3) {
    return `The UK index rarely fights the US market for long. US futures are UP ${us.us500DayPct.toFixed(2)}% today, so the pull from America is positive — it supports UK upward moves.${vixNote}`
  }
  if (us.us500DayPct <= -0.3) {
    return `The UK index rarely fights the US market for long. US futures are DOWN ${Math.abs(us.us500DayPct).toFixed(2)}% today, so the pull from America is negative — it works against UK upward moves.${vixNote}`
  }
  return `The UK index rarely fights the US market for long, but US futures are roughly flat today (${us.us500DayPct >= 0 ? '+' : ''}${us.us500DayPct.toFixed(2)}%) — America is not pushing London either way right now.${vixNote}`
}

export function explainCommodities(c: CommoditiesBlock | null): string {
  const why = 'Oil and copper matter here because oil giants (Shell, BP) and big mining companies make up a large slice of the FTSE 100.'
  if (!c) return `${why} No data yet today.`
  const oil =
    c.brentDayPct == null ? 'oil is unreported'
    : c.brentDayPct >= 0.5 ? `oil is up ${c.brentDayPct.toFixed(2)}% (helps the energy heavyweights)`
    : c.brentDayPct <= -0.5 ? `oil is down ${Math.abs(c.brentDayPct).toFixed(2)}% (weighs on the energy heavyweights)`
    : 'oil is roughly flat'
  const copper =
    c.copperDayPct == null ? 'copper is unreported'
    : c.copperDayPct >= 0.5 ? `copper is up ${c.copperDayPct.toFixed(2)}% — a quick "China's economy looks fine" signal that lifts the miners`
    : c.copperDayPct <= -0.5 ? `copper is down ${Math.abs(c.copperDayPct).toFixed(2)}% — a quick "China demand worry" signal that weighs on the miners`
    : 'copper is roughly flat'
  const oilScore = c.brentDayPct ?? 0
  const copperScore = c.copperDayPct ?? 0
  const net = oilScore + copperScore
  const verdict = net >= 0.7 ? 'Net effect today: supportive for the index.'
    : net <= -0.7 ? 'Net effect today: a drag on the index.'
    : 'Net effect today: roughly neutral.'
  return `${why} Today ${oil}, and ${copper}. ${verdict}`
}

export function explainPositioning(p: PositioningBlock | null): string {
  const why = 'This shows how big professional speculators are positioned on the POUND (updated weekly). It reads through to the index via the pound relationship, and crowded bets often snap back.'
  if (!p || !p.crowding) return `${why} No positioning data available right now.`
  if (p.crowding === 'CROWDED_SHORT') {
    return `${why} Right now they are HEAVILY betting against the pound. If that crowded bet unwinds, the pound would jump — and a jumping pound is a headwind for the index. Treat this as a slow-burning caution for buyers, not a today-signal.`
  }
  if (p.crowding === 'CROWDED_LONG') {
    return `${why} Right now they are heavily betting ON the pound. If that crowded bet unwinds, the pound would fall — which would actually HELP the index. A slow-burning tailwind, not a today-signal.`
  }
  return `${why} Positioning is currently balanced — no crowded bet waiting to snap back. This tile is quiet today.`
}

export function explainOrb(orb: OrbContext | null): string {
  const strategy = 'The strategy here: the first 15 minutes after the 08:00 London open set the day\'s "opening range" — you wait for price to break OUT of that range and trade in the direction of the break.'
  if (!orb) return `${strategy} No data yet.`
  const adrNote = orb.adrUsedPct != null && orb.adrUsedPct >= 70
    ? ` Note: ${orb.adrUsedPct}% of a typical day's total movement has already happened — the easy part of any move may be gone, so favour smaller targets.`
    : orb.adrUsedPct != null && orb.adrUsedPct <= 30
    ? ` Only ${orb.adrUsedPct}% of a typical day's movement has happened so far — there is room left for a real move.`
    : ''
  if (orb.mode === 'PRE_OPEN') {
    return `${strategy} The market hasn't opened yet — the overnight high/low above are tonight's boundaries and tomorrow morning's first reference levels. Nothing to do until 08:00.`
  }
  if (orb.mode === 'ORB_FORMING') {
    return `${strategy} That range is forming RIGHT NOW (08:00–08:15). No trade yet — let the 15 minutes finish, then watch for the break.`
  }
  if (orb.mode === 'POST_ORB') {
    if (orb.orbBrokenDirection === 'UP') {
      return `${strategy} Today price has broken ABOVE the opening range — the day's first signal was upward. The range low${orb.orbLow != null ? ` (${orb.orbLow.toFixed(1)})` : ''} is now the line in the sand: a drop back below it means the signal failed.${adrNote}`
    }
    if (orb.orbBrokenDirection === 'DOWN') {
      return `${strategy} Today price has broken BELOW the opening range — the day's first signal was downward. The range high${orb.orbHigh != null ? ` (${orb.orbHigh.toFixed(1)})` : ''} is now the line in the sand: a rise back above it means the signal failed.${adrNote}`
    }
    return `${strategy} Price is still stuck INSIDE the opening range — no signal yet. The break, whenever it comes, is the cue.${adrNote}`
  }
  return `${strategy} The London session has closed — today's numbers above are the record, and tomorrow's plan starts from a fresh 08:00 range.`
}

export function explainSectors(sectors: SectorRead[]): string {
  const why = 'The FTSE 100 is dominated by a handful of sector blocks — energy, miners, banks, pharma, consumer staples — so the index goes where its heaviest blocks go.'
  if (!sectors || sectors.length === 0) return `${why} No sector reads yet today.`
  const bullish = sectors.filter(s => s.read === 'BULLISH')
  const bearish = sectors.filter(s => s.read === 'BEARISH')
  const lead = bearish.length > bullish.length
    ? `Today the pressure is negative: ${bearish.map(s => s.sector.toLowerCase()).join(' and ')} ${bearish.length === 1 ? 'is' : 'are'} being dragged (${bearish[0].driver}).`
    : bullish.length > bearish.length
    ? `Today the push is positive: ${bullish.map(s => s.sector.toLowerCase()).join(' and ')} ${bullish.length === 1 ? 'is' : 'are'} being lifted (${bullish[0].driver}).`
    : bullish.length === 0 && bearish.length === 0
    ? 'Today no sector block is being pushed hard either way — a quiet, driver-less tape.'
    : `Today the blocks are pulling in opposite directions (${bullish.map(s => s.sector.toLowerCase()).join('/')} up vs ${bearish.map(s => s.sector.toLowerCase()).join('/')} down) — expect a choppier index.`
  return `${why} ${lead} Pharma is always a wildcard: one company (AstraZeneca) is so large it can move the whole index on its own news.`
}

export function explainCalendar(events: Uk100CalendarEvent[]): string {
  const why = 'Scheduled announcements — interest-rate decisions, inflation numbers, jobs data — can move the market violently at the exact minute they come out. The opening-range strategy deliberately stands aside around them.'
  const todayHigh = events.filter(e => e.impact === 'HIGH' && e.daysFromToday === 0)
  const weekHigh = events.filter(e => e.impact === 'HIGH' && e.daysFromToday > 0 && e.daysFromToday <= 4)
  if (todayHigh.length > 0) {
    return `${why} TODAY has ${todayHigh.length} major release${todayHigh.length > 1 ? 's' : ''} (${todayHigh.map(e => `${e.event} at ${e.timeLondon}`).join('; ')}) — avoid holding a trade into ${todayHigh.length > 1 ? 'those minutes' : 'that minute'}.`
  }
  if (weekHigh.length > 0) {
    return `${why} Nothing major today, but ${weekHigh.length} big release${weekHigh.length > 1 ? 's are' : ' is'} coming later this week — markets often drift cautiously in the run-up, so don't expect fully committed moves.`
  }
  if (events.length === 0) {
    return `${why} The calendar feed is currently empty — that usually means a quiet schedule, but it can also mean the feed missed something, so stay alert around 07:00 and 13:30 UK time (the usual release slots) anyway.`
  }
  return `${why} No HIGH-impact releases on the schedule this week — one less risk to manage.`
}
