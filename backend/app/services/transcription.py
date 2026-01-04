"""
Transcription Service - Whisper Integration for CaptionMagic
Stream 2: Handles audio extraction and speech-to-text with word-level timestamps
"""

import os
import subprocess
import tempfile
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
from enum import Enum

import whisper
import torch

logger = logging.getLogger(__name__)


class WhisperModel(str, Enum):
    """Available Whisper model sizes - larger = more accurate but slower"""
    TINY = "tiny"
    BASE = "base"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    LARGE_V2 = "large-v2"
    LARGE_V3 = "large-v3"


@dataclass
class Word:
    """Single word with timestamp data"""
    text: str
    start: float  # seconds
    end: float    # seconds
    confidence: float
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TranscriptSegment:
    """A segment/sentence of transcription"""
    id: int
    text: str
    start: float
    end: float
    words: List[Word]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text,
            "start": self.start,
            "end": self.end,
            "words": [w.to_dict() for w in self.words]
        }


@dataclass
class TranscriptionResult:
    """Complete transcription result"""
    language: str
    language_probability: float
    duration: float
    full_text: str
    words: List[Word]
    segments: List[TranscriptSegment]
    model_used: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "language": self.language,
            "language_probability": self.language_probability,
            "duration": self.duration,
            "full_text": self.full_text,
            "words": [w.to_dict() for w in self.words],
            "segments": [s.to_dict() for s in self.segments],
            "model_used": self.model_used
        }


class TranscriptionService:
    """
    Main transcription service using OpenAI Whisper.
    Extracts audio from video and generates word-level timestamps.
    """
    
    # Model cache to avoid reloading
    _model_cache: Dict[str, whisper.Whisper] = {}
    
    def __init__(
        self,
        model_name: str = "base",
        device: Optional[str] = None,
        ffmpeg_path: str = "ffmpeg"
    ):
        """
        Initialize transcription service.
        
        Args:
            model_name: Whisper model size (tiny, base, small, medium, large)
            device: 'cuda' or 'cpu'. Auto-detects if None.
            ffmpeg_path: Path to ffmpeg binary
        """
        self.model_name = model_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.ffmpeg_path = ffmpeg_path
        self._model: Optional[whisper.Whisper] = None
        
        logger.info(f"TranscriptionService initialized: model={model_name}, device={self.device}")
    
    @property
    def model(self) -> whisper.Whisper:
        """Lazy-load and cache the Whisper model"""
        if self._model is None:
            cache_key = f"{self.model_name}_{self.device}"
            
            if cache_key not in self._model_cache:
                logger.info(f"Loading Whisper model: {self.model_name} on {self.device}")
                self._model_cache[cache_key] = whisper.load_model(
                    self.model_name, 
                    device=self.device
                )
            
            self._model = self._model_cache[cache_key]
        
        return self._model
    
    def extract_audio(
        self, 
        video_path: str, 
        output_path: Optional[str] = None,
        sample_rate: int = 16000
    ) -> str:
        """
        Extract audio from video file using FFmpeg.
        
        Args:
            video_path: Path to input video
            output_path: Path for output audio (creates temp file if None)
            sample_rate: Audio sample rate (16kHz default for Whisper)
            
        Returns:
            Path to extracted audio file
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # Create output path if not provided
        if output_path is None:
            suffix = ".wav"
            fd, output_path = tempfile.mkstemp(suffix=suffix)
            os.close(fd)
        
        # FFmpeg command to extract audio
        cmd = [
            self.ffmpeg_path,
            "-i", video_path,
            "-vn",                    # No video
            "-acodec", "pcm_s16le",   # PCM 16-bit
            "-ar", str(sample_rate),  # Sample rate
            "-ac", "1",               # Mono
            "-y",                     # Overwrite output
            output_path
        ]
        
        logger.info(f"Extracting audio from {video_path}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg error: {e.stderr}")
            raise RuntimeError(f"Failed to extract audio: {e.stderr}")
        
        logger.info(f"Audio extracted to {output_path}")
        return output_path
    
    def get_audio_duration(self, audio_path: str) -> float:
        """Get duration of audio file in seconds"""
        cmd = [
            self.ffmpeg_path.replace("ffmpeg", "ffprobe"),
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            audio_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return float(result.stdout.strip())
        except (subprocess.CalledProcessError, ValueError):
            return 0.0
    
    def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
        initial_prompt: Optional[str] = None,
        temperature: float = 0.0,
        compression_ratio_threshold: float = 2.4,
        no_speech_threshold: float = 0.6,
        condition_on_previous_text: bool = True
    ) -> TranscriptionResult:
        """
        Transcribe audio file with word-level timestamps.
        
        Args:
            audio_path: Path to audio file (WAV, MP3, etc.)
            language: Language code (e.g., 'en', 'es'). Auto-detects if None.
            initial_prompt: Optional prompt to guide transcription style/vocabulary
            temperature: Sampling temperature. 0 = deterministic.
            compression_ratio_threshold: Skip segments with high compression ratio
            no_speech_threshold: Skip segments with low speech probability
            condition_on_previous_text: Use previous output as context
            
        Returns:
            TranscriptionResult with words, segments, and metadata
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        logger.info(f"Starting transcription: {audio_path} (language={language or 'auto'})")
        
        # Get duration for progress tracking
        duration = self.get_audio_duration(audio_path)
        
        # Run Whisper transcription
        result = self.model.transcribe(
            audio_path,
            language=language,
            word_timestamps=True,
            initial_prompt=initial_prompt,
            temperature=temperature,
            compression_ratio_threshold=compression_ratio_threshold,
            no_speech_threshold=no_speech_threshold,
            condition_on_previous_text=condition_on_previous_text,
            verbose=False
        )
        
        # Extract all words from segments
        all_words: List[Word] = []
        segments: List[TranscriptSegment] = []
        
        for seg_idx, segment in enumerate(result.get("segments", [])):
            segment_words: List[Word] = []
            
            for word_data in segment.get("words", []):
                word = Word(
                    text=word_data["word"].strip(),
                    start=round(word_data["start"], 3),
                    end=round(word_data["end"], 3),
                    confidence=round(word_data.get("probability", 1.0), 4)
                )
                segment_words.append(word)
                all_words.append(word)
            
            # Create segment
            segments.append(TranscriptSegment(
                id=seg_idx,
                text=segment.get("text", "").strip(),
                start=round(segment.get("start", 0), 3),
                end=round(segment.get("end", 0), 3),
                words=segment_words
            ))
        
        # Build result
        transcription = TranscriptionResult(
            language=result.get("language", "en"),
            language_probability=round(
                result.get("language_probability", 1.0) 
                if "language_probability" in result else 1.0, 
                4
            ),
            duration=duration,
            full_text=result.get("text", "").strip(),
            words=all_words,
            segments=segments,
            model_used=self.model_name
        )
        
        logger.info(
            f"Transcription complete: {len(all_words)} words, "
            f"{len(segments)} segments, language={transcription.language}"
        )
        
        return transcription
    
    def transcribe_video(
        self,
        video_path: str,
        language: Optional[str] = None,
        initial_prompt: Optional[str] = None,
        cleanup_audio: bool = True,
        **kwargs
    ) -> TranscriptionResult:
        """
        Transcribe video file (extracts audio first).
        
        Args:
            video_path: Path to video file
            language: Language code or None for auto-detect
            initial_prompt: Optional prompt for transcription context
            cleanup_audio: Delete temporary audio file after transcription
            **kwargs: Additional arguments passed to transcribe()
            
        Returns:
            TranscriptionResult with full transcription data
        """
        audio_path = None
        
        try:
            # Extract audio
            audio_path = self.extract_audio(video_path)
            
            # Transcribe
            result = self.transcribe(
                audio_path=audio_path,
                language=language,
                initial_prompt=initial_prompt,
                **kwargs
            )
            
            return result
            
        finally:
            # Cleanup temp audio
            if cleanup_audio and audio_path and os.path.exists(audio_path):
                try:
                    os.remove(audio_path)
                    logger.debug(f"Cleaned up temp audio: {audio_path}")
                except OSError:
                    pass


