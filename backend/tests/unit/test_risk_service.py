import sys
sys.path.insert(0, '.')
from app.services.risk_service import RiskService

class TestRiskService:
    def setup_method(self):
        self.service = RiskService()
    
    def test_read_action(self):
        action = {
            'operation': 'read',
            'target_table': 'customers',
            'condition': 'id = 10',
            'record_count': 1,
            'data_category': 'customer',
            'llm_confidence': 0.9,
            'validation_score': 0.9
        }
        result = self.service.evaluate_action(action)
        assert result['autonomy_level'] == 'AUTONOMOUS'
        assert result['total_risk'] == 17
    
    def test_bulk_delete_action(self):
        action = {
            'operation': 'bulk_delete',
            'target_table': 'customers',
            'condition': 'country = India',
            'record_count': 10000,
            'data_category': 'customer',
            'llm_confidence': 0.3,
            'validation_score': 0.3
        }
        result = self.service.evaluate_action(action)
        assert result['autonomy_level'] == 'REVIEW'
        assert result['total_risk'] > 70
    
    def test_human_readable_audit(self):
        action = {
            'operation': 'bulk_delete',
            'target_table': 'customers',
            'record_count': 10000
        }
        evaluation = {
            'total_risk': 78,
            'autonomy_level': 'REVIEW',
            'risk_breakdown': {
                'reversibility': 30,
                'data_scope': 20,
                'regulatory': 10,
                'confidence': 7
            },
            'description': 'High risk - human review required'
        }
        audit = self.service.get_human_readable_audit(action, evaluation)
        assert 'BULK_DELETE' in audit
        assert '10000' in audit
        assert 'REVIEW' in audit
