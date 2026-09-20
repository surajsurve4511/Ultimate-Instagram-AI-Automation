"""
Content Factory — Orchestrates the full content creation pipeline.

This is the top-level content generation entry point:
1. Pick topic (from trends, calendar, or user input)
2. Determine content type
3. Generate text + images
4. Quality check
5. Store as GeneratedContent (DRAFT)
"""

import logging
import time
from typing import Optional

from src.ai.gemini_brain import GeminiBrain
from src.ai.schemas import ContentPlan
from src.content_gen.text_generator import TextGenerator
from src.content_gen.image_generator import ImageGenerator
from src.content_gen.carousel_builder import CarouselBuilder
from src.core.logging_config import get_logger

logger = get_logger("content_gen.factory")


class ContentFactory:
    """
    Top-level orchestrator for content creation.
    
    Usage:
        factory = ContentFactory(brain)
        content = factory.create_post(
            topic="AI in Healthcare",
            niche="AI education",
            brand_voice="Helpful educator",
            ...
        )
    """

    def __init__(self, brain: Optional[GeminiBrain] = None):
        self._brain = brain or GeminiBrain()
        self._text_gen = TextGenerator(self._brain)
        self._image_gen = ImageGenerator(self._brain)
        self._carousel_builder = CarouselBuilder(self._brain)

    def create_post(
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
        visual_style: str = "clean, modern, professional",
        color_palette: list[str] | None = None,
        generate_images: bool = True,
    ) -> dict:
        """
        Create a complete Instagram post (text + image).
        
        Args:
            topic: What the post is about
            niche, brand_voice, etc: Brand context
            content_type: IMAGE, CAROUSEL, REELS, or STORIES
            generate_images: Whether to generate images
            
        Returns:
            Dict with 'plan' (ContentPlan), 'image_paths' (list)
        """
        logger.info(f"Creating {content_type} post about: {topic}")

        # Route to carousel builder if needed
        if content_type == "CAROUSEL":
            return self._create_carousel(
                topic,
                niche=niche,
                brand_voice=brand_voice,
                target_audience=target_audience,
                tone_keywords=tone_keywords,
                funnel_stage=funnel_stage,
                visual_style=visual_style,
                generate_images=generate_images,
            )

        # Generate text content
        plan = self._text_gen.generate_post(
            topic,
            niche=niche,
            brand_voice=brand_voice,
            target_audience=target_audience,
            tone_keywords=tone_keywords,
            emoji_style=emoji_style,
            forbidden_words=forbidden_words,
            funnel_stage=funnel_stage,
            content_type=content_type,
        )

        image_paths = []

        # Generate image
        if generate_images and content_type in ("IMAGE", "STORIES"):
            try:
                aspect_ratio = "9:16" if content_type == "STORIES" else "1:1"
                path = self._image_gen.generate_post_image(
                    topic,
                    niche=niche,
                    visual_style=visual_style,
                    color_palette=color_palette,
                    caption_preview=plan.caption[:200],
                    content_type=content_type,
                    aspect_ratio=aspect_ratio,
                )
                image_paths.append(path)
            except Exception as e:
                logger.error(f"Image generation failed: {e}")

        return {
            "plan": plan,
            "image_paths": image_paths,
            "content_type": content_type,
            "funnel_stage": funnel_stage,
            "topic": topic,
            "quality_score": self._quality_check(plan, niche, target_audience),
        }

    def _quality_check(self, plan: ContentPlan, niche: str, audience: str) -> float:
        """
        Run an AI quality check on generated content.
        Returns score 0.0-1.0. Scores below 0.6 indicate low quality.
        """
        try:
            prompt = (
                f"Rate this Instagram post on a scale of 0.0 to 1.0.\n"
                f"Niche: {niche} | Audience: {audience}\n"
                f"Caption: {plan.caption[:500]}\n"
                f"Hashtags: {', '.join(plan.hashtags[:10])}\n"
                f"CTA: {plan.call_to_action}\n\n"
                f"Score ONLY based on: relevance, engagement potential, "
                f"caption quality, hashtag mix. Return ONLY a number like 0.85"
            )
            result = self._brain.generate_text_lite(prompt)
            score = float(result.strip().split()[0])
            score = max(0.0, min(1.0, score))  # Clamp
            logger.info("Quality check: %.2f for topic '%s'", score, plan.caption[:50])
            return score
        except Exception:
            return 0.75  # Default if quality check fails

    def _create_carousel(
        self,
        topic: str,
        **kwargs,
    ) -> dict:
        """Create a carousel post."""
        result = self._carousel_builder.build_carousel(topic, **kwargs)
        carousel_plan = result["plan"]

        return {
            "plan": ContentPlan(
                caption=carousel_plan.caption,
                hashtags=carousel_plan.hashtags,
                call_to_action=carousel_plan.call_to_action,
                alt_text=f"Carousel about {topic}",
                content_type="CAROUSEL",
                funnel_stage=carousel_plan.funnel_stage,
                estimated_engagement="HIGH",
            ),
            "carousel_plan": carousel_plan,
            "image_paths": result["image_paths"],
            "content_type": "CAROUSEL",
            "funnel_stage": carousel_plan.funnel_stage,
            "topic": topic,
        }

    def create_batch(
        self,
        topics: list[dict],
        *,
        niche: str = "technology",
        brand_voice: str = "professional",
        target_audience: str = "tech enthusiasts",
        generate_images: bool = True,
    ) -> list[dict]:
        """
        Generate multiple posts in batch.
        
        Args:
            topics: List of dicts with 'topic', optional 'content_type', 'funnel_stage'
            niche, brand_voice, target_audience: Brand context
            generate_images: Whether to generate images
            
        Returns:
            List of created content dicts
        """
        results = []
        for item in topics:
            try:
                result = self.create_post(
                    item["topic"],
                    niche=niche,
                    brand_voice=brand_voice,
                    target_audience=target_audience,
                    content_type=item.get("content_type", "IMAGE"),
                    funnel_stage=item.get("funnel_stage", "TOFU"),
                    generate_images=generate_images,
                )
                results.append(result)
                logger.info(f"Batch: created post {len(results)}/{len(topics)}")
            except Exception as e:
                logger.error(f"Batch: failed for topic '{item['topic']}': {e}")

        return results

    def suggest_topics(
        self,
        niche: str,
        target_audience: str,
        content_pillars: list[str],
        *,
        count: int = 7,
    ) -> list[str]:
        """
        Suggest content topics for the week.
        
        Args:
            niche: Account niche
            target_audience: Audience description
            content_pillars: Main content themes
            count: Number of topics
            
        Returns:
            List of suggested topics
        """
        prompt = (
            f"Suggest {count} specific Instagram post topics for a {niche} account "
            f"targeting {target_audience}.\n\n"
            f"Content pillars: {', '.join(content_pillars)}\n\n"
            f"Mix: 40% TOFU (viral/reach), 30% MOFU (educational), "
            f"15% BOFU (conversion), 15% RETENTION (community).\n\n"
            f"Return only the topics, one per line. Be specific and timely."
        )
        
        result = self._brain.search_web(prompt)
        topics = [t.strip() for t in result.strip().split("\n") if t.strip()]
        return topics[:count]
