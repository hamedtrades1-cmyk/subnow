"""
Whisper transcription service.
"""

import whisper
import tempfile
import os

# Load model once
model = None

def get_model():
    global model
    if model is None:
        print("Loading Whisper model...")
        model = whisper.load_model("base")
        print("Whisper model loaded!")
    return model

def transcribe_video(video_path: str, language: str = None) -> dict:
    """
    Transcribe video using Whisper.
    Returns word-level timestamps.
    """
    m = get_model()
    
    result = m.transcribe(
        video_path,
        language=language,
        word_timestamps=True,
        verbose=False
    )
    
    words = []
    for segment in result.get("segments", []):
        for word_info in segment.get("words", []):
            words.append({
                "text": word_info["word"].strip(),
                "start": round(word_info["start"], 3),
                "end": round(word_info["end"], 3),
                "confidence": round(word_info.get("probability", 1.0), 3)
            })
    
    return {
        "words": words,
        "full_text": result.get("text", "").strip(),
        "language": result.get("language", "en")
    }
