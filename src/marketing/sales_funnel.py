"""
Sales Funnel Engine — Maps content strategy to the customer journey.

Implements the AIDA model (Attention, Interest, Desire, Action) and
TOFU/MOFU/BOFU framework used by top marketing professionals.

This module ensures every piece of content serves a strategic purpose
in the audience's journey from stranger → follower → engaged fan → advocate.
"""
import random
import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field

from src.config.settings import SETTINGS

logger = logging.getLogger(__name__)


class FunnelStage(Enum):
    """Marketing funnel stages."""
    TOFU = "tofu"       # Top of Funnel: Awareness
    MOFU = "mofu"       # Middle of Funnel: Consideration
    BOFU = "bofu"       # Bottom of Funnel: Decision/Action
    RETENTION = "retention"  # Post-conversion: Loyalty


class AIDAPhase(Enum):
    """AIDA model phases for content structure."""
    ATTENTION = "attention"
    INTEREST = "interest"
    DESIRE = "desire"
    ACTION = "action"


@dataclass
class FunnelContentBrief:
    """A strategic brief for content creation at a specific funnel stage."""
    funnel_stage: FunnelStage
    aida_phase: AIDAPhase
    content_type: str                    # post, carousel, reel, story
    topic_angle: str                     # How to approach the topic
    psychology_trigger: str              # Primary psychology trigger
    tone: str                           # Voice/tone to use
    cta_type: str                       # Type of call-to-action
    kpis: List[str]                     # Key performance indicators
    hashtag_strategy: str               # high_volume, niche, branded
    engagement_hook: str                # Specific hook to drive engagement
    recommended_format: str             # carousel, infographic, meme, etc.


