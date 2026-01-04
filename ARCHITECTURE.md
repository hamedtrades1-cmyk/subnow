# CaptionMagic - Submagic Clone Architecture

## Project Overview

CaptionMagic is an open-source alternative to Submagic that provides automated video captioning with animated, styled subtitles.

**Core Features:**
- Video upload and processing
- AI-powered speech-to-text transcription (word-level timestamps)
- Animated caption rendering (karaoke-style, bounce, glow effects)
- Theme customization (fonts, colors, positions, animations)
- Real-time preview
- Video export with burned-in captions

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND                                    │
│                         (Next.js + Tailwind)                            │
├─────────────────────────────────────────────────────────────────────────┤
│  Upload UI  │  Theme Editor  │  Timeline/Preview  │  Export Manager     │
└──────┬──────┴───────┬────────┴─────────┬──────────┴──────────┬──────────┘
       │              │                  │                     │
       ▼              ▼                  ▼                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                              API GATEWAY                                 │
│                         (FastAPI + REST/WebSocket)                      │
├─────────────────────────────────────────────────────────────────────────┤
│  /upload  │  /projects  │  /themes  │  /transcribe  │  /render  │  /ws  │
└──────┬────┴──────┬──────┴─────┬─────┴───────┬───────┴─────┬─────┴───┬───┘
       │           │            │             │             │         │
       ▼           ▼            ▼             ▼             ▼         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           TASK QUEUE                                     │
│                        (Celery + Redis)                                  │
├─────────────────────────────────────────────────────────────────────────┤
│  transcribe_video  │  render_preview  │  export_video  │  apply_theme   │
└──────────┬─────────┴────────┬─────────┴───────┬────────┴────────┬───────┘
           │                  │                 │                 │
           ▼                  ▼                 ▼                 ▼
┌──────────────────┐ ┌────────────────┐ ┌───────────────┐ ┌───────────────┐
│  TRANSCRIPTION   │ │ CAPTION ENGINE │ │ VIDEO RENDER  │ │    STORAGE    │
│    SERVICE       │ │                │ │    SERVICE    │ │               │
├──────────────────┤ ├────────────────┤ ├───────────────┤ ├───────────────┤
│ - Whisper API    │ │ - ASS/SRT Gen  │ │ - FFmpeg      │ │ - S3/MinIO    │
│ - Word timestamps│ │ - Animation    │ │ - Subtitle    │ │ - Local FS    │
│ - Language detect│ │ - Theme apply  │ │   burn-in     │ │ - CDN         │
└──────────────────┘ └────────────────┘ └───────────────┘ └───────────────┘
           │                  │                 │                 │
           └──────────────────┴────────┬────────┴─────────────────┘
                                       ▼
                              ┌─────────────────┐
                              │    DATABASE     │
                              │   (PostgreSQL)  │
                              ├─────────────────┤
                              │ - Projects      │
                              │ - Themes        │
                              │ - Users         │
                              │ - Transcripts   │
                              └─────────────────┘
