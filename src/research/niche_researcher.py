"""
Niche Researcher — Deep-dives into a user's niche using Google Search + Gemini.

Builds a "niche knowledge graph" to inform content strategy.
Identifies content gaps, audience pain points, and strategic opportunities.
"""

import logging
from typing import Optional

from src.ai.gemini_brain import GeminiBrain
from src.ai import prompts

logger = logging.getLogger(__name__)


class NicheResearcher:
    """
    Deep research engine for understanding a user's niche.
    
    Uses Gemini + Google Search to build comprehensive niche knowledge
    that feeds into content strategy and the user's brain/memory.
    
    Usage:
        researcher = NicheResearcher(brain)
        insights = researcher.research_niche(
            niche="AI education",
            target_audience="aspiring AI engineers",
            content_pillars=["tutorials", "tools", "news"]
        )
    """

    def __init__(self, brain: Optional[GeminiBrain] = None):
        self._brain = brain or GeminiBrain()

    def research_niche(
        self,
        niche: str,
        target_audience: str,
        content_pillars: list[str],
        *,
        existing_knowledge: str = "No prior knowledge.",
    ) -> str:
        """
        Comprehensive niche research using Google Search grounding.
        
        Args:
            niche: The niche to research
            target_audience: Target audience description
            content_pillars: Main content themes
            existing_knowledge: What the system already knows
            
        Returns:
            Detailed niche analysis text
        """
        logger.info(f"Researching niche: {niche}")

        system_prompt = prompts.NICHE_RESEARCH.format(
            niche=niche,
            target_audience=target_audience,
            content_pillars=", ".join(content_pillars),
            existing_knowledge=existing_knowledge,
        )

        query = (
            f"Research the {niche} niche for Instagram content strategy. "
            f"What content performs best? What are content gaps? "
            f"What are the audience pain points for {target_audience}?"
        )

        return self._brain.search_web(
            query,
            system_instruction=system_prompt,
        )

    def find_content_gaps(
        self,
        niche: str,
        target_audience: str,
    ) -> str:
        """
        Identify content gaps — what competitors aren't covering.
        
        Returns:
            Analysis of underserved topics and content opportunities
        """
        query = (
            f"In the {niche} niche on Instagram, what topics and content types "
            f"are underserved? What questions does {target_audience} have that "
            f"no one is answering well? What content gaps exist?"
        )

        return self._brain.search_web(
            query,
            system_instruction=(
                f"You are a market research analyst specializing in {niche}. "
                f"Identify specific content opportunities that are being missed "
                f"by current Instagram creators in this space."
            ),
        )

    def map_audience_interests(
        self,
        niche: str,
        target_audience: str,
    ) -> str:
        """
        Map the target audience's interests, pain points, and desires.
        
        Returns:
            Audience interests map
        """
        query = (
            f"What does {target_audience} in the {niche} space care about most? "
            f"What are their biggest challenges, goals, and interests? "
            f"What Instagram content would they find most valuable?"
        )

        return self._brain.search_web(
            query,
            system_instruction=(
                "You are an audience research specialist. Build a detailed "
                "profile of this audience's interests, pain points, goals, "
                "and content consumption preferences on Instagram."
            ),
        )

    def research_hashtag_strategy(
        self,
        niche: str,
    ) -> str:
        """
        Research effective hashtag strategies for the niche.
        
        Returns:
            Hashtag strategy recommendations
        """
        query = (
            f"What are the most effective hashtag strategies for {niche} "
            f"content on Instagram in 2026? Include specific hashtag categories: "
            f"broad reach, niche-specific, community, and trending hashtags."
        )

        return self._brain.search_web(
            query,
            system_instruction=(
                "You are an Instagram hashtag strategist. Provide specific, "
                "actionable hashtag recommendations backed by current best practices."
            ),
        )

    def research_best_posting_times(
        self,
        niche: str,
        target_audience: str,
    ) -> str:
        """
        Research optimal posting times for the niche and audience.
        
        Returns:
            Posting time recommendations
        """
        query = (
            f"What are the best times to post on Instagram for {niche} content "
            f"targeting {target_audience}? Include day-of-week and time-of-day "
            f"recommendations based on current engagement data."
        )

        return self._brain.search_web(
            query,
            system_instruction=(
                "You are a social media timing analyst. Provide specific "
                "posting time recommendations based on current Instagram "
                "engagement patterns for this niche."
            ),
        )
