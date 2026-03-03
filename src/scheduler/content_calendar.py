"""
Content Calendar — Auto-generates optimal posting schedule per user.

Creates calendar slots based on posting frequency, funnel distribution,
and content type diversity. Fills gaps automatically.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from src.config.settings import SETTINGS

logger = logging.getLogger(__name__)


class ContentCalendar:
    """
    Manages the content calendar for an Instagram account.
    
    Usage:
        cal = ContentCalendar()
        schedule = cal.generate_week_schedule(
            posts_per_day=3,
            posting_times=["09:00", "14:00", "18:00"],
            funnel_distribution={"TOFU": 0.4, "MOFU": 0.3, "BOFU": 0.15, "RETENTION": 0.15}
        )
    """

    def generate_week_schedule(
        self,
        *,
        posts_per_day: int = 3,
        posting_times: list[str] | None = None,
        posting_days: list[int] | None = None,
        funnel_distribution: dict | None = None,
        start_date: Optional[datetime] = None,
    ) -> list[dict]:
        """
        Generate a week's content calendar.
        
        Args:
            posts_per_day: Number of posts per day
            posting_times: Times to post (24h format)
            posting_days: Days to post (0=Mon, 6=Sun)
            funnel_distribution: TOFU/MOFU/BOFU/RETENTION percentages
            start_date: Start date (defaults to today)
            
        Returns:
            List of calendar slot dicts
        """
        times = posting_times or SETTINGS.DEFAULT_POSTING_TIMES
        days = posting_days or SETTINGS.DEFAULT_POSTING_DAYS
        funnel = funnel_distribution or SETTINGS.DEFAULT_FUNNEL_DISTRIBUTION
        start = start_date or datetime.now(timezone.utc)

        # Normalize to start of day
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)

        schedule = []
        content_types = ["IMAGE", "CAROUSEL", "IMAGE", "REELS", "IMAGE"]
        funnel_stages = self._distribute_funnel(funnel, posts_per_day * 7)
        stage_idx = 0

        for day_offset in range(7):
            current_date = start + timedelta(days=day_offset)
            weekday = current_date.weekday()

            if weekday not in days:
                continue

            for time_str in times[:posts_per_day]:
                hour, minute = map(int, time_str.split(":"))
                slot_time = current_date.replace(hour=hour, minute=minute)

                slot = {
                    "scheduled_at": slot_time.isoformat(),
                    "content_type": content_types[stage_idx % len(content_types)],
                    "funnel_stage": funnel_stages[stage_idx] if stage_idx < len(funnel_stages) else "TOFU",
                    "suggested_topic": None,
                    "generated_content_id": None,
                    "is_published": False,
                }
                schedule.append(slot)
                stage_idx += 1

        logger.info(f"Generated {len(schedule)} calendar slots for the week")
        return schedule

    @staticmethod
    def _distribute_funnel(funnel: dict, total: int) -> list[str]:
        """Distribute funnel stages across slots based on percentages."""
        stages = []
        for stage, pct in funnel.items():
            count = max(1, round(total * pct))
            stages.extend([stage] * count)
        # Pad or trim
        while len(stages) < total:
            stages.append("TOFU")
        return stages[:total]
