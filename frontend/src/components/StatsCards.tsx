import { useMemo } from "react"
import { AlertTriangle, BarChart3, Globe, TrendingUp } from "lucide-react"
import type { EarthquakeOut } from "../types"
import { alertLabel } from "../utils/alert"

interface StatsCardsProps {
  earthquakes: EarthquakeOut[]
  loading?: boolean
}

export default function StatsCards({ earthquakes, loading = false }: StatsCardsProps) {
  const stats = useMemo(() => {
    if (!earthquakes.length) {
      return {
        total: 0,
        highestMagnitude: 0,
        redAlerts: 0,
        avgConfidence: 0
      }
    }

    const total = earthquakes.length
    const magnitudes = earthquakes.map(eq => eq.magnitude)
    const highestMagnitude = Math.max(...magnitudes)
    
    // Count red alerts (danger level)
    const redAlerts = earthquakes.filter(eq => {
      const alert = alertLabel(eq.alert_level)
      return alert === 'danger'
    }).length

    // Calculate average confidence (mock data for now since API doesn't provide confidence)
    const avgConfidence = 0.85 // This would come from prediction API

    return {
      total,
      highestMagnitude,
      redAlerts,
      avgConfidence
    }
  }, [earthquakes])

  const cards = [
    {
      title: "Total Earthquakes",
      value: stats.total.toLocaleString(),
      icon: Globe,
      color: "blue",
      change: "+12%",
      changeType: "increase" as const
    },
    {
      title: "Highest Magnitude",
      value: stats.highestMagnitude.toFixed(1),
      icon: BarChart3,
      color: "purple",
      change: "+0.3",
      changeType: "increase" as const
    },
    {
      title: "Red Alerts",
      value: stats.redAlerts.toString(),
      icon: AlertTriangle,
      color: "red",
      change: "-2",
      changeType: "decrease" as const
    },
    {
      title: "Avg Confidence",
      value: `${(stats.avgConfidence * 100).toFixed(0)}%`,
      icon: TrendingUp,
      color: "green",
      change: "+5%",
      changeType: "increase" as const
    }
  ]

  const getColorClasses = (color: string) => {
    const colorMap = {
      blue: "from-blue-500/20 to-blue-600/20 border-blue-500/20 text-blue-400",
      purple: "from-purple-500/20 to-purple-600/20 border-purple-500/20 text-purple-400",
      red: "from-red-500/20 to-red-600/20 border-red-500/20 text-red-400",
      green: "from-green-500/20 to-green-600/20 border-green-500/20 text-green-400"
    }
    return colorMap[color as keyof typeof colorMap]
  }

  const getChangeColor = (type: "increase" | "decrease") => {
    return type === "increase" ? "text-green-400" : "text-red-400"
  }

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="h-32 rounded-xl border border-white/10 bg-white/5 animate-pulse" />
        ))}
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card, index) => {
        const Icon = card.icon
        return (
          <div
            key={index}
            className={`
              relative overflow-hidden rounded-xl border backdrop-blur-sm
              bg-gradient-to-br ${getColorClasses(card.color)}
              transition-all duration-300 hover:scale-105 hover:border-opacity-40
            `}
          >
            <div className="relative p-6">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <p className="text-sm font-medium text-white/70">{card.title}</p>
                  <p className="mt-2 text-3xl font-bold text-white">{card.value}</p>
                  <div className={`mt-2 flex items-center text-sm ${getChangeColor(card.changeType)}`}>
                    <span>{card.change}</span>
                    <span className="ml-1 text-xs text-white/50">vs last period</span>
                  </div>
                </div>
                <div className="rounded-lg bg-white/10 p-3">
                  <Icon className="h-6 w-6" />
                </div>
              </div>
              
              {/* Animated background effect */}
              <div className="absolute -right-4 -bottom-4 h-24 w-24 rounded-full bg-white/5 blur-xl" />
              <div className="absolute -right-2 -bottom-2 h-16 w-16 rounded-full bg-white/10 blur-lg" />
            </div>
          </div>
        )
      })}
    </div>
  )
}
