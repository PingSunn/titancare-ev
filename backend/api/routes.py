"""
FastAPI routes for the chat API.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from agents import Runner

from core_agents import create_orchestrator_agent
from models import get_model_registry
from sessions import get_redis_session, create_session_id


router = APIRouter(prefix="/api", tags=["chat"])


# Request/Response Models
class ChatRequest(BaseModel):
    """Chat request payload."""

    message: str = Field(..., description="User message to process")
    session_id: Optional[str] = Field(
        None, description="Session ID for conversation continuity"
    )
    model: Optional[str] = Field(
        None, description="Model alias to use (from llms.txt)"
    )


class ChatResponse(BaseModel):
    """Chat response payload."""

    response: str = Field(..., description="Agent response")
    session_id: str = Field(..., description="Session ID for this conversation")


class SessionResponse(BaseModel):
    """Session creation response."""

    session_id: str = Field(..., description="New session ID")


class ModelsResponse(BaseModel):
    """Available models response."""

    models: list[str] = Field(..., description="List of available model aliases")
    default: str = Field(..., description="Default model alias")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")


# Endpoints
@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="healthy", version="0.1.0")


@router.post("/session", response_model=SessionResponse)
async def create_session(user_id: Optional[str] = None) -> SessionResponse:
    """
    Create a new chat session.

    Args:
        user_id: Optional user identifier to associate with session.

    Returns:
        New session ID.
    """
    session_id = create_session_id(user_id)
    return SessionResponse(session_id=session_id)


@router.get("/models", response_model=ModelsResponse)
async def list_models() -> ModelsResponse:
    """
    List available model aliases.

    Returns:
        List of model aliases from llms.txt.
    """
    registry = get_model_registry()
    return ModelsResponse(
        models=registry.list_aliases(),
        default=registry.get_default(),
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Process a chat message through the agent system.

    The orchestrator agent analyzes the request and delegates to
    appropriate specialized agents, then summarizes the response.

    Args:
        request: Chat request with message, optional session_id, and optional model.

    Returns:
        Agent response and session ID.
    """
    try:
        # Get or create session
        session_id = request.session_id or create_session_id()
        session = get_redis_session(session_id)

        # Get model registry
        registry = get_model_registry()

        # Create orchestrator agent
        orchestrator = create_orchestrator_agent(
            model_registry=registry,
            model_alias=request.model,
        )

        # Run the agent
        result = await Runner.run(
            orchestrator,
            request.message,
            session=session,
        )

        return ChatResponse(
            response=result.final_output,
            session_id=session_id,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat request: {str(e)}",
        )


@router.delete("/session/{session_id}")
async def clear_session(session_id: str) -> dict:
    """
    Clear a session's conversation history.

    Args:
        session_id: Session ID to clear.

    Returns:
        Confirmation message.
    """
    try:
        session = get_redis_session(session_id)
        await session.clear_session()
        return {"message": f"Session {session_id} cleared"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing session: {str(e)}",
        )
