"""
LLM Client - Interface for various LLM providers
"""

import json
import logging
import re
from typing import Dict, Any, Optional
import httpx
from app.config import settings

logger = logging.getLogger(__name__)


class LLMClient:
    """Base LLM client"""
    
    def __init__(self, provider: str = "mock"):
        self.provider = provider.lower()
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def generate_action(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate a structured action from a natural language prompt"""
        if self.provider == "mock":
            return await self._generate_mock(prompt, context)
        elif self.provider == "groq":
            return await self._generate_groq(prompt, context)
        elif self.provider == "ollama":
            return await self._generate_ollama(prompt, context)
        else:
            return await self._generate_mock(prompt, context)
    
    async def _generate_groq(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate action using Groq API"""
        try:
            from groq import Groq
            
            client = Groq(api_key=settings.groq_api_key)
            
            system_prompt = """You are an AI action generator. Convert user requests into structured actions.
            Respond with ONLY a JSON object containing:
            - operation: the action type (read, update, delete, bulk_delete, create)
            - target_table: the target resource
            - condition: the condition (optional)
            - record_count: estimated number of records affected
            - data_category: category of data (customer, pii, financial, internal, public)
            - confidence: your confidence score (0.0 to 1.0)
            - parameters: any additional parameters as an object
            """
            
            response = client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300,
            )
            
            content = response.choices[0].message.content
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            
            result = json.loads(content)
            result["llm_confidence"] = result.get("confidence", 0.7)
            result["validation_score"] = 0.8
            result["agent_id"] = context.get("agent_id", "llm-agent") if context else "llm-agent"
            
            logger.info(f"Groq generated action: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Groq API error: {str(e)}")
            return await self._generate_mock(prompt, context)
    
    async def _generate_ollama(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate action using Ollama (local)"""
        try:
            system_prompt = """You are an AI action generator. Convert user requests into structured actions.
            Respond with ONLY a JSON object containing:
            - operation: the action type (read, update, delete, bulk_delete, create)
            - target_table: the target resource
            - condition: the condition (optional)
            - record_count: estimated number of records affected
            - data_category: category of data (customer, pii, financial, internal, public)
            - confidence: your confidence score (0.0 to 1.0)
            - parameters: any additional parameters
            """
            
            response = await self.client.post(
                f"{settings.ollama_url}/api/generate",
                json={
                    "model": "llama2",
                    "prompt": f"{system_prompt}\n\nUser: {prompt}\n\nResponse (JSON only, no explanation):",
                    "stream": False,
                    "temperature": 0.3,
                }
            )
            
            content = response.json()["response"]
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            
            result = json.loads(content)
            result["llm_confidence"] = result.get("confidence", 0.7)
            result["validation_score"] = 0.8
            result["agent_id"] = context.get("agent_id", "llm-agent") if context else "llm-agent"
            
            return result
            
        except Exception as e:
            logger.error(f"Ollama API error: {str(e)}")
            return await self._generate_mock(prompt, context)
    
    async def _generate_mock(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Mock generation for testing"""
        prompt_lower = prompt.lower()
        
        if "delete all" in prompt_lower or "delete every" in prompt_lower:
            return {
                "operation": "bulk_delete",
                "target_table": "customers",
                "condition": "id > 0",
                "record_count": 10000,
                "data_category": "customer",
                "llm_confidence": 0.4,
                "validation_score": 0.3,
                "agent_id": context.get("agent_id", "llm-agent") if context else "llm-agent",
                "parameters": {}
            }
        elif "delete" in prompt_lower:
            return {
                "operation": "delete",
                "target_table": "customers",
                "condition": "id = 10",
                "record_count": 1,
                "data_category": "customer",
                "llm_confidence": 0.7,
                "validation_score": 0.7,
                "agent_id": context.get("agent_id", "llm-agent") if context else "llm-agent",
                "parameters": {}
            }
        elif "update" in prompt_lower:
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', prompt_lower)
            email = email_match.group(0) if email_match else "new@email.com"
            return {
                "operation": "update",
                "target_table": "customers",
                "condition": "id = 10",
                "record_count": 1,
                "data_category": "customer",
                "llm_confidence": 0.8,
                "validation_score": 0.8,
                "agent_id": context.get("agent_id", "llm-agent") if context else "llm-agent",
                "parameters": {"set": {"email": email}}
            }
        elif "read" in prompt_lower or "get" in prompt_lower:
            return {
                "operation": "read",
                "target_table": "customers",
                "condition": "id = 10",
                "record_count": 1,
                "data_category": "customer",
                "llm_confidence": 0.9,
                "validation_score": 0.9,
                "agent_id": context.get("agent_id", "llm-agent") if context else "llm-agent",
                "parameters": {}
            }
        else:
            return {
                "operation": "read",
                "target_table": "unknown",
                "condition": "",
                "record_count": 0,
                "data_category": "general",
                "llm_confidence": 0.5,
                "validation_score": 0.5,
                "agent_id": context.get("agent_id", "llm-agent") if context else "llm-agent",
                "parameters": {}
            }
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()