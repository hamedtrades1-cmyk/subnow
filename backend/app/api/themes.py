"""
Themes API endpoints.
"""

import sys
import os

# Add caption_engine to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

try:
    from caption_engine.themes import DEFAULT_THEMES, get_theme as get_theme_by_name
except ImportError:
    # Fallback themes if caption_engine not available
    DEFAULT_THEMES = {
        "hormozi": {"name": "Hormozi", "font_family": "Montserrat", "animation_style": "karaoke"},
        "beast": {"name": "Beast", "font_family": "Impact", "animation_style": "pop"},
        "clean": {"name": "Clean", "font_family": "Inter", "animation_style": "none"},
        "neon": {"name": "Neon", "font_family": "Poppins", "animation_style": "glow"},
        "minimal": {"name": "Minimal", "font_family": "Helvetica", "animation_style": "none"},
        "bold": {"name": "Bold", "font_family": "Arial Black", "animation_style": "bounce"},
        "gradient": {"name": "Gradient", "font_family": "Montserrat", "animation_style": "wave"},
        "sara": {"name": "Sara", "font_family": "Poppins", "animation_style": "karaoke"},
    }
    get_theme_by_name = None

router = APIRouter()


@router.get("/")
def list_themes(db: Session = Depends(get_db)):
    """List all available caption themes."""
    themes = []
    for theme_id, theme in DEFAULT_THEMES.items():
        if hasattr(theme, 'to_dict'):
            theme_data = theme.to_dict()
            theme_data['id'] = theme_id
        else:
            theme_data = {"id": theme_id, **theme}
        themes.append(theme_data)
    return themes


@router.get("/{theme_id}")
def get_theme(theme_id: str, db: Session = Depends(get_db)):
    """Get a specific theme by ID."""
    theme_id_lower = theme_id.lower()
    if theme_id_lower not in DEFAULT_THEMES:
        raise HTTPException(status_code=404, detail=f"Theme '{theme_id}' not found")
    
    theme = DEFAULT_THEMES[theme_id_lower]
    if hasattr(theme, 'to_dict'):
        theme_data = theme.to_dict()
        theme_data['id'] = theme_id_lower
    else:
        theme_data = {"id": theme_id_lower, **theme}
    return theme_data


@router.post("/")
def create_theme(db: Session = Depends(get_db)):
    """Create a custom theme (placeholder)."""
    return {"id": "custom", "name": "Custom Theme", "message": "Custom themes not yet implemented"}
