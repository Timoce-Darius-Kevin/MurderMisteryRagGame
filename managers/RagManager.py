import os
from dotenv import load_dotenv
import torch
import random
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFacePipeline
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import ChatHuggingFace
from langchain_core.prompts import ChatPromptTemplate
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from entities.Conversation import Conversation, Question

load_dotenv()
class RagManager:
    
    def __init__(self, model_name: str | None = os.getenv("MISTRAL_7B_HUGGINGFACEHUB")) -> None:
        
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        self.vector_store = Chroma(
            collection_name="conversation_memory",
            embedding_function=self.embeddings,
            persist_directory="./database/conversation_db"
        )
        
        self.llm = self._initialize_llm(model_name)
        self.prompt_template = self._create_prompt_template()
    
    def _initialize_llm(self, model_name: str | None):
        """Initialize the LLM"""
        try:
            if model_name == None:
                raise ValueError
            print(f"Loading model: {model_name}")
            
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                dtype=torch.bfloat16,
                device_map="auto" if torch.cuda.is_available() else None,
                low_cpu_mem_usage=True
            )
            
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
            chat_model = ChatHuggingFace(llm = llm)
            print(f"Model {model_name} loaded successfully!")
            return chat_model
            
        except Exception as e:
            print(f"Error loading model {model_name}: {e}")
            print("Falling back to simpler model...")
            
            try:
                fallback_model = os.getenv("ZEPHYR_7B_HUGGINGFACEHUB")
                print(f"Trying fallback model: {fallback_model}")
                
                tokenizer = AutoTokenizer.from_pretrained(fallback_model)
                model = AutoModelForCausalLM.from_pretrained(str(fallback_model))
                
                pipe = pipeline(
                    "text-generation",
                    model=model,
                    tokenizer=tokenizer,
                    max_new_tokens=50,
                    temperature=0.7
                )
                
                llm = HuggingFacePipeline(pipeline=pipe)
                chat_model = ChatHuggingFace(llm = llm)
                print("Fallback model loaded successfully!")
                return chat_model
                
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
            filter={"players":f"{current_question.speaker.id} - {current_question.listener.id}"}
        )
        
        context = "Previous conversations:\n"
        for i, doc in enumerate(results):
            context += f"{i+1}. {doc.page_content}\n"
        
        return context

    def generate_response(self, current_question: Question):
        """Generate NPC response using RAG"""
        
        if not self.llm:
            return self.fallback_response(current_question)
        try:
            context = self.get_conversation_context(current_question)
            
            prompt = self._create_prompt(current_question, context)
            
            response = self.llm.invoke(prompt)
            
            response_text = response if isinstance(response, str) else getattr(response, 'content', str(response))
            
            response_text = self._clean_response(response_text)
            
            suspicion_change_speaker, suspicion_change_listener = self._calculate_suspicion_change(current_question.question, response_text, current_question.listener.murderer)
            
                
            return response_text, suspicion_change_speaker, suspicion_change_listener 
        except Exception as exception:
            print(f"LLM generation error: {exception}")
            return self.fallback_response(current_question)
    
    def _create_prompt(self, question: Question, context: str):
        """Create prompt for the LLM"""
        return self.prompt_template.format_messages(
                character_name=question.listener.name,
                context=context,
                suspicion_level=question.listener.suspicion,
                role="MURDERER - be defensive and evasive" if question.listener.murderer else "INNOCENT - be helpful and cooperative",
                question=question.question
            )

    def _create_prompt_template(self):
        """Create structured prompt template for consistent message formatting"""
        return ChatPromptTemplate.from_messages([
            ("system", """You are {character_name} in a murder mystery game. Respond naturally while staying in character. The tone should be that of a character in a sherlock holmes novel.

            Context from previous conversations:
            {context}

            Your current suspicion level: {suspicion_level}
            Your secret role: {role}

            Respond naturally and briefly (1-4 sentences). Do not break character. Do not reveal you are an AI."""),
                    ("human", "{question}")
                ])
    
    def fallback_response(self, question: Question):
        """Fallback response system"""
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
        
        responses = murderer_responses if question.listener.murderer else innocent_responses
        response = random.choice(responses)
        
        suspicion_change_speaker = 0
        suspicion_change_listener = 0
        
        suspicious_questions = ["murder", "kill", "weapon", "blood", "knife", "gun", "alibi", "where were you"]
        if any(word in question.question.lower() for word in suspicious_questions):
            suspicion_change_speaker += 2
            suspicion_change_listener += 3 if question.listener.murderer else 1
        
        # Adjust based on response tone
        defensive_responses = ["none of your business", "stop asking", "accusation", "wrong person"]
        if any(word in response.lower() for word in defensive_responses):
            suspicion_change_listener += 2
        
        return response, suspicion_change_speaker, suspicion_change_listener
    
    def _clean_response(self, response: str) -> str:
        """Model-aware cleaning function"""
        
        # Detect model type by response format
        if "<|assistant|>" in response:
            # Zephyr format
            parts = response.split("<|assistant|>", 1)
            if len(parts) > 1:
                response = parts[1].split("<|user|>")[0].strip()
        elif "[/INST]" in response: 
            parts = response.split("[/INST]", 1)
            if len(parts) > 1:
                response = parts[1].strip()
        else:
            for delimiter in ["### Assistant:", "Assistant:", "\n\n"]:
                if delimiter in response:
                    parts = response.split(delimiter, 1)
                    if len(parts) > 1:
                        response = parts[1].strip()
                        break
        
        special_tokens = ["<|endoftext|>", "<s>", "</s>", "[INST]", "[/INST]", "<|system|>", "<|user|>", "<|assistant|>"]
        for token in special_tokens:
            response = response.replace(token, "")
        
        response = response.strip('"\' \n')
        
        if not response or len(response) < 5:
            return "I'm not sure how to respond to that."
        
        return response
    
    def _calculate_suspicion_change(self, question: str, response: str, is_murderer: bool) -> tuple[int, int]:
        """Calculate suspicion change based on question and response"""
        suspicious_keywords = ["murder", "kill", "weapon", "blood", "alibi", "guilty", "crime", "dead", "body"]
        defensive_keywords = ["none of your business", "stop asking", "accusation", "wrong person", "not your concern"]
        cooperative_keywords = ["help", "assist", "truth", "honest", "cooperate", "investigation"]
        
        suspicion_change_speaker = 0
        suspicion_change_listener = 0
        
        question_lower = question.lower()
        if any(keyword in question_lower for keyword in suspicious_keywords):
            suspicion_change_speaker += 2
            # TODO: Implement a mood system. If the murderer has a negative mood because of the question their suspicion increases. The murderer may be a good liar or the question might not be inflmmatory decided by the mood system.
        
        response_lower = response.lower()
        if any(keyword in response_lower for keyword in defensive_keywords):
            suspicion_change_listener += 3
        
        elif any(keyword in response_lower for keyword in cooperative_keywords):
            suspicion_change_listener -= 1
            suspicion_change_speaker -= 1
        
        # Murderers are naturally more suspicious when asked direct questions
        if is_murderer and any(keyword in question_lower for keyword in suspicious_keywords):
            suspicion_change_listener += 2
            
        suspicion_change_speaker = max(min(suspicion_change_speaker, 5), -5)
        suspicion_change_listener = max(min(suspicion_change_listener, 8), -3)
        
        return suspicion_change_speaker, suspicion_change_listener
 