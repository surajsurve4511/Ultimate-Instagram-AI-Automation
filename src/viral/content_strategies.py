"""
Advanced viral content strategies and crowd attraction mechanisms.
"""
from typing import List, Dict, Tuple
from enum import Enum
from dataclasses import dataclass
import random
from datetime import datetime, timedelta

class ViralStrategy(Enum):
    CONTROVERSY = "controversy"
    HUMOR = "humor"
    SHOCK_VALUE = "shock_value"
    INSIDER_SECRETS = "insider_secrets"
    PREDICTIONS = "predictions"
    CHALLENGES = "challenges"
    BEHIND_SCENES = "behind_scenes"
    DEBUNKING = "debunking"
    COMPARISONS = "comparisons"
    TUTORIALS = "tutorials"

@dataclass
class ViralContentPattern:
    strategy: ViralStrategy
    templates: List[str]
    hashtags: List[str]
    engagement_hooks: List[str]
    viral_score: float

class ViralContentGenerator:
    def __init__(self):
        self.viral_patterns = {
            ViralStrategy.CONTROVERSY: ViralContentPattern(
                strategy=ViralStrategy.CONTROVERSY,
                templates=[
                    "🔥 UNPOPULAR OPINION: {topic}\n\n{reasoning}\n\nAgree or disagree? Let me know! 👇",
                    "⚡ HOT TAKE: Everyone's wrong about {topic}\n\n{explanation}\n\nChange my mind in the comments! 🤔",
                    "🌶️ Controversial but true: {statement}\n\n{evidence}\n\nDo you dare to share this? 💪"
                ],
                hashtags=["#UnpopularOpinion", "#HotTake", "#Controversial", "#AIDebate", "#TechTruth"],
                engagement_hooks=["Agree or disagree?", "Change my mind!", "Who else thinks this?"],
                viral_score=0.9
            ),
            
            ViralStrategy.INSIDER_SECRETS: ViralContentPattern(
                strategy=ViralStrategy.INSIDER_SECRETS,
                templates=[
                    "🤫 SECRET that AI companies don't want you to know:\n\n{secret}\n\n{explanation}\n\nSave this before it gets taken down! 💾",
                    "🔒 LEAKED: What's really happening at {company}\n\n{insider_info}\n\nYou didn't hear this from me... 👀",
                    "🚨 INSIDER REVEALS: The truth about {topic}\n\n{revelation}\n\nTag someone who needs to see this! 🏷️"
                ],
                hashtags=["#AISecrets", "#TechInsider", "#Leaked", "#BehindTheScenes", "#TechTruth"],
                engagement_hooks=["Save this!", "You didn't hear this from me", "Tag someone who needs this"],
                viral_score=0.95
            ),
            
            ViralStrategy.PREDICTIONS: ViralContentPattern(
                strategy=ViralStrategy.PREDICTIONS,
                templates=[
                    "🔮 PREDICTION: In 2025, {prediction}\n\n{reasoning}\n\nScreenshot this and thank me later! 📸",
                    "⚡ CALLING IT NOW: {bold_prediction}\n\n{evidence}\n\nRemindMe! 1 year 📅",
                    "🎯 MY BOLD PREDICTION: {future_scenario}\n\n{logic}\n\nWho's brave enough to bet against me? 💰"
                ],
                hashtags=["#AIFuture", "#TechPrediction", "#2025Forecast", "#FutureTech", "#AIRevolution"],
                engagement_hooks=["Screenshot this!", "RemindMe!", "Who's betting against me?"],
                viral_score=0.85
            ),
            
            ViralStrategy.CHALLENGES: ViralContentPattern(
                strategy=ViralStrategy.CHALLENGES,
                templates=[
                    "🏆 30-DAY AI CHALLENGE: {challenge_description}\n\nDay 1: {task}\n\nWho's joining me? Comment 'IN' below! 💪",
                    "⚡ CHALLENGE ACCEPTED: {dare}\n\n{rules}\n\nTag 3 friends to join! 👥",
                    "🎯 VIRAL CHALLENGE: Can you {task}?\n\n{instructions}\n\nPost your results with #AIChallenge! 🚀"
                ],
                hashtags=["#AIChallenge", "#30DayChallenge", "#TechChallenge", "#LearnAI", "#SkillUp"],
                engagement_hooks=["Who's joining?", "Comment 'IN'", "Tag 3 friends"],
                viral_score=0.92
            ),
            
            ViralStrategy.DEBUNKING: ViralContentPattern(
                strategy=ViralStrategy.DEBUNKING,
                templates=[
                    "❌ MYTH BUSTED: {myth}\n\n✅ REALITY: {truth}\n\n{explanation}\n\nStop believing this lie! 🛑",
                    "🚫 EVERYONE'S WRONG ABOUT: {misconception}\n\n📊 THE FACTS: {facts}\n\nShare to educate others! 📚",
                    "💥 EXPOSED: Why {popular_belief} is completely false\n\n{evidence}\n\nI can't believe people still think this! 😤"
                ],
                hashtags=["#MythBusted", "#AIFacts", "#TechTruth", "#FactCheck", "#StopTheLies"],
                engagement_hooks=["Stop believing this!", "Share to educate", "I can't believe people think this"],
                viral_score=0.88
            )
        }
        
        # Advanced viral hooks
        self.viral_hooks = [
            "This will blow your mind in 30 seconds:",
            "Everyone's doing AI wrong except this person:",
            "The AI secret that changed everything:",
            "Why 99% of people fail at AI (and how to be the 1%):",
            "This AI hack will save you 10 hours per week:",
            "The $1B AI mistake everyone's making:",
            "Plot twist: AI isn't what you think it is",
            "This AI tool is about to disrupt everything:",
            "The AI revolution starts with this one trick:",
            "Warning: This AI knowledge is dangerous:"
        ]
        
        # Emotional triggers
        self.emotional_triggers = {
            "curiosity": ["You won't believe", "The secret behind", "What they don't tell you"],
            "urgency": ["Before it's too late", "Limited time", "Right now"],
            "exclusivity": ["Only 1% know this", "Exclusive access", "VIP information"],
            "fear": ["Don't miss out", "Before you lose", "Critical warning"],
            "achievement": ["Level up", "Become elite", "Master this"],
            "social_proof": ["Everyone's talking about", "Viral technique", "Trending method"]
        }

    def generate_viral_content(self, base_content: str, category: str) -> Dict:
        """Generate viral version of content"""
        # Select random viral strategy
        strategy = random.choice(list(self.viral_patterns.keys()))
        pattern = self.viral_patterns[strategy]
        
        # Choose template
        template = random.choice(pattern.templates)
        
        # Generate viral elements
        viral_hook = random.choice(self.viral_hooks)
        emotional_trigger = self._get_emotional_trigger()
        
        # Create viral content
        viral_content = {
            "strategy": strategy.value,
            "hook": viral_hook,
            "template": template,
            "hashtags": pattern.hashtags + ["#ViralAI", "#TechViral", "#AIExposed"],
            "engagement_hook": random.choice(pattern.engagement_hooks),
            "emotional_trigger": emotional_trigger,
            "viral_score": pattern.viral_score,
            "content_type": self._determine_content_type(strategy)
        }
        
        return viral_content
    
    def _get_emotional_trigger(self) -> str:
        """Get random emotional trigger"""
        emotion = random.choice(list(self.emotional_triggers.keys()))
        return random.choice(self.emotional_triggers[emotion])
    
    def _determine_content_type(self, strategy: ViralStrategy) -> str:
        """Determine best content type for strategy"""
        content_types = {
            ViralStrategy.CONTROVERSY: "debate_post",
            ViralStrategy.INSIDER_SECRETS: "revelation_post",
            ViralStrategy.PREDICTIONS: "forecast_post",
            ViralStrategy.CHALLENGES: "challenge_post",
            ViralStrategy.DEBUNKING: "educational_post"
        }
        return content_types.get(strategy, "standard_post")

    def create_viral_series(self, topic: str) -> List[Dict]:
        """Create a series of viral posts around a topic"""
        series_templates = [
            "Part 1/5: The shocking truth about {topic}",
            "Part 2/5: What the experts don't want you to know",
            "Part 3/5: The insider secrets revealed",
            "Part 4/5: How this changes everything",
            "Part 5/5: Your action plan for success"
        ]
        
        series = []
        for i, template in enumerate(series_templates, 1):
            content = {
                "part": i,
                "total_parts": len(series_templates),
                "title": template.format(topic=topic),
                "viral_strategy": "series_building",
                "engagement_hook": f"Part {i} is ready! Who's following the series?",
                "hashtags": [f"#AISeries", f"#Part{i}", "#Viral", "#MustRead"],
                "viral_score": 0.93
            }
            series.append(content)
        
        return series

    def generate_trend_riding_content(self, trending_topic: str) -> Dict:
        """Generate content that rides current trends"""
        trend_templates = [
            "🔥 {trend} + AI = Mind Blown\n\nHere's how AI is revolutionizing {trend}:",
            "⚡ Everyone's talking about {trend}, but here's the AI angle no one sees:",
            "🌟 {trend} is trending, but wait until you see what AI can do with it:",
            "🚀 Plot twist: {trend} is actually powered by AI (and here's proof):"
        ]
        
        template = random.choice(trend_templates)
        
        return {
            "template": template.format(trend=trending_topic),
            "strategy": "trend_riding",
            "hashtags": [f"#{trending_topic.replace(' ', '')}", "#AITrend", "#Trending", "#Viral"],
            "viral_score": 0.87,
            "timing": "immediate"  # Post ASAP while trend is hot
        }

# Global viral content generator
viral_generator = ViralContentGenerator()
