"""
Theme database model - SQLite compatible.
"""

from datetime import datetime
import uuid
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime

from app.database import Base


class Theme(Base):
    __tablename__ = "themes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    is_default = Column(Boolean, default=False)
    is_custom = Column(Boolean, default=True)
    
    font_family = Column(String(100), default="Montserrat")
    font_size = Column(Integer, default=80)
    font_weight = Column(Integer, default=800)
    
    text_color = Column(String(7), default="#FFFFFF")
    highlight_color = Column(String(7), default="#FFFF00")
    outline_color = Column(String(7), default="#000000")
    shadow_color = Column(String(7), default="#000000")
    background_color = Column(String(7), nullable=True)
    
    position_x = Column(Integer, default=50)
    position_y = Column(Integer, default=70)
    alignment = Column(String(10), default="center")
    
    outline_width = Column(Integer, default=4)
    shadow_offset = Column(Integer, default=2)
    shadow_blur = Column(Integer, default=0)
    
    animation_style = Column(String(20), default="karaoke")
    animation_speed = Column(Float, default=1.0)
    
    words_per_line = Column(Integer, default=3)
    max_chars_per_line = Column(Integer, default=30)
    
    uppercase = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
