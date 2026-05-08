import { useEffect, useMemo, useState } from "react"
import { Activity, DatabaseZap, RefreshCw } from "lucide-react"
import type { EarthquakeOut } from "../types"
import { fetchHistory, fetchLive } from "../utils/api"
import { alertLabel } from "../utils/alert"
import AlertBadge from "../components/AlertBadge"
import Card from "../components/Card"
import PredictionForm from "../components/PredictionForm"
import RecentEarthquakesTable from "../components/RecentEarthquakesTable"
import StatsCards from "../components/StatsCards"
import EarthquakeMap from "../components/EarthquakeMap"
import AnalyticsCharts from "../components/AnalyticsCharts"
import LiveAlertPanel from "../components/LiveAlertPanel"
import useInterval from "../hooks/useInterval"

type LoadState = "idle" | "loading" | "ready" | "error"

function formatTime(iso: string) {
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return iso
  return d.toLocaleString()
}

export default function DashboardPage() {
  const [latest, setLatest] = useState<EarthquakeOut | null>(null)
  const [history, setHistory] = useState<EarthquakeOut[]>([])
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null)
  const [liveState, setLiveState] = useState<LoadState>("idle")
  const [historyState, setHistoryState] = useState<LoadState>("idle")
  const [error, setError] = useState<string | null>(null)

  const latestLevel = useMemo(() => (latest ? alertLabel(latest.alert_level) : null), [latest])

  async function loadHistory() {
    setHistoryState((s) => (s === "ready" ? "ready" : "loading"))
    try {
      const res = await fetchHistory()
      setHistory(res.items.slice(0, 50))
      setHistoryState("ready")
    } catch (err) {
      setHistoryState("error")
      setError(err instanceof Error ? err.message : "Failed to load history")
    }
  }

  async function loadLive() {
    setLiveState((s) => (s === "ready" ? "ready" : "loading"))
    try {
      const res = await fetchLive(50)
      setLatest(res)
      setLastRefresh(new Date())
      setLiveState("ready")
      setError(null)
    } catch (err) {
      setLiveState("error")
      setError(err instanceof Error ? err.message : "Failed to load live data")
    }
  }

  async function resetDashboard() {
    // Reset all state to initial values
    setLatest(null)
    setHistory([])
    setLastRefresh(null)
    setError(null)
    setHistoryState("idle")
    setLiveState("idle")
    
    // Reload fresh data
    await loadHistory()
    await loadLive()
  }

  useEffect(() => {
    void loadHistory()
    void loadLive()
  }, [])

  useInterval(() => {
    void loadLive()
  }, 30000) // Update every 30 seconds

  const statusPill =
    liveState === "error"
      ? "bg-red-500/10 text-red-100 ring-red-500/20"
      : liveState === "loading"
        ? "bg-white/5 text-white/70 ring-white/10"
        : "bg-emerald-500/10 text-emerald-100 ring-emerald-500/20"

  return (
    <div className="min-h-screen">
      <div className="sticky top-0 z-10 border-b border-white/10 bg-graphite-950/70 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-3 px-4 py-4">
          <div className="min-w-0">
            <div className="flex items-center gap-2 text-sm font-semibold text-white/85">
              <Activity className="h-4 w-4 text-white/75" />
              Earthquake Monitoring
            </div>
            <div className="mt-1 flex items-center gap-3 text-xs text-white/55">
              <span className={["inline-flex items-center gap-2 rounded-full px-3 py-1 ring-1", statusPill].join(" ")}>
                <span className="h-2 w-2 rounded-full bg-current opacity-80" />
                {liveState === "error" ? "API error" : liveState === "loading" ? "syncing…" : "connected"}
              </span>
              <span className="font-mono">
                {lastRefresh ? `last refresh ${lastRefresh.toLocaleTimeString()}` : "waiting for first refresh"}
              </span>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {latestLevel ? <AlertBadge level={latestLevel} /> : null}
            <button
              type="button"
              onClick={() => {
                void resetDashboard()
              }}
              className="inline-flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs font-semibold text-white/80 hover:bg-white/10 transition-colors"
            >
              <RefreshCw className="h-4 w-4" />
              Reset All
            </button>
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-7xl px-4 py-6 space-y-6">
        {/* Stats Cards */}
        <StatsCards 
          earthquakes={history} 
          loading={historyState === "loading"} 
        />

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content Area */}
          <div className="lg:col-span-2 space-y-6">
            {/* Latest Event Card */}
            <Card className="p-6">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="text-lg font-semibold tracking-wide text-white/90">Latest Event</div>
                  <div className="mt-1 text-sm text-white/60">Real-time earthquake monitoring</div>
                </div>
                <div className="rounded-xl bg-white/5 p-3 ring-1 ring-white/10">
                  <DatabaseZap className="h-6 w-6 text-white/80" />
                </div>
              </div>

              {latest ? (
                <div className="mt-6 grid grid-cols-2 gap-4 md:grid-cols-4">
                  <Stat label="Magnitude" value={latest.magnitude.toFixed(2)} mono />
                  <Stat label="Depth (km)" value={latest.depth.toFixed(1)} mono />
                  <Stat label="Latitude" value={latest.latitude.toFixed(3)} mono />
                  <Stat label="Longitude" value={latest.longitude.toFixed(3)} mono />
                  <div className="col-span-2 md:col-span-4">
                    <div className="mt-2 rounded-xl border border-white/10 bg-white/5 px-4 py-4">
                      <div className="text-sm font-semibold text-white/80">Location</div>
                      <div className="mt-2 text-base font-medium text-white/95">{latest.location}</div>
                      <div className="mt-2 font-mono text-sm text-white/60">{formatTime(latest.time)}</div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="mt-6 rounded-xl border border-white/10 bg-white/5 px-4 py-12 text-center">
                  <div className="text-white/70">
                    {liveState === "loading" ? "Loading latest event…" : "No live event available yet."}
                  </div>
                </div>
              )}
            </Card>

            {/* Earthquake Map */}
            <div>
              <div className="mb-4">
                <div className="text-lg font-semibold text-white/90">Live Earthquake Map</div>
                <div className="mt-1 text-sm text-white/60">Global seismic activity visualization</div>
              </div>
              <EarthquakeMap 
                earthquakes={history.slice(0, 50)} 
                loading={historyState === "loading"} 
                onReset={resetDashboard}
                onRefresh={() => {
                  void loadHistory()
                  void loadLive()
                }}
              />
            </div>

            {/* Analytics Charts */}
            <div>
              <div className="mb-4">
                <div className="text-lg font-semibold text-white/90">Analytics Dashboard</div>
                <div className="mt-1 text-sm text-white/60">Seismic data analysis and trends</div>
              </div>
              <AnalyticsCharts 
                earthquakes={history} 
                loading={historyState === "loading"} 
              />
            </div>

            {/* Recent Earthquakes Table */}
            <div>
              <div className="mb-4 flex items-center justify-between">
                <div>
                  <div className="text-lg font-semibold text-white/90">Recent Earthquakes</div>
                  <div className="mt-1 text-sm text-white/60">Latest seismic events worldwide</div>
                </div>
                <div className="text-sm text-white/60">
                  {historyState === "loading" ? "loading…" : `${history.length} events`}
                </div>
              </div>
              <RecentEarthquakesTable items={history} />
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Live Alert Panel */}
            <LiveAlertPanel 
              earthquakes={history} 
              loading={historyState === "loading"} 
            />

            {/* Prediction Form */}
            <PredictionForm />

            {/* Error Display */}
            {error ? (
              <Card className="p-4">
                <div className="text-sm font-semibold text-white/80">System Alert</div>
                <div className="mt-2 text-sm text-white/70">{error}</div>
              </Card>
            ) : null}

            {/* System Status */}
            <Card className="p-4">
              <div className="text-sm font-semibold text-white/80">System Status</div>
              <div className="mt-3 space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-white/60">Data Source</span>
                  <span className="text-white/80">USGS Live Feed</span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-white/60">Update Interval</span>
                  <span className="text-white/80">30 seconds</span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-white/60">Total Events</span>
                  <span className="text-white/80">{history.length}</span>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}

function Stat({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/5 px-4 py-3">
      <div className="text-xs font-semibold text-white/70">{label}</div>
      <div className={["mt-1 text-lg font-semibold text-white/90", mono ? "font-mono" : ""].join(" ")}>
        {value}
      </div>
    </div>
  )
}

