import type { EarthquakeListResponse, EarthquakeOut, PredictionRequest, PredictionResponse } from "../types"

const DEFAULT_API_BASE = "http://localhost:8000"

export const API_BASE = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? DEFAULT_API_BASE

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {})
    },
    ...init
  })

  if (!res.ok) {
    const text = await res.text().catch(() => "")
    throw new Error(text || `Request failed: ${res.status}`)
  }

  return (await res.json()) as T
}

export async function fetchLive(maxItems = 50): Promise<EarthquakeOut> {
  const qs = new URLSearchParams({ max_items: String(maxItems) })
  return requestJson<EarthquakeOut>(`/earthquakes/live?${qs.toString()}`)
}

export async function fetchHistory(): Promise<EarthquakeListResponse> {
  return requestJson<EarthquakeListResponse>("/earthquakes/history")
}

export async function predict(payload: PredictionRequest): Promise<PredictionResponse> {
  console.log("Prediction URL:", `${API_BASE}/predict/custom`)
  return requestJson<PredictionResponse>("/predict/custom", {
    method: "POST",
    body: JSON.stringify(payload)
  })
}

