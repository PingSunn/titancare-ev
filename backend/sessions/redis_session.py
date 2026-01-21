"""
Redis session management for conversation persistence.
"""

import uuid
from typing import Optional

from agents.extensions.memory import RedisSession

from config import settings


def create_session_id(user_id: Optional[str] = None) -> str:
    """
    Create a unique session ID.

    Args:
        user_id: Optional user identifier to include in session ID.

    Returns:
        Unique session identifier string.
    """
    unique_id = uuid.uuid4().hex[:12]
    if user_id:
        return f"{user_id}_{unique_id}"
    return f"session_{unique_id}"


def get_redis_session(
    session_id: str,
    redis_url: Optional[str] = None,
) -> RedisSession:
    """
    Get or create a Redis session for conversation persistence.

    Args:
        session_id: Unique identifier for the session.
        redis_url: Optional Redis URL override (uses settings.redis_url if not provided).

    Returns:
        RedisSession instance for the given session ID.

    Example:
        ```python
        session = get_redis_session("user_123_abc")
        result = await Runner.run(agent, "Hello", session=session)
        ```
    """
    url = redis_url or settings.redis_url
    return RedisSession.from_url(session_id, url=url)


class SessionManager:
    """
    Manager for handling multiple sessions.
    Provides utilities for session lifecycle management.
    """

    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialize the session manager.

        Args:
            redis_url: Optional Redis URL override.
        """
        self.redis_url = redis_url or settings.redis_url
        self._sessions: dict[str, RedisSession] = {}

    def get_session(self, session_id: str) -> RedisSession:
        """
        Get or create a session by ID.

        Args:
            session_id: Unique session identifier.

        Returns:
            RedisSession instance.
        """
        if session_id not in self._sessions:
            self._sessions[session_id] = get_redis_session(
                session_id, self.redis_url
            )
        return self._sessions[session_id]

    def create_new_session(self, user_id: Optional[str] = None) -> tuple[str, RedisSession]:
        """
        Create a new session with auto-generated ID.

        Args:
            user_id: Optional user identifier.

        Returns:
            Tuple of (session_id, RedisSession).
        """
        session_id = create_session_id(user_id)
        session = self.get_session(session_id)
        return session_id, session

    async def clear_session(self, session_id: str) -> bool:
        """
        Clear a session's conversation history.

        Args:
            session_id: Session to clear.

        Returns:
            True if session was cleared, False if not found.
        """
        if session_id in self._sessions:
            session = self._sessions[session_id]
            await session.clear_session()
            return True
        return False
