"""
Confirmation Service - Handles medium-risk action confirmations
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from app.services.calibration_service import CalibrationService
from app.core.action_executor import ActionExecutor
from app.services.db_service import DatabaseService

logger = logging.getLogger(__name__)

class ConfirmationService:
    """Service for handling action confirmations"""
    
    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service
        self.action_executor = ActionExecutor()
    
    async def get_pending_confirmations(self, agent_id: Optional[str] = None) -> list:
        """Get all actions waiting for confirmation"""
        actions = await self.db_service.get_pending_confirmations(agent_id)
        return [action.to_dict() for action in actions]
    
    async def process_confirmation(self, action_id: str, confirm: bool, 
                                   user_id: str, comment: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a confirmation decision
        
        Args:
            action_id: ID of the action
            confirm: True to confirm, False to reject
            user_id: ID of the user confirming
            comment: Optional comment
        
        Returns:
            Dict with status and message
        """
        # Get action
        action = await self.db_service.get_action(action_id)
        if not action:
            return {"error": "Action not found", "status": "error"}
        
        # Check if action is waiting for confirmation
        if action.status != "waiting_confirmation":
            return {
                "error": f"Action is not waiting for confirmation (current status: {action.status})",
                "status": "error"
            }
        
        # Check if autonomy level is CONFIRM
        if action.autonomy_level != "CONFIRM":
            return {
                "error": f"Action requires {action.autonomy_level}, not CONFIRM",
                "status": "error"
            }
        
        # Initialize calibration service
        cal_service = CalibrationService(self.db_service.session)
        
        if confirm:
            # User confirmed - execute the action
            action_dict = {
                "operation": action.operation,
                "target_table": action.target_table,
                "condition": action.condition,
                "record_count": action.record_count,
                "parameters": action.parameters,
                "agent_id": action.agent_id,
            }
            
            # Execute
            result = await self.action_executor.execute(action_dict)
            
            # Update action status
            await self.db_service.update_action_status(action.id, "executed", result)
            
            # Create audit log
            await self.db_service.create_audit_log(
                action.id,
                "action_confirmed",
                f"User {user_id} confirmed and executed: {result['message']}",
                risk_breakdown={
                    "reversibility": action.reversibility_score,
                    "data_scope": action.data_scope_score,
                    "regulatory": action.regulatory_score,
                    "confidence": action.confidence_score,
                },
                event_data={
                    "user_id": user_id,
                    "comment": comment,
                    "result": result
                }
            )
            
            # ✅ Record decision for calibration (BEFORE commit)
            await cal_service.record_decision(action.operation, "confirm")
            
            await self.db_service.session.commit()
            
            return {
                "status": "executed",
                "message": result["message"],
                "confirmed_by": user_id,
                "confirmed_at": datetime.utcnow().isoformat()
            }
        else:
            # User rejected
            await self.db_service.update_action_status(action.id, "rejected")
            
            # Create audit log
            await self.db_service.create_audit_log(
                action.id,
                "action_confirmation_rejected",
                f"User {user_id} rejected the action: {comment or 'No comment'}",
                risk_breakdown={
                    "reversibility": action.reversibility_score,
                    "data_scope": action.data_scope_score,
                    "regulatory": action.regulatory_score,
                    "confidence": action.confidence_score,
                },
                event_data={
                    "user_id": user_id,
                    "comment": comment
                }
            )
            
            # ✅ Record decision for calibration (BEFORE commit)
            await cal_service.record_decision(action.operation, "reject")
            
            await self.db_service.session.commit()
            
            return {
                "status": "rejected",
                "message": "Action rejected by user",
                "rejected_by": user_id,
                "rejected_at": datetime.utcnow().isoformat()
            }
    
    async def get_confirmation_preview(self, action_id: str) -> Optional[Dict[str, Any]]:
        """Get a preview of an action waiting for confirmation"""
        action = await self.db_service.get_action(action_id)
        if not action:
            return None
        
        if action.status != "waiting_confirmation":
            return None
        
        return {
            "action_id": action.id,
            "agent_id": action.agent_id,
            "operation": action.operation,
            "target_table": action.target_table,
            "condition": action.condition,
            "record_count": action.record_count,
            "parameters": action.parameters,
            "total_risk": action.total_risk,
            "risk_breakdown": {
                "reversibility": action.reversibility_score,
                "data_scope": action.data_scope_score,
                "regulatory": action.regulatory_score,
                "confidence": action.confidence_score,
            },
            "created_at": action.created_at.isoformat() if action.created_at else None,
            "preview_summary": self._generate_preview_summary(action)
        }
    
    def _generate_preview_summary(self, action) -> str:
        """Generate a human-readable preview summary"""
        return f"""
Action: {action.operation.upper()}
Target: {action.target_table or 'N/A'}
Condition: {action.condition or 'N/A'}
Records Affected: {action.record_count or 0}
Risk Score: {action.total_risk}/100
Risk Level: {action.autonomy_level}

Details:
- Reversibility: {action.reversibility_score}/30
- Data Scope: {action.data_scope_score}/25
- Regulatory: {action.regulatory_score}/20
- Confidence: {action.confidence_score}/25
"""