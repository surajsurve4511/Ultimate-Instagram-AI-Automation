"""
Content Calendar API routes — View, generate, and manage the content calendar.
"""

from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.scheduler.content_calendar import ContentCalendar
from src.core.logging_config import get_logger, log_error

logger = get_logger("api.routes.calendar")

router = APIRouter()
_calendar = ContentCalendar()


# ========== Request / Response Models ==========

class GenerateScheduleRequest(BaseModel):
    posts_per_day: int = 3
    posting_times: list[str] | None = None
    posting_days: list[int] | None = None
    funnel_distribution: dict | None = None


# ========== Routes ==========

@router.post("/generate-week")
async def generate_weekly_calendar(request: GenerateScheduleRequest):
    """Generate a week's content calendar with optimal slots."""
    try:
        schedule = _calendar.generate_week_schedule(
            posts_per_day=request.posts_per_day,
            posting_times=request.posting_times,
            posting_days=request.posting_days,
            funnel_distribution=request.funnel_distribution,
        )
        logger.info("Generated %d calendar slots", len(schedule))
        return {
            "total_slots": len(schedule),
            "schedule": schedule,
        }
    except Exception as e:
        log_error("api.calendar", "generate_weekly_calendar", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/default-times")
async def get_default_times():
    """Get the default posting configuration."""
    from src.config.settings import SETTINGS
    return {
        "posting_times": SETTINGS.DEFAULT_POSTING_TIMES,
        "posting_days": SETTINGS.DEFAULT_POSTING_DAYS,
        "posts_per_day": SETTINGS.DEFAULT_POSTS_PER_DAY,
        "funnel_distribution": SETTINGS.DEFAULT_FUNNEL_DISTRIBUTION,
    }
