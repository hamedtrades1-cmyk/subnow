'use client'

import { useRef, useEffect, useMemo, useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Loader2, 
  Wand2, 
  Edit3, 
  Check,
  X,
  AlertCircle
} from 'lucide-react'
import { Word } from '@/types'
import { cn, formatTime } from '@/lib/utils'

interface CaptionEditorProps {
  words: Word[]
  currentTime: number
  onWordsChange: (words: Word[]) => void
  isTranscribing: boolean
  needsTranscription: boolean
  onStartTranscription: () => void
}

export function CaptionEditor({
  words,
  currentTime,
  onWordsChange,
  isTranscribing,
  needsTranscription,
  onStartTranscription,
}: CaptionEditorProps) {
  const scrollRef = useRef<HTMLDivElement>(null)

  // Find current word index
  const currentWordIndex = useMemo(() => {
    return words.findIndex((w) => currentTime >= w.start && currentTime < w.end)
  }, [words, currentTime])

  // Auto-scroll to current word
  useEffect(() => {
    if (currentWordIndex >= 0 && scrollRef.current) {
      const wordElement = scrollRef.current.querySelector(
        `[data-word-index="${currentWordIndex}"]`
      )
      if (wordElement) {
        wordElement.scrollIntoView({ behavior: 'smooth', block: 'center' })
      }
    }
  }, [currentWordIndex])

  // Handle word text edit
  const handleWordEdit = (index: number, newText: string) => {
    const newWords = [...words]
    newWords[index] = { ...newWords[index], text: newText }
    onWordsChange(newWords)
  }

  // Handle word delete
  const handleWordDelete = (index: number) => {
    const newWords = words.filter((_, i) => i !== index)
    onWordsChange(newWords)
  }

  // Group words into lines (for display purposes)
  const wordGroups = useMemo(() => {
    const groups: { words: Array<Word & { originalIndex: number }>; startTime: number }[] = []
    let currentGroup: Array<Word & { originalIndex: number }> = []
    let lastEnd = 0
    const pauseThreshold = 0.5 // seconds

    words.forEach((word, index) => {
      // Start new group if there's a pause
      if (word.start - lastEnd > pauseThreshold && currentGroup.length > 0) {
        groups.push({
          words: currentGroup,
          startTime: currentGroup[0].start,
        })
        currentGroup = []
      }

      currentGroup.push({ ...word, originalIndex: index })
      lastEnd = word.end

      // Also split by word count
      if (currentGroup.length >= 6) {
        groups.push({
          words: currentGroup,
          startTime: currentGroup[0].start,
        })
        currentGroup = []
      }
    })

    // Don't forget the last group
    if (currentGroup.length > 0) {
      groups.push({
        words: currentGroup,
        startTime: currentGroup[0].start,
      })
    }

    return groups
  }, [words])

  // Need transcription state
  if (needsTranscription) {
    return (
      <div className="h-full flex flex-col items-center justify-center p-8 text-center">
        <div className="w-16 h-16 rounded-2xl bg-accent-cyan/10 flex items-center justify-center mb-4">
          <Wand2 className="w-8 h-8 text-accent-cyan" />
        </div>
        <h3 className="text-lg font-semibold mb-2">Ready to transcribe</h3>
        <p className="text-surface-400 mb-6 max-w-xs">
          Generate captions automatically using AI-powered speech recognition.
        </p>
        <button onClick={onStartTranscription} className="btn-primary">
          Start Transcription
        </button>
      </div>
    )
  }

  // Transcribing state
  if (isTranscribing) {
    return (
      <div className="h-full flex flex-col items-center justify-center p-8 text-center">
        <Loader2 className="w-8 h-8 text-accent-cyan animate-spin mb-4" />
        <h3 className="text-lg font-semibold mb-2">Transcribing...</h3>
        <p className="text-surface-400">
          AI is processing your audio. This may take a moment.
        </p>
      </div>
    )
  }

  // No words state
  if (words.length === 0) {
    return (
      <div className="h-full flex flex-col items-center justify-center p-8 text-center">
        <div className="w-16 h-16 rounded-2xl bg-surface-700 flex items-center justify-center mb-4">
          <AlertCircle className="w-8 h-8 text-surface-500" />
        </div>
        <h3 className="text-lg font-semibold mb-2">No captions</h3>
        <p className="text-surface-400 mb-6">
          Transcription produced no results. Try uploading a video with clearer audio.
        </p>
        <button onClick={onStartTranscription} className="btn-secondary">
          Retry Transcription
        </button>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="panel-header flex-none">
        <span className="panel-title">Captions</span>
        <span className="text-xs text-surface-500">{words.length} words</span>
      </div>

      {/* Word list */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4">
        {wordGroups.map((group, groupIndex) => (
          <motion.div
            key={groupIndex}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: groupIndex * 0.02 }}
            className="group"
          >
            {/* Timestamp */}
            <div className="text-xs text-surface-500 font-mono mb-1">
              {formatTime(group.startTime)}
            </div>

            {/* Words */}
            <div className="flex flex-wrap gap-1">
              {group.words.map((word) => (
                <WordChip
                  key={word.originalIndex}
                  word={word}
                  index={word.originalIndex}
                  isActive={word.originalIndex === currentWordIndex}
                  onEdit={handleWordEdit}
                  onDelete={handleWordDelete}
                />
              ))}
            </div>
          </motion.div>
        ))}
      </div>

      {/* Footer hint */}
      <div className="flex-none p-3 border-t border-surface-700 text-xs text-surface-500 text-center">
        Click a word to edit • Changes apply to export
      </div>
    </div>
  )
}

// Individual word chip component
function WordChip({
  word,
  index,
  isActive,
  onEdit,
  onDelete,
}: {
  word: Word
  index: number
  isActive: boolean
  onEdit: (index: number, text: string) => void
  onDelete: (index: number) => void
}) {
  const [isEditing, setIsEditing] = useState(false)
  const [editText, setEditText] = useState(word.text)
  const inputRef = useRef<HTMLInputElement>(null)

  // Focus input when editing
  useEffect(() => {
    if (isEditing && inputRef.current) {
      inputRef.current.focus()
      inputRef.current.select()
    }
  }, [isEditing])

  const handleSave = () => {
    if (editText.trim()) {
      onEdit(index, editText.trim())
    }
    setIsEditing(false)
  }

  const handleCancel = () => {
    setEditText(word.text)
    setIsEditing(false)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSave()
    } else if (e.key === 'Escape') {
      handleCancel()
    }
  }

  if (isEditing) {
    return (
      <div className="inline-flex items-center gap-1 bg-surface-700 rounded px-1">
        <input
          ref={inputRef}
          type="text"
          value={editText}
          onChange={(e) => setEditText(e.target.value)}
          onKeyDown={handleKeyDown}
          onBlur={handleSave}
          className="w-20 bg-transparent text-sm py-1 outline-none"
        />
        <button onClick={handleSave} className="p-0.5 text-green-500 hover:text-green-400">
          <Check className="w-3 h-3" />
        </button>
        <button onClick={handleCancel} className="p-0.5 text-red-500 hover:text-red-400">
          <X className="w-3 h-3" />
        </button>
      </div>
    )
  }

  return (
    <button
      data-word-index={index}
      onClick={() => setIsEditing(true)}
      className={cn(
        'px-2 py-1 rounded text-sm transition-all',
        isActive
          ? 'bg-accent-cyan text-surface-900 font-medium'
          : 'bg-surface-700 text-surface-200 hover:bg-surface-600'
      )}
    >
      {word.text}
    </button>
  )
}
