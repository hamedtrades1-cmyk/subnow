import { NextRequest, NextResponse } from 'next/server'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const response = await fetch(
      `${API_URL}/api/v1/projects/${params.id}/download`
    )
    
    if (!response.ok) {
      return NextResponse.json({ error: 'Download failed' }, { status: response.status })
    }
    
    const blob = await response.blob()
    return new NextResponse(blob, {
      headers: {
        'Content-Type': 'video/mp4',
        'Content-Disposition': `attachment; filename="captioned_video.mp4"`,
      },
    })
  } catch (error) {
    console.error('Download failed:', error)
    return NextResponse.json({ error: 'Download failed' }, { status: 500 })
  }
}
