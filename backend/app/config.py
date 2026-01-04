"""
Application Configuration
"""

import os
from typing import Optional, List
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # App
    app_name: str = "CaptionMagic"
    debug: bool = True
    secret_key: str = "change-me-in-production"
    api_v1_prefix: str = "/api/v1"
    
    # Database
    database_url: str = "sqlite:///./captionmagic.db"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Storage - use local writable path
    storage_type: str = "local"
    storage_path: str = "./uploads"
    s3_bucket: Optional[str] = None
    s3_region: Optional[str] = None
    s3_endpoint: Optional[str] = None
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    
    # FFmpeg
    ffmpeg_path: str = "/usr/bin/ffmpeg"
    ffprobe_path: str = "/usr/bin/ffprobe"
    fonts_dir: str = "./fonts"
    temp_dir: str = "/tmp"
    
    # Whisper
    whisper_model: str = "base"
    whisper_device: str = "cpu"
    
    # Upload limits
    max_upload_size_mb: int = 500
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "*"]
    
    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
