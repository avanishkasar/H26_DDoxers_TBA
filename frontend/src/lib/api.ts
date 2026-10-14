export type Role = 'system' | 'user' | 'assistant'

export interface ChatMessage {
  role: Role
  content: string
}

export interface Health {
  status: 'ok'
  llm_reachable: boolean
  model: string
  model_available: boolean
}

const API_BASE: string = import.meta.env.VITE_API_BASE_URL ?? ''

export class ApiError extends Error {
  readonly status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...init?.headers },
  })
  if (!res.ok) {
    const body = (await res.json().catch(() => null)) as { detail?: unknown } | null
    throw new ApiError(res.status, typeof body?.detail === 'string' ? body.detail : res.statusText)
  }
  return (await res.json()) as T
}

export const getHealth = (signal?: AbortSignal): Promise<Health> =>
  request<Health>('/api/health', { signal })

/** Streams assistant tokens from the SSE endpoint, calling onDelta for each chunk. */
export async function streamChat(
  messages: ChatMessage[],
  onDelta: (delta: string) => void,
  signal?: AbortSignal,
): Promise<void> {
  const res = await fetch(`${API_BASE}/api/chat/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ messages }),
    signal,
  })
  if (!res.ok || !res.body) throw new ApiError(res.status, res.statusText)

  const reader = res.body.pipeThrough(new TextDecoderStream()).getReader()
  let buffer = ''
  for (;;) {
    const { value, done } = await reader.read()
    if (done) return
    buffer += value
    const frames = buffer.split('\n\n')
    buffer = frames.pop() ?? ''
    for (const frame of frames) {
      if (!frame.startsWith('data: ')) continue
      const data = frame.slice(6)
      if (data === '[DONE]') return
      const parsed = JSON.parse(data) as { delta?: string; error?: string }
      if (parsed.error) throw new ApiError(502, parsed.error)
      if (parsed.delta) onDelta(parsed.delta)
    }
  }
}
