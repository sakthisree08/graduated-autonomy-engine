"""
Force calibration adjustment - Run once to set adjustment
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.database import AsyncSessionLocal
from app.services.calibration_service import CalibrationService

async def force_calibration():
    async with AsyncSessionLocal() as session:
        cal_service = CalibrationService(session)
        
        # Get or create calibration for "update"
        calibration = await cal_service._get_or_create("update")
        
        # Force set the adjustment
        calibration.action_count = 10
        calibration.confirm_count = 10
        calibration.risk_adjustment = -3
        calibration.status = "active"
        
        await session.commit()
        print("✅ Calibration adjustment set to -3 for 'update'")
        
        # Verify
        stats = await cal_service.get_stats("update")
        print(f"📊 Stats: {stats}")

if __name__ == "__main__":
    asyncio.run(force_calibration())