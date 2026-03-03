"""
Goal Tracker — Tracks user goals and measures progress.

Monitors follower milestones, engagement targets, content schedule adherence,
and generates progress reports using Gemini.
"""

import logging
from typing import Optional

from src.ai.gemini_brain import GeminiBrain

logger = logging.getLogger(__name__)


class GoalTracker:
    """
    Tracks progress toward user-defined goals.
    """

    def __init__(self, gemini: Optional[GeminiBrain] = None):
        self._gemini = gemini or GeminiBrain()

    def assess_progress(
        self,
        goals: dict,
        current_metrics: dict,
    ) -> str:
        """
        Assess progress toward goals.
        
        Args:
            goals: Dict of goal_name -> target_value
            current_metrics: Dict of metric_name -> current_value
            
        Returns:
            Progress assessment text
        """
        prompt = (
            f"Assess progress toward these Instagram goals:\n\n"
            f"Goals:\n"
        )
        for name, target in goals.items():
            current = current_metrics.get(name, "unknown")
            prompt += f"- {name}: target={target}, current={current}\n"

        prompt += (
            f"\nProvide:\n"
            f"1. Progress percentage for each goal\n"
            f"2. On-track / behind / ahead assessment\n"
            f"3. Specific recommendations to accelerate progress\n"
            f"4. Timeline estimate to reach each goal"
        )

        return self._gemini.analyze(prompt)

    def generate_weekly_report(
        self,
        account_name: str,
        niche: str,
        goals: str,
        weekly_metrics: dict,
        top_posts: str,
        worst_posts: str,
    ) -> str:
        """
        Generate a weekly performance report.
        
        Returns:
            Formatted weekly report text
        """
        from src.ai import prompts as p

        prompt = p.WEEKLY_STRATEGY.format(
            account_name=account_name,
            niche=niche,
            goals=goals,
            weekly_summary=str(weekly_metrics),
            top_posts=top_posts,
            worst_posts=worst_posts,
            content_mix="To be determined from data",
        )

        return self._gemini.analyze(prompt)
