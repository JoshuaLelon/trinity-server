from fastapi import APIRouter
from datetime import datetime
from pydantic import BaseModel

from app.core.config import settings

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint for monitoring the API.
    
    Returns:
        HealthResponse: Status information about the API
    """
    return HealthResponse(
        status="ok",
        version="1.0.0",
        timestamp=datetime.now().isoformat()
    ) 