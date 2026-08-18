import sys
sys.path.insert(0, '.')
from app.core.autonomy_mapper import AutonomyMapper, AutonomyLevel

class TestAutonomyMapper:
    def setup_method(self):
        self.mapper = AutonomyMapper()
    
    def test_autonomous_low(self):
        level = self.mapper.map_to_autonomy(30)
        assert level == AutonomyLevel.AUTONOMOUS
    
    def test_autonomous_boundary(self):
        level = self.mapper.map_to_autonomy(40)
        assert level == AutonomyLevel.AUTONOMOUS
    
    def test_confirm_medium(self):
        level = self.mapper.map_to_autonomy(55)
        assert level == AutonomyLevel.CONFIRM
    
    def test_confirm_boundary(self):
        level = self.mapper.map_to_autonomy(70)
        assert level == AutonomyLevel.CONFIRM
    
    def test_review_high(self):
        level = self.mapper.map_to_autonomy(85)
        assert level == AutonomyLevel.REVIEW
    
    def test_autonomous_requirements(self):
        req = self.mapper.get_action_requirements(AutonomyLevel.AUTONOMOUS)
        assert req['requires_confirmation'] is False
        assert req['can_execute_immediately'] is True
    
    def test_confirm_requirements(self):
        req = self.mapper.get_action_requirements(AutonomyLevel.CONFIRM)
        assert req['requires_confirmation'] is True
        assert req['requires_review'] is False
    
    def test_review_requirements(self):
        req = self.mapper.get_action_requirements(AutonomyLevel.REVIEW)
        assert req['requires_review'] is True
        assert req['can_execute_immediately'] is False
    
    def test_risk_description_low(self):
        desc = self.mapper.get_risk_level_description(25)
        assert 'Very low risk' in desc
    
    def test_risk_description_high(self):
        desc = self.mapper.get_risk_level_description(90)
        assert 'Very high risk' in desc
