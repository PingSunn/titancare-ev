import asyncio
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as chat_router
from sessions.db import init_session_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup: Initializing connections")

    # Initialize conversational sessions DB
    await init_session_db()
    print("SQLite session database initialized")

    # Connect Prisma client to Supabase
    from db import get_client
    await get_client()
    print("Prisma connected to Supabase")

    yield

    # Disconnect Prisma on shutdown
    from db import disconnect
    await disconnect()
    print("Application shutdown: Prisma disconnected")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"], # อนุญาตทุก Method (GET, POST, OPTIONS)
    allow_headers=["*"], # อนุญาตทุก Header
)
# Register API routes
app.include_router(chat_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "TitanCare EV Backend API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
