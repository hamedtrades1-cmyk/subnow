"""
Transcript database model - SQLite compatible.
"""

from datetime import datetime
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON

from app.database import Base


class Transcript(Base):
    __tablename__ = "transcripts"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    
    language = Column(String(10), default="en")
    full_text = Column(Text)
    words_json = Column(JSON, default=list)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Word:
    def __init__(self, text: str, start: float, end: float, confidence: float = 1.0):
        self.text = text
        self.start = start
        self.end = end
        self.confidence = confidence
