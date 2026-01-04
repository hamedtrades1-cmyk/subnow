"""
Video Rendering Service - FFmpeg Operations

Handles:
- Burning ASS subtitles into videos
- Video metadata extraction
- Thumbnail/preview generation
- Format conversion
- Progress tracking
"""

import os
import re
import json
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class RenderError(Exception):
    """Base exception for rendering errors"""
    pass


class FFmpegNotFoundError(RenderError):
    """FFmpeg binary not found"""
    pass


class InvalidVideoError(RenderError):
    """Invalid or corrupted video file"""
    pass


class RenderFailedError(RenderError):
    """Rendering process failed"""
    pass


class VideoCodec(str, Enum):
    H264 = "libx264"
    H265 = "libx265"
    VP9 = "libvpx-vp9"
    COPY = "copy"


class AudioCodec(str, Enum):
    AAC = "aac"
    MP3 = "libmp3lame"
    OPUS = "libopus"
    COPY = "copy"


class OutputPreset(str, Enum):
    """FFmpeg encoding presets - speed vs compression tradeoff"""
    ULTRAFAST = "ultrafast"
    SUPERFAST = "superfast"
    VERYFAST = "veryfast"
    FASTER = "faster"
    FAST = "fast"
    MEDIUM = "medium"
    SLOW = "slow"
    SLOWER = "slower"
    VERYSLOW = "veryslow"


@dataclass
class VideoMetadata:
    """Video file metadata"""
    duration: float  # seconds
    width: int
    height: int
    fps: float
    codec: str
    bitrate: Optional[int]  # kbps
    audio_codec: Optional[str]
    audio_bitrate: Optional[int]
    file_size: int  # bytes
    format_name: str
    
    @property
    def aspect_ratio(self) -> float:
        return self.width / self.height if self.height > 0 else 0
    
    @property
    def resolution(self) -> str:
        return f"{self.width}x{self.height}"
    
    @property
    def is_vertical(self) -> bool:
        return self.height > self.width
    
    @property
    def is_horizontal(self) -> bool:
        return self.width > self.height
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "duration": self.duration,
            "width": self.width,
            "height": self.height,
            "fps": self.fps,
            "codec": self.codec,
            "bitrate": self.bitrate,
            "audio_codec": self.audio_codec,
            "audio_bitrate": self.audio_bitrate,
            "file_size": self.file_size,
            "format_name": self.format_name,
            "aspect_ratio": self.aspect_ratio,
            "resolution": self.resolution,
            "is_vertical": self.is_vertical,
        }


@dataclass
class RenderProgress:
    """Progress information during rendering"""
    frame: int
    fps: float
    total_frames: int
    time_processed: float  # seconds
    total_duration: float  # seconds
    speed: float  # e.g., 2.5x realtime
    bitrate: float  # kbps
    size: int  # bytes written
    
    @property
    def percent_complete(self) -> float:
        if self.total_duration <= 0:
            return 0.0
        return min(100.0, (self.time_processed / self.total_duration) * 100)
    
    @property
    def eta_seconds(self) -> Optional[float]:
        if self.speed <= 0:
            return None
        remaining = self.total_duration - self.time_processed
        return remaining / self.speed


