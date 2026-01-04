import { Project, Theme, Transcript, UploadProgress } from '@/types'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || ''

class APIClient {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE) {
    this.baseUrl = baseUrl
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
      throw new Error(error.detail || `HTTP ${response.status}`)
    }

    return response.json()
  }

  // Projects
  async createProject(
    file: File,
    options?: { title?: string; language?: string },
    onProgress?: (progress: UploadProgress) => void
  ): Promise<Project> {
    const formData = new FormData()
    formData.append('file', file)
    if (options?.title) formData.append('title', options.title)
    if (options?.language) formData.append('language', options.language)

    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest()
      
      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable && onProgress) {
          onProgress({
            loaded: e.loaded,
            total: e.total,
            percentage: Math.round((e.loaded / e.total) * 100),
          })
        }
      })

      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          resolve(JSON.parse(xhr.responseText))
        } else {
          reject(new Error(`Upload failed: ${xhr.status}`))
        }
      })

      xhr.addEventListener('error', () => reject(new Error('Upload failed')))
      xhr.addEventListener('abort', () => reject(new Error('Upload cancelled')))

      xhr.open('POST', `${this.baseUrl}/api/v1/projects`)
      xhr.send(formData)
    })
  }

  async getProjects(): Promise<Project[]> {
    return this.request<Project[]>('/api/v1/projects')
  }

  async getProject(id: string): Promise<Project> {
    return this.request<Project>(`/api/v1/projects/${id}`)
  }

  async deleteProject(id: string): Promise<void> {
    await this.request(`/api/v1/projects/${id}`, { method: 'DELETE' })
  }

  // Transcription
  async startTranscription(
    projectId: string,
    language?: string
  ): Promise<{ task_id: string }> {
    return this.request<{ task_id: string }>(
      `/api/v1/projects/${projectId}/transcribe`,
      {
        method: 'POST',
        body: JSON.stringify({ language }),
      }
    )
  }

  async getTranscript(projectId: string): Promise<Transcript> {
    return this.request<Transcript>(`/api/v1/projects/${projectId}/transcript`)
  }

  async updateTranscript(
    projectId: string,
    words: Array<{ text: string; start: number; end: number }>
  ): Promise<Transcript> {
    return this.request<Transcript>(`/api/v1/projects/${projectId}/transcript`, {
      method: 'PUT',
      body: JSON.stringify({ words }),
    })
  }

  // Themes
  async getThemes(): Promise<Theme[]> {
    return this.request<Theme[]>('/api/v1/themes')
  }

  async getTheme(id: string): Promise<Theme> {
    return this.request<Theme>(`/api/v1/themes/${id}`)
  }

  async createTheme(theme: Partial<Theme>): Promise<Theme> {
    return this.request<Theme>('/api/v1/themes', {
      method: 'POST',
      body: JSON.stringify(theme),
    })
  }

  async updateTheme(id: string, theme: Partial<Theme>): Promise<Theme> {
    return this.request<Theme>(`/api/v1/themes/${id}`, {
      method: 'PUT',
      body: JSON.stringify(theme),
    })
  }

  async deleteTheme(id: string): Promise<void> {
    await this.request(`/api/v1/themes/${id}`, { method: 'DELETE' })
  }

  // Apply theme to project
  async applyTheme(projectId: string, themeId: string): Promise<Project> {
    return this.request<Project>(`/api/v1/projects/${projectId}/apply-theme`, {
      method: 'POST',
      body: JSON.stringify({ theme_id: themeId }),
    })
  }

  // Rendering
  async startRender(projectId: string): Promise<{ task_id: string }> {
    return this.request<{ task_id: string }>(
      `/api/v1/projects/${projectId}/render`,
      { method: 'POST' }
    )
  }

  async getPreviewFrame(
    projectId: string,
    timestamp: number
  ): Promise<{ frame_url: string }> {
    return this.request<{ frame_url: string }>(
      `/api/v1/projects/${projectId}/preview?timestamp=${timestamp}`
    )
  }
}

export const api = new APIClient()

// WebSocket connection helper
export function createWebSocket(projectId: string): WebSocket {
  const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'
  return new WebSocket(`${wsUrl}/api/v1/ws/${projectId}`)
}
