import { motion } from "framer-motion"
import { AlertTriangle, Clock, MapPin } from "lucide-react"
import type { EarthquakeOut } from "../types"
import { alertLabel } from "../utils/alert"

interface LiveAlertPanelProps {
  earthquakes: EarthquakeOut[]
  loading?: boolean
}

export default function LiveAlertPanel({ earthquakes, loading = false }: LiveAlertPanelProps) {
  // Filter for high severity earthquakes (warning and danger)
  const criticalEarthquakes = earthquakes.filter(eq => {
    return eq.alert_level === 'WARNING' || eq.alert_level === 'DANGER'
  }).slice(0, 5) // Show latest 5 critical alerts

  const getAlertColor = (alertLevel: string) => {
    return alertLevel === 'DANGER' ? 'border-red-500 bg-red-500/10' : 'border-yellow-500 bg-yellow-500/10'
  }

  const getAlertIconColor = (alertLevel: string) => {
    return alertLevel === 'DANGER' ? 'text-red-400' : 'text-yellow-400'
  }

  const formatTimeAgo = (time: string) => {
    const now = new Date()
    const eventTime = new Date(time)
    const diffMs = now.getTime() - eventTime.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    
    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins} min ago`
    const diffHours = Math.floor(diffMins / 60)
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`
    return eventTime.toLocaleDateString()
  }

  if (loading) {
    return (
      <div className="rounded-xl border border-white/10 bg-white/5 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Live Alerts</h3>
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-20 rounded-lg border border-white/10 bg-white/5 animate-pulse" />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">Live Critical Alerts</h3>
        <div className="flex items-center gap-2">
          <div className="h-2 w-2 bg-red-500 rounded-full animate-pulse" />
          <span className="text-xs text-white/60">
            {criticalEarthquakes.length} active
          </span>
        </div>
      </div>

      {criticalEarthquakes.length === 0 ? (
        <div className="text-center py-8">
          <AlertTriangle className="h-12 w-12 text-white/20 mx-auto mb-3" />
          <p className="text-white/60 text-sm">No critical alerts at this time</p>
          <p className="text-white/40 text-xs mt-1">System monitoring for high-severity events</p>
        </div>
      ) : (
        <div className="space-y-3">
          {criticalEarthquakes.map((earthquake, index) => (
            <motion.div
              key={`${earthquake.id || index}`}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1, duration: 0.3 }}
              className={`
                rounded-lg border p-4 transition-all duration-300 hover:scale-[1.02]
                ${getAlertColor(earthquake.alert_level)}
                ${earthquake.alert_level === 'DANGER' ? 'animate-pulse' : ''}
              `}
            >
              <div className="flex items-start gap-3">
                <div className={`p-2 rounded-lg bg-black/20 ${getAlertIconColor(earthquake.alert_level)}`}>
                  <AlertTriangle className="h-4 w-4" />
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <h4 className="font-semibold text-white text-sm truncate">
                      M{earthquake.magnitude.toFixed(1)} Earthquake
                    </h4>
                    <span className={`text-xs font-medium capitalize ${getAlertIconColor(earthquake.alert_level)}`}>
                      {alertLabel(earthquake.alert_level)}
                    </span>
                  </div>
                  
                  <div className="flex items-center gap-2 text-xs text-white/60 mb-2">
                    <MapPin className="h-3 w-3" />
                    <span className="truncate">{earthquake.location}</span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3 text-xs text-white/50">
                      <span>Depth: {earthquake.depth.toFixed(1)}km</span>
                      <div className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        <span>{formatTimeAgo(earthquake.time)}</span>
                      </div>
                    </div>
                    
                    {earthquake.alert_level === 'DANGER' && (
                      <motion.div
                        animate={{ scale: [1, 1.1, 1] }}
                        transition={{ repeat: Infinity, duration: 2 }}
                        className="px-2 py-1 bg-red-500 rounded text-xs text-white font-medium"
                      >
                        URGENT
                      </motion.div>
                    )}
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {criticalEarthquakes.length > 0 && (
        <div className="mt-4 pt-4 border-t border-white/10">
          <div className="flex items-center justify-between text-xs text-white/50">
            <span>Auto-updating every 30 seconds</span>
            <div className="flex items-center gap-1">
              <div className="h-2 w-2 bg-green-500 rounded-full" />
              <span>System Active</span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
