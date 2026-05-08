import { ArrowDownRight, ArrowUpRight } from "lucide-react"
import type { EarthquakeOut } from "../types"
import AlertBadge from "./AlertBadge"
import { alertLabel, alertColors } from "../utils/alert"

function formatTime(iso: string) {
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return iso
  return d.toLocaleString()
}

function magnitudeIcon(magnitude: number) {
  if (magnitude >= 6) return <ArrowUpRight className="h-4 w-4 text-red-200" />
  if (magnitude >= 4.5) return <ArrowUpRight className="h-4 w-4 text-orange-200" />
  return <ArrowDownRight className="h-4 w-4 text-emerald-200" />
}

export default function RecentEarthquakesTable({
  items
}: {
  items: EarthquakeOut[]
}) {
  return (
    <div className="overflow-hidden rounded-2xl border border-white/10">
      <div className="grid grid-cols-[1.2fr_1fr_0.9fr_0.9fr] gap-3 bg-white/5 px-4 py-3 text-xs font-semibold uppercase tracking-wide text-white/70">
        <div>Location</div>
        <div>Time</div>
        <div className="text-right">Magnitude</div>
        <div className="text-right">Alert</div>
      </div>
      <div className="max-h-[520px] overflow-auto">
        {items.map((e) => {
          const level = alertLabel(e.alert_level)
          const c = alertColors(level)
          return (
            <div
              key={`${e.time}-${e.latitude}-${e.longitude}-${e.magnitude}`}
              className="group grid grid-cols-[1.2fr_1fr_0.9fr_0.9fr] gap-3 border-t border-white/10 px-4 py-3 text-sm hover:bg-white/5"
            >
              <div className="flex items-center gap-3">
                <div className={["h-8 w-1 rounded-full", c.stripe].join(" ")} />
                <div className="min-w-0">
                  <div className="truncate font-medium text-white/90">{e.location}</div>
                  <div className="font-mono text-xs text-white/55">
                    {e.latitude.toFixed(3)}, {e.longitude.toFixed(3)} · {e.depth.toFixed(1)} km
                  </div>
                </div>
              </div>
              <div className="text-white/75">{formatTime(e.time)}</div>
              <div className="flex items-center justify-end gap-2 font-mono">
                {magnitudeIcon(e.magnitude)}
                <span className="text-white/90">{e.magnitude.toFixed(2)}</span>
              </div>
              <div className="flex justify-end">
                <AlertBadge level={level} />
              </div>
            </div>
          )
        })}
        {items.length === 0 ? (
          <div className="px-4 py-10 text-center text-sm text-white/60">
            No history available yet.
          </div>
        ) : null}
      </div>
    </div>
  )
}

