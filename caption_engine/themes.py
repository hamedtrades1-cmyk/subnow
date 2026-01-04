"""
Theme definitions for CaptionMagic.

Each theme controls the visual appearance and animation of captions.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class AnimationStyle(str, Enum):
    NONE = "none"
    KARAOKE = "karaoke"      # Word-by-word highlight
    BOUNCE = "bounce"        # Words bounce in
    POP = "pop"              # Words scale up
    GLOW = "glow"            # Words glow/pulse
    WAVE = "wave"            # Words wave motion


class Alignment(str, Enum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


@dataclass
class Theme:
    """Caption theme configuration."""
    
    name: str
    
    # Font Settings
    font_family: str = "Montserrat"
    font_size: int = 80
    font_weight: int = 800  # 400=normal, 700=bold, 800=extrabold
    
    # Colors (hex format)
    text_color: str = "#FFFFFF"
    highlight_color: str = "#FFFF00"  # Active word color
    outline_color: str = "#000000"
    shadow_color: str = "#000000"
    background_color: Optional[str] = None  # Optional word background
    
    # Position (percentage)
    position_x: int = 50  # 0-100, from left
    position_y: int = 70  # 0-100, from top
    alignment: Alignment = Alignment.CENTER
    
    # Effects
    outline_width: int = 4
    shadow_offset: int = 2
    shadow_blur: int = 0
    
    # Animation
    animation_style: AnimationStyle = AnimationStyle.KARAOKE
    animation_speed: float = 1.0  # Multiplier
    
    # Line Settings
    words_per_line: int = 3
    max_chars_per_line: int = 30
    line_spacing: int = 10  # pixels between lines
    
    # Advanced
    uppercase: bool = False
    letter_spacing: int = 0
    
    # Metadata
    is_default: bool = False
    is_custom: bool = False
    
    def to_dict(self) -> dict:
        """Convert theme to dictionary."""
        return {
            "name": self.name,
            "font_family": self.font_family,
            "font_size": self.font_size,
            "font_weight": self.font_weight,
            "text_color": self.text_color,
            "highlight_color": self.highlight_color,
            "outline_color": self.outline_color,
            "shadow_color": self.shadow_color,
            "background_color": self.background_color,
            "position_x": self.position_x,
            "position_y": self.position_y,
            "alignment": self.alignment.value,
            "outline_width": self.outline_width,
            "shadow_offset": self.shadow_offset,
            "shadow_blur": self.shadow_blur,
            "animation_style": self.animation_style.value,
            "animation_speed": self.animation_speed,
            "words_per_line": self.words_per_line,
            "max_chars_per_line": self.max_chars_per_line,
            "line_spacing": self.line_spacing,
            "uppercase": self.uppercase,
            "letter_spacing": self.letter_spacing,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Theme":
        """Create theme from dictionary."""
        # Handle enum conversions
        if "alignment" in data and isinstance(data["alignment"], str):
            data["alignment"] = Alignment(data["alignment"])
        if "animation_style" in data and isinstance(data["animation_style"], str):
            data["animation_style"] = AnimationStyle(data["animation_style"])
        return cls(**data)


# =============================================================================
# DEFAULT THEMES
# =============================================================================

THEME_HORMOZI = Theme(
    name="Hormozi",
    font_family="Montserrat",
    font_size=80,
    font_weight=800,
    text_color="#FFFFFF",
    highlight_color="#FFFF00",
    outline_color="#000000",
    outline_width=4,
    shadow_offset=3,
    position_y=70,
    animation_style=AnimationStyle.KARAOKE,
    words_per_line=3,
    uppercase=True,
    is_default=True,
)

THEME_BEAST = Theme(
    name="Beast",
    font_family="Impact",
    font_size=90,
    font_weight=700,
    text_color="#FFFFFF",
    highlight_color="#FF0000",
    outline_color="#000000",
    outline_width=6,
    shadow_offset=4,
    position_y=80,
    animation_style=AnimationStyle.POP,
    words_per_line=2,
    uppercase=True,
    is_default=True,
)

THEME_CLEAN = Theme(
    name="Clean",
    font_family="Inter",
    font_size=60,
    font_weight=600,
    text_color="#FFFFFF",
    highlight_color="#00BFFF",
    outline_color="#000000",
    outline_width=2,
    shadow_offset=1,
    position_y=85,
    animation_style=AnimationStyle.NONE,
    words_per_line=5,
    max_chars_per_line=40,
    is_default=True,
)

THEME_NEON = Theme(
    name="Neon",
    font_family="Poppins",
    font_size=70,
    font_weight=700,
    text_color="#00FF00",
    highlight_color="#FF00FF",
    outline_color="#000000",
    outline_width=3,
    shadow_blur=10,
    position_y=75,
    animation_style=AnimationStyle.GLOW,
    words_per_line=3,
    is_default=True,
)

THEME_MINIMAL = Theme(
    name="Minimal",
    font_family="Helvetica",
    font_size=50,
    font_weight=400,
    text_color="#FFFFFF",
    highlight_color="#FFFFFF",
    outline_color="#000000",
    outline_width=1,
    shadow_offset=0,
    position_y=90,
    animation_style=AnimationStyle.NONE,
    words_per_line=6,
    max_chars_per_line=50,
    is_default=True,
)

THEME_BOLD = Theme(
    name="Bold",
    font_family="Arial Black",
    font_size=85,
    font_weight=900,
    text_color="#FFFFFF",
    highlight_color="#FFA500",
    outline_color="#000000",
    outline_width=5,
    shadow_offset=4,
    position_y=70,
    animation_style=AnimationStyle.BOUNCE,
    words_per_line=2,
    uppercase=True,
    is_default=True,
)

THEME_GRADIENT = Theme(
    name="Gradient",
    font_family="Montserrat",
    font_size=75,
    font_weight=700,
    text_color="#FF6B6B",
    highlight_color="#4ECDC4",
    outline_color="#2C3E50",
    outline_width=3,
    shadow_offset=2,
    position_y=72,
    animation_style=AnimationStyle.WAVE,
    words_per_line=3,
    is_default=True,
)

THEME_SARA = Theme(
    name="Sara",
    font_family="Poppins",
    font_size=65,
    font_weight=600,
    text_color="#FFFFFF",
    highlight_color="#FF69B4",
    outline_color="#000000",
    outline_width=3,
    shadow_offset=2,
    position_y=75,
    animation_style=AnimationStyle.KARAOKE,
    words_per_line=4,
    is_default=True,
)


# Dictionary of all default themes
DEFAULT_THEMES = {
    "hormozi": THEME_HORMOZI,
    "beast": THEME_BEAST,
    "clean": THEME_CLEAN,
    "neon": THEME_NEON,
    "minimal": THEME_MINIMAL,
    "bold": THEME_BOLD,
    "gradient": THEME_GRADIENT,
    "sara": THEME_SARA,
}


def get_theme(name: str) -> Theme:
    """Get a theme by name (case-insensitive)."""
    name_lower = name.lower()
    if name_lower in DEFAULT_THEMES:
        return DEFAULT_THEMES[name_lower]
    raise ValueError(f"Unknown theme: {name}. Available: {list(DEFAULT_THEMES.keys())}")


def list_themes() -> list[str]:
    """List all available theme names."""
    return list(DEFAULT_THEMES.keys())
