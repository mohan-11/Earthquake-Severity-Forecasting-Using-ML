import { useEffect, useRef, useState, useCallback, useMemo } from "react"
import { motion } from "framer-motion"
import { 
  MapContainer, 
  TileLayer, 
  Marker, 
  Popup, 
  useMap,
  ZoomControl,
  Circle
} from "react-leaflet"
import { DivIcon } from "leaflet"
import type { EarthquakeOut } from "../types"
import { alertLabel } from "../utils/alert"
import { 
  MapPin, 
  Maximize2, 
  RotateCcw, 
  RefreshCw,
  Activity
} from "lucide-react"

// Fix for default markers in react-leaflet
import L from "leaflet"

// Set default icon
const DefaultIcon = L.icon({
  iconUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
})

L.Marker.prototype.options.icon = DefaultIcon

interface EarthquakeMapProps {
  earthquakes: EarthquakeOut[]
  loading?: boolean
  onReset?: () => void
  onRefresh?: () => void
}

function MapController({ earthquakes, onReset }: { 
  earthquakes: EarthquakeOut[]
  onReset?: () => void 
}) {
  const map = useMap()
  
  useEffect(() => {
    if (earthquakes.length > 0) {
      // Fit map to show all earthquakes
      const bounds = earthquakes.map(eq => [eq.latitude, eq.longitude] as [number, number])
      map.fitBounds(bounds, { padding: [20, 20] })
    }
  }, [earthquakes, map])

  return null
}

function SeverityZones({ earthquakes }: { earthquakes: EarthquakeOut[] }) {
  const map = useMap()
  
  return (
    <>
      {earthquakes.map((earthquake, index) => {
        const alert = alertLabel(earthquake.alert_level)
        const radius = earthquake.magnitude * 20000 // Dynamic radius based on magnitude
        
        const zoneColors = {
          safe: { fill: '#10b98120', fillOpacity: 0.2, stroke: '#10b981', strokeOpacity: 0.4 },
          warning: { fill: '#f59e0b20', fillOpacity: 0.2, stroke: '#f59e0b', strokeOpacity: 0.4 },
          danger: { fill: '#ef444420', fillOpacity: 0.2, stroke: '#ef4444', strokeOpacity: 0.4 }
        }
        
        const colors = zoneColors[alert as keyof typeof zoneColors] || zoneColors.safe
        
        return (
          <Circle
            key={`zone-${index}`}
            center={[earthquake.latitude, earthquake.longitude]}
            radius={radius}
            pathOptions={{
              color: colors.stroke,
              fillColor: colors.fill,
              fillOpacity: colors.fillOpacity,
              weight: 2,
              opacity: 0.8
            }}
          />
        )
      })}
    </>
  )
}

function createCustomMarker(alertLevel: string, isSelected: boolean = false) {
  const alert = alertLabel(alertLevel)
  const colorMap = {
    safe: { main: "#10b981", glow: "#10b98140", border: "#10b981" },
    warning: { main: "#f59e0b", glow: "#f59e0b40", border: "#f59e0b" },
    danger: { main: "#ef4444", glow: "#ef444440", border: "#ef4444" }
  }
  const colors = colorMap[alert as keyof typeof colorMap] || colorMap.safe
  
  const scale = isSelected ? 1.3 : 1.0
  const size = 16 * scale

  return new DivIcon({
    html: `
      <div style="
        position: relative;
        width: ${size}px;
        height: ${size}px;
        display: flex;
        align-items: center;
        justify-content: center;
      ">
        <div style="
          background: ${colors.main};
          width: ${size * 0.6}px;
          height: ${size * 0.6}px;
          border-radius: 50%;
          border: 2px solid ${colors.border};
          box-shadow: 
            0 0 ${colors.glow},
            inset 0 0 ${colors.glow};
          animation: ${alert === 'DANGER' ? 'pulse 1.5s infinite' : 'none'};
          transition: all 0.3s ease;
        "></div>
        ${alert === 'DANGER' ? `
          <div style="
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: ${size * 1.5}px;
            height: ${size * 1.5}px;
            border-radius: 50%;
            border: 1px solid ${colors.border};
            animation: ripple 2s infinite;
            pointer-events: none;
          "></div>
        ` : ''}
      </div>
      <style>
        @keyframes pulse {
          0% { transform: scale(1); opacity: 1; }
          50% { transform: scale(1.2); opacity: 0.8; }
          100% { transform: scale(1); opacity: 1; }
        }
        @keyframes ripple {
          0% { transform: translate(-50%, -50%) scale(0.8); opacity: 1; }
          100% { transform: translate(-50%, -50%) scale(2); opacity: 0; }
        }
      </style>
    `,
    className: "custom-marker",
    iconSize: [size, size] as [number, number],
    iconAnchor: [size/2, size/2] as [number, number]
  })
}

