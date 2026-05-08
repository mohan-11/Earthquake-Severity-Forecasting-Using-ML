import { useMemo } from "react"
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from "recharts"
import type { EarthquakeOut } from "../types"
import { alertLabel } from "../utils/alert"

interface AnalyticsChartsProps {
  earthquakes: EarthquakeOut[]
  loading?: boolean
}

export default function AnalyticsCharts({ earthquakes, loading = false }: AnalyticsChartsProps) {
  const chartData = useMemo(() => {
    if (!earthquakes.length) {
      return {
        magnitudeTrend: [],
        severityDistribution: [],
        hourlyFrequency: []
      }
    }

    // Magnitude trend over time (last 24 hours grouped by hour)
    const magnitudeTrend = earthquakes
      .sort((a, b) => new Date(a.time).getTime() - new Date(b.time).getTime())
      .slice(-24)
      .map(eq => ({
        time: new Date(eq.time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        magnitude: eq.magnitude,
        alert: alertLabel(eq.alert_level)
      }))

    // Severity distribution
    const severityCounts = earthquakes.reduce((acc, eq) => {
      const alert = alertLabel(eq.alert_level)
      acc[alert] = (acc[alert] || 0) + 1
      return acc
    }, {} as Record<string, number>)

    const severityDistribution = Object.entries(severityCounts).map(([name, value]) => ({
      name: name.charAt(0).toUpperCase() + name.slice(1),
      value,
      color: name === 'safe' ? '#10b981' : name === 'warning' ? '#f59e0b' : '#ef4444'
    }))

    // Earthquakes per hour
    const hourlyData = earthquakes.reduce((acc, eq) => {
      const hour = new Date(eq.time).getHours()
      const hourStr = `${hour}:00`
      if (!acc[hourStr]) {
        acc[hourStr] = { hour: hourStr, count: 0 }
      }
      acc[hourStr].count++
      return acc
    }, {} as Record<string, { hour: string; count: number }>)

    const hourlyFrequency = Object.values(hourlyData).sort((a, b) => 
      parseInt(a.hour) - parseInt(b.hour)
    )

    return {
      magnitudeTrend,
      severityDistribution,
      hourlyFrequency
    }
  }, [earthquakes])

  if (loading) {
    return (
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="h-80 rounded-xl border border-white/10 bg-white/5 animate-pulse" />
        <div className="h-80 rounded-xl border border-white/10 bg-white/5 animate-pulse" />
        <div className="h-80 rounded-xl border border-white/10 bg-white/5 animate-pulse lg:col-span-2" />
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Magnitude Trend Chart */}
      <div className="rounded-xl border border-white/10 bg-white/5 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Magnitude Trend</h3>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={chartData.magnitudeTrend}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis 
              dataKey="time" 
              stroke="#9ca3af"
              tick={{ fill: '#9ca3af', fontSize: 12 }}
            />
            <YAxis 
              stroke="#9ca3af"
              tick={{ fill: '#9ca3af', fontSize: 12 }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1f2937',
                border: '1px solid #374151',
                borderRadius: '8px'
              }}
              labelStyle={{ color: '#f3f4f6' }}
            />
            <Line
              type="monotone"
              dataKey="magnitude"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={{ fill: '#3b82f6', r: 4 }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Severity Distribution Pie Chart */}
      <div className="rounded-xl border border-white/10 bg-white/5 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Severity Distribution</h3>
        <ResponsiveContainer width="100%" height={250}>
          <PieChart>
            <Pie
              data={chartData.severityDistribution}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {chartData.severityDistribution.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: '#1f2937',
                border: '1px solid #374151',
                borderRadius: '8px'
              }}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Hourly Frequency Bar Chart */}
      <div className="rounded-xl border border-white/10 bg-white/5 p-6 lg:col-span-2">
        <h3 className="text-lg font-semibold text-white mb-4">Earthquakes per Hour</h3>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={chartData.hourlyFrequency}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis 
              dataKey="hour" 
              stroke="#9ca3af"
              tick={{ fill: '#9ca3af', fontSize: 12 }}
            />
            <YAxis 
              stroke="#9ca3af"
              tick={{ fill: '#9ca3af', fontSize: 12 }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1f2937',
                border: '1px solid #374151',
                borderRadius: '8px'
              }}
              labelStyle={{ color: '#f3f4f6' }}
            />
            <Bar dataKey="count" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
