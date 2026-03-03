"""
Publisher — Background job that publishes scheduled content via Instagram Graph API.

Workflow:
1. Check calendar for due posts
2. Generate content if needed
3. Upload image to media host
4. Create container via Graph API
5. Poll status until FINISHED
6. Publish container
7. Record result
"""

import logging
import asyncio
from datetime import datetime, timezone
from typing import Optional

from src.instagram.graph_api_client import InstagramGraphAPI
from src.instagram.media_host import MediaHost
from src.auth.auth_service import decrypt_token

logger = logging.getLogger(__name__)


class Publisher:
    """
    Handles the publish workflow for a single post.
    
    Usage:
        pub = Publisher(access_token, ig_user_id)
        media_id = await pub.publish_image(
            image_path="/path/to/image.jpg",
            caption="My post caption...",
        )
    """

    def __init__(
        self,
        access_token: str,
        ig_user_id: str,
        *,
        media_host: Optional[MediaHost] = None,
    ):
        self._api = InstagramGraphAPI(access_token, ig_user_id)
        self._media_host = media_host or MediaHost()

    async def publish_image(
        self,
        image_path: str,
        caption: str,
        *,
        alt_text: Optional[str] = None,
    ) -> str:
        """
        Publish a single image post.
        
        Args:
            image_path: Local path to the image
            caption: Post caption (with hashtags)
            alt_text: Image alt text
            
        Returns:
            Published Instagram media ID
        """
        # Step 1: Make image publicly accessible
        image_url = self._media_host.prepare_for_publishing(image_path)

        # Step 2: Create container
        container_id = await self._api.create_image_container(
            image_url, caption, alt_text=alt_text
        )

        # Step 3: Wait for container to be ready
        await self._api.wait_for_container(container_id)

        # Step 4: Publish
        media_id = await self._api.publish_container(container_id)

        logger.info(f"Published image post: {media_id}")
        return media_id

    async def publish_carousel(
        self,
        image_paths: list[str],
        caption: str,
    ) -> str:
        """
        Publish a carousel post (2-10 images).
        
        Args:
            image_paths: List of local image paths
            caption: Carousel caption
            
        Returns:
            Published Instagram media ID
        """
        # Step 1: Create item containers
        item_ids = []
        for path in image_paths:
            url = self._media_host.prepare_for_publishing(path)
            item_id = await self._api.create_image_container(
                url, is_carousel_item=True
            )
            item_ids.append(item_id)

        # Step 2: Create carousel container
        carousel_id = await self._api.create_carousel_container(item_ids, caption)

        # Step 3: Wait & publish
        await self._api.wait_for_container(carousel_id)
        media_id = await self._api.publish_container(carousel_id)

        logger.info(f"Published carousel: {media_id} ({len(image_paths)} items)")
        return media_id

    async def publish_story(
        self,
        image_path: str,
    ) -> str:
        """
        Publish a story.
        
        Args:
            image_path: Local path to the image
            
        Returns:
            Published media ID
        """
        image_url = self._media_host.prepare_for_publishing(image_path)
        container_id = await self._api.create_story_container(image_url)
        await self._api.wait_for_container(container_id)
        media_id = await self._api.publish_container(container_id)

        logger.info(f"Published story: {media_id}")
        return media_id

    async def check_rate_limit(self) -> dict:
        """Check publishing rate limit before posting."""
        return await self._api.get_publishing_limit()

    async def close(self):
        """Close the API client."""
        await self._api.close()
