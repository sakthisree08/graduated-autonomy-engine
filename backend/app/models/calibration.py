"""
Calibration model - Tracks user decisions and adjusts risk thresholds
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, JSON
from app.database import Base

class Calibration(Base):
    __tablename__ = "calibration"
    
    id = Column(String(36), primary_key=True)
    operation = Column(String(50), nullable=False, unique=True)
    action_count = Column(Integer, default=0)
    confirm_count = Column(Integer, default=0)
    reject_count = Column(Integer, default=0)
    modify_count = Column(Integer, default=0)
    risk_adjustment = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow)
    history = Column(JSON, default=list)
    
    def to_dict(self):
        return {
            "id": self.id,
            "operation": self.operation,
            "action_count": self.action_count,
            "confirm_count": self.confirm_count,
            "reject_count": self.reject_count,
            "modify_count": self.modify_count,
            "risk_adjustment": self.risk_adjustment,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "history": self.history,
        }