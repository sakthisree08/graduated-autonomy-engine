"""
Actions API endpoints
"""

import uuid
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Security
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.database import get_db
from app.schemas.action import ActionRequest, ActionResponse, ConfirmRequest
from app.services.risk_service import RiskService
from app.services.db_service import DatabaseService
from app.services.confirmation_service import ConfirmationService
from app.core.action_executor import ActionExecutor
from app.core.security import get_current_api_key, check_rate_limit

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/actions", tags=["Actions"])
risk_service = RiskService()
action_executor = ActionExecutor()


@router.post("/evaluate", response_model=ActionResponse)
async def evaluate_action(
    request: ActionRequest,
    session: AsyncSession = Depends(get_db),
    api_key: str = Depends(check_rate_limit)  # ← Add security + rate limiting
):
    """
    Evaluate an agent action and determine autonomy level.
    Requires valid API key in X-API-Key header.
    """
    db_service = DatabaseService(session)
    
    try:
        # 1. Create action record
        action = await db_service.create_action(request.model_dump())
        
        # 2. Evaluate risk
        action_dict = request.model_dump()
        evaluation = risk_service.evaluate_action(action_dict)
        
        # 3. Update action with risk scores
        await db_service.update_action_risk(
            action.id,
            {
                "reversibility": evaluation["risk_breakdown"]["reversibility"],
                "data_scope": evaluation["risk_breakdown"]["data_scope"],
                "regulatory": evaluation["risk_breakdown"]["regulatory"],
                "confidence": evaluation["risk_breakdown"]["confidence"],
                "total_risk": evaluation["total_risk"],
                "autonomy_level": evaluation["autonomy_level"],
            }
        )
        
        # 4. Create audit log
        audit_summary = risk_service.get_human_readable_audit(action_dict, evaluation)
        await db_service.create_audit_log(
            action.id,
            "action_evaluated",
            audit_summary,
            evaluation["risk_breakdown"],
            {"action": action_dict}
        )
        
        # 5. Handle based on autonomy level
        response = ActionResponse(
            action_id=action.id,
            total_risk=evaluation["total_risk"],
            autonomy_level=evaluation["autonomy_level"],
            risk_breakdown=evaluation["risk_breakdown"],
            status="pending",
            message=evaluation["description"],
            requires_confirmation=evaluation["requirements"]["requires_confirmation"],
            requires_review=evaluation["requirements"]["requires_review"],
            preview_data=None,
            review_id=None,
        )
        
        if evaluation["autonomy_level"] == "AUTONOMOUS":
            # Execute immediately
            result = await action_executor.execute(action_dict)
            await db_service.update_action_status(action.id, "executed", result)
            response.status = "executed"
            response.message = f"Action executed autonomously: {result['message']}"
            
            await db_service.create_audit_log(
                action.id,
                "action_executed",
                f"Autonomous execution: {result['message']}",
                event_data={"result": result}
            )
            
        elif evaluation["autonomy_level"] == "CONFIRM":
            # Wait for confirmation
            response.status = "waiting_confirmation"
            response.preview_data = {
                "operation": action_dict.get("operation"),
                "target": action_dict.get("target_table"),
                "parameters": action_dict.get("parameters"),
                "record_count": action_dict.get("record_count"),
            }
            
        else:  # REVIEW
            # Create review record
            review = await db_service.create_review(action.id, action_dict)
            response.review_id = review.id
            response.status = "queued_for_review"
        
        await session.commit()
        return response
        
    except Exception as e:
        logger.error(f"Error evaluating action: {str(e)}", exc_info=True)
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{action_id}/confirm")
async def confirm_action(
    action_id: str,
    request: ConfirmRequest,
    session: AsyncSession = Depends(get_db),
    api_key: str = Depends(check_rate_limit)  # ← Add security + rate limiting
):
    """
    Confirm or reject an action (for medium-risk actions).
    Requires valid API key in X-API-Key header.
    """
    db_service = DatabaseService(session)
    confirmation_service = ConfirmationService(db_service)
    
    try:
        result = await confirmation_service.process_confirmation(
            action_id=action_id,
            confirm=request.confirm,
            user_id=request.user_id or "unknown",
            comment=request.comment
        )
        
        if result.get("error"):
            raise HTTPException(status_code=400, detail=result["error"])
        
        await session.commit()
        return result
        
    except Exception as e:
        logger.error(f"Error confirming action: {str(e)}", exc_info=True)
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/pending-confirmations")
async def get_pending_confirmations(
    agent_id: Optional[str] = None,
    session: AsyncSession = Depends(get_db),
    api_key: str = Depends(get_current_api_key)  # ← Add security (no rate limit for GET)
):
    """
    Get all actions waiting for confirmation.
    Requires valid API key in X-API-Key header.
    """
    try:
        db_service = DatabaseService(session)
        confirmation_service = ConfirmationService(db_service)
        
        pending = await confirmation_service.get_pending_confirmations(agent_id)
        
        return {
            "total": len(pending),
            "confirmations": pending
        }
    except Exception as e:
        logger.error(f"Error getting pending confirmations: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{action_id}/preview")
async def get_action_preview(
    action_id: str,
    session: AsyncSession = Depends(get_db),
    api_key: str = Depends(get_current_api_key)  # ← Add security
):
    """
    Get a preview of an action waiting for confirmation.
    Requires valid API key in X-API-Key header.
    """
    try:
        db_service = DatabaseService(session)
        confirmation_service = ConfirmationService(db_service)
        
        preview = await confirmation_service.get_confirmation_preview(action_id)
        
        if not preview:
            raise HTTPException(
                status_code=404, 
                detail="Action not found or not waiting for confirmation"
            )
        
        return preview
    except Exception as e:
        logger.error(f"Error getting action preview: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )