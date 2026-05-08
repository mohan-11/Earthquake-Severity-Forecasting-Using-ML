import { useMemo, useState } from "react"
import { Wand2 } from "lucide-react"
import type { PredictionRequest, PredictionResponse } from "../types"
import Card from "./Card"
import AlertBadge from "./AlertBadge"
import { alertLabel } from "../utils/alert"
import { predict } from "../utils/api"

function toNumber(value: string) {
  const n = Number(value)
  return Number.isFinite(n) ? n : null
}

export default function PredictionForm() {
  const [magnitude, setMagnitude] = useState("5.2")
  const [depth, setDepth] = useState("10")
  const [latitude, setLatitude] = useState("19.07")
  const [longitude, setLongitude] = useState("72.87")
  const [result, setResult] = useState<PredictionResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const payload = useMemo<PredictionRequest | null>(() => {
    const m = toNumber(magnitude)
    const d = toNumber(depth)
    const la = toNumber(latitude)
    const lo = toNumber(longitude)
    if (m === null || d === null || la === null || lo === null) return null
    return { magnitude: m, depth_km: d, latitude: la, longitude: lo, depth: d } as PredictionRequest
  }, [magnitude, depth, latitude, longitude])

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!payload) return
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const res = await predict(payload)
      setResult(res)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Prediction failed")
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card className="p-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="text-sm font-semibold tracking-wide text-white/80">
            Prediction Console
          </div>
          <div className="mt-1 text-xs text-white/55">
            Submit a hypothetical event and get an alert label + confidence.
          </div>
        </div>
        <div className="rounded-xl bg-white/5 p-2 ring-1 ring-white/10">
          <Wand2 className="h-5 w-5 text-white/80" />
        </div>
      </div>

      <form onSubmit={onSubmit} className="mt-5 space-y-4">
        <div className="grid grid-cols-2 gap-3">
          <Field
            label="Magnitude"
            value={magnitude}
            onChange={setMagnitude}
            placeholder="e.g. 5.2"
          />
          <Field
            label="Depth (km)"
            value={depth}
            onChange={setDepth}
            placeholder="e.g. 10"
          />
          <Field
            label="Latitude"
            value={latitude}
            onChange={setLatitude}
            placeholder="e.g. 19.07"
          />
          <Field
            label="Longitude"
            value={longitude}
            onChange={setLongitude}
            placeholder="e.g. 72.87"
          />
        </div>

        <button
          type="submit"
          disabled={!payload || loading}
          className={[
            "w-full rounded-xl px-4 py-3 text-sm font-semibold",
            "bg-white text-graphite-950 transition",
            "hover:bg-white/90 disabled:cursor-not-allowed disabled:opacity-50"
          ].join(" ")}
        >
          {loading ? "Predicting…" : "Predict"}
        </button>
      </form>

      {error ? (
        <div className="mt-4 rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-100">
          {error}
        </div>
      ) : null}

      {result ? (
        <div className="mt-4 rounded-xl border border-white/10 bg-white/5 px-4 py-4">
          <div className="flex items-center justify-between gap-3">
            <div className="text-sm font-semibold text-white/80">Result</div>
            <div className="font-mono text-xs text-white/55">
              confidence {result.confidence.toFixed(2)}
            </div>
          </div>
          <div className="mt-3">
            <AlertBadge level={alertLabel(result.prediction)} />
          </div>
        </div>
      ) : null}
    </Card>
  )
}

function Field({
  label,
  value,
  onChange,
  placeholder
}: {
  label: string
  value: string
  onChange: (v: string) => void
  placeholder: string
}) {
  return (
    <label className="block">
      <div className="text-xs font-semibold text-white/70">{label}</div>
      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        inputMode="decimal"
        className={[
          "mt-1 w-full rounded-xl border border-white/10 bg-graphite-950/40 px-3 py-2.5",
          "font-mono text-sm text-white/90 outline-none",
          "focus:border-white/25 focus:ring-2 focus:ring-white/10"
        ].join(" ")}
      />
    </label>
  )
}