```

---

## Directory Structure

```
captionmagic/
├── ARCHITECTURE.md          # This file
├── TASKS.md                 # Parallel task breakdown
├── docker-compose.yml       # Local development setup
├── .env.example             # Environment variables template
│
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI app entry
│   │   ├── config.py        # Settings/configuration
│   │   ├── database.py      # DB connection
│   │   │
│   │   ├── api/             # API Routes
│   │   │   ├── __init__.py
│   │   │   ├── projects.py  # Project CRUD
│   │   │   ├── upload.py    # File upload handling
│   │   │   ├── transcribe.py# Transcription endpoints
│   │   │   ├── themes.py    # Theme management
│   │   │   ├── render.py    # Video rendering
│   │   │   └── websocket.py # Real-time updates
│   │   │
│   │   ├── models/          # SQLAlchemy Models
│   │   │   ├── __init__.py
│   │   │   ├── project.py
│   │   │   ├── theme.py
│   │   │   ├── transcript.py
│   │   │   └── user.py
│   │   │
│   │   ├── schemas/         # Pydantic Schemas
│   │   │   ├── __init__.py
│   │   │   ├── project.py
│   │   │   ├── theme.py
│   │   │   └── transcript.py
│   │   │
│   │   ├── services/        # Business Logic
│   │   │   ├── __init__.py
│   │   │   ├── storage.py   # File storage service
│   │   │   ├── transcription.py  # Whisper integration
│   │   │   └── video.py     # FFmpeg operations
│   │   │
│   │   └── tasks/           # Celery Tasks
│   │       ├── __init__.py
│   │       ├── celery_app.py
│   │       ├── transcribe.py
│   │       └── render.py
│   │
│   ├── requirements.txt
│   ├── Dockerfile
│   └── alembic/             # DB migrations
│
├── caption-engine/          # Caption Generation Engine
│   ├── __init__.py
│   ├── generator.py         # Main caption generator
│   ├── ass_builder.py       # ASS subtitle builder
│   ├── animations.py        # Animation effects
│   ├── themes.py            # Theme definitions
│   └── utils.py             # Helper functions
│
├── frontend/                # Next.js Frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx           # Landing page
│   │   │   ├── editor/
│   │   │   │   └── [id]/page.tsx  # Main editor
│   │   │   └── api/               # API routes (proxy)
│   │   │
│   │   ├── components/
│   │   │   ├── upload/
│   │   │   │   ├── DropZone.tsx
│   │   │   │   └── UploadProgress.tsx
│   │   │   ├── editor/
│   │   │   │   ├── VideoPreview.tsx
│   │   │   │   ├── Timeline.tsx
│   │   │   │   ├── CaptionEditor.tsx
│   │   │   │   └── ThemeSelector.tsx
│   │   │   ├── themes/
│   │   │   │   ├── ThemeCard.tsx
│   │   │   │   └── ThemeCustomizer.tsx
│   │   │   └── export/
│   │   │       ├── ExportModal.tsx
│   │   │       └── ProgressBar.tsx
│   │   │
│   │   ├── hooks/
│   │   │   ├── useProject.ts
│   │   │   ├── useWebSocket.ts
│   │   │   └── useVideoPlayer.ts
│   │   │
│   │   ├── lib/
│   │   │   ├── api.ts       # API client
│   │   │   └── utils.ts
│   │   │
│   │   └── types/
│   │       ├── project.ts
│   │       ├── theme.ts
│   │       └── transcript.ts
│   │
│   ├── package.json
│   ├── tailwind.config.js
│   └── Dockerfile
│
└── scripts/                 # Utility scripts
    ├── setup.sh             # Initial setup
    ├── seed_themes.py       # Seed default themes
    └── test_transcription.py
```

---

## Data Models

### Project
```python
class Project:
    id: UUID
    title: str
    status: Enum['uploading', 'transcribing', 'ready', 'rendering', 'completed', 'error']
    
    # Files
    original_video_path: str
    original_video_url: str
    rendered_video_path: str | None
    rendered_video_url: str | None
    
    # Settings
    language: str = 'en'
    theme_id: UUID | None
    
    # Metadata
    duration: float  # seconds
    width: int
    height: int
    fps: float
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    # Relations
    transcript: Transcript
    theme: Theme
```

### Transcript
```python
class Transcript:
    id: UUID
    project_id: UUID
    language: str
    
    # Word-level data
    words: List[Word]
    
class Word:
    text: str
    start: float      # seconds
    end: float        # seconds
    confidence: float
```

### Theme
```python
class Theme:
    id: UUID
    name: str
    is_default: bool
    is_custom: bool
    user_id: UUID | None
    
    # Font Settings
    font_family: str = 'Montserrat'
    font_size: int = 80
    font_weight: int = 800
    
    # Colors
    text_color: str = '#FFFFFF'
    highlight_color: str = '#FFFF00'  # Active word
    outline_color: str = '#000000'
    shadow_color: str = '#000000'
    background_color: str | None = None  # Optional word background
    
    # Position
    position_x: int = 50  # percentage from left
    position_y: int = 70  # percentage from top
    alignment: Enum['left', 'center', 'right'] = 'center'
    
    # Effects
    outline_width: int = 4
    shadow_offset: int = 2
    shadow_blur: int = 0
    
    # Animation
    animation_style: Enum['none', 'karaoke', 'bounce', 'pop', 'glow', 'wave']
    words_per_line: int = 3
    max_chars_per_line: int = 30
    
    # Emoji Settings
    show_emojis: bool = True
    emoji_style: Enum['auto', 'animated', 'static', 'none']
