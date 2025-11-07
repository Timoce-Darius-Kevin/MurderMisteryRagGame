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
        
        try:
            self.llm = ChatHuggingFace(
                model_name=model_name,
                task="text-generation",
                huggingfacehub_api_token=os.getenv("HF_TOKEN", "")
            )
        except:
            print("RagManager Warning: Could not load primary model, using fallback")
            self.llm = ChatHuggingFace(
                model_name="unsloth/Llama-3.2-3B-Instruct",
                task="text-generation",
                huggingfacehub_api_token=os.getenv("HF_TOKEN", "")
            )
    
    def _initialize_llm(self, model_name: str):
        """Initialize the LLM with proper error handling"""
        try:
            # Option 1: Using HuggingFace Pipeline (local model)
            print(f"Loading model: {model_name}")
            
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16,
                device_map="auto",
                low_cpu_mem_usage=True
            )
            
            # Create text generation pipeline
            pipe = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                max_new_tokens=100,
                temperature=0.7,
                top_p=0.9,
                repetition_penalty=1.1,
                pad_token_id=tokenizer.eos_token_id
            )
            
            llm = HuggingFacePipeline(pipeline=pipe)
            print("Model loaded successfully!")
            return llm
            
        except Exception as e:
            print(f"Error loading model {model_name}: {e}")
            print("Falling back to simpler model...")
            
            # Fallback to a smaller model
            try:
                fallback_model = "microsoft/DialoGPT-small"
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
            # Fallback responses for Phase 1 testing
            fallback_responses = [
                "I'm not sure what to tell you about that.",
                "I didn't see anything unusual.",
                "That's an interesting question. I wish I could help more.",
                "I was occupied elsewhere at that time.",
                "You should ask someone else about that."
            ]

            return random.choice(fallback_responses), random.randint(-2, 5)
        
        context = self.get_conversation_context(current_question)
        
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", f"""You are {current_question.speaker.name} in a murder mystery game. 
             Respond naturally to questions while hiding that you're the murderer (if you are).
             Use the conversation history to maintain consistency.
             
             Conversation History:
             {context}
             
             Current situation: Suspicion level: {current_question.speaker.suspicion}"""),
            ("human", "{question}")
        ])
        
        chain = prompt_template | self.llm
        
        try:
            response = chain.invoke({
                "player_name": current_question.speaker.name,
                "context": context,
                "suspicion": current_question.speaker.suspicion,
                "question": current_question.question
            })
            
            response_text = response.content if hasattr(response, 'content') else str(response)
            if not isinstance(response_text, str):
                try:
                    response_text = json.dumps(response_text)
                except Exception:
                    response_text = str(response_text)
                    
            # Simple suspicion change logic for Phase 1
            suspicious_keywords = ["murder", "kill", "weapon", "blood", "alibi"]
            suspicion_change = 3 if any(keyword in current_question.question.lower() for keyword in suspicious_keywords) else 0
            
            return response_text, suspicion_change
            
        except Exception as e:
            print(f"LLM Error: {e}")
            return "I'm having trouble responding right now.", 0   