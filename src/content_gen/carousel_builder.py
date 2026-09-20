"""
Carousel Builder — Generates multi-slide carousel content.

Creates complete carousel posts with narrative flow across slides,
matching text and images for each slide.
"""

import logging
from typing import Optional

from src.ai.gemini_brain import GeminiBrain
from src.ai.schemas import CarouselPlan
from src.ai import prompts
from src.content_gen.image_generator import ImageGenerator

logger = logging.getLogger(__name__)


class CarouselBuilder:
    """
    Builds complete carousel posts with text + images for each slide.
    
    Usage:
        builder = CarouselBuilder(brain)
        carousel = builder.build_carousel(
            topic="5 AI Tools You Must Try",
            niche="AI education",
            brand_voice="Helpful educator"
        )
    """

    def __init__(self, brain: Optional[GeminiBrain] = None):
        self._brain = brain or GeminiBrain()
        self._image_gen = ImageGenerator(self._brain)

    def plan_carousel(
        self,
        topic: str,
        *,
        niche: str = "technology",
        brand_voice: str = "professional",
        target_audience: str = "tech enthusiasts",
        tone_keywords: list[str] | None = None,
        funnel_stage: str = "MOFU",
    ) -> CarouselPlan:
        """
        Generate a carousel content plan with slides.
        
        Args:
            topic: Carousel topic/theme
            niche: Account niche
            brand_voice: Brand voice
            target_audience: Target audience
            tone_keywords: Tone keywords
            funnel_stage: Funnel stage
            
        Returns:
            CarouselPlan with slides, caption, hashtags
        """
        prompt = prompts.GENERATE_CAROUSEL.format(
            niche=niche,
            brand_voice=brand_voice,
            target_audience=target_audience,
            tone_keywords=", ".join(tone_keywords or ["informative"]),
            topic=topic,
            funnel_stage=funnel_stage,
        )

        result = self._brain.generate_creative(prompt, schema=CarouselPlan)

        if isinstance(result, CarouselPlan):
            logger.info(f"Carousel plan created: {len(result.slides)} slides")
            return result

        return CarouselPlan(
            title=topic,
            caption=str(result),
            hashtags=[],
            call_to_action="",
            slides=[],
            funnel_stage=funnel_stage,
        )

    def build_carousel(
        self,
        topic: str,
        *,
        niche: str = "technology",
        brand_voice: str = "professional",
        target_audience: str = "tech enthusiasts",
        tone_keywords: list[str] | None = None,
        funnel_stage: str = "MOFU",
        visual_style: str = "clean, modern, consistent",
        generate_images: bool = True,
    ) -> dict:
        """
        Build a complete carousel with plan + images.
        
        Args:
            topic: Carousel topic
            niche, brand_voice, etc: Brand context
            visual_style: Visual style for images
            generate_images: Whether to generate images
            
        Returns:
            Dict with 'plan' (CarouselPlan), 'image_paths' (list of str)
        """
        # Step 1: Generate the text plan
        plan = self.plan_carousel(
            topic,
            niche=niche,
            brand_voice=brand_voice,
            target_audience=target_audience,
            tone_keywords=tone_keywords,
            funnel_stage=funnel_stage,
        )

        image_paths = []

        # Step 2: Generate images for each slide
        if generate_images and plan.slides:
            slide_prompts = [slide.image_prompt for slide in plan.slides]
            image_paths = self._image_gen.generate_carousel_slides(
                slide_prompts,
                visual_style=visual_style,
            )

        return {
            "plan": plan,
            "image_paths": image_paths,
        }
