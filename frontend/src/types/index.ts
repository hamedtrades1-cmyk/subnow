export * from './project'
export * from './theme'

// WebSocket message types
export interface WSMessage {
  type: 'transcription_progress' | 'render_progress' | 'status_change' | 'error'
  data: WSMessageData
}

export interface WSMessageData {
  project_id?: string
  progress?: number // 0-100
  status?: string
  message?: string
  words?: Array<{ text: string; start: number; end: number; confidence: number }>
}

// API Response types
export interface APIResponse<T> {
  data: T
  message?: string
}

export interface APIError {
  detail: string
  status_code: number
}

// Upload types
export interface UploadProgress {
  loaded: number
  total: number
  percentage: number
}
