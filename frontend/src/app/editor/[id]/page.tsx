'use client'

import { useEffect, useState, useCallback } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { 
  ArrowLeft, 
  Download, 
  Loader2,
  AlertCircle,
  Sparkles
} from 'lucide-react'
import { useProject, useWebSocket, useVideoPlayer } from '@/hooks'
import { VideoPreview } from '@/components/editor/VideoPreview'
import { Timeline } from '@/components/editor/Timeline'
import { CaptionEditor } from '@/components/editor/CaptionEditor'
import { ThemeSelector } from '@/components/editor/ThemeSelector'
import { ExportModal } from '@/components/export/ExportModal'
import { cn } from '@/lib/utils'

export default function EditorPage() {
  const params = useParams()
  const router = useRouter()
  const projectId = params.id as string
  
  const [showExportModal, setShowExportModal] = useState(false)
  const [renderProgress, setRenderProgress] = useState(0)
  
  const { 
    project, 
    isLoading, 
    error,
    themes,
    selectedTheme,
    editedWords,
    loadProject,
    loadThemes,
    selectTheme,
    applyTheme,
    updateProjectStatus,
    setEditedWords,
    startTranscription,
    startRender,
  } = useProject()

  const videoPlayer = useVideoPlayer({
    onTimeUpdate: (time) => {
      // Could be used for syncing captions
    },
  })

  // WebSocket for real-time updates
  const { isConnected, lastMessage } = useWebSocket(projectId, {
    onMessage: (message) => {
      switch (message.type) {
        case 'transcription_progress':
          // Handle transcription progress
          break
        case 'render_progress':
          setRenderProgress(message.data.progress || 0)
          break
        case 'status_change':
          if (message.data.status) {
            updateProjectStatus(message.data.status as 'completed' | 'error' | 'ready')
            if (message.data.status === 'completed') {
              loadProject(projectId) // Reload to get rendered video URL
            }
          }
          break
      }
    },
  })

  // Load project and themes on mount
  useEffect(() => {
    loadProject(projectId)
    loadThemes()
  }, [projectId, loadProject, loadThemes])

  // Handle theme apply
  const handleThemeSelect = useCallback(async (themeId: string) => {
    const theme = themes.find(t => t.id === themeId)
    if (theme) {
      selectTheme(theme)
      await applyTheme(themeId)
    }
  }, [themes, selectTheme, applyTheme])

  // Handle export
  const handleExport = useCallback(async () => {
    setShowExportModal(true)
    setRenderProgress(0)
    await startRender()
  }, [startRender])

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-8 h-8 text-accent-cyan animate-spin" />
          <p className="text-surface-400">Loading project...</p>
        </div>
      </div>
    )
  }

  // Error state
  if (error || !project) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center gap-4 text-center">
          <div className="w-16 h-16 rounded-full bg-red-500/10 flex items-center justify-center">
            <AlertCircle className="w-8 h-8 text-red-500" />
          </div>
          <h2 className="text-xl font-semibold">Failed to load project</h2>
          <p className="text-surface-400">{error || 'Project not found'}</p>
          <button onClick={() => router.push('/')} className="btn-secondary">
            Go Home
          </button>
        </div>
      </div>
    )
  }

  const isTranscribing = project.status === 'transcribing'
  const isRendering = project.status === 'rendering'
  const isReady = project.status === 'ready' || project.status === 'completed'
  const needsTranscription = project.status === 'uploading' && !project.transcript

  return (
    <div className="min-h-screen flex flex-col bg-surface-900">
      {/* Header */}
      <header className="flex-none h-16 border-b border-surface-800 px-4 flex items-center justify-between glass-panel">
        <div className="flex items-center gap-4">
          <button 
            onClick={() => router.push('/')} 
            className="btn-ghost p-2"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-cyan to-accent-purple flex items-center justify-center">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
            <div>
              <h1 className="font-semibold truncate max-w-xs">{project.title}</h1>
              <div className="flex items-center gap-2 text-xs text-surface-400">
                <span className={cn(
                  'w-2 h-2 rounded-full',
                  isConnected ? 'bg-green-500' : 'bg-red-500'
                )} />
                {isConnected ? 'Connected' : 'Disconnected'}
              </div>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Status badge */}
          <div className={cn(
            'px-3 py-1 rounded-full text-xs font-medium',
            project.status === 'transcribing' && 'bg-yellow-500/10 text-yellow-500',
            project.status === 'rendering' && 'bg-purple-500/10 text-purple-500',
            project.status === 'completed' && 'bg-green-500/10 text-green-500',
            project.status === 'error' && 'bg-red-500/10 text-red-500',
            (project.status === 'ready' || project.status === 'uploading') && 'bg-surface-700 text-surface-300',
          )}>
            {project.status === 'transcribing' && 'Transcribing...'}
            {project.status === 'rendering' && 'Rendering...'}
            {project.status === 'completed' && 'Completed'}
            {project.status === 'error' && 'Error'}
            {project.status === 'ready' && 'Ready'}
            {project.status === 'uploading' && 'Processing'}
          </div>

          {/* Export button */}
          <button 
            onClick={handleExport}
            disabled={!isReady || isRendering}
            className="btn-primary flex items-center gap-2"
          >
            {isRendering ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Download className="w-4 h-4" />
            )}
            Export
          </button>
        </div>
      </header>

      {/* Main content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left panel - Video Preview */}
        <div className="flex-1 flex flex-col min-w-0 p-4">
          <VideoPreview 
            videoUrl={project.original_video_url}
            videoPlayer={videoPlayer}
            words={editedWords}
            theme={selectedTheme}
            isTranscribing={isTranscribing}
          />
          
          {/* Timeline */}
          <div className="mt-4">
            <Timeline
              duration={project.duration}
              currentTime={videoPlayer.currentTime}
              words={editedWords}
              onSeek={videoPlayer.seek}
              isPlaying={videoPlayer.isPlaying}
              onTogglePlay={videoPlayer.toggle}
            />
          </div>
        </div>

        {/* Right panel - Controls */}
        <div className="w-96 flex-none border-l border-surface-800 flex flex-col overflow-hidden">
          {/* Theme selector */}
          <div className="flex-none border-b border-surface-800">
            <ThemeSelector
              themes={themes}
              selectedTheme={selectedTheme}
              onSelectTheme={handleThemeSelect}
            />
          </div>

          {/* Caption editor */}
          <div className="flex-1 overflow-hidden">
            <CaptionEditor
              words={editedWords}
              currentTime={videoPlayer.currentTime}
              onWordsChange={setEditedWords}
              isTranscribing={isTranscribing}
              needsTranscription={needsTranscription}
              onStartTranscription={startTranscription}
            />
          </div>
        </div>
      </div>

      {/* Export modal */}
      <ExportModal
        isOpen={showExportModal}
        onClose={() => setShowExportModal(false)}
        project={project}
        progress={renderProgress}
        isRendering={isRendering}
      />
    </div>
  )
}
