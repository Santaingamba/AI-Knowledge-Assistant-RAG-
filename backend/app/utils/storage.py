# backend/app/utils/storage.py
"""Storage abstraction for document files.
Supports local filesystem storage (default) and AWS S3 storage.
Configuration via Settings.STORAGE_BACKEND = "local" or "s3".
"""
import os
import shutil
from typing import Protocol, runtime_checkable

from app.core.config import settings

# Optional boto3 import (only needed for S3)
try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError
except ImportError:  # pragma: no cover
    boto3 = None

@runtime_checkable
class StorageBackend(Protocol):
    def save_file(self, file_path: str, file_obj) -> str:
        """Save a file-like object to the storage.
        Returns the absolute path or S3 key where the file was stored.
        """
        ...

    def delete_file(self, identifier: str) -> None:
        """Delete a file given its storage identifier (path or S3 key)."""
        ...

class LocalStorage:
    def __init__(self, base_dir: str = settings.UPLOAD_PATH):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def _full_path(self, filename: str) -> str:
        return os.path.join(self.base_dir, filename)

    def save_file(self, file_path: str, file_obj) -> str:
        # file_path is expected to be a filename (no directory components)
        full_path = self._full_path(file_path)
        # Ensure directory exists
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "wb") as buffer:
            shutil.copyfileobj(file_obj, buffer)
        return full_path

    def delete_file(self, identifier: str) -> None:
        try:
            os.remove(identifier)
        except FileNotFoundError:
            pass

class S3Storage:
    def __init__(self):
        if not boto3:
            raise RuntimeError("boto3 is required for S3 storage but is not installed.")
        if not all([settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY, settings.AWS_REGION, settings.AWS_S3_BUCKET]):
            raise RuntimeError("AWS credentials and bucket must be set for S3 storage.")
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
        self.bucket = settings.AWS_S3_BUCKET

    def save_file(self, file_path: str, file_obj) -> str:
        # file_path will be used as the object key in S3
        try:
            self.s3.upload_fileobj(file_obj, self.bucket, file_path)
        except (BotoCoreError, ClientError) as exc:
            raise RuntimeError(f"Failed to upload to S3: {exc}")
        return file_path  # S3 key

    def delete_file(self, identifier: str) -> None:
        try:
            self.s3.delete_object(Bucket=self.bucket, Key=identifier)
        except (BotoCoreError, ClientError) as exc:
            raise RuntimeError(f"Failed to delete from S3: {exc}")

def get_storage() -> StorageBackend:
    if settings.STORAGE_BACKEND.lower() == "s3":
        return S3Storage()
    return LocalStorage()
