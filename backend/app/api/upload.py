"""
File upload API endpoints.
"""

import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.project import Project
from app.config import settings

router = APIRouter()

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

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
    db: Session = Depends(get_db)
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
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Save file to disk
    file_content = b"".join(chunks)
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # Create project
    project = Project(
        title=title or file.filename,
        status="ready",
        original_video_path=file_path,
        original_video_url=f"/uploads/{unique_filename}",
    )
    
    db.add(project)
    db.commit()
    db.refresh(project)
    
    return {
        "id": project.id,
        "title": project.title,
        "status": project.status,
        "original_video_url": project.original_video_url,
        "message": "Upload complete. Ready for transcription."
    }
