"""
Redis client configuration and utilities for caching.
"""
import redis
import json
import os
from typing import Optional
from . import schemas


class RedisClient:
    """Redis client for caching user data and other application data."""
    
    def __init__(self):
        """Initialize Redis connection with environment configuration."""
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis = redis.from_url(redis_url, decode_responses=True)

    def cache_user(self, user_id: int, user_data: dict, expire_time: int = 3600):
        """
        Cache user data in Redis.
        
        Args:
            user_id: User ID to use as cache key
            user_data: User data dictionary to cache
            expire_time: Expiration time in seconds (default 1 hour)
        """
        key = f"user:{user_id}"
        self.redis.setex(key, expire_time, json.dumps(user_data))

    def get_cached_user(self, user_id: int) -> Optional[dict]:
        """
        Retrieve cached user data from Redis.
        
        Args:
            user_id: User ID to retrieve from cache
            
        Returns:
            User data dictionary if found, None otherwise
        """
        key = f"user:{user_id}"
        cached_data = self.redis.get(key)
        if cached_data:
            return json.loads(cached_data)
        return None

    def invalidate_user_cache(self, user_id: int):
        """
        Remove user data from cache.
        
        Args:
            user_id: User ID to remove from cache
        """
        key = f"user:{user_id}"
        self.redis.delete(key)

    def cache_reset_token(self, email: str, token: str, expire_time: int = 3600):
        """
        Cache password reset token.
        
        Args:
            email: User email
            token: Reset token
            expire_time: Token expiration time in seconds (default 1 hour)
        """
        key = f"reset_token:{email}"
        self.redis.setex(key, expire_time, token)

    def get_reset_token(self, email: str) -> Optional[str]:
        """
        Retrieve password reset token from cache.
        
        Args:
            email: User email
            
        Returns:
            Reset token if found, None otherwise
        """
        key = f"reset_token:{email}"
        return self.redis.get(key)

    def invalidate_reset_token(self, email: str):
        """
        Remove password reset token from cache.
        
        Args:
            email: User email
        """
        key = f"reset_token:{email}"
        self.redis.delete(key)


# Global Redis client instance
redis_client = RedisClient()