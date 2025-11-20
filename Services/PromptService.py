from langchain_core.prompts import ChatPromptTemplate
from entities.Question import Question
from entities.Location import Location
from entities.Room import Room
from entities.Player import Player
from config.GameConfig import GameConfig


class PromptService:
    """Handles prompt template creation and formatting"""
    
    def __init__(self):
        self.prompt_templates = self._create_prompt_templates()
    
    def _create_prompt_templates(self) -> dict:
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
    
    def select_template_type(self, question: Question) -> str:
        """Choose the most appropriate template based on conversation context"""
        question_lower = question.question.lower()

        if question.listener.suspicion > GameConfig.HIGH_SUSPICION_THRESHOLD:
            return "suspicion_high"

        if any(word in question_lower for word in ["item", "carry", "have", "possess", "belongings", "inventory", "what do you have"]):
            return "inventory_query"

        elif any(word in question_lower for word in ["room", "place", "location", "where", "here", "this room"]):
            return "location_aware"

        else:
            return "basic"
    
    def create_prompt(self, question: Question, location: Location, current_room: Room, 
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
