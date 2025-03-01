from fastapi import APIRouter

from app.api import journal, health
from app.core.config import settings

# Create main router
router = APIRouter(prefix=settings.API_PREFIX)

# Include all routers
router.include_router(health.router, tags=["Health"])
router.include_router(journal.router, prefix="/journal", tags=["Journal"]) 