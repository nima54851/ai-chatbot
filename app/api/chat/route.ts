import { NextRequest, NextResponse } from 'next/server'

export const runtime = 'edge'

export async function POST(req: NextRequest) {
  try {
    const { messages } = await req.json()

    const apiKey = process.env.GROQ_API_KEY
    if (!apiKey || apiKey === 'gsk_your_key_here') {
      return NextResponse.json(
        { error: '请先在 .env.local 中配置 GROQ_API_KEY' },
        { status: 401 }
      )
    }

    const modelId = process.env.GROQ_MODEL || 'llama-3.3-70b-versatile'

    const groqRes = await fetch('https://api.groq.com/openai/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: modelId,
        messages: [
          {
            role: 'system',
            content: `你是「万能AI超市」的智能客服助手。产品列表：
1. Telegram号码查询机器人 ¥29/月 - 查询 Telegram 用户信息/号码的机器人
2. GitHub Agent自动化系统 ¥99/月 - GitHub自动化运营工具
3. AI内容推流系统 ¥199/月 - 自动发布内容到多平台
4. n8n工作流自动化系统 ¥149/月 - 无代码自动化工作流

收款：PayPal paypalyinanzo@hotmail.com，USDT TRC20 TFfwcPBSF2t5t5pruoRfN1McxnuStFNkX3Cy
客服：@diquchaxun78_bot（付款后联系获取下载链接）
请用友好专业语气回答。如果用户想购买，引导联系客服。`
          },
          ...messages
        ],
        stream: true,
        max_tokens: 1024,
        temperature: 0.7
      })
    })

    if (!groqRes.ok) {
      const errText = await groqRes.text()
      console.error('Groq API error:', errText)
      return NextResponse.json(
        { error: `Groq API 错误 (${groqRes.status})` },
        { status: 502 }
      )
    }

    // Stream Groq's SSE response directly to the client
    return new Response(groqRes.body, {
      headers: {
        'Content-Type': 'text/plain; charset=utf-8',
        'Transfer-Encoding': 'chunked',
        'Cache-Control': 'no-cache'
      }
    })
  } catch (err: any) {
    console.error('Chat API error:', err)
    return NextResponse.json({ error: err.message || '服务器错误' }, { status: 500 })
  }
}
