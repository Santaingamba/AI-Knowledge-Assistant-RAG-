import { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'
import { Send, User, Brain, Search, MessageSquarePlus, Loader2 } from 'lucide-react'
import api from '@/lib/api'

type Source = { source: string; chunk: number }

type Message = {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: Source[]
}

export function Chat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [chatId, setChatId] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleNewChat = () => {
    setMessages([])
    setChatId(null)
    setError(null)
  }

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setLoading(true)
    setError(null)

    try {
      const response = await api.post('/chat/', {
        message: userMessage.content,
        chat_id: chatId,
      })

      const data = response.data

      // The backend returns the full chat with messages; use the latest chat id
      if (data.id) {
        setChatId(data.id)
      }

      // Find the latest assistant message from the response
      const backendMessages: Array<{
        id: string
        role: string
        content: string
        sources: string | null
        created_at: string
      }> = data.messages || []

      const lastAssistant = backendMessages
        .filter((m) => m.role === 'assistant')
        .pop()

      if (lastAssistant) {
        let parsedSources: Source[] | undefined
        if (lastAssistant.sources) {
          try {
            parsedSources = JSON.parse(lastAssistant.sources)
          } catch {
            parsedSources = undefined
          }
        }

        const assistantMessage: Message = {
          id: lastAssistant.id,
          role: 'assistant',
          content: lastAssistant.content,
          sources: parsedSources,
        }
        setMessages((prev) => [...prev, assistantMessage])
      }
    } catch (err: any) {
      const detail = err.response?.data?.detail
      setError(typeof detail === 'string' ? detail : 'Failed to get a response. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex h-full flex-col gap-4 max-w-5xl mx-auto w-full">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Chat</h1>
          <p className="text-muted-foreground mt-2">Ask questions based on your uploaded documents.</p>
        </div>
        <Button variant="outline" onClick={handleNewChat}>
          <MessageSquarePlus className="mr-2 h-4 w-4" />
          New Chat
        </Button>
      </div>

      <Card className="flex-1 flex flex-col overflow-hidden bg-background">
        <div className="flex-1 overflow-y-auto p-4 space-y-6">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-muted-foreground">
              <Brain className="h-16 w-16 mb-4 text-muted" />
              <p className="text-lg font-medium">How can I help you today?</p>
              <p className="text-sm">I'll answer your questions using only the documents you've uploaded.</p>
            </div>
          ) : (
            messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {msg.role === 'assistant' && (
                  <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                    <Brain className="h-5 w-5 text-primary" />
                  </div>
                )}
                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                    msg.role === 'user'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted/50 border'
                  }`}
                >
                  <p className="whitespace-pre-wrap text-sm leading-relaxed">{msg.content}</p>
                  
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="mt-4 pt-3 border-t border-border/50">
                      <p className="text-xs font-semibold mb-2 opacity-70">Sources:</p>
                      <div className="flex flex-wrap gap-2">
                        {msg.sources.map((src, idx) => (
                          <span
                            key={idx}
                            className="inline-flex items-center rounded-md bg-background px-2 py-1 text-xs font-medium border shadow-sm"
                          >
                            <Search className="h-3 w-3 mr-1" />
                            {src.source} (Chunk {src.chunk})
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
                {msg.role === 'user' && (
                  <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center shrink-0">
                    <User className="h-5 w-5" />
                  </div>
                )}
              </div>
            ))
          )}
          {loading && (
            <div className="flex gap-4 justify-start">
              <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                <Brain className="h-5 w-5 text-primary animate-pulse" />
              </div>
              <div className="bg-muted/50 border rounded-2xl px-4 py-3 flex items-center">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-primary/40 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                  <div className="w-2 h-2 bg-primary/40 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                  <div className="w-2 h-2 bg-primary/40 rounded-full animate-bounce"></div>
                </div>
              </div>
            </div>
          )}
          {error && (
            <div className="rounded-md bg-destructive/10 border border-destructive/20 px-4 py-3 text-sm text-destructive mx-4">
              {error}
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="p-4 bg-background border-t">
          <form onSubmit={handleSend} className="flex gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question about your documents..."
              className="flex-1"
              disabled={loading}
            />
            <Button type="submit" disabled={!input.trim() || loading}>
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
            </Button>
          </form>
          <div className="text-center mt-2">
            <p className="text-xs text-muted-foreground">
              AI Knowledge Assistant can make mistakes. Always verify with the source documents.
            </p>
          </div>
        </div>
      </Card>
    </div>
  )
}
