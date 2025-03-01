import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import router
from app.core.config import settings

# Initialize the FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API for Trinity Journaling App",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(router)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to the Trinity Journaling App API",
        "docs": "/docs",
        "health": f"{settings.API_PREFIX}/health"
    } 