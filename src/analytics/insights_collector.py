"""
Insights Collector — Fetches real post metrics from Instagram Graph API.

Collects engagement data (likes, comments, saves, shares, reach, impressions)
for published posts and account-level metrics (follower growth, profile views).
"""

from datetime import datetime, timezone
from typing import Optional

from src.instagram.graph_api_client import InstagramGraphAPI
from src.core.logging_config import get_logger, log_error

logger = get_logger("analytics.insights_collector")


class InsightsCollector:
    """
    Fetches Instagram Insights data via the official Graph API.

    Usage:
        collector = InsightsCollector(access_token="token123", ig_user_id="17841...")
        metrics = await collector.fetch_post_metrics(media_id="12345")
        account = await collector.fetch_account_insights()
    """

    def __init__(self, access_token: str = "", ig_user_id: str = ""):
        self._api = InstagramGraphAPI(access_token=access_token, ig_user_id=ig_user_id)
        self._access_token = access_token
        self._ig_user_id = ig_user_id

    async def fetch_post_metrics(self, media_id: str) -> dict:
        """
        Fetch engagement metrics for a single post.

        Args:
            media_id: Instagram media ID

        Returns:
            Dict with likes, comments, saves, shares, reach, impressions
        """
        try:
            metrics = await self._api.get_media_insights(
                media_id=media_id,
                metrics=["likes", "comments", "saved", "shares", "reach", "impressions"],
            )
            logger.info("Fetched metrics for media %s", media_id)
            return metrics
        except Exception as e:
            log_error("analytics.insights", "fetch_post_metrics", e, context={"media_id": media_id})
            return {}

    async def fetch_account_insights(self, period: str = "day") -> dict:
        """
        Fetch account-level metrics.

        Args:
            period: Time period ("day", "week", "days_28", "month", "lifetime")

        Returns:
            Dict with follower_count, profile_views, reach, impressions
        """
        try:
            insights = await self._api.get_account_insights(
                metrics=["follower_count", "profile_views", "reach", "impressions"],
                period=period,
            )
            logger.info("Fetched account insights for period '%s'", period)
            return insights
        except Exception as e:
            log_error("analytics.insights", "fetch_account_insights", e)
            return {}

    async def fetch_metrics_for_recent_posts(self, limit: int = 25) -> list[dict]:
        """
        Fetch metrics for the most recent published posts.

        Args:
            limit: Number of recent posts to fetch

        Returns:
            List of dicts with media_id + metrics
        """
        try:
            media_list = await self._api.get_user_media(limit=limit)
            results = []
            for media in media_list:
                media_id = media.get("id")
                if media_id:
                    metrics = await self.fetch_post_metrics(media_id)
                    metrics["media_id"] = media_id
                    metrics["caption"] = media.get("caption", "")[:100]
                    metrics["timestamp"] = media.get("timestamp", "")
                    results.append(metrics)
            logger.info("Fetched metrics for %d recent posts", len(results))
            return results
        except Exception as e:
            log_error("analytics.insights", "fetch_recent_posts", e)
            return []

    async def save_to_db(self, media_id: str, metrics: dict) -> None:
        """Persist post metrics to the PostMetrics DB table."""
        try:
            from src.database.connection import async_session_factory
            from src.database.models import PostMetrics

            async with async_session_factory() as session:
                record = PostMetrics(
                    media_id=media_id,
                    likes=metrics.get("likes", 0),
                    comments=metrics.get("comments", 0),
                    saves=metrics.get("saved", 0),
                    shares=metrics.get("shares", 0),
                    reach=metrics.get("reach", 0),
                    impressions=metrics.get("impressions", 0),
                    fetched_at=datetime.now(timezone.utc),
                )
                session.add(record)
                await session.commit()
            logger.info("Saved metrics for media %s to DB", media_id)
        except Exception as e:
            log_error("analytics.insights", "save_to_db", e)
