import { useState, useMemo } from 'react'
import { useAuth } from '../../hooks/useAuth'
import { useTrades } from '../../hooks/useTrades'
import { computeMetrics } from '../../services/tradeMetrics'
import { LoginGate } from './LoginGate'
import { OverviewSubTab } from './overview/OverviewSubTab'
import { CalendarSubTab } from './calendar/CalendarSubTab'
import { TradeLogSubTab } from './trade-log/TradeLogSubTab'
import styles from './PravzellaTab.module.css'

type SubTab = 'overview' | 'calendar' | 'trade-log'

function PravzellaContent() {
  const { user, signOut } = useAuth()
  const { trades, loading, error } = useTrades(user)
  const [subTab, setSubTab] = useState<SubTab>('overview')

  const metrics = useMemo(() => computeMetrics(trades), [trades])

  return (
    <div className={styles.wrap}>
      <nav className={styles.subNav}>
        <button className={`${styles.subTabBtn} ${subTab === 'overview' ? styles.subTabBtnActive : ''}`} onClick={() => setSubTab('overview')}>
          Overview
        </button>
        <button className={`${styles.subTabBtn} ${subTab === 'calendar' ? styles.subTabBtnActive : ''}`} onClick={() => setSubTab('calendar')}>
          Calendar
        </button>
        <button className={`${styles.subTabBtn} ${subTab === 'trade-log' ? styles.subTabBtnActive : ''}`} onClick={() => setSubTab('trade-log')}>
          Trade Log
        </button>
        <button className={styles.signOutBtn} onClick={signOut}>Sign out</button>
      </nav>

      {error && <div className={styles.errorBanner}>Failed to load trades: {error}</div>}

      <div className={styles.body}>
        {subTab === 'overview' && <OverviewSubTab metrics={metrics} loading={loading} />}
        {subTab === 'calendar' && <CalendarSubTab trades={trades} />}
        {subTab === 'trade-log' && <TradeLogSubTab trades={trades} />}
      </div>
    </div>
  )
}

export function PravzellaTab() {
  return (
    <LoginGate>
      <PravzellaContent />
    </LoginGate>
  )
}
