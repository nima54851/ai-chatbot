'use client'

import { useState, useRef, useEffect } from 'react'
import type { Message } from '@/lib/types'

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const abortRef = useRef<AbortController | null>(null)
  const [apiReady, setApiReady] = useState<boolean | null>(null)

  // 健康检查
  useEffect(() => {
    fetch('/api/health')
      .then(r => r.json())
      .then(d => setApiReady(d.groq_key_configured ?? false))
      .catch(() => setApiReady(false))
  }, [])

  // 滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // 自动聚焦
  useEffect(() => {
    if (!isLoading) textareaRef.current?.focus()
  }, [isLoading])

  const sendMessage = async (content: string) => {
    if (isLoading || !content.trim()) return
    setError('')

    const userMsg: Message = { id: Date.now().toString(), role: 'user', content: content.trim() }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setIsLoading(true)

    const assistantId = (Date.now() + 1).toString()
    setMessages(prev => [...prev, { id: assistantId, role: 'assistant', content: '' }])

    abortRef.current = new AbortController()
    const signal = abortRef.current.signal

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: [...messages, userMsg].map(m => ({ role: m.role, content: m.content })) }),
        signal
      })

      if (!res.ok || !res.body) {
        const err = await res.json().catch(() => ({ error: '请求失败' }))
        throw new Error(err.error || `HTTP ${res.status}`)
      }

      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let done = false
      let fullText = ''

      while (!done) {
        const { value, done: d } = await reader.read()
        done = d
        if (value) {
          fullText += decoder.decode(value, { stream: !done })
          // 解析 SSE chunk
          const lines = fullText.split('\n')
          let delta = ''
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6)
              if (data === '[DONE]') { done = true; break }
              try {
                const json = JSON.parse(data)
                if (json.choices?.[0]?.delta?.content) {
                  delta += json.choices[0].delta.content
                  setMessages(prev =>
                    prev.map(m => m.id === assistantId ? { ...m, content: delta } : m)
                  )
                }
                if (json.error) throw new Error(json.error)
              } catch {/* parse incomplete JSON — skip */}
            }
          }
        }
      }
    } catch (err: any) {
      if (err.name === 'AbortError') {
        setMessages(prev => prev.filter(m => m.id !== assistantId))
      } else {
        setMessages(prev => prev.filter(m => m.id !== assistantId))
        setError(err.message || 'AI 响应失败，请检查网络和 API Key')
      }
    } finally {
      setIsLoading(false)
      textareaRef.current?.focus()
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const text = input.trim()
    if (text) sendMessage(text)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value)
    // auto-resize
    const ta = e.target
    ta.style.height = 'auto'
    ta.style.height = Math.min(ta.scrollHeight, 130) + 'px'
  }

  const hasMessages = messages.length > 0

  return (
    <div className="chat-root">
      {/* Header */}
      <header className="header">
        <div className="header-logo">
          <div className="header-logo-icon">🧭</div>
          <span>灵犀 AI 客服</span>
        </div>
        <div className="header-status">
          <div className="dot" />
          <span>
            {apiReady === null ? '检测中…'
              : apiReady ? 'Groq 在线'
              : '未配置 Key'}
          </span>
        </div>
      </header>

      {/* Chat area */}
      <div className="chat-wrap">
        <div className="chat-container">

          {!hasMessages ? (
            /* Welcome */
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
            /* Messages */
            <div className="messages">
              {messages.map(msg => (
                <div key={msg.id} className={`msg ${msg.role}`}>
                  <div className="msg-avatar">{msg.role === 'assistant' ? '🤖' : '👤'}</div>
                  <div className="msg-bubble">
                    {msg.content
                      ? msg.content
                      : <div className="typing"><span /><span /><span /></div>}
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
          )}

          {error && <div className="error-banner">{error}</div>}

          {/* Input */}
          <div className="input-area">
            <form onSubmit={handleSubmit} className="input-wrap">
              <textarea
                ref={textareaRef}
                className="chat-input"
                placeholder="输入你的问题… (Enter 发送，Shift+Enter 换行)"
                value={input}
                onChange={handleInput}
                onKeyDown={handleKeyDown}
                disabled={isLoading}
                rows={1}
              />
              <button
                type="submit"
                className="send-btn"
                disabled={!input.trim() || isLoading}
              >
                {isLoading ? '⏳' : '↑'}
              </button>
            </form>
            <p className="hint-text">
              {apiReady === false
                ? '⚠️ 请先配置 GROQ_API_KEY 环境变量'
                : '需配置 GROQ_API_KEY — 参考 github.com/nima54851/ai-chatbot'}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