function CustomPopup({ earthquake }: { earthquake: EarthquakeOut }) {
  const alert = alertLabel(earthquake.alert_level)
  const severityColors = {
    safe: "bg-green-500/20 text-green-400 border-green-500/30",
    warning: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30", 
    danger: "bg-red-500/20 text-red-400 border-red-500/30"
  }
  const colorClass = severityColors[alert as keyof typeof severityColors] || severityColors.safe

  return (
    <div className="min-w-72 p-0">
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className={`
          rounded-xl border backdrop-blur-sm
          ${colorClass}
          shadow-lg
        `}
      >
        <div className="p-4">
          {/* Header with magnitude */}
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-lg font-bold text-white">
              M{earthquake.magnitude.toFixed(1)} Earthquake
            </h3>
            <div className={`
              px-2 py-1 rounded-full text-xs font-medium
              ${alert === 'DANGER' ? 'bg-red-500 text-white' : 
                alert === 'WARNING' ? 'bg-yellow-500 text-black' : 
                'bg-green-500 text-white'}
            `}>
              {alert.toUpperCase()}
            </div>
          </div>

          {/* Location */}
          <div className="mb-3">
            <div className="flex items-center gap-2 text-sm text-white/80 mb-1">
              <MapPin className="h-4 w-4" />
              <span className="font-medium">{earthquake.location}</span>
            </div>
          </div>

          {/* Details Grid */}
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <div className="text-white/60">Magnitude</div>
              <div className="text-white font-medium">{earthquake.magnitude.toFixed(1)}</div>
            </div>
            <div>
              <div className="text-white/60">Depth (km)</div>
              <div className="text-white font-medium">{earthquake.depth.toFixed(1)}</div>
            </div>
            <div>
              <div className="text-white/60">Coordinates</div>
              <div className="text-white font-medium">
                {earthquake.latitude.toFixed(3)}, {earthquake.longitude.toFixed(3)}
              </div>
            </div>
            <div>
              <div className="text-white/60">Time</div>
              <div className="text-white font-medium">
                {new Date(earthquake.time).toLocaleString()}
              </div>
            </div>
            <div>
              <div className="text-white/60">Alert Level</div>
              <div className="text-white font-medium capitalize">{alert}</div>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  )
}

