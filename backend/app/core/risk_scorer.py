"""
Risk Scorer - Calculates risk across 4 dimensions
"""

from typing import Dict, Any, Optional

class RiskScorer:
    """Calculates risk scores for agent actions"""
    
    def __init__(self):
        # Maximum scores for each dimension
        self.max_scores = {
            "reversibility": 30,
            "data_scope": 25,
            "regulatory": 20,
            "confidence": 25,
        }
    
    def calculate_reversibility(self, operation: str) -> int:
        """
        Score reversibility of an operation (0-30)
        Higher score = harder to reverse
        """
        # No state change (perfectly reversible)
        if operation in ["read", "list", "search", "get", "query"]:
            return 2
        
        # Easy to reverse
        if operation in ["create", "insert", "add"]:
            return 8
        
        # Medium difficulty
        if operation in ["update", "modify", "edit", "change"]:
            return 15
        
        # Hard to reverse
        if operation in ["delete", "remove", "archive"]:
            return 25
        
        # Very hard to reverse
        if operation in ["bulk_delete", "drop", "truncate", "purge"]:
            return 30
        
        # Default for unknown operations
        return 15
    
    def calculate_data_scope(self, record_count: int) -> int:
        """
        Score data scope based on number of records affected (0-25)
        Higher score = more data affected
        """
        if record_count <= 0:
            return 0
        elif record_count == 1:
            return 2
        elif record_count <= 10:
            return 5
        elif record_count <= 100:
            return 10
        elif record_count <= 1000:
            return 15
        elif record_count <= 10000:
            return 20
        else:
            return 25
    
    def calculate_regulatory(self, data_category: str) -> int:
        """
        Score regulatory sensitivity (0-20)
        Higher score = more regulated
        """
        categories = {
            # No regulatory concern
            "public": 2,
            "anonymous": 2,
            "metadata": 3,
            
            # Low concern
            "internal": 5,
            "business": 5,
            "general": 5,
            
            # Medium concern
            "customer": 10,
            "employee": 10,
            "financial": 12,
            "payment": 12,
            
            # High concern
            "pii": 15,      # Personally Identifiable Information
            "personal": 15,
            "phi": 18,      # Protected Health Information
            "gdpr": 18,     # GDPR regulated data
            "hipaa": 20,    # HIPAA regulated data
            "classified": 20,
            "sensitive": 20,
        }
        
        # Return the score, default to medium (10) if unknown
        return categories.get(data_category.lower(), 10)
    
    def calculate_confidence(self, action: Dict[str, Any]) -> int:
        """
        Calculate confidence score (0-25)
        Higher score = more confident
        
        Combines:
        1. LLM confidence (if available)
        2. Our validation score
        3. Parameter completeness
        """
        # Get LLM confidence (0.0 to 1.0)
        llm_conf = action.get("llm_confidence", 0.5)
        if not isinstance(llm_conf, (int, float)):
            llm_conf = 0.5
        
        # Get our validation score (0.0 to 1.0)
        validation = action.get("validation_score", 0.5)
        if not isinstance(validation, (int, float)):
            validation = 0.5
        
        # Combine: average of LLM confidence and validation
        combined = (llm_conf + validation) / 2
        
        # Clamp to 0-1 range
        combined = max(0.0, min(1.0, combined))
        
        # Map to 0-25 scale
        return int(combined * 25)
    
    def calculate_total_risk(self, scores: Dict[str, int]) -> int:
        """
        Calculate total risk score (0-100)
        
        Formula:
        Total = reversibility + data_scope + regulatory + (25 - confidence)
        """
        reversibility = scores.get("reversibility", 0)
        data_scope = scores.get("data_scope", 0)
        regulatory = scores.get("regulatory", 0)
        confidence = scores.get("confidence", 0)
        
        # Higher confidence REDUCES total risk
        confidence_penalty = 25 - confidence
        
        total = reversibility + data_scope + regulatory + confidence_penalty
        
        # Clamp to 0-100 range
        return max(0, min(100, total))
    
    def get_risk_breakdown(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get complete risk breakdown for an action
        """
        operation = action.get("operation", "unknown")
        record_count = action.get("record_count", 0)
        data_category = action.get("data_category", "unknown")
        
        # Calculate individual scores
        reversibility = self.calculate_reversibility(operation)
        data_scope = self.calculate_data_scope(record_count)
        regulatory = self.calculate_regulatory(data_category)
        confidence = self.calculate_confidence(action)
        
        scores = {
            "reversibility": reversibility,
            "data_scope": data_scope,
            "regulatory": regulatory,
            "confidence": confidence,
        }
        
        total_risk = self.calculate_total_risk(scores)
        
        return {
            "scores": scores,
            "total_risk": total_risk,
            "max_scores": self.max_scores,
        }