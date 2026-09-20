"""
Advanced Logging System — Structured, per-component logging with error tracking.

Features:
- Per-component loggers (ai, database, instagram, scheduler, etc.)
- Colored console output with component labels
- Rotating file logs (error.log, app.log)
- JSON structured logging for production
- Error tracking with full context (component, operation, user)
- Performance timing decorators
- Error summary report

Usage:
    from src.core.logging_config import get_logger, log_error, timed

    logger = get_logger("ai.gemini_brain")
    logger.info("Generating content")

    @timed("content_generation")
    def generate():
        ...

    try:
        ...
    except Exception as e:
        log_error("ai.gemini_brain", "generate_text", e, context={"prompt": prompt[:100]})
"""

import json
import logging
import logging.handlers
import sys
import time
import traceback
import functools
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional

from src.config.settings import SETTINGS

# ========== Directory Setup ==========

LOG_DIR = Path("./logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

# ========== Color Codes (Windows-safe via colorama) ==========

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLORS = {
        "DEBUG": Fore.CYAN,
        "INFO": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "CRITICAL": Fore.RED + Style.BRIGHT,
    }
    COMPONENT_COLORS = {
        "ai": Fore.MAGENTA,
        "database": Fore.BLUE,
        "instagram": Fore.CYAN,
        "scheduler": Fore.YELLOW,
        "auth": Fore.GREEN,
        "research": Fore.LIGHTBLUE_EX,
        "content_gen": Fore.LIGHTMAGENTA_EX,
        "brain": Fore.LIGHTCYAN_EX,
        "analytics": Fore.LIGHTGREEN_EX,
        "api": Fore.LIGHTWHITE_EX,
        "core": Fore.WHITE,
    }
    RESET = Style.RESET_ALL
except ImportError:
    COLORS = {k: "" for k in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]}
    COMPONENT_COLORS = {}
    RESET = ""


# ========== Custom Formatter (Console — Colored + Component Label) ==========

class ColoredComponentFormatter(logging.Formatter):
    """
    Console formatter that shows:
    [TIME] [LEVEL] [COMPONENT] message
    
    With colors per level and per component.
    """

    def format(self, record: logging.LogRecord) -> str:
        # Extract component from logger name (e.g., "src.ai.gemini_brain" -> "ai")
        parts = record.name.split(".")
        component = "core"
        for p in parts:
            if p in COMPONENT_COLORS:
                component = p
                break

        level_color = COLORS.get(record.levelname, "")
        comp_color = COMPONENT_COLORS.get(component, "")

        timestamp = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")

        # Format exception info if present
        exc_text = ""
        if record.exc_info and record.exc_info[2]:
            exc_text = "\n" + "".join(traceback.format_exception(*record.exc_info))

        return (
            f"{RESET}[{timestamp}] "
            f"{level_color}{record.levelname:<8}{RESET} "
            f"{comp_color}[{component:<12}]{RESET} "
            f"{record.getMessage()}"
            f"{exc_text}"
        )


# ========== JSON Formatter (File — Structured) ==========

class JSONFormatter(logging.Formatter):
    """
    Structured JSON logging for file output and production.
    Each line is a valid JSON object for easy parsing/monitoring.
    """

    def format(self, record: logging.LogRecord) -> str:
        # Extract component
        parts = record.name.split(".")
        component = "core"
        for p in parts:
            if p in ("ai", "database", "instagram", "scheduler", "auth",
                      "research", "content_gen", "brain", "analytics", "api"):
                component = p
                break

        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "component": component,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info
        if record.exc_info and record.exc_info[2]:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else "Unknown",
                "message": str(record.exc_info[1]) if record.exc_info[1] else "",
                "traceback": traceback.format_exception(*record.exc_info),
            }

        # Add extra context fields
        for key in ("context", "operation", "user_id", "account_id", "duration_ms"):
            if hasattr(record, key):
                log_entry[key] = getattr(record, key)

        return json.dumps(log_entry, default=str, ensure_ascii=False)


# ========== Error Tracker (In-Memory Ring Buffer) ==========

