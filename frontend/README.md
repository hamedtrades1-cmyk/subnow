# CaptionMagic Frontend

Next.js frontend for CaptionMagic - AI-powered video captioning with animated subtitles.

## Features

- **Video Upload**: Drag-and-drop video upload with progress tracking
- **AI Transcription**: Real-time transcription progress via WebSocket
- **Theme System**: 4 default themes (Hormozi, Beast, Clean, Neon) + custom theme creation
- **Caption Editor**: Word-by-word editing with timeline sync
- **Live Preview**: Real-time caption preview with animation effects
- **Export**: HD video export with burned-in captions

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS with custom dark theme
- **State**: Zustand
- **Animations**: Framer Motion
- **UI Components**: Radix UI primitives
- **TypeScript**: Full type safety

## Getting Started

### Prerequisites

- Node.js 20+
- npm or yarn
- Backend API running (see backend README)

### Installation

```bash
# Install dependencies
npm install

# Copy environment variables
cp .env.example .env.local

# Update .env.local with your API URLs
# NEXT_PUBLIC_API_URL=http://localhost:8000
# NEXT_PUBLIC_WS_URL=ws://localhost:8000

# Start development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the app.

### Docker

```bash
# Build image
docker build -t captionmagic-frontend \
  --build-arg NEXT_PUBLIC_API_URL=http://api:8000 \
  --build-arg NEXT_PUBLIC_WS_URL=ws://api:8000 \
  .

# Run container
docker run -p 3000:3000 captionmagic-frontend
```

## Project Structure

```
src/
├── app/                    # Next.js app router
│   ├── page.tsx            # Landing page
│   ├── layout.tsx          # Root layout
│   ├── globals.css         # Global styles
│   └── editor/
│       └── [id]/page.tsx   # Editor page
│
├── components/
│   ├── upload/             # Upload components
│   │   ├── DropZone.tsx    # Drag & drop upload
│   │   └── UploadProgress.tsx
│   ├── editor/             # Editor components
│   │   ├── VideoPreview.tsx
│   │   ├── Timeline.tsx
│   │   ├── CaptionEditor.tsx
│   │   └── ThemeSelector.tsx
│   ├── themes/             # Theme components
│   │   ├── ThemeCard.tsx
│   │   └── ThemeCustomizer.tsx
│   └── export/             # Export components
│       ├── ExportModal.tsx
│       └── ProgressBar.tsx
│
├── hooks/                  # Custom React hooks
│   ├── useProject.ts       # Project state (Zustand)
│   ├── useWebSocket.ts     # Real-time updates
│   └── useVideoPlayer.ts   # Video playback control
│
├── lib/                    # Utilities
│   ├── api.ts              # API client
│   └── utils.ts            # Helper functions
│
└── types/                  # TypeScript types
    ├── project.ts
    ├── theme.ts
    └── index.ts
```

## Theme System

### Default Themes

| Theme | Style | Animation |
|-------|-------|-----------|
| **Hormozi** | White text, yellow highlight | Karaoke |
| **Beast** | Bold white, red highlight | Pop |
| **Clean** | Minimal, cyan highlight | None |
| **Neon** | Green text, magenta highlight | Glow |

### Animation Styles

- `none` - Static text
- `karaoke` - Word-by-word highlighting
- `bounce` - Bouncing effect on active word
- `pop` - Scale pop animation
- `glow` - Pulsing glow effect
- `wave` - Wave animation across words

## API Integration

The frontend communicates with the backend via:

- **REST API**: Project CRUD, transcription, themes, rendering
- **WebSocket**: Real-time progress updates

See `src/lib/api.ts` for the complete API client.

## Development

```bash
# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Lint code
npm run lint

# Type check
npm run type-check
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000` |
| `NEXT_PUBLIC_WS_URL` | WebSocket URL | `ws://localhost:8000` |

## License

MIT
