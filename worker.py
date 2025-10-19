import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from backend.config.redis import redis_client
from backend.config.settings import settings
from backend.usecases.worker_usecase import WorkerUsecase


async def main():
    print("🚀 Starting Redis Worker for URL Processing")
    print(
        f"Connecting to Redis: {settings.REDIS_URL} and queue: {settings.REDIS_QUEUE_NAME}"
    )

    # Connect to Redis
    try:
        redis_client.connect()
        print("✅ Connected to Redis successfully")
    except Exception as e:
        print(f"❌ Failed to connect to Redis: {str(e)}")
        return

    worker_usecase = WorkerUsecase()
    await worker_usecase.worker_loop()


if __name__ == "__main__":
    asyncio.run(main())
