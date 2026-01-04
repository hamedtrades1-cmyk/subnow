"""
ASS (Advanced SubStation Alpha) subtitle file builder.

Generates properly formatted ASS files with styles and dialogue.
"""

from typing import List, Optional
from .utils import (
    Word, 
    CaptionLine,
    hex_to_ass_color,
    seconds_to_ass_time,
    alignment_to_ass,
    calculate_font_bold,
    calculate_margin_v,
)
from .themes import Theme, AnimationStyle
from .animations import get_animation


class ASSBuilder:
    """
    Builder for creating ASS subtitle files.
    
    Usage:
        builder = ASSBuilder(width=1920, height=1080)
        builder.add_style(theme)
        builder.add_dialogue(lines)
        ass_content = builder.build()
    """
    
    def __init__(self, width: int = 1920, height: int = 1080, title: str = "CaptionMagic"):
        self.width = width
        self.height = height
        self.title = title
        self.styles = []
        self.dialogues = []
    
    def build_header(self) -> str:
        """Generate the [Script Info] section."""
        return f"""[Script Info]
Title: {self.title}
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.601
PlayResX: {self.width}
PlayResY: {self.height}
"""
    
    def build_style(self, theme: Theme, style_name: str = "Default") -> str:
        """
        Generate a V4+ Style line from a theme.
        
        Style format:
        Style: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, 
               OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut,
               ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow,
               Alignment, MarginL, MarginR, MarginV, Encoding
        """
        # Colors in ASS format
        primary_color = hex_to_ass_color(theme.text_color)  # Main text color
        secondary_color = hex_to_ass_color(theme.highlight_color)  # Karaoke highlight
        outline_color = hex_to_ass_color(theme.outline_color)
        shadow_color = hex_to_ass_color(theme.shadow_color)
        
        # Font properties
        bold = -1 if calculate_font_bold(theme.font_weight) else 0
        italic = 0
        underline = 0
        strikeout = 0
        
        # Scale
        scale_x = 100
        scale_y = 100
        
        # Spacing
        spacing = theme.letter_spacing
        angle = 0
        
        # Border style: 1 = outline + shadow, 3 = opaque box
        border_style = 1
        outline = theme.outline_width
        shadow = theme.shadow_offset
        
        # Alignment (numpad style)
        alignment = alignment_to_ass(theme.alignment.value, theme.position_y)
        
        # Margins
        margin_l = 20
        margin_r = 20
        margin_v = calculate_margin_v(theme.position_y, self.height)
        
        # Encoding (0 = ANSI)
        encoding = 1
        
        return (
            f"Style: {style_name},{theme.font_family},{theme.font_size},"
            f"{primary_color},{secondary_color},{outline_color},{shadow_color},"
            f"{bold},{italic},{underline},{strikeout},"
            f"{scale_x},{scale_y},{spacing},{angle},"
            f"{border_style},{outline},{shadow},"
            f"{alignment},{margin_l},{margin_r},{margin_v},{encoding}"
        )
    
    def build_styles_section(self) -> str:
        """Generate the [V4+ Styles] section."""
        header = """
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding"""
        
        styles = "\n".join(self.styles)
        return f"{header}\n{styles}"
    
    def add_style(self, theme: Theme, style_name: str = "Default"):
        """Add a style definition."""
        style_line = self.build_style(theme, style_name)
        self.styles.append(style_line)
    
    def build_dialogue_line(
        self,
        text: str,
        start: float,
        end: float,
        style: str = "Default",
        layer: int = 0,
        margin_l: int = 0,
        margin_r: int = 0,
        margin_v: int = 0,
        effect: str = ""
    ) -> str:
        """
        Generate a single Dialogue line.
        
        Format:
        Dialogue: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
        """
        start_time = seconds_to_ass_time(start)
        end_time = seconds_to_ass_time(end)
        
        return (
            f"Dialogue: {layer},{start_time},{end_time},{style},,"
            f"{margin_l},{margin_r},{margin_v},{effect},{text}"
        )
    
    def add_dialogue(
        self,
        text: str,
        start: float,
        end: float,
        style: str = "Default",
        **kwargs
    ):
        """Add a dialogue line."""
        line = self.build_dialogue_line(text, start, end, style, **kwargs)
        self.dialogues.append(line)
    
    def build_events_section(self) -> str:
        """Generate the [Events] section."""
        header = """
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"""
        
        dialogues = "\n".join(self.dialogues)
        return f"{header}\n{dialogues}"
    
    def build(self) -> str:
        """
        Build the complete ASS file content.
        
        Returns:
            Complete ASS file as string
        """
        parts = [
            self.build_header(),
            self.build_styles_section(),
            self.build_events_section(),
        ]
        return "\n".join(parts)
    
    def save(self, filepath: str):
        """Save ASS content to file."""
        content = self.build()
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)


def create_ass_from_lines(
    lines: List[CaptionLine],
    theme: Theme,
    video_width: int = 1920,
    video_height: int = 1080
) -> str:
    """
    Create ASS content from caption lines.
    
    Args:
        lines: List of CaptionLine objects
        theme: Theme to apply
        video_width: Video width in pixels
        video_height: Video height in pixels
    
    Returns:
        Complete ASS file content as string
    """
    builder = ASSBuilder(width=video_width, height=video_height)
    
    # Add the main style
    builder.add_style(theme, "Default")
    
    # Get the animation function
    animation_func = get_animation(theme.animation_style)
    
    # Add dialogue for each line
    for line in lines:
        # Apply animation to get formatted text
        animated_text = animation_func(line.words, theme)
        
        # Add dialogue
        builder.add_dialogue(
            text=animated_text,
            start=line.start,
            end=line.end,
            style="Default"
        )
    
    return builder.build()


def create_simple_ass(
    words: List[dict],
    theme_name: str = "hormozi",
    video_width: int = 1920,
    video_height: int = 1080,
    words_per_line: int = None,
    max_chars_per_line: int = None
) -> str:
    """
    Simplified function to create ASS from word list.
    
    Args:
        words: List of word dicts with 'text', 'start', 'end' keys
        theme_name: Name of theme to use
        video_width: Video width
        video_height: Video height
        words_per_line: Override theme's words_per_line
        max_chars_per_line: Override theme's max_chars_per_line
    
    Returns:
        ASS file content
    """
    from .themes import get_theme
    from .utils import group_words_into_lines, Word
    
    # Get theme
    theme = get_theme(theme_name)
    
    # Override line settings if provided
    if words_per_line:
        theme.words_per_line = words_per_line
    if max_chars_per_line:
        theme.max_chars_per_line = max_chars_per_line
    
    # Convert dicts to Word objects
    word_objects = [
        Word(
            text=w['text'],
            start=w['start'],
            end=w['end'],
            confidence=w.get('confidence', 1.0)
        )
        for w in words
    ]
    
    # Group into lines
    lines = group_words_into_lines(
        word_objects,
        words_per_line=theme.words_per_line,
        max_chars_per_line=theme.max_chars_per_line
    )
    
    # Create ASS
    return create_ass_from_lines(lines, theme, video_width, video_height)
