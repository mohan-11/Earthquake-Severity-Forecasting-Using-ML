import type { AlertLevel } from "../types"
import { alertColors } from "../utils/alert"

export default function AlertBadge({ level }: { level: AlertLevel }) {
  const c = alertColors(level)
  return (
    <span
      className={[
        "inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-semibold ring-1",
        c.chip,
        c.ring,
        c.glow
      ].join(" ")}
    >
      <span className={["h-2 w-2 rounded-full", c.stripe].join(" ")} />
      {level}
    </span>
  )
}

