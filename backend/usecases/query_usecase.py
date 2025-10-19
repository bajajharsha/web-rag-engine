from typing import Optional

from fastapi import Depends

from backend.prompts.llm_prompt import RAG_PROMPT
from backend.repositories.chunk_repository import ChunkRepository
from backend.usecases.chat_session_usecase import ChatSessionUsecase
from backend.usecases.embedding_usecase import EmbeddingUsecase
from backend.usecases.groq_usecase import GroqUsecase
from backend.usecases.vectordb_usecase import VectorDBUsecase


class QueryUsecase:
    def __init__(
        self,
        embedding_usecase: EmbeddingUsecase = Depends(EmbeddingUsecase),
        vectordb_usecase: VectorDBUsecase = Depends(VectorDBUsecase),
        chunk_repository: ChunkRepository = Depends(ChunkRepository),
        groq_usecase: GroqUsecase = Depends(GroqUsecase),
        chat_session_usecase: ChatSessionUsecase = Depends(ChatSessionUsecase),
    ):
        self.embedding_usecase = embedding_usecase
        self.vectordb_usecase = vectordb_usecase
        self.chunk_repository = chunk_repository
        self.groq_usecase = groq_usecase
        self.chat_session_usecase = chat_session_usecase

    async def query_documents(
        self, request: str, session_id: Optional[str] = None, top_k: int = 5
    ):
        try:
            # Step 0 - Handle chat session (if session_id provided)
            chat_history_text = ""
            if session_id:
                # Get or create session
                await self.chat_session_usecase.get_or_create_session(session_id)

                # Add user message to session
                await self.chat_session_usecase.add_user_message(session_id, request)

                # Get recent chat history for context
                chat_history = await self.chat_session_usecase.get_chat_history(
                    session_id, limit=10
                )

                # Format chat history for LLM (exclude the current message)
                if len(chat_history) > 1:
                    chat_history_text = (
                        self.chat_session_usecase.format_chat_history_for_llm(
                            chat_history[:-1]
                        )
                    )
                    print(f"💬 Using chat history: {len(chat_history) - 1} messages")

            # Step 1 - Generate embedding for user query
            print(f"🔍 Processing query: {request}")
            query_embedding = await self.embedding_usecase.generate_single_embedding(
                request
            )

            if not query_embedding:
                return {
                    "answer": "Sorry, I couldn't process your query. Please try again.",
                    "sources": [],
                    "query": request,
                }

            # Step 2 - Search vector database for similar chunks
            print(f"🔍 Searching for top {top_k} similar chunks...")
            similar_chunks = await self.vectordb_usecase.search_similar(
                query_embedding, top_k=top_k
            )
            print(f"Found {len(similar_chunks)} similar chunks")

            if not similar_chunks:
                return {
                    "answer": "I couldn't find any relevant information for your query.",
                    "sources": [],
                    "query": request,
                }

            # Step 3 - Retrieve chunk content from MongoDB and build context
            context_chunks = []
            cited_sources = []

            for chunk in similar_chunks:
                chunk_content = await self.chunk_repository.get_chunk(chunk["id"])

                if chunk_content:
                    # Add to context for LLM
                    context_chunks.append(
                        {
                            "content": chunk_content["content"],
                            "url": chunk_content["metadata"].get("url", "Unknown URL"),
                            "score": chunk["score"],
                        }
                    )

                    # Add to cited sources
                    cited_sources.append(
                        {
                            "chunk_id": chunk["id"],
                            "url": chunk_content["metadata"].get("url", "Unknown URL"),
                            "content": chunk_content["content"][:200] + "..."
                            if len(chunk_content["content"]) > 200
                            else chunk_content["content"],
                            "score": chunk["score"],
                            "metadata": chunk_content["metadata"],
                        }
                    )

            if not context_chunks:
                return {
                    "answer": "I found similar chunks but couldn't retrieve their content.",
                    "sources": [],
                    "query": request,
                }

            # Step 4 - Build prompt with context, chat history, and query
            context_text = "\n\n".join(
                [
                    f"Source: {chunk['url']}\nContent: {chunk['content']}"
                    for chunk in context_chunks
                ]
            )

            # Use the RAG prompt from the prompts file
            prompt = RAG_PROMPT.format(
                chat_history=chat_history_text, context=context_text, query=request
            )

            # Step 5 - Send to LLM for answer generation
            print("🤖 Generating response with LLM...")
            llm_response = await self.groq_usecase.generate_response(prompt)

            # Step 6 - Save assistant response to session
            if session_id:
                await self.chat_session_usecase.add_assistant_message(
                    session_id, llm_response, cited_sources
                )

            # Step 7 - Return answer with cited sources
            return {"answer": llm_response, "sources": cited_sources, "query": request}

        except Exception as e:
            print(f"❌ Error in query processing: {str(e)}")
            return {
                "answer": f"Sorry, I encountered an error while processing your query: {str(e)}",
                "sources": [],
                "query": request,
            }
