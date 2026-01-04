"""
Transcript Pydantic schemas.
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class WordResponse(BaseModel):
    """Schema for a single word."""
    text: str
    start: float
    end: float
    confidence: float = 1.0


class TranscriptResponse(BaseModel):
    """Schema for transcript responses."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    project_id: UUID
    language: str
    full_text: Optional[str] = None
    words_json: List[dict] = []
    created_at: datetime
    updated_at: datetime


class TranscriptCreate(BaseModel):
    """Schema for creating a transcript."""
    language: str = "en"
    full_text: str
    words_json: List[dict] = []
