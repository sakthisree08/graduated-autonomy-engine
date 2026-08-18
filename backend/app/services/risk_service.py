"""
Risk Service - Main service for risk scoring and autonomy mapping
"""

from typing import Dict, Any, Tuple
from app.core.risk_scorer import RiskScorer
from app.core.autonomy_mapper import AutonomyMapper, AutonomyLevel

class RiskService:
    """Service for calculating risk and mapping to autonomy"""
    
    def __init__(self):
        self.scorer = RiskScorer()
        self.mapper = AutonomyMapper()
    
    def evaluate_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate an action and return risk score and autonomy decision
        """
        # Calculate risk breakdown
        breakdown = self.scorer.get_risk_breakdown(action)
        scores = breakdown["scores"]
        total_risk = breakdown["total_risk"]
        
        # Map to autonomy level
        level = self.mapper.map_to_autonomy(total_risk)
        requirements = self.mapper.get_action_requirements(level)
        description = self.mapper.get_risk_level_description(total_risk)
        
        # Build result
        result = {
            "total_risk": total_risk,
            "autonomy_level": level.value,
            "risk_breakdown": {
                "reversibility": scores["reversibility"],
                "data_scope": scores["data_scope"],
                "regulatory": scores["regulatory"],
                "confidence": scores["confidence"],
                "max_scores": breakdown["max_scores"],
            },
            "requirements": requirements,
            "description": description,
            "thresholds": {
                "autonomous_max": self.mapper.low_threshold,
                "confirm_max": self.mapper.medium_threshold,
            }
        }
        
        return result
    
    def get_human_readable_audit(self, action: Dict[str, Any], 
                                 evaluation: Dict[str, Any]) -> str:
        """
        Generate human-readable audit log entry
        """
        scores = evaluation["risk_breakdown"]
        total = evaluation["total_risk"]
        level = evaluation["autonomy_level"]
        
        audit_text = f"""
Action: {action.get('operation', 'unknown').upper()} 
  Target: {action.get('target_table', 'unknown')}
  Records: {action.get('record_count', 0)}

Risk Breakdown:
  Reversibility: {scores['reversibility']}/30
  Data Scope:    {scores['data_scope']}/25  
  Regulatory:    {scores['regulatory']}/20
  Confidence:    {scores['confidence']}/25
  ─────────────────
  Total Risk:    {total}/100

Decision: {level}
Reason: {evaluation['description']}
"""
        return audit_text