'use client'

import { useRef, useCallback, useMemo, useState } from 'react'
import { motion } from 'framer-motion'
import {
  Play,
  Pause,
  SkipBack,
  SkipForward,
  Volume2,
  VolumeX,
} from 'lucide-react'
import { Word } from '@/types'
import { cn, formatTime, timeToPercent } from '@/lib/utils'

interface TimelineProps {
  duration: number
  currentTime: number
  words: Word[]
  onSeek: (time: number) => void
  isPlaying: boolean
  onTogglePlay: () => void
}

export function Timeline({
  duration,
  currentTime,
  words,
  onSeek,
  isPlaying,
  onTogglePlay,
}: TimelineProps) {
  const trackRef = useRef<HTMLDivElement>(null)
  const [isDragging, setIsDragging] = useState(false)

  // Calculate progress percentage
  const progressPercent = timeToPercent(currentTime, duration)

  // Handle seeking
  const handleSeek = useCallback(
    (e: React.MouseEvent | MouseEvent) => {
      if (!trackRef.current || duration === 0) return

      const rect = trackRef.current.getBoundingClientRect()
      const x = Math.max(0, Math.min(e.clientX - rect.left, rect.width))
      const percent = x / rect.width
      const time = percent * duration

      onSeek(time)
    },
    [duration, onSeek]
  )

  // Drag handlers
  const handleMouseDown = useCallback(
    (e: React.MouseEvent) => {
      setIsDragging(true)
      handleSeek(e)

      const handleMouseMove = (e: MouseEvent) => handleSeek(e)
      const handleMouseUp = () => {
        setIsDragging(false)
        document.removeEventListener('mousemove', handleMouseMove)
        document.removeEventListener('mouseup', handleMouseUp)
      }

      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
    },
    [handleSeek]
  )

  // Generate word segments for visualization
  const wordSegments = useMemo(() => {
    return words.map((word) => ({
      left: timeToPercent(word.start, duration),
      width: timeToPercent(word.end - word.start, duration),
      text: word.text,
    }))
  }, [words, duration])

  return (
    <div className="panel p-4">
      {/* Controls */}
      <div className="flex items-center gap-4 mb-4">
        {/* Playback controls */}
        <div className="flex items-center gap-1">
          <button
            onClick={() => onSeek(Math.max(0, currentTime - 5))}
            className="btn-icon"
            title="Back 5s"
          >
            <SkipBack className="w-4 h-4" />
          </button>

          <button
            onClick={onTogglePlay}
            className={cn(
              'w-10 h-10 rounded-full flex items-center justify-center transition-all',
              isPlaying
                ? 'bg-accent-cyan text-surface-900'
                : 'bg-surface-700 text-surface-100 hover:bg-surface-600'
            )}
          >
            {isPlaying ? (
              <Pause className="w-5 h-5" />
            ) : (
              <Play className="w-5 h-5 ml-0.5" />
            )}
          </button>

          <button
            onClick={() => onSeek(Math.min(duration, currentTime + 5))}
            className="btn-icon"
            title="Forward 5s"
          >
            <SkipForward className="w-4 h-4" />
          </button>
        </div>

        {/* Time display */}
        <div className="flex-1 flex justify-center">
          <span className="font-mono text-sm text-surface-300">
            {formatTime(currentTime)} / {formatTime(duration)}
          </span>
        </div>

        {/* Keyboard shortcuts hint */}
        <div className="text-xs text-surface-500">
          Space to play • ← → to seek
        </div>
      </div>

      {/* Timeline track */}
      <div className="relative">
        {/* Word segments visualization */}
        <div className="h-12 bg-surface-700 rounded-lg overflow-hidden relative mb-2">
          {/* Word blocks */}
          {wordSegments.map((segment, i) => (
            <div
              key={i}
              className="absolute top-0 bottom-0 bg-accent-cyan/20 border-l border-r border-accent-cyan/30"
              style={{
                left: `${segment.left}%`,
                width: `${Math.max(0.5, segment.width)}%`,
              }}
              title={segment.text}
            />
          ))}

          {/* Progress overlay */}
          <div
            className="absolute top-0 bottom-0 left-0 bg-accent-cyan/10 pointer-events-none"
            style={{ width: `${progressPercent}%` }}
          />
        </div>

        {/* Scrubber track */}
        <div
          ref={trackRef}
          onMouseDown={handleMouseDown}
          className={cn(
            'h-2 bg-surface-700 rounded-full overflow-hidden cursor-pointer relative',
            isDragging && 'cursor-grabbing'
          )}
        >
          {/* Progress bar */}
          <motion.div
            className="absolute top-0 bottom-0 left-0 bg-gradient-to-r from-accent-cyan to-accent-purple rounded-full"
            style={{ width: `${progressPercent}%` }}
          />

          {/* Handle */}
          <motion.div
            className={cn(
              'absolute top-1/2 -translate-y-1/2 w-4 h-4 bg-white rounded-full shadow-lg border-2 border-accent-cyan',
              isDragging && 'scale-125'
            )}
            style={{ left: `calc(${progressPercent}% - 8px)` }}
            transition={{ duration: 0.1 }}
          />
        </div>

        {/* Time markers */}
        <div className="flex justify-between mt-1 text-xs text-surface-500 font-mono">
          <span>0:00</span>
          <span>{formatTime(duration / 4)}</span>
          <span>{formatTime(duration / 2)}</span>
          <span>{formatTime((duration * 3) / 4)}</span>
          <span>{formatTime(duration)}</span>
        </div>
      </div>
    </div>
  )
}
