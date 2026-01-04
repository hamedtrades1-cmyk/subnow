import { NextResponse } from 'next/server'

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
  return NextResponse.json(DEFAULT_THEMES)
}
