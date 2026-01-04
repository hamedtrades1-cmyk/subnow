"""
Animation effects for ASS captions.

Each animation function takes words and returns ASS-formatted text with animation tags.
"""

from typing import List
from .utils import Word, escape_ass_text, hex_to_ass_color


def no_animation(words: List[Word], theme) -> str:
    """
    No animation - just display text.
    
    Returns plain text without any animation effects.
    """
    text = " ".join(escape_ass_text(w.text) for w in words)
    if theme.uppercase:
        text = text.upper()
    return text


def karaoke_animation(words: List[Word], theme) -> str:
    """
    Karaoke-style word-by-word highlight.
    
    Uses ASS \\k tag to progressively highlight words.
    The highlight color shows which word is currently being spoken.
    
    Format: {\\k<duration>}word
    Duration is in centiseconds (1/100th of a second).
    """
    parts = []
    highlight_color = hex_to_ass_color(theme.highlight_color)
    
    for i, word in enumerate(words):
        text = escape_ass_text(word.text)
        if theme.uppercase:
            text = text.upper()
        
        # Calculate duration in centiseconds
        duration_cs = word.duration_cs
        
        # Use \kf for smooth fill (karaoke fill)
        # \k = instant switch, \kf = smooth fill, \ko = outline fill
        parts.append(f"{{\\kf{duration_cs}}}{text}")
    
    return " ".join(parts)


def karaoke_word_highlight(words: List[Word], theme) -> str:
    """
    Alternative karaoke that changes word color completely.
    
    Each word starts in text_color and changes to highlight_color when spoken.
    """
    parts = []
    text_color = hex_to_ass_color(theme.text_color)
    highlight_color = hex_to_ass_color(theme.highlight_color)
    
    for word in words:
        text = escape_ass_text(word.text)
        if theme.uppercase:
            text = text.upper()
        
        duration_cs = word.duration_cs
        
        # Use \k for instant color switch
        parts.append(f"{{\\k{duration_cs}}}{text}")
    
    return " ".join(parts)


def bounce_animation(words: List[Word], theme) -> str:
    """
    Words bounce in from below.
    
    Each word moves up and slightly overshoots, then settles.
    Uses \\move and \\t (transform) tags.
    """
    parts = []
    
    for i, word in enumerate(words):
        text = escape_ass_text(word.text)
        if theme.uppercase:
            text = text.upper()
        
        # Stagger the bounce for each word
        delay = i * 50  # 50ms between each word
        bounce_duration = 200  # bounce takes 200ms
        
        # Animation: start 30 pixels below, bounce up 10 pixels above target, settle
        # \move(x1,y1,x2,y2,t1,t2) - move from (x1,y1) to (x2,y2) between t1 and t2 ms
        # We'll use \t (transform) for the bounce effect instead
        
        # Scale bounce: start at 80%, go to 110%, settle at 100%
        parts.append(
            f"{{\\fscx80\\fscy80"
            f"\\t({delay},{delay + bounce_duration},\\fscx110\\fscy110)"
            f"\\t({delay + bounce_duration},{delay + bounce_duration + 100},\\fscx100\\fscy100)}}"
            f"{text}"
        )
    
    return " ".join(parts)


def pop_animation(words: List[Word], theme) -> str:
    """
    Words pop/scale in one at a time.
    
    Each word scales from 0% to 110% then settles at 100%.
    Creates a punchy, energetic feel.
    """
    parts = []
    
    for i, word in enumerate(words):
        text = escape_ass_text(word.text)
        if theme.uppercase:
            text = text.upper()
        
        # Calculate when this word should pop based on timing
        # We'll approximate based on word order
        word_start_ms = int(word.start * 1000) if hasattr(word, 'start') else i * 200
        
        # Pop animation: 0% -> 120% -> 100%
        pop_duration = 150
        settle_duration = 100
        
        parts.append(
            f"{{\\fscx0\\fscy0"
            f"\\t({word_start_ms},{word_start_ms + pop_duration},\\fscx120\\fscy120)"
            f"\\t({word_start_ms + pop_duration},{word_start_ms + pop_duration + settle_duration},\\fscx100\\fscy100)}}"
            f"{text}"
        )
    
    return " ".join(parts)


