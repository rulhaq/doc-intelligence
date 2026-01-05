"""MinIO Object Storage Service"""
from typing import BinaryIO, Optional
from minio import Minio
from minio.error import S3Error
import structlog
from pathlib import Path

from app.core.config import settings
from app.core.exceptions import ServiceUnavailableException

logger = structlog.get_logger()


class MinIOService:
    """MinIO/S3 object storage service"""
    
    def __init__(self):
        # Extract endpoint without scheme
        endpoint = settings.S3_ENDPOINT.replace("http://", "").replace("https://", "")
        
        self.client = Minio(
            endpoint,
            access_key=settings.S3_ACCESS_KEY,
            secret_key=settings.S3_SECRET_KEY,
            secure=settings.S3_SECURE,
        )
        self.bucket = settings.S3_BUCKET
    
    async def initialize_buckets(self):
        """Initialize MinIO buckets"""
        try:
            # Check if bucket exists
            if not self.client.bucket_exists(self.bucket):
                logger.info(f"Creating MinIO bucket: {self.bucket}")
                self.client.make_bucket(self.bucket)
                logger.info(f"MinIO bucket created: {self.bucket}")
            else:
                logger.info(f"MinIO bucket already exists: {self.bucket}")
                
        except S3Error as e:
            logger.error(f"Failed to initialize MinIO buckets: {e}")
            raise ServiceUnavailableException(f"MinIO initialization failed: {e}")
    
    async def upload_file(
        self,
        file: BinaryIO,
        object_name: str,
        content_type: Optional[str] = None,
    ) -> str:
        """
        Upload file to MinIO
        
        Args:
            file: File-like object
            object_name: Object name/path in bucket
            content_type: Content type
            
        Returns:
            Object path
        """
        try:
            # Get file size
            file.seek(0, 2)  # Seek to end
            file_size = file.tell()
            file.seek(0)  # Seek back to start
            
            self.client.put_object(
                bucket_name=self.bucket,
                object_name=object_name,
                data=file,
                length=file_size,
                content_type=content_type or "application/octet-stream",
            )
            
            logger.info(f"Uploaded file to MinIO: {object_name}")
            return object_name
            
        except S3Error as e:
            logger.error(f"Failed to upload file to MinIO: {e}")
            raise ServiceUnavailableException(f"File upload failed: {e}")
    
    async def download_file(self, object_name: str, file_path: str):
        """Download file from MinIO"""
        try:
            self.client.fget_object(
                bucket_name=self.bucket,
                object_name=object_name,
                file_path=file_path,
            )
            logger.info(f"Downloaded file from MinIO: {object_name}")
            
        except S3Error as e:
            logger.error(f"Failed to download file from MinIO: {e}")
            raise ServiceUnavailableException(f"File download failed: {e}")
    
    async def get_file_url(self, object_name: str, expires_seconds: int = 3600) -> str:
        """Get presigned URL for file"""
        try:
            url = self.client.presigned_get_object(
                bucket_name=self.bucket,
                object_name=object_name,
                expires=expires_seconds,
            )
            return url
            
        except S3Error as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            raise ServiceUnavailableException(f"URL generation failed: {e}")
    
    async def delete_file(self, object_name: str) -> bool:
        """Delete file from MinIO"""
        try:
            self.client.remove_object(
                bucket_name=self.bucket,
                object_name=object_name,
            )
            logger.info(f"Deleted file from MinIO: {object_name}")
            return True
            
        except S3Error as e:
            logger.error(f"Failed to delete file from MinIO: {e}")
            return False
    
    async def list_objects(self, prefix: str = "") -> list:
        """List objects in bucket"""
        try:
            objects = self.client.list_objects(
                bucket_name=self.bucket,
                prefix=prefix,
                recursive=True,
            )
            return [obj.object_name for obj in objects]
            
        except S3Error as e:
            logger.error(f"Failed to list objects: {e}")
            return []

