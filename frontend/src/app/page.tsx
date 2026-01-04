'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { 
  Sparkles, 
  Upload, 
  Wand2, 
  Palette, 
  Download,
  Play,
  ChevronRight
} from 'lucide-react'
import { DropZone } from '@/components/upload/DropZone'
import { UploadProgress } from '@/components/upload/UploadProgress'
import { api } from '@/lib/api'
import { UploadProgress as UploadProgressType } from '@/types'

export default function HomePage() {
  const router = useRouter()
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState<UploadProgressType | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleFileSelect = async (file: File) => {
    setIsUploading(true)
    setError(null)
    setUploadProgress({ loaded: 0, total: file.size, percentage: 0 })

    try {
      const project = await api.createProject(
        file,
        { title: file.name.replace(/\.[^/.]+$/, '') },
        (progress) => setUploadProgress(progress)
      )
      
      // Navigate to editor
      router.push(`/editor/${project.id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed')
      setIsUploading(false)
      setUploadProgress(null)
    }
  }

  const features = [
    {
      icon: Wand2,
      title: 'AI Transcription',
      description: 'Powered by Whisper for accurate word-level timestamps',
    },
    {
      icon: Palette,
      title: 'Stunning Themes',
      description: 'Hormozi, Beast, Neon styles with karaoke animations',
    },
    {
      icon: Download,
      title: 'Export Ready',
      description: 'Burn captions directly into your video in seconds',
    },
  ]

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-50 glass-panel border-t-0 border-x-0 rounded-none">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-cyan to-accent-purple flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold">CaptionMagic</span>
          </div>
          
          <nav className="flex items-center gap-6">
            <a href="#features" className="text-surface-400 hover:text-white transition-colors">
              Features
            </a>
            <a href="#themes" className="text-surface-400 hover:text-white transition-colors">
              Themes
            </a>
            <button className="btn-primary flex items-center gap-2">
              <Upload className="w-4 h-4" />
              Get Started
            </button>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <main className="flex-1 pt-24">
        <section className="max-w-7xl mx-auto px-6 py-20">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-surface-800 border border-surface-700 text-sm text-surface-300 mb-6">
                <Sparkles className="w-4 h-4 text-accent-cyan" />
                Open-source Submagic alternative
              </span>
              
              <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
                Create{' '}
                <span className="text-gradient">stunning captions</span>
                {' '}in seconds
              </h1>
              
              <p className="text-xl text-surface-400 mb-10 leading-relaxed">
                AI-powered transcription meets beautiful animated captions.
                Upload your video, pick a theme, and export with burned-in subtitles.
              </p>
            </motion.div>

            {/* Upload Area */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="max-w-2xl mx-auto"
            >
              {isUploading && uploadProgress ? (
                <UploadProgress progress={uploadProgress} />
              ) : (
                <DropZone onFileSelect={handleFileSelect} />
              )}
              
              {error && (
                <div className="mt-4 p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400">
                  {error}
                </div>
              )}
            </motion.div>
          </div>

          {/* Features */}
          <motion.div
            id="features"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            className="grid md:grid-cols-3 gap-6 mt-20"
          >
            {features.map((feature, index) => (
              <div
                key={feature.title}
                className="group panel p-6 hover:border-accent-cyan/50 transition-all duration-300"
              >
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-accent-cyan/20 to-accent-purple/20 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                  <feature.icon className="w-6 h-6 text-accent-cyan" />
                </div>
                <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                <p className="text-surface-400">{feature.description}</p>
              </div>
            ))}
          </motion.div>

          {/* Theme Preview */}
          <motion.div
            id="themes"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.6 }}
            className="mt-32"
          >
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold mb-4">Beautiful Caption Themes</h2>
              <p className="text-surface-400 max-w-xl mx-auto">
                Choose from professionally designed themes or create your own.
                Each theme supports karaoke-style word highlighting.
              </p>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { name: 'Hormozi', highlight: '#FFFF00', text: '#FFFFFF', bg: 'bg-gradient-to-br from-yellow-500/20 to-orange-500/20' },
                { name: 'Beast', highlight: '#FF0000', text: '#FFFFFF', bg: 'bg-gradient-to-br from-red-500/20 to-pink-500/20' },
                { name: 'Clean', highlight: '#00BFFF', text: '#FFFFFF', bg: 'bg-gradient-to-br from-cyan-500/20 to-blue-500/20' },
                { name: 'Neon', highlight: '#FF00FF', text: '#00FF00', bg: 'bg-gradient-to-br from-purple-500/20 to-pink-500/20' },
              ].map((theme) => (
                <div
                  key={theme.name}
                  className={`panel p-6 ${theme.bg} border-surface-700 hover:border-accent-cyan/50 transition-all cursor-pointer`}
                >
                  <div className="aspect-video bg-surface-900/50 rounded-lg flex items-center justify-center mb-4">
                    <div className="text-center">
                      <span style={{ color: theme.text }} className="font-bold text-lg">
                        This is{' '}
                        <span style={{ color: theme.highlight }} className="animate-karaoke inline-block">
                          {theme.name}
                        </span>
                      </span>
                    </div>
                  </div>
                  <h3 className="font-semibold text-center">{theme.name}</h3>
                </div>
              ))}
            </div>
          </motion.div>

          {/* CTA */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.8 }}
            className="text-center mt-32"
          >
            <div className="inline-flex flex-col items-center gap-6 p-8 rounded-2xl glass-panel">
              <h2 className="text-2xl font-bold">Ready to create magic?</h2>
              <p className="text-surface-400">Upload your first video and see the difference.</p>
              <button 
                onClick={() => document.querySelector('input[type="file"]')?.click()}
                className="btn-primary text-lg px-8 py-3 flex items-center gap-2"
              >
                <Play className="w-5 h-5" />
                Start Creating
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>
          </motion.div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-surface-800 py-8">
        <div className="max-w-7xl mx-auto px-6 text-center text-surface-500">
          <p>CaptionMagic — Open-source video captioning</p>
        </div>
      </footer>
    </div>
  )
}
