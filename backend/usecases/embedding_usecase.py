from typing import Any, Dict, List

from sentence_transformers import SentenceTransformer

from backend.config.settings import settings


class EmbeddingUsecase:
    """
    Usecase for generating embeddings using sentence-transformers
    Uses all-MiniLM-L6-v2 model for fast, efficient embeddings
    """

    def __init__(self):
        # Load MiniLM model
        print("🧠 Loading MiniLM embedding model...")
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
        print("✅ MiniLM model loaded successfully")

    async def generate_embeddings(
        self, chunks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate embeddings for a list of chunks

        Args:
            chunks: List of chunk dictionaries with 'content' field

        Returns:
            List of chunks with added 'embedding' field
        """
        if not chunks:
            print("⚠️ No chunks to embed")
            return []

        try:
            print(f"🧠 Generating embeddings for {len(chunks)} chunks...")

            # Extract content from chunks
            chunk_contents = [chunk.get("content", "") for chunk in chunks]

            # Generate embeddings using MiniLM
            embeddings = self.model.encode(
                chunk_contents,
                show_progress_bar=True,
                convert_to_tensor=False,  # Return numpy arrays instead of tensors
            )

            # Add embeddings to chunks
            embedded_chunks = []
            for i, chunk in enumerate(chunks):
                embedded_chunk = chunk.copy()
                embedded_chunk["embedding"] = embeddings[
                    i
                ].tolist()  # Convert to list for JSON serialization
                embedded_chunks.append(embedded_chunk)

            print(f"✅ Generated {len(embedded_chunks)} embeddings")
            return embedded_chunks

        except Exception as e:
            print(f"❌ Error generating embeddings: {str(e)}")
            return chunks  # Return original chunks if embedding fails

    async def generate_single_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text

        Args:
            text: Text to embed

        Returns:
            List of embedding values
        """
        try:
            embedding = self.model.encode([text], convert_to_tensor=False)
            return embedding[0].tolist()
        except Exception as e:
            print(f"❌ Error generating single embedding: {str(e)}")
            return []
