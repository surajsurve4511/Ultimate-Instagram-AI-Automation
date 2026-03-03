"""
Analytics and quality check API routes.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.ai.gemini_brain import GeminiBrain
from src.analytics.analytics_engine import AnalyticsEngine
from src.analytics.marketing_engine import MarketingEngine

router = APIRouter()
_brain = None
_analytics = None
_marketing = None


def _get_engines():
    global _brain, _analytics, _marketing
    if _brain is None:
        _brain = GeminiBrain()
        _analytics = AnalyticsEngine(_brain)
        _marketing = MarketingEngine(_brain)
    return _analytics, _marketing


class QualityCheckRequest(BaseModel):
    caption: str
    hashtags: list[str] = []
    content_type: str = "IMAGE"
    target_audience: str = ""
    brand_voice: str = ""


class PsychologyRequest(BaseModel):
    content: str
    niche: str = "technology"
    target_audience: str = "professionals"
    funnel_stage: str = "TOFU"


class HookRequest(BaseModel):
    topic: str
    niche: str = "technology"
    hook_type: str = "curiosity"


@router.post("/quality-check")
async def quality_check(request: QualityCheckRequest):
    """Run AI quality check on content before publishing."""
    try:
        analytics, _ = _get_engines()
        result = analytics.quality_check(
            request.caption,
            request.hashtags,
            content_type=request.content_type,
            target_audience=request.target_audience,
            brand_voice=request.brand_voice,
        )
        return {"quality_assessment": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/enhance")
async def apply_psychology(request: PsychologyRequest):
    """Enhance content with marketing psychology."""
    try:
        _, marketing = _get_engines()
        result = marketing.apply_psychology(
            request.content,
            niche=request.niche,
            target_audience=request.target_audience,
            funnel_stage=request.funnel_stage,
        )
        return {"enhanced_content": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-hook")
async def generate_hook(request: HookRequest):
    """Generate a scroll-stopping hook for a post."""
    try:
        _, marketing = _get_engines()
        hook = marketing.generate_hook(
            request.topic,
            niche=request.niche,
            hook_type=request.hook_type,
        )
        return {"hook": hook}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
