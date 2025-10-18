import json
from typing import Any, Dict, Optional

from fastapi import HTTPException

from backend.config.redis import redis_client
from backend.config.settings import settings


class QueueService:
    """Service for managing Redis queue operations"""

    def __init__(self):
        self.queue_name = settings.REDIS_QUEUE_NAME

    def push_job(self, job_data: Dict[str, Any]) -> bool:
        """
        Push a job to the Redis queue
        Returns True if successful, False otherwise
        """
        try:
            client = redis_client.get_redis_client()
            # Convert job data to JSON string
            job_json = json.dumps(job_data, default=str)
            # Push to queue (LPUSH adds to left side of list)
            client.lpush(self.queue_name, job_json)
            return True
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to push job to queue: {str(e)}"
            )

    def pop_job(self, timeout: int = 10) -> Optional[Dict[str, Any]]:
        """
        Pop a job from the Redis queue (blocking)
        Returns job data or None if timeout
        """
        try:
            client = redis_client.get_redis_client()
            # BRPOP blocks until job is available or timeout
            result = client.brpop(self.queue_name, timeout=timeout)

            if result:
                # result is tuple: (queue_name, job_json)
                _, job_json = result
                return json.loads(job_json)
            return None
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to pop job from queue: {str(e)}"
            )

    def get_queue_length(self) -> int:
        """Get the number of jobs in the queue"""
        try:
            client = redis_client.get_redis_client()
            return client.llen(self.queue_name)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to get queue length: {str(e)}"
            )
