"""
FastAPI Application — The dashboard backend for the Instagram AI Automation System.

Provides RESTful API endpoints for:
- User authentication (register, login)
- Instagram account management
- User profile & brain management
- Content generation and management
- Content calendar & scheduling
- Publishing
- Analytics & quality checks
- System diagnostics & error tracking

Run with: uvicorn src.api.main:app --reload
Docs: http://localhost:8000/docs (OpenAPI/Swagger)
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from src.config.settings import SETTINGS
from src.core.logging_config import setup_logging, get_logger, get_error_tracker
from src.database.connection import init_db

# Initialize logging FIRST, before anything else
setup_logging(
    console_level=SETTINGS.LOG_LEVEL,
    file_level="DEBUG",
    error_file_level="ERROR",
)

logger = get_logger("api.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("=" * 60)
    logger.info("Instagram AI Automation System v2.0.0 starting...")
    logger.info("=" * 60)

    SETTINGS.create_directories()
    logger.info("Directories created")

    await init_db()
    logger.info("Database initialized")

    # Verify Gemini AI
    try:
        from src.ai.gemini_brain import GeminiBrain
        brain = GeminiBrain()
        status = brain.health_check()
        if status.get("all_ok"):
            logger.info("Gemini AI: ALL MODELS OK")
        else:
            logger.warning("Gemini AI: DEGRADED - %s", status)
    except Exception as e:
        logger.error("Gemini AI: FAILED TO INITIALIZE - %s", e)

    # Start background scheduler
    from src.scheduler.job_runner import start_scheduler, stop_scheduler
    start_scheduler()
    logger.info("Background scheduler started")

    logger.info("System ready. Swagger docs at http://%s:%s/docs", SETTINGS.APP_HOST, SETTINGS.APP_PORT)
    yield

    # Shutdown
    stop_scheduler()
    logger.info("Shutting down...")


app = FastAPI(
    title="Instagram AI Automation",
    description=(
        "Multi-user Instagram content automation powered by Gemini AI. "
        "Generate, schedule, and publish Instagram content using AI."
    ),
    version="2.0.0",
    lifespan=lifespan,
)


# ========== Global Error Handler ==========

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch all unhandled exceptions, log them, and return a clean error response."""
    from src.core.logging_config import log_error
    log_error("api", f"{request.method} {request.url.path}", exc, context={
        "method": request.method,
        "url": str(request.url),
        "client": request.client.host if request.client else "unknown",
    })
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "path": request.url.path,
        },
    )


# ========== Middleware ==========

# CORS — allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve media files (for Instagram to fetch published images)
app.mount("/media", StaticFiles(directory=SETTINGS.IMAGES_STORAGE_PATH), name="media")

# Serve frontend static files (CSS, JS)
import os
_frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend")
if os.path.isdir(_frontend_dir):
    app.mount("/frontend", StaticFiles(directory=_frontend_dir), name="frontend")


# ========== Register All Routes ==========

from src.api.routes import auth, content, instagram, analytics, profile, calendar, accounts, campaigns

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(accounts.router, prefix="/api/accounts", tags=["Accounts"])
app.include_router(profile.router, prefix="/api/profile", tags=["Profile & Brain"])
app.include_router(content.router, prefix="/api/content", tags=["Content"])
app.include_router(calendar.router, prefix="/api/calendar", tags=["Calendar"])
app.include_router(campaigns.router, prefix="/api/campaigns", tags=["Campaigns"])
app.include_router(instagram.router, prefix="/api/instagram", tags=["Instagram"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])


# ========== System Endpoints ==========

@app.get("/", tags=["System"])
async def root():
    """Serve the dashboard frontend."""
    import os
    index_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    return {"status": "ok", "app": "Instagram AI Automation", "version": "2.0.0"}


@app.get("/health", tags=["System"])
async def health_check():
    """Detailed health check with AI and database status."""
    from src.ai.gemini_brain import GeminiBrain

    try:
        brain = GeminiBrain()
        ai_status = brain.health_check()
    except Exception as e:
        ai_status = {"all_ok": False, "error": str(e)}

    tracker = get_error_tracker()
    from src.scheduler.job_runner import get_scheduler_status
    return {
        "status": "healthy" if ai_status.get("all_ok") else "degraded",
        "ai": ai_status,
        "database": "connected",
        "scheduler": get_scheduler_status(),
        "errors": {
            "total": len(tracker._errors),
            "by_component": tracker.count_by_component(),
        },
    }


@app.get("/debug/errors", tags=["System"])
async def get_errors(n: int = 20):
    """Get recent errors for debugging. Shows last N errors with full context."""
    tracker = get_error_tracker()
    return {
        "summary": tracker.summary(),
        "recent_errors": tracker.recent(n),
        "counts": tracker.count_by_component(),
    }


@app.post("/debug/errors/clear", tags=["System"])
async def clear_errors():
    """Clear the error tracker."""
    tracker = get_error_tracker()
    tracker.clear()
    return {"message": "Error tracker cleared"}
