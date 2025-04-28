"""
Application startup and shutdown events
"""
import logging
from fastapi import FastAPI
from app.core.cache import get_redis

logger = logging.getLogger(__name__)

async def startup_handler(app: FastAPI) -> None:
    """
    Execute actions on application startup
    """
    # Initialize Redis connection on startup
    try:
        redis = await get_redis()
        await redis.ping()
        logger.info("Successfully connected to Redis")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        # Don't raise exception here - app should be able to start without Redis
        # (will just run without caching)

async def shutdown_handler(app: FastAPI) -> None:
    """
    Execute actions on application shutdown
    """
    # Close Redis connection on shutdown
    try:
        redis = await get_redis()
        await redis.close()
        logger.info("Redis connection closed")
    except Exception as e:
        logger.error(f"Error closing Redis connection: {e}")