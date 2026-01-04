"""
Project Pydantic schemas.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ProjectCreate(BaseModel):
    title: str
    language: str = "en"


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    language: Optional[str] = None
    theme_id: Optional[str] = None


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    title: str
    status: str
    original_video_url: Optional[str] = None
    rendered_video_url: Optional[str] = None
    duration: Optional[float] = None
    language: str = "en"
    created_at: datetime
    updated_at: datetime
