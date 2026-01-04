import { Project, Theme, Transcript, UploadProgress } from '@/types'

class APIClient {
  async createProject(
    file: File,
    options?: { title?: string; language?: string },
    onProgress?: (progress: UploadProgress) => void
  ): Promise<Project> {
    const formData = new FormData()
    formData.append('file', file)
    if (options?.title) formData.append('title', options.title)
    if (options?.language) formData.append('language', options.language)

    const response = await fetch('/api/upload', {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) throw new Error('Upload failed')
    return response.json()
  }

  async getProjects(): Promise<Project[]> {
    const response = await fetch('/api/projects')
    return response.json()
  }

  async getProject(id: string): Promise<Project> {
    const response = await fetch(`/api/projects/${id}`)
    if (!response.ok) throw new Error('Project not found')
    return response.json()
  }

  async deleteProject(id: string): Promise<void> {
    await fetch(`/api/projects/${id}`, { method: 'DELETE' })
  }

  async startTranscription(projectId: string, language?: string): Promise<{ task_id: string }> {
    const response = await fetch(`/api/projects/${projectId}/transcribe`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ language })
    })
    return response.json()
  }

  async getTranscript(projectId: string): Promise<Transcript> {
    const response = await fetch(`/api/projects/${projectId}/transcript`)
    return response.json()
  }

  async updateTranscript(projectId: string, words: any[]): Promise<Transcript> {
    return { words, full_text: '' } as Transcript
  }

  async getThemes(): Promise<Theme[]> {
    const response = await fetch('/api/themes')
    return response.json()
  }

  async getTheme(id: string): Promise<Theme> {
    const themes = await this.getThemes()
    return themes.find(t => t.id === id) || themes[0]
  }

  async createTheme(theme: Partial<Theme>): Promise<Theme> {
    return { id: 'custom', ...theme } as Theme
  }

  async updateTheme(id: string, theme: Partial<Theme>): Promise<Theme> {
    return { id, ...theme } as Theme
  }

  async deleteTheme(id: string): Promise<void> {}

  async applyTheme(projectId: string, themeId: string): Promise<Project> {
    return {} as Project
  }

  async startRender(projectId: string): Promise<{ task_id: string }> {
    return { task_id: 'mock' }
  }

  async getPreviewFrame(projectId: string, timestamp: number): Promise<{ frame_url: string }> {
    return { frame_url: '' }
  }
}

export const api = new APIClient()

export function createWebSocket(projectId: string): WebSocket {
  return new WebSocket(`ws://localhost:8000/api/v1/ws/${projectId}`)
}
