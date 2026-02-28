"""
Storytelling Engine — Creates multi-post narrative arcs and content series
that keep audiences coming back for more.

Professional content creators use storytelling frameworks to:
  - Build suspense across multiple posts (serial content)
  - Create "open loops" that demand completion
  - Use character arcs and transformations
  - Build emotional investment over time
  - Create callbacks and continuity that reward loyal followers

This module generates narrative structures for all content formats.
"""
import random
import logging
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class NarrativeArc(Enum):
    """Classic storytelling arc types."""
    HEROS_JOURNEY = "heros_journey"       # Zero → struggle → mastery
    MYSTERY_REVEAL = "mystery_reveal"     # Question → investigation → answer
    UNDERDOG = "underdog"                 # Unlikely → challenge → triumph
    TRANSFORMATION = "transformation"     # Before → process → after
    COUNTDOWN = "countdown"               # Urgency → milestones → conclusion
    DEBATE = "debate"                     # Side A vs Side B → verdict


class SeriesType(Enum):
    """Types of content series."""
    DAILY_TIPS = "daily_tips"
    WEEKLY_DEEP_DIVE = "weekly_deep_dive"
    CHALLENGE = "challenge"
    PROGRESSIVE_LEARNING = "progressive_learning"
    MYTH_BUSTING = "myth_busting"
    PREDICTIONS = "predictions"


@dataclass
class StoryBeat:
    """A single beat/moment in a story arc."""
    beat_number: int
    title: str
    content_hook: str
    body_outline: str
    cliffhanger: str       # Open loop for next beat
    emotional_peak: str    # Target emotion at this beat
    content_format: str    # post, carousel, reel, story
    callback: str          # Reference to earlier beat (if any)


@dataclass
class ContentSeries:
    """A planned multi-post content series."""
    series_id: str
    name: str
    narrative_arc: NarrativeArc
    topic: str
    total_episodes: int
    beats: List[StoryBeat]
    hashtag: str            # Series-specific hashtag
    recurring_element: str  # Visual/text element for consistency
    hook_pattern: str       # How episodes are numbered/titled
    status: str = "planned"


