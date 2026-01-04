"""
Video rendering service using FFmpeg.
"""

import subprocess
import os
import tempfile

def render_video_with_captions(
    input_video: str,
    ass_content: str,
    output_path: str = None
) -> str:
    """
    Burn ASS subtitles into video using FFmpeg.
    """
    if output_path is None:
        output_path = input_video.replace('.mp4', '_captioned.mp4')
    
    # Write ASS to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ass', delete=False) as f:
        f.write(ass_content)
        ass_path = f.name
    
    try:
        cmd = [
            'ffmpeg', '-y',
            '-i', input_video,
            '-vf', f"ass={ass_path}",
            '-c:a', 'copy',
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"FFmpeg error: {result.stderr}")
        
        return output_path
    finally:
        os.unlink(ass_path)

def get_video_duration(video_path: str) -> float:
    """Get video duration in seconds."""
    cmd = [
        'ffprobe', '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        video_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return float(result.stdout.strip())
