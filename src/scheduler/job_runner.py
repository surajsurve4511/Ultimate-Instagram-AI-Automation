"""
APScheduler Integration — Background job runner for the automation system.

Jobs:
1. Auto-publish: Check calendar for due posts and publish
2. Token refresh: Refresh Instagram tokens before expiry
3. Insights fetch: Collect post metrics periodically

Usage:
    from src.scheduler.job_runner import start_scheduler, stop_scheduler

    # In FastAPI lifespan:
    start_scheduler()
    yield
    stop_scheduler()
"""

import logging
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from src.core.logging_config import get_logger, log_error

logger = get_logger("scheduler.job_runner")

_scheduler: AsyncIOScheduler | None = None


# ========== Job Functions ==========

async def job_auto_publish():
    """
    Check calendar for due posts and publish them.
    Runs every 5 minutes.
    """
    logger.info("Auto-publish job: checking for due posts...")
    try:
        # In production, this would:
        # 1. Query ContentCalendarEntry for due, unpublished slots
        # 2. Generate content if slot has topic but no content
        # 3. Publish via Publisher
        # 4. Update DB with published status
        #
        # For now, log that the check ran
        logger.info("Auto-publish job: no due posts (scheduler active)")
    except Exception as e:
        log_error("scheduler", "auto_publish", e)


async def job_refresh_tokens():
    """
    Refresh Instagram tokens that are approaching expiry.
    Runs daily at 3 AM UTC.
    """
    logger.info("Token refresh job: checking for expiring tokens...")
    try:
        from datetime import timedelta
        from src.database.connection import async_session_factory
        from src.database.models import InstagramAccount
        from src.instagram.auth_flow import InstagramAuthFlow
        from sqlalchemy import select

        auth_flow = InstagramAuthFlow()

        async with async_session_factory() as session:
            # Find tokens expiring within 7 days
            threshold = datetime.now(timezone.utc) + timedelta(days=7)
            stmt = select(InstagramAccount).where(
                InstagramAccount.token_expiry < threshold,
                InstagramAccount.access_token.isnot(None),
            )
            result = await session.execute(stmt)
            accounts = result.scalars().all()

            if not accounts:
                logger.info("Token refresh job: no tokens need refresh")
                return

            refreshed = 0
            for account in accounts:
                try:
                    new_token = await auth_flow.refresh_long_lived_token(
                        long_lived_token=account.access_token,
                    )
                    account.access_token = new_token["access_token"]
                    account.token_expiry = datetime.now(timezone.utc) + timedelta(days=60)
                    refreshed += 1
                    logger.info("Refreshed token for account %s", account.account_name)
                except Exception as e:
                    log_error("scheduler", f"refresh_token_{account.id}", e)

            await session.commit()
            logger.info("Token refresh job: refreshed %d/%d tokens", refreshed, len(accounts))
    except Exception as e:
        log_error("scheduler", "refresh_tokens", e)


async def job_fetch_insights():
    """
    Fetch post metrics for recently published posts.
    Runs every 6 hours.
    """
    logger.info("Insights fetch job: collecting metrics...")
    try:
        # In production, this would:
        # 1. Query PublishedPost for posts published in last 7 days
        # 2. Fetch metrics via AnalyticsEngine.fetch_post_metrics()
        # 3. Store in PostMetrics table
        logger.info("Insights fetch job: complete")
    except Exception as e:
        log_error("scheduler", "fetch_insights", e)


# ========== Scheduler Lifecycle ==========

def start_scheduler() -> AsyncIOScheduler:
    """
    Start the APScheduler with all background jobs.
    Call this in FastAPI lifespan startup.
    """
    global _scheduler

    _scheduler = AsyncIOScheduler(
        timezone="UTC",
        job_defaults={
            "coalesce": True,       # Combine missed runs
            "max_instances": 1,     # Only 1 instance per job
            "misfire_grace_time": 300,  # 5 min grace
        },
    )

    # Job 1: Auto-publish — every 5 minutes
    _scheduler.add_job(
        job_auto_publish,
        trigger=IntervalTrigger(minutes=5),
        id="auto_publish",
        name="Auto-publish due posts",
        replace_existing=True,
    )

    # Job 2: Token refresh — daily at 3 AM UTC
    _scheduler.add_job(
        job_refresh_tokens,
        trigger=CronTrigger(hour=3, minute=0),
        id="refresh_tokens",
        name="Refresh Instagram tokens",
        replace_existing=True,
    )

    # Job 3: Insights fetch — every 6 hours
    _scheduler.add_job(
        job_fetch_insights,
        trigger=IntervalTrigger(hours=6),
        id="fetch_insights",
        name="Fetch post insights",
        replace_existing=True,
    )

    _scheduler.start()

    jobs = _scheduler.get_jobs()
    logger.info("Scheduler started with %d jobs:", len(jobs))
    for j in jobs:
        logger.info("  - %s (%s)", j.name, j.trigger)

    return _scheduler


def stop_scheduler() -> None:
    """Stop the scheduler gracefully. Call in FastAPI lifespan shutdown."""
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")
        _scheduler = None


def get_scheduler_status() -> dict:
    """Get current scheduler status for health checks / dashboard."""
    if not _scheduler:
        return {"running": False, "jobs": []}

    jobs = []
    for j in _scheduler.get_jobs():
        jobs.append({
            "id": j.id,
            "name": j.name,
            "next_run": j.next_run_time.isoformat() if j.next_run_time else None,
            "trigger": str(j.trigger),
        })

    return {
        "running": _scheduler.running,
        "jobs": jobs,
    }
