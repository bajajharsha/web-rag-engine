from datetime import datetime
from typing import List, Optional

from backend.config.database import mongodb_database
from backend.config.settings import settings


class ChatSessionRepository:
    """Repository for managing chat sessions in MongoDB"""

    def __init__(self):
        pass

    def _get_collection(self):
        """Get the chat_sessions collection"""
        if mongodb_database.mongodb_client is None:
            mongodb_database.connect()
        return mongodb_database.mongodb_client[settings.MONGODB_DB_NAME][
            "chat_sessions"
        ]

    async def create_session(self, session_id: str) -> bool:
        """
        Create a new chat session

        Args:
            session_id: Unique session identifier

        Returns:
            True if successful, False otherwise
        """
        try:
            collection = self._get_collection()

            session_data = {
                "session_id": session_id,
                "messages": [],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }

            await collection.insert_one(session_data)
            print(f"✅ Created new session: {session_id}")
            return True

        except Exception as e:
            print(f"❌ Failed to create session: {str(e)}")
            return False

    async def get_session(self, session_id: str) -> Optional[dict]:
        """
        Get a chat session by ID

        Args:
            session_id: Session identifier

        Returns:
            Session data or None if not found
        """
        try:
            collection = self._get_collection()
            session = await collection.find_one({"session_id": session_id})
            return session

        except Exception as e:
            print(f"❌ Failed to get session: {str(e)}")
            return None

    async def add_message(
        self, session_id: str, role: str, content: str, sources: Optional[List] = None
    ) -> bool:
        """
        Add a message to a chat session

        Args:
            session_id: Session identifier
            role: Message role ('user' or 'assistant')
            content: Message content
            sources: Optional list of sources (for assistant messages)

        Returns:
            True if successful, False otherwise
        """
        try:
            collection = self._get_collection()

            message = {
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow(),
            }

            # Add sources only for assistant messages
            if role == "assistant" and sources:
                message["sources"] = sources

            # Update the session with new message
            result = await collection.update_one(
                {"session_id": session_id},
                {
                    "$push": {"messages": message},
                    "$set": {"updated_at": datetime.utcnow()},
                },
            )

            if result.modified_count > 0:
                print(f"✅ Added {role} message to session {session_id}")
                return True
            else:
                print(f"⚠️ Session {session_id} not found")
                return False

        except Exception as e:
            print(f"❌ Failed to add message: {str(e)}")
            return False

    async def get_recent_messages(self, session_id: str, limit: int = 10) -> List[dict]:
        """
        Get recent messages from a session

        Args:
            session_id: Session identifier
            limit: Maximum number of messages to retrieve (default: 10)

        Returns:
            List of recent messages (most recent last)
        """
        try:
            collection = self._get_collection()

            # Get session and extract messages
            session = await collection.find_one({"session_id": session_id})

            if not session:
                print(f"⚠️ Session {session_id} not found")
                return []

            messages = session.get("messages", [])

            # Return last N messages
            return messages[-limit:] if len(messages) > limit else messages

        except Exception as e:
            print(f"❌ Failed to get recent messages: {str(e)}")
            return []

    async def clear_session(self, session_id: str) -> bool:
        """
        Clear all messages from a session

        Args:
            session_id: Session identifier

        Returns:
            True if successful, False otherwise
        """
        try:
            collection = self._get_collection()

            result = await collection.update_one(
                {"session_id": session_id},
                {
                    "$set": {
                        "messages": [],
                        "updated_at": datetime.utcnow(),
                    }
                },
            )

            if result.modified_count > 0:
                print(f"✅ Cleared session {session_id}")
                return True
            else:
                print(f"⚠️ Session {session_id} not found")
                return False

        except Exception as e:
            print(f"❌ Failed to clear session: {str(e)}")
            return False

    async def delete_session(self, session_id: str) -> bool:
        """
        Delete a chat session

        Args:
            session_id: Session identifier

        Returns:
            True if successful, False otherwise
        """
        try:
            collection = self._get_collection()

            result = await collection.delete_one({"session_id": session_id})

            if result.deleted_count > 0:
                print(f"✅ Deleted session {session_id}")
                return True
            else:
                print(f"⚠️ Session {session_id} not found")
                return False

        except Exception as e:
            print(f"❌ Failed to delete session: {str(e)}")
            return False
