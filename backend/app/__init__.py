"""
API Routes Package
"""
from fastapi import APIRouter

from app.api.projects import router as projects_router
from app.api.themes import router as themes_router
from app.api.upload import router as upload_router
from app.api.transcribe import router as transcribe_router
from app.api.render import router as render_router
from app.api.websocket import router as websocket_router

# Main API router
api_router = APIRouter()

# Include all sub-routers
api_router.include_router(projects_router, prefix="/projects", tags=["projects"])
api_router.include_router(themes_router, prefix="/themes", tags=["themes"])
api_router.include_router(upload_router, prefix="/upload", tags=["upload"])
api_router.include_router(transcribe_router, tags=["transcription"])
api_router.include_router(render_router, tags=["rendering"])
api_router.include_router(websocket_router, tags=["websocket"])
