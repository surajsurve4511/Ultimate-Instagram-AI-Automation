"""
Profile & Brain API routes — Manage brand voice, goals, and user brain.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.ai.gemini_brain import GeminiBrain
from src.brain.user_brain import UserBrain
from src.core.logging_config import get_logger, log_error, timed

logger = get_logger("api.routes.profile")

router = APIRouter()
_brains: dict[str, UserBrain] = {}


def _get_brain(account_id: str = "default") -> UserBrain:
    if account_id not in _brains:
        _brains[account_id] = UserBrain(account_id=account_id)
    return _brains[account_id]


# ========== Request / Response Models ==========

class ProfileSetupRequest(BaseModel):
    account_id: str = "default"
    description: str  # Free-text account description


class LearnRequest(BaseModel):
    account_id: str = "default"
    topic: str
    content: str
    source: str = "user_input"


class AdaptVoiceRequest(BaseModel):
    account_id: str = "default"
    sample_posts: list[str]


class ContextRequest(BaseModel):
    account_id: str = "default"
    topic: str
    top_k: int = 5


class StrategyRequest(BaseModel):
    account_id: str = "default"
    performance_summary: str
    goals: str


# ========== Routes ==========

@router.post("/setup")
async def setup_profile(request: ProfileSetupRequest):
    """Analyze account description and create a brand voice profile."""
    try:
        brain = _get_brain(request.account_id)
        profile = brain.understand_profile(request.description)
        logger.info("Profile setup complete for account=%s", request.account_id)
        return {
            "brand_voice": profile.brand_voice,
            "content_pillars": profile.content_pillars,
            "target_audience": profile.target_audience,
            "tone_keywords": profile.tone_keywords,
            "emoji_style": profile.emoji_style,
            "posting_frequency": profile.posting_frequency,
            "best_content_types": profile.best_content_types,
        }
    except Exception as e:
        log_error("api.profile", "setup_profile", e, context={"account_id": request.account_id})
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/learn")
async def learn_knowledge(request: LearnRequest):
    """Add knowledge to the account's brain memory."""
    try:
        brain = _get_brain(request.account_id)
        brain.learn(request.topic, request.content, source=request.source)
        return {"message": f"Learned about: {request.topic}"}
    except Exception as e:
        log_error("api.profile", "learn_knowledge", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/adapt-voice")
async def adapt_voice(request: AdaptVoiceRequest):
    """Learn writing style from sample posts."""
    try:
        brain = _get_brain(request.account_id)
        analysis = brain.adapt_voice(request.sample_posts)
        return {"voice_analysis": analysis}
    except Exception as e:
        log_error("api.profile", "adapt_voice", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/context")
async def get_context(request: ContextRequest):
    """Retrieve relevant context from brain memory for a topic."""
    try:
        brain = _get_brain(request.account_id)
        context = brain.get_relevant_context(request.topic, top_k=request.top_k)
        return {"topic": request.topic, "context": context}
    except Exception as e:
        log_error("api.profile", "get_context", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/suggest-strategy")
async def suggest_strategy(request: StrategyRequest):
    """Get AI strategy recommendations based on performance and goals."""
    try:
        brain = _get_brain(request.account_id)
        strategy = brain.suggest_strategy(request.performance_summary, request.goals)
        return {"strategy": strategy}
    except Exception as e:
        log_error("api.profile", "suggest_strategy", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/memory-count/{account_id}")
async def memory_count(account_id: str = "default"):
    """Get the number of knowledge entries in the brain."""
    brain = _get_brain(account_id)
    return {"account_id": account_id, "memory_entries": brain._memory.count()}
