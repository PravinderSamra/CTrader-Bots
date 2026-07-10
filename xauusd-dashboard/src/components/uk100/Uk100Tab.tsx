import { useState } from 'react'
import { useUk100Snapshot } from '../../hooks/useUk100Snapshot'
import { Uk100BiasTile } from '../uk100-tiles/Uk100BiasTile'
import { Uk100FxTile } from '../uk100-tiles/Uk100FxTile'
import { Uk100RatesTile } from '../uk100-tiles/Uk100RatesTile'
import { Uk100UsLinkageTile } from '../uk100-tiles/Uk100UsLinkageTile'
import { Uk100CommoditiesTile } from '../uk100-tiles/Uk100CommoditiesTile'
import { Uk100PositioningTile } from '../uk100-tiles/Uk100PositioningTile'
import { Uk100OrbTile } from '../uk100-tiles/Uk100OrbTile'
import { Uk100SectorTile } from '../uk100-tiles/Uk100SectorTile'
import { Uk100CalendarTile } from '../uk100-tiles/Uk100CalendarTile'
import { AiSubTab } from './AiSubTab'
import styles from './Uk100Tab.module.css'

type SubTab = 'macro' | 'ai'

export function Uk100Tab() {
  const [subTab, setSubTab] = useState<SubTab>('macro')
  const snapshot = useUk100Snapshot()

  return (
    <div className={styles.wrap}>
      <nav className={styles.subNav}>
        <button
          className={`${styles.subTabBtn} ${subTab === 'macro' ? styles.subTabBtnActive : ''}`}
          onClick={() => setSubTab('macro')}
        >
          Macro
        </button>
        <button
          className={`${styles.subTabBtn} ${subTab === 'ai' ? styles.subTabBtnActive : ''}`}
          onClick={() => setSubTab('ai')}
        >
          AI Session
        </button>
      </nav>

      {subTab === 'macro' && (
        <main className={styles.main}>
          <div className={styles.biasRow}>
            <Uk100BiasTile bias={snapshot?.bias ?? null} />
          </div>

          <div className={styles.grid3}>
            <Uk100FxTile fx={snapshot?.fx ?? null} prices={snapshot?.prices ?? null} />
            <Uk100RatesTile rates={snapshot?.ukRates ?? null} />
            <Uk100UsLinkageTile usLinkage={snapshot?.usLinkage ?? null} prices={snapshot?.prices ?? null} />
          </div>

          <div className={styles.grid3}>
            <Uk100CommoditiesTile commodities={snapshot?.commodities ?? null} prices={snapshot?.prices ?? null} />
            <Uk100PositioningTile positioning={snapshot?.positioning ?? null} />
            <Uk100OrbTile orb={snapshot?.orbContext ?? null} />
          </div>

          <div className={styles.grid2}>
            <Uk100SectorTile sectors={snapshot?.sectorPanel ?? []} />
            <Uk100CalendarTile events={snapshot?.economicCalendar ?? []} news={snapshot?.newsItems ?? []} />
          </div>
        </main>
      )}

      {subTab === 'ai' && <AiSubTab />}
    </div>
  )
}
