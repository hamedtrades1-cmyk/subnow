"""
Video rendering API endpoints.
"""

import os
import sys

# Add caption_engine to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.project import Project
from app.services.video import render_video_with_captions

try:
    from caption_engine import generate_ass
except ImportError:
    # Fallback if caption_engine not available
    def generate_ass(words, theme, width=1080, height=1920):
        raise ImportError("caption_engine not available")

router = APIRouter()

@router.post("/{project_id}/render")
def start_render(
    project_id: str,
    theme_id: str = "hormozi",
    db: Session = Depends(get_db)
):
    """Render video with burned-in captions."""
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if not project.original_video_path:
        raise HTTPException(status_code=400, detail="No video uploaded")
    
    # Get transcript words from project
    words = project.transcript_words
    if not words:
        raise HTTPException(status_code=400, detail="No transcript available. Please transcribe the video first.")
    
    # Update status
    project.status = "rendering"
    project.theme_id = theme_id
    db.commit()
    
    try:
        # Generate ASS subtitles
        ass_content = generate_ass(words, theme_id, video_width=1080, video_height=1920)
        
        # Render video
        output_path = project.original_video_path.replace('.mp4', '_captioned.mp4')
        render_video_with_captions(
            project.original_video_path,
            ass_content,
            output_path
        )
        
        project.rendered_video_path = output_path
        project.rendered_video_url = f"/uploads/{os.path.basename(output_path)}"
        project.status = "completed"
        db.commit()
        
        return {
            "status": "completed",
            "video_url": project.rendered_video_url,
            "download_url": f"/api/v1/projects/{project_id}/download"
        }
    except Exception as e:
        project.status = "error"
        project.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{project_id}/download")
def download_video(project_id: str, db: Session = Depends(get_db)):
    """Download rendered video."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if not project.rendered_video_path:
        raise HTTPException(status_code=400, detail="Video not rendered yet")
    
    if not os.path.exists(project.rendered_video_path):
        raise HTTPException(status_code=404, detail="Rendered video file not found")
    
    return FileResponse(
        project.rendered_video_path,
        media_type="video/mp4",
        filename=f"{project.title}_captioned.mp4"
    )