# Singleton instance for convenience
_default_service: Optional[TranscriptionService] = None


def get_transcription_service(
    model_name: Optional[str] = None,
    device: Optional[str] = None
) -> TranscriptionService:
    """Get or create the default transcription service"""
    global _default_service
    
    # Get from environment if not provided
    model_name = model_name or os.getenv("WHISPER_MODEL", "base")
    device = device or os.getenv("WHISPER_DEVICE")
    
    if _default_service is None or _default_service.model_name != model_name:
        _default_service = TranscriptionService(
            model_name=model_name,
            device=device
        )
    
    return _default_service


def transcribe_video(
    video_path: str,
    language: Optional[str] = None,
    model_name: Optional[str] = None,
    initial_prompt: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function matching the integration interface.
    
    Args:
        video_path: Path to video file
        language: Language code or None for auto-detect
        model_name: Override default model
        initial_prompt: Context prompt for domain-specific vocabulary
        
    Returns:
        Dict with language, words list, and full_text
        
    Example:
        result = transcribe_video("/path/to/video.mp4", language="en")
        # Returns: {
        #     "language": "en",
        #     "words": [{"text": "Hello", "start": 0.0, "end": 0.5, "confidence": 0.98}, ...],
        #     "full_text": "Hello world...",
        #     "segments": [...],
        #     "duration": 120.5,
        #     "model_used": "base"
        # }
    """
    service = get_transcription_service(model_name=model_name)
    result = service.transcribe_video(
        video_path=video_path,
        language=language,
        initial_prompt=initial_prompt
    )
    return result.to_dict()


# Domain-specific prompts for better accuracy
DOMAIN_PROMPTS = {
    "trading": (
        "Stock trading, futures trading, NQ, MNQ, ES, SPY, scalping, "
        "support, resistance, breakout, momentum, volume, candlestick, "
        "MACD, RSI, moving average, stop loss, take profit, entry, exit"
    ),
    "tech": (
        "Technology, software, programming, API, database, cloud computing, "
        "machine learning, artificial intelligence, deployment, debugging"
    ),
    "fitness": (
        "Fitness, workout, exercise, reps, sets, protein, calories, "
        "muscle, cardio, strength training, hypertrophy, progressive overload"
    ),
    "general": None
}


def get_domain_prompt(domain: str) -> Optional[str]:
    """Get initial prompt for specific content domain"""
    return DOMAIN_PROMPTS.get(domain.lower())
