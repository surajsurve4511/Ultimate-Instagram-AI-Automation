"""
Growth Loop Engine — Implements self-reinforcing viral loops and engagement
mechanics used by the fastest-growing social media accounts.

Growth loops are self-sustaining systems where the output of one cycle
becomes the input for the next, creating exponential growth:

  Content → Engagement → Reach → New Followers → More Engagement → ...

This module implements 4 types of loops:
  1. Viral Loop:      Share-to-unlock, tag-a-friend, challenge chains
  2. Engagement Loop: Comment-to-win, poll-based, interactive series
  3. Retention Loop:  Series & streaks, progressive content, rewards
  4. Referral Loop:   Ambassador program, UGC, community spotlights
"""
import random
import logging
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field

from src.config.settings import SETTINGS

logger = logging.getLogger(__name__)


class LoopType(Enum):
    """Types of growth loops."""
    VIRAL = "viral"
    ENGAGEMENT = "engagement"
    RETENTION = "retention"
    REFERRAL = "referral"


@dataclass
class GrowthLoop:
    """A self-reinforcing growth mechanic."""
    loop_type: LoopType
    name: str
    description: str
    trigger_action: str          # What starts the loop
    reward: str                  # What the user gets
    viral_coefficient: float     # Expected multiplier (>1.0 = viral)
    content_templates: List[str]
    hashtags: List[str]
    duration_days: int
    posts_needed: int
    mechanics: List[str]
    kpis: List[str]