export default function EarthquakeMap({ 
  earthquakes, 
  loading = false, 
  onReset,
  onRefresh 
}: EarthquakeMapProps) {
  const [selectedMarker, setSelectedMarker] = useState<string | null>(null)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [showOnlyCritical, setShowOnlyCritical] = useState(false)
  const [minMagnitude, setMinMagnitude] = useState(0)
  const mapRef = useRef<L.Map>(null)

  // Memoize earthquake data for performance
  const memoizedEarthquakes = useMemo(() => earthquakes, [earthquakes])

  // Filter earthquakes based on user preferences
  const filteredEarthquakes = useMemo(() => {
    let filtered = memoizedEarthquakes
    
    if (showOnlyCritical) {
      filtered = filtered.filter(eq => {
        const alert = alertLabel(eq.alert_level)
        return alert === 'DANGER' || alert === 'WARNING'
      })
    }
    
    if (minMagnitude > 0) {
      filtered = filtered.filter(eq => eq.magnitude >= minMagnitude)
    }
    
    return filtered
  }, [memoizedEarthquakes, showOnlyCritical, minMagnitude])

  // Find strongest earthquake for auto-focus
  const strongestEarthquake = useMemo(() => {
    if (filteredEarthquakes.length === 0) return null
    return filteredEarthquakes.reduce((strongest, current) => 
      current.magnitude > strongest.magnitude ? current : strongest
    )
  }, [filteredEarthquakes])

  // Auto-focus on strongest earthquake
  useEffect(() => {
    if (mapRef.current && strongestEarthquake && filteredEarthquakes.length > 0) {
      const map = mapRef.current
      map.setView([strongestEarthquake.latitude, strongestEarthquake.longitude], 8, {
        animate: true,
        duration: 1.5
      })
    }
  }, [strongestEarthquake, filteredEarthquakes, mapRef])

  const handleMarkerClick = useCallback((earthquakeId: string) => {
    setSelectedMarker(earthquakeId === selectedMarker ? null : earthquakeId)
  }, [selectedMarker])

  const handleFullscreen = useCallback(() => {
    if (mapRef.current) {
      const map = mapRef.current
      if (isFullscreen) {
        map.invalidateSize()
        setIsFullscreen(false)
      } else {
        map.getContainer().requestFullscreen?.()
        setIsFullscreen(true)
      }
    }
  }, [isFullscreen])

  if (loading) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="h-96 rounded-2xl border border-white/10 bg-white/5 backdrop-blur-sm overflow-hidden"
      >
        <div className="h-full flex items-center justify-center">
          <div className="text-center">
            <div className="inline-flex items-center gap-3 mb-4">
              <RefreshCw className="h-6 w-6 animate-spin text-white/60" />
              <span className="text-white/60">Loading earthquake data...</span>
            </div>
            <div className="w-64 h-1 bg-white/10 rounded-full overflow-hidden">
              <motion.div
                className="h-full bg-gradient-to-r from-blue-500 to-purple-500"
                initial={{ width: "0%" }}
                animate={{ width: "100%" }}
                transition={{ duration: 1.5, ease: "easeInOut" }}
              />
            </div>
          </div>
        </div>
      </motion.div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="relative h-96 rounded-2xl border border-white/10 bg-white/5 backdrop-blur-sm overflow-hidden"
    >
      {/* Enhanced Map Title Section */}
      <div className="absolute top-4 left-4 z-10 bg-black/80 backdrop-blur-md rounded-lg px-4 py-2 border border-white/20">
        <div className="flex items-center justify-between gap-4">
          <div>
            <h3 className="text-sm font-semibold text-white mb-1">Live Earthquake Map</h3>
            <div className="flex items-center gap-3 text-xs text-white/60">
              <div className="flex items-center gap-1">
                <Activity className="h-3 w-3 text-green-400" />
                <span>Live</span>
              </div>
              <span>{filteredEarthquakes.length} events</span>
              <span>Updated {new Date().toLocaleTimeString()}</span>
            </div>
          </div>
          
          {/* Enhanced Map Controls */}
          <div className="flex items-center gap-2">
            <button
              onClick={onRefresh}
              className="p-2 rounded-lg bg-white/10 hover:bg-white/20 text-white/80 transition-colors"
              title="Refresh Map"
            >
              <RefreshCw className="h-4 w-4" />
            </button>
            <button
              onClick={onReset}
              className="p-2 rounded-lg bg-white/10 hover:bg-white/20 text-white/80 transition-colors"
              title="Reset Map View"
            >
              <RotateCcw className="h-4 w-4" />
            </button>
            <button
              onClick={handleFullscreen}
              className="p-2 rounded-lg bg-white/10 hover:bg-white/20 text-white/80 transition-colors"
              title="Toggle Fullscreen"
            >
              <Maximize2 className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Filter Controls */}
      <div className="absolute top-4 right-4 z-10 bg-black/80 backdrop-blur-md rounded-lg px-4 py-2 border border-white/20">
        <div className="flex items-center gap-3">
          <label className="text-xs text-white/60">Show Only:</label>
          <select
            value={showOnlyCritical ? 'critical' : 'all'}
            onChange={(e) => setShowOnlyCritical(e.target.value === 'critical')}
            className="bg-white/10 border border-white/20 rounded px-2 py-1 text-xs text-white/80"
          >
            <option value="all">All Events</option>
            <option value="critical">Critical Only</option>
          </select>
          
          <div className="flex items-center gap-2">
            <label className="text-xs text-white/60">Min Magnitude:</label>
            <input
              type="number"
              value={minMagnitude}
              onChange={(e) => setMinMagnitude(parseFloat(e.target.value) || 0)}
              className="bg-white/10 border border-white/20 rounded px-2 py-1 text-xs text-white/80 w-20"
              placeholder="0.0"
              min="0"
              max="10"
              step="0.1"
            />
          </div>
        </div>
      </div>

      <MapContainer
        ref={mapRef}
        center={[20, 0]}
        zoom={2}
        style={{ height: "100%", width: "100%" }}
        className="dark-map"
      >
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
        />
        
        <MapController earthquakes={filteredEarthquakes} onReset={onReset} />
        
        <SeverityZones earthquakes={filteredEarthquakes} />
        
        {filteredEarthquakes.map((earthquake, index) => (
          <Marker
            key={`${earthquake.id || index}`}
            position={[earthquake.latitude, earthquake.longitude]}
            icon={createCustomMarker(
              earthquake.alert_level, 
              selectedMarker === `${earthquake.id || index}`
            )}
            eventHandlers={{
              click: () => handleMarkerClick(`${earthquake.id || index}`)
            }}
          >
            <Popup>
              <CustomPopup earthquake={earthquake} />
            </Popup>
          </Marker>
        ))}
        
        {/* Map Controls */}
        <ZoomControl position="topright" />
      </MapContainer>

      {/* Enhanced Map Legend */}
      <div className="absolute bottom-4 right-4 bg-black/80 backdrop-blur-md rounded-lg p-4 border border-white/20">
        <div className="text-xs font-semibold text-white mb-2">Earthquake Severity Zones</div>
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-green-500 rounded-full border border-white shadow-green-500/50"></div>
            <span className="text-xs text-white/80">Safe (Low Risk)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-yellow-500 rounded-full border border-white shadow-yellow-500/50"></div>
            <span className="text-xs text-white/80">Moderate Risk</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-orange-500 rounded-full border border-white shadow-orange-500/50"></div>
            <span className="text-xs text-white/80">High Risk</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-red-500 rounded-full border border-white shadow-red-500/50 animate-pulse"></div>
            <span className="text-xs text-white/80">Critical Risk</span>
          </div>
        </div>
      </div>
    </motion.div>
  )
}
