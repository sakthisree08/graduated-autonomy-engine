"""
Security module - API Key authentication and rate limiting
"""

import os
import time
import secrets
from typing import Optional
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# API Key header
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# In-memory API key store (in production, use database)
API_KEYS = {
    "dev-key-123": {"name": "Development Key", "created_at": time.time(), "active": True},
    "test-key-456": {"name": "Test Key", "created_at": time.time(), "active": True},
}


def generate_api_key() -> str:
    """Generate a new API key"""
    return secrets.token_urlsafe(32)


def create_api_key(name: str) -> dict:
    """Create a new API key"""
    key = generate_api_key()
    API_KEYS[key] = {
        "name": name,
        "created_at": time.time(),
        "active": True,
    }
    return {"api_key": key, "name": name}


def verify_api_key(api_key: str) -> bool:
    """Verify if API key is valid and active"""
    if api_key not in API_KEYS:
        return False
    return API_KEYS[api_key].get("active", False)


async def get_current_api_key(api_key: str = Security(api_key_header)):
    """Dependency to validate API key"""
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required. Please provide X-API-Key header",
        )
    
    if not verify_api_key(api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API key",
        )
    
    return api_key


# Optional: Rate limiting (simple version)
# In production, use Redis for distributed rate limiting
class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        self.requests = {}
        self.limit = 100  # requests per window
        self.window = 60  # seconds
    
    async def check_limit(self, api_key: str) -> bool:
        """Check if rate limit is exceeded"""
        now = time.time()
        key = f"rate:{api_key}"
        
        if key not in self.requests:
            self.requests[key] = []
        
        # Clean old requests
        self.requests[key] = [
            t for t in self.requests[key] if now - t < self.window
        ]
        
        if len(self.requests[key]) >= self.limit:
            return False
        
        self.requests[key].append(now)
        return True

rate_limiter = RateLimiter()


async def check_rate_limit(api_key: str = Security(get_current_api_key)):
    """Dependency to check rate limit"""
    if not await rate_limiter.check_limit(api_key):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Max {rate_limiter.limit} requests per {rate_limiter.window} seconds",
        )
    return api_key