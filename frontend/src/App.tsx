import { Bot, Loader2, SendHorizontal, Square, User } from 'lucide-react'
import { useEffect, useRef, useState, type FormEvent } from 'react'
import { StatusBadge } from './components/StatusBadge'
import { useHealth } from './hooks/useHealth'
import { streamChat, type ChatMessage } from './lib/api'

export default function App() {
  const health = useHealth()
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [streaming, setStreaming] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const abortRef = useRef<AbortController | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  useEffect(() => () => abortRef.current?.abort(), [])

  async function send(e: FormEvent): Promise<void> {
    e.preventDefault()
    const content = input.trim()
    if (!content || streaming) return

    const history: ChatMessage[] = [...messages, { role: 'user', content }]
    setMessages([...history, { role: 'assistant', content: '' }])
    setInput('')
    setError(null)
    setStreaming(true)

    const controller = new AbortController()
    abortRef.current = controller
    try {
      await streamChat(
        history,
        (delta) =>
          setMessages((prev) => {
            const last = prev.at(-1)
            if (!last) return prev
            return [...prev.slice(0, -1), { ...last, content: last.content + delta }]
          }),
        controller.signal,
      )
    } catch (err: unknown) {
      if (!(err instanceof DOMException && err.name === 'AbortError')) {
        setError(err instanceof Error ? err.message : 'Request failed')
      }
    } finally {
      setStreaming(false)
      abortRef.current = null
    }
  }

  return (
    <div className="mx-auto flex h-full max-w-3xl flex-col px-4">
      <header className="flex items-center justify-between border-b border-zinc-800 py-4">
        <h1 className="text-lg font-semibold tracking-tight">
          H26 <span className="text-violet-400">DDoxers</span>
        </h1>
        <StatusBadge health={health} />
      </header>

      <main className="flex-1 space-y-4 overflow-y-auto py-6">
        {messages.length === 0 && (
          <p className="pt-24 text-center text-sm text-zinc-500">
            Local open-weight model, no cloud APIs. Say something.
          </p>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`flex gap-3 ${m.role === 'user' ? 'flex-row-reverse' : ''}`}>
            <div className="mt-1 grid size-7 shrink-0 place-items-center rounded-full bg-zinc-800">
              {m.role === 'user' ? <User className="size-4" /> : <Bot className="size-4" />}
            </div>
            <div
              className={`max-w-[80%] whitespace-pre-wrap rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
                m.role === 'user' ? 'bg-violet-600 text-white' : 'bg-zinc-900 ring-1 ring-zinc-800'
              }`}
            >
              {m.content || <Loader2 className="size-4 animate-spin text-zinc-500" />}
            </div>
          </div>
        ))}
        {error && <p className="text-center text-sm text-red-400">{error}</p>}
        <div ref={bottomRef} />
      </main>

      <form onSubmit={send} className="flex gap-2 border-t border-zinc-800 py-4">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Message the model…"
          className="flex-1 rounded-xl bg-zinc-900 px-4 py-2.5 text-sm ring-1 ring-zinc-800 outline-none placeholder:text-zinc-600 focus:ring-violet-500"
        />
        {streaming ? (
          <button
            type="button"
            onClick={() => abortRef.current?.abort()}
            className="grid size-10 place-items-center rounded-xl bg-zinc-800 hover:bg-zinc-700"
            aria-label="Stop"
          >
            <Square className="size-4" />
          </button>
        ) : (
          <button
            type="submit"
            disabled={!input.trim()}
            className="grid size-10 place-items-center rounded-xl bg-violet-600 hover:bg-violet-500 disabled:opacity-40"
            aria-label="Send"
          >
            <SendHorizontal className="size-4" />
          </button>
        )}
      </form>
    </div>
  )
}
