'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Check, ChevronDown, Plus, Settings2 } from 'lucide-react'
import { Theme } from '@/types'
import { cn } from '@/lib/utils'
import { ThemeCustomizer } from '@/components/themes/ThemeCustomizer'

interface ThemeSelectorProps {
  themes: Theme[]
  selectedTheme: Theme | null
  onSelectTheme: (themeId: string) => void
}

export function ThemeSelector({
  themes,
  selectedTheme,
  onSelectTheme,
}: ThemeSelectorProps) {
  const [isExpanded, setIsExpanded] = useState(true)
  const [showCustomizer, setShowCustomizer] = useState(false)

  // Separate default and custom themes
  const defaultThemes = themes.filter((t) => t.is_default)
  const customThemes = themes.filter((t) => !t.is_default)

  return (
    <div className="flex flex-col">
      {/* Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="panel-header hover:bg-surface-700/50 transition-colors"
      >
        <span className="panel-title">Themes</span>
        <ChevronDown
          className={cn(
            'w-4 h-4 text-surface-400 transition-transform',
            isExpanded && 'rotate-180'
          )}
        />
      </button>

      {/* Theme grid */}
      {isExpanded && (
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: 'auto', opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          className="p-4 border-b border-surface-700"
        >
          {/* Default themes */}
          <div className="grid grid-cols-2 gap-2 mb-4">
            {defaultThemes.map((theme) => (
              <ThemeCard
                key={theme.id}
                theme={theme}
                isSelected={selectedTheme?.id === theme.id}
                onSelect={() => onSelectTheme(theme.id)}
              />
            ))}
          </div>

          {/* Custom themes section */}
          {customThemes.length > 0 && (
            <>
              <div className="text-xs text-surface-500 uppercase tracking-wide mb-2">
                Custom
              </div>
              <div className="grid grid-cols-2 gap-2 mb-4">
                {customThemes.map((theme) => (
                  <ThemeCard
                    key={theme.id}
                    theme={theme}
                    isSelected={selectedTheme?.id === theme.id}
                    onSelect={() => onSelectTheme(theme.id)}
                  />
                ))}
              </div>
            </>
          )}

          {/* Actions */}
          <div className="flex gap-2">
            <button
              onClick={() => setShowCustomizer(true)}
              className="btn-secondary flex-1 flex items-center justify-center gap-2 text-sm"
            >
              {selectedTheme ? (
                <>
                  <Settings2 className="w-4 h-4" />
                  Customize
                </>
              ) : (
                <>
                  <Plus className="w-4 h-4" />
                  Create Theme
                </>
              )}
            </button>
          </div>
        </motion.div>
      )}

      {/* Theme customizer modal */}
      {showCustomizer && (
        <ThemeCustomizer
          theme={selectedTheme}
          onClose={() => setShowCustomizer(false)}
          onSave={(theme) => {
            // Handle save
            setShowCustomizer(false)
          }}
        />
      )}
    </div>
  )
}

// Theme card component
function ThemeCard({
  theme,
  isSelected,
  onSelect,
}: {
  theme: Theme
  isSelected: boolean
  onSelect: () => void
}) {
  return (
    <button
      onClick={onSelect}
      className={cn(
        'relative p-3 rounded-lg transition-all text-left',
        isSelected
          ? 'bg-accent-cyan/10 ring-2 ring-accent-cyan'
          : 'bg-surface-700 hover:bg-surface-600'
      )}
    >
      {/* Preview */}
      <div
        className="h-10 rounded flex items-center justify-center mb-2 text-sm font-bold"
        style={{
          backgroundColor: '#1a1a1a',
          fontFamily: theme.font_family,
        }}
      >
        <span
          style={{
            color: theme.text_color,
            textShadow: `1px 1px 0 ${theme.outline_color}`,
          }}
        >
          Aa
        </span>
        <span
          style={{
            color: theme.highlight_color,
            textShadow: `1px 1px 0 ${theme.outline_color}`,
            marginLeft: '4px',
          }}
        >
          Bb
        </span>
      </div>

      {/* Name */}
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium truncate">{theme.name}</span>
        {isSelected && (
          <Check className="w-4 h-4 text-accent-cyan flex-none" />
        )}
      </div>

      {/* Animation badge */}
      {theme.animation_style !== 'none' && (
        <div className="text-xs text-surface-400 capitalize mt-1">
          {theme.animation_style}
        </div>
      )}
    </button>
  )
}
