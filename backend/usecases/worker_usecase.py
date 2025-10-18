import asyncio
import json

from backend.config.redis import redis_client
from backend.config.settings import settings
from backend.repositories.url_repository import UrlRepository


class WorkerUsecase:
    def __init__(self):
        self.url_repository = UrlRepository()

    async def worker_loop(self):
        """Main worker loop that processes jobs from Redis queue"""
        print("🔍 Starting worker loop... from usecase")
        print("Press Ctrl+C to stop the worker")

        try:
            while True:
                try:
                    # Check if queue is empty
                    queue_length = redis_client.get_redis_client().llen(
                        settings.REDIS_QUEUE_NAME
                    )

                    if queue_length == 0:
                        print(".", end="", flush=True)  # Show worker is alive
                        await asyncio.sleep(5)  # Wait 5 seconds before checking again
                        continue

                    print(f"\n📊 Queue has {queue_length} jobs")

                    # Get job from queue (blocking pop)
                    job_data = redis_client.get_redis_client().brpop(
                        settings.REDIS_QUEUE_NAME, timeout=10
                    )

                    if job_data:
                        # job_data is tuple: (queue_name, job_json)
                        _, job_json = job_data
                        job = json.loads(job_json)

                        print(
                            f"📥 Received job: {job.get('job_id')} and url: {job.get('url')}"
                        )
                        await self.process_url_job(job)  # ✅ Now using await
                    else:
                        # No job received (timeout)
                        print(".", end="", flush=True)

                except KeyboardInterrupt:
                    print("\n🛑 Worker stopped by user")
                    break
                except Exception as e:
                    print(f"\n❌ Error in worker loop: {str(e)}")
                    await asyncio.sleep(5)  # Wait before retrying

        except Exception as e:
            print(f"❌ Fatal error in worker: {str(e)}")
        finally:
            print("🔌 Worker loop ended")

    async def process_url_job(self, job_data: dict):
        """
        Process a single URL job
        """

        job_id = job_data.get("job_id")
        url = job_data.get("url")

        print(f"🔄 Processing job {job_id} for URL: {url}")

        try:
            # Step 1 - Update job status to "processing" in MongoDB
            print(f"📝[1] Updating job {job_id} status to 'processing'")
            result = await self.url_repository.update_job_status(job_id, "processing")
            if not result:
                print(f"❌ Failed to update job {job_id} status to 'processing'")
                return

            # TODO: Step 2 - Fetch URL content (web scraping)
            print(f"🌐 Fetching content from: {url}")
            # TODO: Use scraping service from backend/services/scraping_service.py

            # TODO: Step 3 - Clean HTML content
            print("🧹 Cleaning HTML content")
            # TODO: Use content cleaning service

            # TODO: Step 4 - Chunk text
            print("📄 Chunking text content")
            # TODO: Use chunking service from backend/services/chunking_service.py

            # TODO: Step 5 - Generate embeddings
            print("🧠 Generating embeddings")
            # TODO: Use embedding service from backend/services/embedding_service.py

            # TODO: Step 6 - Store in vector database
            print("💾 Storing in vector database")
            # TODO: Use vector service from backend/services/vector_service.py

            # TODO: Step 7 - Update job status to "completed" in MongoDB
            print(f"✅ Job {job_id} completed successfully")
            # TODO: Use job repository to update status

        except Exception as e:
            print(f"❌ Error processing job {job_id}: {str(e)}")
            # TODO: Update job status to "failed" in MongoDB
            # TODO: Log error details
