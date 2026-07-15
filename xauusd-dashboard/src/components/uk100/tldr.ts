import type { Uk100SessionRecord, TldrBullet } from '../../types/uk100'

// G3 (UK100-ORB-INTEL-TLDR-DESIGN.md §3.4) — the source of truth for the TL;DR
// is the skill-written `record.tldr`. This is the fallback for records saved
// before that field existed: synthesise what we can from the structured meta
// fields. STRUCTURE and NEWS are omitted here — they aren't reliably derivable
// from meta alone (they live in the analysis text). Returns [] when nothing is
// derivable, in which case the card is hidden.
export function synthesizeTldr(record: Uk100SessionRecord | null): TldrBullet[] {
  if (!record) return []
  if (record.tldr && record.tldr.length > 0) return record.tldr

  const out: TldrBullet[] = []

  // REGIME — the mechanical bias line.
  if (record.bias) {
    const scoreStr = record.biasScore != null ? ` ${record.biasScore >= 0 ? '+' : ''}${record.biasScore}` : ''
    const conv = record.confidence != null ? `, confidence ${record.confidence}/10` : ''
    out.push({ tag: 'REGIME', text: `Bias ${record.bias}${scoreStr}${conv}.` })
  }

  // PLAN — playbook direction + day type, plus the trade idea's shape.
  if (record.orbPlaybook || record.tradeIdea) {
    const pb = record.orbPlaybook
    const ti = record.tradeIdea
    const parts: string[] = []
    if (pb) parts.push(`${pb.direction}${pb.dayType ? ` · ${pb.dayType}` : ''}`)
    if (ti) parts.push(`${ti.direction} ${ti.status}${record.probability != null ? ` (${record.probability}%)` : ''}`)
    if (parts.length > 0) out.push({ tag: 'PLAN', text: parts.join(' — ') })
  }

  // LEVELS — the 2-3 decision-relevant prices.
  {
    const bits: string[] = []
    if (record.invalidation != null) bits.push(`${record.invalidation} invalidation`)
    const t1 = record.tradeIdea?.targets?.[0]
    if (t1 != null) bits.push(`${t1} T1`)
    if (record.drawOnLiquidity != null && record.drawOnLiquidity !== t1) bits.push(`${record.drawOnLiquidity} draw`)
    if (bits.length > 0) out.push({ tag: 'LEVELS', text: bits.join(' · ') })
  }

  // RISK — the next high-impact event.
  if (record.nextHighImpactEvent?.event) {
    out.push({ tag: 'RISK', text: `Next high-impact event: ${record.nextHighImpactEvent.event}.` })
  }

  return out
}
