# usecase to write the business logic to ingest url
# It will be using services and repositories to implement the business logic

import uuid
from datetime import datetime
from typing import Any, Dict

import pytz
from fastapi import Depends

from backend.repositories.url_repository import UrlRepository
from backend.services.queue_service import QueueService

tz_india = pytz.timezone("Asia/Kolkata")


class UrlUsecase:
    def __init__(
        self,
        queue_service: QueueService = Depends(QueueService),
        url_repository: UrlRepository = Depends(UrlRepository),
    ):
        self.queue_service = queue_service
        self.url_repository = url_repository

    async def ingest_url(self, url: str) -> Dict[str, Any]:
        """
        Main method to ingest URL
        URL validation is handled by Pydantic HttpUrl
        """
        print(f"URL Usecase: {url}")

        # Step 1: Create job entry
        job_id = str(uuid.uuid4())
        job_data = {
            "job_id": job_id,
            "url": str(url),
            "status": "pending",
            "submitted_at": datetime.now(tz_india).strftime("%Y-%m-%d %H:%M:%S"),
            "created_at": datetime.now(tz_india).strftime("%Y-%m-%d %H:%M:%S"),
        }
        print(f"Job data: {job_data}")
        # Step 2: Push job to Redis queue
        try:
            self.queue_service.push_job(job_data)
            print(f"Job {job_id} pushed to queue successfully")
        except Exception as e:
            print(f"Failed to push job to queue: {str(e)}")
            raise e

        # Add the url to the database
        try:
            await self.url_repository.add_url(job_data)
            print(f"URL {url} added to database successfully")
        except Exception as e:
            print(f"Failed to add URL to database: {str(e)}")
            raise e

        # Step 3: Return job information
        return {
            "job_id": job_id,
            "status": "pending",
            "message": "URL queued for processing",
            "submitted_at": job_data["submitted_at"],
        }