class VideoService:
    """
    Service for video processing operations using FFmpeg.
    
    Handles subtitle burning, metadata extraction, thumbnail generation,
    and format conversion with progress tracking support.
    """
    
    def __init__(
        self,
        ffmpeg_path: str = "ffmpeg",
        ffprobe_path: str = "ffprobe",
        fonts_dir: Optional[str] = None,
        temp_dir: Optional[str] = None,
    ):
        self.ffmpeg_path = ffmpeg_path
        self.ffprobe_path = ffprobe_path
        self.fonts_dir = fonts_dir
        self.temp_dir = temp_dir or tempfile.gettempdir()
        
        self._validate_ffmpeg()
    
    def _validate_ffmpeg(self) -> None:
        """Verify FFmpeg is installed and accessible"""
        try:
            result = subprocess.run(
                [self.ffmpeg_path, "-version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                raise FFmpegNotFoundError(f"FFmpeg returned error: {result.stderr}")
            logger.info(f"FFmpeg found: {result.stdout.split(chr(10))[0]}")
        except FileNotFoundError:
            raise FFmpegNotFoundError(
                f"FFmpeg not found at '{self.ffmpeg_path}'. "
                "Please install FFmpeg or provide correct path."
            )
        except subprocess.TimeoutExpired:
            raise FFmpegNotFoundError("FFmpeg validation timed out")
    
    def get_metadata(self, video_path: str) -> VideoMetadata:
        """
        Extract metadata from video file using ffprobe.
        
        Args:
            video_path: Path to video file
            
        Returns:
            VideoMetadata object with video properties
            
        Raises:
            InvalidVideoError: If file cannot be read or is not a valid video
        """
        if not os.path.exists(video_path):
            raise InvalidVideoError(f"Video file not found: {video_path}")
        
        cmd = [
            self.ffprobe_path,
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            video_path
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                raise InvalidVideoError(f"ffprobe failed: {result.stderr}")
            
            data = json.loads(result.stdout)
            
        except json.JSONDecodeError as e:
            raise InvalidVideoError(f"Failed to parse video metadata: {e}")
        except subprocess.TimeoutExpired:
            raise InvalidVideoError("Metadata extraction timed out")
        
        # Find video stream
        video_stream = None
        audio_stream = None
        
        for stream in data.get("streams", []):
            if stream.get("codec_type") == "video" and not video_stream:
                video_stream = stream
            elif stream.get("codec_type") == "audio" and not audio_stream:
                audio_stream = stream
        
        if not video_stream:
            raise InvalidVideoError("No video stream found in file")
        
        format_info = data.get("format", {})
        
        # Parse FPS from various formats (e.g., "30/1", "29.97", "30000/1001")
        fps_str = video_stream.get("r_frame_rate", "0/1")
        try:
            if "/" in fps_str:
                num, den = map(float, fps_str.split("/"))
                fps = num / den if den != 0 else 0
            else:
                fps = float(fps_str)
        except (ValueError, ZeroDivisionError):
            fps = 0
        
        # Parse bitrate
        bitrate = None
        if "bit_rate" in video_stream:
            try:
                bitrate = int(video_stream["bit_rate"]) // 1000
            except (ValueError, TypeError):
                pass
        
        audio_codec = None
        audio_bitrate = None
        if audio_stream:
            audio_codec = audio_stream.get("codec_name")
            if "bit_rate" in audio_stream:
                try:
                    audio_bitrate = int(audio_stream["bit_rate"]) // 1000
                except (ValueError, TypeError):
                    pass
        
        return VideoMetadata(
            duration=float(format_info.get("duration", 0)),
            width=int(video_stream.get("width", 0)),
            height=int(video_stream.get("height", 0)),
            fps=round(fps, 3),
            codec=video_stream.get("codec_name", "unknown"),
            bitrate=bitrate,
            audio_codec=audio_codec,
            audio_bitrate=audio_bitrate,
            file_size=int(format_info.get("size", 0)),
            format_name=format_info.get("format_name", "unknown"),
        )
    
    def render_with_subtitles(
        self,
        input_path: str,
        ass_path: str,
        output_path: str,
        video_codec: VideoCodec = VideoCodec.H264,
        audio_codec: AudioCodec = AudioCodec.COPY,
        preset: OutputPreset = OutputPreset.MEDIUM,
        crf: int = 23,
        progress_callback: Optional[Callable[[RenderProgress], None]] = None,
    ) -> str:
        """
        Burn ASS subtitles into video.
        
        Args:
            input_path: Path to input video
            ass_path: Path to ASS subtitle file
            output_path: Path for rendered output
            video_codec: Video codec to use
            audio_codec: Audio codec to use
            preset: Encoding speed preset
            crf: Constant Rate Factor (quality, lower = better, 18-28 typical)
            progress_callback: Optional callback for progress updates
            
        Returns:
            Path to rendered video
            
        Raises:
            InvalidVideoError: If input files are invalid
            RenderFailedError: If rendering fails
        """
        # Validate inputs
        if not os.path.exists(input_path):
            raise InvalidVideoError(f"Input video not found: {input_path}")
        if not os.path.exists(ass_path):
            raise InvalidVideoError(f"Subtitle file not found: {ass_path}")
        
        # Get video metadata for progress tracking
        metadata = self.get_metadata(input_path)
        total_frames = int(metadata.duration * metadata.fps)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Build filter string
        # Escape special characters in path for FFmpeg filter
        escaped_ass_path = ass_path.replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
        
        if self.fonts_dir and os.path.isdir(self.fonts_dir):
            escaped_fonts_dir = self.fonts_dir.replace("\\", "/").replace(":", "\\:")
            vf = f"ass='{escaped_ass_path}':fontsdir='{escaped_fonts_dir}'"
        else:
            vf = f"ass='{escaped_ass_path}'"
        
        # Build FFmpeg command
        cmd = [
            self.ffmpeg_path,
            "-y",  # Overwrite output
            "-i", input_path,
            "-vf", vf,
            "-c:v", video_codec.value,
            "-c:a", audio_codec.value,
            "-progress", "pipe:1",  # Output progress to stdout
            "-nostats",
        ]
        
        # Add codec-specific options
        if video_codec != VideoCodec.COPY:
            cmd.extend([
                "-preset", preset.value,
                "-crf", str(crf),
            ])
            
            # H.264 specific options for compatibility
            if video_codec == VideoCodec.H264:
                cmd.extend([
                    "-profile:v", "high",
                    "-level", "4.1",
                    "-pix_fmt", "yuv420p",  # Ensure compatibility
                ])
        
        cmd.append(output_path)
        
        logger.info(f"Starting render: {' '.join(cmd)}")
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )
            
            # Track progress from stdout
            current_progress: Dict[str, Any] = {}
            
            for line in process.stdout:
                line = line.strip()
                if "=" in line:
                    key, value = line.split("=", 1)
                    current_progress[key] = value
                    
                    # When we get a complete progress update
                    if key == "progress" and progress_callback:
                        try:
                            progress = self._parse_progress(
                                current_progress,
                                total_frames,
                                metadata.duration
                            )
                            progress_callback(progress)
                        except Exception as e:
                            logger.debug(f"Progress parse error: {e}")
                        current_progress = {}
            
            # Wait for process to complete
            _, stderr = process.communicate(timeout=3600)  # 1 hour timeout
            
            if process.returncode != 0:
                raise RenderFailedError(f"FFmpeg failed: {stderr}")
            
            if not os.path.exists(output_path):
                raise RenderFailedError("Output file was not created")
            
            logger.info(f"Render complete: {output_path}")
            return output_path
            
        except subprocess.TimeoutExpired:
            process.kill()
            raise RenderFailedError("Rendering timed out after 1 hour")
        except Exception as e:
            if isinstance(e, RenderFailedError):
                raise
            raise RenderFailedError(f"Rendering failed: {str(e)}")
    
    def _parse_progress(
        self,
        data: Dict[str, str],
        total_frames: int,
        total_duration: float
    ) -> RenderProgress:
        """Parse FFmpeg progress output into RenderProgress object"""
        
        # Parse time (format: HH:MM:SS.ms or microseconds)
        time_str = data.get("out_time_ms", "0")
        try:
            time_processed = int(time_str) / 1_000_000  # microseconds to seconds
        except ValueError:
            time_processed = 0
        
        # Parse frame count
        try:
            frame = int(data.get("frame", 0))
        except ValueError:
            frame = 0
        
        # Parse FPS
        try:
            fps = float(data.get("fps", 0))
        except ValueError:
            fps = 0
        
        # Parse speed (e.g., "2.5x")
        speed_str = data.get("speed", "0x").rstrip("x")
        try:
            speed = float(speed_str) if speed_str != "N/A" else 0
        except ValueError:
            speed = 0
        
        # Parse bitrate (e.g., "1234.5kbits/s")
        bitrate_str = data.get("bitrate", "0")
        try:
            bitrate = float(bitrate_str.replace("kbits/s", "").strip())
        except ValueError:
            bitrate = 0
        
        # Parse size
        try:
            size = int(data.get("total_size", 0))
        except ValueError:
            size = 0
        
        return RenderProgress(
            frame=frame,
            fps=fps,
            total_frames=total_frames,
            time_processed=time_processed,
            total_duration=total_duration,
            speed=speed,
            bitrate=bitrate,
            size=size,
        )
    
    def generate_thumbnail(
        self,
        video_path: str,
        output_path: str,
        time_offset: float = 1.0,
        width: int = 480,
        height: int = -1,  # Auto-calculate to maintain aspect ratio
    ) -> str:
        """
        Generate thumbnail image from video.
        
        Args:
            video_path: Path to video file
            output_path: Path for thumbnail image (jpg/png)
            time_offset: Time in seconds to capture frame
            width: Thumbnail width (height auto-calculated if -1)
            height: Thumbnail height (width auto-calculated if -1)
            
        Returns:
            Path to generated thumbnail
        """
        if not os.path.exists(video_path):
            raise InvalidVideoError(f"Video file not found: {video_path}")
        
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Build scale filter
        if height == -1:
            scale = f"scale={width}:-1"
        elif width == -1:
            scale = f"scale=-1:{height}"
        else:
            scale = f"scale={width}:{height}"
        
        cmd = [
            self.ffmpeg_path,
            "-y",
            "-ss", str(time_offset),
            "-i", video_path,
            "-vf", scale,
            "-vframes", "1",
            "-q:v", "2",  # High quality JPEG
            output_path
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                raise RenderFailedError(f"Thumbnail generation failed: {result.stderr}")
            
            return output_path
            
        except subprocess.TimeoutExpired:
            raise RenderFailedError("Thumbnail generation timed out")
    
    def generate_preview_clip(
        self,
        video_path: str,
        ass_path: str,
        output_path: str,
        start_time: float = 0,
        duration: float = 5,
        scale: float = 0.5,
    ) -> str:
        """
        Generate a short preview clip with subtitles for quick preview.
        
        Args:
            video_path: Path to video file
            ass_path: Path to ASS subtitle file
            output_path: Path for preview clip
            start_time: Start time in seconds
            duration: Duration of preview in seconds
            scale: Scale factor (0.5 = half resolution)
            
        Returns:
            Path to generated preview clip
        """
        if not os.path.exists(video_path):
            raise InvalidVideoError(f"Video file not found: {video_path}")
        if not os.path.exists(ass_path):
            raise InvalidVideoError(f"Subtitle file not found: {ass_path}")
        
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Escape paths
        escaped_ass = ass_path.replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
        
        # Build filter chain: scale down, then apply subtitles
        metadata = self.get_metadata(video_path)
        new_width = int(metadata.width * scale)
        new_height = int(metadata.height * scale)
        
        # Make dimensions even (required by many codecs)
        new_width = new_width - (new_width % 2)
        new_height = new_height - (new_height % 2)
        
        vf = f"scale={new_width}:{new_height},ass='{escaped_ass}'"
        
        cmd = [
            self.ffmpeg_path,
            "-y",
            "-ss", str(start_time),
            "-i", video_path,
            "-t", str(duration),
            "-vf", vf,
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-crf", "28",
            "-c:a", "aac",
            "-b:a", "128k",
            "-pix_fmt", "yuv420p",
            output_path
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                raise RenderFailedError(f"Preview generation failed: {result.stderr}")
            
            return output_path
            
        except subprocess.TimeoutExpired:
            raise RenderFailedError("Preview generation timed out")
    
    def extract_audio(
        self,
        video_path: str,
        output_path: str,
        format: str = "wav",
        sample_rate: int = 16000,
        mono: bool = True,
    ) -> str:
        """
        Extract audio from video for transcription.
        
        Whisper works best with 16kHz mono WAV.
        
        Args:
            video_path: Path to video file
            output_path: Path for audio output
            format: Audio format (wav, mp3, etc.)
            sample_rate: Sample rate in Hz
            mono: Convert to mono if True
            
        Returns:
            Path to extracted audio
        """
        if not os.path.exists(video_path):
            raise InvalidVideoError(f"Video file not found: {video_path}")
        
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        cmd = [
            self.ffmpeg_path,
            "-y",
            "-i", video_path,
            "-vn",  # No video
            "-ar", str(sample_rate),
        ]
        
        if mono:
            cmd.extend(["-ac", "1"])
        
        if format == "wav":
            cmd.extend(["-c:a", "pcm_s16le"])
        elif format == "mp3":
            cmd.extend(["-c:a", "libmp3lame", "-b:a", "192k"])
        
        cmd.append(output_path)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes
            )
            
            if result.returncode != 0:
                raise RenderFailedError(f"Audio extraction failed: {result.stderr}")
            
            return output_path
            
        except subprocess.TimeoutExpired:
            raise RenderFailedError("Audio extraction timed out")
    
    def apply_anti_duplicate_effects(
        self,
        input_path: str,
        output_path: str,
        fps_adjust: float = 0.0,
        brightness: float = 0.0,
        saturation: float = 1.0,
        audio_pitch: float = 1.0,
        flip_horizontal: bool = False,
    ) -> str:
        """
        Apply subtle modifications to avoid duplicate detection on platforms.
        
        Args:
            input_path: Path to input video
            output_path: Path for output video
            fps_adjust: FPS adjustment (e.g., 0.01 to slightly change framerate)
            brightness: Brightness adjustment (-1.0 to 1.0, 0 = no change)
            saturation: Saturation multiplier (1.0 = no change)
            audio_pitch: Audio pitch multiplier (1.0 = no change)
            flip_horizontal: Flip video horizontally
            
        Returns:
            Path to modified video
        """
        if not os.path.exists(input_path):
            raise InvalidVideoError(f"Video file not found: {input_path}")
        
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        metadata = self.get_metadata(input_path)
        
        # Build video filter chain
        vf_parts = []
        
        if brightness != 0 or saturation != 1.0:
            vf_parts.append(f"eq=brightness={brightness}:saturation={saturation}")
        
        if flip_horizontal:
            vf_parts.append("hflip")
        
        vf = ",".join(vf_parts) if vf_parts else None
        
        # Build audio filter chain
        af_parts = []
        
        if audio_pitch != 1.0:
            # asetrate changes pitch without changing duration
            new_rate = int(44100 * audio_pitch)
            af_parts.append(f"asetrate={new_rate},aresample=44100")
        
        af = ",".join(af_parts) if af_parts else None
        
        # Build command
        cmd = [
            self.ffmpeg_path,
            "-y",
            "-i", input_path,
        ]
        
        if vf:
            cmd.extend(["-vf", vf])
        
        if af:
            cmd.extend(["-af", af])
        
        # Handle FPS adjustment
        if fps_adjust != 0:
            new_fps = metadata.fps + fps_adjust
            cmd.extend(["-r", str(new_fps)])
        
        cmd.extend([
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            output_path
        ])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600
            )
            
            if result.returncode != 0:
                raise RenderFailedError(f"Anti-duplicate processing failed: {result.stderr}")
            
            return output_path
            
        except subprocess.TimeoutExpired:
            raise RenderFailedError("Anti-duplicate processing timed out")


# Convenience function matching the integration spec
def render_video(
    input_path: str,
    ass_path: str,
    output_path: str,
    fonts_dir: Optional[str] = None,
    progress_callback: Optional[Callable[[RenderProgress], None]] = None,
) -> str:
    """
    Render video with burned-in subtitles.
    
    This is the main integration point for the Backend → Video Render interface.
    
    Args:
        input_path: Path to input video
        ass_path: Path to ASS subtitle file
        output_path: Path for rendered output
        fonts_dir: Optional custom fonts directory
        progress_callback: Optional progress callback
        
    Returns:
        Path to rendered video
    """
    service = VideoService(fonts_dir=fonts_dir)
    return service.render_with_subtitles(
        input_path=input_path,
        ass_path=ass_path,
        output_path=output_path,
        progress_callback=progress_callback,
    )
