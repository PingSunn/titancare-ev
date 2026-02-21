from fastapi import APIRouter
from pydantic import BaseModel
from core_agents.orchestrator import create_workflow

router = APIRouter()
agent_workflow = create_workflow()

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    reply: str

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    """
    Main conversational endpoint interacting with TitanCare EV multi-agent workflow.
    """
    # Note: LlamaIndex AgentWorkflow handles handoffs, state, and routing internally
    # Further integration of memory/session context can be wired directly via Context
    
    # Send message to Multi-Agent workflow asynchronously
    response = await agent_workflow.run(user_msg=req.message)
    
    return ChatResponse(reply=str(response))

@router.get("/health")
async def health_check():
    """
    Health check endpoint to verify backend connectivity from the frontend.
    """
    return {"status": "ok", "message": "TitanCare EV Backend is running"}
