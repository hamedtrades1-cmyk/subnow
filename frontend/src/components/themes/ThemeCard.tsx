'use client'

import { motion } from 'framer-motion'
import { Check, Trash2 } from 'lucide-react'
import { Theme } from '@/types'
import { cn } from '@/lib/utils'

interface ThemeCardProps {
  theme: Theme
  isSelected: boolean
  onSelect: () => void
  onDelete?: () => void
  showDelete?: boolean
}

export function ThemeCard({
  theme,
  isSelected,
  onSelect,
  onDelete,
  showDelete = false,
}: ThemeCardProps) {
  return (
    <motion.button
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={onSelect}
      className={cn(
        'relative w-full text-left rounded-xl overflow-hidden transition-all group',
        isSelected
          ? 'ring-2 ring-accent-cyan shadow-glow-cyan'
          : 'hover:ring-1 hover:ring-surface-500'
      )}
    >
      {/* Preview area */}
      <div className="aspect-video bg-surface-900 flex items-center justify-center p-4 relative">
        {/* Sample caption */}
        <div
          className="text-center"
          style={{
            fontFamily: theme.font_family,
            fontWeight: theme.font_weight,
            textShadow: `
              ${theme.outline_width}px 0 0 ${theme.outline_color},
              -${theme.outline_width}px 0 0 ${theme.outline_color},
              0 ${theme.outline_width}px 0 ${theme.outline_color},
              0 -${theme.outline_width}px 0 ${theme.outline_color}
            `,
          }}
        >
          <span
            className="text-lg"
            style={{ color: theme.text_color }}
          >
            Hello{' '}
          </span>
          <span
            className={cn(
              'text-lg',
              theme.animation_style === 'bounce' && 'animate-bounce-subtle'
            )}
            style={{ color: theme.highlight_color }}
          >
            World
          </span>
        </div>

        {/* Selected indicator */}
        {isSelected && (
          <div className="absolute top-2 right-2 w-6 h-6 rounded-full bg-accent-cyan flex items-center justify-center">
            <Check className="w-4 h-4 text-surface-900" />
          </div>
        )}

        {/* Delete button */}
        {showDelete && onDelete && !theme.is_default && (
          <button
            onClick={(e) => {
              e.stopPropagation()
              onDelete()
            }}
            className="absolute top-2 left-2 w-6 h-6 rounded-full bg-surface-800/80 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-500"
          >
            <Trash2 className="w-3 h-3" />
          </button>
        )}
      </div>

      {/* Info */}
      <div className="bg-surface-800 p-3">
        <div className="flex items-center justify-between">
          <h3 className="font-medium text-sm truncate">{theme.name}</h3>
          {theme.animation_style !== 'none' && (
            <span className="text-xs text-surface-400 capitalize px-2 py-0.5 bg-surface-700 rounded">
              {theme.animation_style}
            </span>
          )}
        </div>
        <p className="text-xs text-surface-500 mt-1">
          {theme.font_family} • {theme.font_size}px
        </p>
      </div>
    </motion.button>
  )
}
