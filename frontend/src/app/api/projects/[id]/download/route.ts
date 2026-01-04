import { NextRequest, NextResponse } from 'next/server'

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const response = await fetch(
    `http://localhost:8000/api/v1/projects/${params.id}/download`
  )
  
  const blob = await response.blob()
  return new NextResponse(blob, {
    headers: {
      'Content-Type': 'video/mp4',
      'Content-Disposition': `attachment; filename="captioned_video.mp4"`,
    },
  })
}
