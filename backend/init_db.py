"""
Initialize database - Create all tables directly
"""

import asyncio
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from app.database import engine, Base
from app.models import Action, Review, AuditLog

async def init_database():
    """Create all tables"""
    print("🔄 Creating database tables...")
    
    async with engine.begin() as conn:
        # This will create all tables defined in Base.metadata
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Database tables created successfully!")
    print("📊 Tables created:")
    print("  - actions")
    print("  - reviews")
    print("  - audit_logs")

async def verify_tables():
    """Verify tables were created"""
    from sqlalchemy import text
    from app.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("SELECT name FROM sqlite_master WHERE type='table'")
        )
        tables = [row[0] for row in result.fetchall()]
        print(f"📋 Tables in database: {tables}")

async def main():
    await init_database()
    await verify_tables()

if __name__ == "__main__":
    asyncio.run(main())