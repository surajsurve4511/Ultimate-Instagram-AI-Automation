"""
Advanced Gemini AI Engine — The Central Brain of the Automation System.

Upgraded to Gemini 2.0 Flash with:
  - Structured JSON output for consistent content generation
  - Marketing psychology integration (AIDA, Cialdini triggers)
  - Multi-format content generation (caption, carousel, reel scripts)
  - Content analysis and scoring via AI
  - Funnel-stage-aware generation (TOFU/MOFU/BOFU)
  - A/B variant creation for testing
  - Image prompt generation for Imagen
"""
import os
import json
import logging
import hashlib
from typing import Tuple, Dict, List, Optional
from datetime import datetime

import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import numpy as np

from src.content.categories import ContentItem, ContentCategory, CONTENT_TEMPLATES
from src.config.settings import SETTINGS

logger = logging.getLogger(__name__)


# ─── Structured Output Schemas ─────────────────────────────────────────────────

INSTAGRAM_POST_SCHEMA = {
    "type": "object",
    "properties": {
        "hook": {
            "type": "string",
            "description": "A powerful 1-line opening hook (pattern interrupt) to stop the scroll"
        },
        "caption": {
            "type": "string",
            "description": "The main caption body (150-250 words), educational yet engaging"
        },
        "cta": {
            "type": "string",
            "description": "A clear call-to-action encouraging engagement (comment, save, share)"
        },
        "question": {
            "type": "string",
            "description": "An engaging question to boost comments"
        },
        "hashtags": {
            "type": "array",
            "items": {"type": "string"},
            "description": "10-15 relevant hashtags mixing popular and niche"
        },
        "image_description": {
            "type": "string",
            "description": "Detailed visual description for AI image generation"
        },
        "emotional_trigger": {
            "type": "string",
            "enum": ["curiosity", "fear_of_missing_out", "aspiration", "surprise", "urgency", "belonging"],
            "description": "Primary emotional trigger used in the caption"
        },
        "funnel_stage": {
            "type": "string",
            "enum": ["tofu", "mofu", "bofu", "retention"],
            "description": "Marketing funnel stage this content targets"
        },
        "viral_score": {
            "type": "number",
            "description": "Self-assessed viral potential score from 0 to 1"
        }
    },
    "required": ["hook", "caption", "cta", "question", "hashtags", "image_description",
                  "emotional_trigger", "funnel_stage", "viral_score"]
}

CAROUSEL_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string", "description": "Carousel title for the cover slide"},
        "hook": {"type": "string", "description": "Opening hook for the caption"},
        "slides": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "heading": {"type": "string"},
                    "body": {"type": "string"},
                    "visual_note": {"type": "string"}
                }
            },
            "description": "5-10 slides with heading, body text, and visual description"
        },
        "caption": {"type": "string"},
        "cta": {"type": "string"},
        "hashtags": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["title", "hook", "slides", "caption", "cta", "hashtags"]
}

CONTENT_ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "quality_score": {"type": "number", "description": "Overall quality 0-1"},
        "engagement_potential": {"type": "number", "description": "Predicted engagement 0-1"},
        "viral_potential": {"type": "number", "description": "Viral potential 0-1"},
        "emotional_impact": {"type": "string"},
        "improvement_suggestions": {
            "type": "array",
            "items": {"type": "string"}
        },
        "best_posting_time": {"type": "string"},
        "target_audience_fit": {"type": "number", "description": "How well it fits AI education audience 0-1"}
    },
    "required": ["quality_score", "engagement_potential", "viral_potential",
                  "emotional_impact", "improvement_suggestions", "target_audience_fit"]
}

