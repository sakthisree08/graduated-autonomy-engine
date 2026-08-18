"""
Action schemas for API validation
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class ActionRequest(BaseModel):
    """Request to evaluate an action"""
    agent_id: str = Field(..., description="ID of the agent")
    operation: str = Field(..., description="Operation to perform")
    target_table: Optional[str] = Field(None, description="Target table or resource")
    condition: Optional[str] = Field(None, description="Query condition")
    record_count: int = Field(0, description="Number of records affected")
    data_category: str = Field("general", description="Category of data")
    llm_confidence: float = Field(0.5, ge=0.0, le=1.0, description="LLM confidence score")
    validation_score: float = Field(0.5, ge=0.0, le=1.0, description="System validation score")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Additional parameters")
    
    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "agent-001",
                "operation": "read",
                "target_table": "customers",
                "condition": "id = 10",
                "record_count": 1,
                "data_category": "customer",
                "llm_confidence": 0.9,
                "validation_score": 0.9
            }
        }

class ActionResponse(BaseModel):
    """Response after evaluating an action"""
    action_id: str
    total_risk: int
    autonomy_level: str
    risk_breakdown: Dict[str, Any]
    status: str
    message: str
    requires_confirmation: bool = False
    requires_review: bool = False
    preview_data: Optional[Dict[str, Any]] = None
    review_id: Optional[str] = None

class ConfirmRequest(BaseModel):
    """Request to confirm an action"""
    confirm: bool = Field(..., description="True to confirm, False to reject")
    comment: Optional[str] = Field(None, description="Optional comment")

class ReviewRequest(BaseModel):
    """Request to review an action"""
    decision: str = Field(..., description="approve or reject")
    comment: Optional[str] = Field(None, description="Reviewer comment")
    reviewer: str = Field(..., description="Reviewer ID")
"""
Action schemas for API validation
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class ActionRequest(BaseModel):
    """Request to evaluate an action"""
    agent_id: str = Field(..., description="ID of the agent")
    operation: str = Field(..., description="Operation to perform")
    target_table: Optional[str] = Field(None, description="Target table or resource")
    condition: Optional[str] = Field(None, description="Query condition")
    record_count: int = Field(0, description="Number of records affected")
    data_category: str = Field("general", description="Category of data")
    llm_confidence: float = Field(0.5, ge=0.0, le=1.0, description="LLM confidence score")
    validation_score: float = Field(0.5, ge=0.0, le=1.0, description="System validation score")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Additional parameters")
    
    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "agent-001",
                "operation": "update",
                "target_table": "customers",
                "condition": "id = 10",
                "record_count": 1,
                "data_category": "customer",
                "llm_confidence": 0.8,
                "validation_score": 0.8,
                "parameters": {"set": {"email": "new@email.com"}}
            }
        }

class ActionResponse(BaseModel):
    """Response after evaluating an action"""
    action_id: str
    total_risk: int
    autonomy_level: str
    risk_breakdown: Dict[str, Any]
    status: str
    message: str
    requires_confirmation: bool = False
    requires_review: bool = False
    preview_data: Optional[Dict[str, Any]] = None
    review_id: Optional[str] = None

class ConfirmRequest(BaseModel):
    """Request to confirm an action"""
    confirm: bool = Field(..., description="True to confirm, False to reject")
    comment: Optional[str] = Field(None, description="Optional comment")
    user_id: Optional[str] = Field(None, description="User ID who is confirming")

class ReviewRequest(BaseModel):
    """Request to review an action"""
    decision: str = Field(..., description="approve or reject")
    comment: Optional[str] = Field(None, description="Reviewer comment")
    reviewer: str = Field(..., description="Reviewer ID")