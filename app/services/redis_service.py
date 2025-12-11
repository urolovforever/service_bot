"""Redis service for session management"""

import json
import logging
from typing import Optional, Any, Dict
from redis.asyncio import Redis
from app.config import settings

logger = logging.getLogger(__name__)


class RedisService:
    """Redis service for caching and session management"""

    def __init__(self):
        self.redis: Optional[Redis] = None

    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis = Redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
            await self.redis.ping()
            logger.info("Connected to Redis successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis:
            await self.redis.close()
            logger.info("Disconnected from Redis")

    async def set_session(self, user_id: int, key: str, value: Any, ttl: int = None) -> None:
        """Set session data"""
        if not self.redis:
            logger.warning("Redis not connected")
            return

        session_key = f"session:{user_id}:{key}"
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            await self.redis.set(session_key, value, ex=ttl or settings.SESSION_TTL)
        except Exception as e:
            logger.error(f"Failed to set session: {e}")

    async def get_session(self, user_id: int, key: str) -> Optional[Any]:
        """Get session data"""
        if not self.redis:
            logger.warning("Redis not connected")
            return None

        session_key = f"session:{user_id}:{key}"
        try:
            value = await self.redis.get(session_key)
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return None
        except Exception as e:
            logger.error(f"Failed to get session: {e}")
            return None

    async def delete_session(self, user_id: int, key: str) -> None:
        """Delete session data"""
        if not self.redis:
            logger.warning("Redis not connected")
            return

        session_key = f"session:{user_id}:{key}"
        try:
            await self.redis.delete(session_key)
        except Exception as e:
            logger.error(f"Failed to delete session: {e}")

    async def clear_user_session(self, user_id: int) -> None:
        """Clear all user session data"""
        if not self.redis:
            logger.warning("Redis not connected")
            return

        try:
            keys = await self.redis.keys(f"session:{user_id}:*")
            if keys:
                await self.redis.delete(*keys)
        except Exception as e:
            logger.error(f"Failed to clear user session: {e}")

    async def set_browsing_state(
        self,
        user_id: int,
        location_id: int,
        category_id: int,
        provider_ids: list,
        current_index: int = 0,
        filters: Optional[Dict] = None,
    ) -> None:
        """Set browsing state"""
        state = {
            "location_id": location_id,
            "category_id": category_id,
            "provider_ids": provider_ids,
            "current_index": current_index,
            "filters": filters or {},
        }
        await self.set_session(user_id, "browsing_state", state)

    async def get_browsing_state(self, user_id: int) -> Optional[Dict]:
        """Get browsing state"""
        return await self.get_session(user_id, "browsing_state")

    async def update_browsing_index(self, user_id: int, index: int) -> None:
        """Update browsing index"""
        state = await self.get_browsing_state(user_id)
        if state:
            state["current_index"] = index
            await self.set_session(user_id, "browsing_state", state)

    async def increment_rate_limit(self, user_id: int, action: str, ttl: int) -> int:
        """Increment rate limit counter"""
        if not self.redis:
            return 0

        key = f"ratelimit:{user_id}:{action}"
        try:
            count = await self.redis.incr(key)
            if count == 1:
                await self.redis.expire(key, ttl)
            return count
        except Exception as e:
            logger.error(f"Failed to increment rate limit: {e}")
            return 0

    async def get_rate_limit(self, user_id: int, action: str) -> int:
        """Get rate limit counter"""
        if not self.redis:
            return 0

        key = f"ratelimit:{user_id}:{action}"
        try:
            value = await self.redis.get(key)
            return int(value) if value else 0
        except Exception as e:
            logger.error(f"Failed to get rate limit: {e}")
            return 0


# Global Redis service instance
redis_service = RedisService()
