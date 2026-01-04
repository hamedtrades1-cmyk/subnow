"""
Main caption generator - the primary interface for the caption engine.

This module provides the high-level API for generating captions.
"""

from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass

from .themes import Theme, get_theme, DEFAULT_THEMES, AnimationStyle
from .utils import Word, CaptionLine, group_words_into_lines
from .ass_builder import ASSBuilder, create_ass_from_lines


@dataclass
class GeneratorConfig:
    """Configuration for caption generation."""
    video_width: int = 1920
    video_height: int = 1080
    
    # Override theme settings
    words_per_line: Optional[int] = None
    max_chars_per_line: Optional[int] = None
    animation_style: Optional[AnimationStyle] = None
    position_y: Optional[int] = None
    
    # Additional options
    add_padding: float = 0.1  # Extra time at start/end of lines (seconds)


def generate_ass(
    words: Union[List[Word], List[Dict[str, Any]]],
    theme: Union[Theme, str, Dict[str, Any]],
    video_width: int = 1920,
    video_height: int = 1080,
    config: Optional[GeneratorConfig] = None
) -> str:
    """
    Generate ASS subtitle content from words and theme.
    
    This is the main entry point for caption generation.
    
    Args:
        words: List of Word objects or dicts with 'text', 'start', 'end' keys
        theme: Theme object, theme name string, or theme dict
        video_width: Video width in pixels
        video_height: Video height in pixels
        config: Optional GeneratorConfig for additional settings
    
    Returns:
        Complete ASS file content as string
    
    Example:
        >>> words = [
        ...     {"text": "Hello", "start": 0.0, "end": 0.5},
        ...     {"text": "world", "start": 0.5, "end": 1.0},
        ... ]
        >>> ass = generate_ass(words, "hormozi")
        >>> print(ass)
    """
    config = config or GeneratorConfig(
        video_width=video_width,
        video_height=video_height
    )
    
    # Resolve theme
    resolved_theme = _resolve_theme(theme)
    
    # Apply config overrides
    resolved_theme = _apply_config_overrides(resolved_theme, config)
    
    # Convert words to Word objects
    word_objects = _normalize_words(words)
    
    # Group words into lines
    lines = group_words_into_lines(
        word_objects,
        words_per_line=resolved_theme.words_per_line,
        max_chars_per_line=resolved_theme.max_chars_per_line
    )
    
    # Apply padding if configured
    if config.add_padding > 0:
        lines = _add_line_padding(lines, config.add_padding)
    
    # Generate ASS
    return create_ass_from_lines(
        lines,
        resolved_theme,
        config.video_width,
        config.video_height
    )


def generate_ass_file(
    words: Union[List[Word], List[Dict[str, Any]]],
    theme: Union[Theme, str, Dict[str, Any]],
    output_path: str,
    video_width: int = 1920,
    video_height: int = 1080,
    config: Optional[GeneratorConfig] = None
) -> str:
    """
    Generate ASS file and save to disk.
    
    Args:
        words: List of words with timing
        theme: Theme to apply
        output_path: Path to save ASS file
        video_width: Video width
        video_height: Video height
        config: Optional configuration
    
    Returns:
        Path to saved file
    """
    ass_content = generate_ass(
        words, theme, video_width, video_height, config
    )
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(ass_content)
    
    return output_path


def preview_theme(
    theme: Union[Theme, str],
    sample_text: str = "This is a sample caption",
    duration: float = 3.0,
    video_width: int = 1920,
    video_height: int = 1080
) -> str:
    """
    Generate a preview ASS for a theme with sample text.
    
    Useful for showing theme previews in the UI.
    
    Args:
        theme: Theme to preview
        sample_text: Text to display
        duration: How long to display
        video_width: Video width
        video_height: Video height
    
    Returns:
        ASS content
    """
    # Split sample text into words with even timing
    words_text = sample_text.split()
    word_duration = duration / len(words_text)
    
    words = []
    current_time = 0
    for word in words_text:
        words.append({
            "text": word,
            "start": current_time,
            "end": current_time + word_duration
        })
        current_time += word_duration
    
    return generate_ass(words, theme, video_width, video_height)


def _resolve_theme(theme: Union[Theme, str, Dict[str, Any]]) -> Theme:
    """Resolve theme from various input types."""
    if isinstance(theme, Theme):
        return theme
    elif isinstance(theme, str):
        return get_theme(theme)
    elif isinstance(theme, dict):
        return Theme.from_dict(theme)
    else:
        raise TypeError(f"Invalid theme type: {type(theme)}")


