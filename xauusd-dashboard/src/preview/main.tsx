// Preview harness: renders the ladder against a real recorded session so the
// chart can be looked at, not just typechecked. Not part of the app bundle.
import { createRoot } from 'react-dom/client'
import '../styles/tokens.css'
import '../styles/globals.css'
import { GexBotView } from '../components/gexbot/GexBotTab'
import type { GexSnapshot } from '../types/gex'
import fixture from './gexFixture.json'

const f = fixture as unknown as {
  zero: GexSnapshot; full: GexSnapshot; history: GexSnapshot[]
}
// Freeze "now" at the session close so the stale banner reflects a live feed.
const now = new Date((f.zero.source_ts + 60) * 1000)

// Mirror GexBotContent's wrapper: a COLUMN. Laying these out as a row is how
// the first preview put the footnote beside the side panel.
createRoot(document.getElementById('root')!).render(
  <div style={{
    display: 'flex', flexDirection: 'column', gap: 10,
    minHeight: '100vh', padding: '14px 20px 24px',
  }}>
    <GexBotView zero={f.zero} full={f.full} history={f.history} now={now} />
  </div>,
)
