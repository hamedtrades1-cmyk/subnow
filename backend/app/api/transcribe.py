"""
Transcription API endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.project import Project
from app.services.transcription import transcribe_video

router = APIRouter()

@router.post("/{project_id}/transcribe")
def start_transcription(project_id: str, language: str = None, db: Session = Depends(get_db)):
    """Transcribe video using Whisper."""
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if not project.original_video_path:
        raise HTTPException(status_code=400, detail="No video uploaded")
    
    # Update status
    project.status = "transcribing"
    db.commit()
    
    try:
        # Run transcription
        result = transcribe_video(project.original_video_path, language)
        
        # Store transcript in project
        project.transcript_words = result["words"]
        project.transcript_full_text = result["full_text"]
        project.language = result["language"]
        project.status = "transcribed"
        db.commit()
        
        return {
            "status": "completed",
            "words": result["words"],
            "full_text": result["full_text"],
            "language": result["language"]
        }
    except Exception as e:
        project.status = "error"
        project.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{project_id}/transcript")
def get_transcript(project_id: str, db: Session = Depends(get_db)):
    """Get transcript for a project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return {
        "words": project.transcript_words,
        "full_text": project.transcript_full_text or "",
        "language": project.language or "en"
    }
