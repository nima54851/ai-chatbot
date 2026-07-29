import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'AI 客服机器人 - 万能AI超市',
  description: '由 Groq 驱动的智能 AI 客服助手',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh">
      <body>{children}</body>
    </html>
  )
}
