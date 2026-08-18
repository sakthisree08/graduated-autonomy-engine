"""
Action model - Stores agent actions with risk scores
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, JSON, DateTime
from sqlalchemy.orm import relationship
import uuid

from app.database import Base

class Action(Base):
    __tablename__ = "actions"
    
    # Use String for SQLite compatibility
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String(100), nullable=False, index=True)
    operation = Column(String(50), nullable=False)
    target_table = Column(String(100), nullable=True)
    condition = Column(String(500), nullable=True)
    record_count = Column(Integer, default=0)
    data_category = Column(String(50), nullable=True)
    parameters = Column(JSON, nullable=True)
    
    # Confidence scores
    llm_confidence = Column(Float, default=0.5)
    validation_score = Column(Float, default=0.5)
    
    # Risk scores
    reversibility_score = Column(Integer, default=0)
    data_scope_score = Column(Integer, default=0)
    regulatory_score = Column(Integer, default=0)
    confidence_score = Column(Integer, default=0)
    total_risk = Column(Integer, default=0)
    autonomy_level = Column(String(20), default="PENDING")
    
    # Status
    status = Column(String(20), default="pending")
    execution_status = Column(String(20), nullable=True)
    execution_result = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    review = relationship("Review", back_populates="action", uselist=False)
    audit_logs = relationship("AuditLog", back_populates="action")
    
    def to_dict(self):
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "operation": self.operation,
            "target_table": self.target_table,
            "condition": self.condition,
            "record_count": self.record_count,
            "data_category": self.data_category,
            "parameters": self.parameters,
            "llm_confidence": self.llm_confidence,
            "validation_score": self.validation_score,
            "reversibility_score": self.reversibility_score,
            "data_scope_score": self.data_scope_score,
            "regulatory_score": self.regulatory_score,
            "confidence_score": self.confidence_score,
            "total_risk": self.total_risk,
            "autonomy_level": self.autonomy_level,
            "status": self.status,
            "execution_status": self.execution_status,
            "execution_result": self.execution_result,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }