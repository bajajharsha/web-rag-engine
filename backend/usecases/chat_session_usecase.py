from typing import List, Optional

from fastapi import Depends

from backend.repositories.chat_session_repository import ChatSessionRepository


class ChatSessionUsecase:
    """Usecase for managing chat sessions"""

    def __init__(
        self,
        chat_session_repository: ChatSessionRepository = Depends(ChatSessionRepository),
    ):
        self.chat_session_repository = chat_session_repository

    async def get_or_create_session(self, session_id: str) -> dict:
        """
        Get existing session or create new one

        Args:
            session_id: Session identifier

        Returns:
            Session data
        """
        session = await self.chat_session_repository.get_session(session_id)

        if not session:
            await self.chat_session_repository.create_session(session_id)
            session = await self.chat_session_repository.get_session(session_id)

        return session

    async def add_user_message(self, session_id: str, message: str) -> bool:
        """
        Add a user message to the session

        Args:
            session_id: Session identifier
            message: User message content

        Returns:
            True if successful
        """
        return await self.chat_session_repository.add_message(
            session_id=session_id, role="user", content=message
        )

    async def add_assistant_message(
        self, session_id: str, message: str, sources: Optional[List] = None
    ) -> bool:
        """
        Add an assistant message to the session

        Args:
            session_id: Session identifier
            message: Assistant response content
            sources: Optional list of sources

        Returns:
            True if successful
        """
        return await self.chat_session_repository.add_message(
            session_id=session_id, role="assistant", content=message, sources=sources
        )

    async def get_chat_history(self, session_id: str, limit: int = 10) -> List[dict]:
        """
        Get recent chat history for context

        Args:
            session_id: Session identifier
            limit: Maximum number of messages (default: 10 = 5 conversation pairs)

        Returns:
            List of recent messages
        """
        return await self.chat_session_repository.get_recent_messages(session_id, limit)

    def format_chat_history_for_llm(self, messages: List[dict]) -> str:
        """
        Format chat history for LLM context

        Args:
            messages: List of message dictionaries

        Returns:
            Formatted string for LLM prompt
        """
        if not messages:
            return "No previous conversation."

        formatted = []
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")

            if role == "user":
                formatted.append(f"User: {content}")
            elif role == "assistant":
                formatted.append(f"Assistant: {content}")

        return "\n".join(formatted)

    async def clear_session(self, session_id: str) -> bool:
        """
        Clear all messages from a session

        Args:
            session_id: Session identifier

        Returns:
            True if successful
        """
        return await self.chat_session_repository.clear_session(session_id)

    async def delete_session(self, session_id: str) -> bool:
        """
        Delete a session completely

        Args:
            session_id: Session identifier

        Returns:
            True if successful
        """
        return await self.chat_session_repository.delete_session(session_id)
