"""
Project database model - SQLite compatible.
"""

import enum
import json
from datetime import datetime
import uuid
from sqlalchemy import Column, String, Float, Integer, DateTime, Enum, ForeignKey, Text

from app.database import Base


class ProjectStatus(str, enum.Enum):
    UPLOADING = "uploading"
    READY = "ready"
    TRANSCRIBING = "transcribing"
    TRANSCRIBED = "transcribed"
    RENDERING = "rendering"
    COMPLETED = "completed"
    ERROR = "error"


class Project(Base):
    __tablename__ = "projects"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    status = Column(String(20), default="uploading")
    
    original_video_path = Column(String(500))
    original_video_url = Column(String(1000))
    rendered_video_path = Column(String(500))
    rendered_video_url = Column(String(1000))
    
    duration = Column(Float)
    width = Column(Integer)
    height = Column(Integer)
    fps = Column(Float)
    
    language = Column(String(10), default="en")
    theme_id = Column(String(36), nullable=True)
    error_message = Column(Text)
    
    # Transcript data stored as JSON string
    transcript_json = Column(Text, nullable=True)
    transcript_full_text = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def transcript_words(self):
        """Get transcript words as list of dicts."""
        if self.transcript_json:
            return json.loads(self.transcript_json)
        return []
    
    @transcript_words.setter
    def transcript_words(self, words):
        """Set transcript words from list of dicts."""
        self.transcript_json = json.dumps(words) if words else None
