# CaptionMagic - Parallel Development Tasks

## Overview

This document breaks down the project into 5 parallel workstreams that can be developed simultaneously by different Claude instances. Each stream is independent enough to work in parallel, with clear interfaces defined in `ARCHITECTURE.md`.

---

## Stream 1: Backend API + Database
**Estimated Time: 4-6 hours**

### Prerequisites
- PostgreSQL running
- Redis running

### Tasks

#### 1.1 Project Setup (30 min)
```bash
# Create FastAPI project structure
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   └── database.py
├── requirements.txt
└── Dockerfile
```

**Files to create:**
- [ ] `requirements.txt` - Dependencies
- [ ] `app/main.py` - FastAPI app with CORS, routers
- [ ] `app/config.py` - Pydantic settings
- [ ] `app/database.py` - SQLAlchemy setup

#### 1.2 Database Models (1 hour)
- [ ] `app/models/project.py` - Project model
- [ ] `app/models/theme.py` - Theme model  
- [ ] `app/models/transcript.py` - Transcript + Word models
- [ ] `app/models/user.py` - User model (optional, can be basic)
- [ ] Alembic migrations setup

#### 1.3 Pydantic Schemas (30 min)
- [ ] `app/schemas/project.py` - Request/response schemas
- [ ] `app/schemas/theme.py`
- [ ] `app/schemas/transcript.py`

#### 1.4 API Routes (2 hours)
- [ ] `app/api/projects.py` - CRUD operations
- [ ] `app/api/upload.py` - File upload handling (chunked)
- [ ] `app/api/themes.py` - Theme CRUD
- [ ] `app/api/transcribe.py` - Transcription endpoints
- [ ] `app/api/render.py` - Render endpoints
- [ ] `app/api/websocket.py` - WebSocket for progress

#### 1.5 Celery Setup (1 hour)
- [ ] `app/tasks/celery_app.py` - Celery configuration
- [ ] `app/tasks/transcribe.py` - Transcription task
- [ ] `app/tasks/render.py` - Render task

#### 1.6 Storage Service (30 min)
- [ ] `app/services/storage.py` - Local + S3 abstraction

### Deliverables
- Working API server with all endpoints
- Database migrations
- Celery worker setup
- File upload/download working

### Test Commands
```bash
# Start server
uvicorn app.main:app --reload

# Test upload
curl -X POST -F "file=@test.mp4" http://localhost:8000/api/v1/projects

# Test project list
curl http://localhost:8000/api/v1/projects
```

---

## Stream 2: Transcription Service
**Estimated Time: 2-3 hours**

### Prerequisites
- Python with whisper installed (`pip install openai-whisper`)
- FFmpeg (for audio extraction)

### Tasks

#### 2.1 Whisper Integration (1 hour)
- [ ] `app/services/transcription.py` - Main transcription service

```python
# Key functions to implement
def extract_audio(video_path: str) -> str:
    """Extract audio from video using FFmpeg"""
    pass

def transcribe(audio_path: str, language: str = None) -> TranscriptResult:
    """Run Whisper transcription with word timestamps"""
    pass

def format_words(whisper_result: dict) -> List[Word]:
    """Convert Whisper output to our Word format"""
    pass
```

#### 2.2 Language Detection (30 min)
- [ ] Auto-detect language if not specified
- [ ] Support for 50+ languages

#### 2.3 Celery Task Integration (30 min)
- [ ] `app/tasks/transcribe.py` - Async transcription task
- [ ] Progress reporting via WebSocket

#### 2.4 Testing (30 min)
- [ ] Test script with sample videos
- [ ] Accuracy validation

### Deliverables
- `transcribe_video(path, language)` function
- Word-level timestamps with confidence scores
- Progress reporting

### Test Commands
```bash
# Test transcription directly
python -c "
from app.services.transcription import transcribe_video
result = transcribe_video('test.mp4')
print(result)
"
```

### Output Format
```python
{
    "language": "en",
    "full_text": "Hello world this is a test",
    "words": [
        {"text": "Hello", "start": 0.0, "end": 0.5, "confidence": 0.98},
        {"text": "world", "start": 0.5, "end": 1.0, "confidence": 0.95},
        # ...
    ]
}
```

---

## Stream 3: Caption Engine (ASS Generation)
**Estimated Time: 3-4 hours**

### Prerequisites
- Understanding of ASS subtitle format
- Theme schema from ARCHITECTURE.md

### Tasks

#### 3.1 ASS Builder Core (1.5 hours)
- [ ] `caption_engine/ass_builder.py` - ASS file generation

```python
# Key functions
def create_ass_header(width: int, height: int) -> str:
    """Generate ASS header with script info"""
    pass

def create_style(theme: Theme) -> str:
    """Generate V4+ Style line from theme"""
    pass

def create_dialogue_line(words: List[Word], theme: Theme, line_num: int) -> str:
    """Generate single dialogue line with timing"""
    pass
```

