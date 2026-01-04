'use client'

import { motion, AnimatePresence } from 'framer-motion'
import { X, Download, Loader2, Check, ExternalLink, Copy } from 'lucide-react'
import { Project } from '@/types'
import { cn } from '@/lib/utils'
import { ProgressBar } from './ProgressBar'

interface ExportModalProps {
  isOpen: boolean
  onClose: () => void
  project: Project
  progress: number
  isRendering: boolean
}

export function ExportModal({
  isOpen,
  onClose,
  project,
  progress,
  isRendering,
}: ExportModalProps) {
  const isComplete = project.status === 'completed' && project.rendered_video_url

  const handleDownload = () => {
    if (project.rendered_video_url) {
      const link = document.createElement('a')
      link.href = project.rendered_video_url
      link.download = `${project.title}-captioned.mp4`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }
  }

  const handleCopyLink = async () => {
    if (project.rendered_video_url) {
      await navigator.clipboard.writeText(project.rendered_video_url)
    }
  }

  if (!isOpen) return null

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          onClick={(e) => e.stopPropagation()}
          className="w-full max-w-md bg-surface-800 rounded-2xl border border-surface-700 overflow-hidden"
        >
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-surface-700">
            <h2 className="text-lg font-semibold">Export Video</h2>
            <button onClick={onClose} className="btn-icon">
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Content */}
          <div className="p-6">
            {isRendering ? (
              // Rendering state
              <div className="text-center">
                <div className="w-16 h-16 rounded-2xl bg-accent-purple/10 flex items-center justify-center mx-auto mb-4">
                  <Loader2 className="w-8 h-8 text-accent-purple animate-spin" />
                </div>
                <h3 className="text-lg font-semibold mb-2">Rendering Video</h3>
                <p className="text-surface-400 text-sm mb-6">
                  Burning captions into your video. This may take a few minutes.
                </p>
                <ProgressBar progress={progress} />
                <p className="text-sm text-surface-500 mt-2">{progress}% complete</p>
              </div>
            ) : isComplete ? (
              // Complete state
              <div className="text-center">
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: 'spring', stiffness: 200 }}
                  className="w-16 h-16 rounded-2xl bg-green-500/10 flex items-center justify-center mx-auto mb-4"
                >
                  <Check className="w-8 h-8 text-green-500" />
                </motion.div>
                <h3 className="text-lg font-semibold mb-2">Export Complete!</h3>
                <p className="text-surface-400 text-sm mb-6">
                  Your video with captions is ready to download.
                </p>

                {/* Preview */}
                <div className="bg-surface-900 rounded-lg overflow-hidden mb-6">
                  <video
                    src={project.rendered_video_url}
                    className="w-full aspect-video object-contain"
                    controls
                  />
                </div>

                {/* Actions */}
                <div className="flex flex-col gap-3">
                  <button
                    onClick={handleDownload}
                    className="btn-primary w-full flex items-center justify-center gap-2"
                  >
                    <Download className="w-5 h-5" />
                    Download Video
                  </button>

                  <div className="flex gap-2">
                    <button
                      onClick={handleCopyLink}
                      className="btn-secondary flex-1 flex items-center justify-center gap-2"
                    >
                      <Copy className="w-4 h-4" />
                      Copy Link
                    </button>
                    <a
                      href={project.rendered_video_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn-secondary flex-1 flex items-center justify-center gap-2"
                    >
                      <ExternalLink className="w-4 h-4" />
                      Open
                    </a>
                  </div>
                </div>
              </div>
            ) : (
              // Ready to export state
              <div className="text-center">
                <div className="w-16 h-16 rounded-2xl bg-accent-cyan/10 flex items-center justify-center mx-auto mb-4">
                  <Download className="w-8 h-8 text-accent-cyan" />
                </div>
                <h3 className="text-lg font-semibold mb-2">Ready to Export</h3>
                <p className="text-surface-400 text-sm mb-6">
                  Your captions will be permanently burned into the video.
                </p>

                {/* Export settings summary */}
                <div className="bg-surface-900 rounded-lg p-4 mb-6 text-left">
                  <h4 className="text-sm font-medium mb-3">Export Settings</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-surface-400">Resolution</span>
                      <span>{project.width}x{project.height}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-surface-400">Duration</span>
                      <span>{Math.round(project.duration)}s</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-surface-400">Theme</span>
                      <span>{project.theme?.name || 'Default'}</span>
                    </div>
                  </div>
                </div>

                <button className="btn-primary w-full flex items-center justify-center gap-2">
                  <Download className="w-5 h-5" />
                  Start Export
                </button>
              </div>
            )}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}
