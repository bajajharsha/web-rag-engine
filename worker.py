#!/usr/bin/env python3
"""
Simple Redis Worker for URL Processing
This script runs as a separate process to handle URL processing jobs
"""

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
    print(f"📡 Connecting to Redis: {settings.REDIS_URL}")
    print(f"📋 Queue: {settings.REDIS_QUEUE_NAME}")

    # Connect to Redis
    try:
        redis_client.connect()
        print("✅ Connected to Redis successfully")
    except Exception as e:
        print(f"❌ Failed to connect to Redis: {str(e)}")
        return

    # worker usecase -> part of fastapi - will have all the business logic to handle the queue
    worker_usecase = WorkerUsecase()
    await worker_usecase.worker_loop()  # ✅ Now using await


if __name__ == "__main__":
    asyncio.run(main())  # ✅ Run async main function
