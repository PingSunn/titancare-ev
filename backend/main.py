"""
FastAPI application entry point.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from api import router
from models import get_model_registry


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Initialize resources on startup and cleanup on shutdown.
    """
    # Startup
    print("Starting TitanCare Backend...")

    # Pre-load model registry
    registry = get_model_registry()
    print(f"Loaded {len(registry.list_aliases())} model aliases")
    print(f"Default model: {registry.get_default()}")

    yield

    # Shutdown
    print("Shutting down TitanCare Backend...")


# Create FastAPI application
app = FastAPI(
    title="TitanCare Backend",
    description="Multi-agent AI backend using OpenAI Agents SDK",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(router)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "TitanCare Backend",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/api/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
