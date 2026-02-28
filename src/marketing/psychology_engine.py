"""
Psychology Engine — Implements Cialdini's 6 principles and cognitive biases
for maximum content engagement.

This module replicates how top marketing professionals think about audience
psychology. Every content decision is backed by proven persuasion science.

The 6 Principles:
  1. Reciprocity:  Give value first → they feel compelled to engage
  2. Commitment:   Small public pledges → escalating loyalty
  3. Social Proof:  Show others engaging → herd behavior triggers
  4. Authority:    Expert positioning → trust and credibility
  5. Liking:       Relatable personas → parasocial connection
  6. Scarcity:     Limited access → urgency and desire
"""
import random
import logging
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum
from dataclasses import dataclass

from src.config.settings import SETTINGS

logger = logging.getLogger(__name__)


class PsychologyPrinciple(Enum):
    """Cialdini's 6 principles of persuasion."""
    RECIPROCITY = "reciprocity"
    COMMITMENT = "commitment"
    SOCIAL_PROOF = "social_proof"
    AUTHORITY = "authority"
    LIKING = "liking"
    SCARCITY = "scarcity"


class EmotionalTrigger(Enum):
    """Primary emotional triggers for content."""
    CURIOSITY = "curiosity"
    FOMO = "fear_of_missing_out"
    ASPIRATION = "aspiration"
    SURPRISE = "surprise"
    URGENCY = "urgency"
    BELONGING = "belonging"
    PRIDE = "pride"
    OUTRAGE = "outrage"  # Controlled controversy


@dataclass
class PsychologyBrief:
    """Psychology-informed content strategy brief."""
    primary_principle: PsychologyPrinciple
    secondary_principle: PsychologyPrinciple
    emotional_trigger: EmotionalTrigger
    hook_template: str
    cta_template: str
    engagement_mechanic: str
    caption_framework: str
    power_words: List[str]
    cognitive_bias: str
    expected_reaction: str


