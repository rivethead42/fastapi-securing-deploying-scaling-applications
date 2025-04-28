import json
from typing import Any, Optional
from redis.asyncio import Redis
from app.core.config import settings
import pickle

# Initialize Redis connection
redis: Optional[Redis] = None

async def get_redis() -> Redis:
    """
    Get or create a Redis connection
    """
    global redis
    if redis is None:
        redis = Redis.from_url(
            settings.REDIS_URI,
            encoding="utf-8",
            decode_responses=False  # Set to False to support binary data
        )
    return redis

async def get_cache(key: str) -> Optional[Any]:
    """
    Get value from cache
    """
    redis_client = await get_redis()
    value = await redis_client.get(key)
    
    if value is None:
        return None
    
    try:
        # Try to unpickle for complex objects
        return pickle.loads(value)
    except (pickle.PickleError, TypeError):
        try:
            # Try JSON for simpler objects
            return json.loads(value)
        except json.JSONDecodeError:
            # Return raw value if neither works
            return value

async def set_cache(key: str, value: Any, expiration: int = None) -> bool:
    """
    Set value in cache with optional expiration in seconds
    """
    redis_client = await get_redis()
    
    try:
        # Try JSON serialization first for better interoperability
        serialized_value = json.dumps(value)
    except (TypeError, json.JSONDecodeError):
        try:
            # Fall back to pickle for complex objects
            serialized_value = pickle.dumps(value)
        except pickle.PickleError:
            # If all serialization fails, return False
            return False
    
    if expiration:
        return await redis_client.setex(key, expiration, serialized_value)
    else:
        return await redis_client.set(key, serialized_value)

async def delete_cache(key: str) -> int:
    """
    Delete a key from cache
    """
    redis_client = await get_redis()
    return await redis_client.delete(key)

async def flush_cache() -> bool:
    """
    Flush the entire cache (use with caution)
    """
    redis_client = await get_redis()
    return await redis_client.flushdb()

async def get_cache_keys(pattern: str = "*") -> list:
    """
    Get all keys matching pattern
    """
    redis_client = await get_redis()
    return await redis_client.keys(pattern)