"""
Text Generator — Creates Instagram captions, hashtags, CTAs, and alt text.

All text is personalized to the user's brand voice and goals using
Gemini structured output.
"""

import logging
from typing import Optional

from src.ai.gemini_brain import GeminiBrain
from src.ai.schemas import ContentPlan
from src.ai import prompts

logger = logging.getLogger(__name__)


class TextGenerator:
    """
    Generates Instagram text content shaped by the user's brand context.
    
    Usage:
        gen = TextGenerator(brain)
        plan = gen.generate_post(
            topic="OpenAI releases GPT-5",
            niche="AI education",
            brand_voice="Professional but approachable",
            ...
        )
    """

    def __init__(self, brain: Optional[GeminiBrain] = None):
        self._brain = brain or GeminiBrain()

    def generate_post(
        self,
        topic: str,
        *,
        niche: str = "technology",
        brand_voice: str = "professional and engaging",
        target_audience: str = "tech enthusiasts",
        tone_keywords: list[str] | None = None,
        emoji_style: str = "moderate",
        forbidden_words: list[str] | None = None,
        funnel_stage: str = "TOFU",
        content_type: str = "IMAGE",
        extra_context: str = "",
    ) -> ContentPlan:
        """
        Generate a complete Instagram post plan.
        
        Args:
            topic: What the post is about
            niche: Account niche
            brand_voice: Brand voice description
            target_audience: Target audience description
            tone_keywords: Tone-defining keywords
            emoji_style: minimal, moderate, or heavy
            forbidden_words: Words to never use
            funnel_stage: TOFU, MOFU, BOFU, or RETENTION
            content_type: IMAGE, CAROUSEL, REELS, or STORIES
            extra_context: Additional context for generation
            
        Returns:
            ContentPlan with caption, hashtags, CTA, alt text
        """
        prompt = prompts.GENERATE_CAPTION.format(
            niche=niche,
            brand_voice=brand_voice,
            target_audience=target_audience,
            tone_keywords=", ".join(tone_keywords or ["engaging"]),
            emoji_style=emoji_style,
            topic=topic,
            funnel_stage=funnel_stage,
            content_type=content_type,
            forbidden_words=", ".join(forbidden_words or []),
            extra_context=extra_context,
        )

        result = self._brain.generate_creative(prompt, schema=ContentPlan)

        if isinstance(result, ContentPlan):
            logger.info(f"Generated post for topic: {topic[:50]}")
            return result

        # Fallback
        logger.warning("Structured output failed, returning basic plan")
        return ContentPlan(
            caption=str(result),
            hashtags=[],
            call_to_action="",
            alt_text="",
            content_type=content_type,
            funnel_stage=funnel_stage,
            estimated_engagement="MEDIUM",
        )

    def enhance_caption(
        self,
        caption: str,
        *,
        brand_voice: str = "professional",
        improvement_focus: str = "engagement",
    ) -> str:
        """
        Enhance an existing caption to improve quality.
        
        Args:
            caption: Original caption
            brand_voice: Brand voice to maintain
            improvement_focus: What to improve (engagement, clarity, hook, cta)
            
        Returns:
            Enhanced caption text
        """
        prompt = (
            f"Improve this Instagram caption. Focus on: {improvement_focus}\n\n"
            f"Brand voice: {brand_voice}\n\n"
            f"Original caption:\n{caption}\n\n"
            f"Provide only the improved caption, nothing else."
        )
        return self._brain.generate_creative(prompt)

    def generate_hashtags(
        self,
        caption: str,
        niche: str,
        *,
        count: int = 20,
    ) -> list[str]:
        """
        Generate optimized hashtags for a caption.
        
        Uses the lite model for cost efficiency.
        
        Args:
            caption: The post caption
            niche: Account niche
            count: Number of hashtags
            
        Returns:
            List of hashtag strings (with # prefix)
        """
        prompt = (
            f"Generate exactly {count} Instagram hashtags for this post in the {niche} niche.\n\n"
            f"Caption: {caption[:500]}\n\n"
            f"Rules:\n"
            f"- Mix of broad (>1M posts), medium (100K-1M), and niche (<100K)\n"
            f"- All must be relevant to the content\n"
            f"- Include # prefix\n"
            f"- Return only the hashtags, one per line"
        )
        
        result = self._brain.generate_text_lite(prompt)
        hashtags = [
            tag.strip() for tag in result.strip().split("\n")
            if tag.strip().startswith("#")
        ]
        return hashtags[:count]

    def generate_alt_text(
        self,
        image_description: str,
        caption: str,
    ) -> str:
        """
        Generate accessible alt text for an image.
        
        Args:
            image_description: Description of the image
            caption: The post caption for context
            
        Returns:
            Descriptive alt text (max 250 chars)
        """
        prompt = (
            f"Write Instagram alt text for this image (max 250 chars).\n"
            f"Image: {image_description}\n"
            f"Caption context: {caption[:200]}\n"
            f"Be descriptive and accessible. Return only the alt text."
        )
        result = self._brain.generate_text_lite(prompt)
        return result.strip()[:250]
