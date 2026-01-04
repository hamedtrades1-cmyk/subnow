'use client'

import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'

interface ProgressBarProps {
  progress: number // 0-100
  showLabel?: boolean
  size?: 'sm' | 'md' | 'lg'
  variant?: 'default' | 'gradient' | 'striped'
  className?: string
}

export function ProgressBar({
  progress,
  showLabel = false,
  size = 'md',
  variant = 'gradient',
  className,
}: ProgressBarProps) {
  const clampedProgress = Math.max(0, Math.min(100, progress))

  const sizeClasses = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3',
  }

  const variantClasses = {
    default: 'bg-accent-cyan',
    gradient: 'bg-gradient-to-r from-accent-cyan to-accent-purple',
    striped: 'bg-accent-cyan bg-striped',
  }

  return (
    <div className={cn('w-full', className)}>
      <div
        className={cn(
          'w-full bg-surface-700 rounded-full overflow-hidden',
          sizeClasses[size]
        )}
      >
        <motion.div
          className={cn('h-full rounded-full', variantClasses[variant])}
          initial={{ width: 0 }}
          animate={{ width: `${clampedProgress}%` }}
          transition={{ duration: 0.3, ease: 'easeOut' }}
        />
      </div>

      {showLabel && (
        <div className="flex justify-between mt-1 text-xs text-surface-400">
          <span>{clampedProgress}%</span>
          <span>100%</span>
        </div>
      )}
    </div>
  )
}

// Indeterminate progress bar for loading states
export function IndeterminateProgress({
  size = 'md',
  className,
}: {
  size?: 'sm' | 'md' | 'lg'
  className?: string
}) {
  const sizeClasses = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3',
  }

  return (
    <div
      className={cn(
        'w-full bg-surface-700 rounded-full overflow-hidden',
        sizeClasses[size],
        className
      )}
    >
      <motion.div
        className="h-full w-1/3 bg-gradient-to-r from-accent-cyan to-accent-purple rounded-full"
        animate={{
          x: ['0%', '200%', '0%'],
        }}
        transition={{
          duration: 1.5,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
      />
    </div>
  )
}