AB_VARIANT_SCHEMA = {
    "type": "object",
    "properties": {
        "variant_a": {
            "type": "object",
            "properties": {
                "hook": {"type": "string"},
                "caption": {"type": "string"},
                "cta": {"type": "string"},
                "style": {"type": "string", "description": "Description of the tone/approach"}
            }
        },
        "variant_b": {
            "type": "object",
            "properties": {
                "hook": {"type": "string"},
                "caption": {"type": "string"},
                "cta": {"type": "string"},
                "style": {"type": "string"}
            }
        },
        "hypothesis": {
            "type": "string",
            "description": "What this A/B test is designed to learn"
        }
    },
    "required": ["variant_a", "variant_b", "hypothesis"]
}

CAMPAIGN_STRATEGY_SCHEMA = {
    "type": "object",
    "properties": {
        "campaign_name": {"type": "string"},
        "objective": {"type": "string"},
        "duration_days": {"type": "integer"},
        "phases": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "phase_name": {"type": "string"},
                    "days": {"type": "string"},
                    "content_types": {"type": "array", "items": {"type": "string"}},
                    "psychology_triggers": {"type": "array", "items": {"type": "string"}},
                    "posting_frequency": {"type": "string"},
                    "kpis": {"type": "array", "items": {"type": "string"}}
                }
            }
        },
        "hashtag_strategy": {"type": "array", "items": {"type": "string"}},
        "success_criteria": {"type": "object"}
    },
    "required": ["campaign_name", "objective", "duration_days", "phases",
                  "hashtag_strategy", "success_criteria"]
}


# ─── Main Gemini Engine ────────────────────────────────────────────────────────

