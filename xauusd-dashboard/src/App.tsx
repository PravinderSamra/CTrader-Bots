import { useState, useCallback, lazy, Suspense } from 'react'
import { useCTraderPrices, pricesFromSnapshot } from './hooks/useCTraderPrices'
import { useDailySnapshot } from './hooks/useFredData'
import { aggregateData } from './services/dataAggregator'
import { Header } from './components/layout/Header'
import { SessionTimeline } from './components/layout/SessionTimeline'
import { MacroStrip } from './components/layout/MacroStrip'
import { Footer } from './components/layout/Footer'
import { YieldsTile } from './components/tiles/YieldsTile'
import { DollarTile } from './components/tiles/DollarTile'
import { EquitiesTile } from './components/tiles/EquitiesTile'
import { GoldTile } from './components/tiles/GoldTile'
import { CalendarTile } from './components/tiles/CalendarTile'
import { FedTile } from './components/tiles/FedTile'
import { PositioningTile } from './components/tiles/PositioningTile'
import { FlowsTile } from './components/tiles/FlowsTile'
import { BriefingPanel } from './components/briefing/BriefingPanel'
import { GoldSessionTab } from './components/gold-session/GoldSessionTab'
import styles from './App.module.css'

// Lazy-loaded: the Firebase SDK it pulls in is sizeable, and the Macro Dashboard /
// Gold-Session AI tabs (the vast majority of page loads) never touch it.
const PravzellaTab = lazy(() => import('./components/pravzella/PravzellaTab').then(m => ({ default: m.PravzellaTab })))

type DashTab = 'dashboard' | 'gold-session' | 'pravzella'

function getSessionLabel(utcH: number): string {
  if (utcH >= 13 && utcH < 16) return 'OVERLAP'
  if (utcH >= 8 && utcH < 16) return 'LONDON'
  if (utcH >= 16 && utcH < 21) return 'NEW_YORK'
  if (utcH >= 0 && utcH < 8) return 'ASIAN'
  return 'OFF'
}

export function App() {
  const [activeTab, setActiveTab] = useState<DashTab>('dashboard')
  const [refreshKey, setRefreshKey] = useState(0)
  const [lastRefresh, setLastRefresh] = useState('')

  const snapshot = useDailySnapshot()
  const livePrices = useCTraderPrices()
  const prices = livePrices.status === 'live'
    ? livePrices
    : (snapshot?.snapshotPrices ? pricesFromSnapshot(snapshot.snapshotPrices) : livePrices)
  const calendar = snapshot?.economicCalendar ?? []
  const newsItems = snapshot?.newsItems ?? []
  const vix = snapshot?.marketVolatility?.VIX ?? null

  const riskTone = aggregateData(
    prices, snapshot, calendar, newsItems, vix,
    getSessionLabel(new Date().getUTCHours()),
  ).marketVolatility.riskTone

  const handleRefresh = useCallback(() => {
    setRefreshKey(k => k + 1)
    const now = new Date()
    setLastRefresh(
      `${String(now.getUTCHours()).padStart(2,'0')}:${String(now.getUTCMinutes()).padStart(2,'0')} GMT`
    )
  }, [])

  // Suppress unused variable warning for refreshKey
  void refreshKey

  return (
    <div className={styles.app}>
      <Header prices={prices} onRefresh={handleRefresh} lastRefresh={lastRefresh} />

      <SessionTimeline />

      <nav className={styles.tabNav}>
        <button
          className={`${styles.tabBtn} ${activeTab === 'dashboard' ? styles.tabBtnActive : ''}`}
          onClick={() => setActiveTab('dashboard')}
        >
          Macro Dashboard
        </button>
        <button
          className={`${styles.tabBtn} ${activeTab === 'gold-session' ? styles.tabBtnActive : ''}`}
          onClick={() => setActiveTab('gold-session')}
        >
          Gold-Session AI
        </button>
        <button
          className={`${styles.tabBtn} ${activeTab === 'pravzella' ? styles.tabBtnActive : ''}`}
          onClick={() => setActiveTab('pravzella')}
        >
          Pravzella
        </button>
      </nav>

      {activeTab === 'dashboard' && (
        <main className={styles.main}>
          <MacroStrip prices={prices} snapshot={snapshot} />
          {/* Row 1: Yields | Dollar | Calendar */}
          <div className={styles.grid3}>
            <YieldsTile yields={snapshot?.yields ?? null} />
            <DollarTile prices={prices} />
            <CalendarTile events={calendar} />
          </div>

          {/* Row 2: Gold | Risk Tone | Fed */}
          <div className={styles.grid3}>
            <GoldTile
              prices={prices}
              gvz={snapshot?.marketVolatility?.GVZ ?? null}
            />
            <EquitiesTile
              prices={prices}
              vix={vix}
              riskTone={riskTone}
              dollarLiquidity={snapshot?.dollarLiquidity ?? null}
              geopoliticalRisk={snapshot?.geopoliticalRisk ?? null}
            />
            <FedTile fed={snapshot?.fedExpectations ?? null} />
          </div>

          {/* Row 3: Positioning | Flows */}
          <div className={styles.grid2}>
            <PositioningTile cot={snapshot?.positioning ?? null} />
            <FlowsTile flows={snapshot?.etfFlows ?? null} />
          </div>

          {/* Briefing panel — full width */}
          <BriefingPanel briefing={snapshot?.briefing ?? null} newsItems={newsItems} />
        </main>
      )}

      {activeTab === 'gold-session' && (
        <div className={styles.sessionPane}>
          <GoldSessionTab />
        </div>
      )}

      {activeTab === 'pravzella' && (
        <div className={styles.sessionPane}>
          <Suspense fallback={<div className={styles.tabLoading}>Loading…</div>}>
            <PravzellaTab />
          </Suspense>
        </div>
      )}

      <Footer />
    </div>
  )
}