class SalesFunnelEngine:
    """
    Strategic content planning engine that thinks like a marketing director.
    
    Maps every content decision to a funnel stage, ensuring balanced
    audience development across awareness, engagement, and conversion.
    """

    def __init__(self):
        self.funnel_distribution = SETTINGS.FUNNEL_DISTRIBUTION
        self.content_history = []  # Track what we've posted per stage
        
        # Content type effectiveness per funnel stage
        self.stage_content_map = {
            FunnelStage.TOFU: {
                "goal": "Maximum reach and new audience discovery",
                "content_types": ["reel", "post", "carousel"],
                "preferred_formats": ["meme", "shocking_fact", "hot_take", "comparison"],
                "tone": "bold, attention-grabbing, curiosity-driven",
                "cta_types": ["follow", "share", "tag_friend"],
                "kpis": ["reach", "impressions", "profile_visits", "follows"],
                "psychology": ["curiosity", "surprise", "social_proof"],
                "aida_focus": AIDAPhase.ATTENTION,
                "hashtag_strategy": "high_volume",  # Broad reach
                "hooks": [
                    "Stop scrolling — this changes everything about {topic}",
                    "99% of people don't know this about {topic}",
                    "{topic} is about to change the world. Here's why.",
                    "I can't believe more people aren't talking about {topic}",
                    "Delete this app if you haven't tried {topic} yet",
                ]
            },
            FunnelStage.MOFU: {
                "goal": "Deepen engagement and build authority",
                "content_types": ["carousel", "post", "story_series"],
                "preferred_formats": ["tutorial", "deep_dive", "infographic", "comparison"],
                "tone": "educational, authoritative, helpful",
                "cta_types": ["save", "comment", "dm_for_more"],
                "kpis": ["saves", "comments", "shares", "engagement_rate"],
                "psychology": ["authority", "reciprocity", "commitment"],
                "aida_focus": AIDAPhase.INTEREST,
                "hashtag_strategy": "medium_niche",  # Targeted reach
                "hooks": [
                    "Here's exactly how {topic} works (explained simply)",
                    "The complete beginner's guide to {topic} 👇",
                    "I spent 100 hours learning {topic}. Here's what matters.",
                    "Save this — you'll need it when working with {topic}",
                    "The {topic} cheat sheet every developer needs 📋",
                ]
            },
            FunnelStage.BOFU: {
                "goal": "Drive specific actions and conversions",
                "content_types": ["post", "carousel", "story"],
                "preferred_formats": ["tool_review", "career_guide", "case_study", "tutorial_steps"],
                "tone": "practical, actionable, results-focused",
                "cta_types": ["click_link", "try_tool", "apply_now", "join_waitlist"],
                "kpis": ["link_clicks", "profile_actions", "dm_conversations", "saves"],
                "psychology": ["scarcity", "authority", "social_proof"],
                "aida_focus": AIDAPhase.DESIRE,
                "hashtag_strategy": "micro_niche",  # Highly targeted
                "hooks": [
                    "This free {topic} tool replaced my $500/month subscription",
                    "I just landed a {topic} role. Here's my exact strategy.",
                    "The only 3 {topic} resources you actually need in 2025",
                    "This {topic} hack saved me 10 hours per week",
                    "Stop paying for {topic} — use these free alternatives",
                ]
            },
            FunnelStage.RETENTION: {
                "goal": "Build community loyalty and advocacy",
                "content_types": ["post", "story", "carousel"],
                "preferred_formats": ["community_challenge", "behind_scenes", "poll", "ama"],
                "tone": "personal, community-driven, exclusive",
                "cta_types": ["participate", "challenge", "share_experience"],
                "kpis": ["story_replies", "repeat_engagement", "ugc_created", "community_posts"],
                "psychology": ["belonging", "commitment", "reciprocity"],
                "aida_focus": AIDAPhase.ACTION,
                "hashtag_strategy": "branded",  # Community identity
                "hooks": [
                    "Only for our AI Multiverse family 🤖 {topic} challenge!",
                    "Your results from last week's {topic} challenge were INSANE",
                    "Behind the scenes: How I research {topic} content for you",
                    "Community spotlight: What you taught me about {topic}",
                    "Unpopular opinion about {topic} — agree or disagree? 👇",
                ]
            }
        }

    def create_content_brief(self, topic: str,
                              target_stage: FunnelStage = None) -> FunnelContentBrief:
        """
        Create a strategic content brief for a given topic.
        Automatically selects the funnel stage based on distribution goals,
        or uses the specified target stage.
        """
        # Auto-select stage based on distribution if not specified
        if target_stage is None:
            target_stage = self._select_next_stage()

        stage_config = self.stage_content_map[target_stage]

        # Select content type and format
        content_type = random.choice(stage_config["content_types"])
        recommended_format = random.choice(stage_config["preferred_formats"])
        psychology_trigger = random.choice(stage_config["psychology"])
        cta_type = random.choice(stage_config["cta_types"])

        # Create topic angle
        hook_template = random.choice(stage_config["hooks"])
        topic_angle = hook_template.format(topic=topic)

        brief = FunnelContentBrief(
            funnel_stage=target_stage,
            aida_phase=stage_config["aida_focus"],
            content_type=content_type,
            topic_angle=topic_angle,
            psychology_trigger=psychology_trigger,
            tone=stage_config["tone"],
            cta_type=cta_type,
            kpis=stage_config["kpis"],
            hashtag_strategy=stage_config["hashtag_strategy"],
            engagement_hook=topic_angle,
            recommended_format=recommended_format
        )

        # Track for distribution balancing
        self.content_history.append({
            "stage": target_stage.value,
            "timestamp": datetime.now().isoformat()
        })

        logger.info(f"📋 Content brief created: {target_stage.value} | "
                     f"{content_type} | {psychology_trigger} | {recommended_format}")
        return brief

    def create_daily_content_plan(self, topics: List[str],
                                   posts_per_day: int = None) -> List[FunnelContentBrief]:
        """
        Create a balanced daily content plan across funnel stages.
        Ensures strategic distribution of TOFU/MOFU/BOFU/Retention content.
        """
        posts_per_day = posts_per_day or SETTINGS.MAX_POSTS_PER_DAY
        plan = []

        # Determine stage allocation for the day
        stage_allocation = self._calculate_daily_allocation(posts_per_day)

        topic_idx = 0
        for stage, count in stage_allocation.items():
            for _ in range(count):
                topic = topics[topic_idx % len(topics)]
                brief = self.create_content_brief(topic, target_stage=stage)
                plan.append(brief)
                topic_idx += 1

        logger.info(f"📅 Daily plan created: {len(plan)} posts across "
                     f"{len(stage_allocation)} funnel stages")
        return plan

    def get_stage_recommendations(self, current_metrics: Dict) -> Dict:
        """
        Analyze current performance and recommend funnel stage focus.
        This is the 'marketing director brain' — it looks at the big picture.
        """
        recommendations = {
            "current_balance": self._analyze_stage_balance(),
            "recommendations": [],
            "priority_stage": None,
            "reasoning": ""
        }

        balance = recommendations["current_balance"]

        # Check if any stage is underserved
        for stage, target_pct in self.funnel_distribution.items():
            actual_pct = balance.get(stage, 0)
            gap = target_pct - actual_pct

            if gap > 0.1:  # More than 10% below target
                recommendations["recommendations"].append({
                    "stage": stage,
                    "action": f"Increase {stage.upper()} content by {gap*100:.0f}%",
                    "reason": f"Currently at {actual_pct*100:.0f}% vs target {target_pct*100:.0f}%"
                })
                if recommendations["priority_stage"] is None or gap > 0.15:
                    recommendations["priority_stage"] = stage

        # Growth-specific recommendations
        follower_growth = current_metrics.get("follower_growth_rate", 0)
        engagement_rate = current_metrics.get("engagement_rate", 0)

        if follower_growth < 0.02:  # Less than 2% growth
            recommendations["recommendations"].append({
                "stage": "tofu",
                "action": "Increase TOFU viral content for reach",
                "reason": f"Follower growth at {follower_growth*100:.1f}% — need more awareness"
            })

        if engagement_rate < 0.05:  # Less than 5% engagement
            recommendations["recommendations"].append({
                "stage": "mofu",
                "action": "Create more value-driven MOFU content",
                "reason": f"Engagement at {engagement_rate*100:.1f}% — need more depth"
            })

        return recommendations

    def apply_aida_to_caption(self, raw_caption: str, stage: FunnelStage) -> str:
        """
        Structure a caption using the AIDA model.
        Ensures every caption has Attention → Interest → Desire → Action flow.
        """
        stage_config = self.stage_content_map[stage]
        aida_template = {
            FunnelStage.TOFU: "🔥 {hook}\n\n{body}\n\n💡 Did you know? Most people miss this.\n\n👉 {cta}\n\n{question}",
            FunnelStage.MOFU: "📚 {hook}\n\n{body}\n\n💾 Save this for later — you'll thank yourself.\n\n👉 {cta}\n\n{question}",
            FunnelStage.BOFU: "🚀 {hook}\n\n{body}\n\n⚡ Don't wait — opportunities like this don't last.\n\n👉 {cta}\n\n{question}",
            FunnelStage.RETENTION: "🤖 {hook}\n\n{body}\n\n💬 Our community is the best. Prove it below 👇\n\n👉 {cta}\n\n{question}",
        }

        # This is a structural guide — actual content generation is in Gemini
        return aida_template.get(stage, "{hook}\n\n{body}\n\n{cta}")

    # ─── Private Methods ──────────────────────────────────────────────────

    def _select_next_stage(self) -> FunnelStage:
        """Select the next funnel stage based on distribution goals."""
        balance = self._analyze_stage_balance()

        # Find the stage with the biggest gap between target and actual
        max_gap = -1
        next_stage = FunnelStage.TOFU  # Default

        for stage_str, target_pct in self.funnel_distribution.items():
            actual_pct = balance.get(stage_str, 0)
            gap = target_pct - actual_pct
            if gap > max_gap:
                max_gap = gap
                next_stage = FunnelStage(stage_str)

        return next_stage

    def _analyze_stage_balance(self) -> Dict[str, float]:
        """Analyze the current distribution of content across funnel stages."""
        if not self.content_history:
            return {stage: 0.0 for stage in self.funnel_distribution.keys()}

        # Only look at recent history (last 30 days)
        cutoff = (datetime.now() - timedelta(days=30)).isoformat()
        recent = [h for h in self.content_history
                  if h["timestamp"] > cutoff]

        if not recent:
            return {stage: 0.0 for stage in self.funnel_distribution.keys()}

        total = len(recent)
        balance = {}
        for stage in self.funnel_distribution.keys():
            count = sum(1 for h in recent if h["stage"] == stage)
            balance[stage] = count / total

        return balance

    def _calculate_daily_allocation(self, posts_per_day: int) -> Dict[FunnelStage, int]:
        """Calculate how many posts per funnel stage for today."""
        allocation = {}
        remaining = posts_per_day

        # Sort by priority (TOFU first for growth)
        stages_by_weight = sorted(
            self.funnel_distribution.items(),
            key=lambda x: x[1],
            reverse=True
        )

        for stage_str, weight in stages_by_weight:
            count = max(1, round(posts_per_day * weight))
            count = min(count, remaining)
            if count > 0:
                allocation[FunnelStage(stage_str)] = count
                remaining -= count
            if remaining <= 0:
                break

        # Ensure at least one TOFU post for growth
        if FunnelStage.TOFU not in allocation and remaining > 0:
            allocation[FunnelStage.TOFU] = 1

        return allocation

    def to_dict(self, brief: FunnelContentBrief) -> Dict:
        """Convert a FunnelContentBrief to a dictionary for JSON serialization."""
        return {
            "funnel_stage": brief.funnel_stage.value,
            "aida_phase": brief.aida_phase.value,
            "content_type": brief.content_type,
            "topic_angle": brief.topic_angle,
            "psychology_trigger": brief.psychology_trigger,
            "tone": brief.tone,
            "cta_type": brief.cta_type,
            "kpis": brief.kpis,
            "hashtag_strategy": brief.hashtag_strategy,
            "engagement_hook": brief.engagement_hook,
            "recommended_format": brief.recommended_format,
        }


# Global instance
funnel_engine = SalesFunnelEngine()
