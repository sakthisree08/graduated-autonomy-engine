"""
Database service for storing actions and reviews
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.models.action import Action
from app.models.review import Review
from app.models.audit import AuditLog

class DatabaseService:
    """Service for database operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_action(self, action_data: Dict[str, Any]) -> Action:
        """Create a new action record"""
        action = Action(
            id=str(uuid.uuid4()),
            agent_id=action_data.get("agent_id"),
            operation=action_data.get("operation"),
            target_table=action_data.get("target_table"),
            condition=action_data.get("condition"),
            record_count=action_data.get("record_count", 0),
            data_category=action_data.get("data_category", "general"),
            parameters=action_data.get("parameters"),
            llm_confidence=action_data.get("llm_confidence", 0.5),
            validation_score=action_data.get("validation_score", 0.5),
        )
        
        self.session.add(action)
        await self.session.flush()
        return action
    
    async def update_action_risk(self, action_id: str, risk_data: Dict[str, Any]):
        """Update action with risk scores"""
        action = await self.get_action(action_id)
        if action:
            action.reversibility_score = risk_data.get("reversibility", 0)
            action.data_scope_score = risk_data.get("data_scope", 0)
            action.regulatory_score = risk_data.get("regulatory", 0)
            action.confidence_score = risk_data.get("confidence", 0)
            action.total_risk = risk_data.get("total_risk", 0)
            action.autonomy_level = risk_data.get("autonomy_level", "PENDING")
            
            await self.session.flush()
    
    async def update_action_status(self, action_id: str, status: str, 
                                   execution_result: Optional[Dict] = None):
        """Update action status"""
        action = await self.get_action(action_id)
        if action:
            action.status = status
            if execution_result:
                action.execution_result = execution_result
                action.execution_status = "executed"
            await self.session.flush()
    
    async def get_action(self, action_id: str) -> Optional[Action]:
        """Get action by ID"""
        result = await self.session.execute(
            select(Action).where(Action.id == action_id)
        )
        return result.scalar_one_or_none()
    
    async def create_review(self, action_id: str, action_data: Dict[str, Any]) -> Review:
        """Create a review record"""
        review = Review(
            id=str(uuid.uuid4()),
            action_id=action_id,
            review_status="pending",
            created_at=datetime.utcnow(),
        )
        
        self.session.add(review)
        await self.session.flush()
        return review
    
    async def update_review(self, review_id: str, data: Dict[str, Any]):
        """Update review record"""
        review = await self.get_review(review_id)
        if review:
            for key, value in data.items():
                if hasattr(review, key):
                    setattr(review, key, value)
            await self.session.flush()
    
    async def get_review(self, review_id: str) -> Optional[Review]:
        """Get review by ID"""
        result = await self.session.execute(
            select(Review).where(Review.id == review_id)
        )
        return result.scalar_one_or_none()
    
    async def create_audit_log(self, action_id: str, event_type: str,
                               summary: str, risk_breakdown: Optional[Dict] = None,
                               event_data: Optional[Dict] = None):
        """Create an audit log entry"""
        audit = AuditLog(
            id=str(uuid.uuid4()),
            action_id=action_id,
            event_type=event_type,
            summary=summary,
            risk_breakdown=risk_breakdown,
            event_data=event_data,
            timestamp=datetime.utcnow(),
        )
        
        self.session.add(audit)
        await self.session.flush()
    
    async def get_audit_logs(self, limit: int = 100, offset: int = 0) -> List[AuditLog]:
        """Get audit logs"""
        result = await self.session.execute(
            select(AuditLog)
            .order_by(desc(AuditLog.timestamp))
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()
    
    async def get_pending_reviews(self) -> List[Review]:
        """Get all pending reviews"""
        result = await self.session.execute(
            select(Review).where(Review.review_status == "pending")
        )
        return result.scalars().all()
    
    async def get_pending_confirmations(self, agent_id: Optional[str] = None) -> List[Action]:
        """Get all actions waiting for confirmation"""
        query = select(Action).where(Action.status == "waiting_confirmation")
        if agent_id:
            query = query.where(Action.agent_id == agent_id)
        result = await self.session.execute(query.order_by(desc(Action.created_at)))
        return result.scalars().all()
    
    async def get_action_with_details(self, action_id: str) -> Optional[Dict]:
        """Get action with review details"""
        action = await self.get_action(action_id)
        if not action:
            return None
        
        result = action.to_dict()
        
        # Get review if exists
        if action.autonomy_level == "REVIEW":
            review = await self.get_review_by_action(action_id)
            if review:
                result["review"] = review.to_dict()
        
        return result
    
    async def get_review_by_action(self, action_id: str) -> Optional[Review]:
        """Get review by action ID"""
        result = await self.session.execute(
            select(Review).where(Review.action_id == action_id)
        )
        return result.scalar_one_or_none()