import type { AlertLevel } from "../types"

export function alertLabel(level: string): AlertLevel {
  const upper = level.toUpperCase()
  if (upper === "SAFE" || upper === "WARNING" || upper === "DANGER") {
    return upper as AlertLevel
  }
  return "SAFE"
}

export function alertColors(level: AlertLevel): {
  chip: string
  ring: string
  glow: string
  stripe: string
} {
  if (level === "SAFE") {
    return {
      chip: "bg-emerald-500/15 text-emerald-200",
      ring: "ring-emerald-500/30",
      glow: "shadow-[0_0_0_1px_rgba(16,185,129,0.25),0_0_24px_rgba(16,185,129,0.18)]",
      stripe: "bg-emerald-500"
    }
  }
  if (level === "WARNING") {
    return {
      chip: "bg-orange-500/15 text-orange-200",
      ring: "ring-orange-500/30",
      glow: "shadow-[0_0_0_1px_rgba(249,115,22,0.25),0_0_24px_rgba(249,115,22,0.16)]",
      stripe: "bg-orange-500"
    }
  }
  return {
    chip: "bg-red-500/15 text-red-200",
    ring: "ring-red-500/30",
    glow: "shadow-[0_0_0_1px_rgba(239,68,68,0.28),0_0_24px_rgba(239,68,68,0.16)]",
    stripe: "bg-red-500"
  }
}

