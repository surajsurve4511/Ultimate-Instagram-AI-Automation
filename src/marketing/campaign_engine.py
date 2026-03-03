"""
Campaign Engine — Multi-day coordinated content campaigns.

Manages campaign lifecycle:
1. Create campaign with theme, duration, and goals
2. Auto-generate content for each day of the campaign
3. Mid-campaign adjustments based on performance
4. Post-campaign analysis and learnings
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from src.ai.gemini_brain import GeminiBrain
from src.marketing.funnel_mapper import FunnelMapper
from src.core.logging_config import get_logger, log_error

logger = get_logger("marketing.campaign_engine")


class Campaign:
    """Data class representing a campaign."""

    def __init__(
        self,
        name: str,
        theme: str,
        goal: str,
        duration_days: int,
        posts_per_day: int = 1,
        niche: str = "technology",
        target_audience: str = "general",
        brand_voice: str = "professional",
    ):
        self.name = name
        self.theme = theme
        self.goal = goal
        self.duration_days = duration_days
        self.posts_per_day = posts_per_day
        self.niche = niche
        self.target_audience = target_audience
        self.brand_voice = brand_voice
        self.start_date = None
        self.content_plan = []
        self.status = "DRAFT"


class CampaignEngine:
    """
    Plans and manages multi-day content campaigns.

    Usage:
        engine = CampaignEngine(brain)
        campaign = engine.create_campaign(
            name="AI Week",
            theme="The future of AI in everyday life",
            goal="increase engagement 20%",
            duration_days=7,
        )
        plan = engine.generate_campaign_plan(campaign)
    """

    def __init__(self, brain: Optional[GeminiBrain] = None):
        self._brain = brain or GeminiBrain()
        self._funnel_mapper = FunnelMapper(self._brain)

    def create_campaign(
        self,
        name: str,
        theme: str,
        goal: str,
        duration_days: int,
        *,
        posts_per_day: int = 1,
        niche: str = "technology",
        target_audience: str = "general",
        brand_voice: str = "professional",
        start_date: Optional[datetime] = None,
    ) -> Campaign:
        """
        Create a new content campaign.

        Args:
            name: Campaign name (e.g., "AI Week")
            theme: Central theme (e.g., "Future of AI in daily life")
            goal: Campaign goal (e.g., "increase engagement 20%")
            duration_days: How many days the campaign runs
            posts_per_day: Posts per day during campaign
            start_date: When to start (defaults to tomorrow)

        Returns:
            Campaign object with metadata
        """
        campaign = Campaign(
            name=name,
            theme=theme,
            goal=goal,
            duration_days=duration_days,
            posts_per_day=posts_per_day,
            niche=niche,
            target_audience=target_audience,
            brand_voice=brand_voice,
        )
        campaign.start_date = start_date or (datetime.now(timezone.utc) + timedelta(days=1))
        logger.info("Created campaign '%s': %d days, %d posts/day", name, duration_days, posts_per_day)
        return campaign

    def generate_campaign_plan(self, campaign: Campaign) -> list[dict]:
        """
        Use Gemini to generate a full content plan for the campaign.

        Returns:
            List of dicts with day, topic, content_type, funnel_stage, hook
        """
        total_posts = campaign.duration_days * campaign.posts_per_day

        prompt = (
            f"Plan a {campaign.duration_days}-day Instagram content campaign.\n\n"
            f"Campaign: {campaign.name}\n"
            f"Theme: {campaign.theme}\n"
            f"Goal: {campaign.goal}\n"
            f"Niche: {campaign.niche}\n"
            f"Audience: {campaign.target_audience}\n"
            f"Posts per day: {campaign.posts_per_day}\n"
            f"Total posts needed: {total_posts}\n\n"
            f"For each post, provide:\n"
            f"- Day number\n"
            f"- Topic\n"
            f"- Content type (IMAGE, CAROUSEL, REELS)\n"
            f"- Funnel stage (TOFU, MOFU, BOFU, RETENTION)\n"
            f"- Hook (first line of caption to grab attention)\n\n"
            f"Create a narrative arc: start with awareness, build interest, "
            f"peak with value, close with community. Each post should connect "
            f"to the next. Format as numbered list."
        )

        result = self._brain.generate_text(
            prompt,
            system_instruction=(
                f"You are an Instagram campaign strategist for the {campaign.niche} niche. "
                f"Create campaign plans that tell a story across multiple days, "
                f"building towards the campaign goal."
            ),
        )

        # Parse the result into structured plan
        plan = self._parse_campaign_plan(result, campaign)
        campaign.content_plan = plan
        campaign.status = "PLANNED"

        logger.info("Generated plan for '%s': %d posts", campaign.name, len(plan))
        return plan

    def _parse_campaign_plan(self, text: str, campaign: Campaign) -> list[dict]:
        """Parse Gemini's campaign plan text into structured data."""
        lines = [l.strip() for l in text.strip().split("\n") if l.strip()]
        plan = []
        current_day = 1

        for line in lines:
            # Simple heuristic parse — look for day markers and content
            lower = line.lower()
            if "day" in lower and any(c.isdigit() for c in line):
                # Extract day number
                for word in line.split():
                    if word.isdigit():
                        current_day = int(word)
                        break

            # If line contains actionable content
            if len(line) > 20 and not line.startswith("#"):
                # Determine content type from text
                content_type = "IMAGE"
                if "carousel" in lower:
                    content_type = "CAROUSEL"
                elif "reel" in lower:
                    content_type = "REELS"

                # Determine funnel stage
                funnel_stage = "TOFU"
                if "educational" in lower or "tutorial" in lower:
                    funnel_stage = "MOFU"
                elif "conversion" in lower or "cta" in lower:
                    funnel_stage = "BOFU"
                elif "community" in lower or "poll" in lower:
                    funnel_stage = "RETENTION"

                plan.append({
                    "day": current_day,
                    "topic": line[:200],
                    "content_type": content_type,
                    "funnel_stage": funnel_stage,
                    "campaign": campaign.name,
                })

        return plan

    def analyze_campaign_performance(
        self,
        campaign: Campaign,
        metrics: list[dict],
    ) -> str:
        """
        Analyze a running/completed campaign's performance using Gemini.

        Args:
            campaign: The campaign
            metrics: List of post metrics dicts (likes, comments, saves, reach)

        Returns:
            AI-generated analysis with recommendations
        """
        metrics_summary = "\n".join(
            f"Day {m.get('day', '?')}: likes={m.get('likes', 0)}, "
            f"comments={m.get('comments', 0)}, saves={m.get('saves', 0)}, "
            f"reach={m.get('reach', 0)}"
            for m in metrics
        )

        prompt = (
            f"Analyze this Instagram campaign's performance:\n\n"
            f"Campaign: {campaign.name}\n"
            f"Theme: {campaign.theme}\n"
            f"Goal: {campaign.goal}\n\n"
            f"Metrics by day:\n{metrics_summary}\n\n"
            f"Provide:\n"
            f"1. Overall performance assessment\n"
            f"2. Best performing content and why\n"
            f"3. What underperformed and why\n"
            f"4. Mid-campaign adjustments (if still running)\n"
            f"5. Learnings for future campaigns"
        )

        analysis = self._brain.analyze(prompt)
        logger.info("Analyzed campaign '%s' performance", campaign.name)
        return analysis
