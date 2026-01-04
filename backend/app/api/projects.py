"""
Projects API endpoints.
"""

import os
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.project import Project

router = APIRouter()

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/")
def list_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    return projects


@router.get("/{project_id}")
def get_project(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/")
async def create_project(
    file: UploadFile = File(...),
    title: str = Form(None),
    language: str = Form("en"),
    db: Session = Depends(get_db)
):
    """Upload video and create project."""
    
    # Generate unique filename
    file_ext = os.path.splitext(file.filename)[1] or ".mp4"
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Save file
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Create project
    project = Project(
        title=title or file.filename,
        status="ready",
        original_video_path=file_path,
        original_video_url=f"/uploads/{unique_filename}",
        language=language,
    )
    
    db.add(project)
    db.commit()
    db.refresh(project)
    
    return {
        "id": project.id,
        "title": project.title,
        "status": project.status,
        "original_video_url": project.original_video_url,
        "language": project.language,
        "created_at": project.created_at,
        "updated_at": project.updated_at,
    }


@router.delete("/{project_id}")
def delete_project(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return {"status": "deleted"}
