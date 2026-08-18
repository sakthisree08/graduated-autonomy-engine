"""
Test script for Risk Scoring Engine
"""

import json
from app.core.risk_scorer import RiskScorer
from app.core.autonomy_mapper import AutonomyMapper, AutonomyLevel
from app.services.risk_service import RiskService

def test_risk_scorer():
    print("=" * 60)
    print("🧪 TESTING RISK SCORING ENGINE")
    print("=" * 60)
    
    # Create service
    service = RiskService()
    
    # Test Case 1: READ - Should be AUTONOMOUS
    print("\n📋 Test 1: READ customer WHERE id = 10")
    action1 = {
        "operation": "read",
        "target_table": "customers",
        "condition": "id = 10",
        "record_count": 1,
        "data_category": "customer",
        "llm_confidence": 0.9,
        "validation_score": 0.9,
    }
    result1 = service.evaluate_action(action1)
    print(f"  Total Risk: {result1['total_risk']}")
    print(f"  Autonomy Level: {result1['autonomy_level']}")
    print(f"  Breakdown: {json.dumps(result1['risk_breakdown'], indent=2)}")
    
    # Test Case 2: UPDATE - Should be CONFIRM
    print("\n📋 Test 2: UPDATE customer SET email WHERE id = 10")
    action2 = {
        "operation": "update",
        "target_table": "customers",
        "condition": "id = 10",
        "record_count": 1,
        "data_category": "customer",
        "llm_confidence": 0.8,
        "validation_score": 0.8,
        "parameters": {"set": {"email": "new@email.com"}}
    }
    result2 = service.evaluate_action(action2)
    print(f"  Total Risk: {result2['total_risk']}")
    print(f"  Autonomy Level: {result2['autonomy_level']}")
    print(f"  Breakdown: {json.dumps(result2['risk_breakdown'], indent=2)}")
    
    # Test Case 3: BULK DELETE - Should be REVIEW
    print("\n📋 Test 3: DELETE FROM customers WHERE country = 'India'")
    action3 = {
        "operation": "bulk_delete",
        "target_table": "customers",
        "condition": "country = 'India'",
        "record_count": 10000,
        "data_category": "customer",
        "llm_confidence": 0.3,
        "validation_score": 0.3,
    }
    result3 = service.evaluate_action(action3)
    print(f"  Total Risk: {result3['total_risk']}")
    print(f"  Autonomy Level: {result3['autonomy_level']}")
    print(f"  Breakdown: {json.dumps(result3['risk_breakdown'], indent=2)}")
    
    # Generate human-readable audit for Test 3
    print("\n📋 Human-Readable Audit Log:")
    audit = service.get_human_readable_audit(action3, result3)
    print(audit)
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ SUMMARY - Risk Scoring Engine Tests")
    print("=" * 60)
    print(f"✅ Test 1 (READ): {result1['autonomy_level']} - Should be AUTONOMOUS")
    print(f"✅ Test 2 (UPDATE): {result2['autonomy_level']} - Should be CONFIRM")
    print(f"✅ Test 3 (BULK DELETE): {result3['autonomy_level']} - Should be REVIEW")

if __name__ == "__main__":
    test_risk_scorer()