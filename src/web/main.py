"""
FastAPI main application for Z2 Web Dashboard
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import settings
from .api import jobs, stats, websocket


# Import job queue manager
from .services.job_queue import job_queue_manager


# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Z2 Web Dashboard...")
    print(f"📊 Database: {settings.DATABASE_URL}")
    print(f"🔧 API: {settings.API_PREFIX}")

    # Start job queue workers
    await job_queue_manager.start()

    yield

    # Shutdown
    print("🛑 Shutting down Z2 Web Dashboard...")

    # Stop job queue workers
    await job_queue_manager.stop()


# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(jobs.router, prefix=settings.API_PREFIX)
app.include_router(stats.router, prefix=settings.API_PREFIX)
app.include_router(websocket.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Z2 AI Knowledge Distillery Platform API",
        "version": settings.API_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.web.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
