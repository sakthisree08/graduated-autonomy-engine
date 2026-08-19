"""
API Key management routes
"""

from fastapi import APIRouter, HTTPException, Security, status
from pydantic import BaseModel
from app.core.security import create_api_key, API_KEYS, get_current_api_key

router = APIRouter(prefix="/api/v1/keys", tags=["API Keys"])


class KeyCreateRequest(BaseModel):
    name: str


class KeyCreateResponse(BaseModel):
    api_key: str
    name: str
    message: str


@router.post("/create", response_model=KeyCreateResponse)
async def create_new_key(request: KeyCreateRequest):
    """Create a new API key"""
    result = create_api_key(request.name)
    return {
        "api_key": result["api_key"],
        "name": result["name"],
        "message": "API key created successfully. Save this key - it won't be shown again!"
    }


@router.get("/list")
async def list_keys():
    """List all API keys"""
    keys = []
    for key, info in API_KEYS.items():
        keys.append({
            "key": key[:8] + "..." + key[-8:],  # Show only partial key
            "name": info.get("name", "Unnamed"),
            "created_at": info.get("created_at"),
            "active": info.get("active", True),
        })
    return {"keys": keys}


@router.post("/revoke/{api_key}")
async def revoke_key(api_key: str):
    """Revoke an API key"""
    if api_key not in API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    API_KEYS[api_key]["active"] = False
    return {"message": "API key revoked successfully"}