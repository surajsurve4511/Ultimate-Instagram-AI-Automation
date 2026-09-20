"""
Content generation API routes.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.ai.gemini_brain import GeminiBrain
from src.content_gen.content_factory import ContentFactory

router = APIRouter()
_brain = None
_factory = None


def _get_factory() -> ContentFactory:
    global _brain, _factory
    if _factory is None:
        _brain = GeminiBrain()
        _factory = ContentFactory(_brain)
    return _factory


class PostRequest(BaseModel):
    topic: str
    niche: str = "technology"
    brand_voice: str = "professional and engaging"
    target_audience: str = "tech enthusiasts"
    funnel_stage: str = "TOFU"
    content_type: str = "IMAGE"
    generate_images: bool = False  # Default false for API (can be slow)


class TopicSuggestionRequest(BaseModel):
    niche: str
    target_audience: str
    content_pillars: list[str]
    count: int = 7


@router.post("/generate")
async def generate_post(request: PostRequest):
    """Generate a new Instagram post."""
    try:
        factory = _get_factory()
        result = factory.create_post(
            request.topic,
            niche=request.niche,
            brand_voice=request.brand_voice,
            target_audience=request.target_audience,
            funnel_stage=request.funnel_stage,
            content_type=request.content_type,
            generate_images=request.generate_images,
        )
        # Serialize the plan
        plan = result["plan"]
        return {
            "caption": plan.caption,
            "hashtags": plan.hashtags,
            "call_to_action": plan.call_to_action,
            "alt_text": plan.alt_text,
            "content_type": result["content_type"],
            "funnel_stage": result["funnel_stage"],
            "image_paths": result.get("image_paths", []),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/suggest-topics")
async def suggest_topics(request: TopicSuggestionRequest):
    """Suggest content topics for the week."""
    try:
        factory = _get_factory()
        topics = factory.suggest_topics(
            request.niche,
            request.target_audience,
            request.content_pillars,
            count=request.count,
        )
        return {"topics": topics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
