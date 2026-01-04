import { NextRequest, NextResponse } from 'next/server'

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  return NextResponse.json({
    words: [
      { text: 'Hello', start: 0.0, end: 0.4 },
      { text: 'and', start: 0.4, end: 0.6 },
      { text: 'welcome', start: 0.6, end: 1.0 },
      { text: 'to', start: 1.0, end: 1.2 },
      { text: 'a', start: 1.2, end: 1.3 },
      { text: 'new', start: 1.3, end: 1.5 },
      { text: 'day', start: 1.5, end: 2.0 },
      { text: 'this', start: 2.2, end: 2.5 },
      { text: 'is', start: 2.5, end: 2.7 },
      { text: 'your', start: 2.7, end: 3.0 },
      { text: 'caption', start: 3.0, end: 3.5 },
      { text: 'test', start: 3.5, end: 4.0 },
    ],
    full_text: 'Hello and welcome to a new day this is your caption test',
    language: 'en'
  })
}
