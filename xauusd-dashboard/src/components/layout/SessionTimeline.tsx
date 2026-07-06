import { useState, useEffect } from 'react'
import styles from './SessionTimeline.module.css'

// Sessions in UTC minutes (fixed reference — Header.tsx uses same boundaries)
const SESSIONS = [
  { name: 'ASIAN',    start:    0, end:  8*60, cls: styles.segAsian    },
  { name: 'LONDON',   start:  8*60, end: 13*60, cls: styles.segLondon   },
  { name: 'OVERLAP',  start: 13*60, end: 16*60, cls: styles.segOverlap  },
  { name: 'NY',       start: 16*60, end: 21*60, cls: styles.segNY       },
  { name: 'OFF',      start: 21*60, end: 24*60, cls: styles.segAsian    },
]

// Kill zone bands in UTC minutes (approximate, DST can shift ±60min but close enough for visual)
const KZ_BANDS = [
  { name: 'London KZ',  start:  7*60, end: 10*60, cls: styles.kzLondon  },
  { name: 'NY KZ',      start: 12*60+30, end: 16*60, cls: styles.kzNY   },
  { name: 'Lon Close',  start: 14*60, end: 15*60, cls: styles.kzClose   },
]

function pct(mins: number) { return (mins / (24 * 60)) * 100 }

function labelForMinutes(utcMins: number): string {
  const h = Math.floor(utcMins / 60) % 24
  return `${String(h).padStart(2,'0')}:00`
}

export function SessionTimeline() {
  const [now, setNow] = useState(new Date())
  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 60_000)
    return () => clearInterval(id)
  }, [])

  const utcMins = now.getUTCHours() * 60 + now.getUTCMinutes()
  const nowPct  = pct(utcMins)

  const activeSeg = SESSIONS.find(s => utcMins >= s.start && utcMins < s.end) ?? SESSIONS[SESSIONS.length - 1]
  const activeKZ  = KZ_BANDS.find(kz => utcMins >= kz.start && utcMins < kz.end)

  return (
    <div className={styles.shell}>
      <div className={styles.barWrap}>
        {/* Session segments */}
        {SESSIONS.map(s => (
          <div
            key={s.name}
            className={`${styles.seg} ${s.cls}`}
            style={{ left: `${pct(s.start)}%`, width: `${pct(s.end - s.start)}%` }}
            title={s.name}
          />
        ))}

        {/* Kill zone overlays */}
        {KZ_BANDS.map(kz => (
          <div
            key={kz.name}
            className={`${styles.kz} ${kz.cls}`}
            style={{ left: `${pct(kz.start)}%`, width: `${pct(kz.end - kz.start)}%` }}
            title={kz.name}
          />
        ))}

        {/* Hour ticks */}
        {[4, 8, 12, 13, 16, 21].map(h => (
          <div key={h} className={styles.tick} style={{ left: `${pct(h * 60)}%` }} />
        ))}

        {/* Now cursor */}
        <div className={styles.cursor} style={{ left: `${nowPct}%` }} title="Now" />
      </div>

      {/* Labels */}
      <div className={styles.labels}>
        <span className={`${styles.lbl} ${styles.lblAsian}`}   style={{ left: `${pct(4 * 60)}%` }}>ASIAN</span>
        <span className={`${styles.lbl} ${styles.lblLondon}`}  style={{ left: `${pct(10.5 * 60)}%` }}>LONDON</span>
        <span className={`${styles.lbl} ${styles.lblOverlap}`} style={{ left: `${pct(14.5 * 60)}%` }}>OVR</span>
        <span className={`${styles.lbl} ${styles.lblNY}`}      style={{ left: `${pct(18.5 * 60)}%` }}>NEW YORK</span>

        {/* Boundary times */}
        {[0, 8, 13, 16, 21].map(h => (
          <span
            key={h}
            className={styles.timeLbl}
            style={{ left: `${pct(h * 60)}%` }}
          >
            {labelForMinutes(h * 60)}
          </span>
        ))}
      </div>

      {/* Active indicator */}
      <div className={styles.nowLabel}>
        <span className={styles.nowDot} />
        <span className={styles.nowText}>
          {activeKZ ? activeKZ.name : activeSeg.name}
        </span>
        <span className={styles.nowUtc}>{labelForMinutes(utcMins)} GMT</span>
      </div>
    </div>
  )
}
