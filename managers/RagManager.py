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
from entities.Question import Question
from entities.Conversation import Conversation
from entities.Location import Location
from entities.Player import Player
from entities.Room import Room

load_dotenv()

class RagManager:
    
    # LLAMA_3B_HUGGINGFACEHUB
    # MISTRAL_7B_HUGGINGFACEHUB
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
        self.prompt_templates = self._create_prompt_templates()
    
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
            chat_model = ChatHuggingFace(llm=llm)
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
                chat_model = ChatHuggingFace(llm=llm)
                print("Fallback model loaded successfully!")
                return chat_model
                
            except Exception as e2:
                print(f"Error loading fallback model: {e2}")
                print("Using rule-based fallback system.")
                return None
    
    def add_conversation(self, conversation: Conversation, turn: int) -> None:
        """Store a conversation in memory"""
        doc = Document(
            page_content=f"Question: {conversation.question.question}\nResponse: {conversation.response}",
            metadata={
                "player_ids": f"{conversation.question.speaker.id}-{conversation.question.listener.id}",
                "players": f"{conversation.question.speaker.name}-{conversation.question.listener.name}",
                "turn": turn
            }
        )
        self.vector_store.add_documents([doc])
        
    def get_conversation_context(self, current_question: Question, number_docs_to_retrieve: int = 3) -> str:
        """Retrieve relevant conversation history"""
        
        if self.vector_store._collection.count() == 0:
            return "No previous conversations."
        
        # Search for conversations between these two players
        player_filter = f"{current_question.speaker.id}-{current_question.listener.id}"
        results = self.vector_store.similarity_search(
            f"Conversation between {current_question.speaker.name} and {current_question.listener.name}: {current_question.question}",
            k=number_docs_to_retrieve,
            filter={"player_ids": player_filter}
        )
        
        if not results:
            return "No previous conversations with this person."
        
        context = "Previous conversations with this person:\n"
        for i, doc in enumerate(results):
            context += f"{i+1}. {doc.page_content}\n"
        
        return context

    def generate_response(self, question: Question, location: Location, current_room: Room, nearby_players: list[Player]):
        """Generate NPC response using RAG with proper context"""
        
        if not self.llm:
            return self.fallback_response(question)
        
        try:
            context = self.get_conversation_context(question)
            template_type = self.select_appropriate_template(question)
            prompt = self._create_prompt(question, location, current_room, context, template_type, nearby_players)
            
            response = self.llm.invoke(prompt)
            
            response_text = response if isinstance(response, str) else getattr(response, 'content', str(response))
            
            response_text = self._clean_response(response_text)
            
            suspicion_change_speaker, suspicion_change_listener = self._calculate_suspicion_change(
                question.question, response_text, question.listener.murderer,
                question.listener.lying_ability, question.listener.mood
            )
            
            # If this is an inventory question and the listener is innocent, mark their items as known
            if "inventory" in self.select_appropriate_template(question) and not question.listener.murderer:
                for item in question.listener.inventory:
                    if not item.murder_weapon:  # Don't automatically reveal murder weapons
                        item.known = True
            
            return response_text, suspicion_change_speaker, suspicion_change_listener 
            
        except Exception as exception:
            print(f"LLM generation error: {exception}")
            return self.fallback_response(question)
    
    def _create_prompt(self, question: Question, location: Location, current_room: Room, 
                      context: str, template_type: str, nearby_players: list[Player]):
        """Create appropriate prompt based on template type"""
        
        listener = question.listener

        nearby_players_text = ""
        if nearby_players:
            nearby_players_text = ", ".join([p.name for p in nearby_players if p.id != listener.id])

        known_inventory = [item for item in listener.inventory if item.known]
        inventory_text = "None known to others"
        if known_inventory:
            inventory_text = ", ".join([f"{item.name} ({item.description})" for item in known_inventory])

        template = self.prompt_templates[template_type]
        print(context)
        messages = template.format_messages(
            character_name=listener.name,
            character_job=listener.job,
            character_mood=listener.mood,
            location_name=location.name,
            location_description=location.description,
            event_description=location.event_description,
            current_room_name=current_room.name,
            current_room_description=current_room.description,
            room_type=current_room.room_type,
            nearby_players=nearby_players_text,
            known_inventory=inventory_text,
            context=context,
            question=question.question,
            role="MURDERER - be defensive, evasive, and careful about what you reveal" if listener.murderer else "INNOCENT - be helpful, cooperative, and truthful",
            suspicion_level=listener.suspicion
        )
        
        return messages
    
    def _create_prompt_templates(self):
        """Create comprehensive prompt templates for different scenarios"""
        
        return {
            "basic": ChatPromptTemplate.from_messages([
                ("system", """You are {character_name}, a {character_job} attending an event at {location_name}. 
                Location: {location_description}
                Event: {event_description}
                Current Room: {current_room_name} - {current_room_description}
                Your Role: {role}
                Your Mood: {character_mood}
                Your Known Items: {known_inventory}
                Nearby People: {nearby_players}
                Suspicion Level: {suspicion_level}

                {context}

                IMPORTANT: Respond ONLY with your character's dialogue. Do not include any explanations, labels, or system messages.
                Keep your responses brief (1-2 sentences). Stay consistent with your role and mood. 
                If you're the murderer, be careful not to reveal your guilt. If innocent, try to be helpful."""),
                                ("human", "{question}")
                            ]),
                            
                            "inventory_query": ChatPromptTemplate.from_messages([
                                ("system", """You are {character_name}, a {character_job} at {location_name}.
                Your Role: {role}  
                Your Mood: {character_mood}
                Your Actual Inventory: {known_inventory}
                Suspicion Level: {suspicion_level}

                {context}

                IMPORTANT: Respond ONLY with your character's dialogue about what items you have. 
                - If you're INNOCENT: Be truthful about items others know you have. You can mention personal items freely.
                - If you're the MURDERER: Be evasive about suspicious items. You might lie about or downplay certain items, especially weapons. 
                - Never directly admit to having a murder weapon if you're the murderer.
                - Keep responses natural and in character.
                - Do not include any explanations, labels, or system messages."""),
                                ("human", "{question}")
                            ]),
                            
                            "location_aware": ChatPromptTemplate.from_messages([
                                ("system", """You are {character_name} in the {current_room_name} at {location_name}.
                Room Description: {current_room_description}
                Room Type: {room_type}
                Nearby People: {nearby_players}
                Your Role: {role}
                Your Job: {character_job}

                {context}

                Incorporate your surroundings into your response naturally. Reference the room features or other people if relevant.
                Keep responses brief and in character."""),
                                ("human", "{question}")
                            ]),
                            
                            "suspicion_high": ChatPromptTemplate.from_messages([
                                ("system", """You are {character_name}. People are becoming suspicious of you.
                Your Suspicion Level: {suspicion_level}
                Your Role: {role}
                Your Mood: {character_mood}

                {context}

                You're feeling defensive due to high suspicion. Choose your words carefully.
                - If INNOCENT: You might be frustrated or anxious about false suspicion.
                - If MURDERER: You're becoming nervous and more careful about what you say.
                Respond accordingly, keeping answers brief but meaningful."""),
                                ("human", "{question}")
                            ])
                        }
    
    def select_appropriate_template(self, question: Question) -> str:
        """Choose the most appropriate template based on conversation context"""
        question_lower = question.question.lower()

        if question.listener.suspicion > 25:
            return "suspicion_high"

        if any(word in question_lower for word in ["item", "carry", "have", "possess", "belongings", "inventory", "what do you have"]):
            return "inventory_query"

        elif any(word in question_lower for word in ["room", "place", "location", "where", "here", "this room"]):
            return "location_aware"

        else:
            return "basic"
    
    def fallback_response(self, question: Question):
        """Fallback response system when LLM fails"""
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
        """Clean up model response to extract only the assistant's reply"""
        # Convert to string if needed
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
        
        # Remove any remaining special tokens
        special_tokens = [
            "<|endoftext|>", "<s>", "</s>", "[INST]", "[/INST]", 
            "<|system|>", "<|user|>", "<|assistant|>", "### System:",
            "System:", "### Human:", "Human:", "### Instruction:"
        ]
        for token in special_tokens:
            response = response.replace(token, "")
        
        # Remove any prompt template fragments that might have been included
        prompt_fragments = [
            "Respond in character", "Keep responses brief", "Stay consistent",
            "Your Role:", "Location:", "Current Room:", "Your Mood:"
        ]
        
        # Split by newlines and filter out lines that contain prompt instructions
        lines = response.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if line and not any(fragment in line for fragment in prompt_fragments):
                cleaned_lines.append(line)
        
        response = ' '.join(cleaned_lines)
        
        # Final cleanup
        response = response.strip('"\' \n\t')
        
        # If the response is empty or too short after cleaning, use fallback
        if not response or len(response) < 5:
            return "I'm not sure how to respond to that."
        
        # Ensure the response doesn't start with the question
        if "?" in response and response.find("?") < len(response) // 3:
            # Likely includes the question, try to extract after the last question mark
            parts = response.rsplit("?", 1)
            if len(parts) > 1:
                response = parts[1].strip()
        
        return response
    
    def _calculate_suspicion_change(self, question: str, response: str, is_murderer: bool, 
                                  lying_ability: int, mood: str) -> tuple[int, int]:
        """Calculate suspicion change based on question and response"""
        suspicious_keywords = ["murder", "kill", "weapon", "blood", "alibi", "guilty", "crime", "dead", "body"]
        defensive_keywords = ["none of your business", "stop asking", "accusation", "wrong person", "not your concern"]
        cooperative_keywords = ["help", "assist", "truth", "honest", "cooperate", "investigation"]
        
        suspicion_change_speaker = 0
        suspicion_change_listener = 0
        
        question_lower = question.lower()
        if any(keyword in question_lower for keyword in suspicious_keywords):
            suspicion_change_speaker += 2
            if is_murderer:
                # Good liars (high lying_ability) don't get as suspicious from direct questions
                if lying_ability > 7 and mood not in ["defensive", "angry"]:
                    suspicion_change_listener += 3
                else:
                    suspicion_change_listener += 1
            else:
                suspicion_change_listener += 1
            
            
                
        response_lower = response.lower()
        if any(keyword in response_lower for keyword in defensive_keywords):
            suspicion_change_listener += 3
        
        elif any(keyword in response_lower for keyword in cooperative_keywords):
            suspicion_change_listener -= 1
            suspicion_change_speaker -= 1
        
        # Murderers are naturally more suspicious when asked direct questions
        if is_murderer and any(keyword in question_lower for keyword in suspicious_keywords):
            suspicion_change_listener += 2
            
        # mood will affect suspicon by itself
        if mood == "angry":
            suspicion_change_listener += 2
        elif mood == "defensive":
            suspicion_change_listener += 1
        elif mood == "cooperative":
            suspicion_change_speaker -= 1
            
        suspicion_change_speaker = max(min(suspicion_change_speaker, 5), -5)
        suspicion_change_listener = max(min(suspicion_change_listener, 8), -3)
        
        return suspicion_change_speaker, suspicion_change_listener

    def clear_database(self) -> None:
        """Clear the entire conversation database"""
        try:
            self.vector_store.delete_collection()
            print("Conversation database cleared.")
        except Exception as e:
            print(f"Error clearing database: {e}")
            try:
                all_docs = self.vector_store.get()
                if 'ids' in all_docs and all_docs['ids']:
                    self.vector_store.delete(ids=all_docs['ids'])
            except Exception as e2:
                print(f"Error with fallback cleanup: {e2}")