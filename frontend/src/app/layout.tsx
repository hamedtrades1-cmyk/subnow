import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'CaptionMagic - AI-Powered Video Captions',
  description: 'Create stunning animated captions for your videos with AI-powered transcription and beautiful themes.',
  keywords: ['video captions', 'subtitles', 'transcription', 'AI', 'video editor'],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-surface-900">
        {/* Background pattern */}
        <div className="fixed inset-0 bg-grid opacity-50 pointer-events-none" />
        
        {/* Ambient glow effects */}
        <div className="fixed top-0 left-1/4 w-96 h-96 bg-accent-cyan/10 rounded-full blur-3xl pointer-events-none" />
        <div className="fixed bottom-0 right-1/4 w-96 h-96 bg-accent-purple/10 rounded-full blur-3xl pointer-events-none" />
        
        {/* Main content */}
        <div className="relative z-10">
          {children}
        </div>
      </body>
    </html>
  )
}
