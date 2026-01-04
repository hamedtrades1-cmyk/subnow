"""
Video rendering API endpoints.
"""

from uuid import UUID
from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.post("/{project_id}/render")
async def start_render(project_id: UUID):
    """Start video render for a project."""
    return {"status": "started", "project_id": str(project_id)}


@router.get("/{project_id}/render/status")
async def get_render_status(project_id: UUID):
    """Get render progress."""
    return {"project_id": str(project_id), "progress": 0, "status": "pending"}
