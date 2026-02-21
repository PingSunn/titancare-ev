import json
from fastapi import APIRouter
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from core_agents.orchestrator import create_workflow
from sessions.db import get_session_history, save_session_history

router = APIRouter()
agent_workflow = create_workflow()

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    reply: str

def _serialize_messages(messages: list[BaseMessage]) -> str:
    """Serialize LangChain messages to a JSON string for storage."""
    serialized = []
    for msg in messages:
        serialized.append({
            "type": msg.__class__.__name__,
            "content": msg.content,
        })
    return json.dumps(serialized)

def _deserialize_messages(history_json: str) -> list[BaseMessage]:
    """Deserialize stored JSON back into LangChain message objects."""
    try:
        raw = json.loads(history_json)
        messages = []
        for item in raw:
            if item["type"] == "HumanMessage":
                messages.append(HumanMessage(content=item["content"]))
            elif item["type"] == "AIMessage":
                messages.append(AIMessage(content=item["content"]))
        return messages
    except Exception:
        return []

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    """
    Main conversational endpoint interacting with TitanCare EV multi-agent workflow.
    Maintains full conversation history per session_id.
    """
    # 1. Load existing conversation history for this session
    history_json = await get_session_history(req.session_id)
    history: list[BaseMessage] = _deserialize_messages(history_json) if history_json else []

    # 2. Append the new user message
    history.append(HumanMessage(content=req.message))

    # 3. Invoke the LangGraph workflow with the full history
    final_state = await agent_workflow.ainvoke({"messages": history})

    # 4. Extract the AI's response (last message in state)
    final_response = final_state["messages"][-1].content

    # 5. Append the AI response to history and persist
    history.append(AIMessage(content=final_response))
    await save_session_history(req.session_id, _serialize_messages(history))

    return ChatResponse(reply=str(final_response))

@router.get("/health")
async def health_check():
    """
    Health check endpoint to verify backend connectivity from the frontend.
    """
    return {"status": "ok", "message": "TitanCare EV Backend is running"}
