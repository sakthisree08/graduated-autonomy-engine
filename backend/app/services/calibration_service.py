"""
Calibration Service - Learns from human decisions
"""

import uuid
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.calibration import Calibration

logger = logging.getLogger(__name__)


class CalibrationService:
    """Service for adaptive calibration of risk thresholds"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def record_decision(self, operation: str, decision: str, 
                              modification: Optional[Dict] = None):
        """Record a human decision for an operation"""
        calibration = await self._get_or_create(operation)
        calibration.action_count += 1
        
        if decision == "confirm":
            calibration.confirm_count += 1
        elif decision == "reject":
            calibration.reject_count += 1
        elif decision == "modify":
            calibration.modify_count += 1
        
        if not calibration.history:
            calibration.history = []
        calibration.history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "decision": decision,
            "modification": modification,
        })
        
        if len(calibration.history) > 100:
            calibration.history = calibration.history[-100:]
        
        calibration.last_updated = datetime.utcnow()
        calibration.risk_adjustment = self._calculate_adjustment(calibration)
        
        await self.session.flush()
        return calibration
    
    async def get_adjustment(self, operation: str) -> int:
        """Get risk adjustment for an operation (-5 to +5)"""
        calibration = await self._get_or_create(operation)
        return calibration.risk_adjustment
    
    async def apply_adjustment(self, operation: str, base_risk: int) -> int:
        """Apply calibration adjustment to a risk score"""
        adjustment = await self.get_adjustment(operation)
        adjusted = base_risk + adjustment
        return max(0, min(100, adjusted))
    
    async def get_stats(self, operation: str) -> Dict[str, Any]:
        """Get calibration statistics for an operation"""
        calibration = await self._get_or_create(operation)
        
        if calibration.action_count == 0:
            return {
                "operation": operation,
                "actions": 0,
                "confirm_rate": 0,
                "reject_rate": 0,
                "modify_rate": 0,
                "adjustment": 0,
                "status": "insufficient_data"
            }
        
        return {
            "operation": calibration.operation,
            "actions": calibration.action_count,
            "confirm_rate": calibration.confirm_count / calibration.action_count,
            "reject_rate": calibration.reject_count / calibration.action_count,
            "modify_rate": calibration.modify_count / calibration.action_count,
            "adjustment": calibration.risk_adjustment,
            "status": "active" if calibration.action_count > 10 else "learning",
        }
    
    async def _get_or_create(self, operation: str) -> Calibration:
        """Get or create calibration record"""
        result = await self.session.execute(
            select(Calibration).where(Calibration.operation == operation)
        )
        calibration = result.scalar_one_or_none()
        
        if not calibration:
            calibration = Calibration(
                id=str(uuid.uuid4()),
                operation=operation,
                action_count=0,
                confirm_count=0,
                reject_count=0,
                modify_count=0,
                risk_adjustment=0,
                history=[],
            )
            self.session.add(calibration)
            await self.session.flush()
        
        return calibration
    
    def _calculate_adjustment(self, calibration: Calibration) -> int:
        """Calculate risk adjustment based on human decisions"""
        if calibration.action_count < 10:
            return 0
        
        confirm_rate = calibration.confirm_count / calibration.action_count
        reject_rate = calibration.reject_count / calibration.action_count
        modify_rate = calibration.modify_count / calibration.action_count
        
        if confirm_rate > 0.8:
            adjustment = -3
        elif confirm_rate > 0.6 and modify_rate < 0.2:
            adjustment = -1
        elif reject_rate > 0.4:
            adjustment = 3
        elif modify_rate > 0.4:
            adjustment = 2
        else:
            adjustment = 0
        
        return max(-5, min(5, adjustment))