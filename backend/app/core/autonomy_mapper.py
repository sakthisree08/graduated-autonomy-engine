"""
Autonomy Mapper - Maps risk scores to autonomy levels
"""

from enum import Enum
from typing import Dict, Any

class AutonomyLevel(str, Enum):
    """Autonomy levels for agent actions"""
    AUTONOMOUS = "AUTONOMOUS"
    CONFIRM = "CONFIRM" 
    REVIEW = "REVIEW"
    
class AutonomyMapper:
    """Maps risk scores to autonomy levels"""
    
    def __init__(self, low_threshold: int = 40, medium_threshold: int = 70):
        self.low_threshold = low_threshold      # ≤ 40 = AUTONOMOUS
        self.medium_threshold = medium_threshold  # ≤ 70 = CONFIRM
    
    def map_to_autonomy(self, total_risk: int) -> AutonomyLevel:
        """
        Map total risk score to autonomy level
        
        Rules:
        - 0-40: AUTONOMOUS (execute without human)
        - 41-70: CONFIRM (show preview, ask user)
        - 71-100: REVIEW (human review queue)
        """
        if total_risk <= self.low_threshold:
            return AutonomyLevel.AUTONOMOUS
        elif total_risk <= self.medium_threshold:
            return AutonomyLevel.CONFIRM
        else:
            return AutonomyLevel.REVIEW
    
    def get_action_requirements(self, level: AutonomyLevel) -> Dict[str, Any]:
        """
        Get requirements for each autonomy level
        """
        requirements = {
            AutonomyLevel.AUTONOMOUS: {
                "requires_confirmation": False,
                "requires_review": False,
                "message": "Action executed autonomously",
                "can_execute_immediately": True,
            },
            AutonomyLevel.CONFIRM: {
                "requires_confirmation": True,
                "requires_review": False,
                "message": "User confirmation required",
                "can_execute_immediately": False,
            },
            AutonomyLevel.REVIEW: {
                "requires_confirmation": False,
                "requires_review": True,
                "message": "Human review required",
                "can_execute_immediately": False,
            },
        }
        return requirements.get(level, requirements[AutonomyLevel.AUTONOMOUS])
    
    def get_risk_level_description(self, total_risk: int) -> str:
        """Get human-readable description of risk level"""
        if total_risk <= 30:
            return "Very low risk - completely safe to execute"
        elif total_risk <= 40:
            return "Low risk - safe to execute autonomously"
        elif total_risk <= 55:
            return "Medium-low risk - user confirmation recommended"
        elif total_risk <= 70:
            return "Medium risk - user confirmation required"
        elif total_risk <= 85:
            return "High risk - human review required"
        else:
            return "Very high risk - immediate human review required"