#### 3.2 Word Grouping (1 hour)
- [ ] `caption_engine/generator.py` - Main generator

```python
def group_words_into_lines(words: List[Word], theme: Theme) -> List[Line]:
    """
    Group words into display lines based on:
    - words_per_line
    - max_chars_per_line
    - Natural sentence breaks
    """
    pass
```

#### 3.3 Animation Effects (1 hour)
- [ ] `caption_engine/animations.py` - Effect implementations

```python
# Animation types to implement
def karaoke_effect(words: List[Word]) -> str:
    """Word-by-word highlight using \k tags"""
    pass

def bounce_effect(words: List[Word]) -> str:
    """Words bounce in using \move"""
    pass

def pop_effect(words: List[Word]) -> str:
    """Words scale up using \t and \fscx/\fscy"""
    pass

def glow_effect(words: List[Word]) -> str:
    """Words glow using \blur and color transitions"""
    pass

def wave_effect(words: List[Word]) -> str:
    """Words wave using position offsets"""
    pass
```

#### 3.4 Color Conversion (30 min)
- [ ] `caption_engine/utils.py` - Helper functions

```python
def hex_to_ass_color(hex_color: str) -> str:
    """Convert #FFFFFF to &H00FFFFFF (ASS BGR format)"""
    pass

def position_to_alignment(x: int, y: int) -> int:
    """Convert percentage position to ASS alignment (1-9)"""
    pass
```

### Deliverables
- `generate_ass(transcript, theme, width, height)` function
- All animation styles working
- Proper timing and positioning

### Test Commands
```bash
python -c "
from caption_engine import generate_ass
from caption_engine.themes import DEFAULT_THEMES

words = [
    {'text': 'Hello', 'start': 0.0, 'end': 0.5},
    {'text': 'world', 'start': 0.5, 'end': 1.0},
]

ass = generate_ass(words, DEFAULT_THEMES['hormozi'], 1920, 1080)
print(ass)
"
```

### Output Format
```ass
[Script Info]
Title: CaptionMagic Generated
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, ...
Style: Default,Montserrat,80,...

[Events]
Format: Layer, Start, End, Style, ...
Dialogue: 0,0:00:00.00,0:00:01.00,Default,,0,0,0,,{\k50}Hello {\k50}world
```

---

## Stream 4: Video Rendering Service
**Estimated Time: 2-3 hours**

### Prerequisites
- FFmpeg installed
- Font files available

### Tasks

#### 4.1 FFmpeg Wrapper (1 hour)
- [ ] `app/services/video.py` - Video processing functions

```python
def get_video_info(path: str) -> VideoInfo:
    """Get video metadata (duration, resolution, fps)"""
    pass

def render_with_subtitles(
    input_path: str,
    ass_path: str,
    output_path: str,
    fonts_dir: str = None
) -> str:
    """Burn ASS subtitles into video"""
    pass

def generate_preview(
    input_path: str,
    ass_path: str,
    start: float,
    duration: float = 10
) -> str:
    """Generate short preview clip"""
    pass
```

#### 4.2 Progress Tracking (30 min)
- [ ] Parse FFmpeg output for progress percentage
- [ ] Report via callback/WebSocket

```python
def render_with_progress(
    input_path: str,
    ass_path: str,
    output_path: str,
    progress_callback: Callable[[float], None]
) -> str:
    """Render with progress reporting"""
    pass
```

#### 4.3 Font Management (30 min)
- [ ] Font directory setup
- [ ] Download/include common fonts (Montserrat, Inter, Poppins, Impact)

#### 4.4 Celery Task (30 min)
- [ ] `app/tasks/render.py` - Async render task
- [ ] Progress via WebSocket

#### 4.5 Quality Settings (30 min)
- [ ] Output quality presets (720p, 1080p, original)
- [ ] Codec settings (h264, h265)

### Deliverables
- `render_video(input, ass, output)` function
- Progress reporting
- Preview generation
- Multiple quality outputs

### Test Commands
```bash
# Test render
python -c "
from app.services.video import render_with_subtitles
render_with_subtitles('input.mp4', 'captions.ass', 'output.mp4')
"

# Direct FFmpeg test
ffmpeg -i input.mp4 -vf "ass=captions.ass" -c:a copy output.mp4
```

---

## Stream 5: Frontend (Next.js)
**Estimated Time: 5-7 hours**

### Prerequisites
- Node.js 18+
- Backend API running

### Tasks

#### 5.1 Project Setup (30 min)
```bash
npx create-next-app@latest frontend --typescript --tailwind --eslint
cd frontend
npm install @tanstack/react-query axios lucide-react
```

- [ ] Project structure setup
- [ ] Tailwind configuration
- [ ] API client setup

#### 5.2 Upload Component (1 hour)
- [ ] `components/upload/DropZone.tsx` - Drag & drop upload
- [ ] `components/upload/UploadProgress.tsx` - Progress bar
- [ ] File validation (video types, size limits)