def pop_sequential(words: List[Word], theme) -> str:
    """
    Simplified pop animation where words appear sequentially.
    
    Each word pops in when it's spoken.
    """
    parts = []
    
    # Get the line start time (first word start)
    line_start = words[0].start if words else 0
    
    for i, word in enumerate(words):
        text = escape_ass_text(word.text)
        if theme.uppercase:
            text = text.upper()
        
        # Time relative to line start (in milliseconds)
        relative_start_ms = int((word.start - line_start) * 1000)
        
        # Pop animation timing
        pop_up = 100  # ms to scale up
        settle = 80   # ms to settle
        
        parts.append(
            f"{{\\fscx0\\fscy0"
            f"\\t(0,{relative_start_ms},\\fscx0\\fscy0)"  # Stay invisible until word time
            f"\\t({relative_start_ms},{relative_start_ms + pop_up},\\fscx115\\fscy115)"  # Pop up
            f"\\t({relative_start_ms + pop_up},{relative_start_ms + pop_up + settle},\\fscx100\\fscy100)}}"  # Settle
            f"{text}"
        )
    
    return " ".join(parts)


def glow_animation(words: List[Word], theme) -> str:
    """
    Words glow/pulse effect.
    
    Uses blur and color transitions to create a glowing effect.
    """
    parts = []
    highlight_color = hex_to_ass_color(theme.highlight_color)
    text_color = hex_to_ass_color(theme.text_color)
    
    for i, word in enumerate(words):
        text = escape_ass_text(word.text)
        if theme.uppercase:
            text = text.upper()
        
        # Pulse timing
        pulse_in = 150
        pulse_out = 150
        delay = i * 100
        
        # Glow effect: increase border/blur, change color, then revert
        parts.append(
            f"{{\\blur0\\bord{theme.outline_width}"
            f"\\t({delay},{delay + pulse_in},\\blur3\\bord{theme.outline_width + 2}\\c{highlight_color})"
            f"\\t({delay + pulse_in},{delay + pulse_in + pulse_out},\\blur0\\bord{theme.outline_width}\\c{text_color})}}"
            f"{text}"
        )
    
    return " ".join(parts)


def wave_animation(words: List[Word], theme) -> str:
    """
    Words wave up and down in sequence.
    
    Creates a wave motion across the text.
    """
    parts = []
    
    for i, word in enumerate(words):
        text = escape_ass_text(word.text)
        if theme.uppercase:
            text = text.upper()
        
        # Wave timing - offset for each word to create wave
        wave_offset = i * 100  # ms offset between words
        wave_up = 200
        wave_down = 200
        
        # Use \frz (rotation) for a subtle wave, or \fry for 3D-ish effect
        # Or use position offset with \pos override - but that's complex
        # Let's use scale for a simpler wave effect
        parts.append(
            f"{{\\fscy100"
            f"\\t({wave_offset},{wave_offset + wave_up},\\fscy110)"
            f"\\t({wave_offset + wave_up},{wave_offset + wave_up + wave_down},\\fscy100)}}"
            f"{text}"
        )
    
    return " ".join(parts)


def typewriter_animation(words: List[Word], theme) -> str:
    """
    Words appear one at a time like a typewriter.
    
    Each word fades/appears when it's spoken.
    """
    parts = []
    line_start = words[0].start if words else 0
    
    for word in words:
        text = escape_ass_text(word.text)
        if theme.uppercase:
            text = text.upper()
        
        # Time relative to line start
        relative_start_ms = int((word.start - line_start) * 1000)
        fade_duration = 50  # Very quick fade in
        
        # Alpha: FF = invisible, 00 = visible
        parts.append(
            f"{{\\alpha&HFF"
            f"\\t(0,{relative_start_ms},\\alpha&HFF)"  # Stay invisible
            f"\\t({relative_start_ms},{relative_start_ms + fade_duration},\\alpha&H00)}}"  # Fade in
            f"{text}"
        )
    
    return " ".join(parts)


# =============================================================================
# ANIMATION REGISTRY
# =============================================================================

ANIMATIONS = {
    "none": no_animation,
    "karaoke": karaoke_animation,
    "bounce": bounce_animation,
    "pop": pop_sequential,
    "glow": glow_animation,
    "wave": wave_animation,
    "typewriter": typewriter_animation,
}


def get_animation(style: str):
    """
    Get animation function by style name.
    
    Args:
        style: Animation style name
    
    Returns:
        Animation function
    
    Raises:
        ValueError: If style not found
    """
    style_lower = style.lower() if isinstance(style, str) else style.value
    if style_lower in ANIMATIONS:
        return ANIMATIONS[style_lower]
    raise ValueError(f"Unknown animation style: {style}. Available: {list(ANIMATIONS.keys())}")


def list_animations() -> List[str]:
    """List all available animation styles."""
    return list(ANIMATIONS.keys())
