"""
Storage service for file management.

Supports local filesystem and S3-compatible storage.
"""

import os
import aiofiles
from abc import ABC, abstractmethod
from typing import Optional
import boto3
from botocore.exceptions import ClientError

from app.config import settings


class StorageBackend(ABC):
    """Abstract base class for storage backends."""
    
    @abstractmethod
    async def save_file(self, content: bytes, filename: str, folder: str = "") -> str:
        """Save file and return path."""
        pass
    
    @abstractmethod
    async def get_file(self, path: str) -> bytes:
        """Get file content."""
        pass
    
    @abstractmethod
    async def delete_file(self, path: str) -> bool:
        """Delete file."""
        pass
    
    @abstractmethod
    async def get_url(self, path: str, expires_in: int = 3600) -> str:
        """Get URL to access file."""
        pass
    
    @abstractmethod
    async def exists(self, path: str) -> bool:
        """Check if file exists."""
        pass


class LocalStorage(StorageBackend):
    """Local filesystem storage backend."""
    
    def __init__(self, base_path: str):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)
    
    def _get_full_path(self, path: str) -> str:
        return os.path.join(self.base_path, path)
    
    async def save_file(self, content: bytes, filename: str, folder: str = "") -> str:
        """Save file to local filesystem."""
        if folder:
            dir_path = os.path.join(self.base_path, folder)
            os.makedirs(dir_path, exist_ok=True)
            path = os.path.join(folder, filename)
        else:
            path = filename
        
        full_path = self._get_full_path(path)
        
        async with aiofiles.open(full_path, 'wb') as f:
            await f.write(content)
        
        return path
    
    async def get_file(self, path: str) -> bytes:
        """Read file from local filesystem."""
        full_path = self._get_full_path(path)
        
        async with aiofiles.open(full_path, 'rb') as f:
            return await f.read()
    
    async def delete_file(self, path: str) -> bool:
        """Delete file from local filesystem."""
        full_path = self._get_full_path(path)
        
        try:
            os.remove(full_path)
            return True
        except OSError:
            return False
    
    async def get_url(self, path: str, expires_in: int = 3600) -> str:
        """Get URL for local file (served by API)."""
        return f"/api/v1/files/{path}"
    
    async def exists(self, path: str) -> bool:
        """Check if file exists."""
        return os.path.exists(self._get_full_path(path))


class S3Storage(StorageBackend):
    """S3-compatible storage backend (AWS S3, MinIO, etc.)."""
    
    def __init__(
        self,
        bucket: str,
        endpoint_url: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        region: str = "us-east-1"
    ):
        self.bucket = bucket
        self.client = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
        )
        
        # Ensure bucket exists
        try:
            self.client.head_bucket(Bucket=bucket)
        except ClientError:
            self.client.create_bucket(Bucket=bucket)
    
    async def save_file(self, content: bytes, filename: str, folder: str = "") -> str:
        """Save file to S3."""
        key = f"{folder}/{filename}" if folder else filename
        
        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=content,
        )
        
        return key
    
    async def get_file(self, path: str) -> bytes:
        """Get file from S3."""
        response = self.client.get_object(Bucket=self.bucket, Key=path)
        return response['Body'].read()
    
    async def delete_file(self, path: str) -> bool:
        """Delete file from S3."""
        try:
            self.client.delete_object(Bucket=self.bucket, Key=path)
            return True
        except ClientError:
            return False
    
    async def get_url(self, path: str, expires_in: int = 3600) -> str:
        """Get presigned URL for S3 object."""
        url = self.client.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket, 'Key': path},
            ExpiresIn=expires_in,
        )
        return url
    
    async def exists(self, path: str) -> bool:
        """Check if file exists in S3."""
        try:
            self.client.head_object(Bucket=self.bucket, Key=path)
            return True
        except ClientError:
            return False


class StorageService:
    """
    Storage service that wraps the configured backend.
    
    Automatically selects local or S3 storage based on settings.
    """
    
    def __init__(self):
        if settings.storage_type == "s3":
            self.backend = S3Storage(
                bucket=settings.s3_bucket,
                endpoint_url=settings.s3_endpoint,
                access_key=settings.aws_access_key_id,
                secret_key=settings.aws_secret_access_key,
                region=settings.s3_region,
            )
        else:
            self.backend = LocalStorage(settings.storage_path)
    
    async def save_file(self, content: bytes, filename: str, folder: str = "") -> str:
        return await self.backend.save_file(content, filename, folder)
    
    async def get_file(self, path: str) -> bytes:
        return await self.backend.get_file(path)
    
    async def delete_file(self, path: str) -> bool:
        return await self.backend.delete_file(path)
    
    async def get_url(self, path: str, expires_in: int = 3600) -> str:
        return await self.backend.get_url(path, expires_in)
    
    async def exists(self, path: str) -> bool:
        return await self.backend.exists(path)


# Global storage service instance
storage_service = StorageService()
