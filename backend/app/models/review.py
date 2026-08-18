"""
Review model - Human review queue for high-risk actions
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
import uuid

from app.database import Base

class Review(Base):
    __tablename__ = "reviews"
    
    # Use String for SQLite compatibility
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    action_id = Column(String(36), ForeignKey("actions.id"), nullable=False)
    
    reviewer = Column(String(100), nullable=True)
    review_status = Column(String(20), default="pending")
    decision = Column(String(20), nullable=True)
    comment = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)
    assigned_at = Column(DateTime, nullable=True)
    sla_deadline = Column(DateTime, nullable=True)
    escalation_level = Column(Integer, default=0)
    
    # Relationships
    action = relationship("Action", back_populates="review")
    
    def to_dict(self):
        return {
            "id": self.id,
            "action_id": self.action_id,
            "reviewer": self.reviewer,
            "review_status": self.review_status,
            "decision": self.decision,
            "comment": self.comment,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "assigned_at": self.assigned_at.isoformat() if self.assigned_at else None,
            "sla_deadline": self.sla_deadline.isoformat() if self.sla_deadline else None,
            "escalation_level": self.escalation_level,
        }