def _normalize_words(words: Union[List[Word], List[Dict[str, Any]]]) -> List[Word]:
    """Convert word dicts to Word objects."""
    normalized = []
    for w in words:
        if isinstance(w, Word):
            normalized.append(w)
        elif isinstance(w, dict):
            normalized.append(Word(
                text=w['text'],
                start=w['start'],
                end=w['end'],
                confidence=w.get('confidence', 1.0)
            ))
        else:
            raise TypeError(f"Invalid word type: {type(w)}")
    return normalized


def _apply_config_overrides(theme: Theme, config: GeneratorConfig) -> Theme:
    """Apply configuration overrides to theme."""
    # Create a copy to avoid modifying original
    import copy
    theme = copy.deepcopy(theme)
    
    if config.words_per_line is not None:
        theme.words_per_line = config.words_per_line
    if config.max_chars_per_line is not None:
        theme.max_chars_per_line = config.max_chars_per_line
    if config.animation_style is not None:
        theme.animation_style = config.animation_style
    if config.position_y is not None:
        theme.position_y = config.position_y
    
    return theme


def _add_line_padding(lines: List[CaptionLine], padding: float) -> List[CaptionLine]:
    """Add time padding to lines to prevent abrupt cuts."""
    padded = []
    for i, line in enumerate(lines):
        # Create new words with padded timing
        new_words = []
        for j, word in enumerate(line.words):
            new_word = Word(
                text=word.text,
                start=word.start - padding if j == 0 else word.start,
                end=word.end + padding if j == len(line.words) - 1 else word.end,
                confidence=word.confidence
            )
            # Ensure start isn't negative
            new_word.start = max(0, new_word.start)
            new_words.append(new_word)
        
        padded.append(CaptionLine(words=new_words))
    
    return padded


# =============================================================================
# BATCH PROCESSING
# =============================================================================

def generate_all_theme_previews(
    sample_text: str = "This is how your captions will look",
    duration: float = 3.0,
    video_width: int = 1920,
    video_height: int = 1080
) -> Dict[str, str]:
    """
    Generate preview ASS for all default themes.
    
    Returns:
        Dict mapping theme name to ASS content
    """
    previews = {}
    for name, theme in DEFAULT_THEMES.items():
        previews[name] = preview_theme(
            theme, sample_text, duration, video_width, video_height
        )
    return previews


# =============================================================================
# VALIDATION
# =============================================================================

def validate_words(words: List[Dict[str, Any]]) -> List[str]:
    """
    Validate word list for required fields and timing consistency.
    
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    if not words:
        errors.append("Word list is empty")
        return errors
    
    required_fields = ['text', 'start', 'end']
    prev_end = 0
    
    for i, word in enumerate(words):
        # Check required fields
        for field in required_fields:
            if field not in word:
                errors.append(f"Word {i}: missing required field '{field}'")
        
        if 'start' in word and 'end' in word:
            # Check timing validity
            if word['start'] < 0:
                errors.append(f"Word {i}: start time is negative")
            if word['end'] < word['start']:
                errors.append(f"Word {i}: end time before start time")
            
            # Check ordering (words should be sequential)
            if word['start'] < prev_end - 0.1:  # Allow small overlap
                errors.append(f"Word {i}: overlaps with previous word")
            
            prev_end = word['end']
    
    return errors


def validate_theme(theme: Dict[str, Any]) -> List[str]:
    """
    Validate theme configuration.
    
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    # Required fields
    if 'name' not in theme:
        errors.append("Theme must have a name")
    
    # Validate colors
    color_fields = ['text_color', 'highlight_color', 'outline_color', 'shadow_color']
    for field in color_fields:
        if field in theme:
            color = theme[field]
            if not color.startswith('#') or len(color) not in [4, 7]:
                errors.append(f"Invalid color format for {field}: {color}")
    
    # Validate ranges
    if 'font_size' in theme:
        if not (10 <= theme['font_size'] <= 200):
            errors.append("font_size should be between 10 and 200")
    
    if 'position_y' in theme:
        if not (0 <= theme['position_y'] <= 100):
            errors.append("position_y should be between 0 and 100")
    
    if 'words_per_line' in theme:
        if not (1 <= theme['words_per_line'] <= 10):
            errors.append("words_per_line should be between 1 and 10")
    
    return errors
