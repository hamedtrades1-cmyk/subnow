export type AnimationStyle = 
  | 'none' 
  | 'karaoke' 
  | 'bounce' 
  | 'pop' 
  | 'glow' 
  | 'wave'

export type TextAlignment = 'left' | 'center' | 'right'

export type EmojiStyle = 'auto' | 'animated' | 'static' | 'none'

export interface Theme {
  id: string
  name: string
  is_default: boolean
  is_custom: boolean
  user_id: string | null
  
  // Font Settings
  font_family: string
  font_size: number
  font_weight: number
  
  // Colors
  text_color: string
  highlight_color: string
  outline_color: string
  shadow_color: string
  background_color: string | null
  
  // Position
  position_x: number // percentage
  position_y: number // percentage
  alignment: TextAlignment
  
  // Effects
  outline_width: number
  shadow_offset: number
  shadow_blur: number
  
  // Animation
  animation_style: AnimationStyle
  words_per_line: number
  max_chars_per_line: number
  
  // Emoji
  show_emojis: boolean
  emoji_style: EmojiStyle
}

export interface ThemeCreate {
  name: string
  font_family?: string
  font_size?: number
  font_weight?: number
  text_color?: string
  highlight_color?: string
  outline_color?: string
  shadow_color?: string
  background_color?: string | null
  position_x?: number
  position_y?: number
  alignment?: TextAlignment
  outline_width?: number
  shadow_offset?: number
  shadow_blur?: number
  animation_style?: AnimationStyle
  words_per_line?: number
  max_chars_per_line?: number
  show_emojis?: boolean
  emoji_style?: EmojiStyle
}

export interface ThemeUpdate extends Partial<ThemeCreate> {}

// Default themes from the architecture
export const DEFAULT_THEMES: Partial<Theme>[] = [
  {
    name: 'Hormozi',
    font_family: 'Montserrat',
    font_size: 80,
    font_weight: 800,
    text_color: '#FFFFFF',
    highlight_color: '#FFFF00',
    outline_color: '#000000',
    outline_width: 4,
    position_y: 70,
    animation_style: 'karaoke',
    words_per_line: 3,
  },
  {
    name: 'Beast',
    font_family: 'Impact',
    font_size: 90,
    font_weight: 700,
    text_color: '#FFFFFF',
    highlight_color: '#FF0000',
    outline_color: '#000000',
    outline_width: 6,
    position_y: 80,
    animation_style: 'pop',
    words_per_line: 2,
  },
  {
    name: 'Clean',
    font_family: 'Inter',
    font_size: 60,
    font_weight: 600,
    text_color: '#FFFFFF',
    highlight_color: '#00BFFF',
    outline_color: '#000000',
    outline_width: 2,
    position_y: 85,
    animation_style: 'none',
    words_per_line: 5,
  },
  {
    name: 'Neon',
    font_family: 'Poppins',
    font_size: 70,
    font_weight: 700,
    text_color: '#00FF00',
    highlight_color: '#FF00FF',
    outline_color: '#000000',
    outline_width: 3,
    shadow_blur: 10,
    position_y: 75,
    animation_style: 'glow',
    words_per_line: 3,
  },
]
