import { NextRequest, NextResponse } from 'next/server'

export async function POST(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const body = await request.json().catch(() => ({}))
    const themeId = body.theme_id || 'hormozi'
    
    const response = await fetch(
      `http://localhost:8000/api/v1/projects/${params.id}/render?theme_id=${themeId}`,
      { method: 'POST' }
    )
    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    return NextResponse.json({ error: 'Render failed' }, { status: 500 })
  }
}
