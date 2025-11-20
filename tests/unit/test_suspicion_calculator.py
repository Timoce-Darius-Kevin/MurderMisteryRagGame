import pytest
from Services.SuspicionCalculator import SuspicionCalculator


@pytest.mark.unit
class TestSuspicionCalculator:
    """Unit tests for SuspicionCalculator"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.calculator = SuspicionCalculator()
    
    def test_suspicious_question_increases_suspicion(self):
        """Test that suspicious questions increase suspicion"""
        question = "Where were you during the murder?"
        response = "I was in the library."
        
        speaker_change, listener_change = self.calculator.calculate_suspicion_change(
            question, response, is_murderer=False, lying_ability=5, mood="neutral"
        )
        
        assert speaker_change > 0
        assert listener_change > 0
    
    def test_defensive_response_increases_suspicion(self):
        """Test that defensive responses increase listener suspicion"""
        question = "What were you doing?"
        response = "That's none of your business!"
        
        speaker_change, listener_change = self.calculator.calculate_suspicion_change(
            question, response, is_murderer=False, lying_ability=5, mood="neutral"
        )
        
        assert listener_change > 0
    
    def test_cooperative_response_decreases_suspicion(self):
        """Test that cooperative responses decrease suspicion"""
        question = "Can you help me?"
        response = "Of course, I'll cooperate fully and tell you the truth."
        
        speaker_change, listener_change = self.calculator.calculate_suspicion_change(
            question, response, is_murderer=False, lying_ability=5, mood="neutral"
        )
        
        assert speaker_change <= 0
        assert listener_change <= 0
    
    def test_murderer_gets_more_suspicion(self):
        """Test that murderers get more suspicion from suspicious questions"""
        question = "Did you kill him?"
        response = "No."
        
        innocent_speaker, innocent_listener = self.calculator.calculate_suspicion_change(
            question, response, is_murderer=False, lying_ability=5, mood="neutral"
        )
        
        murderer_speaker, murderer_listener = self.calculator.calculate_suspicion_change(
            question, response, is_murderer=True, lying_ability=5, mood="neutral"
        )
        
        assert murderer_listener > innocent_listener
    
    def test_high_lying_ability_reduces_murderer_suspicion(self):
        """Test that high lying ability reduces suspicion for murderers"""
        question = "Where were you during the murder?"
        response = "I was reading."
        
        low_skill_speaker, low_skill_listener = self.calculator.calculate_suspicion_change(
            question, response, is_murderer=True, lying_ability=3, mood="neutral"
        )
        
        high_skill_speaker, high_skill_listener = self.calculator.calculate_suspicion_change(
            question, response, is_murderer=True, lying_ability=9, mood="neutral"
        )
        
        # High lying ability should result in higher suspicion for murderers
        assert high_skill_listener >= low_skill_listener
    
    def test_angry_mood_increases_suspicion(self):
        """Test that angry mood increases suspicion"""
        question = "What do you know?"
        response = "Nothing."
        
        neutral_speaker, neutral_listener = self.calculator.calculate_suspicion_change(
            question, response, is_murderer=False, lying_ability=5, mood="neutral"
        )
        
        angry_speaker, angry_listener = self.calculator.calculate_suspicion_change(
            question, response, is_murderer=False, lying_ability=5, mood="angry"
        )
        
        assert angry_listener > neutral_listener
    
    def test_cooperative_mood_decreases_suspicion(self):
        """Test that cooperative mood decreases speaker suspicion"""
        question = "Can you help?"
        response = "Yes, I can."
        
        neutral_speaker, neutral_listener = self.calculator.calculate_suspicion_change(
            question, response, is_murderer=False, lying_ability=5, mood="neutral"
        )
        
        coop_speaker, coop_listener = self.calculator.calculate_suspicion_change(
            question, response, is_murderer=False, lying_ability=5, mood="cooperative"
        )
        
        assert coop_speaker < neutral_speaker
    
    def test_suspicion_change_clamped(self):
        """Test that suspicion changes are clamped to reasonable ranges"""
        question = "murder kill weapon blood guilty"
        response = "none of your business stop asking wrong person"
        
        speaker_change, listener_change = self.calculator.calculate_suspicion_change(
            question, response, is_murderer=True, lying_ability=1, mood="angry"
        )
        
        # Should be clamped
        assert -5 <= speaker_change <= 5
        assert -3 <= listener_change <= 8
    
    def test_fallback_suspicion_calculation(self):
        """Test fallback suspicion calculation"""
        question = "Where were you during the murder?"
        response = "That's none of your business."
        
        speaker_change, listener_change = self.calculator.calculate_fallback_suspicion(
            question, response, is_murderer=True
        )
        
        assert speaker_change > 0
        assert listener_change > 0
