"""FastAPI application setup"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from tracker import __version__
from tracker.api.middleware import (
    ErrorHandlingMiddleware,
    LoggingMiddleware,
    setup_logging,
)
from tracker.api.routers import auth, entries, feedback, stats
from tracker.api.routers import export as export_router
from tracker.core.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events - startup and shutdown"""
    # Startup
    setup_logging()
    init_db()
    yield
    # Shutdown


app = FastAPI(
    title="Tracker API",
    description="Daily logging app with AI motivational feedback",
    version=__version__,
    lifespan=lifespan,
)

# Add custom middleware (order matters - first added = outermost)
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(LoggingMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(entries.router)
app.include_router(feedback.router)
app.include_router(stats.router)
app.include_router(export_router.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Tracker API",
        "version": __version__,
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}
