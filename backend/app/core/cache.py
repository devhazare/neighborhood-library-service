"""Caching utilities using Redis."""

import json
import hashlib
from functools import wraps
from typing import Optional, Any, Callable
import os

try:
    from redis import Redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class CacheClient:
    """Redis cache client with fallback to no-op if Redis is unavailable."""

    def __init__(self):
        """Initialize Redis client if available."""
        self.enabled = False
        self.client = None

        if REDIS_AVAILABLE:
            redis_host = os.getenv("REDIS_HOST", "localhost")
            redis_port = int(os.getenv("REDIS_PORT", "6379"))

            try:
                self.client = Redis(
                    host=redis_host,
                    port=redis_port,
                    decode_responses=True,
                    socket_connect_timeout=1,
                    socket_timeout=1
                )
                # Test connection
                self.client.ping()
                self.enabled = True
            except Exception as e:
                print(f"Redis unavailable, caching disabled: {e}")
                self.enabled = False

    def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        if not self.enabled:
            return None
        try:
            return self.client.get(key)
        except Exception:
            return None

    def set(self, key: str, value: str, ttl: int = 300) -> bool:
        """Set value in cache with TTL."""
        if not self.enabled:
            return False
        try:
            return self.client.setex(key, ttl, value)
        except Exception:
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self.enabled:
            return False
        try:
            return self.client.delete(key) > 0
        except Exception:
            return False

    def clear_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        if not self.enabled:
            return 0
        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception:
            return 0


# Global cache instance
cache_client = CacheClient()


def cache_key(*args, **kwargs) -> str:
    """Generate cache key from function arguments."""
    key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
    return hashlib.md5(key_data.encode()).hexdigest()


def cached(ttl: int = 300, key_prefix: str = ""):
    """
    Decorator to cache function results.

    Args:
        ttl: Time to live in seconds (default: 300 = 5 minutes)
        key_prefix: Prefix for cache key

    Usage:
        @cached(ttl=600, key_prefix="books")
        async def get_book(book_id: str):
            return await fetch_book(book_id)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            func_name = f"{func.__module__}.{func.__qualname__}"
            key = f"{key_prefix}:{func_name}:{cache_key(*args, **kwargs)}"

            # Try to get from cache
            cached_value = cache_client.get(key)
            if cached_value:
                try:
                    return json.loads(cached_value)
                except json.JSONDecodeError:
                    pass

            # Execute function
            result = await func(*args, **kwargs)

            # Store in cache
            try:
                cache_client.set(key, json.dumps(result), ttl)
            except (TypeError, json.JSONEncodeError):
                # Result not JSON serializable, skip caching
                pass

            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Generate cache key
            func_name = f"{func.__module__}.{func.__qualname__}"
            key = f"{key_prefix}:{func_name}:{cache_key(*args, **kwargs)}"

            # Try to get from cache
            cached_value = cache_client.get(key)
            if cached_value:
                try:
                    return json.loads(cached_value)
                except json.JSONDecodeError:
                    pass

            # Execute function
            result = func(*args, **kwargs)

            # Store in cache
            try:
                cache_client.set(key, json.dumps(result), ttl)
            except (TypeError, json.JSONEncodeError):
                # Result not JSON serializable, skip caching
                pass

            return result

        # Return appropriate wrapper based on whether function is async
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def invalidate_cache(pattern: str):
    """
    Invalidate all cache entries matching pattern.

    Usage:
        invalidate_cache("books:*")  # Clear all book-related cache
    """
    return cache_client.clear_pattern(pattern)

