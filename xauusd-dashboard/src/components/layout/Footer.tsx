import styles from './Footer.module.css'

export function Footer() {
  return (
    <footer className={styles.footer}>
      <span className={styles.text}>
        XAUUSD Intelligence Dashboard · Prices via CTrader MCP · Macro via FRED / Finnhub · AI via Anthropic
      </span>
      <span className={styles.text}>
        Data is for informational purposes only. Not financial advice. Trade responsibly.
      </span>
    </footer>
  )
}
