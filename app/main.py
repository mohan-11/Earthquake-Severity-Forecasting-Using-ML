import asyncio
import logging
from contextlib import asynccontextmanager
import os
import threading
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.connection import init_db
from app.database.session import AsyncSessionLocal
from app.routers.earthquake_router import router as earthquake_router
from app.routers.predict_router import router as predict_router
from app.services.earthquake_service import process_and_store_earthquakes

# Configure application logging (visible in terminal).
# `force=True` ensures this format is applied even if something configured logging earlier.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    force=True,
)
logger = logging.getLogger(__name__)

_bg_thread_lock = threading.Lock()
_bg_thread: threading.Thread | None = None


def _get_fetch_interval_seconds() -> int:
    """Read fetch interval from env, defaulting to 60 seconds."""
    raw_value = os.getenv("FETCH_INTERVAL_SECONDS", "60")
    try:
        interval = int(raw_value)
        if interval <= 0:
            raise ValueError("Interval must be positive")
        return interval
    except (TypeError, ValueError):
        logger.warning(
            "Invalid FETCH_INTERVAL_SECONDS=%r; using default 60 seconds.",
            raw_value,
        )
        return 60


async def _fetch_once() -> int:
    """Fetch from USGS and store into DB once (async-safe)."""
    async with AsyncSessionLocal() as db:
        records = await process_and_store_earthquakes(db)
        # Note: the service deduplicates at the DB level, so `len(records)` is
        # "attempted to store" not "inserted". It's still useful for visibility.
        return len(records)


def background_fetch() -> None:
    """
    Background thread that periodically fetches and stores earthquakes.

    - Runs `process_and_store_earthquakes()` on an async event loop inside this thread.
    - Uses `time.sleep()` so it doesn't block the FastAPI main server.
    """
    interval_seconds = _get_fetch_interval_seconds()
    logger.info(
        "Background fetch thread starting (interval=%ss). Set FETCH_INTERVAL_SECONDS=5 for testing.",
        interval_seconds,
    )

    # Each thread needs its own event loop for async calls.
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        while True:
            try:
                logger.info("Background fetch: fetching USGS data...")
                attempted = loop.run_until_complete(_fetch_once())
                logger.info("Background fetch: update complete (attempted=%d).", attempted)
            except Exception as e:
                logger.exception("Error in background task.")

            time.sleep(interval_seconds)
    finally:
        logger.info("Background fetch thread stopping; closing event loop.")
        loop.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure SQLite tables exist when FastAPI starts.
    await init_db()
    interval_seconds = _get_fetch_interval_seconds()
    logger.info("Background fetch interval is set to %s seconds.", interval_seconds)
    global _bg_thread
    logger.info("🚀 Starting background thread...")
    with _bg_thread_lock:
        if _bg_thread is None or not _bg_thread.is_alive():
            _bg_thread = threading.Thread(target=background_fetch, daemon=True)
            _bg_thread.start()
            logger.info("✅ Background thread started")
        else:
            logger.info("Background thread already running; skipping start.")
    yield


def create_app() -> FastAPI:
    # Production optimizations
    app = FastAPI(
        lifespan=lifespan, 
        title="Earthquake Prediction API",
        description="Production-ready earthquake prediction and monitoring API",
        version="1.0.0",
        docs_url="/docs" if os.getenv("DEBUG", "false").lower() == "true" else None
    )

    # Enhanced CORS configuration for production
    cors_origins_env = os.getenv("CORS_ORIGINS", "*")
    origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()] if cors_origins_env else ["*"]
    
    # Security headers middleware
    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
        expose_headers=["*"]
    )

    # Include routers
    app.include_router(earthquake_router)
    app.include_router(predict_router)

    # Production health check
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "environment": os.getenv("DEBUG", "false")
        }

    return app


app = create_app()
