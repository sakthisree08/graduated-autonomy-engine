"""
Agent API endpoints - Natural language interface
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import logging

from app.database import get_db
from app.services.agent_service import AgentService
from app.services.db_service import DatabaseService
from app.core.action_executor import ActionExecutor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/agent", tags=["Agent"])


class AgentRequest(BaseModel):
    """Natural language agent request"""
    prompt: str
    agent_id: str = "agent-001"
    provider: str = "mock"  # mock, groq, ollama


class AgentResponse(BaseModel):
    """Agent response"""
    prompt: str
    action: dict
    risk_score: int
    autonomy_level: str
    status: str
    message: str
    requires_confirmation: bool
    requires_review: bool
    action_id: str = None
    review_id: str = None


@router.post("/chat", response_model=AgentResponse)
async def chat_with_agent(
    request: AgentRequest,
    session: AsyncSession = Depends(get_db)
):
    """
    Chat with an AI agent via natural language.
    The agent generates an action, which is then governed by the risk engine.
    """
    try:
        db_service = DatabaseService(session)
        agent_service = AgentService(db_service)
        action_executor = ActionExecutor()
        
        # Use mock provider by default (no API key needed)
        # If user wants a different provider, use the one from request
        provider = request.provider if request.provider != "mock" else "mock"
        
        # Process the request
        result = await agent_service.process_request(
            prompt=request.prompt,
            agent_id=request.agent_id
        )
        
        evaluation = result["risk_evaluation"]
        action = result["generated_action"]
        
        # Create the action in database
        action_record = await db_service.create_action(action)
        
        # Update with risk scores
        await db_service.update_action_risk(
            action_record.id,
            {
                "reversibility": evaluation["risk_breakdown"]["reversibility"],
                "data_scope": evaluation["risk_breakdown"]["data_scope"],
                "regulatory": evaluation["risk_breakdown"]["regulatory"],
                "confidence": evaluation["risk_breakdown"]["confidence"],
                "total_risk": evaluation["total_risk"],
                "autonomy_level": evaluation["autonomy_level"],
            }
        )
        
        # Create audit log for evaluation
        audit_summary = agent_service.risk_service.get_human_readable_audit(action, evaluation)
        await db_service.create_audit_log(
            action_record.id,
            "action_evaluated",
            audit_summary,
            evaluation["risk_breakdown"],
            {"action": action, "prompt": request.prompt}
        )
        
        # Handle based on autonomy level
        action_id = action_record.id
        review_id = None
        status = "processed"
        
        if evaluation["autonomy_level"] == "AUTONOMOUS":
            # Execute immediately
            result = await action_executor.execute(action)
            await db_service.update_action_status(action_id, "executed", result)
            status = "executed"
            
            await db_service.create_audit_log(
                action_id,
                "action_executed",
                f"Autonomous execution: {result['message']}",
                event_data={"result": result}
            )
            
        elif evaluation["autonomy_level"] == "CONFIRM":
            # Wait for confirmation
            await db_service.update_action_status(action_id, "waiting_confirmation")
            status = "waiting_confirmation"
            
        else:  # REVIEW
            # Create review record
            review = await db_service.create_review(action_id, action)
            review_id = review.id
            await db_service.update_action_status(action_id, "queued_for_review")
            status = "queued_for_review"
            
            await db_service.create_audit_log(
                action_id,
                "review_created",
                f"Action queued for human review. Review ID: {review_id}",
                evaluation["risk_breakdown"],
                {"review_id": review_id}
            )
        
        await session.commit()
        
        return AgentResponse(
            prompt=request.prompt,
            action=action,
            risk_score=evaluation["total_risk"],
            autonomy_level=evaluation["autonomy_level"],
            status=status,
            message=evaluation["description"],
            requires_confirmation=evaluation["requirements"]["requires_confirmation"],
            requires_review=evaluation["requirements"]["requires_review"],
            action_id=action_id,
            review_id=review_id,
        )
        
    except Exception as e:
        logger.error(f"Agent chat error: {str(e)}", exc_info=True)
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/providers")
async def get_providers():
    """Get available LLM providers"""
    return {
        "providers": [
            {"name": "mock", "description": "Mock provider (no API key needed)"},
            {"name": "groq", "description": "Groq API (requires GROQ_API_KEY in .env)"},
            {"name": "ollama", "description": "Local Ollama (requires OLLAMA_URL in .env)"},
        ]
    }