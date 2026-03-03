"""
User Brain — The core intelligence layer per Instagram account.

Each user's account gets its own "brain" that:
- Understands their brand voice by analyzing their description
- Maintains long-term memory about their niche
- Adapts content strategy based on performance
- Provides context for every AI generation call
"""

import logging
from collections import deque
from typing import Optional

from src.ai.gemini_brain import GeminiBrain
from src.ai.schemas import BrandVoiceProfile
from src.ai import prompts
from src.brain.memory_store import MemoryStore
from src.core.logging_config import get_logger

logger = get_logger("brain.user_brain")


class UserBrain:
    """
    Per-account intelligence layer.
    
    Usage:
        brain = UserBrain(gemini, account_id="123")
        profile = brain.understand_profile("I run an AI education account...")
        context = brain.get_relevant_context("GPT-5 release")
    """

    def __init__(
        self,
        gemini: Optional[GeminiBrain] = None,
        account_id: str = "default",
    ):
        self._gemini = gemini or GeminiBrain()
        self._account_id = account_id
        self._memory = MemoryStore(gemini=self._gemini, collection_name=f"brain_{account_id}")
        # Conversation history — ring buffer, max 50 interactions
        self._conversation_history: deque = deque(maxlen=50)

    def understand_profile(self, user_description: str) -> BrandVoiceProfile:
        """
        Analyze a user's account description and generate a brand voice profile.
        
        Args:
            user_description: Free-text description of the account, niche, goals
            
        Returns:
            BrandVoiceProfile with voice, pillars, audience, tone, etc.
        """
        prompt = prompts.UNDERSTAND_PROFILE.format(
            user_description=user_description,
        )

        result = self._gemini.analyze(prompt, schema=BrandVoiceProfile)

        if isinstance(result, BrandVoiceProfile):
            logger.info(f"Profile understood: {result.content_pillars}")
            # Store the understanding as knowledge
            self._memory.add_knowledge(
                topic="Brand Profile",
                content=f"Voice: {result.brand_voice}. Pillars: {', '.join(result.content_pillars)}. Audience: {result.target_audience}.",
                source="profile_analysis",
            )
            return result

        return BrandVoiceProfile(
            brand_voice="professional and engaging",
            content_pillars=["industry news", "tutorials", "insights"],
            target_audience="professionals and enthusiasts",
            tone_keywords=["informative", "helpful"],
            forbidden_words=[],
            emoji_style="moderate",
            example_caption="Check out this amazing insight!",
            posting_frequency=3,
            best_content_types=["IMAGE", "CAROUSEL"],
        )

    def get_relevant_context(self, topic: str, *, top_k: int = 5) -> str:
        """
        Retrieve relevant knowledge about a topic from memory.
        
        Args:
            topic: Topic to find context for
            top_k: Number of relevant entries to retrieve
            
        Returns:
            Combined relevant context as text
        """
        entries = self._memory.search(topic, top_k=top_k)
        if not entries:
            return "No prior knowledge about this topic."
        
        context_parts = []
        for entry in entries:
            context_parts.append(f"- {entry.get('topic', '')}: {entry.get('content', '')}")
        
        return "\n".join(context_parts)

    def learn(self, topic: str, content: str, *, source: str = "observation") -> None:
        """
        Add new knowledge to the brain's memory.
        
        Args:
            topic: Knowledge topic
            content: What was learned
            source: Where the knowledge came from
        """
        self._memory.add_knowledge(topic=topic, content=content, source=source)
        logger.info(f"Learned about: {topic}")

    def adapt_voice(self, sample_posts: list[str]) -> str:
        """
        Learn the user's writing style from sample posts.
        
        Args:
            sample_posts: List of example captions/posts
            
        Returns:
            Analysis of the writing style
        """
        samples = "\n---\n".join(sample_posts[:10])
        prompt = (
            f"Analyze the writing style of these Instagram posts:\n\n{samples}\n\n"
            f"Describe: tone, vocabulary, sentence structure, emoji usage, "
            f"hashtag patterns, CTA style, and overall personality."
        )

        analysis = self._gemini.analyze(prompt)
        self._memory.add_knowledge(
            topic="Writing Style",
            content=analysis,
            source="style_analysis",
        )
        return analysis

    def suggest_strategy(self, performance_summary: str, goals: str) -> str:
        """
        Suggest content strategy adjustments based on performance data.
        
        Args:
            performance_summary: Recent performance data
            goals: User's goals
            
        Returns:
            Strategy recommendations
        """
        context = self.get_relevant_context("content strategy performance")
        prompt = (
            f"Based on this performance data and goals, suggest strategy adjustments.\n\n"
            f"Performance:\n{performance_summary}\n\n"
            f"Goals: {goals}\n\n"
            f"Past context:\n{context}"
        )
        return self._gemini.analyze(prompt)

    def chat(self, message: str, *, system_instruction: str = "") -> str:
        """
        Send a message to the brain with conversation history for continuity.

        Args:
            message: User's message/question
            system_instruction: Optional system prompt override

        Returns:
            AI response (also stored in history)
        """
        # Build history context
        history_text = ""
        if self._conversation_history:
            recent = list(self._conversation_history)[-10:]  # Last 10 turns
            history_text = "\n".join(
                f"{turn['role']}: {turn['content'][:200]}" for turn in recent
            )
            history_text = f"\nConversation history:\n{history_text}\n\n"

        # Get relevant memory context
        memory_context = self.get_relevant_context(message, top_k=3)

        full_prompt = (
            f"{history_text}"
            f"Relevant knowledge:\n{memory_context}\n\n"
            f"User: {message}"
        )

        default_instruction = (
            f"You are the AI brain for Instagram account '{self._account_id}'. "
            f"Use conversation history and knowledge to provide personalized, "
            f"contextual responses."
        )

        response = self._gemini.generate_text(
            full_prompt,
            system_instruction=system_instruction or default_instruction,
        )

        # Store in history
        self._conversation_history.append({"role": "user", "content": message})
        self._conversation_history.append({"role": "assistant", "content": response})

        logger.info("Chat turn %d for account '%s'", len(self._conversation_history) // 2, self._account_id)
        return response

    def get_conversation_history(self, last_n: int = 20) -> list[dict]:
        """Get the most recent conversation turns."""
        return list(self._conversation_history)[-last_n:]

    def clear_conversation_history(self) -> None:
        """Clear conversation history (memory is preserved)."""
        self._conversation_history.clear()
        logger.info("Cleared conversation history for '%s'", self._account_id)
