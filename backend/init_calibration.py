"""
Initialize calibration table
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import engine, Base
from app.models.calibration import Calibration

async def init():
    """Create the calibration table"""
    print("🔄 Creating calibration table...")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Calibration table created successfully!")

if __name__ == "__main__":
    asyncio.run(init())