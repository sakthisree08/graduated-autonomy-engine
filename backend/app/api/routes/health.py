"""
Health check endpoint
"""

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from datetime import datetime

router = APIRouter(tags=["Health"])

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "graduated-autonomy-engine",
        }
    )