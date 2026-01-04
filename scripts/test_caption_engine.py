#!/usr/bin/env python3
"""
Test script for the CaptionMagic caption engine.

Run this to verify the caption engine is working correctly.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from caption_engine import generate_ass, DEFAULT_THEMES
from caption_engine.themes import get_theme, list_themes, Theme, AnimationStyle
from caption_engine.utils import hex_to_ass_color, seconds_to_ass_time, Word, group_words_into_lines
from caption_engine.animations import list_animations


def test_color_conversion():
    """Test hex to ASS color conversion."""
    print("\n=== Testing Color Conversion ===")
    
    test_cases = [
        ("#FFFFFF", "&H00FFFFFF"),  # White
        ("#000000", "&H00000000"),  # Black
        ("#FF0000", "&H000000FF"),  # Red (RGB to BGR)
        ("#00FF00", "&H0000FF00"),  # Green
        ("#0000FF", "&H00FF0000"),  # Blue
        ("#FFFF00", "&H0000FFFF"),  # Yellow
    ]
    
    for hex_color, expected in test_cases:
        result = hex_to_ass_color(hex_color)
        status = "✓" if result == expected else "✗"
        print(f"  {status} {hex_color} -> {result} (expected {expected})")


def test_time_conversion():
    """Test seconds to ASS time conversion."""
    print("\n=== Testing Time Conversion ===")
    
    test_cases = [
        (0, "0:00:00.00"),
        (1.5, "0:00:01.50"),
        (65.5, "0:01:05.50"),
        (3723.45, "1:02:03.45"),
    ]
    
    for seconds, expected in test_cases:
        result = seconds_to_ass_time(seconds)
        status = "✓" if result == expected else "✗"
        print(f"  {status} {seconds}s -> {result} (expected {expected})")


def test_word_grouping():
    """Test word grouping into lines."""
    print("\n=== Testing Word Grouping ===")
    
    words = [
        Word(text="Hello", start=0.0, end=0.5),
        Word(text="world", start=0.5, end=1.0),
        Word(text="this", start=1.0, end=1.3),
        Word(text="is", start=1.3, end=1.5),
        Word(text="a", start=1.5, end=1.6),
        Word(text="test", start=1.6, end=2.0),
        Word(text="of", start=2.0, end=2.2),
        Word(text="captions", start=2.2, end=3.0),
    ]
    
    lines = group_words_into_lines(words, words_per_line=3)
    
    print(f"  Input: {len(words)} words")
    print(f"  Output: {len(lines)} lines")
    for i, line in enumerate(lines):
        print(f"    Line {i+1}: \"{line.text}\" ({line.start:.2f}s - {line.end:.2f}s)")


def test_themes():
    """Test theme functionality."""
    print("\n=== Testing Themes ===")
    
    print(f"  Available themes: {list_themes()}")
    print(f"  Available animations: {list_animations()}")
    
    # Test getting a theme
    theme = get_theme("hormozi")
    print(f"\n  Hormozi theme:")
    print(f"    Font: {theme.font_family} {theme.font_size}px")
    print(f"    Colors: text={theme.text_color}, highlight={theme.highlight_color}")
    print(f"    Animation: {theme.animation_style.value}")


def test_ass_generation():
    """Test full ASS generation."""
    print("\n=== Testing ASS Generation ===")
    
    # Sample words (simulating Whisper output)
    words = [
        {"text": "Hello", "start": 0.0, "end": 0.4},
        {"text": "everyone", "start": 0.4, "end": 0.9},
        {"text": "welcome", "start": 1.0, "end": 1.4},
        {"text": "to", "start": 1.4, "end": 1.5},
        {"text": "the", "start": 1.5, "end": 1.6},
        {"text": "show", "start": 1.6, "end": 2.0},
        {"text": "today", "start": 2.1, "end": 2.5},
        {"text": "we", "start": 2.6, "end": 2.7},
        {"text": "are", "start": 2.7, "end": 2.8},
        {"text": "going", "start": 2.8, "end": 3.0},
        {"text": "to", "start": 3.0, "end": 3.1},
        {"text": "talk", "start": 3.1, "end": 3.4},
        {"text": "about", "start": 3.4, "end": 3.7},
        {"text": "something", "start": 3.8, "end": 4.2},
        {"text": "amazing", "start": 4.3, "end": 5.0},
    ]
    
    # Test with different themes
    themes_to_test = ["hormozi", "beast", "clean", "neon"]
    
    for theme_name in themes_to_test:
        print(f"\n  Generating with '{theme_name}' theme...")
        ass_content = generate_ass(words, theme_name, 1920, 1080)
        
        # Count lines
        dialogue_lines = [l for l in ass_content.split('\n') if l.startswith('Dialogue:')]
        print(f"    Generated {len(dialogue_lines)} dialogue lines")
        print(f"    Total size: {len(ass_content)} bytes")


def test_ass_output():
    """Test and display actual ASS output."""
    print("\n=== Sample ASS Output ===")
    
    words = [
        {"text": "This", "start": 0.0, "end": 0.3},
        {"text": "is", "start": 0.3, "end": 0.5},
        {"text": "a", "start": 0.5, "end": 0.6},
        {"text": "test", "start": 0.6, "end": 1.0},
    ]
    
    ass_content = generate_ass(words, "hormozi", 1920, 1080)
    
    # Print first part of output
    lines = ass_content.split('\n')
    print("\n  (First 30 lines)")
    for line in lines[:30]:
        print(f"  {line}")
    
    if len(lines) > 30:
        print(f"  ... ({len(lines) - 30} more lines)")


def test_save_file():
    """Test saving ASS to file."""
    print("\n=== Testing File Save ===")
    
    from caption_engine.generator import generate_ass_file
    
    words = [
        {"text": "Test", "start": 0.0, "end": 0.5},
        {"text": "caption", "start": 0.5, "end": 1.0},
        {"text": "file", "start": 1.0, "end": 1.5},
    ]
    
    output_path = "/tmp/test_captions.ass"
    generate_ass_file(words, "hormozi", output_path)
    
    if os.path.exists(output_path):
        size = os.path.getsize(output_path)
        print(f"  ✓ File saved: {output_path} ({size} bytes)")
    else:
        print(f"  ✗ File not created")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("CaptionMagic Caption Engine Tests")
    print("=" * 60)
    
    test_color_conversion()
    test_time_conversion()
    test_word_grouping()
    test_themes()
    test_ass_generation()
    test_ass_output()
    test_save_file()
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
