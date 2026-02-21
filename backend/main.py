import asyncio
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from api.routes import router as chat_router
from sessions.db import init_session_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup ML models, DB connections, or Redis/SQLite sessions here
    print("Application startup: Initializing connections")
    
    # Initialize conversational sessions DB
    await init_session_db()
    print("SQLite session database initialized")
    
    # Initialize relational database tables
    import database
    from models import appointment
    database.Base.metadata.create_all(bind=database.engine)
    print("SQLAlchemy database tables created/verified")
    
    yield
    print("Application shutdown: Cleaning up resources")

app = FastAPI(lifespan=lifespan)

# Register API routes
app.include_router(chat_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "TitanCare EV Backend API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
