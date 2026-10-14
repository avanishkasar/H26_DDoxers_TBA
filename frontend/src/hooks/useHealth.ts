import { useEffect, useState } from 'react'
import { getHealth, type Health } from '../lib/api'

const POLL_MS = 10_000

export function useHealth(): Health | null {
  const [health, setHealth] = useState<Health | null>(null)

  useEffect(() => {
    let controller = new AbortController()
    const poll = (): void => {
      controller.abort()
      controller = new AbortController()
      getHealth(controller.signal)
        .then(setHealth)
        .catch((err: unknown) => {
          if (err instanceof DOMException && err.name === 'AbortError') return
          setHealth(null)
        })
    }
    poll()
    const id = window.setInterval(poll, POLL_MS)
    return () => {
      window.clearInterval(id)
      controller.abort()
    }
  }, [])

  return health
}
