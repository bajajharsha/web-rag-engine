from backend.config.database import mongodb_database
from backend.config.settings import settings


class ChunkRepository:
    def __init__(self):
        pass

    def _get_collection(self):
        """Get the chunks collection, ensuring MongoDB is connected"""
        if mongodb_database.mongodb_client is None:
            mongodb_database.connect()
        return mongodb_database.mongodb_client[settings.MONGODB_DB_NAME]["chunks"]

    async def add_chunk(self, chunk_id: str, chunk_data: dict):
        """
        Add a chunk to the database

        Args:
            chunk_id: Unique identifier for the chunk
            chunk_data: Dictionary containing content and metadata
        """
        try:
            collection = self._get_collection()

            # Prepare chunk document for MongoDB
            chunk_document = {
                "chunk_id": chunk_id,
                "content": chunk_data.get("content"),
                "metadata": chunk_data.get("metadata", {}),
            }

            collection.insert_one(chunk_document)
            return True
        except Exception as e:
            print(f"❌ Failed to add chunk to database: {str(e)}")
            return False

    async def get_chunk(self, chunk_id: str):
        """
        Get a chunk by ID

        Args:
            chunk_id: The chunk ID to retrieve

        Returns:
            Dictionary with content and metadata, or None if not found
        """
        try:
            collection = self._get_collection()
            chunk = collection.find_one({"chunk_id": chunk_id})

            if chunk:
                return {
                    "id": chunk.get("chunk_id"),
                    "content": chunk.get("content"),
                    "metadata": chunk.get("metadata", {}),
                }
            return None
        except Exception as e:
            print(f"❌ Failed to get chunk from database: {str(e)}")
            return None

    async def get_chunks_by_job_id(self, job_id: str):
        """
        Get all chunks for a specific job

        Args:
            job_id: The job ID to retrieve chunks for

        Returns:
            List of chunk dictionaries
        """
        try:
            collection = self._get_collection()
            chunks = collection.find({"metadata.job_id": job_id})

            return [
                {
                    "id": chunk.get("chunk_id"),
                    "content": chunk.get("content"),
                    "metadata": chunk.get("metadata", {}),
                }
                for chunk in chunks
            ]
        except Exception as e:
            print(f"❌ Failed to get chunks from database: {str(e)}")
            return []

    async def get_chunks_by_url(self, url: str):
        """
        Get all chunks for a specific URL

        Args:
            url: The URL to retrieve chunks for

        Returns:
            List of chunk dictionaries
        """
        try:
            collection = self._get_collection()
            chunks = collection.find({"metadata.url": url})

            return [
                {
                    "id": chunk.get("chunk_id"),
                    "content": chunk.get("content"),
                    "metadata": chunk.get("metadata", {}),
                }
                for chunk in chunks
            ]
        except Exception as e:
            print(f"❌ Failed to get chunks from database: {str(e)}")
            return []
