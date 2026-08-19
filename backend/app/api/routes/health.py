"""
Health check and metrics endpoints
"""

from fastapi import APIRouter, status, Response
from fastapi.responses import JSONResponse, PlainTextResponse
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


@router.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    try:
        from app.core.metrics import get_metrics
        return PlainTextResponse(
            content=get_metrics(),
            media_type="text/plain"
        )
    except ImportError as e:
        return PlainTextResponse(
            content=f"# Metrics not available: {str(e)}",
            media_type="text/plain"
        )