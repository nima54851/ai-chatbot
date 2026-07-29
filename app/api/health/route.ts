import { NextResponse } from 'next/server'

export const runtime = 'edge'

export async function GET() {
  return NextResponse.json({
    status: 'ok',
    groq_key_configured: !!process.env.GROQ_API_KEY && process.env.GROQ_API_KEY !== 'gsk_your_key_here',
    model: process.env.GROQ_MODEL || 'llama-3.3-70b-versatile',
  })
}