```

---

## API Endpoints

### Projects
```
POST   /api/v1/projects              # Create project (upload video)
GET    /api/v1/projects              # List user's projects
GET    /api/v1/projects/{id}         # Get project details
DELETE /api/v1/projects/{id}         # Delete project
PATCH  /api/v1/projects/{id}         # Update project settings
```

### Transcription
```
POST   /api/v1/projects/{id}/transcribe     # Start transcription
GET    /api/v1/projects/{id}/transcript     # Get transcript
PATCH  /api/v1/projects/{id}/transcript     # Edit transcript (manual corrections)
```

### Themes
```
GET    /api/v1/themes                       # List all themes
POST   /api/v1/themes                       # Create custom theme
GET    /api/v1/themes/{id}                  # Get theme details
PATCH  /api/v1/themes/{id}                  # Update theme
DELETE /api/v1/themes/{id}                  # Delete custom theme
POST   /api/v1/projects/{id}/apply-theme    # Apply theme to project
```

### Rendering
```
POST   /api/v1/projects/{id}/render         # Start video render
GET    /api/v1/projects/{id}/render/status  # Get render progress
GET    /api/v1/projects/{id}/download       # Download rendered video
POST   /api/v1/projects/{id}/preview        # Generate preview clip
```

### WebSocket
```
WS     /api/v1/ws/{project_id}              # Real-time updates
                                            # - transcription progress
                                            # - render progress
                                            # - status changes
```

---

## Key Technical Components

### 1. Transcription Service (Whisper)

```python
# Uses OpenAI Whisper for word-level timestamps
import whisper

def transcribe(audio_path: str, language: str = None) -> dict:
    model = whisper.load_model("base")  # or "small", "medium", "large"
    result = model.transcribe(
        audio_path,
        language=language,
        word_timestamps=True,
        verbose=False
    )
    
    words = []
    for segment in result["segments"]:
        for word_data in segment.get("words", []):
            words.append({
                "text": word_data["word"].strip(),
                "start": word_data["start"],
                "end": word_data["end"],
                "confidence": word_data.get("probability", 1.0)
            })
    
    return {
        "language": result["language"],
        "words": words,
        "full_text": result["text"]
    }
```

### 2. ASS Subtitle Generation

ASS (Advanced SubStation Alpha) format supports:
- Rich text styling
- Positioning
- Animation effects
- Color changes (karaoke)

```ass
[Script Info]
Title: CaptionMagic Generated
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Montserrat,80,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,4,2,2,10,10,50,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:02.50,Default,,0,0,0,,{\k25}Hello {\k30}world {\k20}this {\k25}is {\k35}caption
```

### 3. FFmpeg Rendering

```bash
# Burn subtitles into video
ffmpeg -i input.mp4 -vf "ass=captions.ass" -c:a copy output.mp4

