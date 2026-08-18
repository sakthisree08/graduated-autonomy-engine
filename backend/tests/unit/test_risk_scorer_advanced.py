import sys
sys.path.insert(0, '.')
from app.core.risk_scorer import RiskScorer

class TestRiskScorerAdvanced:
    def setup_method(self):
        self.scorer = RiskScorer()
    
    def test_confidence_high(self):
        action = {'llm_confidence': 0.9, 'validation_score': 0.9}
        score = self.scorer.calculate_confidence(action)
        assert score >= 22
    
    def test_confidence_low(self):
        action = {'llm_confidence': 0.3, 'validation_score': 0.3}
        score = self.scorer.calculate_confidence(action)
        assert score <= 8
    
    def test_confidence_mixed(self):
        action = {'llm_confidence': 0.8, 'validation_score': 0.4}
        score = self.scorer.calculate_confidence(action)
        assert 10 < score < 20
    
    def test_total_risk_low(self):
        scores = {
            'reversibility': 2,
            'data_scope': 2,
            'regulatory': 10,
            'confidence': 22
        }
        total = self.scorer.calculate_total_risk(scores)
        assert total == 17
    
    def test_total_risk_medium(self):
        scores = {
            'reversibility': 15,
            'data_scope': 5,
            'regulatory': 10,
            'confidence': 18
        }
        total = self.scorer.calculate_total_risk(scores)
        assert total == 37
    
    def test_breakdown_complete(self):
        action = {
            'operation': 'bulk_delete',
            'record_count': 10000,
            'data_category': 'hipaa',
            'llm_confidence': 0.4,
            'validation_score': 0.3
        }
        breakdown = self.scorer.get_risk_breakdown(action)
        assert 'scores' in breakdown
        assert 'total_risk' in breakdown
        assert 'max_scores' in breakdown
        assert breakdown['scores']['reversibility'] == 30
        assert breakdown['scores']['data_scope'] == 20
        assert breakdown['scores']['regulatory'] == 20
        assert breakdown['scores']['confidence'] == 8
    
    def test_unknown_operation(self):
        score = self.scorer.calculate_reversibility('unknown')
        assert score == 15
    
    def test_empty_data_scope(self):
        score = self.scorer.calculate_data_scope(0)
        assert score == 0
    
    def test_regulatory_unknown(self):
        score = self.scorer.calculate_regulatory('unknown')
        assert score == 10