class PsychologyEngine:
    """
    Applies proven persuasion psychology to content creation.
    
    Thinks like a behavioral psychologist designing each piece of content
    to trigger specific cognitive responses and actions.
    """

    def __init__(self):
        self.trigger_weights = SETTINGS.PSYCHOLOGY_TRIGGERS
        self.principle_history = []  # Track usage for variety

        # ─── Principle Playbooks ──────────────────────────────────────

        self.principle_playbooks = {
            PsychologyPrinciple.RECIPROCITY: {
                "description": "Give massive value first — audience feels obligation to engage",
                "hooks": [
                    "FREE: The {topic} resource that took me 50 hours to build",
                    "I'm giving away my complete {topic} strategy (save this 💾)",
                    "Here's everything I wish someone told me about {topic}",
                    "My best {topic} tips — all free, no strings attached 🎁",
                    "I compiled the ultimate {topic} guide so you don't have to",
                ],
                "ctas": [
                    "I spent weeks creating this. All I ask? Share it with one friend who needs it 🤝",
                    "If this helped you, drop a 💾 so I know to make more like this",
                    "This was free. The only 'cost'? Tag someone who NEEDS this 👇",
                    "Save this for when you need it — and comment which tip was best!",
                ],
                "engagement_mechanics": [
                    "Save this for later",
                    "DM '🎁' for bonus resources",
                    "Comment 'YES' for the full breakdown",
                ],
                "power_words": ["free", "gift", "exclusive", "complimentary", "bonus",
                               "unlock", "access", "yours"],
                "cognitive_bias": "Reciprocity bias — receiving value creates social obligation",
            },
            PsychologyPrinciple.COMMITMENT: {
                "description": "Get small commitments that escalate into loyalty",
                "hooks": [
                    "Challenge: Can you learn {topic} in 7 days? 🏆",
                    "Drop a 🤖 if you're committed to learning {topic} this year",
                    "Day 1 of my {topic} journey — who's joining me?",
                    "I'm making a public commitment: Master {topic} by 2025",
                    "The {topic} accountability thread — post your progress below 📈",
                ],
                "ctas": [
                    "Make it official: Comment 'I'M IN 🚀' below to join the challenge",
                    "Public commitment = 3x follow-through. Type your goal below 👇",
                    "Join the challenge: Day 1 starts NOW. Comment your commitment.",
                    "Drop a 🔥 if you're doing this with us — we're in this together",
                ],
                "engagement_mechanics": [
                    "Challenge participation",
                    "Public pledge in comments",
                    "Progress reporting",
                    "Streak tracking",
                ],
                "power_words": ["commit", "join", "challenge", "together", "pledge",
                               "promise", "accountability", "streak"],
                "cognitive_bias": "Commitment-consistency — public statements drive follow-through",
            },
            PsychologyPrinciple.SOCIAL_PROOF: {
                "description": "Show others engaging to trigger herd behavior",
                "hooks": [
                    "10,000+ people are already learning {topic} with us 🤯",
                    "This {topic} post got 5,000 saves. Here's why 👇",
                    "Everyone is talking about {topic} — here's what they're saying",
                    "My followers asked for {topic} content 200+ times. Here you go!",
                    "The {topic} tip that went viral with 500K views last week",
                ],
                "ctas": [
                    "Join the 10,000+ who already follow for daily AI insights 🤖",
                    "This is our most saved post EVER. Don't be the one who missed it 💾",
                    "Our community is growing fast — follow before we go private 🔒",
                    "500 people asked for this in DMs. Share with someone who needs it!",
                ],
                "engagement_mechanics": [
                    "Highlight community size",
                    "Show engagement metrics",
                    "Feature user testimonials",
                    "Display follower milestones",
                ],
                "power_words": ["everyone", "trending", "viral", "most popular",
                               "thousands", "community", "join", "growing"],
                "cognitive_bias": "Bandwagon effect — people follow what others are doing",
            },
            PsychologyPrinciple.AUTHORITY: {
                "description": "Position as the expert — build trust through demonstrated knowledge",
                "hooks": [
                    "After 5 years studying {topic}, here's what actually matters",
                    "I reviewed 100+ {topic} papers. Here's the #1 insight.",
                    "The truth about {topic} that most 'experts' won't tell you",
                    "PhD researcher explains {topic} in 60 seconds",
                    "Breaking: New {topic} research changes everything we knew",
                ],
                "ctas": [
                    "Follow for research-backed AI insights you won't find elsewhere 🧪",
                    "Save this — it's based on actual research, not opinions 📊",
                    "Want the full research breakdown? DM 'RESEARCH' 🔬",
                    "This is backed by data, not hype. Share with someone who needs facts.",
                ],
                "engagement_mechanics": [
                    "Cite research and data",
                    "Use academic credibility",
                    "Reference expert opinions",
                    "Show credentials",
                ],
                "power_words": ["research", "study", "proven", "data", "expert",
                               "science", "fact", "evidence", "peer-reviewed"],
                "cognitive_bias": "Authority bias — expert signals increase trust and compliance",
            },
            PsychologyPrinciple.LIKING: {
                "description": "Be relatable and build parasocial connections",
                "hooks": [
                    "Honest confession: I failed at {topic} before I succeeded",
                    "The {topic} mistake that almost ended my career (story time 🫠)",
                    "Real talk about {topic} — no sugar coating",
                    "My unpopular opinion about {topic}: hot take incoming 🔥",
                    "Behind the scenes of how I actually learn about {topic}",
                ],
                "ctas": [
                    "Can you relate? Tell me your {topic} story below 👇",
                    "Follow for honest AI content — no fake guru energy 🙅",
                    "DM me if you've experienced this too — you're not alone 💪",
                    "Share your honest experience with {topic} — I'll reply to every comment",
                ],
                "engagement_mechanics": [
                    "Personal stories",
                    "Behind-the-scenes content",
                    "Vulnerability and honesty",
                    "Reply to all comments",
                ],
                "power_words": ["honestly", "real talk", "confession", "personal",
                               "behind the scenes", "story", "relatable", "human"],
                "cognitive_bias": "Liking principle — we engage more with people we relate to",
            },
            PsychologyPrinciple.SCARCITY: {
                "description": "Create urgency through limited access or time",
                "hooks": [
                    "This {topic} resource will be deleted in 24 hours ⏳",
                    "Only sharing this {topic} secret ONCE — screenshot NOW",
                    "🚨 Limited time: Free {topic} masterclass (spots filling fast)",
                    "This {topic} hack won't work after the next update — act NOW",
                    "Deleting this post tomorrow — save it while you can 💾",
                ],
                "ctas": [
                    "Save NOW — this post goes away in 24 hours ⏰",
                    "Only 50 spots left. DM 'SPOT' before they're gone 🔥",
                    "This offer expires tonight. Don't say I didn't warn you ⚡",
                    "Screenshot this before it's gone — you'll need it later 📸",
                ],
                "engagement_mechanics": [
                    "Limited time offers",
                    "Countdown urgency",
                    "Exclusive access",
                    "Early bird benefits",
                ],
                "power_words": ["limited", "exclusive", "only", "now", "hurry",
                               "last chance", "deadline", "rare", "vanishing"],
                "cognitive_bias": "Scarcity bias — perceived rarity increases perceived value",
            },
        }

        # ─── Emotional Trigger Templates ─────────────────────────────

        self.emotional_triggers = {
            EmotionalTrigger.CURIOSITY: {
                "patterns": [
                    "The {topic} secret nobody is talking about...",
                    "What happens when you combine {topic} with this?",
                    "I discovered something about {topic} that blew my mind 🤯",
                ],
                "gap_technique": "Open a question → withhold the answer → deliver in the content"
            },
            EmotionalTrigger.FOMO: {
                "patterns": [
                    "Everyone is switching to {topic} — are you behind?",
                    "If you're not using {topic} yet, you're already losing",
                    "The {topic} shift is happening NOW — here's how to catch up",
                ],
                "gap_technique": "Highlight what they miss if they don't act"
            },
            EmotionalTrigger.ASPIRATION: {
                "patterns": [
                    "How {topic} can 10x your career in 2025",
                    "From zero to {topic} expert — the realistic path",
                    "The {topic} skill that will define the next decade of AI",
                ],
                "gap_technique": "Paint the future they want → show the path there"
            },
            EmotionalTrigger.SURPRISE: {
                "patterns": [
                    "Plot twist: {topic} works the OPPOSITE of what you'd expect",
                    "This {topic} fact made me question everything I knew",
                    "Wait — {topic} can actually do THAT? 😱",
                ],
                "gap_technique": "Subvert expectations → deliver the twist → explain why"
            },
            EmotionalTrigger.URGENCY: {
                "patterns": [
                    "You have 30 days to learn {topic} before it's too late",
                    "The {topic} window is closing — here's your last chance",
                    "{topic} is changing THIS WEEK — prepare now or fall behind",
                ],
                "gap_technique": "Create a time-bound reason to act immediately"
            },
            EmotionalTrigger.BELONGING: {
                "patterns": [
                    "Welcome to the {topic} revolution — you're one of us now 🤖",
                    "If you understand {topic}, you're ahead of 99% of people",
                    "The {topic} community is the best on Instagram — here's why",
                ],
                "gap_technique": "Define an in-group → invite them in → celebrate membership"
            },
        }

    def create_psychology_brief(self, topic: str,
                                  target_principle: PsychologyPrinciple = None,
                                  target_emotion: EmotionalTrigger = None) -> PsychologyBrief:
        """
        Create a psychology-informed content strategy brief.
        Selects the optimal psychological approach for the topic.
        """
        if target_principle is None:
            target_principle = self._select_principle()

        if target_emotion is None:
            target_emotion = self._select_emotion(target_principle)

        secondary = self._select_complementary_principle(target_principle)
        playbook = self.principle_playbooks[target_principle]

        # Build the brief
        hook = random.choice(playbook["hooks"]).format(topic=topic)
        cta = random.choice(playbook["ctas"]).format(topic=topic)
        mechanic = random.choice(playbook["engagement_mechanics"])

        # Build caption framework using AIDA + psychology
        caption_framework = self._build_caption_framework(
            target_principle, target_emotion, topic
        )

        brief = PsychologyBrief(
            primary_principle=target_principle,
            secondary_principle=secondary,
            emotional_trigger=target_emotion,
            hook_template=hook,
            cta_template=cta,
            engagement_mechanic=mechanic,
            caption_framework=caption_framework,
            power_words=playbook["power_words"],
            cognitive_bias=playbook["cognitive_bias"],
            expected_reaction=f"{target_emotion.value} → {target_principle.value} compliance"
        )

        self.principle_history.append({
            "principle": target_principle.value,
            "emotion": target_emotion.value,
            "timestamp": datetime.now().isoformat()
        })

        logger.info(f"🧠 Psychology brief: {target_principle.value} + {target_emotion.value}")
        return brief

    def get_power_words(self, principle: PsychologyPrinciple = None,
                         count: int = 5) -> List[str]:
        """Get persuasive power words for a specific principle or mixed."""
        if principle:
            words = self.principle_playbooks[principle]["power_words"]
        else:
            all_words = []
            for pb in self.principle_playbooks.values():
                all_words.extend(pb["power_words"])
            words = list(set(all_words))

        return random.sample(words, min(count, len(words)))

    def analyze_caption_psychology(self, caption: str) -> Dict:
        """Analyze which psychology principles a caption uses (heuristic-based)."""
        analysis = {
            "principles_detected": [],
            "emotions_detected": [],
            "power_words_found": [],
            "psychology_score": 0.0,
            "suggestions": []
        }

        caption_lower = caption.lower()

        # Check each principle
        for principle, playbook in self.principle_playbooks.items():
            words_found = [w for w in playbook["power_words"] if w.lower() in caption_lower]
            if words_found:
                analysis["principles_detected"].append(principle.value)
                analysis["power_words_found"].extend(words_found)

        # Check emotional triggers
        for trigger, config in self.emotional_triggers.items():
            for pattern in config["patterns"]:
                # Simplified pattern matching
                key_phrases = pattern.replace("{topic}", "").strip().lower().split()
                if any(phrase in caption_lower for phrase in key_phrases if len(phrase) > 4):
                    if trigger.value not in analysis["emotions_detected"]:
                        analysis["emotions_detected"].append(trigger.value)

        # Score
        score = 0.0
        score += min(0.3, len(analysis["principles_detected"]) * 0.15)
        score += min(0.3, len(analysis["power_words_found"]) * 0.05)
        score += min(0.2, len(analysis["emotions_detected"]) * 0.1)

        # Check for CTA
        cta_indicators = ["follow", "save", "share", "comment", "dm", "click", "join", "tag"]
        if any(ind in caption_lower for ind in cta_indicators):
            score += 0.2

        analysis["psychology_score"] = min(1.0, score)

        # Add suggestions
        if not analysis["principles_detected"]:
            analysis["suggestions"].append("Add persuasion elements: power words, social proof, or urgency")
        if not analysis["emotions_detected"]:
            analysis["suggestions"].append("Missing emotional trigger — add curiosity gap or FOMO")
        if score < 0.5:
            analysis["suggestions"].append("Caption lacks psychological depth — consider using AIDA model")

        return analysis

    # ─── Private Methods ──────────────────────────────────────────────────

    def _select_principle(self) -> PsychologyPrinciple:
        """Select principle based on weighted distribution and variety."""
        principles = list(PsychologyPrinciple)
        weights = [self.trigger_weights.get(p.value, 0.1) for p in principles]

        # Reduce weight of recently used principles
        if self.principle_history:
            recent = [h["principle"] for h in self.principle_history[-5:]]
            for i, p in enumerate(principles):
                if p.value in recent:
                    weights[i] *= 0.5  # Halve weight for recent usage

        # Normalize
        total = sum(weights)
        weights = [w / total for w in weights]

        return random.choices(principles, weights=weights, k=1)[0]

    def _select_emotion(self, principle: PsychologyPrinciple) -> EmotionalTrigger:
        """Select the best emotional trigger for a given principle."""
        emotion_map = {
            PsychologyPrinciple.RECIPROCITY: [EmotionalTrigger.ASPIRATION, EmotionalTrigger.BELONGING],
            PsychologyPrinciple.COMMITMENT: [EmotionalTrigger.PRIDE, EmotionalTrigger.BELONGING],
            PsychologyPrinciple.SOCIAL_PROOF: [EmotionalTrigger.FOMO, EmotionalTrigger.BELONGING],
            PsychologyPrinciple.AUTHORITY: [EmotionalTrigger.CURIOSITY, EmotionalTrigger.SURPRISE],
            PsychologyPrinciple.LIKING: [EmotionalTrigger.BELONGING, EmotionalTrigger.CURIOSITY],
            PsychologyPrinciple.SCARCITY: [EmotionalTrigger.URGENCY, EmotionalTrigger.FOMO],
        }
        options = emotion_map.get(principle, list(EmotionalTrigger))
        return random.choice(options)

    def _select_complementary_principle(self,
                                          primary: PsychologyPrinciple) -> PsychologyPrinciple:
        """Select a complementary secondary principle."""
        combos = {
            PsychologyPrinciple.RECIPROCITY: PsychologyPrinciple.LIKING,
            PsychologyPrinciple.COMMITMENT: PsychologyPrinciple.SOCIAL_PROOF,
            PsychologyPrinciple.SOCIAL_PROOF: PsychologyPrinciple.SCARCITY,
            PsychologyPrinciple.AUTHORITY: PsychologyPrinciple.SOCIAL_PROOF,
            PsychologyPrinciple.LIKING: PsychologyPrinciple.RECIPROCITY,
            PsychologyPrinciple.SCARCITY: PsychologyPrinciple.AUTHORITY,
        }
        return combos.get(primary, PsychologyPrinciple.SOCIAL_PROOF)

    def _build_caption_framework(self, principle: PsychologyPrinciple,
                                   emotion: EmotionalTrigger,
                                   topic: str) -> str:
        """Build a structured caption framework combining principle + emotion."""
        return (
            f"[HOOK: {emotion.value} trigger about {topic}]\n\n"
            f"[BODY: Apply {principle.value} — {self.principle_playbooks[principle]['description']}]\n\n"
            f"[PROOF: Social proof or authority element]\n\n"
            f"[CTA: {principle.value}-based call to action]\n\n"
            f"[POWER WORDS: Use {', '.join(random.sample(self.principle_playbooks[principle]['power_words'], 3))}]"
        )

    def to_dict(self, brief: PsychologyBrief) -> Dict:
        """Convert PsychologyBrief to dictionary."""
        return {
            "primary_principle": brief.primary_principle.value,
            "secondary_principle": brief.secondary_principle.value,
            "emotional_trigger": brief.emotional_trigger.value,
            "hook_template": brief.hook_template,
            "cta_template": brief.cta_template,
            "engagement_mechanic": brief.engagement_mechanic,
            "caption_framework": brief.caption_framework,
            "power_words": brief.power_words,
            "cognitive_bias": brief.cognitive_bias,
            "expected_reaction": brief.expected_reaction,
        }


# Global instance
psychology_engine = PsychologyEngine()