class GeminiContentGenerator:
    """
    Advanced Gemini AI engine that serves as the central brain for all
    content generation, analysis, and strategic decision-making.
    """

    def __init__(self):
        self.api_key = SETTINGS.GEMINI_API_KEY
        if self.api_key:
            genai.configure(api_key=self.api_key)
            # Primary model: Gemini 2.0 Flash for speed + quality
            self.model = genai.GenerativeModel(
                model_name=SETTINGS.GEMINI_MODEL,
                generation_config=genai.GenerationConfig(
                    temperature=SETTINGS.GEMINI_TEMPERATURE,
                    max_output_tokens=SETTINGS.GEMINI_MAX_TOKENS,
                    response_mime_type="application/json",
                ),
            )
            # Flexible text model for non-JSON tasks
            self.text_model = genai.GenerativeModel(
                model_name=SETTINGS.GEMINI_MODEL,
                generation_config=genai.GenerationConfig(
                    temperature=SETTINGS.GEMINI_TEMPERATURE,
                    max_output_tokens=SETTINGS.GEMINI_MAX_TOKENS,
                ),
            )
            logger.info(f"✅ Gemini engine initialized with model: {SETTINGS.GEMINI_MODEL}")
        else:
            self.model = None
            self.text_model = None
            logger.warning("⚠️ Gemini API key not set. AI generation will use fallbacks.")

    # ─── Core Content Generation ───────────────────────────────────────────

    def generate_post_content(self, content_item: ContentItem,
                               funnel_stage: str = "tofu",
                               psychology_trigger: str = "curiosity") -> Dict:
        """
        Generate a complete Instagram post using Gemini structured output.
        Incorporates marketing psychology and funnel-stage awareness.
        """
        try:
            template_config = CONTENT_TEMPLATES.get(
                content_item.category, CONTENT_TEMPLATES[ContentCategory.AI_NEWS]
            )

            prompt = f"""You are an elite social media marketer and viral content strategist 
for an AI education Instagram account (@_ai_multiverse_) with a growing audience.

Generate an Instagram post for this content:

TOPIC: {content_item.title}
DESCRIPTION: {content_item.description}
CATEGORY: {content_item.category.value}
SOURCE: {content_item.source_url}

MARKETING CONTEXT:
- Funnel stage: {funnel_stage.upper()} ({"awareness & reach" if funnel_stage == "tofu" else "engagement & education" if funnel_stage == "mofu" else "conversion & action" if funnel_stage == "bofu" else "loyalty & community"})
- Primary psychology trigger: {psychology_trigger}
- Target audience: Tech enthusiasts, AI learners, developers, students aged 18-35

REQUIREMENTS:
1. HOOK: Write a scroll-stopping first line using the {psychology_trigger} trigger. 
   Use pattern interrupts like "Stop scrolling if...", bold claims, or curiosity gaps.
2. CAPTION: 150-250 words. Apply the AIDA model:
   - Attention: The hook
   - Interest: Unique angle on the topic
   - Desire: What the reader gains / FOMO / social proof
   - Action: Clear CTA
3. Use Cialdini's principles where natural: reciprocity (give value), social proof 
   (mention community), scarcity (limited knowledge), authority (expert positioning)
4. HASHTAGS: Mix 5 high-volume + 5 niche + 3 branded hashtags
5. IMAGE: Describe a visually striking, Instagram-optimized image concept
6. Score your own viral potential honestly (0-1)

Return valid JSON matching the Instagram post schema."""

            response = self.model.generate_content(prompt)
            result = json.loads(response.text)

            # Validate and ensure all required fields
            result = self._validate_post_result(result, content_item, template_config)
            logger.info(f"✅ Generated post content: {result.get('hook', '')[:60]}...")
            return result

        except Exception as e:
            logger.error(f"❌ Gemini generation failed: {e}")
            return self.create_fallback_content(content_item)

    def generate_carousel_content(self, topic: str, num_slides: int = 7,
                                   style: str = "educational") -> Dict:
        """Generate a multi-slide carousel post with storytelling arc."""
        try:
            prompt = f"""You are creating a viral Instagram carousel for an AI education account.

TOPIC: {topic}
NUMBER OF SLIDES: {num_slides}
STYLE: {style}

Create a carousel that tells a STORY — not just a list. Use this structure:
- Slide 1: Cover with bold, curiosity-driven title
- Slides 2-{num_slides-1}: Progressive revelation, each slide building on the last.
  Use the "open loop" technique — end each slide with a reason to swipe.
- Final slide: CTA slide with actionable takeaway

For each slide, include:
- A punchy heading (max 8 words)
- Body text (max 30 words — it's a slide, not an essay)
- Visual note describing what the slide should look like

Apply the CURIOSITY GAP: headline promises something, content delivers piece by piece.

Return valid JSON matching the carousel schema."""

            response = self.model.generate_content(prompt)
            result = json.loads(response.text)
            logger.info(f"✅ Generated carousel: {result.get('title', '')}")
            return result

        except Exception as e:
            logger.error(f"❌ Carousel generation failed: {e}")
            return self._fallback_carousel(topic)

    def generate_reel_script(self, topic: str, duration_seconds: int = 30) -> Dict:
        """Generate a reel script with hook, body, and CTA."""
        try:
            prompt = f"""Create a viral Instagram Reel script about: {topic}

Duration: {duration_seconds} seconds
Account: AI education (@_ai_multiverse_)

Structure:
- HOOK (0-3 sec): Pattern interrupt — something unexpected that stops scrolling
- BODY (3-{duration_seconds-5} sec): Deliver value fast, use visual cuts
- CTA ({duration_seconds-5}-{duration_seconds} sec): Clear action (follow, save, comment)

Return JSON with:
{{
  "hook_text": "...",
  "hook_visual": "description of what's shown",
  "body_segments": [
    {{"text": "...", "visual": "...", "duration_sec": N}}
  ],
  "cta_text": "...",
  "cta_visual": "...",
  "caption": "full reel caption",
  "hashtags": ["..."],
  "trending_audio_suggestion": "...",
  "estimated_viral_score": 0.0
}}"""

            response = self.model.generate_content(prompt)
            return json.loads(response.text)

        except Exception as e:
            logger.error(f"❌ Reel script generation failed: {e}")
            return {"hook_text": topic, "caption": topic, "hashtags": ["#AI", "#Tech"]}

    # ─── Content Analysis & Scoring ────────────────────────────────────────

    def analyze_content_quality(self, caption: str, hashtags: List[str] = None,
                                 image_description: str = None) -> Dict:
        """
        AI-powered content quality analysis.
        Replaces heuristic scoring with Gemini intelligence.
        """
        try:
            hashtag_str = " ".join(hashtags) if hashtags else "none provided"
            img_str = image_description or "no image description"

            prompt = f"""You are an Instagram content analyst for an AI education account. 
Analyze this post CRITICALLY and honestly:

CAPTION:
{caption}

HASHTAGS: {hashtag_str}
IMAGE CONCEPT: {img_str}

Evaluate on:
1. quality_score (0-1): Grammar, clarity, value delivered, professionalism
2. engagement_potential (0-1): Likelihood of likes, comments, saves
3. viral_potential (0-1): Likelihood of shares and reaching explore page
4. emotional_impact: Which emotion does this trigger and how strongly?
5. improvement_suggestions: 3-5 specific, actionable improvements
6. best_posting_time: Optimal time to post this (e.g., "Tuesday 6 PM IST")
7. target_audience_fit (0-1): How well it fits AI-interested 18-35 demographic

Be HONEST — don't inflate scores. Average Instagram posts score 0.3-0.5.
Only truly exceptional content scores above 0.8.

Return valid JSON matching the content analysis schema."""

            response = self.model.generate_content(prompt)
            result = json.loads(response.text)
            logger.info(f"📊 Content analysis: quality={result.get('quality_score')}, "
                        f"engagement={result.get('engagement_potential')}, "
                        f"viral={result.get('viral_potential')}")
            return result

        except Exception as e:
            logger.error(f"❌ Content analysis failed: {e}")
            return {
                "quality_score": 0.5,
                "engagement_potential": 0.5,
                "viral_potential": 0.3,
                "emotional_impact": "neutral",
                "improvement_suggestions": ["Could not analyze — using defaults"],
                "target_audience_fit": 0.5
            }

    def score_and_improve(self, content: Dict) -> Dict:
        """Score content and return improved version if below threshold."""
        analysis = self.analyze_content_quality(
            caption=content.get("caption", ""),
            hashtags=content.get("hashtags", []),
            image_description=content.get("image_description", "")
        )

        content["analysis"] = analysis

        # If quality is below threshold, ask Gemini to improve it
        if analysis.get("quality_score", 0) < SETTINGS.MIN_ENGAGEMENT_SCORE:
            logger.info("📝 Content below quality threshold — requesting improvement...")
            try:
                improve_prompt = f"""Improve this Instagram caption. It scored {analysis['quality_score']}/1.0.

CURRENT CAPTION:
{content.get('caption', '')}

ISSUES:
{json.dumps(analysis.get('improvement_suggestions', []))}

Write an IMPROVED version that addresses all issues.
Keep the same topic but make it more engaging, add a stronger hook,
better CTA, and more value for the reader.

Return JSON with: {{"improved_caption": "...", "improved_hook": "...", "improved_cta": "..."}}"""

                response = self.model.generate_content(improve_prompt)
                improvements = json.loads(response.text)

                content["caption"] = improvements.get("improved_caption", content["caption"])
                content["hook"] = improvements.get("improved_hook", content.get("hook", ""))
                content["cta"] = improvements.get("improved_cta", content.get("cta", ""))
                content["was_improved"] = True
                logger.info("✅ Content improved successfully")

            except Exception as e:
                logger.warning(f"⚠️ Improvement failed: {e}")

        return content

    # ─── A/B Testing ──────────────────────────────────────────────────────

    def generate_ab_variants(self, topic: str, category: str = "ai_news") -> Dict:
        """Generate A/B test variants for a topic to learn what works best."""
        try:
            prompt = f"""Create two DISTINCTLY DIFFERENT Instagram post variants for A/B testing.

TOPIC: {topic}
CATEGORY: {category}
ACCOUNT: AI education (@_ai_multiverse_)

VARIANT A should use: Direct, educational tone with data/facts
VARIANT B should use: Emotional, storytelling tone with curiosity gaps

Each variant needs: hook, caption (150-200 words), and CTA.
Also state your HYPOTHESIS: what is this test designed to learn?

Example hypothesis: "Emotional hooks drive 2x more saves than factual hooks for AI news"

Return valid JSON with variant_a, variant_b, and hypothesis."""

            response = self.model.generate_content(prompt)
            result = json.loads(response.text)
            logger.info(f"🔬 Generated A/B variants. Hypothesis: {result.get('hypothesis', '')[:60]}...")
            return result

        except Exception as e:
            logger.error(f"❌ A/B variant generation failed: {e}")
            return {
                "variant_a": {"hook": topic, "caption": topic, "cta": "Follow for more!", "style": "educational"},
                "variant_b": {"hook": f"You won't believe what's happening in {topic}!", "caption": topic, "cta": "Save this!", "style": "emotional"},
                "hypothesis": "Testing educational vs emotional tone"
            }

    # ─── Campaign Strategy Generation ─────────────────────────────────────

    def generate_campaign_strategy(self, topic: str, duration_days: int = 7,
                                    goal: str = "follower_growth") -> Dict:
        """Generate a complete marketing campaign strategy using Gemini."""
        try:
            prompt = f"""You are a senior social media strategist designing a campaign 
for an AI education Instagram account.

CAMPAIGN BRIEF:
- Topic: {topic}
- Duration: {duration_days} days
- Primary goal: {goal}
- Account: @_ai_multiverse_ (AI education, tech-savvy audience 18-35)

Design a COMPLETE campaign strategy with:
1. Campaign name (catchy, memorable)
2. Clear objective statement
3. Phases (e.g., teaser → launch → sustain → wrap-up)
4. For each phase:
   - Which content types (post, carousel, reel, story)
   - Psychology triggers to use (curiosity, FOMO, social proof, etc.)
   - Posting frequency
   - KPIs to track
5. Hashtag strategy (branded + trending + niche)
6. Clear success criteria with numbers

Apply growth hacking principles:
- Viral loops (share to unlock)
- Engagement loops (comment to participate)
- Series hooks (episode-based content)

Return valid JSON matching the campaign strategy schema."""

            response = self.model.generate_content(prompt)
            result = json.loads(response.text)
            logger.info(f"🎯 Generated campaign: {result.get('campaign_name', '')}")
            return result

        except Exception as e:
            logger.error(f"❌ Campaign strategy generation failed: {e}")
            return self._fallback_campaign(topic, duration_days)

    # ─── Hashtag Intelligence ─────────────────────────────────────────────

    def optimize_hashtags(self, caption: str, category: str,
                           current_hashtags: List[str] = None) -> Dict:
        """AI-powered hashtag optimization for maximum reach."""
        try:
            current = " ".join(current_hashtags) if current_hashtags else "none"
            prompt = f"""Optimize hashtags for this Instagram post:

CAPTION SUMMARY: {caption[:200]}
CATEGORY: {category}
CURRENT HASHTAGS: {current}

Create 3 tiers:
1. HIGH VOLUME (5 tags): >1M posts, for broad reach (e.g., #AI, #Technology)
2. MEDIUM NICHE (5 tags): 100K-1M posts, for targeted reach
3. MICRO NICHE (5 tags): <100K posts, for ranking on explore page

Also suggest:
- 2 branded hashtags for the account
- Current trending hashtags related to AI (if applicable)

Return JSON:
{{
  "high_volume": ["..."],
  "medium_niche": ["..."],
  "micro_niche": ["..."],
  "branded": ["..."],
  "trending": ["..."],
  "recommended_order": ["all 15+ hashtags in optimal order"]
}}"""

            response = self.model.generate_content(prompt)
            return json.loads(response.text)

        except Exception as e:
            logger.error(f"❌ Hashtag optimization failed: {e}")
            return {
                "recommended_order": current_hashtags or ["#AI", "#MachineLearning", "#Tech",
                    "#ArtificialIntelligence", "#Innovation"]
            }

    # ─── Psychology-Driven Hook Generator ─────────────────────────────────

    def generate_hooks(self, topic: str, count: int = 5,
                        triggers: List[str] = None) -> List[Dict]:
        """Generate multiple scroll-stopping hooks using psychology triggers."""
        try:
            trigger_list = triggers or ["curiosity", "fomo", "surprise", "authority", "belonging"]
            prompt = f"""Generate {count} DIFFERENT scroll-stopping Instagram hooks about: {topic}

Each hook should use a DIFFERENT psychology trigger from: {', '.join(trigger_list)}

A great hook:
- Is 1 sentence (max 15 words)
- Creates an irresistible urge to keep reading
- Uses pattern interrupt (unexpected statement)
- Examples: "99% of developers are using AI wrong.", "This free tool replaced my $500/month subscription."

Return JSON:
{{
  "hooks": [
    {{"text": "...", "trigger": "which psychology trigger", "power_score": 0.0-1.0}}
  ]
}}"""

            response = self.model.generate_content(prompt)
            result = json.loads(response.text)
            return result.get("hooks", [])

        except Exception as e:
            logger.error(f"❌ Hook generation failed: {e}")
            return [{"text": f"🚀 {topic}", "trigger": "curiosity", "power_score": 0.5}]

    # ─── Image Generation ─────────────────────────────────────────────────

    def generate_image_prompt(self, content_item: ContentItem,
                                style: str = "modern") -> str:
        """Generate a detailed, high-quality image prompt for AI image generation."""
        try:
            prompt = f"""Create a detailed image generation prompt for an Instagram post.

TOPIC: {content_item.title}
CATEGORY: {content_item.category.value}
STYLE: {style}

The prompt should describe:
1. Subject/scene (what is visually shown)
2. Color palette (vibrant, harmonious — blues, purples, cyans for tech)
3. Composition (Instagram 1:1 square format)
4. Mood/atmosphere (professional, futuristic, inspiring)
5. Typography space (leave room for text overlay)
6. Style reference (digital art, cinematic, minimalist, etc.)

Write a single paragraph image prompt (100-150 words), ready to be used 
directly with an image generation model.

Return JSON: {{"prompt": "...", "negative_prompt": "things to avoid", "style_tags": ["..."]}}"""

            response = self.model.generate_content(prompt)
            result = json.loads(response.text)
            return result.get("prompt", f"Modern digital illustration of {content_item.title}")

        except Exception as e:
            logger.error(f"❌ Image prompt generation failed: {e}")
            return f"Modern AI technology illustration for {content_item.title}, " \
                   f"digital art style, vibrant blue and purple gradient, 1:1 format"

    def create_text_overlay_image(self, background_color: tuple, text: str,
                                    subtitle: str = "",
                                    size: tuple = (1080, 1080),
                                    brand_name: str = "@_ai_multiverse_") -> Image.Image:
        """Create a professional text overlay image with gradient and branding."""
        img = Image.new('RGB', size, background_color)
        draw = ImageDraw.Draw(img)

        # Create gradient background
        for y in range(size[1]):
            factor = y / size[1]
            r = int(background_color[0] * (1 - factor * 0.6))
            g = int(background_color[1] * (1 - factor * 0.4))
            b = int(background_color[2] * (1 - factor * 0.2))
            draw.line([(0, y), (size[0], y)], fill=(max(0, r), max(0, g), max(0, b)))

        # Add subtle geometric pattern overlay
        for i in range(0, size[0], 80):
            for j in range(0, size[1], 80):
                opacity = int(20 + (i + j) % 30)
                draw.ellipse([i-2, j-2, i+2, j+2],
                             fill=(255, 255, 255, opacity) if opacity > 30 else None)

        # Load fonts with fallback
        try:
            title_font = ImageFont.truetype("arial.ttf", 72)
            subtitle_font = ImageFont.truetype("arial.ttf", 36)
            brand_font = ImageFont.truetype("arial.ttf", 28)
        except (OSError, IOError):
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            brand_font = ImageFont.load_default()

        # Word wrap title text
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=title_font)
            if bbox[2] - bbox[0] <= size[0] - 120:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))

        # Center text vertically
        line_height = 85
        total_height = len(lines) * line_height + (60 if subtitle else 0)
        start_y = (size[1] - total_height) // 2 - 30

        # Draw title lines with shadow
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=title_font)
            text_width = bbox[2] - bbox[0]
            x = (size[0] - text_width) // 2
            y = start_y + (i * line_height)

            # Shadow
            draw.text((x + 3, y + 3), line, font=title_font, fill=(0, 0, 0, 100))
            # Main text
            draw.text((x, y), line, font=title_font, fill='white')

        # Draw subtitle
        if subtitle:
            sub_y = start_y + len(lines) * line_height + 20
            bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
            sub_x = (size[0] - (bbox[2] - bbox[0])) // 2
            draw.text((sub_x, sub_y), subtitle, font=subtitle_font, fill=(200, 200, 255))

        # Add brand watermark at bottom
        brand_text = brand_name
        bbox = draw.textbbox((0, 0), brand_text, font=brand_font)
        brand_x = (size[0] - (bbox[2] - bbox[0])) // 2
        brand_y = size[1] - 60
        draw.text((brand_x, brand_y), brand_text, font=brand_font, fill=(255, 255, 255, 150))

        # Add accent line at top
        draw.rectangle([0, 0, size[0], 6], fill=(100, 200, 255))

        return img

    # ─── Fallback Methods ─────────────────────────────────────────────────

    def create_fallback_caption(self, content_item: ContentItem) -> str:
        """Create fallback caption if Gemini fails."""
        template_config = CONTENT_TEMPLATES.get(
            content_item.category, CONTENT_TEMPLATES[ContentCategory.AI_NEWS]
        )
        hashtags_str = " ".join(template_config["hashtags"])

        return template_config["template"].format(
            title=content_item.title,
            description=content_item.description[:150] + "...",
            hashtags=hashtags_str,
            source_url=content_item.source_url
        )

    def create_fallback_content(self, content_item: ContentItem) -> Dict:
        """Create complete fallback content when Gemini is unavailable."""
        template_config = CONTENT_TEMPLATES.get(
            content_item.category, CONTENT_TEMPLATES[ContentCategory.AI_NEWS]
        )

        return {
            "hook": f"🚀 {content_item.title}",
            "caption": self.create_fallback_caption(content_item),
            "cta": "Follow @_ai_multiverse_ for daily AI insights! 🤖",
            "question": "What do you think about this? Share your thoughts! 💭",
            "hashtags": template_config["hashtags"],
            "image_description": f"AI technology illustration for {content_item.category.value}",
            "emotional_trigger": "curiosity",
            "funnel_stage": "tofu",
            "viral_score": 0.4
        }

    def _validate_post_result(self, result: Dict, content_item: ContentItem,
                                template_config: Dict) -> Dict:
        """Ensure all required fields exist in the post result."""
        defaults = {
            "hook": f"🚀 {content_item.title}",
            "caption": self.create_fallback_caption(content_item),
            "cta": "Follow for more AI insights! 🤖",
            "question": "What are your thoughts? 💭",
            "hashtags": template_config["hashtags"],
            "image_description": f"Modern AI illustration for {content_item.title}",
            "emotional_trigger": "curiosity",
            "funnel_stage": "tofu",
            "viral_score": 0.5
        }

        for key, default in defaults.items():
            if key not in result or not result[key]:
                result[key] = default

        return result

    def _fallback_carousel(self, topic: str) -> Dict:
        """Fallback carousel content."""
        return {
            "title": f"🧠 {topic}",
            "hook": f"Everything you need to know about {topic} 👇",
            "slides": [
                {"heading": "Introduction", "body": f"Let's explore {topic}", "visual_note": "Cover slide"},
                {"heading": "Key Facts", "body": "Here's what you should know", "visual_note": "Fact slide"},
                {"heading": "Why It Matters", "body": "This changes everything", "visual_note": "Impact slide"},
                {"heading": "What's Next", "body": "The future looks exciting", "visual_note": "Future slide"},
                {"heading": "Take Action", "body": "Save this for later! 💾", "visual_note": "CTA slide"},
            ],
            "caption": f"Everything about {topic} in 5 slides! Save for later 💾",
            "cta": "Follow @_ai_multiverse_ for daily AI insights!",
            "hashtags": ["#AI", "#MachineLearning", "#Tech", "#AIEducation", "#Innovation"]
        }

    def _fallback_campaign(self, topic: str, duration_days: int) -> Dict:
        """Fallback campaign strategy."""
        return {
            "campaign_name": f"AI Deep Dive: {topic}",
            "objective": f"Educate audience about {topic} and grow followers",
            "duration_days": duration_days,
            "phases": [
                {
                    "phase_name": "Teaser",
                    "days": "1-2",
                    "content_types": ["post", "story"],
                    "psychology_triggers": ["curiosity"],
                    "posting_frequency": "2x daily",
                    "kpis": ["reach", "saves"]
                },
                {
                    "phase_name": "Launch",
                    "days": f"3-{duration_days}",
                    "content_types": ["carousel", "reel", "post"],
                    "psychology_triggers": ["authority", "social_proof"],
                    "posting_frequency": "3x daily",
                    "kpis": ["engagement_rate", "follower_growth"]
                }
            ],
            "hashtag_strategy": ["#AI", "#MachineLearning", "#AIEducation", "#Tech"],
            "success_criteria": {
                "min_engagement_rate": "5%",
                "target_followers_gained": 100,
                "min_saves_per_post": 20
            }
        }


