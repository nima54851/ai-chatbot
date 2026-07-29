'use client'

import { useState, useRef, useEffect } from 'react'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const abortRef = useRef<AbortController | null>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async (content: string) => {
    if (isLoading) return
    setError('')

    const userMsg: Message = { id: Date.now().toString(), role: 'user', content }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setIsLoading(true)

    // Placeholder while streaming
    const assistantId = (Date.now() + 1).toString()
    setMessages(prev => [...prev, { id: assistantId, role: 'assistant', content: '' }])

    abortRef.current = new AbortController()
    const signal = abortRef.current.signal

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: [...messages, userMsg].map(m => ({ role: m.role, content: m.content }))
        }),
        signal
      })

      if (!res.ok) {
        const err = await res.json().catch(() => ({ error: '请求失败' }))
        throw new Error(err.error || `HTTP ${res.status}`)
      }

      const reader = res.body!.getReader()
      const decoder = new TextDecoder()
      let done = false
      let fullText = ''

      while (!done) {
        const { value, done: d } = await reader.read()
        done = d
        if (value) {
          fullText += decoder.decode(value, { stream: !d })
          setMessages(prev =>
            prev.map(m => m.id === assistantId ? { ...m, content: fullText } : m)
          )
        }
      }
    } catch (err: any) {
      if (err.name === 'AbortError') {
        // user cancelled — clean up the empty placeholder
        setMessages(prev => prev.filter(m => m.id !== assistantId))
      } else {
        setError(err.message || 'AI 响应失败，请检查 API Key 配置')
        setMessages(prev => prev.filter(m => m.id !== assistantId))
      }
    } finally {
      setIsLoading(false)
      textareaRef.current?.focus()
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const text = input.trim()
    if (text && !isLoading) sendMessage(text)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <div className="main-layout">
      {/* Header */}
      <header className="header">
        <div className="header-logo">
          <div className="header-logo-icon">🧭</div>
          <span>AI 客服</span>
        </div>
        <div className="header-status">
          <div className="header-status-dot" />
          <span>Groq 在线</span>
        </div>
      </header>

      {/* Chat Container */}
      <div className="chat-container">
        {!messages.length ? (
          <div className="welcome">
            <div className="welcome-icon">🤖</div>
            <h2>你好，我是灵犀 AI 客服</h2>
            <p>由 Groq Llama 3.3 70B 驱动的大脑，可以回答关于万能AI超市产品的任何问题。</p>
            <div className="welcome-tips">
              <span className="welcome-tip">📱 Telegram机器人</span>
              <span className="welcome-tip">⚡ GitHub自动化</span>
              <span className="welcome-tip">📣 内容推流</span>
              <span className="welcome-tip">🔗 n8n工作流</span>
            </div>
          </div>
        ) : (
          <div className="messages">
            {messages.map(msg => (
              <div key={msg.id} className={`msg ${msg.role}`}>
                <div className="msg-avatar">{msg.role === 'assistant' ? '🤖' : '👤'}</div>
                <div className="msg-bubble">{msg.content || <span className="msg-typing"><span /><span /><span /></span>}</div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}

        {error && <div className="error-banner">⚠️ {error}</div>}

        {/* Input */}
        <div className="input-area">
          <form onSubmit={handleSubmit} className="input-wrap">
            <textarea
              ref={textareaRef}
              className="chat-input"
              placeholder="输入你的问题... (Enter 发送，Shift+Enter 换行)"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isLoading}
              rows={1}
            />
            <button type="submit" className="send-btn" disabled={!input.trim() || isLoading}>
              {isLoading ? '⏳' : '↑'}
            </button>
          </form>
          <p style={{ fontSize: '0.7rem', color: 'var(--muted)', marginTop: '0.4rem', textAlign: 'center' }}>
            需配置 GROQ_API_KEY（参考 .env.local）
          </p>
        </div>
      </div>
    </div>
  )
}
