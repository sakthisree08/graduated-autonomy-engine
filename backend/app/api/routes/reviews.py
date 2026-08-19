"""
Reviews API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from datetime import datetime

from app.database import get_db
from app.services.db_service import DatabaseService
from app.core.action_executor import ActionExecutor
from app.schemas.action import ReviewRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/reviews", tags=["Reviews"])
action_executor = ActionExecutor()


@router.get("/pending")
async def get_pending_reviews(
    session: AsyncSession = Depends(get_db)
):
    """Get all pending reviews"""
    try:
        db_service = DatabaseService(session)
        reviews = await db_service.get_pending_reviews()
        
        result = []
        for review in reviews:
            action = await db_service.get_action(review.action_id)
            result.append({
                "review_id": review.id,
                "action_id": review.action_id,
                "action": action.to_dict() if action else None,
                "submitted_at": review.created_at.isoformat() if review.created_at else None,
            })
        
        return {"reviews": result}
    except Exception as e:
        logger.error(f"Error getting pending reviews: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{review_id}/approve")
async def approve_review(
    review_id: str,
    request: ReviewRequest,
    session: AsyncSession = Depends(get_db)
):
    """Approve a pending review"""
    try:
        db_service = DatabaseService(session)
        
        # Get review
        review = await db_service.get_review(review_id)
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        
        if review.review_status != "pending":
            raise HTTPException(status_code=400, detail="Review already processed")
        
        # Get action
        action = await db_service.get_action(review.action_id)
        if not action:
            raise HTTPException(status_code=404, detail="Action not found")
        
        # Prepare action dict for execution
        action_dict = {
            "operation": action.operation,
            "target_table": action.target_table,
            "condition": action.condition,
            "record_count": action.record_count,
            "parameters": action.parameters,
            "agent_id": action.agent_id,
        }
        
        # Execute the action
        result = await action_executor.execute(action_dict)
        
        # Update review - use datetime object, not string
        now = datetime.utcnow()
        await db_service.update_review(review_id, {
            "review_status": "approved",
            "reviewer": request.reviewer,
            "decision": "approve",
            "comment": request.comment,
            "reviewed_at": now,  # datetime object
        })
        
        # Update action
        await db_service.update_action_status(action.id, "executed", result)
        
        # Audit log
        await db_service.create_audit_log(
            action.id,
            "review_approved",
            f"Human reviewer {request.reviewer} approved the action: {result.get('message', 'Executed')}",
            {
                "reversibility": action.reversibility_score,
                "data_scope": action.data_scope_score,
                "regulatory": action.regulatory_score,
                "confidence": action.confidence_score,
            },
            {"reviewer": request.reviewer, "comment": request.comment, "result": result}
        )
        
        await session.commit()
        return {"status": "approved", "message": result.get("message", "Action executed successfully")}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving review: {str(e)}", exc_info=True)
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{review_id}/reject")
async def reject_review(
    review_id: str,
    request: ReviewRequest,
    session: AsyncSession = Depends(get_db)
):
    """Reject a pending review"""
    try:
        db_service = DatabaseService(session)
        
        review = await db_service.get_review(review_id)
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        
        if review.review_status != "pending":
            raise HTTPException(status_code=400, detail="Review already processed")
        
        # Get action
        action = await db_service.get_action(review.action_id)
        if not action:
            raise HTTPException(status_code=404, detail="Action not found")
        
        # Update review - use datetime object, not string
        now = datetime.utcnow()
        await db_service.update_review(review_id, {
            "review_status": "rejected",
            "reviewer": request.reviewer,
            "decision": "reject",
            "comment": request.comment,
            "reviewed_at": now,  # datetime object
        })
        
        # Update action
        await db_service.update_action_status(action.id, "rejected")
        
        # Audit log
        await db_service.create_audit_log(
            action.id,
            "review_rejected",
            f"Human reviewer {request.reviewer} rejected the action: {request.comment or 'No comment'}",
            {
                "reversibility": action.reversibility_score,
                "data_scope": action.data_scope_score,
                "regulatory": action.regulatory_score,
                "confidence": action.confidence_score,
            },
            {"reviewer": request.reviewer, "comment": request.comment}
        )
        
        await session.commit()
        return {"status": "rejected", "message": "Action rejected by human reviewer"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rejecting review: {str(e)}", exc_info=True)
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    from app.core.security import get_current_api_key, check_rate_limit

@router.get("/pending")
async def get_pending_reviews(
    session: AsyncSession = Depends(get_db),
    api_key: str = Depends(get_current_api_key)  # ← Add security
):
    # ... rest of code

@router.post("/{review_id}/approve")
async def approve_review(
    review_id: str,
    request: ReviewRequest,
    session: AsyncSession = Depends(get_db),
    api_key: str = Depends(check_rate_limit)  # ← Add security + rate limiting
):
    # ... rest of code

@router.post("/{review_id}/reject")
async def reject_review(
    review_id: str,
    request: ReviewRequest,
    session: AsyncSession = Depends(get_db),
    api_key: str = Depends(check_rate_limit)  # ← Add security + rate limiting
):
    # ... rest of code