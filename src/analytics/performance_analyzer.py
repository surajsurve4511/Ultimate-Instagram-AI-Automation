"""
Performance Analyzer — Gemini-powered analysis of content performance data.

Identifies patterns, correlates content attributes with engagement,
and generates actionable recommendations to improve future content.
"""

from typing import Optional

from src.ai.gemini_brain import GeminiBrain
from src.core.logging_config import get_logger

logger = get_logger("analytics.performance_analyzer")


class PerformanceAnalyzer:
    """
    Uses Gemini to analyze content performance and find patterns.

    Usage:
        analyzer = PerformanceAnalyzer(brain)
        insights = analyzer.analyze_performance(metrics_data)
        patterns = analyzer.find_top_patterns(metrics_data)
    """

    def __init__(self, brain: Optional[GeminiBrain] = None):
        self._brain = brain or GeminiBrain()

    def analyze_performance(
        self,
        posts: list[dict],
        *,
        niche: str = "technology",
    ) -> dict:
        """
        Comprehensive Gemini-powered analysis of post performance.

        Args:
            posts: List of dicts with caption, content_type, funnel_stage,
                   likes, comments, saves, reach, etc.
            niche: Account niche for context

        Returns:
            Dict with summary, top_patterns, weak_areas, recommendations
        """
        # Build metrics summary
        lines = []
        for i, p in enumerate(posts[:30], 1):  # Cap at 30 to fit context
            lines.append(
                f"{i}. Type:{p.get('content_type','?')} | "
                f"Stage:{p.get('funnel_stage','?')} | "
                f"Likes:{p.get('likes',0)} | Comments:{p.get('comments',0)} | "
                f"Saves:{p.get('saves',0)} | Reach:{p.get('reach',0)} | "
                f"Caption:{p.get('caption','')[:80]}"
            )

        metrics_text = "\n".join(lines)

        prompt = (
            f"Analyze this Instagram account's content performance.\n"
            f"Niche: {niche}\n\n"
            f"Post data (most recent):\n{metrics_text}\n\n"
            f"Provide:\n"
            f"1. Overall performance summary (2-3 sentences)\n"
            f"2. Top 3 patterns in high-performing posts\n"
            f"3. Top 3 weak areas that need improvement\n"
            f"4. Specific, actionable recommendations (5 bullet points)\n"
            f"5. Optimal posting times based on engagement patterns"
        )

        result = self._brain.analyze(
            prompt,
            system_instruction=(
                "You are an Instagram analytics expert. Analyze performance data "
                "and find actionable patterns. Be specific with data-backed insights. "
                "Don't be generic — reference specific post types and numbers."
            ),
        )

        logger.info("Analyzed performance of %d posts", len(posts))

        return {
            "analysis": result,
            "posts_analyzed": len(posts),
            "niche": niche,
        }

    def find_best_content_type(self, posts: list[dict]) -> dict:
        """
        Find which content types perform best.

        Returns:
            Dict mapping content_type to avg engagement
        """
        from collections import defaultdict

        type_metrics = defaultdict(lambda: {"count": 0, "total_engagement": 0})

        for p in posts:
            ct = p.get("content_type", "IMAGE")
            engagement = (
                p.get("likes", 0) + p.get("comments", 0) * 3
                + p.get("saves", 0) * 5 + p.get("shares", 0) * 4
            )
            type_metrics[ct]["count"] += 1
            type_metrics[ct]["total_engagement"] += engagement

        result = {}
        for ct, data in type_metrics.items():
            avg = data["total_engagement"] / data["count"] if data["count"] else 0
            result[ct] = {
                "count": data["count"],
                "avg_engagement_score": round(avg, 1),
            }

        # Sort by avg engagement
        result = dict(sorted(result.items(), key=lambda x: x[1]["avg_engagement_score"], reverse=True))

        logger.info("Content type analysis: %s", result)
        return result

    def find_best_funnel_stage(self, posts: list[dict]) -> dict:
        """Find which funnel stages perform best."""
        from collections import defaultdict

        stage_metrics = defaultdict(lambda: {"count": 0, "total_engagement": 0})

        for p in posts:
            stage = p.get("funnel_stage", "TOFU")
            engagement = (
                p.get("likes", 0) + p.get("comments", 0) * 3
                + p.get("saves", 0) * 5 + p.get("shares", 0) * 4
            )
            stage_metrics[stage]["count"] += 1
            stage_metrics[stage]["total_engagement"] += engagement

        result = {}
        for stage, data in stage_metrics.items():
            avg = data["total_engagement"] / data["count"] if data["count"] else 0
            result[stage] = {
                "count": data["count"],
                "avg_engagement_score": round(avg, 1),
            }

        return dict(sorted(result.items(), key=lambda x: x[1]["avg_engagement_score"], reverse=True))

    def generate_strategy_adjustments(
        self,
        current_performance: dict,
        goals: dict,
    ) -> str:
        """
        Generate strategy adjustments based on performance vs goals.

        Args:
            current_performance: Current metrics summary
            goals: Target metrics

        Returns:
            AI-generated strategy adjustment recommendations
        """
        prompt = (
            f"Based on current performance vs goals, suggest strategy adjustments.\n\n"
            f"Current: {current_performance}\n"
            f"Goals: {goals}\n\n"
            f"Provide 5 specific, actionable adjustments to close the gap."
        )

        return self._brain.analyze(prompt)
