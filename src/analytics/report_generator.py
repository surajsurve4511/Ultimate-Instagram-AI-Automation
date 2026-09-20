"""
Report Generator — Generates weekly/monthly performance reports.

Uses Gemini to create human-readable reports with summaries,
data tables, insights, and recommendations.
"""

from datetime import datetime, timezone
from typing import Optional

from src.ai.gemini_brain import GeminiBrain
from src.core.logging_config import get_logger

logger = get_logger("analytics.report_generator")


class ReportGenerator:
    """
    Generates AI-powered performance reports.

    Usage:
        gen = ReportGenerator(brain)
        report = gen.weekly_report(posts, account_metrics)
    """

    def __init__(self, brain: Optional[GeminiBrain] = None):
        self._brain = brain or GeminiBrain()

    def weekly_report(
        self,
        posts: list[dict],
        account_metrics: dict = None,
        *,
        niche: str = "technology",
    ) -> dict:
        """
        Generate a weekly performance report.

        Args:
            posts: Posts from the past week with metrics
            account_metrics: Account-level metrics (follower count, etc.)
            niche: Account niche

        Returns:
            Dict with report sections: summary, highlights, lowlights, recommendations
        """
        # Compute aggregates
        total_likes = sum(p.get("likes", 0) for p in posts)
        total_comments = sum(p.get("comments", 0) for p in posts)
        total_saves = sum(p.get("saves", 0) for p in posts)
        total_reach = sum(p.get("reach", 0) for p in posts)
        avg_engagement = (total_likes + total_comments + total_saves) / max(len(posts), 1)

        # Sort to find best and worst
        sorted_posts = sorted(
            posts,
            key=lambda p: p.get("likes", 0) + p.get("comments", 0) * 3 + p.get("saves", 0) * 5,
            reverse=True,
        )
        best = sorted_posts[:3] if sorted_posts else []
        worst = sorted_posts[-3:] if len(sorted_posts) > 3 else []

        prompt = (
            f"Generate a weekly Instagram performance report.\n\n"
            f"Niche: {niche}\n"
            f"Posts this week: {len(posts)}\n"
            f"Total likes: {total_likes}\n"
            f"Total comments: {total_comments}\n"
            f"Total saves: {total_saves}\n"
            f"Total reach: {total_reach}\n"
            f"Avg engagement per post: {avg_engagement:.0f}\n"
            f"Follower count: {account_metrics.get('followers', 'N/A') if account_metrics else 'N/A'}\n\n"
            f"Top 3 posts (by engagement score):\n"
            + "\n".join(f"- {p.get('caption', '')[:80]}" for p in best)
            + f"\n\nBottom 3 posts:\n"
            + "\n".join(f"- {p.get('caption', '')[:80]}" for p in worst)
            + f"\n\nProvide:\n"
            f"1. Executive summary (3 sentences)\n"
            f"2. Key wins\n"
            f"3. Areas for improvement\n"
            f"4. Top 5 recommendations for next week\n"
            f"5. Content mix suggestion for next week"
        )

        narrative = self._brain.generate_text(
            prompt,
            system_instruction=(
                "You are an Instagram analytics expert generating a weekly report. "
                "Be concise, data-driven, and actionable. Use numbers to back up insights."
            ),
        )

        report = {
            "period": "weekly",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "metrics": {
                "total_posts": len(posts),
                "total_likes": total_likes,
                "total_comments": total_comments,
                "total_saves": total_saves,
                "total_reach": total_reach,
                "avg_engagement": round(avg_engagement, 1),
            },
            "best_posts": [
                {"caption": p.get("caption", "")[:100], "likes": p.get("likes", 0)}
                for p in best
            ],
            "narrative": narrative,
        }

        logger.info("Generated weekly report: %d posts, avg engagement %.1f", len(posts), avg_engagement)
        return report

    def monthly_report(
        self,
        weekly_reports: list[dict],
        *,
        niche: str = "technology",
    ) -> dict:
        """
        Generate a monthly report from weekly data.

        Args:
            weekly_reports: List of weekly report dicts
            niche: Account niche

        Returns:
            Monthly summary report
        """
        # Aggregate weekly metrics
        total_posts = sum(r["metrics"]["total_posts"] for r in weekly_reports)
        total_likes = sum(r["metrics"]["total_likes"] for r in weekly_reports)

        prompt = (
            f"Generate a monthly Instagram performance summary.\n\n"
            f"Niche: {niche}\n"
            f"Weeks: {len(weekly_reports)}\n"
            f"Total posts: {total_posts}\n"
            f"Total likes: {total_likes}\n\n"
            f"Weekly summaries:\n"
            + "\n".join(r.get("narrative", "")[:200] for r in weekly_reports)
            + "\n\nProvide a concise monthly overview with trends and strategy for next month."
        )

        narrative = self._brain.generate_text(prompt)

        report = {
            "period": "monthly",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_posts": total_posts,
            "total_likes": total_likes,
            "weeks_covered": len(weekly_reports),
            "narrative": narrative,
        }

        logger.info("Generated monthly report: %d posts across %d weeks", total_posts, len(weekly_reports))
        return report
