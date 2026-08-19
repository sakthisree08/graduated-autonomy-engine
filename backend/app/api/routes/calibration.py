"""
Calibration API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.calibration_service import CalibrationService
from app.core.security import get_current_api_key
from datetime import datetime

router = APIRouter(prefix="/api/v1/calibration", tags=["Calibration"])

@router.get("/stats/{operation}")
async def get_calibration_stats(
    operation: str,
    session: AsyncSession = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """Get calibration stats for an operation"""
    service = CalibrationService(session)
    stats = await service.get_stats(operation)
    return stats

@router.get("/all")
async def get_all_calibration_stats(
    session: AsyncSession = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """Get all calibration stats"""
    from sqlalchemy import select
    from app.models.calibration import Calibration
    
    result = await session.execute(select(Calibration))
    calibrations = result.scalars().all()
    
    return {
        "calibrations": [c.to_dict() for c in calibrations]
    }

@router.post("/reset/{operation}")
async def reset_calibration(
    operation: str,
    session: AsyncSession = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """Reset calibration for an operation"""
    service = CalibrationService(session)
    
    calibration = await service._get_or_create(operation)
    calibration.action_count = 0
    calibration.confirm_count = 0
    calibration.reject_count = 0
    calibration.modify_count = 0
    calibration.risk_adjustment = 0
    calibration.history = []
    calibration.last_updated = datetime.utcnow()
    
    await session.commit()
    return {"message": f"Calibration reset for {operation}"}