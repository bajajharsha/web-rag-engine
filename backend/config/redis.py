import redis
from fastapi import HTTPException

from backend.config.settings import settings


class RedisClient:
    def __init__(self, redis_url: str, db: int = 0) -> None:
        self.redis_url = redis_url
        self.db = db
        self.redis_client = None

    def connect(self):
        """Connect to Redis server"""
        try:
            self.redis_client = redis.from_url(
                self.redis_url, db=self.db, decode_responses=True
            )
            # Test connection
            self.redis_client.ping()
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Unable to connect to Redis: {str(e)}"
            )

    def get_redis_client(self):
        """Get Redis client instance"""
        if not self.redis_client:
            raise HTTPException(status_code=503, detail="Redis client is not connected")
        return self.redis_client

    def disconnect(self):
        """Disconnect from Redis"""
        try:
            if self.redis_client:
                self.redis_client.close()
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Unable to close Redis connection: {str(e)}"
            )


# Instantiate the Redis client
redis_client = RedisClient(settings.REDIS_URL, settings.REDIS_DB)
