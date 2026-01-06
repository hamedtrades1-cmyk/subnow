import { NextResponse } from 'next/server'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Fallback themes in case backend is not available
const DEFAULT_THEMES = [
  {
    id: 'hormozi',
    name: 'Hormozi',
    font_family: 'Montserrat',
    font_size: 80,
    text_color: '#FFFFFF',
    highlight_color: '#FFFF00',
    animation_style: 'karaoke',
    is_default: true,
  },
  {
    id: 'beast',
    name: 'Beast',
    font_family: 'Impact',
    font_size: 90,
    text_color: '#FFFFFF',
    highlight_color: '#FF0000',
    animation_style: 'pop',
    is_default: true,
  },
  {
    id: 'clean',
    name: 'Clean',
    font_family: 'Inter',
    font_size: 60,
    text_color: '#FFFFFF',
    highlight_color: '#00BFFF',
    animation_style: 'none',
    is_default: true,
  },
  {
    id: 'neon',
    name: 'Neon',
    font_family: 'Poppins',
    font_size: 70,
    text_color: '#00FF00',
    highlight_color: '#FF00FF',
    animation_style: 'glow',
    is_default: true,
  },
]

export async function GET() {
  try {
    const response = await fetch(`${API_URL}/api/v1/themes/`)
    if (response.ok) {
      const data = await response.json()
      return NextResponse.json(data)
    }
  } catch (error) {
    console.error('Failed to fetch themes from backend:', error)
  }
  // Return fallback themes if backend is not available
  return NextResponse.json(DEFAULT_THEMES)
}
