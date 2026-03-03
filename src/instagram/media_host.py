"""
Media Host — Serves generated images at publicly accessible URLs.

Instagram Graph API requires image_url to be a publicly accessible URL
because it cURLs the image when creating containers.

This module provides a simple static file server for development.
In production, use cloud storage (S3, GCS) instead.

Docs: https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/content-publishing
"""

import logging
import shutil
from pathlib import Path
from typing import Optional

from src.config.settings import SETTINGS

logger = logging.getLogger(__name__)


class MediaHost:
    """
    Manages media files and generates public URLs for Instagram publishing.
    
    In development: serves from a local directory via FastAPI static files.
    In production: upload to cloud storage (S3, GCS) and return the CDN URL.
    
    Usage:
        host = MediaHost()
        url = host.prepare_for_publishing("/path/to/image.jpg")
        # url = "http://localhost:8000/media/image_12345.jpg"
        # Use this url as image_url in Instagram Graph API
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        media_dir: Optional[str] = None,
    ):
        self._base_url = (base_url or SETTINGS.MEDIA_UPLOAD_BASE_URL).rstrip("/")
        self._media_dir = Path(media_dir or SETTINGS.IMAGES_STORAGE_PATH)
        self._media_dir.mkdir(parents=True, exist_ok=True)

    def prepare_for_publishing(
        self,
        local_path: str,
        *,
        filename: Optional[str] = None,
    ) -> str:
        """
        Prepare a local image file for Instagram publishing.
        
        Copies the file to the media serving directory and returns
        the public URL that Instagram can access.
        
        Args:
            local_path: Path to the local image file
            filename: Custom filename for the hosted file
            
        Returns:
            Public URL where Instagram can access the image
        """
        source = Path(local_path)
        if not source.exists():
            raise FileNotFoundError(f"Image not found: {local_path}")

        # Use custom filename or keep original
        if filename:
            dest_name = filename
        else:
            dest_name = source.name

        dest = self._media_dir / dest_name

        # Copy to serving directory if not already there
        if source.resolve() != dest.resolve():
            shutil.copy2(str(source), str(dest))
            logger.info(f"Copied {source.name} to media directory")

        url = f"{self._base_url}/{dest_name}"
        logger.info(f"Media URL: {url}")
        return url

    def prepare_batch(self, local_paths: list[str]) -> list[str]:
        """
        Prepare multiple files for publishing.
        
        Args:
            local_paths: List of local file paths
            
        Returns:
            List of public URLs
        """
        return [self.prepare_for_publishing(p) for p in local_paths]

    def cleanup(self, filename: str) -> None:
        """
        Remove a published file from the media directory.
        Call after Instagram has successfully fetched the image.
        
        Args:
            filename: Name of the file to remove
        """
        path = self._media_dir / filename
        if path.exists():
            path.unlink()
            logger.info(f"Cleaned up: {filename}")

    def cleanup_all(self) -> int:
        """
        Remove all files from the media directory.
        
        Returns:
            Number of files removed
        """
        count = 0
        for f in self._media_dir.iterdir():
            if f.is_file():
                f.unlink()
                count += 1
        logger.info(f"Cleaned up {count} files")
        return count
