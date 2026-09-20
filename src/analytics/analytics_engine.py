"""
Analytics Engine — Fetches Instagram Insights and analyzes performance with Gemini.

Uses Instagram Graph API Insights endpoints to fetch metrics,
then feeds them to Gemini for intelligent analysis and recommendations.

Ref: https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-media/insights
"""

import logging
from typing import Optional

import httpx

from src.ai.gemini_brain import GeminiBrain
from src.ai.schemas import PerformanceInsight, StrategyRecommendation, EngagementPrediction
from src.ai import prompts
from src.config.settings import SETTINGS

logger = logging.getLogger(__name__)


class AnalyticsEngine:
    """
    Fetches IG Insights and uses Gemini for performance analysis.
    
    Usage:
        engine = AnalyticsEngine(brain, access_token, ig_user_id)
        metrics = await engine.fetch_post_metrics(media_id)
        analysis = engine.analyze_performance(all_metrics)
    """

    def __init__(
        self,
        gemini: Optional[GeminiBrain] = None,
        access_token: Optional[str] = None,
        ig_user_id: Optional[str] = None,
    ):
        self._gemini = gemini or GeminiBrain()
        self._access_token = access_token
        self._ig_user_id = ig_user_id
        self._api_version = SETTINGS.INSTAGRAM_GRAPH_API_VERSION
        self._base_url = f"{SETTINGS.INSTAGRAM_GRAPH_API_HOST}/{self._api_version}"

    async def fetch_post_metrics(self, media_id: str) -> dict:
        """
        Fetch engagement metrics for a specific post.
        
        Args:
            media_id: Instagram media ID
            
        Returns:
            Dict with likes, comments, saves, shares, reach, impressions
        """
        url = f"{self._base_url}/{media_id}/insights"
        params = {
            "metric": "likes,comments,saved,shares,reach,impressions",
            "access_token": self._access_token,
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        metrics = {}
        for item in data.get("data", []):
            metrics[item["name"]] = item["values"][0]["value"]

        return metrics

    async def fetch_account_insights(self, *, period: str = "day") -> dict:
        """
        Fetch account-level insights.
        
        Args:
            period: Time period (day, week, days_28, month)
            
        Returns:
            Account insight metrics
        """
        url = f"{self._base_url}/{self._ig_user_id}/insights"
        params = {
            "metric": "impressions,reach,follower_count,profile_views",
            "period": period,
            "access_token": self._access_token,
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()

    def analyze_performance(
        self,
        performance_data: str,
        *,
        niche: str = "technology",
        goals: str = "grow followers and engagement",
        follower_count: str = "unknown",
        content_pillars: list[str] | None = None,
    ) -> str:
        """
        Analyze performance data with Gemini.
        
        Args:
            performance_data: Formatted metrics data string
            niche: Account niche
            goals: User goals
            follower_count: Current follower count
            content_pillars: Content pillars
            
        Returns:
            Performance analysis text
        """
        system_prompt = prompts.ANALYZE_PERFORMANCE.format(
            performance_data=performance_data,
            niche=niche,
            goals=goals,
            follower_count=follower_count,
            content_pillars=", ".join(content_pillars or []),
        )

        return self._gemini.analyze(system_prompt)

    def predict_engagement(
        self,
        caption: str,
        content_type: str,
        niche: str,
        *,
        past_performance: str = "",
    ) -> EngagementPrediction:
        """
        Predict engagement for content before publishing.
        
        Returns:
            EngagementPrediction with predicted metrics
        """
        prompt = (
            f"Predict Instagram engagement for this post:\n\n"
            f"Content type: {content_type}\n"
            f"Niche: {niche}\n"
            f"Caption: {caption[:500]}\n\n"
            f"Past performance context: {past_performance or 'No data yet'}"
        )

        result = self._gemini.analyze(prompt, schema=EngagementPrediction)
        if isinstance(result, EngagementPrediction):
            return result

        return EngagementPrediction(
            predicted_engagement_rate=3.0,
            predicted_likes_range="20-50",
            predicted_saves_range="5-15",
            confidence=0.5,
            reasoning="Default prediction due to limited data.",
            improvement_suggestions=["Track more posts for better predictions"],
        )

    def quality_check(
        self,
        caption: str,
        hashtags: list[str],
        *,
        content_type: str = "IMAGE",
        target_audience: str = "",
        brand_voice: str = "",
    ) -> str:
        """
        Check content quality before publishing.
        
        Returns:
            Quality assessment with scores and PASS/FAIL
        """
        prompt = prompts.QUALITY_CHECK.format(
            caption=caption,
            hashtags=", ".join(hashtags),
            content_type=content_type,
            target_audience=target_audience or "general audience",
            brand_voice=brand_voice or "professional",
        )

        return self._gemini.analyze(prompt)