class GrowthLoopEngine:
    """
    Engine that designs and manages self-reinforcing growth loops.
    
    Each loop is engineered to create a flywheel effect:
    the more it runs, the faster it grows.
    """

    def __init__(self):
        self.active_loops = {}
        self.loop_history = []

        # ─── Loop Blueprints ──────────────────────────────────────────

        self.loop_blueprints = {
            LoopType.VIRAL: {
                "loops": [
                    {
                        "name": "Share-to-Unlock Challenge",
                        "description": "Share the post on your story to unlock exclusive AI resources",
                        "trigger": "User shares post to story and tags account",
                        "reward": "Exclusive AI resource pack via DM",
                        "viral_coefficient": 2.5,
                        "template": "🔓 UNLOCK: Share this post on your story + tag @_ai_multiverse_ to get our exclusive {topic} resource pack!\n\nThis pack includes:\n• {resource_1}\n• {resource_2}\n• {resource_3}\n\nOnly available for the next 48 hours ⏳",
                        "posts_needed": 3,
                        "duration": 7,
                    },
                    {
                        "name": "Tag-a-Friend Chain",
                        "description": "Tag friends in comments — each tag enters you in a draw",
                        "trigger": "User tags a friend",
                        "reward": "Entry into exclusive giveaway / free resource",
                        "viral_coefficient": 3.0,
                        "template": "🎁 TAG & WIN: Tag a friend who needs to learn about {topic}!\n\nEvery tag = 1 entry to win:\n🏆 {prize}\n\nRules:\n1. Follow @_ai_multiverse_\n2. Like this post\n3. Tag friends (unlimited entries!)\n\nWinner announced in 72 hours! ⏰",
                        "posts_needed": 2,
                        "duration": 3,
                    },
                    {
                        "name": "Challenge Chain",
                        "description": "Complete an AI challenge and nominate others",
                        "trigger": "User posts their challenge result and tags friends",
                        "reward": "Community recognition + feature on account",
                        "viral_coefficient": 2.0,
                        "template": "🏆 {topic} CHALLENGE!\n\nRules:\n1. Try {challenge_action}\n2. Post your result with #{hashtag}\n3. Nominate 3 friends\n\nBest results get featured on our account! 🌟\n\nI'm nominating: @friend1 @friend2 @friend3\n\nYour turn! 👇",
                        "posts_needed": 5,
                        "duration": 14,
                    },
                ],
            },
            LoopType.ENGAGEMENT: {
                "loops": [
                    {
                        "name": "Comment-to-Learn",
                        "description": "Comment a keyword to get detailed explanation via DM",
                        "trigger": "User comments specific keyword",
                        "reward": "Personalized AI explanation",
                        "viral_coefficient": 1.5,
                        "template": "💡 Want to understand {topic} in 60 seconds?\n\nComment '{keyword}' below and I'll DM you a simple explanation!\n\nAlready sent to 500+ people. Don't miss out! 📬",
                        "posts_needed": 2,
                        "duration": 3,
                    },
                    {
                        "name": "Poll-Based Series",
                        "description": "Audience votes decide the next content topic",
                        "trigger": "User votes in story poll",
                        "reward": "Content they actually want",
                        "viral_coefficient": 1.3,
                        "template": "📊 YOU DECIDE: What should I cover next?\n\nA) {option_a}\nB) {option_b}\nC) {option_c}\n\nComment your choice below! Most voted topic drops tomorrow 🔥\n\nLast time, you chose {previous_winner} and it went VIRAL!",
                        "posts_needed": 3,
                        "duration": 7,
                    },
                    {
                        "name": "This-or-That Debates",
                        "description": "Polarizing comparisons that drive comments",
                        "trigger": "User takes a side in the comments",
                        "reward": "Community engagement + being heard",
                        "viral_coefficient": 1.8,
                        "template": "⚔️ DEBATE TIME:\n\n{option_a} vs {option_b}\n\nWhich one wins for {topic}?\n\nComment Team A or Team B — and defend your choice! 🔥\n\nI'll reveal the community verdict tomorrow 📊",
                        "posts_needed": 2,
                        "duration": 2,
                    },
                ],
            },
            LoopType.RETENTION: {
                "loops": [
                    {
                        "name": "Daily AI Fact Series",
                        "description": "Daily content drop that creates habit formation",
                        "trigger": "User returns daily for new content",
                        "reward": "Consistent valuable learning",
                        "viral_coefficient": 1.2,
                        "template": "📅 Day {day}/30 of #AIFactsDaily\n\nToday's {topic} fact:\n\n{fact}\n\n💡 Did you know this?\nSave this series and learn something new every day!\n\nMissed yesterday? Check our highlights! 📌",
                        "posts_needed": 30,
                        "duration": 30,
                    },
                    {
                        "name": "Progressive Learning Path",
                        "description": "Multi-week learning journey with increasing complexity",
                        "trigger": "User follows the series to level up",
                        "reward": "Progressive skill building",
                        "viral_coefficient": 1.4,
                        "template": "🎓 {topic} Mastery — Level {level}/5\n\n{content}\n\n⬆️ Complete this level? Comment 'DONE ✅' to unlock Level {next_level}!\n\nMissed earlier levels? Check pinned post 📌",
                        "posts_needed": 10,
                        "duration": 14,
                    },
                    {
                        "name": "Weekly Recap + Preview",
                        "description": "Sunday recap of best content + preview of next week",
                        "trigger": "User anticipates weekly roundup",
                        "reward": "Curated best-of + sneak peek",
                        "viral_coefficient": 1.1,
                        "template": "📋 WEEKLY AI RECAP — Week {week}\n\nThis week's highlights:\n🔥 {highlight_1}\n📊 {highlight_2}\n🎯 {highlight_3}\n\nNext week preview:\n👀 {preview}\n\nTurn on notifications 🔔 to never miss an update!",
                        "posts_needed": 1,
                        "duration": 7,
                    },
                ],
            },
            LoopType.REFERRAL: {
                "loops": [
                    {
                        "name": "Community Spotlight",
                        "description": "Feature community members who engage most",
                        "trigger": "User contributes valuable content/comments",
                        "reward": "Being featured to thousands of followers",
                        "viral_coefficient": 2.0,
                        "template": "🌟 COMMUNITY SPOTLIGHT 🌟\n\nThis week's AI Multiverse MVP: @{username}!\n\nTheir {topic} contribution blew our minds:\n'{contribution}'\n\nWant to be featured? Share your AI journey with #{hashtag}! 🤖",
                        "posts_needed": 1,
                        "duration": 7,
                    },
                    {
                        "name": "UGC Repost Campaign",
                        "description": "Encourage audience to create content for reposting",
                        "trigger": "User creates content using branded hashtag",
                        "reward": "Exposure to larger audience",
                        "viral_coefficient": 2.5,
                        "template": "📸 REPOST ALERT!\n\nWe're featuring the BEST {topic} content from our community!\n\nHow to get featured:\n1. Create a post/reel about {topic}\n2. Use #{hashtag}\n3. Tag @_ai_multiverse_\n\nBest posts get reshared to our {follower_count}+ followers! 🚀",
                        "posts_needed": 3,
                        "duration": 14,
                    },
                    {
                        "name": "Ambassador Program",
                        "description": "Most engaged followers become brand ambassadors",
                        "trigger": "User applies through DM/form",
                        "reward": "Exclusive content, early access, recognition",
                        "viral_coefficient": 3.0,
                        "template": "🤖 AI MULTIVERSE AMBASSADOR PROGRAM 🤖\n\nWe're selecting 10 ambassadors for {topic}!\n\nBenefits:\n⭐ Early access to all content\n⭐ Exclusive {topic} resources\n⭐ Direct line to our research team\n⭐ Featured on our account monthly\n\nTo apply: DM us 'AMBASSADOR' + why you're passionate about {topic}\n\nApplications close in 48 hours! ⏳",
                        "posts_needed": 2,
                        "duration": 30,
                    },
                ],
            },
        }

    def design_growth_loop(self, topic: str,
                            loop_type: LoopType = None,
                            duration_days: int = 7) -> GrowthLoop:
        """
        Design a growth loop for a specific topic.
        Selects the most effective loop type based on current needs.
        """
        if loop_type is None:
            loop_type = self._select_optimal_loop_type()

        blueprints = self.loop_blueprints[loop_type]["loops"]
        blueprint = random.choice(blueprints)

        # Create branded hashtag
        topic_slug = topic.lower().replace(" ", "").replace("-", "")[:15]
        branded_hashtag = f"#AIMultiverse{topic_slug.title()}"

        loop = GrowthLoop(
            loop_type=loop_type,
            name=blueprint["name"],
            description=blueprint["description"],
            trigger_action=blueprint["trigger"],
            reward=blueprint["reward"],
            viral_coefficient=blueprint["viral_coefficient"],
            content_templates=[blueprint["template"]],
            hashtags=[branded_hashtag, "#AIMultiverse", "#AICommunity",
                      "#LearnAI", "#AIEducation"],
            duration_days=min(duration_days, blueprint["duration"]),
            posts_needed=blueprint["posts_needed"],
            mechanics=[
                f"Trigger: {blueprint['trigger']}",
                f"Reward: {blueprint['reward']}",
                f"Expected viral coefficient: {blueprint['viral_coefficient']}x",
            ],
            kpis=self._get_loop_kpis(loop_type)
        )

        # Track active loop
        loop_id = f"{loop_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.active_loops[loop_id] = {
            "loop": loop,
            "started_at": datetime.now().isoformat(),
            "topic": topic,
            "status": "active"
        }

        logger.info(f"🔄 Growth loop designed: {loop.name} ({loop_type.value}) | "
                     f"Viral coefficient: {loop.viral_coefficient}x")
        return loop

    def create_loop_content_series(self, loop: GrowthLoop,
                                     topic: str) -> List[Dict]:
        """Create all content pieces needed for a growth loop."""
        content_series = []
        template = loop.content_templates[0]

        for day in range(1, loop.posts_needed + 1):
            content = {
                "day": day,
                "type": loop.loop_type.value,
                "template": template,
                "topic": topic,
                "hashtags": loop.hashtags,
                "loop_name": loop.name,
                "cta": loop.trigger_action,
                "reward": loop.reward,
                "timing": f"Day {day}/{loop.posts_needed}",
            }
            content_series.append(content)

        logger.info(f"📝 Created {len(content_series)} content pieces for "
                     f"'{loop.name}' loop")
        return content_series

    def get_recommended_loops(self, metrics: Dict = None) -> List[Dict]:
        """Recommend growth loops based on current account metrics."""
        recommendations = []

        if metrics is None:
            metrics = {}

        follower_count = metrics.get("follower_count", 0)
        engagement_rate = metrics.get("engagement_rate", 0)
        growth_rate = metrics.get("follower_growth_rate", 0)

        # Low follower count → focus on viral loops
        if follower_count < 1000:
            recommendations.append({
                "loop_type": LoopType.VIRAL.value,
                "reason": f"With {follower_count} followers, prioritize viral loops for rapid growth",
                "expected_impact": "2-3x follower growth in first month",
                "recommended_loop": "Tag-a-Friend Chain"
            })

        # Low engagement → focus on engagement loops
        if engagement_rate < 0.05:
            recommendations.append({
                "loop_type": LoopType.ENGAGEMENT.value,
                "reason": f"Engagement at {engagement_rate*100:.1f}% — need interaction mechanics",
                "expected_impact": "2x comment rate within 2 weeks",
                "recommended_loop": "Comment-to-Learn"
            })

        # Stagnant growth → referral loops
        if growth_rate < 0.02:
            recommendations.append({
                "loop_type": LoopType.REFERRAL.value,
                "reason": "Growth has plateaued — leverage existing audience for referrals",
                "expected_impact": "New organic reach channel",
                "recommended_loop": "UGC Repost Campaign"
            })

        # Good base → retention loops
        if follower_count > 500 and engagement_rate > 0.03:
            recommendations.append({
                "loop_type": LoopType.RETENTION.value,
                "reason": "Solid base — focus on retention to prevent unfollows",
                "expected_impact": "Reduce unfollow rate by 50%",
                "recommended_loop": "Daily AI Fact Series"
            })

        # Default: always suggest at least one
        if not recommendations:
            recommendations.append({
                "loop_type": LoopType.VIRAL.value,
                "reason": "Start with viral loops to build initial momentum",
                "expected_impact": "Build growth flywheel",
                "recommended_loop": "Share-to-Unlock Challenge"
            })

        return recommendations

    def get_active_loops_status(self) -> List[Dict]:
        """Get status of all active growth loops."""
        status = []
        for loop_id, data in self.active_loops.items():
            loop = data["loop"]
            started = datetime.fromisoformat(data["started_at"])
            days_active = (datetime.now() - started).days

            status.append({
                "id": loop_id,
                "name": loop.name,
                "type": loop.loop_type.value,
                "topic": data["topic"],
                "days_active": days_active,
                "total_duration": loop.duration_days,
                "progress_pct": min(100, (days_active / loop.duration_days) * 100),
                "viral_coefficient": loop.viral_coefficient,
                "status": data["status"],
            })

        return status

    # ─── Private Methods ──────────────────────────────────────────────────

    def _select_optimal_loop_type(self) -> LoopType:
        """Select the best loop type based on recent usage and variety."""
        recent_types = [h.get("type") for h in self.loop_history[-5:]]

        # Prefer types not used recently
        all_types = list(LoopType)
        available = [t for t in all_types if t.value not in recent_types]

        if not available:
            available = all_types

        selected = random.choice(available)
        self.loop_history.append({
            "type": selected.value,
            "timestamp": datetime.now().isoformat()
        })

        return selected

    def _get_loop_kpis(self, loop_type: LoopType) -> List[str]:
        """Get relevant KPIs for a loop type."""
        kpi_map = {
            LoopType.VIRAL: ["shares", "story_mentions", "new_followers", "reach"],
            LoopType.ENGAGEMENT: ["comments", "saves", "dm_conversations", "engagement_rate"],
            LoopType.RETENTION: ["return_rate", "story_views", "profile_visits", "streak_count"],
            LoopType.REFERRAL: ["ugc_posts", "ambassador_count", "referral_follows", "mentions"],
        }
        return kpi_map.get(loop_type, ["engagement_rate"])

    def to_dict(self, loop: GrowthLoop) -> Dict:
        """Convert GrowthLoop to dictionary."""
        return {
            "loop_type": loop.loop_type.value,
            "name": loop.name,
            "description": loop.description,
            "trigger_action": loop.trigger_action,
            "reward": loop.reward,
            "viral_coefficient": loop.viral_coefficient,
            "content_templates": loop.content_templates,
            "hashtags": loop.hashtags,
            "duration_days": loop.duration_days,
            "posts_needed": loop.posts_needed,
            "mechanics": loop.mechanics,
            "kpis": loop.kpis,
        }


# Global instance
growth_engine = GrowthLoopEngine()
