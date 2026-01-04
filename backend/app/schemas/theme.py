"""
Theme Pydantic schemas.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ThemeBase(BaseModel):
    name: str
    font_family: str = "Montserrat"
    font_size: int = 80
    font_weight: int = 800
    text_color: str = "#FFFFFF"
    highlight_color: str = "#FFFF00"
    outline_color: str = "#000000"
    shadow_color: str = "#000000"
    background_color: Optional[str] = None
    position_x: int = 50
    position_y: int = 70
    alignment: str = "center"
    outline_width: int = 4
    shadow_offset: int = 2
    shadow_blur: int = 0
    animation_style: str = "karaoke"
    animation_speed: float = 1.0
    words_per_line: int = 3
    max_chars_per_line: int = 30
    uppercase: bool = False


class ThemeCreate(ThemeBase):
    pass


class ThemeUpdate(BaseModel):
    name: Optional[str] = None
    font_family: Optional[str] = None
    font_size: Optional[int] = None
    text_color: Optional[str] = None
    highlight_color: Optional[str] = None
    animation_style: Optional[str] = None


class ThemeResponse(ThemeBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    is_default: bool
    is_custom: bool
    created_at: datetime
    updated_at: datetime
