"""
Audit Log model - Complete audit trail for all actions
"""

from datetime import datetime
from sqlalchemy import Column, String, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
import uuid

from app.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    # Use String for SQLite compatibility
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    action_id = Column(String(36), ForeignKey("actions.id"), nullable=False)
    
    event_type = Column(String(50), nullable=False)
    event_data = Column(JSON, nullable=True)
    summary = Column(Text, nullable=True)
    risk_breakdown = Column(JSON, nullable=True)
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    action = relationship("Action", back_populates="audit_logs")
    
    def to_dict(self):
        return {
            "id": self.id,
            "action_id": self.action_id,
            "event_type": self.event_type,
            "event_data": self.event_data,
            "summary": self.summary,
            "risk_breakdown": self.risk_breakdown,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }