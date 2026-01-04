"""
Utility functions for caption generation.
"""

from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class Word:
    """A single word with timing information."""
    text: str
    start: float  # seconds
    end: float    # seconds
    confidence: float = 1.0
    
    @property
    def duration(self) -> float:
        """Duration in seconds."""
        return self.end - self.start
    
    @property
    def duration_cs(self) -> int:
        """Duration in centiseconds (for ASS \\k tags)."""
        return int(self.duration * 100)


@dataclass 
class CaptionLine:
    """A line of caption containing multiple words."""
    words: List[Word]
    
    @property
    def text(self) -> str:
        """Combined text of all words."""
        return " ".join(w.text for w in self.words)
    
    @property
    def start(self) -> float:
        """Start time of first word."""
        return self.words[0].start if self.words else 0
    
    @property
    def end(self) -> float:
        """End time of last word."""
        return self.words[-1].end if self.words else 0
    
    @property
    def duration(self) -> float:
        """Total duration."""
        return self.end - self.start


def hex_to_ass_color(hex_color: str) -> str:
    """
    Convert hex color to ASS color format.
    
    ASS uses BGR order with alpha: &HAABBGGRR
    For opaque colors: &H00BBGGRR
    
    Args:
        hex_color: Color in format '#RRGGBB' or '#RGB'
    
    Returns:
        ASS color string like '&H00FFFFFF'
    
    Examples:
        >>> hex_to_ass_color('#FFFFFF')
        '&H00FFFFFF'
        >>> hex_to_ass_color('#FF0000')  # Red
        '&H000000FF'
        >>> hex_to_ass_color('#00FF00')  # Green  
        '&H0000FF00'
    """
    # Remove # if present
    hex_color = hex_color.lstrip('#')
    
    # Handle shorthand (#RGB)
    if len(hex_color) == 3:
        hex_color = ''.join(c * 2 for c in hex_color)
    
    # Parse RGB values
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    
    # ASS uses BGR order
    return f"&H00{b:02X}{g:02X}{r:02X}"


def ass_color_to_hex(ass_color: str) -> str:
    """
    Convert ASS color back to hex format.
    
    Args:
        ass_color: Color in format '&HAABBGGRR' or '&H00BBGGRR'
    
    Returns:
        Hex color string like '#RRGGBB'
    """
    # Remove &H prefix
    color = ass_color.lstrip('&H').lstrip('&h')
    
    # Pad to 8 characters if needed
    color = color.zfill(8)
    
    # Extract BGR (skip alpha)
    b = int(color[2:4], 16)
    g = int(color[4:6], 16)
    r = int(color[6:8], 16)
    
    return f"#{r:02X}{g:02X}{b:02X}"


def seconds_to_ass_time(seconds: float) -> str:
    """
    Convert seconds to ASS timestamp format.
    
    Args:
        seconds: Time in seconds
    
    Returns:
        ASS timestamp string 'H:MM:SS.CC'
    
    Examples:
        >>> seconds_to_ass_time(0)
        '0:00:00.00'
        >>> seconds_to_ass_time(65.5)
        '0:01:05.50'
        >>> seconds_to_ass_time(3723.45)
        '1:02:03.45'
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centisecs = int((seconds % 1) * 100)
    
    return f"{hours}:{minutes:02d}:{secs:02d}.{centisecs:02d}"


def ass_time_to_seconds(ass_time: str) -> float:
    """
    Convert ASS timestamp to seconds.
    
    Args:
        ass_time: ASS timestamp 'H:MM:SS.CC'
    
    Returns:
        Time in seconds
    """
    parts = ass_time.split(':')
    hours = int(parts[0])
    minutes = int(parts[1])
    secs_cs = parts[2].split('.')
    secs = int(secs_cs[0])
    centisecs = int(secs_cs[1]) if len(secs_cs) > 1 else 0
    
    return hours * 3600 + minutes * 60 + secs + centisecs / 100


def alignment_to_ass(alignment: str, position_y: int) -> int:
    """
    Convert alignment and vertical position to ASS alignment number.
    
    ASS alignment is a numpad-style grid:
    7 8 9  (top)
    4 5 6  (middle)
    1 2 3  (bottom)
    
    Args:
        alignment: 'left', 'center', or 'right'
        position_y: Vertical position percentage (0=top, 100=bottom)
    
    Returns:
        ASS alignment number (1-9)
    """
    # Determine vertical position
    if position_y < 33:
        v_offset = 6  # Top row (7, 8, 9)
    elif position_y < 66:
        v_offset = 3  # Middle row (4, 5, 6)
    else:
        v_offset = 0  # Bottom row (1, 2, 3)
    
    # Determine horizontal alignment
    if alignment == 'left':
        h_base = 1
    elif alignment == 'right':
        h_base = 3
    else:  # center
        h_base = 2
    
    return v_offset + h_base


def position_to_pixels(
    position_x: int, 
    position_y: int, 
    video_width: int, 
    video_height: int
) -> Tuple[int, int]:
    """
    Convert percentage position to pixel coordinates.
    
    Args:
        position_x: Horizontal position (0-100)
        position_y: Vertical position (0-100)
        video_width: Video width in pixels
        video_height: Video height in pixels
    
    Returns:
        Tuple of (x_pixels, y_pixels)
    """
    x = int(video_width * position_x / 100)
    y = int(video_height * position_y / 100)
    return x, y


def escape_ass_text(text: str) -> str:
    """
    Escape special characters for ASS format.
    
    Args:
        text: Raw text
    
    Returns:
        Escaped text safe for ASS
    """
    # ASS special characters
    text = text.replace('\\', '\\\\')
    text = text.replace('{', '\\{')
    text = text.replace('}', '\\}')
    text = text.replace('\n', '\\N')
    return text


def group_words_into_lines(
    words: List[Word],
    words_per_line: int = 3,
    max_chars_per_line: int = 30
) -> List[CaptionLine]:
    """
    Group words into display lines.
    
    Uses both word count and character limits to create natural line breaks.
    
    Args:
        words: List of Word objects with timing
        words_per_line: Target words per line
        max_chars_per_line: Maximum characters per line
    
    Returns:
        List of CaptionLine objects
    """
    if not words:
        return []
    
    lines = []
    current_words = []
    current_chars = 0
    
    for word in words:
        word_len = len(word.text)
        
        # Check if adding this word would exceed limits
        would_exceed_words = len(current_words) >= words_per_line
        would_exceed_chars = current_chars + word_len + 1 > max_chars_per_line  # +1 for space
        
        # Start new line if limits exceeded (and we have words)
        if current_words and (would_exceed_words or would_exceed_chars):
            lines.append(CaptionLine(words=current_words))
            current_words = []
            current_chars = 0
        
        # Add word to current line
        current_words.append(word)
        current_chars += word_len + 1  # +1 for space
    
    # Don't forget last line
    if current_words:
        lines.append(CaptionLine(words=current_words))
    
    return lines


def calculate_font_bold(weight: int) -> bool:
    """Determine if font weight should render as bold."""
    return weight >= 700


def calculate_margin_v(position_y: int, video_height: int) -> int:
    """
    Calculate vertical margin for ASS positioning.
    
    For bottom-aligned text, margin is from bottom.
    For top-aligned text, margin is from top.
    """
    if position_y > 50:
        # Bottom half - margin from bottom
        return int(video_height * (100 - position_y) / 100)
    else:
        # Top half - margin from top
        return int(video_height * position_y / 100)
