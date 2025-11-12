from entities.Player import Player
from entities.Location import Location
from entities.Conversation import Question
from entities.Room import Room
from managers.GameManager import GameManager
import random

def ask_about_inventory(game_manager: GameManager, selected_player: Player):
    """Ask a player about their inventory - returns formatted response data"""
    question = Question(
        game_manager.user_player,
        selected_player,
        "What items are you carrying?"
    )
    response, suspicion_change_speaker, suspicion_change_listener = game_manager.strike_conversation(question)
    
    return {
        'response': response,
        'suspicion_change_speaker': suspicion_change_speaker,
        'suspicion_change_listener': suspicion_change_listener,
        'player_name': selected_player.name
    }

def generate_location() -> Location:
    location_names_with_descriptions = {
        "Haunted Manor": "An old manor at the edge of the city, surrounded by dead trees with pre-victorian furniture. While the outside looks fairly unkempt the inside is clean and luxurious.",
        "Ravenswood Manor": "A gothic mansion shrouded in mist, with towering spires and ivy-covered walls that seem to whisper secrets of the past.",
        "Blackwood Estate": "A sprawling estate with a dark history, where the wealthy and powerful once gathered for decadent parties that often ended in tragedy."
    }
    
    event_descriptions = [
        "You were called here by a friend for a masked ball. When you get here, you find commotion, and a man has been killed. You must find out what has happened and who did it.",
        "A storm has trapped you and other guests in this remote manor. During the night, one of the guests was murdered. The killer must be among you.",
        "You arrived for what was supposed to be a weekend retreat, but found the host dead in the library. Now everyone is a suspect and no one can leave until the storm passes."
    ]
    
    possible_rooms = [
        # Main Floor Rooms
        Room("Grand Entrance Hall", "A magnificent marble-floored hall with a sweeping staircase. Portraits of stern-faced ancestors line the walls, their eyes seeming to follow your every move.", random.randint(8, 15)),
        Room("Ballroom", "An opulent ballroom with crystal chandeliers and polished oak floors. Faded banners hang from the ceiling, and a grand piano sits silent in the corner.", random.randint(10, 20)),
        Room("Library", "Floor-to-ceiling bookshelves filled with leather-bound tomes. A ladder slides along a brass rail, and the scent of old paper and leather fills the air.", random.randint(4, 8)),
        Room("Dining Hall", "A long mahogany table set for twenty with fine china and silver candelabras. The remains of an abandoned meal suggest the party was interrupted suddenly.", random.randint(8, 12)),
        Room("Conservatory", "A glass-walled room filled with exotic plants, some withered and dying. The humid air carries the scent of earth and decay.", random.randint(5, 10)),
        Room("Study", "A cozy room with a large oak desk, green leather chairs, and a dying fire in the hearth. Papers are scattered about as if someone left in a hurry.", random.randint(3, 6)),
        Room("Smoking Room", "A masculine room with dark wood paneling and leather armchairs. The air is thick with the lingering scent of cigar smoke and brandy.", random.randint(4, 8)),
        
        # Upper Floor Rooms
        Room("Master Bedroom", "An extravagant bedroom with a four-poster bed and velvet drapes. A vanity table is covered in perfume bottles and jewelry boxes.", random.randint(3, 6)),
        Room("Guest Bedroom (East)", "A comfortable room with floral wallpaper and a bay window overlooking the gardens. The bed is neatly made, untouched.", random.randint(2, 4)),
        Room("Guest Bedroom (West)", "This room shows signs of recent occupation - clothes are strewn about and the bed is unmade. A half-packed suitcase lies open.", random.randint(2, 4)),
        Room("Gallery", "A long hallway displaying paintings of landscapes and portraits. One painting hangs crookedly, as if recently disturbed.", random.randint(6, 12)),
        
        # Service Areas
        Room("Kitchen", "A large, industrial kitchen with copper pots hanging from the ceiling. The air smells of herbs and recently baked bread.", random.randint(4, 8)),
        Room("Butler's Pantry", "A small room between kitchen and dining hall, filled with silverware, linens, and serving dishes neatly arranged.", random.randint(2, 4)),
        Room("Wine Cellar", "A cold, stone-walled room filled with racks of dusty wine bottles. The air is damp and carries the scent of oak and fermentation.", random.randint(3, 6)),
        
        # Outdoor Areas
        Room("Rose Garden", "A formal garden with manicured hedges and rose bushes, though many have withered. Marble statues stand guard along the pathways.", random.randint(6, 15)),
        Room("Maze Garden", "A labyrinth of tall hedges that seems to shift and change. The sound of footsteps echoes, but you can never see who makes them.", random.randint(5, 12)),
        Room("Fountain Courtyard", "A central courtyard with a moss-covered marble fountain. The water has stopped flowing, leaving the basin filled with murky water.", random.randint(8, 18)),
        
        # Special Rooms
        Room("Observatory", "A circular room at the top of the manor with a domed glass ceiling. Astronomical charts and telescopes suggest an interest in the stars.", random.randint(3, 6)),
        Room("Music Room", "Filled with various instruments - a grand piano, several violins, and a harp covered in a dusty cloth. Sheet music is scattered on stands.", random.randint(4, 8)),
        Room("Trophy Room", "Mounted animal heads line the walls, their glass eyes staring blankly. Hunting rifles are displayed in a locked glass case.", random.randint(4, 8))
    ]
    
    real_location_name, real_location_description = random.choice(list(location_names_with_descriptions.items()))
    location_event = random.choice(event_descriptions)
    
    selected_rooms = random.sample(possible_rooms, random.randint(6, 10))
    
    location = Location(real_location_name, real_location_description, 10, location_event, selected_rooms)
    return location

def register_user_player(name: str) -> Player:
    """Register user player - now takes name as parameter"""
    return Player(0, name, 0)

def get_player_job(selected_player: Player) -> dict:
    """Get a player's job information"""
    return {
        'player_name': selected_player.name,
        'job': selected_player.job,
        'response': f"My profession is {selected_player.job}."
    }

def get_player_known_items(selected_player: Player) -> dict:
    """Get a player's known items"""
    known_items = selected_player.get_known_items()
    if known_items:
        items_text = ", ".join([f"{item.name} ({item.description})" for item in known_items])
        response = f"From what I've shared, I have: {items_text}"
    else:
        response = "I haven't shared information about any items I'm carrying."
    
    return {
        'player_name': selected_player.name,
        'known_items': known_items,
        'response': response
    }

def get_user_inventory(user_player: Player) -> dict:
    """Get the user's own inventory"""
    if user_player.inventory:
        items_text = "\n".join([f"• {item.name} - {item.description} (Type: {item.item_type})" for item in user_player.inventory])
        response = f"You are carrying:\n{items_text}"

    else:
        response = "You are not carrying any items."
    
    return {
        'inventory': user_player.inventory,
        'response': response
    }