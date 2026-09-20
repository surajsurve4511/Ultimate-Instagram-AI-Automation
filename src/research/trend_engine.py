"""
Trend Engine — Discovers and analyzes trending topics using Gemini + Google Search.

Replaces all web scrapers (BeautifulSoup, Selenium, pytrends, tweepy, feedparser)
and Perplexity API with the built-in Google Search grounding tool.

Docs: https://ai.google.dev/gemini-api/docs/google-search
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from src.ai.gemini_brain import GeminiBrain
from src.ai.schemas import TrendAnalysis, TrendReport
from src.ai import prompts
from src.core.logging_config import get_logger, log_error

logger = get_logger("research.trend_engine")


class TrendEngine:
    """
    Discovers trending topics using Gemini + Google Search grounding.
    
    Instead of scraping 8+ websites, we use Gemini's built-in Google Search
    tool to find and analyze trends in real-time. This is:
    - More reliable (no scraper breakage)
    - More comprehensive (Google's full index)
    - More intelligent (Gemini analyzes relevance)
    - Fully legal (official API)
    
    Usage:
        engine = TrendEngine(brain)
        trends = engine.discover_trends(
            niche="AI education",
            target_audience="aspiring AI engineers",
            content_pillars=["tutorials", "tools", "news"]
        )
    """

    def __init__(self, brain: Optional[GeminiBrain] = None):
        self._brain = brain or GeminiBrain()

    def discover_trends(
        self,
        niche: str,
        target_audience: str,
        content_pillars: list[str],
        *,
        max_trends: int = 10,
    ) -> TrendReport:
        """
        Discover current trending topics relevant to the user's niche.
        
        Uses Google Search grounding to find real-time trends, then
        Gemini analyzes them for relevance and suggests content angles.
        
        Args:
            niche: The account's content niche
            target_audience: Description of the target audience
            content_pillars: Main content themes
            max_trends: Maximum number of trends to return
            
        Returns:
            TrendReport with ranked, analyzed trends
        """
        logger.info(f"Discovering trends for niche: {niche}")

        system_prompt = prompts.RESEARCH_TRENDS.format(
            niche=niche,
            target_audience=target_audience,
            content_pillars=", ".join(content_pillars),
        )

        query = (
            f"What are the latest trending topics in {niche} right now? "
            f"Include breaking news, viral discussions, upcoming events, "
            f"and emerging trends. Focus on what will be relevant to "
            f"{target_audience}. Find at most {max_trends} trends."
        )

        result = self._brain.search_web(
            query,
            system_instruction=system_prompt,
            schema=TrendReport,
        )

        if isinstance(result, TrendReport):
            logger.info(f"Found {len(result.trends)} trends")
            return result
        
        # Fallback: if structured output failed, parse manually
        logger.warning("Structured output failed for trends, using text response")
        return TrendReport(
            trends=[],
            summary=str(result),
            recommended_priority=[],
        )

    def find_viral_content(
        self,
        niche: str,
        *,
        platform: str = "Instagram",
    ) -> str:
        """
        Find currently viral content formats and ideas in the niche.
        
        Args:
            niche: Content niche
            platform: Social platform to focus on
            
        Returns:
            Analysis of viral content patterns
        """
        query = (
            f"What types of {platform} content are going viral right now "
            f"in the {niche} space? What formats, hooks, and styles are "
            f"getting the most engagement? Include specific examples."
        )

        return self._brain.search_web(
            query,
            system_instruction=(
                f"You are a viral content analyst for {platform}. "
                f"Identify specific content patterns that are driving "
                f"high engagement right now. Be specific with examples."
            ),
        )

    def monitor_competitors(
        self,
        niche: str,
        competitor_accounts: list[str],
    ) -> str:
        """
        Analyze what competitors are posting and what's working.
        
        Args:
            niche: Content niche
            competitor_accounts: List of competitor Instagram handles
            
        Returns:
            Competitive analysis text
        """
        accounts_str = ", ".join(f"@{a}" for a in competitor_accounts)
        
        query = (
            f"What content strategies are working for these Instagram accounts "
            f"in the {niche} niche: {accounts_str}? What types of posts are "
            f"getting the most engagement? What can we learn from them?"
        )

        return self._brain.search_web(
            query,
            system_instruction=(
                "You are a competitive intelligence analyst for Instagram. "
                "Analyze the content strategies of these accounts and identify "
                "what's working, what's not, and what opportunities exist."
            ),
        )

    def find_upcoming_events(
        self,
        niche: str,
        *,
        days_ahead: int = 30,
    ) -> str:
        """
        Find upcoming events, launches, and announcements in the niche.
        Being ahead of events = being ahead of trends.
        
        Args:
            niche: Content niche
            days_ahead: How many days to look ahead
            
        Returns:
            Upcoming events analysis
        """
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        
        query = (
            f"What major events, product launches, conferences, or announcements "
            f"are happening in the {niche} space in the next {days_ahead} days "
            f"after {today}? Include dates and significance."
        )

        return self._brain.search_web(
            query,
            system_instruction=(
                f"You are an events researcher for the {niche} industry. "
                f"Find upcoming events that would be relevant for Instagram "
                f"content creation. Focus on events that will generate buzz."
            ),
        )

    def analyze_single_topic(
        self,
        topic: str,
        niche: str,
        target_audience: str,
    ) -> TrendAnalysis:
        """
        Deep-analyze a single topic for content potential.
        
        Args:
            topic: The topic to analyze
            niche: Account niche
            target_audience: Target audience
            
        Returns:
            Detailed TrendAnalysis
        """
        query = (
            f"Analyze this topic for Instagram content potential: '{topic}'. "
            f"The account is in the {niche} niche targeting {target_audience}. "
            f"How trending is this? What content angles could work? "
            f"What's the virality potential on Instagram?"
        )

        result = self._brain.search_web(
            query,
            system_instruction=(
                "You are an Instagram content strategist. Deeply analyze "
                "this topic for its potential as Instagram content. Consider "
                "timeliness, audience interest, and virality potential."
            ),
            schema=TrendAnalysis,
        )

        if isinstance(result, TrendAnalysis):
            return result
        
        return TrendAnalysis(
            trend_name=topic,
            description=str(result),
            relevance_score=0.5,
            virality_potential="MEDIUM",
            suggested_angles=["General overview"],
            timeliness="TRENDING",
            source_urls=[],
        )

    async def save_to_db(self, trends: TrendReport, niche: str) -> int:
        """
        Persist discovered trends to TrendSnapshot DB table.

        Args:
            trends: Discovered trend report
            niche: The niche these trends are for

        Returns:
            Number of trends saved
        """
        try:
            from src.database.connection import async_session_factory
            from src.database.models import TrendSnapshot

            saved = 0
            async with async_session_factory() as session:
                for trend in trends.trends:
                    snapshot = TrendSnapshot(
                        niche=niche,
                        trend_name=trend.trend_name,
                        description=trend.description,
                        relevance_score=trend.relevance_score,
                        virality_potential=trend.virality_potential,
                        suggested_angles=str(trend.suggested_angles),
                        source_urls=str(trend.source_urls),
                        discovered_at=datetime.now(timezone.utc),
                    )
                    session.add(snapshot)
                    saved += 1
                await session.commit()

            logger.info("Saved %d trends to DB for niche '%s'", saved, niche)
            return saved
        except Exception as e:
            log_error("research.trend_engine", "save_to_db", e)
            return 0
