import type { ReactNode } from "react"

export default function Card({
  children,
  className
}: {
  children: ReactNode
  className?: string
}) {
  return (
    <div
      className={[
        "rounded-2xl border border-white/10 bg-graphite-900/70 backdrop-blur",
        "shadow-[0_0_0_1px_rgba(255,255,255,0.04),0_18px_48px_rgba(0,0,0,0.6)]",
        className ?? ""
      ].join(" ")}
    >
      {children}
    </div>
  )
}

