"""
File upload API endpoints.
"""

import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.project import Project, ProjectStatus
from app.services.storage import storage_service
from app.config import settings

router = APIRouter()

ALLOWED_VIDEO_TYPES = {
    "video/mp4",
    "video/quicktime",
    "video/x-msvideo",
    "video/webm",
    "video/x-matroska",
}


@router.post("/video")
async def upload_video(
    file: UploadFile = File(...),
    title: str = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a video file and create a new project.
    
    Returns the created project with upload status.
    """
    # Validate file type
    if file.content_type not in ALLOWED_VIDEO_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_VIDEO_TYPES)}"
        )
    
    # Check file size (read in chunks)
    max_size = settings.max_upload_size_mb * 1024 * 1024
    file_size = 0
    chunks = []
    
    while True:
        chunk = await file.read(1024 * 1024)  # 1MB chunks
        if not chunk:
            break
        file_size += len(chunk)
        chunks.append(chunk)
        
        if file_size > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum: {settings.max_upload_size_mb}MB"
            )
    
    # Generate unique filename
    file_ext = os.path.splitext(file.filename)[1] or ".mp4"
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    
    # Save file
    file_content = b"".join(chunks)
    file_path = await storage_service.save_file(
        file_content,
        unique_filename,
        folder="uploads"
    )
    file_url = await storage_service.get_url(file_path)
    
    # Create project
    project = Project(
        title=title or file.filename,
        status=ProjectStatus.UPLOADING,
        original_video_path=file_path,
        original_video_url=file_url,
    )
    
    db.add(project)
    await db.commit()
    await db.refresh(project)
    
    # Update status to ready for transcription
    project.status = ProjectStatus.READY
    await db.commit()
    
    return {
        "project_id": str(project.id),
        "title": project.title,
        "status": project.status.value,
        "video_url": file_url,
        "message": "Upload complete. Ready for transcription."
    }


@router.post("/video/chunk")
async def upload_video_chunk(
    chunk: UploadFile = File(...),
    upload_id: str = None,
    chunk_number: int = 0,
    total_chunks: int = 1,
):
    """
    Upload video in chunks for large files.
    
    This is an alternative to the single upload endpoint for very large files.
    """
    # This is a simplified implementation
    # In production, you'd want to track chunks in Redis and assemble them
    
    chunk_path = f"chunks/{upload_id}/{chunk_number}"
    content = await chunk.read()
    await storage_service.save_file(content, chunk_path)
    
    return {
        "upload_id": upload_id,
        "chunk_number": chunk_number,
        "total_chunks": total_chunks,
        "status": "chunk_received"
    }