# With custom font directory
ffmpeg -i input.mp4 -vf "ass=captions.ass:fontsdir=/fonts" -c:a copy output.mp4
```

### 4. Animation Effects

**Karaoke Effect (word highlighting)**
```ass
{\k100}Word1 {\k150}Word2 {\k80}Word3
# \k = duration in centiseconds before highlight moves to next word
```

**Bounce Effect**
```ass
{\move(960,800,960,750,0,200)\move(960,750,960,800,200,400)}Word
# Move up then down
```

**Pop/Scale Effect**
```ass
{\fscx80\fscy80\t(0,100,\fscx100\fscy100)}Word
# Scale from 80% to 100%
```

---

## Default Themes (Seed Data)

```python
DEFAULT_THEMES = [
    {
        "name": "Hormozi",
        "font_family": "Montserrat",
        "font_size": 80,
        "font_weight": 800,
        "text_color": "#FFFFFF",
        "highlight_color": "#FFFF00",
        "outline_color": "#000000",
        "outline_width": 4,
        "position_y": 70,
        "animation_style": "karaoke",
        "words_per_line": 3
    },
    {
        "name": "Beast",
        "font_family": "Impact",
        "font_size": 90,
        "font_weight": 700,
        "text_color": "#FFFFFF",
        "highlight_color": "#FF0000",
        "outline_color": "#000000",
        "outline_width": 6,
        "position_y": 80,
        "animation_style": "pop",
        "words_per_line": 2
    },
    {
        "name": "Clean",
        "font_family": "Inter",
        "font_size": 60,
        "font_weight": 600,
        "text_color": "#FFFFFF",
        "highlight_color": "#00BFFF",
        "outline_color": "#000000",
        "outline_width": 2,
        "position_y": 85,
        "animation_style": "none",
        "words_per_line": 5
    },
    {
        "name": "Neon",
        "font_family": "Poppins",
        "font_size": 70,
        "font_weight": 700,
        "text_color": "#00FF00",
        "highlight_color": "#FF00FF",
        "outline_color": "#000000",
        "outline_width": 3,
        "shadow_blur": 10,
        "position_y": 75,
        "animation_style": "glow",
        "words_per_line": 3
    }
]
```

---

## Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/captionmagic

# Redis (Celery broker)
REDIS_URL=redis://localhost:6379/0

# Storage
STORAGE_TYPE=local  # or 's3'
STORAGE_PATH=/data/uploads
S3_BUCKET=captionmagic
S3_REGION=us-east-1
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=

# Whisper
WHISPER_MODEL=base  # base, small, medium, large
WHISPER_DEVICE=cpu  # cpu or cuda

# App
SECRET_KEY=your-secret-key
CORS_ORIGINS=http://localhost:3000
MAX_UPLOAD_SIZE_MB=500

# FFmpeg
FFMPEG_PATH=/usr/bin/ffmpeg
FONTS_DIR=/app/fonts
```

---

## Development Setup

```bash
# 1. Clone and setup
git clone https://github.com/you/captionmagic
cd captionmagic
cp .env.example .env

# 2. Start services with Docker
docker-compose up -d

# 3. Run migrations
cd backend && alembic upgrade head

# 4. Seed default themes
python scripts/seed_themes.py

# 5. Start backend
uvicorn app.main:app --reload --port 8000

# 6. Start Celery worker
celery -A app.tasks.celery_app worker --loglevel=info

# 7. Start frontend
cd frontend && npm install && npm run dev
```

---

## Parallel Development Streams

See `TASKS.md` for detailed breakdown of parallel workstreams.

| Stream | Owner | Components |
|--------|-------|------------|
| **Stream 1** | Claude Instance 1 | Backend API + Database |
| **Stream 2** | Claude Instance 2 | Transcription Service |
| **Stream 3** | Claude Instance 3 | Caption Engine (ASS generation) |
| **Stream 4** | Claude Instance 4 | Video Rendering (FFmpeg) |
| **Stream 5** | Claude Instance 5 | Frontend (Next.js) |

---

## Integration Points

When working in parallel, these are the key interfaces between components:

### Backend → Caption Engine
```python
from caption_engine import generate_ass

ass_content = generate_ass(
    transcript=transcript,  # List of words with timestamps
    theme=theme,            # Theme settings dict
    video_width=1920,
    video_height=1080
)
```

### Backend → Transcription
```python
from services.transcription import transcribe_video

result = transcribe_video(
    video_path="/path/to/video.mp4",
    language="en"  # or None for auto-detect
)
# Returns: {"language": "en", "words": [...], "full_text": "..."}
```

### Backend → Video Render
```python
from services.video import render_video

output_path = render_video(
    input_path="/path/to/input.mp4",
    ass_path="/path/to/captions.ass",
    output_path="/path/to/output.mp4"
)
```

### Frontend → Backend
```typescript
// API client
const api = {
  createProject: (file: File) => POST('/api/v1/projects', { file }),
  getProject: (id: string) => GET(`/api/v1/projects/${id}`),
  startTranscription: (id: string) => POST(`/api/v1/projects/${id}/transcribe`),
  applyTheme: (id: string, themeId: string) => POST(`/api/v1/projects/${id}/apply-theme`, { themeId }),
  startRender: (id: string) => POST(`/api/v1/projects/${id}/render`),
}

// WebSocket for real-time updates
const ws = new WebSocket(`ws://localhost:8000/api/v1/ws/${projectId}`)
ws.onmessage = (event) => {
  const { type, data } = JSON.parse(event.data)
  // type: 'transcription_progress' | 'render_progress' | 'status_change'
}
```
