/* WARNING: VITE_ANTHROPIC_KEY is embedded in the built JS bundle and visible
   in browser DevTools. Acceptable for a private personal repo only.
   Regenerate the key if this repository ever goes public. */

import type { AggregatedData } from './dataAggregator'
import type { BriefingResult } from '../types/dashboard'

const ANTHROPIC_KEY = import.meta.env.VITE_ANTHROPIC_KEY ?? ''
const MODEL = 'claude-sonnet-4-6'
const MAX_TOKENS = 1200

const SYSTEM_PROMPT = `You are a senior gold trading analyst and market intelligence advisor.
Your job is to write a daily intelligence briefing for a beginner day trader who uses ICT / Smart Money Concepts methodology to trade XAUUSD.

The trader only trades WITH the trend (buying into uptrends, selling into downtrends) using the 1H chart to determine trend direction, the 5M chart for signals, and the 1M chart for precise entry. They trade during the London and New York sessions.

You will receive a structured JSON snapshot of all the day's market data.

Write a SINGLE flowing briefing paragraph (200–300 words) using PLAIN, BEGINNER-FRIENDLY language. Avoid jargon wherever possible. When you use a financial term, briefly explain what it means in brackets.

Your briefing MUST follow this structure within the single paragraph:
1. REGIME LINE: Which forces are most relevant today and why.
2. OVERNIGHT CONTEXT: What happened in Asia, where gold opened London, direction of the dollar and yields overnight, any key headlines.
3. DIRECTIONAL BIAS with plain reasoning: Is the day likely to favour gold going UP, DOWN, or being CHOPPY — and in simple terms, WHY.
4. CONFIDENCE SCORE: Express confidence in the bias as X/10. Explain what would change the view.
5. EVENT RISK: Any scheduled news today, when it hits (GMT), what to expect and how to position around it.
6. KEY LEVELS: The most important price levels to watch today. Use the ADR data to comment on how much move is likely remaining.
7. TRADE INTEGRATION: Explicit guidance on whether today is a good day for trend-following trades, what size/conviction is appropriate.

End with one sentence that a beginner can screenshot and remember for the day.

CRITICAL RULES:
- Use plain English. Write as if explaining to a smart person who is new to financial markets.
- Never say "in conclusion" or "to summarise".
- Do NOT make up data. Only use what is in the JSON. If data is null, say so.
- Return your response as JSON:
  { "biasScore": number from -5 to +5 (negative = bearish, positive = bullish), "biasLabel": "BEARISH" | "NEUTRAL" | "BULLISH", "confidence": number 1-10, "briefing": "your paragraph here" }`

export async function generateBriefing(data: AggregatedData): Promise<BriefingResult> {
  if (!ANTHROPIC_KEY) throw new Error('VITE_ANTHROPIC_KEY not set')

  const response = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'x-api-key': ANTHROPIC_KEY,
      'anthropic-version': '2023-06-01',
      'content-type': 'application/json',
      'anthropic-dangerous-direct-browser-access': 'true',
    },
    body: JSON.stringify({
      model: MODEL,
      max_tokens: MAX_TOKENS,
      system: SYSTEM_PROMPT,
      messages: [
        {
          role: 'user',
          content: `Here is today's market data snapshot:\n\n${JSON.stringify(data, null, 2)}`,
        },
      ],
    }),
  })

  if (!response.ok) {
    const err = await response.text()
    throw new Error(`Anthropic API error ${response.status}: ${err}`)
  }

  const body = await response.json() as {
    content: Array<{ type: string; text: string }>
  }
  const text = body.content.find(c => c.type === 'text')?.text ?? ''

  // Strip markdown code fences if Claude wrapped the JSON
  const cleaned = text.replace(/^```json?\s*/i, '').replace(/\s*```$/, '').trim()
  const parsed = JSON.parse(cleaned) as Omit<BriefingResult, 'generatedAt'>

  return { ...parsed, generatedAt: new Date().toISOString() }
}
