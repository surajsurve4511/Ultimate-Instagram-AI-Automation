"""
Instagram Graph API Client — Official publishing via Meta's API.

This replaces the unofficial `instagrapi` library with the official
Instagram Graph API. It supports:
- Single image posts
- Carousel posts (up to 10 items)
- Reels
- Stories
- Publishing rate limit checking

Official docs: https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/content-publishing

Endpoints used:
- POST /<IG_ID>/media — Create media container
- POST /<IG_ID>/media_publish — Publish container
- GET /<CONTAINER_ID>?fields=status_code — Check container status
- GET /<IG_ID>/content_publishing_limit — Check rate limit
"""

import logging
import time
from typing import Optional

import httpx

from src.config.settings import SETTINGS

logger = logging.getLogger(__name__)

# Container status codes from the API
STATUS_EXPIRED = "EXPIRED"
STATUS_ERROR = "ERROR"
STATUS_FINISHED = "FINISHED"
STATUS_IN_PROGRESS = "IN_PROGRESS"
STATUS_PUBLISHED = "PUBLISHED"


class InstagramGraphAPI:
    """
    Official Instagram Graph API client for content publishing.
    
    Usage:
        client = InstagramGraphAPI(access_token, ig_user_id)
        
        # Single image post
        container_id = await client.create_image_container(image_url, caption)
        await client.wait_for_container(container_id)
        media_id = await client.publish_container(container_id)
        
        # Carousel post
        item_ids = []
        for url in image_urls:
            item_id = await client.create_image_container(url, is_carousel_item=True)
            item_ids.append(item_id)
        carousel_id = await client.create_carousel_container(item_ids, caption)
        await client.wait_for_container(carousel_id)
        media_id = await client.publish_container(carousel_id)
    """

    def __init__(
        self,
        access_token: str,
        ig_user_id: str,
        *,
        api_version: Optional[str] = None,
    ):
        """
        Initialize the client.
        
        Args:
            access_token: Instagram User access token (from OAuth flow)
            ig_user_id: Instagram Professional account ID
            api_version: API version (default from settings)
        """
        self._access_token = access_token
        self._ig_user_id = ig_user_id
        self._api_version = api_version or SETTINGS.INSTAGRAM_GRAPH_API_VERSION
        self._base_url = f"{SETTINGS.INSTAGRAM_GRAPH_API_HOST}/{self._api_version}"
        self._client = httpx.AsyncClient(timeout=60.0)

    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()

    def _headers(self) -> dict:
        """Common headers for all requests."""
        return {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
        }

    # ========== Container Creation ==========

    async def create_image_container(
        self,
        image_url: str,
        caption: Optional[str] = None,
        *,
        alt_text: Optional[str] = None,
        is_carousel_item: bool = False,
    ) -> str:
        """
        Create a media container for a single image post.
        
        Args:
            image_url: Public URL of the image (must be JPEG, publicly accessible)
            caption: Post caption (not used for carousel items)
            alt_text: Image alt text for accessibility
            is_carousel_item: If True, this is part of a carousel
            
        Returns:
            Container ID
            
        Ref: https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/content-publishing
        """
        payload = {"image_url": image_url}

        if caption and not is_carousel_item:
            payload["caption"] = caption
        if alt_text:
            payload["alt_text"] = alt_text
        if is_carousel_item:
            payload["is_carousel_item"] = True

        url = f"{self._base_url}/{self._ig_user_id}/media"
        response = await self._client.post(url, headers=self._headers(), json=payload)
        response.raise_for_status()

        data = response.json()
        container_id = data["id"]
        logger.info(f"Created image container: {container_id}")
        return container_id

    async def create_video_container(
        self,
        video_url: str,
        caption: Optional[str] = None,
        *,
        media_type: str = "REELS",
        is_carousel_item: bool = False,
    ) -> str:
        """
        Create a media container for a video/reel.
        
        Args:
            video_url: Public URL of the video
            caption: Post caption
            media_type: REELS or VIDEO
            is_carousel_item: If part of a carousel
            
        Returns:
            Container ID
        """
        payload = {
            "video_url": video_url,
            "media_type": media_type,
        }

        if caption and not is_carousel_item:
            payload["caption"] = caption
        if is_carousel_item:
            payload["is_carousel_item"] = True

        url = f"{self._base_url}/{self._ig_user_id}/media"
        response = await self._client.post(url, headers=self._headers(), json=payload)
        response.raise_for_status()

        data = response.json()
        container_id = data["id"]
        logger.info(f"Created video container: {container_id}")
        return container_id

    async def create_story_container(
        self,
        media_url: str,
        *,
        is_video: bool = False,
    ) -> str:
        """
        Create a container for an Instagram Story.
        
        Args:
            media_url: Public URL of the image or video
            is_video: True if the media is a video
            
        Returns:
            Container ID
        """
        payload = {"media_type": "STORIES"}

        if is_video:
            payload["video_url"] = media_url
        else:
            payload["image_url"] = media_url

        url = f"{self._base_url}/{self._ig_user_id}/media"
        response = await self._client.post(url, headers=self._headers(), json=payload)
        response.raise_for_status()

        data = response.json()
        container_id = data["id"]
        logger.info(f"Created story container: {container_id}")
        return container_id

    async def create_carousel_container(
        self,
        children_ids: list[str],
        caption: str,
    ) -> str:
        """
        Create a carousel container from existing item containers.
        
        Args:
            children_ids: List of container IDs (up to 10)
            caption: Carousel post caption
            
        Returns:
            Carousel container ID
            
        Ref: Carousels limited to 10 items. Images cropped based on first image.
        """
        if len(children_ids) > 10:
            raise ValueError("Carousel limited to 10 items")
        if len(children_ids) < 2:
            raise ValueError("Carousel requires at least 2 items")

        payload = {
            "media_type": "CAROUSEL",
            "children": ",".join(children_ids),
            "caption": caption,
        }

        url = f"{self._base_url}/{self._ig_user_id}/media"
        response = await self._client.post(url, headers=self._headers(), json=payload)
        response.raise_for_status()

        data = response.json()
        container_id = data["id"]
        logger.info(f"Created carousel container: {container_id} ({len(children_ids)} items)")
        return container_id

    # ========== Publishing ==========

    async def publish_container(self, container_id: str) -> str:
        """
        Publish a media container to Instagram.
        
        Args:
            container_id: The container to publish
            
        Returns:
            Published media ID
            
        Ref: Rate limit is 100 API-published posts per 24 hours.
        """
        url = f"{self._base_url}/{self._ig_user_id}/media_publish"
        payload = {"creation_id": container_id}

        response = await self._client.post(url, headers=self._headers(), json=payload)
        response.raise_for_status()

        data = response.json()
        media_id = data["id"]
        logger.info(f"Published: container={container_id} -> media={media_id}")
        return media_id

    # ========== Status & Rate Limits ==========

    async def check_container_status(self, container_id: str) -> str:
        """
        Check the publishing status of a container.
        
        Returns:
            Status code: EXPIRED, ERROR, FINISHED, IN_PROGRESS, PUBLISHED
        """
        url = f"{self._base_url}/{container_id}"
        params = {"fields": "status_code"}

        response = await self._client.get(
            url, headers=self._headers(), params=params
        )
        response.raise_for_status()

        data = response.json()
        status = data.get("status_code", "UNKNOWN")
        logger.debug(f"Container {container_id} status: {status}")
        return status

    async def wait_for_container(
        self,
        container_id: str,
        *,
        max_wait_seconds: int = 300,
        poll_interval: int = 10,
    ) -> str:
        """
        Poll container status until it's ready to publish.
        
        Args:
            container_id: Container to wait for
            max_wait_seconds: Maximum wait time
            poll_interval: Seconds between polls (recommended: >= 10)
            
        Returns:
            Final status code
            
        Raises:
            TimeoutError: If container doesn't finish in time
            RuntimeError: If container enters ERROR or EXPIRED state
        """
        start_time = time.time()

        while time.time() - start_time < max_wait_seconds:
            status = await self.check_container_status(container_id)

            if status == STATUS_FINISHED:
                return status
            elif status == STATUS_PUBLISHED:
                return status
            elif status == STATUS_ERROR:
                raise RuntimeError(f"Container {container_id} failed with ERROR")
            elif status == STATUS_EXPIRED:
                raise RuntimeError(f"Container {container_id} expired")
            
            # Still IN_PROGRESS
            await self._async_sleep(poll_interval)

        raise TimeoutError(
            f"Container {container_id} did not finish within {max_wait_seconds}s"
        )

    async def get_publishing_limit(self) -> dict:
        """
        Check current publishing rate limit usage.
        
        Returns:
            Dict with rate limit data (quota_usage, quota_total, etc.)
        """
        url = f"{self._base_url}/{self._ig_user_id}/content_publishing_limit"
        response = await self._client.get(url, headers=self._headers())
        response.raise_for_status()
        return response.json()

    # ========== Helpers ==========

    @staticmethod
    async def _async_sleep(seconds: int):
        """Async sleep helper."""
        import asyncio
        await asyncio.sleep(seconds)
