"""
Audit API endpoints
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.db_service import DatabaseService

router = APIRouter(prefix="/api/v1/audit", tags=["Audit"])

@router.get("/")
async def get_audit_logs(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db)
):
    """Get audit logs"""
    db_service = DatabaseService(session)
    logs = await db_service.get_audit_logs(limit, offset)
    
    return {
        "total": len(logs),
        "limit": limit,
        "offset": offset,
        "logs": [log.to_dict() for log in logs]
    }