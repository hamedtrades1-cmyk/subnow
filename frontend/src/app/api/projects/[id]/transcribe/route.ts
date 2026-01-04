import { NextRequest, NextResponse } from 'next/server'

export async function POST(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  console.log('Calling real transcription for project:', params.id)
  
  try {
    const response = await fetch(
      `http://localhost:8000/api/v1/projects/${params.id}/transcribe`,
      { 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      }
    )
    
    if (!response.ok) {
      const error = await response.text()
      console.error('Transcription error:', error)
      return NextResponse.json({ error }, { status: response.status })
    }
    
    const data = await response.json()
    console.log('Transcription result:', data)
    return NextResponse.json(data)
  } catch (error) {
    console.error('Transcription failed:', error)
    return NextResponse.json({ error: 'Transcription failed' }, { status: 500 })
  }
}
