import json
import os
import torch
import random
from typing import List
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFacePipeline
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import ChatHuggingFace
from langchain_core.prompts import ChatPromptTemplate
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from entities.Conversation import Conversation, Question


class RagManager:
    
    def __init__(self, model_name: str = "mistralai/Mistral-7B-Instruct-v0.3") -> None:
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        self.vector_store = Chroma(
            collection_name="conversation_memory",
            embedding_function=self.embeddings,
            persist_directory="./database/conversation_db"
        )
        
        self.llm = self._initialize_llm(model_name)
    
    def _initialize_llm(self, model_name: str):
        """Initialize the LLM with proper error handling"""
        try:
            # Option 1: Using HuggingFace Pipeline (local model)
            print(f"Loading model: {model_name}")
            
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float32,
                device_map="auto" if torch.cuda.is_available() else None,
                low_cpu_mem_usage=True
            )
            
            # Create text generation pipeline
            pipe = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                max_new_tokens=100,
                temperature=0.8,
                top_p=0.9,
                repetition_penalty=1.1,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id
            )
            
            llm = HuggingFacePipeline(pipeline=pipe)
            print(f"Model {model_name} loaded successfully!")
            return llm
            
        except Exception as e:
            print(f"Error loading model {model_name}: {e}")
            print("Falling back to simpler model...")
            
            # Fallback to a smaller model
            try:
                fallback_model = "microsoft/DialoGPT-medium"
                print(f"Trying fallback model: {fallback_model}")
                
                tokenizer = AutoTokenizer.from_pretrained(fallback_model)
                model = AutoModelForCausalLM.from_pretrained(fallback_model)
                
                pipe = pipeline(
                    "text-generation",
                    model=model,
                    tokenizer=tokenizer,
                    max_new_tokens=50,
                    temperature=0.7
                )
                
                llm = HuggingFacePipeline(pipeline=pipe)
                print("Fallback model loaded successfully!")
                return llm
                
            except Exception as e2:
                print(f"Error loading fallback model: {e2}")
                print("Using rule-based fallback system.")
                return None
    
    def add_conversation(self, conversation: Conversation, turn: int) -> None:
        """Store a conversation in memory"""
        doc = Document(
                page_content=f"Question: {conversation.question}\nResponse: {conversation.response}",
                metadata={
                    "player_ids": f"{conversation.question.speaker.id} - {conversation.question.listener.id}",\
                    "players": f"{conversation.question.speaker.name} - {conversation.question.listener.name}",\
                    "turn": turn
                    }
                )
        self.vector_store.add_documents([doc])
        
    def get_conversation_context(self, current_question: Question, number_docs_to_retrieve: int = 3) -> str:
        """Retrieve relevant conversation history"""
        
        if self.vector_store._collection.count() == 0:
            return "No previous conversations."
        
        results = self.vector_store.similarity_search(
            f"Conversation with {current_question.speaker}: {current_question.question}",
            k=number_docs_to_retrieve,
            filter={"players":f"{current_question.speaker.name} - {current_question.listener.name}"}
        )
        
        context = "Previous conversations:\n"
        for i, doc in enumerate(results):
            context += f"{i+1}. {doc.page_content}\n"
        
        return context

    def generate_response(self, current_question: Question, conversation_history: List[Question] = []):
        """Generate NPC response using RAG"""
        
        if not self.llm:
            return self.fallback_response(current_question)
        try:
            context = self.get_conversation_context(current_question)
            
            prompt = self._create_prompt(current_question, context)
            
            print(f"DEBUG - Prompt: {prompt}")
            
            response = self.llm.invoke(prompt)
            
            response_text = response if isinstance(response, str) else getattr(response, 'content', str(response))

            print(f"DEBUG - Raw response: {response_text}") 
            
            response_text = self._clean_response(response_text)
            
            suspicion_change = self._calculate_suspicion_change(current_question.question, response_text)
            
                
            return response_text, suspicion_change 
        except Exception as exception:
            print(f"LLM generation error: {exception}")
            return self.fallback_response(current_question)
    
    def _create_prompt(self, question: Question, context: str):
        """Create prompt for the LLM"""
        prompt = f"""You are {question.listener.name} in a murder mystery game. Respond naturally to the question while staying in character.
                Context from previous conversations:
                {context}

                Your current suspicion level: {question.listener.suspicion}
                Your role: {'Murderer' if question.listener.murderer else 'Innocent guest'}

                Question from another player: "{question}"

                Respond naturally and briefly (1-4 sentences). Do not break character. Do not reveal you are an AI.

                Response:"""
        return prompt

    def fallback_response(self, question: Question):
        """Fallback response system"""
        import random
        
        # Character-based responses
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
        ]
        
        responses = murderer_responses if question.speaker.murderer else innocent_responses
        response = random.choice(responses)
        
        # Simple suspicion logic
        suspicious_questions = ["murder", "kill", "weapon", "blood", "knife", "gun", "alibi", "where were you"]
        suspicion_change = 5 if any(word in question.question.lower() for word in suspicious_questions) else random.randint(-2, 2)
        
        return response, suspicion_change
    
    def _clean_response(self, response: str) -> str:
        """Clean up LLM response"""
        # Remove any prompt fragments and extra whitespace
        if "Response:" in response:
            response = response.split("Response:")[-1].strip()
        response = response.split("\n")[0].strip()  # Take first line only
        response = response.split('.')[0] + '.' if '.' in response else response
        if not response or len(response) < 5:
            return "I'm not sure how to respond to that."
        return response
    
    def _calculate_suspicion_change(self, question: str, response: str) -> int:
        """Calculate suspicion change based on question and response"""
        suspicious_keywords = ["murder", "kill", "weapon", "blood", "alibi", "guilty"]
        defensive_keywords = ["none of your business", "stop asking", "accusation", "wrong person"]
        
        base_change = 0
        if any(keyword in question.lower() for keyword in suspicious_keywords):
            base_change += 3
        if any(keyword in response.lower() for keyword in defensive_keywords):
            base_change += 2
            
        return min(max(base_change, -5), 10)
 