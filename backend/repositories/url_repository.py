from backend.config.database import mongodb_database


class UrlRepository:
    def __init__(self):
        pass

    def _get_collection(self):
        """Get the collection, ensuring MongoDB is connected"""
        if mongodb_database.mongodb_client is None:
            mongodb_database.connect()
        return mongodb_database.get_urls_collection()

    async def add_url(self, url_data: dict):
        """Add a url to the database"""
        try:
            collection = self._get_collection()
            collection.insert_one(url_data)
            print(f"URL {url_data['url']} added to database successfully")
            return True
        except Exception as e:
            print(f"Failed to add URL to database: {str(e)}")
            return False

    async def update_job_status(self, job_id: str, status: str):
        """Update the status of a job"""
        try:
            collection = self._get_collection()
            collection.update_one({"job_id": job_id}, {"$set": {"status": status}})
            print(f"Job {job_id} status updated to {status} successfully")
            return True
        except Exception as e:
            print(f"Failed to update job status: {str(e)}")
            return False
