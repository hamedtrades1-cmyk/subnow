"""
Themes API endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db

router = APIRouter()


@router.get("/")
def list_themes(db: Session = Depends(get_db)):
    return []


@router.get("/{theme_id}")
def get_theme(theme_id: str, db: Session = Depends(get_db)):
    return {"id": theme_id, "name": "Hormozi", "animation_style": "karaoke"}


@router.post("/")
def create_theme(db: Session = Depends(get_db)):
    return {"id": "123", "name": "Custom Theme"}
