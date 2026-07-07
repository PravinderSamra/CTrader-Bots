import { useHistory, type HistorySeries } from '../../hooks/useHistory'
import { SparkLine } from './SparkLine'

interface Props {
  metric: HistorySeries
  /** true = colour by direction (green up / red down); false = neutral gold. */
  signed?: boolean
  label?: string
}

/**
 * Drop-in 7-day sparkline for a dashboard tile. Renders nothing until at least
 * two history points exist (so tiles look unchanged before history accrues).
 */
export function TileSpark({ metric, signed = false, label }: Props) {
  const { series } = useHistory()
  const data = series(metric)
  if (data.filter(v => v != null).length < 2) return null
  return (
    <div className="tile-spark">
      <SparkLine data={data} width={140} height={26} signed={signed} ariaLabel={label ?? `${metric} 7-day trend`} />
      <span className="tile-spark-label">7-day</span>
    </div>
  )
}
