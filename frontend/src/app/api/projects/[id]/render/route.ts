import { NextRequest, NextResponse } from 'next/server'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function POST(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const body = await request.json().catch(() => ({}))
    const themeId = body.theme_id || 'hormozi'
    
    const response = await fetch(
      `${API_URL}/api/v1/projects/${params.id}/render?theme_id=${themeId}`,
      { method: 'POST' }
    )
    
    if (!response.ok) {
      const error = await response.text()
      console.error('Render error:', error)
      return NextResponse.json({ error: 'Render failed' }, { status: response.status })
    }
    
    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Render failed:', error)
    return NextResponse.json({ error: 'Render failed' }, { status: 500 })
  }
}
