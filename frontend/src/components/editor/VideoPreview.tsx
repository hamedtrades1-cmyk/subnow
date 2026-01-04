'use client'

import { useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Loader2 } from 'lucide-react'
import { Theme, Word } from '@/types'
import { cn, formatTime } from '@/lib/utils'

interface VideoPreviewProps {
  videoUrl: string
  videoPlayer: {
    videoRef: React.RefObject<HTMLVideoElement | null>
    isPlaying: boolean
    currentTime: number
    duration: number
    isLoading: boolean
    toggle: () => void
  }
  words: Word[]
  theme: Theme | null
  isTranscribing: boolean
}

export function VideoPreview({
  videoUrl,
  videoPlayer,
  words,
  theme,
  isTranscribing,
}: VideoPreviewProps) {
  const { videoRef, isPlaying, currentTime, duration, isLoading, toggle } = videoPlayer

  // Get current caption based on time
  const currentCaption = useMemo(() => {
    if (!words.length || !theme) return null

    // Find words in current time window
    const wordsPerLine = theme.words_per_line || 3
    const currentIndex = words.findIndex(
      (w) => currentTime >= w.start && currentTime < w.end
    )
    
    if (currentIndex === -1) return null

    // Get group of words
    const groupStart = Math.floor(currentIndex / wordsPerLine) * wordsPerLine
    const groupEnd = Math.min(groupStart + wordsPerLine, words.length)
    const groupWords = words.slice(groupStart, groupEnd)
    
    // Find active word within group
    const activeIndex = currentIndex - groupStart

    return { words: groupWords, activeIndex }
  }, [words, currentTime, theme])

  // Generate caption style from theme
  const captionStyle = useMemo(() => {
    if (!theme) return {}
    
    return {
      fontFamily: theme.font_family,
      fontSize: `${theme.font_size / 2}px`, // Scale down for preview
      fontWeight: theme.font_weight,
      color: theme.text_color,
      textShadow: `
        ${theme.outline_width}px 0 0 ${theme.outline_color},
        -${theme.outline_width}px 0 0 ${theme.outline_color},
        0 ${theme.outline_width}px 0 ${theme.outline_color},
        0 -${theme.outline_width}px 0 ${theme.outline_color},
        ${theme.shadow_offset}px ${theme.shadow_offset}px ${theme.shadow_blur}px ${theme.shadow_color}
      `,
      textAlign: theme.alignment as 'left' | 'center' | 'right',
    }
  }, [theme])

  return (
    <div className="flex-1 flex flex-col panel overflow-hidden">
      {/* Video container */}
      <div 
        className="relative flex-1 bg-black flex items-center justify-center video-container cursor-pointer"
        onClick={toggle}
      >
        <video
          ref={videoRef}
          src={videoUrl}
          className="max-w-full max-h-full object-contain"
          playsInline
        />

        {/* Loading overlay */}
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/50">
            <Loader2 className="w-8 h-8 text-accent-cyan animate-spin" />
          </div>
        )}

        {/* Transcribing overlay */}
        {isTranscribing && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/70">
            <div className="flex flex-col items-center gap-3">
              <Loader2 className="w-8 h-8 text-accent-cyan animate-spin" />
              <p className="text-sm text-surface-300">Transcribing audio...</p>
            </div>
          </div>
        )}

        {/* Caption overlay */}
        <AnimatePresence mode="wait">
          {currentCaption && theme && (
            <motion.div
              key={currentCaption.words.map(w => w.text).join('-')}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.15 }}
              className="absolute left-4 right-4 pointer-events-none"
              style={{
                bottom: `${100 - (theme.position_y || 70)}%`,
              }}
            >
              <div 
                className="flex flex-wrap justify-center gap-x-3"
                style={captionStyle}
              >
                {currentCaption.words.map((word, i) => (
                  <CaptionWord
                    key={`${word.text}-${word.start}`}
                    word={word}
                    isActive={i === currentCaption.activeIndex}
                    theme={theme}
                  />
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Play/Pause indicator */}
        <AnimatePresence>
          {!isPlaying && !isLoading && !isTranscribing && (
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              className="absolute inset-0 flex items-center justify-center pointer-events-none"
            >
              <div className="w-16 h-16 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center">
                <div className="w-0 h-0 border-t-8 border-b-8 border-l-12 border-transparent border-l-white ml-1" />
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Video controls overlay */}
        <div className="video-controls absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/80 to-transparent">
          <div className="flex items-center justify-between text-sm">
            <span className="font-mono text-surface-300">
              {formatTime(currentTime)} / {formatTime(duration)}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

// Caption word component with animation
function CaptionWord({ 
  word, 
  isActive, 
  theme 
}: { 
  word: Word
  isActive: boolean
  theme: Theme 
}) {
  const animationStyle = theme.animation_style

  return (
    <motion.span
      className={cn('inline-block', isActive && 'relative')}
      style={{
        color: isActive ? theme.highlight_color : theme.text_color,
      }}
      animate={
        isActive && animationStyle === 'bounce'
          ? { y: [0, -4, 0] }
          : isActive && animationStyle === 'pop'
          ? { scale: [1, 1.1, 1] }
          : undefined
      }
      transition={{ duration: 0.2 }}
    >
      {word.text}
      
      {/* Glow effect for neon theme */}
      {isActive && animationStyle === 'glow' && (
        <motion.span
          className="absolute inset-0 blur-sm"
          style={{ color: theme.highlight_color }}
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 0.5, repeat: Infinity }}
        >
          {word.text}
        </motion.span>
      )}
    </motion.span>
  )
}
