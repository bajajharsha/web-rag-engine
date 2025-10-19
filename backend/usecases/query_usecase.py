from fastapi import Depends

from backend.repositories.chunk_repository import ChunkRepository
from backend.usecases.embedding_usecase import EmbeddingUsecase
from backend.usecases.vectordb_usecase import VectorDBUsecase


class QueryUsecase:
    def __init__(
        self,
        embedding_usecase: EmbeddingUsecase = Depends(EmbeddingUsecase),
        vectordb_usecase: VectorDBUsecase = Depends(VectorDBUsecase),
        chunk_repository: ChunkRepository = Depends(ChunkRepository),
    ):
        self.embedding_usecase = embedding_usecase
        self.vectordb_usecase = vectordb_usecase
        self.chunk_repository = chunk_repository

    async def query_documents(self, request: str):
        # Step 1 - Generate embedding for user query
        query_embedding = await self.embedding_usecase.generate_single_embedding(
            request
        )

        # Step 2 - Search vector database for similar chunks
        similar_chunks = await self.vectordb_usecase.search_similar(query_embedding)
        print(f"Similar chunks: {similar_chunks}")

        # Step 3 - Retrieve chunk content from MongoDB
        for chunk in similar_chunks:
            chunk_content = await self.chunk_repository.get_chunk(chunk["id"])
            print(f"Chunk content: {chunk_content}")

        # Step 4 - Build prompt with context and query

        # TODO: Step 5 - Send to LLM for answer generation
        # TODO: Step 6 - Return answer with cited sourcespass

        return "This is a placeholder response. Query processing not yet implemented."
