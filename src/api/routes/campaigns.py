"""
Campaigns API routes — Create and manage multi-day content campaigns.
"""

from fastapi import APIRouter
from pydantic import BaseModel

from src.marketing.campaign_engine import CampaignEngine
from src.marketing.funnel_mapper import FunnelMapper
from src.core.logging_config import get_logger

logger = get_logger("api.routes.campaigns")

router = APIRouter()


# ========== Request Models ==========

class CreateCampaignRequest(BaseModel):
    name: str
    theme: str
    goal: str
    duration_days: int = 7
    posts_per_day: int = 1
    niche: str = "technology"
    target_audience: str = "general"
    brand_voice: str = "professional"


class ClassifyTopicRequest(BaseModel):
    topic: str
    niche: str = "technology"


class DistributionRequest(BaseModel):
    stages: list[str]


# ========== Routes ==========

@router.post("/create")
async def create_campaign(request: CreateCampaignRequest):
    """Create a campaign and generate its content plan."""
    engine = CampaignEngine()
    campaign = engine.create_campaign(
        name=request.name,
        theme=request.theme,
        goal=request.goal,
        duration_days=request.duration_days,
        posts_per_day=request.posts_per_day,
        niche=request.niche,
        target_audience=request.target_audience,
        brand_voice=request.brand_voice,
    )
    plan = engine.generate_campaign_plan(campaign)
    return {
        "campaign": {
            "name": campaign.name,
            "theme": campaign.theme,
            "goal": campaign.goal,
            "duration_days": campaign.duration_days,
            "status": campaign.status,
        },
        "plan": plan,
        "total_posts": len(plan),
    }


@router.post("/classify-topic")
async def classify_funnel_stage(request: ClassifyTopicRequest):
    """Classify a content topic into a funnel stage (TOFU/MOFU/BOFU/RETENTION)."""
    mapper = FunnelMapper()
    stage = mapper.classify_topic(request.topic, niche=request.niche)
    return {"topic": request.topic, "funnel_stage": stage}


@router.post("/analyze-distribution")
async def analyze_distribution(request: DistributionRequest):
    """Analyze funnel distribution of existing content."""
    mapper = FunnelMapper()
    analysis = mapper.analyze_distribution(request.stages)
    return analysis


@router.get("/plan-week")
async def plan_week(posts_per_day: int = 2, days: int = 7):
    """Generate an optimal funnel distribution plan for a week."""
    mapper = FunnelMapper()
    plan = mapper.plan_week_distribution(posts_per_day=posts_per_day, days=days)
    return {"plan": plan, "total_posts": len(plan)}