#### 5.3 Theme Selector (1.5 hours)
- [ ] `components/themes/ThemeCard.tsx` - Theme preview card
- [ ] `components/themes/ThemeSelector.tsx` - Grid of themes
- [ ] `components/themes/ThemeCustomizer.tsx` - Custom theme editor

#### 5.4 Video Preview (1.5 hours)
- [ ] `components/editor/VideoPreview.tsx` - Video player with captions overlay
- [ ] Caption rendering on canvas (real-time preview)
- [ ] Sync with transcript

#### 5.5 Caption Editor (1 hour)
- [ ] `components/editor/CaptionEditor.tsx` - Edit transcript text
- [ ] `components/editor/Timeline.tsx` - Visual timeline

#### 5.6 Export Flow (1 hour)
- [ ] `components/export/ExportModal.tsx` - Export options
- [ ] `components/export/ProgressBar.tsx` - Render progress
- [ ] Download link generation

#### 5.7 Main Editor Page (1 hour)
- [ ] `app/editor/[id]/page.tsx` - Main editor layout
- [ ] State management
- [ ] WebSocket integration for updates

#### 5.8 Landing Page (30 min)
- [ ] `app/page.tsx` - Simple landing with upload CTA

### Deliverables
- Complete UI matching Submagic
- Upload → Edit → Export flow
- Real-time preview
- Theme customization

### Key Components Structure
```
components/
├── upload/
│   ├── DropZone.tsx         # Drag-drop upload area
│   └── UploadProgress.tsx   # Upload progress indicator
├── editor/
│   ├── VideoPreview.tsx     # Main video player with captions
│   ├── Timeline.tsx         # Caption timeline
│   ├── CaptionEditor.tsx    # Text editing panel
│   └── ThemeSelector.tsx    # Theme picker sidebar
├── themes/
│   ├── ThemeCard.tsx        # Single theme preview
│   └── ThemeCustomizer.tsx  # Custom theme form
└── export/
    ├── ExportModal.tsx      # Export settings modal
    └── ProgressBar.tsx      # Render progress
```

---

## Integration Testing

After all streams complete, run integration tests:

### Test 1: Full Flow
```bash
# 1. Upload video
curl -X POST -F "file=@test.mp4" http://localhost:8000/api/v1/projects

# 2. Start transcription
curl -X POST http://localhost:8000/api/v1/projects/{id}/transcribe

# 3. Apply theme
curl -X POST http://localhost:8000/api/v1/projects/{id}/apply-theme \
  -H "Content-Type: application/json" \
  -d '{"themeId": "hormozi-uuid"}'

# 4. Start render
curl -X POST http://localhost:8000/api/v1/projects/{id}/render

# 5. Download result
curl -O http://localhost:8000/api/v1/projects/{id}/download
```

### Test 2: WebSocket Updates
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/project-id')
ws.onmessage = (e) => console.log(JSON.parse(e.data))
```

---

## Communication Between Instances

When running multiple Claude instances, use this file as the source of truth. Each instance should:

1. **Read ARCHITECTURE.md first** - Understand the full system
2. **Focus on assigned stream** - Don't overlap with other streams
3. **Follow interfaces exactly** - Use the function signatures defined
4. **Update this file** - Mark tasks complete as you go

### Interface Contracts

All instances must agree on these interfaces:

```python
# Transcription output (Stream 2 → Stream 1)
TranscriptResult = {
    "language": str,
    "words": List[{"text": str, "start": float, "end": float, "confidence": float}],
    "full_text": str
}

# Caption engine input/output (Stream 3)
def generate_ass(
    words: List[Word],
    theme: Theme,
    video_width: int,
    video_height: int
) -> str:  # Returns ASS file content

# Video render input (Stream 4)
def render_video(
    input_path: str,
    ass_path: str,
    output_path: str,
    progress_callback: Callable[[float], None] = None
) -> str:  # Returns output path
```

---

## Priority Order

If working sequentially or with limited instances:

1. **Stream 3: Caption Engine** - Core differentiator, complex logic
2. **Stream 2: Transcription** - Required for any demo
3. **Stream 1: Backend API** - Ties everything together
4. **Stream 4: Video Render** - Can use FFmpeg directly initially
5. **Stream 5: Frontend** - Can use Postman/curl initially

---

## Quick Start Commands for Each Instance

### Instance 1 (Backend)
```bash
cd captionmagic/backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Instance 2 (Transcription)
```bash
cd captionmagic/backend
pip install openai-whisper
python -c "import whisper; whisper.load_model('base')"  # Download model
```

### Instance 3 (Caption Engine)
```bash
cd captionmagic/caption-engine
python -m pytest tests/  # Run tests
```

### Instance 4 (Video Render)
```bash
ffmpeg -version  # Verify FFmpeg
cd captionmagic/backend
python scripts/test_render.py
```

### Instance 5 (Frontend)
```bash
cd captionmagic/frontend
npm install
npm run dev
```