class ErrorTracker:
    """
    Tracks recent errors in a ring buffer for quick diagnostics.
    
    Usage:
        tracker = ErrorTracker()
        tracker.record("ai.gemini_brain", "generate_text", error, context)
        print(tracker.summary())
    """

    def __init__(self, max_errors: int = 200):
        self._errors: list[dict] = []
        self._max_errors = max_errors
        self._error_counts: dict[str, int] = {}

    def record(
        self,
        component: str,
        operation: str,
        error: Exception,
        *,
        context: Optional[dict] = None,
    ) -> None:
        """Record an error occurrence."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "component": component,
            "operation": operation,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "context": context or {},
        }
        self._errors.append(entry)
        if len(self._errors) > self._max_errors:
            self._errors.pop(0)

        # Count by component
        key = f"{component}.{operation}"
        self._error_counts[key] = self._error_counts.get(key, 0) + 1

    def recent(self, n: int = 10) -> list[dict]:
        """Get the N most recent errors."""
        return self._errors[-n:]

    def count_by_component(self) -> dict[str, int]:
        """Get error counts grouped by component.operation."""
        return dict(sorted(self._error_counts.items(), key=lambda x: -x[1]))

    def summary(self) -> str:
        """Generate a human-readable error summary."""
        if not self._errors:
            return "No errors recorded."

        lines = [f"=== Error Summary ({len(self._errors)} total errors) ===\n"]

        # Top offenders
        lines.append("Error counts by component:")
        for key, count in sorted(self._error_counts.items(), key=lambda x: -x[1])[:10]:
            lines.append(f"  {key}: {count}")

        # Last 5 errors
        lines.append(f"\nLast 5 errors:")
        for err in self._errors[-5:]:
            lines.append(
                f"  [{err['timestamp'][:19]}] {err['component']}.{err['operation']}: "
                f"{err['error_type']}: {err['error_message'][:100]}"
            )

        return "\n".join(lines)

    def clear(self) -> None:
        """Clear all tracked errors."""
        self._errors.clear()
        self._error_counts.clear()


# ========== Global Error Tracker ==========

_error_tracker = ErrorTracker()


# ========== Setup Function ==========

def setup_logging(
    *,
    console_level: str = "INFO",
    file_level: str = "DEBUG",
    error_file_level: str = "ERROR",
    log_dir: str = "./logs",
) -> None:
    """
    Configure the global logging system.
    
    Creates:
    - Console handler (colored, component-labeled)
    - app.log (rotating, JSON structured, all levels)
    - error.log (rotating, JSON structured, ERROR+ only)
    
    Call this ONCE at application startup.
    """
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    # Clear existing handlers
    root.handlers.clear()

    # 1. Console Handler — colored with component labels
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(getattr(logging, console_level.upper(), logging.INFO))
    console.setFormatter(ColoredComponentFormatter())
    root.addHandler(console)

    # 2. App Log — rotating JSON, all levels
    app_handler = logging.handlers.RotatingFileHandler(
        str(log_path / "app.log"),
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding="utf-8",
    )
    app_handler.setLevel(getattr(logging, file_level.upper(), logging.DEBUG))
    app_handler.setFormatter(JSONFormatter())
    root.addHandler(app_handler)

    # 3. Error Log — rotating JSON, ERROR+ only
    error_handler = logging.handlers.RotatingFileHandler(
        str(log_path / "error.log"),
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3,
        encoding="utf-8",
    )
    error_handler.setLevel(getattr(logging, error_file_level.upper(), logging.ERROR))
    error_handler.setFormatter(JSONFormatter())
    root.addHandler(error_handler)

    # Suppress noisy third-party loggers
    for name in ("httpx", "httpcore", "chromadb", "urllib3", "opentelemetry", "hpack"):
        logging.getLogger(name).setLevel(logging.WARNING)

    logging.info("Logging system initialized: console=%s, file=%s, errors=%s",
                 console_level, file_level, error_file_level)


# ========== Helper Functions ==========

def get_logger(name: str) -> logging.Logger:
    """
    Get a named logger for a component.
    
    Usage:
        logger = get_logger("ai.gemini_brain")
        logger.info("Generating content", extra={"context": {"model": "flash"}})
    """
    return logging.getLogger(f"src.{name}")


def log_error(
    component: str,
    operation: str,
    error: Exception,
    *,
    context: Optional[dict] = None,
    logger: Optional[logging.Logger] = None,
) -> None:
    """
    Log an error with full context and track it in the error tracker.
    
    Args:
        component: Which component failed (e.g., "ai.gemini_brain")
        operation: Which operation failed (e.g., "generate_text")
        error: The exception
        context: Optional dict of contextual data (prompt, user_id, etc.)
        logger: Optional specific logger; defaults to component logger
    """
    _error_tracker.record(component, operation, error, context=context)

    log = logger or get_logger(component)
    log.error(
        f"[{operation}] {type(error).__name__}: {error}",
        exc_info=True,
        extra={
            "operation": operation,
            "context": context or {},
        },
    )


def get_error_tracker() -> ErrorTracker:
    """Get the global error tracker for diagnostics."""
    return _error_tracker


# ========== Decorators ==========

def timed(operation_name: str = ""):
    """
    Decorator that logs execution time for a function.
    
    Usage:
        @timed("content_generation")
        def generate_post(topic):
            ...
    
    Logs:
        [INFO] [content_gen] content_generation completed in 1234ms
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            op = operation_name or func.__qualname__
            logger = logging.getLogger(func.__module__)
            start = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.perf_counter() - start) * 1000
                logger.info(
                    f"{op} completed in {duration_ms:.0f}ms",
                    extra={"duration_ms": duration_ms, "operation": op},
                )
                return result
            except Exception as e:
                duration_ms = (time.perf_counter() - start) * 1000
                log_error(
                    func.__module__,
                    op,
                    e,
                    context={"duration_ms": duration_ms},
                    logger=logger,
                )
                raise
        return wrapper
    return decorator


def timed_async(operation_name: str = ""):
    """
    Async version of timed decorator.
    
    Usage:
        @timed_async("publish_post")
        async def publish(container_id):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            op = operation_name or func.__qualname__
            logger = logging.getLogger(func.__module__)
            start = time.perf_counter()
            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.perf_counter() - start) * 1000
                logger.info(
                    f"{op} completed in {duration_ms:.0f}ms",
                    extra={"duration_ms": duration_ms, "operation": op},
                )
                return result
            except Exception as e:
                duration_ms = (time.perf_counter() - start) * 1000
                log_error(
                    func.__module__,
                    op,
                    e,
                    context={"duration_ms": duration_ms},
                    logger=logger,
                )
                raise
        return wrapper
    return decorator


def safe_execute(
    component: str,
    operation: str,
    *,
    default: Any = None,
    reraise: bool = False,
):
    """
    Decorator that catches and logs all exceptions.
    
    Usage:
        @safe_execute("ai.gemini_brain", "generate_text", default="", reraise=False)
        def generate_text(prompt):
            ...  # If this fails, returns "" instead of crashing
    
    Args:
        component: Component name for error tracking
        operation: Operation name
        default: Return value if an exception occurs
        reraise: If True, logs and re-raises; if False, returns default
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                log_error(component, operation, e)
                if reraise:
                    raise
                return default
        return wrapper
    return decorator
