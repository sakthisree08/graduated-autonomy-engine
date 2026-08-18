import sys
sys.path.insert(0, '.')
from app.core.risk_scorer import RiskScorer

def test_risk_scorer():
    scorer = RiskScorer()
    assert scorer.calculate_reversibility('read') == 2
    assert scorer.calculate_reversibility('update') == 15
    assert scorer.calculate_reversibility('delete') == 25
    print('? All risk scorer tests passed!')
