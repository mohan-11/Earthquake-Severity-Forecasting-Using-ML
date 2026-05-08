export type AlertLevel = "SAFE" | "WARNING" | "DANGER"

export type EarthquakeOut = {
  id: number | null
  magnitude: number
  depth: number
  latitude: number
  longitude: number
  location: string
  time: string
  alert_level: AlertLevel
}

export type EarthquakeListResponse = {
  count: number
  items: EarthquakeOut[]
}

export type PredictionRequest = {
  magnitude: number
  depth: number
  latitude: number
  longitude: number
}

export type PredictionResponse = {
  prediction: AlertLevel
  confidence: number
}

