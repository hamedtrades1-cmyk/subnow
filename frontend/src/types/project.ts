export type ProjectStatus = 
  | 'uploading' 
  | 'transcribing' 
  | 'ready' 
  | 'rendering' 
  | 'completed' 
  | 'error'

export interface Project {
  id: string
  title: string
  status: ProjectStatus
  
  // Files
  original_video_path: string
  original_video_url: string
  rendered_video_path: string | null
  rendered_video_url: string | null
  
  // Settings
  language: string
  theme_id: string | null
  
  // Metadata
  duration: number // seconds
  width: number
  height: number
  fps: number
  
  // Timestamps
  created_at: string
  updated_at: string
  
  // Relations
  transcript: Transcript | null
  theme: Theme | null
}

export interface ProjectCreate {
  title?: string
  language?: string
}

export interface Transcript {
  id: string
  project_id: string
  language: string
  words: Word[]
  full_text?: string
}

export interface Word {
  text: string
  start: number // seconds
  end: number   // seconds
  confidence: number
}
