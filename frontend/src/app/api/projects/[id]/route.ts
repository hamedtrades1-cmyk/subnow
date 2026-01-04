import { NextRequest, NextResponse } from 'next/server'

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const response = await fetch(`http://localhost:8000/api/v1/projects/${params.id}`)
  const data = await response.json()
  
  // Fix video URL to use our proxy
  if (data.original_video_url) {
    data.original_video_url = `/api${data.original_video_url}`
  }
  
  return NextResponse.json(data)
}