class StorytellingEngine:
    """
    Creates compelling narrative structures across multiple posts.
    
    Transforms dry topics into stories that keep audiences invested.
    """

    def __init__(self):
        self.active_series = {}
        self.completed_series = []

        # ─── Narrative Arc Templates ──────────────────────────────────

        self.arc_templates = {
            NarrativeArc.HEROS_JOURNEY: {
                "description": "The classic journey from novice to expert",
                "beats": [
                    {"title": "The Ordinary World", "emotion": "relatability",
                     "outline": "Show the everyday struggle everyone faces with {topic}"},
                    {"title": "The Call to Adventure", "emotion": "curiosity",
                     "outline": "Reveal why {topic} is about to change everything"},
                    {"title": "Crossing the Threshold", "emotion": "excitement",
                     "outline": "First steps into mastering {topic} — the basics that matter"},
                    {"title": "Tests and Allies", "emotion": "struggle",
                     "outline": "Common challenges in {topic} and how to overcome them"},
                    {"title": "The Transformation", "emotion": "triumph",
                     "outline": "The 'aha moment' when {topic} finally clicks"},
                    {"title": "The Return with Knowledge", "emotion": "empowerment",
                     "outline": "Sharing mastery of {topic} — the expert perspective"},
                ],
                "ideal_for": ["tutorials", "learning_paths", "career_stories"],
            },
            NarrativeArc.MYSTERY_REVEAL: {
                "description": "Build curiosity with progressive revelation",
                "beats": [
                    {"title": "The Mystery", "emotion": "intrigue",
                     "outline": "Something incredible is happening with {topic} — but what?"},
                    {"title": "Clue #1", "emotion": "curiosity",
                     "outline": "First hint about what makes {topic} so powerful"},
                    {"title": "Clue #2", "emotion": "deepening_curiosity",
                     "outline": "More evidence — the pattern becomes clearer"},
                    {"title": "The Red Herring", "emotion": "surprise",
                     "outline": "What most people THINK about {topic} is wrong"},
                    {"title": "The Reveal", "emotion": "enlightenment",
                     "outline": "The truth about {topic} that changes everything"},
                ],
                "ideal_for": ["ai_news", "myth_busting", "insider_secrets"],
            },
            NarrativeArc.TRANSFORMATION: {
                "description": "Before/after transformation story",
                "beats": [
                    {"title": "The Before", "emotion": "empathy",
                     "outline": "Life/work before knowing about {topic}"},
                    {"title": "The Discovery", "emotion": "excitement",
                     "outline": "How {topic} was discovered/encountered"},
                    {"title": "The Process", "emotion": "education",
                     "outline": "Step-by-step implementation of {topic}"},
                    {"title": "The After", "emotion": "aspiration",
                     "outline": "The dramatic results after applying {topic}"},
                ],
                "ideal_for": ["tool_reviews", "case_studies", "career_changes"],
            },
            NarrativeArc.COUNTDOWN: {
                "description": "Urgency-driven countdown series",
                "beats": [
                    {"title": "The Ticking Clock", "emotion": "urgency",
                     "outline": "Why {topic} has a deadline — act now or miss out"},
                    {"title": "Day 3", "emotion": "fomo",
                     "outline": "Progress update — what's changed so far with {topic}"},
                    {"title": "Day 2", "emotion": "tension",
                     "outline": "Almost there — the critical {topic} insights"},
                    {"title": "Day 1", "emotion": "anticipation",
                     "outline": "Final preparations for {topic}"},
                    {"title": "The Moment", "emotion": "climax",
                     "outline": "The big {topic} reveal/launch/conclusion"},
                ],
                "ideal_for": ["product_launches", "events", "challenges"],
            },
            NarrativeArc.DEBATE: {
                "description": "Present two sides, let audience decide",
                "beats": [
                    {"title": "The Question", "emotion": "curiosity",
                     "outline": "The biggest debate in {topic} right now"},
                    {"title": "Side A", "emotion": "agreement",
                     "outline": "The strongest arguments FOR {topic} approach A"},
                    {"title": "Side B", "emotion": "consideration",
                     "outline": "The strongest arguments FOR {topic} approach B"},
                    {"title": "The Evidence", "emotion": "analysis",
                     "outline": "Data and examples from both sides of {topic}"},
                    {"title": "The Verdict", "emotion": "resolution",
                     "outline": "Community verdict + expert analysis on {topic}"},
                ],
                "ideal_for": ["comparisons", "hot_takes", "community_engagement"],
            },
        }

    def create_content_series(self, topic: str,
                                arc_type: NarrativeArc = None,
                                num_episodes: int = None) -> ContentSeries:
        """
        Create a planned content series with a compelling narrative arc.
        """
        if arc_type is None:
            arc_type = self._select_best_arc(topic)

        template = self.arc_templates[arc_type]
        beats_template = template["beats"]

        if num_episodes:
            # Adjust number of beats
            if num_episodes < len(beats_template):
                beats_template = beats_template[:num_episodes]
            elif num_episodes > len(beats_template):
                # Duplicate middle beats for expansion
                extra = num_episodes - len(beats_template)
                middle_idx = len(beats_template) // 2
                for i in range(extra):
                    beats_template.insert(middle_idx + i, {
                        "title": f"Deep Dive Part {i+1}",
                        "emotion": "education",
                        "outline": f"Additional insights about {{topic}} — Part {i+1}"
                    })

        # Generate story beats
        beats = []
        for i, bt in enumerate(beats_template):
            cliffhanger = self._generate_cliffhanger(
                topic, i + 1, len(beats_template), arc_type
            )
            callback = self._generate_callback(i, beats_template) if i > 0 else ""

            beat = StoryBeat(
                beat_number=i + 1,
                title=bt["title"],
                content_hook=self._generate_episode_hook(
                    topic, bt["title"], i + 1, len(beats_template)
                ),
                body_outline=bt["outline"].format(topic=topic),
                cliffhanger=cliffhanger,
                emotional_peak=bt["emotion"],
                content_format=self._select_format_for_beat(i, len(beats_template)),
                callback=callback
            )
            beats.append(beat)

        # Create series-specific hashtag
        topic_slug = topic.lower().replace(" ", "")[:12]
        series_hashtag = f"#AIMultiverse{topic_slug.title()}Series"

        series = ContentSeries(
            series_id=f"series_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            name=f"The {topic} Story",
            narrative_arc=arc_type,
            topic=topic,
            total_episodes=len(beats),
            beats=beats,
            hashtag=series_hashtag,
            recurring_element=f"📌 Part {{n}}/{len(beats)} of our {topic} series",
            hook_pattern=f"Episode {{n}} of '{topic}' — {{title}}",
            status="planned"
        )

        self.active_series[series.series_id] = series
        logger.info(f"📖 Content series created: '{series.name}' with "
                     f"{len(beats)} episodes using {arc_type.value} arc")
        return series

    def get_next_episode(self, series_id: str) -> Optional[StoryBeat]:
        """Get the next episode to post for an active series."""
        series = self.active_series.get(series_id)
        if not series:
            return None

        # Find first unposted beat
        for beat in series.beats:
            # In production, check against posted content DB
            return beat

        return None

    def generate_episode_caption_prompt(self, series: ContentSeries,
                                          beat: StoryBeat) -> str:
        """
        Generate a Gemini prompt for creating the actual episode caption.
        Includes narrative context, callbacks, and cliffhangers.
        """
        prompt = f"""You are writing Episode {beat.beat_number}/{series.total_episodes} of 
an Instagram content series called "{series.name}".

NARRATIVE ARC: {series.narrative_arc.value}
TOPIC: {series.topic}
EPISODE TITLE: {beat.title}

STORY CONTEXT:
- Content outline: {beat.body_outline}
- Target emotion at this point: {beat.emotional_peak}
- This episode's format: {beat.content_format}

{"CALLBACK (reference to previous episode): " + beat.callback if beat.callback else ""}
CLIFFHANGER FOR NEXT EPISODE: {beat.cliffhanger}

INSTRUCTIONS:
1. Start with: "{series.recurring_element.format(n=beat.beat_number)}"
2. Write the hook: {beat.content_hook}
3. Deliver the content outlined above
4. End with the cliffhanger to keep them coming back
5. Use series hashtag: {series.hashtag}

The emotional arc should peak at: {beat.emotional_peak}

Make the audience NEED to see the next episode."""

        return prompt

    # ─── Private Methods ──────────────────────────────────────────────────

    def _select_best_arc(self, topic: str) -> NarrativeArc:
        """Select the most fitting narrative arc for the topic."""
        topic_lower = topic.lower()

        # Simple keyword matching for arc selection
        if any(w in topic_lower for w in ["learn", "tutorial", "guide", "beginner"]):
            return NarrativeArc.HEROS_JOURNEY
        elif any(w in topic_lower for w in ["secret", "hidden", "unknown", "truth"]):
            return NarrativeArc.MYSTERY_REVEAL
        elif any(w in topic_lower for w in ["vs", "compare", "better", "which"]):
            return NarrativeArc.DEBATE
        elif any(w in topic_lower for w in ["results", "change", "before", "after"]):
            return NarrativeArc.TRANSFORMATION
        elif any(w in topic_lower for w in ["launch", "deadline", "coming", "soon"]):
            return NarrativeArc.COUNTDOWN
        else:
            return random.choice(list(NarrativeArc))

    def _generate_cliffhanger(self, topic: str, current: int,
                                total: int, arc: NarrativeArc) -> str:
        """Generate a cliffhanger for the current beat."""
        if current >= total:
            return "🎯 Series complete! What should our next deep dive be about? Comment below!"

        cliffhangers = [
            f"But here's where it gets REALLY interesting... Part {current+1} drops tomorrow 👀",
            f"Wait until you see what we reveal in Part {current+1}... it changes EVERYTHING 🤯",
            f"This was just the beginning. Part {current+1} is where the magic happens ✨",
            f"If you thought this was mind-blowing, Part {current+1} will break your brain 🧠",
            f"Don't miss Part {current+1} — save this post and turn on notifications 🔔",
        ]
        return random.choice(cliffhangers)

    def _generate_callback(self, current_idx: int,
                             beats: List[Dict]) -> str:
        """Generate a callback to a previous episode."""
        if current_idx == 0:
            return ""

        prev_title = beats[current_idx - 1]["title"]
        callbacks = [
            f"Remember in Part {current_idx} when we talked about '{prev_title}'? It gets deeper.",
            f"Building on what we learned in '{prev_title}'...",
            f"If you missed Part {current_idx}, go back — you'll need that context 📌",
        ]
        return random.choice(callbacks)

    def _generate_episode_hook(self, topic: str, title: str,
                                 episode: int, total: int) -> str:
        """Generate a hook for a specific episode."""
        hooks = [
            f"📖 Part {episode}/{total}: {title} — The {topic} saga continues...",
            f"🔥 Episode {episode}: '{title}' — You're NOT ready for this",
            f"📌 {topic} Series [{episode}/{total}] — {title}",
            f"⚡ Part {episode} just dropped! '{title}' — Save this NOW",
        ]
        return random.choice(hooks)

    def _select_format_for_beat(self, beat_idx: int, total_beats: int) -> str:
        """Select optimal content format based on beat position in arc."""
        if beat_idx == 0:
            return "reel"           # Opening — maximum reach
        elif beat_idx == total_beats - 1:
            return "carousel"       # Conclusion — deep engagement
        elif beat_idx == 1:
            return "carousel"       # Second beat — build depth
        else:
            return random.choice(["post", "carousel", "reel"])

    def to_dict(self, series: ContentSeries) -> Dict:
        """Convert ContentSeries to dictionary."""
        return {
            "series_id": series.series_id,
            "name": series.name,
            "narrative_arc": series.narrative_arc.value,
            "topic": series.topic,
            "total_episodes": series.total_episodes,
            "beats": [
                {
                    "beat_number": b.beat_number,
                    "title": b.title,
                    "content_hook": b.content_hook,
                    "body_outline": b.body_outline,
                    "cliffhanger": b.cliffhanger,
                    "emotional_peak": b.emotional_peak,
                    "content_format": b.content_format,
                    "callback": b.callback,
                }
                for b in series.beats
            ],
            "hashtag": series.hashtag,
            "recurring_element": series.recurring_element,
            "hook_pattern": series.hook_pattern,
            "status": series.status,
        }


# Global instance
storytelling_engine = StorytellingEngine()
