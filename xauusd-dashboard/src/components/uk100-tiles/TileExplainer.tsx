import styles from './TileExplainer.module.css'

/**
 * Plain-English disclosure row for the bottom of a UK100 macro tile.
 *
 * Native <details>/<summary> rather than a hover tooltip: the dashboard is
 * used on phones where hover doesn't exist, and a permanently-visible
 * paragraph on all nine tiles would double the page height. The row is a
 * visible affordance a non-expert will actually find, and costs one line
 * when collapsed.
 *
 * `text` is expected to come from explainers.ts — computed from the tile's
 * LIVE values (what today's number means), not a static glossary definition.
 */
export function TileExplainer({ text }: { text: string }) {
  return (
    <details className={styles.explainer}>
      <summary className={styles.summary}>
        <span className={styles.icon} aria-hidden>?</span>
        What does this mean for today?
      </summary>
      <p className={styles.body}>{text}</p>
    </details>
  )
}
