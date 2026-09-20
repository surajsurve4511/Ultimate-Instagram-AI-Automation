"""
Marketing Psychology Engine — Applies behavioral science to Instagram content.

Integrates AIDA framework, Cialdini's principles, and funnel-aware messaging
to create psychologically compelling content.
"""

import logging
from typing import Optional

from src.ai.gemini_brain import GeminiBrain
from src.ai import prompts

logger = logging.getLogger(__name__)


class MarketingEngine:
    """
    Applies marketing psychology to content.
    
    Frameworks:
    - AIDA (Attention, Interest, Desire, Action)
    - Cialdini's 6 Principles (Reciprocity, Commitment, Social Proof, Authority, Liking, Scarcity)
    - Funnel-aware messaging (TOFU → BOFU)
    """

    def __init__(self, gemini: Optional[GeminiBrain] = None):
        self._gemini = gemini or GeminiBrain()

    def apply_psychology(
        self,
        content: str,
        *,
        niche: str = "technology",
        target_audience: str = "professionals",
        funnel_stage: str = "TOFU",
    ) -> str:
        """
        Enhance content with psychological triggers.
        
        Args:
            content: Original caption/CTA
            niche: Account niche
            target_audience: Target audience
            funnel_stage: Current funnel stage
            
        Returns:
            Enhanced content with psychology applied
        """
        prompt = prompts.APPLY_PSYCHOLOGY.format(
            content=content,
            niche=niche,
            target_audience=target_audience,
            funnel_stage=funnel_stage,
        )
        return self._gemini.generate_creative(prompt)

    def generate_hook(
        self,
        topic: str,
        *,
        niche: str = "technology",
        hook_type: str = "curiosity",
    ) -> str:
        """
        Generate a scroll-stopping hook for a post.
        
        Args:
            topic: Post topic
            niche: Account niche
            hook_type: Type of hook (curiosity, controversy, stat, story, challenge)
            
        Returns:
            Hook text (first line of caption)
        """
        prompt = (
            f"Generate a scroll-stopping Instagram hook for: {topic}\n"
            f"Niche: {niche}\n"
            f"Hook type: {hook_type}\n\n"
            f"This is the FIRST LINE of the caption and must:\n"
            f"- Break the user's scroll pattern\n"
            f"- Create immediate curiosity or emotion\n"
            f"- Be under 125 characters (shows in preview)\n"
            f"- Not be clickbait — it must deliver on the promise\n\n"
            f"Return only the hook text."
        )
        return self._gemini.generate_creative(prompt)

    def create_cta(
        self,
        funnel_stage: str,
        *,
        action_type: str = "engage",
    ) -> str:
        """
        Generate a funnel-appropriate call-to-action.
        
        Args:
            funnel_stage: TOFU, MOFU, BOFU, or RETENTION
            action_type: engage, save, share, follow, buy, click
            
        Returns:
            CTA text
        """
        cta_frameworks = {
            "TOFU": "Focus on getting engagement: likes, comments, follows. Low commitment.",
            "MOFU": "Focus on saves and shares: valuable content worth bookmarking.",
            "BOFU": "Focus on conversion: link in bio, sign up, buy, download.",
            "RETENTION": "Focus on community: DMs, questions, user-generated content.",
        }

        framework = cta_frameworks.get(funnel_stage, cta_frameworks["TOFU"])

        prompt = (
            f"Generate an Instagram call-to-action.\n"
            f"Funnel stage: {funnel_stage}\n"
            f"Desired action: {action_type}\n"
            f"Framework: {framework}\n"
            f"Return only the CTA text (2-3 lines max)."
        )
        return self._gemini.generate_creative(prompt)

    def score_virality(self, caption: str, *, niche: str = "general") -> dict:
        """
        Score a caption's viral potential.
        
        Returns:
            Dict with 'score' (0-10), 'factors', 'improvements'
        """
        prompt = (
            f"Score this Instagram caption's viral potential (0-10) for the {niche} niche:\n\n"
            f"{caption}\n\n"
            f"Assess:\n"
            f"1. Hook strength (0-10)\n"
            f"2. Emotional trigger (0-10)\n"
            f"3. Shareability (0-10)\n"
            f"4. Save-worthiness (0-10)\n"
            f"5. Comment-bait (0-10)\n"
            f"6. Overall virality score (0-10)\n\n"
            f"Return as JSON with 'scores', 'overall', and 'improvements' keys."
        )
        
        result = self._gemini.analyze(prompt)
        # Return raw text — can be parsed by caller if structured output is needed
        return {"analysis": result}
