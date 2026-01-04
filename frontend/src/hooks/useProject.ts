import { create } from 'zustand'
import { Project, Theme, Word } from '@/types'
import { api } from '@/lib/api'

interface ProjectState {
  project: Project | null
  isLoading: boolean
  error: string | null
  themes: Theme[]
  selectedTheme: Theme | null
  editedWords: Word[]
  hasUnsavedChanges: boolean
  
  loadProject: (id: string) => Promise<void>
  setProject: (project: Project) => void
  updateProjectStatus: (status: Project['status']) => void
  loadThemes: () => Promise<void>
  selectTheme: (theme: Theme) => void
  applyTheme: (themeId: string) => Promise<void>
  setEditedWords: (words: Word[]) => void
  updateWord: (index: number, word: Partial<Word>) => void
  saveTranscript: () => Promise<void>
  startTranscription: () => Promise<void>
  startRender: () => Promise<void>
  reset: () => void
}

const initialState = {
  project: null,
  isLoading: false,
  error: null,
  themes: [],
  selectedTheme: null,
  editedWords: [],
  hasUnsavedChanges: false,
}

export const useProject = create<ProjectState>((set, get) => ({
  ...initialState,

  loadProject: async (id: string) => {
    set({ isLoading: true, error: null })
    try {
      const project = await api.getProject(id)
      
      // Also try to load transcript
      try {
        const transcript = await api.getTranscript(id)
        if (transcript?.words?.length > 0) {
          set({ 
            project: { ...project, status: 'transcribed' },
            isLoading: false,
            editedWords: transcript.words,
          })
          return
        }
      } catch (e) {
        // No transcript yet, that's okay
      }
      
      set({ 
        project, 
        isLoading: false,
        editedWords: [],
      })
    } catch (err) {
      set({ 
        error: err instanceof Error ? err.message : 'Failed to load project',
        isLoading: false 
      })
    }
  },

  setProject: (project: Project) => {
    set({ project })
  },

  updateProjectStatus: (status: Project['status']) => {
    const { project } = get()
    if (project) {
      set({ project: { ...project, status } })
    }
  },

  loadThemes: async () => {
    try {
      const themes = await api.getThemes()
      set({ themes })
    } catch (err) {
      console.error('Failed to load themes:', err)
    }
  },

  selectTheme: (theme: Theme) => {
    set({ selectedTheme: theme })
  },

  applyTheme: async (themeId: string) => {
    const { project, themes } = get()
    if (!project) return
    
    try {
      const theme = themes.find(t => t.id === themeId) || null
      set({ selectedTheme: theme })
    } catch (err) {
      console.error('Failed to apply theme:', err)
    }
  },

  setEditedWords: (words: Word[]) => {
    set({ editedWords: words, hasUnsavedChanges: true })
  },

  updateWord: (index: number, updates: Partial<Word>) => {
    const { editedWords } = get()
    const newWords = [...editedWords]
    newWords[index] = { ...newWords[index], ...updates }
    set({ editedWords: newWords, hasUnsavedChanges: true })
  },

  saveTranscript: async () => {
    set({ hasUnsavedChanges: false })
  },

  startTranscription: async () => {
    const { project } = get()
    if (!project) return
    
    set({ project: { ...project, status: 'transcribing' } })
    
    try {
      // Call transcription API
      await api.startTranscription(project.id)
      
      // Immediately fetch the transcript (mock returns it instantly)
      const transcript = await api.getTranscript(project.id)
      
      set({ 
        project: { ...project, status: 'transcribed' },
        editedWords: transcript.words || [],
      })
    } catch (err) {
      console.error('Failed to transcribe:', err)
      set({ project: { ...project, status: 'error' } })
    }
  },

  startRender: async () => {
    const { project } = get()
    if (!project) return
    
    try {
      await api.startRender(project.id)
      set({ project: { ...project, status: 'rendering' } })
    } catch (err) {
      console.error('Failed to start render:', err)
    }
  },

  reset: () => set(initialState),
}))
