async def _generate_mock(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Mock generation for testing"""
    prompt_lower = prompt.lower()
    
    # Simple intent detection
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
        import re
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