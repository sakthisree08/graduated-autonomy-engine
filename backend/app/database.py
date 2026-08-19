"""
Database configuration and session management
"""

import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import MetaData

# Create base class for models
Base = declarative_base()

# Determine database path
if os.environ.get("RENDER"):
    # On Render, use /tmp directory (writable)
    db_path = "/tmp/graduated_autonomy.db"
else:
    # Local development
    db_path = "./graduated_autonomy.db"

DATABASE_URL = f"sqlite+aiosqlite:///{db_path}"

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Dependency to get database session
async def get_db() -> AsyncSession:
    """Get database session for dependency injection"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()