import random
from entities.Question import Question


class ResponseService:
    """Handles response generation and cleaning"""
    
    def __init__(self, llm_service):
        self.llm = llm_service.model if llm_service else None
    
    def generate_response(self, prompt) -> str:
        """Generate response from LLM using the provided prompt"""
        if not self.llm:
            raise ValueError("LLM not available")
        
        response = self.llm.invoke(prompt)
        response_text = response if isinstance(response, str) else getattr(response, 'content', str(response))
        return self.clean_response(response_text)
    
    def clean_response(self, response: str) -> str:
        """Clean up model response to extract only the assistant's reply"""
        response = str(response)

        assistant_markers = [
            "Assistant:", "### Assistant:", "<|assistant|>", 
            "[/INST]", "### Response:", "Response:"
        ]
        
        for marker in assistant_markers:
            if marker in response:
                parts = response.split(marker, 1)
                if len(parts) > 1:
                    response = parts[1].strip()
                    break

        if "Human:" in response or "human" in response.lower():
            question_markers = ["Human:", "human:", "Question:", "### Human:"]
            for marker in question_markers:
                if marker in response:
                    parts = response.rsplit(marker, 1)
                    if len(parts) > 1:
                        response = parts[1].strip()
                        break
        special_tokens = [
            "<|endoftext|>", "<s>", "</s>", "[INST]", "[/INST]", 
            "<|system|>", "<|user|>", "<|assistant|>", "### System:",
            "System:", "### Human:", "Human:", "### Instruction:"
        ]
        for token in special_tokens:
            response = response.replace(token, "")
        
        prompt_fragments = [
            "Respond in character", "Keep responses brief", "Stay consistent",
            "Your Role:", "Location:", "Current Room:", "Your Mood:"
        ]
        
        lines = response.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if line and not any(fragment in line for fragment in prompt_fragments):
                cleaned_lines.append(line)
        
        response = ' '.join(cleaned_lines).strip('"\' \n\t')
        
        if not response or len(response) < 5:
            return "I'm not sure how to respond to that."
    
        if "?" in response and response.find("?") < len(response) // 3:
            parts = response.rsplit("?", 1)
            if len(parts) > 1:
                response = parts[1].strip()
        
        return response
    
    def generate_fallback_response(self, question: Question) -> str:
        """Generate a fallback response when LLM is unavailable"""
        innocent_responses = [
            "I don't know anything about that incident.",
            "I was in the library reading at that time.",
            "That's quite an accusation! I'm innocent!",
            "I think you should ask someone else about that.",
            "I didn't see anything unusual, sorry.",
            "That sounds serious, but I can't help you.",
            "I was talking with other guests when it happened.",
            "My memory is a bit fuzzy about that time.",
        ]
        
        murderer_responses = [
            "I have no idea what you're talking about.",
            "Why are you asking me? I'm just a guest here.",
            "That's none of your business, really.",
            "I think you're asking the wrong person.",
            "I was alone in my room at that time.",
            "You should focus on finding real clues.",
            "I don't appreciate these accusations.",
            "Perhaps you should look elsewhere for answers.",
        ]
        
        responses = murderer_responses if question.listener.murderer else innocent_responses
        return random.choice(responses)
