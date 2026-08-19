"""
Database configuration
"""

import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Use /tmp for Render (writable) or local directory
if os.environ.get("RENDER"):
    # On Render, use /tmp directory (writable)
    db_path = "/tmp/graduated_autonomy.db"
else:
    # Local development
    db_path = "./graduated_autonomy.db"

DATABASE_URL = f"sqlite+aiosqlite:///{db_path}"

engine = create_async_engine(
    DATABASE_URL,
    echo=True if os.environ.get("DEBUG", "False") == "True" else False,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()