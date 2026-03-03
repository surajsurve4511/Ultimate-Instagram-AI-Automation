"""
Pydantic schemas for Gemini structured output.

These schemas are passed to Gemini's structured output feature to ensure
consistent, parseable JSON responses from all AI calls.

Docs: https://ai.google.dev/gemini-api/docs/structured-output
"""

from typing import Optional
from pydantic import BaseModel, Field


# ========== Content Generation Schemas ==========

class ContentPlan(BaseModel):
    """Structured output for a complete Instagram post plan."""
    caption: str = Field(description="The Instagram caption text, engaging and on-brand")
    hashtags: list[str] = Field(description="List of relevant hashtags (10-30)")
    call_to_action: str = Field(description="Clear call-to-action for the audience")
    alt_text: str = Field(description="Descriptive alt text for accessibility")
    content_type: str = Field(description="One of: IMAGE, CAROUSEL, REELS, STORIES")
    funnel_stage: str = Field(description="One of: TOFU, MOFU, BOFU, RETENTION")
    estimated_engagement: str = Field(description="LOW, MEDIUM, HIGH, or VIRAL")


class CarouselSlide(BaseModel):
    """A single slide in a carousel post."""
    slide_number: int = Field(description="Slide position (1-10)")
    headline: str = Field(description="Bold headline text for the slide")
    body_text: str = Field(description="Body content for the slide")
    image_prompt: str = Field(description="Detailed prompt for generating the slide image")


class CarouselPlan(BaseModel):
    """Structured output for a carousel post."""
    title: str = Field(description="Overall carousel title/theme")
    caption: str = Field(description="The Instagram caption for the carousel post")
    hashtags: list[str] = Field(description="Relevant hashtags")
    call_to_action: str = Field(description="CTA for the carousel")
    slides: list[CarouselSlide] = Field(description="List of carousel slides (3-10)")
    funnel_stage: str = Field(description="One of: TOFU, MOFU, BOFU, RETENTION")


# ========== Image Generation Schemas ==========

class ImagePrompt(BaseModel):
    """Structured prompt for AI image generation via Nano Banana."""
    scene_description: str = Field(description="Detailed description of the scene to generate")
    style: str = Field(description="Visual style, e.g. 'minimalist tech', 'vibrant gradient'")
    mood: str = Field(description="Emotional mood, e.g. 'inspiring', 'professional', 'playful'")
    colors: list[str] = Field(description="Dominant color palette to use")
    text_overlay: Optional[str] = Field(default=None, description="Text to include in the image, if any")
    aspect_ratio: str = Field(default="1:1", description="Aspect ratio: 1:1, 4:5, 9:16")


# ========== Research & Trends Schemas ==========

class TrendAnalysis(BaseModel):
    """Structured output for a single trend analysis."""
    trend_name: str = Field(description="Name/title of the trend")
    description: str = Field(description="Brief description of the trend")
    relevance_score: float = Field(description="Relevance to user's niche, 0.0-1.0")
    virality_potential: str = Field(description="LOW, MEDIUM, HIGH, or VIRAL")
    suggested_angles: list[str] = Field(description="Content angles to cover this trend")
    timeliness: str = Field(description="BREAKING, TRENDING, EMERGING, EVERGREEN")
    source_urls: list[str] = Field(default=[], description="URLs where this trend was found")


class TrendReport(BaseModel):
    """A batch of trend analyses."""
    trends: list[TrendAnalysis] = Field(description="List of analyzed trends")
    summary: str = Field(description="Overall summary of the trend landscape")
    recommended_priority: list[str] = Field(description="Trend names ordered by priority to cover")


# ========== Brand Voice Schemas ==========

class BrandVoiceProfile(BaseModel):
    """Structured profile of a user's brand voice and content strategy."""
    brand_voice: str = Field(description="Description of the brand's tone and personality")
    content_pillars: list[str] = Field(description="3-5 main content themes/topics")
    target_audience: str = Field(description="Description of the ideal audience")
    tone_keywords: list[str] = Field(description="Keywords that define the tone")
    forbidden_words: list[str] = Field(description="Words/phrases to never use")
    emoji_style: str = Field(description="minimal, moderate, or heavy")
    example_caption: str = Field(description="An example caption in the brand's voice")
    posting_frequency: int = Field(description="Recommended posts per day")
    best_content_types: list[str] = Field(description="Best content types for this niche")


# ========== Analytics Schemas ==========

class EngagementPrediction(BaseModel):
    """AI-predicted engagement metrics for content."""
    predicted_engagement_rate: float = Field(description="Predicted engagement rate 0-100%")
    predicted_likes_range: str = Field(description="Estimated likes range, e.g. '50-100'")
    predicted_saves_range: str = Field(description="Estimated saves range")
    confidence: float = Field(description="Confidence in prediction, 0.0-1.0")
    reasoning: str = Field(description="Explanation of the prediction")
    improvement_suggestions: list[str] = Field(description="How to improve the content")


class PerformanceInsight(BaseModel):
    """AI analysis of post/account performance."""
    key_finding: str = Field(description="Main insight discovered")
    data_basis: str = Field(description="What data supports this finding")
    recommendation: str = Field(description="Actionable recommendation")
    priority: str = Field(description="LOW, MEDIUM, HIGH")


class StrategyRecommendation(BaseModel):
    """AI-generated strategy recommendation."""
    current_assessment: str = Field(description="Assessment of current performance")
    recommendations: list[str] = Field(description="List of specific recommendations")
    content_mix_adjustment: Optional[dict] = Field(
        default=None, description="Suggested changes to content mix percentages"
    )
    priority_topics: list[str] = Field(description="Topics to prioritize")
    avoid_topics: list[str] = Field(description="Topics to avoid or reduce")
