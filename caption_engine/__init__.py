"""
CaptionMagic Caption Engine

Generates animated ASS subtitles from word-level transcripts.
"""

from .generator import generate_ass
from .themes import DEFAULT_THEMES, Theme

__all__ = ['generate_ass', 'DEFAULT_THEMES', 'Theme']
__version__ = '0.1.0'
