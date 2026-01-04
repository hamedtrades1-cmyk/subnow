import { NextRequest, NextResponse } from 'next/server'

export async function POST(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const response = await fetch(
      `http://localhost:8000/api/v1/projects/${params.id}/transcribe`,
      { method: 'POST' }
    )
    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    return NextResponse.json({ error: 'Transcription failed' }, { status: 500 })
  }
}
