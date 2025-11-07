import os
from typing import List
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document
from langchain_huggingface import ChatHuggingFace
from langchain_core.prompts import ChatPromptTemplate
from entities.Conversation import Conversation
import random

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
    
    def add_conversation(self, conversation: Conversation, turn: int) -> None:
        """Store a conversation in memory"""
        doc = Document(
                page_content=f"Question: {conversation.question}\nResponse: {conversation.response}",
                metadata={
                    "player_ids": f"{conversation.speaker.id} - {conversation.listener.id}",\
                    "players": f"{conversation.speaker.name} - {conversation.listener.name}",\
                    "suspicion_change_user": conversation.suspicion_change_speaker,\
                    "suspicion_change_player": conversation.suspicion_change_listener,\
                    "turn": turn
                    }
                )
        self.vector_store.add_documents([doc])
        
    def get_conversation_context(self, current_conversation: Conversation, number_docs_to_retrieve: int = 3) -> str:
        """Retrieve relevant conversation history"""
        
        if self.vector_store._collection.count() == 0:
            return "No previous conversations."
        
        results = self.vector_store.similarity_search(
            f"Conversation with {current_conversation.speaker}: {current_conversation.question}",
            k=number_docs_to_retrieve,
            filter={"players":f"{current_conversation.speaker.name} - {current_conversation.listener.name}"}
        )
        
        context = "Previous conversations:\n"
        for i, doc in enumerate(results):
            context += f"{i+1}. {doc.page_content}\n"
        
        return context

    def generate_response(self, current_conversation: Conversation, conversation_history: List['Conversation'] = []):
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
        
        context = self.get_conversation_context(current_conversation)
        
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", f"""You are {current_conversation.speaker.name} in a murder mystery game. 
             Respond naturally to questions while hiding that you're the murderer (if you are).
             Use the conversation history to maintain consistency.
             
             Conversation History:
             {context}
             
             Current situation: Suspicion level: {current_conversation.speaker.suspicion}"""),
            ("human", "{question}")
        ])
        
        chain = prompt_template | self.llm
        
        try:
            response = chain.invoke({
                "player_name": current_conversation.speaker.name,
                "context": context,
                "suspicion": current_conversation.speaker.suspicion,
                "question": current_conversation.question
            })
            
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            # Simple suspicion change logic for Phase 1
            suspicious_keywords = ["murder", "kill", "weapon", "blood", "alibi"]
            suspicion_change = 3 if any(keyword in current_conversation.question.lower() for keyword in suspicious_keywords) else 0
            
            return response_text, suspicion_change
            
        except Exception as e:
            print(f"LLM Error: {e}")
            return "I'm having trouble responding right now.", 0

# Singleton instance
rag_manager = RagManager()   