from config.GameConfig import GameConfig


class SuspicionCalculator:
    """Calculates suspicion changes based on conversations and interactions"""
    
    SUSPICIOUS_KEYWORDS = ["murder", "kill", "weapon", "blood", "alibi", "guilty", "crime", "dead", "body"]
    DEFENSIVE_KEYWORDS = ["none of your business", "stop asking", "accusation", "wrong person", "not your concern"]
    COOPERATIVE_KEYWORDS = ["help", "assist", "truth", "honest", "cooperate", "investigation"]
    
    def calculate_suspicion_change(self, question: str, response: str, is_murderer: bool, 
                                   lying_ability: int, mood: str) -> tuple[int, int]:
        """Calculate suspicion change based on question and response
        
        Returns:
            tuple[int, int]: (suspicion_change_speaker, suspicion_change_listener)
        """
        suspicion_change_speaker = 0
        suspicion_change_listener = 0
        
        question_lower = question.lower()
        response_lower = response.lower()
        
        if any(keyword in question_lower for keyword in self.SUSPICIOUS_KEYWORDS):
            suspicion_change_speaker += 2
            if is_murderer:
                # Good liars don't get as suspicious from direct questions
                if lying_ability > 7 and mood not in ["defensive", "angry"]:
                    suspicion_change_listener += 3
                else:
                    suspicion_change_listener += 1
            else:
                suspicion_change_listener += 1
        
        if any(keyword in response_lower for keyword in self.DEFENSIVE_KEYWORDS):
            suspicion_change_listener += 3
        
        elif any(keyword in response_lower for keyword in self.COOPERATIVE_KEYWORDS):
            suspicion_change_listener -= 1
            suspicion_change_speaker -= 1
        
        # Murderers are naturally more suspicious when asked direct questions
        if is_murderer and any(keyword in question_lower for keyword in self.SUSPICIOUS_KEYWORDS):
            suspicion_change_listener += GameConfig.MURDERER_SUSPICION_MODIFIER

        if mood == "angry":
            suspicion_change_listener += 2
        elif mood == "defensive":
            suspicion_change_listener += 1
        elif mood == "cooperative":
            suspicion_change_speaker -= 1
        
        suspicion_change_speaker = max(min(suspicion_change_speaker, 5), -5)
        suspicion_change_listener = max(min(suspicion_change_listener, 8), -3)
        
        return suspicion_change_speaker, suspicion_change_listener
    
    def calculate_fallback_suspicion(self, question: str, response: str, is_murderer: bool) -> tuple[int, int]:
        """Calculate suspicion for fallback responses
        
        Returns:
            tuple[int, int]: (suspicion_change_speaker, suspicion_change_listener)
        """
        suspicion_change_speaker = 0
        suspicion_change_listener = 0
        
        if any(word in question.lower() for word in self.SUSPICIOUS_KEYWORDS):
            suspicion_change_speaker += 2
            suspicion_change_listener += 3 if is_murderer else 1
        
        if any(word in response.lower() for word in self.DEFENSIVE_KEYWORDS):
            suspicion_change_listener += 2
        
        return suspicion_change_speaker, suspicion_change_listener
