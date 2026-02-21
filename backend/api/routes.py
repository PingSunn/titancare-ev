from fastapi import APIRouter
from pydantic import BaseModel
from core_agents.specialized import create_specialized_agent
# from sessions.db import save_session_history, get_session_history

router = APIRouter()
agent = create_specialized_agent()

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    reply: str

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    """
    Main conversational endpoint interacting with TitanCare EV agents.
    """
    # Note: LlamaIndex agent.run() handles tool orchestration
    # Further integration of memory/session context can be wired here
    
    # Send message to agent asynchronously
    response = await agent.run(req.message)
    
    return ChatResponse(reply=str(response))