# ─── Convenience Functions ─────────────────────────────────────────────────────

def generate_image_and_description(topic: str) -> Tuple[str, str]:
    """Main function to generate image and description for Instagram post."""
    generator = GeminiContentGenerator()

    from src.content.categories import ContentItem, ContentCategory
    from datetime import datetime
    import hashlib

    content_item = ContentItem(
        title=topic,
        description=f"Latest updates and insights about {topic}",
        category=ContentCategory.AI_NEWS,
        source_url="https://example.com",
        content_hash=hashlib.md5(topic.encode()).hexdigest(),
        engagement_score=0.8,
        created_at=datetime.now().isoformat(),
        tags=["ai", "technology", "innovation"]
    )

    # Generate content with marketing psychology
    post_content = generator.generate_post_content(
        content_item,
        funnel_stage="tofu",
        psychology_trigger="curiosity"
    )

    # Score and potentially improve the content
    post_content = generator.score_and_improve(post_content)

    # Create branded image
    colors = [
        (30, 60, 180),   # Deep blue
        (100, 40, 200),  # Purple
        (20, 120, 180),  # Teal
        (180, 40, 100),  # Magenta
    ]
    background_color = colors[hash(topic) % len(colors)]

    img = generator.create_text_overlay_image(
        background_color,
        topic[:60],
        subtitle="Swipe to learn more →" if len(topic) > 30 else ""
    )

    # Save image
    os.makedirs(SETTINGS.IMAGES_STORAGE_PATH, exist_ok=True)
    image_path = os.path.join(SETTINGS.IMAGES_STORAGE_PATH, f"post_{hashlib.md5(topic.encode()).hexdigest()[:8]}.png")
    img.save(image_path)

    # Format final description
    hook = post_content.get('hook', '')
    caption = post_content.get('caption', '')
    cta = post_content.get('cta', '')
    question = post_content.get('question', '')
    hashtags = ' '.join(post_content.get('hashtags', []))

    final_description = f"{hook}\n\n{caption}\n\n{question}\n\n{cta}\n\n{hashtags}"

    return image_path, final_description


# Global instance
gemini_engine = GeminiContentGenerator()
