'use client'

import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, Film, AlertCircle } from 'lucide-react'
import { cn, formatBytes, isVideoFile } from '@/lib/utils'

interface DropZoneProps {
  onFileSelect: (file: File) => void
  maxSize?: number // in bytes
  accept?: Record<string, string[]>
  className?: string
}

const DEFAULT_MAX_SIZE = 500 * 1024 * 1024 // 500MB
const DEFAULT_ACCEPT = {
  'video/*': ['.mp4', '.mov', '.avi', '.mkv', '.webm'],
}

export function DropZone({
  onFileSelect,
  maxSize = DEFAULT_MAX_SIZE,
  accept = DEFAULT_ACCEPT,
  className,
}: DropZoneProps) {
  const [error, setError] = useState<string | null>(null)

  const onDrop = useCallback(
    (acceptedFiles: File[], rejectedFiles: unknown[]) => {
      setError(null)

      if (rejectedFiles.length > 0) {
        setError('Please upload a valid video file (MP4, MOV, AVI, MKV, WebM)')
        return
      }

      const file = acceptedFiles[0]
      if (!file) return

      if (!isVideoFile(file)) {
        setError('Please upload a video file')
        return
      }

      if (file.size > maxSize) {
        setError(`File too large. Maximum size is ${formatBytes(maxSize)}`)
        return
      }

      onFileSelect(file)
    },
    [onFileSelect, maxSize]
  )

  const { getRootProps, getInputProps, isDragActive, isDragAccept, isDragReject } = useDropzone({
    onDrop,
    accept,
    maxSize,
    multiple: false,
  })

  return (
    <div
      {...getRootProps()}
      className={cn(
        'relative rounded-2xl border-2 border-dashed p-12 transition-all duration-300 cursor-pointer group',
        isDragActive && 'scale-[1.02]',
        isDragAccept && 'border-accent-cyan bg-accent-cyan/5',
        isDragReject && 'border-red-500 bg-red-500/5',
        !isDragActive && 'border-surface-600 hover:border-accent-cyan/50 hover:bg-surface-800/50',
        className
      )}
    >
      <input {...getInputProps()} />
      
      {/* Background glow on hover */}
      <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-accent-cyan/5 to-accent-purple/5 opacity-0 group-hover:opacity-100 transition-opacity" />
      
      <div className="relative flex flex-col items-center gap-6">
        {/* Icon */}
        <div className={cn(
          'w-20 h-20 rounded-2xl flex items-center justify-center transition-all duration-300',
          isDragAccept && 'bg-accent-cyan/20 scale-110',
          isDragReject && 'bg-red-500/20',
          !isDragActive && 'bg-surface-800 group-hover:bg-accent-cyan/10 group-hover:scale-105'
        )}>
          {isDragReject ? (
            <AlertCircle className="w-10 h-10 text-red-500" />
          ) : (
            <Film className="w-10 h-10 text-accent-cyan" />
          )}
        </div>

        {/* Text */}
        <div className="text-center">
          {isDragActive ? (
            isDragAccept ? (
              <p className="text-lg font-medium text-accent-cyan">Drop to upload!</p>
            ) : (
              <p className="text-lg font-medium text-red-400">Invalid file type</p>
            )
          ) : (
            <>
              <p className="text-lg font-medium mb-2">
                Drag & drop your video here
              </p>
              <p className="text-surface-400 mb-4">
                or click to browse
              </p>
            </>
          )}
        </div>

        {/* Upload button */}
        {!isDragActive && (
          <button className="btn-primary flex items-center gap-2">
            <Upload className="w-4 h-4" />
            Select Video
          </button>
        )}

        {/* File info */}
        {!isDragActive && (
          <p className="text-sm text-surface-500">
            MP4, MOV, AVI, MKV, WebM • Max {formatBytes(maxSize)}
          </p>
        )}

        {/* Error message */}
        {error && (
          <div className="flex items-center gap-2 text-red-400 text-sm">
            <AlertCircle className="w-4 h-4" />
            {error}
          </div>
        )}
      </div>
    </div>
  )
}
