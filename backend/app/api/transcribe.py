"""
Transcription API endpoints.
"""

from uuid import UUID
from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.post("/{project_id}/transcribe")
async def start_transcription(project_id: UUID, language: str = "en"):
    """Start transcription for a project."""
    return {"status": "started", "project_id": str(project_id), "language": language}


@router.get("/{project_id}/transcript")
async def get_transcript(project_id: UUID):
    """Get transcript for a project."""
    return {"project_id": str(project_id), "words": [], "full_text": ""}
