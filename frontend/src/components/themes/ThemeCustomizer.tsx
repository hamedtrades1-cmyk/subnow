'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Save } from 'lucide-react'
import * as Slider from '@radix-ui/react-slider'
import { Theme, AnimationStyle, TextAlignment } from '@/types'
import { cn } from '@/lib/utils'

interface ThemeCustomizerProps {
  theme: Theme | null
  onClose: () => void
  onSave: (theme: Partial<Theme>) => void
}

const FONTS = [
  'Montserrat',
  'Impact',
  'Inter',
  'Poppins',
  'Roboto',
  'Open Sans',
  'Oswald',
  'Bebas Neue',
]

const ANIMATIONS: AnimationStyle[] = ['none', 'karaoke', 'bounce', 'pop', 'glow', 'wave']

const ALIGNMENTS: TextAlignment[] = ['left', 'center', 'right']

export function ThemeCustomizer({ theme, onClose, onSave }: ThemeCustomizerProps) {
  const [formData, setFormData] = useState({
    name: theme?.name || 'Custom Theme',
    font_family: theme?.font_family || 'Montserrat',
    font_size: theme?.font_size || 80,
    font_weight: theme?.font_weight || 700,
    text_color: theme?.text_color || '#FFFFFF',
    highlight_color: theme?.highlight_color || '#FFFF00',
    outline_color: theme?.outline_color || '#000000',
    outline_width: theme?.outline_width || 4,
    shadow_blur: theme?.shadow_blur || 0,
    position_y: theme?.position_y || 70,
    alignment: theme?.alignment || 'center',
    animation_style: theme?.animation_style || 'karaoke',
    words_per_line: theme?.words_per_line || 3,
  })

  const updateField = <K extends keyof typeof formData>(
    key: K,
    value: typeof formData[K]
  ) => {
    setFormData((prev) => ({ ...prev, [key]: value }))
  }

  const handleSave = () => {
    onSave(formData)
  }

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
          className="w-full max-w-lg bg-surface-800 rounded-2xl border border-surface-700 overflow-hidden max-h-[90vh] flex flex-col"
        >
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-surface-700">
            <h2 className="text-lg font-semibold">
              {theme ? 'Edit Theme' : 'Create Theme'}
            </h2>
            <button onClick={onClose} className="btn-icon">
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-4 space-y-6">
            {/* Theme name */}
            <div>
              <label className="block text-sm font-medium text-surface-300 mb-2">
                Theme Name
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => updateField('name', e.target.value)}
                className="input"
                placeholder="My Custom Theme"
              />
            </div>

            {/* Preview */}
            <div>
              <label className="block text-sm font-medium text-surface-300 mb-2">
                Preview
              </label>
              <div className="bg-surface-900 rounded-lg p-6 flex items-center justify-center">
                <div
                  style={{
                    fontFamily: formData.font_family,
                    fontSize: `${formData.font_size / 2}px`,
                    fontWeight: formData.font_weight,
                    textAlign: formData.alignment,
                    textShadow: `
                      ${formData.outline_width}px 0 0 ${formData.outline_color},
                      -${formData.outline_width}px 0 0 ${formData.outline_color},
                      0 ${formData.outline_width}px 0 ${formData.outline_color},
                      0 -${formData.outline_width}px 0 ${formData.outline_color}
                    `,
                  }}
                >
                  <span style={{ color: formData.text_color }}>This is </span>
                  <span style={{ color: formData.highlight_color }}>awesome</span>
                </div>
              </div>
            </div>

            {/* Font settings */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-surface-300 mb-2">
                  Font Family
                </label>
                <select
                  value={formData.font_family}
                  onChange={(e) => updateField('font_family', e.target.value)}
                  className="input"
                >
                  {FONTS.map((font) => (
                    <option key={font} value={font}>
                      {font}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-surface-300 mb-2">
                  Font Size: {formData.font_size}
                </label>
                <Slider.Root
                  value={[formData.font_size]}
                  onValueChange={([v]) => updateField('font_size', v)}
                  min={40}
                  max={120}
                  step={2}
                  className="relative flex items-center w-full h-5"
                >
                  <Slider.Track className="bg-surface-700 relative grow rounded-full h-2">
                    <Slider.Range className="absolute bg-accent-cyan rounded-full h-full" />
                  </Slider.Track>
                  <Slider.Thumb className="block w-5 h-5 bg-white rounded-full shadow-lg focus:outline-none focus:ring-2 focus:ring-accent-cyan" />
                </Slider.Root>
              </div>
            </div>

            {/* Colors */}
            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-surface-300 mb-2">
                  Text Color
                </label>
                <div className="flex gap-2">
                  <input
                    type="color"
                    value={formData.text_color}
                    onChange={(e) => updateField('text_color', e.target.value)}
                    className="w-10 h-10 rounded cursor-pointer"
                  />
                  <input
                    type="text"
                    value={formData.text_color}
                    onChange={(e) => updateField('text_color', e.target.value)}
                    className="input flex-1 font-mono text-sm"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-surface-300 mb-2">
                  Highlight
                </label>
                <div className="flex gap-2">
                  <input
                    type="color"
                    value={formData.highlight_color}
                    onChange={(e) => updateField('highlight_color', e.target.value)}
                    className="w-10 h-10 rounded cursor-pointer"
                  />
                  <input
                    type="text"
                    value={formData.highlight_color}
                    onChange={(e) => updateField('highlight_color', e.target.value)}
                    className="input flex-1 font-mono text-sm"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-surface-300 mb-2">
                  Outline
                </label>
                <div className="flex gap-2">
                  <input
                    type="color"
                    value={formData.outline_color}
                    onChange={(e) => updateField('outline_color', e.target.value)}
                    className="w-10 h-10 rounded cursor-pointer"
                  />
                  <input
                    type="text"
                    value={formData.outline_color}
                    onChange={(e) => updateField('outline_color', e.target.value)}
                    className="input flex-1 font-mono text-sm"
                  />
                </div>
              </div>
            </div>

            {/* Effects */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-surface-300 mb-2">
                  Outline Width: {formData.outline_width}
                </label>
                <Slider.Root
                  value={[formData.outline_width]}
                  onValueChange={([v]) => updateField('outline_width', v)}
                  min={0}
                  max={10}
                  step={1}
                  className="relative flex items-center w-full h-5"
                >
                  <Slider.Track className="bg-surface-700 relative grow rounded-full h-2">
                    <Slider.Range className="absolute bg-accent-cyan rounded-full h-full" />
                  </Slider.Track>
                  <Slider.Thumb className="block w-5 h-5 bg-white rounded-full shadow-lg focus:outline-none focus:ring-2 focus:ring-accent-cyan" />
                </Slider.Root>
              </div>

              <div>
                <label className="block text-sm font-medium text-surface-300 mb-2">
                  Position Y: {formData.position_y}%
                </label>
                <Slider.Root
                  value={[formData.position_y]}
                  onValueChange={([v]) => updateField('position_y', v)}
                  min={10}
                  max={90}
                  step={5}
                  className="relative flex items-center w-full h-5"
                >
                  <Slider.Track className="bg-surface-700 relative grow rounded-full h-2">
                    <Slider.Range className="absolute bg-accent-cyan rounded-full h-full" />
                  </Slider.Track>
                  <Slider.Thumb className="block w-5 h-5 bg-white rounded-full shadow-lg focus:outline-none focus:ring-2 focus:ring-accent-cyan" />
                </Slider.Root>
              </div>
            </div>

            {/* Animation */}
            <div>
              <label className="block text-sm font-medium text-surface-300 mb-2">
                Animation Style
              </label>
              <div className="grid grid-cols-3 gap-2">
                {ANIMATIONS.map((anim) => (
                  <button
                    key={anim}
                    onClick={() => updateField('animation_style', anim)}
                    className={cn(
                      'px-3 py-2 rounded-lg text-sm font-medium capitalize transition-all',
                      formData.animation_style === anim
                        ? 'bg-accent-cyan text-surface-900'
                        : 'bg-surface-700 text-surface-300 hover:bg-surface-600'
                    )}
                  >
                    {anim}
                  </button>
                ))}
              </div>
            </div>

            {/* Layout */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-surface-300 mb-2">
                  Alignment
                </label>
                <div className="flex gap-2">
                  {ALIGNMENTS.map((align) => (
                    <button
                      key={align}
                      onClick={() => updateField('alignment', align)}
                      className={cn(
                        'flex-1 px-3 py-2 rounded-lg text-sm font-medium capitalize transition-all',
                        formData.alignment === align
                          ? 'bg-accent-cyan text-surface-900'
                          : 'bg-surface-700 text-surface-300 hover:bg-surface-600'
                      )}
                    >
                      {align}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-surface-300 mb-2">
                  Words per Line: {formData.words_per_line}
                </label>
                <Slider.Root
                  value={[formData.words_per_line]}
                  onValueChange={([v]) => updateField('words_per_line', v)}
                  min={1}
                  max={8}
                  step={1}
                  className="relative flex items-center w-full h-5"
                >
                  <Slider.Track className="bg-surface-700 relative grow rounded-full h-2">
                    <Slider.Range className="absolute bg-accent-cyan rounded-full h-full" />
                  </Slider.Track>
                  <Slider.Thumb className="block w-5 h-5 bg-white rounded-full shadow-lg focus:outline-none focus:ring-2 focus:ring-accent-cyan" />
                </Slider.Root>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="flex justify-end gap-3 p-4 border-t border-surface-700">
            <button onClick={onClose} className="btn-secondary">
              Cancel
            </button>
            <button onClick={handleSave} className="btn-primary flex items-center gap-2">
              <Save className="w-4 h-4" />
              Save Theme
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}
