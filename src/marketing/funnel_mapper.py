"""
Funnel Mapper — Maps content to TOFU/MOFU/BOFU marketing funnel stages.

Gemini decides the funnel stage for each piece of content and ensures
balanced distribution across the calendar.

TOFU  (40%): Viral hooks, trending content, broad reach
MOFU  (30%): Educational, tutorials, deep-dives
BOFU  (15%): Conversion, product mentions, calls-to-action
RETENTION (15%): Community, behind-the-scenes, polls
"""

from typing import Optional

from src.ai.gemini_brain import GeminiBrain
from src.ai import prompts
from src.core.logging_config import get_logger

logger = get_logger("marketing.funnel_mapper")

# Default funnel distribution targets
FUNNEL_DISTRIBUTION = {
    "TOFU": 0.40,
    "MOFU": 0.30,
    "BOFU": 0.15,
    "RETENTION": 0.15,
}

FUNNEL_DESCRIPTIONS = {
    "TOFU": "Top of Funnel — Awareness. Viral, trending, shareable content to attract new followers.",
    "MOFU": "Middle of Funnel — Consideration. Educational, tutorials, deep-dives to build trust.",
    "BOFU": "Bottom of Funnel — Conversion. Product mentions, testimonials, CTAs to drive action.",
    "RETENTION": "Retention — Loyalty. Community content, polls, behind-the-scenes, Q&A.",
}


class FunnelMapper:
    """
    Maps content topics to funnel stages using AI analysis.

    Usage:
        mapper = FunnelMapper(brain)
        stage = mapper.classify_topic("How to use ChatGPT for coding", niche="AI education")
        plan = mapper.plan_week_distribution(posts_per_day=2)
    """

    def __init__(self, brain: Optional[GeminiBrain] = None):
        self._brain = brain or GeminiBrain()

    def classify_topic(self, topic: str, *, niche: str = "technology") -> str:
        """
        Classify a content topic into a funnel stage.

        Args:
            topic: The content topic
            niche: Account niche for context

        Returns:
            Funnel stage: "TOFU", "MOFU", "BOFU", or "RETENTION"
        """
        prompt = (
            f"Classify this Instagram post topic into ONE funnel stage.\n\n"
            f"Topic: {topic}\n"
            f"Niche: {niche}\n\n"
            f"Stages:\n"
            f"- TOFU: Viral, trending, broad reach, awareness\n"
            f"- MOFU: Educational, tutorials, deep-dives, trust-building\n"
            f"- BOFU: Conversion, product mentions, testimonials, CTAs\n"
            f"- RETENTION: Community, polls, behind-the-scenes, Q&A\n\n"
            f"Return ONLY the stage name (e.g. TOFU)"
        )

        result = self._brain.generate_text_lite(prompt).strip().upper()
        # Validate
        if result not in FUNNEL_DISTRIBUTION:
            result = "TOFU"  # Default
        logger.info("Topic '%s' → %s", topic[:50], result)
        return result

    def classify_batch(
        self,
        topics: list[str],
        *,
        niche: str = "technology",
    ) -> dict[str, str]:
        """
        Classify multiple topics into funnel stages.

        Returns:
            Dict mapping topic → stage
        """
        result = {}
        for topic in topics:
            result[topic] = self.classify_topic(topic, niche=niche)
        return result

    def analyze_distribution(
        self,
        content_stages: list[str],
    ) -> dict:
        """
        Analyze current funnel distribution and compare to targets.

        Args:
            content_stages: List of funnel stages of existing content

        Returns:
            Dict with current distribution, target, and gaps
        """
        total = len(content_stages) if content_stages else 1
        current = {
            stage: content_stages.count(stage) / total
            for stage in FUNNEL_DISTRIBUTION
        }

        gaps = {
            stage: FUNNEL_DISTRIBUTION[stage] - current.get(stage, 0)
            for stage in FUNNEL_DISTRIBUTION
        }

        return {
            "current": current,
            "target": FUNNEL_DISTRIBUTION,
            "gaps": gaps,
            "recommendation": max(gaps, key=gaps.get),  # Most underrepresented stage
        }

    def plan_week_distribution(
        self,
        *,
        posts_per_day: int = 2,
        days: int = 7,
    ) -> list[dict]:
        """
        Plan the funnel stage distribution for a week of posts.

        Returns:
            List of dicts with 'day', 'slot', 'funnel_stage'
        """
        total_posts = posts_per_day * days
        schedule = []

        for stage, ratio in FUNNEL_DISTRIBUTION.items():
            count = round(total_posts * ratio)
            for _ in range(count):
                schedule.append({"funnel_stage": stage})

        # Fill remaining slots
        while len(schedule) < total_posts:
            schedule.append({"funnel_stage": "TOFU"})

        # Trim if over
        schedule = schedule[:total_posts]

        # Assign to days
        for i, slot in enumerate(schedule):
            slot["day"] = (i // posts_per_day) + 1
            slot["slot"] = (i % posts_per_day) + 1

        logger.info("Planned %d posts across %d days", total_posts, days)
        return schedule
