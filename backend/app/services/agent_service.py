"""
Agent Service - Handles natural language requests via LLM
"""

import logging
from typing import Dict, Any, Optional
from app.core.llm_client import LLMClient
from app.services.risk_service import RiskService
from app.services.db_service import DatabaseService

logger = logging.getLogger(__name__)


class AgentService:
    """Service for processing natural language agent requests"""
    
    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service
        self.llm_client = LLMClient(provider="mock")  # Default to mock
        self.risk_service = RiskService()
    
    async def set_provider(self, provider: str):
        """Set the LLM provider"""
        self.llm_client = LLMClient(provider=provider)
    
    async def process_request(self, prompt: str, agent_id: str = "agent-001", 
                              context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a natural language request:
        1. LLM generates structured action
        2. Risk engine evaluates
        3. Execute or wait for approval
        """
        if context is None:
            context = {"agent_id": agent_id}
        
        try:
            # 1. Generate action from LLM
            action = await self.llm_client.generate_action(prompt, context)
            action["agent_id"] = agent_id
            
            logger.info(f"LLM generated action: {action}")
            
            # 2. Evaluate with risk engine
            evaluation = self.risk_service.evaluate_action(action)
            
            # 3. Store in database (using existing action flow)
            from app.schemas.action import ActionRequest
            
            # 4. Return the evaluation result
            return {
                "prompt": prompt,
                "generated_action": action,
                "risk_evaluation": evaluation,
                "status": evaluation["autonomy_level"],
                "message": evaluation["description"]
            }
            
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}", exc_info=True)
            raise