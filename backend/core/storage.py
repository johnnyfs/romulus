"""MinIO/S3 storage client for managing asset uploads."""

import uuid
from datetime import timedelta

from minio import Minio

from config import settings


class StorageClient:
    """Client for interacting with MinIO/S3 storage."""

    def __init__(self):
        # Use localhost for both operations and URL generation
        # Docker extra_hosts maps localhost to host gateway
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        self.bucket = settings.MINIO_BUCKET
        self._ensure_bucket()

    def _ensure_bucket(self):
        """Ensure the bucket exists, create it if it doesn't."""
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

    def generate_storage_key(self, filename: str) -> str:
        """Generate a unique storage key for a file."""
        # Use UUID to ensure uniqueness
        file_id = uuid.uuid4()
        # Preserve the original extension if present
        extension = ""
        if "." in filename:
            extension = filename.rsplit(".", 1)[1]
            return f"{file_id}.{extension}"
        return str(file_id)

    def get_presigned_upload_url(self, storage_key: str, expires: timedelta = timedelta(hours=1)) -> str:
        """Generate a presigned URL for uploading a file."""
        return self.client.presigned_put_object(self.bucket, storage_key, expires=expires)

    def get_download_url(self, storage_key: str, expires: timedelta = timedelta(days=7)) -> str:
        """Generate a presigned URL for downloading a file."""
        return self.client.presigned_get_object(self.bucket, storage_key, expires=expires)

    def delete_object(self, storage_key: str):
        """Delete an object from storage."""
        self.client.remove_object(self.bucket, storage_key)

    def object_exists(self, storage_key: str) -> bool:
        """Check if an object exists in storage."""
        try:
            self.client.stat_object(self.bucket, storage_key)
            return True
        except Exception:
            return False


# Singleton instance
_storage_client = None


def get_storage_client() -> StorageClient:
    """Get or create the storage client singleton."""
    global _storage_client
    if _storage_client is None:
        _storage_client = StorageClient()
    return _storage_client
