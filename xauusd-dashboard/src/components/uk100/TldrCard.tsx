import type { TldrBullet, TldrTag } from '../../types/uk100'
// Reuse the AI-session card chrome (card + cardTitle) so the TL;DR sits in the
// same visual system as the rest of the brief.
import card from '../gold-session/GoldSessionTab.module.css'
import styles from './TldrCard.module.css'

// Chip colour by tag — reuses the global badge classes.
function tagBadge(tag: TldrTag): string {
  if (tag === 'PLAN') return 'badge-gold'
  if (tag === 'RISK' || tag === 'NEWS') return 'badge-amber'
  return 'badge-muted'
}

export function TldrCard({ bullets }: { bullets: TldrBullet[] }) {
  return (
    <div className={card.card}>
      <h3 className={card.cardTitle}>TL;DR</h3>
      <div className={styles.list}>
        {bullets.map((b, i) => (
          <div key={i} className={styles.row}>
            <span className={`badge ${tagBadge(b.tag)} ${styles.tag}`}>{b.tag}</span>
            <span className={styles.text}>{b.text}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
