'use client'

import { motion } from 'framer-motion'
import { Upload, Loader2 } from 'lucide-react'
import { formatBytes } from '@/lib/utils'
import { UploadProgress as UploadProgressType } from '@/types'

interface UploadProgressProps {
  progress: UploadProgressType
  fileName?: string
}

export function UploadProgress({ progress, fileName }: UploadProgressProps) {
  const isComplete = progress.percentage >= 100

  return (
    <div className="rounded-2xl border-2 border-accent-cyan/30 bg-surface-800/50 p-8">
      <div className="flex flex-col items-center gap-6">
        {/* Icon */}
        <div className="w-20 h-20 rounded-2xl bg-accent-cyan/10 flex items-center justify-center">
          {isComplete ? (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: 'spring', stiffness: 200 }}
            >
              <Upload className="w-10 h-10 text-accent-cyan" />
            </motion.div>
          ) : (
            <Loader2 className="w-10 h-10 text-accent-cyan animate-spin" />
          )}
        </div>

        {/* Status text */}
        <div className="text-center">
          <p className="text-lg font-medium mb-1">
            {isComplete ? 'Processing video...' : 'Uploading...'}
          </p>
          {fileName && (
            <p className="text-surface-400 text-sm truncate max-w-xs">
              {fileName}
            </p>
          )}
        </div>

        {/* Progress bar */}
        <div className="w-full max-w-md">
          <div className="h-2 bg-surface-700 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-accent-cyan to-accent-purple rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${progress.percentage}%` }}
              transition={{ duration: 0.3 }}
            />
          </div>
          
          {/* Progress info */}
          <div className="flex justify-between mt-2 text-sm text-surface-400">
            <span>{progress.percentage}%</span>
            <span>
              {formatBytes(progress.loaded)} / {formatBytes(progress.total)}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}
