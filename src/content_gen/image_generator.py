"""
Image Generator — Creates Instagram visuals using Nano Banana (Gemini native image gen).

Replaces PIL-based text overlays with AI-generated images.
All images are saved as JPEG for Instagram compatibility.

Docs: https://ai.google.dev/gemini-api/docs/image-generation
"""

import logging
import os
from pathlib import Path
from typing import Optional

from src.ai.gemini_brain import GeminiBrain
from src.ai.schemas import ImagePrompt
from src.ai import prompts
from src.config.settings import SETTINGS

logger = logging.getLogger(__name__)


class ImageGenerator:
    """
    Generates Instagram images using Nano Banana (Gemini native image gen).
    
    Usage:
        gen = ImageGenerator(brain)
        path = gen.generate_post_image(
            topic="AI in Healthcare",
            niche="AI education",
            visual_style="clean, modern, tech"
        )
    """

    def __init__(self, brain: Optional[GeminiBrain] = None):
        self._brain = brain or GeminiBrain()
        self._output_dir = Path(SETTINGS.IMAGES_STORAGE_PATH)
        self._output_dir.mkdir(parents=True, exist_ok=True)

    def generate_post_image(
        self,
        topic: str,
        *,
        niche: str = "technology",
        visual_style: str = "clean, modern, professional",
        color_palette: list[str] | None = None,
        caption_preview: str = "",
        content_type: str = "IMAGE",
        aspect_ratio: str = "1:1",
        filename: Optional[str] = None,
    ) -> str:
        """
        Generate an image for an Instagram post.
        
        Args:
            topic: Post topic
            niche: Account niche
            visual_style: Visual style preferences
            color_palette: Preferred colors
            caption_preview: Caption text for context
            content_type: IMAGE, CAROUSEL, REELS, or STORIES
            aspect_ratio: 1:1 (square), 4:5 (portrait), 9:16 (story/reel)
            filename: Custom filename (auto-generated if not provided)
            
        Returns:
            Path to the saved JPEG image
        """
        # First, get a detailed image prompt from Gemini
        prompt_request = prompts.GENERATE_IMAGE_PROMPT.format(
            niche=niche,
            visual_style=visual_style,
            color_palette=", ".join(color_palette or ["blue", "white", "neutral"]),
            topic=topic,
            caption_preview=caption_preview[:200],
            content_type=content_type,
            aspect_ratio=aspect_ratio,
        )

        image_prompt_obj = self._brain.analyze(prompt_request, schema=ImagePrompt)

        if isinstance(image_prompt_obj, ImagePrompt):
            full_prompt = (
                f"{image_prompt_obj.scene_description}. "
                f"Style: {image_prompt_obj.style}. "
                f"Mood: {image_prompt_obj.mood}. "
                f"Colors: {', '.join(image_prompt_obj.colors)}."
            )
            if image_prompt_obj.text_overlay:
                full_prompt += f" Include text: '{image_prompt_obj.text_overlay}'."
        else:
            full_prompt = (
                f"Create a visually striking Instagram image about '{topic}'. "
                f"Style: {visual_style}. Aspect ratio: {aspect_ratio}."
            )

        # Generate the image using Nano Banana
        if not filename:
            import time
            filename = f"post_{int(time.time())}.jpg"

        save_path = str(self._output_dir / filename)

        self._brain.generate_image(
            full_prompt,
            aspect_ratio=aspect_ratio,
            save_path=save_path,
        )

        logger.info(f"Generated image: {save_path}")
        return save_path

    def generate_carousel_slides(
        self,
        slide_prompts: list[str],
        *,
        visual_style: str = "consistent, clean, modern",
        aspect_ratio: str = "1:1",
        prefix: str = "carousel",
    ) -> list[str]:
        """
        Generate multiple images for a carousel post.
        
        Args:
            slide_prompts: List of prompts, one per slide
            visual_style: Consistent style for all slides
            aspect_ratio: Aspect ratio for all slides
            prefix: Filename prefix
            
        Returns:
            List of paths to saved images
        """
        import time
        
        paths = []
        timestamp = int(time.time())

        for i, prompt in enumerate(slide_prompts):
            full_prompt = (
                f"{prompt}. "
                f"Style: {visual_style}. "
                f"This is slide {i + 1} of {len(slide_prompts)} in a carousel. "
                f"Maintain visual consistency across all slides."
            )
            
            filename = f"{prefix}_{timestamp}_slide{i + 1}.jpg"
            save_path = str(self._output_dir / filename)

            try:
                self._brain.generate_image(
                    full_prompt,
                    aspect_ratio=aspect_ratio,
                    save_path=save_path,
                )
                paths.append(save_path)
                logger.info(f"Generated carousel slide {i + 1}: {save_path}")
            except Exception as e:
                logger.error(f"Failed to generate slide {i + 1}: {e}")

        return paths

    def generate_from_prompt(
        self,
        prompt: str,
        *,
        aspect_ratio: str = "1:1",
        filename: Optional[str] = None,
    ) -> str:
        """
        Generate an image from a raw prompt (no preprocessing).
        
        Args:
            prompt: Direct image generation prompt
            aspect_ratio: Aspect ratio
            filename: Output filename
            
        Returns:
            Path to saved image
        """
        import time
        
        if not filename:
            filename = f"custom_{int(time.time())}.jpg"
        
        save_path = str(self._output_dir / filename)
        self._brain.generate_image(prompt, aspect_ratio=aspect_ratio, save_path=save_path)
        
        logger.info(f"Generated custom image: {save_path}")
        return save_path
