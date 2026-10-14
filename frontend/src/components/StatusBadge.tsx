import { CircleCheck, CircleAlert, CircleX } from 'lucide-react'
import type { Health } from '../lib/api'

export function StatusBadge({ health }: { health: Health | null }) {
  if (!health) {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-full bg-red-500/10 px-3 py-1 text-xs text-red-400 ring-1 ring-red-500/30">
        <CircleX className="size-3.5" /> API offline
      </span>
    )
  }
  if (!health.llm_reachable || !health.model_available) {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-full bg-amber-500/10 px-3 py-1 text-xs text-amber-400 ring-1 ring-amber-500/30">
        <CircleAlert className="size-3.5" />
        {health.llm_reachable ? `${health.model} not pulled` : 'Ollama offline'}
      </span>
    )
  }
  return (
    <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-500/10 px-3 py-1 text-xs text-emerald-400 ring-1 ring-emerald-500/30">
      <CircleCheck className="size-3.5" /> {health.model}
    </span>
  )
}
