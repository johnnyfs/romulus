"""MinIO/S3 storage client for managing asset uploads."""

import json
import uuid
from datetime import timedelta
from io import BytesIO

from minio import Minio

from config import settings
from core.schemas import AssetData, AssetType, ResourceData, ResourceType


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

    def generate_storage_key(self, filename: str, data: AssetData | ResourceData, data_id: uuid.UUID) -> str:
        """Generate a storage key based on asset/resource type and processing state.

        For resources: resources/{type}/{state}/{id}/{filename}
        For assets: assets/{type}/{id}/{filename}
        Example: resources/images/raw/123e4567-e89b-12d3-a456-426614174000/fish.png
        Example: assets/palettes/123e4567-e89b-12d3-a456-426614174000/palette.json
        """
        # Check if this is a resource (has state attribute) vs asset (no state)
        if hasattr(data, 'state'):
            # Resources have a processing state
            if data.type == ResourceType.IMAGE:
                return f"resources/images/{data.state.value}/{data_id}/{filename}"
            else:
                return f"resources/{data.type.value}/{data_id}/{filename}"
        else:
            # Assets don't have a processing state
            if data.type == AssetType.PALETTE:
                return f"assets/palettes/{data_id}/{filename}"
            else:
                return f"assets/{data.type.value}/{data_id}/{filename}"

    def write_metadata(self, storage_key: str, metadata: dict) -> None:
        """Write metadata.json file alongside the asset."""
        # Construct metadata file path
        metadata_key = f"{storage_key}.metadata.json"

        # Serialize metadata to JSON
        metadata_json = json.dumps(metadata, indent=2, default=str)
        metadata_bytes = metadata_json.encode('utf-8')

        # Upload to MinIO
        self.client.put_object(
            self.bucket,
            metadata_key,
            BytesIO(metadata_bytes),
            length=len(metadata_bytes),
            content_type='application/json'
        )

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
