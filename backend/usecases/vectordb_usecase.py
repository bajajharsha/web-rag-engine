from typing import Any, Dict, List, Optional

from pinecone import Pinecone, ServerlessSpec

from backend.config.settings import settings


class VectorDBUsecase:
    """
    Usecase for vector database operations using Pinecone
    Handles upserting embeddings and metadata for retrieval
    """

    def __init__(self):
        # Initialize Pinecone client
        print("🌲 Initializing Pinecone client...")
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index_name = settings.PINECONE_INDEX_NAME
        self.index = None
        print("✅ Pinecone client initialized")

    def _get_index(self):
        """Get or create Pinecone index"""
        if self.index is None:
            try:
                # Check if index exists
                if self.index_name not in self.pc.list_indexes().names():
                    print(f"🔨 Creating Pinecone index: {self.index_name}")
                    self.pc.create_index(
                        name=self.index_name,
                        dimension=settings.EMBEDDING_DIMENSION,
                        metric="cosine",
                        spec=ServerlessSpec(
                            cloud="aws", region=settings.PINECONE_ENVIRONMENT
                        ),
                    )
                    print(f"✅ Created index: {self.index_name}")

                self.index = self.pc.Index(self.index_name)
                print(f"✅ Connected to index: {self.index_name}")
            except Exception as e:
                print(f"❌ Error connecting to Pinecone: {str(e)}")
                raise e

        return self.index

    async def upsert_embeddings(self, embedded_chunks: List[Dict[str, Any]]) -> bool:
        """
        Upsert embeddings to Pinecone vector database

        Args:
            embedded_chunks: List of chunks with embeddings and metadata

        Returns:
            True if successful, False otherwise
        """
        if not embedded_chunks:
            print("⚠️ No embedded chunks to upsert")
            return False

        try:
            print(f"🌲 Upserting {len(embedded_chunks)} embeddings to Pinecone...")

            # Prepare vectors for Pinecone
            vectors = []
            for chunk in embedded_chunks:
                # Extract essential metadata for retrieval (no content)
                metadata = {
                    "chunk_id": chunk.get("id"),
                    "url": chunk.get("metadata", {}).get("url"),
                    "job_id": chunk.get("metadata", {}).get("job_id"),
                }

                # Remove empty metadata fields
                metadata = {k: v for k, v in metadata.items() if v}

                vectors.append(
                    {
                        "id": chunk.get("id"),
                        "values": chunk.get("embedding"),
                        "metadata": metadata,
                    }
                )

            # Upsert to Pinecone
            index = self._get_index()
            index.upsert(vectors=vectors)

            print(f"✅ Successfully upserted {len(vectors)} vectors to Pinecone")
            return True

        except Exception as e:
            print(f"❌ Error upserting to Pinecone: {str(e)}")
            return False

    async def search_similar(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter_dict: Optional[Dict] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors in Pinecone

        Args:
            query_embedding: Query vector to search for
            top_k: Number of results to return
            filter_dict: Optional metadata filter

        Returns:
            List of search results with metadata
        """
        try:
            print(f"🔍 Searching Pinecone for top {top_k} similar vectors...")

            index = self._get_index()
            results = index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter_dict,
            )

            # Format results
            search_results = []
            for match in results.matches:
                search_results.append(
                    {"id": match.id, "score": match.score, "metadata": match.metadata}
                )

            print(f"✅ Found {len(search_results)} similar vectors")
            return search_results

        except Exception as e:
            print(f"❌ Error searching Pinecone: {str(e)}")
            return []

    async def delete_by_job_id(self, job_id: str) -> bool:
        """
        Delete all vectors for a specific job

        Args:
            job_id: Job ID to delete vectors for

        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"🗑️ Deleting vectors for job: {job_id}")

            index = self._get_index()
            index.delete(filter={"job_id": job_id})

            print(f"✅ Deleted vectors for job: {job_id}")
            return True

        except Exception as e:
            print(f"❌ Error deleting vectors: {str(e)}")
            return False
