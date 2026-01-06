import { NextRequest, NextResponse } from 'next/server'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const response = await fetch(`${API_URL}/api/v1/projects/${params.id}`)
    const data = await response.json()
    
    // Fix video URL to use our proxy
    if (data.original_video_url) {
      data.original_video_url = `/api${data.original_video_url}`
    }
    
    return NextResponse.json(data)
  } catch (error) {
    console.error('Failed to fetch project:', error)
    return NextResponse.json({ error: 'Project not found' }, { status: 404 })
  }
}
