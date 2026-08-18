import sys
sys.path.insert(0, '.')
from app.core.risk_scorer import RiskScorer

class TestRiskScorer:
    def setup_method(self):
        self.scorer = RiskScorer()
    
    def test_reversibility_read(self):
        assert self.scorer.calculate_reversibility('read') == 2
    
    def test_reversibility_update(self):
        assert self.scorer.calculate_reversibility('update') == 15
    
    def test_reversibility_delete(self):
        assert self.scorer.calculate_reversibility('delete') == 25
    
    def test_reversibility_bulk_delete(self):
        assert self.scorer.calculate_reversibility('bulk_delete') == 30
    
    def test_data_scope_single(self):
        assert self.scorer.calculate_data_scope(1) == 2
    
    def test_data_scope_100(self):
        assert self.scorer.calculate_data_scope(100) == 10
    
    def test_data_scope_10000(self):
        assert self.scorer.calculate_data_scope(10000) == 20
    
    def test_regulatory_public(self):
        assert self.scorer.calculate_regulatory('public') == 2
    
    def test_regulatory_customer(self):
        assert self.scorer.calculate_regulatory('customer') == 10
    
    def test_regulatory_pii(self):
        assert self.scorer.calculate_regulatory('pii') == 15
    
    def test_total_risk(self):
        scores = {
            'reversibility': 25,
            'data_scope': 20,
            'regulatory': 15,
            'confidence': 8
        }
        total = self.scorer.calculate_total_risk(scores)
        assert total == 77
